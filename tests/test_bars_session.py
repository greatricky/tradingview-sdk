"""fetch_bars against a local fake chart-session server (pagination, errors)."""

import asyncio
import json
import time

import pytest
import websockets

from tradingview_sdk._chart import SERIES_ID
from tradingview_sdk._protocol import decode_frame, parse_json_message, wrap_raw
from tradingview_sdk.auth import AuthTokenCache, Credentials
from tradingview_sdk.bar_stream import BarStream
from tradingview_sdk.bars import _MAX_ROUNDS, fetch_bars
from tradingview_sdk.errors import (
    BarTimeoutError,
    IncompleteBarsError,
    ProtocolError,
    SymbolNotFoundError,
)

BAR_SECONDS = 86_400
NEWEST = 1_700_000_000


class FakeChartServer:
    """Serves ``history`` bars newest-first, one load round per create_series/request_more_data."""

    def __init__(
        self,
        *,
        history: int,
        per_round: int = 5,
        symbol_error: bool = False,
        symbol_error_reason: str | None = None,
        bad_bar: bool = False,
        symbol_meta: dict | None = None,
    ):
        self.history = history
        self.per_round = per_round
        self.symbol_error = symbol_error
        self.symbol_error_reason = symbol_error_reason
        self.bad_bar = bad_bar
        # What symbol_resolved describes the instrument as; the bare default is what
        # every pre-0.5.0 test replied with.
        self.symbol_meta = {"currency_code": "USD"} if symbol_meta is None else symbol_meta
        self.rounds = 0
        self.served = 0
        self.received: list[dict] = []
        self._server = None

    async def start(self) -> str:
        self._server = await websockets.serve(self._handler, "127.0.0.1", 0)
        return f"ws://127.0.0.1:{self._server.sockets[0].getsockname()[1]}/socket.io/websocket"

    async def stop(self) -> None:
        self._server.close()
        await self._server.wait_closed()

    def _bar(self, index: int) -> dict:
        """Bar ``index`` counting back from the newest."""
        t = NEWEST - index * BAR_SECONDS
        if self.bad_bar and index == 1:  # a session with no trades comes back as nulls
            return {"i": index, "v": [t, None, None, None, None, 0]}
        return {"i": index, "v": [t, 10.0, 12.0, 9.0, float(index), 100.0]}

    async def _load_round(self, ws, chart_session: str) -> None:
        remaining = max(0, self.history - self.served)
        count = min(self.per_round, remaining)
        points = [self._bar(self.served + i) for i in range(count)]
        self.served += count
        self.rounds += 1
        if points:
            await ws.send(wrap_raw(json.dumps(
                {"m": "timescale_update", "p": [chart_session, {SERIES_ID: {"s": points}}]}
            )))
        await ws.send(wrap_raw(json.dumps({"m": "series_completed", "p": [chart_session, SERIES_ID]})))

    async def _handler(self, ws):
        await ws.send(wrap_raw(json.dumps({"session_id": "fake"})))
        try:
            async for frame in ws:
                for message in decode_frame(frame):
                    data = parse_json_message(message)
                    if not data:
                        continue
                    self.received.append(data)
                    method, params = data["m"], data["p"]
                    if method == "resolve_symbol":
                        if self.symbol_error:
                            detail = [self.symbol_error_reason] if self.symbol_error_reason else []
                            await ws.send(wrap_raw(json.dumps(
                                {"m": "symbol_error", "p": [params[0], params[1], *detail]}
                            )))
                            continue
                        await ws.send(wrap_raw(json.dumps(
                            {"m": "symbol_resolved", "p": [params[0], params[1], self.symbol_meta]}
                        )))
                    elif method in ("create_series", "request_more_data"):
                        await self._load_round(ws, params[0])
        except websockets.ConnectionClosed:
            pass


async def _fetch(server, *, timeout: float = 5.0, **kwargs):
    url = await server.start()
    try:
        return await fetch_bars(
            symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=timeout, **kwargs
        )
    finally:
        await server.stop()


async def test_pages_back_over_many_rounds():
    # 5 bars per round: reaching `start` needs several request_more_data rounds, which
    # is exactly the path that used to hang after the first one.
    server = FakeChartServer(history=40, per_round=5)
    start = NEWEST - 30 * BAR_SECONDS
    result = await asyncio.wait_for(_fetch(server, interval="1D", start=start), timeout=20)
    assert server.rounds >= 7                              # 1 create_series + 6+ request_more_data
    assert len(result) == 31                               # inclusive of the `start` bar
    assert list(result.times) == sorted(result.times)
    assert result.bars[0].time == start
    assert result.currency == "USD"


async def test_stops_when_history_is_exhausted():
    # Only 12 bars exist but 500 were asked for: the server keeps completing rounds
    # with nothing new, and the loop must notice instead of paging to _MAX_ROUNDS.
    server = FakeChartServer(history=12, per_round=5)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=500), timeout=20)
    assert len(result) == 12
    assert server.rounds <= 5


