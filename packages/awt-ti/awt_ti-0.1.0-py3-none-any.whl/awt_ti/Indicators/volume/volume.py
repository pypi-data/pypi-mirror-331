"""Technical Analysis Volume Indicators.

This module implements various technical analysis volume indicators used in financial markets.
Each indicator is implemented as a function that takes a pandas DataFrame containing OHLCV data
and returns the calculated volume indicator values.

Note:
    All functions expect a pandas DataFrame with at least these columns: ['Open', 'High', 'Low', 'Close', 'Volume']
"""

import numpy as np
import pandas as pd
import yfinance

#from Technical_Analysis.Indicators.momentum.momentum import ta_mo_RSI

def ta_volume_vema(df: pd.DataFrame, period: int = 10, column: str = "Volume") -> pd.Series:
    """Calculate the Volume Exponential Moving Average (VEMA).

    The VEMA applies exponential smoothing to volume data, giving more weight to recent
    volume values while maintaining sensitivity to volume changes.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 10.
        column (str, optional): Name of the volume column. Defaults to "Volume".

    Returns:
        pd.Series: VEMA values. Interpretation:
            - Rising VEMA suggests increasing volume trend
            - Falling VEMA suggests decreasing volume trend
            - Can confirm price trends when aligned

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> vema = ta_volume_vema(df)
    """
    try:
        if column not in df.columns:
            raise ValueError(f"DataFrame must contain column: {column}")
            
        return df[column].ewm(span=period, min_periods=0, adjust=False).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Volume EMA: {str(e)}")


def ta_volume_vsma(df: pd.DataFrame, period: int = 10, column: str = "Volume") -> pd.Series:
    """Calculate the Volume Simple Moving Average (VSMA).

    The VSMA provides a smoothed view of volume trends by calculating the arithmetic
    mean of volume over a specified period.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 10.
        column (str, optional): Name of the volume column. Defaults to "Volume".

    Returns:
        pd.Series: VSMA values. Interpretation:
            - Rising VSMA indicates increasing volume trend
            - Falling VSMA indicates decreasing volume trend
            - Crossovers with raw volume can signal volume trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> vsma = ta_volume_vsma(df)
    """
    try:
        if column not in df.columns:
            raise ValueError(f"DataFrame must contain column: {column}")
            
        return df[column].rolling(window=period, min_periods=0).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Volume SMA: {str(e)}")


def ta_volume_volumersi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Volume Relative Strength Index (V-RSI).

    The V-RSI applies the RSI concept to volume data, measuring the momentum of volume
    changes to identify potential volume trend reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: V-RSI values ranging from 0 to 100. Interpretation:
            - Values above 70 indicate overbought volume conditions
            - Values below 30 indicate oversold volume conditions
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> vrsi = ta_volume_volumersi(df)

    References:
        - https://www.investopedia.com/terms/r/rsi.asp
    """
    try:
        if 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Volume' column")
            
        df = df.copy()
        delta = df['Volume'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        vrsi = 100 - (100 / (1 + rs))
        
        return vrsi
    except Exception as e:
        raise ValueError(f"Error calculating Volume RSI: {str(e)}")


# Volume Force Index (VFI)
def vfi(df, period=13):
    vfi = ((df['Close'] - df['Open']) / df['Open']) * df['Volume']
    vfi = vfi.rolling(window=period).sum()
    return vfi

# Volume flow indicator
def ta_volume_VolumeFlowIndicator(df: pd.DataFrame, periods: int = 21) -> pd.Series:
    """Calculate the Volume Flow Indicator (VFI).

    The VFI combines price and volume data to measure the balance between positive
    and negative volume flow, helping identify potential trend strength and reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume
        periods (int, optional): The lookback period. Defaults to 21.

    Returns:
        pd.Series: VFI values. Interpretation:
            - Positive values indicate buying pressure
            - Negative values indicate selling pressure
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11, 44.23, 44.52],
        ...     'Low': [44.12, 44.25, 43.72, 43.98, 44.15],
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33],
        ...     'Volume': [1000, 1200, 900, 1500, 1100]
        ... })
        >>> vfi = ta_volume_VolumeFlowIndicator(df)

    References:
        - https://www.investopedia.com/terms/v/volume-price-trend-indicator.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy()
        mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        mfv = mfm * df['Volume']
        
        cmfv = mfv.rolling(window=periods).sum()
        cvol = df['Volume'].rolling(window=periods).sum()
        
        vfi = cmfv / cvol
        return vfi
    except Exception as e:
        raise ValueError(f"Error calculating Volume Flow Indicator: {str(e)}")


