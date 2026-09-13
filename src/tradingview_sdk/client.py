"""Sync and async TradingView client facades."""

from __future__ import annotations

import asyncio
import time
from dataclasses import replace
from datetime import date, datetime
from typing import Any, AsyncIterator, Iterator, Sequence

import httpx

from ._http import BASE_HEADERS, RequestSpec, execute_async, execute_sync
from ._sync import run_coro_blocking
from .auth import AuthTokenCache, Credentials
from .bars import DEFAULT_BAR_TIMEOUT, DEFAULT_BARS, Adjustment, Interval, fetch_bars
from .errors import SymbolNotFoundError
from .models import (
    BarSet,
    PineSource,
    Quote,
    ScreenerResult,
    Strategy,
    StrategyCard,
    StrategyPage,
    SymbolInfo,
)
from .quotes import DEFAULT_QUOTE_FIELDS, build_quote_request, parse_quote_response
from .screener import (
    ETF_SCREENER_DEFAULT,
    STOCK_SCREENER_DEFAULT,
    ScreenerQuery,
    build_screener_request,
    parse_screener_response,
)
from .scripts import (
    build_listing_request,
    build_pine_source_request,
    build_script_page_request,
    normalize_script_url,
    parse_listing_page,
    parse_pine_source,
    parse_script_page,
)
from .search import build_search_request, parse_search_response, pick_full_symbol

_PAGE_DELAY = 0.5  # politeness delay between listing page fetches


def _resolve_credentials(credentials: Credentials | None) -> Credentials:
    return credentials if credentials is not None else Credentials.from_env()


