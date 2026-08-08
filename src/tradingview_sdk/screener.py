"""Screener query builder and stock/ETF presets (scanner /{market}/scan)."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field, replace
from typing import Any, Sequence

from ._http import RequestSpec
from .errors import ParseError
from .models import ScreenerResult, ScreenerRow

SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"


@dataclass(frozen=True)
class Filter:
    """One screener filter expression, e.g. ``Filter.gt("market_cap_basic", 1e9)``."""

    left: str
    operation: str
    right: Any = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"left": self.left, "operation": self.operation}
        if self.right is not None:
            d["right"] = self.right
        return d

    # -- convenience constructors ------------------------------------------
    @classmethod
    def gt(cls, column: str, value: Any) -> "Filter":
        return cls(column, "greater", value)

    @classmethod
    def gte(cls, column: str, value: Any) -> "Filter":
        return cls(column, "egreater", value)

    @classmethod
    def lt(cls, column: str, value: Any) -> "Filter":
        return cls(column, "less", value)

    @classmethod
    def lte(cls, column: str, value: Any) -> "Filter":
        return cls(column, "eless", value)

    @classmethod
    def eq(cls, column: str, value: Any) -> "Filter":
        return cls(column, "equal", value)

    @classmethod
    def ne(cls, column: str, value: Any) -> "Filter":
        return cls(column, "nequal", value)

    @classmethod
    def between(cls, column: str, low: Any, high: Any) -> "Filter":
        return cls(column, "in_range", [low, high])

    @classmethod
    def in_(cls, column: str, values: Sequence[Any]) -> "Filter":
        return cls(column, "in_range", list(values))

    @classmethod
    def has(cls, column: str, values: Sequence[str]) -> "Filter":
        """Array column contains any of the values (e.g. typespecs has ["etf"])."""
        return cls(column, "has", list(values))

    @classmethod
    def has_none_of(cls, column: str, values: Sequence[str]) -> "Filter":
        return cls(column, "has_none_of", list(values))

    @classmethod
    def match(cls, column: str, pattern: str) -> "Filter":
        return cls(column, "match", pattern)


DEFAULT_STOCK_COLUMNS: tuple[str, ...] = (
    "name",
    "description",
    "type",
    "typespecs",
    "close",
    "currency",
    "change",
    "volume",
    "relative_volume_10d_calc",
    "market_cap_basic",
    "price_earnings_ttm",
    "earnings_per_share_diluted_ttm",
    "dividends_yield_current",
    "sector",
    "recommendation_mark",
    "exchange",
)

DEFAULT_ETF_COLUMNS: tuple[str, ...] = (
    "name",
    "description",
    "type",
    "typespecs",
    "close",
    "currency",
    "change",
    "volume",
    "relative_volume_10d_calc",
    "aum",
    "fund_flows.1M",
    "expense_ratio",
    "asset_class.tr",
    "focus.tr",
    "nav_total_return.5Y",
    "exchange",
)

# filter2 tree used by the web stock screener: common/preferred stocks, DRs,
# and closed-end funds (funds that are not ETFs).
_STOCK_FILTER2: dict[str, Any] = {
    "operator": "and",
    "operands": [
        {
            "operation": {
                "operator": "or",
                "operands": [
                    {
                        "operation": {
                            "operator": "and",
                            "operands": [
                                {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}},
                            ],
                        }
                    },
                    {
                        "operation": {
                            "operator": "and",
                            "operands": [
                                {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}},
                            ],
                        }
                    },
                    {
                        "operation": {
                            "operator": "and",
                            "operands": [
                                {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                            ],
                        }
                    },
                    {
                        "operation": {
                            "operator": "and",
                            "operands": [
                                {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}},
                            ],
                        }
                    },
                ],
            }
        }
    ],
}


@dataclass(frozen=True)
class ScreenerQuery:
    """Immutable fluent builder mirroring the scanner POST body.

    Example::

        q = (ScreenerQuery()
             .where(Filter.gt("market_cap_basic", 1e10), Filter.gt("volume", 1e6))
             .select("name", "close", "change", "market_cap_basic")
             .order_by("market_cap_basic")
             .limit(50))
    """

    market_name: str = "america"
    filters: tuple[Filter, ...] = ()
    filter2: dict[str, Any] | None = None
    columns: tuple[str, ...] = DEFAULT_STOCK_COLUMNS
    sort_by: str = "market_cap_basic"
    sort_desc: bool = True
    start: int = 0
    count: int = 50
    label_product: str | None = "screener-stock"

    def where(self, *filters: Filter) -> "ScreenerQuery":
        return replace(self, filters=self.filters + filters)

    def select(self, *columns: str) -> "ScreenerQuery":
        return replace(self, columns=tuple(columns))

    def order_by(self, column: str, *, desc: bool = True) -> "ScreenerQuery":
        return replace(self, sort_by=column, sort_desc=desc)

    def limit(self, n: int) -> "ScreenerQuery":
        return replace(self, count=n)

    def offset(self, n: int) -> "ScreenerQuery":
        return replace(self, start=n)

    def market(self, market: str) -> "ScreenerQuery":
        """Target market, e.g. "america", "germany", "crypto", "forex"."""
        return replace(self, market_name=market)

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "columns": list(self.columns),
            "filter": [f.to_dict() for f in self.filters],
            "ignore_unknown_fields": False,
            "options": {"lang": "en"},
            "range": [self.start, self.start + self.count],
            "sort": {"sortBy": self.sort_by, "sortOrder": "desc" if self.sort_desc else "asc"},
            "symbols": {},
            "markets": [self.market_name],
        }
        if self.filter2 is not None:
            payload["filter2"] = copy.deepcopy(self.filter2)
        return payload


STOCK_SCREENER_DEFAULT = ScreenerQuery(
    filters=(Filter.eq("is_primary", True), Filter.eq("active_symbol", True)),
    filter2=_STOCK_FILTER2,
    columns=DEFAULT_STOCK_COLUMNS,
    sort_by="market_cap_basic",
    label_product="screener-stock",
)

ETF_SCREENER_DEFAULT = ScreenerQuery(
    filters=(Filter.has("typespecs", ["etf"]),),
    columns=DEFAULT_ETF_COLUMNS,
    sort_by="aum",
    label_product="screener-etf",
)


def build_screener_request(query: ScreenerQuery) -> RequestSpec:
    params = {"label-product": query.label_product} if query.label_product else None
    return RequestSpec(
        "POST",
        SCANNER_URL.format(market=query.market_name),
        params=params,
        json_body=query.to_payload(),
    )


def parse_screener_response(query: ScreenerQuery, data: Any) -> ScreenerResult:
    if not isinstance(data, dict) or "data" not in data:
        raise ParseError(f"Unexpected screener response shape: {str(data)[:200]}")
    columns = query.columns
    rows: list[ScreenerRow] = []
    for item in data["data"] or []:
        if not isinstance(item, dict) or "s" not in item:
            raise ParseError(f"Unexpected screener row shape: {str(item)[:200]}")
        values = item.get("d")
        if not isinstance(values, list):
            raise ParseError(f"Screener row {item['s']!r} carries no column data: {str(item)[:200]}")
        # zip() would silently truncate here, so a short row must fail at parse time
        # rather than as a surprise KeyError on the missing column at the call site.
        if len(values) < len(columns):
            raise ParseError(
                f"Screener returned {len(values)} values for {len(columns)} requested columns "
                f"on {item['s']!r}; this market may not support all of them."
            )
        rows.append(ScreenerRow(symbol=item["s"], columns=dict(zip(columns, values)), raw=values))
    return ScreenerResult(total_count=int(data.get("totalCount", len(rows))), rows=rows, columns=columns)