def ta_volume_OBV(df: pd.DataFrame) -> pd.Series:
    """Calculate the On-Balance Volume (OBV).

    OBV is a cumulative indicator that adds volume on up days and subtracts volume
    on down days to show buying and selling pressure over time.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: OBV values. Interpretation:
            - Rising OBV indicates accumulation/buying pressure
            - Falling OBV indicates distribution/selling pressure
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33],
        ...     'Volume': [1000, 1200, 900, 1500, 1100]
        ... })
        >>> obv = ta_volume_OBV(df)

    References:
        - https://www.investopedia.com/terms/o/onbalancevolume.asp
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy()
        obv = []
        previous = 0
        
        for index, row in df.iterrows():
            if row['Close'] > previous:
                current_obv = obv[-1] + row['Volume'] if len(obv) > 0 else row['Volume']
            elif row['Close'] < previous:
                current_obv = obv[-1] - row['Volume'] if len(obv) > 0 else -row['Volume']
            else:
                current_obv = obv[-1] if len(obv) > 0 else 0
                
            obv.append(current_obv)
            previous = row['Close']
            
        return pd.Series(obv, index=df.index)
    except Exception as e:
        raise ValueError(f"Error calculating On-Balance Volume: {str(e)}")


def ta_volume_NVI(df: pd.DataFrame, n: int = 255) -> pd.Series:
    """Calculate the Negative Volume Index (NVI).

    The NVI is a cumulative indicator that only changes on days when volume decreases,
    helping identify smart money movements in low volume periods.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'Volume': Trading volume
        n (int, optional): The lookback period. Defaults to 255.

    Returns:
        pd.Series: NVI values. Interpretation:
            - Rising NVI during low volume suggests smart money buying
            - Falling NVI during low volume suggests smart money selling
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95, 44.03, 44.33],
        ...     'Volume': [1000, 900, 1200, 800, 1100]
        ... })
        >>> nvi = ta_volume_NVI(df)

    References:
        - https://www.investopedia.com/terms/n/nvi.asp
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        nvi = pd.Series(index=df.index, dtype='float64')
        nvi.iloc[0] = 1000
        
        for i in range(1, len(df)):
            if df['Volume'].iloc[i] < df['Volume'].iloc[i - 1]:
                nvi.iloc[i] = nvi.iloc[i - 1] + (df['Close'].iloc[i] - df['Close'].iloc[i - 1]) / \
                             df['Close'].iloc[i - 1] * nvi.iloc[i - 1]
            else:
                nvi.iloc[i] = nvi.iloc[i - 1]
                
        return nvi
    except Exception as e:
        raise ValueError(f"Error calculating Negative Volume Index: {str(e)}")


# split into 2
def calculate_mass_and_force(dataframe, n1=9, n2=25):
    high = dataframe['High']
    low = dataframe['Low']
    close = dataframe['Close']
    volume = dataframe['Volume']

    # Calculate the single-period range for each day
    range = high - low

    # Calculate the Exponential Moving Average (EMA) of the range for the first period
    # Should be ewm?
    ema_range = range.rolling(n1).mean()

    # Calculate the Mass Index for each day
    ema_ratio = ema_range / ema_range.rolling(n1).mean()
    mass_index = ema_ratio.rolling(n1).sum()

    # Calculate the Force Index for each day
    force_index = range * volume
    force_ema = force_index.rolling(n2).mean()

    # Add the calculated values as new columns in the original DataFrame
    dataframe['Mass_Index'] = mass_index
    dataframe['Force_Index'] = force_ema

    return dataframe

