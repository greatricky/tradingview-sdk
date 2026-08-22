"""TradingView websocket wire protocol: ``~m~<len>~m~<payload>`` framing.

``<len>`` is the payload's length as JavaScript's ``String.length`` reports it —
UTF-16 code units, *not* bytes. Verified against production: a ``qsd`` frame
carrying ``"local_description":"삼성전자보통주"`` declares ``~m~99~m~`` for a
payload of 99 characters / 113 UTF-8 bytes, and reading the prefix as a byte
count truncates the JSON and desyncs the rest of the frame.

For every character in the Basic Multilingual Plane — which covers TradingView's
instrument names, CJK included — one code unit is one Python character, so plain
slicing is exact. Only astral characters (emoji, U+10000 and above) count as two
units in JavaScript and one in Python, and those take the slower walk below.
"""

from __future__ import annotations

import json
import random
import re
import string
from typing import Any

_FRAME_RE = re.compile(r"~m~(\d+)~m~")
_HEARTBEAT_RE = re.compile(r"^~h~\d+$")

WS_URL = "wss://data.tradingview.com/socket.io/websocket?from=chart%2F&type=chart"
WS_ORIGIN = "https://www.tradingview.com"


def utf16_len(text: str) -> int:
    """Length in UTF-16 code units — what the server's ``String.length`` counts."""
    if text.isascii():
        return len(text)
    return len(text.encode("utf-16-le")) // 2


def encode_message(method: str, params: list[Any]) -> str:
    """Encode one protocol message.

    ``ensure_ascii=True`` keeps the payload ASCII-only, so the length prefix is
    unambiguous no matter how the receiver counts it.
    """
    payload = json.dumps({"m": method, "p": params}, separators=(",", ":"), ensure_ascii=True)
    return f"~m~{len(payload)}~m~{payload}"


def wrap_raw(payload: str) -> str:
    """Wrap an already-serialized payload (e.g. a heartbeat echo)."""
    return f"~m~{utf16_len(payload)}~m~{payload}"


def decode_frame(frame: str | bytes) -> list[str]:
    """Split one websocket frame into its ``~m~``-framed payloads."""
    text = frame.decode("utf-8", "replace") if isinstance(frame, (bytes, bytearray)) else frame
    if _has_astral(text):
        return _decode_utf16(text)
    return _decode_chars(text)


def _has_astral(text: str) -> bool:
    """True if any character sits outside the BMP, where JS counts two code units.

    ``isascii()`` is a cached flag on the string object, so the overwhelmingly common
    all-ASCII frame costs nothing; only the rare non-ASCII frame pays the scan.
    """
    return not text.isascii() and bool(text) and max(text) > "\uffff"


def _decode_chars(text: str) -> list[str]:
    messages: list[str] = []
    pos = 0
    while pos < len(text):
        m = _FRAME_RE.match(text, pos)
        if not m:
            # Tolerate trailing garbage rather than dropping the whole frame.
            break
        start = m.end()
        end = start + int(m.group(1))
        messages.append(text[start:end])
        pos = end
    return messages


def _decode_utf16(text: str) -> list[str]:
    """Slice by UTF-16 code units, counting astral characters as the server does."""
    messages: list[str] = []
    pos = 0
    while pos < len(text):
        m = _FRAME_RE.match(text, pos)
        if not m:
            break
        units = int(m.group(1))
        start = end = m.end()
        consumed = 0
        while end < len(text) and consumed < units:
            consumed += 2 if text[end] > "￿" else 1
            end += 1
        messages.append(text[start:end])
        pos = end
    return messages


def is_heartbeat(message: str) -> bool:
    return bool(_HEARTBEAT_RE.match(message))


def parse_json_message(message: str) -> dict[str, Any] | None:
    """Parse a JSON protocol message; returns None for non-JSON payloads."""
    if not message or message[0] != "{":
        return None
    try:
        data = json.loads(message)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def generate_session_id(prefix: str = "qs") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{prefix}_{suffix}"
