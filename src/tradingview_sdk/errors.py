"""Exception hierarchy for tradingview_sdk."""

from __future__ import annotations


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


class StreamClosedError(TradingViewError):
    """The quote stream was closed and will not reconnect."""
