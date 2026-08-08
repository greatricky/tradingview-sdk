"""Live quote streaming: subscriptions, iterators, callbacks, and snapshots.

A guided tour of QuoteStream — run with:
    uv run python examples/stream_quotes.py

Uses 24/7 crypto symbols so it produces output outside equity market hours.
"""

import asyncio

from tradingview_sdk import DEFAULT_WS_FIELDS, QuoteStream

BTC, ETH, SOL = "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


async def take(updates, n: int, timeout: float = 20.0) -> list:
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
    # `async with` opens the socket, authenticates, and closes it on exit.
    # Reconnects (with backoff) and resubscribes automatically after a drop.
    async with QuoteStream() as stream:
        # -----------------------------------------------------------------
        section("1. Subscribe to symbols")
        await stream.subscribe(BTC, ETH)
        print(f"  subscriptions: {sorted(stream.subscriptions)}")

        # -----------------------------------------------------------------
        section("2. Consume the update stream")
        # updates() is an async iterator of QuoteUpdate; many can run at once.
        for update in await take(stream.updates(), 6):
            price = update.last_price
            change = update.snapshot.get("chp")
            print(
                f"  {update.symbol:<18} last={price if price is not None else '—':<12}"
                f" chg={change if change is not None else '—':<10} fields_in_tick={len(update.changes)}"
            )

        # -----------------------------------------------------------------
        section("3. What a QuoteUpdate carries")
        update = (await take(stream.updates(), 1))[0]
        print(f"  .symbol       {update.symbol}")
        print(f"  .changes      only the fields in THIS tick: {sorted(update.changes)}")
        print(f"  .snapshot     merged view of everything seen so far ({len(update.snapshot)} fields)")
        print(f"  .last_price   {update.last_price}   (shortcut for .snapshot['lp'])")
        print(f"  .received_at  {update.received_at:.3f}  (time.monotonic() of receipt)")

        # -----------------------------------------------------------------
        section("4. Filter the iterator to specific symbols")
        eth_only = await take(stream.updates(ETH), 3)
        print(f"  updates({ETH!r}) yielded {len(eth_only)} updates, all ETH: "
              f"{all(u.symbol == ETH for u in eth_only)}")

        # -----------------------------------------------------------------
        section("5. Callbacks instead of iteration")
        # on_update() accepts sync or async callbacks and returns an unregister fn.
        seen: list[str] = []
        unregister = stream.on_update(lambda u: seen.append(u.symbol))
        await take(stream.updates(), 5)          # let some traffic flow
        unregister()                             # stop receiving callbacks
        print(f"  callback fired {len(seen)} times: {sorted(set(seen))}")
        before = len(seen)
        await take(stream.updates(), 3)
        print(f"  after unregister(), callback fired {len(seen) - before} more times")

        # -----------------------------------------------------------------
        section("6. Point-in-time snapshots")
        # snapshot() needs no iteration — it returns the latest merged fields.
        for symbol in (BTC, ETH):
            snap = stream.snapshot(symbol) or {}
            print(f"  {symbol:<18} lp={snap.get('lp')}  bid={snap.get('bid')}  ask={snap.get('ask')}"
                  f"  vol={snap.get('volume')}")

        # -----------------------------------------------------------------
        section("7. Change subscriptions mid-stream")
        await stream.unsubscribe(ETH)
        await stream.subscribe(SOL)
        print(f"  swapped ETH -> SOL; now: {sorted(stream.subscriptions)}")
        symbols = {u.symbol for u in await take(stream.updates(), 6)}
        print(f"  symbols seen after the swap: {sorted(symbols)}")

    # ---------------------------------------------------------------------
    section("8. Choose which fields the server sends")
    print(f"  DEFAULT_WS_FIELDS ({len(DEFAULT_WS_FIELDS)}): {', '.join(DEFAULT_WS_FIELDS[:8])} ...")
    # A narrower set means smaller, faster ticks.
    async with QuoteStream(fields=("lp", "volume")) as lean:
        await lean.subscribe(BTC)
        update = (await take(lean.updates(), 1))[0]
        print(f"  with fields=('lp', 'volume') -> tick carries {sorted(update.changes)}")


if __name__ == "__main__":
    asyncio.run(main())
