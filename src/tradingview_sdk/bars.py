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
from .errors import BarTimeoutError, ProtocolError, SymbolNotFoundError
from .models import Bar, BarSet

logger = logging.getLogger("tradingview_sdk.bars")

DEFAULT_BARS = 300
_PER_REQUEST = 5000     # bars asked for per create_series / request_more_data round
_MAX_ROUNDS = 20        # safety cap on request_more_data pagination
_CLOSE_GRACE = 1.0      # seconds spent on the closing handshake before dropping the socket

DEFAULT_BAR_TIMEOUT = 5.0
"""Default silence watchdog for one chart session, in seconds.

This is *not* a total deadline. It bounds the websocket handshake and then each
wait for the next inbound frame, so a server that accepts the connection and then
says nothing costs about this much per attempt (plus :data:`_CLOSE_GRACE` to drop
the socket) instead of hanging. A healthy
server answers ``create_series`` in well under a second and pauses at most a few
hundred milliseconds between frames even mid-pagination, so 5s fires only on a
real stall. It is deliberately tighter than the long-lived streaming client's
watchdog (:data:`~tradingview_sdk._stream.RECV_TIMEOUT`, 30s): that one
reconnects and resumes, while a one-shot fetch just gives up, so waiting longer
buys nothing and callers who try several exchanges per symbol pay it each time.

Each wait covers a whole websocket message rather than idle time alone, because
that is the granularity ``recv()`` offers. A 5000-bar load round arrives as one
~520 KB frame, which needs a link under roughly 1 Mbps to take 5s — so on a
congested or tethered connection a large ``start=`` range may need a bigger
``timeout`` even though the server is healthy.
"""


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
    timeout: float = DEFAULT_BAR_TIMEOUT,
) -> BarSet:
    """Fetch historical OHLCV bars for ``symbol`` over one chart-session websocket.

    ``bars`` is the number of most-recent bars to return. Pass ``start`` (and
    optionally ``end``) to page back until that time is covered; ``start`` then
    takes precedence over the ``bars`` count. Times are epoch seconds UTC.

    ``timeout`` is the silence watchdog in seconds (see
    :data:`DEFAULT_BAR_TIMEOUT`), not a total deadline. If the session stalls
    before any bars arrive this raises :class:`BarTimeoutError`; if it stalls
    after some arrived, the bars collected so far are returned with
    ``raw["truncated"] = True`` rather than thrown away, so check that flag before
    treating a result as a complete answer.
    """
    if timeout is None or timeout <= 0:
        # Reachable from the public get_bars facades: asyncio.timeout(None) would
        # disable the watchdog entirely and <= 0 would fail against a healthy server.
        raise ValueError(f"timeout must be a positive number of seconds, not {timeout!r}")
    interval = str(interval)
    adjustment = str(adjustment)
    start_ts = to_epoch(start)
    end_ts = to_epoch(end)
    token = await resolve_ws_token(auth)

    load = _Load(symbol=symbol)
    initial = _PER_REQUEST if start_ts is not None else min(_PER_REQUEST, max(bars, 1))

    # open_timeout defaults to 10s in websockets, which would outlive a 5s watchdog
    # and surface as a bare TimeoutError; bind both ends of the attempt to `timeout`.
    try:
        ws = await websockets.connect(
            url,
            additional_headers={"Origin": WS_ORIGIN},
            user_agent_header=BASE_HEADERS["User-Agent"],
            max_size=2**24,
            open_timeout=timeout,
            close_timeout=_CLOSE_GRACE,
        )
    except TimeoutError as exc:
        raise BarTimeoutError(f"timed out after {timeout}s connecting to {url}") from exc

    truncated = False
    try:
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
                    raise BarTimeoutError(
                        f"timed out after {timeout}s waiting for bars of {symbol!r}"
                    )
                # Partial data beats none, but the caller must be able to tell: the
                # `start`/`bars` filters below silently hide the shortfall otherwise.
                truncated = True
                logger.warning(
                    "chart session for %r went quiet after %d round(s); returning %d bars",
                    symbol, rounds, len(load.collected),
                )
                break
            if len(load.collected) == before:
                break  # exhausted: the server has nothing older to give

            # A load round finished — decide whether to page further back. Only bars
            # that survive the `end` filter count toward the target, otherwise
            # `bars=300, end=<a year ago>` stops on 300 recent bars and returns none.
            earliest = min(load.collected) if load.collected else None
            usable = (
                len(load.collected)
                if end_ts is None
                else sum(1 for t in load.collected if t <= end_ts)
            )
            have_enough_count = start_ts is None and usable >= bars
            reached_start = start_ts is not None and earliest is not None and earliest <= start_ts
            if have_enough_count or reached_start or rounds >= _MAX_ROUNDS:
                break

            before = len(load.collected)
            await send("request_more_data", request_more_data_params(cs, _PER_REQUEST))
            rounds += 1
    finally:
        await _close_quietly(ws)

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
        raw={
            "chart_session_rounds": rounds,
            "bar_count": len(ordered),
            "truncated": truncated,
        },
    )


async def _close_quietly(ws: Any, grace: float = _CLOSE_GRACE) -> None:
    """Close the socket without letting a stalled peer bill the caller for it.

    A server that went silent mid-session tends to ignore the closing handshake too,
    and websockets then waits out its own ``close_timeout`` — dead time stacked on
    top of the watchdog the caller asked for, which is what made a stall cost 15s
    against a 5s ``timeout``. Give the handshake a short grace, then drop the
    transport; this is a one-shot session that is being torn down regardless.
    """
    try:
        async with asyncio.timeout(grace):
            await ws.close()
    except (TimeoutError, OSError, websockets.WebSocketException):
        pass
    finally:
        transport = getattr(ws, "transport", None)
        if transport is not None:
            transport.abort()


async def _read_until_completed(ws: Any, load: _Load, timeout: float) -> bool:
    """Read frames into ``load`` until the server finishes the current load round.

    Returns True on ``series_completed``, False if the connection closed or went
    quiet first. Both the initial ``create_series`` load and every
    ``request_more_data`` round go through here, so a completion event can never
    be consumed by one loop while another is still waiting for it.

    An unknown symbol — including a real ticker on the wrong exchange — comes back
    as ``symbol_error`` right after ``resolve_symbol`` and raises immediately, so
    callers never wait out the watchdog for it.
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
                # `params` is only guaranteed to be JSON, so index it defensively: a
                # dict-shaped payload would raise KeyError past a bare len() check.
                reason = params[2] if isinstance(params, list) and len(params) > 2 else None
                raise SymbolNotFoundError(
                    f"TradingView could not resolve symbol {load.symbol!r}"
                    + (f": {str(reason)[:200]}" if reason else "")
                )
            elif method in ("series_error", "critical_error", "protocol_error"):
                raise ProtocolError(
                    f"TradingView sent {method} for {load.symbol!r}: {str(params)[:200]}"
                )
        if completed:
            return True
