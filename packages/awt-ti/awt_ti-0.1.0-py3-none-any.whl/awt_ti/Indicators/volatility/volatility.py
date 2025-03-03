"""Technical Analysis Volatility Indicators.

This module implements various technical analysis volatility indicators used in financial markets.
Each indicator is implemented as a function that takes a pandas DataFrame containing OHLCV data
and returns the calculated volatility indicator values.

Note:
    All functions expect a pandas DataFrame with at least these columns: ['Open', 'High', 'Low', 'Close', 'Volume']
"""

import pandas as pd
import numpy as np
#from Technical_Analysis.Indicators.movingAverages.movingAverages import ta_ma_SMA, ta_ma_EMA

def ta_vol_VarianceRatios(df: pd.DataFrame) -> tuple[float, float, float]:
    """Calculate the Variance Ratios.

    Computes three variance ratios that measure the distribution characteristics
    of returns: variance, skewness, and kurtosis.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices

    Returns:
        tuple[float, float, float]: A tuple containing:
            - vr_2: Variance (second moment)
            - vr_3: Skewness (third moment)
            - vr_4: Kurtosis (fourth moment)
        Interpretation:
            - vr_2: Measures spread of returns
            - vr_3: Measures asymmetry of returns
            - vr_4: Measures tail thickness of returns

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> vr2, vr3, vr4 = ta_vol_VarianceRatios(df)

    References:
        - https://www.investopedia.com/terms/v/variance.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Compute the log returns
        log_returns = np.log(df['Close']) - np.log(df['Close'].shift(1))

        # Compute the variance ratios
        vr_2 = np.var(log_returns)  # Variance
        vr_3 = np.sum((log_returns - np.mean(log_returns)) ** 3) / ((len(log_returns) - 1) * vr_2 ** (3 / 2))  # Skewness
        vr_4 = np.sum((log_returns - np.mean(log_returns)) ** 4) / ((len(log_returns) - 1) * vr_2 ** 2) - 3  # Excess Kurtosis

        return vr_2, vr_3, vr_4
    except Exception as e:
        raise ValueError(f"Error calculating Variance Ratios: {str(e)}")

def ta_vol_ChoppinessIndex(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Choppiness Index.

    The Choppiness Index measures the trendiness or choppiness of price action,
    helping identify ranging markets versus trending markets.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Choppiness Index values ranging from 0 to 100. Interpretation:
            - Values above 61.8 suggest a choppy market
            - Values below 38.2 suggest a trending market
            - Range-bound markets tend to have higher values

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> chop = ta_vol_ChoppinessIndex(df)

    References:
        - https://www.tradingview.com/support/solutions/43000501980-choppiness-index/
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        # Compute the True Range and Average True Range
        df = df.copy()
        df['TR'] = np.maximum.reduce([
            df['High'] - df['Low'],
            abs(df['High'] - df['Close'].shift(1)),
            abs(df['Low'] - df['Close'].shift(1))
        ])
        df['ATR'] = df['TR'].rolling(period).mean()

        # Compute the range over the period
        high_over_period = df['High'].rolling(period).max()
        low_over_period = df['Low'].rolling(period).min()
        range_over_period = high_over_period - low_over_period

        # Compute the Choppiness Index
        choppiness_index = 100 * np.log10(df['ATR'].rolling(period).sum() / range_over_period) / np.log10(period)

        return choppiness_index
    except Exception as e:
        raise ValueError(f"Error calculating Choppiness Index: {str(e)}")

def ta_vol_Returns(df: pd.DataFrame, window: int = 1) -> pd.Series:
    """Calculate the percentage returns over a specified window.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The number of periods to calculate returns over. Defaults to 1.

    Returns:
        pd.Series: Percentage returns. Interpretation:
            - Positive values indicate price increases
            - Negative values indicate price decreases
            - Larger absolute values indicate larger price changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> returns = ta_vol_Returns(df)

    References:
        - https://www.investopedia.com/terms/r/return.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return df['Close'].pct_change(window).dropna()
    except Exception as e:
        raise ValueError(f"Error calculating Returns: {str(e)}")

