"""Community scripts: browsing the listing, backtest reports, and Pine source.

A guided tour of tv.list_strategies() / iter_strategies() / get_strategy() — run with:
    uv run python examples/strategies.py
"""

from tradingview_sdk import AuthRequiredError, TradingView


def section(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def num(value, spec: str = ",.2f") -> str:
    """Format a possibly-missing numeric stat."""
    return format(value, spec) if isinstance(value, (int, float)) else "—"


with TradingView() as tv:
    # ---------------------------------------------------------------------
    section("1. Browse the strategy listing")
    # Mirrors tradingview.com/scripts/?script_type=strategies
    page = tv.list_strategies()
    print(f"page {page.page}: {len(page)} scripts, more pages available: {page.has_next}")
    for card in page.cards[:8]:
        print(f"  {num(card.likes, ',d'):>6} likes  {card.title[:52]:<54} by {card.author}")

    # ---------------------------------------------------------------------
    section("2. What a StrategyCard carries")
    card = page.cards[0]
    print(f"  .title           {card.title}")
    print(f"  .author          {card.author}")
    print(f"  .likes           {card.likes}")
    print(f"  .slug            {card.slug}")
    print(f"  .url             {card.url}")
    print(f"  .script_type     {card.script_type}")
    print(f"  .script_id_part  {card.script_id_part}   <- fetches the Pine source")
    print(f"  .symbol          {card.symbol}   (chart the script was published on)")
    print(f"  .created_at      {card.created_at}")

    # ---------------------------------------------------------------------
    section("3. Page through the listing lazily")
    # iter_strategies() walks pages for you (with a politeness delay between them).
    titles = []
    for card in tv.iter_strategies(max_pages=2):
        titles.append(card.title)
    print(f"  collected {len(titles)} scripts across 2 pages")
    print(f"  first: {titles[0][:60]}")
    print(f"  last:  {titles[-1][:60]}")

    # ---------------------------------------------------------------------
    section("4. Indicators, not just strategies")
    # script_type switches the listing: "strategies" (default), "indicators",
    # "libraries", or "all".
    indicators = tv.list_strategies(script_type="indicators")
    print(f"  {len(indicators)} indicators on page 1:")
    for study in indicators.cards[:5]:
        print(f"    {num(study.likes, ',d'):>6} likes  {study.title[:56]}")

    # ---------------------------------------------------------------------
    section("5. Full detail for one script")
    # Accepts a slug or a full URL; pulls metadata + report + Pine source.
    target = next(c for c in page.cards if c.script_id_part and c.script_id_part.startswith("PUB;"))
    strategy = tv.get_strategy(target.url)
    print(f"  {strategy.title}")
    print(f"    author          {strategy.author}")
    print(f"    backtested on   {strategy.chart_symbol} @ {strategy.chart_interval}")
    print(f"    pine id         {strategy.script_id_part} (v{strategy.version})")
    print(f"    is_strategy     {strategy.is_strategy}   likes {strategy.likes}")
    print(f"    url             {strategy.url}")

    # ---------------------------------------------------------------------
    section("6. The published backtest report")
    report = strategy.report
    if report is None:
        print("  (this script publishes no strategy report)")
    else:
        stats = report.all
        print(f"  currency: {report.currency}")
        print(f"    net profit       {num(stats.net_profit):>14}  ({num(stats.net_profit_percent, '.2%')})")
        print(f"    gross profit     {num(stats.gross_profit):>14}")
        print(f"    gross loss       {num(stats.gross_loss):>14}")
        print(f"    total trades     {num(stats.total_trades, ',d'):>14}"
              f"  (win rate {num(stats.percent_profitable, '.1%')})")
        print(f"    profit factor    {num(stats.profit_factor):>14}")
        print(f"    avg trade        {num(stats.avg_trade):>14}")
        print(f"    max drawdown     {num(report.max_drawdown):>14}"
              f"  ({num(report.max_drawdown_percent, '.2%')})")
        print(f"    sharpe / sortino {num(report.sharpe_ratio):>14} / {num(report.sortino_ratio)}")
        print(f"    buy & hold       {num(report.buy_hold_return):>14}")

        # ---------------------------------------------------------------
        section("7. Long vs short breakdown, and the trade list")
        print(f"  {'':<8} {'net profit':>14} {'trades':>8} {'win rate':>10} {'profit factor':>14}")
        for label, group in (("all", report.all), ("long", report.long), ("short", report.short)):
            if group:
                print(
                    f"  {label:<8} {num(group.net_profit):>14} {num(group.total_trades, ',d'):>8}"
                    f" {num(group.percent_profitable, '.1%'):>10} {num(group.profit_factor):>14}"
                )
        print(f"\n  .trades      {len(report.trades)} individual trades")
        print(f"  .buy_hold_curve  {len(report.buy_hold_curve)} equity points")
        print(f"  .date_range  {report.date_range or '—'}")

    # ---------------------------------------------------------------------
    section("8. Pine source code")
    # get_strategy(include_source=False) skips this extra request; you can also
    # fetch it directly with tv.get_pine_source(script_id_part).
    try:
        source = strategy.source or tv.get_pine_source(strategy.script_id_part)
        print(f"  {source.name}  kind={source.kind}  v{source.version}  access={source.access}")
        print(f"  {len(source.source_text):,} chars — first lines:\n")
        for line in source.source_text.splitlines()[:12]:
            print(f"    {line}")
        print("    ...")
    except AuthRequiredError:
        # Protected / invite-only scripts do not expose their source.
        print("  source is protected (invite-only or closed-source script)")
