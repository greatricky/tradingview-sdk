# tradingview-sdk

Unofficial Python SDK for TradingView's web APIs:

- **Instrument information** — symbol search with exchange, type, ISIN/CUSIP, currency
- **Latest quotes** — one REST call for price, change, volume, bid/ask, fundamentals
- **Streaming prices** — websocket client with dynamic subscribe/unsubscribe of many tickers
- **Historical bars (OHLCV)** — daily/intraday candles over any date range as typed `BarSet`/`Bar` objects (optional pandas `.to_dataframe()`), plus a live bar stream
- **Stock & ETF screeners** — programmatic equivalents of [tradingview.com/screener](https://www.tradingview.com/screener/) and [tradingview.com/etf-screener](https://www.tradingview.com/etf-screener/) with a fluent query builder
- **Community strategies** — list open-source strategies, fetch the published backtest **strategy report** (net profit, profit factor, drawdown, trade list, equity curves) and the full **Pine source code**

> ⚠️ This SDK uses TradingView's private web endpoints, which are undocumented and may change without notice. It is not affiliated with or endorsed by TradingView. Use responsibly and respect their terms of service.

## Install

```bash
uv sync          # from this repo (dev)
# or
pip install .
pip install ".[pandas]"   # adds pandas, for BarSet.to_dataframe()
```

Requires Python 3.11+. Dependencies: `httpx`, `websockets`, `selectolax`. `pandas` is an optional extra — everything works without it except `BarSet.to_dataframe()`, which imports it lazily.

## Quickstart

### Instrument info & quotes (sync)

```python
from tradingview_sdk import TradingView

with TradingView() as tv:
    # 1. Instrument information
    for info in tv.search_symbols("AAPL"):
        print(info.full_symbol, info.type, info.isin, info.description)

    # 2. Latest quote — accepts "NASDAQ:AAPL" or a bare "AAPL"
    quote = tv.get_quote("NASDAQ:AAPL")
    print(quote.last, quote.change, quote.volume, quote["market_cap_basic"])
```

Every method also exists on `AsyncTradingView` with an identical signature:

```python
from tradingview_sdk import AsyncTradingView

async with AsyncTradingView() as tv:
    quote = await tv.get_quote("NASDAQ:AAPL")
```

### Streaming prices (websocket)

```python
import asyncio
from tradingview_sdk import QuoteStream

async def main():
    async with QuoteStream() as stream:
        await stream.subscribe("NASDAQ:AAPL", "BINANCE:BTCUSDT")

        async for update in stream.updates():
            print(update.symbol, update.last_price, update.changes)

            # add/remove tickers at any time, mid-stream
            await stream.unsubscribe("NASDAQ:AAPL")
            await stream.subscribe("NASDAQ:TSLA", "BINANCE:ETHUSDT")

asyncio.run(main())
```

- `stream.updates("NASDAQ:TSLA")` — filtered iterator for specific symbols; multiple concurrent iterators are fine.
- `stream.on_update(callback)` — sync or async callback alternative; returns an unregister function.
- `stream.snapshot("NASDAQ:AAPL")` — latest merged field values.
- Reconnects automatically with exponential backoff and **resubscribes everything** after a drop.

### Historical bars (OHLCV)

```python
from datetime import date, datetime, timezone
from tradingview_sdk import TradingView, Interval

with TradingView() as tv:
    # Index — most-recent N candles (accepts "EXCHANGE:TICKER" or a bare ticker)
    spx = tv.get_bars("SP:SPX", Interval.DAY, bars=300)
    print(spx.symbol, spx.interval, len(spx))
    print(spx.last.close, spx.closes[-5:])

    # Stock — a daily range; a plain date is the natural input here
    # (no time-of-day / tz needed). `start` wins over `bars`, paging back to reach it.
    aapl = tv.get_bars("NASDAQ:AAPL", Interval.DAY, start=date(2026, 1, 1))

    # Crypto — an intraday, timezone-aware window. The tz matters because these
    # bars are intraday, and BTCUSDT trades 24/7 so every hour is populated.
    btc = tv.get_bars("BINANCE:BTCUSDT", "60",   # "60" = 60-minute bars
                      start=datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc),
                      end=datetime(2026, 8, 8, tzinfo=timezone.utc))

    df = btc.to_dataframe()   # optional: pandas DataFrame indexed by UTC time
```

- `bars=N` returns the N most-recent candles; pass `start`/`end` to fetch a range instead — the SDK paginates automatically. Use a timezone-aware `datetime` for intraday precision, or a plain `date` (or epoch seconds) for daily ranges.
- `interval` accepts the `Interval` enum (`Interval.MIN_5`, `Interval.HOUR_1`, `Interval.DAY`, `Interval.WEEK`, …) or any raw TradingView resolution string (`"1"`, `"5"`, `"60"`, `"240"`, `"1D"`, `"1W"`, `"1M"`).
- `adjustment` mirrors TradingView's single chart "ADJ" toggle (plain strings `"splits"`/`"dividends"` work too):
  - `Adjustment.SPLITS` → split-adjusted only (dividends left in) — the default.
  - `Adjustment.DIVIDENDS` → split-adjusted and dividend-adjusted.

  Splits are always applied (there is no split-off mode), and the latest bar is identical either way — only historical bars change.
- Each `Bar` has `time` (epoch seconds, UTC), `open`/`high`/`low`/`close`/`volume`, and a `.datetime` (aware UTC). `BarSet` is iterable/indexable with `.last`, `.closes`, `.times`, … and a lazy `.to_dataframe()` (needs pandas only if you call it). Bar times are always UTC, and a naive `start`/`end` `datetime` is interpreted as UTC.
- Bars load over a websocket chart session; anonymous access returns delayed data (log in for realtime — see [Authentication](#authentication-optional)).

**Streaming bars** — `BarStream` mirrors `QuoteStream` for live, updating candles:

```python
import asyncio
from tradingview_sdk import BarStream

async def main():
    async with BarStream() as stream:
        await stream.subscribe("BINANCE:BTCUSDT", "1")   # 1-minute bars
        async for u in stream.updates():
            print(u.symbol, u.interval, u.bar.close, "closed" if u.closed else "forming")

asyncio.run(main())
```

Each `BarUpdate` carries the latest `bar` and `closed` — `False` while the bar is still forming, `True` once a newer bar has started.

### Screeners

```python
from tradingview_sdk import TradingView, ScreenerQuery, Filter

with TradingView() as tv:
    stocks = tv.screen_stocks()          # defaults mirror the web stock screener
    etfs = tv.screen_etfs()              # defaults mirror the web ETF screener
    print(stocks.total_count, etfs.total_count)

    # Custom query
    query = (
        ScreenerQuery()
        .where(
            Filter.gt("market_cap_basic", 10e9),
            Filter.between("price_earnings_ttm", 0, 15),
            Filter.gt("volume", 2_000_000),
        )
        .select("name", "close", "change", "market_cap_basic", "price_earnings_ttm", "sector")
        .order_by("market_cap_basic")
        .limit(100)
    )
    for row in tv.screen(query):
        print(row.symbol, row["price_earnings_ttm"])
```

Any column/filter field the web screener supports works here. Use `.market("germany")`, `.market("crypto")`, etc. for other markets.

#### Field catalog

All ~1,100 screener fields are available as a typed enum with metadata (generated from TradingView's scanner `metainfo` endpoint — regenerate with `uv run python scripts/generate_fields.py`):

```python
from tradingview_sdk import Field, FIELDS, field_info, search_fields

Field.MARKET_CAP_BASIC              # == "market_cap_basic", usable anywhere a field name goes
Field.RSI.info.description          # "Relative Strength Index (14). Range 0-100; <30 oversold, >70 overbought."
FIELDS["sector"].values             # allowed values: ("Commercial Services", ..., "Utilities")
FIELDS["change"].type               # FieldType.PERCENT  (12.5 means 12.5%)
FIELDS["change"].timeframes         # ("1", "5", "15", "30", "60", "120", "240", "1W", "1M")
Field.CHANGE.tf("60")               # "change|60" — change on the 60-minute chart
search_fields("dividend yield")     # find fields by name/description substring
```

Each `FieldInfo` carries: `name`, `type` (semantics: `percent` = percentage points, `price`/`fundamental_price` = monetary, `time` = UNIX timestamp, `num_slice` = per-period history array), a human-readable `description` (hand-curated for the ~120 most-used fields, auto-derived otherwise), `values` (the allowed values for enumerated text fields like `sector`, `industry`, `exchange`, `type`, `typespecs`), and `timeframes` (fields that exist per chart timeframe via the `"name|tf"` suffix). Some fund classification fields (`asset_class`, `focus`, `niche`, `weighting_scheme`) return internal ids — select the `.tr`-suffixed twin column (e.g. `"asset_class.tr"`) for readable labels.

### Community strategies

```python
from tradingview_sdk import TradingView

with TradingView() as tv:
    # List open-source strategies (paginated; also: tv.iter_strategies())
    page = tv.list_strategies()
    for card in page:
        print(card.title, card.author, card.likes, card.url)

    # Full detail: metadata + published strategy report + Pine source
    s = tv.get_strategy("eUCT3oSF-WW-Pro-Flow-Zones-Miracle-V4")  # slug or full URL
    print(s.title, s.chart_symbol, s.chart_interval)

    r = s.report                      # the "Strategy report" from the script page
    print(r.all.net_profit, r.all.total_trades, r.all.profit_factor)
    print(r.max_drawdown, r.sharpe_ratio, r.sortino_ratio)
    print(r.trades[:2])               # individual trades
    print(r.buy_hold_curve[:5])       # buy & hold equity curve

    print(s.source.source_text)       # full Pine source (open-source scripts)
```

Protected/invite-only scripts raise `AuthRequiredError` for the source; the report and metadata still parse when the page publishes them.

## Authentication (optional)

Everything works anonymously. Logging in upgrades websocket data from delayed to realtime for exchanges you have data entitlements for, per your TradingView account.

Copy the `sessionid` and `sessionid_sign` cookies from a logged-in browser (DevTools → Application → Cookies → tradingview.com), then either:

```bash
export TV_SESSION_ID="..."
export TV_SESSION_ID_SIGN="..."
```

(picked up automatically), or pass explicitly:

```python
from tradingview_sdk import Credentials, QuoteStream, TradingView

creds = Credentials(session_id="...", session_sign="...")
tv = TradingView(credentials=creds)
stream = QuoteStream(credentials=creds)
```

## Development

```bash
uv sync
uv run pytest             # offline tests (protocol codec, parsers vs recorded fixtures, fake WS server)
uv run pytest -m live     # live smoke tests against real endpoints
uv run python examples/historical_bars.py
uv run python examples/stream_quotes.py
```

Package layout: pure request-builders/parsers per endpoint (`search.py`, `quotes.py`, `screener.py`, `scripts.py`, `_chart.py`), thin sync/async facades (`client.py`), and async websocket clients (`ws.py` for quotes, `bars.py`/`bar_stream.py` for OHLCV) over the `~m~`-framed TradingView protocol (`_protocol.py`).

### Releasing to PyPI

Tagging a version runs `.github/workflows/release.yml`, which builds and publishes to PyPI, then creates the matching GitHub Release. To cut a release:

```bash
# bump `version` in pyproject.toml (the single source of truth), then:
git commit -am "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

The workflow guards that the tag matches the package version, runs the offline tests, publishes to PyPI (idempotently), and attaches the built artifacts to the GitHub Release.

## Error handling

All errors derive from `TradingViewError`: `HTTPStatusError` (with `RateLimitError` for 429 and `AuthRequiredError` for 401/403), `SymbolNotFoundError`, `ParseError` (markup drift), `ProtocolError`, and `StreamClosedError`. Every model keeps the raw payload on `.raw` so new upstream fields remain accessible.

## License

MIT — see [LICENSE](LICENSE).
