"""Technical Analysis Trend Indicators.

This module implements various technical analysis trend indicators used in financial markets.
Each indicator is implemented as a function that takes a pandas DataFrame containing OHLCV data
and returns the calculated trend indicator values.

Note:
    All functions expect a pandas DataFrame with at least these columns: ['Open', 'High', 'Low', 'Close', 'Volume']
"""

import pandas as pd
import numpy as np
from awt_ti.Indicators.movingAverages.movingAverages import *

def ta_trend_ParabolicSarUp(df: pd.DataFrame, acceleration: float = 0.02, maximum: float = 0.2) -> pd.Series:
    """Calculate the Parabolic SAR (Stop And Reverse) indicator for uptrends.

    The Parabolic SAR is a technical indicator used to determine the direction of an
    asset's momentum and potential reversal points.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        acceleration (float, optional): Acceleration factor. Defaults to 0.02.
        maximum (float, optional): Maximum acceleration factor. Defaults to 0.2.

    Returns:
        pd.Series: SAR values for uptrends. Interpretation:
            - When price crosses above SAR, a buy signal is generated
            - When price crosses below SAR, a sell signal is generated
            - SAR acts as a trailing stop loss that adjusts based on price movement

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> sar_up = ta_trend_ParabolicSarUp(df)

    References:
        - https://www.investopedia.com/terms/p/parabolicindicator.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy()
        df['High_Shift'] = df['High'].shift(1)
        df['Low_Shift'] = df['Low'].shift(1)
        df['SAR'] = df['Low_Shift']
        df['EP'] = df['High']
        df['ACC'] = acceleration
        df['MAX_ACC'] = maximum
        df['Trend'] = None
        df.loc[0, 'Trend'] = 'Long'
        df.loc[1, 'Trend'] = 'Long'
        
        for i in range(2, len(df)):
            if df.loc[i - 1, 'Trend'] == 'Long':
                if df.loc[i, 'Low'] < df.loc[i - 1, 'SAR']:
                    df.loc[i, 'Trend'] = 'Short'
                    df.loc[i, 'SAR'] = df.loc[i - 1, 'EP']
                    df.loc[i, 'EP'] = df.loc[i, 'Low']
                    df.loc[i, 'ACC'] = acceleration
                else:
                    df.loc[i, 'SAR'] = df.loc[i - 1, 'SAR'] + \
                                     df.loc[i - 1, 'ACC'] * \
                                     (df.loc[i - 1, 'EP'] - df.loc[i - 1, 'SAR'])
                    df.loc[i, 'EP'] = max(df.loc[i, 'EP'], df.loc[i, 'High'])
                    df.loc[i, 'ACC'] = min(df.loc[i - 1, 'ACC'] + acceleration, maximum)
            else:
                if df.loc[i, 'High'] > df.loc[i - 1, 'SAR']:
                    df.loc[i, 'Trend'] = 'Long'
                    df.loc[i, 'SAR'] = df.loc[i - 1, 'EP']
                    df.loc[i, 'EP'] = df.loc[i, 'High']
                    df.loc[i, 'ACC'] = acceleration
                else:
                    df.loc[i, 'SAR'] = df.loc[i - 1, 'SAR'] - \
                                     df.loc[i - 1, 'ACC'] * \
                                     (df.loc[i - 1, 'SAR'] - df.loc[i - 1, 'EP'])
                    df.loc[i, 'EP'] = min(df.loc[i, 'EP'], df.loc[i, 'Low'])
                    df.loc[i, 'ACC'] = min(df.loc[i - 1, 'ACC'] + acceleration, maximum)
        
        return df['SAR']
    except Exception as e:
        raise ValueError(f"Error calculating Parabolic SAR Up: {str(e)}")

def ta_trend_ParabolicSarDown(df: pd.DataFrame, af: float = 0.02, max_af: float = 0.2) -> pd.Series:
    """Calculate the Parabolic SAR (Stop And Reverse) indicator for downtrends.

    The Parabolic SAR is a technical indicator used to determine the direction of an
    asset's momentum and potential reversal points, specifically for downtrends.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        af (float, optional): Acceleration factor. Defaults to 0.02.
        max_af (float, optional): Maximum acceleration factor. Defaults to 0.2.

    Returns:
        pd.Series: SAR values for downtrends. Interpretation:
            - When price crosses below SAR, a sell signal is generated
            - When price crosses above SAR, a buy signal is generated
            - SAR acts as a trailing stop loss that adjusts based on price movement

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> sar_down = ta_trend_ParabolicSarDown(df)

    References:
        - https://www.investopedia.com/terms/p/parabolicindicator.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        sar = high.iloc[0]  # Initialize SAR with first high value
        ep = low.iloc[0]  # Initialize EP with first low value
        af_current = af  # Initialize acceleration factor

        # Initialize lists to store the values for each day
        sar_values = [sar]
        trend_direction = [-1]  # Downwards trend
        ep_values = [ep]

        for i in range(1, len(high)):
            prev_sar = sar
            prev_ep = ep

            # If current trend is upwards, switch to downwards trend
            if trend_direction[-1] == 1:
                sar = prev_ep
                trend_direction.append(-1)
                ep = low.iloc[i]
                af_current = af
            # If current trend is downwards, continue in same direction
            else:
                sar = prev_sar + af_current * (prev_ep - prev_sar)
                if sar > high.iloc[i-1]:
                    sar = high.iloc[i-1]
                trend_direction.append(-1)
                if low.iloc[i] < ep:
                    ep = low.iloc[i]
                    af_current = min(af_current + af, max_af)

            sar_values.append(sar)
            ep_values.append(ep)

        return pd.Series(sar_values, index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating Parabolic SAR Down: {str(e)}")

def ta_trend_ParabolicSarDiff(df: pd.DataFrame, af: float = 0.02, max_af: float = 0.2) -> pd.Series:
    """Calculate the difference between Parabolic SAR Up and Down indicators.

    This function calculates the difference between the uptrend and downtrend
    Parabolic SAR values to identify potential trend strength and reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        af (float, optional): Acceleration factor. Defaults to 0.02.
        max_af (float, optional): Maximum acceleration factor. Defaults to 0.2.

    Returns:
        pd.Series: Difference between SAR Up and Down values. Interpretation:
            - Positive values indicate uptrend dominance
            - Negative values indicate downtrend dominance
            - Larger absolute values suggest stronger trends

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> sar_diff = ta_trend_ParabolicSarDiff(df)

    References:
        - https://www.investopedia.com/terms/p/parabolicindicator.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        up = ta_trend_ParabolicSarUp(df)
        down = ta_trend_ParabolicSarDown(df)
        return pd.Series([u - d for u, d in zip(up, down)], index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating Parabolic SAR Difference: {str(e)}")

def ta_trend_MACD(df: pd.DataFrame, fast_window: int = 12, slow_window: int = 26, 
                  signal_window: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Moving Average Convergence Divergence (MACD).

    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages of an asset's price.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        fast_window (int, optional): Fast EMA period. Defaults to 12.
        slow_window (int, optional): Slow EMA period. Defaults to 26.
        signal_window (int, optional): Signal line period. Defaults to 9.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - macd: MACD line (fast EMA - slow EMA)
            - signal: Signal line (EMA of MACD)
            - histogram: MACD histogram (MACD - signal)
        Interpretation:
            - MACD crossing above signal line is bullish
            - MACD crossing below signal line is bearish
            - Histogram shows momentum of price movement

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> macd, signal, hist = ta_trend_MACD(df)

    References:
        - https://www.investopedia.com/terms/m/macd.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        fast_ema = ta_ma_EMA(df, fast_window)
        slow_ema = ta_ma_EMA(df, slow_window)
        macd = pd.Series([fast - slow for fast, slow in zip(fast_ema, slow_ema)], index=df.index)
        signal = pd.Series(ta_ma_EMA(macd, signal_window), index=df.index)
        histogram = pd.Series([m - s for m, s in zip(macd, signal)], index=df.index)
        
        return macd, signal, histogram
    except Exception as e:
        raise ValueError(f"Error calculating MACD: {str(e)}")

def ta_trend_MACDDiff(df: pd.DataFrame) -> pd.Series:
    """Calculate the difference between MACD and its signal line.

    This function calculates the difference between the MACD line and its signal
    line to identify potential trend changes and momentum shifts.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices

    Returns:
        pd.Series: MACD difference values. Interpretation:
            - Positive values indicate bullish momentum
            - Negative values indicate bearish momentum
            - Crossing zero line may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> macd_diff = ta_trend_MACDDiff(df)

    References:
        - https://www.investopedia.com/terms/m/macd.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        macd, signal, _ = ta_trend_MACD(df)
        return pd.Series([m - s for m, s in zip(macd, signal)], index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating MACD Difference: {str(e)}")

def ta_trend_VortexIndicator(df: pd.DataFrame, n: int = 14) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Vortex Indicator.

    The Vortex Indicator consists of two oscillating lines that capture positive
    and negative trend movement. Crossovers between these lines can signal trend
    reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        n (int, optional): The lookback period. Defaults to 14.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - vi: Vortex Indicator
            - vi_pos: Positive Vortex Movement
            - vi_neg: Negative Vortex Movement
        Interpretation:
            - VI+ crossing above VI- suggests bullish trend
            - VI- crossing above VI+ suggests bearish trend
            - Larger spread between lines indicates stronger trend

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> vi, vi_pos, vi_neg = ta_trend_VortexIndicator(df)

    References:
        - https://www.investopedia.com/terms/v/vortex-indicator-vi.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high_diff = df['High'].diff()
        low_diff = df['Low'].diff().abs()
        tr = high_diff.combine(low_diff, max)
        vi_pos = high_diff * low_diff
        vi_pos = vi_pos.rolling(window=n).sum()
        vi_neg = tr.rolling(window=n).sum()
        vi = vi_pos / vi_neg
        
        return vi, vi_pos, vi_neg
    except Exception as e:
        raise ValueError(f"Error calculating Vortex Indicator: {str(e)}")

def ta_trend_IchimokuCloud(df: pd.DataFrame, tenkan_period: int = 9, 
                          kijun_period: int = 26, senkou_b_period: int = 52) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """Calculate the Ichimoku Cloud indicator.

    The Ichimoku Cloud is a comprehensive trend trading system that provides
    information about trend direction, momentum, and potential support/resistance
    levels.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        tenkan_period (int, optional): Conversion line period. Defaults to 9.
        kijun_period (int, optional): Base line period. Defaults to 26.
        senkou_b_period (int, optional): Leading Span B period. Defaults to 52.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]: A tuple containing:
            - tenkan_sen: Conversion line (short-term trend)
            - kijun_sen: Base line (medium-term trend)
            - senkou_a: Leading Span A (first cloud boundary)
            - senkou_b: Leading Span B (second cloud boundary)
            - chikou_span: Lagging Span
        Interpretation:
            - Price above cloud is bullish
            - Price below cloud is bearish
            - Cloud thickness indicates trend strength
            - Tenkan/Kijun crossovers signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> tenkan, kijun, senkou_a, senkou_b, chikou = ta_trend_IchimokuCloud(df)

    References:
        - https://www.investopedia.com/terms/i/ichimoku-cloud.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        # Compute the Tenkan-sen line
        high_prices = df['High'].rolling(tenkan_period).max()
        low_prices = df['Low'].rolling(tenkan_period).min()
        tenkan_sen = (high_prices + low_prices) / 2

        # Compute the Kijun-sen line
        high_prices = df['High'].rolling(kijun_period).max()
        low_prices = df['Low'].rolling(kijun_period).min()
        kijun_sen = (high_prices + low_prices) / 2

        # Compute the Senkou A line
        senkou_a = (tenkan_sen + kijun_sen) / 2

        # Compute the Senkou B line
        high_prices = df['High'].rolling(senkou_b_period).max()
        low_prices = df['Low'].rolling(senkou_b_period).min()
        senkou_b = (high_prices + low_prices) / 2

        # Compute the Chikou Span
        chikou_span = df['Close'].shift(-kijun_period)

        return tenkan_sen, kijun_sen, senkou_a, senkou_b.shift(kijun_period), chikou_span
    except Exception as e:
        raise ValueError(f"Error calculating Ichimoku Cloud: {str(e)}")

def ta_trend_ElderRay(df: pd.DataFrame, n_fast: int = 13, n_slow: int = 26, 
                      sma_window: int = 10) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Elder Ray indicator.

    The Elder Ray indicator measures the relative strength of bulls and bears by
    comparing buying and selling pressure to a moving average.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n_fast (int, optional): Fast period. Defaults to 13.
        n_slow (int, optional): Slow period. Defaults to 26.
        sma_window (int, optional): Smoothing period. Defaults to 10.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - bull_power: Bull Power line
            - bear_power: Bear Power line
            - elder_ray: Elder Ray value
        Interpretation:
            - Positive Bull Power with negative Bear Power is bullish
            - Negative Bull Power with positive Bear Power is bearish
            - Divergences can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> bull, bear, er = ta_trend_ElderRay(df)

    References:
        - https://www.investopedia.com/terms/e/elderray.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = df.copy()
        bull_power = df['Close'] - df['Close'].rolling(n_fast).mean()
        bear_power = -df['Close'] + df['Close'].rolling(n_slow).mean()
        elder_ray = bull_power / bear_power
        elder_ray = elder_ray.rolling(sma_window).mean()
        
        return bull_power, bear_power, elder_ray
    except Exception as e:
        raise ValueError(f"Error calculating Elder Ray: {str(e)}")

def ta_trend_ADX(df: pd.DataFrame, n: int = 14) -> pd.DataFrame:
    """Calculate the Average Directional Index (ADX).

    The ADX measures trend strength without regard to trend direction. Higher
    values indicate a stronger trend, while lower values indicate a weaker trend.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.DataFrame: DataFrame containing:
            - +DI: Positive Directional Indicator
            - -DI: Negative Directional Indicator
            - ADX: Average Directional Index
        Interpretation:
            - ADX > 25 indicates strong trend
            - ADX < 20 indicates weak trend
            - +DI > -DI suggests uptrend
            - -DI > +DI suggests downtrend

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> adx_df = ta_trend_ADX(df)

    References:
        - https://www.investopedia.com/terms/a/adx.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        close = df['Close']

        # Calculate the +DM and -DM values
        plus_DM = np.zeros(df.shape[0])
        minus_DM = np.zeros(df.shape[0])
        for i in range(1, df.shape[0]):
            if high[i] - high[i - 1] > low[i - 1] - low[i]:
                plus_DM[i] = high[i] - high[i - 1]
            if low[i - 1] - low[i] > high[i] - high[i - 1]:
                minus_DM[i] = low[i - 1] - low[i]

        # Calculate the +DI and -DI values
        plus_DI = pd.Series(plus_DM).rolling(window=n).mean()
        minus_DI = pd.Series(minus_DM).rolling(window=n).mean()

        # Calculate the DX value
        dx = 100 * np.abs((plus_DI - minus_DI) / (plus_DI + minus_DI))

        # Calculate the ADX value
        adx = dx.rolling(window=n).mean()

        # Combine results into a dataframe
        dmi = pd.concat([plus_DI, minus_DI, adx], axis=1)
        dmi.columns = ['+DI', '-DI', 'ADX']

        return dmi
    except Exception as e:
        raise ValueError(f"Error calculating ADX: {str(e)}")

def ta_trend_Zigzag(df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
    """Calculate the ZigZag indicator.

    The ZigZag indicator filters out price movements smaller than a specified
    percentage, helping identify significant price reversals and trends.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        threshold (float, optional): Minimum percentage change for a reversal. Defaults to 0.05.

    Returns:
        pd.Series: ZigZag values. Interpretation:
            - Non-zero values mark significant price pivots
            - Zero values indicate no significant change
            - Connect non-zero points to see major trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> zigzag = ta_trend_Zigzag(df)

    References:
        - https://www.investopedia.com/terms/z/zig_zag_indicator.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        zigzag = low.copy()
        
        # Initialize variables
        last_high = high.iloc[0]
        last_low = low.iloc[0]
        trend = 1  # 1 for uptrend, -1 for downtrend
        
        for i in range(1, len(high)):
            if trend == 1:  # Looking for a high
                if high[i] > last_high:
                    last_high = high[i]
                    zigzag[i] = last_high
                elif low[i] < last_low * (1 - threshold):
                    trend = -1
                    last_low = low[i]
                    zigzag[i] = last_low
            else:  # Looking for a low
                if low[i] < last_low:
                    last_low = low[i]
                    zigzag[i] = last_low
                elif high[i] > last_high * (1 + threshold):
                    trend = 1
                    last_high = high[i]
                    zigzag[i] = last_high
                    
        return zigzag
    except Exception as e:
        raise ValueError(f"Error calculating ZigZag: {str(e)}")

def ta_trend_KST(df: pd.DataFrame, r1: int = 10, r2: int = 15, r3: int = 20, r4: int = 30,
                 w1: int = 10, w2: int = 10, w3: int = 10, w4: int = 15) -> tuple[pd.Series, pd.Series]:
    """Calculate the Know Sure Thing (KST) oscillator.

    The KST is a complex momentum oscillator based on the smoothed rate of change
    of four different time periods, designed to identify major stock market cycle
    junctures.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        r1 (int, optional): First ROC period. Defaults to 10.
        r2 (int, optional): Second ROC period. Defaults to 15.
        r3 (int, optional): Third ROC period. Defaults to 20.
        r4 (int, optional): Fourth ROC period. Defaults to 30.
        w1 (int, optional): First MA period. Defaults to 10.
        w2 (int, optional): Second MA period. Defaults to 10.
        w3 (int, optional): Third MA period. Defaults to 10.
        w4 (int, optional): Fourth MA period. Defaults to 15.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - kst: KST line
            - signal: Signal line
        Interpretation:
            - KST crossing above signal line is bullish
            - KST crossing below signal line is bearish
            - Divergences can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> kst, signal = ta_trend_KST(df)

    References:
        - https://www.investopedia.com/terms/k/know-sure-thing-kst.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Calculate ROC values
        roc1 = df['Close'].pct_change(r1)
        roc2 = df['Close'].pct_change(r2)
        roc3 = df['Close'].pct_change(r3)
        roc4 = df['Close'].pct_change(r4)
        
        # Calculate smoothed ROC values
        sroc1 = roc1.rolling(w1).mean()
        sroc2 = roc2.rolling(w2).mean()
        sroc3 = roc3.rolling(w3).mean()
        sroc4 = roc4.rolling(w4).mean()
        
        # Calculate KST
        kst = 1 * sroc1 + 2 * sroc2 + 3 * sroc3 + 4 * sroc4
        signal = kst.rolling(9).mean()
        
        return kst, signal
    except Exception as e:
        raise ValueError(f"Error calculating KST: {str(e)}")

def ta_trend_DPO(df: pd.DataFrame, period: int = 20, signal_period: int = 9) -> tuple[pd.Series, pd.Series]:
    """Calculate the Detrended Price Oscillator (DPO).

    The DPO is designed to remove trend from price to better identify cycles.
    It subtracts a displaced moving average from the price.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 20.
        signal_period (int, optional): Signal line period. Defaults to 9.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - dpo: DPO line
            - signal: Signal line
        Interpretation:
            - Positive DPO indicates price above trend
            - Negative DPO indicates price below trend
            - Zero crossovers can signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> dpo, signal = ta_trend_DPO(df)

    References:
        - https://www.investopedia.com/terms/d/detrended-price-oscillator-dpo.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Calculate the displaced moving average
        shift = int(period / 2 + 1)
        ma = df['Close'].rolling(window=period).mean().shift(shift)
        
        # Calculate DPO
        dpo = df['Close'] - ma
        signal = dpo.rolling(window=signal_period).mean()
        
        return dpo, signal
    except Exception as e:
        raise ValueError(f"Error calculating DPO: {str(e)}")

def ta_trend_Trix(df: pd.DataFrame, n: int = 24) -> pd.Series:
    """Calculate the Triple Exponential Average (TRIX).

    TRIX is a momentum oscillator that shows the rate of change of a triple
    exponentially smoothed moving average, designed to filter out insignificant
    price movements.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 24.

    Returns:
        pd.Series: TRIX values. Interpretation:
            - Positive values indicate bullish momentum
            - Negative values indicate bearish momentum
            - Zero line crossovers can signal trend changes
            - Divergences can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> trix = ta_trend_Trix(df)

    References:
        - https://www.investopedia.com/terms/t/trix.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Calculate triple smoothed EMA
        ema1 = df['Close'].ewm(span=n, min_periods=n).mean()
        ema2 = ema1.ewm(span=n, min_periods=n).mean()
        ema3 = ema2.ewm(span=n, min_periods=n).mean()
        
        # Calculate TRIX
        trix = ema3.pct_change() * 100
        
        return trix
    except Exception as e:
        raise ValueError(f"Error calculating TRIX: {str(e)}")

def ta_trend_Aroon(df: pd.DataFrame, n: int = 20) -> tuple[pd.Series, pd.Series]:
    """Calculate the Aroon indicator.

    The Aroon indicator measures the time between highs and lows over a time period.
    The indicator consists of the "Aroon Up" and "Aroon Down" lines.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        n (int, optional): The lookback period. Defaults to 20.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - aroon_up: Aroon Up line
            - aroon_down: Aroon Down line
        Interpretation:
            - Aroon Up > Aroon Down suggests uptrend
            - Aroon Down > Aroon Up suggests downtrend
            - Values above 70 indicate strong trend
            - Values below 30 indicate weak trend

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> aroon_up, aroon_down = ta_trend_Aroon(df)

    References:
        - https://www.investopedia.com/terms/a/aroon.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        # Calculate Aroon Up
        rolling_high = df['High'].rolling(window=n)
        days_since_high = rolling_high.apply(lambda x: n - x.argmax())
        aroon_up = 100 * (n - days_since_high) / n

        # Calculate Aroon Down
        rolling_low = df['Low'].rolling(window=n)
        days_since_low = rolling_low.apply(lambda x: n - x.argmin())
        aroon_down = 100 * (n - days_since_low) / n

        return aroon_up, aroon_down
    except Exception as e:
        raise ValueError(f"Error calculating Aroon: {str(e)}")

def ta_trend_CCI(df: pd.DataFrame, n: int = 20) -> pd.Series:
    """Calculate the Commodity Channel Index (CCI).

    The CCI measures the current price level relative to an average price level
    over a given period, helping identify cyclical turns in commodities.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 20.

    Returns:
        pd.Series: CCI values. Interpretation:
            - Values above +100 indicate overbought
            - Values below -100 indicate oversold
            - Trend direction changes at zero line
            - Extreme readings can signal reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> cci = ta_trend_CCI(df)

    References:
        - https://www.investopedia.com/terms/c/commoditychannelindex.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        ma = tp.rolling(window=n).mean()
        md = tp.rolling(window=n).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - ma) / (0.015 * md)
        
        return cci
    except Exception as e:
        raise ValueError(f"Error calculating CCI: {str(e)}")

def add_Trends(df: pd.DataFrame) -> pd.DataFrame:
    """Add all trend indicators to the DataFrame.

    This function calculates and adds various trend-based technical indicators
    to the provided DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.DataFrame: Original DataFrame with added trend indicator columns.
        See individual indicator functions for detailed column descriptions.

    Raises:
        ValueError: If required columns are missing or if any indicator calculation fails.
    """
    try:
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        df = df.copy()

        try:
            # Parabolic SAR Indicators
            df['ta_trend_PSAR_Up'] = ta_trend_ParabolicSarUp(df)
            df['ta_trend_PSAR_Down'] = ta_trend_ParabolicSarDown(df)
            df['ta_trend_PSAR_Diff'] = ta_trend_ParabolicSarDiff(df)
        except Exception as e:
            print(f"Warning: Error calculating Parabolic SAR indicators: {str(e)}")

        try:
            # MACD Components
            macd, signal, histogram = ta_trend_MACD(df)
            df['ta_trend_MACD_Line'] = macd
            df['ta_trend_MACD_Signal'] = signal
            df['ta_trend_MACD_Histogram'] = histogram
            df['ta_trend_MACD_Diff'] = ta_trend_MACDDiff(df)
        except Exception as e:
            print(f"Warning: Error calculating MACD components: {str(e)}")

        try:
            # Vortex Indicator
            vi, vi_pos, vi_neg = ta_trend_VortexIndicator(df)
            df['ta_trend_VI'] = vi
            df['ta_trend_VI_Plus'] = vi_pos
            df['ta_trend_VI_Minus'] = vi_neg
        except Exception as e:
            print(f"Warning: Error calculating Vortex indicator: {str(e)}")

        try:
            # Ichimoku Cloud Components
            tenkan, kijun, senkou_a, senkou_b, chikou = ta_trend_IchimokuCloud(df)
            df['ta_trend_Ichimoku_Tenkan'] = tenkan
            df['ta_trend_Ichimoku_Kijun'] = kijun
            df['ta_trend_Ichimoku_SenkouA'] = senkou_a
            df['ta_trend_Ichimoku_SenkouB'] = senkou_b
            df['ta_trend_Ichimoku_Chikou'] = chikou
        except Exception as e:
            print(f"Warning: Error calculating Ichimoku Cloud components: {str(e)}")

        try:
            # Elder Ray Components
            bull_power, bear_power, elder_ray = ta_trend_ElderRay(df)
            df['ta_trend_ElderRay_Bull'] = bull_power
            df['ta_trend_ElderRay_Bear'] = bear_power
            df['ta_trend_ElderRay_Line'] = elder_ray
        except Exception as e:
            print(f"Warning: Error calculating Elder Ray components: {str(e)}")

        try:
            # ADX Components
            adx_df = ta_trend_ADX(df)
            df['ta_trend_ADX_Plus'] = adx_df['+DI']
            df['ta_trend_ADX_Minus'] = adx_df['-DI']
            df['ta_trend_ADX_Line'] = adx_df['ADX']
        except Exception as e:
            print(f"Warning: Error calculating ADX components: {str(e)}")

        try:
            # KST Components
            kst_line, kst_signal = ta_trend_KST(df)
            df['ta_trend_KST_Line'] = kst_line
            df['ta_trend_KST_Signal'] = kst_signal
            df['ta_trend_KST_Histogram'] = kst_line - kst_signal
        except Exception as e:
            print(f"Warning: Error calculating KST components: {str(e)}")

        try:
            # DPO Components
            dpo_line, dpo_signal = ta_trend_DPO(df)
            df['ta_trend_DPO_Line'] = dpo_line
            df['ta_trend_DPO_Signal'] = dpo_signal
            df['ta_trend_DPO_Histogram'] = dpo_line - dpo_signal
        except Exception as e:
            print(f"Warning: Error calculating DPO components: {str(e)}")

        try:
            # Single Value Indicators
            df['ta_trend_TRIX'] = ta_trend_Trix(df)
            df['ta_trend_CCI'] = ta_trend_CCI(df)
        except Exception as e:
            print(f"Warning: Error calculating single value indicators: {str(e)}")

        try:
            # ZigZag Indicator
            df['ta_trend_ZigZag'] = ta_trend_Zigzag(df)
        except Exception as e:
            print(f"Warning: Error calculating ZigZag indicator: {str(e)}")

        try:
            # Aroon Components
            aroon_up, aroon_down = ta_trend_Aroon(df)
            df['ta_trend_Aroon_Up'] = aroon_up
            df['ta_trend_Aroon_Down'] = aroon_down
            df['ta_trend_Aroon_Diff'] = aroon_up - aroon_down
        except Exception as e:
            print(f"Warning: Error calculating Aroon components: {str(e)}")

        return df

    except Exception as e:
        raise ValueError(f"Error adding trend indicators: {str(e)}")

# Example usage commented out for production
'''
df = yf.Ticker('AAPL').history(period='max')
print(df.columns)
df = add_Trends(df)
import plotly.express as px
fig = px.line(df)
fig.show()
'''
