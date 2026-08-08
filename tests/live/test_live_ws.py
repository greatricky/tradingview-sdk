"""Live websocket streaming tests: pytest -m live

Uses 24/7 crypto symbols so the tests pass outside equity market hours.
"""

import asyncio

import pytest

from tradingview_sdk import AsyncTradingView, BarStream, Interval, QuoteStream

pytestmark = pytest.mark.live


async def test_subscribe_and_receive_snapshots():
    async with QuoteStream() as stream:
        await stream.subscribe("BINANCE:BTCUSDT", "NASDAQ:AAPL")
        seen: dict[str, float] = {}
        async with asyncio.timeout(30):
            async for update in stream.updates():
                if update.last_price is not None:
                    seen[update.symbol] = update.last_price
                if len(seen) >= 2:
                    break
        assert seen["BINANCE:BTCUSDT"] > 0
        assert seen["NASDAQ:AAPL"] > 0


async def test_dynamic_add_remove():
    async with QuoteStream() as stream:
        await stream.subscribe("BINANCE:BTCUSDT")
        async with asyncio.timeout(30):
            async for update in stream.updates("BINANCE:BTCUSDT"):
                if update.last_price:
                    break
        await stream.unsubscribe("BINANCE:BTCUSDT")
        await stream.subscribe("BINANCE:ETHUSDT")
        assert stream.subscriptions == frozenset({"BINANCE:ETHUSDT"})
        async with asyncio.timeout(30):
            async for update in stream.updates("BINANCE:ETHUSDT"):
                if update.last_price:
                    break


async def test_get_bars_history():
    async with AsyncTradingView() as tv:
        bars = await tv.get_bars("BINANCE:BTCUSDT", Interval.DAY, bars=50)
    assert len(bars) >= 10
    assert list(bars.times) == sorted(bars.times)          # ascending
    assert all(b.low <= b.close <= b.high for b in bars)
    assert bars.last.close > 0
    assert bars.currency  # e.g. "USDT"


async def test_get_bars_date_range():
    from datetime import datetime, timedelta, timezone

    start = datetime.now(timezone.utc) - timedelta(days=120)
    async with AsyncTradingView() as tv:
        bars = await tv.get_bars("BINANCE:BTCUSDT", Interval.DAY, start=start)
    assert bars[0].datetime >= start - timedelta(days=5)    # paged back to ~start
    assert len(bars) >= 90


async def test_bar_stream_updates():
    async with BarStream() as stream:
        await stream.subscribe("BINANCE:BTCUSDT", "1")
        async with asyncio.timeout(30):
            async for update in stream.updates():
                assert update.symbol == "BINANCE:BTCUSDT"
                assert update.interval == "1"
                assert update.bar.close > 0
                break
        assert stream.snapshot("BINANCE:BTCUSDT", "1") is not None