def volume_by_price(df, n):
    """Computes the volume by price for a given period."""
    high = df['High'].rolling(n).max()
    low = df['Low'].rolling(n).min()
    price_range = high - low
    num_price_levels = 10
    price_levels = np.linspace(low.iloc[-1], high.iloc[-1], num_price_levels)
    volume_by_price = pd.DataFrame(index=price_levels, columns=['Volume'])
    for i in range(len(price_levels)):
        if i == 0:
            volume_by_price.loc[price_levels[i]] = df['Volume'][df['Close'] <= price_levels[i]].sum()
        elif i == num_price_levels - 1:
            volume_by_price.loc[price_levels[i]] = df['Volume'][df['Close'] > price_levels[i - 1]].sum()
        else:
            volume_by_price.loc[price_levels[i]] = df['Volume'][
                (df['Close'] > price_levels[i - 1]) & (df['Close'] <= price_levels[i])].sum()
    return volume_by_price



def ta_volume_BOP(df: pd.DataFrame) -> pd.Series:
    """Calculate the Balance of Power (BOP) indicator.

    The BOP measures the strength of buyers versus sellers by comparing the closing
    price to the opening price and factoring in volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: BOP values. Interpretation:
            - Positive values indicate buying pressure
            - Negative values indicate selling pressure
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Open': [44.12, 44.25, 43.72],
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> bop = ta_volume_BOP(df)

    References:
        - https://www.investopedia.com/terms/b/bop.asp
    """
    try:
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        df = df.copy()
        bop = ((df['Close'] - df['Open']) / (df['High'] - df['Low'])) * df['Volume']
        return pd.Series(bop, name='BOP')
    except Exception as e:
        raise ValueError(f"Error calculating Balance of Power: {str(e)}")

def calculate_vwap_vwma(dataframe, anchor_date=None, window_size=20):
    # Calculate VWAP
    dataframe['TP'] = (dataframe['High'] + dataframe['Low'] + dataframe['Close']) / 3
    dataframe['TPV'] = dataframe['TP'] * dataframe['Volume']
    dataframe['Cumulative TPV'] = dataframe['TPV'].cumsum()
    dataframe['Cumulative Volume'] = dataframe['Volume'].cumsum()
    dataframe['VWAP'] = dataframe['Cumulative TPV'] / dataframe['Cumulative Volume']

    # Calculate VMA
    dataframe['VWMA'] = dataframe['Volume'].rolling(window=window_size).mean()

    # Calculate Anchored VWAP
    if anchor_date:
        anchor_data = dataframe.loc[:anchor_date]
        anchor_tpv = (anchor_data['High'] + anchor_data['Low'] + anchor_data['Close']) / 3 * anchor_data['Volume']
        anchor_volume = anchor_data['Volume'].sum()
        anchor_vwap = anchor_tpv.sum() / anchor_volume

        dataframe['Anchored VWAP'] = anchor_vwap

    return dataframe.drop(columns=['Cumulative TPV', 'Cumulative Volume'])  # ,'TP', 'TPV',])

def ta_volume_RelativeVolume(df: pd.DataFrame, n: int = 50) -> pd.Series:
    """Calculate the Relative Volume indicator.

    The Relative Volume compares the current volume to the average volume over a
    specified period to identify unusual volume activity.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        n (int, optional): The lookback period. Defaults to 50.

    Returns:
        pd.Series: Relative Volume values. Interpretation:
            - Values above 1 indicate above-average volume
            - Values below 1 indicate below-average volume
            - Spikes may signal significant price movements

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> rv = ta_volume_RelativeVolume(df)

    References:
        - https://www.investopedia.com/terms/r/relativestrength.asp
    """
    try:
        if 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Volume' column")
            
        vol = df['Volume'].rolling(n).sum()
        rv = df['Volume'] / vol
        return pd.Series(rv, name='RelativeVolume')
    except Exception as e:
        raise ValueError(f"Error calculating Relative Volume: {str(e)}")

