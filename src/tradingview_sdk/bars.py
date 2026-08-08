"""Historical OHLCV bars via a one-shot TradingView chart session."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any

import websockets

from ._chart import (
    SERIES_ID,
    create_series_params,
    parse_timescale_update,
    request_more_data_params,
    resolve_symbol_params,
    symbol_currency,
)
from ._http import BASE_HEADERS
from ._protocol import (
    WS_ORIGIN,
    WS_URL,
    decode_frame,
    encode_message,
    generate_session_id,
    is_heartbeat,
    parse_json_message,
    wrap_raw,
)
from .auth import AuthTokenCache, resolve_ws_token
from .errors import ProtocolError, SymbolNotFoundError
from .models import Bar, BarSet

logger = logging.getLogger("tradingview_sdk.bars")

DEFAULT_BARS = 300
_PER_REQUEST = 5000     # bars asked for per create_series / request_more_data round
_MAX_ROUNDS = 20        # safety cap on request_more_data pagination
_RECV_TIMEOUT = 20.0    # watchdog: no inbound frame for this long => give up


class Interval(StrEnum):
    """Common chart resolutions. Any raw TradingView resolution string also works."""

    MIN_1 = "1"
    MIN_3 = "3"
    MIN_5 = "5"
    MIN_15 = "15"
    MIN_30 = "30"
    MIN_45 = "45"
    HOUR_1 = "60"
    HOUR_2 = "120"
    HOUR_3 = "180"
    HOUR_4 = "240"
    DAY = "1D"
    WEEK = "1W"
    MONTH = "1M"


class Adjustment(StrEnum):
    """Historical price adjustment, mirroring TradingView's single chart "ADJ" toggle.

    - ``Adjustment.SPLITS`` -> split-adjusted only (dividends left in). The default;
      splits are always applied and cannot be turned off.
    - ``Adjustment.DIVIDENDS`` -> split-adjusted *and* dividend-adjusted (the chart's
      "Adjust data for dividends" toggle). Dividend mode is a superset of splits.

    Only past bars are adjusted — the latest bar is identical in both modes.
    """

    SPLITS = "splits"
    DIVIDENDS = "dividends"


def to_epoch(value: datetime | date | int | float | None) -> int | None:
    """Coerce a datetime/date/epoch into epoch seconds (UTC); naive datetimes are UTC."""
    if value is None:
        return None
    if isinstance(value, bool):  # guard: bool is an int subclass
        raise TypeError("start/end must be a datetime, date, or epoch seconds")
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return int(value.timestamp())
    if isinstance(value, date):
        return int(datetime(value.year, value.month, value.day, tzinfo=timezone.utc).timestamp())
    raise TypeError(f"start/end must be a datetime, date, or epoch seconds, not {type(value).__name__}")


@dataclass
class _Load:
    """Everything one chart session accumulates across its load rounds."""

    symbol: str
    collected: dict[int, Bar] = field(default_factory=dict)
    currency: str | None = None


async def fetch_bars(
    *,
    symbol: str,
    interval: str = Interval.DAY,
    bars: int = DEFAULT_BARS,
    start: datetime | date | int | float | None = None,
    end: datetime | date | int | float | None = None,
    adjustment: str | Adjustment = Adjustment.SPLITS,
    auth: AuthTokenCache,
    url: str = WS_URL,
    timeout: float = _RECV_TIMEOUT,
) -> BarSet:
    """Fetch historical OHLCV bars for ``symbol`` over one chart-session websocket.

    ``bars`` is the number of most-recent bars to return. Pass ``start`` (and
    optionally ``end``) to page back until that time is covered; ``start`` then
    takes precedence over the ``bars`` count. Times are epoch seconds UTC.
    """
    interval = str(interval)
    adjustment = str(adjustment)
    start_ts = to_epoch(start)
    end_ts = to_epoch(end)
    token = await resolve_ws_token(auth)

    load = _Load(symbol=symbol)
    initial = _PER_REQUEST if start_ts is not None else min(_PER_REQUEST, max(bars, 1))

    async with websockets.connect(
        url,
        additional_headers={"Origin": WS_ORIGIN},
        user_agent_header=BASE_HEADERS["User-Agent"],
        max_size=2**24,
    ) as ws:
        cs = generate_session_id("cs")

        async def send(method: str, params: list[Any]) -> None:
            await ws.send(encode_message(method, params))

        await send("set_auth_token", [token])
        await send("chart_create_session", [cs, ""])
        await send("switch_timezone", [cs, "Etc/UTC"])
        await send("resolve_symbol", resolve_symbol_params(cs, symbol, adjustment=adjustment))
        await send("create_series", create_series_params(cs, interval, initial))

        rounds = 0
        before = -1  # bar count at the previous round; -1 so the first round always counts
        while True:
            if not await _read_until_completed(ws, load, timeout):
                if not load.collected:
                    raise ProtocolError(f"timed out waiting for bars of {symbol!r}")
                logger.warning(
                    "chart session for %r went quiet after %d round(s); returning %d bars",
                    symbol, rounds, len(load.collected),
                )
                break
            if len(load.collected) == before:
                break  # exhausted: the server has nothing older to give

            # A load round finished — decide whether to page further back.
            earliest = min(load.collected) if load.collected else None
            have_enough_count = start_ts is None and len(load.collected) >= bars
            reached_start = start_ts is not None and earliest is not None and earliest <= start_ts
            if have_enough_count or reached_start or rounds >= _MAX_ROUNDS:
                break

            before = len(load.collected)
            await send("request_more_data", request_more_data_params(cs, _PER_REQUEST))
            rounds += 1

    collected = load.collected
    ordered = [collected[t] for t in sorted(collected)]
    if end_ts is not None:
        ordered = [b for b in ordered if b.time <= end_ts]
    if start_ts is not None:
        ordered = [b for b in ordered if b.time >= start_ts]
    elif len(ordered) > bars:
        ordered = ordered[-bars:]

    return BarSet(
        symbol=symbol,
        interval=interval,
        bars=tuple(ordered),
        currency=load.currency,
        raw={"chart_session_rounds": rounds, "bar_count": len(ordered)},
    )


async def _read_until_completed(ws: Any, load: _Load, timeout: float) -> bool:
    """Read frames into ``load`` until the server finishes the current load round.

    Returns True on ``series_completed``, False if the connection closed or went
    quiet first. Both the initial ``create_series`` load and every
    ``request_more_data`` round go through here, so a completion event can never
    be consumed by one loop while another is still waiting for it.
    """
    while True:
        try:
            async with asyncio.timeout(timeout):
                frame = await ws.recv()
        except (TimeoutError, websockets.ConnectionClosed):
            return False

        completed = False
        for message in decode_frame(frame):
            if is_heartbeat(message):
                await ws.send(wrap_raw(message))
                continue
            data = parse_json_message(message)
            if data is None:
                continue
            method = data.get("m")
            params = data.get("p") or []
            if method in ("timescale_update", "du"):
                for bar in parse_timescale_update(params, SERIES_ID):
                    load.collected[bar.time] = bar
            elif method == "symbol_resolved":
                load.currency = load.currency or symbol_currency(params)
            elif method == "series_completed":
                completed = True  # finish the frame first: more bars may follow it
            elif method == "symbol_error":
                raise SymbolNotFoundError(f"TradingView could not resolve symbol {load.symbol!r}")
            elif method in ("series_error", "critical_error", "protocol_error"):
                raise ProtocolError(
                    f"TradingView sent {method} for {load.symbol!r}: {str(params)[:200]}"
                )
        if completed:
            return True