def ta_vol_LogReturns(df: pd.DataFrame, window: int = 1) -> pd.Series:
    """Calculate the logarithmic returns over a specified window.

    Log returns are preferred in financial analysis as they are additive and more
    likely to be normally distributed.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The number of periods to calculate returns over. Defaults to 1.

    Returns:
        pd.Series: Logarithmic returns. Interpretation:
            - Positive values indicate price increases
            - Negative values indicate price decreases
            - Values are approximately equal to percentage returns for small changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> log_returns = ta_vol_LogReturns(df)

    References:
        - https://www.investopedia.com/terms/l/log-normal-distribution.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return np.log(df['Close'] / df['Close'].shift(window)).dropna()
    except Exception as e:
        raise ValueError(f"Error calculating Log Returns: {str(e)}")

def ta_vol_Volatility(df: pd.DataFrame, window: int = 1) -> pd.Series:
    """Calculate the rolling variance of returns as a measure of volatility.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period for calculating variance. Defaults to 1.

    Returns:
        pd.Series: Volatility values. Interpretation:
            - Higher values indicate more volatile price action
            - Lower values indicate more stable price action
            - Can be used to identify periods of market stress

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> volatility = ta_vol_Volatility(df)

    References:
        - https://www.investopedia.com/terms/v/volatility.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        returns = ta_vol_Returns(df)
        return returns.rolling(window).var().dropna()
    except Exception as e:
        raise ValueError(f"Error calculating Volatility: {str(e)}")

def ta_vol_TP(data: pd.DataFrame):
    return (data['High'] + data['Low'] + data['Close']) / 3

def ta_vol_MP(df):
    mp = (df['High'] + df['Low']) / 2
    return mp

# -------------------Volatility indicators-----------------
import pandas as pd

def ta_vol_BollingerBands_Upper(data: pd.DataFrame, period=20):
    """
    Calculates the upper Bollinger Band.

    :param data: DataFrame containing 'Close' price data.
    :param period: Number of periods for calculating the moving average and standard deviation.
    :return: Series representing the upper Bollinger Band.
    """
    from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_SMA
    sma = ta_ma_SMA(data, period)
    std = data['Close'].rolling(period).std()
    return sma + std * 2

def ta_vol_BollingerBands_Lower(data: pd.DataFrame, period=20):
    """
    Calculates the lower Bollinger Band.

    :param data: DataFrame containing 'Close' price data.
    :param period: Number of periods for calculating the moving average and standard deviation.
    :return: Series representing the lower Bollinger Band.
    """
    from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_SMA
    sma = ta_ma_SMA(data, period)
    std = data['Close'].rolling(period).std()
    return sma - std * 2

def ta_vol_BollingerBands(data: pd.DataFrame, period=20):
    """
    Computes Bollinger Bands (upper, lower, and simple moving average).

    :param data: DataFrame containing 'Close' price data.
    :param period: Number of periods for calculation.
    :return: Tuple of (upper band, lower band, simple moving average).
    """
    from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_SMA
    return ta_vol_BollingerBands_Upper(data, period), ta_vol_BollingerBands_Lower(data, period), ta_ma_SMA(data, period)
    

def ta_vol_BollingerBandWidth(data):
    a, b, c = ta_vol_BollingerBands(data=data)
    return a - b


# Keltner Channels
def ta_vol_KeltnerChannel(data: pd.DataFrame, period=20, k=2):
    """
    Keltner Channels: Keltner Channels are similar to Bollinger Bands, but instead of using standard deviation to calculate the channel width, Keltner Channels use the average true range (ATR) of the stock's price. The ATR is a measure of the stock's volatility, and traders use Keltner Channels to identify potential buy and sell signals based on the stock's price action relative to the channels.
    :param data:
    :param period:
    :param k:
    :return:
    """
    from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_EMA
    ema = ta_ma_EMA(data, period)
    keltner_up = ema + ta_vol_ATR(data, period) * k  # Calculate top band
    keltner_down = ema - ta_vol_ATR(data, period) * k  # Calculate bottom band
    return keltner_up, keltner_down, ema


def ta_vol_KeltnerChannelWidth(data):
    a, b, c = ta_vol_KeltnerChannel(data=data)
    return a - b



def ta_vol_ChaikinVolatility(df: pd.DataFrame, n: int = 1) -> pd.Series:
    """Calculate the Chaikin Volatility indicator.

    The Chaikin Volatility indicator measures the rate of change of the spread
    between high and low prices, indicating volatility levels.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 1.

    Returns:
        pd.Series: Chaikin Volatility values. Interpretation:
            - Rising values indicate increasing volatility
            - Falling values indicate decreasing volatility
            - Extreme values may signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> cv = ta_vol_ChaikinVolatility(df)

    References:
        - https://www.investopedia.com/terms/c/chaikinvolatility.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        cv = clv.rolling(n).std() * np.sqrt(n)
        return cv
    except Exception as e:
        raise ValueError(f"Error calculating Chaikin Volatility: {str(e)}")

def ta_vol_TR(df: pd.DataFrame) -> pd.Series:
    """Calculate the True Range.

    The True Range is the greatest of: current high - current low, 
    abs(current high - previous close), or abs(current low - previous close).

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices

    Returns:
        pd.Series: True Range values. Interpretation:
            - Higher values indicate higher volatility
            - Lower values indicate lower volatility
            - Used as input for other indicators like ATR

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> tr = ta_vol_TR(df)

    References:
        - https://www.investopedia.com/terms/a/atr.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_close, high_low, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range
    except Exception as e:
        raise ValueError(f"Error calculating True Range: {str(e)}")

