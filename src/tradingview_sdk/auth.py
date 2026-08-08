"""Credentials and websocket auth-token resolution."""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import time
from dataclasses import dataclass

import httpx

from ._http import BASE_HEADERS

logger = logging.getLogger("tradingview_sdk.auth")

ANONYMOUS_TOKEN = "unauthorized_user_token"

_QUOTE_TOKEN_URL = "https://www.tradingview.com/quote_token/"
_HOME_URL = "https://www.tradingview.com/"

_AUTH_TOKEN_RE = re.compile(r'"auth_token"\s*:\s*"([^"]+)"')


@dataclass(frozen=True)
class Credentials:
    """Optional TradingView session cookies.

    Copy ``sessionid`` and ``sessionid_sign`` from your logged-in browser
    (DevTools -> Application -> Cookies -> tradingview.com).
    """

    session_id: str | None = None
    session_sign: str | None = None

    @classmethod
    def from_env(cls) -> "Credentials":
        return cls(
            session_id=os.environ.get("TV_SESSION_ID") or None,
            session_sign=os.environ.get("TV_SESSION_ID_SIGN") or None,
        )

    @property
    def is_authenticated(self) -> bool:
        return bool(self.session_id)

    def as_cookies(self) -> dict[str, str]:
        cookies: dict[str, str] = {}
        if self.session_id:
            cookies["sessionid"] = self.session_id
        if self.session_sign:
            cookies["sessionid_sign"] = self.session_sign
        return cookies


def _jwt_exp(token: str) -> float | None:
    """Best-effort read of a JWT's exp claim without verifying the signature."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        exp = claims.get("exp")
        return float(exp) if exp is not None else None
    except Exception:
        return None


class AuthTokenCache:
    """Resolves and caches the websocket auth token for a set of credentials."""

    def __init__(self, credentials: Credentials | None):
        self._credentials = credentials or Credentials()
        self._token: str | None = None
        self._expires_at: float | None = None

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    def cached(self) -> str | None:
        if self._token is None:
            return None
        if self._expires_at is not None and time.time() > self._expires_at - 60:
            return None
        return self._token

    def store(self, token: str) -> str:
        self._token = token
        self._expires_at = _jwt_exp(token)
        return token

    @staticmethod
    def extract_from_html(html: str) -> str | None:
        m = _AUTH_TOKEN_RE.search(html)
        return m.group(1) if m else None


async def resolve_ws_token(auth: AuthTokenCache) -> str:
    """Resolve the websocket auth token for a set of credentials.

    Anonymous credentials yield the shared ``unauthorized_user_token`` (delayed
    data). Authenticated credentials fetch — and cache — a per-session JWT from the
    dedicated quote-token endpoint, falling back to scraping the home page. Shared
    by every websocket client (:class:`~tradingview_sdk.ws.QuoteStream`, the bars
    fetcher, and :class:`~tradingview_sdk.bar_stream.BarStream`).
    """
    creds = auth.credentials
    if not creds.is_authenticated:
        return ANONYMOUS_TOKEN
    cached = auth.cached()
    if cached:
        return cached
    async with httpx.AsyncClient(
        headers=BASE_HEADERS, cookies=creds.as_cookies(), timeout=15.0, follow_redirects=True
    ) as client:
        # Preferred: dedicated quote-token endpoint.
        try:
            resp = await client.get(_QUOTE_TOKEN_URL)
            if resp.status_code == 200:
                token = resp.json() if resp.text.startswith('"') else resp.text.strip().strip('"')
                if isinstance(token, str) and token:
                    return auth.store(token)
        except (httpx.HTTPError, ValueError):
            pass
        # Fallback: scrape auth_token from the home page.
        try:
            resp = await client.get(_HOME_URL)
            token = AuthTokenCache.extract_from_html(resp.text)
            if token:
                return auth.store(token)
        except httpx.HTTPError:
            pass
    logger.warning("could not fetch authenticated WS token; falling back to anonymous (delayed) data")
    return ANONYMOUS_TOKEN
