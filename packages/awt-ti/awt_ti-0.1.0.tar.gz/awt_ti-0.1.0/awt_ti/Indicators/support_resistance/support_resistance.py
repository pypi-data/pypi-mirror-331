"""Technical Analysis Support and Resistance Indicators.

This module implements various technical analysis support and resistance indicators
used in financial markets. Each indicator helps identify potential price levels
where the market may find support (price stops falling) or resistance (price stops rising).

Note:
    All functions expect a pandas DataFrame with at least these columns:
    ['Open', 'High', 'Low', 'Close']
"""

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

def find_support_resistance(df: pd.DataFrame, price_col: str = 'Close', 
                          window: int = 5) -> pd.DataFrame:
    """Find support and resistance levels using local extrema.

    Identifies potential support and resistance levels by finding local minima
    and maxima in the price series.

    Args:
        df (pd.DataFrame): DataFrame containing market data with price column
        price_col (str, optional): Column name for price data. Defaults to 'Close'.
        window (int, optional): Window size for finding extrema. Defaults to 5.

    Returns:
        pd.DataFrame: Original DataFrame with added columns:
            - support: Support levels (local minima)
            - resistance: Resistance levels (local maxima)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [100, 101, 99, 102, 98, 103]
        ... })
        >>> result = find_support_resistance(df)
    """
    try:
        if price_col not in df.columns:
            raise ValueError(f"DataFrame must contain column: {price_col}")

        df = df.copy()
        
        # Find local minima (support)
        df['support'] = df.iloc[argrelextrema(
            df[price_col].values, np.less_equal, order=window)[0]][price_col]

        # Find local maxima (resistance)
        df['resistance'] = df.iloc[argrelextrema(
            df[price_col].values, np.greater_equal, order=window)[0]][price_col]

        return df
    except Exception as e:
        raise ValueError(f"Error finding support/resistance levels: {str(e)}")

def fibonacci_retracement(df: pd.DataFrame, high_col: str = 'High', 
                        low_col: str = 'Low', 
                        levels: list = [0.236, 0.382, 0.5, 0.618, 0.786]) -> pd.DataFrame:
    """Calculate Fibonacci retracement levels.

    Computes Fibonacci retracement levels based on the highest high and lowest low
    prices in the given period.

    Args:
        df (pd.DataFrame): DataFrame containing market data
        high_col (str, optional): Column name for high prices. Defaults to 'High'.
        low_col (str, optional): Column name for low prices. Defaults to 'Low'.
        levels (list, optional): Fibonacci levels to calculate. 
            Defaults to [0.236, 0.382, 0.5, 0.618, 0.786].

    Returns:
        pd.DataFrame: DataFrame containing Fibonacci retracement levels:
            - One column for each specified level
            - Column names are percentage strings (e.g., '23.6%')

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [105, 104, 106],
        ...     'Low': [98, 97, 99]
        ... })
        >>> fib_levels = fibonacci_retracement(df)
    """
    try:
        required_columns = [high_col, low_col]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        # Compute highest high and lowest low
        highest_price = df[high_col].max()
        lowest_price = df[low_col].min()
        price_range = highest_price - lowest_price

        # Calculate retracement levels
        retracement_values = {f"{level*100:.1f}%": highest_price - price_range * level 
                            for level in levels}

        return pd.DataFrame(retracement_values, index=[0])
    except Exception as e:
        raise ValueError(f"Error calculating Fibonacci retracements: {str(e)}")


def fibonacci_arcs(df: pd.DataFrame, low_col: str = 'Low', high_col: str = 'High', 
                   levels: list = [0, 0.236, 0.382, 0.5, 0.618, 1]) -> None:
    """
    Computes and plots Fibonacci Arcs based on the high and low values in a given stock DataFrame.

    Fibonacci Arcs are used to identify potential support and resistance levels based on percentage 
    retracements from a significant price range.

    Args:
        df (pd.DataFrame): DataFrame containing stock data with required high and low columns.
        low_col (str, optional): Column name for the lowest price (default is "Low").
        high_col (str, optional): Column name for the highest price (default is "High").
        levels (list, optional): List of Fibonacci retracement levels (default is [0, 0.236, 0.382, 0.5, 0.618, 1]).

    Returns:
        None: Displays the Fibonacci Arcs plot.

    Example:
        >>> df = pd.DataFrame({"Low": [100, 105, 110], "High": [150, 160, 170], "Close": [145, 155, 165]})
        >>> fibonacci_arcs(df)
    """
    # Compute the high and low values for the indicator
    low_val = df[low_col].min()
    high_val = df[high_col].max()

    # Compute the range and mid point
    range_val = high_val - low_val
    mid_point = low_val + range_val / 2

    # Compute Fibonacci levels
    levels_val = [mid_point - level * range_val for level in levels[::-1]]

    # Plot the Fibonacci Arcs
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    for level in levels_val:
        plt.axhline(y=level, linestyle='--', label=f'Fibonacci Arc {round(mid_point - level, 2)}')
    
    plt.legend()
    plt.title('Fibonacci Arcs')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()


