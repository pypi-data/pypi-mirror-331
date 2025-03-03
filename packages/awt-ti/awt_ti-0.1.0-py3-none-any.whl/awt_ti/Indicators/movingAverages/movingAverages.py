"""Technical Analysis Moving Average Indicators.

This module implements various technical analysis moving average indicators used in financial markets.
Each indicator is implemented as a function that takes a pandas DataFrame containing OHLCV data
and returns the calculated moving average values.

Note:
    All functions expect a pandas DataFrame with at least these columns: ['Open', 'High', 'Low', 'Close', 'Volume']
"""

# Moving Averages
# 'Moving Averages (MA) - A Moving Average is a line on a stock chart that represents the average price of a stock over a specified number of periods. The two most commonly used moving averages are the 50-day and 200-day moving averages. The 50-day MA is used to identify short-term trends, while the 200-day MA is used to identify long-term trends.'

# --------------------------Moving Averages--------------------------------------------
import numpy as np
import pandas as pd
import yfinance
from scipy.signal import butter, lfilter
from numpy.fft import fft


def ta_ma_SmoothSMA(df: pd.DataFrame, window: int = 14, smoothing_factor: float = 0.2) -> pd.Series:
    """Calculate the Smoothed Simple Moving Average.

    A variation of the Simple Moving Average that applies additional smoothing to reduce noise
    and provide a clearer trend signal.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.
        smoothing_factor (float, optional): The smoothing factor between 0 and 1. Defaults to 0.2.

    Returns:
        pd.Series: Smoothed SMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> ssma = ta_ma_SmoothSMA(df)
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        sma = data.rolling(window=window).mean()
        smoothed_sma = (sma * smoothing_factor) + (sma.shift(1) * (1 - smoothing_factor))
        return smoothed_sma
    except Exception as e:
        raise ValueError(f"Error calculating Smoothed SMA: {str(e)}")

def ta_ma_DoubleSmoothEma(df: pd.DataFrame, alpha1: float = 0.1, alpha2: float = 0.2, column: str = 'Close') -> pd.Series:
    """Calculate the Double Smoothed Exponential Moving Average.

    Applies two levels of exponential smoothing to reduce noise and lag in the moving average.
    This can help identify trends more clearly than a single EMA.

    Args:
        df (pd.DataFrame): DataFrame containing market data
        alpha1 (float, optional): First smoothing factor (0 < alpha1 < 1). Defaults to 0.1.
        alpha2 (float, optional): Second smoothing factor (0 < alpha2 < 1). Defaults to 0.2.
        column (str, optional): Column name to calculate the average on. Defaults to 'Close'.

    Returns:
        pd.Series: Double smoothed EMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than single EMA, better for longer-term trends

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> dsema = ta_ma_DoubleSmoothEma(df)

    References:
        - https://www.investopedia.com/terms/d/double-exponential-moving-average.asp
    """
    try:
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
            
        ema1 = df[column].ewm(alpha=alpha1, adjust=False).mean()
        ema2 = ema1.ewm(alpha=alpha2, adjust=False).mean()
        return 2 * ema1 - ema2
    except Exception as e:
        raise ValueError(f"Error calculating Double Smoothed EMA: {str(e)}")


def ta_ma_TripleSmoothEMA(df: pd.DataFrame, column: str = 'Close', alpha1: float = 0.1, alpha2: float = 0.15, alpha3: float = 0.2) -> pd.Series:
    """Calculate the Triple Smoothed Exponential Moving Average.

    Applies three levels of exponential smoothing to create an extremely smooth moving average.
    This indicator is useful for identifying long-term trends with minimal noise.

    Args:
        df (pd.DataFrame): DataFrame containing market data
        column (str, optional): Column name to calculate the average on. Defaults to 'Close'.
        alpha1 (float, optional): First smoothing factor (0 < alpha1 < 1). Defaults to 0.1.
        alpha2 (float, optional): Second smoothing factor (0 < alpha2 < 1). Defaults to 0.15.
        alpha3 (float, optional): Third smoothing factor (0 < alpha3 < 1). Defaults to 0.2.

    Returns:
        pd.Series: Triple smoothed EMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Very smooth, best for long-term trend identification

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> tsema = ta_ma_TripleSmoothEMA(df)

    References:
        - https://www.investopedia.com/terms/t/triple-exponential-moving-average.asp
    """
    try:
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
            
        ema1 = df[column].ewm(alpha=alpha1, adjust=False).mean()
        ema2 = ema1.ewm(alpha=alpha2, adjust=False).mean()
        ema3 = ema2.ewm(alpha=alpha3, adjust=False).mean()
        return 3 * ema1 - 3 * ema2 + ema3
    except Exception as e:
        raise ValueError(f"Error calculating Triple Smoothed EMA: {str(e)}")

def ta_ma_SMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Simple Moving Average (SMA).

    The Simple Moving Average gives equal weight to each price in the average.
    It is calculated by taking the sum of closing prices over a period and dividing by that period.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: SMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Crossovers between different SMAs can signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> sma = ta_ma_SMA(df)

    References:
        - https://www.investopedia.com/terms/s/sma.asp
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        if window > len(data):
            raise ValueError("Window must be smaller than the length of data")
            
        sma = [np.NaN] * (window - 1)
        for i in range(len(data) - window + 1):
            sma.append(sum(data.iloc[i:i + window]) / window)
        return pd.Series(sma, index=data.index)
    except Exception as e:
        raise ValueError(f"Error calculating SMA: {str(e)}")


# Double check
def ta_ma_EMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Exponential Moving Average (EMA).

    The EMA gives more weight to recent prices and less weight to older prices.
    It is more responsive to recent price changes than the SMA.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: EMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More responsive to recent price changes than SMA

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> ema = ta_ma_EMA(df)

    References:
        - https://www.investopedia.com/terms/e/ema.asp
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        if window > len(data):
            raise ValueError("Window must be smaller than the length of data")
            
        alpha = 2 / (window + 1)
        ema = [np.NaN] * (window - 1)
        ema.append(sum(data[:window]) / window)
        
        for i in range(len(data) - window):
            ema.append(alpha * data[window + i] + (1 - alpha) * ema[-1])
            
        return pd.Series(ema, index=data.index)
    except Exception as e:
        raise ValueError(f"Error calculating EMA: {str(e)}")


def ta_ma_KAMA(df: pd.DataFrame, n: int = 10, pow1: int = 2, pow2: int = 30) -> pd.Series:
    """Calculate the Kaufman Adaptive Moving Average (KAMA).

    KAMA is a moving average designed to account for market noise and volatility.
    It adapts to price changes - moving faster in trending markets and slower in ranging markets.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.
        pow1 (int, optional): Fast EMA period. Defaults to 2.
        pow2 (int, optional): Slow EMA period. Defaults to 30.

    Returns:
        pd.Series: KAMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to volatility, more responsive in trending markets

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> kama = ta_ma_KAMA(df)

    References:
        - https://www.investopedia.com/terms/k/kaufmansadaptivemovingaverage.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        change = abs(df['Close'] - df['Close'].shift(1))
        volatility = change.rolling(n).sum()
        
        # Calculate efficiency ratio
        er = change / volatility
        
        # Calculate smoothing constant
        sc = ((er * (2 / (pow1 + 1) - 2 / (pow2 + 1)) + 2 / (pow2 + 1)) ** 2).rolling(n).sum()
        
        # Calculate KAMA
        kama = np.zeros_like(df['Close'])
        kama[n - 1] = df['Close'].iloc[n - 1]
        
        for i in range(n, len(df)):
            kama[i] = kama[i - 1] + sc[i] * (df['Close'].iloc[i] - kama[i - 1])
            
        return pd.Series(kama, index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating KAMA: {str(e)}")


def ta_ma_WMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Weighted Moving Average (WMA).

    The WMA assigns higher weights to more recent prices and lower weights to older prices.
    This makes it more responsive to recent price changes than the SMA.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: WMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More responsive to recent prices than SMA

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> wma = ta_ma_WMA(df)

    References:
        - https://www.investopedia.com/terms/w/weightedaverage.asp
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        
        weights = [i + 1 for i in range(window)]
        total_weights = sum(weights)
        
        wma = [np.NaN] * window
        diff = len(data) - window
        
        for x in range(diff):
            weighted_data = [data[i + x] * weights[i] for i in range(window)]
            wma.append(sum(weighted_data) / total_weights)
            
        return pd.Series(wma, index=data.index)
    except Exception as e:
        raise ValueError(f"Error calculating WMA: {str(e)}")


def ta_ma_HMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Hull Moving Average (HMA).

    The HMA reduces lag in moving averages while maintaining smoothness.
    It's calculated using weighted moving averages with different periods.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: HMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Less lag than traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> hma = ta_ma_HMA(df)

    References:
        - https://www.investopedia.com/terms/h/hullmovingaverage.asp
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        wma1 = ta_ma_WMA(data, window // 2)
        wma2 = ta_ma_WMA(wma1, window // 2)
        return wma2
    except Exception as e:
        raise ValueError(f"Error calculating HMA: {str(e)}")


def ta_ma_TRMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Triangular Moving Average (TRMA).

    The TRMA is a double-smoothed simple moving average that puts more weight
    on the middle portion of the price series to reduce lag.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: TRMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than SMA but with more lag

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> trma = ta_ma_TRMA(df)

    References:
        - https://www.investopedia.com/terms/t/triangularaverage.asp
    """
    try:
        data = df['Close'] if isinstance(df, pd.DataFrame) else df
        sma = ta_ma_SMA(data, window)
        wma = ta_ma_WMA(data, window)
        return pd.Series([(s + m) / 2 for s, m in zip(sma, wma)], index=data.index)
    except Exception as e:
        raise ValueError(f"Error calculating TRMA: {str(e)}")


def ta_ma_VMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Variable Moving Average (VMA).

    The VMA adjusts its smoothing factor based on market volatility.
    It becomes more responsive during volatile periods and smoother during stable periods.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: VMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market volatility

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> vma = ta_ma_VMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        data = df['Close']
        volatility = sum(abs(data[i + 1] - data[i]) for i in range(window - 1)) / window
        smoothing_factor = 2 / (window + 1) if volatility > 0.1 else 2 / (window + 1) + 0.5 * (volatility - 0.1)
        return ta_ma_SmoothSMA(data, window, smoothing_factor)
    except Exception as e:
        raise ValueError(f"Error calculating VMA: {str(e)}")

def ta_ma_McginleyDynamic(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Calculate the McGinley Dynamic indicator.

    The McGinley Dynamic is a technical indicator designed to track the market
    better than existing moving averages. It minimizes price separation and helps
    to reduce whipsaws.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.

    Returns:
        pd.Series: McGinley Dynamic values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market speed, less lag than traditional MAs

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> md = ta_ma_McginleyDynamic(df)

    References:
        - https://school.stockcharts.com/doku.php?id=technical_indicators:mcginley_dynamic
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = df.copy()
        md = df['Close'].iloc[0]
        result = pd.Series(index=df.index, dtype=float)
        result.iloc[0] = md
        
        for i in range(1, len(df)):
            price = df['Close'].iloc[i]
            prev_md = md
            md += (price - prev_md) / (n * (price / prev_md) ** 4)
            result.iloc[i] = md
            
        return result
    except Exception as e:
        raise ValueError(f"Error calculating McGinley Dynamic: {str(e)}")

def ta_ma_AdaptiveMA(df: pd.DataFrame, n: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    """Calculate the Adaptive Moving Average (AMA).

    The AMA automatically adjusts its smoothing period based on market conditions.
    It moves faster in trending markets and slower in ranging markets.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.
        fast (int, optional): Fast EMA period. Defaults to 2.
        slow (int, optional): Slow EMA period. Defaults to 30.

    Returns:
        pd.Series: AMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market conditions automatically

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> ama = ta_ma_AdaptiveMA(df)

    References:
        - https://www.investopedia.com/terms/a/adaptivemovingaverage.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        smooth = pd.Series(index=df.index)
        smooth.iloc[0] = close.iloc[0]
        
        # Calculate Efficiency Ratio
        ER_num = abs(close - close.shift(n))
        ER_den = pd.Series(0.0, index=df.index)
        
        for i in range(1, n+1):
            ER_den += abs(close.shift(i) - close.shift(i+1))
            
        ER = ER_num / ER_den
        SC = ((ER * (2.0 / (fast + 1) - 2.0 / (slow + 1))) + 2 / (slow + 1)) ** 2.0
        
        for i in range(n, len(df)):
            smooth.iloc[i] = smooth.iloc[i-1] + SC.iloc[i] * (close.iloc[i] - smooth.iloc[i-1])
            
        return smooth
    except Exception as e:
        raise ValueError(f"Error calculating Adaptive Moving Average: {str(e)}")

def ta_ma_ZeroLagExponentialMA(df: pd.DataFrame, window: int = 12) -> pd.Series:
    """Calculate the Zero-Lag Exponential Moving Average (ZLEMA).

    The ZLEMA attempts to eliminate the lag associated with traditional moving averages
    by removing older price data and applying more weight to recent prices.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 12.

    Returns:
        pd.Series: ZLEMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Faster response to price changes than traditional EMAs

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> zlema = ta_ma_ZeroLagExponentialMA(df)

    References:
        - https://www.investopedia.com/terms/z/zero-lag-exponential-moving-average.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        ema = df['Close'].ewm(span=window, adjust=False).mean()
        zlema = 2 * ema - ema.ewm(span=window, adjust=False).mean()
        return zlema
    except Exception as e:
        raise ValueError(f"Error calculating Zero-Lag Exponential Moving Average: {str(e)}")

def ta_ma_T3MA(df: pd.DataFrame, period: int = 14, vfactor: float = 0.7) -> pd.Series:
    """Calculate the T3 Moving Average (T3MA).

    The T3MA is a type of moving average that uses multiple EMAs to reduce lag
    while maintaining smoothness. It was developed by Tim Tillson.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.
        vfactor (float, optional): Volume factor between 0 and 1. Defaults to 0.7.

    Returns:
        pd.Series: T3MA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than traditional MAs with less lag

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> t3ma = ta_ma_T3MA(df)

    References:
        - https://school.stockcharts.com/doku.php?id=technical_indicators:t3_moving_average
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        EMA1 = pd.Series(df['Close'].ewm(span=period).mean())
        EMA2 = pd.Series(EMA1.ewm(span=period).mean())
        EMA3 = pd.Series(EMA2.ewm(span=period).mean())
        
        # Calculate T3 coefficients
        C1 = -vfactor * vfactor * vfactor
        C2 = 3 * vfactor * vfactor + 3 * vfactor * vfactor * vfactor
        C3 = -6 * vfactor * vfactor - 3 * vfactor - 3 * vfactor * vfactor * vfactor
        C4 = 1 + 3 * vfactor + vfactor * vfactor * vfactor + 3 * vfactor * vfactor
        
        # Calculate T3
        T3 = pd.Series(0.0, index=df.index)
        for i in range(period-1, len(df.index)):
            T3[i] = C1 * EMA3[i] + C2 * EMA2[i] + C3 * EMA1[i] + C4 * df['Close'][i]
            
        return T3
    except Exception as e:
        raise ValueError(f"Error calculating T3 Moving Average: {str(e)}")

def ta_ma_JurikMA(df: pd.DataFrame, period: int = 14, vfactor: float = 0.7) -> pd.Series:
    """Calculate the Jurik Moving Average (JMA).

    The JMA is an advanced moving average that attempts to minimize noise and lag
    while maintaining smoothness. It was developed by Mark Jurik.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.
        vfactor (float, optional): Volume factor between 0 and 1. Defaults to 0.7.

    Returns:
        pd.Series: JMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Highly responsive with minimal noise

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> jma = ta_ma_JurikMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        alpha = 2 * np.pi / (period + 1)
        b = np.cos(alpha)
        a1 = -b
        c1 = 1 - b
        c2 = c1 / 2
        
        Jurik = pd.Series(0.0, index=df.index)
        for i in range(1, len(df.index)):
            Jurik[i] = c1 * (1 - a1 / 2) * df['Close'][i] + c2 * (1 + a1) * Jurik[i-1]
            
        return Jurik
    except Exception as e:
        raise ValueError(f"Error calculating Jurik Moving Average: {str(e)}")

def ta_ma_GuppyMultipleMA(df: pd.DataFrame, short_periods: list = [3, 5, 8, 10, 12, 15], 
                         long_periods: list = [30, 35, 40, 45, 50, 60]) -> tuple[pd.Series, pd.Series]:
    """Calculate the Guppy Multiple Moving Average (GMMA).

    The GMMA uses multiple EMAs of different periods to identify trend changes and strength.
    It consists of two groups: short-term (fast) and long-term (slow) moving averages.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        short_periods (list, optional): Periods for short-term EMAs. Defaults to [3, 5, 8, 10, 12, 15].
        long_periods (list, optional): Periods for long-term EMAs. Defaults to [30, 35, 40, 45, 50, 60].

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - guppy_short: Average of short-term EMAs
            - guppy_long: Average of long-term EMAs

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> short, long = ta_ma_GuppyMultipleMA(df)

    References:
        - https://www.investopedia.com/terms/g/guppy-multiple-moving-average.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = df.copy()
        
        # Calculate short-term EMAs
        for period in short_periods:
            df[f'ShortEMA_{period}'] = df['Close'].ewm(span=period).mean()
            
        # Calculate long-term EMAs
        for period in long_periods:
            df[f'LongEMA_{period}'] = df['Close'].ewm(span=period).mean()
            
        # Calculate averages
        guppy_short = df[[f'ShortEMA_{period}' for period in short_periods]].transpose().mean()
        guppy_long = df[[f'LongEMA_{period}' for period in long_periods]].transpose().mean()
        
        return guppy_short, guppy_long
    except Exception as e:
        raise ValueError(f"Error calculating Guppy Multiple Moving Average: {str(e)}")

def ta_ma_FRAMA(df: pd.DataFrame, window: int = 10) -> pd.Series:
    """Calculate the Fractal Adaptive Moving Average (FRAMA).

    FRAMA is an adaptive moving average that adjusts its smoothing based on the
    fractal dimension of the price series, making it more responsive to trends.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 10.

    Returns:
        pd.Series: FRAMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market fractals automatically

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> frama = ta_ma_FRAMA(df)

    References:
        - https://www.mesasoftware.com/papers/FRAMA.pdf
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy().reset_index()
        
        # Define constants
        alpha = 2 / (window + 1)
        d1 = 0.5 * np.exp(-1.414 * 3 / window) - np.exp(-1.414 * 3 / (window * window))
        d2 = np.exp(-1.414 * 3 / window) - 2 * np.exp(-1.414 * 3 / (window * window))
        c1 = d1
        c2 = -d2
        c3 = 1 - c1 - c2
        
        # Calculate high and low fractals
        df['max'] = df['High'].rolling(window=window).max()
        df['min'] = df['Low'].rolling(window=window).min()
        
        # Calculate FRAMA
        df['diff'] = 0
        for i in range(1, len(df)):
            if df.loc[i, 'max'] == df.loc[i-1, 'max'] and df.loc[i, 'min'] == df.loc[i-1, 'min']:
                df.loc[i, 'diff'] = 0
            else:
                df.loc[i, 'diff'] = abs(df.loc[i, 'max'] - df.loc[i-1, 'max']) + abs(df.loc[i, 'min'] - df.loc[i-1, 'min'])
                
        df['ER'] = df['diff'] / (window * 2)
        
        # Initialize FRAMA
        df['FRAMA'] = df['Close']
        
        # Calculate FRAMA for each row
        for i in range(window, len(df)):
            sum_ER = 0
            for j in range(i-window, i):
                sum_ER += df.loc[j, 'ER']
            P = c1 * sum_ER + c2 * sum_ER * sum_ER + c3
            df.loc[i, 'FRAMA'] = P * df.loc[i, 'Close'] + (1 - P) * df.loc[i-window, 'FRAMA']
            
        df.drop(['max', 'min', 'diff', 'ER'], axis=1, inplace=True)
        return df.set_index(df.index)['FRAMA']
    except Exception as e:
        raise ValueError(f"Error calculating FRAMA: {str(e)}")

def ta_ma_RainbowMA(df: pd.DataFrame, periods: list = [8, 13, 21, 34, 55]) -> pd.DataFrame:
    """Calculate the Rainbow Moving Average.

    The Rainbow Moving Average uses multiple SMAs of different periods to create
    a visual representation of trend strength and potential support/resistance levels.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        periods (list, optional): List of periods for the moving averages. 
            Defaults to [8, 13, 21, 34, 55].

    Returns:
        pd.DataFrame: DataFrame containing Rainbow MA values for each period.
            Column names are formatted as 'ta_ma_RainbowMA_{period}'.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> rainbow = ta_ma_RainbowMA(df)

    References:
        - https://school.stockcharts.com/doku.php?id=technical_indicators:rainbow_moving_average
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        close = df['Close']
        rm = pd.concat([close.rolling(window=p).mean() for p in periods], axis=1)
        rm.columns = [f'ta_ma_RainbowMA_{p}' for p in periods]
        return rm
    except Exception as e:
        raise ValueError(f"Error calculating Rainbow Moving Average: {str(e)}")

def ta_ma_ModifiedMa(df: pd.DataFrame, window: int = 9) -> pd.Series:
    """Calculate the Modified Moving Average (MMA).

    The MMA is a variation of the EMA that reduces the impact of older data points
    while maintaining smoothness.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 9.

    Returns:
        pd.Series: MMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than traditional EMA

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> mma = ta_ma_ModifiedMa(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return df["Close"].ewm(span=window, min_periods=window).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Modified Moving Average: {str(e)}")


def ta_ma_CenteredMa(df: pd.DataFrame, window: int = 9) -> pd.Series:
    """Calculate the Centered Moving Average (CMA).

    The CMA is a variation of the simple moving average that is centered on the data point,
    using an equal number of data points before and after the current point.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 9.

    Returns:
        pd.Series: CMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More responsive to price changes than traditional MA

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> cma = ta_ma_CenteredMa(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return df["Close"].rolling(window=window, center=True).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Centered Moving Average: {str(e)}")


def ta_ma_WildersMa(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Wilder's Moving Average.

    A smoothed moving average developed by J. Welles Wilder that gives more weight
    to recent data while maintaining a smooth output.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Wilder's MA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> wma = ta_ma_WildersMa(df)

    References:
        - Wilder, J. W. (1978). New Concepts in Technical Trading Systems
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        ma = df['Close'].rolling(window=window).mean()
        weights = np.arange(1, window+1)
        weights_sum = np.sum(weights)
        
        for i in range(window, len(df)):
            ma[i] = ma[i-1] + (df['Close'][i] - ma[i-1]) * (weights_sum - weights[-1]) / weights_sum
            weights = np.insert(weights[:-1], 0, window)
            weights_sum = np.sum(weights)
            
        return ma
    except Exception as e:
        raise ValueError(f"Error calculating Wilder's Moving Average: {str(e)}")

def ta_ma_GeometricMa(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Geometric Moving Average (GMA).

    The GMA uses the geometric mean instead of the arithmetic mean, making it less
    sensitive to extreme values while maintaining trend information.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: GMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Less sensitive to outliers than arithmetic moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> gma = ta_ma_GeometricMa(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return np.power(df['Close'].rolling(window=window).apply(lambda x: np.prod(x)), 1/window)
    except Exception as e:
        raise ValueError(f"Error calculating Geometric Moving Average: {str(e)}")

def ta_ma_AlligatorMa(df: pd.DataFrame, jaw_period: int = 13, teeth_period: int = 8, 
                      lips_period: int = 5) -> pd.DataFrame:
    """Calculate the Alligator Moving Average indicator.

    The Alligator indicator consists of three smoothed moving averages (Jaw, Teeth, and Lips)
    that help identify trend direction and potential trading opportunities.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        jaw_period (int, optional): Period for the Jaw line (blue). Defaults to 13.
        teeth_period (int, optional): Period for the Teeth line (red). Defaults to 8.
        lips_period (int, optional): Period for the Lips line (green). Defaults to 5.

    Returns:
        pd.DataFrame: DataFrame containing three columns:
            - ta_ma_AlligatorMA_Jaw: Jaw line (longest period)
            - ta_ma_AlligatorMa_Teeth: Teeth line (medium period)
            - ta_ma_AlligatorMa_Lips: Lips line (shortest period)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> alligator = ta_ma_AlligatorMa(df)

    References:
        - https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/alligator
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df_jaw = pd.DataFrame()
        df_teeth = pd.DataFrame()
        df_lips = pd.DataFrame()
        
        # Calculate Jaw line (blue)
        df_jaw["ta_ma_AlligatorMA_Jaw"] = df["Close"].rolling(window=jaw_period).mean().shift(jaw_period)
        
        # Calculate Teeth line (red)
        df_teeth["ta_ma_AlligatorMa_Teeth"] = df["Close"].rolling(window=teeth_period).mean().shift(teeth_period)
        
        # Calculate Lips line (green)
        df_lips["ta_ma_AlligatorMa_Lips"] = df["Close"].rolling(window=lips_period).mean().shift(lips_period)
        
        return pd.concat([df_jaw, df_teeth, df_lips], axis=1)
    except Exception as e:
        raise ValueError(f"Error calculating Alligator Moving Average: {str(e)}")

def ta_ma_SSMA(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Super Smoother Moving Average (SSMA).

    The SSMA is a low-lag moving average that uses a combination of weighted moving
    averages to reduce noise while maintaining responsiveness to price changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: SSMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than traditional moving averages with less lag

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> ssma = ta_ma_SSMA(df)

    References:
        - Ehlers, J. (2001). Rocket Science for Traders
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        alpha = 2 / (period + 1)
        beta = 1 - alpha
        ssf = (df['Close'] + 2 * df['Close'].shift(1) + df['Close'].shift(2)) / 4
        sssf = pd.Series(index=df.index, dtype='float64')
        sssf[0] = df['Close'][0]
        
        for i in range(1, len(df)):
            sssf[i] = alpha * ssf[i] + beta * sssf[i - 1]
            
        return sssf
    except Exception as e:
        raise ValueError(f"Error calculating Super Smoother Moving Average: {str(e)}")

def ta_ma_LSMA(df: pd.DataFrame, window: int = 25) -> pd.Series:
    """Calculate the Least Squares Moving Average (LSMA).

    The LSMA uses linear regression to calculate a moving average that minimizes
    the sum of squared deviations from the price data.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 25.

    Returns:
        pd.Series: LSMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More responsive to price changes than traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> lsma = ta_ma_LSMA(df)

    References:
        - https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/linear-regression
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        weights = np.arange(1, window + 1)
        denominator = np.sum(weights)
        return df['Close'].rolling(window).apply(lambda x: np.dot(x, weights) / denominator, raw=True)
    except Exception as e:
        raise ValueError(f"Error calculating Least Squares Moving Average: {str(e)}")

def ta_ma_ALMA(df: pd.DataFrame, window: int = 9, sigma: float = 6, offset: float = 0.85) -> pd.Series:
    """Calculate the Arnaud Legoux Moving Average (ALMA).

    ALMA is a moving average that combines a Gaussian distribution with an offset
    to reduce lag while maintaining smoothness.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 9.
        sigma (float, optional): Controls the smoothness. Defaults to 6.
        offset (float, optional): Controls the responsiveness. Defaults to 0.85.

    Returns:
        pd.Series: ALMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Reduced lag compared to traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> alma = ta_ma_ALMA(df)

    References:
        - https://www.prorealcode.com/prorealtime-indicators/alma-arnaud-legoux-moving-average/
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        m = offset * (window - 1)
        s = window / sigma
        w = np.array([np.exp(-(i - m) ** 2 / (2 * s ** 2)) for i in range(window)])
        return ((df['Close'] * w).sum() / w.sum()).rolling(window).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Arnaud Legoux Moving Average: {str(e)}")

def ta_ma_MEDMA(df: pd.DataFrame, window: int = 10) -> pd.Series:
    """Calculate the Median Moving Average (MEDMA).

    The MEDMA uses the median instead of the mean, making it more robust to outliers
    and extreme values in the price data.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 10.

    Returns:
        pd.Series: MEDMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More robust to outliers than traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> medma = ta_ma_MEDMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return df['Close'].rolling(window).median()
    except Exception as e:
        raise ValueError(f"Error calculating Median Moving Average: {str(e)}")

def ta_ma_ZLMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Zero-Lag Moving Average (ZLMA).

    The ZLMA attempts to eliminate the lag in traditional moving averages by
    using a combination of shorter-term moving averages.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: ZLMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Reduced lag compared to traditional moving averages

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> zlma = ta_ma_ZLMA(df)

    References:
        - https://www.tradingview.com/script/0nAJxpya-Zero-Lag-Moving-Average/
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return 2 * df['Close'].rolling(window // 2).mean() - df['Close'].rolling(window).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Zero-Lag Moving Average: {str(e)}")

def ta_ma_DetrendedMA(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculate the Detrended Moving Average (DMA).

    The DMA removes the trend component from the price series by subtracting
    a simple moving average from the original price data.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 20.

    Returns:
        pd.Series: DMA values. Interpretation:
            - Positive values indicate price above trend
            - Negative values indicate price below trend
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> dma = ta_ma_DetrendedMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        detrended = df['Close'] - df['Close'].rolling(window).mean()
        return detrended.rolling(window).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Detrended Moving Average: {str(e)}")

def ta_ma_VIDYA(df: pd.DataFrame, window: int = 9, alpha: float = 0.2) -> pd.Series:
    """Calculate the Variable Index Dynamic Average (VIDYA).

    VIDYA is an adaptive moving average that adjusts its smoothing factor based
    on market volatility, becoming more responsive in volatile markets.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 9.
        alpha (float, optional): The smoothing factor. Defaults to 0.2.

    Returns:
        pd.Series: VIDYA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market volatility automatically

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> vidya = ta_ma_VIDYA(df)

    References:
        - Chande, T. (1992). The New Technical Trader
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        vol = df['Close'].diff().abs().rolling(window).mean()
        vidya = df['Close'].rolling(window).mean() + alpha * (df['Close'] - df['Close'].rolling(window).mean()) / vol
        return vidya
    except Exception as e:
        raise ValueError(f"Error calculating Variable Index Dynamic Average: {str(e)}")

def ta_ma_ChandeViDynamic(df: pd.DataFrame, period: int = 14, a_factor: float = 0.2) -> pd.Series:
    """Calculate Chande's Variable Index Dynamic Average.

    A dynamic moving average that adjusts its sensitivity based on price momentum
    and volatility, developed by Tushar Chande.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.
        a_factor (float, optional): The acceleration factor. Defaults to 0.2.

    Returns:
        pd.Series: VI Dynamic Average values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Adapts to market conditions automatically

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> vi = ta_ma_ChandeViDynamic(df)

    References:
        - Chande, T. (1992). The New Technical Trader
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        diff = abs(df['Close'] - df['Close'].shift(1))
        direction = df['Close'] - df['Close'].shift(1)
        volatility = diff.rolling(period).sum()
        volatility[period:] = volatility[period:] + volatility[:-(period)].mean()
        
        vi = pd.Series(index=df.index, dtype='float64')
        vi[0] = df['Close'][0]
        
        for i in range(1, len(df)):
            if direction[i] > 0:
                vi[i] = vi[i - 1] + (a_factor / volatility[i]) * (df['Close'][i] - vi[i - 1])
            elif direction[i] < 0:
                vi[i] = vi[i - 1] - (a_factor / volatility[i]) * (vi[i - 1] - df['Close'][i])
            else:
                vi[i] = vi[i - 1]
                
        return vi
    except Exception as e:
        raise ValueError(f"Error calculating Chande's VI Dynamic Average: {str(e)}")

def ta_ma_HighLowMa(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the High-Low Moving Average.

    A moving average that uses both high and low prices to provide a more
    comprehensive view of price action.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: High-Low MA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Provides support/resistance levels

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15]
        ... })
        >>> hlma = ta_ma_HighLowMa(df)
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        hl = (df['High'] + df['Low']) / 2
        return hl.rolling(period).mean()
    except Exception as e:
        raise ValueError(f"Error calculating High-Low Moving Average: {str(e)}")

def ta_ma_TripleWeightedMA(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Triple Weighted Moving Average (TWMA).

    A weighted moving average that applies triple weight to the most recent data
    points, providing faster response to price changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: TWMA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - More responsive to recent price changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> twma = ta_ma_TripleWeightedMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        weights = [1, 2, 3]  # Triple weighting scheme
        return df['Close'].rolling(window=window, center=False).apply(
            lambda x: np.dot(x[-3:], weights) / sum(weights) if len(x) >= 3 else np.nan
        )
    except Exception as e:
        raise ValueError(f"Error calculating Triple Weighted Moving Average: {str(e)}")


def butter_worth_filter(df: pd.DataFrame, cutoff: float, fs: int = 1, 
                      order: int = 2) -> pd.DataFrame:
    """Apply a Butterworth filter to smooth price data.

    The Butterworth filter is a type of signal processing filter designed to have
    a frequency response that is as flat as possible in the passband.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        cutoff (float): Cutoff frequency for the filter
        fs (int, optional): Sampling frequency of the data. Defaults to 1.
        order (int, optional): Order of the filter. Defaults to 2.

    Returns:
        pd.DataFrame: DataFrame with filtered close prices. Interpretation:
            - Smoothed price data with reduced noise
            - Higher order = sharper cutoff but more computational cost
            - Lower cutoff = smoother output but more lag

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> filtered = butter_worth_filter(df, cutoff=0.1)

    References:
        - https://en.wikipedia.org/wiki/Butterworth_filter
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Design filter
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        
        # Filter data
        prices = df['Close'].values
        filtered_prices = lfilter(b, a, prices)
        
        # Create filtered dataframe
        filtered_df = df.copy()
        filtered_df['Close'] = filtered_prices
        
        return filtered_df
    except Exception as e:
        raise ValueError(f"Error applying Butterworth filter: {str(e)}")

def ta_ma_DisplacedMA(df: pd.DataFrame, displacement: int = 20) -> pd.Series:
    """Calculate the Displaced Moving Average (DMA).

    The DMA shifts a simple moving average forward or backward in time to help
    identify potential support/resistance levels or trend changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        displacement (int, optional): Number of periods to shift. Defaults to 20.
            - Positive values shift forward in time
            - Negative values shift backward in time

    Returns:
        pd.Series: Displaced MA values. Interpretation:
            - Can be used to identify potential support/resistance levels
            - Helps visualize historical price relationships
            - Useful for trend analysis

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> dma = ta_ma_DisplacedMA(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return df['Close'].rolling(window=20).mean().shift(displacement)
    except Exception as e:
        raise ValueError(f"Error calculating Displaced Moving Average: {str(e)}")

def ta_ma_WildersSmoothMa(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate Wilder's Smoothed Moving Average.

    A variation of the exponential moving average that uses Wilder's smoothing method,
    which gives more weight to recent data while maintaining smoothness.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Wilder's Smoothed MA values. Interpretation:
            - Values above price indicate downtrend
            - Values below price indicate uptrend
            - Smoother than traditional EMAs

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> wsma = ta_ma_WildersSmoothMa(df)

    References:
        - Wilder, J. W. (1978). New Concepts in Technical Trading Systems
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        alpha = 1/window
        ma = pd.Series(index=df.index, dtype='float64')
        ma[0] = df['Close'][0]
        
        for i in range(1, len(df)):
            ma[i] = alpha * df['Close'][i] + (1 - alpha) * ma[i-1]
            
        return ma
    except Exception as e:
        raise ValueError(f"Error calculating Wilder's Smoothed Moving Average: {str(e)}")
def ta_ma_FourierTransformMa(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculate the Fourier Transform Moving Average (FTMA).

    The FTMA uses the Fourier Transform to decompose the price series into its
    frequency components and then reconstructs the moving average based on these    
    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: FTMA values. Interpretation:
            - Smoothed moving average that captures price trends and cycles
            - More responsive to price changes than traditional moving averages
            - Can be used to identify trend changes and potential support/resistance levels

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})       
        >>> ftma = ta_ma_FourierTransformMa(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        # Calculate Fourier Transform
        fft_values = np.fft.fft(df['Close'])
        fft_values = np.fft.fftshift(fft_values)
        fft_values = np.abs(fft_values)
        fft_values = fft_values / len(df)
        fft_values = fft_values[len(df)//2:]
        
        # Reconstruct moving average
        ftma = pd.Series(index=df.index, dtype='float64')
        ftma[0] = df['Close'][0]
        
        for i in range(1, len(df)):
            ftma[i] = np.dot(fft_values, np.exp(2j * np.pi * i * np.arange(len(fft_values)) / len(df)))
        
        return ftma
    except Exception as e:
        raise ValueError(f"Error calculating Fourier Transform Moving Average: {str(e)}")

def add_MovingAverages(df:pd.DataFrame):
    # FAST SLOW AND HIST
    df['ta_ma_SMA_14'] = ta_ma_SMA(df,14)
    df['ta_ma_SMA_25'] = ta_ma_SMA(df, 25)
    df['ta_ma_SMA_50'] = ta_ma_SMA(df, 50)
    df['ta_ma_SMA_100'] = ta_ma_SMA(df, 100)
    df['ta_ma_SMA_200'] = ta_ma_SMA(df, 200)

    df['ta_ma_EMA_12'] = ta_ma_EMA(df,12)
    df['ta_ma_EMA_26'] = ta_ma_EMA(df, 26)
    df['ta_ma_EMA_50'] = ta_ma_EMA(df, 50)
    df['ta_ma_EMA_100'] = ta_ma_EMA(df, 100)
    df['ta_ma_EMA_200'] = ta_ma_EMA(df, 200)


    df['ta_ma_WMA'] = ta_ma_WMA(df)
    df['ta_ma_HMA'] = ta_ma_HMA(df)
    df['ta_ma_TRMA'] = ta_ma_TRMA(df)
    df['ta_ma_VMA'] = ta_ma_VMA(df)
    df['ta_ma_KAMA'] = ta_ma_KAMA(df)



    df['ta_ma_SmoothSMA'] = ta_ma_SmoothSMA(df)
    df['ta_ma_DoubleSmoothEma'] = ta_ma_DoubleSmoothEma(df)
    df['ta_ma_TripleSmoothEMA']=ta_ma_TripleSmoothEMA(df)


    df['ta_ma_FRAMA'] = ta_ma_FRAMA(df)
    df['ta_ma_T3MA']=ta_ma_T3MA(df)
    df['ta_ma_JurikMA'] = ta_ma_JurikMA(df)
    df['ta_ma_GuppyMultipleMA_long'],df['ta_ma_GuppyMultipleMA_short'] = ta_ma_GuppyMultipleMA(df)

    #[8, 13, 21, 34, 55]

    # Rainbow MA
    #df = pd.concat([df,ta_ma_rainbowMA(df)],axis=1)
    df['ta_ma_RainbowMA']= ta_ma_RainbowMA(df).mean(axis=1)


    df['ta_ma_AdaptiveMA'] = ta_ma_AdaptiveMA(df)

    df['ta_ma_ZeroLagExponentialMA'] = ta_ma_ZeroLagExponentialMA(df)

    df['ta_ma_McginleyDynamic'] = ta_ma_McginleyDynamic(df)


   

    df['ta_ma_ModifiedMa'] = ta_ma_ModifiedMa(df)
    df['ta_ma_FourierTransformMa']=ta_ma_FourierTransformMa(df)




    df['ta_ma_WildersMA']=ta_ma_WildersMa(df)
    df['ta_ma_WildersSmoothMa']=ta_ma_WildersSmoothMa(df)

    df['ta_ma_GeometricMa']=ta_ma_GeometricMa(df)
    df['ta_ma_CenteredMa']=ta_ma_CenteredMa(df)

    df = pd.concat([df, ta_ma_AlligatorMa(df)], axis=1)


    #df['ta_ma_ALMA'] = ta_ma_ALMA(df)
    #df['ta_ma_LSMA'] = ta_ma_LSMA(df)
    #df['ta_ma_ZLMA'] = ta_ma_ZLMA(df)
    #df['ta_ma_SSMA'] = ta_ma_SSMA(df)

    #df['ta_ma_DetrendedMA'] = ta_ma_DetrendedMA(df)
    #df['ta_ma_MedianMA'] = ta_ma_MEDMA(df)
    #df['ta_ma_HighLowMA'] = ta_ma_HighLowMa(df)
    #df['ta_ma_ChandeViDynamic'] = ta_ma_ChandeViDynamic(df)

    return df