async def test_single_round_when_count_is_satisfied():
    server = FakeChartServer(history=40, per_round=5)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=3), timeout=20)
    assert len(result) == 3
    assert server.rounds == 1
    assert result.raw["chart_session_rounds"] == 0


async def test_null_price_bar_is_skipped_not_fatal():
    server = FakeChartServer(history=5, per_round=5, bad_bar=True)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)
    assert len(result) == 4                                # the null bar dropped, the rest kept
    assert NEWEST - BAR_SECONDS not in result.times


@pytest.mark.parametrize(
    "reason, expected",
    [(None, r"could not resolve symbol 'X:Y'$"), ("invalid symbol", "invalid symbol")],
)
async def test_symbol_error_maps_to_symbol_not_found(reason, expected):
    # A real ticker on the wrong exchange (e.g. NYSE:AAPL) is rejected exactly like a
    # bogus one: symbol_error right after resolve_symbol. The short `timeout` here is
    # the point — if that rejection ever stopped raising, the watchdog would fire and
    # the wrong exception type would surface instead of this test hanging for 5s.
    server = FakeChartServer(history=5, symbol_error=True, symbol_error_reason=reason)
    with pytest.raises(SymbolNotFoundError, match=expected):
        await asyncio.wait_for(_fetch(server, interval="1D", bars=5, timeout=0.3), timeout=20)


async def test_silent_server_times_out_with_bar_timeout_error():
    server = FakeChartServer(history=0, per_round=0)
    server._load_round = lambda ws, cs: asyncio.sleep(0)   # never completes a round
    with pytest.raises(BarTimeoutError, match="timed out"):
        await asyncio.wait_for(_fetch(server, interval="1D", bars=5, timeout=0.3), timeout=20)
    # Callers separate "retry this" from "the server said no", and pre-existing
    # `except ProtocolError` handlers must keep working.
    assert issubclass(BarTimeoutError, (ProtocolError, TimeoutError))


async def test_stall_after_some_bars_returns_them_flagged_as_truncated():
    # A stall partway through pagination keeps the bars already collected; without the
    # flag the `start` filter would hand back a short series that looks complete.
    server = FakeChartServer(history=40, per_round=5)
    original = server._load_round
    calls = 0

    async def stall_after_first(ws, chart_session):
        nonlocal calls
        calls += 1
        if calls > 1:
            return          # answer the first round, then go silent
        await original(ws, chart_session)

    server._load_round = stall_after_first
    start = NEWEST - 30 * BAR_SECONDS
    result = await asyncio.wait_for(
        _fetch(server, interval="1D", start=start, timeout=0.3), timeout=20
    )
    assert 0 < len(result) < 30
    assert result.raw["truncated"] is True


async def test_complete_load_is_not_flagged_as_truncated():
    server = FakeChartServer(history=40, per_round=5)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)
    assert result.raw["truncated"] is False


async def test_strict_turns_a_truncated_load_into_an_error_carrying_the_bars():
    # Same stall as above. A caller that records what it fetches cannot afford to
    # forget the flag, so strict mode makes the shortfall an exception — one that
    # still hands over what arrived and is still retryable as a BarTimeoutError.
    server = FakeChartServer(history=40, per_round=5)
    original = server._load_round
    calls = 0

    async def stall_after_first(ws, chart_session):
        nonlocal calls
        calls += 1
        if calls > 1:
            return
        await original(ws, chart_session)

    server._load_round = stall_after_first
    start = NEWEST - 30 * BAR_SECONDS
    with pytest.raises(IncompleteBarsError, match="partial") as info:
        await asyncio.wait_for(
            _fetch(server, interval="1D", start=start, timeout=0.3, strict=True), timeout=20
        )
    partial = info.value.bars
    assert 0 < len(partial) < 30
    assert partial.raw["truncated"] is True
    assert partial.currency == "USD"
    assert isinstance(info.value, BarTimeoutError)


async def test_strict_with_nothing_collected_is_still_the_plain_timeout():
    # Nothing to attach, so nothing to promote: the parent class, as before.
    server = FakeChartServer(history=0, per_round=0)
    server._load_round = lambda ws, cs: asyncio.sleep(0)
    with pytest.raises(BarTimeoutError) as info:
        await asyncio.wait_for(
            _fetch(server, interval="1D", bars=5, timeout=0.3, strict=True), timeout=20
        )
    assert not isinstance(info.value, IncompleteBarsError)


async def test_strict_does_not_touch_a_complete_load():
    server = FakeChartServer(history=40, per_round=5)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5, strict=True), timeout=20)
    assert len(result) == 5 and result.raw["truncated"] is False


async def test_round_cap_before_start_is_flagged_truncated():
    # 200 bars of history at 5 a round: `start` 150 days back needs 30 rounds, but
    # the cap stops paging at _MAX_ROUNDS. The server never stalled, so nothing
    # else marks the shortfall — the cap exit has to, or the `start` filter below
    # it hides a 105-bar answer to a 151-bar question as complete.
    server = FakeChartServer(history=200, per_round=5)
    start = NEWEST - 150 * BAR_SECONDS
    result = await asyncio.wait_for(_fetch(server, interval="1D", start=start), timeout=20)
    assert server.rounds == _MAX_ROUNDS + 1                # create_series + the capped pages
    assert 0 < len(result) < 151
    assert result.bars[0].time > start
    assert result.raw["truncated"] is True
    assert result.raw["chart_session_rounds"] == _MAX_ROUNDS


