"""
Technical_Analysis Package

This package provides technical indicators, options pricing, and backtesting strategies
for quantitative finance and algorithmic trading.

Submodules:
    - Backtest: Implements backtesting strategies.
    - Indicators: Collection of technical analysis indicators.
    - Options: Option pricing models using yFinance data.
"""

from .Backtest import *
from .Indicators import *
from .Options import *
from .DataFetch import *
__all__ = ["Backtest", "Indicators", "Options", "DataFetch"]
