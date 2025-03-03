"""Technical Analysis Momentum Indicators.

This module implements various technical analysis momentum indicators used in financial markets.
Each indicator is implemented as a function that takes a pandas DataFrame containing OHLCV data
and returns the calculated indicator values.

Note:
    All functions expect a pandas DataFrame with at least these columns: ['Open', 'High', 'Low', 'Close', 'Volume']
"""

import numpy as np
import pandas as pd
#from Technical_Analysis.Indicators.movingAverages.movingAverages import ta_ma_EMA,ta_ma_SMA
   

def ta_mo_RVI(df: pd.DataFrame, n: int = 10) -> tuple[pd.Series, pd.Series]:
    """Calculate the Relative Vigor Index (RVI).

    The RVI measures the conviction of a recent price action and the likelihood
    that it will continue. It is calculated by comparing the positioning of the
    close relative to the open price over several periods.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - rvi: The RVI line
            - rvi_signal: The signal line

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> rvi, signal = ta_mo_RVI(df)

    References:
        - https://www.investopedia.com/terms/r/relative_vigor_index.asp
    """
    try:
        h = (df['High'] + df['Close'].shift(1)) / 2
        l = (df['Low'] + df['Close'].shift(1)) / 2
        c = (2 * df['Close'] + df['High'] + df['Low']) / 4
        from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_SMA
        rvi = ta_ma_SMA((h - l) / (c - l), n)
        rvi_signal = ta_ma_SMA(rvi, n)
        return rvi, rvi_signal
    except Exception as e:
        raise ValueError(f"Error calculating RVI: {str(e)}")

def ta_mo_WildersMovingAverage(df: pd.DataFrame, column: str = 'Close', period: int = 14) -> pd.Series:
    """Calculate Wilder's Moving Average.

    Wilder's Moving Average is a type of modified moving average that was developed by J. Welles Wilder.
    It is similar to an exponential moving average but with a different weighting factor.

    Args:
        df (pd.DataFrame): DataFrame containing market data
        column (str, optional): The column name to calculate the average on. Defaults to 'Close'.
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Wilder's Moving Average values

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> wma = ta_mo_WildersMovingAverage(df)

    References:
        - https://www.investopedia.com/terms/w/wilders.asp
    """
    try:
        if column not in df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")
            
        weighted_prices = df[column].rolling(period).apply(
            lambda x: np.sum(x * (1 - np.arange(period) / period)),
            raw=True
        )
        divisor = np.cumsum(np.ones(period))[-1]
        return weighted_prices / divisor
    except Exception as e:
        raise ValueError(f"Error calculating Wilder's Moving Average: {str(e)}")

def ta_mo_RSI(df: pd.DataFrame, n: int = 14) -> np.ndarray:
    """Calculate the Relative Strength Index (RSI).

    The RSI is a momentum indicator that measures the magnitude of recent price changes
    to evaluate overbought or oversold conditions. It oscillates between 0 and 100.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
        n (int, optional): The number of periods to use for RSI calculation. Defaults to 14.

    Returns:
        np.ndarray: Array containing the RSI values. Values range from 0 to 100.
            - RSI > 70 typically indicates overbought conditions
            - RSI < 30 typically indicates oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> rsi = ta_mo_RSI(df)
    """
    prices = df['Close']
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed >= 0].sum()/n
    down = -seed[seed < 0].sum()/n
    rs = up / down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1. + rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n
        rs = up / down
        rsi[i] = 100. - 100./(1. + rs)
    
    return rsi

