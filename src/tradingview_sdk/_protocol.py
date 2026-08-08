"""TradingView websocket wire protocol: ``~m~<len>~m~<payload>`` framing.

``<len>`` counts *bytes* of the UTF-8 payload, not characters, so framing is done
on bytes throughout. A single non-ASCII character anywhere in a frame (a
``description`` like "Société Générale", a CJK instrument name) otherwise makes
every character-based slice land short, truncating that message and desyncing
the reader for the rest of the frame.
"""

from __future__ import annotations

import json
import random
import re
import string
from typing import Any

_FRAME_RE = re.compile(rb"~m~(\d+)~m~")
_HEARTBEAT_RE = re.compile(r"^~h~\d+$")

WS_URL = "wss://data.tradingview.com/socket.io/websocket?from=chart%2F&type=chart"
WS_ORIGIN = "https://www.tradingview.com"


def _framed(payload: str) -> str:
    return f"~m~{len(payload.encode('utf-8'))}~m~{payload}"


def encode_message(method: str, params: list[Any]) -> str:
    """Encode one protocol message.

    ``ensure_ascii=True`` keeps the payload ASCII-only, which TradingView's own
    client does too; the length prefix is computed in bytes either way.
    """
    payload = json.dumps({"m": method, "p": params}, separators=(",", ":"), ensure_ascii=True)
    return _framed(payload)


def wrap_raw(payload: str) -> str:
    """Wrap an already-serialized payload (e.g. a heartbeat echo)."""
    return _framed(payload)


def decode_frame(frame: str | bytes) -> list[str]:
    """Split one websocket frame into its ``~m~``-framed payloads."""
    raw = frame.encode("utf-8") if isinstance(frame, str) else frame
    messages: list[str] = []
    pos = 0
    while pos < len(raw):
        m = _FRAME_RE.match(raw, pos)
        if not m:
            # Tolerate trailing garbage rather than dropping the whole frame.
            break
        start = m.end()
        end = start + int(m.group(1))
        messages.append(raw[start:end].decode("utf-8", "replace"))
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
