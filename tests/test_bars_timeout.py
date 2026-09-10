"""The get_bars facades' silence watchdog: pass-through, validation, error type."""

import pytest

from tradingview_sdk import AsyncTradingView, BarTimeoutError, ProtocolError, TradingView
from tradingview_sdk import client as client_module
from tradingview_sdk.auth import AuthTokenCache, Credentials
from tradingview_sdk.bars import _CLOSE_GRACE, fetch_bars
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


async def test_connect_timeout_raises_bar_timeout_error():
    # A host that accepts TCP but never completes the websocket handshake must be
    # bounded by `timeout` too, not by websockets' own 10s open_timeout default.
    import asyncio

    server = await asyncio.start_server(lambda r, w: asyncio.sleep(60), "127.0.0.1", 0)
    url = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/socket.io/websocket"
    try:
        loop = asyncio.get_running_loop()
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="connecting"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=0.5
            )
        assert loop.time() - began < 5.0        # not websockets' 10s open_timeout
    finally:
        server.close()
        await server.wait_closed()


async def _stalling_ws_server():
    """Completes the websocket handshake, then never speaks again — including on close."""
    import asyncio
    import base64
    import hashlib

    async def handler(reader, writer):
        request = await reader.readuntil(b"\r\n\r\n")
        key = ""
        for line in request.decode(errors="replace").split("\r\n"):
            if line.lower().startswith("sec-websocket-key:"):
                key = line.split(":", 1)[1].strip()
        digest = hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        writer.write(
            b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
            b"Connection: Upgrade\r\nSec-WebSocket-Accept: "
            + base64.b64encode(digest)
            + b"\r\n\r\n"
        )
        await writer.drain()
        await asyncio.sleep(300)

    return await asyncio.start_server(handler, "127.0.0.1", 0)


async def test_stalled_session_does_not_pay_the_close_handshake_on_top():
    # A server that goes silent mid-session ignores the closing handshake too. websockets
    # would wait out its own close_timeout there, which made a 5s watchdog cost 15s wall
    # clock — most of the stall budget spent after the decision to give up was made.
    import asyncio

    server = await _stalling_ws_server()
    url = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/socket.io/websocket"
    try:
        loop = asyncio.get_running_loop()
        began = loop.time()
        with pytest.raises(BarTimeoutError, match="waiting for bars"):
            await fetch_bars(
                symbol="X:Y", auth=AuthTokenCache(Credentials()), url=url, timeout=1.0
            )
        elapsed = loop.time() - began
    finally:
        server.close()
        await server.wait_closed()
    # The watchdog plus the close grace, nowhere near websockets' 10s close_timeout.
    assert elapsed < 1.0 + _CLOSE_GRACE + 1.0, f"stall cost {elapsed:.1f}s"


def test_bar_timeout_error_stays_catchable_as_protocol_error():
    assert issubclass(BarTimeoutError, ProtocolError)
    assert issubclass(BarTimeoutError, TimeoutError)
