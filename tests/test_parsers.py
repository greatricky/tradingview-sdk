import pytest

from tradingview_sdk.errors import ParseError, SymbolNotFoundError
from tradingview_sdk.quotes import parse_quote_response
from tradingview_sdk.screener import ScreenerQuery, parse_screener_response
from tradingview_sdk.scripts import (
    SCRIPT_TYPES,
    build_listing_request,
    normalize_script_url,
    parse_listing_page,
    parse_pine_source,
    parse_script_page,
)
from tradingview_sdk.search import parse_search_response


def test_parse_search(fixture_json):
    symbols = parse_search_response(fixture_json("search_aapl.json"))
    assert symbols
    top = symbols[0]
    assert top.symbol == "AAPL"
    assert top.exchange == "NASDAQ"
    assert top.full_symbol == "NASDAQ:AAPL"
    assert top.type == "stock"
    assert top.isin == "US0378331005"
    assert "common" in top.typespecs


def test_parse_search_bad_shape():
    with pytest.raises(ParseError):
        parse_search_response(["nope"])


def test_search_routing_prefix_wins_over_display_exchange(fixture_json):
    # BYMA's CEDEARs display as BYMA but are addressed as BCBA:AAPL everywhere else.
    symbols = parse_search_response(fixture_json("search_aapl.json"))
    prefixed = [s for s in symbols if s.prefix]
    assert prefixed, "fixture should contain at least one prefixed listing"
    for s in prefixed:
        assert s.prefix != s.exchange
        assert s.full_symbol == f"{s.prefix}:{s.symbol}"


def test_parse_quote(fixture_json):
    quote = parse_quote_response("NASDAQ:AAPL", fixture_json("quote_aapl.json"))
    assert quote.symbol == "NASDAQ:AAPL"
    assert quote.last and quote.last > 0
    assert quote["currency"] == "USD"
    assert quote.get("nonexistent") is None


def test_parse_quote_empty_is_not_found():
    with pytest.raises(SymbolNotFoundError):
        parse_quote_response("NASDAQ:NOPE", {"close": None, "volume": None})


def test_parse_screener(fixture_json):
    query = ScreenerQuery().select("name", "description", "close", "change", "volume", "market_cap_basic")
    result = parse_screener_response(query, fixture_json("screener_scan.json"))
    assert result.total_count > 100
    assert len(result.rows) == 5
    top = result.rows[0]
    assert ":" in top.symbol
    assert top["market_cap_basic"] > 1e11
    assert list(result.columns) == ["name", "description", "close", "change", "volume", "market_cap_basic"]


def test_parse_screener_short_row_raises_instead_of_truncating(fixture_json):
    query = ScreenerQuery().select("name", "close", "volume")
    with pytest.raises(ParseError, match="requested columns"):
        parse_screener_response(query, {"data": [{"s": "NASDAQ:AAPL", "d": ["Apple", 1.0]}], "totalCount": 1})


def test_parse_screener_row_without_symbol_raises():
    query = ScreenerQuery().select("name")
    with pytest.raises(ParseError, match="row shape"):
        parse_screener_response(query, {"data": [{"d": ["Apple"]}], "totalCount": 1})


def test_parse_listing(fixture_text):
    page = parse_listing_page(fixture_text("listing.html"), page=1)
    assert len(page) >= 10
    assert page.has_next
    card = page.cards[0]
    assert card.slug
    assert card.title
    assert card.url.startswith("https://www.tradingview.com/script/")
    assert card.author
    assert card.script_type == "strategy"
    assert card.script_id_part and card.script_id_part.startswith("PUB;")


def test_parse_listing_fallback_anchor_scrape():
    html = """
    <html><body>
      <a href="/script/abc123-My-Strategy/">My Strategy</a>
      <a href="/script/def456-Other/">Other</a>
      <a href="/scripts/page-2/?script_type=strategies">next</a>
    </body></html>
    """
    page = parse_listing_page(html, page=1)
    assert [c.slug for c in page.cards] == ["abc123-My-Strategy", "def456-Other"]
    assert page.has_next


def test_parse_listing_empty_raises():
    with pytest.raises(ParseError):
        parse_listing_page("<html><body>nothing here</body></html>")


def test_normalize_script_url():
    slug = "eUCT3oSF-WW-Pro-Flow-Zones-Miracle-V4"
    expected = f"https://www.tradingview.com/script/{slug}/"
    assert normalize_script_url(slug) == (slug, expected)
    assert normalize_script_url(expected) == (slug, expected)
    assert normalize_script_url(f"/script/{slug}/") == (slug, expected)


def test_parse_script_page(fixture_text):
    strategy = parse_script_page(fixture_text("script_page.html"), "eUCT3oSF-WW-Pro-Flow-Zones-Miracle-V4")
    assert strategy.title == "WW Pro Flow Zones Miracle V4"
    assert strategy.author == "ChristakisO"
    assert strategy.script_id_part == "PUB;411703a1c0234aa6b7ae14b6a9002495"
    assert strategy.is_strategy
    assert strategy.chart_symbol == "MEXC:XAUUSDT.P"
    assert strategy.chart_interval == "15"

    report = strategy.report
    assert report is not None
    assert report.currency == "USDT"
    assert report.all.total_trades == 27
    assert report.all.profit_factor == pytest.approx(1.9329, rel=1e-3)
    assert report.all.percent_profitable == pytest.approx(0.6296, rel=1e-3)
    assert report.long is not None and report.short is not None
    assert report.max_drawdown == pytest.approx(93.25)
    assert report.sharpe_ratio is not None
    assert len(report.buy_hold_curve) > 0
    assert len(report.trades) == 27
    assert "backtest" in report.date_range