async def test_strict_refuses_a_round_capped_load():
    server = FakeChartServer(history=200, per_round=5)
    start = NEWEST - 150 * BAR_SECONDS
    with pytest.raises(IncompleteBarsError) as info:
        await asyncio.wait_for(_fetch(server, interval="1D", start=start, strict=True), timeout=20)
    assert info.value.bars.raw["truncated"] is True
    assert 0 < len(info.value.bars) < 151


async def test_round_cap_on_a_bars_count_is_flagged_truncated():
    # The same cap on the `bars=` path: more bars asked for than the rounds can
    # carry, with history still left, is a short answer too.
    server = FakeChartServer(history=200, per_round=5)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=150), timeout=20)
    assert 0 < len(result) < 150
    assert result.raw["truncated"] is True


async def test_reaching_start_exactly_at_the_cap_is_not_truncated():
    # The cap only counts when the range is still uncovered: a fetch whose last
    # allowed round reaches `start` is complete, however many rounds it took.
    server = FakeChartServer(history=200, per_round=5)
    covered = 5 * (_MAX_ROUNDS + 1)                        # bars the cap can carry
    start = NEWEST - (covered - 1) * BAR_SECONDS
    result = await asyncio.wait_for(_fetch(server, interval="1D", start=start), timeout=20)
    assert len(result) == covered
    assert result.bars[0].time == start
    assert result.raw["truncated"] is False


# --- symbol_resolved metadata and the session spec ---------------------------

_CBOE_VIX = {
    "currency_code": "USD",
    "timezone": "America/Chicago",
    "session": "0215-0826,0830-1516",
    "type": "index",
    "description": "CBOE Volatility Index",
}


async def test_result_carries_the_resolved_timezone_and_session():
    # A daily bar is stamped at its session open in the exchange's own zone, so a
    # caller dating bars needs both of these — they were dropped before 0.5.0.
    server = FakeChartServer(history=5, symbol_meta=_CBOE_VIX)
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)
    assert result.timezone == "America/Chicago"
    assert result.session == "0215-0826,0830-1516"
    assert result.currency == "USD"
    assert result.raw["symbol_resolved"] == _CBOE_VIX     # the whole reply, unmodelled fields included


async def test_missing_or_malformed_resolved_fields_read_as_none():
    server = FakeChartServer(history=5, symbol_meta={"currency_code": "USD", "timezone": "", "session": 7})
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)
    assert result.timezone is None and result.session is None


def _resolve_spec(server: FakeChartServer) -> str:
    (msg,) = [m for m in server.received if m["m"] == "resolve_symbol"]
    return msg["p"][2]


async def test_session_is_sent_in_the_resolve_spec_when_asked_for():
    server = FakeChartServer(history=5)
    await asyncio.wait_for(_fetch(server, interval="1D", bars=5, session="regular"), timeout=20)
    assert _resolve_spec(server) == '={"adjustment":"splits","symbol":"X:Y","session":"regular"}'


async def test_default_resolve_spec_is_byte_identical_to_earlier_releases():
    # `session=None` must not change the wire request: a series someone has been
    # fetching since 0.1.0 has to keep coming back the same.
    server = FakeChartServer(history=5)
    await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)
    assert _resolve_spec(server) == '={"adjustment":"splits","symbol":"X:Y"}'


# --- BarStream over the same fake chart session -----------------------------

async def test_bar_stream_handshake_updates_and_close():
    # BarStream shares its supervisor with QuoteStream, so exercise the chart-session
    # handshake and message routing end to end over the shared plumbing.
    server = FakeChartServer(history=3, per_round=3)
    url = await server.start()
    try:
        started = None
        async with BarStream(url=url) as stream:
            await stream.subscribe("X:Y", "1D")
            async with asyncio.timeout(5):
                async for update in stream.updates():
                    assert update.symbol == "X:Y"
                    assert update.interval == "1D"
                    assert update.bar.time == NEWEST     # seeded with the newest bar only
                    break
            assert stream.snapshot("X:Y", "1D") is not None
            started = time.monotonic()
        assert time.monotonic() - started < 2.0          # no recv-watchdog stall on exit
    finally:
        await server.stop()

    methods = [m["m"] for m in server.received]
    assert methods[:2] == ["set_auth_token", "chart_create_session"]
    assert "create_series" in methods


async def test_end_without_start_pages_back_to_fill_the_count():
    # Bars newer than `end` are discarded by the filter, so they must not satisfy the
    # count target — otherwise the call returns far fewer bars than asked for, or none.
    server = FakeChartServer(history=60, per_round=5)
    end = NEWEST - 20 * BAR_SECONDS
    result = await asyncio.wait_for(_fetch(server, interval="1D", bars=5, end=end), timeout=20)
    assert len(result) == 5
    assert all(b.time <= end for b in result)
    assert result.bars[-1].time == end
