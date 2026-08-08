"""Live strategy listing/detail tests: pytest -m live"""

import pytest

from tradingview_sdk import TradingView

pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def tv():
    with TradingView() as client:
        yield client


def test_list_strategies_first_page(tv):
    page = tv.list_strategies()
    assert len(page) >= 10
    assert page.has_next
    assert all(card.url.startswith("https://www.tradingview.com/script/") for card in page.cards)


def test_list_strategies_second_page(tv):
    page = tv.list_strategies(page=2)
    assert len(page) >= 10


def test_get_strategy_with_report_and_source(tv):
    # find an open-source strategy from the listing (PUB; id => source is public)
    page = tv.list_strategies()
    card = next(c for c in page.cards if c.script_id_part and c.script_id_part.startswith("PUB;"))
    strategy = tv.get_strategy(card.url)
    assert strategy.title
    assert strategy.script_id_part == card.script_id_part
    assert strategy.source is not None
    assert "strategy" in strategy.source.source_text
    if strategy.report is not None:
        assert strategy.report.all is not None
        assert strategy.report.all.total_trades is not None
