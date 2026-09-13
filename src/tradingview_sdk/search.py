"""Symbol search (instrument information) — pure spec + parser."""

from __future__ import annotations

import re
from typing import Any

from ._http import RequestSpec
from .errors import ParseError
from .models import SymbolInfo

SEARCH_URL = "https://symbol-search.tradingview.com/symbol_search/v3/"

_EM_TAG_RE = re.compile(r"</?em>")


def build_search_request(
    text: str,
    *,
    search_type: str | None = "stocks",
    exchange: str = "",
    country: str = "US",
    lang: str = "en",
) -> RequestSpec:
    params: dict[str, Any] = {
        "text": text,
        "hl": 0,
        "exchange": exchange,
        "lang": lang,
        "domain": "production",
        "sort_by_country": country,
    }
    if search_type:
        params["search_type"] = search_type
    return RequestSpec("GET", SEARCH_URL, params=params)


def pick_full_symbol(matches: list[SymbolInfo], text: str) -> str | None:
    """The ``EXCHANGE:TICKER`` a bare ``text`` should mean, given its search results.

    An exact ticker match wins over the first result. Futures are listed under
    their root — searching ``ES1!`` returns ``CME:ES`` with the continuous and
    dated contracts in ``raw["contracts"]`` (measured 2026-09-13) — and the root is
    not a chartable symbol, so a contract whose ticker matches is looked for too,
    routed by its own ``prefix`` (``CME_MINI:ES1!``) when it carries one.
    """
    wanted = text.upper()
    for m in matches:
        if m.symbol.upper() == wanted:
            return m.full_symbol
        for contract in m.raw.get("contracts") or ():
            if not isinstance(contract, dict):
                continue
            ticker = _EM_TAG_RE.sub("", str(contract.get("symbol") or ""))
            if ticker.upper() == wanted:
                route = contract.get("prefix") or contract.get("exchange") or m.prefix or m.exchange
                return f"{route}:{ticker}"
    return matches[0].full_symbol if matches else None


def parse_search_response(data: Any) -> list[SymbolInfo]:
    if not isinstance(data, dict) or "symbols" not in data:
        raise ParseError(f"Unexpected symbol-search response shape: {str(data)[:200]}")
    out: list[SymbolInfo] = []
    for item in data["symbols"]:
        symbol = _EM_TAG_RE.sub("", item.get("symbol", ""))
        out.append(
            SymbolInfo(
                symbol=symbol,
                exchange=item.get("exchange", ""),
                description=item.get("description", ""),
                type=item.get("type", ""),
                typespecs=tuple(item.get("typespecs") or ()),
                currency=item.get("currency_code"),
                country=item.get("country"),
                isin=item.get("isin"),
                cusip=item.get("cusip"),
                prefix=item.get("prefix"),
                raw=item,
            )
        )
    return out
