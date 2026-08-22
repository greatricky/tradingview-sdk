import json

import pytest

from tradingview_sdk import Adjustment, Bar, BarSet, Interval
from tradingview_sdk._chart import (
    create_series_params,
    parse_timescale_update,
    request_more_data_params,
    resolve_symbol_params,
    symbol_spec,
)
from tradingview_sdk._protocol import decode_frame, encode_message, parse_json_message
from tradingview_sdk.bar_stream import BarStream, _Series
from tradingview_sdk.bars import to_epoch


# --- request builders -------------------------------------------------------

def test_symbol_spec():
    assert symbol_spec("SP:SPX") == '={"adjustment":"splits","symbol":"SP:SPX"}'
    assert symbol_spec("NASDAQ:AAPL", adjustment="dividends", session="regular") == (
        '={"adjustment":"dividends","symbol":"NASDAQ:AAPL","session":"regular"}'
    )


def test_adjustment_enum():
    assert str(Adjustment.SPLITS) == "splits"
    assert str(Adjustment.DIVIDENDS) == "dividends"
    # the enum flows through symbol_spec as a plain string
    assert symbol_spec("NYSE:WU", adjustment=Adjustment.DIVIDENDS) == (
        '={"adjustment":"dividends","symbol":"NYSE:WU"}'
    )


def test_resolve_and_create_series_params():
    assert resolve_symbol_params("cs_1", "SP:SPX") == [
        "cs_1",
        "sds_sym_1",
        '={"adjustment":"splits","symbol":"SP:SPX"}',
    ]
    assert create_series_params("cs_1", "1D", 300) == ["cs_1", "sds_1", "s1", "sds_sym_1", "1D", 300, ""]
    assert request_more_data_params("cs_1", 500) == ["cs_1", "sds_1", 500]


def test_interval_serializes_as_plain_string():
    # StrEnum members are plain strings on the wire.
    assert str(Interval.DAY) == "1D"
    assert json.dumps([Interval.HOUR_1]) == '["60"]'
    frame = encode_message("create_series", create_series_params("cs", Interval.HOUR_4, 10))
    assert parse_json_message(decode_frame(frame)[0])["p"][4] == "240"


# --- timescale_update parser (against a recorded fixture) --------------------

def test_parse_timescale_update(fixture_json):
    params = fixture_json("bars_btcusdt.json")
    bars = parse_timescale_update(params, "sds_1")
    assert len(bars) >= 5
    assert all(isinstance(b, Bar) for b in bars)
    # ascending by time, OHLC sane, integer epoch seconds
    assert [b.time for b in bars] == sorted(b.time for b in bars)
    for b in bars:
        assert isinstance(b.time, int)
        assert b.low <= b.open <= b.high
        assert b.low <= b.close <= b.high
        assert b.volume is not None and b.volume > 0


def test_parse_timescale_update_ignores_wrong_series(fixture_json):
    params = fixture_json("bars_btcusdt.json")
    assert parse_timescale_update(params, "sds_99") == []


# --- BarSet / Bar models ----------------------------------------------------

def _sample_bars():
    return (
        Bar(1_700_000_000, 10.0, 12.0, 9.0, 11.0, 100.0),
        Bar(1_700_086_400, 11.0, 13.0, 10.5, 12.5, 200.0),
    )


def test_barset_accessors():
    bs = BarSet(symbol="X:Y", interval="1D", bars=_sample_bars(), currency="USD")
    assert len(bs) == 2
    assert list(bs)[0].close == 11.0
    assert bs[-1].close == 12.5
    assert bs.last.close == 12.5
    assert bs.closes == (11.0, 12.5)
    assert bs.times == (1_700_000_000, 1_700_086_400)
    assert bs.opens == (10.0, 11.0) and bs.highs == (12.0, 13.0) and bs.lows == (9.0, 10.5)
    assert bs.volumes == (100.0, 200.0)


def test_bar_datetime_is_utc():
    b = Bar(1_700_000_000, 1, 1, 1, 1, None)
    assert b.datetime.tzinfo is not None
    assert b.datetime.year == 2023


def test_empty_barset_last_is_none():
    assert BarSet(symbol="X:Y", interval="1D", bars=()).last is None


