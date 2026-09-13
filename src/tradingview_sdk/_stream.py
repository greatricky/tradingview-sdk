"""Shared websocket plumbing for the streaming clients.

:class:`~tradingview_sdk.ws.QuoteStream` (quote sessions) and
:class:`~tradingview_sdk.bar_stream.BarStream` (chart sessions) differ only in
their handshake and in how they interpret protocol messages. Everything under
that — connect, reconnect with backoff, heartbeat echo, consumer fan-out and
shutdown — lives here, so a fix lands once instead of in two near-identical
copies. Subclasses implement :meth:`_StreamBase._handshake` and
:meth:`_StreamBase._handle_data`.
"""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import random
import time
import weakref
from typing import Any, AsyncIterator, Callable, Generic, Protocol, TypeVar

import websockets

from ._http import BASE_HEADERS
from ._protocol import (
    WS_ORIGIN,
    WS_URL,
    decode_frame,
    encode_message,
    is_heartbeat,
    parse_json_message,
    wrap_raw,
)
from .auth import AuthTokenCache, Credentials, resolve_ws_token
from .errors import StreamClosedError

logger = logging.getLogger("tradingview_sdk.stream")

CLOSED = object()  # queue sentinel

# messages that indicate the server gave up on this connection
FATAL_METHODS = frozenset({"critical_error", "protocol_error"})

RECV_TIMEOUT = 30.0         # watchdog: no inbound frame for this long => reconnect
STABLE_CONNECTION = 60.0    # connection older than this resets the backoff
_MAX_BACKOFF = 30.0
_MAX_BACKOFF_EXPONENT = 6   # 0.5 * 2**6 = 32s, already past _MAX_BACKOFF


class _HasSymbol(Protocol):
    @property
    def symbol(self) -> str: ...


U = TypeVar("U", bound=_HasSymbol)

#: one registered consumer: an optional symbol filter and the queue it feeds
_QueueEntry = tuple[frozenset[str] | None, asyncio.Queue]


def _discard(queues: list[_QueueEntry], entry: _QueueEntry) -> None:
    """Unregister a consumer queue.

    Module-level on purpose: a :func:`weakref.finalize` callback must not close
    over the generator whose collection it is waiting for.
    """
    with contextlib.suppress(ValueError):
        queues.remove(entry)


