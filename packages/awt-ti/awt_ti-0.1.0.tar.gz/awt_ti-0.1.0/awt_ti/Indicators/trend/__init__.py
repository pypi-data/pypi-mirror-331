"""
Technical Analysis Trend Indicators Module.

This package provides various trend indicators used in financial market analysis.
Each indicator function takes a pandas DataFrame containing OHLCV data and 
returns calculated trend indicator values.

Available indicators:
- Parabolic SAR (Up/Down/Diff)
- MACD (Moving Average Convergence Divergence)
- Vortex Indicator
- Ichimoku Cloud
- Elder Ray Index
- ADX (Average Directional Index)
- ZigZag Indicator
- Know Sure Thing (KST)
- Detrended Price Oscillator (DPO)
- TRIX (Triple Exponential Moving Average)
- Aroon Indicator
- Commodity Channel Index (CCI)

Note:
    All functions expect a pandas DataFrame with at least these columns: 
    ['Open', 'High', 'Low', 'Close', 'Volume']
"""

from .trend import (
    ta_trend_ParabolicSarUp,
    ta_trend_ParabolicSarDown,
    ta_trend_ParabolicSarDiff,
    ta_trend_MACD,
    ta_trend_MACDDiff,
    ta_trend_VortexIndicator,
    ta_trend_IchimokuCloud,
    ta_trend_ElderRay,
    ta_trend_ADX,
    ta_trend_Zigzag,
    ta_trend_KST,
    ta_trend_DPO,
    ta_trend_Trix,
    ta_trend_Aroon,
    ta_trend_CCI,
    add_Trends
)

__all__ = [
    "ta_trend_ParabolicSarUp",
    "ta_trend_ParabolicSarDown",
    "ta_trend_ParabolicSarDiff",
    "ta_trend_MACD",
    "ta_trend_MACDDiff",
    "ta_trend_VortexIndicator",
    "ta_trend_IchimokuCloud",
    "ta_trend_ElderRay",
    "ta_trend_ADX",
    "ta_trend_Zigzag",
    "ta_trend_KST",
    "ta_trend_DPO",
    "ta_trend_Trix",
    "ta_trend_Aroon",
    "ta_trend_CCI",
    "add_Trends"
]
