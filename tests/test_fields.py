import importlib.util
import json
from enum import StrEnum
from pathlib import Path

from tradingview_sdk import Filter, ScreenerQuery
from tradingview_sdk.fields import (
    FIELDS,
    TIMEFRAMES,
    Field,
    FieldType,
    field_info,
    search_fields,
    with_timeframe,
)
import pytest


def test_catalog_covers_enum():
    assert len(Field) == len(FIELDS) > 1000
    for member in list(Field)[:50]:
        assert member.value in FIELDS
        assert member.info.name == member.value


def test_known_fields_present_with_metadata():
    assert Field.MARKET_CAP_BASIC == "market_cap_basic"
    assert FIELDS["market_cap_basic"].type is FieldType.FUNDAMENTAL_PRICE
    assert "capitalization" in FIELDS["market_cap_basic"].description.lower()
    assert "0-100" in FIELDS["RSI"].description
    assert FIELDS["change"].type is FieldType.PERCENT
    assert FIELDS["aum"].description.startswith("Assets under management")


def test_enumerated_value_ranges():
    sector = FIELDS["sector"]
    assert sector.values is not None
    assert "Finance" in sector.values
    assert "Electronic Technology" in sector.values
    assert set(FIELDS["type"].values) == {"stock", "fund", "dr", "structured"}
    assert "etf" in FIELDS["typespecs"].values
    assert "NASDAQ" in FIELDS["exchange"].values


def test_timeframe_variants():
    assert TIMEFRAMES == ("1", "5", "15", "30", "60", "120", "240", "1W", "1M")
    assert Field.CHANGE.tf("60") == "change|60"
    assert with_timeframe("close", "1W") == "close|1W"
    with pytest.raises(ValueError):
        Field.SECTOR.tf("60")  # no timeframe variants
    with pytest.raises(ValueError):
        Field.CHANGE.tf("99")  # invalid timeframe


def test_field_info_lookup_handles_variants():
    assert field_info("close|1W") is FIELDS["close"]
    assert field_info("close") is FIELDS["close"]
    assert field_info("no_such_field") is None


def test_search_fields():
    hits = search_fields("dividend yield")
    assert any(f.name == "dividends_yield_current" for f in hits)
    assert search_fields("zzz_no_match_zzz") == []


def test_adx_plus_minus_members_distinct():
    assert Field.ADX_PLUS_DI == "ADX+DI"
    assert Field.ADX_DI == "ADX-DI"


def _load_generator():
    """Import scripts/generate_fields.py, which is not part of the package."""
    path = Path(__file__).parent.parent / "scripts" / "generate_fields.py"
    spec = importlib.util.spec_from_file_location("generate_fields", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_member_names_match_the_committed_enum():
    generator = _load_generator()
    assert generator.assign_member_names(FIELDS) == {m.value: m.name for m in Field}


def test_generated_member_names_survive_a_suffix_collision():
    # "ADX+DI" and "ADX+DI[1]" already differ by exactly the suffix pattern used for
    # collisions, so a generated name can land on a natural one; Enum would then
    # raise "Attempted to reuse key" and break the whole package on import.
    generator = _load_generator()
    names = ["a.b", "a_b", "a_b_2"]
    members = generator.assign_member_names(names)
    assert len(set(members.values())) == 3
    assert StrEnum("Generated", [(m, n) for n, m in members.items()])  # would raise on a dupe


def test_enum_works_in_screener_query():
    q = (
        ScreenerQuery()
        .where(Filter.gt(Field.MARKET_CAP_BASIC, 1e9))
        .select(Field.NAME, Field.CLOSE, Field.CHANGE.tf("60"))
        .order_by(Field.VOLUME)
    )
    payload = q.to_payload()
    # StrEnum members must serialize as their plain string values
    assert json.loads(json.dumps(payload["columns"])) == ["name", "close", "change|60"]
    assert payload["filter"] == [{"left": "market_cap_basic", "operation": "greater", "right": 1e9}]
    assert payload["sort"]["sortBy"] == "volume"
