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
    symbol_info,
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
from .errors import BarTimeoutError, IncompleteBarsError, ProtocolError, SymbolNotFoundError
from .models import Bar, BarSet

logger = logging.getLogger("tradingview_sdk.bars")

DEFAULT_BARS = 300
# Bars asked for per create_series / request_more_data round. A chunk size, not
# a server limit: measured 2026-09-13 over anonymous chart sessions, a single
# 60 000-bar create_series returned every bar the server holds — all 20 005 of
# TVC:SPX (1871-02-01 on), 9 260 of CBOE:VIX, 11 523 of NASDAQ:AAPL — and the
# same at 20 000 for intraday (BINANCE:BTCUSDT "60" and "1"). So the round size
# only trades round trips against frame size: ~104 bytes per bar puts a full
# round near 2 MB, well inside ``max_size`` and about 3.5 Mbps to land within
# the default watchdog, while making every daily series reachable anonymously a
# one-round fetch. It was 5000 (~520 KB, 5 rounds for SPX) through 0.4.0.
_PER_REQUEST = 20_000
_MAX_ROUNDS = 20        # safety cap on request_more_data pagination
_CLOSE_GRACE = 1.0      # seconds spent on the closing handshake before dropping the socket
_DEADLINE_FLOOR = 30.0  # smallest derived total deadline, however tight `timeout` is

