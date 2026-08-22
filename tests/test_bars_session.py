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
from tradingview_sdk.bars import fetch_bars
from tradingview_sdk.errors import ProtocolError, SymbolNotFoundError

BAR_SECONDS = 86_400
NEWEST = 1_700_000_000


class FakeChartServer:
    """Serves ``history`` bars newest-first, one load round per create_series/request_more_data."""

    def __init__(self, *, history: int, per_round: int = 5, symbol_error: bool = False, bad_bar: bool = False):
        self.history = history
        self.per_round = per_round
        self.symbol_error = symbol_error
        self.bad_bar = bad_bar
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
                            await ws.send(wrap_raw(json.dumps(
                                {"m": "symbol_error", "p": [params[0], params[1]]}
                            )))
                            continue
                        await ws.send(wrap_raw(json.dumps(
                            {"m": "symbol_resolved", "p": [params[0], params[1], {"currency_code": "USD"}]}
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


async def test_symbol_error_maps_to_symbol_not_found():
    server = FakeChartServer(history=5, symbol_error=True)
    with pytest.raises(SymbolNotFoundError):
        await asyncio.wait_for(_fetch(server, interval="1D", bars=5), timeout=20)


async def test_silent_server_times_out_with_protocol_error():
    server = FakeChartServer(history=0, per_round=0)
    server._load_round = lambda ws, cs: asyncio.sleep(0)   # never completes a round
    with pytest.raises(ProtocolError, match="timed out"):
        await asyncio.wait_for(_fetch(server, interval="1D", bars=5, timeout=0.3), timeout=20)


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
