"""Community scripts: strategy listing, detail (report), and Pine source."""

from __future__ import annotations

import html
import json
import re
from typing import Any, Callable, Iterator
from urllib.parse import quote

from selectolax.parser import HTMLParser

from ._http import RequestSpec
from .errors import ParseError
from .models import (
    PineSource,
    Strategy,
    StrategyCard,
    StrategyPage,
    StrategyReport,
    StrategyStats,
)

BASE_URL = "https://www.tradingview.com"
PINE_FACADE_URL = "https://pine-facade.tradingview.com/pine-facade/get/{script_id}/last"

#: Listing filters accepted by /scripts/. Anything else 404s upstream.
SCRIPT_TYPES: tuple[str, ...] = ("strategies", "indicators", "libraries", "all")

_SLUG_RE = re.compile(r"/script/([^/?#]+)")


# ---------------------------------------------------------------------------
# Embedded init-data extraction
# ---------------------------------------------------------------------------

def iter_init_data_blobs(html: str) -> Iterator[dict[str, Any]]:
    """Yield each parsed ``application/prs.init-data+json`` blob on a page."""
    tree = HTMLParser(html)
    for node in tree.css('script[type="application/prs.init-data+json"]'):
        text = node.text(deep=True)
        if not text:
            continue
        try:
            data = json.loads(text)
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict):
            yield data


def find_in_init_data(html: str, predicate: Callable[[Any], bool]) -> Any:
    """Depth-first search of all init-data blobs for a value matching predicate."""

    def walk(obj: Any) -> Any:
        if predicate(obj):
            return obj
        if isinstance(obj, dict):
            for v in obj.values():
                found = walk(v)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for v in obj:
                found = walk(v)
                if found is not None:
                    return found
        return None

    for blob in iter_init_data_blobs(html):
        found = walk(blob)
        if found is not None:
            return found
    return None


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def build_listing_request(page: int = 1, script_type: str = "strategies") -> RequestSpec:
    if script_type not in SCRIPT_TYPES:
        raise ValueError(
            f"invalid script_type {script_type!r}; expected one of {', '.join(SCRIPT_TYPES)}"
        )
    path = "/scripts/" if page <= 1 else f"/scripts/page-{page}/"
    return RequestSpec(
        "GET",
        f"{BASE_URL}{path}",
        params={"script_type": script_type},
        headers={"Accept": "text/html"},
    )


def _card_from_item(item: dict[str, Any]) -> StrategyCard:
    url = item.get("chart_url") or ""
    if url.startswith("/"):
        url = BASE_URL + url
    m = _SLUG_RE.search(url)
    slug = m.group(1) if m else str(item.get("image_url") or item.get("id") or "")
    user = item.get("user") or {}
    symbol = item.get("symbol") or {}
    return StrategyCard(
        slug=slug,
        title=item.get("name") or "",
        url=url,
        author=user.get("username"),
        likes=item.get("likes_count"),
        script_id_part=item.get("script_id_part"),
        script_type=item.get("script_type"),
        symbol=symbol.get("full_name") or symbol.get("name"),
        created_at=item.get("created_at"),
        raw=item,
    )


def parse_listing_page(html: str, page: int = 1) -> StrategyPage:
    """Parse a /scripts/ listing page into cards.

    Prefers the embedded init-data JSON (rich card data); falls back to
    scraping ``/script/<slug>`` anchors when the blob is absent.
    """
    ideas = find_in_init_data(
        html,
        lambda o: isinstance(o, dict) and "items" in o and "total" in o and isinstance(o.get("items"), list),
    )
    if ideas and ideas["items"] and isinstance(ideas["items"][0], dict) and "chart_url" in ideas["items"][0]:
        cards = [_card_from_item(item) for item in ideas["items"]]
        return StrategyPage(cards=cards, page=page, has_next=bool(ideas.get("next")))

    # Fallback: anchor scraping (degraded: no author/likes).
    tree = HTMLParser(html)
    seen: set[str] = set()
    cards = []
    for node in tree.css('a[href*="/script/"]'):
        href = node.attributes.get("href") or ""
        m = _SLUG_RE.search(href)
        if not m or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        title = (node.text(deep=True) or "").strip()
        cards.append(
            StrategyCard(
                slug=m.group(1),
                title=title,
                url=f"{BASE_URL}/script/{m.group(1)}/",
                author=None,
                likes=None,
                script_id_part=None,
                script_type=None,
                symbol=None,
                created_at=None,
                raw={"href": href},
            )
        )
    if not cards:
        raise ParseError(
            "Could not find script cards on listing page; TradingView markup may have changed."
        )
    return StrategyPage(cards=cards, page=page, has_next=f"/scripts/page-{page + 1}/" in html)


# ---------------------------------------------------------------------------
# Detail page
# ---------------------------------------------------------------------------

def normalize_script_url(slug_or_url: str) -> tuple[str, str]:
    """Accept a slug, ``/script/...`` path, or full URL; return (slug, url)."""
    m = _SLUG_RE.search(slug_or_url)
    slug = m.group(1) if m else slug_or_url.strip("/")
    return slug, f"{BASE_URL}/script/{slug}/"