def ta_mo_TSI(df: pd.DataFrame, r: int = 25, s: int = 13) -> list:
    """Calculate the True Strength Index (TSI).

    The True Strength Index (TSI) is a momentum oscillator based on a double smoothing of price changes.
    It shows both trend direction and overbought/oversold conditions.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        r (int, optional): First smoothing period. Defaults to 25.
        s (int, optional): Second smoothing period. Defaults to 13.

    Returns:
        list: The TSI values. Values typically range from -100 to +100:
            - Values above +25 indicate overbought conditions
            - Values below -25 indicate oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> tsi = ta_mo_TSI(df)

    References:
        - https://www.investopedia.com/terms/t/tsi.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        prices = df['Close']
        pc = np.diff(prices)  # Price change
        from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_EMA
        # Double smoothing
        ema1 = ta_ma_EMA(pc, r)
        ema2 = ta_ma_EMA(ema1, s)
        ema3 = ta_ma_EMA(np.abs(pc), r)
        ema4 = ta_ma_EMA(ema3, s)
        
        # Calculate TSI
        tsi = [100 * e2/e4 if e4 != 0 else 0 for e2, e4 in zip(ema2, ema4)]
        return [np.NaN] + tsi
    except Exception as e:
        raise ValueError(f"Error calculating TSI: {str(e)}")

def ta_mo_HurstSpectralOscillator(df: pd.DataFrame, lag: int = 14) -> float:
    """Calculate the Hurst Spectral Oscillator.

    The Hurst Spectral Oscillator measures the long-term memory of a time series and
    its tendency to either trend or mean revert.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        lag (int, optional): The lookback period. Defaults to 14.

    Returns:
        float: The Hurst exponent value:
            - H > 0.5 indicates a trending series
            - H < 0.5 indicates a mean-reverting series
            - H = 0.5 indicates a random walk

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> hurst = ta_mo_HurstSpectralOscillator(df)

    References:
        - https://en.wikipedia.org/wiki/Hurst_exponent
    """
    try:
        price = df['Close']
        log_returns = np.log(price / price.shift(1)).dropna()
        tau = [np.sqrt(np.mean(np.power(log_returns[i:] - log_returns[:-i], 2))) 
               for i in range(1, lag + 1)]
        poly = np.polyfit(np.log(range(1, lag + 1)), np.log(tau), 1)
        h = poly[0] * 2
        return h
    except Exception as e:
        raise ValueError(f"Error calculating Hurst Spectral Oscillator: {str(e)}")

def ta_mo_UltimateOscillator(df: pd.DataFrame, period1: int = 7, period2: int = 14, period3: int = 28) -> pd.Series:
    """Calculate the Ultimate Oscillator.

    The Ultimate Oscillator is a momentum oscillator that incorporates three different
    time periods to improve the accuracy of overbought/oversold signals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        period1 (int, optional): First (shortest) period. Defaults to 7.
        period2 (int, optional): Second (medium) period. Defaults to 14.
        period3 (int, optional): Third (longest) period. Defaults to 28.

    Returns:
        pd.Series: Ultimate Oscillator values ranging from 0 to 100:
            - Values > 70 indicate overbought conditions
            - Values < 30 indicate oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> uo = ta_mo_UltimateOscillator(df)

    References:
        - https://www.investopedia.com/terms/u/ultimateoscillator.asp
    """
    try:
        stock_data = df.copy()
        
        # Calculate buying pressure (BP) and true range (TR)
        stock_data['bp'] = stock_data['Close'] - pd.concat(
            [stock_data['Low'], stock_data['Close'].shift(1)], axis=1).min(axis=1)
        stock_data['tr'] = pd.concat(
            [stock_data['High'], stock_data['Close'].shift(1)], axis=1).max(axis=1) - pd.concat(
            [stock_data['Low'], stock_data['Close'].shift(1)], axis=1).min(axis=1)
        
        # Calculate averages for different periods
        stock_data['average_bp1'] = stock_data['bp'].rolling(window=period1).mean()
        stock_data['average_tr1'] = stock_data['tr'].rolling(window=period1).mean()
        stock_data['average_bp2'] = stock_data['bp'].rolling(window=period2).mean()
        stock_data['average_tr2'] = stock_data['tr'].rolling(window=period2).mean()
        stock_data['average_bp3'] = stock_data['bp'].rolling(window=period3).mean()
        stock_data['average_tr3'] = stock_data['tr'].rolling(window=period3).mean()
        
        # Calculate Ultimate Oscillator
        stock_data['ultimate_oscillator'] = 100 * (
            (4 * stock_data['average_bp1'] / stock_data['average_tr1']) +
            (2 * stock_data['average_bp2'] / stock_data['average_tr2']) +
            (stock_data['average_bp3'] / stock_data['average_tr3'])
        ) / (4 + 2 + 1)
        
        return stock_data['ultimate_oscillator']
    except Exception as e:
        raise ValueError(f"Error calculating Ultimate Oscillator: {str(e)}")

def ta_mo_CMO(df, period=14):
    """
    The Chande Momentum Oscillator, on the other hand, is a momentum oscillator that measures the difference between the sum of the up closes and the sum of the down closes over a specified period. The CMO oscillates between +100 and -100, with readings above +50 indicating bullish momentum and readings below -50 indicating bearish momentum. Like the SMI, the CMO can be used to identify overbought and oversold conditions, as well as to signal possible trend reversals
    :param df:
    :param period:
    :return:
    """
    # Calculate the difference between the close price and previous close price
    delta = df['Close'].diff()

    # Calculate the up and down changes
    up_change = delta.where(delta > 0, 0)
    down_change = abs(delta.where(delta < 0, 0))

    # Calculate the sum of up and down changes over the specified period
    up_sum = up_change.rolling(window=period).sum()
    down_sum = down_change.rolling(window=period).sum()

    # Calculate the CMO value
    CMO = 100 * (up_sum - down_sum) / (up_sum + down_sum)

    return CMO

def ta_mo_CoppockCurve(df):
    """
    The Coppock curve is a technical analysis tool used in finance to determine long-term momentum in the stock market. It was developed by E.S. Coppock in the 1960s and measures the rate of change in a weighted moving average of the sum of the 11-month rate of change in the spot price of a stock, plus the 14-month rate of change in the spot price. The Coppock curve is often used by investors and traders to determine long-term buying or selling opportunities in the stock market, and is considered a long-term momentum indicator.
    :param df:
    :return:
    """
    if 'Adj Close' in df.columns:
        c = 'Adj Close'
    else:
        c = 'Close'
    # Calculate the rate of change (ROC) over a 11-period and 14-period
    roc11 = df[c].pct_change(periods=11)
    roc14 = df[c].pct_change(periods=14)

    # Calculate the weighted sum of ROC11 and ROC14
    coppock = (roc11 + roc14) * (11 * 14) / 2

    # Add the weighted sum to a 10-period weighted moving average of the sum
    coppock = coppock.rolling(window=10).mean()

    # Return the result
    return coppock

def ta_mo_PPO(df: pd.DataFrame, n1: int = 12, n2: int = 26, n3: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Percentage Price Oscillator (PPO).

    The PPO is a momentum oscillator that measures the difference between two moving
    averages as a percentage of the larger moving average.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n1 (int, optional): Short-term period. Defaults to 12.
        n2 (int, optional): Long-term period. Defaults to 26.
        n3 (int, optional): Signal line period. Defaults to 9.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - ppo: The PPO line
            - ppo_hist: The PPO histogram (difference between PPO and signal)
            - ppo_signal: The signal line

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> ppo, hist, signal = ta_mo_PPO(df)

    References:
        - https://www.investopedia.com/terms/p/ppo.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Calculate EMAs
        ema_short = df['Close'].ewm(span=n1, min_periods=n1).mean()
        ema_long = df['Close'].ewm(span=n2, min_periods=n2).mean()
        
        # Calculate PPO
        ppo = 100 * (ema_short - ema_long) / ema_long
        ppo_signal = ppo.ewm(span=n3, min_periods=n3).mean()
        ppo_hist = ppo - ppo_signal
        
        return ppo, ppo_hist, ppo_signal
    except Exception as e:
        raise ValueError(f"Error calculating PPO: {str(e)}")

def ta_mo_StochOscillator(df: pd.DataFrame, n: int = 14, k: int = 3, d: int = 3) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """Calculate the Stochastic Oscillator.

    The Stochastic Oscillator is a momentum indicator comparing a particular closing price
    of a security to a range of its prices over a certain period of time.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        n (int, optional): The number of periods for the stochastic calculation. Defaults to 14.
        k (int, optional): The number of periods for the %K smoothing. Defaults to 3.
        d (int, optional): The number of periods for the %D smoothing. Defaults to 3.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series, pd.Series]: A tuple containing:
            - stoch_k: The fast %K line
            - stoch_d: The slow %K line
            - stoch_ds: The slow %D line
            - stoch_sig: The signal line

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> k, d, ds, sig = ta_mo_StochOscillator(df)

    References:
        - https://www.investopedia.com/terms/s/stochasticoscillator.asp
    """
    try:
        # Input validation
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
        
        # Calculate the stochastic oscillator components
        low_min = df['Low'].rolling(window=n).min()
        high_max = df['High'].rolling(window=n).max()
        
        # Avoid division by zero
        denominator = high_max - low_min
        denominator = denominator.where(denominator != 0, 1)
        
        stoch_k = ((df['Close'] - low_min) / denominator) * 100
        stoch_d = stoch_k.rolling(window=k).mean()
        stoch_ds = stoch_d.rolling(window=d).mean()
        stoch_sig = stoch_ds.rolling(window=3).mean()
        
        return stoch_k, stoch_d, stoch_ds, stoch_sig
        
    except Exception as e:
        raise ValueError(f"Error calculating Stochastic Oscillator: {str(e)}")

def ta_mo_APO(df: pd.DataFrame, fast_period: int = 10, slow_period: int = 30, signal_period: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Absolute Price Oscillator (APO).

    The APO is a momentum indicator that measures the difference between two exponential
    moving averages of different periods. Unlike PPO, APO shows the absolute difference.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        fast_period (int, optional): Short-term period. Defaults to 10.
        slow_period (int, optional): Long-term period. Defaults to 30.
        signal_period (int, optional): Signal line period. Defaults to 9.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - apo: The APO line
            - histogram: The APO histogram (difference between APO and signal)
            - signal: The signal line

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> apo, hist, signal = ta_mo_APO(df)

    References:
        - https://www.investopedia.com/terms/a/absolutepriceoscillator.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        fast_ema = df['Close'].ewm(span=fast_period, adjust=False).mean()
        slow_ema = df['Close'].ewm(span=slow_period, adjust=False).mean()
        apo = fast_ema - slow_ema
        signal = apo.ewm(span=signal_period, adjust=False).mean()
        histogram = apo - signal
        return apo, histogram, signal
    except Exception as e:
        raise ValueError(f"Error calculating APO: {str(e)}")

def ta_mo_KRI(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Calculate the Kairi Relative Index (KRI).

    The Kairi Relative Index measures the deviation of price from its simple moving average
    as a percentage. It helps identify overbought and oversold conditions.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 10.

    Returns:
        pd.Series: The Kairi Relative Index values. Values are expressed as percentages:
            - Positive values indicate price is above its moving average
            - Negative values indicate price is below its moving average
            - Extreme values suggest potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> kri = ta_mo_KRI(df)

    References:
        - https://www.investopedia.com/terms/k/kairi-relative-index.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        df = df.copy()
        close = df['Close']
        ma = close.rolling(n).mean()
        kairi = (close - ma) / ma
        return kairi
    except Exception as e:
        raise ValueError(f"Error calculating Kairi Relative Index: {str(e)}")

def ta_mo_ConnorsRSI(df: pd.DataFrame, n1: int = 3, n2: int = 2, n3: int = 100) -> pd.Series:
    """Calculate the ConnorsRSI (CRSI).

    The ConnorsRSI is a composite indicator that combines three components:
    - RSI of price changes
    - Streak RSI (consecutive up/down days)
    - Percentile Rank of price changes

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n1 (int, optional): Period for price change RSI. Defaults to 3.
        n2 (int, optional): Period for streak RSI. Defaults to 2.
        n3 (int, optional): Period for percentile rank. Defaults to 100.

    Returns:
        pd.Series: ConnorsRSI values ranging from 0 to 100:
            - Values > 90 indicate overbought conditions
            - Values < 10 indicate oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> crsi = ta_mo_ConnorsRSI(df)

    References:
        - https://school.stockcharts.com/doku.php?id=technical_indicators:connors_rsi
    """
    try:
        df = df.copy()
        close = df['Close']
        
        # Calculate components
        delta = close.diff()
        up = delta.where(delta > 0, 0)
        down = -delta.where(delta < 0, 0)
        
        # Component 1: Price change RSI
        sma1 = close.rolling(n1).mean()
        sma2 = close.rolling(n2).mean()
        
        # Component 2: Streak RSI
        rsi1 = sma1.rolling(n3).apply(lambda x: np.mean(up[-n3:]) / np.mean(down[-n3:]))
        rsi2 = sma2.rolling(n3).apply(lambda x: np.mean(up[-n3:]) / np.mean(down[-n3:]))
        rsi3 = (rsi1 + rsi2) / 2
        
        # Component 3: Percentile rank
        c_rsi = (rsi3 - rsi3.rolling(n1).min()) / (rsi3.rolling(n1).max() - rsi3.rolling(n1).min())
        
        return c_rsi
    except Exception as e:
        raise ValueError(f"Error calculating ConnorsRSI: {str(e)}")

def ta_mo_PMO(df: pd.DataFrame, short: int = 10, long: int = 35, signal: int = 20) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Price Momentum Oscillator (PMO).

    The PMO is a technical momentum indicator that shows the rate of change of a
    weighted moving average of price. It's similar to MACD but more sensitive to
    price changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        short (int, optional): Short-term period. Defaults to 10.
        long (int, optional): Long-term period. Defaults to 35.
        signal (int, optional): Signal line period. Defaults to 20.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - pmo: The PMO line
            - pmo_hist: The PMO histogram (difference between PMO and signal)
            - pmo_signal: The signal line

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> pmo, hist, signal = ta_mo_PMO(df)

    References:
        - https://school.stockcharts.com/doku.php?id=technical_indicators:pmo
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        # Calculate EMAs
        ema_short = df['Close'].ewm(span=short, adjust=False).mean()
        ema_long = df['Close'].ewm(span=long, adjust=False).mean()
        
        # Calculate ROC
        roc = ((ema_short - ema_long) / ema_long) * 100
        
        # Calculate PMO components
        pmo = roc.ewm(span=signal, adjust=False).mean()
        pmo_signal = pmo.ewm(span=signal, adjust=False).mean()
        pmo_hist = roc - pmo
        
        return pmo, pmo_hist, pmo_signal
    except Exception as e:
        raise ValueError(f"Error calculating PMO: {str(e)}")

def ta_mo_SpecialK(df: pd.DataFrame, short_window: int = 10, long_window: int = 30, smoothing_period: int = 10) -> pd.Series:
    """Calculate Price's Special K indicator.

    The Special K indicator combines stochastic oscillators of different periods to
    create a unique momentum indicator that helps identify potential trend reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        short_window (int, optional): Short-term period. Defaults to 10.
        long_window (int, optional): Long-term period. Defaults to 30.
        smoothing_period (int, optional): Smoothing period. Defaults to 10.

    Returns:
        pd.Series: Special K values. Interpretation:
            - Rising values suggest bullish momentum
            - Falling values suggest bearish momentum
            - Extreme values may indicate overbought/oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> sk = ta_mo_SpecialK(df)
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        # Calculate stochastic components
        fast_k = (df['Close'] - df['Low'].rolling(window=short_window).min()) / (
            df['High'].rolling(window=short_window).max() - df['Low'].rolling(window=short_window).min())
        slow_k = fast_k.rolling(window=long_window).mean()
        slow_d = slow_k.rolling(window=smoothing_period).mean()

        # Calculate signal lines
        fast_d = fast_k.rolling(window=smoothing_period).mean()
        slow_sd = slow_d.rolling(window=smoothing_period).mean()

        # Calculate Special K
        special_k = slow_sd + (slow_sd - fast_d)
        
        return special_k
    except Exception as e:
        raise ValueError(f"Error calculating Special K: {str(e)}")

