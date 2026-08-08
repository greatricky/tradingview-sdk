from tradingview_sdk.screener import (
    ETF_SCREENER_DEFAULT,
    STOCK_SCREENER_DEFAULT,
    Filter,
    ScreenerQuery,
    build_screener_request,
)


def test_default_stock_payload_shape():
    payload = STOCK_SCREENER_DEFAULT.to_payload()
    assert payload["markets"] == ["america"]
    assert payload["sort"] == {"sortBy": "market_cap_basic", "sortOrder": "desc"}
    assert payload["range"] == [0, 50]
    assert {"left": "is_primary", "operation": "equal", "right": True} in payload["filter"]
    assert payload["filter2"]["operator"] == "and"
    assert "name" in payload["columns"]


def test_default_etf_payload_shape():
    payload = ETF_SCREENER_DEFAULT.to_payload()
    assert {"left": "typespecs", "operation": "has", "right": ["etf"]} in payload["filter"]
    assert payload["sort"]["sortBy"] == "aum"
    assert "aum" in payload["columns"]


def test_builder_is_immutable_and_fluent():
    base = ScreenerQuery()
    q = (
        base.where(Filter.gt("market_cap_basic", 1e10), Filter.between("close", 10, 100))
        .select("name", "close")
        .order_by("volume", desc=False)
        .limit(25)
        .offset(50)
        .market("germany")
    )
    assert base.to_payload()["range"] == [0, 50]  # base untouched
    payload = q.to_payload()
    assert payload["filter"] == [
        {"left": "market_cap_basic", "operation": "greater", "right": 1e10},
        {"left": "close", "operation": "in_range", "right": [10, 100]},
    ]
    assert payload["columns"] == ["name", "close"]
    assert payload["sort"] == {"sortBy": "volume", "sortOrder": "asc"}
    assert payload["range"] == [50, 75]
    assert payload["markets"] == ["germany"]


def test_filter_constructors():
    assert Filter.eq("type", "stock").to_dict() == {"left": "type", "operation": "equal", "right": "stock"}
    assert Filter.has("typespecs", ["etf"]).to_dict() == {"left": "typespecs", "operation": "has", "right": ["etf"]}
    assert Filter.lte("close", 5).operation == "eless"
    assert Filter.match("name", "AAP").operation == "match"


def test_request_spec_url_and_label():
    spec = build_screener_request(ETF_SCREENER_DEFAULT)
    assert spec.url == "https://scanner.tradingview.com/america/scan"
    assert spec.params == {"label-product": "screener-etf"}
    spec2 = build_screener_request(ScreenerQuery().market("crypto"))
    assert spec2.url == "https://scanner.tradingview.com/crypto/scan"