def ta_volume_PVO(df: pd.DataFrame, n1: int = 12, n2: int = 26) -> pd.Series:
    """Calculate the Percentage Volume Oscillator (PVO).

    The PVO is a volume-based indicator that shows the relationship between two
    volume moving averages as a percentage, similar to MACD but for volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        n1 (int, optional): Fast period. Defaults to 12.
        n2 (int, optional): Slow period. Defaults to 26.

    Returns:
        pd.Series: PVO values. Interpretation:
            - Positive values indicate volume expansion
            - Negative values indicate volume contraction
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> pvo = ta_volume_PVO(df)

    References:
        - https://www.investopedia.com/terms/p/pvo.asp
    """
    try:
        if 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Volume' column")
            
        fast_ema = df['Volume'].ewm(span=n1, adjust=False).mean()
        slow_ema = df['Volume'].ewm(span=n2, adjust=False).mean()
        pvo = ((fast_ema - slow_ema) / slow_ema) * 100
        return pd.Series(pvo, name='PVO')
    except Exception as e:
        raise ValueError(f"Error calculating PVO: {str(e)}")

def ta_volume_StochPVO(df: pd.DataFrame, n1: int = 12, n2: int = 26, k_period: int = 14, d_period: int = 3) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate the Stochastic Percentage Volume Oscillator (Stoch PVO).

    The Stoch PVO combines the PVO with stochastic calculations to identify
    overbought and oversold conditions in volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        n1 (int, optional): Fast period for PVO. Defaults to 12.
        n2 (int, optional): Slow period for PVO. Defaults to 26.
        k_period (int, optional): %K period. Defaults to 14.
        d_period (int, optional): %D period. Defaults to 3.

    Returns:
        tuple[pd.Series, pd.Series, pd.Series]: A tuple containing:
            - stoch_pvo: Stochastic PVO line
            - signal: Signal line
            - histogram: Histogram values
        Interpretation:
            - Values above 80 indicate overbought volume conditions
            - Values below 20 indicate oversold volume conditions
            - Signal line crossovers may indicate volume trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> stoch_pvo, signal, hist = ta_volume_StochPVO(df)

    References:
        - https://www.investopedia.com/terms/s/stochasticoscillator.asp
    """
    try:
        if 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Volume' column")
            
        # Calculate PVO
        pvo = ta_volume_PVO(df, n1, n2)
        
        # Calculate Stochastic of PVO
        lowest_low = pvo.rolling(window=k_period).min()
        highest_high = pvo.rolling(window=k_period).max()
        
        stoch_pvo = 100 * (pvo - lowest_low) / (highest_high - lowest_low)
        signal = stoch_pvo.rolling(window=d_period).mean()
        histogram = stoch_pvo - signal
        
        return stoch_pvo, signal, histogram
    except Exception as e:
        raise ValueError(f"Error calculating Stochastic PVO: {str(e)}")

def ta_volume_MoneyFlowVolume(df: pd.DataFrame) -> pd.Series:
    """Calculate the Money Flow Volume.

    Money Flow Volume measures the flow of money into or out of a security by
    multiplying the typical price by volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: Money Flow Volume values. Interpretation:
            - Positive values indicate buying pressure
            - Negative values indicate selling pressure
            - Used in other indicators like Chaikin Money Flow

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> mfv = ta_volume_MoneyFlowVolume(df)

    References:
        - https://www.investopedia.com/terms/m/moneyflow.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        return pd.Series(typical_price * df['Volume'], name='MFV')
    except Exception as e:
        raise ValueError(f"Error calculating Money Flow Volume: {str(e)}")

