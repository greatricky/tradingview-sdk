from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest

from tradingview_sdk._http import RequestSpec, execute_sync, retry_after_seconds
from tradingview_sdk.errors import RateLimitError


def test_retry_after_accepts_delta_seconds():
    assert retry_after_seconds("120") == 120.0
    assert retry_after_seconds(" 30 ") == 30.0


def test_retry_after_accepts_http_date():
    # RFC 9110 allows either form; a CDN in front of TradingView may send the date.
    when = datetime.now(timezone.utc) + timedelta(seconds=90)
    seconds = retry_after_seconds(format_datetime(when, usegmt=True))
    assert seconds is not None and 60 <= seconds <= 120


def test_retry_after_past_date_clamps_to_zero():
    assert retry_after_seconds("Wed, 21 Oct 2015 07:28:00 GMT") == 0.0


def test_retry_after_ignores_junk():
    assert retry_after_seconds(None) is None
    assert retry_after_seconds("") is None
    assert retry_after_seconds("soon") is None


def test_http_date_429_still_raises_rate_limit_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}, text="slow down")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(RateLimitError) as excinfo:
            execute_sync(client, RequestSpec("GET", "https://example.test/"), retries=0)
    assert excinfo.value.retry_after == 0.0