def test_to_dataframe():
    pd = pytest.importorskip("pandas")
    bs = BarSet(symbol="X:Y", interval="1D", bars=_sample_bars())
    df = bs.to_dataframe()
    assert list(df.columns) == ["open", "high", "low", "close", "volume"]
    assert len(df) == 2
    assert df["close"].tolist() == [11.0, 12.5]
    assert isinstance(df.index, pd.DatetimeIndex)


# --- to_epoch ---------------------------------------------------------------

def test_to_epoch():
    from datetime import date, datetime, timezone

    assert to_epoch(None) is None
    assert to_epoch(1_700_000_000) == 1_700_000_000
    assert to_epoch(datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)) == 1_700_000_000
    # naive datetime is treated as UTC
    assert to_epoch(datetime(2023, 11, 14, 22, 13, 20)) == 1_700_000_000
    assert to_epoch(date(2023, 1, 1)) == 1_672_531_200
    with pytest.raises(TypeError):
        to_epoch("2023-01-01")


# --- BarStream forming/closed contract (offline) ----------------------------

def _stream_with_series():
    stream = BarStream()
    series = _Series(symbol="X:Y", interval="1D", bars=10, chart_session="cs_test")
    stream._by_session[series.chart_session] = series
    stream._desired[(series.symbol, series.interval)] = series
    seen = []
    stream.on_update(lambda u: seen.append((u.bar.time, u.bar.close, u.closed)))
    return stream, series, seen


def test_barstream_seed_emits_only_newest():
    stream, series, seen = _stream_with_series()
    history = [Bar(t, 1, 1, 1, float(t), 1.0) for t in (100, 200, 300)]
    stream._ingest(series, history, historical=True)
    # only the newest bar is emitted (no replay of the whole history)
    assert seen == [(300, 300.0, False)]
    assert series.last_time == 300


def test_barstream_routes_by_chart_session():
    # TradingView allows one series per chart session, so each subscription gets its
    # own session and updates are routed by the session id in p[0] (not the series id,
    # which is always "sds_1" within its own session).
    stream, series, _ = _stream_with_series()
    other = _Series(symbol="A:B", interval="1D", bars=10, chart_session="cs_other")
    stream._by_session[other.chart_session] = other
    symbols: list[str] = []
    stream.on_update(lambda u: symbols.append(u.symbol))

    payload = {"sds_1": {"s": [{"i": 0, "v": [100, 1, 1, 1, 42.0, 1.0]}]}}
    stream._route_bars(["cs_other", payload], historical=True)
    assert other.last_bar.close == 42.0    # landed on the other session's series
    assert series.last_bar is None         # and not on this one
    assert symbols == ["A:B"]

    stream._route_bars(["cs_test", payload], historical=True)
    assert series.last_bar.close == 42.0
    assert symbols == ["A:B", "X:Y"]

    stream._route_bars(["cs_unknown", payload], historical=True)  # unknown session: ignored
    assert symbols == ["A:B", "X:Y"]


def test_barstream_forming_then_close():
    stream, series, seen = _stream_with_series()
    stream._ingest(series, [Bar(300, 1, 1, 1, 300.0, 1.0)], historical=True)
    seen.clear()
    # same period updates -> forming
    stream._ingest(series, [Bar(300, 1, 1, 1, 305.0, 2.0)], historical=False)
    # new period -> prior bar closes, new one forms
    stream._ingest(series, [Bar(400, 1, 1, 1, 401.0, 1.0)], historical=False)
    assert seen == [
        (300, 305.0, False),
        (300, 305.0, True),
        (400, 401.0, False),
    ]
    assert series.last_time == 400


def test_unparseable_points_are_skipped_and_logged(caplog):
    from tradingview_sdk._chart import parse_series_bars

    params = ["cs", {"sds_1": {"s": [
        {"i": 0, "v": [100, 1.0, 2.0, 0.5, 1.5, 10.0]},
        {"i": 1, "v": [200, None, None, None, None, 0]},   # hypothetical gap bar
        {"i": 2, "v": [300]},                               # too short
        "not-a-dict",
        {"i": 3, "v": [400, 1.0, 2.0, 0.5, 1.9, None]},     # null volume is legal
    ]}}]
    bars = parse_series_bars(params, "sds_1")
    assert [b.time for b in bars] == [100, 400]
    assert bars[1].volume is None
    assert any("skipped 3 unparseable bar point(s) of 5" in r.getMessage() for r in caplog.records)
