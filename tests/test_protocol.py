import json

from tradingview_sdk._protocol import (
    decode_frame,
    encode_message,
    generate_session_id,
    is_heartbeat,
    parse_json_message,
    utf16_len,
    wrap_raw,
)


def test_encode_roundtrip():
    frame = encode_message("quote_add_symbols", ["qs_abc", "NASDAQ:AAPL"])
    messages = decode_frame(frame)
    assert len(messages) == 1
    data = parse_json_message(messages[0])
    assert data == {"m": "quote_add_symbols", "p": ["qs_abc", "NASDAQ:AAPL"]}


def test_encode_length_prefix_matches():
    frame = encode_message("set_auth_token", ["unauthorized_user_token"])
    assert frame.startswith("~m~")
    length = int(frame.split("~m~")[1])
    payload = frame.split("~m~", 3)[3] if frame.count("~m~") > 2 else frame[len(f"~m~{length}~m~"):]
    assert len(payload) == length


def test_decode_multiple_messages_in_one_frame():
    m1 = encode_message("a", [1])
    m2 = encode_message("b", [2])
    hb = wrap_raw("~h~7")
    messages = decode_frame(m1 + hb + m2)
    assert len(messages) == 3
    assert parse_json_message(messages[0])["m"] == "a"
    assert messages[1] == "~h~7"
    assert parse_json_message(messages[2])["m"] == "b"


def test_heartbeat_detection_and_echo():
    hb = "~h~42"
    assert is_heartbeat(hb)
    assert not is_heartbeat('{"m":"qsd"}')
    assert wrap_raw(hb) == "~m~5~m~~h~42"


def test_server_hello_is_not_json_message():
    # first payload from the server is a JSON object without "m"
    data = parse_json_message('{"session_id":"x","timestamp":1}')
    assert data is not None
    assert data.get("m") is None
    assert parse_json_message("~h~1") is None
    assert parse_json_message("not json {") is None


def test_decode_tolerates_trailing_garbage():
    good = encode_message("a", [])
    assert decode_frame(good + "junk") == decode_frame(good)


def test_length_prefix_counts_utf16_code_units_not_bytes():
    # Captured verbatim from production: the payload is 99 characters and 113 UTF-8
    # bytes, and the server declares 99 — JavaScript's String.length. Reading the
    # prefix as a byte count truncates the JSON and desyncs the rest of the frame.
    payload = (
        '{"m":"qsd","p":["qs_vvg85v09ah13",{"n":"KRX:005930","s":"ok",'
        '"v":{"local_description":"\uc0bc\uc131\uc804\uc790\ubcf4\ud1b5\uc8fc"}}]}'
    )
    assert len(payload) == 99 and len(payload.encode("utf-8")) == 113

    wire = f"~m~99~m~{payload}" + encode_message("after", [1])
    messages = decode_frame(wire)
    assert len(messages) == 2
    assert json.loads(messages[0])["p"][1]["v"]["local_description"] == "\uc0bc\uc131\uc804\uc790\ubcf4\ud1b5\uc8fc"
    assert parse_json_message(messages[1])["m"] == "after"


def test_astral_characters_count_as_two_units():
    # Outside the BMP, JavaScript counts a surrogate pair as 2 while Python's len()
    # counts 1, so plain character slicing would come up short.
    payload = '{"n":"\U0001f680"}'
    assert len(payload) == 9 and utf16_len(payload) == 10

    wire = f"~m~{utf16_len(payload)}~m~{payload}" + wrap_raw("~h~3")
    messages = decode_frame(wire)
    assert messages == [payload, "~h~3"]


def test_wrap_raw_prefixes_the_utf16_length():
    assert wrap_raw("Société") == "~m~7~m~Société"      # 7 chars, 9 UTF-8 bytes
    assert wrap_raw("~h~42") == "~m~5~m~~h~42"


def test_decode_accepts_raw_bytes():
    frame = encode_message("a", [1])
    assert decode_frame(frame.encode("utf-8")) == decode_frame(frame)


def test_session_id_shape():
    sid = generate_session_id("qs")
    assert sid.startswith("qs_")
    assert len(sid) == 3 + 12
    assert sid != generate_session_id("qs")


def test_ascii_frames_skip_the_astral_scan():
    # _has_astral must short-circuit on the cached ASCII flag: scanning every frame
    # with max() is ~10^6 times more expensive and pointless for ASCII payloads.
    from tradingview_sdk._protocol import _has_astral

    assert _has_astral("") is False
    assert _has_astral('{"a":1}') is False
    assert _has_astral("삼성전자") is False          # BMP: one char, one code unit
    assert _has_astral('{"n":"🚀"}') is True
