"""QuoteStream behavior against a local fake TradingView server."""

import asyncio
import gc
import json
import time

import pytest
import websockets

from tradingview_sdk import _stream
from tradingview_sdk._protocol import decode_frame, parse_json_message, wrap_raw
from tradingview_sdk.ws import QuoteStream


class FakeTVServer:
    """Minimal ~m~-speaking server: replies to quote_add_symbols with qsd."""

    def __init__(self):
        self.received: list[dict] = []
        self.heartbeat_echoes: list[str] = []
        self.connections = 0
        self.subscribed_per_connection: list[list[str]] = []
        self._server = None
        self.drop_next = asyncio.Event()

    async def start(self):
        self._server = await websockets.serve(self._handler, "127.0.0.1", 0)
        port = self._server.sockets[0].getsockname()[1]
        return f"ws://127.0.0.1:{port}/socket.io/websocket"

    async def stop(self):
        self._server.close()
        await self._server.wait_closed()

    async def _handler(self, ws):
        self.connections += 1
        self.subscribed_per_connection.append([])
        conn_subs = self.subscribed_per_connection[-1]
        await ws.send(wrap_raw(json.dumps({"session_id": "fake", "protocol": "json"})))
        await ws.send(wrap_raw("~h~1"))
        try:
            async for frame in ws:
                for message in decode_frame(frame):
                    if message.startswith("~h~"):
                        self.heartbeat_echoes.append(message)
                        continue
                    data = parse_json_message(message)
                    if not data:
                        continue
                    self.received.append(data)
                    if data["m"] == "quote_add_symbols":
                        session = data["p"][0]
                        for symbol in data["p"][1:]:
                            conn_subs.append(symbol)
                            body = {"n": symbol, "s": "ok", "v": {"lp": 100.0 + len(symbol), "volume": 1}}
                            await ws.send(wrap_raw(json.dumps({"m": "qsd", "p": [session, body]})))
                            await ws.send(wrap_raw(json.dumps({"m": "quote_completed", "p": [session, symbol]})))
                    if self.drop_next.is_set():
                        self.drop_next.clear()
                        await ws.close()
                        return
        except websockets.ConnectionClosed:
            pass


@pytest.fixture
async def fake_server():
    server = FakeTVServer()
    url = await server.start()
    yield server, url
    await server.stop()


async def test_handshake_subscribe_and_updates(fake_server):
    server, url = fake_server
    async with QuoteStream(url=url) as stream:
        await stream.subscribe("NASDAQ:AAPL", "BINANCE:BTCUSDT")
        seen = {}
        async with asyncio.timeout(5):
            async for update in stream.updates():
                seen[update.symbol] = update.last_price
                if len(seen) == 2:
                    break
        assert set(seen) == {"NASDAQ:AAPL", "BINANCE:BTCUSDT"}
        assert stream.snapshot("NASDAQ:AAPL")["lp"] == seen["NASDAQ:AAPL"]

    methods = [m["m"] for m in server.received]
    assert methods[:3] == ["set_auth_token", "quote_create_session", "quote_set_fields"]
    assert server.received[0]["p"] == ["unauthorized_user_token"]
    assert "quote_add_symbols" in methods


async def test_heartbeat_echoed(fake_server):
    server, url = fake_server
    async with QuoteStream(url=url) as stream:
        await stream.subscribe("X:Y")
        async with asyncio.timeout(5):
            while not server.heartbeat_echoes:
                await asyncio.sleep(0.02)
    assert server.heartbeat_echoes[0] == "~h~1"


async def test_unsubscribe_sends_remove(fake_server):
    server, url = fake_server
    async with QuoteStream(url=url) as stream:
        await stream.subscribe("A:B", "C:D")
        await stream.unsubscribe("A:B")
        assert stream.subscriptions == frozenset({"C:D"})
        async with asyncio.timeout(5):
            while not any(m["m"] == "quote_remove_symbols" for m in server.received):
                await asyncio.sleep(0.02)
        remove = next(m for m in server.received if m["m"] == "quote_remove_symbols")
        assert remove["p"][1:] == ["A:B"]