def test_parse_script_page_bad_html():
    with pytest.raises(ParseError):
        parse_script_page("<html></html>", "whatever")


def test_parse_script_page_null_idea_data_raises_parse_error():
    # Deleted / access-restricted scripts still carry the key, with a null value.
    html = (
        '<html><body><script type="application/prs.init-data+json">'
        '{"page": {"ssrIdeaData": null}}</script></body></html>'
    )
    with pytest.raises(ParseError):
        parse_script_page(html, "whatever")


def test_parse_pine_source(fixture_json):
    src = parse_pine_source("PUB;411703a1c0234aa6b7ae14b6a9002495", fixture_json("pine_source.json"))
    assert src.name == "WW Pro Flow Zones Miracle V4"
    assert src.kind == "strategy"
    assert src.access == "open_no_auth"
    assert "strategy(" in src.source_text
    assert "source" not in src.raw  # raw excludes the big source body


def test_listing_request_validates_script_type():
    # Upstream 404s on unknown filters (e.g. "studies"), so fail fast with a clear error.
    for script_type in SCRIPT_TYPES:
        spec = build_listing_request(1, script_type)
        assert spec.params["script_type"] == script_type
    with pytest.raises(ValueError, match="invalid script_type"):
        build_listing_request(1, "studies")


def test_parse_pine_source_unescapes_name():
    # pine-facade HTML-escapes scriptName; the source body is raw.
    src = parse_pine_source(
        "PUB;x",
        {"scriptName": "Setup -&gt; Trigger &amp; Exit", "source": "//@version=6", "extra": {}},
    )
    assert src.name == "Setup -> Trigger & Exit"


# --- listing pages past the end ------------------------------------------------


def test_listing_page_past_the_end_is_empty(fixture_text):
    # The server redirects /scripts/page-N/ past the last page to /scripts/ and
    # serves page 1 (measured 2026-09-13: page 43 of 42 came back as page 1 with
    # `next` set). Trusting the body would report page 1's cards as page 43 and
    # keep `has_next` true.
    from tradingview_sdk.scripts import listing_page_served, parse_listing_page

    html = fixture_text("listing.html")
    page = parse_listing_page(html, 43, final_url="https://www.tradingview.com/scripts/?script_type=strategies")
    assert page.cards == [] and page.page == 43 and page.has_next is False
    # The same body at its own URL parses as usual.
    assert len(parse_listing_page(html, 1, final_url="https://www.tradingview.com/scripts/?x=1")) > 0
    assert len(parse_listing_page(html, 2, final_url="https://www.tradingview.com/scripts/page-2/")) > 0

    assert listing_page_served("https://www.tradingview.com/scripts/", 1)
    assert listing_page_served("https://www.tradingview.com/scripts/page-1/", 1)
    assert listing_page_served("https://www.tradingview.com/scripts/page-7/?script_type=all", 7)
    assert not listing_page_served("https://www.tradingview.com/scripts/", 7)
    assert not listing_page_served("https://www.tradingview.com/scripts/page-70/", 7)


def test_unavailable_script_is_reported_as_such():
    from tradingview_sdk.errors import ParseError
    from tradingview_sdk.scripts import parse_script_page

    html = '<script type="application/prs.init-data+json">{"ssrIdeaData": null}</script>'
    with pytest.raises(ParseError, match="not available"):
        parse_script_page(html, "gone-slug")
    with pytest.raises(ParseError, match="markup may have changed"):
        parse_script_page("<html></html>", "gone-slug")


# --- bare-ticker resolution -----------------------------------------------------


def test_pick_full_symbol_prefers_exact_ticker_then_first():
    from tradingview_sdk.models import SymbolInfo
    from tradingview_sdk.search import pick_full_symbol

    def info(symbol, exchange, prefix=None, contracts=None):
        raw = {"contracts": contracts} if contracts else {}
        return SymbolInfo(symbol, exchange, "", "stock", (), None, None, None, None, prefix=prefix, raw=raw)

    assert pick_full_symbol([], "AAPL") is None
    assert pick_full_symbol([info("AAPLX", "NYSE"), info("AAPL", "NASDAQ")], "aapl") == "NASDAQ:AAPL"
    assert pick_full_symbol([info("AAPLX", "NYSE")], "AAPL") == "NYSE:AAPLX"
    # A CEDEAR is displayed under BYMA but routed via its prefix.
    assert pick_full_symbol([info("AAPL", "BYMA", prefix="BCBA")], "AAPL") == "BCBA:AAPL"


def test_pick_full_symbol_finds_a_futures_contract_under_its_root():
    # Searching "ES1!" lists the root CME:ES, with the contracts nested; the root
    # is not chartable and the contract carries its own routing prefix
    # (measured 2026-09-13).
    from tradingview_sdk.models import SymbolInfo
    from tradingview_sdk.search import pick_full_symbol

    root = SymbolInfo("ES", "CME", "", "futures", (), None, None, None, None,
                      raw={"contracts": [{"symbol": "ES1!", "prefix": "CME_MINI"}, {"symbol": "ESZ2026"}]})
    other = SymbolInfo("ES", "ASX24", "", "futures", (), None, None, None, None,
                       raw={"contracts": [{"symbol": "ES1!"}]})
    assert pick_full_symbol([root, other], "ES1!") == "CME_MINI:ES1!"
    assert pick_full_symbol([root, other], "ESZ2026") == "CME:ESZ2026"   # no prefix: the root's exchange
    assert pick_full_symbol([other], "ES1!") == "ASX24:ES1!"
    assert pick_full_symbol([root], "ES2!") == "CME:ES"                 # no match anywhere: first result