DEFAULT_BAR_TIMEOUT = 5.0
"""Default silence watchdog for one chart session, in seconds.

It bounds the websocket handshake and then each wait for the next frame that
carries protocol *progress*, so a server that accepts the connection and then
stops making progress costs about this much per attempt (plus
:data:`_CLOSE_GRACE` to drop the socket) instead of hanging. A healthy
server answers ``create_series`` in well under a second and pauses at most a few
hundred milliseconds between frames even mid-pagination, so 5s fires only on a
real stall. It is deliberately tighter than the long-lived streaming client's
watchdog (:data:`~tradingview_sdk._stream.RECV_TIMEOUT`, 30s): that one
reconnects and resumes, while a one-shot fetch just gives up, so waiting longer
buys nothing and callers who try several exchanges per symbol pay it each time.

Each wait covers a whole websocket message rather than idle time alone, because
that is the granularity ``recv()`` offers. A full :data:`_PER_REQUEST` load round
arrives as one frame of roughly 2 MB, which needs a link under about 3.5 Mbps to
take 5s — so on a congested or tethered connection a deep series or a large
``start=`` range may need a bigger ``timeout`` even though the server is healthy.

Heartbeats deliberately do not count as progress. The server sends them every few
seconds and this client echoes them back to stay connected, so a watchdog re-armed
on *any* inbound frame would never fire against the session it exists to catch:
one that is alive and chatty but has stopped delivering bars. That hole widens
exactly where the paragraph above sends callers — raise ``timeout`` past the
server's heartbeat interval and an all-heartbeat session becomes unbounded.

This is still not a total deadline: it re-arms on every load round, so a server
that keeps making slow progress can outlive any number of windows. That is what
``fetch_bars(deadline=...)`` bounds; see :func:`_default_deadline`.
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


def _default_deadline(timeout: float) -> float:
    """Total wall-clock backstop for one chart session, derived from ``timeout``.

    The watchdog alone cannot bound a session: it re-arms on every scrap of progress,
    so a server that dribbles out one frame just inside each window runs forever
    without ever being "silent". This is the outer bound on that.

    It covers every wait on the server — the token fetch, the handshake, and each
    read — which is the whole of a session in practice. It is not a hard cancel: an
    outbound ``send`` that blocks because the peer has stopped reading its socket
    sits outside it, which needs a peer that heartbeats at us while refusing tens of
    kilobytes back, and is not a shape TradingView produces.

    It is deliberately loose — a backstop against a hang, not a service level. The
    budget is one full watchdog window per pagination round (:data:`_MAX_ROUNDS`),
    which no healthy fetch comes near spending, floored so that a caller who tightens
    ``timeout`` for snappy per-frame failure does not silently also buy a total
    deadline too short for a legitimate multi-round ``start=`` range.
    """
    return max(_DEADLINE_FLOOR, timeout * _MAX_ROUNDS)


class _DeadlineReached(Exception):
    """The total deadline expired mid-session. Internal: never escapes ``fetch_bars``."""


@dataclass
class _Load:
    """Everything one chart session accumulates across its load rounds."""

    symbol: str
    collected: dict[int, Bar] = field(default_factory=dict)
    currency: str | None = None
    resolved: dict[str, Any] = field(default_factory=dict)  # the symbol_resolved reply


async def fetch_bars(
    *,
    symbol: str,
    interval: str = Interval.DAY,
    bars: int = DEFAULT_BARS,
    start: datetime | date | int | float | None = None,
    end: datetime | date | int | float | None = None,
    adjustment: str | Adjustment = Adjustment.SPLITS,
    session: str | None = None,
    auth: AuthTokenCache,
    url: str = WS_URL,
    timeout: float = DEFAULT_BAR_TIMEOUT,
    deadline: float | None = None,
    strict: bool = False,
) -> BarSet:
    """Fetch historical OHLCV bars for ``symbol`` over one chart-session websocket.

    ``bars`` is the number of most-recent bars to return. Pass ``start`` (and
    optionally ``end``) to page back until that time is covered; ``start`` then
    takes precedence over the ``bars`` count. Times are epoch seconds UTC.

    ``session`` names the trading session the bars are built from — ``"regular"``
    or ``"extended"`` — and is sent in the ``resolve_symbol`` spec. ``None`` omits
    it and leaves the choice to the server, which is exactly the request every
    earlier release sent, so existing fetches do not move.

    The reply's ``symbol_resolved`` description is kept: ``BarSet.timezone`` and
    ``BarSet.session`` are the exchange timezone and trading-hours string, and the
    whole dict sits on ``raw["symbol_resolved"]``.

    ``timeout`` is the silence watchdog in seconds (see
    :data:`DEFAULT_BAR_TIMEOUT`), applied to the handshake and then to each wait
    for the next frame that carries progress. ``deadline`` is the total wall clock
    the whole call may spend, defaulting to :func:`_default_deadline` of ``timeout``;
    it is what bounds a server that stays busy without ever finishing.

    Both give up the same way. If the session ends before any bars arrive this
    raises :class:`BarTimeoutError`; if it ends after some arrived, the bars
    collected so far are returned with ``raw["truncated"] = True`` rather than
    thrown away, so check that flag before treating a result as a complete answer.
    ``strict=True`` turns that second case into an :class:`IncompleteBarsError`
    (a ``BarTimeoutError`` carrying the partial set on ``.bars``) — for a caller
    that records what it fetches and must never file a short answer as a whole one.
    The same flag (and error) marks a fetch that spent all :data:`_MAX_ROUNDS`
    pagination rounds without reaching ``start`` or ``bars``.
    """
    if timeout is None or timeout <= 0:
        # Reachable from the public get_bars facades: asyncio.timeout(None) would
        # disable the watchdog entirely and <= 0 would fail against a healthy server.
        raise ValueError(f"timeout must be a positive number of seconds, not {timeout!r}")
    if deadline is None:
        deadline = _default_deadline(timeout)
    elif deadline <= 0:
        # `None` means "derive one", so there is no way to ask for no deadline at all:
        # an unbounded fetch_bars is the bug this argument exists to make unreachable.
        raise ValueError(f"deadline must be a positive number of seconds, not {deadline!r}")
    if isinstance(bars, bool) or not isinstance(bars, int) or bars < 1:
        # bars=0 slipped through as `ordered[-0:]`, which is every bar, and a negative
        # count sliced from the wrong end; neither is a request worth guessing at.
        raise ValueError(f"bars must be a positive integer, not {bars!r}")
    start_ts = to_epoch(start)
    end_ts = to_epoch(end)
    if start_ts is not None and end_ts is not None and end_ts < start_ts:
        # Would silently return an empty set after paging back to `start` in full.
        raise ValueError(f"end ({end!r}) is before start ({start!r})")
    loop = asyncio.get_running_loop()
    # Started before the token fetch so `deadline` means what it says for the caller,
    # rather than only covering the part of the call after the REST round trip.
    expires_at = loop.time() + deadline

    interval = str(interval)
    adjustment = str(adjustment)
    token = await resolve_ws_token(auth)

    load = _Load(symbol=symbol)
    initial = _PER_REQUEST if start_ts is not None else min(_PER_REQUEST, bars)

    # open_timeout defaults to 10s in websockets, which would outlive a 5s watchdog
    # and surface as a bare TimeoutError; bind both ends of the attempt to `timeout`,
    # or to what is left of the deadline when a caller set one tighter than that.
    open_timeout = min(timeout, expires_at - loop.time())
    if open_timeout <= 0:
        raise BarTimeoutError(
            f"deadline of {deadline}s expired before the chart session for {symbol!r} opened"
        )
    try:
        ws = await websockets.connect(
            url,
            additional_headers={"Origin": WS_ORIGIN},
            user_agent_header=BASE_HEADERS["User-Agent"],
            max_size=2**24,
            open_timeout=open_timeout,
            close_timeout=_CLOSE_GRACE,
        )
    except TimeoutError as exc:
        raise BarTimeoutError(f"timed out after {open_timeout:g}s connecting to {url}") from exc

    truncated = False
    try:
        cs = generate_session_id("cs")

        async def send(method: str, params: list[Any]) -> None:
            await ws.send(encode_message(method, params))

        await send("set_auth_token", [token])
        await send("chart_create_session", [cs, ""])
        await send("switch_timezone", [cs, "Etc/UTC"])
        await send(
            "resolve_symbol",
            resolve_symbol_params(cs, symbol, adjustment=adjustment, session=session),
        )
        await send("create_series", create_series_params(cs, interval, initial))

        rounds = 0
        before = -1  # bar count at the previous round; -1 so the first round always counts
        try:
            while True:
                if not await _read_until_completed(ws, load, timeout, expires_at):
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
                reached_start = (
                    start_ts is not None and earliest is not None and earliest <= start_ts
                )
                if have_enough_count or reached_start:
                    break
                if rounds >= _MAX_ROUNDS:
                    # The cap is a guard against runaway pagination, not a result: the
                    # server still had more and the caller's range is not covered, so
                    # this is a shortfall like a stall, and strict mode must see it.
                    truncated = True
                    logger.warning(
                        "chart session for %r hit the %d-round cap before covering its "
                        "range; returning %d bars",
                        symbol, _MAX_ROUNDS, len(load.collected),
                    )
                    break

                before = len(load.collected)
                await send("request_more_data", request_more_data_params(cs, _PER_REQUEST))
                rounds += 1
        except _DeadlineReached:
            # Same bargain as the watchdog above: whatever arrived is worth returning,
            # flagged, and only an empty session is an error.
            if not load.collected:
                raise BarTimeoutError(
                    f"deadline of {deadline}s expired before any bars of {symbol!r} arrived"
                ) from None
            truncated = True
            logger.warning(
                "chart session for %r hit its %ss deadline after %d round(s); returning %d bars",
                symbol, deadline, rounds, len(load.collected),
            )
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

    result = BarSet(
        symbol=symbol,
        interval=interval,
        bars=tuple(ordered),
        currency=load.currency,
        timezone=_optional_str(load.resolved.get("timezone")),
        session=_optional_str(load.resolved.get("session")),
        raw={
            "chart_session_rounds": rounds,
            "bar_count": len(ordered),
            "truncated": truncated,
            "symbol_resolved": load.resolved,
        },
    )
    if truncated and strict:
        # Built first so the error carries exactly what the lenient mode returns.
        raise IncompleteBarsError(
            f"chart session for {symbol!r} ended after {len(ordered)} bar(s) without "
            f"finishing; strict mode refuses a partial answer",
            bars=result,
        )
    return result


def _optional_str(value: Any) -> str | None:
    """A non-empty string from the server's dict, else None — never a stray type."""
    return value if isinstance(value, str) and value else None


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


