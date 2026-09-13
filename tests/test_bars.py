import json

import pytest

from tradingview_sdk import Adjustment, Bar, BarSet, Interval
from tradingview_sdk._chart import (
    create_series_params,
    parse_timescale_update,
    request_more_data_params,
    resolve_symbol_params,
    symbol_currency,
    symbol_info,
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


def test_barset_resolved_fields_default_to_none():
    # Added in 0.5.0 with defaults so every earlier keyword construction still works.
    bs = BarSet(symbol="X:Y", interval="1D", bars=())
    assert bs.timezone is None and bs.session is None


# --- symbol_resolved metadata -----------------------------------------------

_RESOLVED = {
    "currency_code": "USD",
    "timezone": "America/Chicago",
    "session": "0215-0826,0830-1516",
    "type": "index",
}


def test_symbol_info_returns_the_whole_description():
    params = ["cs_1", "sds_sym_1", _RESOLVED]
    assert symbol_info(params) is _RESOLVED
    assert symbol_currency(params) == "USD"


@pytest.mark.parametrize(
    "params",
    [[], ["cs_1"], ["cs_1", "sds_sym_1"], ["cs_1", "sds_sym_1", "not-a-dict"], {"m": "x"}],
)
def test_symbol_info_is_empty_on_any_other_shape(params):
    assert symbol_info(params) == {}
    assert symbol_currency(params) is None


def test_symbol_currency_key_fallbacks_are_unchanged():
    assert symbol_currency(["cs", "sym", {"currency-id": "EUR"}]) == "EUR"
    assert symbol_currency(["cs", "sym", {"currency_id": "GBP"}]) == "GBP"


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


# --- server errors addressed to one series ------------------------------------


def test_barstream_drops_a_series_the_server_rejects(caplog):
    # A critical_error carrying one of our chart-session ids means that one
    # create_series was rejected — the socket and the other sessions stay up
    # (measured 2026-09-13). It must retire the series, not the connection: a
    # reconnect would replay the same request and fail forever.
    stream, series, seen = _stream_with_series()
    other = _Series(symbol="A:B", interval="1D", bars=10, chart_session="cs_other")
    stream._by_session[other.chart_session] = other
    stream._desired[(other.symbol, other.interval)] = other

    absorbed = stream._absorb_error(
        "critical_error", ["cs_test", "invalid parameters", "method: create_series"]
    )
    assert absorbed is True
    assert stream.subscriptions == frozenset({("A:B", "1D")})
    assert "cs_test" not in stream._by_session
    assert any("dropping 'X:Y' 1D" in r.getMessage() for r in caplog.records)
    assert seen == []


def test_barstream_symbol_and_series_errors_drop_their_series(caplog):
    stream, series, _ = _stream_with_series()
    stream._handle_data("symbol_error", ["cs_test", "sds_sym_1", "invalid symbol"])
    assert stream.subscriptions == frozenset()
    # The series_error that follows the symbol_error finds nothing left: no second
    # warning, no error.
    before = len(caplog.records)
    stream._handle_data("series_error", ["cs_test", "sds_1", "s1", "resolve error"])
    assert len([r for r in caplog.records[before:] if r.levelname == "WARNING"]) == 0


def test_barstream_still_treats_a_session_less_critical_error_as_fatal():
    stream, _, _ = _stream_with_series()
    assert stream._absorb_error("critical_error", ["not a session", "auth failed"]) is False
    assert stream._absorb_error("critical_error", []) is False
    # An error for a chart session we already unsubscribed is ours to ignore, not
    # a reason to reconnect.
    assert stream._absorb_error("critical_error", ["cs_gone", "invalid parameters"]) is True
    assert stream.subscriptions == frozenset({("X:Y", "1D")})


async def test_barstream_subscribe_passes_adjustment_and_session_to_resolve_symbol():
    # The streaming chart session is the same resolve_symbol + create_series
    # handshake fetch_bars uses, so it takes the same options.
    stream = BarStream()
    sent = []

    async def capture(method, params):
        sent.append((method, params))

    stream._send = capture
    stream._connected.set()   # pretend the handshake is done so subscribe sends now
    await stream.subscribe("NASDAQ:AAPL", "60", adjustment=Adjustment.DIVIDENDS, session="extended")
    await stream.subscribe("BINANCE:BTCUSDT", "1")
    specs = [p[2] for m, p in sent if m == "resolve_symbol"]
    assert specs == [
        '={"adjustment":"dividends","symbol":"NASDAQ:AAPL","session":"extended"}',
        '={"adjustment":"splits","symbol":"BINANCE:BTCUSDT"}',
    ]
    # Options ride along with the series, so a reconnect replays them.
    sent.clear()
    await stream._handshake("tok")
    assert [p[2] for m, p in sent if m == "resolve_symbol"] == specs
    # Same (symbol, interval) with other options is a no-op, as documented.
    sent.clear()
    await stream.subscribe("NASDAQ:AAPL", "60", session="regular")
    assert sent == [] and stream.subscriptions == {("NASDAQ:AAPL", "60"), ("BINANCE:BTCUSDT", "1")}


async def test_barstream_handshake_notices_subscribes_that_land_mid_handshake():
    # A subscribe/unsubscribe that runs while the handshake is parked on a send
    # sees is_connected False and does not send; the handshake must therefore
    # re-read the desired set rather than replay a snapshot taken up front.
    stream = BarStream()
    await stream.subscribe("A:B", "1D")
    await stream.subscribe("C:D", "1D")
    sent = []

    async def capture(method, params):
        sent.append((method, params))
        if method == "create_series" and not any(k == ("E:F", "1D") for k in stream.subscriptions):
            await stream.subscribe("E:F", "1D")        # late arrival
            await stream.unsubscribe("C:D", "1D")      # late departure

    stream._send = capture
    await stream._handshake("tok")
    resolved = [json.loads(p[2][1:])["symbol"] for m, p in sent if m == "resolve_symbol"]
    assert resolved == ["A:B", "E:F"]
    assert stream.subscriptions == {("A:B", "1D"), ("E:F", "1D")}
    assert sorted(s.symbol for s in stream._by_session.values()) == ["A:B", "E:F"]


def test_barstream_protocol_error_stays_fatal_even_with_a_session_id():
    stream, _, _ = _stream_with_series()
    assert stream._absorb_error("protocol_error", ["cs_test", "wrong data"]) is False
    assert stream.subscriptions == frozenset({("X:Y", "1D")})
