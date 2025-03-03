"""""Technical Analysis Moving Averages Module

This module provides various moving average indicators for technical analysis,
including SMA, EMA, WMA, and other advanced variations.

Exposed Functions:
    - ta_ma_SMA: Simple Moving Average
    - ta_ma_EMA: Exponential Moving Average
    - ta_ma_WMA: Weighted Moving Average
    - ta_ma_HMA: Hull Moving Average
    - ta_ma_KAMA: Kaufman Adaptive Moving Average
    - ta_ma_T3MA: T3 Moving Average
    - ta_ma_JurikMA: Jurik Moving Average
    - ta_ma_RainbowMA: Rainbow Moving Average
    - ta_ma_AdaptiveMA: Adaptive Moving Average
    - ta_ma_ZeroLagExponentialMA: Zero-Lag Exponential Moving Average
    - ta_ma_McginleyDynamic: McGinley Dynamic Moving Average
    - ta_ma_ModifiedMa: Modified Moving Average
    - ta_ma_FourierTransformMa: Fourier Transform Moving Average
    - ta_ma_WildersMA: Wilder's Moving Average
    - ta_ma_GeometricMa: Geometric Moving Average
    - ta_ma_CenteredMa: Centered Moving Average
    - ta_ma_AlligatorMa: Alligator Moving Average
    - ta_ma_ALMA: Arnaud Legoux Moving Average
    - ta_ma_LSMA: Least Squares Moving Average
    - ta_ma_MEDMA: Median Moving Average
    - ta_ma_ZLMA: Zero-Lag Moving Average
    - ta_ma_DetrendedMA: Detrended Moving Average
    - ta_ma_VIDYA: Variable Index Dynamic Average
    - ta_ma_ChandeViDynamic: Chande Variable Index Dynamic Average
    - ta_ma_HighLowMa: High-Low Moving Average
    - ta_ma_TripleWeightedMA: Triple Weighted Moving Average
    - ta_ma_DisplacedMA: Displaced Moving Average
    - ta_ma_WildersSmoothMa: Wilder's Smoothed Moving Average
    - ta_ma_SmoothSMA: Smooth Simple Moving Average
    - ta_ma_DblSmoothEma: Double Smooth Exponential Moving Average
    - ta_ma_TripleSmoothEMA: Triple Smooth Exponential Moving Average
    - ta_ma_FourierTransformMa: Fourier Transform Moving Average
    - ta_ma_WildersSmoothMa: Wilder's Smoothed Moving Average
    - ta_ma_GeometricMa: Geometric Moving Average
    - ta_ma_CenteredMa: Centered Moving Average
    - ta_ma_AlligatorMa: Alligator Moving Average
    - ta_ma_SmoothSMA: Smooth Simple Moving Average
Example Usage:
    >>> from Technical_Analysis.Indicators.movingAverages import ta_ma_SMA
    >>> ta_ma_SMA(df, window=14)

"""

from .movingAverages import (
    ta_ma_SMA,
    ta_ma_EMA,
    ta_ma_WMA,
    ta_ma_HMA,
    ta_ma_KAMA,
    ta_ma_T3MA,
    ta_ma_JurikMA,
    ta_ma_RainbowMA,
    ta_ma_AdaptiveMA,
    ta_ma_ZeroLagExponentialMA,
    ta_ma_McginleyDynamic,
    ta_ma_ModifiedMa,
    ta_ma_FourierTransformMa,
    ta_ma_WildersMa,
    ta_ma_GeometricMa,
    ta_ma_CenteredMa,
    ta_ma_AlligatorMa,
    ta_ma_ALMA,
    ta_ma_LSMA,
    ta_ma_MEDMA,
    ta_ma_ZLMA,
    ta_ma_DetrendedMA,
    ta_ma_VIDYA,
    ta_ma_ChandeViDynamic,
    ta_ma_HighLowMa,
    butter_worth_filter,
    ta_ma_TripleWeightedMA,
    ta_ma_SmoothSMA,
    ta_ma_DoubleSmoothEma,
    ta_ma_TripleSmoothEMA,
    ta_ma_FRAMA,
    #ta_ma_ParabolicSar_Up,
    #ta_ma_ParabolicSar_Down,
    ta_ma_DisplacedMA,
    ta_ma_WildersSmoothMa,
    add_MovingAverages,
)

__all__ = [
    "ta_ma_SMA",
    "ta_ma_EMA",
    "ta_ma_WMA",
    "ta_ma_HMA",    
    "ta_ma_KAMA",
    "ta_ma_T3MA",
    "ta_ma_JurikMA",
    "ta_ma_RainbowMA",
    "ta_ma_AdaptiveMA",
    "ta_ma_ZeroLagExponentialMA",   
    "ta_ma_McginleyDynamic",
    "ta_ma_ModifiedMa",
    "ta_ma_FourierTransformMa",
    "ta_ma_WildersMa",
    "ta_ma_GeometricMa",
    "ta_ma_CenteredMa", 
    "ta_ma_AlligatorMa",
    "ta_ma_ALMA",
    "ta_ma_LSMA",
    "ta_ma_MEDMA",
    "ta_ma_ZLMA",
    "ta_ma_DetrendedMA",    
    "ta_ma_VIDYA",
    "ta_ma_ChandeViDynamic",
    "ta_ma_HighLowMa",
    "ta_ma_TripleWeightedMA",
    #"ta_ma_ParabolicSar_Up",
    #"ta_ma_ParabolicSar_Down",  
    "ta_ma_DisplacedMA",
    "ta_ma_WildersSmoothMa",    
    "ta_ma_SmoothSMA",
    "ta_ma_DoubleSmoothEma",
    "ta_ma_TripleSmoothEMA",
    "ta_ma_FourierTransformMa",
    "ta_ma_WildersSmoothMa",
    "ta_ma_GeometricMa",
    "ta_ma_CenteredMa",
    "ta_ma_AlligatorMa",
    "ta_ma_ALMA",
    "ta_ma_LSMA",
    "ta_ma_MEDMA",
    "ta_ma_ZLMA",
    "ta_ma_DetrendedMA",
    "ta_ma_VIDYA",
    "ta_ma_ChandeViDynamic",
    "ta_ma_HighLowMa",
    "ta_ma_TripleWeightedMA",
    "butter_worth_filter",
    "add_MovingAverages",
    "ta_ma_SmoothSMA",
    "ta_ma_FRAMA",
    "add_MovingAverages",
]
from .movingAverages import ta_ma_TRMA
from .movingAverages import ta_ma_VMA
from .movingAverages import ta_ma_GuppyMultipleMA
from .movingAverages import ta_ma_SSMA