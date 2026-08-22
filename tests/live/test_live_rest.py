"""Live smoke tests against real TradingView endpoints: pytest -m live"""

import pytest

from tradingview_sdk import AsyncTradingView, Filter, ScreenerQuery, TradingView
from tradingview_sdk.errors import SymbolNotFoundError

pytestmark = pytest.mark.live


@pytest.fixture
def tv():
    with TradingView() as client:
        yield client


def test_search_symbols(tv):
    results = tv.search_symbols("AAPL")
    assert any(s.full_symbol == "NASDAQ:AAPL" and s.type == "stock" for s in results)


def test_get_quote(tv):
    quote = tv.get_quote("NASDAQ:AAPL")
    assert quote.last and quote.last > 0
    assert quote["currency"] == "USD"


def test_get_quote_bare_symbol(tv):
    quote = tv.get_quote("MSFT")
    assert quote.symbol == "NASDAQ:MSFT"
    assert quote.last and quote.last > 0


def test_unknown_symbol_raises_symbol_not_found(tv):
    """Guards the ``no_404=true`` request param.

    With it, an unknown symbol comes back as ``200 null``; without it the endpoint
    404s and the SDK would surface HTTPStatusError instead. If TradingView ever
    stops honouring the param, this is what catches it.
    """
    with pytest.raises(SymbolNotFoundError):
        tv.get_quote("NASDAQ:ZZZZZZZZ")


def test_routing_prefix_is_used_for_full_symbol(tv):
    """Some listings display one exchange but are addressed under another.

    BYMA's CEDEARs quote as BCBA:AAPL; BYMA:AAPL does not exist upstream.
    """
    results = tv.search_symbols("AAPL", search_type=None)
    prefixed = [s for s in results if s.prefix and s.prefix != s.exchange]
    assert prefixed, "expected at least one listing whose routing prefix differs"
    for info in prefixed:
        assert info.full_symbol.startswith(f"{info.prefix}:")
    quote = tv.get_quote("BCBA:AAPL")
    assert quote.last and quote.last > 0


def test_stock_screener_defaults(tv):
    result = tv.screen_stocks()
    assert result.total_count > 1000
    assert len(result.rows) == 50
    assert all(":" in row.symbol for row in result.rows)


def test_etf_screener_defaults(tv):
    result = tv.screen_etfs()
    assert result.total_count > 500
    top = result.rows[0]
    assert "etf" in (top.get("typespecs") or [])
    assert top.get("aum") and top["aum"] > 1e10


def test_custom_screener_query(tv):
    query = (
        ScreenerQuery()
        .where(Filter.gt("market_cap_basic", 1e12))
        .select("name", "close", "market_cap_basic")
        .order_by("market_cap_basic")
        .limit(20)
    )
    result = tv.screen(query)
    names = {row.symbol for row in result.rows}
    assert "NASDAQ:AAPL" in names or "NASDAQ:NVDA" in names


async def test_async_client_parity():
    async with AsyncTradingView() as tv:
        quote = await tv.get_quote("NASDAQ:AAPL")
        assert quote.last and quote.last > 0
        results = await tv.search_symbols("SPY", search_type=None)
        assert results