async def test_reconnect_resubscribes(fake_server):
    server, url = fake_server
    async with QuoteStream(url=url) as stream:
        await stream.subscribe("A:B")
        async with asyncio.timeout(5):
            async for update in stream.updates("A:B"):
                break
        server.drop_next.set()
        await stream.subscribe("C:D")  # triggers a send; server then drops the connection
        async with asyncio.timeout(10):
            while server.connections < 2 or "C:D" not in (
                server.subscribed_per_connection[-1] if server.subscribed_per_connection else []
            ):
                await asyncio.sleep(0.05)
        # second connection got the full desired set replayed
        assert set(server.subscribed_per_connection[-1]) == {"A:B", "C:D"}


async def test_close_ends_iterators(fake_server):
    _, url = fake_server
    stream = QuoteStream(url=url)
    await stream.start()
    await stream.subscribe("A:B")
    iterator = stream.updates()

    async def consume():
        items = []
        async for update in iterator:
            items.append(update)
        return items

    task = asyncio.create_task(consume())
    await asyncio.sleep(0.3)
    await stream.close()
    async with asyncio.timeout(5):
        await task  # iterator ends instead of hanging


async def test_close_does_not_wait_out_the_recv_watchdog(fake_server):
    # close() used to block for the full _RECV_TIMEOUT because cancelling the
    # supervisor does not reliably interrupt the recv() it is parked on.
    _, url = fake_server
    stream = QuoteStream(url=url)
    await stream.start()
    await stream.subscribe("A:B")
    started = time.monotonic()
    await stream.close()
    assert time.monotonic() - started < 2.0


async def test_unstarted_iterator_does_not_leak_its_queue(fake_server):
    # A generator that is never iterated never runs its finally clause, so the
    # queue has to be dropped when the iterator itself is collected.
    _, url = fake_server
    stream = QuoteStream(url=url)
    await stream.start()
    for _ in range(3):
        stream.updates("A:B")  # built and immediately discarded
    gc.collect()
    assert stream._queues == []
    await stream.close()


async def test_async_callback_completes_and_logs_its_errors(fake_server, caplog):
    _, url = fake_server
    finished = asyncio.Event()

    async def handler(update):
        await asyncio.sleep(0)  # a real handler awaits; the task must survive that
        finished.set()
        raise RuntimeError("boom")

    async with QuoteStream(url=url) as stream:
        stream.on_update(handler)
        await stream.subscribe("A:B")
        async with asyncio.timeout(5):
            await finished.wait()
            while stream._callback_tasks:
                await asyncio.sleep(0.01)

    assert any("on_update callback failed" in r.getMessage() for r in caplog.records)


async def test_reconnect_backoff_exponent_is_clamped(monkeypatch):
    # An endpoint that stays unreachable must not grow 2**attempt until float()
    # overflows and kills the supervisor without waking its consumers.
    delays: list[float] = []

    class Stop(Exception):
        pass

    async def fake_sleep(delay):
        delays.append(delay)
        if len(delays) >= 1500:
            raise Stop

    async def always_fails():
        raise ConnectionError("unreachable")

    stream = QuoteStream(url="ws://127.0.0.1:1/nope")
    monkeypatch.setattr(stream, "_connect_and_run", always_fails)
    monkeypatch.setattr(_stream.asyncio, "sleep", fake_sleep)

    with pytest.raises(Stop):
        await stream._supervise()

    assert len(delays) == 1500
    assert max(delays) <= _stream._MAX_BACKOFF * 1.4


async def test_slow_consumer_drops_oldest(fake_server):
    _, url = fake_server
    stream = QuoteStream(url=url)
    stream._queue_size = 2
    queue: asyncio.Queue = asyncio.Queue(2)
    stream._queues.append((None, queue))
    for i in range(5):
        stream._offer(queue, i)
    assert queue.qsize() == 2
    assert queue.get_nowait() == 3
    assert queue.get_nowait() == 4
    await stream.close()
