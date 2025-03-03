"""Technical Analysis Support and Resistance Indicators

This module provides various technical analysis indicators for identifying support
and resistance levels in financial markets.

Included Indicators:
- **Support & Resistance Levels**: Detects price levels where buying or selling pressure occurs.
- **Fibonacci Levels**: Includes retracements, arcs, fans, and time zones.
- **Pivot Points**: Calculates classic floor trader pivot points.
- **Maximum Drawdown**: Measures the largest peak-to-trough decline.
- **Relative Extremes**: Identifies relative price extremes over a rolling window.
"""

from .support_resistance import (
    find_support_resistance,
    fibonacci_retracement,
    fibonacci_arcs,
    fibonacci_fan,
    fibonacci_time_zone,
    max_drawdown,
    relative_extremes,
    support_resistance_points,
    calculate_pivot_points,
)

__all__ = [
    "find_support_resistance",
    "fibonacci_retracement",
    "fibonacci_arcs",
    "fibonacci_fan",
    "fibonacci_time_zone",
    "max_drawdown",
    "relative_extremes",
    "support_resistance_points",
    "calculate_pivot_points",
]
