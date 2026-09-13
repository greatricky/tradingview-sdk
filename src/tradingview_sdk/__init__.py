"""Unofficial Python SDK for TradingView.

Quotes, symbol search, streaming prices, stock/ETF screeners, and
community strategies (listing, performance reports, Pine source).
"""

from .auth import Credentials
from .client import AsyncTradingView, TradingView
from .fields import (
    FIELDS,
    TIMEFRAMES,
    Field,
    FieldInfo,
    FieldType,
    field_info,
    search_fields,
    with_timeframe,
)
from .errors import (
    AuthRequiredError,
    BarTimeoutError,
    HTTPStatusError,
    IncompleteBarsError,
    ParseError,
    ProtocolError,
    RateLimitError,
    StreamClosedError,
    SymbolNotFoundError,
    TradingViewError,
)
from .models import (
    Bar,
    BarSet,
    BarUpdate,
    PineSource,
    Quote,
    QuoteUpdate,
    ScreenerResult,
    ScreenerRow,
    Strategy,
    StrategyCard,
    StrategyPage,
    StrategyReport,
    StrategyStats,
    SymbolInfo,
)
from .bars import DEFAULT_BAR_TIMEOUT, DEFAULT_BARS, Adjustment, Interval, fetch_bars
from .bar_stream import BarStream
from .quotes import DEFAULT_QUOTE_FIELDS
from .scripts import SCRIPT_TYPES
from .screener import (
    DEFAULT_ETF_COLUMNS,
    DEFAULT_STOCK_COLUMNS,
    ETF_SCREENER_DEFAULT,
    STOCK_SCREENER_DEFAULT,
    Filter,
    ScreenerQuery,
)
from .ws import DEFAULT_WS_FIELDS, QuoteStream

try:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version

    __version__ = _pkg_version("tradingview-sdk")
except PackageNotFoundError:  # pragma: no cover - running from an uninstalled source tree
    __version__ = "0.0.0"

__all__ = [
    "AsyncTradingView",
    "TradingView",
    "QuoteStream",
    "BarStream",
    "Interval",
    "Adjustment",
    "fetch_bars",
    "Credentials",
    "Filter",
    "ScreenerQuery",
    "Field",
    "FieldInfo",
    "FieldType",
    "FIELDS",
    "TIMEFRAMES",
    "field_info",
    "search_fields",
    "with_timeframe",
    "STOCK_SCREENER_DEFAULT",
    "ETF_SCREENER_DEFAULT",
    "DEFAULT_STOCK_COLUMNS",
    "DEFAULT_ETF_COLUMNS",
    "DEFAULT_QUOTE_FIELDS",
    "DEFAULT_WS_FIELDS",
    "DEFAULT_BARS",
    "DEFAULT_BAR_TIMEOUT",
    "SCRIPT_TYPES",
    # models
    "SymbolInfo",
    "Quote",
    "QuoteUpdate",
    "Bar",
    "BarSet",
    "BarUpdate",
    "ScreenerResult",
    "ScreenerRow",
    "StrategyCard",
    "StrategyPage",
    "Strategy",
    "StrategyReport",
    "StrategyStats",
    "PineSource",
    # errors
    "TradingViewError",
    "HTTPStatusError",
    "RateLimitError",
    "AuthRequiredError",
    "SymbolNotFoundError",
    "ParseError",
    "ProtocolError",
    "BarTimeoutError",
    "IncompleteBarsError",
    "StreamClosedError",
]
