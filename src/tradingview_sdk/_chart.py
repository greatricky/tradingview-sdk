"""Pure helpers for TradingView's chart-session protocol (bars/OHLCV).

The chart session layers on the same ``~m~``-framed transport as quotes
(``_protocol.py``): after ``chart_create_session`` you ``resolve_symbol`` and
``create_series``; the server answers with ``timescale_update`` (the bars) and
``series_completed``, then streams ``du`` updates for the forming bar. These
functions build the outgoing message params and parse the incoming payloads,
kept socket-free so they are unit-testable — mirroring the ``build_*``/``parse_*``
split used by ``quotes.py`` and ``screener.py``.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .models import Bar

logger = logging.getLogger("tradingview_sdk.chart")

SYMBOL_ID = "sds_sym_1"
SERIES_ID = "sds_1"
SERIES_LABEL = "s1"


def symbol_spec(symbol: str, *, adjustment: str = "splits", session: str | None = None) -> str:
    """Build the ``resolve_symbol`` spec string, e.g. ``={"adjustment":"splits","symbol":"SP:SPX"}``.

    ``adjustment`` mirrors TradingView's chart setting: ``"splits"`` (the default —
    adjust for splits only) or ``"dividends"`` (the chart's "Adjust data for
    dividends" / ADJ toggle, which back-adjusts historical prices for dividends).
    """
    spec: dict[str, str] = {"adjustment": str(adjustment), "symbol": symbol}
    if session:
        spec["session"] = session
    return "=" + json.dumps(spec, separators=(",", ":"))


def resolve_symbol_params(
    chart_session: str,
    symbol: str,
    *,
    adjustment: str = "splits",
    session: str | None = None,
    symbol_id: str = SYMBOL_ID,
) -> list[Any]:
    return [chart_session, symbol_id, symbol_spec(symbol, adjustment=adjustment, session=session)]


def create_series_params(
    chart_session: str,
    interval: str,
    count: int,
    *,
    series_id: str = SERIES_ID,
    symbol_id: str = SYMBOL_ID,
) -> list[Any]:
    return [chart_session, series_id, SERIES_LABEL, symbol_id, str(interval), int(count), ""]


def request_more_data_params(chart_session: str, count: int, *, series_id: str = SERIES_ID) -> list[Any]:
    return [chart_session, series_id, int(count)]


def _bar_from_values(values: list[Any]) -> Bar | None:
    """Turn one ``{"v": [time, open, high, low, close, volume]}`` array into a :class:`Bar`.

    Returns None for an unusable point rather than raising. Every point observed in
    production has been fully numeric, so this is defensive: were that to change, one
    bad point must not fail a whole ``get_bars`` call or — worse — tear down a
    :class:`~tradingview_sdk.bar_stream.BarStream` connection and reconnect on every
    replay of it. ``parse_series_bars`` logs whatever it drops.
    """
    if not isinstance(values, list) or len(values) < 5:
        return None
    try:
        return Bar(
            time=int(values[0]),
            open=float(values[1]),
            high=float(values[2]),
            low=float(values[3]),
            close=float(values[4]),
            volume=float(values[5]) if len(values) > 5 and values[5] is not None else None,
            raw=list(values),
        )
    except (TypeError, ValueError):
        return None


def parse_series_bars(params: list[Any], series_id: str = SERIES_ID) -> list[Bar]:
    """Extract bars from a ``timescale_update`` or ``du`` message's ``p`` list.

    Both messages carry ``[chart_session, {series_id: {"s": [{"i": idx, "v": [...]}, ...]}}]``.
    Returns the bars in the order the server sent them (ascending by time).
    """
    if len(params) < 2 or not isinstance(params[1], dict):
        return []
    series = params[1].get(series_id)
    if not isinstance(series, dict):
        return []
    bars: list[Bar] = []
    skipped = 0
    for point in series.get("s") or []:
        if not isinstance(point, dict):
            skipped += 1
            continue
        bar = _bar_from_values(point.get("v"))
        if bar is None:
            skipped += 1
        else:
            bars.append(bar)
    if skipped:
        # Never seen in practice; a burst of these means the payload shape moved.
        logger.warning("skipped %d unparseable bar point(s) of %d", skipped, skipped + len(bars))
    return bars


# ``timescale_update`` (initial/history load) and ``du`` (live updates) share a shape.
parse_timescale_update = parse_series_bars
parse_du = parse_series_bars


def symbol_info(params: list[Any]) -> dict[str, Any]:
    """The instrument description a ``symbol_resolved`` message carries, or ``{}``.

    ``p`` is ``[chart_session, symbol_id, {...}]``; the dict is the server's own
    account of the symbol — currency, ``timezone`` (the exchange zone its bar
    stamps are in), ``session`` (the trading-hours string, e.g. ``"0930-1600"``),
    type, description and more. Returned whole so callers can read fields this
    client does not model.
    """
    if not isinstance(params, list) or len(params) < 3 or not isinstance(params[2], dict):
        return {}
    return params[2]


def symbol_currency(params: list[Any]) -> str | None:
    """Best-effort currency code from a ``symbol_resolved`` message's ``p`` list."""
    meta = symbol_info(params)
    return meta.get("currency_code") or meta.get("currency-id") or meta.get("currency_id")
