"""Typed return models. Every model keeps ``raw`` for forward compatibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True, slots=True)
class SymbolInfo:
    """One result from symbol search."""

    symbol: str          # ticker, e.g. "AAPL"
    exchange: str        # e.g. "NASDAQ"
    description: str
    type: str            # "stock" | "fund" | "dr" | ...
    typespecs: tuple[str, ...]
    currency: str | None
    country: str | None
    isin: str | None
    cusip: str | None
    prefix: str | None = None    # routing prefix, when it differs from `exchange`
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    @property
    def full_symbol(self) -> str:
        """EXCHANGE:TICKER form used by every other endpoint.

        Some listings are displayed under one exchange but addressed under
        another — BYMA's CEDEARs, for instance, are routed as ``BCBA:AAPL``.
        Search returns that routing name in ``prefix``, which wins when present.
        """
        return f"{self.prefix or self.exchange}:{self.symbol}"


@dataclass(frozen=True, slots=True)
class Quote:
    """Latest quote snapshot for one instrument."""

    symbol: str          # "NASDAQ:AAPL"
    fields: dict[str, Any] = field(repr=False, default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self.fields[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.fields.get(key, default)

    @property
    def last(self) -> float | None:
        return self.fields.get("close")

    @property
    def change(self) -> float | None:
        return self.fields.get("change")

    @property
    def volume(self) -> float | None:
        return self.fields.get("volume")


@dataclass(frozen=True, slots=True)
class ScreenerRow:
    symbol: str                       # "NASDAQ:NVDA"
    columns: dict[str, Any]           # column name -> value
    raw: list[Any] = field(repr=False, default_factory=list)

    def __getitem__(self, key: str) -> Any:
        return self.columns[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.columns.get(key, default)


@dataclass(frozen=True, slots=True)
class ScreenerResult:
    total_count: int
    rows: list[ScreenerRow]
    columns: tuple[str, ...]

    def __iter__(self):
        return iter(self.rows)

    def __len__(self) -> int:
        return len(self.rows)


@dataclass(frozen=True, slots=True)
class StrategyCard:
    """One entry in the community scripts listing."""

    slug: str            # "eUCT3oSF-WW-Pro-Flow-Zones-Miracle-V4"
    title: str
    url: str             # absolute URL
    author: str | None
    likes: int | None
    script_id_part: str | None    # "PUB;<hex>" when exposed by the listing
    script_type: str | None       # "strategy" | "indicator" | "library"
    symbol: str | None            # e.g. "AMEX:SPY" — symbol of the published chart
    created_at: str | None
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class StrategyPage:
    cards: list[StrategyCard]
    page: int
    has_next: bool

    def __iter__(self):
        return iter(self.cards)

    def __len__(self) -> int:
        return len(self.cards)


@dataclass(frozen=True, slots=True)
class StrategyStats:
    """Performance stats for one trade group ("all", "long", or "short")."""

    net_profit: float | None
    net_profit_percent: float | None
    gross_profit: float | None
    gross_loss: float | None
    percent_profitable: float | None
    profit_factor: float | None
    total_trades: int | None
    winning_trades: int | None
    losing_trades: int | None
    avg_trade: float | None
    commission_paid: float | None
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class StrategyReport:
    """The published strategy report (backtest results) shown on a script page."""

    currency: str | None
    date_range: dict[str, Any]        # {"backtest": {from,to}, "trade": {from,to}} (ms epochs)
    all: StrategyStats | None         # all trades
    long: StrategyStats | None        # long trades only
    short: StrategyStats | None       # short trades only
    max_drawdown: float | None
    max_drawdown_percent: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    open_pl: float | None
    buy_hold_return: float | None
    buy_hold_curve: list[float] = field(repr=False, default_factory=list)
    trades: list[dict[str, Any]] = field(repr=False, default_factory=list)
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class PineSource:
    script_id: str        # "PUB;..."
    name: str
    kind: str | None      # "strategy" | "study"
    version: str | None
    access: str | None    # e.g. "open_no_auth"
    source_text: str
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class Strategy:
    """Full detail for one published script/strategy."""

    slug: str
    url: str
    title: str
    author: str | None
    script_id_part: str | None    # "PUB;<hex>" — used for pine-facade
    version: str | None
    chart_symbol: str | None      # symbol the published chart/report was run on
    chart_interval: str | None
    likes: int | None
    is_strategy: bool
    report: StrategyReport | None
    source: PineSource | None
    raw: dict[str, Any] = field(repr=False, default_factory=dict)


@dataclass(frozen=True, slots=True)
class QuoteUpdate:
    """One incremental websocket quote update."""

    symbol: str
    changes: dict[str, Any]       # fields present in this update only
    snapshot: dict[str, Any]      # merged view of all fields seen so far
    received_at: float            # time.monotonic() of receipt

    @property
    def last_price(self) -> float | None:
        return self.snapshot.get("lp")


@dataclass(frozen=True, slots=True)
class Bar:
    """One OHLCV candle. ``time`` is the bar's open time (epoch seconds, UTC)."""

    time: int            # epoch seconds (UTC) of the bar open
    open: float
    high: float
    low: float
    close: float
    volume: float | None
    raw: list[Any] = field(repr=False, default_factory=list)

    @property
    def datetime(self) -> datetime:
        """Bar open time as a timezone-aware UTC ``datetime``."""
        return datetime.fromtimestamp(self.time, tz=timezone.utc)


