"""
Technical_Analysis.DataFetch.yfinance_data_fetcher

This module provides functions to fetch financial market data using `yfinance` and `yahoo_fin.options`.

Features:
    - Stock price retrieval.
    - Option chain retrieval.
    - Expiration date conversion.
    - Market summary calculations.
"""

import yfinance as yf
from datetime import datetime, timedelta
from yahoo_fin import options
import pandas as pd


def get_stock_price_data(ticker: str, start_date: str, end_date: str, period: str = "1d") -> pd.DataFrame:
    """
    Fetches historical stock price data from Yahoo Finance.

    Args:
        ticker (str): Stock ticker symbol.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        period (str, optional): Data retrieval period (default: "1d").

    Returns:
        pd.DataFrame: DataFrame containing stock price data.
    """
    return yf.download(ticker, start=start_date, end=end_date, period=period)


def get_risk_free_rate() -> pd.DataFrame:
    """
    Fetches the risk-free rate from the 10-Year Treasury Note Yield (^TNX).

    Returns:
        pd.DataFrame: Risk-free rate data.
    """
    return yf.download("^TNX") / 100


def convert_date(date_string: str) -> str:
    """
    Converts an options expiration date from Yahoo Finance into ISO format (YYYY-MM-DD).

    Args:
        date_string (str): Date in format 'Month Day, Year' (e.g., "January 19, 2024").

    Returns:
        str: Formatted date in 'YYYY-MM-DD'.
    """
    return datetime.strptime(date_string, "%B %d, %Y").strftime("%Y-%m-%d")


def get_expiration_date(symbol: str) -> list:
    """
    Fetches available expiration dates for an options contract.

    Args:
        symbol (str): Stock ticker symbol.

    Returns:
        list: List of expiration dates in 'YYYY-MM-DD' format.
    """
    return [convert_date(o) for o in options.get_expiration_dates(symbol)]


def get_option_chain(symbol: str, date_str: str, raw: bool = False, cleanOC: bool = True, 
                     onlyPuts: bool = False, onlyCalls: bool = False, add_date: bool = False, 
                     set_index: str = "") -> dict:
    """
    Retrieves the options chain for a given symbol and expiration date.

    Args:
        symbol (str): Stock ticker symbol.
        date_str (str): Expiration date in 'YYYY-MM-DD' format.
        raw (bool, optional): If True, return raw data (default: False).
        cleanOC (bool, optional): If True, cleans the options chain (default: True).
        onlyPuts (bool, optional): If True, returns only put options (default: False).
        onlyCalls (bool, optional): If True, returns only call options (default: False).
        add_date (bool, optional): If True, adds expiration date to options chain (default: False).
        set_index (str, optional): Column name to set as index.

    Returns:
        dict: Dictionary containing 'calls' and 'puts' data.
    """
    oc = options.get_options_chain(symbol, date_str, raw=raw)

    if add_date:
        oc["puts"]["Expiration Date"] = date_str
        oc["calls"]["Expiration Date"] = date_str

    if cleanOC:
        if set_index:
            oc["puts"].set_index(set_index, inplace=True)
            oc["calls"].set_index(set_index, inplace=True)

        oc["puts"] = oc["puts"].to_dict(orient="index")
        oc["calls"] = oc["calls"].to_dict(orient="index")

    if onlyPuts:
        return oc["puts"]
    if onlyCalls:
        return oc["calls"]

    return oc


def compute_put_call_ratio(data_dict: dict, date: str, strike_price: float = None) -> float:
    """
    Computes the put-call ratio for a given date and optional strike price.

    Args:
        data_dict (dict): Dictionary containing options data.
        date (str): Date in 'YYYY-MM-DD' format.
        strike_price (float, optional): Specific strike price to evaluate.

    Returns:
        float: Put-call ratio, or an error message if calls volume is zero.
    """
    if date not in data_dict["calls"] or date not in data_dict["puts"]:
        return None  # Date not found

    calls_volume = data_dict["calls"][date]["Volume"]
    puts_volume = data_dict["puts"][date]["Volume"]

    if strike_price is not None:
        calls_strike = [
            strike for strike, contract_data in data_dict["calls"].items()
            if contract_data["Strike"] == strike_price
        ]
        puts_strike = [
            strike for strike, contract_data in data_dict["puts"].items()
            if contract_data["Strike"] == strike_price
        ]

        if not calls_strike or not puts_strike:
            return None  # Strike price not found

        calls_volume = data_dict["calls"][calls_strike[0]]["Volume"]
        puts_volume = data_dict["puts"][puts_strike[0]]["Volume"]

    if calls_volume == 0:
        return "Error: Calls volume is zero"

    return puts_volume / calls_volume


def get_ticker_history(symbol: str, cleanDateIndex: bool = True, retClose: bool = True, 
                       closeCol: str = "Adj Close", max: bool = True, keepVol: bool = False) -> pd.DataFrame:
    """
    Retrieves historical stock price data.

    Args:
        symbol (str): Stock ticker symbol.
        cleanDateIndex (bool, optional): If True, clean date index (default: True).
        retClose (bool, optional): If True, return only close prices (default: True).
        closeCol (str, optional): Column name for adjusted close price (default: "Adj Close").
        max (bool, optional): If True, fetches max available data (default: True).
        keepVol (bool, optional): If True, keeps volume data (default: False).

    Returns:
        pd.DataFrame: Stock historical data.
    """
    df = yf.download(symbol, period="max") if max else yf.download(symbol, start=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))

    if retClose:
        if not keepVol:
            df.rename(columns={closeCol: symbol}, inplace=True)
            return df[symbol]
        else:
            df.rename(columns={closeCol: symbol, "Volume": f"{symbol}_volume"}, inplace=True)
            return df[[symbol, f"{symbol}_volume"]]

    return df


def get_market_summary(tickers: list = ["BTC-USD", "ETH-USD", "^GSPC", "DX-Y.NYB"], reference_date: str = None) -> dict:
    """
    Fetches market summary showing percentage change over different periods.

    Args:
        tickers (list, optional): List of ticker symbols to fetch (default: cryptocurrencies, S&P500, Dollar Index).
        reference_date (str, optional): Reference date for calculations (default: None, uses today).

    Returns:
        dict: Dictionary with percent changes for 1D, 7D, 30D, YTD.
    """
    reference_date = pd.Timestamp(datetime.now().date()) if reference_date is None else pd.Timestamp(reference_date)

    start_date = pd.Timestamp(year=reference_date.year, month=1, day=1) - pd.Timedelta(days=10)
    end_date = reference_date + pd.Timedelta(days=1)

    data = yf.download(tickers, start=start_date, end=end_date)
    close_prices = data["Adj Close"].ffill()

    first_of_year = pd.Timestamp(year=reference_date.year, month=1, day=1)
    ytd_start = close_prices[:first_of_year].last_valid_index() if pd.isna(close_prices.loc[first_of_year].all()) else first_of_year

    dates_needed = {
        "1D": reference_date - pd.Timedelta(days=1),
        "7D": reference_date - pd.Timedelta(days=7),
        "30D": reference_date - pd.Timedelta(days=30),
        "YTD": ytd_start,
    }

    results = {}
    for ticker in tickers:
        changes = {}
        latest_price = close_prices.at[reference_date, ticker] if reference_date in close_prices.index else None

        if latest_price:
            for period, date in dates_needed.items():
                changes[period] = f"{((latest_price - close_prices.at[date, ticker]) / close_prices.at[date, ticker]) * 100:.2f}%" if date in close_prices.index else "N/A"
        results[ticker] = changes

    return results
