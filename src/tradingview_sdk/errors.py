"""Exception hierarchy for tradingview_sdk."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import BarSet


class TradingViewError(Exception):
    """Base class for all tradingview_sdk errors."""


class HTTPStatusError(TradingViewError):
    """A TradingView endpoint returned an unexpected HTTP status."""

    def __init__(self, status: int, url: str, body_snippet: str = ""):
        self.status = status
        self.url = url
        self.body_snippet = body_snippet
        super().__init__(f"HTTP {status} from {url}: {body_snippet[:200]}")


class RateLimitError(HTTPStatusError):
    """HTTP 429 — slow down."""

    def __init__(self, url: str, body_snippet: str = "", retry_after: float | None = None):
        self.retry_after = retry_after
        super().__init__(429, url, body_snippet)


class AuthRequiredError(HTTPStatusError):
    """The resource requires a logged-in TradingView session (or is not public)."""

    def __init__(self, url: str, body_snippet: str = "", status: int = 401):
        super().__init__(status, url, body_snippet)


class SymbolNotFoundError(TradingViewError):
    """No instrument matched the given symbol/query."""


class ParseError(TradingViewError):
    """A TradingView response did not have the expected shape.

    TradingView's markup/JSON may have changed; consider updating the SDK.
    """


class ProtocolError(TradingViewError):
    """Malformed websocket frame or unexpected protocol message."""


class BarTimeoutError(ProtocolError, TimeoutError):
    """A chart session went silent past its watchdog before any bars arrived.

    This is the one bars failure worth retrying: the server never answered, so the
    same request may well succeed on the next attempt or another connection. A
    plain :class:`ProtocolError` (the server rejected the request) and a
    :class:`SymbolNotFoundError` (wrong ticker or wrong exchange) are verdicts, not
    stalls — retrying those only burns time.

    Subclasses ``ProtocolError`` so pre-existing ``except ProtocolError`` handlers
    keep catching it, and the builtin ``TimeoutError`` to match how the streaming
    client reports a connect timeout.
    """


class IncompleteBarsError(BarTimeoutError):
    """A chart session stalled or hit its deadline AFTER some bars had arrived.

    Raised only by ``fetch_bars(strict=True)`` / ``get_bars(strict=True)``; the
    default mode returns the partial set flagged ``raw["truncated"] = True``
    instead. ``bars`` is exactly that partial :class:`~tradingview_sdk.BarSet`, so
    a caller that wants it still has it. Subclasses :class:`BarTimeoutError`
    because the remedy is the same — retry — and a session that produced nothing
    at all still raises the plain parent.
    """

    def __init__(self, message: str, bars: BarSet):
        self.bars = bars
        super().__init__(message)

    def __reduce__(self):
        # ``bars`` is not in ``args``, so the default reduce would rebuild this
        # without it; matters when the error crosses a process boundary.
        return type(self), (self.args[0], self.bars)


class StreamClosedError(TradingViewError):
    """The quote stream was closed and will not reconnect."""