def fibonacci_fan(df: pd.DataFrame, low_col: str = 'Low', high_col: str = 'High', 
                  levels: list = [0, 0.236, 0.382, 0.5, 0.618, 1]) -> None:
    """
    Computes and plots Fibonacci Fan lines based on price retracements.

    Fibonacci Fans help identify potential trend lines and resistance/support levels.

    Args:
        df (pd.DataFrame): DataFrame containing stock data with required high and low columns.
        low_col (str, optional): Column name for the lowest price (default is "Low").
        high_col (str, optional): Column name for the highest price (default is "High").
        levels (list, optional): List of Fibonacci retracement levels (default is [0, 0.236, 0.382, 0.5, 0.618, 1]).

    Returns:
        None: Displays the Fibonacci Fan plot.

    Example:
        >>> df = pd.DataFrame({"Low": [100, 105, 110], "High": [150, 160, 170], "Close": [145, 155, 165]})
        >>> fibonacci_fan(df)
    """
    # Compute the high and low values for the indicator
    low_val = df[low_col].min()
    high_val = df[high_col].max()

    # Compute the range and mid point
    range_val = high_val - low_val
    mid_point = low_val + range_val / 2

    # Compute Fibonacci Fan levels
    levels_val = [mid_point - level * range_val for level in levels[::-1]]

    # Plot Fibonacci Fan lines
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    for i, level in enumerate(levels_val):
        plt.plot(df.index, [(i + 1) * level - i * mid_point] * len(df.index),
                 linestyle='--', label=f'Fibonacci Fan {round(mid_point - level, 2)}')

    plt.legend()
    plt.title('Fibonacci Fan')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()


def fibonacci_time_zone(df: pd.DataFrame, start_date: str, end_date: str, 
                        high: str = 'High', low: str = 'Low') -> list:
    """
    Computes Fibonacci Time Zones, which help identify potential time-based support and resistance levels.

    Fibonacci Time Zones are calculated based on the high and low prices over a given time period.

    Args:
        df (pd.DataFrame): DataFrame containing stock data with a date index.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        high (str, optional): Column name for the highest price (default is "High").
        low (str, optional): Column name for the lowest price (default is "Low").

    Returns:
        list: A list of computed Fibonacci Time Zones values.

    Example:
        >>> df = pd.DataFrame({"Date": ["2023-01-01", "2023-02-01", "2023-03-01"], 
                               "High": [150, 160, 170], "Low": [100, 105, 110]})
        >>> df.set_index("Date", inplace=True)
        >>> fibonacci_time_zone(df, "2023-01-01", "2023-03-01")
    """
    # Filter the dataframe based on the start and end dates
    df = df.loc[start_date:end_date]

    # Compute the highest high and lowest low over the time period
    max_high = df[high].max()
    min_low = df[low].min()

    # Compute the range of prices over the time period
    price_range = max_high - min_low

    # Compute the Fibonacci time zones
    time_zones = [min_low + price_range * level for level in
                  [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.236, 1.382, 1.618]]

    return time_zones