class AsyncTradingView:
    """Async client for TradingView's (unofficial) REST endpoints."""

    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        timeout: float = 15.0,
        retries: int = 2,
    ):
        self.credentials = _resolve_credentials(credentials)
        self._retries = retries
        # One cache for the client's lifetime: a per-call cache would never hit, so
        # every get_bars() would re-fetch the websocket token over HTTP.
        self._auth = AuthTokenCache(self.credentials)
        self._client = httpx.AsyncClient(
            headers=BASE_HEADERS,
            cookies=self.credentials.as_cookies(),
            timeout=timeout,
            follow_redirects=True,
        )

    async def __aenter__(self) -> "AsyncTradingView":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(self, spec: RequestSpec) -> httpx.Response:
        return await execute_async(self._client, spec, self._retries)

    # -- instrument info ---------------------------------------------------
    async def search_symbols(
        self,
        text: str,
        *,
        search_type: str | None = "stocks",
        exchange: str = "",
        country: str = "US",
        lang: str = "en",
    ) -> list[SymbolInfo]:
        """Search instruments. search_type: stocks|funds|futures|forex|crypto|index|bond|economic or None for all."""
        resp = await self._request(
            build_search_request(text, search_type=search_type, exchange=exchange, country=country, lang=lang)
        )
        return parse_search_response(resp.json())

    # -- latest quote ------------------------------------------------------
    async def get_quote(self, symbol: str, *, fields: Sequence[str] = DEFAULT_QUOTE_FIELDS) -> Quote:
        """Latest quote for "EXCHANGE:TICKER" (bare tickers are resolved via search)."""
        symbol = await self._resolve_symbol(symbol)
        resp = await self._request(build_quote_request(symbol, fields))
        return parse_quote_response(symbol, resp.json())

    # -- historical bars (OHLCV) ------------------------------------------
    async def get_bars(
        self,
        symbol: str,
        interval: str | Interval = Interval.DAY,
        *,
        bars: int = DEFAULT_BARS,
        start: datetime | date | int | float | None = None,
        end: datetime | date | int | float | None = None,
        adjustment: str | Adjustment = Adjustment.SPLITS,
        session: str | None = None,
        timeout: float = DEFAULT_BAR_TIMEOUT,
        deadline: float | None = None,
        strict: bool = False,
    ) -> BarSet:
        """Historical OHLCV bars for "EXCHANGE:TICKER" (bare tickers are resolved via search).

        ``bars`` is the number of most-recent candles; pass ``start`` (and optionally
        ``end``) to page back over a date range instead. Uses a one-shot chart-session
        websocket; anonymous access returns delayed data.

        ``session`` selects the trading session the candles are built from:
        ``"regular"`` or ``"extended"``. Left ``None`` it is not sent and the server
        picks, which is the request every earlier release made. The result's
        ``timezone`` and ``session`` fields report what the server resolved — the
        exchange zone its bar stamps are in and the trading-hours string — with the
        whole ``symbol_resolved`` reply on ``raw["symbol_resolved"]``.

        ``timeout`` (default :data:`~tradingview_sdk.DEFAULT_BAR_TIMEOUT`, 5s) is this
        call's websocket silence watchdog, separate from the constructor's ``timeout``,
        which is the HTTP read timeout for the REST endpoints. Raising one does not
        raise the other. It bounds the chart-session handshake and each wait for the
        next frame that carries progress — heartbeats do not count, so a session that
        stays chatty without delivering bars still trips it — and a stalled server
        costs ~``timeout`` plus a one-second close grace per attempt, raising
        :class:`~tradingview_sdk.BarTimeoutError`.

        ``timeout`` re-arms on every load round, so it bounds a stall but not the call.
        ``deadline`` is the total seconds the chart session may spend, defaulting to a
        loose backstop derived from ``timeout`` — high enough that a legitimate
        multi-round ``start=`` range never meets it, present so that a server which
        stays busy without ever finishing cannot hang the caller. Bars that already
        arrived come back with ``raw["truncated"] = True`` either way — unless
        ``strict=True``, which raises :class:`~tradingview_sdk.IncompleteBarsError`
        (a ``BarTimeoutError`` carrying that partial set on ``.bars``) instead, for a
        caller that must never mistake a short answer for a whole one. The same
        flag marks a fetch that used up its pagination rounds before covering
        the range asked for.

        Each load round arrives as one websocket frame — up to roughly 2 MB for a
        full chunk — that has to land within ``timeout``, so on a slow link (under
        about 3.5 Mbps) a deep series or large ``start=`` range can trip the
        watchdog with the server perfectly healthy; raise ``timeout`` there.

        Neither one covers resolving a bare ticker through ``search_symbols``, which
        happens before the session opens and runs under the constructor's ``timeout``.
        ``deadline`` does cover the websocket-token fetch, since that is the session's
        own first step; ``timeout`` does not.

        An unknown symbol, or a real ticker on the wrong exchange, raises
        ``SymbolNotFoundError`` as soon as the server rejects it — typically well under
        a second, never after waiting out the watchdog.
        """
        symbol = await self._resolve_symbol(symbol)
        return await fetch_bars(
            symbol=symbol,
            interval=str(interval),
            bars=bars,
            start=start,
            end=end,
            adjustment=adjustment,
            session=session,
            auth=self._auth,
            timeout=timeout,
            deadline=deadline,
            strict=strict,
        )

    async def _resolve_symbol(self, symbol: str) -> str:
        if ":" in symbol:
            return symbol
        matches = await self.search_symbols(symbol, search_type=None)
        full = pick_full_symbol(matches, symbol)
        if full is None:
            raise SymbolNotFoundError(f"No instrument found for {symbol!r}")
        return full

    # -- screeners ---------------------------------------------------------
    async def screen(self, query: ScreenerQuery) -> ScreenerResult:
        resp = await self._request(build_screener_request(query))
        return parse_screener_response(query, resp.json())

    async def screen_stocks(self, query: ScreenerQuery | None = None) -> ScreenerResult:
        """Stock screener (defaults mirror tradingview.com/screener/)."""
        return await self.screen(query if query is not None else STOCK_SCREENER_DEFAULT)

    async def screen_etfs(self, query: ScreenerQuery | None = None) -> ScreenerResult:
        """ETF screener (defaults mirror tradingview.com/etf-screener/)."""
        return await self.screen(query if query is not None else ETF_SCREENER_DEFAULT)

    # -- community strategies ---------------------------------------------
    async def list_strategies(self, *, page: int = 1, script_type: str = "strategies") -> StrategyPage:
        """One page of the community scripts listing.

        script_type: "strategies" (default), "indicators", "libraries", or "all"
        (see :data:`~tradingview_sdk.scripts.SCRIPT_TYPES`); anything else raises
        ``ValueError``. A page past the last one is an empty page with
        ``has_next`` False.
        """
        resp = await self._request(build_listing_request(page, script_type))
        return parse_listing_page(resp.text, page, final_url=str(resp.url))

    async def iter_strategies(
        self, *, max_pages: int | None = None, script_type: str = "strategies"
    ) -> AsyncIterator[StrategyCard]:
        """Walk the listing page by page (see :meth:`list_strategies` for script_type)."""
        page = 1
        while max_pages is None or page <= max_pages:
            result = await self.list_strategies(page=page, script_type=script_type)
            for card in result.cards:
                yield card
            if not result.has_next:
                return
            page += 1
            await asyncio.sleep(_PAGE_DELAY)

    async def get_strategy(self, slug_or_url: str, *, include_source: bool = True) -> Strategy:
        """Full strategy detail: metadata, published strategy report, and Pine source."""
        resp = await self._request(build_script_page_request(slug_or_url))
        strategy = parse_script_page(resp.text, slug_or_url)
        if include_source and strategy.script_id_part:
            source = await self.get_pine_source(strategy.script_id_part)
            strategy = _with_source(strategy, source)
        return strategy

    async def get_pine_source(self, script_id_part: str) -> PineSource:
        resp = await self._request(build_pine_source_request(script_id_part))
        return parse_pine_source(script_id_part, resp.json())


