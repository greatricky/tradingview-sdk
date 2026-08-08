"""Stock & ETF screeners: presets, the query builder, filters, and the field catalog.

A guided tour of tv.screen*() and ScreenerQuery — run with:
    uv run python examples/run_screener.py
"""

from tradingview_sdk import (
    FIELDS,
    Field,
    Filter,
    ScreenerQuery,
    TradingView,
    field_info,
    search_fields,
)


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def num(value, spec: str = ",.2f") -> str:
    """Format a possibly-missing numeric column."""
    return format(value, spec) if isinstance(value, (int, float)) else "—"


with TradingView() as tv:
    # ---------------------------------------------------------------------
    section("1. Built-in presets that mirror the web screeners")
    # tradingview.com/screener/ and /etf-screener/, same defaults and columns.
    stocks = tv.screen_stocks()
    print(f"US stocks matching the default screen: {stocks.total_count:,}")
    for row in stocks.rows[:5]:
        print(f"  {row.symbol:<18} close={num(row['close']):>9}  mcap={num(row['market_cap_basic'], ',.0f'):>18}")

    etfs = tv.screen_etfs()
    print(f"\nUS ETFs: {etfs.total_count:,}")
    for row in etfs.rows[:5]:
        print(f"  {row.symbol:<18} {row['description'][:34]:<36} AUM={num(row['aum'], ',.0f'):>16}")

    # ---------------------------------------------------------------------
    section("2. Build a custom query")
    # ScreenerQuery is an immutable fluent builder — every method returns a copy.
    query = (
        ScreenerQuery()
        .where(
            Filter.gt(Field.MARKET_CAP_BASIC, 10e9),      # large caps
            Filter.gt(Field.VOLUME, 2_000_000),           # liquid
            Filter.between(Field.PRICE_EARNINGS_TTM, 0, 15),
            Filter.eq(Field.SECTOR, "Finance"),           # values: FIELDS["sector"].values
        )
        .select(Field.NAME, Field.CLOSE, Field.CHANGE, Field.MARKET_CAP_BASIC,
                Field.PRICE_EARNINGS_TTM, Field.RSI)
        .order_by(Field.PRICE_EARNINGS_TTM, desc=False)   # cheapest first
        .limit(8)
    )
    result = tv.screen(query)
    print(f"Finance large caps with P/E < 15: {result.total_count} matches")
    print(f"  {'symbol':<18} {'close':>9} {'chg%':>8} {'P/E':>7} {'RSI':>6}")
    for row in result:
        print(
            f"  {row.symbol:<18} {num(row[Field.CLOSE]):>9} {num(row[Field.CHANGE], '+.2f'):>8}"
            f" {num(row[Field.PRICE_EARNINGS_TTM]):>7} {num(row[Field.RSI], '.1f'):>6}"
        )

    # ---------------------------------------------------------------------
    section("3. The filter vocabulary")
    # Every operator the web screener supports has a constructor.
    print("  Filter.gt/gte/lt/lte(col, v)     numeric comparisons")
    print("  Filter.eq/ne(col, v)             equality")
    print("  Filter.between(col, lo, hi)      inclusive range")
    print("  Filter.in_(col, [a, b, c])       membership")
    print("  Filter.has/has_none_of(col, [..])  array columns (e.g. typespecs)")
    print("  Filter.match(col, 'pattern')     text match")
    # Example: dividend-paying tech, excluding preferred shares.
    dividend_tech = tv.screen(
        ScreenerQuery()
        .where(
            Filter.in_(Field.SECTOR, ["Technology Services", "Electronic Technology"]),
            Filter.gt(Field.DIVIDENDS_YIELD_CURRENT, 1.0),
            Filter.has_none_of(Field.TYPESPECS, ["preferred"]),
        )
        .select(Field.NAME, Field.CLOSE, Field.DIVIDENDS_YIELD_CURRENT, Field.SECTOR)
        .order_by(Field.DIVIDENDS_YIELD_CURRENT)
        .limit(5)
    )
    print(f"\n  dividend-paying tech ({dividend_tech.total_count} matches):")
    for row in dividend_tech:
        print(f"    {row.symbol:<16} yield={num(row['dividends_yield_current']):>6}%  {row['sector']}")

    # ---------------------------------------------------------------------
    section("4. The typed field catalog")
    # ~1,100 fields with metadata, generated from TradingView's metainfo endpoint.
    print(f"  FIELDS holds {len(FIELDS):,} fields; Field.X is a StrEnum member")
    print(f"  Field.MARKET_CAP_BASIC == {str(Field.MARKET_CAP_BASIC)!r}  (a plain str anywhere a name goes)")
    info = Field.RECOMMENDATION_MARK.info
    print(f"\n  {info.name}: {info.description}")
    print(f"    type={info.type.value}")
    rsi = field_info("RSI")
    print(f"  {rsi.name}: {rsi.description}")
    print(f"\n  enumerated values, e.g. FIELDS['sector'].values ({len(FIELDS['sector'].values)} total):")
    print(f"    {FIELDS['sector'].values[:4]} ...")
    print("\n  search the catalog by name or description:")
    for found in search_fields("expense")[:4]:
        print(f"    {found.name:<24} {found.description[:46]}")

    # ---------------------------------------------------------------------
    section("5. Per-timeframe field variants")
    # Many fields exist per chart timeframe as "name|tf".
    print(f"  FIELDS['change'].timeframes = {FIELDS['change'].timeframes}")
    print(f"  Field.CHANGE.tf('60')       = {Field.CHANGE.tf('60')!r}   (change on the 60-min chart)")
    movers = tv.screen(
        ScreenerQuery()
        .where(Filter.gt(Field.MARKET_CAP_BASIC, 50e9))
        .select(Field.NAME, Field.CLOSE, Field.CHANGE, Field.CHANGE.tf("60"), Field.CHANGE.tf("1W"))
        .order_by(Field.CHANGE.tf("1W"))
        .limit(5)
    )
    print(f"\n  {'symbol':<16} {'day%':>8} {'60min%':>8} {'week%':>8}")
    for row in movers:
        print(
            f"  {row.symbol:<16} {num(row['change'], '+.2f'):>8}"
            f" {num(row['change|60'], '+.2f'):>8} {num(row['change|1W'], '+.2f'):>8}"
        )

    # ---------------------------------------------------------------------
    section("6. Other markets")
    # .market() targets any market the web screener serves.
    crypto = tv.screen(
        ScreenerQuery()
        .market("crypto")
        .select(Field.NAME, Field.CLOSE, Field.CHANGE, Field.MARKET_CAP_CALC)
        .order_by(Field.MARKET_CAP_CALC)
        .limit(5)
    )
    print(f"  crypto by market cap ({crypto.total_count:,} instruments):")
    for row in crypto:
        print(
            f"    {row.symbol:<24} close={num(row['close']):>12}"
            f"  chg={num(row['change'], '+.2f'):>8}%  mcap={num(row['market_cap_calc'], ',.0f'):>18}"
        )
    germany = tv.screen(
        ScreenerQuery().market("germany").select(Field.NAME, Field.CLOSE, Field.MARKET_CAP_BASIC).limit(3)
    )
    print(f"\n  germany ({germany.total_count:,} instruments): {[r.symbol for r in germany]}")

    # ---------------------------------------------------------------------
    section("7. Paging through a large result set")
    # .limit() sets the page size, .offset() the starting row.
    base = ScreenerQuery().select(Field.NAME, Field.CLOSE, Field.MARKET_CAP_BASIC).limit(3)
    for page in range(3):
        rows = tv.screen(base.offset(page * 3))
        print(f"  rows {page * 3:>2}-{page * 3 + 2:<2} {[r.symbol for r in rows]}")

    # ---------------------------------------------------------------------
    section("8. Working with the returned ScreenerResult")
    print(f"  .total_count   {result.total_count}   (matches server-side, before .limit())")
    print(f"  len(result)    {len(result)}     (rows actually returned)")
    print(f"  .columns       {tuple(str(c) for c in result.columns[:3])} ...")
    row = result.rows[0]
    print("\n  each row is a ScreenerRow:")
    print(f"    .symbol            {row.symbol}")
    print(f"    row['close']       {num(row['close'])}")
    print(f"    row.get('missing') {row.get('missing')}")
    print(f"    .columns           dict of {len(row.columns)} column -> value")