def ta_mo_WilliamsR(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Williams %R indicator.

    Williams %R is a momentum indicator that measures overbought and oversold levels,
    similar to a stochastic oscillator. It reflects the level of the close relative
    to the highest high for a look-back period.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: Williams %R values ranging from -100 to 0:
            - Values between -20 and 0 indicate overbought
            - Values between -80 and -100 indicate oversold

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> wr = ta_mo_WilliamsR(df)

    References:
        - https://www.investopedia.com/terms/w/williamsr.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        hh = high.rolling(period).max()
        ll = low.rolling(period).min()
        
        # Avoid division by zero
        denominator = hh - ll
        denominator = denominator.where(denominator != 0, 1)
        
        wr = -100 * (hh - close) / denominator
        return wr
    except Exception as e:
        raise ValueError(f"Error calculating Williams %R: {str(e)}")

def ta_mo_RainbowOscillator(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Calculate the Rainbow Oscillator.

    The Rainbow Oscillator uses multiple moving averages of different periods to
    create a momentum indicator that helps identify trend strength and potential reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): Base period for calculations. Defaults to 10.

    Returns:
        pd.Series: Rainbow Oscillator values. Interpretation:
            - Positive values indicate bullish momentum
            - Negative values indicate bearish momentum
            - Extreme values may indicate overbought/oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> rainbow = ta_mo_RainbowOscillator(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        close = df['Close']
        # Calculate Rate of Change
        roc = ((close - close.shift(n)) / close.shift(n)) * 100
        
        # Calculate multiple moving averages
        ma1 = roc.rolling(window=n, min_periods=n).mean()
        ma2 = roc.rolling(window=n*2, min_periods=n*2).mean()
        ma3 = roc.rolling(window=n*4, min_periods=n*4).mean()
        
        # Calculate Rainbow Oscillator
        return (ma1 + ma2 + ma3) / 3
    except Exception as e:
        raise ValueError(f"Error calculating Rainbow Oscillator: {str(e)}")

def ta_mo_Qstick(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Calculate the Qstick indicator.

    The Qstick indicator measures the buying and selling pressure by comparing
    opening and closing prices. It helps identify trend bias in the market.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'Close': Closing prices

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - sma: Simple Moving Average of the Qstick values
            - ema: Exponential Moving Average of the Qstick values

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Open': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33]
        ... })
        >>> sma, ema = ta_mo_Qstick(df)

    References:
        - https://www.investopedia.com/terms/q/qstick.asp
    """
    try:
        required_columns = ['Open', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        diff = df['Close'] - df['Open']
        from awt_ti.Indicators.movingAverages.movingAverages import ta_ma_EMA,ta_ma_SMA
        return ta_ma_SMA(diff), ta_ma_EMA(diff)
    except Exception as e:
        raise ValueError(f"Error calculating Qstick: {str(e)}")

def ta_mo_ROC(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Calculate the Rate of Change (ROC).

    The Rate of Change (ROC) indicator measures the percentage change in price between
    the current price and the price n periods ago.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        n (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: ROC values expressed as percentages:
            - Positive values indicate upward momentum
            - Negative values indicate downward momentum
            - Extreme values may indicate overbought/oversold conditions

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> roc = ta_mo_ROC(df)

    References:
        - https://www.investopedia.com/terms/r/rateofchange.asp
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        return 100 * df['Close'].pct_change(periods=n)
    except Exception as e:
        raise ValueError(f"Error calculating Rate of Change: {str(e)}")

def ta_mo_CenterOfGravity(df: pd.DataFrame, period: int = 10) -> float:
    """Calculate the Center of Gravity (COG) oscillator.

    The Center of Gravity oscillator is a momentum indicator that gives more weight
    to recent prices, helping to identify potential trend reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 10.

    Returns:
        float: The Center of Gravity value:
            - Rising values suggest increasing upward momentum
            - Falling values suggest increasing downward momentum

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Close': [44.34, 44.09, 44.15, 43.61, 44.33]})
        >>> cog = ta_mo_CenterOfGravity(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        weights = np.arange(1, period + 1)
        numerator = np.sum(weights * df['Close'].rolling(window=period).mean())
        denominator = np.sum(weights)
        
        return numerator / denominator if denominator != 0 else 0
    except Exception as e:
        raise ValueError(f"Error calculating Center of Gravity: {str(e)}")

def add_Momentum(df):
    df['ta_mo_stoch_K'],df['ta_mo_stoch_D'],\
    df['ta_mo_stoch_DS'],df['ta_mo_stoch_signal']=ta_mo_StochOscillator(df)

    df['ta_mo_CoppockCurve'] = ta_mo_CoppockCurve(df)

    df['ta_mo_CMO'] = ta_mo_CMO(df)
    df['ta_mo_HurstSpectralOscillator']=ta_mo_HurstSpectralOscillator(df)
    df['ta_mo_UltimateOscillator']=ta_mo_UltimateOscillator(df)

    df['ta_mo_ConnorsRSI']=ta_mo_ConnorsRSI(df)
    df['ta_mo_KairiIndex']=ta_mo_KRI(df)

    df['ta_mo_RSI']=ta_mo_RSI(df)
    df['ta_mo_TSI']=ta_mo_TSI(df)

    df['ta_mo_RVI'],df['ta_mo_RVI_signal']=ta_mo_RVI(df)


    df['ta_mo_APO'],df['ta_mo_APO_hist'],df['ta_mo_APO_signal']=ta_mo_APO(df)
    df['ta_mo_PPO'],df['ta_mo_PPO_hist'],df['ta_mo_PPO_signal']=ta_mo_PPO(df)


    df['ta_mo_Qstick_SMA'],df['ta_mo_Qstick_EMA']=ta_mo_Qstick(df)

    df['ta_mo_ROC']=ta_mo_ROC(df)

    df['ta_mo_PMO'],df['ta_mo_PMO_hist'],df['ta_mo_PMO_signal']=ta_mo_PMO(df)
    df['ta_mo_WildersMovingAverage'] = ta_mo_WildersMovingAverage(df)

    df['ta_mo_SpecialK']=ta_mo_SpecialK(df)
    df['ta_mo_WilliamsR']=ta_mo_WilliamsR(df)

    #df['ta_mo_CMB'],df['ta_mo_CMB_signal']=ta_mo_CMB(df)
    #df = pd.concat([df,ta_mo_TTMSqueeze(df)],axis=1)
    return df



