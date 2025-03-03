"""
Technical Analysis Advanced Indicators Module.

This package provides various advanced indicators used in financial market analysis.
Each indicator function takes a pandas DataFrame containing OHLCV data and 
returns calculated indicator values.

Available indicators:
- Elliott Wave (Larger Trend, Major Waves, Corrective Waves, Minor Waves)
- Hurst Exponent
- Renko Chart
- Standard Deviation Channel
- Adaptive Moving Average (AMA)
- Average True Range Percentage (ATR%)
- Alpha-Beta Ratio
- Linear Regression Intercept (LRI)
- Arms' Accumulation/Distribution Index (ADI)
- Envelope Bands
- Polarized Fractal Efficiency (PFE)
- ERGO Indicator
- Chande Forecast Oscillator (CFO)
- Parabolic SAR Downtrend
- Elder Force Index
- Chande Qstick Indicator

Note:
    All functions expect a pandas DataFrame with appropriate columns for each indicator.
    See individual function docstrings for required columns.
"""

from .other import (
    larger_trend,
    major_waves,
    corrective_waves,
    minor_waves,
    elliot_wave_steps_3_4,
    elliot_wave_steps_5_6,
    hurst_exponent,
    renko,
    std_dev_channel,
    adaptive_ma,
    atrp,
    alpha_beta_ratio,
    lri,
    arms_adi,
    envelope_bands,
    polarized_fractal_efficiency,
    ergo,
    cfo,
    parabolic_sar_down,
    elder_force_index,
    chande_qstick
)

__all__ = [
    "larger_trend",
    "major_waves",
    "corrective_waves",
    "minor_waves",
    "elliot_wave_steps_3_4",
    "elliot_wave_steps_5_6",
    "hurst_exponent",
    "renko",
    "std_dev_channel",
    "adaptive_ma",
    "atrp",
    "alpha_beta_ratio",
    "lri",
    "arms_adi",
    "envelope_bands",
    "polarized_fractal_efficiency",
    "ergo",
    "cfo",
    "parabolic_sar_down",
    "elder_force_index",
    "chande_qstick"
]