"""
Technical_Analysis.DataFetch

This package provides data-fetching utilities using `yfinance` for retrieving:
    - Historical stock price data
    - Options chain and expiration dates
    - Market summary and risk-free rates

Modules:
    - yfinance_data_fetcher: Functions for retrieving financial data.

Example Usage:
    >>> from Technical_Analysis.DataFetch import get_stock_price_data
    >>> df = get_stock_price_data("AAPL", "2023-01-01", "2023-12-31")
    >>> print(df.head())
"""

# Import key functions from yfinance_data_fetcher for direct access
from .yfinance_data_fetcher import (
    get_stock_price_data,
    get_risk_free_rate,
    convert_date,
    get_expiration_date,
    get_option_chain,
    compute_put_call_ratio,
    get_ticker_history,
    get_market_summary,
)

# Define all available functions when importing the module
__all__ = [
    "get_stock_price_data",
    "get_risk_free_rate",
    "convert_date",
    "get_expiration_date",
    "get_option_chain",
    "compute_put_call_ratio",
    "get_ticker_history",
    "get_market_summary",
]
