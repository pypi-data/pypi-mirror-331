"""
Technical_Analysis.Options

This module provides functionality for options contract analysis, including:
- Fetching options data from Yahoo Finance (`yfinopts.py`).
- Computing theoretical option pricing using the Black-Scholes model.
- Calculating options Greeks (delta, gamma, vega, theta, rho).

Modules:
    - yfinopts: Defines the `OptionContract` class for analyzing stock options.

Example:
    ```python
    from Technical_Analysis.Options import OptionContract
    
    contract = OptionContract(
        symbol="AAPL",
        date_str="2024-12-20",
        strike_price=150,
        contract_type="calls",
        options_contract_data=option_data
    )
    
    print(contract.black_scholes())  # Calculate theoretical option price
    print(contract.delta())          # Calculate Delta
    ```
"""

from .yfinopts import OptionContract

__all__ = ["OptionContract"]