def ta_mo_Qstick(df: pd.DataFrame, period: int = 10) -> tuple[pd.Series, pd.Series]:
    """Calculate the Qstick indicator.

    The Qstick indicator measures the buying and selling pressure by comparing
    opening and closing prices over a period of time.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'Close': Closing prices
        period (int, optional): The lookback period. Defaults to 10.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - sma: Simple Moving Average of Qstick
            - ema: Exponential Moving Average of Qstick
        Interpretation:
            - Values above 0 indicate buying pressure
            - Values below 0 indicate selling pressure
            - Trend changes at zero line crossovers

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Open': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95]
        ... })
        >>> sma, ema = ta_mo_Qstick(df, 10)

    References:
        - https://www.investopedia.com/terms/q/qstick.asp
    """
    try:
        required_columns = ['Open', 'Close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        diff = df['Close'] - df['Open']
        sma = diff.rolling(window=period).mean()
        ema = diff.ewm(span=period, adjust=False).mean()
        return pd.Series(sma, name='Qstick_SMA'), pd.Series(ema, name='Qstick_EMA')
    except Exception as e:
        raise ValueError(f"Error calculating Qstick: {str(e)}")

def add_Volume(df: pd.DataFrame) -> pd.DataFrame:
    """Add all volume indicators to the DataFrame.

    This function calculates and adds various volume-based technical indicators
    to the provided DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Open': Opening prices
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.DataFrame: Original DataFrame with added volume indicator columns:
            - ta_volume_VEMA_10: Volume Exponential Moving Average (10 periods)
            - ta_volume_VSMA_10: Volume Simple Moving Average (10 periods)
            - ta_volume_VolumeRSI: Volume Relative Strength Index
            - ta_volume_OBV: On-Balance Volume
            - ta_volume_PVI: Positive Volume Index
            - ta_volume_NVI: Negative Volume Index
            - ta_volume_VWAP: Volume Weighted Average Price
            - ta_volume_BOP: Balance of Power
            - ta_volume_PVO_fast: Fast Percentage Volume Oscillator
            - ta_volume_PVO_slow: Slow Percentage Volume Oscillator
            - ta_volume_StochPVO: Stochastic PVO components
            - ta_volume_MFI: Money Flow Index
            - ta_volume_MFV: Money Flow Volume
            - ta_volume_AD: Accumulation/Distribution
            - ta_volume_RelativeVolume_50: 50-period Relative Volume
            - ta_volume_ChaikinMoneyFlow: Chaikin Money Flow
            - ta_volume_VolumeFlowIndicator: Volume Flow Indicator
            - ta_volume_VolumeMA: Volume Moving Average
            - ta_volume_ChaikinADL: Chaikin ADL
            - ta_volume_VPT: Volume Price Trend
            - ta_volume_EMV: Ease of Movement
            - ta_volume_ForceIndex: Force Index

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Open': [44.12, 44.25, 43.72],
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> df_with_indicators = add_Volume(df)
    """
    try:
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")

        df = df.copy()

        # Volume Moving Averages
        df['ta_volume_VEMA_10'] = ta_volume_vema(df)
        df['ta_volume_VSMA_10'] = ta_volume_vsma(df)
        df['ta_volume_VolumeMA'] = ta_volume_VolumeMA(df)

        # Volume Momentum Indicators
        df['ta_volume_VolumeRSI'] = ta_volume_volumersi(df)
        df['ta_volume_MFI'] = ta_volume_MFI(df)

        # Volume Trend Indicators
        df['ta_volume_OBV'] = ta_volume_OBV(df)
        df['ta_volume_PVI'] = ta_volume_PVI(df)
        df['ta_volume_NVI'] = ta_volume_NVI(df)
        df['ta_volume_VWAP'] = ta_volume_VWAP(df)
        df['ta_volume_VPT'] = ta_volume_VPT(df)

        # Volume Price Indicators
        df['ta_volume_BOP'] = ta_volume_BOP(df)
        df['ta_volume_ForceIndex'] = ta_volume_ForceIndex(df)
        emv, emv_ma = ta_volume_EMV(df)
        df['ta_volume_EMV'] = emv
        df['ta_volume_EMVMA'] = emv_ma

        # Volume Oscillators
        df['ta_volume_PVO'] = ta_volume_PVO(df)
        df['ta_volume_PVO_signal'] = df['ta_volume_PVO'].ewm(span=9, adjust=False).mean()
        df['ta_volume_PVO_hist'] = df['ta_volume_PVO'] - df['ta_volume_PVO_signal']

        stoch_pvo, signal, hist = ta_volume_StochPVO(df)
        df['ta_volume_StochPVO'] = stoch_pvo
        df['ta_volume_StochPVO_signal'] = signal
        df['ta_volume_StochPVO_hist'] = hist

        # Money Flow Indicators
        df['ta_volume_MFV'] = ta_volume_MoneyFlowVolume(df)
        df['ta_volume_ChaikinMoneyFlow'] = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low']) * df['Volume']
        df['ta_volume_ChaikinMoneyFlow'] = df['ta_volume_ChaikinMoneyFlow'].rolling(window=20).mean()
        df['ta_volume_ChaikinADL'] = ta_volume_ChaikinADL(df)
        
        # Calculate Accumulation/Distribution Line (AD)
        mfm = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        df['ta_volume_AD'] = (mfm * df['Volume']).cumsum()

        # Volume Analysis
        df['ta_volume_RelativeVolume_50'] = ta_volume_RelativeVolume(df)
        df['ta_volume_VolumeFlowIndicator'] = ta_volume_VolumeFlowIndicator(df)

        return df
    except Exception as e:
        raise ValueError(f"Error adding volume indicators: {str(e)}")

def ta_volume_VWAP(df: pd.DataFrame) -> pd.Series:
    """Calculate the Volume Weighted Average Price (VWAP).

    VWAP is a trading benchmark that represents the average price a security
    has traded at throughout the day, weighted by volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: VWAP values. Interpretation:
            - Price above VWAP indicates bullish sentiment
            - Price below VWAP indicates bearish sentiment
            - Often used as a fair price benchmark

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> vwap = ta_volume_VWAP(df)

    References:
        - https://www.investopedia.com/terms/v/vwap.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        return pd.Series((typical_price * df['Volume']).cumsum() / df['Volume'].cumsum(), name='VWAP')
    except Exception as e:
        raise ValueError(f"Error calculating VWAP: {str(e)}")

def ta_volume_PVI(df: pd.DataFrame) -> pd.Series:
    """Calculate the Positive Volume Index (PVI).

    The PVI is a cumulative indicator that focuses on days when volume increases,
    helping identify smart money movements in high volume periods.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: PVI values. Interpretation:
            - Rising PVI during high volume suggests institutional buying
            - Falling PVI during high volume suggests institutional selling
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> pvi = ta_volume_PVI(df)

    References:
        - https://www.investopedia.com/terms/p/pvi.asp
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        pvi = pd.Series(index=df.index, dtype='float64')
        pvi.iloc[0] = 1000
        
        for i in range(1, len(df)):
            if df['Volume'].iloc[i] > df['Volume'].iloc[i - 1]:
                pvi.iloc[i] = pvi.iloc[i - 1] + (df['Close'].iloc[i] - df['Close'].iloc[i - 1]) / \
                             df['Close'].iloc[i - 1] * pvi.iloc[i - 1]
            else:
                pvi.iloc[i] = pvi.iloc[i - 1]
                
        return pvi
    except Exception as e:
        raise ValueError(f"Error calculating Positive Volume Index: {str(e)}")

def ta_volume_VolumeMA(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """Calculate the Volume Moving Average (VolumeMA).

    VolumeMA smooths volume data to identify trends in trading activity and
    potential price reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required column:
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 20.

    Returns:
        pd.Series: VolumeMA values. Interpretation:
            - Volume above MA suggests strong trend
            - Volume below MA suggests weak trend
            - Crossovers can signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'Volume': [1000, 1200, 900, 1500, 1100]})
        >>> vma = ta_volume_VolumeMA(df)

    References:
        - https://www.investopedia.com/terms/v/volume.asp
    """
    try:
        if 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Volume' column")
            
        return df['Volume'].rolling(window=period).mean()
    except Exception as e:
        raise ValueError(f"Error calculating Volume MA: {str(e)}")

def ta_volume_ChaikinADL(df: pd.DataFrame) -> pd.Series:
    """Calculate the Chaikin Accumulation/Distribution Line (ADL).

    The ADL combines price and volume to show if a security is being accumulated
    or distributed, helping identify potential trend reversals.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: ADL values. Interpretation:
            - Rising ADL suggests accumulation/buying pressure
            - Falling ADL suggests distribution/selling pressure
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> adl = ta_volume_ChaikinADL(df)

    References:
        - https://www.investopedia.com/terms/a/accumulationdistribution.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        clv = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low'])
        adl = (clv * df['Volume']).cumsum()
        return pd.Series(adl, name='ADL')
    except Exception as e:
        raise ValueError(f"Error calculating Chaikin ADL: {str(e)}")

def ta_volume_VPT(df: pd.DataFrame) -> pd.Series:
    """Calculate the Volume Price Trend (VPT).

    The VPT shows the cumulative volume that drives a price trend, considering
    both price changes and volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'Volume': Trading volume

    Returns:
        pd.Series: VPT values. Interpretation:
            - Rising VPT confirms uptrend
            - Falling VPT confirms downtrend
            - Divergences can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> vpt = ta_volume_VPT(df)

    References:
        - https://www.investopedia.com/terms/v/vpt.asp
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        price_change = df['Close'].pct_change()
        vpt = (df['Volume'] * price_change).cumsum()
        return pd.Series(vpt, name='VPT')
    except Exception as e:
        raise ValueError(f"Error calculating VPT: {str(e)}")

def ta_volume_EMV(df: pd.DataFrame, period: int = 14) -> tuple[pd.Series, pd.Series]:
    """Calculate the Ease of Movement (EMV) indicator.

    EMV measures the ease with which price moves up or down by relating price
    change to volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        tuple[pd.Series, pd.Series]: A tuple containing:
            - emv: Raw EMV values
            - emv_ma: EMV moving average
        Interpretation:
            - Positive EMV indicates upward price movement is easier
            - Negative EMV indicates downward price movement is easier
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> emv, emv_ma = ta_volume_EMV(df)

    References:
        - https://www.investopedia.com/terms/e/easeofmovement.asp
    """
    try:
        required_columns = ['High', 'Low', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        distance = ((df['High'] + df['Low']) / 2) - ((df['High'].shift(1) + df['Low'].shift(1)) / 2)
        box_ratio = df['Volume'] / (df['High'] - df['Low'])
        emv = distance / box_ratio
        emv_ma = emv.rolling(window=period).mean()
        return pd.Series(emv, name='EMV'), pd.Series(emv_ma, name='EMV_MA')
    except Exception as e:
        raise ValueError(f"Error calculating EMV: {str(e)}")

def ta_volume_ForceIndex(df: pd.DataFrame, period: int = 13) -> pd.Series:
    """Calculate the Force Index.

    The Force Index measures the power behind price movements by considering
    price changes and volume.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'Close': Closing prices
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 13.

    Returns:
        pd.Series: Force Index values. Interpretation:
            - Positive values indicate buying pressure
            - Negative values indicate selling pressure
            - Zero line crossovers may signal trend changes

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> fi = ta_volume_ForceIndex(df)

    References:
        - https://www.investopedia.com/terms/f/force-index.asp
    """
    try:
        required_columns = ['Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        force = df['Close'].diff() * df['Volume']
        return pd.Series(force.ewm(span=period, adjust=False).mean(), name='ForceIndex')
    except Exception as e:
        raise ValueError(f"Error calculating Force Index: {str(e)}")

def ta_volume_MFI(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate the Money Flow Index (MFI).

    The MFI is a momentum indicator that measures the inflow and outflow of money
    into an asset over a specific period of time.

    Args:
        df (pd.DataFrame): DataFrame containing market data with required columns:
            - 'High': High prices
            - 'Low': Low prices
            - 'Close': Closing prices
            - 'Volume': Trading volume
        period (int, optional): The lookback period. Defaults to 14.

    Returns:
        pd.Series: MFI values ranging from 0 to 100. Interpretation:
            - Values above 80 indicate overbought conditions
            - Values below 20 indicate oversold conditions
            - Divergences with price can signal potential reversals

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'High': [44.55, 44.77, 44.11],
        ...     'Low': [44.12, 44.25, 43.72],
        ...     'Close': [44.34, 44.44, 43.95],
        ...     'Volume': [1000, 1200, 900]
        ... })
        >>> mfi = ta_volume_MFI(df)

    References:
        - https://www.investopedia.com/terms/m/mfi.asp
    """
    try:
        required_columns = ['High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame must contain columns: {required_columns}")
            
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(window=period).sum()
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(window=period).sum()
        
        money_ratio = positive_flow / negative_flow
        mfi = 100 - (100 / (1 + money_ratio))
        
        return pd.Series(mfi, name='MFI')
    except Exception as e:
        raise ValueError(f"Error calculating Money Flow Index: {str(e)}")
