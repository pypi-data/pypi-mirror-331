# Technical Indicators

A comprehensive Python library for technical analysis indicators in financial markets.

## Features

- Support and Resistance Indicators
  - Pivot Points (Floor Trader's Method)
  - Fibonacci Retracements
  - Support/Resistance Level Detection
  - Maximum Drawdown Analysis
- Moving Averages
- Volume Indicators
- Momentum Indicators
- Trend Indicators

## Installation

Using pip:
```bash
pip install technical-indicators
```

Using Poetry:
```bash
poetry add technical-indicators
```

## Quick Start

```python
import pandas as pd
from Technical_Analysis.Indicators.supportResistance import calculate_pivot_points

# Create or load your price data
df = pd.DataFrame({
    'High': [105, 104, 106],
    'Low': [98, 97, 99],
    'Close': [102, 101, 103]
})

# Calculate pivot points
pivots = calculate_pivot_points(df)
print(pivots)
```

## Documentation

Full documentation is available at [https://technical-indicators.readthedocs.io](https://technical-indicators.readthedocs.io)

### Support and Resistance Indicators

The library provides various methods to identify potential support and resistance levels:

```python
from Technical_Analysis.Indicators.supportResistance import (
    find_support_resistance,
    fibonacci_retracement,
    calculate_pivot_points
)

# Find support and resistance levels
levels = find_support_resistance(df)

# Calculate Fibonacci retracements
fib_levels = fibonacci_retracement(df)

# Calculate pivot points
pivots = calculate_pivot_points(df)
```

## Development

This project uses Poetry for dependency management. To set up the development environment:

1. Install Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/TechnicalIndicators.git
cd TechnicalIndicators
```

3. Install dependencies:
```bash
poetry install
```

4. Run tests:
```bash
poetry run pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 