"""Live OHLCV bar streaming: forming vs closed candles across several series.

A guided tour of BarStream — run with:
    uv run python examples/stream_bars.py

Uses 24/7 crypto symbols so it produces output outside equity market hours.
"""

import asyncio

from tradingview_sdk import BarStream, Interval

BTC, ETH, SOL = "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


async def take(updates, n: int, timeout: float = 25.0) -> list:
    """Collect up to `n` updates from an async iterator, giving up after `timeout`."""
    collected: list = []
    try:
        async with asyncio.timeout(timeout):
            async for update in updates:
                collected.append(update)
                if len(collected) >= n:
                    break
    except TimeoutError:
        pass
    return collected


async def main() -> None:
    # `async with` opens the chart-session socket and closes it on exit;
    # it reconnects with backoff and recreates every series after a drop.
    async with BarStream() as stream:
        # -----------------------------------------------------------------
        section("1. Subscribe to a (symbol, interval) series")
        # Each subscription is a series: the same symbol can run at several
        # intervals at once. Interval takes the enum or a raw string.
        await stream.subscribe(BTC, Interval.MIN_1)
        print(f"  subscriptions: {sorted(stream.subscriptions)}")

        # -----------------------------------------------------------------
        section("2. Watch the current candle update in real time")
        # The first update seeds from the initial history load; after that each
        # tick restates the still-forming bar (closed=False).
        for update in await take(stream.updates(), 5):
            bar = update.bar
            state = "CLOSED " if update.closed else "forming"
            print(
                f"  {update.symbol:<18} {update.interval:>3}  {bar.datetime:%H:%M}  {state}"
                f"  O={bar.open:>10,.2f} H={bar.high:>10,.2f} L={bar.low:>10,.2f} C={bar.close:>10,.2f}"
            )

        # -----------------------------------------------------------------
        section("3. What a BarUpdate carries")
        update = (await take(stream.updates(), 1))[0]
        bar = update.bar
        print(f"  .symbol     {update.symbol}")
        print(f"  .interval   {update.interval}")
        print(f"  .bar        Bar(time={bar.time}, O={bar.open}, H={bar.high}, L={bar.low},"
              f" C={bar.close}, V={bar.volume})")
        print(f"  .bar.datetime  {bar.datetime:%Y-%m-%d %H:%M %Z}  (aware UTC)")
        print(f"  .closed     {update.closed}"
              f"   <- False while the bar forms; True once a newer bar starts")
        print(f"  .received_at  {update.received_at:.3f}  (time.monotonic() of receipt)")

        # -----------------------------------------------------------------
        section("4. Many symbols and intervals at once")
        await stream.subscribe(ETH, Interval.MIN_1)
        await stream.subscribe(BTC, Interval.MIN_5)   # same symbol, second series
        print(f"  now streaming {len(stream.subscriptions)} series:")
        for symbol, interval in sorted(stream.subscriptions):
            print(f"    {symbol:<18} {interval}")
        seen = {(u.symbol, u.interval) for u in await take(stream.updates(), 8)}
        print(f"  series seen in the next 8 updates: {sorted(seen)}")

        # -----------------------------------------------------------------
        section("5. Filter the iterator to specific symbols")
        eth_only = await take(stream.updates(ETH), 3)
        print(f"  updates({ETH!r}) yielded {len(eth_only)} updates, all ETH: "
              f"{all(u.symbol == ETH for u in eth_only)}")

        # -----------------------------------------------------------------
        section("6. Callbacks instead of iteration")
        # on_update() accepts sync or async callbacks and returns an unregister fn.
        ticks: list[tuple[str, str]] = []
        unregister = stream.on_update(lambda u: ticks.append((u.symbol, u.interval)))
        await take(stream.updates(), 5)
        unregister()
        print(f"  callback fired {len(ticks)} times across {len(set(ticks))} series")
        before = len(ticks)
        await take(stream.updates(), 3)
        print(f"  after unregister(), callback fired {len(ticks) - before} more times")

        # -----------------------------------------------------------------
        section("7. Point-in-time snapshots")
        # snapshot() returns the latest bar for a series without iterating.
        for symbol, interval in ((BTC, Interval.MIN_1), (BTC, Interval.MIN_5), (ETH, Interval.MIN_1)):
            snap = stream.snapshot(symbol, interval)
            if snap:
                print(f"  {symbol:<18} {str(interval):>3}  {snap.datetime:%H:%M}  close={snap.close:,.2f}")

        # -----------------------------------------------------------------
        section("8. Change subscriptions mid-stream")
        await stream.unsubscribe(ETH, Interval.MIN_1)
        await stream.subscribe(SOL, Interval.MIN_1)
        print(f"  swapped ETH/1m -> SOL/1m; now: {sorted(stream.subscriptions)}")
        symbols = {u.symbol for u in await take(stream.updates(), 6)}
        print(f"  symbols seen after the swap: {sorted(symbols)}")


if __name__ == "__main__":
    asyncio.run(main())
