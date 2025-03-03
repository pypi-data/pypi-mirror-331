import pandas as pd
import numpy as np
from scipy.stats import stats
from scipy.signal import hilbert, butter, filtfilt




import pandas as pd


import pandas as pd
import numpy as np
from scipy.signal import hilbert, butter, filtfilt




'''
def advance_decline_line(stock_df):
    """
    Computes the Advance-Decline Line of a stock dataframe

    Parameters:
    stock_df (pd.DataFrame): A pandas dataframe containing the stock's price data

    Returns:
    pd.Series: A pandas series containing the Advance-Decline Line
    """
    # Compute the Advances and Declines
    advances = ((stock_df['Close'] - stock_df['Open']) > 0).cumsum()
    declines = ((stock_df['Close'] - stock_df['Open']) < 0).cumsum()

    # Compute the Advance-Decline Line
    advance_decline_line = advances - declines

    return advance_decline_line
'''

#-----------ELLIOT
import pandas as pd


def larger_trend(stock_df: pd.DataFrame) -> str:
    """Identifies the larger trend of the stock.

    Parameters:
        stock_df (pd.DataFrame): DataFrame containing the stock's price data with 'Close' column

    Returns:
        str: A string indicating the larger trend of the stock ('Bullish' or 'Bearish')
    """
    long_term_ma = stock_df['Close'].rolling(window=200).mean()
    return "Bullish" if long_term_ma.iloc[-1] > long_term_ma.iloc[0] else "Bearish"


import pandas as pd


