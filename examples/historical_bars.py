"""Historical OHLCV bars: intervals, ranges, adjustments, and the BarSet API.

A guided tour of tv.get_bars() — run with:
    uv run python examples/historical_bars.py
"""

import asyncio
from datetime import date, datetime, timezone

from tradingview_sdk import Adjustment, AsyncTradingView, Interval, TradingView

DAILY_OR_LONGER = ("1D", "1W", "1M")


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def show(bars, limit: int = 5) -> None:
    """Print a BarSet header plus its last `limit` bars as an aligned OHLCV table."""
    stamp = "%Y-%m-%d" if bars.interval in DAILY_OR_LONGER else "%Y-%m-%d %H:%M"
    print(f"{bars.symbol}  interval={bars.interval}  bars={len(bars)}  currency={bars.currency or '—'}")
    for bar in bars[-limit:]:
        volume = f"{bar.volume:>13,.0f}" if bar.volume is not None else f"{'—':>13}"
        print(
            f"  {bar.datetime:{stamp}}  O={bar.open:>10,.2f}  H={bar.high:>10,.2f}"
            f"  L={bar.low:>10,.2f}  C={bar.close:>10,.2f}  V={volume}"
        )


async def latest_close(symbol: str) -> float:
    """The async client mirrors the sync one method-for-method."""
    async with AsyncTradingView() as tv:
        bars = await tv.get_bars(symbol, Interval.DAY, bars=1)
        return bars.last.close


with TradingView() as tv:
    # ---------------------------------------------------------------------
    section("1. The N most recent candles")
    # `bars=N` is the simplest form. Symbols take "EXCHANGE:TICKER"...
    daily = tv.get_bars("BINANCE:BTCUSDT", Interval.DAY, bars=200)
    show(daily)
    # ...or a bare ticker, which is resolved via symbol search.
    print(f"\nbare ticker 'AAPL' resolved to -> {tv.get_bars('AAPL', Interval.DAY, bars=1).symbol}")

    # ---------------------------------------------------------------------
    section("2. Any interval: the Interval enum or a raw resolution string")
    # Interval is a StrEnum, so Interval.HOUR_1 and "60" are interchangeable.
    for interval in (Interval.MIN_5, "60", Interval.DAY, Interval.WEEK):
        bars = tv.get_bars("BINANCE:BTCUSDT", interval, bars=3)
        closes = ", ".join(f"{c:,.2f}" for c in bars.closes)
        print(f"  {str(interval):>4}  last 3 closes: {closes}")

    # ---------------------------------------------------------------------
    section("3. An intraday window (timezone-aware start/end)")
    # Time of day — and therefore the timezone — is meaningful for intraday bars.
    # A naive datetime would be read as UTC. BTCUSDT trades 24/7, so every hour
    # in the window is populated.
    window = tv.get_bars(
        "BINANCE:BTCUSDT",
        Interval.HOUR_1,
        start=datetime(2026, 8, 1, 8, 0, tzinfo=timezone.utc),
        end=datetime(2026, 8, 2, 8, 0, tzinfo=timezone.utc),
    )
    print(f"requested 08:00 -> 08:00 UTC, got {len(window)} hourly bars:")
    print(f"  first {window[0].datetime:%Y-%m-%d %H:%M %Z}   last {window.last.datetime:%Y-%m-%d %H:%M %Z}")

    # ---------------------------------------------------------------------
    section("4. A daily range (a plain date needs no time-of-day)")
    # `start` wins over the bar count: the SDK pages backwards until it is covered.
    ytd = tv.get_bars("SP:SPX", Interval.DAY, start=date(2026, 1, 1))
    print(f"S&P 500 year-to-date: {len(ytd)} daily bars since {ytd[0].datetime:%Y-%m-%d}")
    show(ytd, limit=3)

    # ---------------------------------------------------------------------
    section("5. Split and dividend adjustment")
    # TradingView exposes one "ADJ" toggle, and the two modes nest:
    #   Adjustment.SPLITS    -> split-adjusted only (dividends left in), the default
    #   Adjustment.DIVIDENDS -> split-adjusted *and* dividend-adjusted
    # AAPL has both a 4:1 split (2020) and regular dividends.
    since = date(2015, 1, 1)
    splits = tv.get_bars("NASDAQ:AAPL", Interval.MONTH, start=since, adjustment=Adjustment.SPLITS)
    divs = tv.get_bars("NASDAQ:AAPL", Interval.MONTH, start=since, adjustment=Adjustment.DIVIDENDS)
    by_time = {bar.time: bar for bar in divs}
    print(f"{'bar':>10}  {'SPLITS':>10}  {'DIVIDENDS':>10}   difference")
    for bar in (splits[0], splits.last):
        other = by_time.get(bar.time)
        if other:
            gap = "identical" if bar.close == other.close else f"{bar.close / other.close - 1:+.1%}"
            print(f"  {bar.datetime:%Y-%m}  {bar.close:>10,.2f}  {other.close:>10,.2f}   {gap}")
    print("\nOnly history is restated — the latest bar is the same in both modes.")

    # ---------------------------------------------------------------------
    section("6. Working with the returned BarSet")
    # BarSet behaves like an immutable sequence of Bar objects...
    print(f"  len(bars)        {len(daily)}")
    print(f"  bars[0]          {daily[0].datetime:%Y-%m-%d} close={daily[0].close:,.2f}")
    print(f"  bars[-1] / .last {daily.last.datetime:%Y-%m-%d} close={daily.last.close:,.2f}")
    print(f"  max(b.high ...)  {max(b.high for b in daily):,.2f}   (BarSet is iterable)")
    # ...and exposes each field as a column, handy for indicators.
    closes = daily.closes
    sma20 = sum(closes[-20:]) / 20
    print(f"\n  .closes[-3:]     {tuple(round(c, 2) for c in closes[-3:])}")
    print(f"  .times[-1]       {daily.times[-1]}  (epoch seconds, UTC)")
    print(f"  20-bar SMA       {sma20:,.2f}  from .closes")
    # Each Bar carries the raw values plus a timezone-aware datetime.
    bar = daily.last
    print(f"\n  last bar         time={bar.time} datetime={bar.datetime:%Y-%m-%d %H:%M %Z}")
    print(f"                   O={bar.open} H={bar.high} L={bar.low} C={bar.close} V={bar.volume}")

    # ---------------------------------------------------------------------
    section("7. Optional pandas export")
    # Imports pandas lazily, so it stays an optional dependency.
    try:
        df = daily.to_dataframe()
        print(f"DataFrame{df.shape} indexed by UTC timestamp:\n{df.tail(3)}")
    except ImportError:
        print("(install pandas to use bars.to_dataframe())")

# -------------------------------------------------------------------------
section("8. The same call on AsyncTradingView")
# Every sync method exists on AsyncTradingView with an identical signature.
print(f"  BINANCE:ETHUSDT last daily close = {asyncio.run(latest_close('BINANCE:ETHUSDT')):,.2f}")