async def _read_until_completed(
    ws: Any, load: _Load, timeout: float, expires_at: float
) -> bool:
    """Read frames into ``load`` until the server finishes the current load round.

    Returns True on ``series_completed``, False if the connection closed or went
    quiet first, and raises :class:`_DeadlineReached` when the session's total
    ``expires_at`` passes. Both the initial ``create_series`` load and every
    ``request_more_data`` round go through here, so a completion event can never
    be consumed by one loop while another is still waiting for it.

    The watchdog is anchored to the last frame that carried *progress*, not to the
    last frame of any kind. Heartbeats arrive on their own schedule and are echoed
    back, so re-arming on them would let a session that has stopped delivering bars
    outlive ``timeout`` forever whenever the heartbeat interval is the shorter of
    the two — a stall that answers "still here" is precisely what the watchdog is
    for. ``expires_at`` then covers the case the watchdog structurally cannot: real
    progress that never adds up to a finished round.

    An unknown symbol — including a real ticker on the wrong exchange — comes back
    as ``symbol_error`` right after ``resolve_symbol`` and raises immediately, so
    callers never wait out the watchdog for it.
    """
    loop = asyncio.get_running_loop()
    quiet_at = loop.time() + timeout
    while True:
        # Re-checked before every read: a peer that keeps a frame always ready would
        # otherwise starve the timeout below and spin past the deadline.
        if loop.time() >= expires_at:
            raise _DeadlineReached
        # Compared rather than measured after the fact, so the two cannot be confused
        # when they land in the same millisecond.
        deadline_first = expires_at <= quiet_at
        try:
            async with asyncio.timeout_at(min(quiet_at, expires_at)):
                frame = await ws.recv()
        except TimeoutError:
            if deadline_first:
                raise _DeadlineReached from None
            return False
        except websockets.ConnectionClosed:
            return False

        completed = False
        progressed = False
        for message in decode_frame(frame):
            if is_heartbeat(message):
                await ws.send(wrap_raw(message))
                continue
            # Anything that is not a heartbeat is the server doing work, including
            # payloads this client does not parse — the watchdog asks whether the
            # session is advancing, not whether we understood the latest frame.
            progressed = True
            data = parse_json_message(message)
            if data is None:
                continue
            method = data.get("m")
            params = data.get("p") or []
            if method in ("timescale_update", "du"):
                for bar in parse_timescale_update(params, SERIES_ID):
                    load.collected[bar.time] = bar
            elif method == "symbol_resolved":
                # Kept whole: timezone and session decide how a caller may date a
                # bar, and fields this client does not model stay reachable on raw.
                load.resolved = load.resolved or symbol_info(params)
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
        if progressed:
            quiet_at = loop.time() + timeout
