"""Run an async coroutine to completion from synchronous code.

The websocket-backed features (bars) are implemented async; the sync facade needs
to drive them without an event loop of its own. ``run_coro_blocking`` uses
``asyncio.run`` normally, but falls back to a one-shot worker thread when it is
called from inside an already-running loop (so ``TradingView.get_bars`` stays
usable even from an async application, at the cost of a thread hop).
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any, Coroutine


def run_coro_blocking(coro: Coroutine[Any, Any, Any]) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # Inside a running loop: run the coroutine on a private loop in another thread.
    box: dict[str, Any] = {}

    def _runner() -> None:
        try:
            box["value"] = asyncio.run(coro)
        except BaseException as exc:  # noqa: BLE001 - re-raised on the caller's thread
            box["error"] = exc

    thread = threading.Thread(target=_runner, name="tv-sync-runner")
    thread.start()
    thread.join()
    if "error" in box:
        raise box["error"]
    return box["value"]
