"""
backtest.py

This module contains multiple trading strategies for backtesting using the 
`backtesting` library. Each strategy implements a different technical analysis 
approach, leveraging indicators from `Technical_Analysis.Indicators`.

Classes:
    - RSIStrategy: Uses Relative Strength Index (RSI) for buy/sell signals.
    - VWAPStrategy: Uses Volume Weighted Average Price (VWAP) for entries/exits.
    - IchimokuCloudStrategy: Uses Ichimoku Cloud for trend identification.
    - BollingerBandsReversionStrategy: Uses Bollinger Bands for mean reversion.
    - MACDCrossoverStrategy: Uses MACD crossovers for trading signals.
    - ElderRayIndexStrategy: Uses the Elder Ray Index to evaluate bullish/bearish trends.
    - MovingAverageCrossoverStrategySMA: Uses simple moving average crossovers.
    - MovingAverageCrossoverStrategyEMA: Uses exponential moving average crossovers.
    - MACDRSIStrategy: Combines MACD and RSI indicators.
    - BollingerRSIStochStrategy: Combines Bollinger Bands, RSI, and Stochastic Oscillator.
    - BollingerStochasticStrategy: Uses Bollinger Bands with Stochastic Oscillator.
    
Dictionary:
    - strat_map: A dictionary mapping strategy names to their respective classes.
"""

from backtesting import Strategy
from awt_ti.Indicators.volume import ta_volume_VWAP
from awt_ti.Indicators.volatility import ta_vol_BollingerBands_Upper, ta_vol_BollingerBands_Lower
from awt_ti.Indicators.trend import *
from awt_ti.Indicators.support_resistance import *
from awt_ti.Indicators.other import *
from awt_ti.Indicators.movingAverages import ta_ma_SMA, ta_ma_EMA
from awt_ti.Indicators.trend import (
    ta_trend_IchimokuCloud,
    ta_trend_MACD, 
    ta_trend_ElderRay
)
from awt_ti.Indicators.momentum import (
    ta_mo_RSI, ta_mo_StochOscillator
)

class RSIStrategy(Strategy):
    """
    A trading strategy based on the Relative Strength Index (RSI).

    Entry:
        - Buy when RSI < 30 (oversold condition).
        - Sell when RSI > 70 (overbought condition).
    """
    def init(self):
        self.rsi = self.I(ta_mo_RSI, self.data.df, n=14)

    def next(self):
        rsi_value = self.rsi[-1]
        if rsi_value < 30:
            self.position.close()
            self.buy()
        elif rsi_value > 70:
            self.position.close()
            self.sell()


class VWAPStrategy(Strategy):
    """
    A trading strategy based on the Volume Weighted Average Price (VWAP).

    Entry:
        - Buy when price is above VWAP.
        - Sell when price is below VWAP.
    """
    def init(self):
        self.vwap = self.I(ta_volume_VWAP, self.data.df)

    def next(self):
        if self.data['Close'] > self.vwap[-1]:
            self.position.close()
            self.buy()
        else:
            self.position.close()
            self.sell()


class IchimokuCloudStrategy(Strategy):
    """
    A trading strategy based on the Ichimoku Cloud indicator.

    Entry:
        - Buy when price is above both Senkou A and Senkou B.
        - Sell when price is below both Senkou A and Senkou B.
         Returns:
        tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]: A tuple containing:
    """
    def init(self):
        self.senkouA = self.I(ta_trend_IchimokuCloud, self.data.df)
        self.senkouB = self.I(ta_trend_IchimokuCloud, self.data.df)

    def next(self):
        if self.data['Close'] > self.senkouA[-1] and self.data['Close'] > self.senkouB[-1]:
            self.position.close()
            self.buy()
        elif self.data['Close'] < self.senkouA[-1] and self.data['Close'] < self.senkouB[-1]:
            self.position.close()
            self.sell()


class BollingerBandsReversionStrategy(Strategy):
    """
    A mean reversion strategy using Bollinger Bands.

    Entry:
        - Buy when price is below the lower Bollinger Band.
        - Sell when price is above the upper Bollinger Band.
    """
    def init(self):
        self.bb_lower = self.I(ta_vol_BollingerBands_Lower, self.data.df)
        self.bb_upper = self.I(ta_vol_BollingerBands_Upper, self.data.df)

    def next(self):
        if self.data['Close'] < self.bb_lower[-1]:
            self.position.close()
            self.buy()
        elif self.data['Close'] > self.bb_upper[-1]:
            self.position.close()
            self.sell()


class MACDCrossoverStrategy(Strategy):
    """
    A trading strategy using MACD crossovers.

    Entry:
        - Buy when MACD crosses above the signal line.
        - Sell when MACD crosses below the signal line.
    """
    def init(self):
        self.macd, self.macd_signal, self.macd_hist = self.I(ta_trend_MACD, self.data.df)

    def next(self):
        if self.macd[-1] > self.macd_signal[-1]:
            self.position.close()
            self.buy()
        elif self.macd[-1] < self.macd_signal[-1]:
            self.position.close()
            self.sell()


class ElderRayIndexStrategy(Strategy):
    """
    A trading strategy based on the Elder Ray Index.

    Entry:
        - Buy when Bull Power is greater than Bear Power.
        - Sell when Bear Power is greater than Bull Power.
    """
    def init(self):
        # Elder Ray Components
        self.bull, self.bear, self.elder_ray = self.I(ta_trend_ElderRay, self.data.df)
        #self.bull = self.I(ta_trend_elderRay_BullPower, self.data.df)
        #self.bear = self.I(ta_trend_elderRay_BearPower, self.data.df)
        #self.bear = self.I(ta_trend_elderRay_BearPower, self.data.df)

    def next(self):
        if self.bull[-1] > self.bear[-1]:
            self.position.close()
            self.buy()
        elif self.bull[-1] < self.bear[-1]:
            self.position.close()
            self.sell()


