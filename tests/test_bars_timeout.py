"""The get_bars facades' silence watchdog: pass-through, validation, error type."""

import asyncio
import base64
import hashlib
import json
from contextlib import asynccontextmanager

import pytest
import websockets

from tradingview_sdk import AsyncTradingView, BarTimeoutError, ProtocolError, TradingView
from tradingview_sdk import bars as bars_module
from tradingview_sdk import client as client_module
from tradingview_sdk._chart import SERIES_ID
from tradingview_sdk._protocol import decode_frame, parse_json_message, wrap_raw
from tradingview_sdk.auth import AuthTokenCache, Credentials
from tradingview_sdk.bars import (
    _CLOSE_GRACE,
    _DEADLINE_FLOOR,
    _MAX_ROUNDS,
    _default_deadline,
    fetch_bars,
)
from tradingview_sdk.models import BarSet


@pytest.fixture
def capture_fetch(monkeypatch):
    calls: list[dict] = []

    async def fake_fetch_bars(**kwargs):
        calls.append(kwargs)
        return BarSet(symbol=kwargs["symbol"], interval=kwargs["interval"], bars=())

    monkeypatch.setattr(client_module, "fetch_bars", fake_fetch_bars)
    return calls


def test_sync_get_bars_defaults_to_five_seconds_and_passes_timeout_through(capture_fetch):
    # 5s is the documented default: a stalled server costs that much per attempt, so
    # a caller trying several exchanges per symbol stays bounded.
    with TradingView() as tv:
        tv.get_bars("X:Y", "1D", bars=3)
        tv.get_bars("X:Y", "1D", bars=3, timeout=1.5)
    assert [c["timeout"] for c in capture_fetch] == [5.0, 1.5]


async def test_async_get_bars_defaults_to_five_seconds_and_passes_timeout_through(capture_fetch):
    async with AsyncTradingView() as tv:
        await tv.get_bars("X:Y", "1D", bars=3)
        await tv.get_bars("X:Y", "1D", bars=3, timeout=2.5)
    assert [c["timeout"] for c in capture_fetch] == [5.0, 2.5]


@pytest.mark.parametrize("bad", [None, 0, -1.0])
async def test_non_positive_timeout_is_rejected(bad):
    # None would disable the watchdog outright and <= 0 would fail every healthy call;
    # both are reachable now that `timeout` is a public argument.
    with pytest.raises(ValueError, match="positive"):
        await fetch_bars(symbol="X:Y", auth=AuthTokenCache(Credentials()), timeout=bad)


async def _accept_websocket(reader, writer) -> None:
    """Answer the opening handshake so the client believes it has a live session."""
    request = await reader.readuntil(b"\r\n\r\n")
    key = ""
    for line in request.decode(errors="replace").split("\r\n"):
        if line.lower().startswith("sec-websocket-key:"):
            key = line.split(":", 1)[1].strip()
    digest = hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
    writer.write(
        b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
        b"Connection: Upgrade\r\nSec-WebSocket-Accept: " + base64.b64encode(digest) + b"\r\n\r\n"
    )
    await writer.drain()


@asynccontextmanager
async def _silent_server(*, handshake: bool):
    """A server that accepts the connection and then never speaks — not even to close.

    The handler parks on ``read()`` rather than sleeping a fixed time. Python 3.12's
    ``Server.wait_closed()`` blocks until every handler returns (3.11 and 3.14 return
    immediately), so a sleeping handler hangs the whole suite there for its full
    duration; waiting for EOF ends the handler the moment the client disconnects, on
    every version.
    """

    async def handler(reader, writer):
        try:
            if handshake:
                await _accept_websocket(reader, writer)
            await reader.read()          # silent; returns only once the client goes away
        except (asyncio.IncompleteReadError, ConnectionResetError):
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    try:
        yield f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/socket.io/websocket"
    finally:
        server.close()
        # Bounded: a socket the SDK failed to drop should fail this test, not hang it.
        await asyncio.wait_for(server.wait_closed(), timeout=10)


async def test_connect_timeout_raises_bar_timeout_error():
    # A host that accepts TCP but never completes the websocket handshake must be
    # bounded by `timeout` too, not by websockets' own 10s open_timeout default.
    loop = asyncio.get_running_loop()
    async with _silent_server(handshake=False) as url:
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="connecting"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=0.5
            )
        assert loop.time() - began < 5.0        # not websockets' 10s open_timeout


async def test_stalled_session_does_not_pay_the_close_handshake_on_top():
    # A server that goes silent mid-session ignores the closing handshake too. websockets
    # would wait out its own close_timeout there, which made a 5s watchdog cost 15s wall
    # clock — most of the stall budget spent after the decision to give up was made.
    loop = asyncio.get_running_loop()
    async with _silent_server(handshake=True) as url:
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="waiting for bars"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=1.0
            )
        elapsed = loop.time() - began
    # The watchdog plus the close grace, nowhere near websockets' 10s close_timeout.
    assert elapsed < 1.0 + _CLOSE_GRACE + 1.0, f"stall cost {elapsed:.1f}s"