def build_script_page_request(slug_or_url: str) -> RequestSpec:
    _, url = normalize_script_url(slug_or_url)
    return RequestSpec("GET", url, headers={"Accept": "text/html"})


def _stats_from_group(group: Any) -> StrategyStats | None:
    if not isinstance(group, dict):
        return None
    return StrategyStats(
        net_profit=group.get("netProfit"),
        net_profit_percent=group.get("netProfitPercent"),
        gross_profit=group.get("grossProfit"),
        gross_loss=group.get("grossLoss"),
        percent_profitable=group.get("percentProfitable"),
        profit_factor=group.get("profitFactor"),
        total_trades=group.get("totalTrades"),
        winning_trades=group.get("numberOfWiningTrades"),
        losing_trades=group.get("numberOfLosingTrades"),
        avg_trade=group.get("avgTrade"),
        commission_paid=group.get("commissionPaid"),
        raw=group,
    )


def parse_report_data(report_data: dict[str, Any]) -> StrategyReport:
    perf = report_data.get("performance") or {}
    settings = report_data.get("settings") or {}
    return StrategyReport(
        currency=report_data.get("currency"),
        date_range=settings.get("dateRange") or {},
        all=_stats_from_group(perf.get("all")),
        long=_stats_from_group(perf.get("long")),
        short=_stats_from_group(perf.get("short")),
        max_drawdown=perf.get("maxStrategyDrawDown"),
        max_drawdown_percent=perf.get("maxStrategyDrawDownPercent"),
        sharpe_ratio=perf.get("sharpeRatio"),
        sortino_ratio=perf.get("sortinoRatio"),
        open_pl=perf.get("openPL"),
        buy_hold_return=perf.get("buyHoldReturn"),
        buy_hold_curve=report_data.get("buyHold") or [],
        trades=report_data.get("trades") or [],
        raw=report_data,
    )


def _find_report_data(chart_content: Any) -> dict[str, Any] | None:
    """Locate reportData in the published chart state (StudyStrategy source)."""

    def walk(obj: Any) -> dict[str, Any] | None:
        if isinstance(obj, dict):
            rd = obj.get("reportData")
            if isinstance(rd, dict) and "performance" in rd:
                return rd
            for v in obj.values():
                found = walk(v)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for v in obj:
                found = walk(v)
                if found is not None:
                    return found
        return None

    return walk(chart_content)


def parse_script_page(html: str, slug_or_url: str) -> Strategy:
    slug, url = normalize_script_url(slug_or_url)
    # A deleted or access-restricted script still carries the key, with a null value.
    idea = find_in_init_data(
        html,
        lambda o: isinstance(o, dict) and isinstance(o.get("ssrIdeaData"), dict),
    )
    if not idea:
        raise ParseError(
            f"Could not find script data on {url}; TradingView markup may have changed."
        )
    idea = idea["ssrIdeaData"]
    script = idea.get("script") or {}
    user = idea.get("user") or {}
    symbol = idea.get("symbol") or {}

    report: StrategyReport | None = None
    content = idea.get("content")
    if isinstance(content, str) and content:
        try:
            chart = json.loads(content)
        except ValueError:
            chart = None
        if chart is not None:
            report_data = _find_report_data(chart)
            if report_data:
                report = parse_report_data(report_data)

    return Strategy(
        slug=slug,
        url=url,
        title=idea.get("name") or "",
        author=user.get("username"),
        script_id_part=script.get("script_id_part"),
        version=str(script.get("version_maj")) if script.get("version_maj") is not None else None,
        chart_symbol=symbol.get("pro_symbol") or symbol.get("full_name"),
        chart_interval=str(idea.get("interval")) if idea.get("interval") is not None else None,
        likes=idea.get("likes_count"),
        is_strategy=(script.get("script_type") == "strategy"),
        report=report,
        source=None,
        raw=idea,
    )


# ---------------------------------------------------------------------------
# Pine source (pine-facade)
# ---------------------------------------------------------------------------

def build_pine_source_request(script_id_part: str) -> RequestSpec:
    return RequestSpec("GET", PINE_FACADE_URL.format(script_id=quote(script_id_part, safe="")))


def parse_pine_source(script_id_part: str, data: Any) -> PineSource:
    if not isinstance(data, dict) or "source" not in data:
        raise ParseError(f"Unexpected pine-facade response: {str(data)[:200]}")
    extra = data.get("extra") or {}
    return PineSource(
        script_id=script_id_part,
        # pine-facade HTML-escapes scriptName (e.g. "A -&gt; B"); the source text is raw.
        name=html.unescape(data.get("scriptName") or ""),
        kind=extra.get("kind"),
        version=data.get("lastVersionMaj") or extra.get("originalScriptVersion"),
        access=data.get("scriptAccess"),
        source_text=data.get("source") or "",
        raw={k: v for k, v in data.items() if k != "source"},
    )