class MovingAverageCrossoverStrategySMA(Strategy):
    """
    A simple moving average (SMA) crossover strategy.

    Entry:
        - Buy when the short SMA crosses above the long SMA.
        - Sell when the short SMA crosses below the long SMA.

    Attributes:
        short_window (int): Short-term moving average period.
        long_window (int): Long-term moving average period.
    """
    short_window = 25
    long_window = 50

    def init(self):
        self.short_ma = self.I(ta_ma_SMA, self.data.df, self.short_window)
        self.long_ma = self.I(ta_ma_SMA, self.data.df, self.long_window)

    def next(self):
        if self.short_ma[-1] > self.long_ma[-1]:
            self.position.close()
            self.buy()
        elif self.short_ma[-1] < self.long_ma[-1]:
            self.position.close()
            self.sell()


class MovingAverageCrossoverStrategyEMA(Strategy):
    """
    An exponential moving average (EMA) crossover strategy.

    Entry:
        - Buy when the short EMA crosses above the long EMA.
        - Sell when the short EMA crosses below the long EMA.

    Attributes:
        short_window (int): Short-term moving average period.
        long_window (int): Long-term moving average period.
    """
    short_window = 25
    long_window = 50

    def init(self):
        self.short_ma = self.I(ta_ma_EMA, self.data.df, self.short_window)
        self.long_ma = self.I(ta_ma_EMA, self.data.df, self.long_window)

    def next(self):
        if self.short_ma[-1] > self.long_ma[-1]:
            self.position.close()
            self.buy()
        elif self.short_ma[-1] < self.long_ma[-1]:
            self.position.close()
            self.sell()


class MACDRSIStrategy(Strategy):
    """
    A trading strategy combining MACD and RSI indicators.

    Entry:
        - Buy when MACD > MACD signal and RSI < 30.
        - Sell when MACD < MACD signal and RSI > 70.
    """
    def init(self):
        self.macd, self.macd_signal, self.macd_hist = self.I(ta_trend_MACD, self.data.df)
        self.rsi = self.I(ta_mo_RSI, self.data.df, n=14)

    def next(self):
        if self.macd[-1] > self.macd_signal[-1] and self.rsi[-1] < 30:
            self.position.close()
            self.buy()
        elif self.macd[-1] < self.macd_signal[-1] and self.rsi[-1] > 70:
            self.position.close()
            self.sell()


class BollingerRSIStochStrategy(Strategy):
    """
    A trading strategy combining Bollinger Bands, RSI, and Stochastic Oscillator.

    Entry:
        - Buy when price <= lower Bollinger Band, RSI < 30, and Stochastic K > Stochastic D.
        - Sell when price >= upper Bollinger Band, RSI > 70, and Stochastic K < Stochastic D.
    """
    def init(self):
        self.rsi = self.I(ta_mo_RSI, self.data.df, n=14)
        
        self.bb_lower = self.I(ta_vol_BollingerBands_Lower, self.data.df)
        self.bb_upper = self.I(ta_vol_BollingerBands_Upper, self.data.df)
        self.stoch_k, self.stoch_d = self.I(ta_mo_StochOscillator, self.data.df)

    def next(self):
        if (self.data['Close'] <= self.bb_lower[-1] and self.rsi[-1] < 30 and 
                self.stoch_k[-1] > self.stoch_d[-1]):
            self.position.close()
            self.buy()
        elif (self.data['Close'] >= self.bb_upper[-1] and self.rsi[-1] > 70 and 
                self.stoch_k[-1] < self.stoch_d[-1]):
            self.position.close()
            self.sell()


class BollingerStochasticStrategy(Strategy):
    """
    A trading strategy using Bollinger Bands and Stochastic Oscillator.

    Entry:
        - Buy when price < lower Bollinger Band and Stochastic K < 20.
        - Sell when price > upper Bollinger Band and Stochastic K > 80.
    """
    def init(self):
        self.bb_lower = self.I(ta_vol_BollingerBands_Lower, self.data.df)
        self.bb_upper = self.I(ta_vol_BollingerBands_Upper, self.data.df)
        self.stoch_k, self.stoch_d = self.I(ta_mo_StochOscillator, self.data.df)

    def next(self):
        if self.data['Close'] < self.bb_lower[-1] and self.stoch_k[-1] < 20:
            self.position.close()
            self.buy()
        elif self.data['Close'] > self.bb_upper[-1] and self.stoch_k[-1] > 80:
            self.position.close()
            self.sell()

# Strategy Mapping
strat_map = {
    'RSIStrategy': RSIStrategy,
    'VWAPStrategy': VWAPStrategy,
    'IchimokuCloudStrategy': IchimokuCloudStrategy,
    'BollingerBandsReversionStrategy': BollingerBandsReversionStrategy,
    'MACDCrossoverStrategy': MACDCrossoverStrategy,
    'ElderRayIndexStrategy': ElderRayIndexStrategy,
    'MovingAverageCrossoverStrategySMA': MovingAverageCrossoverStrategySMA,
    'MovingAverageCrossoverStrategyEMA': MovingAverageCrossoverStrategyEMA,
    'MACDRSIStrategy': MACDRSIStrategy,
    'BollingerRSIStochStrategy': BollingerRSIStochStrategy,
    'BollingerStochasticStrategy': BollingerStochasticStrategy,
}