def major_waves(stock_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies the major waves of the stock.

    Parameters:
        stock_df (pd.DataFrame): DataFrame containing the stock's price data with 'High' and 'Low' columns

    Returns:
        pd.DataFrame: DataFrame containing the major waves of the stock
    """
    price_diff = stock_df['High'] - stock_df['Low']
    max_diff = price_diff.rolling(window=30).max()
    waves = pd.cut(price_diff,
                  bins=[0, max_diff.quantile(0.25), max_diff.quantile(0.5), 
                       max_diff.quantile(0.75), max_diff.max()],
                  labels=['Wave 1', 'Wave 2', 'Wave 3', 'Wave 4'])
    waves_df = pd.concat([stock_df, waves], axis=1)
    waves_df.rename(columns={0: 'Major Wave'}, inplace=True)
    return waves_df


import pandas as pd


def corrective_waves(stock_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies the corrective waves of the stock.

    Parameters:
        stock_df (pd.DataFrame): DataFrame containing the stock's price data with 'High' and 'Low' columns

    Returns:
        pd.DataFrame: DataFrame containing the corrective waves of the stock
    """
    price_diff = stock_df['High'] - stock_df['Low']
    max_diff = price_diff.rolling(window=10).max()
    waves = pd.cut(price_diff,
                  bins=[0, max_diff.quantile(0.25), max_diff.quantile(0.5), 
                       max_diff.quantile(0.75), max_diff.max()],
                  labels=['Wave A', 'Wave B', 'Wave C', 'Wave D'])
    waves_df = pd.concat([stock_df, waves], axis=1)
    waves_df.rename(columns={0: 'Corrective Wave'}, inplace=True)
    return waves_df


import pandas as pd


def minor_waves(stock_df: pd.DataFrame) -> pd.DataFrame:
    """Identifies the minor waves of the stock.

    Parameters:
        stock_df (pd.DataFrame): DataFrame containing the stock's price data with 'High' and 'Low' columns

    Returns:
        pd.DataFrame: DataFrame containing the minor waves of the stock
    """
    price_diff = stock_df['High'] - stock_df['Low']
    max_diff = price_diff.rolling(window=5).max()
    waves = pd.cut(price_diff,
                  bins=[0, max_diff.quantile(0.25), max_diff.quantile(0.5), 
                       max_diff.quantile(0.75), max_diff.max()],
                  labels=['Wave i', 'Wave ii', 'Wave iii', 'Wave iv'])
    waves_df = pd.concat([stock_df, waves], axis=1)
    waves_df.rename(columns={0: 'Minor Wave'}, inplace=True)
    return waves_df


import pandas as pd


import pandas as pd

def elliot_wave_steps_3_4(major_wave_df: pd.DataFrame, wave_dfs: list) -> tuple:
    """Determine corrective waves and price targets based on Elliott Wave analysis.

    Parameters:
        major_wave_df (pd.DataFrame): DataFrame containing major wave data
        wave_dfs (list): List of DataFrames containing wave data

    Returns:
        tuple: (corrective_waves, price_targets)
    """
    corrective_waves = []
    for i, wave_df in enumerate(wave_dfs):
        if len(wave_df) > 0:
            if major_wave_df.iloc[i]['type'] == 'Bullish':
                if wave_df.iloc[-1]['close'] < wave_df.iloc[-2]['close']:
                    corrective_waves.append(wave_df)
            elif major_wave_df.iloc[i]['type'] == 'Bearish':
                if wave_df.iloc[-1]['close'] > wave_df.iloc[-2]['close']:
                    corrective_waves.append(wave_df)

    price_targets = []
    for i, wave_df in enumerate(corrective_waves):
        if len(wave_df) > 0:
            if major_wave_df.iloc[i]['type'] == 'Bullish':
                wave_high = wave_df['close'].max()
                wave_low = wave_df['close'].min()
                price_targets.append(wave_high + (wave_high - wave_low))
            elif major_wave_df.iloc[i]['type'] == 'Bearish':
                wave_high = wave_df['close'].max()
                wave_low = wave_df['close'].min()
                price_targets.append(wave_low - (wave_high - wave_low))

    return corrective_waves, price_targets
def elliot_wave_steps_5_6(price_targets: list, current_price: float) -> tuple:
    """Determine buy/sell signals and stop loss/take profit levels based on Elliott Wave analysis.

    Parameters:
        price_targets (list): List of price targets
        current_price (float): Current price

    Returns:
        tuple: (buy_or_sell, stop_loss_levels, take_profit_levels)
    """
    buy_or_sell = []
    stop_loss_levels = []
    take_profit_levels = []
    
    for target in price_targets:
        if current_price > target:
            buy_or_sell.append('Sell')
            stop_loss_levels.append(target + (target - current_price))
            take_profit_levels.append(current_price - (target - current_price))
        elif current_price < target:
            buy_or_sell.append('Buy')
            stop_loss_levels.append(target - (current_price - target))
            take_profit_levels.append(current_price + (current_price - target))
        else:
            buy_or_sell.append('Hold')
            stop_loss_levels.append(current_price - (target - current_price))
            take_profit_levels.append(current_price + (target - current_price))

    return buy_or_sell, stop_loss_levels, take_profit_levels
import pandas as pd
import numpy as np











import pandas as pd
import numpy as np
'''
def fischer_transform(df, n=10):
    """
    Calculates the Fischer Transformation for a given stock dataframe.
    Args:
        df (pd.DataFrame): The stock dataframe.
        n (int): The number of periods to use for calculation.
    Returns:
        pd.DataFrame: The Fischer Transform values.
    """
    df['max'] = df['High'].rolling(n).max()
    df['min'] = df['Low'].rolling(n).min()
    df['range'] = df['max'] - df['min']
    df['center'] = (df['max'] + df['min']) / 2
    df['x'] = 2 * ((df['Close'] - df['center']) / df['range'])
    df['fischer'] = np.log((np.exp(2 * df['x']) + 1) / (np.exp(2 * df['x']) - 1))
    return df['fischer']
'''

import numpy as np
import pandas as pd

def hurst_exponent(df: pd.DataFrame, lags: list = None) -> float:
    """Calculate the Hurst Exponent for a given stock DataFrame.

    The Hurst Exponent measures the long-term memory of a time series. It relates
    to the autocorrelations of the time series and the rate at which these decrease
    as the lag between pairs of values increases.

    Parameters:
        df (pd.DataFrame): DataFrame containing the stock's price data with 'Close' column
        lags (list, optional): List of lags to use for calculation. Defaults to range(2, 100)

    Returns:
        float: The Hurst Exponent value. Values:
            - H < 0.5: Time series is mean reverting
            - H = 0.5: Time series is random walk
            - H > 0.5: Time series is trending
    """
    if not lags:
        lags = range(2, 100)
    ts = df['Close'].values
    tau = [np.std(np.subtract(ts[lag:], ts[:-lag])) for lag in lags]
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    return poly[0] * 2.0
import pandas as pd




import pandas as pd
import numpy as np






def renko(df: pd.DataFrame, brick_size: float) -> pd.DataFrame:
    """Calculate Renko chart data for a given DataFrame.

    Renko charts filter out minor price movements to better identify the trend.

    Parameters:
        df (pd.DataFrame): DataFrame with 'date', 'close' columns
        brick_size (float): Size of each brick in price units

    Returns:
        pd.DataFrame: DataFrame containing Renko chart data with columns:
            - date: Date of the brick
            - open: Opening price of the brick
            - high: High price of the brick
            - low: Low price of the brick
            - close: Closing price of the brick
    """
    renko_df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close'])
    current_price = df.iloc[0]['close']
    prev_price = current_price
    direction = 0  # 1 for up, -1 for down
    
    for i in range(len(df)):
        if abs(current_price - prev_price) >= brick_size:
            num_bricks = int(abs(current_price - prev_price) // brick_size)
            for j in range(num_bricks):
                direction = 1 if current_price > prev_price else -1
                renko_df = pd.concat([renko_df, pd.DataFrame({
                    'date': [df.iloc[i]['date']],
                    'open': [prev_price],
                    'high': [prev_price + direction * brick_size],
                    'low': [prev_price - direction * brick_size],
                    'close': [current_price]
                })], ignore_index=True)
                prev_price += direction * brick_size
        current_price = df.iloc[i]['close']
    
    return renko_df


def std_dev_channel(df: pd.DataFrame, n: int, num_std_dev: int = 2) -> pd.DataFrame:
    """Calculate Standard Deviation Channel data.

    The Standard Deviation Channel helps identify potential support and resistance
    levels based on price volatility.

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' column
        n (int): Window size for calculations
        num_std_dev (int): Number of standard deviations for bands. Defaults to 2

    Returns:
        pd.DataFrame: DataFrame with columns:
            - date: Date of the calculation
            - rolling_mean: n-period moving average
            - upper_band: Upper channel band
            - lower_band: Lower channel band
    """
    rolling_mean = df['close'].rolling(window=n).mean()
    rolling_std = df['close'].rolling(window=n).std()
    upper_band = rolling_mean + num_std_dev * rolling_std
    lower_band = rolling_mean - num_std_dev * rolling_std
    
    return pd.DataFrame({
        'date': df['date'],
        'rolling_mean': rolling_mean,
        'upper_band': upper_band,
        'lower_band': lower_band
    })


'''
def chandelier_exit(high, low, close, atr_period=22, multiplier=3.0):
    atr = ta.average_true_range(high, low, close, atr_period)
    long_exit = close - (atr * multiplier)
    short_exit = close + (atr * multiplier)
    return long_exit, short_exit
def bressert_dss(close, length=8, smoothing_length=8, double_smoothing_length=8):
    smoothed = ta.sma(close, length)
    double_smoothed = ta.sma(smoothed, length)
    stoch_k = (close - smoothed) / (double_smoothed - smoothed)
    stoch_d = ta.sma(stoch_k, smoothing_length)
    dss = ta.sma(stoch_d, double_smoothing_length)
    return dss
def chop_zone_oscillator(high, low, close, period=14, multiplier=1.5):
    atr = ta.average_true_range(high, low, close, period)
    tr = ta.true_range(high, low, close)
    cz = atr / (multiplier * np.sqrt(tr))
    return cz
'''

def standard_error(close: pd.Series, period: int = 20) -> pd.Series:
    """Calculate the Standard Error of a price series.

    The Standard Error measures the standard deviation of sample means and can be
    used to estimate price volatility.

    Parameters:
        close (pd.Series): Series of closing prices
        period (int): Rolling window period. Defaults to 20

    Returns:
        pd.Series: Standard Error values
    """
    return close.rolling(period).std() / np.sqrt(period)


import pandas as pd
import numpy as np


def correlation_coefficient(df: pd.DataFrame, x_col: str, y_col: str, period: int) -> pd.DataFrame:
    """Compute rolling correlation coefficient between two columns.

    Parameters:
        df (pd.DataFrame): Input DataFrame
        x_col (str): Column name for first variable
        y_col (str): Column name for second variable
        period (int): Rolling window period

    Returns:
        pd.DataFrame: DataFrame with correlation coefficients
    """
    rolling_corr = df[x_col].rolling(window=period).corr(df[y_col])
    return pd.DataFrame(rolling_corr, columns=['correlation_coefficient'])






import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



'''
def pvt(df):
    close, volume = df['Close'], df['Volume']
    pvt = ((close - close.shift(1)) / close.shift(1)) * volume
    return pvt.cumsum()
'''




import numpy as np



import pandas as pd

'''
def pivot_points(stock_df):
    """
    Computes and returns pivot points, support and resistance levels
    based on the previous period's high, low and close prices of a stock.

    Parameters:
    stock_df (pandas.DataFrame): DataFrame containing the OHLC data of a stock

    Returns:
    pandas.DataFrame: DataFrame containing the pivot points, support and resistance levels
    """
    prev_close = stock_df['Close'].shift(1)
    prev_high = stock_df['High'].shift(1)
    prev_low = stock_df['Low'].shift(1)

    pivot_point = (prev_high + prev_low + prev_close) / 3
    resistance_1 = (2 * pivot_point) - prev_low
    resistance_2 = pivot_point + (prev_high - prev_low)
    resistance_3 = prev_high + 2 * (pivot_point - prev_low)
    support_1 = (2 * pivot_point) - prev_high
    support_2 = pivot_point - (prev_high - prev_low)
    support_3 = prev_low - 2 * (prev_high - pivot_point)

    pivot_df = pd.DataFrame({'Pivot': pivot_point, 'R1': resistance_1, 'R2': resistance_2,
                             'R3': resistance_3, 'S1': support_1, 'S2': support_2, 'S3': support_3})

    return pivot_df
'''


'''
def swing_index(high, low, close, prev_high, prev_low, prev_close):
    """
    Calculates the Swing Index for a given stock using the High, Low, and Close prices.

    Parameters:
    -----------
    high: pandas Series
        Series containing the High prices of the stock.
    low: pandas Series
        Series containing the Low prices of the stock.
    close: pandas Series
        Series containing the Close prices of the stock.
    prev_high: pandas Series
        Series containing the previous day's High prices of the stock.
    prev_low: pandas Series
        Series containing the previous day's Low prices of the stock.
    prev_close: pandas Series
        Series containing the previous day's Close prices of the stock.

    Returns:
    --------
    pandas Series
        Series containing the Swing Index values for each day in the input Series.
    """
    pivot = ((high + low + close) / 3).shift(1)
    prev_pivot = ((prev_high + prev_low + prev_close) / 3).shift(1)
    r1 = abs(high - prev_pivot)
    r2 = abs(low - prev_pivot)
    r3 = abs(high - low)
    r = pd.concat([r1, r2, r3], axis=1).max(axis=1)
    k = pd.Series(0.0, index=high.index)
    for i in range(1, len(high)):
        if high[i] >= prev_high[i]:
            bp = high[i]
        else:
            bp = prev_high[i]
        if low[i] <= prev_low[i]:
            sp = low[i]
        else:
            sp = prev_low[i]
        if close[i] > prev_close[i]:
            t = max(high[i] - prev_close[i], prev_close[i] - prev_low[i])
        elif close[i] < prev_close[i]:
            t = max(low[i] - prev_close[i], prev_close[i] - high[i])
        else:
            t = high[i] - low[i]
        if t == 0:
            rsi = 0
        else:
            rsi = 50 * ((close[i] - prev_close[i]) + 0.5 * (close[i] - prev_open[i]) + 0.25 * (
                        prev_close[i] - prev_open[i])) / t
        si = bp - sp
        si = si + (0.5 * si / r[i]) * abs(si / r[i]) + 0.25 * k[i - 1]
        if abs(si) < 1:
            si = 0
        k[i] = si * rsi + (1 - rsi) * k[i - 1]
    return k
'''
import pandas as pd


def alpha_beta_ratio(df: pd.DataFrame, window: int) -> pd.Series:
    """Calculate the Alpha-Beta ratio for a given stock DataFrame.

    The Alpha-Beta ratio measures the relationship between excess returns (alpha)
    and market sensitivity (beta).

    :param df: DataFrame containing market data with 'Close' column
    :type df: pd.DataFrame
    :param window: Rolling window period for calculations
    :type window: int
    :return: Series containing Alpha-Beta ratio values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing

    The ratio interpretation:
        * > 1: Alpha dominates, indicating strong stock-specific performance
        * = 1: Balanced alpha and beta influence
        * < 1: Beta dominates, indicating strong market influence

    Example::

        df = pd.DataFrame({
            'Close': [100, 101, 99, 102]
        })
        ratio = alpha_beta_ratio(df, window=20)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        close = df['Close']
        returns = close.pct_change()
        alpha = returns.rolling(window).apply(
            lambda x: np.sum(x * (x.index - x.index.mean())) / 
            np.sum((x.index - x.index.mean())**2))
        beta = returns.rolling(window).cov(
            returns.index.to_series().apply(lambda x: x.value)
        ).apply(lambda x: x.iloc[0,1] / x.iloc[1,1])
        
        return pd.Series(alpha / beta, name='Alpha_Beta_Ratio')
    except Exception as e:
        raise ValueError(f"Error calculating Alpha-Beta ratio: {str(e)}")

def atrp(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Calculate the Average True Range Percentage.

    ATR% normalizes the Average True Range by price level, making it comparable
    across different securities.

    :param df: DataFrame containing market data with 'High', 'Low', 'Close' columns
    :type df: pd.DataFrame
    :param n: Period for ATR calculation, defaults to 14
    :type n: int, optional
    :return: Series containing ATR percentage values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing

    The ATR% interpretation:
        * Higher values indicate higher volatility
        * Lower values indicate lower volatility
        * Can be used to adjust position sizes across different securities

    Example::

        df = pd.DataFrame({
            'High': [100, 101, 99],
            'Low': [98, 99, 97],
            'Close': [99, 100, 98]
        })
        atr_pct = atrp(df, n=14)
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        tr = np.maximum(df['High'] - df['Low'], 
                       np.abs(df['High'] - df['Close'].shift()))
        tr = np.maximum(tr, np.abs(df['Low'] - df['Close'].shift()))
        atr = pd.Series(tr).rolling(n).mean()
        return pd.Series(atr / df['Close'] * 100, name='ATR_Percent')
    except Exception as e:
        raise ValueError(f"Error calculating ATR Percentage: {str(e)}")

def adaptive_ma(df: pd.DataFrame, n: int = 10, 
               fast_w: float = 2/(2+1), slow_w: float = 2/(30+1)) -> pd.Series:
    """Calculate the Adaptive Moving Average.

    AMA adjusts its smoothing based on market conditions, responding quickly to
    trending markets and slowly to ranging markets.

    :param df: DataFrame containing market data with 'Close' column
    :type df: pd.DataFrame
    :param n: Period for initial moving average, defaults to 10
    :type n: int, optional
    :param fast_w: Fast weight factor, defaults to 2/(2+1)
    :type fast_w: float, optional
    :param slow_w: Slow weight factor, defaults to 2/(30+1)
    :type slow_w: float, optional
    :return: Series containing Adaptive Moving Average values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing

    The AMA interpretation:
        * Faster response in trending markets
        * Slower response in ranging markets
        * Crossovers with price can signal trend changes

    Example::

        df = pd.DataFrame({
            'Close': [100, 101, 99, 102]
        })
        ama = adaptive_ma(df, n=10)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        l = len(df)
        ema1 = df['Close'].rolling(n).mean()
        ema2 = pd.Series(np.zeros(l))
        ema3 = pd.Series(np.zeros(l))
        
        for i in range(n, l):
            ema2[i] = ema1[i] * fast_w + ema2[i - 1] * (1 - fast_w)
            ema3[i] = ema1[i] * slow_w + ema3[i - 1] * (1 - slow_w)
            
        dm = abs(ema2 - ema3)
        c1 = fast_w / slow_w
        c2 = (fast_w / slow_w) ** 2
        am = pd.Series(np.zeros(l))
        
        for i in range(n, l):
            am[i] = (c1 - c2 + 1) * ema3[i] - c1 * ema2[i] + c2 * df['Close'][i]
            
        return pd.Series(am, name='Adaptive_MA')
    except Exception as e:
        raise ValueError(f"Error calculating Adaptive Moving Average: {str(e)}")

def lri(df: pd.DataFrame, n: int = 14) -> float:
    """Calculate the Linear Regression Intercept.

    The LRI helps identify potential support/resistance levels based on linear
    regression analysis.

    :param df: DataFrame containing market data with 'Close' column
    :type df: pd.DataFrame
    :param n: Period for regression calculation, defaults to 14
    :type n: int, optional
    :return: Linear regression intercept value
    :rtype: float
    :raises ValueError: If required columns are missing

    The LRI interpretation:
        * Higher values suggest stronger upward bias
        * Lower values suggest stronger downward bias
        * Can be used with slope to assess trend strength

    Example::

        df = pd.DataFrame({
            'Close': [100, 101, 99, 102]
        })
        intercept = lri(df, n=14)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        x = np.arange(n)
        y = df['Close'][-n:].values
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        return intercept
    except Exception as e:
        raise ValueError(f"Error calculating Linear Regression Intercept: {str(e)}")

def arms_adi(df: pd.DataFrame) -> pd.Series:
    """Calculate Arms' Accumulation/Distribution Index.

    The ADI measures the relationship between price and volume to identify
    buying/selling pressure.

    :param df: DataFrame containing market data with 'Close', 'High', 'Low', 'Volume' columns
    :type df: pd.DataFrame
    :return: Series containing ADI values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing

    The ADI interpretation:
        * Rising ADI suggests accumulation (buying pressure)
        * Falling ADI suggests distribution (selling pressure)
        * Divergences with price can signal potential reversals

    Example::

        df = pd.DataFrame({
            'Close': [100, 101, 99],
            'High': [102, 103, 100],
            'Low': [98, 99, 97],
            'Volume': [1000, 1200, 800]
        })
        adi = arms_adi(df)
    """
    try:
        required_columns = ['Close', 'High', 'Low', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        adi = clv * df['Volume']
        return pd.Series(adi.cumsum(), name='Arms_ADI')
    except Exception as e:
        raise ValueError(f"Error calculating Arms ADI: {str(e)}")

def envelope_bands(df: pd.DataFrame, n: int = 20, m: float = 0.02) -> tuple:
    """Calculate Envelope Bands around a moving average.

    Envelope Bands create percentage-based channels around a moving average to
    identify potential overbought and oversold conditions.

    :param df: DataFrame containing market data with 'Close' column
    :type df: pd.DataFrame
    :param n: Period for moving average calculation, defaults to 20
    :type n: int, optional
    :param m: Multiplier for band width, defaults to 0.02 (2%)
    :type m: float, optional
    :return: Tuple containing (upper_band, lower_band)
    :rtype: tuple
    :raises ValueError: If required columns are missing

    The Envelope Bands interpretation:
        * Price above upper band suggests overbought
        * Price below lower band suggests oversold
        * Band width can be adjusted based on volatility
        * Can be used with various types of moving averages

    Example::

        df = pd.DataFrame({
            'Close': [100, 101, 99, 102]
        })
        upper, lower = envelope_bands(df, n=20, m=0.02)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")
            
        sma = df['Close'].rolling(window=n).mean()
        upper_band = sma * (1 + m)
        lower_band = sma * (1 - m)
        return upper_band, lower_band
    except Exception as e:
        raise ValueError(f"Error calculating Envelope Bands: {str(e)}")


'''
def lri(df, n=14):
    x = np.arange(n)
    y = df['Close'][-n:].values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return intercept
def arms_adi(df):
    clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
    adi = clv * df['Volume']
    return adi.cumsum()
'''




def polarized_fractal_efficiency(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Calculate the Polarized Fractal Efficiency (PFE) indicator.

    PFE measures the efficiency of price movements by comparing directional
    movement to total movement, helping identify trending vs choppy conditions.

    :param df: DataFrame containing market data with 'High' and 'Low' columns
    :type df: pd.DataFrame
    :param n: Number of periods for calculation, defaults to 10
    :type n: int, optional
    :return: Series containing PFE values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing

    The PFE interpretation:
        * Values near +100: Strong upward trend efficiency
        * Values near -100: Strong downward trend efficiency
        * Values near 0: Choppy, inefficient price movement
        * Trend changes often occur after extreme readings

    Example::

        df = pd.DataFrame({
            'High': [100, 101, 99],
            'Low': [98, 99, 97]
        })
        pfe = polarized_fractal_efficiency(df, n=10)
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        hl_avg = (df['High'] + df['Low']) / 2
        change = hl_avg.diff()
        total_range = df['High'] - df['Low']
        
        up = (change > 0) & (total_range > 0)
        down = (change < 0) & (total_range > 0)
        
        up_fe = np.abs(change[up] / total_range[up])
        down_fe = np.abs(change[down] / total_range[down])
        
        up_fe = up_fe.fillna(0)
        down_fe = down_fe.fillna(0)
        
        polarized = (up_fe - down_fe).rolling(window=n, min_periods=1).mean()
        return pd.Series(polarized, name='PFE')
    except Exception as e:
        raise ValueError(f"Error calculating PFE: {str(e)}")











def ergo(df: pd.DataFrame, short_period: int = 10, long_period: int = 30, 
         signal_period: int = 20) -> pd.DataFrame:
    """Calculate the ERGO indicator.

    ERGO measures market volatility and momentum to identify potential trend changes.

    Parameters:
        df (pd.DataFrame): DataFrame with 'close' column
        short_period (int): Short-term period. Defaults to 10
        long_period (int): Long-term period. Defaults to 30
        signal_period (int): Signal line period. Defaults to 20

    Returns:
        pd.DataFrame: DataFrame with columns:
            - ergo: ERGO line values
            - signal: Signal line values
    """
    change = df['close'].diff()
    volatility = change.abs().rolling(window=short_period).sum()
    ema_volatility = volatility.ewm(span=long_period, min_periods=long_period).mean()
    ergo = (change / ema_volatility) * 100
    signal = ergo.ewm(span=signal_period, min_periods=signal_period).mean()
    
    return pd.DataFrame({
        'ergo': ergo,
        'signal': signal
    })


def cfo(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Chande Forecast Oscillator (CFO).

    The CFO compares the current price to a forecasted price based on linear regression.

    Parameters:
        df (pd.DataFrame): DataFrame with 'high', 'low', 'close' columns
        period (int): Lookback period. Defaults to 14

    Returns:
        pd.Series: CFO values
    """
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    roc = typical_price.pct_change(period)
    forecast = typical_price.shift(period) + (period * roc)
    error = typical_price - forecast
    deviation = error.rolling(window=period).std()
    cfo = (error / deviation) * 100
    
    return pd.Series(cfo, name='CFO')






def parabolic_sar_down(df: pd.DataFrame, acceleration_factor: float = 0.02, max_factor: float = 0.2) -> pd.Series:
    """Calculate the Parabolic SAR (Stop And Reverse) indicator for downtrends.

    The Parabolic SAR is a trend-following indicator that helps identify potential
    stop and reverse points in a downtrend. It adjusts automatically as the trend
    develops and accelerates.

    :param df: DataFrame containing market data with 'High' and 'Low' prices
    :type df: pd.DataFrame
    :param acceleration_factor: Initial acceleration factor, defaults to 0.02
    :type acceleration_factor: float, optional
    :param max_factor: Maximum acceleration factor, defaults to 0.2
    :type max_factor: float, optional
    :return: Series of SAR values for downtrend
    :rtype: pd.Series
    :raises ValueError: If required columns are missing or calculation fails

    The SAR values can be interpreted as follows:

    - SAR points above price indicate downtrend
    - SAR points below price indicate potential trend reversal
    - Distance between SAR and price shows trend strength
    - Acceleration factor increases with trend strength

    Example::

        df = pd.DataFrame({
            'High': [44.55, 44.77, 44.11],
            'Low': [44.12, 44.25, 43.72]
        })
        sar = parabolic_sar_down(df)
    """
    try:
        required_columns = ['High', 'Low']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        # Initialize variables
        af = acceleration_factor
        max_af = max_factor
        ep = df['High'][0]
        sar = df['High'][0]
        trend = -1  # downtrend
        sar_list = [sar]

        for i in range(1, len(df)):
            # Update extreme price (EP) and acceleration factor (AF)
            if df['Low'][i] < ep:
                ep = df['Low'][i]
                af = min(af + acceleration_factor, max_factor)
            
            # Check for trend changes
            if trend == 1:
                if df['Low'][i] <= sar:
                    trend = -1
                    sar = ep
                    ep = df['High'][i]
                    af = acceleration_factor
            else:
                if df['High'][i] >= sar:
                    trend = 1
                    sar = ep
                    ep = df['Low'][i]
                    af = acceleration_factor

            # Calculate SAR based on trend
            if trend == 1:
                sar = sar + af * (ep - sar)
                sar = min(sar, df['Low'][i - 1], df['Low'][i - 2])
            else:
                sar = sar - af * (sar - ep)
                sar = max(sar, df['High'][i - 1], df['High'][i - 2])
            
            sar_list.append(sar)

        return pd.Series(sar_list, index=df.index, name='SAR_Down')
    except Exception as e:
        raise ValueError(f"Error calculating Parabolic SAR Down: {str(e)}")

def elder_force_index(df: pd.DataFrame, period_1: int = 2, period_2: int = 13) -> pd.Series:
    """Calculate Elder's Force Index indicator.

    The Force Index measures the power behind price movements by considering price
    changes and volume. It helps identify potential reversals and trend strength.

    :param df: DataFrame containing market data with 'Close' and 'Volume'
    :type df: pd.DataFrame
    :param period_1: Initial smoothing period, defaults to 2
    :type period_1: int, optional
    :param period_2: Second smoothing period, defaults to 13
    :type period_2: int, optional
    :return: Force Index values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing or calculation fails

    The Force Index can be interpreted as follows:

    - Positive values indicate buying pressure
    - Negative values indicate selling pressure
    - Divergences with price suggest potential reversals
    - Crosses above/below zero signal trend changes

    Example::

        df = pd.DataFrame({
            'Close': [44.34, 44.44, 43.95],
            'Volume': [1000, 1200, 900]
        })
        force = elder_force_index(df)
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        force_index = (df['Close'].diff(period_1) * df['Volume']) / 1000000000
        ema_force_index = force_index.rolling(period_2).mean()
        return pd.Series(ema_force_index, name='Force_Index')
    except Exception as e:
        raise ValueError(f"Error calculating Elder's Force Index: {str(e)}")

def chande_qstick(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate Chande's Qstick indicator.

    The Qstick indicator measures the relative position of closes to opens over a
    given period, helping identify the dominance of black or white candlesticks
    and potential trend bias.

    :param df: DataFrame containing market data with 'Open' and 'Close' prices
    :type df: pd.DataFrame
    :param period: Lookback period for calculation, defaults to 14
    :type period: int, optional
    :return: Qstick values
    :rtype: pd.Series
    :raises ValueError: If required columns are missing or calculation fails

    The Qstick values can be interpreted as follows:

    - Values above zero indicate bullish bias (more white candlesticks)
    - Values below zero indicate bearish bias (more black candlesticks)
    - Extreme values suggest strong trending conditions
    - Zero line crosses may signal trend changes

    Example::

        df = pd.DataFrame({
            'Open': [44.12, 44.25, 43.72],
            'Close': [44.34, 44.44, 43.95]
        })
        qstick = chande_qstick(df)
    """
    try:
        required_columns = ['Open', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        qstick = (df['Close'] - df['Open'].rolling(period).mean()).rolling(period).sum()
        return pd.Series(qstick, name='Qstick')
    except Exception as e:
        raise ValueError(f"Error calculating Qstick: {str(e)}")