def test_bar_timeout_error_stays_catchable_as_protocol_error():
    assert issubclass(BarTimeoutError, ProtocolError)
    assert issubclass(BarTimeoutError, TimeoutError)


# -- a session that is alive and chatty, but not finishing ---------------------


@asynccontextmanager
async def _chart_server(handler):
    """Serve ``handler`` on a websocket and yield its chart-session URL.

    ``wait_closed`` is bounded for the same reason as :func:`_silent_server`: these
    handlers pump forever by design, so a socket the SDK failed to drop should fail
    the test rather than hang the suite.
    """
    server = await websockets.serve(handler, "127.0.0.1", 0)
    try:
        yield f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/socket.io/websocket"
    finally:
        server.close()
        await asyncio.wait_for(server.wait_closed(), timeout=10)


def _timescale_update(chart_session: str, times: list[int]) -> str:
    points = [{"i": i, "v": [t, 10.0, 12.0, 9.0, 11.0, 100.0]} for i, t in enumerate(times)]
    return wrap_raw(json.dumps(
        {"m": "timescale_update", "p": [chart_session, {SERIES_ID: {"s": points}}]}
    ))


class _NeverCompletes:
    """Answers the handshake, then repeats one payload forever without finishing a round.

    ``payload`` is what it repeats: a heartbeat exercises the watchdog (the session is
    responsive but stalled), a real protocol message exercises the deadline (the session
    is genuinely advancing and the watchdog is right not to fire). ``bars`` are delivered
    once, before the repetition starts, to reach the partial-result path.
    """

    def __init__(self, *, payload: str, bars: list[int] | None = None, every: float = 0.05):
        self.payload = payload
        self.bars = bars or []
        self.every = every
        self.echoes: list[str] = []

    async def __call__(self, ws) -> None:
        pump: asyncio.Task | None = None

        async def repeat(chart_session: str) -> None:
            if self.bars:
                await ws.send(_timescale_update(chart_session, self.bars))
            while True:
                await ws.send(self.payload)
                await asyncio.sleep(self.every)

        try:
            await ws.send(wrap_raw(json.dumps({"session_id": "fake"})))
            async for frame in ws:
                for message in decode_frame(frame):
                    if message.startswith("~h~"):
                        self.echoes.append(message)
                        continue
                    data = parse_json_message(message)
                    if not data:
                        continue
                    method, params = data["m"], data["p"]
                    if method == "resolve_symbol":
                        await ws.send(wrap_raw(json.dumps(
                            {"m": "symbol_resolved",
                             "p": [params[0], params[1], {"currency_code": "USD"}]}
                        )))
                    elif method == "create_series" and pump is None:
                        pump = asyncio.create_task(repeat(params[0]))
        except websockets.ConnectionClosed:
            pass
        finally:
            if pump is not None:
                pump.cancel()


async def test_heartbeats_do_not_re_arm_the_silence_watchdog():
    # The server answers resolve_symbol and then sends nothing but heartbeats, 20x
    # faster than the watchdog. Echoing those keeps the socket alive, which is correct;
    # letting them count as progress is what made `timeout` unenforceable for any caller
    # whose watchdog is longer than the server's heartbeat interval.
    server = _NeverCompletes(payload=wrap_raw("~h~1"))
    loop = asyncio.get_running_loop()
    async with _chart_server(server) as url:
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="waiting for bars"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=1.0
            )
        elapsed = loop.time() - began
    assert elapsed < 1.0 + _CLOSE_GRACE + 1.0, f"heartbeats extended the stall to {elapsed:.1f}s"
    # Guards against passing for the wrong reason: the client must still be echoing,
    # so this is a watchdog that fires on a live connection, not a dead one.
    assert server.echoes, "client stopped echoing heartbeats"


async def test_total_deadline_bounds_a_session_that_keeps_making_progress():
    # Real protocol frames, faster than the watchdog, that never add up to
    # series_completed. The watchdog cannot catch this by design — the session is
    # advancing — so only the total deadline ends the call.
    payload = wrap_raw(json.dumps({"m": "series_loading", "p": ["cs", SERIES_ID]}))
    loop = asyncio.get_running_loop()
    async with _chart_server(_NeverCompletes(payload=payload)) as url:
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="deadline"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url,
                timeout=1.0, deadline=1.5,
            )
        elapsed = loop.time() - began
    assert 1.5 <= elapsed < 1.5 + _CLOSE_GRACE + 1.0, f"deadline gave up after {elapsed:.1f}s"


async def test_deadline_returns_the_bars_that_arrived_rather_than_raising():
    # Same stall, but after a load round delivered bars: the deadline takes the same
    # bargain the watchdog does — partial data, flagged, beats an exception.
    payload = wrap_raw(json.dumps({"m": "series_loading", "p": ["cs", SERIES_ID]}))
    times = [1_700_000_000 - i * 86_400 for i in range(3)]
    server = _NeverCompletes(payload=payload, bars=sorted(times))
    async with _chart_server(server) as url:
        result = await fetch_bars(
            symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url,
            timeout=1.0, deadline=1.5,
        )
    assert [b.time for b in result.bars] == sorted(times)
    assert result.raw["truncated"] is True


