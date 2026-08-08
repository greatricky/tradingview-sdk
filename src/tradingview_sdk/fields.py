"""TradingView screener field catalog (GENERATED - do not edit by hand).

Regenerate with:  uv run python scripts/generate_fields.py
Source: https://scanner.tradingview.com/america/metainfo (3774 fields, 1118 base names).

Semantics by field type:
  - price: price in symbol currency
  - fundamental_price: monetary value in fundamental/fund currency
  - percent: percentage points (12.5 means 12.5%)
  - number: plain number
  - bool: boolean
  - text: text
  - time: UNIX timestamp (seconds)
  - time-yyyymmdd: date as YYYYMMDD
  - num_slice: array of numbers (per-period history)
  - map: structured object
  - set: array of tags
  - interface: structured object

Timeframe variants: fields listed in ``FieldInfo.timeframes`` also exist as
``"<name>|<tf>"`` (e.g. ``"change|60"`` = change on the 60-minute chart);
build them with ``Field.CHANGE.tf('60')`` or ``with_timeframe()``.
Some text fields with internal-id values (asset_class, focus, niche,
weighting_scheme, ...) have a readable twin column suffixed ``.tr``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum


class FieldType(str, Enum):
    BOOL = "bool"
    FUNDAMENTAL_PRICE = "fundamental_price"
    INTERFACE = "interface"
    MAP = "map"
    NUM_SLICE = "num_slice"
    NUMBER = "number"
    PERCENT = "percent"
    PRICE = "price"
    SET = "set"
    TEXT = "text"
    TIME = "time"
    TIME_YYYYMMDD = "time-yyyymmdd"


@dataclass(frozen=True, slots=True)
class FieldInfo:
    """Metadata for one screener field."""

    name: str
    type: FieldType
    description: str
    values: tuple[str, ...] | None = None      # allowed values (enumerated text fields)
    timeframes: tuple[str, ...] | None = None  # available '|<tf>' chart-timeframe variants


TIMEFRAMES = ('1', '5', '15', '30', '60', '120', '240', '1W', '1M')


def with_timeframe(field: str, timeframe: str) -> str:
    """Return the per-timeframe variant of a field, e.g. ("change", "60") -> "change|60"."""
    info = FIELDS.get(str(field))
    if info is None or info.timeframes is None:
        raise ValueError(f"field {field!r} has no timeframe variants")
    if timeframe not in info.timeframes:
        raise ValueError(f"field {field!r}: invalid timeframe {timeframe!r} (valid: {info.timeframes})")
    return f"{field}|{timeframe}"


def field_info(name: str) -> FieldInfo | None:
    """Look up field metadata; understands "<name>|<tf>" timeframe variants."""
    name = str(name)
    if name in FIELDS:
        return FIELDS[name]
    root = name.split("|", 1)[0]
    return FIELDS.get(root)


def search_fields(query: str) -> list[FieldInfo]:
    """Case-insensitive substring search over field names and descriptions."""
    q = query.lower()
    return [info for info in FIELDS.values() if q in info.name.lower() or q in info.description.lower()]


class Field(StrEnum):
    """Every base screener field name (see FIELDS for metadata)."""

    def tf(self, timeframe: str) -> str:
        """Per-timeframe variant, e.g. Field.CHANGE.tf("60") -> "change|60"."""
        return with_timeframe(self.value, timeframe)

    @property
    def info(self) -> FieldInfo:
        return FIELDS[self.value]

    ADR = 'ADR'
    ADRP = 'ADRP'
    ADX = 'ADX'
    ADX_PLUS_DI = 'ADX+DI'
    ADX_PLUS_DI_1 = 'ADX+DI[1]'
    ADX_PLUS_DI_100 = 'ADX+DI_100'
    ADX_PLUS_DI_100_1 = 'ADX+DI_100[1]'
    ADX_PLUS_DI_20 = 'ADX+DI_20'
    ADX_PLUS_DI_20_1 = 'ADX+DI_20[1]'
    ADX_PLUS_DI_50 = 'ADX+DI_50'
    ADX_PLUS_DI_50_1 = 'ADX+DI_50[1]'
    ADX_PLUS_DI_9 = 'ADX+DI_9'
    ADX_PLUS_DI_9_1 = 'ADX+DI_9[1]'
    ADX_DI = 'ADX-DI'
    ADX_DI_1 = 'ADX-DI[1]'
    ADX_DI_100 = 'ADX-DI_100'
    ADX_DI_100_1 = 'ADX-DI_100[1]'
    ADX_DI_20 = 'ADX-DI_20'
    ADX_DI_20_1 = 'ADX-DI_20[1]'
    ADX_DI_50 = 'ADX-DI_50'
    ADX_DI_50_1 = 'ADX-DI_50[1]'
    ADX_DI_9 = 'ADX-DI_9'
    ADX_DI_9_1 = 'ADX-DI_9[1]'
    ADX_100 = 'ADX_100'
    ADX_20 = 'ADX_20'
    ADX_50 = 'ADX_50'
    ADX_9 = 'ADX_9'
    AO = 'AO'
    AO_1 = 'AO[1]'
    AO_2 = 'AO[2]'
    ATR = 'ATR'
    ATRP = 'ATRP'
    AROON_DOWN = 'Aroon.Down'
    AROON_UP = 'Aroon.Up'
    AVGVALUE_TRADED_10D = 'AvgValue.Traded_10d'
    AVGVALUE_TRADED_30D = 'AvgValue.Traded_30d'
    AVGVALUE_TRADED_60D = 'AvgValue.Traded_60d'
    AVGVALUE_TRADED_90D = 'AvgValue.Traded_90d'
    BB_BASIS = 'BB.basis'
    BB_BASIS_50 = 'BB.basis_50'
    BB_LOWER = 'BB.lower'
    BB_LOWER_50 = 'BB.lower_50'
    BB_UPPER = 'BB.upper'
    BB_UPPER_50 = 'BB.upper_50'
    BBPOWER = 'BBPower'
    CCI20 = 'CCI20'
    CCI20_1 = 'CCI20[1]'
    CANDLE_3BLACKCROWS = 'Candle.3BlackCrows'
    CANDLE_3WHITESOLDIERS = 'Candle.3WhiteSoldiers'
    CANDLE_ABANDONEDBABY_BEARISH = 'Candle.AbandonedBaby.Bearish'
    CANDLE_ABANDONEDBABY_BULLISH = 'Candle.AbandonedBaby.Bullish'
    CANDLE_DARKCLOUDCOVER_BEARISH = 'Candle.DarkCloudCover.Bearish'
    CANDLE_DOJI = 'Candle.Doji'
    CANDLE_DOJI_DRAGONFLY = 'Candle.Doji.Dragonfly'
    CANDLE_DOJI_GRAVESTONE = 'Candle.Doji.Gravestone'
    CANDLE_DOJISTAR_BEARISH = 'Candle.DojiStar.Bearish'
    CANDLE_DOJISTAR_BULLISH = 'Candle.DojiStar.Bullish'
    CANDLE_DOWNSIDETASUKIGAP_BEARISH = 'Candle.DownsideTasukiGap.Bearish'
    CANDLE_ENGULFING_BEARISH = 'Candle.Engulfing.Bearish'
    CANDLE_ENGULFING_BULLISH = 'Candle.Engulfing.Bullish'
    CANDLE_EVENINGDOJISTAR_BEARISH = 'Candle.EveningDojiStar.Bearish'
    CANDLE_EVENINGSTAR = 'Candle.EveningStar'
    CANDLE_FALLINGTHREEMETHODS_BEARISH = 'Candle.FallingThreeMethods.Bearish'
    CANDLE_FALLINGWINDOW_BEARISH = 'Candle.FallingWindow.Bearish'
    CANDLE_HAMMER = 'Candle.Hammer'
    CANDLE_HANGINGMAN = 'Candle.HangingMan'
    CANDLE_HARAMI_BEARISH = 'Candle.Harami.Bearish'
    CANDLE_HARAMI_BULLISH = 'Candle.Harami.Bullish'
    CANDLE_HARAMICROSS_BEARISH = 'Candle.HaramiCross.Bearish'
    CANDLE_HARAMICROSS_BULLISH = 'Candle.HaramiCross.Bullish'
    CANDLE_INVERTEDHAMMER = 'Candle.InvertedHammer'
    CANDLE_KICKING_BEARISH = 'Candle.Kicking.Bearish'
    CANDLE_KICKING_BULLISH = 'Candle.Kicking.Bullish'
    CANDLE_LONGSHADOW_LOWER = 'Candle.LongShadow.Lower'
    CANDLE_LONGSHADOW_UPPER = 'Candle.LongShadow.Upper'
    CANDLE_MARUBOZU_BLACK = 'Candle.Marubozu.Black'
    CANDLE_MARUBOZU_WHITE = 'Candle.Marubozu.White'
    CANDLE_MORNINGDOJISTAR_BULLISH = 'Candle.MorningDojiStar.Bullish'
    CANDLE_MORNINGSTAR = 'Candle.MorningStar'
    CANDLE_ONNECK_BEARISH = 'Candle.OnNeck.Bearish'
    CANDLE_PIERCING_BULLISH = 'Candle.Piercing.Bullish'
    CANDLE_RISINGTHREEMETHODS_BULLISH = 'Candle.RisingThreeMethods.Bullish'
    CANDLE_RISINGWINDOW_BULLISH = 'Candle.RisingWindow.Bullish'
    CANDLE_SHOOTINGSTAR = 'Candle.ShootingStar'
    CANDLE_SPINNINGTOP_BLACK = 'Candle.SpinningTop.Black'
    CANDLE_SPINNINGTOP_WHITE = 'Candle.SpinningTop.White'
    CANDLE_TRISTAR_BEARISH = 'Candle.TriStar.Bearish'
    CANDLE_TRISTAR_BULLISH = 'Candle.TriStar.Bullish'
    CANDLE_TWEEZERBOTTOM_BULLISH = 'Candle.TweezerBottom.Bullish'
    CANDLE_TWEEZERTOP_BEARISH = 'Candle.TweezerTop.Bearish'
    CANDLE_UPSIDETASUKIGAP_BULLISH = 'Candle.UpsideTasukiGap.Bullish'
    CHAIKINMONEYFLOW = 'ChaikinMoneyFlow'
    DONCHCH20_LOWER = 'DonchCh20.Lower'
    DONCHCH20_MIDDLE = 'DonchCh20.Middle'
    DONCHCH20_UPPER = 'DonchCh20.Upper'
    EMA10 = 'EMA10'
    EMA100 = 'EMA100'
    EMA12 = 'EMA12'
    EMA120 = 'EMA120'
    EMA13 = 'EMA13'
    EMA14 = 'EMA14'
    EMA144 = 'EMA144'
    EMA15 = 'EMA15'
    EMA150 = 'EMA150'
    EMA2 = 'EMA2'
    EMA20 = 'EMA20'
    EMA200 = 'EMA200'
    EMA21 = 'EMA21'
    EMA25 = 'EMA25'
    EMA250 = 'EMA250'
    EMA26 = 'EMA26'
    EMA3 = 'EMA3'
    EMA30 = 'EMA30'
    EMA300 = 'EMA300'
    EMA34 = 'EMA34'
    EMA40 = 'EMA40'
    EMA5 = 'EMA5'
    EMA50 = 'EMA50'
    EMA55 = 'EMA55'
    EMA6 = 'EMA6'
    EMA60 = 'EMA60'
    EMA7 = 'EMA7'
    EMA75 = 'EMA75'
    EMA8 = 'EMA8'
    EMA89 = 'EMA89'
    EMA9 = 'EMA9'
    HIGH_1M = 'High.1M'
    HIGH_1M_DATE = 'High.1M.Date'
    HIGH_3M = 'High.3M'
    HIGH_3M_DATE = 'High.3M.Date'
    HIGH_5D = 'High.5D'
    HIGH_6M = 'High.6M'
    HIGH_6M_DATE = 'High.6M.Date'
    HIGH_ALL = 'High.All'
    HIGH_ALL_CALC = 'High.All.Calc'
    HIGH_ALL_CALC_DATE = 'High.All.Calc.Date'
    HIGH_ALL_DATE = 'High.All.Date'
    HULLMA20 = 'HullMA20'
    HULLMA200 = 'HullMA200'
    HULLMA9 = 'HullMA9'
    ICHIMOKU_BLINE = 'Ichimoku.BLine'
    ICHIMOKU_BLINE_20_60_120_30 = 'Ichimoku.BLine_20_60_120_30'
    ICHIMOKU_CLINE = 'Ichimoku.CLine'
    ICHIMOKU_CLINE_20_60_120_30 = 'Ichimoku.CLine_20_60_120_30'
    ICHIMOKU_LEAD1 = 'Ichimoku.Lead1'
    ICHIMOKU_LEAD1_20_60_120_30 = 'Ichimoku.Lead1_20_60_120_30'
    ICHIMOKU_LEAD2 = 'Ichimoku.Lead2'
    ICHIMOKU_LEAD2_20_60_120_30 = 'Ichimoku.Lead2_20_60_120_30'
    KLTCHNL_BASIS = 'KltChnl.basis'
    KLTCHNL_LOWER = 'KltChnl.lower'
    KLTCHNL_UPPER = 'KltChnl.upper'
    LOW_1M = 'Low.1M'
    LOW_1M_DATE = 'Low.1M.Date'
    LOW_3M = 'Low.3M'
    LOW_3M_DATE = 'Low.3M.Date'
    LOW_5D = 'Low.5D'
    LOW_6M = 'Low.6M'
    LOW_6M_DATE = 'Low.6M.Date'
    LOW_AFTER_HIGH_ALL = 'Low.After.High.All'
    LOW_ALL = 'Low.All'
    LOW_ALL_CALC = 'Low.All.Calc'
    LOW_ALL_CALC_DATE = 'Low.All.Calc.Date'
    LOW_ALL_DATE = 'Low.All.Date'
    MACD_HIST = 'MACD.hist'
    MACD_MACD = 'MACD.macd'
    MACD_SIGNAL = 'MACD.signal'
    MOM = 'Mom'
    MOM_1 = 'Mom[1]'
    MOM_14 = 'Mom_14'
    MOM_14_1 = 'Mom_14[1]'
    MONEYFLOW = 'MoneyFlow'
    OPEN_ALL_CALC = 'Open.All.Calc'
    P_SAR = 'P.SAR'
    PERF_10Y = 'Perf.10Y'
    PERF_10Y_ABS = 'Perf.10Y_abs'
    PERF_1M = 'Perf.1M'
    PERF_1M_MARKETCAP = 'Perf.1M.MarketCap'
    PERF_1M_ABS = 'Perf.1M_abs'
    PERF_1W_MARKETCAP = 'Perf.1W.MarketCap'
    PERF_1Y_MARKETCAP = 'Perf.1Y.MarketCap'
    PERF_3M = 'Perf.3M'
    PERF_3M_MARKETCAP = 'Perf.3M.MarketCap'
    PERF_3M_ABS = 'Perf.3M_abs'
    PERF_3Y = 'Perf.3Y'
    PERF_3Y_ABS = 'Perf.3Y_abs'
    PERF_5D = 'Perf.5D'
    PERF_5D_ABS = 'Perf.5D_abs'
    PERF_5Y = 'Perf.5Y'
    PERF_5Y_MARKETCAP = 'Perf.5Y.MarketCap'
    PERF_5Y_ABS = 'Perf.5Y_abs'
    PERF_6M = 'Perf.6M'
    PERF_6M_MARKETCAP = 'Perf.6M.MarketCap'
    PERF_6M_ABS = 'Perf.6M_abs'
    PERF_ALL = 'Perf.All'
    PERF_ALL_ABS = 'Perf.All_abs'
    PERF_W = 'Perf.W'
    PERF_W_ABS = 'Perf.W_abs'
    PERF_Y = 'Perf.Y'
    PERF_YTD = 'Perf.YTD'
    PERF_YTD_MARKETCAP = 'Perf.YTD.MarketCap'
    PERF_YTD_ABS = 'Perf.YTD_abs'
    PERF_Y_ABS = 'Perf.Y_abs'
    PIVOT_M_CAMARILLA_MIDDLE = 'Pivot.M.Camarilla.Middle'
    PIVOT_M_CAMARILLA_R1 = 'Pivot.M.Camarilla.R1'
    PIVOT_M_CAMARILLA_R2 = 'Pivot.M.Camarilla.R2'
    PIVOT_M_CAMARILLA_R3 = 'Pivot.M.Camarilla.R3'
    PIVOT_M_CAMARILLA_S1 = 'Pivot.M.Camarilla.S1'
    PIVOT_M_CAMARILLA_S2 = 'Pivot.M.Camarilla.S2'
    PIVOT_M_CAMARILLA_S3 = 'Pivot.M.Camarilla.S3'
    PIVOT_M_CLASSIC_MIDDLE = 'Pivot.M.Classic.Middle'
    PIVOT_M_CLASSIC_R1 = 'Pivot.M.Classic.R1'
    PIVOT_M_CLASSIC_R2 = 'Pivot.M.Classic.R2'
    PIVOT_M_CLASSIC_R3 = 'Pivot.M.Classic.R3'
    PIVOT_M_CLASSIC_S1 = 'Pivot.M.Classic.S1'
    PIVOT_M_CLASSIC_S2 = 'Pivot.M.Classic.S2'
    PIVOT_M_CLASSIC_S3 = 'Pivot.M.Classic.S3'
    PIVOT_M_DEMARK_MIDDLE = 'Pivot.M.Demark.Middle'
    PIVOT_M_DEMARK_R1 = 'Pivot.M.Demark.R1'
    PIVOT_M_DEMARK_S1 = 'Pivot.M.Demark.S1'
    PIVOT_M_FIBONACCI_MIDDLE = 'Pivot.M.Fibonacci.Middle'
    PIVOT_M_FIBONACCI_R1 = 'Pivot.M.Fibonacci.R1'
    PIVOT_M_FIBONACCI_R2 = 'Pivot.M.Fibonacci.R2'
    PIVOT_M_FIBONACCI_R3 = 'Pivot.M.Fibonacci.R3'
    PIVOT_M_FIBONACCI_S1 = 'Pivot.M.Fibonacci.S1'
    PIVOT_M_FIBONACCI_S2 = 'Pivot.M.Fibonacci.S2'
    PIVOT_M_FIBONACCI_S3 = 'Pivot.M.Fibonacci.S3'
    PIVOT_M_WOODIE_MIDDLE = 'Pivot.M.Woodie.Middle'
    PIVOT_M_WOODIE_R1 = 'Pivot.M.Woodie.R1'
    PIVOT_M_WOODIE_R2 = 'Pivot.M.Woodie.R2'
    PIVOT_M_WOODIE_R3 = 'Pivot.M.Woodie.R3'
    PIVOT_M_WOODIE_S1 = 'Pivot.M.Woodie.S1'
    PIVOT_M_WOODIE_S2 = 'Pivot.M.Woodie.S2'
    PIVOT_M_WOODIE_S3 = 'Pivot.M.Woodie.S3'
    ROC = 'ROC'
    RSI = 'RSI'
    RSI10 = 'RSI10'
    RSI10_1 = 'RSI10[1]'
    RSI2 = 'RSI2'
    RSI20 = 'RSI20'
    RSI20_1 = 'RSI20[1]'
    RSI21 = 'RSI21'
    RSI21_1 = 'RSI21[1]'
    RSI2_1 = 'RSI2[1]'
    RSI3 = 'RSI3'
    RSI30 = 'RSI30'
    RSI30_1 = 'RSI30[1]'
    RSI3_1 = 'RSI3[1]'
    RSI4 = 'RSI4'
    RSI4_1 = 'RSI4[1]'
    RSI5 = 'RSI5'
    RSI5_1 = 'RSI5[1]'
    RSI7 = 'RSI7'
    RSI7_1 = 'RSI7[1]'
    RSI9 = 'RSI9'
    RSI9_1 = 'RSI9[1]'
    RSI_1 = 'RSI[1]'
    REC_BBPOWER = 'Rec.BBPower'
    REC_HULLMA9 = 'Rec.HullMA9'
    REC_ICHIMOKU = 'Rec.Ichimoku'
    REC_STOCH_RSI = 'Rec.Stoch.RSI'
    REC_UO = 'Rec.UO'
    REC_VWMA = 'Rec.VWMA'
    REC_WR = 'Rec.WR'
    RECOMMEND_ALL = 'Recommend.All'
    RECOMMEND_MA = 'Recommend.MA'
    RECOMMEND_OTHER = 'Recommend.Other'
    SMA10 = 'SMA10'
    SMA100 = 'SMA100'
    SMA12 = 'SMA12'
    SMA120 = 'SMA120'
    SMA13 = 'SMA13'
    SMA14 = 'SMA14'
    SMA144 = 'SMA144'
    SMA15 = 'SMA15'
    SMA150 = 'SMA150'
    SMA2 = 'SMA2'
    SMA20 = 'SMA20'
    SMA200 = 'SMA200'
    SMA21 = 'SMA21'
    SMA25 = 'SMA25'
    SMA250 = 'SMA250'
    SMA26 = 'SMA26'
    SMA3 = 'SMA3'
    SMA30 = 'SMA30'
    SMA300 = 'SMA300'
    SMA34 = 'SMA34'
    SMA40 = 'SMA40'
    SMA5 = 'SMA5'
    SMA50 = 'SMA50'
    SMA55 = 'SMA55'
    SMA6 = 'SMA6'
    SMA60 = 'SMA60'
    SMA7 = 'SMA7'
    SMA75 = 'SMA75'
    SMA8 = 'SMA8'
    SMA89 = 'SMA89'
    SMA9 = 'SMA9'
    STOCH_D = 'Stoch.D'
    STOCH_D_1 = 'Stoch.D[1]'
    STOCH_D_14_1_3 = 'Stoch.D_14_1_3'
    STOCH_D_14_1_3_1 = 'Stoch.D_14_1_3[1]'
    STOCH_D_5_3_3 = 'Stoch.D_5_3_3'
    STOCH_D_5_3_3_1 = 'Stoch.D_5_3_3[1]'
    STOCH_D_6_3_3 = 'Stoch.D_6_3_3'
    STOCH_D_6_3_3_1 = 'Stoch.D_6_3_3[1]'
    STOCH_D_8_3_3 = 'Stoch.D_8_3_3'
    STOCH_D_8_3_3_1 = 'Stoch.D_8_3_3[1]'
    STOCH_K = 'Stoch.K'
    STOCH_K_1 = 'Stoch.K[1]'
    STOCH_K_14_1_3 = 'Stoch.K_14_1_3'
    STOCH_K_14_1_3_1 = 'Stoch.K_14_1_3[1]'
    STOCH_K_5_3_3 = 'Stoch.K_5_3_3'
    STOCH_K_5_3_3_1 = 'Stoch.K_5_3_3[1]'
    STOCH_K_6_3_3 = 'Stoch.K_6_3_3'
    STOCH_K_6_3_3_1 = 'Stoch.K_6_3_3[1]'
    STOCH_K_8_3_3 = 'Stoch.K_8_3_3'
    STOCH_K_8_3_3_1 = 'Stoch.K_8_3_3[1]'
    STOCH_RSI_D = 'Stoch.RSI.D'
    STOCH_RSI_K = 'Stoch.RSI.K'
    UO = 'UO'
    VWAP = 'VWAP'
    VWMA = 'VWMA'
    VOLATILITY_D = 'Volatility.D'
    VOLATILITY_M = 'Volatility.M'
    VOLATILITY_W = 'Volatility.W'
    W_R = 'W.R'
    ACTIVE_SYMBOL = 'active_symbol'
    ACTIVELY_MANAGED = 'actively_managed'
    AFTER_TAX_MARGIN = 'after_tax_margin'
    ALL_TIME_HIGH = 'all_time_high'
    ALL_TIME_HIGH_DAY = 'all_time_high_day'
    ALL_TIME_LOW = 'all_time_low'
    ALL_TIME_LOW_DAY = 'all_time_low_day'
    ALL_TIME_OPEN = 'all_time_open'
    ALTMAN_Z_SCORE_FY = 'altman_z_score_fy'
    ALTMAN_Z_SCORE_TTM = 'altman_z_score_ttm'
    AMOUNT_RECENT = 'amount_recent'
    AMOUNT_UPCOMING = 'amount_upcoming'
    ASSET_CLASS = 'asset_class'
    ASSET_TURNOVER_CURRENT = 'asset_turnover_current'
    ASSET_TURNOVER_FY = 'asset_turnover_fy'
    AUM = 'aum'
    AUM_PERF_1M = 'aum_perf.1M'
    AUM_PERF_1Y = 'aum_perf.1Y'
    AUM_PERF_3M = 'aum_perf.3M'
    AUM_PERF_3Y = 'aum_perf.3Y'
    AUM_PERF_5Y = 'aum_perf.5Y'
    AUM_PERF_YTD = 'aum_perf.YTD'
    AVERAGE_VOLUME = 'average_volume'
    AVERAGE_VOLUME_10D_CALC = 'average_volume_10d_calc'
    AVERAGE_VOLUME_30D_CALC = 'average_volume_30d_calc'
    AVERAGE_VOLUME_60D_CALC = 'average_volume_60d_calc'
    AVERAGE_VOLUME_90D_CALC = 'average_volume_90d_calc'
    BARS_COUNT = 'bars_count'
    BASE_CURRENCY_KIND = 'base_currency_kind'
    BASIC_EPS_NET_INCOME = 'basic_eps_net_income'
    BETA_1_YEAR = 'beta_1_year'
    BETA_3_YEAR = 'beta_3_year'
    BETA_5_YEAR = 'beta_5_year'
    BOOK_TANGIBLE_PER_SHARE_CURRENT = 'book_tangible_per_share_current'
    BOOK_TANGIBLE_PER_SHARE_FH = 'book_tangible_per_share_fh'
    BOOK_TANGIBLE_PER_SHARE_FQ = 'book_tangible_per_share_fq'
    BOOK_TANGIBLE_PER_SHARE_FY = 'book_tangible_per_share_fy'
    BOOK_VALUE_PER_SHARE_CURRENT = 'book_value_per_share_current'
    BOOK_VALUE_PER_SHARE_ESTIMATE_FH = 'book_value_per_share_estimate_fh'
    BOOK_VALUE_PER_SHARE_ESTIMATE_FQ = 'book_value_per_share_estimate_fq'
    BOOK_VALUE_PER_SHARE_ESTIMATE_FY = 'book_value_per_share_estimate_fy'
    BOOK_VALUE_PER_SHARE_FH = 'book_value_per_share_fh'
    BOOK_VALUE_PER_SHARE_FQ = 'book_value_per_share_fq'
    BOOK_VALUE_PER_SHARE_FY = 'book_value_per_share_fy'
    BRAND = 'brand'
    BUYBACK_YIELD = 'buyback_yield'
    CAPEX_PER_SHARE_CURRENT = 'capex_per_share_current'
    CAPEX_PER_SHARE_FH = 'capex_per_share_fh'
    CAPEX_PER_SHARE_FQ = 'capex_per_share_fq'
    CAPEX_PER_SHARE_FY = 'capex_per_share_fy'
    CAPEX_PER_SHARE_TTM = 'capex_per_share_ttm'
    CAPITAL_EXPENDITURES_ESTIMATE_FH = 'capital_expenditures_estimate_fh'
    CAPITAL_EXPENDITURES_ESTIMATE_FQ = 'capital_expenditures_estimate_fq'
    CAPITAL_EXPENDITURES_ESTIMATE_FY = 'capital_expenditures_estimate_fy'
    CAPITAL_EXPENDITURES_ESTIMATE_NTM = 'capital_expenditures_estimate_ntm'
    CAPITAL_EXPENDITURES_FH = 'capital_expenditures_fh'
    CAPITAL_EXPENDITURES_FQ = 'capital_expenditures_fq'
    CAPITAL_EXPENDITURES_FY = 'capital_expenditures_fy'
    CAPITAL_EXPENDITURES_QOQ_GROWTH_FQ = 'capital_expenditures_qoq_growth_fq'
    CAPITAL_EXPENDITURES_TTM = 'capital_expenditures_ttm'
    CAPITAL_EXPENDITURES_UNCHANGED_FQ_H = 'capital_expenditures_unchanged_fq_h'
    CAPITAL_EXPENDITURES_UNCHANGED_FY_H = 'capital_expenditures_unchanged_fy_h'
    CAPITAL_EXPENDITURES_UNCHANGED_TTM_H = 'capital_expenditures_unchanged_ttm_h'
    CAPITAL_EXPENDITURES_YOY_GROWTH_FQ = 'capital_expenditures_yoy_growth_fq'
    CAPITAL_EXPENDITURES_YOY_GROWTH_FY = 'capital_expenditures_yoy_growth_fy'
    CAPITAL_EXPENDITURES_YOY_GROWTH_TTM = 'capital_expenditures_yoy_growth_ttm'
    CASH_DIVIDEND_COVERAGE_RATIO_FY = 'cash_dividend_coverage_ratio_fy'
    CASH_DIVIDEND_COVERAGE_RATIO_TTM = 'cash_dividend_coverage_ratio_ttm'
    CASH_F_FINANCING_ACTIVITIES_ESTIMATE_FH = 'cash_f_financing_activities_estimate_fh'
    CASH_F_FINANCING_ACTIVITIES_ESTIMATE_FQ = 'cash_f_financing_activities_estimate_fq'
    CASH_F_FINANCING_ACTIVITIES_ESTIMATE_FY = 'cash_f_financing_activities_estimate_fy'
    CASH_F_FINANCING_ACTIVITIES_ESTIMATE_NTM = 'cash_f_financing_activities_estimate_ntm'
    CASH_F_FINANCING_ACTIVITIES_FH = 'cash_f_financing_activities_fh'
    CASH_F_FINANCING_ACTIVITIES_FQ = 'cash_f_financing_activities_fq'
    CASH_F_FINANCING_ACTIVITIES_FY = 'cash_f_financing_activities_fy'
    CASH_F_FINANCING_ACTIVITIES_TTM = 'cash_f_financing_activities_ttm'
    CASH_F_INVESTING_ACTIVITIES_ESTIMATE_FH = 'cash_f_investing_activities_estimate_fh'
    CASH_F_INVESTING_ACTIVITIES_ESTIMATE_FQ = 'cash_f_investing_activities_estimate_fq'
    CASH_F_INVESTING_ACTIVITIES_ESTIMATE_FY = 'cash_f_investing_activities_estimate_fy'
    CASH_F_INVESTING_ACTIVITIES_ESTIMATE_NTM = 'cash_f_investing_activities_estimate_ntm'
    CASH_F_INVESTING_ACTIVITIES_FH = 'cash_f_investing_activities_fh'
    CASH_F_INVESTING_ACTIVITIES_FQ = 'cash_f_investing_activities_fq'
    CASH_F_INVESTING_ACTIVITIES_FY = 'cash_f_investing_activities_fy'
    CASH_F_INVESTING_ACTIVITIES_TTM = 'cash_f_investing_activities_ttm'
    CASH_F_OPERATING_ACTIVITIES_ESTIMATE_FH = 'cash_f_operating_activities_estimate_fh'
    CASH_F_OPERATING_ACTIVITIES_ESTIMATE_FQ = 'cash_f_operating_activities_estimate_fq'
    CASH_F_OPERATING_ACTIVITIES_ESTIMATE_FY = 'cash_f_operating_activities_estimate_fy'
    CASH_F_OPERATING_ACTIVITIES_ESTIMATE_NTM = 'cash_f_operating_activities_estimate_ntm'
    CASH_F_OPERATING_ACTIVITIES_FH = 'cash_f_operating_activities_fh'
    CASH_F_OPERATING_ACTIVITIES_FQ = 'cash_f_operating_activities_fq'
    CASH_F_OPERATING_ACTIVITIES_FY = 'cash_f_operating_activities_fy'
    CASH_F_OPERATING_ACTIVITIES_TTM = 'cash_f_operating_activities_ttm'
    CASH_N_EQUIVALENTS_FQ = 'cash_n_equivalents_fq'
    CASH_N_EQUIVALENTS_FY = 'cash_n_equivalents_fy'
    CASH_N_SHORT_TERM_INVEST_ESTIMATE_FH = 'cash_n_short_term_invest_estimate_fh'
    CASH_N_SHORT_TERM_INVEST_ESTIMATE_FQ = 'cash_n_short_term_invest_estimate_fq'
    CASH_N_SHORT_TERM_INVEST_ESTIMATE_FY = 'cash_n_short_term_invest_estimate_fy'
    CASH_N_SHORT_TERM_INVEST_FQ = 'cash_n_short_term_invest_fq'
    CASH_N_SHORT_TERM_INVEST_FY = 'cash_n_short_term_invest_fy'
    CASH_N_SHORT_TERM_INVEST_TO_TOTAL_CURRENT_LIABILITIES_FQ = 'cash_n_short_term_invest_to_total_current_liabilities_fq'
    CASH_N_SHORT_TERM_INVEST_TO_TOTAL_CURRENT_LIABILITIES_FY = 'cash_n_short_term_invest_to_total_current_liabilities_fy'
    CASH_N_SHORT_TERM_INVEST_TO_TOTAL_DEBT_FQ = 'cash_n_short_term_invest_to_total_debt_fq'
    CASH_N_SHORT_TERM_INVEST_TO_TOTAL_DEBT_FY = 'cash_n_short_term_invest_to_total_debt_fy'
    CASH_PER_SHARE_CURRENT = 'cash_per_share_current'
    CASH_PER_SHARE_FH = 'cash_per_share_fh'
    CASH_PER_SHARE_FQ = 'cash_per_share_fq'
    CASH_PER_SHARE_FY = 'cash_per_share_fy'
    CASH_RATIO = 'cash_ratio'
    CATEGORY = 'category'
    CFI_CODE = 'cfi_code'
    CHANGE = 'change'
    CHANGE_ABS = 'change_abs'
    CHANGE_FROM_OPEN = 'change_from_open'
    CHANGE_FROM_OPEN_ABS = 'change_from_open_abs'
    CLOSE = 'close'
    CONTINUOUS_DIVIDEND_GROWTH = 'continuous_dividend_growth'
    CONTINUOUS_DIVIDEND_PAYOUT = 'continuous_dividend_payout'
    COST_OF_GOODS_ESTIMATE_FH = 'cost_of_goods_estimate_fh'
    COST_OF_GOODS_ESTIMATE_FQ = 'cost_of_goods_estimate_fq'
    COST_OF_GOODS_ESTIMATE_FY = 'cost_of_goods_estimate_fy'
    COST_OF_GOODS_ESTIMATE_NTM = 'cost_of_goods_estimate_ntm'
    COUNTRY = 'country'
    COUNTRY_CODE_FUND = 'country_code_fund'
    COUPON = 'coupon'
    CRYPTOASSET_INFO_DESCRIPTION = 'cryptoasset-info.description'
    CRYPTOASSET_INFO_ID = 'cryptoasset-info.id'
    CURRENCY = 'currency'
    CURRENCY_HEDGED_FLAG = 'currency_hedged_flag'
    CURRENCY_ID = 'currency_id'
    CURRENCY_KIND = 'currency_kind'
    CURRENT_RATIO = 'current_ratio'
    CURRENT_RATIO_CURRENT = 'current_ratio_current'
    CURRENT_RATIO_FQ = 'current_ratio_fq'
    CURRENT_RATIO_FY = 'current_ratio_fy'
    CURRENT_SESSION = 'current_session'
    CURRENT_YIELD = 'current_yield'
    DAILY_BAR_TIME = 'daily-bar.time'
    DAYS_TO_MATURITY = 'days_to_maturity'
    DEBT_TO_ASSET_FQ = 'debt_to_asset_fq'
    DEBT_TO_ASSET_FY = 'debt_to_asset_fy'
    DEBT_TO_ASSETS = 'debt_to_assets'
    DEBT_TO_EQUITY = 'debt_to_equity'
    DEBT_TO_EQUITY_FQ = 'debt_to_equity_fq'
    DEBT_TO_EQUITY_FY = 'debt_to_equity_fy'
    DEBT_TO_REVENUE_FY = 'debt_to_revenue_fy'
    DEBT_TO_REVENUE_TTM = 'debt_to_revenue_ttm'
    DESCRIPTION = 'description'
    DILUTED_SHARES_OUTSTANDING_FQ = 'diluted_shares_outstanding_fq'
    DIVIDEND_AMOUNT_RECENT = 'dividend_amount_recent'
    DIVIDEND_AMOUNT_UPCOMING = 'dividend_amount_upcoming'
    DIVIDEND_EX_DATE_RECENT = 'dividend_ex_date_recent'
    DIVIDEND_EX_DATE_UPCOMING = 'dividend_ex_date_upcoming'
    DIVIDEND_FREQUENCY_RECENT = 'dividend_frequency_recent'
    DIVIDEND_FREQUENCY_UPCOMING = 'dividend_frequency_upcoming'
    DIVIDEND_PAYMENT_DATE_RECENT = 'dividend_payment_date_recent'
    DIVIDEND_PAYMENT_DATE_UPCOMING = 'dividend_payment_date_upcoming'
    DIVIDEND_PAYOUT_RATIO_FY = 'dividend_payout_ratio_fy'
    DIVIDEND_PAYOUT_RATIO_PERCENT_FQ = 'dividend_payout_ratio_percent_fq'
    DIVIDEND_PAYOUT_RATIO_PERCENT_FY = 'dividend_payout_ratio_percent_fy'
    DIVIDEND_PAYOUT_RATIO_TTM = 'dividend_payout_ratio_ttm'
    DIVIDEND_TREATMENT = 'dividend_treatment'
    DIVIDEND_YIELD_RECENT = 'dividend_yield_recent'
    DIVIDEND_YIELD_UPCOMING = 'dividend_yield_upcoming'
    DIVIDENDS_FREQUENCY = 'dividends_frequency'
    DIVIDENDS_PAID = 'dividends_paid'
    DIVIDENDS_PER_SHARE_FQ = 'dividends_per_share_fq'
    DIVIDENDS_YIELD = 'dividends_yield'
    DIVIDENDS_YIELD_CURRENT = 'dividends_yield_current'
    DIVIDENDS_YIELD_FQ = 'dividends_yield_fq'
    DIVIDENDS_YIELD_FY = 'dividends_yield_fy'
    DPS_COMMON_STOCK_PRIM_ISSUE_FH = 'dps_common_stock_prim_issue_fh'
    DPS_COMMON_STOCK_PRIM_ISSUE_FQ = 'dps_common_stock_prim_issue_fq'
    DPS_COMMON_STOCK_PRIM_ISSUE_FY = 'dps_common_stock_prim_issue_fy'
    DPS_COMMON_STOCK_PRIM_ISSUE_FY_H = 'dps_common_stock_prim_issue_fy_h'
    DPS_COMMON_STOCK_PRIM_ISSUE_TTM = 'dps_common_stock_prim_issue_ttm'
    DPS_COMMON_STOCK_PRIM_ISSUE_YOY_GROWTH_FY = 'dps_common_stock_prim_issue_yoy_growth_fy'
    DPS_ESTIMATE_FH = 'dps_estimate_fh'
    DPS_ESTIMATE_FQ = 'dps_estimate_fq'
    DPS_ESTIMATE_FY = 'dps_estimate_fy'
    DPS_ESTIMATE_NTM = 'dps_estimate_ntm'
    EARNINGS_FQ_H = 'earnings_fq_h'
    EARNINGS_PER_SHARE_BASIC_CAGR_5Y = 'earnings_per_share_basic_cagr_5y'
    EARNINGS_PER_SHARE_BASIC_FH = 'earnings_per_share_basic_fh'
    EARNINGS_PER_SHARE_BASIC_FQ = 'earnings_per_share_basic_fq'
    EARNINGS_PER_SHARE_BASIC_FY = 'earnings_per_share_basic_fy'
    EARNINGS_PER_SHARE_BASIC_FY_H = 'earnings_per_share_basic_fy_h'
    EARNINGS_PER_SHARE_BASIC_TTM = 'earnings_per_share_basic_ttm'
    EARNINGS_PER_SHARE_DILUTED_5Y_GROWTH_FY = 'earnings_per_share_diluted_5y_growth_fy'
    EARNINGS_PER_SHARE_DILUTED_FH = 'earnings_per_share_diluted_fh'
    EARNINGS_PER_SHARE_DILUTED_FQ = 'earnings_per_share_diluted_fq'
    EARNINGS_PER_SHARE_DILUTED_FQ_H = 'earnings_per_share_diluted_fq_h'
    EARNINGS_PER_SHARE_DILUTED_FY = 'earnings_per_share_diluted_fy'
    EARNINGS_PER_SHARE_DILUTED_FY_H = 'earnings_per_share_diluted_fy_h'
    EARNINGS_PER_SHARE_DILUTED_QOQ_GROWTH_FQ = 'earnings_per_share_diluted_qoq_growth_fq'
    EARNINGS_PER_SHARE_DILUTED_TTM = 'earnings_per_share_diluted_ttm'
    EARNINGS_PER_SHARE_DILUTED_TTM_H = 'earnings_per_share_diluted_ttm_h'
    EARNINGS_PER_SHARE_DILUTED_YOY_GROWTH_FQ = 'earnings_per_share_diluted_yoy_growth_fq'
    EARNINGS_PER_SHARE_DILUTED_YOY_GROWTH_FY = 'earnings_per_share_diluted_yoy_growth_fy'
    EARNINGS_PER_SHARE_DILUTED_YOY_GROWTH_TTM = 'earnings_per_share_diluted_yoy_growth_ttm'
    EARNINGS_PER_SHARE_FH = 'earnings_per_share_fh'
    EARNINGS_PER_SHARE_FORECAST_FQ = 'earnings_per_share_forecast_fq'
    EARNINGS_PER_SHARE_FORECAST_NEXT_FH = 'earnings_per_share_forecast_next_fh'
    EARNINGS_PER_SHARE_FORECAST_NEXT_FQ = 'earnings_per_share_forecast_next_fq'
    EARNINGS_PER_SHARE_FORECAST_NEXT_FY = 'earnings_per_share_forecast_next_fy'
    EARNINGS_PER_SHARE_FQ = 'earnings_per_share_fq'
    EARNINGS_PER_SHARE_FY = 'earnings_per_share_fy'
    EARNINGS_PUBLICATION_TYPE_FQ = 'earnings_publication_type_fq'
    EARNINGS_PUBLICATION_TYPE_NEXT_FQ = 'earnings_publication_type_next_fq'
    EARNINGS_RELEASE_CALENDAR_DATE = 'earnings_release_calendar_date'
    EARNINGS_RELEASE_DATE = 'earnings_release_date'
    EARNINGS_RELEASE_NEXT_CALENDAR_DATE = 'earnings_release_next_calendar_date'
    EARNINGS_RELEASE_NEXT_DATE = 'earnings_release_next_date'
    EARNINGS_RELEASE_NEXT_TIME = 'earnings_release_next_time'
    EARNINGS_RELEASE_NEXT_TRADING_DATE_FQ = 'earnings_release_next_trading_date_fq'
    EARNINGS_RELEASE_NEXT_TRADING_DATE_FY = 'earnings_release_next_trading_date_fy'
    EARNINGS_RELEASE_TIME = 'earnings_release_time'
    EARNINGS_RELEASE_TRADING_DATE_FQ = 'earnings_release_trading_date_fq'
    EARNINGS_RELEASE_TRADING_DATE_FY = 'earnings_release_trading_date_fy'
    EARNINGS_YIELD = 'earnings_yield'
    EBIT_ESTIMATE_FH = 'ebit_estimate_fh'
    EBIT_ESTIMATE_FQ = 'ebit_estimate_fq'
    EBIT_ESTIMATE_FY = 'ebit_estimate_fy'
    EBIT_ESTIMATE_NTM = 'ebit_estimate_ntm'
    EBIT_PER_SHARE_CURRENT = 'ebit_per_share_current'
    EBIT_PER_SHARE_FH = 'ebit_per_share_fh'
    EBIT_PER_SHARE_FQ = 'ebit_per_share_fq'
    EBIT_PER_SHARE_FY = 'ebit_per_share_fy'
    EBIT_PER_SHARE_TTM = 'ebit_per_share_ttm'
    EBIT_TTM = 'ebit_ttm'
    EBITDA = 'ebitda'
    EBITDA_ESTIMATE_FH = 'ebitda_estimate_fh'
    EBITDA_ESTIMATE_FQ = 'ebitda_estimate_fq'
    EBITDA_ESTIMATE_FY = 'ebitda_estimate_fy'
    EBITDA_ESTIMATE_NTM = 'ebitda_estimate_ntm'
    EBITDA_FH = 'ebitda_fh'
    EBITDA_FQ = 'ebitda_fq'
    EBITDA_FQ_H = 'ebitda_fq_h'
    EBITDA_FY = 'ebitda_fy'
    EBITDA_FY_H = 'ebitda_fy_h'
    EBITDA_INTERST_COVER_FY = 'ebitda_interst_cover_fy'
    EBITDA_INTERST_COVER_TTM = 'ebitda_interst_cover_ttm'
    EBITDA_LESS_CAPEX_INTERST_COVER_FY = 'ebitda_less_capex_interst_cover_fy'
    EBITDA_LESS_CAPEX_INTERST_COVER_TTM = 'ebitda_less_capex_interst_cover_ttm'
    EBITDA_MARGIN_FY = 'ebitda_margin_fy'
    EBITDA_MARGIN_TTM = 'ebitda_margin_ttm'
    EBITDA_PER_EMPLOYEE_FY = 'ebitda_per_employee_fy'
    EBITDA_PER_SHARE_CURRENT = 'ebitda_per_share_current'
    EBITDA_PER_SHARE_FH = 'ebitda_per_share_fh'
    EBITDA_PER_SHARE_FQ = 'ebitda_per_share_fq'
    EBITDA_PER_SHARE_FY = 'ebitda_per_share_fy'
    EBITDA_PER_SHARE_TTM = 'ebitda_per_share_ttm'
    EBITDA_QOQ_GROWTH_FQ = 'ebitda_qoq_growth_fq'
    EBITDA_TTM = 'ebitda_ttm'
    EBITDA_TTM_H = 'ebitda_ttm_h'
    EBITDA_YOY_GROWTH_FQ = 'ebitda_yoy_growth_fq'
    EBITDA_YOY_GROWTH_FY = 'ebitda_yoy_growth_fy'
    EBITDA_YOY_GROWTH_TTM = 'ebitda_yoy_growth_ttm'
    EFFECTIVE_INTEREST_RATE_ON_DEBT_FY = 'effective_interest_rate_on_debt_fy'
    EFFECTIVE_INTEREST_RATE_ON_DEBT_TTM = 'effective_interest_rate_on_debt_ttm'
    ENTERPRISE_VALUE_CURRENT = 'enterprise_value_current'
    ENTERPRISE_VALUE_EBIT_FWD = 'enterprise_value_ebit_fwd'
    ENTERPRISE_VALUE_EBITDA_CURRENT = 'enterprise_value_ebitda_current'
    ENTERPRISE_VALUE_EBITDA_FWD = 'enterprise_value_ebitda_fwd'
    ENTERPRISE_VALUE_EBITDA_TTM = 'enterprise_value_ebitda_ttm'
    ENTERPRISE_VALUE_FQ = 'enterprise_value_fq'
    ENTERPRISE_VALUE_SALES_FWD = 'enterprise_value_sales_fwd'
    ENTERPRISE_VALUE_TO_EBIT_TTM = 'enterprise_value_to_ebit_ttm'
    ENTERPRISE_VALUE_TO_FREE_CASH_FLOW_TTM = 'enterprise_value_to_free_cash_flow_ttm'
    ENTERPRISE_VALUE_TO_GROSS_PROFIT_TTM = 'enterprise_value_to_gross_profit_ttm'
    ENTERPRISE_VALUE_TO_REVENUE_TTM = 'enterprise_value_to_revenue_ttm'
    EPS_DILUTED_GROWTH_PERCENT_FQ = 'eps_diluted_growth_percent_fq'
    EPS_DILUTED_GROWTH_PERCENT_FY = 'eps_diluted_growth_percent_fy'
    EPS_ESTIMATE_NTM = 'eps_estimate_ntm'
    EPS_SURPRISE_FQ = 'eps_surprise_fq'
    EPS_SURPRISE_PERCENT_FQ = 'eps_surprise_percent_fq'
    ETF_FUND_CURRENCY = 'etf_fund_currency'
    ETF_HOLDINGS_COUNT = 'etf_holdings_count'
    EX_DIVIDEND_DATE_RECENT = 'ex_dividend_date_recent'
    EX_DIVIDEND_DATE_UPCOMING = 'ex_dividend_date_upcoming'
    EXCHANGE = 'exchange'
    EXPECTED_ANNUAL_DIVIDENDS = 'expected_annual_dividends'
    EXPENSE_RATIO = 'expense_ratio'
    EXPIRATION = 'expiration'
    FIRST_BAR_TIME = 'first_bar_time'
    FISCAL_PERIOD_CURRENT = 'fiscal_period_current'
    FISCAL_PERIOD_END_CURRENT = 'fiscal_period_end_current'
    FISCAL_PERIOD_END_FH = 'fiscal_period_end_fh'
    FISCAL_PERIOD_END_FH_H = 'fiscal_period_end_fh_h'
    FISCAL_PERIOD_END_FQ = 'fiscal_period_end_fq'
    FISCAL_PERIOD_END_FY = 'fiscal_period_end_fy'
    FISCAL_PERIOD_FY = 'fiscal_period_fy'
    FISCAL_PERIOD_FY_H = 'fiscal_period_fy_h'
    FIXED_ASSETS_TURNOVER_FQ = 'fixed_assets_turnover_fq'
    FIXED_ASSETS_TURNOVER_FY = 'fixed_assets_turnover_fy'
    FLOAT_SHARES_OUTSTANDING = 'float_shares_outstanding'
    FLOAT_SHARES_OUTSTANDING_CURRENT = 'float_shares_outstanding_current'
    FLOAT_SHARES_PERCENT_CURRENT = 'float_shares_percent_current'
    FOCUS = 'focus'
    FRACTIONAL = 'fractional'
    FREE_CASH_FLOW = 'free_cash_flow'
    FREE_CASH_FLOW_CAGR_5Y = 'free_cash_flow_cagr_5y'
    FREE_CASH_FLOW_ESTIMATE_FH = 'free_cash_flow_estimate_fh'
    FREE_CASH_FLOW_ESTIMATE_FQ = 'free_cash_flow_estimate_fq'
    FREE_CASH_FLOW_ESTIMATE_FY = 'free_cash_flow_estimate_fy'
    FREE_CASH_FLOW_ESTIMATE_NTM = 'free_cash_flow_estimate_ntm'
    FREE_CASH_FLOW_FH = 'free_cash_flow_fh'
    FREE_CASH_FLOW_FQ = 'free_cash_flow_fq'
    FREE_CASH_FLOW_FQ_H = 'free_cash_flow_fq_h'
    FREE_CASH_FLOW_FY = 'free_cash_flow_fy'
    FREE_CASH_FLOW_FY_H = 'free_cash_flow_fy_h'
    FREE_CASH_FLOW_MARGIN_FY = 'free_cash_flow_margin_fy'
    FREE_CASH_FLOW_MARGIN_TTM = 'free_cash_flow_margin_ttm'
    FREE_CASH_FLOW_PER_EMPLOYEE_FY = 'free_cash_flow_per_employee_fy'
    FREE_CASH_FLOW_PER_SHARE_CURRENT = 'free_cash_flow_per_share_current'
    FREE_CASH_FLOW_PER_SHARE_FH = 'free_cash_flow_per_share_fh'
    FREE_CASH_FLOW_PER_SHARE_FQ = 'free_cash_flow_per_share_fq'
    FREE_CASH_FLOW_PER_SHARE_FY = 'free_cash_flow_per_share_fy'
    FREE_CASH_FLOW_PER_SHARE_TTM = 'free_cash_flow_per_share_ttm'
    FREE_CASH_FLOW_QOQ_GROWTH_FQ = 'free_cash_flow_qoq_growth_fq'
    FREE_CASH_FLOW_TTM = 'free_cash_flow_ttm'
    FREE_CASH_FLOW_TTM_H = 'free_cash_flow_ttm_h'
    FREE_CASH_FLOW_YOY_GROWTH_FQ = 'free_cash_flow_yoy_growth_fq'
    FREE_CASH_FLOW_YOY_GROWTH_FY = 'free_cash_flow_yoy_growth_fy'
    FREE_CASH_FLOW_YOY_GROWTH_TTM = 'free_cash_flow_yoy_growth_ttm'
    FREQUENCY_RECENT = 'frequency_recent'
    FREQUENCY_UPCOMING = 'frequency_upcoming'
    FUND_FLOWS_1M = 'fund_flows.1M'
    FUND_FLOWS_1Y = 'fund_flows.1Y'
    FUND_FLOWS_3M = 'fund_flows.3M'
    FUND_FLOWS_3Y = 'fund_flows.3Y'
    FUND_FLOWS_5Y = 'fund_flows.5Y'
    FUND_FLOWS_YTD = 'fund_flows.YTD'
    FUNDAMENTAL_CURRENCY_CODE = 'fundamental_currency_code'
    GAP = 'gap'
    GAP_DOWN = 'gap_down'
    GAP_DOWN_ABS = 'gap_down_abs'
    GAP_UP = 'gap_up'
    GAP_UP_ABS = 'gap_up_abs'
    GOODWILL = 'goodwill'
    GOODWILL_FQ = 'goodwill_fq'
    GOODWILL_FY = 'goodwill_fy'
    GRAHAM_NUMBERS_FY = 'graham_numbers_fy'
    GRAHAM_NUMBERS_TTM = 'graham_numbers_ttm'
    GROSS_MARGIN = 'gross_margin'
    GROSS_MARGIN_FY = 'gross_margin_fy'
    GROSS_MARGIN_PERCENT_TTM = 'gross_margin_percent_ttm'
    GROSS_MARGIN_TTM = 'gross_margin_ttm'
    GROSS_PROFIT = 'gross_profit'
    GROSS_PROFIT_ESTIMATE_FH = 'gross_profit_estimate_fh'
    GROSS_PROFIT_ESTIMATE_FQ = 'gross_profit_estimate_fq'
    GROSS_PROFIT_ESTIMATE_FY = 'gross_profit_estimate_fy'
    GROSS_PROFIT_ESTIMATE_NTM = 'gross_profit_estimate_ntm'
    GROSS_PROFIT_FH = 'gross_profit_fh'
    GROSS_PROFIT_FQ = 'gross_profit_fq'
    GROSS_PROFIT_FQ_H = 'gross_profit_fq_h'
    GROSS_PROFIT_FY = 'gross_profit_fy'
    GROSS_PROFIT_FY_H = 'gross_profit_fy_h'
    GROSS_PROFIT_MARGIN_FY = 'gross_profit_margin_fy'
    GROSS_PROFIT_QOQ_GROWTH_FQ = 'gross_profit_qoq_growth_fq'
    GROSS_PROFIT_TTM = 'gross_profit_ttm'
    GROSS_PROFIT_TTM_H = 'gross_profit_ttm_h'
    GROSS_PROFIT_YOY_GROWTH_FQ = 'gross_profit_yoy_growth_fq'
    GROSS_PROFIT_YOY_GROWTH_FY = 'gross_profit_yoy_growth_fy'
    GROSS_PROFIT_YOY_GROWTH_TTM = 'gross_profit_yoy_growth_ttm'
    HAS_IPO_DATA = 'has_ipo_data'
    HAS_IPO_DETAILS_VISIBLE = 'has_ipo_details_visible'
    HIGH = 'high'
    HOLDINGS_REGION = 'holdings_region'
    HOLDS_DERIVATIVES_FLAG = 'holds_derivatives_flag'
    INCOME_FROM_CONT_OPS_FH = 'income_from_cont_ops_fh'
    INCOME_FROM_CONT_OPS_FQ = 'income_from_cont_ops_fq'
    INCOME_FROM_CONT_OPS_FY = 'income_from_cont_ops_fy'
    INCOME_FROM_CONT_OPS_TTM = 'income_from_cont_ops_ttm'
    INDEX = 'index'
    INDEX_ID = 'index_id'
    INDEX_PRIORITY = 'index_priority'
    INDEX_PROVIDER = 'index_provider'
    INDEXES = 'indexes'
    INDICATED_ANNUAL_DIVIDEND = 'indicated_annual_dividend'
    INDICATORS_BARS_COUNT = 'indicators_bars_count'
    INDUSTRY = 'industry'
    INTERST_COVER_FY = 'interst_cover_fy'
    INTERST_COVER_TTM = 'interst_cover_ttm'
    INVENT_TURNOVER_CURRENT = 'invent_turnover_current'
    INVENT_TURNOVER_FY = 'invent_turnover_fy'
    INVERSE_FLAG = 'inverse_flag'
    IPO_ANNOUNCEMENT_DATE = 'ipo_announcement_date'
    IPO_BLANK_CHECK_FLAG = 'ipo_blank_check_flag'
    IPO_DEAL_AMOUNT_USD = 'ipo_deal_amount_usd'
    IPO_MARKET_CAP_USD = 'ipo_market_cap_usd'
    IPO_OFFER_DATE = 'ipo_offer_date'
    IPO_OFFER_PRICE_PERFORMANCE = 'ipo_offer_price_performance'
    IPO_OFFER_PRICE_USD = 'ipo_offer_price_usd'
    IPO_OFFER_TIME = 'ipo_offer_time'
    IPO_OFFERED_SHARES = 'ipo_offered_shares'
    IPO_OFFERED_SHARES_PRIMARY = 'ipo_offered_shares_primary'
    IPO_OFFERED_SHARES_SECONDARY = 'ipo_offered_shares_secondary'
    IPO_PRICE_RANGE_USD_MAX = 'ipo_price_range_usd_max'
    IPO_PRICE_RANGE_USD_MIN = 'ipo_price_range_usd_min'
    IPO_SHARES_OUTSTANDING = 'ipo_shares_outstanding'
    IPO_SPLITFACTOR_TO_OFFER = 'ipo_splitfactor_to_offer'
    IS_BLACKLISTED = 'is_blacklisted'
    IS_PRIMARY = 'is_primary'
    IS_SHARIAH_COMPLIANT = 'is_shariah_compliant'
    IS_SYMBOL_PRIMARY_LISTING = 'is_symbol_primary_listing'
    ISSUANCE_OF_STOCK_NET_TTM = 'issuance_of_stock_net_ttm'
    ISSUER = 'issuer'
    K1_FORM = 'k1_form'
    KIND = 'kind'
    KIND_DELAY = 'kind-delay'
    LAST_PRICE_UPDATE_TIME = 'last-price-update-time'
    LAST_PRICE_UPDATE_TIME_INTRADAY = 'last-price-update-time-intraday'
    LAST_ANNUAL_EPS = 'last_annual_eps'
    LAST_ANNUAL_REVENUE = 'last_annual_revenue'
    LAST_BAR_UPDATE_TIME = 'last_bar_update_time'
    LAST_REPORT_FREQUENCY = 'last_report_frequency'
    LAUNCH_DATE = 'launch_date'
    LEVERAGE = 'leverage'
    LEVERAGE_RATIO = 'leverage_ratio'
    LEVERAGED_FLAG = 'leveraged_flag'
    LOGOID = 'logoid'
    LONG_TERM_CAPITAL = 'long_term_capital'
    LONG_TERM_DEBT_FQ = 'long_term_debt_fq'
    LONG_TERM_DEBT_FY = 'long_term_debt_fy'
    LONG_TERM_DEBT_TO_ASSETS_FQ = 'long_term_debt_to_assets_fq'
    LONG_TERM_DEBT_TO_ASSETS_FY = 'long_term_debt_to_assets_fy'
    LONG_TERM_DEBT_TO_EQUITY_FQ = 'long_term_debt_to_equity_fq'
    LOW = 'low'
    LOW_AFTER_HIGH_ALL_CHANGE = 'low_after_high_all_change'
    LOW_AFTER_HIGH_ALL_CHANGE_ABS = 'low_after_high_all_change_abs'
    MARKET = 'market'
    MARKET_CAP_BASIC = 'market_cap_basic'
    MARKET_CAP_CALC = 'market_cap_calc'
    MATURITY_DATE = 'maturity_date'
    MINMOV = 'minmov'
    MINMOVE2 = 'minmove2'
    MINUTE_BAR_TIME = 'minute-bar.time'
    MOST_RECENT_QUARTER_DATE = 'most_recent_quarter_date'
    NAME = 'name'
    NAV = 'nav'
    NAV_DISCOUNT_PREMIUM = 'nav_discount_premium'
    NAV_PERF_1M = 'nav_perf.1M'
    NAV_PERF_1Y = 'nav_perf.1Y'
    NAV_PERF_3M = 'nav_perf.3M'
    NAV_PERF_3Y = 'nav_perf.3Y'
    NAV_PERF_5Y = 'nav_perf.5Y'
    NAV_PERF_YTD = 'nav_perf.YTD'
    NAV_TOTAL_RETURN_1M = 'nav_total_return.1M'
    NAV_TOTAL_RETURN_1Y = 'nav_total_return.1Y'
    NAV_TOTAL_RETURN_3M = 'nav_total_return.3M'
    NAV_TOTAL_RETURN_3Y = 'nav_total_return.3Y'
    NAV_TOTAL_RETURN_5Y = 'nav_total_return.5Y'
    NAV_TOTAL_RETURN_6M = 'nav_total_return.6M'
    NAV_TOTAL_RETURN_YTD = 'nav_total_return.YTD'
    NCAVPS_RATIO_CURRENT = 'ncavps_ratio_current'
    NCAVPS_RATIO_FH = 'ncavps_ratio_fh'
    NCAVPS_RATIO_FQ = 'ncavps_ratio_fq'
    NCAVPS_RATIO_FY = 'ncavps_ratio_fy'
    NEG_CAPITAL_EXPENDITURES_FH = 'neg_capital_expenditures_fh'
    NEG_CAPITAL_EXPENDITURES_FQ = 'neg_capital_expenditures_fq'
    NEG_CAPITAL_EXPENDITURES_FY = 'neg_capital_expenditures_fy'
    NEG_CAPITAL_EXPENDITURES_TTM = 'neg_capital_expenditures_ttm'
    NEG_RESEARCH_AND_DEV_FH = 'neg_research_and_dev_fh'
    NEG_RESEARCH_AND_DEV_FQ = 'neg_research_and_dev_fq'
    NEG_RESEARCH_AND_DEV_FY = 'neg_research_and_dev_fy'
    NEG_RESEARCH_AND_DEV_TTM = 'neg_research_and_dev_ttm'
    NEG_TOTAL_CASH_DIVIDENDS_PAID_FH = 'neg_total_cash_dividends_paid_fh'
    NEG_TOTAL_CASH_DIVIDENDS_PAID_FQ = 'neg_total_cash_dividends_paid_fq'
    NEG_TOTAL_CASH_DIVIDENDS_PAID_FY = 'neg_total_cash_dividends_paid_fy'
    NEG_TOTAL_CASH_DIVIDENDS_PAID_TTM = 'neg_total_cash_dividends_paid_ttm'
    NET_DEBT = 'net_debt'
    NET_DEBT_FQ = 'net_debt_fq'
    NET_DEBT_FY = 'net_debt_fy'
    NET_DEBT_TO_EBITDA_FQ = 'net_debt_to_ebitda_fq'
    NET_DEBT_TO_EBITDA_FY = 'net_debt_to_ebitda_fy'
    NET_INCOME = 'net_income'
    NET_INCOME_BEF_DISC_OPER_FY = 'net_income_bef_disc_oper_fy'
    NET_INCOME_BEF_DISC_OPER_MARGIN_FY = 'net_income_bef_disc_oper_margin_fy'
    NET_INCOME_CAGR_5Y = 'net_income_cagr_5y'
    NET_INCOME_ESTIMATE_FH = 'net_income_estimate_fh'
    NET_INCOME_ESTIMATE_FQ = 'net_income_estimate_fq'
    NET_INCOME_ESTIMATE_FY = 'net_income_estimate_fy'
    NET_INCOME_ESTIMATE_NTM = 'net_income_estimate_ntm'
    NET_INCOME_FH = 'net_income_fh'
    NET_INCOME_FQ = 'net_income_fq'
    NET_INCOME_FQ_H = 'net_income_fq_h'
    NET_INCOME_FY = 'net_income_fy'
    NET_INCOME_FY_H = 'net_income_fy_h'
    NET_INCOME_PER_EMPLOYEE_FY = 'net_income_per_employee_fy'
    NET_INCOME_QOQ_GROWTH_FQ = 'net_income_qoq_growth_fq'
    NET_INCOME_TTM = 'net_income_ttm'
    NET_INCOME_TTM_H = 'net_income_ttm_h'
    NET_INCOME_YOY_GROWTH_FQ = 'net_income_yoy_growth_fq'
    NET_INCOME_YOY_GROWTH_FY = 'net_income_yoy_growth_fy'
    NET_INCOME_YOY_GROWTH_TTM = 'net_income_yoy_growth_ttm'
    NET_MARGIN = 'net_margin'
    NET_MARGIN_FY = 'net_margin_fy'
    NET_MARGIN_TTM = 'net_margin_ttm'
    NET_REVENUE_AFTER_PROVISION_FH = 'net_revenue_after_provision_fh'
    NET_REVENUE_AFTER_PROVISION_FQ = 'net_revenue_after_provision_fq'
    NET_REVENUE_AFTER_PROVISION_FY = 'net_revenue_after_provision_fy'
    NET_REVENUE_AFTER_PROVISION_TTM = 'net_revenue_after_provision_ttm'
    NET_REVENUE_FH = 'net_revenue_fh'
    NET_REVENUE_FQ = 'net_revenue_fq'
    NET_REVENUE_FY = 'net_revenue_fy'
    NET_REVENUE_TTM = 'net_revenue_ttm'
    NEXT_DIVIDEND_DATE = 'next_dividend_date'
    NICHE = 'niche'
    NON_GAAP_PRICE_TO_EARNINGS_PER_SHARE_FORECAST_NEXT_FY = 'non_gaap_price_to_earnings_per_share_forecast_next_fy'
    NUMBER_OF_EMPLOYEES = 'number_of_employees'
    NUMBER_OF_EMPLOYEES_FY = 'number_of_employees_fy'
    NUMBER_OF_SHAREHOLDERS = 'number_of_shareholders'
    NUMBER_OF_SHAREHOLDERS_FY = 'number_of_shareholders_fy'
    OPEN = 'open'
    OPER_INCOME_FH = 'oper_income_fh'
    OPER_INCOME_FQ = 'oper_income_fq'
    OPER_INCOME_FY = 'oper_income_fy'
    OPER_INCOME_MARGIN_FY = 'oper_income_margin_fy'
    OPER_INCOME_PER_EMPLOYEE_FY = 'oper_income_per_employee_fy'
    OPER_INCOME_TTM = 'oper_income_ttm'
    OPERATING_CASH_FLOW_PER_SHARE_CURRENT = 'operating_cash_flow_per_share_current'
    OPERATING_CASH_FLOW_PER_SHARE_FH = 'operating_cash_flow_per_share_fh'
    OPERATING_CASH_FLOW_PER_SHARE_FQ = 'operating_cash_flow_per_share_fq'
    OPERATING_CASH_FLOW_PER_SHARE_FY = 'operating_cash_flow_per_share_fy'
    OPERATING_CASH_FLOW_PER_SHARE_TTM = 'operating_cash_flow_per_share_ttm'
    OPERATING_MARGIN = 'operating_margin'
    OPERATING_MARGIN_FY = 'operating_margin_fy'
    OPERATING_MARGIN_TTM = 'operating_margin_ttm'
    PAYMENT_DATE_RECENT = 'payment_date_recent'
    PAYMENT_DATE_UPCOMING = 'payment_date_upcoming'
    PIOTROSKI_F_SCORE_FY = 'piotroski_f_score_fy'
    PIOTROSKI_F_SCORE_TTM = 'piotroski_f_score_ttm'
    POST_CHANGE = 'post_change'
    POSTMARKET_CHANGE = 'postmarket_change'
    POSTMARKET_CHANGE_ABS = 'postmarket_change_abs'
    POSTMARKET_CLOSE = 'postmarket_close'
    POSTMARKET_HIGH = 'postmarket_high'
    POSTMARKET_LOW = 'postmarket_low'
    POSTMARKET_OPEN = 'postmarket_open'
    POSTMARKET_TIME = 'postmarket_time'
    POSTMARKET_VOLUME = 'postmarket_volume'
    PRE_CHANGE = 'pre_change'
    PRE_CHANGE_ABS = 'pre_change_abs'
    PRE_TAX_MARGIN = 'pre_tax_margin'
    PRE_TAX_MARGIN_TTM = 'pre_tax_margin_ttm'
    PREFERRED_DIVIDENDS = 'preferred_dividends'
    PREMARKET_CHANGE = 'premarket_change'
    PREMARKET_CHANGE_ABS = 'premarket_change_abs'
    PREMARKET_CHANGE_FROM_OPEN = 'premarket_change_from_open'
    PREMARKET_CHANGE_FROM_OPEN_ABS = 'premarket_change_from_open_abs'
    PREMARKET_CLOSE = 'premarket_close'
    PREMARKET_GAP = 'premarket_gap'
    PREMARKET_HIGH = 'premarket_high'
    PREMARKET_LOW = 'premarket_low'
    PREMARKET_OPEN = 'premarket_open'
    PREMARKET_TIME = 'premarket_time'
    PREMARKET_VOLUME = 'premarket_volume'
    PRICE_52_WEEK_HIGH = 'price_52_week_high'
    PRICE_52_WEEK_HIGH_DATE = 'price_52_week_high_date'
    PRICE_52_WEEK_LOW = 'price_52_week_low'
    PRICE_52_WEEK_LOW_DATE = 'price_52_week_low_date'
    PRICE_ANNUAL_BOOK = 'price_annual_book'
    PRICE_ANNUAL_SALES = 'price_annual_sales'
    PRICE_BOOK_CURRENT = 'price_book_current'
    PRICE_BOOK_FQ = 'price_book_fq'
    PRICE_BOOK_FWD = 'price_book_fwd'
    PRICE_BOOK_RATIO = 'price_book_ratio'
    PRICE_CASH_FLOW_CURRENT = 'price_cash_flow_current'
    PRICE_EARNINGS_CURRENT = 'price_earnings_current'
    PRICE_EARNINGS_FORWARD_FY = 'price_earnings_forward_fy'
    PRICE_EARNINGS_FWD = 'price_earnings_fwd'
    PRICE_EARNINGS_GROWTH_TTM = 'price_earnings_growth_ttm'
    PRICE_EARNINGS_TTM = 'price_earnings_ttm'
    PRICE_FREE_CASH_FLOW_CURRENT = 'price_free_cash_flow_current'
    PRICE_FREE_CASH_FLOW_TTM = 'price_free_cash_flow_ttm'
    PRICE_REVENUE_TTM = 'price_revenue_ttm'
    PRICE_SALES = 'price_sales'
    PRICE_SALES_CURRENT = 'price_sales_current'
    PRICE_SALES_FWD = 'price_sales_fwd'
    PRICE_SALES_RATIO = 'price_sales_ratio'
    PRICE_TARGET_1Y = 'price_target_1y'
    PRICE_TARGET_1Y_DELTA = 'price_target_1y_delta'
    PRICE_TARGET_AVERAGE = 'price_target_average'
    PRICE_TARGET_HIGH = 'price_target_high'
    PRICE_TARGET_LOW = 'price_target_low'
    PRICE_TARGET_MEDIAN = 'price_target_median'
    PRICE_TO_CASH_F_OPERATING_ACTIVITIES_TTM = 'price_to_cash_f_operating_activities_ttm'
    PRICE_TO_CASH_RATIO = 'price_to_cash_ratio'
    PRICE_TO_WORKING_CAPITAL_FQ = 'price_to_working_capital_fq'
    PRICESCALE = 'pricescale'
    PROVIDER_ID = 'provider-id'
    QUICK_RATIO = 'quick_ratio'
    QUICK_RATIO_CURRENT = 'quick_ratio_current'
    QUICK_RATIO_FQ = 'quick_ratio_fq'
    QUICK_RATIO_FY = 'quick_ratio_fy'
    RATES_CF = 'rates_cf'
    RATES_CURRENT = 'rates_current'
    RATES_DIVIDEND_RECENT = 'rates_dividend_recent'
    RATES_DIVIDEND_UPCOMING = 'rates_dividend_upcoming'
    RATES_EARNINGS_FQ = 'rates_earnings_fq'
    RATES_EARNINGS_NEXT_FQ = 'rates_earnings_next_fq'
    RATES_FH = 'rates_fh'
    RATES_FQ = 'rates_fq'
    RATES_FY = 'rates_fy'
    RATES_MC = 'rates_mc'
    RATES_PT = 'rates_pt'
    RATES_TIME_SERIES = 'rates_time_series'
    RATES_TTM = 'rates_ttm'
    RECEIVABLES_TURNOVER_FQ = 'receivables_turnover_fq'
    RECEIVABLES_TURNOVER_FY = 'receivables_turnover_fy'
    RECOMMENDATION_BUY = 'recommendation_buy'
    RECOMMENDATION_HOLD = 'recommendation_hold'
    RECOMMENDATION_MARK = 'recommendation_mark'
    RECOMMENDATION_OVER = 'recommendation_over'
    RECOMMENDATION_SELL = 'recommendation_sell'
    RECOMMENDATION_TOTAL = 'recommendation_total'
    RECOMMENDATION_UNDER = 'recommendation_under'
    RELATIVE_VOLUME = 'relative_volume'
    RELATIVE_VOLUME_10D_CALC = 'relative_volume_10d_calc'
    RESEARCH_AND_DEV_ESTIMATE_FH = 'research_and_dev_estimate_fh'
    RESEARCH_AND_DEV_ESTIMATE_FQ = 'research_and_dev_estimate_fq'
    RESEARCH_AND_DEV_ESTIMATE_FY = 'research_and_dev_estimate_fy'
    RESEARCH_AND_DEV_ESTIMATE_NTM = 'research_and_dev_estimate_ntm'
    RESEARCH_AND_DEV_FH = 'research_and_dev_fh'
    RESEARCH_AND_DEV_FQ = 'research_and_dev_fq'
    RESEARCH_AND_DEV_FY = 'research_and_dev_fy'
    RESEARCH_AND_DEV_PER_EMPLOYEE_FY = 'research_and_dev_per_employee_fy'
    RESEARCH_AND_DEV_RATIO_FY = 'research_and_dev_ratio_fy'
    RESEARCH_AND_DEV_RATIO_TTM = 'research_and_dev_ratio_ttm'
    RESEARCH_AND_DEV_TTM = 'research_and_dev_ttm'
    RETURN_OF_INVESTED_CAPITAL_PERCENT_TTM = 'return_of_invested_capital_percent_ttm'
    RETURN_ON_ASSETS = 'return_on_assets'
    RETURN_ON_ASSETS_FQ = 'return_on_assets_fq'
    RETURN_ON_ASSETS_FY = 'return_on_assets_fy'
    RETURN_ON_CAPITAL_EMPLOYED_FQ = 'return_on_capital_employed_fq'
    RETURN_ON_CAPITAL_EMPLOYED_FY = 'return_on_capital_employed_fy'
    RETURN_ON_COMMON_EQUITY_FY = 'return_on_common_equity_fy'
    RETURN_ON_COMMON_EQUITY_TTM = 'return_on_common_equity_ttm'
    RETURN_ON_EQUITY = 'return_on_equity'
    RETURN_ON_EQUITY_ADJUST_TO_BOOK_FY = 'return_on_equity_adjust_to_book_fy'
    RETURN_ON_EQUITY_ADJUST_TO_BOOK_TTM = 'return_on_equity_adjust_to_book_ttm'
    RETURN_ON_EQUITY_FQ = 'return_on_equity_fq'
    RETURN_ON_EQUITY_FY = 'return_on_equity_fy'
    RETURN_ON_INVESTED_CAPITAL = 'return_on_invested_capital'
    RETURN_ON_INVESTED_CAPITAL_FQ = 'return_on_invested_capital_fq'
    RETURN_ON_INVESTED_CAPITAL_FY = 'return_on_invested_capital_fy'
    RETURN_ON_TANG_ASSETS_FQ = 'return_on_tang_assets_fq'
    RETURN_ON_TANG_ASSETS_FY = 'return_on_tang_assets_fy'
    RETURN_ON_TANG_EQUITY_FQ = 'return_on_tang_equity_fq'
    RETURN_ON_TANG_EQUITY_FY = 'return_on_tang_equity_fy'
    RETURN_ON_TOTAL_CAPITAL_FQ = 'return_on_total_capital_fq'
    RETURN_ON_TOTAL_CAPITAL_FY = 'return_on_total_capital_fy'
    REVENUE_ESTIMATE_NTM = 'revenue_estimate_ntm'
    REVENUE_FORECAST_FQ = 'revenue_forecast_fq'
    REVENUE_FORECAST_NEXT_FH = 'revenue_forecast_next_fh'
    REVENUE_FORECAST_NEXT_FQ = 'revenue_forecast_next_fq'
    REVENUE_FORECAST_NEXT_FY = 'revenue_forecast_next_fy'
    REVENUE_FQ = 'revenue_fq'
    REVENUE_PER_EMPLOYEE = 'revenue_per_employee'
    REVENUE_PER_EMPLOYEE_FY = 'revenue_per_employee_fy'
    REVENUE_PER_SHARE_CURRENT = 'revenue_per_share_current'
    REVENUE_PER_SHARE_FH = 'revenue_per_share_fh'
    REVENUE_PER_SHARE_FQ = 'revenue_per_share_fq'
    REVENUE_PER_SHARE_FY = 'revenue_per_share_fy'
    REVENUE_PER_SHARE_TTM = 'revenue_per_share_ttm'
    REVENUE_SURPRISE_FQ = 'revenue_surprise_fq'
    REVENUE_SURPRISE_PERCENT_FQ = 'revenue_surprise_percent_fq'
    REVENUES_FQ_H = 'revenues_fq_h'
    RTC = 'rtc'
    SECTOR = 'sector'
    SELECTION_CRITERIA = 'selection_criteria'
    SELL_GEN_ADMIN_EXP_OTHER_FY = 'sell_gen_admin_exp_other_fy'
    SELL_GEN_ADMIN_EXP_OTHER_RATIO_FY = 'sell_gen_admin_exp_other_ratio_fy'
    SELL_GEN_ADMIN_EXP_OTHER_RATIO_TTM = 'sell_gen_admin_exp_other_ratio_ttm'
    SELL_GEN_ADMIN_EXP_OTHER_TTM = 'sell_gen_admin_exp_other_ttm'
    SELL_GEN_ADMIN_EXP_TOTAL_ESTIMATE_FH = 'sell_gen_admin_exp_total_estimate_fh'
    SELL_GEN_ADMIN_EXP_TOTAL_ESTIMATE_FQ = 'sell_gen_admin_exp_total_estimate_fq'
    SELL_GEN_ADMIN_EXP_TOTAL_ESTIMATE_FY = 'sell_gen_admin_exp_total_estimate_fy'
    SELL_GEN_ADMIN_EXP_TOTAL_ESTIMATE_NTM = 'sell_gen_admin_exp_total_estimate_ntm'
    SHARE_BUYBACK_RATIO_FQ = 'share_buyback_ratio_fq'
    SHARE_BUYBACK_RATIO_FY = 'share_buyback_ratio_fy'
    SHARES_OUTSTANDING = 'shares_outstanding'
    SHORT_TERM_DEBT_FQ = 'short_term_debt_fq'
    SHORT_TERM_DEBT_FY = 'short_term_debt_fy'
    SHRHLDRS_EQUITY_FQ = 'shrhldrs_equity_fq'
    SHRHLDRS_EQUITY_FY = 'shrhldrs_equity_fy'
    SHRHLDRS_EQUITY_TO_TOTAL_ASSETS_FQ = 'shrhldrs_equity_to_total_assets_fq'
    SHRHLDRS_EQUITY_TO_TOTAL_ASSETS_FY = 'shrhldrs_equity_to_total_assets_fy'
    SLOAN_RATIO_FY = 'sloan_ratio_fy'
    SLOAN_RATIO_TTM = 'sloan_ratio_ttm'
    SOURCE_LOGOID = 'source-logoid'
    STRATEGY = 'strategy'
    SUBMARKET = 'submarket'
    SUBSESSIONS = 'subsessions'
    SUBTYPE = 'subtype'
    SUM_FOR_ENTERPRISE_VALUE = 'sum_for_enterprise_value'
    SUSTAINABLE_GROWTH_RATE_FY = 'sustainable_growth_rate_fy'
    SUSTAINABLE_GROWTH_RATE_TTM = 'sustainable_growth_rate_ttm'
    TIME = 'time'
    TIME_BUSINESS_DAY = 'time_business_day'
    TOBIN_Q_RATIO_FQ = 'tobin_q_ratio_fq'
    TOBIN_Q_RATIO_FY = 'tobin_q_ratio_fy'
    TOP_REVENUE_COUNTRY_CODE = 'top_revenue_country_code'
    TOTAL_ASSETS = 'total_assets'
    TOTAL_ASSETS_ESTIMATE_FH = 'total_assets_estimate_fh'
    TOTAL_ASSETS_ESTIMATE_FQ = 'total_assets_estimate_fq'
    TOTAL_ASSETS_ESTIMATE_FY = 'total_assets_estimate_fy'
    TOTAL_ASSETS_FQ = 'total_assets_fq'
    TOTAL_ASSETS_FQ_H = 'total_assets_fq_h'
    TOTAL_ASSETS_FY = 'total_assets_fy'
    TOTAL_ASSETS_FY_H = 'total_assets_fy_h'
    TOTAL_ASSETS_PER_EMPLOYEE_FY = 'total_assets_per_employee_fy'
    TOTAL_ASSETS_QOQ_GROWTH_FQ = 'total_assets_qoq_growth_fq'
    TOTAL_ASSETS_TO_EQUITY_FQ = 'total_assets_to_equity_fq'
    TOTAL_ASSETS_TO_EQUITY_FY = 'total_assets_to_equity_fy'
    TOTAL_ASSETS_YOY_GROWTH_FQ = 'total_assets_yoy_growth_fq'
    TOTAL_ASSETS_YOY_GROWTH_FY = 'total_assets_yoy_growth_fy'
    TOTAL_CAPITAL = 'total_capital'
    TOTAL_CASH_DIVIDENDS_PAID_FH = 'total_cash_dividends_paid_fh'
    TOTAL_CASH_DIVIDENDS_PAID_FQ = 'total_cash_dividends_paid_fq'
    TOTAL_CASH_DIVIDENDS_PAID_FY = 'total_cash_dividends_paid_fy'
    TOTAL_CASH_DIVIDENDS_PAID_TTM = 'total_cash_dividends_paid_ttm'
    TOTAL_CURRENT_ASSETS = 'total_current_assets'
    TOTAL_CURRENT_ASSETS_FQ = 'total_current_assets_fq'
    TOTAL_CURRENT_ASSETS_FY = 'total_current_assets_fy'
    TOTAL_CURRENT_LIABILITIES_FQ = 'total_current_liabilities_fq'
    TOTAL_CURRENT_LIABILITIES_FY = 'total_current_liabilities_fy'
    TOTAL_DEBT = 'total_debt'
    TOTAL_DEBT_ESTIMATE_FH = 'total_debt_estimate_fh'
    TOTAL_DEBT_ESTIMATE_FQ = 'total_debt_estimate_fq'
    TOTAL_DEBT_ESTIMATE_FY = 'total_debt_estimate_fy'
    TOTAL_DEBT_FQ = 'total_debt_fq'
    TOTAL_DEBT_FQ_H = 'total_debt_fq_h'
    TOTAL_DEBT_FY = 'total_debt_fy'
    TOTAL_DEBT_FY_H = 'total_debt_fy_h'
    TOTAL_DEBT_PER_EMPLOYEE_FY = 'total_debt_per_employee_fy'
    TOTAL_DEBT_PER_SHARE_CURRENT = 'total_debt_per_share_current'
    TOTAL_DEBT_PER_SHARE_FH = 'total_debt_per_share_fh'
    TOTAL_DEBT_PER_SHARE_FQ = 'total_debt_per_share_fq'
    TOTAL_DEBT_PER_SHARE_FY = 'total_debt_per_share_fy'
    TOTAL_DEBT_QOQ_GROWTH_FQ = 'total_debt_qoq_growth_fq'
    TOTAL_DEBT_TO_CAPITAL_FQ = 'total_debt_to_capital_fq'
    TOTAL_DEBT_TO_CAPITAL_FY = 'total_debt_to_capital_fy'
    TOTAL_DEBT_TO_EBITDA_FQ = 'total_debt_to_ebitda_fq'
    TOTAL_DEBT_TO_EBITDA_FY = 'total_debt_to_ebitda_fy'
    TOTAL_DEBT_YOY_GROWTH_FQ = 'total_debt_yoy_growth_fq'
    TOTAL_DEBT_YOY_GROWTH_FY = 'total_debt_yoy_growth_fy'
    TOTAL_EQUITY_FQ = 'total_equity_fq'
    TOTAL_EQUITY_FY = 'total_equity_fy'
    TOTAL_LIABILITIES_FQ = 'total_liabilities_fq'
    TOTAL_LIABILITIES_FY = 'total_liabilities_fy'
    TOTAL_REVENUE = 'total_revenue'
    TOTAL_REVENUE_5Y_GROWTH_FY = 'total_revenue_5y_growth_fy'
    TOTAL_REVENUE_CAGR_5Y = 'total_revenue_cagr_5y'
    TOTAL_REVENUE_FH = 'total_revenue_fh'
    TOTAL_REVENUE_FQ = 'total_revenue_fq'
    TOTAL_REVENUE_FQ_H = 'total_revenue_fq_h'
    TOTAL_REVENUE_FY = 'total_revenue_fy'
    TOTAL_REVENUE_FY_H = 'total_revenue_fy_h'
    TOTAL_REVENUE_QOQ_GROWTH_FQ = 'total_revenue_qoq_growth_fq'
    TOTAL_REVENUE_TTM = 'total_revenue_ttm'
    TOTAL_REVENUE_TTM_H = 'total_revenue_ttm_h'
    TOTAL_REVENUE_YOY_GROWTH_FQ = 'total_revenue_yoy_growth_fq'
    TOTAL_REVENUE_YOY_GROWTH_FY = 'total_revenue_yoy_growth_fy'
    TOTAL_REVENUE_YOY_GROWTH_TTM = 'total_revenue_yoy_growth_ttm'
    TOTAL_SHARES_OUTSTANDING = 'total_shares_outstanding'
    TOTAL_SHARES_OUTSTANDING_CALCULATED = 'total_shares_outstanding_calculated'
    TOTAL_SHARES_OUTSTANDING_CURRENT = 'total_shares_outstanding_current'
    TOTAL_SHARES_OUTSTANDING_FUNDAMENTAL = 'total_shares_outstanding_fundamental'
    TRANSPARENT_HOLDING_FLAG = 'transparent_holding_flag'
    TYPE = 'type'
    TYPESPECS = 'typespecs'
    UCITS_COMPLIANT_FLAG = 'ucits_compliant_flag'
    UPDATE_TIME = 'update-time'
    UPDATE_MODE = 'update_mode'
    UPDATE_TIME_2 = 'update_time'
    VOLUME = 'volume'
    VOLUME_CHANGE = 'volume_change'
    VOLUME_CHANGE_ABS = 'volume_change_abs'
    WEIGHT_TOP_10 = 'weight_top_10'
    WEIGHT_TOP_25 = 'weight_top_25'
    WEIGHT_TOP_50 = 'weight_top_50'
    WEIGHTING_SCHEME = 'weighting_scheme'
    WORKING_CAPITAL_FQ = 'working_capital_fq'
    WORKING_CAPITAL_PER_SHARE_CURRENT = 'working_capital_per_share_current'
    WORKING_CAPITAL_PER_SHARE_FH = 'working_capital_per_share_fh'
    WORKING_CAPITAL_PER_SHARE_FQ = 'working_capital_per_share_fq'
    WORKING_CAPITAL_PER_SHARE_FY = 'working_capital_per_share_fy'
    YIELD_RECENT = 'yield_recent'
    YIELD_UPCOMING = 'yield_upcoming'
    ZMIJEWSKI_SCORE_FY = 'zmijewski_score_fy'
    ZMIJEWSKI_SCORE_TTM = 'zmijewski_score_ttm'


FIELDS: dict[str, FieldInfo] = {
    'ADR': FieldInfo('ADR', FieldType.NUMBER, 'ADR.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADRP': FieldInfo('ADRP', FieldType.NUMBER, 'ADRP.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX': FieldInfo('ADX', FieldType.NUMBER, 'Average Directional Index (14). Range 0-100; >25 = trending.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI': FieldInfo('ADX+DI', FieldType.NUMBER, 'Positive directional indicator +DI (14). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI[1]': FieldInfo('ADX+DI[1]', FieldType.NUMBER, 'ADX+DI (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_100': FieldInfo('ADX+DI_100', FieldType.NUMBER, 'ADX+DI (100).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_100[1]': FieldInfo('ADX+DI_100[1]', FieldType.NUMBER, 'ADX+DI (100) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_20': FieldInfo('ADX+DI_20', FieldType.NUMBER, 'ADX+DI (20).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_20[1]': FieldInfo('ADX+DI_20[1]', FieldType.NUMBER, 'ADX+DI (20) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_50': FieldInfo('ADX+DI_50', FieldType.NUMBER, 'ADX+DI (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_50[1]': FieldInfo('ADX+DI_50[1]', FieldType.NUMBER, 'ADX+DI (50) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_9': FieldInfo('ADX+DI_9', FieldType.NUMBER, 'ADX+DI (9).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX+DI_9[1]': FieldInfo('ADX+DI_9[1]', FieldType.NUMBER, 'ADX+DI (9) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI': FieldInfo('ADX-DI', FieldType.NUMBER, 'Negative directional indicator -DI (14). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI[1]': FieldInfo('ADX-DI[1]', FieldType.NUMBER, 'ADX DI (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_100': FieldInfo('ADX-DI_100', FieldType.NUMBER, 'ADX DI (100).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_100[1]': FieldInfo('ADX-DI_100[1]', FieldType.NUMBER, 'ADX DI (100) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_20': FieldInfo('ADX-DI_20', FieldType.NUMBER, 'ADX DI (20).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_20[1]': FieldInfo('ADX-DI_20[1]', FieldType.NUMBER, 'ADX DI (20) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_50': FieldInfo('ADX-DI_50', FieldType.NUMBER, 'ADX DI (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_50[1]': FieldInfo('ADX-DI_50[1]', FieldType.NUMBER, 'ADX DI (50) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_9': FieldInfo('ADX-DI_9', FieldType.NUMBER, 'ADX DI (9).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX-DI_9[1]': FieldInfo('ADX-DI_9[1]', FieldType.NUMBER, 'ADX DI (9) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX_100': FieldInfo('ADX_100', FieldType.NUMBER, 'ADX (100).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX_20': FieldInfo('ADX_20', FieldType.NUMBER, 'ADX (20).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX_50': FieldInfo('ADX_50', FieldType.NUMBER, 'ADX (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ADX_9': FieldInfo('ADX_9', FieldType.NUMBER, 'ADX (9).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'AO': FieldInfo('AO', FieldType.NUMBER, 'Awesome Oscillator.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'AO[1]': FieldInfo('AO[1]', FieldType.NUMBER, 'Awesome Oscillator (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'AO[2]': FieldInfo('AO[2]', FieldType.NUMBER, 'AO[2].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ATR': FieldInfo('ATR', FieldType.NUMBER, 'Average True Range (14), absolute price units.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ATRP': FieldInfo('ATRP', FieldType.NUMBER, 'ATRP.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Aroon.Down': FieldInfo('Aroon.Down', FieldType.NUMBER, 'Aroon Down.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Aroon.Up': FieldInfo('Aroon.Up', FieldType.NUMBER, 'Aroon Up.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'AvgValue.Traded_10d': FieldInfo('AvgValue.Traded_10d', FieldType.NUMBER, 'Avgvalue traded 10d.'),
    'AvgValue.Traded_30d': FieldInfo('AvgValue.Traded_30d', FieldType.NUMBER, 'Avgvalue traded 30d.'),
    'AvgValue.Traded_60d': FieldInfo('AvgValue.Traded_60d', FieldType.NUMBER, 'Avgvalue traded 60d.'),
    'AvgValue.Traded_90d': FieldInfo('AvgValue.Traded_90d', FieldType.NUMBER, 'Avgvalue traded 90d.'),
    'BB.basis': FieldInfo('BB.basis', FieldType.NUMBER, 'Bollinger Bands basis.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BB.basis_50': FieldInfo('BB.basis_50', FieldType.NUMBER, 'Bollinger Bands basis (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BB.lower': FieldInfo('BB.lower', FieldType.NUMBER, 'Bollinger Band lower (20,2).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BB.lower_50': FieldInfo('BB.lower_50', FieldType.NUMBER, 'Bollinger Bands lower (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BB.upper': FieldInfo('BB.upper', FieldType.NUMBER, 'Bollinger Band upper (20,2).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BB.upper_50': FieldInfo('BB.upper_50', FieldType.NUMBER, 'Bollinger Bands upper (50).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'BBPower': FieldInfo('BBPower', FieldType.NUMBER, 'Bull Bear Power.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'CCI20': FieldInfo('CCI20', FieldType.NUMBER, 'Commodity Channel Index (20). Typically -200..+200, unbounded.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'CCI20[1]': FieldInfo('CCI20[1]', FieldType.NUMBER, 'CCI20 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.3BlackCrows': FieldInfo('Candle.3BlackCrows', FieldType.NUMBER, 'Candle 3blackcrows.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.3WhiteSoldiers': FieldInfo('Candle.3WhiteSoldiers', FieldType.NUMBER, 'Candle 3whitesoldiers.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.AbandonedBaby.Bearish': FieldInfo('Candle.AbandonedBaby.Bearish', FieldType.NUMBER, 'Candle abandonedbaby bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.AbandonedBaby.Bullish': FieldInfo('Candle.AbandonedBaby.Bullish', FieldType.NUMBER, 'Candle abandonedbaby bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.DarkCloudCover.Bearish': FieldInfo('Candle.DarkCloudCover.Bearish', FieldType.NUMBER, 'Candle darkcloudcover bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Doji': FieldInfo('Candle.Doji', FieldType.NUMBER, 'Candle Doji.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Doji.Dragonfly': FieldInfo('Candle.Doji.Dragonfly', FieldType.NUMBER, 'Candle Doji dragonfly.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Doji.Gravestone': FieldInfo('Candle.Doji.Gravestone', FieldType.NUMBER, 'Candle Doji gravestone.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.DojiStar.Bearish': FieldInfo('Candle.DojiStar.Bearish', FieldType.NUMBER, 'Candle dojistar bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.DojiStar.Bullish': FieldInfo('Candle.DojiStar.Bullish', FieldType.NUMBER, 'Candle dojistar bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.DownsideTasukiGap.Bearish': FieldInfo('Candle.DownsideTasukiGap.Bearish', FieldType.NUMBER, 'Candle downsidetasukigap bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Engulfing.Bearish': FieldInfo('Candle.Engulfing.Bearish', FieldType.NUMBER, 'Candle engulfing bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Engulfing.Bullish': FieldInfo('Candle.Engulfing.Bullish', FieldType.NUMBER, 'Candle engulfing bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.EveningDojiStar.Bearish': FieldInfo('Candle.EveningDojiStar.Bearish', FieldType.NUMBER, 'Candle eveningdojistar bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.EveningStar': FieldInfo('Candle.EveningStar', FieldType.NUMBER, 'Candle eveningstar.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.FallingThreeMethods.Bearish': FieldInfo('Candle.FallingThreeMethods.Bearish', FieldType.NUMBER, 'Candle fallingthreemethods bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.FallingWindow.Bearish': FieldInfo('Candle.FallingWindow.Bearish', FieldType.NUMBER, 'Candle fallingwindow bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Hammer': FieldInfo('Candle.Hammer', FieldType.NUMBER, 'Candle hammer.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.HangingMan': FieldInfo('Candle.HangingMan', FieldType.NUMBER, 'Candle hangingman.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Harami.Bearish': FieldInfo('Candle.Harami.Bearish', FieldType.NUMBER, 'Candle harami bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Harami.Bullish': FieldInfo('Candle.Harami.Bullish', FieldType.NUMBER, 'Candle harami bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.HaramiCross.Bearish': FieldInfo('Candle.HaramiCross.Bearish', FieldType.NUMBER, 'Candle haramicross bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.HaramiCross.Bullish': FieldInfo('Candle.HaramiCross.Bullish', FieldType.NUMBER, 'Candle haramicross bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.InvertedHammer': FieldInfo('Candle.InvertedHammer', FieldType.NUMBER, 'Candle invertedhammer.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Kicking.Bearish': FieldInfo('Candle.Kicking.Bearish', FieldType.NUMBER, 'Candle kicking bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Kicking.Bullish': FieldInfo('Candle.Kicking.Bullish', FieldType.NUMBER, 'Candle kicking bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.LongShadow.Lower': FieldInfo('Candle.LongShadow.Lower', FieldType.NUMBER, 'Candle longshadow Lower.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.LongShadow.Upper': FieldInfo('Candle.LongShadow.Upper', FieldType.NUMBER, 'Candle longshadow Upper.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Marubozu.Black': FieldInfo('Candle.Marubozu.Black', FieldType.NUMBER, 'Candle marubozu Black.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Marubozu.White': FieldInfo('Candle.Marubozu.White', FieldType.NUMBER, 'Candle marubozu White.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.MorningDojiStar.Bullish': FieldInfo('Candle.MorningDojiStar.Bullish', FieldType.NUMBER, 'Candle morningdojistar bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.MorningStar': FieldInfo('Candle.MorningStar', FieldType.NUMBER, 'Candle morningstar.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.OnNeck.Bearish': FieldInfo('Candle.OnNeck.Bearish', FieldType.NUMBER, 'Candle onneck bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.Piercing.Bullish': FieldInfo('Candle.Piercing.Bullish', FieldType.NUMBER, 'Candle piercing bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.RisingThreeMethods.Bullish': FieldInfo('Candle.RisingThreeMethods.Bullish', FieldType.NUMBER, 'Candle risingthreemethods bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.RisingWindow.Bullish': FieldInfo('Candle.RisingWindow.Bullish', FieldType.NUMBER, 'Candle risingwindow bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.ShootingStar': FieldInfo('Candle.ShootingStar', FieldType.NUMBER, 'Candle shootingstar.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.SpinningTop.Black': FieldInfo('Candle.SpinningTop.Black', FieldType.NUMBER, 'Candle spinningtop Black.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.SpinningTop.White': FieldInfo('Candle.SpinningTop.White', FieldType.NUMBER, 'Candle spinningtop White.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.TriStar.Bearish': FieldInfo('Candle.TriStar.Bearish', FieldType.NUMBER, 'Candle tristar bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.TriStar.Bullish': FieldInfo('Candle.TriStar.Bullish', FieldType.NUMBER, 'Candle tristar bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.TweezerBottom.Bullish': FieldInfo('Candle.TweezerBottom.Bullish', FieldType.NUMBER, 'Candle tweezerbottom bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.TweezerTop.Bearish': FieldInfo('Candle.TweezerTop.Bearish', FieldType.NUMBER, 'Candle tweezertop bearish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Candle.UpsideTasukiGap.Bullish': FieldInfo('Candle.UpsideTasukiGap.Bullish', FieldType.NUMBER, 'Candle upsidetasukigap bullish.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ChaikinMoneyFlow': FieldInfo('ChaikinMoneyFlow', FieldType.NUMBER, 'Chaikinmoneyflow.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'DonchCh20.Lower': FieldInfo('DonchCh20.Lower', FieldType.NUMBER, 'Donchch20 Lower.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'DonchCh20.Middle': FieldInfo('DonchCh20.Middle', FieldType.NUMBER, 'Donchch20 middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'DonchCh20.Upper': FieldInfo('DonchCh20.Upper', FieldType.NUMBER, 'Donchch20 Upper.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA10': FieldInfo('EMA10', FieldType.NUMBER, 'EMA10.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA100': FieldInfo('EMA100', FieldType.NUMBER, 'EMA100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA12': FieldInfo('EMA12', FieldType.NUMBER, 'EMA12.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA120': FieldInfo('EMA120', FieldType.NUMBER, 'EMA120.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA13': FieldInfo('EMA13', FieldType.NUMBER, 'EMA13.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA14': FieldInfo('EMA14', FieldType.NUMBER, 'EMA14.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA144': FieldInfo('EMA144', FieldType.NUMBER, 'EMA144.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA15': FieldInfo('EMA15', FieldType.NUMBER, 'EMA15.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA150': FieldInfo('EMA150', FieldType.NUMBER, 'EMA150.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA2': FieldInfo('EMA2', FieldType.NUMBER, 'EMA2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA20': FieldInfo('EMA20', FieldType.NUMBER, 'EMA20.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA200': FieldInfo('EMA200', FieldType.NUMBER, 'EMA200.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA21': FieldInfo('EMA21', FieldType.NUMBER, 'EMA21.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA25': FieldInfo('EMA25', FieldType.NUMBER, 'EMA25.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA250': FieldInfo('EMA250', FieldType.NUMBER, 'EMA250.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA26': FieldInfo('EMA26', FieldType.NUMBER, 'EMA26.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA3': FieldInfo('EMA3', FieldType.NUMBER, 'EMA3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA30': FieldInfo('EMA30', FieldType.NUMBER, 'EMA30.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA300': FieldInfo('EMA300', FieldType.NUMBER, 'EMA300.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA34': FieldInfo('EMA34', FieldType.NUMBER, 'EMA34.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA40': FieldInfo('EMA40', FieldType.NUMBER, 'EMA40.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA5': FieldInfo('EMA5', FieldType.NUMBER, 'EMA5.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA50': FieldInfo('EMA50', FieldType.NUMBER, 'EMA50.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA55': FieldInfo('EMA55', FieldType.NUMBER, 'EMA55.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA6': FieldInfo('EMA6', FieldType.NUMBER, 'EMA6.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA60': FieldInfo('EMA60', FieldType.NUMBER, 'EMA60.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA7': FieldInfo('EMA7', FieldType.NUMBER, 'EMA7.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA75': FieldInfo('EMA75', FieldType.NUMBER, 'EMA75.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA8': FieldInfo('EMA8', FieldType.NUMBER, 'EMA8.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA89': FieldInfo('EMA89', FieldType.NUMBER, 'EMA89.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'EMA9': FieldInfo('EMA9', FieldType.NUMBER, 'EMA9.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'High.1M': FieldInfo('High.1M', FieldType.NUMBER, 'High over 1 month.'),
    'High.1M.Date': FieldInfo('High.1M.Date', FieldType.TIME, 'High over 1 month Date [UNIX timestamp (seconds)].'),
    'High.3M': FieldInfo('High.3M', FieldType.NUMBER, 'High over 3 months.'),
    'High.3M.Date': FieldInfo('High.3M.Date', FieldType.TIME, 'High over 3 months Date [UNIX timestamp (seconds)].'),
    'High.5D': FieldInfo('High.5D', FieldType.NUMBER, 'High 5D.'),
    'High.6M': FieldInfo('High.6M', FieldType.NUMBER, 'High over 6 months.'),
    'High.6M.Date': FieldInfo('High.6M.Date', FieldType.TIME, 'High over 6 months Date [UNIX timestamp (seconds)].'),
    'High.All': FieldInfo('High.All', FieldType.NUMBER, 'All-time high price.'),
    'High.All.Calc': FieldInfo('High.All.Calc', FieldType.NUMBER, 'High over all time calculated.'),
    'High.All.Calc.Date': FieldInfo('High.All.Calc.Date', FieldType.TIME, 'High over all time calculated Date [UNIX timestamp (seconds)].'),
    'High.All.Date': FieldInfo('High.All.Date', FieldType.TIME, 'High over all time Date [UNIX timestamp (seconds)].'),
    'HullMA20': FieldInfo('HullMA20', FieldType.NUMBER, 'Hullma20.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'HullMA200': FieldInfo('HullMA200', FieldType.NUMBER, 'Hullma200.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'HullMA9': FieldInfo('HullMA9', FieldType.NUMBER, 'Hullma9.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.BLine': FieldInfo('Ichimoku.BLine', FieldType.NUMBER, 'Ichimoku BLine.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.BLine_20_60_120_30': FieldInfo('Ichimoku.BLine_20_60_120_30', FieldType.NUMBER, 'Ichimoku BLine (20) (60) (120) (30).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.CLine': FieldInfo('Ichimoku.CLine', FieldType.NUMBER, 'Ichimoku CLine.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.CLine_20_60_120_30': FieldInfo('Ichimoku.CLine_20_60_120_30', FieldType.NUMBER, 'Ichimoku CLine (20) (60) (120) (30).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.Lead1': FieldInfo('Ichimoku.Lead1', FieldType.NUMBER, 'Ichimoku Lead1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.Lead1_20_60_120_30': FieldInfo('Ichimoku.Lead1_20_60_120_30', FieldType.NUMBER, 'Ichimoku Lead1 (20) (60) (120) (30).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.Lead2': FieldInfo('Ichimoku.Lead2', FieldType.NUMBER, 'Ichimoku Lead2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Ichimoku.Lead2_20_60_120_30': FieldInfo('Ichimoku.Lead2_20_60_120_30', FieldType.NUMBER, 'Ichimoku Lead2 (20) (60) (120) (30).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'KltChnl.basis': FieldInfo('KltChnl.basis', FieldType.NUMBER, 'Kltchnl basis.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'KltChnl.lower': FieldInfo('KltChnl.lower', FieldType.NUMBER, 'Kltchnl lower.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'KltChnl.upper': FieldInfo('KltChnl.upper', FieldType.NUMBER, 'Kltchnl upper.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Low.1M': FieldInfo('Low.1M', FieldType.NUMBER, 'Low over 1 month.'),
    'Low.1M.Date': FieldInfo('Low.1M.Date', FieldType.TIME, 'Low over 1 month Date [UNIX timestamp (seconds)].'),
    'Low.3M': FieldInfo('Low.3M', FieldType.NUMBER, 'Low over 3 months.'),
    'Low.3M.Date': FieldInfo('Low.3M.Date', FieldType.TIME, 'Low over 3 months Date [UNIX timestamp (seconds)].'),
    'Low.5D': FieldInfo('Low.5D', FieldType.NUMBER, 'Low 5D.'),
    'Low.6M': FieldInfo('Low.6M', FieldType.NUMBER, 'Low over 6 months.'),
    'Low.6M.Date': FieldInfo('Low.6M.Date', FieldType.TIME, 'Low over 6 months Date [UNIX timestamp (seconds)].'),
    'Low.After.High.All': FieldInfo('Low.After.High.All', FieldType.PRICE, 'Low After High over all time.'),
    'Low.All': FieldInfo('Low.All', FieldType.NUMBER, 'All-time low price.'),
    'Low.All.Calc': FieldInfo('Low.All.Calc', FieldType.NUMBER, 'Low over all time calculated.'),
    'Low.All.Calc.Date': FieldInfo('Low.All.Calc.Date', FieldType.TIME, 'Low over all time calculated Date [UNIX timestamp (seconds)].'),
    'Low.All.Date': FieldInfo('Low.All.Date', FieldType.TIME, 'Low over all time Date [UNIX timestamp (seconds)].'),
    'MACD.hist': FieldInfo('MACD.hist', FieldType.NUMBER, 'MACD hist.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'MACD.macd': FieldInfo('MACD.macd', FieldType.NUMBER, 'MACD line (12,26).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'MACD.signal': FieldInfo('MACD.signal', FieldType.NUMBER, 'MACD signal line (9).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Mom': FieldInfo('Mom', FieldType.NUMBER, 'Momentum (10).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Mom[1]': FieldInfo('Mom[1]', FieldType.NUMBER, 'Momentum (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Mom_14': FieldInfo('Mom_14', FieldType.NUMBER, 'Momentum (14).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Mom_14[1]': FieldInfo('Mom_14[1]', FieldType.NUMBER, 'Momentum (14) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'MoneyFlow': FieldInfo('MoneyFlow', FieldType.NUMBER, 'Moneyflow.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Open.All.Calc': FieldInfo('Open.All.Calc', FieldType.NUMBER, 'Open All calculated.'),
    'P.SAR': FieldInfo('P.SAR', FieldType.NUMBER, 'P SAR.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Perf.10Y': FieldInfo('Perf.10Y', FieldType.NUMBER, 'Price performance over 10 years, percent.'),
    'Perf.10Y_abs': FieldInfo('Perf.10Y_abs', FieldType.NUMBER, 'Performance over 10 years (absolute).'),
    'Perf.1M': FieldInfo('Perf.1M', FieldType.NUMBER, 'Price performance over 1 month, percent.'),
    'Perf.1M.MarketCap': FieldInfo('Perf.1M.MarketCap', FieldType.NUMBER, 'Performance over 1 month marketcap.'),
    'Perf.1M_abs': FieldInfo('Perf.1M_abs', FieldType.NUMBER, 'Performance over 1 month (absolute).'),
    'Perf.1W.MarketCap': FieldInfo('Perf.1W.MarketCap', FieldType.NUMBER, 'Performance 1W marketcap.'),
    'Perf.1Y.MarketCap': FieldInfo('Perf.1Y.MarketCap', FieldType.NUMBER, 'Performance over 1 year marketcap.'),
    'Perf.3M': FieldInfo('Perf.3M', FieldType.NUMBER, 'Price performance over 3 months, percent.'),
    'Perf.3M.MarketCap': FieldInfo('Perf.3M.MarketCap', FieldType.NUMBER, 'Performance over 3 months marketcap.'),
    'Perf.3M_abs': FieldInfo('Perf.3M_abs', FieldType.NUMBER, 'Performance over 3 months (absolute).'),
    'Perf.3Y': FieldInfo('Perf.3Y', FieldType.NUMBER, 'Performance over 3 years.'),
    'Perf.3Y_abs': FieldInfo('Perf.3Y_abs', FieldType.NUMBER, 'Performance over 3 years (absolute).'),
    'Perf.5D': FieldInfo('Perf.5D', FieldType.NUMBER, 'Performance 5D.'),
    'Perf.5D_abs': FieldInfo('Perf.5D_abs', FieldType.NUMBER, 'Performance 5D (absolute).'),
    'Perf.5Y': FieldInfo('Perf.5Y', FieldType.NUMBER, 'Price performance over 5 years, percent.'),
    'Perf.5Y.MarketCap': FieldInfo('Perf.5Y.MarketCap', FieldType.NUMBER, 'Performance over 5 years marketcap.'),
    'Perf.5Y_abs': FieldInfo('Perf.5Y_abs', FieldType.NUMBER, 'Performance over 5 years (absolute).'),
    'Perf.6M': FieldInfo('Perf.6M', FieldType.NUMBER, 'Price performance over 6 months, percent.'),
    'Perf.6M.MarketCap': FieldInfo('Perf.6M.MarketCap', FieldType.NUMBER, 'Performance over 6 months marketcap.'),
    'Perf.6M_abs': FieldInfo('Perf.6M_abs', FieldType.NUMBER, 'Performance over 6 months (absolute).'),
    'Perf.All': FieldInfo('Perf.All', FieldType.NUMBER, 'Price performance since inception, percent.'),
    'Perf.All_abs': FieldInfo('Perf.All_abs', FieldType.NUMBER, 'Performance over all time (absolute).'),
    'Perf.W': FieldInfo('Perf.W', FieldType.NUMBER, 'Price performance over 1 week, percent.'),
    'Perf.W_abs': FieldInfo('Perf.W_abs', FieldType.NUMBER, 'Performance over 1 week (absolute).'),
    'Perf.Y': FieldInfo('Perf.Y', FieldType.NUMBER, 'Price performance over 1 year, percent.'),
    'Perf.YTD': FieldInfo('Perf.YTD', FieldType.NUMBER, 'Price performance year-to-date, percent.'),
    'Perf.YTD.MarketCap': FieldInfo('Perf.YTD.MarketCap', FieldType.NUMBER, 'Performance year-to-date marketcap.'),
    'Perf.YTD_abs': FieldInfo('Perf.YTD_abs', FieldType.NUMBER, 'Performance year-to-date (absolute).'),
    'Perf.Y_abs': FieldInfo('Perf.Y_abs', FieldType.NUMBER, 'Performance over 1 year (absolute).'),
    'Pivot.M.Camarilla.Middle': FieldInfo('Pivot.M.Camarilla.Middle', FieldType.NUMBER, 'Pivot M camarilla middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.R1': FieldInfo('Pivot.M.Camarilla.R1', FieldType.NUMBER, 'Pivot M camarilla R1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.R2': FieldInfo('Pivot.M.Camarilla.R2', FieldType.NUMBER, 'Pivot M camarilla R2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.R3': FieldInfo('Pivot.M.Camarilla.R3', FieldType.NUMBER, 'Pivot M camarilla R3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.S1': FieldInfo('Pivot.M.Camarilla.S1', FieldType.NUMBER, 'Pivot M camarilla S1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.S2': FieldInfo('Pivot.M.Camarilla.S2', FieldType.NUMBER, 'Pivot M camarilla S2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Camarilla.S3': FieldInfo('Pivot.M.Camarilla.S3', FieldType.NUMBER, 'Pivot M camarilla S3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.Middle': FieldInfo('Pivot.M.Classic.Middle', FieldType.NUMBER, 'Pivot M classic middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.R1': FieldInfo('Pivot.M.Classic.R1', FieldType.NUMBER, 'Pivot M classic R1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.R2': FieldInfo('Pivot.M.Classic.R2', FieldType.NUMBER, 'Pivot M classic R2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.R3': FieldInfo('Pivot.M.Classic.R3', FieldType.NUMBER, 'Pivot M classic R3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.S1': FieldInfo('Pivot.M.Classic.S1', FieldType.NUMBER, 'Pivot M classic S1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.S2': FieldInfo('Pivot.M.Classic.S2', FieldType.NUMBER, 'Pivot M classic S2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Classic.S3': FieldInfo('Pivot.M.Classic.S3', FieldType.NUMBER, 'Pivot M classic S3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Demark.Middle': FieldInfo('Pivot.M.Demark.Middle', FieldType.NUMBER, 'Pivot M demark middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Demark.R1': FieldInfo('Pivot.M.Demark.R1', FieldType.NUMBER, 'Pivot M demark R1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Demark.S1': FieldInfo('Pivot.M.Demark.S1', FieldType.NUMBER, 'Pivot M demark S1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.Middle': FieldInfo('Pivot.M.Fibonacci.Middle', FieldType.NUMBER, 'Pivot M fibonacci middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.R1': FieldInfo('Pivot.M.Fibonacci.R1', FieldType.NUMBER, 'Pivot M fibonacci R1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.R2': FieldInfo('Pivot.M.Fibonacci.R2', FieldType.NUMBER, 'Pivot M fibonacci R2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.R3': FieldInfo('Pivot.M.Fibonacci.R3', FieldType.NUMBER, 'Pivot M fibonacci R3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.S1': FieldInfo('Pivot.M.Fibonacci.S1', FieldType.NUMBER, 'Pivot M fibonacci S1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.S2': FieldInfo('Pivot.M.Fibonacci.S2', FieldType.NUMBER, 'Pivot M fibonacci S2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Fibonacci.S3': FieldInfo('Pivot.M.Fibonacci.S3', FieldType.NUMBER, 'Pivot M fibonacci S3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.Middle': FieldInfo('Pivot.M.Woodie.Middle', FieldType.NUMBER, 'Pivot M woodie middle.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.R1': FieldInfo('Pivot.M.Woodie.R1', FieldType.NUMBER, 'Pivot M woodie R1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.R2': FieldInfo('Pivot.M.Woodie.R2', FieldType.NUMBER, 'Pivot M woodie R2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.R3': FieldInfo('Pivot.M.Woodie.R3', FieldType.NUMBER, 'Pivot M woodie R3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.S1': FieldInfo('Pivot.M.Woodie.S1', FieldType.NUMBER, 'Pivot M woodie S1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.S2': FieldInfo('Pivot.M.Woodie.S2', FieldType.NUMBER, 'Pivot M woodie S2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Pivot.M.Woodie.S3': FieldInfo('Pivot.M.Woodie.S3', FieldType.NUMBER, 'Pivot M woodie S3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'ROC': FieldInfo('ROC', FieldType.NUMBER, 'Rate of change.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI': FieldInfo('RSI', FieldType.NUMBER, 'Relative Strength Index (14). Range 0-100; <30 oversold, >70 overbought.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI10': FieldInfo('RSI10', FieldType.NUMBER, 'RSI10.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI10[1]': FieldInfo('RSI10[1]', FieldType.NUMBER, 'RSI10 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI2': FieldInfo('RSI2', FieldType.NUMBER, 'RSI2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI20': FieldInfo('RSI20', FieldType.NUMBER, 'RSI20.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI20[1]': FieldInfo('RSI20[1]', FieldType.NUMBER, 'RSI20 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI21': FieldInfo('RSI21', FieldType.NUMBER, 'RSI21.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI21[1]': FieldInfo('RSI21[1]', FieldType.NUMBER, 'RSI21 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI2[1]': FieldInfo('RSI2[1]', FieldType.NUMBER, 'RSI2 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI3': FieldInfo('RSI3', FieldType.NUMBER, 'RSI3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI30': FieldInfo('RSI30', FieldType.NUMBER, 'RSI30.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI30[1]': FieldInfo('RSI30[1]', FieldType.NUMBER, 'RSI30 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI3[1]': FieldInfo('RSI3[1]', FieldType.NUMBER, 'RSI3 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI4': FieldInfo('RSI4', FieldType.NUMBER, 'RSI4.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI4[1]': FieldInfo('RSI4[1]', FieldType.NUMBER, 'RSI4 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI5': FieldInfo('RSI5', FieldType.NUMBER, 'RSI5.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI5[1]': FieldInfo('RSI5[1]', FieldType.NUMBER, 'RSI5 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI7': FieldInfo('RSI7', FieldType.NUMBER, 'Relative Strength Index (7). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI7[1]': FieldInfo('RSI7[1]', FieldType.NUMBER, 'RSI7 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI9': FieldInfo('RSI9', FieldType.NUMBER, 'RSI9.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI9[1]': FieldInfo('RSI9[1]', FieldType.NUMBER, 'RSI9 (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'RSI[1]': FieldInfo('RSI[1]', FieldType.NUMBER, 'RSI (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.BBPower': FieldInfo('Rec.BBPower', FieldType.NUMBER, 'Recommendation bbpower.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.HullMA9': FieldInfo('Rec.HullMA9', FieldType.NUMBER, 'Recommendation hullma9.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.Ichimoku': FieldInfo('Rec.Ichimoku', FieldType.NUMBER, 'Recommendation ichimoku.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.Stoch.RSI': FieldInfo('Rec.Stoch.RSI', FieldType.NUMBER, 'Recommendation stochastic RSI.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.UO': FieldInfo('Rec.UO', FieldType.NUMBER, 'Recommendation Ultimate Oscillator.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.VWMA': FieldInfo('Rec.VWMA', FieldType.NUMBER, 'Recommendation VWMA.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Rec.WR': FieldInfo('Rec.WR', FieldType.NUMBER, 'Recommendation Williams %R.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Recommend.All': FieldInfo('Recommend.All', FieldType.NUMBER, 'TradingView overall technical rating: -1 (strong sell) .. +1 (strong buy).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Recommend.MA': FieldInfo('Recommend.MA', FieldType.NUMBER, 'Technical rating from moving averages: -1 .. +1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Recommend.Other': FieldInfo('Recommend.Other', FieldType.NUMBER, 'Technical rating from oscillators: -1 .. +1.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA10': FieldInfo('SMA10', FieldType.NUMBER, 'SMA10.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA100': FieldInfo('SMA100', FieldType.NUMBER, 'SMA100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA12': FieldInfo('SMA12', FieldType.NUMBER, 'SMA12.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA120': FieldInfo('SMA120', FieldType.NUMBER, 'SMA120.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA13': FieldInfo('SMA13', FieldType.NUMBER, 'SMA13.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA14': FieldInfo('SMA14', FieldType.NUMBER, 'SMA14.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA144': FieldInfo('SMA144', FieldType.NUMBER, 'SMA144.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA15': FieldInfo('SMA15', FieldType.NUMBER, 'SMA15.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA150': FieldInfo('SMA150', FieldType.NUMBER, 'SMA150.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA2': FieldInfo('SMA2', FieldType.NUMBER, 'SMA2.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA20': FieldInfo('SMA20', FieldType.NUMBER, 'SMA20.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA200': FieldInfo('SMA200', FieldType.NUMBER, 'SMA200.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA21': FieldInfo('SMA21', FieldType.NUMBER, 'SMA21.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA25': FieldInfo('SMA25', FieldType.NUMBER, 'SMA25.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA250': FieldInfo('SMA250', FieldType.NUMBER, 'SMA250.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA26': FieldInfo('SMA26', FieldType.NUMBER, 'SMA26.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA3': FieldInfo('SMA3', FieldType.NUMBER, 'SMA3.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA30': FieldInfo('SMA30', FieldType.NUMBER, 'SMA30.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA300': FieldInfo('SMA300', FieldType.NUMBER, 'SMA300.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA34': FieldInfo('SMA34', FieldType.NUMBER, 'SMA34.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA40': FieldInfo('SMA40', FieldType.NUMBER, 'SMA40.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA5': FieldInfo('SMA5', FieldType.NUMBER, 'SMA5.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA50': FieldInfo('SMA50', FieldType.NUMBER, 'SMA50.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA55': FieldInfo('SMA55', FieldType.NUMBER, 'SMA55.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA6': FieldInfo('SMA6', FieldType.NUMBER, 'SMA6.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA60': FieldInfo('SMA60', FieldType.NUMBER, 'SMA60.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA7': FieldInfo('SMA7', FieldType.NUMBER, 'SMA7.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA75': FieldInfo('SMA75', FieldType.NUMBER, 'SMA75.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA8': FieldInfo('SMA8', FieldType.NUMBER, 'SMA8.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA89': FieldInfo('SMA89', FieldType.NUMBER, 'SMA89.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'SMA9': FieldInfo('SMA9', FieldType.NUMBER, 'SMA9.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D': FieldInfo('Stoch.D', FieldType.NUMBER, 'Stochastic %D (14,3,3). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D[1]': FieldInfo('Stoch.D[1]', FieldType.NUMBER, 'Stochastic D (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_14_1_3': FieldInfo('Stoch.D_14_1_3', FieldType.NUMBER, 'Stochastic D (14) (1) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_14_1_3[1]': FieldInfo('Stoch.D_14_1_3[1]', FieldType.NUMBER, 'Stochastic D (14) (1) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_5_3_3': FieldInfo('Stoch.D_5_3_3', FieldType.NUMBER, 'Stochastic D (5) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_5_3_3[1]': FieldInfo('Stoch.D_5_3_3[1]', FieldType.NUMBER, 'Stochastic D (5) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_6_3_3': FieldInfo('Stoch.D_6_3_3', FieldType.NUMBER, 'Stochastic D (6) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_6_3_3[1]': FieldInfo('Stoch.D_6_3_3[1]', FieldType.NUMBER, 'Stochastic D (6) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_8_3_3': FieldInfo('Stoch.D_8_3_3', FieldType.NUMBER, 'Stochastic D (8) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.D_8_3_3[1]': FieldInfo('Stoch.D_8_3_3[1]', FieldType.NUMBER, 'Stochastic D (8) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K': FieldInfo('Stoch.K', FieldType.NUMBER, 'Stochastic %K (14,3,3). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K[1]': FieldInfo('Stoch.K[1]', FieldType.NUMBER, 'Stochastic K (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_14_1_3': FieldInfo('Stoch.K_14_1_3', FieldType.NUMBER, 'Stochastic K (14) (1) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_14_1_3[1]': FieldInfo('Stoch.K_14_1_3[1]', FieldType.NUMBER, 'Stochastic K (14) (1) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_5_3_3': FieldInfo('Stoch.K_5_3_3', FieldType.NUMBER, 'Stochastic K (5) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_5_3_3[1]': FieldInfo('Stoch.K_5_3_3[1]', FieldType.NUMBER, 'Stochastic K (5) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_6_3_3': FieldInfo('Stoch.K_6_3_3', FieldType.NUMBER, 'Stochastic K (6) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_6_3_3[1]': FieldInfo('Stoch.K_6_3_3[1]', FieldType.NUMBER, 'Stochastic K (6) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_8_3_3': FieldInfo('Stoch.K_8_3_3', FieldType.NUMBER, 'Stochastic K (8) (3) (3).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.K_8_3_3[1]': FieldInfo('Stoch.K_8_3_3[1]', FieldType.NUMBER, 'Stochastic K (8) (3) (3) (previous bar).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.RSI.D': FieldInfo('Stoch.RSI.D', FieldType.NUMBER, 'Stochastic RSI %D. Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Stoch.RSI.K': FieldInfo('Stoch.RSI.K', FieldType.NUMBER, 'Stochastic RSI %K. Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'UO': FieldInfo('UO', FieldType.NUMBER, 'Ultimate Oscillator (7,14,28). Range 0-100.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'VWAP': FieldInfo('VWAP', FieldType.NUMBER, 'Volume-weighted average price for the session.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'VWMA': FieldInfo('VWMA', FieldType.NUMBER, 'VWMA.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'Volatility.D': FieldInfo('Volatility.D', FieldType.NUMBER, 'Daily volatility, percent.'),
    'Volatility.M': FieldInfo('Volatility.M', FieldType.NUMBER, 'Monthly volatility, percent.'),
    'Volatility.W': FieldInfo('Volatility.W', FieldType.NUMBER, 'Weekly volatility, percent.'),
    'W.R': FieldInfo('W.R', FieldType.NUMBER, 'Williams %R (14). Range -100..0; <-80 oversold, >-20 overbought.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'active_symbol': FieldInfo('active_symbol', FieldType.BOOL, 'True when the symbol is actively trading. Values: true/false.'),
    'actively_managed': FieldInfo('actively_managed', FieldType.TEXT, 'Whether the fund is actively managed.', values=('0', '1')),
    'after_tax_margin': FieldInfo('after_tax_margin', FieldType.PERCENT, 'After tax margin [percentage points (12.5 means 12.5%)].'),
    'all_time_high': FieldInfo('all_time_high', FieldType.PRICE, 'All time high.'),
    'all_time_high_day': FieldInfo('all_time_high_day', FieldType.TIME, 'All time high day [UNIX timestamp (seconds)].'),
    'all_time_low': FieldInfo('all_time_low', FieldType.PRICE, 'All time low.'),
    'all_time_low_day': FieldInfo('all_time_low_day', FieldType.TIME, 'All time low day [UNIX timestamp (seconds)].'),
    'all_time_open': FieldInfo('all_time_open', FieldType.PRICE, 'All time open.'),
    'altman_z_score_fy': FieldInfo('altman_z_score_fy', FieldType.NUMBER, 'Altman z score (fiscal year).'),
    'altman_z_score_ttm': FieldInfo('altman_z_score_ttm', FieldType.NUMBER, 'Altman z score (trailing twelve months).'),
    'amount_recent': FieldInfo('amount_recent', FieldType.FUNDAMENTAL_PRICE, 'Amount recent [monetary value in fundamental/fund currency].'),
    'amount_upcoming': FieldInfo('amount_upcoming', FieldType.FUNDAMENTAL_PRICE, 'Amount upcoming [monetary value in fundamental/fund currency].'),
    'asset_class': FieldInfo('asset_class', FieldType.TEXT, "Fund asset class (internal id; select 'asset_class.tr' as a column for the readable label, e.g. Equity).", values=('1af0389838508d7016a9841eb6273962', '4071518f1736a5a43dae51b47590322f', '8fe80395f389e29e3ea42210337f0350', 'b090e99b8d95f5837ec178c2d3d3fc50', 'b6e443a6c4a8a2e7918c5dbf3d45c796', 'c05f85d35d1cd0be6ebb2af4be16e06a')),
    'asset_turnover_current': FieldInfo('asset_turnover_current', FieldType.NUMBER, 'Asset turnover current.'),
    'asset_turnover_fy': FieldInfo('asset_turnover_fy', FieldType.NUMBER, 'Asset turnover (fiscal year).'),
    'aum': FieldInfo('aum', FieldType.FUNDAMENTAL_PRICE, 'Assets under management (fund currency).'),
    'aum_perf.1M': FieldInfo('aum_perf.1M', FieldType.NUMBER, 'Assets under management performance 1M.'),
    'aum_perf.1Y': FieldInfo('aum_perf.1Y', FieldType.NUMBER, 'Assets under management performance 1Y.'),
    'aum_perf.3M': FieldInfo('aum_perf.3M', FieldType.NUMBER, 'Assets under management performance 3M.'),
    'aum_perf.3Y': FieldInfo('aum_perf.3Y', FieldType.NUMBER, 'Assets under management performance 3Y.'),
    'aum_perf.5Y': FieldInfo('aum_perf.5Y', FieldType.NUMBER, 'Assets under management performance 5Y.'),
    'aum_perf.YTD': FieldInfo('aum_perf.YTD', FieldType.NUMBER, 'Assets under management performance year-to-date.'),
    'average_volume': FieldInfo('average_volume', FieldType.NUMBER, 'Average volume.'),
    'average_volume_10d_calc': FieldInfo('average_volume_10d_calc', FieldType.NUMBER, 'Average daily volume, 10 days.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'average_volume_30d_calc': FieldInfo('average_volume_30d_calc', FieldType.NUMBER, 'Average daily volume, 30 days.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'average_volume_60d_calc': FieldInfo('average_volume_60d_calc', FieldType.NUMBER, 'Average daily volume, 60 days.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'average_volume_90d_calc': FieldInfo('average_volume_90d_calc', FieldType.NUMBER, 'Average daily volume, 90 days.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'bars_count': FieldInfo('bars_count', FieldType.NUMBER, 'Bars count.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'base_currency_kind': FieldInfo('base_currency_kind', FieldType.TEXT, 'Base currency kind.'),
    'basic_eps_net_income': FieldInfo('basic_eps_net_income', FieldType.FUNDAMENTAL_PRICE, 'Basic EPS net income [monetary value in fundamental/fund currency].'),
    'beta_1_year': FieldInfo('beta_1_year', FieldType.NUMBER, 'Beta vs the market over 1 year (1.0 = market-like risk).'),
    'beta_3_year': FieldInfo('beta_3_year', FieldType.NUMBER, 'Beta vs the market over 3 years.'),
    'beta_5_year': FieldInfo('beta_5_year', FieldType.NUMBER, 'Beta vs the market over 5 years.'),
    'book_tangible_per_share_current': FieldInfo('book_tangible_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Book tangible per share current [monetary value in fundamental/fund currency].'),
    'book_tangible_per_share_fh': FieldInfo('book_tangible_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Book tangible per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'book_tangible_per_share_fq': FieldInfo('book_tangible_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Book tangible per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'book_tangible_per_share_fy': FieldInfo('book_tangible_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Book tangible per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_current': FieldInfo('book_value_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Book value per share current [monetary value in fundamental/fund currency].'),
    'book_value_per_share_estimate_fh': FieldInfo('book_value_per_share_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Book value per share estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_estimate_fq': FieldInfo('book_value_per_share_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Book value per share estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_estimate_fy': FieldInfo('book_value_per_share_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Book value per share estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_fh': FieldInfo('book_value_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Book value per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_fq': FieldInfo('book_value_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Book value per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'book_value_per_share_fy': FieldInfo('book_value_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Book value per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'brand': FieldInfo('brand', FieldType.TEXT, 'Fund brand (e.g. Vanguard, iShares).', values=('21Shares', '3Edge', '3iQ', 'AAM', 'AB Funds', 'ACSI Funds', 'ACV', 'ADRhedged', 'AGF', 'ALPS', 'AMG Funds', 'AOT', 'ARK', 'ARS', 'ATAC', 'AXS Investments', 'Abacus', 'Absolute', 'Academy', 'Acquirers Fund', 'ActivePassive', 'Acuitas', 'Adaptiv', 'Adaptive', 'Adasina', 'Advent', 'AdvisorShares', 'Akre', 'Alaska', 'Alerian', 'Alexis', 'Alger', 'Alki', 'Allianz', 'Allspring', 'Alpha', 'Alpha Architect', 'Alpha Blue Capital', 'Alpha Brands', 'Alphabit', 'Alternative Access', 'Altrius', 'Altshares', 'Amana', 'American Beacon', 'American Century', 'Amplify', 'Amplius', 'Amundi', 'Anfield', 'Angel Oak', 'Anydrus', 'Applied Finance', 'Aptus', 'Archer Funds', 'Argent', 'Arimathea', 'Arin', 'Aristotle', 'Arlington', 'Armada ETF Advisors', 'Armor', 'Arrow Funds', 'ArrowShares', 'Astoria', 'Atlas', 'Aura', 'Avantis', 'Avory', 'Avos', 'Aztlan', 'BBH', 'BMO', 'BNY Mellon', 'BWM', 'Bahl & Gaynor', 'Baillie Gifford Funds', 'Ballast', 'Bancreek', 'Barclays', 'Baron', 'Bastion', 'Beacon', 'BeeHive', 'BetaPro', 'Billionaires', 'Bitwise', 'Bluemonte', 'Blueprint', 'BondBloxx', 'Brandes', 'BrandywineGLOBAL', 'Brendan Wood', 'Bridges Capital', 'Bridgeway', 'Brookmont', 'Brookstone', 'Brown Advisory', 'BufferLABS', 'Build', 'Burney', 'Bushido', 'CCM', 'CI', 'CORE16', 'COtwo', 'Cabana', 'Calamos', 'Calvert', 'Cambiar Funds', 'Cambria', 'Canary', 'CapForce', 'Capital Group', 'Carbon Collective', 'Castellan', 'CastleArk', 'Chesapeake', 'ChinaAMC', 'City Different', 'ClearBridge', 'ClearShares', 'Climate Global', 'Clockwise Capital', 'Clough', 'Coastal', 'Cohen & Steers', 'CoinShares', 'Columbia', 'Concourse', 'Conductor Fund', 'Congress', 'Convergence', 'Core Alternative', 'CoreValues Alpha', 'Corgi', 'Counterpoint', 'CresAlta', 'Crossmark', 'Cullen', 'Cultivar', 'Cyber Hornet', 'DAC', 'DB', 'DGA', 'Dakota', 'Dana', 'Davis', 'Day Hagan', 'Defender', 'Defiance', 'Diamond Hill', 'Dimensional', 'Direxion', 'Discipline Funds', 'Distillate', 'Donoghue Forlines', 'DoubleLine', 'Draco', 'EA Series Trust', 'EMQQ Global', 'ERShares', 'ETFB', 'ETRACS', 'Eagle', 'Eaton Vance', 'Eldridge', 'Elm', 'Emerald', 'Equable', 'Euclidean', 'Even Herd', 'Eventide', 'Evoke', 'F/m', 'FINQ', 'FM', 'FPA', 'FT Vest', 'Fairlead', 'Faith Investor Services', 'Federated Hermes', 'Fidelity', 'Fidelity Advisor', 'First Eagle', 'First Manhattan', 'First Trust', 'Fitzgerald', 'FlexShares', 'FolioBeyond', 'Formidable', 'Fortuna', 'Founder', 'Franklin', 'Franklin Templeton', 'Free Market', 'Freedom', 'Freedom Day', 'Frontier', 'FundX', 'Fundsmith', 'Fundstrat', 'GGM', 'GMO', 'GQG Partners', 'GSR', 'Gabelli', 'Gadsden', 'GammaRoad', 'Genter Capital', 'Global X', 'Golden Eagle', 'Goldman Sachs', 'Goose Hollow', 'Gotham', 'GraniteShares', 'Grayscale', 'Grizzle', 'Guggenheim', 'Guinness Atkinson', 'Guru', 'HCM', 'Harbor', 'Harding Loevner', 'Harrison Street', 'Hartford', 'Hashdex', 'Hedgeye', 'Hennessy', 'Hexis', 'Hilton', 'Honeytree', 'Horizon', 'Horizon Kinetics', 'Horizons', 'Hotchkis & Wiley', 'Hoya', 'Hull', 'Humilis', 'Hypatia Capital', 'IDX', 'Impact Shares', 'Impax', 'IncomeSTKd', 'Indexperts', 'InfraCap', 'Innovator', 'Inspire', 'Intech ETFs', 'Invesco', 'JLens', 'JPMorgan', 'Janus Henderson', 'Janus Henderson Tabula', 'Jensen', 'John Hancock', 'KKM Financial', 'Keating', 'Kensington', 'Kingsbarn', 'Kovitz', 'KraneShares', 'Kurv', 'L&G', 'LOGIQ', 'LSV', 'Langar', 'Lazard', 'LeaderShares', 'Leatherback', 'Leuthold', 'Leverage Shares', 'Liberty One', 'LionShares', 'Little Harbor Advisors', 'Logan', 'Long Pond', 'Longview', 'M.D. Sass', 'MC', 'MFS', 'MIG', 'MKAM', 'MRBL', 'MUFG', 'MUSQ', 'Madison', 'Madison Avenue', 'Main Funds', 'Mairs & Power', 'Man', 'Mango', 'Manzil', 'MarketDesk', 'Mason Capital', 'Matrix', 'Matthews', 'Max', 'McElhenny Sheffield', 'Measured Risk Portfolios', 'Meridian', 'Militia', 'Miller', 'Milliman', 'Mohr Funds', 'Monarch', 'Moonvest', 'Morgan Dempsey', 'Morgan Stanley', 'Motley Fool', 'Myriad Capital', 'NETL', 'NEXT FUNDS', 'NPF', 'Natixis', 'Ned Davis Research', 'Nelson', 'Neos', 'NestYield', 'Neuberger Berman', 'New York Life Investments', 'Nicholas', 'Nomura', 'North Shore', 'North Square', 'Northern Trust', 'NovaTide', 'Nuveen', 'OTG', 'Oakmark', 'Obra', 'Ocean Park', 'Oneascent', 'Onefund', 'Opportunistic', 'Optimize', 'Opus Capital Management', 'Osprey', 'Overlay Shares', 'PGIM', 'PIMCO', 'PL', 'PLUS', 'PMV', 'Pabrai', 'Pacer', 'Pacific Funds', 'Palmer Square', 'Parametric', 'Pareto', 'Parnassus Investments', 'Pathfinder', 'PeakShares', 'Peerless', 'Performance Trust', 'Pictet', 'Pinnacle', 'PlanRock', 'Polen', 'Porter & Company', 'Portfolio Building Block', 'Praxis', 'Principal', 'ProShares', 'Procure', 'Prospera Funds', 'PurePlay', 'Purpose', 'Putnam', 'Pzena', 'Q3', 'QRAFT', 'Quadratic', 'Qualivian', 'RAFI Indices', 'RAM', 'RBC', 'REX Microsectors', 'REX Shares', 'REX-Osprey', 'ROBO Global', 'ROC', 'Rainwater', 'Range', 'Rareview Funds', 'Rayliant', 'Raymond James', 'Reckoner', 'Regan', 'Relative Sentiment', 'Renaissance', 'Return Stacked', 'Ritholtz', 'River1', 'RiverNorth', 'RockCreek', 'Rockefeller', 'Roundhill', 'Ruk', 'Russell Investments', 'SEI', 'SMI Funds', 'SP Funds', 'SPDR', 'SRH', 'STF', 'SWP', 'Saba', 'SanJac Alpha', 'Sapient', 'Sarmaya Partners', 'Scharf', 'Schwab', 'Segall Bryant & Hamill', 'Shelton Capital', 'Simplify', 'Skylar', 'Smart', 'SoFi', 'SonicShares', 'Sophus', 'Sound Income Strategies', 'SoundWatch Capital', "Sovereign's", 'Sparkline', 'Spear', 'Sprott', 'Stacked', 'Stance', 'State Street', 'Sterling Capital', 'StockSnips', 'Stone Ridge', 'Strategas', 'Strategy Shares', 'Stratified', 'Strive', 'Subversive', 'Summit Global Investments', 'Suncoast', 'Swan', 'Swisscanto', 'Symmetry Panoramic', 'T-Rex', 'T. Rowe Price', 'TCW', 'THOR', 'Tactical Funds', 'TappAlpha', 'Tema', 'Templeton', 'Teucrium', 'Texas Capital', 'The Brinsmere Funds', 'The Future Fund', 'The Nightview', 'Themes', 'Thornburg', 'Thrivent', 'TimesSquare', 'Timothy', 'Toews', 'Tortoise', 'Touchstone', 'Towle', 'TradersAI', 'Tradr', 'Transamerica', 'Tremblant', 'TrueShares', 'Truth Social', 'Tuttle Capital', 'Tweedy, Browne Co.', 'Twin Oak', 'US Commodity Funds', 'US Global', 'USCF', 'USCF Advisers', 'UVA', 'Unlimited', 'VanEck', 'Vanguard', 'Variant Perception', 'Vegashares', 'Vert', 'VictoryShares', 'Vident', 'Virtus', 'VistaShares', 'Volatility Shares', 'Vontobel', 'Vox', 'Voya', 'WBI Shares', 'WEBs', 'WHITEWOLF', 'Wahed', 'WarCap', 'Warren', 'Wasatch', 'Wayfinder', 'WealthTrust', 'Wedbush', 'Weitz', 'Western Asset', 'Westwood', 'Wisdom', 'WisdomTree', 'Worth Charting', 'X-Square', 'XFUNDS', 'Xtrackers', 'Yall Street', 'YieldMax', 'Yoke', 'ZEGA', 'Zacks', 'aberdeen', 'iM', 'iMGP', 'iPath', 'iShares', 'xETFs')),
    'buyback_yield': FieldInfo('buyback_yield', FieldType.FUNDAMENTAL_PRICE, 'Buyback yield [monetary value in fundamental/fund currency].'),
    'capex_per_share_current': FieldInfo('capex_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Capex per share current [monetary value in fundamental/fund currency].'),
    'capex_per_share_fh': FieldInfo('capex_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Capex per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'capex_per_share_fq': FieldInfo('capex_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Capex per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'capex_per_share_fy': FieldInfo('capex_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Capex per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'capex_per_share_ttm': FieldInfo('capex_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'Capex per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_estimate_fh': FieldInfo('capital_expenditures_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_estimate_fq': FieldInfo('capital_expenditures_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_estimate_fy': FieldInfo('capital_expenditures_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_estimate_ntm': FieldInfo('capital_expenditures_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures estimate ntm [monetary value in fundamental/fund currency].'),
    'capital_expenditures_fh': FieldInfo('capital_expenditures_fh', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_fq': FieldInfo('capital_expenditures_fq', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_fy': FieldInfo('capital_expenditures_fy', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures (fiscal year) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_qoq_growth_fq': FieldInfo('capital_expenditures_qoq_growth_fq', FieldType.PERCENT, 'Capital expenditures quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'capital_expenditures_ttm': FieldInfo('capital_expenditures_ttm', FieldType.FUNDAMENTAL_PRICE, 'Capital expenditures (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'capital_expenditures_unchanged_fq_h': FieldInfo('capital_expenditures_unchanged_fq_h', FieldType.NUM_SLICE, 'Capital expenditures unchanged (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'capital_expenditures_unchanged_fy_h': FieldInfo('capital_expenditures_unchanged_fy_h', FieldType.NUM_SLICE, 'Capital expenditures unchanged (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'capital_expenditures_unchanged_ttm_h': FieldInfo('capital_expenditures_unchanged_ttm_h', FieldType.NUM_SLICE, 'Capital expenditures unchanged (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'capital_expenditures_yoy_growth_fq': FieldInfo('capital_expenditures_yoy_growth_fq', FieldType.PERCENT, 'Capital expenditures year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'capital_expenditures_yoy_growth_fy': FieldInfo('capital_expenditures_yoy_growth_fy', FieldType.PERCENT, 'Capital expenditures year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'capital_expenditures_yoy_growth_ttm': FieldInfo('capital_expenditures_yoy_growth_ttm', FieldType.PERCENT, 'Capital expenditures year-over-year growth (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'cash_dividend_coverage_ratio_fy': FieldInfo('cash_dividend_coverage_ratio_fy', FieldType.NUMBER, 'Cash dividend coverage ratio (fiscal year).'),
    'cash_dividend_coverage_ratio_ttm': FieldInfo('cash_dividend_coverage_ratio_ttm', FieldType.NUMBER, 'Cash dividend coverage ratio (trailing twelve months).'),
    'cash_f_financing_activities_estimate_fh': FieldInfo('cash_f_financing_activities_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_estimate_fq': FieldInfo('cash_f_financing_activities_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_estimate_fy': FieldInfo('cash_f_financing_activities_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_estimate_ntm': FieldInfo('cash_f_financing_activities_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities estimate ntm [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_fh': FieldInfo('cash_f_financing_activities_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_fq': FieldInfo('cash_f_financing_activities_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_fy': FieldInfo('cash_f_financing_activities_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_financing_activities_ttm': FieldInfo('cash_f_financing_activities_ttm', FieldType.FUNDAMENTAL_PRICE, 'Cash from financing activities (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_estimate_fh': FieldInfo('cash_f_investing_activities_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_estimate_fq': FieldInfo('cash_f_investing_activities_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_estimate_fy': FieldInfo('cash_f_investing_activities_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_estimate_ntm': FieldInfo('cash_f_investing_activities_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities estimate ntm [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_fh': FieldInfo('cash_f_investing_activities_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_fq': FieldInfo('cash_f_investing_activities_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_fy': FieldInfo('cash_f_investing_activities_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_investing_activities_ttm': FieldInfo('cash_f_investing_activities_ttm', FieldType.FUNDAMENTAL_PRICE, 'Cash from investing activities (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_estimate_fh': FieldInfo('cash_f_operating_activities_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_estimate_fq': FieldInfo('cash_f_operating_activities_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_estimate_fy': FieldInfo('cash_f_operating_activities_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_estimate_ntm': FieldInfo('cash_f_operating_activities_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities estimate ntm [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_fh': FieldInfo('cash_f_operating_activities_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_fq': FieldInfo('cash_f_operating_activities_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_fy': FieldInfo('cash_f_operating_activities_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_f_operating_activities_ttm': FieldInfo('cash_f_operating_activities_ttm', FieldType.FUNDAMENTAL_PRICE, 'Cash from operating activities (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'cash_n_equivalents_fq': FieldInfo('cash_n_equivalents_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash and equivalents (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_n_equivalents_fy': FieldInfo('cash_n_equivalents_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash and equivalents (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_estimate_fh': FieldInfo('cash_n_short_term_invest_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash and short term invest estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_estimate_fq': FieldInfo('cash_n_short_term_invest_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash and short term invest estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_estimate_fy': FieldInfo('cash_n_short_term_invest_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash and short term invest estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_fq': FieldInfo('cash_n_short_term_invest_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash and short term invest (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_fy': FieldInfo('cash_n_short_term_invest_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash and short term invest (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_n_short_term_invest_to_total_current_liabilities_fq': FieldInfo('cash_n_short_term_invest_to_total_current_liabilities_fq', FieldType.NUMBER, 'Cash and short term invest to total current liabilities (fiscal quarter).'),
    'cash_n_short_term_invest_to_total_current_liabilities_fy': FieldInfo('cash_n_short_term_invest_to_total_current_liabilities_fy', FieldType.NUMBER, 'Cash and short term invest to total current liabilities (fiscal year).'),
    'cash_n_short_term_invest_to_total_debt_fq': FieldInfo('cash_n_short_term_invest_to_total_debt_fq', FieldType.NUMBER, 'Cash and short term invest to total debt (fiscal quarter).'),
    'cash_n_short_term_invest_to_total_debt_fy': FieldInfo('cash_n_short_term_invest_to_total_debt_fy', FieldType.NUMBER, 'Cash and short term invest to total debt (fiscal year).'),
    'cash_per_share_current': FieldInfo('cash_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Cash per share current [monetary value in fundamental/fund currency].'),
    'cash_per_share_fh': FieldInfo('cash_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Cash per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cash_per_share_fq': FieldInfo('cash_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Cash per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cash_per_share_fy': FieldInfo('cash_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Cash per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'cash_ratio': FieldInfo('cash_ratio', FieldType.NUMBER, 'Cash ratio.'),
    'category': FieldInfo('category', FieldType.TEXT, 'Category.', values=('1', '26', '27', '3', '34', '35', '4', '44', '5', '50', '56', '57', '58', '59', '6', '60', '61', '62', '63', '64', '65', '66', '68', '69', '7', '70', '71', '75', '8')),
    'cfi_code': FieldInfo('cfi_code', FieldType.TEXT, 'CFI code.', values=('CECGES', 'CECGMS', 'CECGMX', 'CECIEU', 'CECJLS', 'CECJLU', 'CECJMU', 'CECJRS', 'CEMGLS', 'CEMILS', 'CEMJLS', 'CEOGBS', 'CEOGBU', 'CEOGCS', 'CEOGDS', 'CEOGES', 'CEOGEU', 'CEOGLS', 'CEOGLX', 'CEOGMS', 'CEOGXX', 'CEOIBS', 'CEOICS', 'CEOICX', 'CEOIDS', 'CEOIES', 'CEOILS', 'CEOILU', 'CEOILX', 'CEOIMS', 'CEOIMU', 'CEOIMX', 'CEOIRS', 'CEOIRX', 'CEOIVS', 'CEOIXS', 'CEOIXX', 'CEOJBS', 'CEOJBU', 'CEOJCS', 'CEOJCU', 'CEOJDS', 'CEOJES', 'CEOJEU', 'CEOJLS', 'CEOJLU', 'CEOJLX', 'CEOJMS', 'CEOJRS', 'CEOJXS', 'CEOXCX', 'CEOXMX', 'CEOXXS', 'CEOXXX', 'CEXGLS', 'CEXIBS', 'CEXICX', 'CEXIMS', 'CEXIMX', 'CEXJLS', 'CEXJMS', 'CEXXMX', 'CEXXXS', 'CICGLS', 'CICGXS', 'CICGXX', 'CICIBS', 'CICIBX', 'CICIES', 'CICILS', 'CICIMS', 'CICIMX', 'CICIRS', 'CICIRX', 'CICIXX', 'CICJBS', 'CICJCS', 'CICJLQ', 'CICJLS', 'CICJLU', 'CICJMS', 'CICJMU', 'CICJXS', 'CICXLS', 'CICXMX', 'CICXXX', 'CIMJLS', 'CIOGLX', 'CIOGXX', 'CIOIES', 'CIOILS', 'CIOIXX', 'CIOJLS', 'CIOJLU', 'CIOJMS', 'CIOJRS', 'CIOXMX', 'CIOXXX', 'CIXXFX', 'CIXXXS', 'CIXXXX', 'EFNCCR', 'EFNNFR', 'EFNRCX', 'EFNXCR', 'EFNXFR', 'EFVCFR', 'EFVRCR', 'EFVRFR', 'EFVXCR', 'EFVXFR', 'EPNAFR', 'EPNCAR', 'EPNCCR', 'EPNCFR', 'EPNCQR', 'EPNNAR', 'EPNNCR', 'EPNNFR', 'EPNRAR', 'EPNRCR', 'EPNRFR', 'EPNTCR', 'EPNTFR', 'EPNXAR', 'EPNXCR', 'EPNXFR', 'EPNXUR', 'EPNXXB', 'EPRNFR', 'EPRRAR', 'EPRRCR', 'EPVCCR', 'EPVCFR', 'EPVCQR', 'EPVGFR', 'EPVNAR', 'EPVNCR', 'EPVNFR', 'EPVRAR', 'EPVRCR', 'EPVRFR', 'EPVTFR', 'EPVXCR', 'EPVXFR', 'EPVXUR', 'EPXNFR', 'EPXXXX', 'ESEUFN', 'ESEUFR', 'ESNUFB', 'ESNUFN', 'ESNUFR', 'ESNUFX', 'ESNUOR', 'ESNUPR', 'ESRTFR', 'ESRUFR', 'ESVTFM', 'ESVTFN', 'ESVTFR', 'ESVTXR', 'ESVUFB', 'ESVUFM', 'ESVUFN', 'ESVUFR', 'ESVUFX', 'ESVUOR', 'ESVUPR', 'ESVUXN', 'ESVUXR', 'ESVUXX', 'ESVXFN', 'ESVXFR', 'ESVXFX', 'ESVXXR', 'ESVXXX', 'ESXTFX', 'ESXUFX', 'ESXUXR', 'ESXXFX', 'ESXXXB', 'ESXXXN', 'ESXXXR', 'ESXXXX')),
    'change': FieldInfo('change', FieldType.PERCENT, 'Price change, percent (e.g. -7.35 means -7.35%).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'change_abs': FieldInfo('change_abs', FieldType.PRICE, 'Price change, absolute (symbol currency).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'change_from_open': FieldInfo('change_from_open', FieldType.PERCENT, 'Percent change from session open.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'change_from_open_abs': FieldInfo('change_from_open_abs', FieldType.PRICE, 'Change from open (absolute).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'close': FieldInfo('close', FieldType.PRICE, 'Last/close price (symbol currency).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'continuous_dividend_growth': FieldInfo('continuous_dividend_growth', FieldType.NUMBER, 'Continuous dividend growth.'),
    'continuous_dividend_payout': FieldInfo('continuous_dividend_payout', FieldType.NUMBER, 'Continuous dividend payout.'),
    'cost_of_goods_estimate_fh': FieldInfo('cost_of_goods_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Cost of goods estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'cost_of_goods_estimate_fq': FieldInfo('cost_of_goods_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Cost of goods estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'cost_of_goods_estimate_fy': FieldInfo('cost_of_goods_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Cost of goods estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'cost_of_goods_estimate_ntm': FieldInfo('cost_of_goods_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Cost of goods estimate ntm [monetary value in fundamental/fund currency].'),
    'country': FieldInfo('country', FieldType.TEXT, 'Country of incorporation / domicile.', values=('Argentina', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Barbados', 'Belgium', 'Bermuda', 'Brazil', 'British Virgin Islands', 'Cambodia', 'Canada', 'Cayman Islands', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Cyprus', 'Denmark', 'Dominican Republic', 'Egypt', 'El Salvador', 'Faroe Islands', 'Finland', 'France', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Liechtenstein', 'Luxembourg', 'Macau', 'Malaysia', 'Malta', 'Mauritius', 'Mexico', 'Monaco', 'Mongolia', 'Netherlands', 'New Zealand', 'Nigeria', 'Norway', 'Panama', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Puerto Rico', 'Romania', 'Singapore', 'South Africa', 'South Korea', 'Spain', 'Sweden', 'Switzerland', 'Taiwan', 'Tanzania', 'Thailand', 'Turkey', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Vietnam')),
    'country_code_fund': FieldInfo('country_code_fund', FieldType.TEXT, 'Country code fund.', values=('AE', 'AR', 'AT', 'AU', 'AZ', 'BB', 'BE', 'BM', 'BR', 'BS', 'CA', 'CH', 'CL', 'CN', 'CO', 'CR', 'CY', 'DE', 'DK', 'DO', 'EG', 'ES', 'FI', 'FO', 'FR', 'GB', 'GH', 'GI', 'GR', 'HK', 'HU', 'ID', 'IE', 'IL', 'IN', 'IS', 'IT', 'JM', 'JO', 'JP', 'KH', 'KR', 'KY', 'KZ', 'LI', 'LU', 'MC', 'MN', 'MO', 'MT', 'MU', 'MX', 'MY', 'NG', 'NL', 'NO', 'NZ', 'PA', 'PE', 'PH', 'PL', 'PR', 'PT', 'RO', 'SE', 'SG', 'SV', 'TH', 'TR', 'TW', 'TZ', 'US', 'UY', 'VG', 'VN', 'ZA')),
    'coupon': FieldInfo('coupon', FieldType.NUMBER, 'Coupon.'),
    'cryptoasset-info.description': FieldInfo('cryptoasset-info.description', FieldType.TEXT, 'Cryptoasset info description.'),
    'cryptoasset-info.id': FieldInfo('cryptoasset-info.id', FieldType.TEXT, 'Cryptoasset info ID.'),
    'currency': FieldInfo('currency', FieldType.TEXT, 'Trading currency.', values=('USD',)),
    'currency_hedged_flag': FieldInfo('currency_hedged_flag', FieldType.TEXT, 'Currency hedged flag.', values=('0', '1')),
    'currency_id': FieldInfo('currency_id', FieldType.TEXT, 'Currency ID.', values=('USD',)),
    'currency_kind': FieldInfo('currency_kind', FieldType.TEXT, 'Currency kind.', values=('fiat',)),
    'current_ratio': FieldInfo('current_ratio', FieldType.NUMBER, 'Current ratio.'),
    'current_ratio_current': FieldInfo('current_ratio_current', FieldType.NUMBER, 'Current ratio current.'),
    'current_ratio_fq': FieldInfo('current_ratio_fq', FieldType.NUMBER, 'Current ratio (current assets / current liabilities), latest fiscal quarter.'),
    'current_ratio_fy': FieldInfo('current_ratio_fy', FieldType.NUMBER, 'Current ratio (fiscal year).'),
    'current_session': FieldInfo('current_session', FieldType.TEXT, 'Current market session phase for the symbol.', values=('out_of_session',)),
    'current_yield': FieldInfo('current_yield', FieldType.PERCENT, 'Current yield [percentage points (12.5 means 12.5%)].'),
    'daily-bar.time': FieldInfo('daily-bar.time', FieldType.NUMBER, 'Daily bar time.'),
    'days_to_maturity': FieldInfo('days_to_maturity', FieldType.NUMBER, 'Days to maturity.'),
    'debt_to_asset_fq': FieldInfo('debt_to_asset_fq', FieldType.NUMBER, 'Debt to asset (fiscal quarter).'),
    'debt_to_asset_fy': FieldInfo('debt_to_asset_fy', FieldType.NUMBER, 'Debt to asset (fiscal year).'),
    'debt_to_assets': FieldInfo('debt_to_assets', FieldType.NUMBER, 'Debt to assets.'),
    'debt_to_equity': FieldInfo('debt_to_equity', FieldType.NUMBER, 'Debt to equity.'),
    'debt_to_equity_fq': FieldInfo('debt_to_equity_fq', FieldType.NUMBER, 'Total debt / equity, latest fiscal quarter.'),
    'debt_to_equity_fy': FieldInfo('debt_to_equity_fy', FieldType.NUMBER, 'Debt to equity (fiscal year).'),
    'debt_to_revenue_fy': FieldInfo('debt_to_revenue_fy', FieldType.NUMBER, 'Debt to revenue (fiscal year).'),
    'debt_to_revenue_ttm': FieldInfo('debt_to_revenue_ttm', FieldType.NUMBER, 'Debt to revenue (trailing twelve months).'),
    'description': FieldInfo('description', FieldType.TEXT, 'Instrument name / company description line.'),
    'diluted_shares_outstanding_fq': FieldInfo('diluted_shares_outstanding_fq', FieldType.FUNDAMENTAL_PRICE, 'Diluted shares outstanding (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'dividend_amount_recent': FieldInfo('dividend_amount_recent', FieldType.FUNDAMENTAL_PRICE, 'Dividend amount recent [monetary value in fundamental/fund currency].'),
    'dividend_amount_upcoming': FieldInfo('dividend_amount_upcoming', FieldType.FUNDAMENTAL_PRICE, 'Dividend amount upcoming [monetary value in fundamental/fund currency].'),
    'dividend_ex_date_recent': FieldInfo('dividend_ex_date_recent', FieldType.TIME, 'Dividend ex date recent [UNIX timestamp (seconds)].'),
    'dividend_ex_date_upcoming': FieldInfo('dividend_ex_date_upcoming', FieldType.TIME, 'Dividend ex date upcoming [UNIX timestamp (seconds)].'),
    'dividend_frequency_recent': FieldInfo('dividend_frequency_recent', FieldType.TEXT, 'Dividend frequency recent.'),
    'dividend_frequency_upcoming': FieldInfo('dividend_frequency_upcoming', FieldType.TEXT, 'Dividend frequency upcoming.'),
    'dividend_payment_date_recent': FieldInfo('dividend_payment_date_recent', FieldType.TIME, 'Dividend payment date recent [UNIX timestamp (seconds)].'),
    'dividend_payment_date_upcoming': FieldInfo('dividend_payment_date_upcoming', FieldType.TIME, 'Dividend payment date upcoming [UNIX timestamp (seconds)].'),
    'dividend_payout_ratio_fy': FieldInfo('dividend_payout_ratio_fy', FieldType.PERCENT, 'Dividend payout ratio (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'dividend_payout_ratio_percent_fq': FieldInfo('dividend_payout_ratio_percent_fq', FieldType.PERCENT, 'Dividend payout ratio percent (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'dividend_payout_ratio_percent_fy': FieldInfo('dividend_payout_ratio_percent_fy', FieldType.PERCENT, 'Dividend payout ratio percent (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'dividend_payout_ratio_ttm': FieldInfo('dividend_payout_ratio_ttm', FieldType.PERCENT, 'Dividend payout ratio (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'dividend_treatment': FieldInfo('dividend_treatment', FieldType.TEXT, 'How dividends are treated (accumulating/distributing).', values=('Capitalizes', 'Distributes')),
    'dividend_yield_recent': FieldInfo('dividend_yield_recent', FieldType.NUMBER, 'Dividend yield recent.'),
    'dividend_yield_upcoming': FieldInfo('dividend_yield_upcoming', FieldType.NUMBER, 'Dividend yield upcoming.'),
    'dividends_frequency': FieldInfo('dividends_frequency', FieldType.TEXT, 'Dividend payment frequency.', values=('Annual', 'Monthly', 'Other', 'Quarterly', 'Semi-annual', 'Weekly')),
    'dividends_paid': FieldInfo('dividends_paid', FieldType.FUNDAMENTAL_PRICE, 'Dividends paid [monetary value in fundamental/fund currency].'),
    'dividends_per_share_fq': FieldInfo('dividends_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'dividends_yield': FieldInfo('dividends_yield', FieldType.NUMBER, 'Dividend yield (trailing), percent.'),
    'dividends_yield_current': FieldInfo('dividends_yield_current', FieldType.PERCENT, 'Dividend yield, percent (e.g. 0.34 = 0.34%).'),
    'dividends_yield_fq': FieldInfo('dividends_yield_fq', FieldType.PERCENT, 'Dividends yield (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'dividends_yield_fy': FieldInfo('dividends_yield_fy', FieldType.PERCENT, 'Dividends yield (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'dps_common_stock_prim_issue_fh': FieldInfo('dps_common_stock_prim_issue_fh', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share common stock prim issue (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'dps_common_stock_prim_issue_fq': FieldInfo('dps_common_stock_prim_issue_fq', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share common stock prim issue (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'dps_common_stock_prim_issue_fy': FieldInfo('dps_common_stock_prim_issue_fy', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share common stock prim issue (fiscal year) [monetary value in fundamental/fund currency].'),
    'dps_common_stock_prim_issue_fy_h': FieldInfo('dps_common_stock_prim_issue_fy_h', FieldType.NUM_SLICE, 'Dividends per share common stock prim issue (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'dps_common_stock_prim_issue_ttm': FieldInfo('dps_common_stock_prim_issue_ttm', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share common stock prim issue (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'dps_common_stock_prim_issue_yoy_growth_fy': FieldInfo('dps_common_stock_prim_issue_yoy_growth_fy', FieldType.PERCENT, 'Dividends per share common stock prim issue year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'dps_estimate_fh': FieldInfo('dps_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'dps_estimate_fq': FieldInfo('dps_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'dps_estimate_fy': FieldInfo('dps_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'dps_estimate_ntm': FieldInfo('dps_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Dividends per share estimate ntm [monetary value in fundamental/fund currency].'),
    'earnings_fq_h': FieldInfo('earnings_fq_h', FieldType.INTERFACE, 'Earnings (fiscal quarter) (historical series).'),
    'earnings_per_share_basic_cagr_5y': FieldInfo('earnings_per_share_basic_cagr_5y', FieldType.PERCENT, 'Earnings per share basic CAGR 5y [percentage points (12.5 means 12.5%)].'),
    'earnings_per_share_basic_fh': FieldInfo('earnings_per_share_basic_fh', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share basic (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_basic_fq': FieldInfo('earnings_per_share_basic_fq', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share basic (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_basic_fy': FieldInfo('earnings_per_share_basic_fy', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share basic (fiscal year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_basic_fy_h': FieldInfo('earnings_per_share_basic_fy_h', FieldType.NUM_SLICE, 'Earnings per share basic (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'earnings_per_share_basic_ttm': FieldInfo('earnings_per_share_basic_ttm', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share basic (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_diluted_5y_growth_fy': FieldInfo('earnings_per_share_diluted_5y_growth_fy', FieldType.PERCENT, 'Earnings per share diluted 5y growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'earnings_per_share_diluted_fh': FieldInfo('earnings_per_share_diluted_fh', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share diluted (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_diluted_fq': FieldInfo('earnings_per_share_diluted_fq', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share diluted (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_diluted_fq_h': FieldInfo('earnings_per_share_diluted_fq_h', FieldType.NUM_SLICE, 'Earnings per share diluted (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'earnings_per_share_diluted_fy': FieldInfo('earnings_per_share_diluted_fy', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share diluted (fiscal year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_diluted_fy_h': FieldInfo('earnings_per_share_diluted_fy_h', FieldType.NUM_SLICE, 'Earnings per share diluted (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'earnings_per_share_diluted_qoq_growth_fq': FieldInfo('earnings_per_share_diluted_qoq_growth_fq', FieldType.PERCENT, 'Earnings per share diluted quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'earnings_per_share_diluted_ttm': FieldInfo('earnings_per_share_diluted_ttm', FieldType.FUNDAMENTAL_PRICE, 'Diluted EPS, trailing twelve months.'),
    'earnings_per_share_diluted_ttm_h': FieldInfo('earnings_per_share_diluted_ttm_h', FieldType.NUM_SLICE, 'Earnings per share diluted (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'earnings_per_share_diluted_yoy_growth_fq': FieldInfo('earnings_per_share_diluted_yoy_growth_fq', FieldType.PERCENT, 'Earnings per share diluted year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'earnings_per_share_diluted_yoy_growth_fy': FieldInfo('earnings_per_share_diluted_yoy_growth_fy', FieldType.PERCENT, 'Earnings per share diluted year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'earnings_per_share_diluted_yoy_growth_ttm': FieldInfo('earnings_per_share_diluted_yoy_growth_ttm', FieldType.PERCENT, 'Diluted EPS growth TTM year-over-year, percent.'),
    'earnings_per_share_fh': FieldInfo('earnings_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_forecast_fq': FieldInfo('earnings_per_share_forecast_fq', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share forecast (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_forecast_next_fh': FieldInfo('earnings_per_share_forecast_next_fh', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share forecast next (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_forecast_next_fq': FieldInfo('earnings_per_share_forecast_next_fq', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share forecast next (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_forecast_next_fy': FieldInfo('earnings_per_share_forecast_next_fy', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share forecast next (fiscal year) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_fq': FieldInfo('earnings_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'earnings_per_share_fy': FieldInfo('earnings_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Earnings per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'earnings_publication_type_fq': FieldInfo('earnings_publication_type_fq', FieldType.NUMBER, 'Earnings publication type (fiscal quarter).'),
    'earnings_publication_type_next_fq': FieldInfo('earnings_publication_type_next_fq', FieldType.NUMBER, 'Earnings publication type next (fiscal quarter).'),
    'earnings_release_calendar_date': FieldInfo('earnings_release_calendar_date', FieldType.TIME, 'Earnings release calendar date [UNIX timestamp (seconds)].'),
    'earnings_release_date': FieldInfo('earnings_release_date', FieldType.TIME, 'Last earnings report date (UNIX timestamp).'),
    'earnings_release_next_calendar_date': FieldInfo('earnings_release_next_calendar_date', FieldType.TIME, 'Earnings release next calendar date [UNIX timestamp (seconds)].'),
    'earnings_release_next_date': FieldInfo('earnings_release_next_date', FieldType.TIME, 'Next scheduled earnings report date (UNIX timestamp).'),
    'earnings_release_next_time': FieldInfo('earnings_release_next_time', FieldType.NUMBER, 'Earnings release next time.'),
    'earnings_release_next_trading_date_fq': FieldInfo('earnings_release_next_trading_date_fq', FieldType.TIME, 'Earnings release next trading date (fiscal quarter) [UNIX timestamp (seconds)].'),
    'earnings_release_next_trading_date_fy': FieldInfo('earnings_release_next_trading_date_fy', FieldType.TIME, 'Earnings release next trading date (fiscal year) [UNIX timestamp (seconds)].'),
    'earnings_release_time': FieldInfo('earnings_release_time', FieldType.NUMBER, 'Earnings release time.'),
    'earnings_release_trading_date_fq': FieldInfo('earnings_release_trading_date_fq', FieldType.TIME, 'Earnings release trading date (fiscal quarter) [UNIX timestamp (seconds)].'),
    'earnings_release_trading_date_fy': FieldInfo('earnings_release_trading_date_fy', FieldType.TIME, 'Earnings release trading date (fiscal year) [UNIX timestamp (seconds)].'),
    'earnings_yield': FieldInfo('earnings_yield', FieldType.PERCENT, 'Earnings yield [percentage points (12.5 means 12.5%)].'),
    'ebit_estimate_fh': FieldInfo('ebit_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'EBIT estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ebit_estimate_fq': FieldInfo('ebit_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'EBIT estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ebit_estimate_fy': FieldInfo('ebit_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'EBIT estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebit_estimate_ntm': FieldInfo('ebit_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'EBIT estimate ntm [monetary value in fundamental/fund currency].'),
    'ebit_per_share_current': FieldInfo('ebit_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'EBIT per share current [monetary value in fundamental/fund currency].'),
    'ebit_per_share_fh': FieldInfo('ebit_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'EBIT per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ebit_per_share_fq': FieldInfo('ebit_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'EBIT per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ebit_per_share_fy': FieldInfo('ebit_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'EBIT per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebit_per_share_ttm': FieldInfo('ebit_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'EBIT per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'ebit_ttm': FieldInfo('ebit_ttm', FieldType.FUNDAMENTAL_PRICE, 'EBIT (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'ebitda': FieldInfo('ebitda', FieldType.FUNDAMENTAL_PRICE, 'EBITDA [monetary value in fundamental/fund currency].'),
    'ebitda_estimate_fh': FieldInfo('ebitda_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'EBITDA estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ebitda_estimate_fq': FieldInfo('ebitda_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'EBITDA estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ebitda_estimate_fy': FieldInfo('ebitda_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'EBITDA estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebitda_estimate_ntm': FieldInfo('ebitda_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'EBITDA estimate ntm [monetary value in fundamental/fund currency].'),
    'ebitda_fh': FieldInfo('ebitda_fh', FieldType.FUNDAMENTAL_PRICE, 'EBITDA (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ebitda_fq': FieldInfo('ebitda_fq', FieldType.FUNDAMENTAL_PRICE, 'EBITDA (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ebitda_fq_h': FieldInfo('ebitda_fq_h', FieldType.NUM_SLICE, 'EBITDA (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'ebitda_fy': FieldInfo('ebitda_fy', FieldType.FUNDAMENTAL_PRICE, 'EBITDA (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebitda_fy_h': FieldInfo('ebitda_fy_h', FieldType.NUM_SLICE, 'EBITDA (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'ebitda_interst_cover_fy': FieldInfo('ebitda_interst_cover_fy', FieldType.NUMBER, 'EBITDA interst cover (fiscal year).'),
    'ebitda_interst_cover_ttm': FieldInfo('ebitda_interst_cover_ttm', FieldType.NUMBER, 'EBITDA interst cover (trailing twelve months).'),
    'ebitda_less_capex_interst_cover_fy': FieldInfo('ebitda_less_capex_interst_cover_fy', FieldType.NUMBER, 'EBITDA less capex interst cover (fiscal year).'),
    'ebitda_less_capex_interst_cover_ttm': FieldInfo('ebitda_less_capex_interst_cover_ttm', FieldType.NUMBER, 'EBITDA less capex interst cover (trailing twelve months).'),
    'ebitda_margin_fy': FieldInfo('ebitda_margin_fy', FieldType.PERCENT, 'EBITDA margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'ebitda_margin_ttm': FieldInfo('ebitda_margin_ttm', FieldType.PERCENT, 'EBITDA margin (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'ebitda_per_employee_fy': FieldInfo('ebitda_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebitda_per_share_current': FieldInfo('ebitda_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per share current [monetary value in fundamental/fund currency].'),
    'ebitda_per_share_fh': FieldInfo('ebitda_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ebitda_per_share_fq': FieldInfo('ebitda_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ebitda_per_share_fy': FieldInfo('ebitda_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'ebitda_per_share_ttm': FieldInfo('ebitda_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'EBITDA per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'ebitda_qoq_growth_fq': FieldInfo('ebitda_qoq_growth_fq', FieldType.PERCENT, 'EBITDA quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'ebitda_ttm': FieldInfo('ebitda_ttm', FieldType.FUNDAMENTAL_PRICE, 'EBITDA (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'ebitda_ttm_h': FieldInfo('ebitda_ttm_h', FieldType.NUM_SLICE, 'EBITDA (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'ebitda_yoy_growth_fq': FieldInfo('ebitda_yoy_growth_fq', FieldType.PERCENT, 'EBITDA year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'ebitda_yoy_growth_fy': FieldInfo('ebitda_yoy_growth_fy', FieldType.PERCENT, 'EBITDA year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'ebitda_yoy_growth_ttm': FieldInfo('ebitda_yoy_growth_ttm', FieldType.PERCENT, 'EBITDA year-over-year growth (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'effective_interest_rate_on_debt_fy': FieldInfo('effective_interest_rate_on_debt_fy', FieldType.PERCENT, 'Effective interest rate on debt (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'effective_interest_rate_on_debt_ttm': FieldInfo('effective_interest_rate_on_debt_ttm', FieldType.PERCENT, 'Effective interest rate on debt (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'enterprise_value_current': FieldInfo('enterprise_value_current', FieldType.FUNDAMENTAL_PRICE, 'Enterprise value, current.'),
    'enterprise_value_ebit_fwd': FieldInfo('enterprise_value_ebit_fwd', FieldType.NUMBER, 'Enterprise value EBIT fwd.'),
    'enterprise_value_ebitda_current': FieldInfo('enterprise_value_ebitda_current', FieldType.NUMBER, 'Enterprise value EBITDA current.'),
    'enterprise_value_ebitda_fwd': FieldInfo('enterprise_value_ebitda_fwd', FieldType.NUMBER, 'Enterprise value EBITDA fwd.'),
    'enterprise_value_ebitda_ttm': FieldInfo('enterprise_value_ebitda_ttm', FieldType.NUMBER, 'EV / EBITDA, TTM.'),
    'enterprise_value_fq': FieldInfo('enterprise_value_fq', FieldType.FUNDAMENTAL_PRICE, 'Enterprise value (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'enterprise_value_sales_fwd': FieldInfo('enterprise_value_sales_fwd', FieldType.NUMBER, 'Enterprise value sales fwd.'),
    'enterprise_value_to_ebit_ttm': FieldInfo('enterprise_value_to_ebit_ttm', FieldType.NUMBER, 'Enterprise value to EBIT (trailing twelve months).'),
    'enterprise_value_to_free_cash_flow_ttm': FieldInfo('enterprise_value_to_free_cash_flow_ttm', FieldType.NUMBER, 'Enterprise value to free cash flow (trailing twelve months).'),
    'enterprise_value_to_gross_profit_ttm': FieldInfo('enterprise_value_to_gross_profit_ttm', FieldType.NUMBER, 'Enterprise value to gross profit (trailing twelve months).'),
    'enterprise_value_to_revenue_ttm': FieldInfo('enterprise_value_to_revenue_ttm', FieldType.NUMBER, 'Enterprise value to revenue (trailing twelve months).'),
    'eps_diluted_growth_percent_fq': FieldInfo('eps_diluted_growth_percent_fq', FieldType.PERCENT, 'EPS diluted growth percent (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'eps_diluted_growth_percent_fy': FieldInfo('eps_diluted_growth_percent_fy', FieldType.PERCENT, 'EPS diluted growth percent (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'eps_estimate_ntm': FieldInfo('eps_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'EPS estimate ntm [monetary value in fundamental/fund currency].'),
    'eps_surprise_fq': FieldInfo('eps_surprise_fq', FieldType.FUNDAMENTAL_PRICE, 'EPS surprise (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'eps_surprise_percent_fq': FieldInfo('eps_surprise_percent_fq', FieldType.PERCENT, 'EPS surprise percent (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'etf_fund_currency': FieldInfo('etf_fund_currency', FieldType.TEXT, 'ETF fund currency.', values=('CAD', 'CHF', 'EUR', 'GBP', 'JPY', 'USD')),
    'etf_holdings_count': FieldInfo('etf_holdings_count', FieldType.NUMBER, 'Number of holdings in the fund.'),
    'ex_dividend_date_recent': FieldInfo('ex_dividend_date_recent', FieldType.TIME, 'Ex dividend date recent [UNIX timestamp (seconds)].'),
    'ex_dividend_date_upcoming': FieldInfo('ex_dividend_date_upcoming', FieldType.TIME, 'Ex dividend date upcoming [UNIX timestamp (seconds)].'),
    'exchange': FieldInfo('exchange', FieldType.TEXT, 'Listing exchange.', values=('AMEX', 'CBOE', 'NASDAQ', 'NYSE', 'OTC')),
    'expected_annual_dividends': FieldInfo('expected_annual_dividends', FieldType.NUMBER, 'Expected annual dividends.'),
    'expense_ratio': FieldInfo('expense_ratio', FieldType.NUMBER, 'Fund expense ratio, percent (e.g. 0.03 = 0.03%).'),
    'expiration': FieldInfo('expiration', FieldType.TIME, 'Expiration [UNIX timestamp (seconds)].'),
    'first_bar_time': FieldInfo('first_bar_time', FieldType.TIME, 'First bar time [UNIX timestamp (seconds)].'),
    'fiscal_period_current': FieldInfo('fiscal_period_current', FieldType.TEXT, 'Fiscal period current.', values=('2025-H1', '2025-H2', '2025-Q2', '2025-Q3', '2025-Q4', '2026-H1', '2026-H2', '2026-Q1', '2026-Q2', '2026-Q3', '2026-Q4')),
    'fiscal_period_end_current': FieldInfo('fiscal_period_end_current', FieldType.TIME, 'Fiscal period end current [UNIX timestamp (seconds)].'),
    'fiscal_period_end_fh': FieldInfo('fiscal_period_end_fh', FieldType.TIME, 'Fiscal period end (fiscal half-year) [UNIX timestamp (seconds)].'),
    'fiscal_period_end_fh_h': FieldInfo('fiscal_period_end_fh_h', FieldType.NUM_SLICE, 'Fiscal period end (fiscal half-year) (historical series) [array of numbers (per-period history)].'),
    'fiscal_period_end_fq': FieldInfo('fiscal_period_end_fq', FieldType.TIME, 'Fiscal period end (fiscal quarter) [UNIX timestamp (seconds)].'),
    'fiscal_period_end_fy': FieldInfo('fiscal_period_end_fy', FieldType.TIME, 'Fiscal period end (fiscal year) [UNIX timestamp (seconds)].'),
    'fiscal_period_fy': FieldInfo('fiscal_period_fy', FieldType.TEXT, 'Fiscal period (fiscal year).', values=('2024', '2025', '2026')),
    'fiscal_period_fy_h': FieldInfo('fiscal_period_fy_h', FieldType.NUM_SLICE, 'Fiscal period (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'fixed_assets_turnover_fq': FieldInfo('fixed_assets_turnover_fq', FieldType.NUMBER, 'Fixed assets turnover (fiscal quarter).'),
    'fixed_assets_turnover_fy': FieldInfo('fixed_assets_turnover_fy', FieldType.NUMBER, 'Fixed assets turnover (fiscal year).'),
    'float_shares_outstanding': FieldInfo('float_shares_outstanding', FieldType.NUMBER, 'Float shares outstanding.'),
    'float_shares_outstanding_current': FieldInfo('float_shares_outstanding_current', FieldType.NUMBER, 'Public float (shares), current.'),
    'float_shares_percent_current': FieldInfo('float_shares_percent_current', FieldType.PERCENT, 'Float shares percent current [percentage points (12.5 means 12.5%)].'),
    'focus': FieldInfo('focus', FieldType.TEXT, "Fund investment focus (internal id; use 'focus.tr' column for the readable label, e.g. Large cap).", values=('1', '10', '105', '106', '115', '123', '13', '18', '20', '2004', '2011', '2025', '2029', '2034', '2040', '2043', '2055', '2056', '2059', '2069', '2071', '2075', '2091', '2092', '2094', '2096', '2103', '2107', '2108', '2111', '2113', '2114', '2116', '2119', '2120', '2121', '2122', '2123', '2125', '2127', '2128', '2129', '2135', '2149', '2153', '2154', '2180', '2181', '2183', '2186', '2195', '2203', '2204', '2213', '23', '2430', '25', '29', '30', '31', '32', '52', '53', '54', '55', '56', '58', '59', '6', '61', '62', '63', '64', '66', '68', '70', '73', '78', '87', '9', '90', '91', '94')),
    'fractional': FieldInfo('fractional', FieldType.TEXT, 'Fractional.', values=('false',)),
    'free_cash_flow': FieldInfo('free_cash_flow', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow [monetary value in fundamental/fund currency].'),
    'free_cash_flow_cagr_5y': FieldInfo('free_cash_flow_cagr_5y', FieldType.PERCENT, 'Free cash flow CAGR 5y [percentage points (12.5 means 12.5%)].'),
    'free_cash_flow_estimate_fh': FieldInfo('free_cash_flow_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_estimate_fq': FieldInfo('free_cash_flow_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_estimate_fy': FieldInfo('free_cash_flow_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_estimate_ntm': FieldInfo('free_cash_flow_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow estimate ntm [monetary value in fundamental/fund currency].'),
    'free_cash_flow_fh': FieldInfo('free_cash_flow_fh', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_fq': FieldInfo('free_cash_flow_fq', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_fq_h': FieldInfo('free_cash_flow_fq_h', FieldType.NUM_SLICE, 'Free cash flow (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'free_cash_flow_fy': FieldInfo('free_cash_flow_fy', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow (fiscal year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_fy_h': FieldInfo('free_cash_flow_fy_h', FieldType.NUM_SLICE, 'Free cash flow (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'free_cash_flow_margin_fy': FieldInfo('free_cash_flow_margin_fy', FieldType.PERCENT, 'Free cash flow margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'free_cash_flow_margin_ttm': FieldInfo('free_cash_flow_margin_ttm', FieldType.PERCENT, 'Free cash flow margin, percent, TTM.'),
    'free_cash_flow_per_employee_fy': FieldInfo('free_cash_flow_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_per_share_current': FieldInfo('free_cash_flow_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per share current [monetary value in fundamental/fund currency].'),
    'free_cash_flow_per_share_fh': FieldInfo('free_cash_flow_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_per_share_fq': FieldInfo('free_cash_flow_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_per_share_fy': FieldInfo('free_cash_flow_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_per_share_ttm': FieldInfo('free_cash_flow_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_qoq_growth_fq': FieldInfo('free_cash_flow_qoq_growth_fq', FieldType.PERCENT, 'Free cash flow quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'free_cash_flow_ttm': FieldInfo('free_cash_flow_ttm', FieldType.FUNDAMENTAL_PRICE, 'Free cash flow (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'free_cash_flow_ttm_h': FieldInfo('free_cash_flow_ttm_h', FieldType.NUM_SLICE, 'Free cash flow (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'free_cash_flow_yoy_growth_fq': FieldInfo('free_cash_flow_yoy_growth_fq', FieldType.PERCENT, 'Free cash flow year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'free_cash_flow_yoy_growth_fy': FieldInfo('free_cash_flow_yoy_growth_fy', FieldType.PERCENT, 'Free cash flow year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'free_cash_flow_yoy_growth_ttm': FieldInfo('free_cash_flow_yoy_growth_ttm', FieldType.PERCENT, 'Free cash flow year-over-year growth (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'frequency_recent': FieldInfo('frequency_recent', FieldType.TEXT, 'Frequency recent.'),
    'frequency_upcoming': FieldInfo('frequency_upcoming', FieldType.TEXT, 'Frequency upcoming.'),
    'fund_flows.1M': FieldInfo('fund_flows.1M', FieldType.FUNDAMENTAL_PRICE, 'Net fund flows over 1 month (fund currency).'),
    'fund_flows.1Y': FieldInfo('fund_flows.1Y', FieldType.FUNDAMENTAL_PRICE, 'Net fund flows over 1 year.'),
    'fund_flows.3M': FieldInfo('fund_flows.3M', FieldType.FUNDAMENTAL_PRICE, 'Net fund flows over 3 months.'),
    'fund_flows.3Y': FieldInfo('fund_flows.3Y', FieldType.FUNDAMENTAL_PRICE, 'Fund flows 3Y [monetary value in fundamental/fund currency].'),
    'fund_flows.5Y': FieldInfo('fund_flows.5Y', FieldType.FUNDAMENTAL_PRICE, 'Fund flows 5Y [monetary value in fundamental/fund currency].'),
    'fund_flows.YTD': FieldInfo('fund_flows.YTD', FieldType.FUNDAMENTAL_PRICE, 'Fund flows year-to-date [monetary value in fundamental/fund currency].'),
    'fundamental_currency_code': FieldInfo('fundamental_currency_code', FieldType.TEXT, 'Currency used for fundamental (financial statement) values.', values=('USD',)),
    'gap': FieldInfo('gap', FieldType.PERCENT, 'Opening gap, percent.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'gap_down': FieldInfo('gap_down', FieldType.PERCENT, 'Gap down [percentage points (12.5 means 12.5%)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'gap_down_abs': FieldInfo('gap_down_abs', FieldType.PRICE, 'Gap down (absolute).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'gap_up': FieldInfo('gap_up', FieldType.PERCENT, 'Gap up [percentage points (12.5 means 12.5%)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'gap_up_abs': FieldInfo('gap_up_abs', FieldType.PRICE, 'Gap up (absolute).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'goodwill': FieldInfo('goodwill', FieldType.FUNDAMENTAL_PRICE, 'Goodwill [monetary value in fundamental/fund currency].'),
    'goodwill_fq': FieldInfo('goodwill_fq', FieldType.FUNDAMENTAL_PRICE, 'Goodwill (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'goodwill_fy': FieldInfo('goodwill_fy', FieldType.FUNDAMENTAL_PRICE, 'Goodwill (fiscal year) [monetary value in fundamental/fund currency].'),
    'graham_numbers_fy': FieldInfo('graham_numbers_fy', FieldType.NUMBER, 'Graham numbers (fiscal year).'),
    'graham_numbers_ttm': FieldInfo('graham_numbers_ttm', FieldType.NUMBER, 'Graham numbers (trailing twelve months).'),
    'gross_margin': FieldInfo('gross_margin', FieldType.PERCENT, 'Gross margin [percentage points (12.5 means 12.5%)].'),
    'gross_margin_fy': FieldInfo('gross_margin_fy', FieldType.PERCENT, 'Gross margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'gross_margin_percent_ttm': FieldInfo('gross_margin_percent_ttm', FieldType.PERCENT, 'Gross margin percent (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'gross_margin_ttm': FieldInfo('gross_margin_ttm', FieldType.PERCENT, 'Gross margin, percent, TTM.'),
    'gross_profit': FieldInfo('gross_profit', FieldType.FUNDAMENTAL_PRICE, 'Gross profit [monetary value in fundamental/fund currency].'),
    'gross_profit_estimate_fh': FieldInfo('gross_profit_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Gross profit estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'gross_profit_estimate_fq': FieldInfo('gross_profit_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Gross profit estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'gross_profit_estimate_fy': FieldInfo('gross_profit_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Gross profit estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'gross_profit_estimate_ntm': FieldInfo('gross_profit_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Gross profit estimate ntm [monetary value in fundamental/fund currency].'),
    'gross_profit_fh': FieldInfo('gross_profit_fh', FieldType.FUNDAMENTAL_PRICE, 'Gross profit (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'gross_profit_fq': FieldInfo('gross_profit_fq', FieldType.FUNDAMENTAL_PRICE, 'Gross profit (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'gross_profit_fq_h': FieldInfo('gross_profit_fq_h', FieldType.NUM_SLICE, 'Gross profit (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'gross_profit_fy': FieldInfo('gross_profit_fy', FieldType.FUNDAMENTAL_PRICE, 'Gross profit (fiscal year) [monetary value in fundamental/fund currency].'),
    'gross_profit_fy_h': FieldInfo('gross_profit_fy_h', FieldType.NUM_SLICE, 'Gross profit (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'gross_profit_margin_fy': FieldInfo('gross_profit_margin_fy', FieldType.PERCENT, 'Gross profit margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'gross_profit_qoq_growth_fq': FieldInfo('gross_profit_qoq_growth_fq', FieldType.PERCENT, 'Gross profit quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'gross_profit_ttm': FieldInfo('gross_profit_ttm', FieldType.FUNDAMENTAL_PRICE, 'Gross profit (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'gross_profit_ttm_h': FieldInfo('gross_profit_ttm_h', FieldType.NUM_SLICE, 'Gross profit (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'gross_profit_yoy_growth_fq': FieldInfo('gross_profit_yoy_growth_fq', FieldType.PERCENT, 'Gross profit year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'gross_profit_yoy_growth_fy': FieldInfo('gross_profit_yoy_growth_fy', FieldType.PERCENT, 'Gross profit year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'gross_profit_yoy_growth_ttm': FieldInfo('gross_profit_yoy_growth_ttm', FieldType.PERCENT, 'Gross profit year-over-year growth (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'has_ipo_data': FieldInfo('has_ipo_data', FieldType.BOOL, 'Has IPO data.'),
    'has_ipo_details_visible': FieldInfo('has_ipo_details_visible', FieldType.BOOL, 'Has IPO details visible.'),
    'high': FieldInfo('high', FieldType.PRICE, 'Session high price.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'holdings_region': FieldInfo('holdings_region', FieldType.TEXT, 'Holdings region.', values=('176a9161fef684328415321c640ada1a', '2402e241d9f16aa08de32421e0fa211f', '3e8961795f30b441beb6aa81b2478c76', '460491fc520f4dbfcff22d1a45f6b056', '55a6587f79a2d84489e92e46d0a83f09', '7612e84033b6f5f1a8b8039d9e25d9b5', '96685265014af86dfee96774c03f6bab', '9c70933aff6b2a6d08c687a6cbb6b765', 'a48e5d3946d87117fc67cd7de5f2c02a', 'cb2afe0cf8f6511856c8a73ea8de821e')),
    'holds_derivatives_flag': FieldInfo('holds_derivatives_flag', FieldType.TEXT, 'Holds derivatives flag.', values=('0', '1')),
    'income_from_cont_ops_fh': FieldInfo('income_from_cont_ops_fh', FieldType.FUNDAMENTAL_PRICE, 'Income from continuous ops (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'income_from_cont_ops_fq': FieldInfo('income_from_cont_ops_fq', FieldType.FUNDAMENTAL_PRICE, 'Income from continuous ops (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'income_from_cont_ops_fy': FieldInfo('income_from_cont_ops_fy', FieldType.FUNDAMENTAL_PRICE, 'Income from continuous ops (fiscal year) [monetary value in fundamental/fund currency].'),
    'income_from_cont_ops_ttm': FieldInfo('income_from_cont_ops_ttm', FieldType.FUNDAMENTAL_PRICE, 'Income from continuous ops (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'index': FieldInfo('index', FieldType.TEXT, 'Index.', values=("{'id': 'CBOE:SPESG', 'name': 'S&P 500 ESG'}", "{'id': 'CBOEFTSE:MRUT', 'name': 'Mini-Russell 2000'}", "{'id': 'DJ:DJA', 'name': 'Dow Jones Composite Average'}", "{'id': 'DJ:DJI', 'name': 'Dow Jones Industrial Average'}", "{'id': 'DJ:DJT', 'name': 'Dow Jones Transportation Average'}", "{'id': 'DJ:DJU', 'name': 'Dow Jones Utility Average'}", "{'id': 'NASDAQ:BANK', 'name': 'NASDAQ Bank'}", "{'id': 'NASDAQ:BKX', 'name': 'KBW NASDAQ Bank'}", "{'id': 'NASDAQ:CELS', 'name': 'NASDAQ Clean Edge Green Energy'}", "{'id': 'NASDAQ:CPQ', 'name': 'ISE CTA Cloud Computing'}", "{'id': 'NASDAQ:HGX', 'name': 'PHLX Housing Sector'}", "{'id': 'NASDAQ:HXC', 'name': 'NASDAQ Golden Dragon China'}", "{'id': 'NASDAQ:INDS', 'name': 'NASDAQ Industrials'}", "{'id': 'NASDAQ:INSR', 'name': 'NASDAQ Insurance'}", "{'id': 'NASDAQ:IXCO', 'name': 'NASDAQ Computer'}", "{'id': 'NASDAQ:IXIC', 'name': 'NASDAQ Composite'}", "{'id': 'NASDAQ:IXTC', 'name': 'NASDAQ Telecommunications'}", "{'id': 'NASDAQ:KFTX', 'name': 'KBW NASDAQ Financial Technology'}", "{'id': 'NASDAQ:NBI', 'name': 'NASDAQ Biotechnology'}", "{'id': 'NASDAQ:NCX', 'name': 'Nasdaq Innovators Completion Cap'}", "{'id': 'NASDAQ:NDX', 'name': 'NASDAQ 100'}", "{'id': 'NASDAQ:NDXT', 'name': 'NASDAQ-100 Technology Sector'}", "{'id': 'NASDAQ:NQUSB451020', 'name': 'NASDAQ US Benchmark Food Producers'}", "{'id': 'NASDAQ:NQUSLG', 'name': 'Nasdaq US Large Cap Growth'}", "{'id': 'NASDAQ:NQUSMG', 'name': 'Nasdaq US Mid Cap Growth'}", "{'id': 'NASDAQ:NQUSSG', 'name': 'Nasdaq US Small Cap Growth'}", "{'id': 'NASDAQ:NYMETA', 'name': 'NASDAQ CB Insights Metaverse US'}", "{'id': 'NASDAQ:OFIN', 'name': 'NASDAQ Real Estate and Other Financial Services'}", "{'id': 'NASDAQ:OSX', 'name': 'PHLX Oil Service Sector'}", "{'id': 'NASDAQ:SOX', 'name': 'PHLX Semiconductor Sector'}", "{'id': 'NASDAQ:TRAN', 'name': 'NASDAQ Transportation'}", "{'id': 'NASDAQ:UTY', 'name': 'PHLX Utilities Sector'}", "{'id': 'NASDAQ:XAU', 'name': 'PHLX Gold/Silver Sector'}", "{'id': 'SP:SPX', 'name': 'S&P 500'}", "{'id': 'STOXX:EDD15P', 'name': 'STOXX Developed Markets 150'}", "{'id': 'STOXX:EDD24BP', 'name': 'STOXX Developed Markets 2400'}", "{'id': 'STOXX:EDE15BP', 'name': 'STOXX Emerging Markets 1500'}", "{'id': 'STOXX:SX150P', 'name': 'STOXX Global 150'}", "{'id': 'STOXX:SX50UL', 'name': 'STOXX USA 500'}", "{'id': 'STOXX:SX50UP', 'name': 'STOXX USA 500'}", "{'id': 'STOXX:SX5AP', 'name': 'STOXX North America 50'}", "{'id': 'STOXX:SXA1E', 'name': 'STOXX North America 600'}", "{'id': 'STOXX:SXAMBCP', 'name': 'STOXX Americas 100'}", "{'id': 'STOXX:SXGBCP', 'name': 'STOXX Global 200'}", "{'id': 'STOXX:SXW1E', 'name': 'STOXX Global 1800'}", "{'id': 'STOXX:SXW8E', 'name': 'STOXX Global 1800 ex Europe'}", "{'id': 'STOXX:SXW9E', 'name': 'STOXX Global 1800 ex Asia/Pacific'}", "{'id': 'TVC:RUA', 'name': 'Russell 3000'}", "{'id': 'TVC:RUI', 'name': 'Russell 1000'}", "{'id': 'TVC:RUT', 'name': 'Russell 2000'}")),
    'index_id': FieldInfo('index_id', FieldType.TEXT, 'Index ID.', values=('SYML:CBOE;SPESG', 'SYML:CBOEFTSE;MRUT', 'SYML:DJ;DJA', 'SYML:DJ;DJI', 'SYML:DJ;DJT', 'SYML:DJ;DJU', 'SYML:NASDAQ;BANK', 'SYML:NASDAQ;BKX', 'SYML:NASDAQ;CELS', 'SYML:NASDAQ;CPQ', 'SYML:NASDAQ;HGX', 'SYML:NASDAQ;HXC', 'SYML:NASDAQ;INDS', 'SYML:NASDAQ;INSR', 'SYML:NASDAQ;IXCO', 'SYML:NASDAQ;IXIC', 'SYML:NASDAQ;IXTC', 'SYML:NASDAQ;KFTX', 'SYML:NASDAQ;NBI', 'SYML:NASDAQ;NCX', 'SYML:NASDAQ;NDX', 'SYML:NASDAQ;NDXT', 'SYML:NASDAQ;NQUSB451020', 'SYML:NASDAQ;NQUSLG', 'SYML:NASDAQ;NQUSMG', 'SYML:NASDAQ;NQUSSG', 'SYML:NASDAQ;NYMETA', 'SYML:NASDAQ;OFIN', 'SYML:NASDAQ;OSX', 'SYML:NASDAQ;SOX', 'SYML:NASDAQ;TRAN', 'SYML:NASDAQ;UTY', 'SYML:NASDAQ;XAU', 'SYML:SP;SPX', 'SYML:STOXX;EDD15P', 'SYML:STOXX;EDD24BP', 'SYML:STOXX;EDE15BP', 'SYML:STOXX;SX150P', 'SYML:STOXX;SX50UL', 'SYML:STOXX;SX50UP', 'SYML:STOXX;SX5AP', 'SYML:STOXX;SXA1E', 'SYML:STOXX;SXAMBCP', 'SYML:STOXX;SXGBCP', 'SYML:STOXX;SXW1E', 'SYML:STOXX;SXW8E', 'SYML:STOXX;SXW9E', 'SYML:TVC;RUA', 'SYML:TVC;RUI', 'SYML:TVC;RUT')),
    'index_priority': FieldInfo('index_priority', FieldType.NUMBER, 'Index priority.'),
    'index_provider': FieldInfo('index_provider', FieldType.TEXT, 'Provider of the tracked index.', values=('ARK Investment Management LP', 'Abacus FCF Advisors LLC', 'Acquirers Funds LLC', 'Akros S.R.L.', 'American Century Investment Management, Inc.', 'Auspice Capital Advisors Ltd.', 'Aztlan Equity Management LLC (Mexico)', 'BITA GmbH', 'BUZZ Indexes', 'Barclays Capital, Inc.', 'Bianco Research Advisors LLC', 'Big Tree Capital LLC', 'Bitwise Asset Management, Inc.', 'Bitwise Index Services LLC', 'BlackRock Index Services LLC', 'Bloomberg Finance LP', 'Bloomberg Index Services Ltd.', 'BlueStar Global Investors LLC', 'Breakwave Advisors LLC', 'CF Benchmarks Ltd.', 'CIBC World Markets, Inc.', 'CME Group, Inc.', 'CSat Investment Advisory LP', 'Calvert Research & Management', 'Carroll Financial Associates, Inc.', 'Cboe Exchange, Inc. (Illinois)', 'Center for Research in Security Prices LLC', 'Change Finance PBC', 'Charles Schwab Investment Management, Inc.', 'China Securities Index Co., Ltd.', 'CoinDesk Indices, Inc.', 'Colterpoint, LLC', 'Columbia Management Investment Advisers LLC', 'DBX ETF Trust', 'Deutsche Börse AG', 'Dimensional Fund Advisors', 'EMQQ Global LLC', 'Eisfeldt Consulting LLC', 'Equbot, Inc.', 'Etho Capital LLC', 'FTSE Fixed Income LLC', 'FTSE Group', 'FTSE International Ltd.', 'FactSet Research Systems, Inc.', 'Fidelity Management & Research Co. LLC', 'Frank Russell Co.', 'Franklin Advisers, Inc.', 'Fuzzy Logix LLC', 'Gapstow Capital Partners LP', 'Global X Management Co. LLC', 'Goldman Sachs International', 'Hang Seng Indexes Co., Ltd.', 'Harbor Capital Advisors, Inc.', 'Hedgeye Risk Management LLC', 'Howard Capital Management Group LLC', 'Hoya Capital Real Estate LLC', 'ICE Data Indices LLC', 'IPOX Schuster LLC', 'Index Design Group LLC', 'India Index Services & Products Ltd.', 'Indxx LLC', 'Inspire Investing LLC', 'Invesco Indexing LLC', "Investor's Business Daily, Inc.", 'JUST Capital Foundation, Inc.', 'Kelly Indexes LLC', 'LPX AG', 'Lattice Strategies LLC', 'Level ETF Ventures LLC', 'Life + Liberty Indexes', 'LifeSci Index Partners LLC', 'Lukka, Inc.', 'Lunt Capital Management, Inc.', 'MSCI, Inc.', 'Market Vectors Exchange Traded Notes', 'MarketGrader Capital LLC', 'MarketVector Indexes GmbH', 'MerQube, Inc.', 'Merrill Lynch International', 'Metaurus Advisors LLC', 'Mirae Asset Global Index Pvt Ltd.', 'Morningstar, Inc.', 'Mount Lucas Management LP', 'NASDAQ', 'Nasdaq ISE LLC', 'Ned Davis Research, Inc.', 'New York Life Investment Management LLC', 'Newfound Research LLC', 'Nikkei, Inc.', 'Numeric Investors LLC', "O'Shares Investment Advisers LLC (US)", 'Oak City Consulting LLC', 'Optimize Financial, Inc.', 'Palmer Square Capital Management LLC', 'ProShare Advisors LLC', 'Quant Insight Ltd.', 'Quantix Commodities LP', 'Red Rocks Capital LLC', 'Redwood Investment Management LLC (California)', 'Refinitiv Benchmark Services (UK) Ltd.', 'Rennaissance Capital Mgt Invt', 'Research Affiliates LLC', 'Richard Bernstein Advisors LLC', 'Rocky Mountain Financial Advisors LLC', 'Roundhill Financial, Inc.', 'S&P Dow Jones Indices LLC', 'S&P OpCo LLC', 'SL Advisors LLC', 'SPADE DEFENSE INDEX', 'STOXX AG', 'Shenzhen Securities Information Co., Ltd.', 'Solactive AG', 'State Street Investment Management', 'SummerHaven Investment Management LLC', 'Syntax Advisors LLC', 'Teucrium Trading LLC', 'The London Bullion Market Association', 'The London Metal Exchange', 'The Motley Fool, LLC', 'The Northern Trust Co.', 'Thor Analytics LLC', 'Tortoise Index Solutions LLC', 'U.S. Global Investors, Inc.', 'UBS Americas, Inc.', 'Value Line Funds Investment Trust', 'VettaFi LLC', 'Vident Financial LLC', 'Water Island Capital LLC', 'WilderShares LLC', 'WisdomTree Asset Management, Inc.', 'Zacks Investment Management, Inc.')),
    'indexes': FieldInfo('indexes', FieldType.INTERFACE, 'Indexes.'),
    'indicated_annual_dividend': FieldInfo('indicated_annual_dividend', FieldType.FUNDAMENTAL_PRICE, 'Indicated annual dividend [monetary value in fundamental/fund currency].'),
    'indicators_bars_count': FieldInfo('indicators_bars_count', FieldType.NUMBER, 'Indicators bars count.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'industry': FieldInfo('industry', FieldType.TEXT, 'FactSet industry.', values=('Advertising/Marketing Services', 'Aerospace & Defense', 'Agricultural Commodities/Milling', 'Air Freight/Couriers', 'Airlines', 'Alternative Power Generation', 'Aluminum', 'Apparel/Footwear', 'Apparel/Footwear Retail', 'Auto Parts: OEM', 'Automotive Aftermarket', 'Beverages: Alcoholic', 'Beverages: Non-Alcoholic', 'Biotechnology', 'Broadcasting', 'Building Products', 'Cable/Satellite TV', 'Casinos/Gaming', 'Catalog/Specialty Distribution', 'Chemicals: Agricultural', 'Chemicals: Major Diversified', 'Chemicals: Specialty', 'Coal', 'Commercial Printing/Forms', 'Computer Communications', 'Computer Peripherals', 'Computer Processing Hardware', 'Construction Materials', 'Consumer Sundries', 'Containers/Packaging', 'Contract Drilling', 'Data Processing Services', 'Department Stores', 'Discount Stores', 'Drugstore Chains', 'Electric Utilities', 'Electrical Products', 'Electronic Components', 'Electronic Equipment/Instruments', 'Electronic Production Equipment', 'Electronics Distributors', 'Electronics/Appliance Stores', 'Electronics/Appliances', 'Engineering & Construction', 'Environmental Services', 'Finance/Rental/Leasing', 'Financial Conglomerates', 'Financial Publishing/Services', 'Food Distributors', 'Food Retail', 'Food: Major Diversified', 'Food: Meat/Fish/Dairy', 'Food: Specialty/Candy', 'Forest Products', 'Gas Distributors', 'General Government', 'Home Furnishings', 'Home Improvement Chains', 'Homebuilding', 'Hospital/Nursing Management', 'Hotels/Resorts/Cruise lines', 'Household/Personal Care', 'Industrial Conglomerates', 'Industrial Machinery', 'Industrial Specialties', 'Information Technology Services', 'Insurance Brokers/Services', 'Integrated Oil', 'Internet Retail', 'Internet Software/Services', 'Investment Banks/Brokers', 'Investment Managers', 'Investment Trusts/Mutual Funds', 'Life/Health Insurance', 'Major Banks', 'Major Telecommunications', 'Managed Health Care', 'Marine Shipping', 'Media Conglomerates', 'Medical Distributors', 'Medical Specialties', 'Medical/Nursing Services', 'Metal Fabrication', 'Miscellaneous', 'Miscellaneous Commercial Services', 'Miscellaneous Manufacturing', 'Motor Vehicles', 'Movies/Entertainment', 'Multi-Line Insurance', 'Office Equipment/Supplies', 'Oil & Gas Pipelines', 'Oil & Gas Production', 'Oil Refining/Marketing', 'Oilfield Services/Equipment', 'Other Consumer Services', 'Other Consumer Specialties', 'Other Metals/Minerals', 'Other Transportation', 'Packaged Software', 'Personnel Services', 'Pharmaceuticals: Generic', 'Pharmaceuticals: Major', 'Pharmaceuticals: Other', 'Precious Metals', 'Property/Casualty Insurance', 'Publishing: Books/Magazines', 'Publishing: Newspapers', 'Pulp & Paper', 'Railroads', 'Real Estate Development', 'Real Estate Investment Trusts', 'Recreational Products', 'Regional Banks', 'Restaurants', 'Savings Banks', 'Semiconductors', 'Services to the Health Industry', 'Specialty Insurance', 'Specialty Stores', 'Specialty Telecommunications', 'Steel', 'Telecommunications Equipment', 'Textiles', 'Tobacco', 'Tools & Hardware', 'Trucking', 'Trucks/Construction/Farm Machinery', 'Water Utilities', 'Wholesale Distributors', 'Wireless Telecommunications')),
    'interst_cover_fy': FieldInfo('interst_cover_fy', FieldType.NUMBER, 'Interst cover (fiscal year).'),
    'interst_cover_ttm': FieldInfo('interst_cover_ttm', FieldType.NUMBER, 'Interst cover (trailing twelve months).'),
    'invent_turnover_current': FieldInfo('invent_turnover_current', FieldType.NUMBER, 'Invent turnover current.'),
    'invent_turnover_fy': FieldInfo('invent_turnover_fy', FieldType.NUMBER, 'Invent turnover (fiscal year).'),
    'inverse_flag': FieldInfo('inverse_flag', FieldType.NUMBER, 'Inverse flag.'),
    'ipo_announcement_date': FieldInfo('ipo_announcement_date', FieldType.TIME, 'IPO announcement date [UNIX timestamp (seconds)].'),
    'ipo_blank_check_flag': FieldInfo('ipo_blank_check_flag', FieldType.BOOL, 'IPO blank check flag.'),
    'ipo_deal_amount_usd': FieldInfo('ipo_deal_amount_usd', FieldType.NUMBER, 'IPO deal amount usd.'),
    'ipo_market_cap_usd': FieldInfo('ipo_market_cap_usd', FieldType.NUMBER, 'IPO market cap usd.'),
    'ipo_offer_date': FieldInfo('ipo_offer_date', FieldType.TIME, 'IPO offer date [UNIX timestamp (seconds)].'),
    'ipo_offer_price_performance': FieldInfo('ipo_offer_price_performance', FieldType.PERCENT, 'IPO offer price performance [percentage points (12.5 means 12.5%)].'),
    'ipo_offer_price_usd': FieldInfo('ipo_offer_price_usd', FieldType.NUMBER, 'IPO offer price usd.'),
    'ipo_offer_time': FieldInfo('ipo_offer_time', FieldType.TIME, 'IPO offer time [UNIX timestamp (seconds)].'),
    'ipo_offered_shares': FieldInfo('ipo_offered_shares', FieldType.NUMBER, 'IPO offered shares.'),
    'ipo_offered_shares_primary': FieldInfo('ipo_offered_shares_primary', FieldType.NUMBER, 'IPO offered shares primary.'),
    'ipo_offered_shares_secondary': FieldInfo('ipo_offered_shares_secondary', FieldType.NUMBER, 'IPO offered shares secondary.'),
    'ipo_price_range_usd_max': FieldInfo('ipo_price_range_usd_max', FieldType.NUMBER, 'IPO price range usd maximum.'),
    'ipo_price_range_usd_min': FieldInfo('ipo_price_range_usd_min', FieldType.NUMBER, 'IPO price range usd minimum.'),
    'ipo_shares_outstanding': FieldInfo('ipo_shares_outstanding', FieldType.NUMBER, 'IPO shares outstanding.'),
    'ipo_splitfactor_to_offer': FieldInfo('ipo_splitfactor_to_offer', FieldType.NUMBER, 'IPO splitfactor to offer.'),
    'is_blacklisted': FieldInfo('is_blacklisted', FieldType.BOOL, 'Is blacklisted.'),
    'is_primary': FieldInfo('is_primary', FieldType.BOOL, 'True when this is the primary listing of the instrument. Values: true/false.'),
    'is_shariah_compliant': FieldInfo('is_shariah_compliant', FieldType.BOOL, 'Is shariah compliant.'),
    'is_symbol_primary_listing': FieldInfo('is_symbol_primary_listing', FieldType.BOOL, 'Is symbol primary listing.'),
    'issuance_of_stock_net_ttm': FieldInfo('issuance_of_stock_net_ttm', FieldType.FUNDAMENTAL_PRICE, 'Issuance of stock net (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'issuer': FieldInfo('issuer', FieldType.TEXT, 'Fund issuer company.', values=('21Shares AG', '21co Holdings Ltd.', '3EDGE Asset Management LP', '3Fourteen & SMI Advisory Services LLC', '818, Inc.', 'ACP Horizon Holdings LP', 'AG Financial Services Group', 'AGF Management Ltd.', 'AJM Ventures LLC', 'AMG National Corp.', 'AOT Invest LLC', 'ARK Invest LLC', 'Abacus Global Management, Inc.', 'Aberdeen Group Plc', 'Absolute Investment Advisers LLC', 'Acquirers Funds LLC', 'Acuitas Investments LLC', 'Advent Capital Management LLC', 'Aegon Ltd.', 'Affiliated Managers Group, Inc.', 'Akre Capital Management LLC', 'Albert D. Mason, Inc.', 'Alexis Investment Partners LLC', 'Alger Associates, Inc. (United States)', 'AllianceBernstein LP', 'Allianz SE', 'Allspring Group Holdings LLC', 'Alternative Access Funds LLC', 'AmeriLife Group LLC', 'American Beacon Advisors, Inc.', 'American Beacon Partners', 'American Century Cos., Inc.', 'Ameriprise Financial, Inc.', 'Amplify Holding Co. LLC', 'Angel Oak Cos. LP', 'Aptus Holdings LLC', 'Arax Investment Partners LLC', 'Archer Investment Corp.', 'Argent Holdings, Inc.', 'Aristotle Capital Management LLC', 'Arlington Capital Ltd.', 'Arrow Investment Advisors LLC', 'Azimut Holding SpA', 'BCP CC Holdings LP', 'BPCE SA', 'Bahl & Gaynor, Inc.', 'Baillie Gifford & Co.', 'Baird Financial Group, Inc.', 'Bancreek Capital Management LP', 'Bank of Montreal', 'Barclays PLC', 'Baron Capital Group, Inc.', 'Belpointe Financial Holdings LLC', 'Beyond Investing LLC', 'Bitwise Asset Management, Inc.', 'BlackRock, Inc.', 'Bondbloxx Investment Management Corp.', 'Brandes Worldwide Holdings LP', 'Brookfield Asset Management Ltd.', 'Brookmont Capital Management LLC', 'Brown Advisory Management LLC', 'Brown Brothers Harriman & Co.', 'Build Asset Management LLC', 'CCM Holding Co. LLC', 'CCM Partners LP', 'CI Financial Corp.', 'COtwo Advisors LLC', 'CYBER HORNET ETFs LLC', 'Calamos Family Partners, Inc.', 'Cambiar Holdings LLLP', 'Cambria Investment Management LP', 'Canary Capital Group, Inc.', 'Capital Impact Advisors LLC', 'Cary Street Partners Financial LLC', 'CastleArk Management LLC', 'Cavalier16, Inc.', 'China International Capital Corp. Ltd.', 'Clough CGI LLC', 'Cohen & Steers, Inc. (New York)', 'Coinshares International Ltd.', 'Colliers International Group, Inc.', 'Concourse Capital Advisors LLC', 'Convergence Investment Partners LLC', 'Core Alternative Capital LLC', 'Corgi Insurance Services, Inc.', 'Corgi Strategies LLC', 'Cottonwood ETF Holdings LLC', 'Counterpoint Mutual Funds LLC', 'Cullen Capital Management LLC', 'Cultivar Capital, Inc.', 'Cygnet Capital LLC', 'Dakota Wealth Management LLC (Florida)', 'Davis Selected Advisers LP', 'Dawn Global Topco Ltd.', 'Deegan Holdings LLC', 'Defiance ETFs LLC', 'Defiance Group Holdings LLC', 'Deutsche Bank AG', 'Dhandho Holdings LP', 'Diamond Hill Investment Group LLC', 'Digital Currency Group, Inc.', 'Dimensional Holdings, Inc.', 'Distillate Capital Partners LLC', 'Distribution Cognizant LLC', 'Dividend Assets Capital Holdings, Inc.', 'Donoghue Forlines LLC', 'Doubleline ETF Holdings LP', 'Dvx Ventures LLC', 'ETP Holding Co. LLC', 'Eagle Capital Management LLC', 'Emirate of Abu Dhabi (United Arab Emirates)', 'Empirical Finance LLC', 'Envestnet, Inc.', 'Estate Counselors LLC', 'Eventide Asset Management LLC', 'Everence Association, Inc.', 'F/m Investments LLC', 'FMC Group Holdings LP', 'FMR LLC', 'Faith Investor Services LLC', 'Falconx Holdings Ltd.', 'Federated Hermes, Inc.', 'First Eagle Investment Management LLC', 'First Pacific Advisors LP', 'First Trust Advisors LP', 'Focus Financial Partners, Inc.', 'Formidable Asset Management LLC', 'Fortuna Funds LLC', 'Founder ETFs LLC', 'Framework Digital Advisors LLC', 'Franklin Resources, Inc.', 'Frontier Asset Management LLC', 'Future Fund Advisors LLC', 'GAMCO Investors, Inc.', 'GC Ferry Parent LP', 'GQG Partners, Inc.', 'Gladius Capital Management LP', 'Golden Eagle Asset Management Co., Ltd.', 'Goose Hollow Capital Management LLC', 'Graff Capital', 'Granite Group Advisors LLC', 'GraniteShares, Inc.', 'Grantham, Mayo, Van Otterloo & Co. LLC', 'Guardian Capital Group Ltd.', 'Guggenheim Capital LLC', 'Guinness Atkinson Asset Management, Inc.', 'HWCap Holdings LLC', 'Hashdex Ltd.', 'Hedgeye Risk Management LLC', 'Hennessy Advisors, Inc.', 'Hexis Capital Management Ltd.', 'Horizon Investments LLC', 'Horizon Kinetics Holding Corp.', 'Howard Capital Management, Inc. (Georgia)', 'Hull Investments LLC', 'Hypatia Capital Group LLC', 'IDX Advisors LLC', 'Impax Asset Management Group Plc', 'Indexperts LLC', 'Infrastructure Capital Advisors LLC', 'Inspire Impact Group LLC', 'Intech Holdings LLC', 'Inverdale Capital Management LLC', 'Invesco Ltd.', 'IronHorse Holdings LLC', 'Ishares Digital Assets AG', 'JPMorgan Chase & Co.', 'Janus Henderson Group Plc', 'Jensen Investment Management, Inc.', 'Kensington Asset Management LLC', 'Killir Kapital Management LLC', 'Kingsbarn Capital Management LLC', 'Kingsview Partners LLC', 'Kurv Investment, Inc.', 'Lagan Holding Co. Trust', 'Langar Holdings, Inc.', 'Lazard, Inc.', 'Le Mouvement des caisses Desjardins', 'LionShares LLC', 'Liquid Strategies LLC', 'Little Harbor Advisors LLC', 'Logan Capital Management, Inc.', 'Long Pond Capital LP', 'M. D. Sass LLC', 'M2 Financial LLC', 'MIG Capital LLC', 'MM VAM LLC', 'Madison Investment Holdings, Inc.', 'Main Management LLC', 'Mairs & Power, Inc.', 'Man Group Plc (Jersey)', 'Manulife Financial Corp.', 'Marathon Partners LLC', 'Matthews International Capital Management LLC', 'Measured Risk Portfolios, Inc.', 'Merchant Investment Management LLC', 'Miller Value Partners LLC', 'Milliman, Inc.', 'Mirae Asset Global Investments Co., Ltd.', 'Mitsubishi UFJ Financial Group, Inc.', 'Monex Group, Inc.', 'Morgan Stanley', 'Msc Group SA', 'Myriad Asset Management Advisors LLC', 'NBSH Acquisition LLC', 'NEOS Investments LLC', 'NSI Holdings, Inc.', 'NZC Capital LLC', 'Neil Azous Revocable Trust', 'New York Life Insurance Co.', 'Nicholas Wealth LLC', 'Nightview Capital LLC', 'Noa LLC', 'Nomura Holdings, Inc.', 'Norris, Perne & French LLP', 'Northern Trust Corp.', 'Nuveen LLC', 'Nuveen Securities LLC', 'ORIX Corp.', 'Ocean Park Asset Management LLC', 'Oneascent Holdings LLC', 'Optimize Financial, Inc.', 'Osprey Funds LLC', 'PMV Capital LLC', 'PTAM Holdings LLC', 'Pacer Advisors, Inc.', 'Pacific Investments Ltd.', 'Palmer Square Holdings LLC', 'Paralel Technologies LLC', 'Peakshares LLC', 'Pettee Investors, Inc.', 'Pictet & Partners', 'PlanRock Investment Management LLC', 'Polen Capital Management LLC', 'Precidian Investments LLC', 'Principal Financial Group, Inc.', 'ProShare Advisors LLC', 'ProcureAM LLC', 'Prospera Funds, Inc.', 'Prudential Financial, Inc.', 'Purpose Unlimited, Inc.', 'Pzena Investment Management LP', 'Q3 Asset Management Corp.', 'RDJ Associates LLC', 'Rafferty Asset Management LLC', 'Rational Advisors, Inc.', 'Raymond James Financial, Inc.', 'Redbird Capital Partners Alternative Holdings LLC', 'Redwood Investment Holdco LLC', 'Reflection Asset Management LLC', 'Regan Capital LLC', 'Renaissance Capital LLC', 'Retireful LLC', 'Reverence Capital Partners LLC', 'Rex Financial LLC', 'Ridgeline Research LLC', 'RiverNorth Holding Co.', 'Rock Point Partners LLC', 'Roundhill Financial, Inc.', 'Royal Bank of Canada', 'Running Oak Capital LLC', 'Russell Investments Group Ltd.', 'S.C.M. Edge, LLC', 'SAS Rue la Boétie', 'SEI Investments Co.', 'SR Partners LLC', 'SS&C Technologies Holdings, Inc.', 'SWP Investment Management LLC', 'Sammons Enterprises, Inc.', 'Saracen Energy Advisors LP', 'Saturna Capital Corp.', 'Scharf Investments LLC', 'ShariaPortfolio, Inc.', 'Simplify Asset Management, Inc.', 'Sound Capital Holdings LLC', 'Sound Capital Solutions LLC', 'Soundwatch Capital LLC', "Sovereign's Capital Management LLC", 'Spear Advisors LLC', 'Spend Life Wisely Co., Inc.', 'Split Rock Private Trading & Wealth Management LLC', 'Sprott, Inc.', 'State Street Corp.', 'State of Zurich', 'Sterling Capital Management LLC', 'Stone Ridge Holdings Group LP', 'Summit Global LLC', 'Sun Life Financial, Inc.', 'Swan Global Holdings (US) LLC', 'Symmetry Partners LLC', 'T. Rowe Price Group, Inc.', 'TFG Parent Holdings LLC', 'TIAA Board of Governors', 'Tapp Finance, Inc.', 'Teucrium Trading LLC', 'Texas Capital Bancshares, Inc.', 'The Applied Finance Group Ltd.', 'The Bank of New York Mellon Corp.', 'The Burney Co.', 'The Capital Group Cos., Inc.', 'The Charles Schwab Corp.', 'The Eighth Wonder Foundation', 'The Goldman Sachs Group, Inc.', 'The Greenwood Trust', 'The Hartford Insurance Group, Inc.', 'The Leuthold Group LLC', 'The Marygold Cos, Inc.', 'The Mcivy Co. LLC', 'The Motley Fool Holdings, Inc.', 'The TCW Group, Inc.', 'The Vanguard Group, Inc.', 'Thor Trading Advisors LLC', 'Thornburg Investment Management, Inc.', 'Thrivent Financial for Lutherans', 'Timothy Partners Ltd.', 'Toews Corp.', 'TortoiseEcofin Investments LLC', 'Tremblant Advisors LP', 'Truemark Group LLC', 'Tuttle Capital Management LLC', 'Twin Oak Holdings LP', 'U.S. Global Investors, Inc.', 'UBS Group AG', 'Van Eck Associates Corp.', 'Vega Financial Group, LLC', 'Veritas Liberabit Vos LLC', 'Vert Asset Management LLC', 'Victory Capital Holdings, Inc.', "Vident Investors' Oversight Trust", 'Virtus Investment Partners, Inc.', 'Volatility Shares LLC', 'Vontobel Holding AG', 'WA Holdings, Inc.', 'WBI Trading Co., Inc.', 'WEBs Investments, Inc.', 'Wahed Invest LLC', 'Warren Capital Management, Inc.', 'Water Island Capital Partners LP', 'Waverly Advisors LLC', 'Waystone Governance Ltd.', 'WealthTrust Asset Management LLC', 'Wedbush Family Partners LLC', 'Weitz Investment Management, Inc.', 'Wellesley Asset Management, Inc.', 'Wellington Management Group LLP', 'Western & Southern Mutual Holding Co.', 'Westwood Holdings Group, Inc.', 'Wilson Lane Group LLC', 'WisdomTree, Inc.', 'World Gold Council Ltd.', 'Worth Charting Group LLC', 'X Square Capital LLC', 'Yorkville America LLC', 'iM Global Partner SAS')),
    'k1_form': FieldInfo('k1_form', FieldType.TEXT, 'K1 form.', values=('0', '1')),
    'kind': FieldInfo('kind', FieldType.TEXT, 'Kind.', values=('rt',)),
    'kind-delay': FieldInfo('kind-delay', FieldType.NUMBER, 'Kind delay.'),
    'last-price-update-time': FieldInfo('last-price-update-time', FieldType.TIME, 'Last price update time [UNIX timestamp (seconds)].'),
    'last-price-update-time-intraday': FieldInfo('last-price-update-time-intraday', FieldType.TIME, 'Last price update time intraday [UNIX timestamp (seconds)].'),
    'last_annual_eps': FieldInfo('last_annual_eps', FieldType.FUNDAMENTAL_PRICE, 'Last annual EPS [monetary value in fundamental/fund currency].'),
    'last_annual_revenue': FieldInfo('last_annual_revenue', FieldType.FUNDAMENTAL_PRICE, 'Last annual revenue [monetary value in fundamental/fund currency].'),
    'last_bar_update_time': FieldInfo('last_bar_update_time', FieldType.NUMBER, 'Last bar update time.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'last_report_frequency': FieldInfo('last_report_frequency', FieldType.NUMBER, 'Last report frequency.'),
    'launch_date': FieldInfo('launch_date', FieldType.TIME, 'Launch date [UNIX timestamp (seconds)].'),
    'leverage': FieldInfo('leverage', FieldType.TEXT, 'Leverage.', values=('03c3e49bdc7aeee29cfd314c475fb410', '1437a5ebc1f95c484fe8cd180aea771c', '1636f70a7bf29b6ae3bdd70362782a50', '205b83335c9d5a9dad8dae82e0856c1f', '3c10eee496eb162ae0ed866403f2f032', '49204706ae89a84f49643608a4a1eccb', '496c5d6ea632c128a304c0b683f2bdfc', '70963b2ddfe1f798eda29e875ace6ab4', '88ba1211175189c63246bb29132b1d2e', 'a91c78e040f7b9d158f381e197f8beb4', 'b17077929ec55058d0eafe7827587934', 'c8bb3176ea791b632824fe397e9d0935', 'ca2e0331f4d1d23b2cd299f128853317', 'ded39cc46d3bcec2b9a969a7fdb5fabe', 'e782cde821fae6ce1b676cfd4d140aa8', 'ea26d532fadeb8bf0bc57e3ef88cec27')),
    'leverage_ratio': FieldInfo('leverage_ratio', FieldType.TEXT, 'Fund leverage ratio (e.g. 2, 3 for leveraged ETFs).', values=('1.25x', '1.5x', '2x', '3x', 'Other', 'Variable')),
    'leveraged_flag': FieldInfo('leveraged_flag', FieldType.TEXT, 'Leverage classification of the fund.', values=('Inverse', 'Leveraged', 'Non-leveraged')),
    'logoid': FieldInfo('logoid', FieldType.TEXT, 'Identifier of the instrument logo image.'),
    'long_term_capital': FieldInfo('long_term_capital', FieldType.NUMBER, 'Long term capital.'),
    'long_term_debt_fq': FieldInfo('long_term_debt_fq', FieldType.FUNDAMENTAL_PRICE, 'Long term debt (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'long_term_debt_fy': FieldInfo('long_term_debt_fy', FieldType.FUNDAMENTAL_PRICE, 'Long term debt (fiscal year) [monetary value in fundamental/fund currency].'),
    'long_term_debt_to_assets_fq': FieldInfo('long_term_debt_to_assets_fq', FieldType.NUMBER, 'Long term debt to assets (fiscal quarter).'),
    'long_term_debt_to_assets_fy': FieldInfo('long_term_debt_to_assets_fy', FieldType.NUMBER, 'Long term debt to assets (fiscal year).'),
    'long_term_debt_to_equity_fq': FieldInfo('long_term_debt_to_equity_fq', FieldType.NUMBER, 'Long term debt to equity (fiscal quarter).'),
    'low': FieldInfo('low', FieldType.PRICE, 'Session low price.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'low_after_high_all_change': FieldInfo('low_after_high_all_change', FieldType.PERCENT, 'Low after high over all time change [percentage points (12.5 means 12.5%)].'),
    'low_after_high_all_change_abs': FieldInfo('low_after_high_all_change_abs', FieldType.PRICE, 'Low after high over all time change (absolute).'),
    'market': FieldInfo('market', FieldType.TEXT, 'TradingView market this symbol belongs to (e.g. america).', values=('america',)),
    'market_cap_basic': FieldInfo('market_cap_basic', FieldType.FUNDAMENTAL_PRICE, 'Market capitalization (fundamental currency).'),
    'market_cap_calc': FieldInfo('market_cap_calc', FieldType.NUMBER, 'Market cap calculated.'),
    'maturity_date': FieldInfo('maturity_date', FieldType.TIME_YYYYMMDD, 'Maturity date.'),
    'minmov': FieldInfo('minmov', FieldType.NUMBER, 'Minmov.'),
    'minmove2': FieldInfo('minmove2', FieldType.NUMBER, 'Minmove2.'),
    'minute-bar.time': FieldInfo('minute-bar.time', FieldType.NUMBER, 'Minute bar time.'),
    'most_recent_quarter_date': FieldInfo('most_recent_quarter_date', FieldType.TIME, 'Most recent quarter date [UNIX timestamp (seconds)].'),
    'name': FieldInfo('name', FieldType.TEXT, 'Ticker symbol (without exchange prefix).'),
    'nav': FieldInfo('nav', FieldType.FUNDAMENTAL_PRICE, 'Net asset value per share.'),
    'nav_discount_premium': FieldInfo('nav_discount_premium', FieldType.NUMBER, 'Price premium/discount to NAV, percent.'),
    'nav_perf.1M': FieldInfo('nav_perf.1M', FieldType.NUMBER, 'NAV performance 1M.'),
    'nav_perf.1Y': FieldInfo('nav_perf.1Y', FieldType.NUMBER, 'NAV performance 1Y.'),
    'nav_perf.3M': FieldInfo('nav_perf.3M', FieldType.NUMBER, 'NAV performance 3M.'),
    'nav_perf.3Y': FieldInfo('nav_perf.3Y', FieldType.NUMBER, 'NAV performance 3Y.'),
    'nav_perf.5Y': FieldInfo('nav_perf.5Y', FieldType.NUMBER, 'NAV performance 5Y.'),
    'nav_perf.YTD': FieldInfo('nav_perf.YTD', FieldType.NUMBER, 'NAV performance year-to-date.'),
    'nav_total_return.1M': FieldInfo('nav_total_return.1M', FieldType.NUMBER, 'NAV total return 1M.'),
    'nav_total_return.1Y': FieldInfo('nav_total_return.1Y', FieldType.NUMBER, 'NAV total return over 1 year, percent.'),
    'nav_total_return.3M': FieldInfo('nav_total_return.3M', FieldType.NUMBER, 'NAV total return 3M.'),
    'nav_total_return.3Y': FieldInfo('nav_total_return.3Y', FieldType.NUMBER, 'NAV total return over 3 years, percent.'),
    'nav_total_return.5Y': FieldInfo('nav_total_return.5Y', FieldType.NUMBER, 'NAV total return over 5 years, percent.'),
    'nav_total_return.6M': FieldInfo('nav_total_return.6M', FieldType.NUMBER, 'NAV total return 6M.'),
    'nav_total_return.YTD': FieldInfo('nav_total_return.YTD', FieldType.NUMBER, 'NAV total return year-to-date, percent.'),
    'ncavps_ratio_current': FieldInfo('ncavps_ratio_current', FieldType.FUNDAMENTAL_PRICE, 'Ncavps ratio current [monetary value in fundamental/fund currency].'),
    'ncavps_ratio_fh': FieldInfo('ncavps_ratio_fh', FieldType.FUNDAMENTAL_PRICE, 'Ncavps ratio (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'ncavps_ratio_fq': FieldInfo('ncavps_ratio_fq', FieldType.FUNDAMENTAL_PRICE, 'Ncavps ratio (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'ncavps_ratio_fy': FieldInfo('ncavps_ratio_fy', FieldType.FUNDAMENTAL_PRICE, 'Ncavps ratio (fiscal year) [monetary value in fundamental/fund currency].'),
    'neg_capital_expenditures_fh': FieldInfo('neg_capital_expenditures_fh', FieldType.FUNDAMENTAL_PRICE, 'Neg capital expenditures (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'neg_capital_expenditures_fq': FieldInfo('neg_capital_expenditures_fq', FieldType.FUNDAMENTAL_PRICE, 'Neg capital expenditures (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'neg_capital_expenditures_fy': FieldInfo('neg_capital_expenditures_fy', FieldType.FUNDAMENTAL_PRICE, 'Neg capital expenditures (fiscal year) [monetary value in fundamental/fund currency].'),
    'neg_capital_expenditures_ttm': FieldInfo('neg_capital_expenditures_ttm', FieldType.FUNDAMENTAL_PRICE, 'Neg capital expenditures (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'neg_research_and_dev_fh': FieldInfo('neg_research_and_dev_fh', FieldType.FUNDAMENTAL_PRICE, 'Neg research and deviation (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'neg_research_and_dev_fq': FieldInfo('neg_research_and_dev_fq', FieldType.FUNDAMENTAL_PRICE, 'Neg research and deviation (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'neg_research_and_dev_fy': FieldInfo('neg_research_and_dev_fy', FieldType.FUNDAMENTAL_PRICE, 'Neg research and deviation (fiscal year) [monetary value in fundamental/fund currency].'),
    'neg_research_and_dev_ttm': FieldInfo('neg_research_and_dev_ttm', FieldType.FUNDAMENTAL_PRICE, 'Neg research and deviation (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'neg_total_cash_dividends_paid_fh': FieldInfo('neg_total_cash_dividends_paid_fh', FieldType.FUNDAMENTAL_PRICE, 'Neg total cash dividends paid (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'neg_total_cash_dividends_paid_fq': FieldInfo('neg_total_cash_dividends_paid_fq', FieldType.FUNDAMENTAL_PRICE, 'Neg total cash dividends paid (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'neg_total_cash_dividends_paid_fy': FieldInfo('neg_total_cash_dividends_paid_fy', FieldType.FUNDAMENTAL_PRICE, 'Neg total cash dividends paid (fiscal year) [monetary value in fundamental/fund currency].'),
    'neg_total_cash_dividends_paid_ttm': FieldInfo('neg_total_cash_dividends_paid_ttm', FieldType.FUNDAMENTAL_PRICE, 'Neg total cash dividends paid (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'net_debt': FieldInfo('net_debt', FieldType.FUNDAMENTAL_PRICE, 'Net debt [monetary value in fundamental/fund currency].'),
    'net_debt_fq': FieldInfo('net_debt_fq', FieldType.FUNDAMENTAL_PRICE, 'Net debt (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'net_debt_fy': FieldInfo('net_debt_fy', FieldType.FUNDAMENTAL_PRICE, 'Net debt (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_debt_to_ebitda_fq': FieldInfo('net_debt_to_ebitda_fq', FieldType.NUMBER, 'Net debt to EBITDA (fiscal quarter).'),
    'net_debt_to_ebitda_fy': FieldInfo('net_debt_to_ebitda_fy', FieldType.NUMBER, 'Net debt to EBITDA (fiscal year).'),
    'net_income': FieldInfo('net_income', FieldType.FUNDAMENTAL_PRICE, 'Net income [monetary value in fundamental/fund currency].'),
    'net_income_bef_disc_oper_fy': FieldInfo('net_income_bef_disc_oper_fy', FieldType.FUNDAMENTAL_PRICE, 'Net income bef disc operating (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_income_bef_disc_oper_margin_fy': FieldInfo('net_income_bef_disc_oper_margin_fy', FieldType.PERCENT, 'Net income bef disc operating margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'net_income_cagr_5y': FieldInfo('net_income_cagr_5y', FieldType.PERCENT, 'Net income CAGR 5y [percentage points (12.5 means 12.5%)].'),
    'net_income_estimate_fh': FieldInfo('net_income_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Net income estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'net_income_estimate_fq': FieldInfo('net_income_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Net income estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'net_income_estimate_fy': FieldInfo('net_income_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Net income estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_income_estimate_ntm': FieldInfo('net_income_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Net income estimate ntm [monetary value in fundamental/fund currency].'),
    'net_income_fh': FieldInfo('net_income_fh', FieldType.FUNDAMENTAL_PRICE, 'Net income (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'net_income_fq': FieldInfo('net_income_fq', FieldType.FUNDAMENTAL_PRICE, 'Net income (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'net_income_fq_h': FieldInfo('net_income_fq_h', FieldType.NUM_SLICE, 'Net income (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'net_income_fy': FieldInfo('net_income_fy', FieldType.FUNDAMENTAL_PRICE, 'Net income (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_income_fy_h': FieldInfo('net_income_fy_h', FieldType.NUM_SLICE, 'Net income (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'net_income_per_employee_fy': FieldInfo('net_income_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Net income per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_income_qoq_growth_fq': FieldInfo('net_income_qoq_growth_fq', FieldType.PERCENT, 'Net income quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'net_income_ttm': FieldInfo('net_income_ttm', FieldType.FUNDAMENTAL_PRICE, 'Net income (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'net_income_ttm_h': FieldInfo('net_income_ttm_h', FieldType.NUM_SLICE, 'Net income (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'net_income_yoy_growth_fq': FieldInfo('net_income_yoy_growth_fq', FieldType.PERCENT, 'Net income year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'net_income_yoy_growth_fy': FieldInfo('net_income_yoy_growth_fy', FieldType.PERCENT, 'Net income year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'net_income_yoy_growth_ttm': FieldInfo('net_income_yoy_growth_ttm', FieldType.PERCENT, 'Net income year-over-year growth (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'net_margin': FieldInfo('net_margin', FieldType.PERCENT, 'Net margin [percentage points (12.5 means 12.5%)].'),
    'net_margin_fy': FieldInfo('net_margin_fy', FieldType.PERCENT, 'Net margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'net_margin_ttm': FieldInfo('net_margin_ttm', FieldType.PERCENT, 'Net profit margin, percent, TTM.'),
    'net_revenue_after_provision_fh': FieldInfo('net_revenue_after_provision_fh', FieldType.FUNDAMENTAL_PRICE, 'Net revenue after provision (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'net_revenue_after_provision_fq': FieldInfo('net_revenue_after_provision_fq', FieldType.FUNDAMENTAL_PRICE, 'Net revenue after provision (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'net_revenue_after_provision_fy': FieldInfo('net_revenue_after_provision_fy', FieldType.FUNDAMENTAL_PRICE, 'Net revenue after provision (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_revenue_after_provision_ttm': FieldInfo('net_revenue_after_provision_ttm', FieldType.FUNDAMENTAL_PRICE, 'Net revenue after provision (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'net_revenue_fh': FieldInfo('net_revenue_fh', FieldType.FUNDAMENTAL_PRICE, 'Net revenue (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'net_revenue_fq': FieldInfo('net_revenue_fq', FieldType.FUNDAMENTAL_PRICE, 'Net revenue (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'net_revenue_fy': FieldInfo('net_revenue_fy', FieldType.FUNDAMENTAL_PRICE, 'Net revenue (fiscal year) [monetary value in fundamental/fund currency].'),
    'net_revenue_ttm': FieldInfo('net_revenue_ttm', FieldType.FUNDAMENTAL_PRICE, 'Net revenue (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'next_dividend_date': FieldInfo('next_dividend_date', FieldType.TIME, 'Next dividend date [UNIX timestamp (seconds)].'),
    'niche': FieldInfo('niche', FieldType.TEXT, "Fund niche segment (internal id; use 'niche.tr' column for the readable label).", values=('10', '100', '1000', '101', '1011', '1013', '1015', '1016', '1017', '1018', '1019', '102', '1020', '1021', '1028', '1033', '1034', '1035', '1037', '1038', '104', '1040', '1043', '1044', '105', '106', '1066', '1067', '1068', '107', '1072', '1073', '1074', '1075', '1077', '1078', '1079', '108', '1081', '1082', '1083', '1084', '1085', '1086', '1087', '1088', '1089', '1091', '1092', '1094', '1095', '1096', '1097', '1098', '11', '110', '1100', '1101', '111', '116', '12', '126', '127', '13', '14', '141', '143', '144', '145', '150', '155', '16', '167', '169', '171', '174', '18', '19', '192', '193', '20', '30', '33', '34', '35', '36', '37', '38', '39', '4', '40', '42', '43', '47', '48', '49', '50', '53', '55', '56', '57', '58', '6', '60', '61', '65', '67', '69', '7', '70', '72', '83', '85', '86', '88', '89', '9', '90', '92', '93', '94', '9521', '9522', '9523', '9524', '9527', '9528', '9529', '9530', '9532', '9534', '9535', '9536', '9540', '9547', '9548', '9549', '9550', '9552', '9553', '9557', '9558', '9562', '9563', '9564', '9565', '9566', '9568', '9569', '9571', '9574', '9575', '9578', '9580', '9581', '9582', '9583', '9584', '9587', '9588', '9589', '9590', '9591', '9592', '9594', '9595', '9596', '9597', '9598', '9599', '9601', '9602', '9603', '9604', '9606', '9607', '9609', '9611', '9616', '9617', '97', '98', '9861', '9864', '9866', '9897', '9898', '9937')),
    'non_gaap_price_to_earnings_per_share_forecast_next_fy': FieldInfo('non_gaap_price_to_earnings_per_share_forecast_next_fy', FieldType.NUMBER, 'Non GAAP price to earnings per share forecast next (fiscal year).'),
    'number_of_employees': FieldInfo('number_of_employees', FieldType.NUMBER, 'Number of employees.'),
    'number_of_employees_fy': FieldInfo('number_of_employees_fy', FieldType.NUMBER, 'Number of employees (fiscal year).'),
    'number_of_shareholders': FieldInfo('number_of_shareholders', FieldType.NUMBER, 'Number of shareholders.'),
    'number_of_shareholders_fy': FieldInfo('number_of_shareholders_fy', FieldType.NUMBER, 'Number of shareholders (fiscal year).'),
    'open': FieldInfo('open', FieldType.PRICE, 'Session open price.', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'oper_income_fh': FieldInfo('oper_income_fh', FieldType.FUNDAMENTAL_PRICE, 'Operating income (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'oper_income_fq': FieldInfo('oper_income_fq', FieldType.FUNDAMENTAL_PRICE, 'Operating income (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'oper_income_fy': FieldInfo('oper_income_fy', FieldType.FUNDAMENTAL_PRICE, 'Operating income (fiscal year) [monetary value in fundamental/fund currency].'),
    'oper_income_margin_fy': FieldInfo('oper_income_margin_fy', FieldType.PERCENT, 'Operating income margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'oper_income_per_employee_fy': FieldInfo('oper_income_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Operating income per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'oper_income_ttm': FieldInfo('oper_income_ttm', FieldType.FUNDAMENTAL_PRICE, 'Operating income (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'operating_cash_flow_per_share_current': FieldInfo('operating_cash_flow_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Operating cash flow per share current [monetary value in fundamental/fund currency].'),
    'operating_cash_flow_per_share_fh': FieldInfo('operating_cash_flow_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Operating cash flow per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'operating_cash_flow_per_share_fq': FieldInfo('operating_cash_flow_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Operating cash flow per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'operating_cash_flow_per_share_fy': FieldInfo('operating_cash_flow_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Operating cash flow per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'operating_cash_flow_per_share_ttm': FieldInfo('operating_cash_flow_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'Operating cash flow per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'operating_margin': FieldInfo('operating_margin', FieldType.PERCENT, 'Operating margin [percentage points (12.5 means 12.5%)].'),
    'operating_margin_fy': FieldInfo('operating_margin_fy', FieldType.PERCENT, 'Operating margin (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'operating_margin_ttm': FieldInfo('operating_margin_ttm', FieldType.PERCENT, 'Operating margin, percent, TTM.'),
    'payment_date_recent': FieldInfo('payment_date_recent', FieldType.TIME, 'Payment date recent [UNIX timestamp (seconds)].'),
    'payment_date_upcoming': FieldInfo('payment_date_upcoming', FieldType.TIME, 'Payment date upcoming [UNIX timestamp (seconds)].'),
    'piotroski_f_score_fy': FieldInfo('piotroski_f_score_fy', FieldType.NUMBER, 'Piotroski from score (fiscal year).'),
    'piotroski_f_score_ttm': FieldInfo('piotroski_f_score_ttm', FieldType.NUMBER, 'Piotroski from score (trailing twelve months).'),
    'post_change': FieldInfo('post_change', FieldType.PERCENT, 'Post change [percentage points (12.5 means 12.5%)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'postmarket_change': FieldInfo('postmarket_change', FieldType.PERCENT, 'Post-market percent change.'),
    'postmarket_change_abs': FieldInfo('postmarket_change_abs', FieldType.PRICE, 'Postmarket change (absolute).'),
    'postmarket_close': FieldInfo('postmarket_close', FieldType.PRICE, 'Post-market last price.'),
    'postmarket_high': FieldInfo('postmarket_high', FieldType.PRICE, 'Postmarket high.'),
    'postmarket_low': FieldInfo('postmarket_low', FieldType.PRICE, 'Postmarket low.'),
    'postmarket_open': FieldInfo('postmarket_open', FieldType.PRICE, 'Postmarket open.'),
    'postmarket_time': FieldInfo('postmarket_time', FieldType.TIME, 'Postmarket time [UNIX timestamp (seconds)].'),
    'postmarket_volume': FieldInfo('postmarket_volume', FieldType.NUMBER, 'Post-market volume.'),
    'pre_change': FieldInfo('pre_change', FieldType.PERCENT, 'Pre change [percentage points (12.5 means 12.5%)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'pre_change_abs': FieldInfo('pre_change_abs', FieldType.PRICE, 'Pre change (absolute).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'pre_tax_margin': FieldInfo('pre_tax_margin', FieldType.PERCENT, 'Pre tax margin [percentage points (12.5 means 12.5%)].'),
    'pre_tax_margin_ttm': FieldInfo('pre_tax_margin_ttm', FieldType.PERCENT, 'Pre tax margin (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'preferred_dividends': FieldInfo('preferred_dividends', FieldType.NUMBER, 'Preferred dividends.'),
    'premarket_change': FieldInfo('premarket_change', FieldType.PERCENT, 'Pre-market percent change.'),
    'premarket_change_abs': FieldInfo('premarket_change_abs', FieldType.PRICE, 'Premarket change (absolute).'),
    'premarket_change_from_open': FieldInfo('premarket_change_from_open', FieldType.PERCENT, 'Premarket change from open [percentage points (12.5 means 12.5%)].'),
    'premarket_change_from_open_abs': FieldInfo('premarket_change_from_open_abs', FieldType.NUMBER, 'Premarket change from open (absolute).'),
    'premarket_close': FieldInfo('premarket_close', FieldType.PRICE, 'Pre-market last price.'),
    'premarket_gap': FieldInfo('premarket_gap', FieldType.PERCENT, 'Premarket gap [percentage points (12.5 means 12.5%)].'),
    'premarket_high': FieldInfo('premarket_high', FieldType.PRICE, 'Premarket high.'),
    'premarket_low': FieldInfo('premarket_low', FieldType.PRICE, 'Premarket low.'),
    'premarket_open': FieldInfo('premarket_open', FieldType.PRICE, 'Premarket open.'),
    'premarket_time': FieldInfo('premarket_time', FieldType.TIME, 'Premarket time [UNIX timestamp (seconds)].'),
    'premarket_volume': FieldInfo('premarket_volume', FieldType.NUMBER, 'Pre-market volume.'),
    'price_52_week_high': FieldInfo('price_52_week_high', FieldType.NUMBER, 'Highest price of the last 52 weeks.'),
    'price_52_week_high_date': FieldInfo('price_52_week_high_date', FieldType.TIME, 'Price (52) week high date [UNIX timestamp (seconds)].'),
    'price_52_week_low': FieldInfo('price_52_week_low', FieldType.NUMBER, 'Lowest price of the last 52 weeks.'),
    'price_52_week_low_date': FieldInfo('price_52_week_low_date', FieldType.TIME, 'Price (52) week low date [UNIX timestamp (seconds)].'),
    'price_annual_book': FieldInfo('price_annual_book', FieldType.NUMBER, 'Price annual book.'),
    'price_annual_sales': FieldInfo('price_annual_sales', FieldType.NUMBER, 'Price annual sales.'),
    'price_book_current': FieldInfo('price_book_current', FieldType.NUMBER, 'Price book current.'),
    'price_book_fq': FieldInfo('price_book_fq', FieldType.NUMBER, 'Price / book ratio, latest fiscal quarter.'),
    'price_book_fwd': FieldInfo('price_book_fwd', FieldType.NUMBER, 'Price book fwd.'),
    'price_book_ratio': FieldInfo('price_book_ratio', FieldType.NUMBER, 'Price book ratio.'),
    'price_cash_flow_current': FieldInfo('price_cash_flow_current', FieldType.NUMBER, 'Price cash flow current.'),
    'price_earnings_current': FieldInfo('price_earnings_current', FieldType.NUMBER, 'Price earnings current.'),
    'price_earnings_forward_fy': FieldInfo('price_earnings_forward_fy', FieldType.NUMBER, 'Price earnings forward (fiscal year).'),
    'price_earnings_fwd': FieldInfo('price_earnings_fwd', FieldType.NUMBER, 'Price earnings fwd.'),
    'price_earnings_growth_ttm': FieldInfo('price_earnings_growth_ttm', FieldType.NUMBER, 'PEG ratio (P/E divided by earnings growth), TTM.'),
    'price_earnings_ttm': FieldInfo('price_earnings_ttm', FieldType.NUMBER, 'P/E ratio, trailing twelve months. Typically ~0-100+; negative earnings give null/negative.'),
    'price_free_cash_flow_current': FieldInfo('price_free_cash_flow_current', FieldType.NUMBER, 'Price free cash flow current.'),
    'price_free_cash_flow_ttm': FieldInfo('price_free_cash_flow_ttm', FieldType.NUMBER, 'Price / free-cash-flow ratio, TTM.'),
    'price_revenue_ttm': FieldInfo('price_revenue_ttm', FieldType.NUMBER, 'Price revenue (trailing twelve months).'),
    'price_sales': FieldInfo('price_sales', FieldType.PRICE, 'Price sales.'),
    'price_sales_current': FieldInfo('price_sales_current', FieldType.NUMBER, 'Price / sales ratio, current.'),
    'price_sales_fwd': FieldInfo('price_sales_fwd', FieldType.NUMBER, 'Price sales fwd.'),
    'price_sales_ratio': FieldInfo('price_sales_ratio', FieldType.NUMBER, 'Price sales ratio.'),
    'price_target_1y': FieldInfo('price_target_1y', FieldType.PRICE, 'Price target 1y.'),
    'price_target_1y_delta': FieldInfo('price_target_1y_delta', FieldType.PERCENT, 'Price target 1y delta [percentage points (12.5 means 12.5%)].'),
    'price_target_average': FieldInfo('price_target_average', FieldType.NUMBER, 'Average analyst price target.'),
    'price_target_high': FieldInfo('price_target_high', FieldType.NUMBER, 'Price target high.'),
    'price_target_low': FieldInfo('price_target_low', FieldType.NUMBER, 'Price target low.'),
    'price_target_median': FieldInfo('price_target_median', FieldType.NUMBER, 'Price target median.'),
    'price_to_cash_f_operating_activities_ttm': FieldInfo('price_to_cash_f_operating_activities_ttm', FieldType.NUMBER, 'Price to cash from operating activities (trailing twelve months).'),
    'price_to_cash_ratio': FieldInfo('price_to_cash_ratio', FieldType.NUMBER, 'Price to cash ratio.'),
    'price_to_working_capital_fq': FieldInfo('price_to_working_capital_fq', FieldType.NUMBER, 'Price to working capital (fiscal quarter).'),
    'pricescale': FieldInfo('pricescale', FieldType.NUMBER, 'Pricescale.'),
    'provider-id': FieldInfo('provider-id', FieldType.TEXT, 'Provider ID.', values=('ice',)),
    'quick_ratio': FieldInfo('quick_ratio', FieldType.NUMBER, 'Quick ratio.'),
    'quick_ratio_current': FieldInfo('quick_ratio_current', FieldType.NUMBER, 'Quick ratio current.'),
    'quick_ratio_fq': FieldInfo('quick_ratio_fq', FieldType.NUMBER, 'Quick ratio, latest fiscal quarter.'),
    'quick_ratio_fy': FieldInfo('quick_ratio_fy', FieldType.NUMBER, 'Quick ratio (fiscal year).'),
    'rates_cf': FieldInfo('rates_cf', FieldType.MAP, 'Rates cf.'),
    'rates_current': FieldInfo('rates_current', FieldType.MAP, 'Rates current.'),
    'rates_dividend_recent': FieldInfo('rates_dividend_recent', FieldType.MAP, 'Rates dividend recent.'),
    'rates_dividend_upcoming': FieldInfo('rates_dividend_upcoming', FieldType.MAP, 'Rates dividend upcoming.'),
    'rates_earnings_fq': FieldInfo('rates_earnings_fq', FieldType.MAP, 'Rates earnings (fiscal quarter).'),
    'rates_earnings_next_fq': FieldInfo('rates_earnings_next_fq', FieldType.MAP, 'Rates earnings next (fiscal quarter).'),
    'rates_fh': FieldInfo('rates_fh', FieldType.MAP, 'Rates (fiscal half-year).'),
    'rates_fq': FieldInfo('rates_fq', FieldType.MAP, 'Rates (fiscal quarter).'),
    'rates_fy': FieldInfo('rates_fy', FieldType.MAP, 'Rates (fiscal year).'),
    'rates_mc': FieldInfo('rates_mc', FieldType.MAP, 'Rates mc.'),
    'rates_pt': FieldInfo('rates_pt', FieldType.MAP, 'Rates pt.'),
    'rates_time_series': FieldInfo('rates_time_series', FieldType.MAP, 'Rates time series.'),
    'rates_ttm': FieldInfo('rates_ttm', FieldType.MAP, 'Rates (trailing twelve months).'),
    'receivables_turnover_fq': FieldInfo('receivables_turnover_fq', FieldType.NUMBER, 'Receivables turnover (fiscal quarter).'),
    'receivables_turnover_fy': FieldInfo('receivables_turnover_fy', FieldType.NUMBER, 'Receivables turnover (fiscal year).'),
    'recommendation_buy': FieldInfo('recommendation_buy', FieldType.NUMBER, 'Recommendation buy.'),
    'recommendation_hold': FieldInfo('recommendation_hold', FieldType.NUMBER, 'Recommendation hold.'),
    'recommendation_mark': FieldInfo('recommendation_mark', FieldType.NUMBER, 'Analyst consensus rating: 1=Strong Buy .. 3=Hold .. 5=Strong Sell.'),
    'recommendation_over': FieldInfo('recommendation_over', FieldType.NUMBER, 'Recommendation over.'),
    'recommendation_sell': FieldInfo('recommendation_sell', FieldType.NUMBER, 'Recommendation sell.'),
    'recommendation_total': FieldInfo('recommendation_total', FieldType.NUMBER, 'Number of analyst ratings contributing to the consensus.'),
    'recommendation_under': FieldInfo('recommendation_under', FieldType.NUMBER, 'Recommendation under.'),
    'relative_volume': FieldInfo('relative_volume', FieldType.NUMBER, 'Relative volume.'),
    'relative_volume_10d_calc': FieldInfo('relative_volume_10d_calc', FieldType.NUMBER, 'Volume / 10-day average volume (1.0 = normal, >1 elevated).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'research_and_dev_estimate_fh': FieldInfo('research_and_dev_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'research_and_dev_estimate_fq': FieldInfo('research_and_dev_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'research_and_dev_estimate_fy': FieldInfo('research_and_dev_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'research_and_dev_estimate_ntm': FieldInfo('research_and_dev_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation estimate ntm [monetary value in fundamental/fund currency].'),
    'research_and_dev_fh': FieldInfo('research_and_dev_fh', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'research_and_dev_fq': FieldInfo('research_and_dev_fq', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'research_and_dev_fy': FieldInfo('research_and_dev_fy', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation (fiscal year) [monetary value in fundamental/fund currency].'),
    'research_and_dev_per_employee_fy': FieldInfo('research_and_dev_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'research_and_dev_ratio_fy': FieldInfo('research_and_dev_ratio_fy', FieldType.PERCENT, 'Research and deviation ratio (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'research_and_dev_ratio_ttm': FieldInfo('research_and_dev_ratio_ttm', FieldType.PERCENT, 'Research and deviation ratio (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'research_and_dev_ttm': FieldInfo('research_and_dev_ttm', FieldType.FUNDAMENTAL_PRICE, 'Research and deviation (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'return_of_invested_capital_percent_ttm': FieldInfo('return_of_invested_capital_percent_ttm', FieldType.PERCENT, 'Return of invested capital percent (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'return_on_assets': FieldInfo('return_on_assets', FieldType.PERCENT, 'Return on assets [percentage points (12.5 means 12.5%)].'),
    'return_on_assets_fq': FieldInfo('return_on_assets_fq', FieldType.PERCENT, 'Return on assets, percent, latest fiscal quarter.'),
    'return_on_assets_fy': FieldInfo('return_on_assets_fy', FieldType.PERCENT, 'Return on assets (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_capital_employed_fq': FieldInfo('return_on_capital_employed_fq', FieldType.PERCENT, 'Return on capital employed (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'return_on_capital_employed_fy': FieldInfo('return_on_capital_employed_fy', FieldType.PERCENT, 'Return on capital employed (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_common_equity_fy': FieldInfo('return_on_common_equity_fy', FieldType.PERCENT, 'Return on common equity (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_common_equity_ttm': FieldInfo('return_on_common_equity_ttm', FieldType.PERCENT, 'Return on common equity (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'return_on_equity': FieldInfo('return_on_equity', FieldType.PERCENT, 'Return on equity [percentage points (12.5 means 12.5%)].'),
    'return_on_equity_adjust_to_book_fy': FieldInfo('return_on_equity_adjust_to_book_fy', FieldType.PERCENT, 'Return on equity adjust to book (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_equity_adjust_to_book_ttm': FieldInfo('return_on_equity_adjust_to_book_ttm', FieldType.PERCENT, 'Return on equity adjust to book (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'return_on_equity_fq': FieldInfo('return_on_equity_fq', FieldType.PERCENT, 'Return on equity, percent, latest fiscal quarter.'),
    'return_on_equity_fy': FieldInfo('return_on_equity_fy', FieldType.PERCENT, 'Return on equity (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_invested_capital': FieldInfo('return_on_invested_capital', FieldType.PERCENT, 'Return on invested capital [percentage points (12.5 means 12.5%)].'),
    'return_on_invested_capital_fq': FieldInfo('return_on_invested_capital_fq', FieldType.PERCENT, 'Return on invested capital, percent, latest fiscal quarter.'),
    'return_on_invested_capital_fy': FieldInfo('return_on_invested_capital_fy', FieldType.PERCENT, 'Return on invested capital (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_tang_assets_fq': FieldInfo('return_on_tang_assets_fq', FieldType.PERCENT, 'Return on tang assets (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'return_on_tang_assets_fy': FieldInfo('return_on_tang_assets_fy', FieldType.PERCENT, 'Return on tang assets (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_tang_equity_fq': FieldInfo('return_on_tang_equity_fq', FieldType.PERCENT, 'Return on tang equity (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'return_on_tang_equity_fy': FieldInfo('return_on_tang_equity_fy', FieldType.PERCENT, 'Return on tang equity (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'return_on_total_capital_fq': FieldInfo('return_on_total_capital_fq', FieldType.PERCENT, 'Return on total capital (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'return_on_total_capital_fy': FieldInfo('return_on_total_capital_fy', FieldType.PERCENT, 'Return on total capital (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'revenue_estimate_ntm': FieldInfo('revenue_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Revenue estimate ntm [monetary value in fundamental/fund currency].'),
    'revenue_forecast_fq': FieldInfo('revenue_forecast_fq', FieldType.FUNDAMENTAL_PRICE, 'Revenue forecast (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'revenue_forecast_next_fh': FieldInfo('revenue_forecast_next_fh', FieldType.FUNDAMENTAL_PRICE, 'Revenue forecast next (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'revenue_forecast_next_fq': FieldInfo('revenue_forecast_next_fq', FieldType.FUNDAMENTAL_PRICE, 'Revenue forecast next (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'revenue_forecast_next_fy': FieldInfo('revenue_forecast_next_fy', FieldType.FUNDAMENTAL_PRICE, 'Revenue forecast next (fiscal year) [monetary value in fundamental/fund currency].'),
    'revenue_fq': FieldInfo('revenue_fq', FieldType.FUNDAMENTAL_PRICE, 'Revenue (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'revenue_per_employee': FieldInfo('revenue_per_employee', FieldType.FUNDAMENTAL_PRICE, 'Revenue per employee [monetary value in fundamental/fund currency].'),
    'revenue_per_employee_fy': FieldInfo('revenue_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Revenue per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'revenue_per_share_current': FieldInfo('revenue_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Revenue per share current [monetary value in fundamental/fund currency].'),
    'revenue_per_share_fh': FieldInfo('revenue_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Revenue per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'revenue_per_share_fq': FieldInfo('revenue_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Revenue per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'revenue_per_share_fy': FieldInfo('revenue_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Revenue per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'revenue_per_share_ttm': FieldInfo('revenue_per_share_ttm', FieldType.FUNDAMENTAL_PRICE, 'Revenue per share (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'revenue_surprise_fq': FieldInfo('revenue_surprise_fq', FieldType.FUNDAMENTAL_PRICE, 'Revenue surprise (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'revenue_surprise_percent_fq': FieldInfo('revenue_surprise_percent_fq', FieldType.PERCENT, 'Revenue surprise percent (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'revenues_fq_h': FieldInfo('revenues_fq_h', FieldType.INTERFACE, 'Revenues (fiscal quarter) (historical series).'),
    'rtc': FieldInfo('rtc', FieldType.PRICE, 'Rtc.'),
    'sector': FieldInfo('sector', FieldType.TEXT, 'FactSet economic sector.', values=('Commercial Services', 'Communications', 'Consumer Durables', 'Consumer Non-Durables', 'Consumer Services', 'Distribution Services', 'Electronic Technology', 'Energy Minerals', 'Finance', 'Government', 'Health Services', 'Health Technology', 'Industrial Services', 'Miscellaneous', 'Non-Energy Minerals', 'Process Industries', 'Producer Manufacturing', 'Retail Trade', 'Technology Services', 'Transportation', 'Utilities')),
    'selection_criteria': FieldInfo('selection_criteria', FieldType.TEXT, 'Selection criteria.', values=('1', '10', '12', '13', '16', '17', '2', '20', '23', '24', '25', '26', '27', '28', '29', '3', '31', '32', '34', '35', '36', '38', '39', '40', '43', '45', '5', '6', '8', '9')),
    'sell_gen_admin_exp_other_fy': FieldInfo('sell_gen_admin_exp_other_fy', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp other (fiscal year) [monetary value in fundamental/fund currency].'),
    'sell_gen_admin_exp_other_ratio_fy': FieldInfo('sell_gen_admin_exp_other_ratio_fy', FieldType.PERCENT, 'Sell gen admin exp other ratio (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'sell_gen_admin_exp_other_ratio_ttm': FieldInfo('sell_gen_admin_exp_other_ratio_ttm', FieldType.PERCENT, 'Sell gen admin exp other ratio (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'sell_gen_admin_exp_other_ttm': FieldInfo('sell_gen_admin_exp_other_ttm', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp other (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'sell_gen_admin_exp_total_estimate_fh': FieldInfo('sell_gen_admin_exp_total_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp total estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'sell_gen_admin_exp_total_estimate_fq': FieldInfo('sell_gen_admin_exp_total_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp total estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'sell_gen_admin_exp_total_estimate_fy': FieldInfo('sell_gen_admin_exp_total_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp total estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'sell_gen_admin_exp_total_estimate_ntm': FieldInfo('sell_gen_admin_exp_total_estimate_ntm', FieldType.FUNDAMENTAL_PRICE, 'Sell gen admin exp total estimate ntm [monetary value in fundamental/fund currency].'),
    'share_buyback_ratio_fq': FieldInfo('share_buyback_ratio_fq', FieldType.PERCENT, 'Share buyback ratio (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'share_buyback_ratio_fy': FieldInfo('share_buyback_ratio_fy', FieldType.PERCENT, 'Share buyback ratio (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'shares_outstanding': FieldInfo('shares_outstanding', FieldType.NUMBER, 'Shares outstanding.'),
    'short_term_debt_fq': FieldInfo('short_term_debt_fq', FieldType.FUNDAMENTAL_PRICE, 'Short term debt (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'short_term_debt_fy': FieldInfo('short_term_debt_fy', FieldType.FUNDAMENTAL_PRICE, 'Short term debt (fiscal year) [monetary value in fundamental/fund currency].'),
    'shrhldrs_equity_fq': FieldInfo('shrhldrs_equity_fq', FieldType.FUNDAMENTAL_PRICE, 'Shrhldrs equity (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'shrhldrs_equity_fy': FieldInfo('shrhldrs_equity_fy', FieldType.FUNDAMENTAL_PRICE, 'Shrhldrs equity (fiscal year) [monetary value in fundamental/fund currency].'),
    'shrhldrs_equity_to_total_assets_fq': FieldInfo('shrhldrs_equity_to_total_assets_fq', FieldType.NUMBER, 'Shrhldrs equity to total assets (fiscal quarter).'),
    'shrhldrs_equity_to_total_assets_fy': FieldInfo('shrhldrs_equity_to_total_assets_fy', FieldType.NUMBER, 'Shrhldrs equity to total assets (fiscal year).'),
    'sloan_ratio_fy': FieldInfo('sloan_ratio_fy', FieldType.PERCENT, 'Sloan ratio (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'sloan_ratio_ttm': FieldInfo('sloan_ratio_ttm', FieldType.PERCENT, 'Sloan ratio (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'source-logoid': FieldInfo('source-logoid', FieldType.TEXT, 'Source logoid.', values=('source/AMEX', 'source/CBOE', 'source/NASDAQ', 'source/NYSE', 'source/OTC')),
    'strategy': FieldInfo('strategy', FieldType.TEXT, 'Strategy.', values=('1', '13', '14', '15', '16', '17', '18', '19', '2', '20', '22', '23', '24', '25', '26', '27', '28', '30', '31', '32', '33', '34', '35', '4', '41', '48', '49', '5')),
    'submarket': FieldInfo('submarket', FieldType.TEXT, 'Sub-market segment (e.g. OTC tier).', values=('', 'OTCQB', 'OTCQX', 'PINK')),
    'subsessions': FieldInfo('subsessions', FieldType.INTERFACE, 'Subsessions.'),
    'subtype': FieldInfo('subtype', FieldType.TEXT, 'Subtype.', values=('', 'closedend', 'common', 'etf', 'preferred', 'reit', 'unit')),
    'sum_for_enterprise_value': FieldInfo('sum_for_enterprise_value', FieldType.FUNDAMENTAL_PRICE, 'Sum for enterprise value [monetary value in fundamental/fund currency].'),
    'sustainable_growth_rate_fy': FieldInfo('sustainable_growth_rate_fy', FieldType.PERCENT, 'Sustainable growth rate (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'sustainable_growth_rate_ttm': FieldInfo('sustainable_growth_rate_ttm', FieldType.PERCENT, 'Sustainable growth rate (trailing twelve months) [percentage points (12.5 means 12.5%)].'),
    'time': FieldInfo('time', FieldType.TIME, 'Time [UNIX timestamp (seconds)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'time_business_day': FieldInfo('time_business_day', FieldType.NUMBER, 'Time business day.'),
    'tobin_q_ratio_fq': FieldInfo('tobin_q_ratio_fq', FieldType.NUMBER, 'Tobin q ratio (fiscal quarter).'),
    'tobin_q_ratio_fy': FieldInfo('tobin_q_ratio_fy', FieldType.NUMBER, 'Tobin q ratio (fiscal year).'),
    'top_revenue_country_code': FieldInfo('top_revenue_country_code', FieldType.TEXT, 'Top revenue country code.', values=('AE', 'AR', 'AT', 'AU', 'AZ', 'BD', 'BE', 'BF', 'BG', 'BM', 'BO', 'BR', 'BW', 'CA', 'CD', 'CG', 'CH', 'CI', 'CL', 'CM', 'CN', 'CO', 'CR', 'CZ', 'DE', 'DK', 'DO', 'DZ', 'EC', 'EG', 'ES', 'FI', 'FJ', 'FR', 'GA', 'GB', 'GE', 'GH', 'GL', 'GR', 'GT', 'GY', 'HK', 'HR', 'HT', 'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IS', 'IT', 'JE', 'JP', 'KG', 'KH', 'KR', 'KY', 'KZ', 'LK', 'LT', 'LU', 'MA', 'MC', 'MG', 'MH', 'ML', 'MN', 'MO', 'MT', 'MX', 'MY', 'NA', 'NG', 'NI', 'NL', 'NO', 'NZ', 'PE', 'PG', 'PH', 'PK', 'PL', 'PR', 'PT', 'QA', 'RO', 'RU', 'SA', 'SE', 'SG', 'TH', 'TR', 'TT', 'TW', 'TZ', 'UA', 'US', 'UZ', 'VG', 'VN', 'ZA', 'ZM', 'ZW')),
    'total_assets': FieldInfo('total_assets', FieldType.FUNDAMENTAL_PRICE, 'Total assets [monetary value in fundamental/fund currency].'),
    'total_assets_estimate_fh': FieldInfo('total_assets_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Total assets estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'total_assets_estimate_fq': FieldInfo('total_assets_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Total assets estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_assets_estimate_fy': FieldInfo('total_assets_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Total assets estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_assets_fq': FieldInfo('total_assets_fq', FieldType.FUNDAMENTAL_PRICE, 'Total assets (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_assets_fq_h': FieldInfo('total_assets_fq_h', FieldType.NUM_SLICE, 'Total assets (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'total_assets_fy': FieldInfo('total_assets_fy', FieldType.FUNDAMENTAL_PRICE, 'Total assets (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_assets_fy_h': FieldInfo('total_assets_fy_h', FieldType.NUM_SLICE, 'Total assets (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'total_assets_per_employee_fy': FieldInfo('total_assets_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Total assets per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_assets_qoq_growth_fq': FieldInfo('total_assets_qoq_growth_fq', FieldType.PERCENT, 'Total assets quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_assets_to_equity_fq': FieldInfo('total_assets_to_equity_fq', FieldType.NUMBER, 'Total assets to equity (fiscal quarter).'),
    'total_assets_to_equity_fy': FieldInfo('total_assets_to_equity_fy', FieldType.NUMBER, 'Total assets to equity (fiscal year).'),
    'total_assets_yoy_growth_fq': FieldInfo('total_assets_yoy_growth_fq', FieldType.PERCENT, 'Total assets year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_assets_yoy_growth_fy': FieldInfo('total_assets_yoy_growth_fy', FieldType.PERCENT, 'Total assets year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'total_capital': FieldInfo('total_capital', FieldType.NUMBER, 'Total capital.'),
    'total_cash_dividends_paid_fh': FieldInfo('total_cash_dividends_paid_fh', FieldType.FUNDAMENTAL_PRICE, 'Total cash dividends paid (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'total_cash_dividends_paid_fq': FieldInfo('total_cash_dividends_paid_fq', FieldType.FUNDAMENTAL_PRICE, 'Total cash dividends paid (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_cash_dividends_paid_fy': FieldInfo('total_cash_dividends_paid_fy', FieldType.FUNDAMENTAL_PRICE, 'Total cash dividends paid (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_cash_dividends_paid_ttm': FieldInfo('total_cash_dividends_paid_ttm', FieldType.FUNDAMENTAL_PRICE, 'Total cash dividends paid (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'total_current_assets': FieldInfo('total_current_assets', FieldType.FUNDAMENTAL_PRICE, 'Total current assets [monetary value in fundamental/fund currency].'),
    'total_current_assets_fq': FieldInfo('total_current_assets_fq', FieldType.FUNDAMENTAL_PRICE, 'Total current assets (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_current_assets_fy': FieldInfo('total_current_assets_fy', FieldType.FUNDAMENTAL_PRICE, 'Total current assets (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_current_liabilities_fq': FieldInfo('total_current_liabilities_fq', FieldType.FUNDAMENTAL_PRICE, 'Total current liabilities (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_current_liabilities_fy': FieldInfo('total_current_liabilities_fy', FieldType.FUNDAMENTAL_PRICE, 'Total current liabilities (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_debt': FieldInfo('total_debt', FieldType.FUNDAMENTAL_PRICE, 'Total debt [monetary value in fundamental/fund currency].'),
    'total_debt_estimate_fh': FieldInfo('total_debt_estimate_fh', FieldType.FUNDAMENTAL_PRICE, 'Total debt estimate (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'total_debt_estimate_fq': FieldInfo('total_debt_estimate_fq', FieldType.FUNDAMENTAL_PRICE, 'Total debt estimate (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_debt_estimate_fy': FieldInfo('total_debt_estimate_fy', FieldType.FUNDAMENTAL_PRICE, 'Total debt estimate (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_debt_fq': FieldInfo('total_debt_fq', FieldType.FUNDAMENTAL_PRICE, 'Total debt (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_debt_fq_h': FieldInfo('total_debt_fq_h', FieldType.NUM_SLICE, 'Total debt (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'total_debt_fy': FieldInfo('total_debt_fy', FieldType.FUNDAMENTAL_PRICE, 'Total debt (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_debt_fy_h': FieldInfo('total_debt_fy_h', FieldType.NUM_SLICE, 'Total debt (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'total_debt_per_employee_fy': FieldInfo('total_debt_per_employee_fy', FieldType.FUNDAMENTAL_PRICE, 'Total debt per employee (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_debt_per_share_current': FieldInfo('total_debt_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Total debt per share current [monetary value in fundamental/fund currency].'),
    'total_debt_per_share_fh': FieldInfo('total_debt_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Total debt per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'total_debt_per_share_fq': FieldInfo('total_debt_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Total debt per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_debt_per_share_fy': FieldInfo('total_debt_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Total debt per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_debt_qoq_growth_fq': FieldInfo('total_debt_qoq_growth_fq', FieldType.PERCENT, 'Total debt quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_debt_to_capital_fq': FieldInfo('total_debt_to_capital_fq', FieldType.NUMBER, 'Total debt to capital (fiscal quarter).'),
    'total_debt_to_capital_fy': FieldInfo('total_debt_to_capital_fy', FieldType.NUMBER, 'Total debt to capital (fiscal year).'),
    'total_debt_to_ebitda_fq': FieldInfo('total_debt_to_ebitda_fq', FieldType.NUMBER, 'Total debt to EBITDA (fiscal quarter).'),
    'total_debt_to_ebitda_fy': FieldInfo('total_debt_to_ebitda_fy', FieldType.NUMBER, 'Total debt to EBITDA (fiscal year).'),
    'total_debt_yoy_growth_fq': FieldInfo('total_debt_yoy_growth_fq', FieldType.PERCENT, 'Total debt year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_debt_yoy_growth_fy': FieldInfo('total_debt_yoy_growth_fy', FieldType.PERCENT, 'Total debt year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'total_equity_fq': FieldInfo('total_equity_fq', FieldType.FUNDAMENTAL_PRICE, 'Total equity (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_equity_fy': FieldInfo('total_equity_fy', FieldType.FUNDAMENTAL_PRICE, 'Total equity (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_liabilities_fq': FieldInfo('total_liabilities_fq', FieldType.FUNDAMENTAL_PRICE, 'Total liabilities (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_liabilities_fy': FieldInfo('total_liabilities_fy', FieldType.FUNDAMENTAL_PRICE, 'Total liabilities (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_revenue': FieldInfo('total_revenue', FieldType.FUNDAMENTAL_PRICE, 'Total revenue [monetary value in fundamental/fund currency].'),
    'total_revenue_5y_growth_fy': FieldInfo('total_revenue_5y_growth_fy', FieldType.PERCENT, 'Total revenue 5y growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'total_revenue_cagr_5y': FieldInfo('total_revenue_cagr_5y', FieldType.PERCENT, 'Total revenue CAGR 5y [percentage points (12.5 means 12.5%)].'),
    'total_revenue_fh': FieldInfo('total_revenue_fh', FieldType.FUNDAMENTAL_PRICE, 'Total revenue (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'total_revenue_fq': FieldInfo('total_revenue_fq', FieldType.FUNDAMENTAL_PRICE, 'Total revenue (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'total_revenue_fq_h': FieldInfo('total_revenue_fq_h', FieldType.NUM_SLICE, 'Total revenue (fiscal quarter) (historical series) [array of numbers (per-period history)].'),
    'total_revenue_fy': FieldInfo('total_revenue_fy', FieldType.FUNDAMENTAL_PRICE, 'Total revenue (fiscal year) [monetary value in fundamental/fund currency].'),
    'total_revenue_fy_h': FieldInfo('total_revenue_fy_h', FieldType.NUM_SLICE, 'Total revenue (fiscal year) (historical series) [array of numbers (per-period history)].'),
    'total_revenue_qoq_growth_fq': FieldInfo('total_revenue_qoq_growth_fq', FieldType.PERCENT, 'Total revenue quarter-over-quarter growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_revenue_ttm': FieldInfo('total_revenue_ttm', FieldType.FUNDAMENTAL_PRICE, 'Total revenue (trailing twelve months) [monetary value in fundamental/fund currency].'),
    'total_revenue_ttm_h': FieldInfo('total_revenue_ttm_h', FieldType.NUM_SLICE, 'Total revenue (trailing twelve months) (historical series) [array of numbers (per-period history)].'),
    'total_revenue_yoy_growth_fq': FieldInfo('total_revenue_yoy_growth_fq', FieldType.PERCENT, 'Total revenue year-over-year growth (fiscal quarter) [percentage points (12.5 means 12.5%)].'),
    'total_revenue_yoy_growth_fy': FieldInfo('total_revenue_yoy_growth_fy', FieldType.PERCENT, 'Total revenue year-over-year growth (fiscal year) [percentage points (12.5 means 12.5%)].'),
    'total_revenue_yoy_growth_ttm': FieldInfo('total_revenue_yoy_growth_ttm', FieldType.PERCENT, 'Revenue growth TTM year-over-year, percent.'),
    'total_shares_outstanding': FieldInfo('total_shares_outstanding', FieldType.NUMBER, 'Total shares outstanding.'),
    'total_shares_outstanding_calculated': FieldInfo('total_shares_outstanding_calculated', FieldType.NUMBER, 'Total shares outstanding calculated.'),
    'total_shares_outstanding_current': FieldInfo('total_shares_outstanding_current', FieldType.NUMBER, 'Shares outstanding, current.'),
    'total_shares_outstanding_fundamental': FieldInfo('total_shares_outstanding_fundamental', FieldType.NUMBER, 'Total shares outstanding fundamental.'),
    'transparent_holding_flag': FieldInfo('transparent_holding_flag', FieldType.TEXT, 'Transparent holding flag.', values=('0', '1')),
    'type': FieldInfo('type', FieldType.TEXT, 'Instrument type.', values=('dr', 'fund', 'stock', 'structured')),
    'typespecs': FieldInfo('typespecs', FieldType.SET, 'Type qualifiers (array), e.g. common, preferred, etf, reit, closedend.', values=('', 'closedend', 'common', 'etf', 'preferred', 'reit', 'unit')),
    'ucits_compliant_flag': FieldInfo('ucits_compliant_flag', FieldType.TEXT, "UCITS compliance: '1' = compliant, '0' = not.", values=('0', '1')),
    'update-time': FieldInfo('update-time', FieldType.NUMBER, 'Update time.'),
    'update_mode': FieldInfo('update_mode', FieldType.TEXT, 'Data update mode for the session, e.g. streaming or delayed_streaming_900.', values=('streaming',), timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'update_time': FieldInfo('update_time', FieldType.TIME, 'Update time [UNIX timestamp (seconds)].'),
    'volume': FieldInfo('volume', FieldType.NUMBER, 'Session volume (shares/contracts).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'volume_change': FieldInfo('volume_change', FieldType.PERCENT, 'Volume change [percentage points (12.5 means 12.5%)].', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'volume_change_abs': FieldInfo('volume_change_abs', FieldType.NUMBER, 'Volume change (absolute).', timeframes=('1', '5', '15', '30', '60', '120', '240', '1W', '1M')),
    'weight_top_10': FieldInfo('weight_top_10', FieldType.PERCENT, 'Weight top (10) [percentage points (12.5 means 12.5%)].'),
    'weight_top_25': FieldInfo('weight_top_25', FieldType.PERCENT, 'Weight top (25) [percentage points (12.5 means 12.5%)].'),
    'weight_top_50': FieldInfo('weight_top_50', FieldType.PERCENT, 'Weight top (50) [percentage points (12.5 means 12.5%)].'),
    'weighting_scheme': FieldInfo('weighting_scheme', FieldType.TEXT, "Index weighting scheme (internal id; use 'weighting_scheme.tr' for the readable label).", values=('1', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '22', '25', '3', '4', '5', '6', '7', '8', '9')),
    'working_capital_fq': FieldInfo('working_capital_fq', FieldType.FUNDAMENTAL_PRICE, 'Working capital (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'working_capital_per_share_current': FieldInfo('working_capital_per_share_current', FieldType.FUNDAMENTAL_PRICE, 'Working capital per share current [monetary value in fundamental/fund currency].'),
    'working_capital_per_share_fh': FieldInfo('working_capital_per_share_fh', FieldType.FUNDAMENTAL_PRICE, 'Working capital per share (fiscal half-year) [monetary value in fundamental/fund currency].'),
    'working_capital_per_share_fq': FieldInfo('working_capital_per_share_fq', FieldType.FUNDAMENTAL_PRICE, 'Working capital per share (fiscal quarter) [monetary value in fundamental/fund currency].'),
    'working_capital_per_share_fy': FieldInfo('working_capital_per_share_fy', FieldType.FUNDAMENTAL_PRICE, 'Working capital per share (fiscal year) [monetary value in fundamental/fund currency].'),
    'yield_recent': FieldInfo('yield_recent', FieldType.NUMBER, 'Yield recent.'),
    'yield_upcoming': FieldInfo('yield_upcoming', FieldType.NUMBER, 'Yield upcoming.'),
    'zmijewski_score_fy': FieldInfo('zmijewski_score_fy', FieldType.NUMBER, 'Zmijewski score (fiscal year).'),
    'zmijewski_score_ttm': FieldInfo('zmijewski_score_ttm', FieldType.NUMBER, 'Zmijewski score (trailing twelve months).'),
}
