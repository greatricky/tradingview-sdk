"""Streaming OHLCV bar websocket client (BarStream).

Like :class:`~tradingview_sdk.ws.QuoteStream`, but over *chart* sessions: each
``subscribe(symbol, interval)`` gets its own chart session carrying one series
(TradingView caps a chart session at a single series), all multiplexed over one
websocket and routed back by chart-session id. The server sends the initial
history (``timescale_update``) and then live ``du`` updates for the forming bar.
Each emitted :class:`~tradingview_sdk.models.BarUpdate` carries ``closed`` — True
once a newer bar has started, False while the bar is still forming.

The connection supervisor, reconnect backoff and consumer fan-out are shared
with :class:`~tradingview_sdk.ws.QuoteStream` via
:class:`~tradingview_sdk._stream._StreamBase`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from ._chart import SERIES_ID, create_series_params, parse_series_bars, resolve_symbol_params
from ._protocol import WS_URL, generate_session_id
from ._stream import _StreamBase
from .auth import Credentials
from .models import Bar, BarUpdate

DEFAULT_STREAM_BARS = 300  # history requested when a series is created

Key = tuple[str, str]  # (symbol, interval)


@dataclass(slots=True)
class _Series:
    symbol: str
    interval: str
    bars: int
    chart_session: str = ""      # assigned each time the series is (re)created
    last_time: int | None = field(default=None)
    last_bar: Bar | None = field(default=None)


class BarStream(_StreamBase[BarUpdate]):
    """Realtime/delayed OHLCV bar streaming with dynamic subscribe/unsubscribe.

    Usage::

        async with BarStream() as stream:
            await stream.subscribe("BINANCE:BTCUSDT", "5")
            async for update in stream.updates():
                print(update.symbol, update.interval, update.bar.close, update.closed)
    """

    _task_name = "tv-bar-supervisor"
    _closed_message = "BarStream is closed"

    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        reconnect: bool = True,
        url: str = WS_URL,
    ):
        super().__init__(credentials=credentials, reconnect=reconnect, url=url)
        self._desired: dict[Key, _Series] = {}
        self._by_session: dict[str, _Series] = {}

    # ------------------------------------------------------------------ API

    async def subscribe(self, symbol: str, interval: str = "1D", *, bars: int = DEFAULT_STREAM_BARS) -> None:
        """Add a (symbol, interval) series to the stream."""
        key: Key = (symbol, str(interval))
        if key in self._desired:
            return
        series = _Series(symbol=symbol, interval=str(interval), bars=bars)
        self._desired[key] = series
        if self._ws is not None:
            await self._create_series(series)

    async def unsubscribe(self, symbol: str, interval: str = "1D") -> None:
        """Remove a (symbol, interval) series from the stream."""
        key: Key = (symbol, str(interval))
        series = self._desired.pop(key, None)
        if series is None:
            return
        session = series.chart_session
        self._by_session.pop(session, None)
        if self._ws is not None and session:
            await self._send("chart_delete_session", [session])

    @property
    def subscriptions(self) -> frozenset[Key]:
        return frozenset(self._desired)

    def snapshot(self, symbol: str, interval: str = "1D") -> Bar | None:
        """Latest known bar for a subscribed (symbol, interval)."""
        series = self._desired.get((symbol, str(interval)))
        return series.last_bar if series is not None else None

    # ------------------------------------------------------------- protocol

    async def _handshake(self, token: str) -> None:
        self._by_session.clear()  # sessions from a previous connection are gone
        await self._send("set_auth_token", [token])
        for series in list(self._desired.values()):
            await self._create_series(series)

    async def _create_series(self, series: _Series) -> None:
        """Give the series its own chart session — TradingView allows one series per session."""
        self._by_session.pop(series.chart_session, None)
        chart_session = generate_session_id("cs")
        series.chart_session = chart_session
        self._by_session[chart_session] = series
        await self._send("chart_create_session", [chart_session, ""])
        await self._send("switch_timezone", [chart_session, "Etc/UTC"])
        await self._send("resolve_symbol", resolve_symbol_params(chart_session, series.symbol))
        await self._send("create_series", create_series_params(chart_session, series.interval, series.bars))

    def _handle_data(self, method: str | None, params: list[Any]) -> None:
        if method in ("timescale_update", "du"):
            self._route_bars(params, historical=(method == "timescale_update"))

    def _route_bars(self, params: list[Any], *, historical: bool) -> None:
        if len(params) < 2 or not isinstance(params[1], dict):
            return
        series = self._by_session.get(params[0])  # params[0] is the chart session id
        if series is None:
            return
        self._ingest(series, parse_series_bars(params, SERIES_ID), historical=historical)

    def _ingest(self, series: _Series, bars: list[Bar], *, historical: bool) -> None:
        if not bars:
            return
        # First data for this series: seed with the newest bar only (avoids replaying
        # the whole history as events, both on initial load and after a reconnect).
        if series.last_time is None:
            newest = max(bars, key=lambda b: b.time)
            series.last_time = newest.time
            series.last_bar = newest
            self._emit(series, newest, closed=False)
            return
        for bar in sorted(bars, key=lambda b: b.time):
            last = series.last_time
            if bar.time < last:
                if not historical:  # a live correction to an older, finalized bar
                    self._emit(series, bar, closed=True)
                continue  # replayed history — ignore
            if bar.time > last:
                if series.last_bar is not None:
                    self._emit(series, series.last_bar, closed=True)  # prior bar just closed
                series.last_time = bar.time
                series.last_bar = bar
                self._emit(series, bar, closed=False)
            else:  # same period — the forming bar updated
                series.last_bar = bar
                self._emit(series, bar, closed=False)

    def _emit(self, series: _Series, bar: Bar, *, closed: bool) -> None:
        self._dispatch(
            BarUpdate(
                symbol=series.symbol,
                interval=series.interval,
                bar=bar,
                closed=closed,
                received_at=time.monotonic(),
            )
        )
