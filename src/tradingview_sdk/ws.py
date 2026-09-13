"""Streaming quote websocket client (QuoteStream)."""

from __future__ import annotations

import logging
import time
from typing import Any, Sequence

from ._protocol import WS_URL, generate_session_id
from ._stream import _StreamBase
from .auth import Credentials
from .models import QuoteUpdate

logger = logging.getLogger("tradingview_sdk.ws")

DEFAULT_WS_FIELDS: tuple[str, ...] = (
    "lp",            # last price
    "lp_time",
    "ch",            # change (abs)
    "chp",           # change (%)
    "bid",
    "ask",
    "open_price",
    "high_price",
    "low_price",
    "prev_close_price",
    "volume",
    "currency_code",
    "short_name",
    "exchange",
    "description",
    "type",
    "update_mode",
    "rtc",           # realtime close (extended data)
    "rch",
    "rchp",
)


class QuoteStream(_StreamBase[QuoteUpdate]):
    """Realtime/delayed quote streaming with dynamic subscribe/unsubscribe.

    Usage::

        async with QuoteStream() as stream:
            await stream.subscribe("NASDAQ:AAPL", "BINANCE:BTCUSDT")
            async for update in stream.updates():
                print(update.symbol, update.last_price)
    """

    _task_name = "tv-quote-supervisor"
    _closed_message = "QuoteStream is closed"

    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        fields: Sequence[str] = DEFAULT_WS_FIELDS,
        reconnect: bool = True,
        url: str = WS_URL,
    ):
        super().__init__(credentials=credentials, reconnect=reconnect, url=url)
        self._fields = tuple(fields)

        self._desired: set[str] = set()
        self._snapshots: dict[str, dict[str, Any]] = {}
        self._completed: set[str] = set()
        self._session_id = ""

    # ------------------------------------------------------------------ API

    async def subscribe(self, *symbols: str) -> None:
        """Add symbols ("EXCHANGE:TICKER") to the stream."""
        new = [s for s in symbols if s not in self._desired]
        self._desired.update(new)
        if new and self.is_connected:
            await self._send("quote_add_symbols", [self._session_id, *new])

    async def unsubscribe(self, *symbols: str) -> None:
        """Remove symbols from the stream."""
        present = [s for s in symbols if s in self._desired]
        self._desired.difference_update(present)
        for s in present:
            self._snapshots.pop(s, None)
            self._completed.discard(s)
        if present and self.is_connected:
            await self._send("quote_remove_symbols", [self._session_id, *present])

    @property
    def subscriptions(self) -> frozenset[str]:
        return frozenset(self._desired)

    def snapshot(self, symbol: str) -> dict[str, Any] | None:
        """Latest merged field values for a subscribed symbol."""
        snap = self._snapshots.get(symbol)
        return dict(snap) if snap is not None else None

    # ------------------------------------------------------------- protocol

    async def _handshake(self, token: str) -> None:
        self._session_id = generate_session_id("qs")
        await self._send("set_auth_token", [token])
        await self._send("quote_create_session", [self._session_id])
        await self._send("quote_set_fields", [self._session_id, *self._fields])
        # Re-derived after every send rather than read once: a subscribe or
        # unsubscribe that lands while a send here is parked (backpressure) sees
        # is_connected False and leaves it to this loop, so the loop has to notice.
        added: set[str] = set()
        while True:
            new = sorted(self._desired - added)
            gone = sorted(added - self._desired)
            if not new and not gone:
                return
            if new:
                added.update(new)
                await self._send("quote_add_symbols", [self._session_id, *new])
            if gone:
                added.difference_update(gone)
                await self._send("quote_remove_symbols", [self._session_id, *gone])

    def _handle_data(self, method: str | None, params: list[Any]) -> None:
        if method == "qsd":
            self._handle_qsd(params)
        elif method == "quote_completed" and len(params) >= 2:
            self._completed.add(params[1])

    def _handle_qsd(self, params: list[Any]) -> None:
        if len(params) < 2 or not isinstance(params[1], dict):
            return
        body = params[1]
        symbol = body.get("n")
        if not symbol:
            return
        if body.get("s") == "error":
            # An unknown symbol answers with status "error", errmsg "no_such_symbol"
            # and an empty "v" (measured 2026-09-13). Dispatching that would hand
            # consumers a QuoteUpdate with no changes and no snapshot. Checked before
            # "v" so the warning is not lost if the error frame carries no "v" at all.
            logger.warning(
                "quote for %r failed: %s", symbol, body.get("errmsg") or str(body)[:200]
            )
            return
        values = body.get("v")
        if not isinstance(values, dict):
            return
        snap = self._snapshots.setdefault(symbol, {})
        snap.update(values)
        self._dispatch(
            QuoteUpdate(
                symbol=symbol,
                changes=values,
                snapshot=dict(snap),
                received_at=time.monotonic(),
            )
        )
