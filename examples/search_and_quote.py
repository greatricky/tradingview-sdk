"""Instrument search and latest quotes: lookup, identifiers, and quote fields.

A guided tour of tv.search_symbols() and tv.get_quote() — run with:
    uv run python examples/search_and_quote.py
"""

import asyncio

from tradingview_sdk import AsyncTradingView, Field, TradingView


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def num(value, spec: str = ",.2f") -> str:
    """Format a possibly-missing numeric quote field."""
    return format(value, spec) if isinstance(value, (int, float)) else "—"


async def async_quote(symbol: str):
    """The async client mirrors the sync one method-for-method."""
    async with AsyncTradingView() as tv:
        return await tv.get_quote(symbol)


with TradingView() as tv:
    # ---------------------------------------------------------------------
    section("1. Search instruments by name or ticker")
    # Defaults to US stocks; every hit is a SymbolInfo.
    for info in tv.search_symbols("apple")[:5]:
        print(f"  {info.full_symbol:<20} {info.type:<8} {info.currency:<5} {info.description}")

    # ---------------------------------------------------------------------
    section("2. Search any asset class, or scope to an exchange / country")
    # search_type=None searches every class (stock, crypto, futures, forex, ...).
    print("search_type=None — all asset classes matching 'gold':")
    for info in tv.search_symbols("gold", search_type=None)[:6]:
        specs = ",".join(info.typespecs) or "—"
        print(f"  {info.full_symbol:<24} type={info.type:<10} specs={specs:<16} {info.description[:32]}")

    # Narrow by asset class, exchange, or the country used to rank results.
    print("\nsearch_type='crypto':")
    for info in tv.search_symbols("ETH", search_type="crypto")[:3]:
        print(f"  {info.full_symbol:<24} {info.description[:44]}")

    print("\nexchange='NASDAQ':")
    for info in tv.search_symbols("micro", exchange="NASDAQ")[:3]:
        print(f"  {info.full_symbol:<24} {info.description[:44]}")

    # ---------------------------------------------------------------------
    section("3. What a SymbolInfo carries")
    info = tv.search_symbols("AAPL")[0]
    print(f"  .symbol       {info.symbol}          .exchange   {info.exchange}")
    print(f"  .full_symbol  {info.full_symbol}   <- the 'EXCHANGE:TICKER' form every endpoint takes")
    print(f"  .type         {info.type}         .typespecs  {info.typespecs}")
    print(f"  .currency     {info.currency}           .country    {info.country}")
    print(f"  .isin         {info.isin}   .cusip      {info.cusip}")
    print(f"  .description  {info.description}")
    print(f"  .raw          dict with {len(info.raw)} upstream keys (forward-compatible)")

    # ---------------------------------------------------------------------
    section("4. Latest quote")
    # Accepts "EXCHANGE:TICKER" or a bare ticker (resolved via search).
    quote = tv.get_quote("NASDAQ:AAPL")
    print(f"  {quote.symbol}  {quote['description']}")
    print(f"    last   {num(quote.last)} {quote['currency']}      change  {num(quote.change, '+.2f')}%")
    print(f"    open   {num(quote['open'])}   high {num(quote['high'])}   low {num(quote['low'])}")
    print(f"    volume {num(quote.volume, ',.0f')}      bid/ask {num(quote.get('bid'))} / {num(quote.get('ask'))}")
    print(f"\n  bare ticker 'TSLA' resolved to -> {tv.get_quote('TSLA').symbol}")

    # ---------------------------------------------------------------------
    section("5. Pick exactly the fields you want")
    # Any screener field works here; Field enum members are plain strings.
    fundamentals = tv.get_quote(
        "NASDAQ:MSFT",
        fields=(Field.CLOSE, Field.MARKET_CAP_BASIC, Field.PRICE_EARNINGS_TTM,
                Field.DIVIDENDS_YIELD_CURRENT, Field.RSI, Field.SECTOR),
    )
    print(f"  {fundamentals.symbol} ({fundamentals['sector']})")
    print(f"    close        {num(fundamentals['close'])}")
    print(f"    market cap   {num(fundamentals['market_cap_basic'], ',.0f')}")
    print(f"    P/E (ttm)    {num(fundamentals['price_earnings_ttm'])}")
    print(f"    div yield    {num(fundamentals.get('dividends_yield_current'))}%")
    print(f"    RSI(14)      {num(fundamentals['RSI'], '.1f')}")

    # ---------------------------------------------------------------------
    section("6. Working with the returned Quote")
    print("  quote.last / .change / .volume   convenience accessors")
    print(f"  quote['close']                  raises KeyError if absent -> {num(quote['close'])}")
    print(f"  quote.get('nonexistent')        returns None -> {quote.get('nonexistent')}")
    print(f"  quote.fields                    every field returned ({len(quote.fields)} here)")
    print("\n  all fields:")
    for key, value in sorted(quote.fields.items()):
        print(f"    {key:<28} {value}")

# -------------------------------------------------------------------------
section("7. The same calls on AsyncTradingView")
async_result = asyncio.run(async_quote("BINANCE:BTCUSDT"))
print(f"  {async_result.symbol} last = {num(async_result.last)}")