class _StreamBase(Generic[U]):
    """Connection supervisor, consumer fan-out and lifecycle shared by the streams."""

    _task_name = "tv-stream-supervisor"
    _closed_message = "stream is closed"

    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        reconnect: bool = True,
        url: str = WS_URL,
    ):
        self._auth = AuthTokenCache(credentials if credentials is not None else Credentials.from_env())
        self._reconnect = reconnect
        self._url = url

        self._ws: Any = None
        self._send_lock = asyncio.Lock()
        self._supervisor_task: asyncio.Task | None = None
        self._connected = asyncio.Event()
        self._connected_at: float | None = None
        self._closed = False

        self._queues: list[_QueueEntry] = []
        self._callbacks: list[Callable[[U], Any]] = []
        self._callback_tasks: set[asyncio.Task] = set()
        self._queue_size = 512

    # ------------------------------------------------------------ lifecycle

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def start(self, *, wait_connected: bool = True, timeout: float = 20.0) -> None:
        """Start the connection supervisor (idempotent)."""
        if self._closed:
            raise StreamClosedError(self._closed_message)
        if self._supervisor_task is None:
            self._supervisor_task = asyncio.create_task(self._supervise(), name=self._task_name)
        if wait_connected:
            await self._wait_connected(timeout)

    async def _wait_connected(self, timeout: float) -> None:
        """Wait for the first connection, or for the supervisor to give up trying.

        With ``reconnect=False`` an unreachable endpoint ends the supervisor straight
        away; waiting on the event alone would stall for the whole timeout first.
        """
        assert self._supervisor_task is not None
        waiter = asyncio.ensure_future(self._connected.wait())
        try:
            done, _ = await asyncio.wait(
                {waiter, self._supervisor_task},
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            waiter.cancel()
        if waiter in done:
            return
        if self._supervisor_task in done:
            # Retrieve the exception (if any) so it is not reported as never-retrieved,
            # and carry it as the cause.
            cause = None if self._supervisor_task.cancelled() else self._supervisor_task.exception()
            raise StreamClosedError(
                f"{self._closed_message}: could not connect to {self._url}"
            ) from cause
        raise TimeoutError(f"timed out after {timeout}s connecting to {self._url}")

    async def close(self) -> None:
        """Terminally close the stream; iterators end, no reconnects."""
        if self._closed:
            return
        self._closed = True
        # Close the socket *before* cancelling. The supervisor is normally parked on
        # recv() inside a timeout, and asyncio can drop a cancellation that races the
        # recv completing — close() would then block until the watchdog fired. Closing
        # the socket ends the read loop deterministically; the cancel below is only a
        # backstop for a supervisor sleeping between reconnects.
        await self._close_ws()
        if self._supervisor_task is not None:
            self._supervisor_task.cancel()
            try:
                await self._supervisor_task
            except asyncio.CancelledError:
                # Expected: we just cancelled it. But if the caller cancelled *us*
                # while we waited, that cancellation has to keep propagating.
                current = asyncio.current_task()
                if current is not None and current.cancelling():
                    raise
            except Exception:  # noqa: BLE001
                # close() runs from __aexit__, where raising would replace whatever
                # exception the caller's `async with` body was already propagating.
                logger.exception("connection supervisor failed during close")
        await self._drain_callbacks()
        self._wake_consumers()

    async def _drain_callbacks(self, grace: float = 1.0) -> None:
        """Let in-flight async callbacks finish, then cancel whatever is still running.

        Without this they outlive the stream and surface as "Task was destroyed but
        it is pending" once the loop shuts down.
        """
        pending = set(self._callback_tasks)
        if not pending:
            return
        _, still_running = await asyncio.wait(pending, timeout=grace)
        for task in still_running:
            task.cancel()
        if still_running:
            await asyncio.wait(still_running)

    def _wake_consumers(self) -> None:
        """End every registered iterator."""
        for _, queue in self._queues:
            self._offer(queue, CLOSED)

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def is_connected(self) -> bool:
        """True once the current connection's handshake has finished.

        The socket exists a little earlier than this, while the handshake is still
        in flight — a subscribe that sends on it then lands before the server-side
        session exists (or duplicates what the handshake is about to replay), so
        subscribe/unsubscribe key their "send now or let the handshake do it"
        decision on this, not on the socket.
        """
        return self._connected.is_set()

    # ------------------------------------------------------------- consumers

    def updates(self, *symbols: str) -> AsyncIterator[U]:
        """Async iterator over updates (optionally filtered to symbols)."""
        if self._closed:
            raise StreamClosedError(self._closed_message)
        symbol_filter = frozenset(symbols) if symbols else None
        queue: asyncio.Queue = asyncio.Queue(self._queue_size)
        entry: _QueueEntry = (symbol_filter, queue)
        # Registered eagerly so updates arriving before the first `async for` are buffered.
        self._queues.append(entry)

        async def gen() -> AsyncIterator[U]:
            try:
                while True:
                    item = await queue.get()
                    if item is CLOSED:
                        return
                    yield item
            finally:
                _discard(self._queues, entry)

        iterator = gen()
        # A generator that is never started never runs its `finally`, so also drop the
        # queue when the iterator itself is collected — otherwise an iterator that is
        # built and discarded leaks a queue that every dispatch keeps filling.
        finalizer = weakref.finalize(iterator, _discard, self._queues, entry)
        finalizer.atexit = False
        return iterator

    def on_update(self, callback: Callable[[U], Any]) -> Callable[[], None]:
        """Register a sync or async callback; returns an unregister function."""
        self._callbacks.append(callback)

        def unregister() -> None:
            with contextlib.suppress(ValueError):
                self._callbacks.remove(callback)

        return unregister

    def _dispatch(self, update: U) -> None:
        for symbol_filter, queue in self._queues:
            if symbol_filter is None or update.symbol in symbol_filter:
                self._offer(queue, update)
        for callback in list(self._callbacks):
            try:
                result = callback(update)
            except Exception:  # noqa: BLE001
                logger.exception("on_update callback failed")
                continue
            if inspect.isawaitable(result):
                self._spawn_callback(result)

    def _spawn_callback(self, awaitable: Any) -> None:
        """Drive an async callback, holding the task so it is not collected mid-flight."""
        task = asyncio.ensure_future(awaitable)
        self._callback_tasks.add(task)
        task.add_done_callback(self._callback_finished)

    def _callback_finished(self, task: asyncio.Task) -> None:
        self._callback_tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            logger.error("on_update callback failed", exc_info=task.exception())

    @staticmethod
    def _offer(queue: asyncio.Queue, item: Any) -> None:
        """Non-blocking put with drop-oldest overflow (newest data wins)."""
        while True:
            try:
                queue.put_nowait(item)
                return
            except asyncio.QueueFull:
                with contextlib.suppress(asyncio.QueueEmpty):
                    queue.get_nowait()

    # ------------------------------------------------------- connection loop

    async def _supervise(self) -> None:
        attempt = 0
        while not self._closed:
            self._connected_at = None
            try:
                await self._connect_and_run()
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.debug("connection error: %r", exc)
            finally:
                connected_at = self._connected_at
                self._connected.clear()
                await self._close_ws()
            if not self._reconnect or self._closed:
                break
            if connected_at and time.monotonic() - connected_at > STABLE_CONNECTION:
                attempt = 0
            # The exponent is clamped: an endpoint that stays unreachable for hours
            # would otherwise grow 2**attempt past what float() can represent.
            delay = min(_MAX_BACKOFF, 0.5 * 2**attempt) * (1 + random.random() * 0.4)
            attempt = min(attempt + 1, _MAX_BACKOFF_EXPONENT)
            logger.debug("reconnecting in %.1fs", delay)
            await asyncio.sleep(delay)
        # terminal exit: wake all consumers
        self._closed = True
        self._wake_consumers()

    async def _connect_and_run(self) -> None:
        token = await resolve_ws_token(self._auth)
        async with websockets.connect(
            self._url,
            additional_headers={"Origin": WS_ORIGIN},
            user_agent_header=BASE_HEADERS["User-Agent"],
            max_size=2**24,
        ) as ws:
            self._ws = ws
            await self._handshake(token)
            self._connected_at = time.monotonic()
            self._connected.set()
            while True:
                async with asyncio.timeout(RECV_TIMEOUT):
                    frame = await ws.recv()
                for message in decode_frame(frame):
                    if is_heartbeat(message):
                        await self._send_raw(wrap_raw(message))
                        continue
                    await self._handle_message(message)

    async def _close_ws(self) -> None:
        ws, self._ws = self._ws, None
        if ws is not None:
            with contextlib.suppress(Exception):
                await ws.close()

    async def _send(self, method: str, params: list[Any]) -> None:
        await self._send_raw(encode_message(method, params))

    async def _send_raw(self, payload: str) -> None:
        ws = self._ws
        if ws is None:
            return
        async with self._send_lock:
            await ws.send(payload)

    # -------------------------------------------------------------- messages

    async def _handle_message(self, message: str) -> None:
        data = parse_json_message(message)
        if data is None:
            return  # server hello / non-JSON payloads
        method = data.get("m")
        params = data.get("p") or []
        if method in FATAL_METHODS and not self._absorb_error(method, params):
            logger.warning("server sent %s: %s", method, str(params)[:200])
            raise ConnectionError(f"TradingView sent {method}")
        try:
            self._handle_data(method, params)
        except Exception:  # noqa: BLE001
            # Dropping the socket over one bad payload forces a full reconnect and
            # resubscribe, and repeats for every replay of that payload.
            logger.exception("could not handle %s message", method)

    # ----------------------------------------------------- subclass contract

    async def _handshake(self, token: str) -> None:
        """Authenticate and (re)create the server-side sessions on a fresh connection."""
        raise NotImplementedError

    def _absorb_error(self, method: str, params: list[Any]) -> bool:
        """Return True if a ``critical_error``/``protocol_error`` is scoped narrowly
        enough to handle in place, so the connection is kept rather than dropped.

        The default treats every one as fatal. A subclass whose server-side
        sessions can fail independently overrides this, because reconnecting
        would recreate the same failing session and loop forever.
        """
        return False

    def _handle_data(self, method: str | None, params: list[Any]) -> None:
        """Handle one decoded, non-fatal protocol message."""
        raise NotImplementedError
