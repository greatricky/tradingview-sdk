"""Latest-quote REST endpoint (scanner /symbol) — pure spec + parser."""

from __future__ import annotations

from typing import Any, Sequence

from ._http import RequestSpec
from .errors import ParseError, SymbolNotFoundError
from .models import Quote

QUOTE_URL = "https://scanner.tradingview.com/symbol"

DEFAULT_QUOTE_FIELDS: tuple[str, ...] = (
    "name",
    "description",
    "type",
    "exchange",
    "currency",
    "close",
    "open",
    "high",
    "low",
    "change",
    "change_abs",
    "volume",
    "bid",
    "ask",
    "market_cap_basic",
    "price_earnings_ttm",
    "premarket_close",
    "premarket_change",
    "postmarket_close",
    "postmarket_change",
)


def build_quote_request(symbol: str, fields: Sequence[str] = DEFAULT_QUOTE_FIELDS) -> RequestSpec:
    return RequestSpec(
        "GET",
        QUOTE_URL,
        params={"symbol": symbol, "fields": ",".join(fields), "no_404": "false"},
    )


def parse_quote_response(symbol: str, data: Any) -> Quote:
    if not isinstance(data, dict):
        raise ParseError(f"Unexpected quote response for {symbol}: {str(data)[:200]}")
    if not data or all(v is None for v in data.values()):
        raise SymbolNotFoundError(f"No quote data for symbol {symbol!r}")
    return Quote(symbol=symbol, fields=data)