@dataclass(frozen=True, slots=True)
class BarSet:
    """Historical OHLCV bars for one instrument, oldest first."""

    symbol: str                       # "SP:SPX"
    interval: str                     # resolution, e.g. "1D", "60"
    bars: tuple[Bar, ...]
    currency: str | None = None
    raw: dict[str, Any] = field(repr=False, default_factory=dict)

    def __iter__(self):
        return iter(self.bars)

    def __len__(self) -> int:
        return len(self.bars)

    def __getitem__(self, index):
        return self.bars[index]

    @property
    def last(self) -> Bar | None:
        return self.bars[-1] if self.bars else None

    @property
    def times(self) -> tuple[int, ...]:
        return tuple(b.time for b in self.bars)

    @property
    def opens(self) -> tuple[float, ...]:
        return tuple(b.open for b in self.bars)

    @property
    def highs(self) -> tuple[float, ...]:
        return tuple(b.high for b in self.bars)

    @property
    def lows(self) -> tuple[float, ...]:
        return tuple(b.low for b in self.bars)

    @property
    def closes(self) -> tuple[float, ...]:
        return tuple(b.close for b in self.bars)

    @property
    def volumes(self) -> tuple[float | None, ...]:
        return tuple(b.volume for b in self.bars)

    def to_dataframe(self):
        """Return the bars as a pandas ``DataFrame`` indexed by UTC timestamp.

        Requires pandas, imported lazily so it stays an optional dependency.
        """
        try:
            import pandas as pd
        except ModuleNotFoundError as exc:  # pragma: no cover - optional dep
            raise ImportError(
                "BarSet.to_dataframe() requires pandas; install it with `pip install pandas`."
            ) from exc
        frame = pd.DataFrame(
            {
                "open": self.opens,
                "high": self.highs,
                "low": self.lows,
                "close": self.closes,
                "volume": self.volumes,
            },
            index=pd.to_datetime(self.times, unit="s", utc=True),
        )
        frame.index.name = "time"
        return frame


@dataclass(frozen=True, slots=True)
class BarUpdate:
    """One incremental websocket bar update from :class:`~tradingview_sdk.bar_stream.BarStream`."""

    symbol: str
    interval: str
    bar: Bar
    closed: bool          # True once a newer bar has started; False for the still-forming bar
    received_at: float    # time.monotonic() of receipt