class TradingView:
    """Sync client with the same surface as :class:`AsyncTradingView`."""

    def __init__(
        self,
        *,
        credentials: Credentials | None = None,
        timeout: float = 15.0,
        retries: int = 2,
    ):
        self.credentials = _resolve_credentials(credentials)
        self._retries = retries
        self._auth = AuthTokenCache(self.credentials)
        self._client = httpx.Client(
            headers=BASE_HEADERS,
            cookies=self.credentials.as_cookies(),
            timeout=timeout,
            follow_redirects=True,
        )

    def __enter__(self) -> "TradingView":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def _request(self, spec: RequestSpec) -> httpx.Response:
        return execute_sync(self._client, spec, self._retries)

    def search_symbols(
        self,
        text: str,
        *,
        search_type: str | None = "stocks",
        exchange: str = "",
        country: str = "US",
        lang: str = "en",
    ) -> list[SymbolInfo]:
        resp = self._request(
            build_search_request(text, search_type=search_type, exchange=exchange, country=country, lang=lang)
        )
        return parse_search_response(resp.json())

    def get_quote(self, symbol: str, *, fields: Sequence[str] = DEFAULT_QUOTE_FIELDS) -> Quote:
        symbol = self._resolve_symbol(symbol)
        resp = self._request(build_quote_request(symbol, fields))
        return parse_quote_response(symbol, resp.json())

    def get_bars(
        self,
        symbol: str,
        interval: str | Interval = Interval.DAY,
        *,
        bars: int = DEFAULT_BARS,
        start: datetime | date | int | float | None = None,
        end: datetime | date | int | float | None = None,
        adjustment: str | Adjustment = Adjustment.SPLITS,
        session: str | None = None,
        timeout: float = DEFAULT_BAR_TIMEOUT,
        deadline: float | None = None,
        strict: bool = False,
    ) -> BarSet:
        """See :meth:`AsyncTradingView.get_bars`.

        ``timeout`` is the websocket silence watchdog for this call (default
        :data:`~tradingview_sdk.DEFAULT_BAR_TIMEOUT`), not the constructor's HTTP timeout;
        ``deadline`` is the total wall clock the chart session may spend. This form
        blocks a thread for the duration, so the bound matters more here than in the
        async one.
        """
        symbol = self._resolve_symbol(symbol)
        return run_coro_blocking(
            fetch_bars(
                symbol=symbol,
                interval=str(interval),
                bars=bars,
                start=start,
                end=end,
                adjustment=adjustment,
                session=session,
                auth=self._auth,
                timeout=timeout,
                deadline=deadline,
                strict=strict,
            )
        )

    def _resolve_symbol(self, symbol: str) -> str:
        if ":" in symbol:
            return symbol
        matches = self.search_symbols(symbol, search_type=None)
        full = pick_full_symbol(matches, symbol)
        if full is None:
            raise SymbolNotFoundError(f"No instrument found for {symbol!r}")
        return full

    def screen(self, query: ScreenerQuery) -> ScreenerResult:
        resp = self._request(build_screener_request(query))
        return parse_screener_response(query, resp.json())

    def screen_stocks(self, query: ScreenerQuery | None = None) -> ScreenerResult:
        return self.screen(query if query is not None else STOCK_SCREENER_DEFAULT)

    def screen_etfs(self, query: ScreenerQuery | None = None) -> ScreenerResult:
        return self.screen(query if query is not None else ETF_SCREENER_DEFAULT)

    def list_strategies(self, *, page: int = 1, script_type: str = "strategies") -> StrategyPage:
        """One page of the community scripts listing.

        script_type: "strategies" (default), "indicators", "libraries", or "all"
        (see :data:`~tradingview_sdk.scripts.SCRIPT_TYPES`); anything else raises
        ``ValueError``.
        """
        resp = self._request(build_listing_request(page, script_type))
        return parse_listing_page(resp.text, page, final_url=str(resp.url))

    def iter_strategies(
        self, *, max_pages: int | None = None, script_type: str = "strategies"
    ) -> Iterator[StrategyCard]:
        """Walk the listing page by page (see :meth:`list_strategies` for script_type)."""
        page = 1
        while max_pages is None or page <= max_pages:
            result = self.list_strategies(page=page, script_type=script_type)
            yield from result.cards
            if not result.has_next:
                return
            page += 1
            time.sleep(_PAGE_DELAY)

    def get_strategy(self, slug_or_url: str, *, include_source: bool = True) -> Strategy:
        resp = self._request(build_script_page_request(slug_or_url))
        strategy = parse_script_page(resp.text, slug_or_url)
        if include_source and strategy.script_id_part:
            source = self.get_pine_source(strategy.script_id_part)
            strategy = _with_source(strategy, source)
        return strategy

    def get_pine_source(self, script_id_part: str) -> PineSource:
        resp = self._request(build_pine_source_request(script_id_part))
        return parse_pine_source(script_id_part, resp.json())


def _with_source(strategy: Strategy, source: PineSource) -> Strategy:
    return replace(strategy, source=source)


__all__ = ["AsyncTradingView", "TradingView", "normalize_script_url"]
