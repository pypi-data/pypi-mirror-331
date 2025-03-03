"""
Technical_Analysis.Backtest

This module provides backtesting strategies using technical indicators.

Modules:
    - backtest: Contains multiple trading strategies.

Example:
    ```python
    from Technical_Analysis.Backtest import strat_map, RSIStrategy
    from backtesting import Backtest

    bt = Backtest(data, RSIStrategy, cash=10000, commission=0.002)
    results = bt.run()
    bt.plot()
    ```
"""

from .backtest import (
    RSIStrategy,
    VWAPStrategy,
    IchimokuCloudStrategy,
    BollingerBandsReversionStrategy,
    MACDCrossoverStrategy,
    ElderRayIndexStrategy,
    MovingAverageCrossoverStrategySMA,
    MovingAverageCrossoverStrategyEMA,
    MACDRSIStrategy,
    BollingerRSIStochStrategy,
    BollingerStochasticStrategy,
    strat_map
)

__all__ = [
    "RSIStrategy",
    "VWAPStrategy",
    "IchimokuCloudStrategy",
    "BollingerBandsReversionStrategy",
    "MACDCrossoverStrategy",
    "ElderRayIndexStrategy",
    "MovingAverageCrossoverStrategySMA",
    "MovingAverageCrossoverStrategyEMA",
    "MACDRSIStrategy",
    "BollingerRSIStochStrategy",
    "BollingerStochasticStrategy",
    "strat_map"
]