async def test_a_healthy_session_interleaved_with_heartbeats_still_completes():
    # The other side of the watchdog change: heartbeats sprinkled through a good
    # session must not break it, and must still be echoed.
    echoes: list[str] = []
    times = [1_700_000_000 - i * 86_400 for i in range(3)]

    async def handler(ws):
        try:
            await ws.send(wrap_raw(json.dumps({"session_id": "fake"})))
            async for frame in ws:
                for message in decode_frame(frame):
                    if message.startswith("~h~"):
                        echoes.append(message)
                        continue
                    data = parse_json_message(message)
                    if not data:
                        continue
                    method, params = data["m"], data["p"]
                    if method == "resolve_symbol":
                        await ws.send(wrap_raw("~h~1"))
                        await ws.send(wrap_raw(json.dumps(
                            {"m": "symbol_resolved",
                             "p": [params[0], params[1], {"currency_code": "USD"}]}
                        )))
                    elif method == "create_series":
                        await ws.send(wrap_raw("~h~2"))
                        await ws.send(_timescale_update(params[0], sorted(times)))
                        await ws.send(wrap_raw("~h~3"))
                        await ws.send(wrap_raw(json.dumps(
                            {"m": "series_completed", "p": [params[0], SERIES_ID]}
                        )))
        except websockets.ConnectionClosed:
            pass

    async with _chart_server(handler) as url:
        # bars=3 so the first round already satisfies the target: this test is about
        # heartbeats surviving a load, not about pagination (covered in test_bars_session).
        result = await fetch_bars(
            symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=2.0, bars=3
        )
    assert [b.time for b in result.bars] == sorted(times)
    assert result.raw["truncated"] is False
    assert echoes == ["~h~1", "~h~2", "~h~3"]


@pytest.mark.parametrize("bad", [0, -1.0])
async def test_non_positive_deadline_is_rejected(bad):
    # None is not in this list on purpose: it means "derive one", so there is no way
    # to ask fetch_bars for no total bound at all.
    with pytest.raises(ValueError, match="deadline must be a positive"):
        await fetch_bars(
            symbol="X:Y", auth=AuthTokenCache(Credentials()), timeout=1.0, deadline=bad
        )


@pytest.mark.parametrize("timeout", [0.1, 1.0, 5.0, 30.0, 120.0])
def test_default_deadline_never_preempts_the_watchdog(timeout):
    # The deadline is a backstop, not a second watchdog: if it could fire first, a
    # plain stall would report the wrong cause and a healthy multi-round `start=`
    # range would start failing. One full watchdog window per pagination round, with
    # a floor so a tightened `timeout` does not silently tighten this too.
    derived = _default_deadline(timeout)
    assert derived >= _DEADLINE_FLOOR
    assert derived >= timeout * _MAX_ROUNDS
    assert derived > timeout


def test_get_bars_facades_pass_the_deadline_through(capture_fetch):
    with TradingView() as tv:
        tv.get_bars("X:Y", "1D", bars=3)
        tv.get_bars("X:Y", "1D", bars=3, deadline=12.0)
    assert [c["deadline"] for c in capture_fetch] == [None, 12.0]


async def test_async_get_bars_passes_the_deadline_through(capture_fetch):
    async with AsyncTradingView() as tv:
        await tv.get_bars("X:Y", "1D", bars=3)
        await tv.get_bars("X:Y", "1D", bars=3, deadline=7.5)
    assert [c["deadline"] for c in capture_fetch] == [None, 7.5]


async def test_a_deadline_tighter_than_the_watchdog_wins_and_says_so():
    # The two clocks race on the very first read. Whichever is nearer must both end
    # the call and name itself, or a caller tuning one of them is debugging blind.
    loop = asyncio.get_running_loop()
    async with _silent_server(handshake=True) as url:
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="deadline of 0.3s"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url,
                timeout=5.0, deadline=0.3,
            )
        elapsed = loop.time() - began
    assert elapsed < 5.0, f"the watchdog outranked a tighter deadline ({elapsed:.1f}s)"


async def test_deadline_spent_before_the_session_opens_is_reported_as_such(monkeypatch):
    # The clock starts before the token fetch, so `deadline` covers the REST leg too.
    # Exhausting it there must not fall through to websockets.connect with a
    # non-positive open_timeout.
    async def slow_token(auth):
        await asyncio.sleep(0.3)
        return "token"

    monkeypatch.setattr(bars_module, "resolve_ws_token", slow_token)
    async with _silent_server(handshake=True) as url:
        with pytest.raises(BarTimeoutError, match="expired before the chart session"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url,
                timeout=5.0, deadline=0.1,
            )
