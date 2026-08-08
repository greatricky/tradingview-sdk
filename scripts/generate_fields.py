"""Generate src/tradingview_sdk/fields.py from the scanner metainfo endpoint.

Usage:
    uv run python scripts/generate_fields.py [path/to/metainfo.json]

Without an argument it fetches https://scanner.tradingview.com/america/metainfo
live. The generated module contains a ``Field`` StrEnum of every base field
name, plus a ``FIELDS`` catalog with type, human-readable description, allowed
values (for enumerated text fields), and available intraday/weekly/monthly
timeframe variants.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

OUT_PATH = Path(__file__).parent.parent / "src" / "tradingview_sdk" / "fields.py"
METAINFO_URL = "https://scanner.tradingview.com/america/metainfo"

# ---------------------------------------------------------------------------
# Description generation
# ---------------------------------------------------------------------------

# snake_case / dotted tokens expanded into readable words
TOKEN_EXPANSIONS = {
    "ttm": "(trailing twelve months)",
    "fy": "(fiscal year)",
    "fq": "(fiscal quarter)",
    "fh": "(fiscal half-year)",
    "yoy": "year-over-year",
    "qoq": "quarter-over-quarter",
    "mrq": "(most recent quarter)",
    "eps": "EPS",
    "ebitda": "EBITDA",
    "ebit": "EBIT",
    "aum": "assets under management",
    "nav": "NAV",
    "ytd": "year-to-date",
    "abs": "(absolute)",
    "avg": "average",
    "pct": "percent",
    "calc": "calculated",
    "perf": "performance",
    "rec": "recommendation",
    "chg": "change",
    "coef": "coefficient",
    "std": "standard deviation",
    "dps": "dividends per share",
    "fcf": "free cash flow",
    "roa": "return on assets",
    "roe": "return on equity",
    "roic": "return on invested capital",
    "pe": "P/E",
    "cagr": "CAGR",
    "gaap": "GAAP",
    "cfi": "CFI",
    "ucits": "UCITS",
    "etf": "ETF",
    "etn": "ETN",
    "ipo": "IPO",
    "id": "ID",
    "url": "URL",
    "vwap": "VWAP",
    "rsi": "RSI",
    "macd": "MACD",
    "adx": "ADX",
    "atr": "ATR",
    "sma": "SMA",
    "ema": "EMA",
    "bb": "Bollinger Bands",
    "cci": "CCI",
    "ao": "Awesome Oscillator",
    "uo": "Ultimate Oscillator",
    "mom": "momentum",
    "stoch": "stochastic",
    "wr": "Williams %R",
    "roc": "rate of change",
    "hl": "high/low",
    "n": "and",
    "f": "from",
    "curr": "current",
    "prev": "previous",
    "cont": "continuous",
    "oper": "operating",
    "op": "operating",
    "recm": "recommendation",
    "num": "number of",
    "qty": "quantity",
    "mkt": "market",
    "cap": "cap",
    "div": "dividend",
    "vol": "volume",
    "dev": "deviation",
    "min": "minimum",
    "max": "maximum",
    "tr": "(translated label)",
    "h": "(historical series)",
}

# Perf.X / interval-ish tail tokens
PERIOD_TOKENS = {
    "w": "1 week",
    "1m": "1 month",
    "3m": "3 months",
    "6m": "6 months",
    "y": "1 year",
    "1y": "1 year",
    "3y": "3 years",
    "5y": "5 years",
    "10y": "10 years",
    "all": "all time",
    "d": "1 day",
}

# Hand-written descriptions (and value-range notes) for the most-used fields.
# Every key is validated against metainfo at generation time.
CURATED = {
    # identity / classification
    "name": "Ticker symbol (without exchange prefix).",
    "description": "Instrument name / company description line.",
    "logoid": "Identifier of the instrument logo image.",
    "type": "Instrument type.",
    "typespecs": "Type qualifiers (array), e.g. common, preferred, etf, reit, closedend.",
    "exchange": "Listing exchange.",
    "currency": "Trading currency.",
    "fundamental_currency_code": "Currency used for fundamental (financial statement) values.",
    "sector": "FactSet economic sector.",
    "industry": "FactSet industry.",
    "country": "Country of incorporation / domicile.",
    "market": "TradingView market this symbol belongs to (e.g. america).",
    "submarket": "Sub-market segment (e.g. OTC tier).",
    "is_primary": "True when this is the primary listing of the instrument. Values: true/false.",
    "active_symbol": "True when the symbol is actively trading. Values: true/false.",
    "update_mode": "Data update mode for the session, e.g. streaming or delayed_streaming_900.",
    "current_session": "Current market session phase for the symbol.",
    # price / volume
    "close": "Last/close price (symbol currency).",
    "open": "Session open price.",
    "high": "Session high price.",
    "low": "Session low price.",
    "change": "Price change, percent (e.g. -7.35 means -7.35%).",
    "change_abs": "Price change, absolute (symbol currency).",
    "change_from_open": "Percent change from session open.",
    "gap": "Opening gap, percent.",
    "volume": "Session volume (shares/contracts).",
    "average_volume_10d_calc": "Average daily volume, 10 days.",
    "average_volume_30d_calc": "Average daily volume, 30 days.",
    "average_volume_60d_calc": "Average daily volume, 60 days.",
    "average_volume_90d_calc": "Average daily volume, 90 days.",
    "relative_volume_10d_calc": "Volume / 10-day average volume (1.0 = normal, >1 elevated).",
    "VWAP": "Volume-weighted average price for the session.",
    "premarket_change": "Pre-market percent change.",
    "premarket_close": "Pre-market last price.",
    "premarket_volume": "Pre-market volume.",
    "postmarket_change": "Post-market percent change.",
    "postmarket_close": "Post-market last price.",
    "postmarket_volume": "Post-market volume.",
    "price_52_week_high": "Highest price of the last 52 weeks.",
    "price_52_week_low": "Lowest price of the last 52 weeks.",
    "High.All": "All-time high price.",
    "Low.All": "All-time low price.",
    # valuation / size
    "market_cap_basic": "Market capitalization (fundamental currency).",
    "price_earnings_ttm": "P/E ratio, trailing twelve months. Typically ~0-100+; negative earnings give null/negative.",
    "price_earnings_growth_ttm": "PEG ratio (P/E divided by earnings growth), TTM.",
    "price_sales_current": "Price / sales ratio, current.",
    "price_book_fq": "Price / book ratio, latest fiscal quarter.",
    "price_free_cash_flow_ttm": "Price / free-cash-flow ratio, TTM.",
    "enterprise_value_current": "Enterprise value, current.",
    "enterprise_value_ebitda_ttm": "EV / EBITDA, TTM.",
    # fundamentals
    "earnings_per_share_diluted_ttm": "Diluted EPS, trailing twelve months.",
    "earnings_per_share_diluted_yoy_growth_ttm": "Diluted EPS growth TTM year-over-year, percent.",
    "total_revenue_yoy_growth_ttm": "Revenue growth TTM year-over-year, percent.",
    "dividends_yield_current": "Dividend yield, percent (e.g. 0.34 = 0.34%).",
    "dividends_yield": "Dividend yield (trailing), percent.",
    "gross_margin_ttm": "Gross margin, percent, TTM.",
    "operating_margin_ttm": "Operating margin, percent, TTM.",
    "net_margin_ttm": "Net profit margin, percent, TTM.",
    "free_cash_flow_margin_ttm": "Free cash flow margin, percent, TTM.",
    "return_on_equity_fq": "Return on equity, percent, latest fiscal quarter.",
    "return_on_assets_fq": "Return on assets, percent, latest fiscal quarter.",
    "return_on_invested_capital_fq": "Return on invested capital, percent, latest fiscal quarter.",
    "debt_to_equity_fq": "Total debt / equity, latest fiscal quarter.",
    "current_ratio_fq": "Current ratio (current assets / current liabilities), latest fiscal quarter.",
    "quick_ratio_fq": "Quick ratio, latest fiscal quarter.",
    "total_shares_outstanding_current": "Shares outstanding, current.",
    "float_shares_outstanding_current": "Public float (shares), current.",
    "number_of_employees": "Number of employees.",
    "earnings_release_date": "Last earnings report date (UNIX timestamp).",
    "earnings_release_next_date": "Next scheduled earnings report date (UNIX timestamp).",
    # performance / risk
    "Perf.W": "Price performance over 1 week, percent.",
    "Perf.1M": "Price performance over 1 month, percent.",
    "Perf.3M": "Price performance over 3 months, percent.",
    "Perf.6M": "Price performance over 6 months, percent.",
    "Perf.YTD": "Price performance year-to-date, percent.",
    "Perf.Y": "Price performance over 1 year, percent.",
    "Perf.5Y": "Price performance over 5 years, percent.",
    "Perf.10Y": "Price performance over 10 years, percent.",
    "Perf.All": "Price performance since inception, percent.",
    "Volatility.D": "Daily volatility, percent.",
    "Volatility.W": "Weekly volatility, percent.",
    "Volatility.M": "Monthly volatility, percent.",
    "beta_1_year": "Beta vs the market over 1 year (1.0 = market-like risk).",
    "beta_3_year": "Beta vs the market over 3 years.",
    "beta_5_year": "Beta vs the market over 5 years.",
    # analyst / ratings
    "recommendation_mark": "Analyst consensus rating: 1=Strong Buy .. 3=Hold .. 5=Strong Sell.",
    "recommendation_total": "Number of analyst ratings contributing to the consensus.",
    "price_target_average": "Average analyst price target.",
    "Recommend.All": "TradingView overall technical rating: -1 (strong sell) .. +1 (strong buy).",
    "Recommend.MA": "Technical rating from moving averages: -1 .. +1.",
    "Recommend.Other": "Technical rating from oscillators: -1 .. +1.",
    # technicals (bounded oscillators get explicit ranges)
    "RSI": "Relative Strength Index (14). Range 0-100; <30 oversold, >70 overbought.",
    "RSI7": "Relative Strength Index (7). Range 0-100.",
    "Stoch.K": "Stochastic %K (14,3,3). Range 0-100.",
    "Stoch.D": "Stochastic %D (14,3,3). Range 0-100.",
    "Stoch.RSI.K": "Stochastic RSI %K. Range 0-100.",
    "Stoch.RSI.D": "Stochastic RSI %D. Range 0-100.",
    "MACD.macd": "MACD line (12,26).",
    "MACD.signal": "MACD signal line (9).",
    "ADX": "Average Directional Index (14). Range 0-100; >25 = trending.",
    "ADX+DI": "Positive directional indicator +DI (14). Range 0-100.",
    "ADX-DI": "Negative directional indicator -DI (14). Range 0-100.",
    "CCI20": "Commodity Channel Index (20). Typically -200..+200, unbounded.",
    "AO": "Awesome Oscillator.",
    "Mom": "Momentum (10).",
    "W.R": "Williams %R (14). Range -100..0; <-80 oversold, >-20 overbought.",
    "ATR": "Average True Range (14), absolute price units.",
    "BB.upper": "Bollinger Band upper (20,2).",
    "BB.lower": "Bollinger Band lower (20,2).",
    "BBPower": "Bull Bear Power.",
    "UO": "Ultimate Oscillator (7,14,28). Range 0-100.",
    # ETF-specific
    "aum": "Assets under management (fund currency).",
    "expense_ratio": "Fund expense ratio, percent (e.g. 0.03 = 0.03%).",
    "nav": "Net asset value per share.",
    "nav_discount_premium": "Price premium/discount to NAV, percent.",
    "fund_flows.1M": "Net fund flows over 1 month (fund currency).",
    "fund_flows.3M": "Net fund flows over 3 months.",
    "fund_flows.1Y": "Net fund flows over 1 year.",
    "asset_class": "Fund asset class (internal id; select 'asset_class.tr' as a column for the readable label, e.g. Equity).",
    "focus": "Fund investment focus (internal id; use 'focus.tr' column for the readable label, e.g. Large cap).",
    "niche": "Fund niche segment (internal id; use 'niche.tr' column for the readable label).",
    "etf_holdings_count": "Number of holdings in the fund.",
    "actively_managed": "Whether the fund is actively managed.",
    "leveraged_flag": "Leverage classification of the fund.",
    "leverage_ratio": "Fund leverage ratio (e.g. 2, 3 for leveraged ETFs).",
    "index_provider": "Provider of the tracked index.",
    "brand": "Fund brand (e.g. Vanguard, iShares).",
    "issuer": "Fund issuer company.",
    "weighting_scheme": "Index weighting scheme (internal id; use 'weighting_scheme.tr' for the readable label).",
    "ucits_compliant_flag": "UCITS compliance: '1' = compliant, '0' = not.",
    "dividend_treatment": "How dividends are treated (accumulating/distributing).",
    "dividends_frequency": "Dividend payment frequency.",
    "nav_total_return.1Y": "NAV total return over 1 year, percent.",
    "nav_total_return.3Y": "NAV total return over 3 years, percent.",
    "nav_total_return.5Y": "NAV total return over 5 years, percent.",
    "nav_total_return.YTD": "NAV total return year-to-date, percent.",
}

TYPE_NOTES = {
    "price": "price in symbol currency",
    "fundamental_price": "monetary value in fundamental/fund currency",
    "percent": "percentage points (12.5 means 12.5%)",
    "number": "plain number",
    "bool": "boolean",
    "text": "text",
    "time": "UNIX timestamp (seconds)",
    "time-yyyymmdd": "date as YYYYMMDD",
    "num_slice": "array of numbers (per-period history)",
    "map": "structured object",
    "set": "array of tags",
    "interface": "structured object",
}


def humanize(name: str) -> str:
    """Build a readable description from a field name."""
    text = name
    prev_bar = text.endswith("[1]")
    if prev_bar:
        text = text[:-3]
    tokens = re.split(r"[._\-]", text)
    words: list[str] = []
    for i, token in enumerate(tokens):
        if not token:
            continue
        low = token.lower()
        if i > 0 and low in PERIOD_TOKENS and tokens[0].lower() in ("perf", "high", "low", "aum_perf"):
            words.append(f"over {PERIOD_TOKENS[low]}")
        elif low in TOKEN_EXPANSIONS:
            words.append(TOKEN_EXPANSIONS[low])
        elif re.fullmatch(r"\d+", token):
            words.append(f"({token})")
        elif token.isupper() or (token[0].isupper() and len(token) <= 5):
            words.append(token)
        else:
            words.append(low.replace("_", " "))
    out = " ".join(words)
    out = out[0].upper() + out[1:] if out else name
    if prev_bar:
        out += " (previous bar)"
    return out + "."


def sanitize_member(name: str) -> str:
    s = name.replace("+", "_PLUS_")
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").upper()
    if s[0].isdigit():
        s = "F_" + s
    return s


def assign_member_names(names: Iterable[str]) -> dict[str, str]:
    """Map field names to unique enum member names (collisions resolved by sort order).

    Suffixed names are registered alongside natural ones: "X" colliding twice
    yields "X_2", which a third field may also sanitize to on its own (real names
    like ``ADX+DI`` and ``ADX+DI[1]`` differ by exactly that pattern), and Enum
    rejects a reused key with a TypeError at import time.
    """
    members: dict[str, str] = {}
    used: set[str] = set()
    for name in sorted(names):
        key = sanitize_member(name)
        if key in used:
            stem, suffix = key, 2
            while key in used:
                key = f"{stem}_{suffix}"
                suffix += 1
        used.add(key)
        members[name] = key
    return members


def main() -> None:
    if len(sys.argv) > 1:
        meta = json.loads(Path(sys.argv[1]).read_text())
    else:
        import urllib.request

        req = urllib.request.Request(
            METAINFO_URL,
            headers={"User-Agent": "Mozilla/5.0", "Origin": "https://www.tradingview.com"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            meta = json.loads(resp.read())

    fields = {f["n"]: f for f in meta["fields"]}

    # Valid scan columns that metainfo does not list (verified live).
    for extra in ("name", "description", "logoid"):
        fields.setdefault(extra, {"n": extra, "t": "text", "r": None})

    missing = [k for k in CURATED if k not in fields]
    if missing:
        raise SystemExit(f"CURATED keys not in metainfo: {missing}")

    base = {n: f for n, f in fields.items() if "|" not in n}
    tf_map: dict[str, set[str]] = {}
    for n in fields:
        if "|" in n:
            root, tf = n.split("|", 1)
            tf_map.setdefault(root, set()).add(tf)

    def tf_sort_key(tf: str) -> tuple[int, int]:
        if tf.endswith("W"):
            return (1, int(tf[:-1] or 1))
        if tf.endswith("M"):
            return (2, int(tf[:-1] or 1))
        return (0, int(tf))

    members = assign_member_names(base)

    lines: list[str] = []
    w = lines.append
    w('"""TradingView screener field catalog (GENERATED - do not edit by hand).')
    w("")
    w("Regenerate with:  uv run python scripts/generate_fields.py")
    w(f"Source: {METAINFO_URL} ({len(fields)} fields, {len(base)} base names).")
    w("")
    w("Semantics by field type:")
    for t, note in TYPE_NOTES.items():
        w(f"  - {t}: {note}")
    w("")
    w("Timeframe variants: fields listed in ``FieldInfo.timeframes`` also exist as")
    w('``"<name>|<tf>"`` (e.g. ``"change|60"`` = change on the 60-minute chart);')
    w("build them with ``Field.CHANGE.tf('60')`` or ``with_timeframe()``.")
    w("Some text fields with internal-id values (asset_class, focus, niche,")
    w("weighting_scheme, ...) have a readable twin column suffixed ``.tr``.")
    w('"""')
    w("")
    w("from __future__ import annotations")
    w("")
    w("from dataclasses import dataclass")
    w("from enum import Enum, StrEnum")
    w("")
    w("")
    w("class FieldType(str, Enum):")
    for t in sorted(TYPE_NOTES):
        w(f'    {t.upper().replace("-", "_")} = "{t}"')
    w("")
    w("")
    w("@dataclass(frozen=True, slots=True)")
    w("class FieldInfo:")
    w('    """Metadata for one screener field."""')
    w("")
    w("    name: str")
    w("    type: FieldType")
    w("    description: str")
    w("    values: tuple[str, ...] | None = None      # allowed values (enumerated text fields)")
    w("    timeframes: tuple[str, ...] | None = None  # available '|<tf>' chart-timeframe variants")
    w("")
    w("")
    w(f"TIMEFRAMES = {tuple(sorted({t for s in tf_map.values() for t in s}, key=tf_sort_key))!r}")
    w("")
    w("")
    w("def with_timeframe(field: str, timeframe: str) -> str:")
    w('    """Return the per-timeframe variant of a field, e.g. ("change", "60") -> "change|60"."""')
    w("    info = FIELDS.get(str(field))")
    w("    if info is None or info.timeframes is None:")
    w("        raise ValueError(f\"field {field!r} has no timeframe variants\")")
    w("    if timeframe not in info.timeframes:")
    w("        raise ValueError(f\"field {field!r}: invalid timeframe {timeframe!r} (valid: {info.timeframes})\")")
    w('    return f"{field}|{timeframe}"')
    w("")
    w("")
    w("def field_info(name: str) -> FieldInfo | None:")
    w('    """Look up field metadata; understands "<name>|<tf>" timeframe variants."""')
    w("    name = str(name)")
    w("    if name in FIELDS:")
    w("        return FIELDS[name]")
    w('    root = name.split("|", 1)[0]')
    w("    return FIELDS.get(root)")
    w("")
    w("")
    w("def search_fields(query: str) -> list[FieldInfo]:")
    w('    """Case-insensitive substring search over field names and descriptions."""')
    w("    q = query.lower()")
    w("    return [info for info in FIELDS.values() if q in info.name.lower() or q in info.description.lower()]")
    w("")
    w("")
    w("class Field(StrEnum):")
    w('    """Every base screener field name (see FIELDS for metadata)."""')
    w("")
    w("    def tf(self, timeframe: str) -> str:")
    w('        """Per-timeframe variant, e.g. Field.CHANGE.tf("60") -> "change|60"."""')
    w("        return with_timeframe(self.value, timeframe)")
    w("")
    w("    @property")
    w("    def info(self) -> FieldInfo:")
    w("        return FIELDS[self.value]")
    w("")
    for n in sorted(base):
        w(f"    {members[n]} = {n!r}")
    w("")
    w("")
    w("FIELDS: dict[str, FieldInfo] = {")
    for n in sorted(base):
        f = base[n]
        ftype = f["t"].upper().replace("-", "_")
        desc = CURATED.get(n) or humanize(n)
        if n not in CURATED:
            note = TYPE_NOTES.get(f["t"])
            if f["t"] in ("percent", "time", "num_slice", "fundamental_price") and note:
                desc = desc[:-1] + f" [{note}]."
        values = tuple(sorted(str(v) for v in f["r"])) if f.get("r") else None
        tfs = tuple(sorted(tf_map[n], key=tf_sort_key)) if n in tf_map else None
        parts = [f"{n!r}: FieldInfo({n!r}, FieldType.{ftype}, {desc!r}"]
        if values is not None:
            parts.append(f", values={values!r}")
        if tfs is not None:
            parts.append(f", timeframes={tfs!r}")
        parts.append("),")
        w("    " + "".join(parts))
    w("}")
    w("")

    OUT_PATH.write_text("\n".join(lines))
    print(f"wrote {OUT_PATH} ({len(base)} fields, {OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
