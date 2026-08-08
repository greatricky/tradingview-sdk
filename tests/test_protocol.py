import json

from tradingview_sdk._protocol import (
    decode_frame,
    encode_message,
    generate_session_id,
    is_heartbeat,
    parse_json_message,
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


def test_length_prefix_counts_bytes_not_characters():
    # The server frames non-ASCII payloads (CJK names, "Société Générale") by byte
    # length; slicing by characters truncates the message and desyncs everything
    # after it in the same frame. Built here the way the server sends it.
    payload = json.dumps({"m": "qsd", "p": [{"n": "Société Générale"}]}, ensure_ascii=False)
    assert len(payload.encode("utf-8")) > len(payload)  # the test is only meaningful if so
    wire = f"~m~{len(payload.encode('utf-8'))}~m~{payload}" + encode_message("after", [1])

    messages = decode_frame(wire)
    assert len(messages) == 2
    assert parse_json_message(messages[0])["p"][0]["n"] == "Société Générale"
    assert parse_json_message(messages[1])["m"] == "after"


def test_wrap_raw_prefixes_the_byte_length():
    assert wrap_raw("Société") == "~m~9~m~Société"  # 7 characters, 9 UTF-8 bytes


def test_decode_accepts_raw_bytes():
    frame = encode_message("a", [1])
    assert decode_frame(frame.encode("utf-8")) == decode_frame(frame)


def test_session_id_shape():
    sid = generate_session_id("qs")
    assert sid.startswith("qs_")
    assert len(sid) == 3 + 12
    assert sid != generate_session_id("qs")
