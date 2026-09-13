"""Shared HTTP plumbing: request specs, headers, retries, error mapping."""

from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import httpx

from .errors import AuthRequiredError, HTTPStatusError, RateLimitError

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)

BASE_HEADERS = {
    "User-Agent": USER_AGENT,
    "Origin": "https://www.tradingview.com",
    "Referer": "https://www.tradingview.com/",
    "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass(frozen=True)
class RequestSpec:
    """A declarative HTTP request; executed by either the sync or async client."""

    method: str
    url: str
    params: dict[str, Any] | None = None
    json_body: Any = None
    headers: dict[str, str] = field(default_factory=dict)


def retry_after_seconds(value: str | None) -> float | None:
    """Seconds to wait from a ``Retry-After`` header.

    RFC 9110 allows either delta-seconds or an HTTP-date; a CDN or WAF in front of
    TradingView may well send the date form. Unparseable values yield None rather
    than replacing the RateLimitError the caller is trying to raise.
    """
    if not value:
        return None
    value = value.strip()
    try:
        return float(value)
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def _check_response(resp: httpx.Response) -> httpx.Response:
    if resp.status_code < 400:
        return resp
    url = str(resp.request.url)
    snippet = resp.text[:300]
    if resp.status_code == 429:
        raise RateLimitError(url, snippet, retry_after_seconds(resp.headers.get("Retry-After")))
    if resp.status_code in (401, 403):
        raise AuthRequiredError(url, snippet, status=resp.status_code)
    raise HTTPStatusError(resp.status_code, url, snippet)


def _retryable(exc: Exception) -> bool:
    # Every request this SDK makes is a read, so a retry after a torn connection or
    # a timeout at any stage (pool, connect, write, read) cannot double-apply anything.
    if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError)):
        return True
    return isinstance(exc, HTTPStatusError) and not isinstance(exc, (RateLimitError, AuthRequiredError)) and exc.status >= 500


def _backoff(attempt: int) -> float:
    return min(2.0, 0.3 * (2**attempt)) * (1 + random.random() * 0.3)


def execute_sync(client: httpx.Client, spec: RequestSpec, retries: int = 2) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = client.request(
                spec.method, spec.url, params=spec.params, json=spec.json_body, headers=spec.headers or None
            )
            return _check_response(resp)
        except Exception as exc:  # noqa: BLE001
            if attempt < retries and _retryable(exc):
                last_exc = exc
                time.sleep(_backoff(attempt))
                continue
            raise
    raise last_exc  # pragma: no cover — unreachable


async def execute_async(client: httpx.AsyncClient, spec: RequestSpec, retries: int = 2) -> httpx.Response:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = await client.request(
                spec.method, spec.url, params=spec.params, json=spec.json_body, headers=spec.headers or None
            )
            return _check_response(resp)
        except Exception as exc:  # noqa: BLE001
            if attempt < retries and _retryable(exc):
                last_exc = exc
                await asyncio.sleep(_backoff(attempt))
                continue
            raise
    raise last_exc  # pragma: no cover — unreachable