def max_drawdown(df: pd.DataFrame) -> float:
    """Calculate the maximum drawdown from peak to trough.

    Maximum drawdown measures the largest peak-to-trough decline in the
    asset's price, expressed as a percentage.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices

    Returns:
        float: Maximum drawdown value as a decimal (e.g., 0.25 = 25% drawdown)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [100, 95, 90, 95, 85]
        ... })
        >>> drawdown = max_drawdown(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        # Calculate running maximum
        cummax = df['Close'].cummax()
        
        # Calculate drawdown
        drawdown = (df['Close'] - cummax) / cummax
        
        return abs(drawdown.min())
    except Exception as e:
        raise ValueError(f"Error calculating maximum drawdown: {str(e)}")


def relative_extremes(df: pd.DataFrame, window: int = 100) -> pd.DataFrame:
    """Calculate relative price extremes.

    Identifies relative maximum and minimum values over a rolling window,
    useful for finding potential support and resistance zones.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Close': Closing prices
        window (int, optional): Rolling window size. Defaults to 100.

    Returns:
        pd.DataFrame: DataFrame containing:
            - relative_max: Relative maximum values
            - relative_min: Relative minimum values

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [100, 102, 98, 103, 97]
        ... })
        >>> extremes = relative_extremes(df)
    """
    try:
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        # Calculate rolling extremes
        roll_max = df['Close'].rolling(window=window, min_periods=1).max()
        roll_min = df['Close'].rolling(window=window, min_periods=1).min()

        # Calculate relative values
        rel_max = df['Close'] / roll_max - 1
        rel_min = df['Close'] / roll_min - 1

        return pd.DataFrame({
            'relative_max': rel_max,
            'relative_min': rel_min
        })
    except Exception as e:
        raise ValueError(f"Error calculating relative extremes: {str(e)}")


def support_resistance_points(df: pd.DataFrame, lookback: int = 100, 
                           threshold: float = 0.02) -> dict:
    """Identify significant support and resistance points.

    Finds potential support and resistance points by analyzing price movements
    relative to historical highs and lows.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
        lookback (int, optional): Lookback period for analysis. Defaults to 100.
        threshold (float, optional): Minimum price change threshold. Defaults to 0.02.

    Returns:
        dict: Dictionary containing:
            - 'support': Series of support points
            - 'resistance': Series of resistance points

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [105, 104, 106],
        ...     'Low': [98, 97, 99],
        ...     'Close': [102, 101, 103]
        ... })
        >>> points = support_resistance_points(df)
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        # Calculate rolling extremes
        roll_max = df['Close'].rolling(window=lookback, min_periods=1).max()
        roll_min = df['Close'].rolling(window=lookback, min_periods=1).min()

        # Calculate relative price changes
        rel_max = df['Close'] / roll_max - 1
        rel_min = df['Close'] / roll_min - 1

        # Identify support and resistance points
        support = df.loc[rel_min >= threshold, 'Low']
        resistance = df.loc[rel_max >= threshold, 'High']

        return {'support': support, 'resistance': resistance}
    except Exception as e:
        raise ValueError(f"Error calculating support/resistance points: {str(e)}")


def calculate_pivot_points(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate classic pivot points and support/resistance levels.

    Computes pivot points and associated support/resistance levels based on
    the previous period's high, low, and close prices using the floor trader's method.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices

    Returns:
        pd.DataFrame: DataFrame containing:
            - PP: Pivot Point (main pivot level)
            - R1, R2, R3: Resistance levels 1, 2, and 3
            - S1, S2, S3: Support levels 1, 2, and 3

    Notes:
        The pivot point calculations use the floor trader's method:
        - PP = (H + L + C) / 3
        - R1 = (2 × PP) - L
        - S1 = (2 × PP) - H
        - R2 = PP + (H - L)
        - S2 = PP - (H - L)
        - R3 = H + 2(PP - L)
        - S3 = L - 2(H - PP)

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [105, 104, 106],
        ...     'Low': [98, 97, 99],
        ...     'Close': [102, 101, 103]
        ... })
        >>> pivots = calculate_pivot_points(df)
    """
    try:
        required_columns = ['High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        df = df.copy()

        # Calculate pivot point
        pp = (df['High'] + df['Low'] + df['Close']) / 3

        # Calculate support and resistance levels
        r1 = 2 * pp - df['Low']  # First resistance
        s1 = 2 * pp - df['High']  # First support
        r2 = pp + (df['High'] - df['Low'])  # Second resistance
        s2 = pp - (df['High'] - df['Low'])  # Second support
        r3 = df['High'] + 2 * (pp - df['Low'])  # Third resistance
        s3 = df['Low'] - 2 * (df['High'] - pp)  # Third support

        return pd.DataFrame({
            'PP': pp,  # Pivot Point
            'R1': r1, 'R2': r2, 'R3': r3,  # Resistance levels
            'S1': s1, 'S2': s2, 'S3': s3   # Support levels
        })
    except Exception as e:
        raise ValueError(f"Error calculating pivot points: {str(e)}")