def ta_vol_ATR(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Average True Range (ATR).

    The ATR is a technical analysis indicator that measures market volatility
    by decomposing the entire range of an asset price for that period.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: ATR values. Interpretation:
            - Higher values indicate higher volatility
            - Lower values indicate lower volatility
            - Often used for position sizing and stop placement

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> atr = ta_vol_ATR(df)

    References:
        - https://www.investopedia.com/terms/a/atr.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        return ta_vol_TR(df).rolling(period).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Average True Range: {str(e)}")

def ta_vol_MassIndex(df: pd.DataFrame, n: int = 9, m: int = 25) -> pd.Series:
    """Calculate the Mass Index.

    The Mass Index identifies trend reversals by comparing the trading range over
    multiple periods, focusing on range expansions and contractions.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        n (int, optional): First EMA period. Defaults to 9.
        m (int, optional): Sum period. Defaults to 25.

    Returns:
        pd.Series: Mass Index values. Interpretation:
            - Values above 27 suggest potential trend reversal
            - Bulge occurs when index rises above 27 then drops below 26.5
            - Used to identify reversal bulges regardless of direction

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> mi = ta_vol_MassIndex(df)

    References:
        - https://www.investopedia.com/terms/m/massindex.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        range_high_low = high - low
        single_ema = pd.Series(range_high_low.ewm(span=n, min_periods=n).mean())
        double_ema = pd.Series(single_ema.ewm(span=n, min_periods=n).mean())
        ema_ratio = single_ema / double_ema
        mass_index = pd.Series(ema_ratio.rolling(m).sum(), name='Mass Index_' + str(n) + '_' + str(m))
        return mass_index
    except Exception as e:
        raise ValueError(f"Error calculating Mass Index: {str(e)}")

def ta_vol_PercentB(df: pd.DataFrame, n: int = 20, mult: float = 2) -> pd.Series:
    """Calculate the %B (Percent B) indicator.

    %B shows where price is in relation to the Bollinger Bands. The values range
    from 0 to 1, with 0.5 being the middle band.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 20.
        mult (float, optional): Standard deviation multiplier. Defaults to 2.

    Returns:
        pd.Series: %B values ranging from 0 to 1. Interpretation:
            - Values above 1 indicate price above upper band
            - Values below 0 indicate price below lower band
            - Value of 0.5 indicates price at middle band

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> percent_b = ta_vol_PercentB(df)

    References:
        - https://www.investopedia.com/terms/b/bollingerbands.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        mid = df['Close'].rolling(n).mean()
        std = df['Close'].rolling(n).std()
        upper = mid + mult * std
        lower = mid - mult * std
        percent_b = (df['Close'] - lower) / (upper - lower)
        return percent_b
    except Exception as e:
        raise ValueError(f"Error calculating %B: {str(e)}")

def ta_vol_PercentK(df: pd.DataFrame, ema_period: int = 20, atr_period: int = 10, 
                    atr_multiplier: float = 2) -> pd.Series:
    """Calculate the %K (Percent K) indicator.

    %K shows where price is in relation to the Keltner Channels. The values range
    from 0 to 1, with 0.5 being the middle channel.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'High': High prices
            - 'Low': Low prices
        ema_period (int, optional): EMA period for middle line. Defaults to 20.
        atr_period (int, optional): ATR period for channel width. Defaults to 10.
        atr_multiplier (float, optional): ATR multiplier. Defaults to 2.

    Returns:
        pd.Series: %K values ranging from 0 to 1. Interpretation:
            - Values above 1 indicate price above upper channel
            - Values below 0 indicate price below lower channel
            - Value of 0.5 indicates price at middle channel

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> percent_k = ta_vol_PercentK(df)

    References:
        - https://www.investopedia.com/terms/k/keltnerchannel.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        # Calculate EMA
        from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_EMA
        ema = ta_ma_EMA(df['Close'], window=ema_period)

        # Calculate ATR
        atr = ta_vol_ATR(df, atr_period)

        # Calculate upper and lower Keltner Channels
        upper_kc = ema + atr_multiplier * atr
        lower_kc = ema - atr_multiplier * atr

        # Calculate percent K
        percent_k = (df['Close'] - lower_kc) / (upper_kc - lower_kc)

        return percent_k
    except Exception as e:
        raise ValueError(f"Error calculating %K: {str(e)}")

def ta_vol_UlcerIndex(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Calculate the Ulcer Index.

    The Ulcer Index measures downside risk by incorporating both the depth and
    duration of price declines, squaring the percentage decline to penalize
    larger drops more heavily.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Ulcer Index values. Interpretation:
            - Higher values indicate deeper/longer drawdowns
            - Lower values indicate shallower/shorter drawdowns
            - Used to assess portfolio risk and compare investments

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> ui = ta_vol_UlcerIndex(df)

    References:
        - https://www.investopedia.com/terms/u/ulcerindex.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = df.copy()
        rs = df['Close'].pct_change()
        dd = (1 - df['Close'] / df['Close'].rolling(n).max()) * 100
        ui = np.sqrt((1 / n) * (dd ** 2).rolling(n).sum())
        return ui
    except Exception as e:
        raise ValueError(f"Error calculating Ulcer Index: {str(e)}")

def ta_vol_AberrationIndicator(df: pd.DataFrame, n: int = 10) -> float:
    """Calculate the Aberration Indicator.

    The Aberration Indicator measures the deviation of price from its average
    range, helping identify potential price extremes and reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.

    Returns:
        float: Aberration Indicator value. Interpretation:
            - Positive values indicate price above normal range
            - Negative values indicate price below normal range
            - Larger absolute values suggest greater deviation

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> ai = ta_vol_AberrationIndicator(df)

    References:
        - Technical Analysis of Stocks & Commodities magazine
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high_prices = df['High'].rolling(window=n).max()
        low_prices = df['Low'].rolling(window=n).min()
        mid_prices = (high_prices + low_prices) / 2
        ai = df['Close'] - mid_prices

        return ai.mean()
    except Exception as e:
        raise ValueError(f"Error calculating Aberration Indicator: {str(e)}")

def ta_vol_FractalDimensionIndex(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Calculate the Fractal Dimension Index (FDI).

    The FDI measures the fractal nature of price movement, helping identify
    whether price action is trending or ranging.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        n (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: FDI values. Interpretation:
            - Values near 1 indicate trending market
            - Values near 2 indicate ranging market
            - Used to identify market state and potential transitions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72]
        ... })
        >>> fdi = ta_vol_FractalDimensionIndex(df)

    References:
        - https://www.investopedia.com/terms/f/fractal-markets-hypothesis-fmh.asp
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high, low = df['High'], df['Low']
        rs = np.log(high / low).cumsum()
        fdi = np.zeros(n-1)
        
        for i in range(n-1, len(high)):
            rescaled_range = (rs[i] - rs[i-n+1]) / n
            fdi = np.append(fdi, rescaled_range)
            
        return pd.Series(fdi, index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating Fractal Dimension Index: {str(e)}")

def ta_vol_VQI(df: pd.DataFrame, period: int = 14, factor: float = 2) -> pd.Series:
    """Calculate the Volatility Quality Index (VQI).

    The VQI compares price volatility to average volatility to identify periods
    of unusual market activity and potential trend changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.
        factor (float, optional): Volatility multiplier. Defaults to 2.

    Returns:
        pd.Series: VQI values. Interpretation:
            - Higher values indicate higher quality volatility
            - Lower values indicate lower quality volatility
            - Can be used to confirm trend strength

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> vqi = ta_vol_VQI(df)

    References:
        - Technical Analysis of Stocks & Commodities magazine
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        TR = pd.Series(0.0, index=df.index)
        for i in range(1, len(df.index)):
            TR[i] = max(df['High'][i], df['Close'][i-1]) - min(df['Low'][i], df['Close'][i-1])
            
        ATR = TR.rolling(window=period).mean()
        std_dev = df['Close'].rolling(window=period).std()
        
        VQI = pd.Series(0.0, index=df.index)
        for i in range(period, len(df.index)):
            VQI[i] = (std_dev[i] / ATR[i]) * factor
            
        return VQI
    except Exception as e:
        raise ValueError(f"Error calculating Volatility Quality Index: {str(e)}")

def ta_vol_EfficiencyRatio(df: pd.DataFrame, window: int = 26) -> pd.Series:
    """Calculate the Efficiency Ratio.

    The Efficiency Ratio measures the efficiency of price movement by comparing
    the net price change to the total path length of price movement.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 26.

    Returns:
        pd.Series: Efficiency Ratio values ranging from 0 to 1. Interpretation:
            - Values near 1 indicate efficient price movement (trending)
            - Values near 0 indicate inefficient price movement (ranging)
            - Used to identify market state and trend strength

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> er = ta_vol_EfficiencyRatio(df)

    References:
        - https://www.investopedia.com/terms/e/efficiencyratio.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        close = df['Close']
        change = close.diff()
        volatility = (high - low).rolling(window).sum()
        return change.abs().rolling(window).sum() / volatility
    except Exception as e:
        raise ValueError(f"Error calculating Efficiency Ratio: {str(e)}")

def add_Volatility(df: pd.DataFrame) -> pd.DataFrame:
    """Add all volatility indicators to the DataFrame.

    This function calculates and adds various volatility indicators to the input
    DataFrame, providing a comprehensive view of market volatility.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.DataFrame: Original DataFrame with added columns:
            - ta_vol_Returns_*: Returns over different periods
            - ta_vol_LogReturns_*: Log returns over different periods
            - ta_vol_Volatility_*: Volatility over different periods
            - ta_vol_TP: Typical Price
            - ta_vol_TR: True Range
            - ta_vol_ATR: Average True Range
            - ta_vol_BollingerBand_*: Bollinger Band components
            - ta_vol_KeltnerChannel_*: Keltner Channel components
            - ta_vol_ChaikinVolatility: Chaikin Volatility
            - ta_vol_UlcerIndex: Ulcer Index

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Open': [44.12, 44.25, 43.72],
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> df_with_indicators = add_Volatility(df)

    Note:
        This function adds multiple timeframe variants of some indicators
        (1, 5, 10, 30, 90 periods) to provide both short and long-term perspectives.
    """
    try:
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy()

        # Add returns and volatility indicators for different timeframes
        df['ta_vol_Returns_1'] = ta_vol_Returns(df)
        df['ta_vol_Returns_5'] = ta_vol_Returns(df, 5)
        df['ta_vol_Returns_10'] = ta_vol_Returns(df, 10)
        df['ta_vol_Returns_30'] = ta_vol_Returns(df, 30)
        df['ta_vol_Returns_90'] = ta_vol_Returns(df, 90)

        df['ta_vol_LogReturns'] = ta_vol_LogReturns(df)
        df['ta_vol_LogReturns_5'] = ta_vol_LogReturns(df, 5)
        df['ta_vol_LogReturns_10'] = ta_vol_LogReturns(df, 10)
        df['ta_vol_LogReturns_30'] = ta_vol_LogReturns(df, 30)
        df['ta_vol_LogReturns_90'] = ta_vol_LogReturns(df, 90)

        df['ta_vol_Volatility_1'] = ta_vol_Volatility(df)
        df['ta_vol_Volatility_5'] = ta_vol_Volatility(df, 5)
        df['ta_vol_Volatility_10'] = ta_vol_Volatility(df, 10)
        df['ta_vol_Volatility_30'] = ta_vol_Volatility(df, 30)
        df['ta_vol_Volatility_90'] = ta_vol_Volatility(df, 90)

        # Add price-based indicators
        df['ta_vol_TP'] = ta_vol_TP(df)
        df['ta_vol_TR'] = ta_vol_TR(df)
        df['ta_vol_ATR'] = ta_vol_ATR(df)

        # Add Bollinger Bands
        df['ta_vol_BollingerBand_Upper'], df['ta_vol_BollingerBand_Lower'], df['ta_vol_BollingerBand_middle'] = ta_vol_BollingerBands(df)
        df['ta_vol_BollingerBand_Width'] = ta_vol_BollingerBandWidth(df)
        df['ta_vol_PercentB'] = ta_vol_PercentB(df)

        # Add Keltner Channels
        df['ta_vol_KeltnerChannel_Upper'], df['ta_vol_KeltnerChannel_Lower'], df['ta_vol_KeltnerChannel_middle'] = ta_vol_KeltnerChannel(df)
        df['ta_vol_KeltnerChannel_Width'] = ta_vol_KeltnerChannelWidth(df)
        df['ta_vol_PercentK'] = ta_vol_PercentK(df)

        # Add other volatility indicators
        df['ta_vol_ChaikinVolatility'] = ta_vol_ChaikinVolatility(df)
        df['ta_vol_UlcerIndex'] = ta_vol_UlcerIndex(df)

        return df
    except Exception as e:
        raise ValueError(f"Error adding volatility indicators: {str(e)}")
