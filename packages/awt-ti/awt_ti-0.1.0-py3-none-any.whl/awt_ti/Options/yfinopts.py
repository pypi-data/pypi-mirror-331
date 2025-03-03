"""
yfinopts.py

This module defines the OptionContract class for analyzing stock options using Yahoo Finance (yfinance) data.

Classes:
    - OptionContract: Represents an options contract and calculates its pricing and Greeks.

Methods:
    - getTickerHistory(ticker, retClose=True, closeCol='Adj Close', max=True): Fetches historical stock price data.
    - calculate_time_to_expiry(): Computes the number of days until the contract expires.
    - compute_stock_volatility(): Estimates the annualized volatility of the stock.
    - black_scholes(): Calculates the option price using the Black-Scholes model.
    - delta(): Computes the option's delta (sensitivity to stock price changes).
    - gamma(): Computes the option's gamma (sensitivity of delta to stock price changes).
    - vega(): Computes the option's vega (sensitivity to volatility changes).
    - theta(): Computes the option's theta (time decay of option value).
    - rho(): Computes the option's rho (sensitivity to interest rate changes).
    - print_input_parameters(): Displays all input parameters used in option pricing calculations.
"""

import datetime
import pandas as pd
import numpy as np
from scipy.stats import norm
import yfinance as yf
from datetime import datetime, timedelta

from awt_ti.DataFetch.yfinance_data_fetcher import get_ticker_history


class OptionContract:
    """
    Represents an option contract with methods to analyze and compute option pricing
    using the Black-Scholes model, historical stock volatility, and Greeks.

    Attributes:
        symbol (str): The stock ticker symbol.
        date_str (str): Expiration date of the option in 'YYYY-MM-DD' format.
        strike_price (float): The option's strike price.
        contract_type (str): The type of option ('calls' or 'puts').
        options_contract_data (dict): Data for the option contract.
        risk_free_rate (float): The risk-free rate (defaults to the last value of the '^IRX' index).
        oc_contract_symbol (str): Option contract symbol.
        hst_prc_stock (pd.Series): Historical stock price data.
        hst_contact_stock (pd.Series): Historical option price data.
        ts_opt_stock (pd.DataFrame): Merged stock and option historical data.
        time_to_expiry (int): Days remaining until expiration.
        implied_volatility (float): Implied volatility of the option.
        volatility (float): Computed stock volatility.
        premium (float): Last traded price of the option.
    """

    def __init__(self, symbol, date_str, strike_price, contract_type, options_contract_data, risk_free_rate=None):
        """
        Initializes an OptionContract object.

        Args:
            symbol (str): The stock ticker symbol.
            date_str (str): Expiration date in 'YYYY-MM-DD' format.
            strike_price (float): The strike price of the option.
            contract_type (str): 'calls' for call options, 'puts' for put options.
            options_contract_data (dict): Dictionary containing option contract data.
            risk_free_rate (float, optional): Risk-free interest rate. Defaults to last value of '^IRX' index.
        """
        if not risk_free_rate:
            risk_free_rate = get_ticker_history('^IRX')[-1] / 100
            self.risk_free_rate = round(risk_free_rate, 4)

        self.symbol = symbol
        self.date_str = date_str
        self.strike_price = round(strike_price, 2)
        self.contract_type = contract_type
        self.options_contract_data = options_contract_data
        self.oc_contract_symbol = options_contract_data['Contract Name']
        self.hst_prc_stock = self.getTickerHistory(symbol, retClose=True)
        self.hst_contact_stock = self.getTickerHistory(self.oc_contract_symbol, retClose=True)
        self.ts_opt_stock = pd.merge(self.hst_contact_stock, self.hst_prc_stock, left_index=True, right_index=True)
        self.time_to_expiry = self.calculate_time_to_expiry()
        self.implied_volatility = round(float(self.options_contract_data['Implied Volatility'].replace('%', '')), 2)
        self.volatility = round(self.compute_stock_volatility(), 4)
        self.premium = self.options_contract_data['Last Price']

    def getTickerHistory(self, ticker, retClose=True, closeCol='Adj Close', max=True):
        """
        Fetches historical price data for a given ticker using Yahoo Finance.

        Args:
            ticker (str): The stock ticker symbol.
            retClose (bool, optional): If True, returns adjusted close prices. Defaults to True.
            closeCol (str, optional): Column name for closing price. Defaults to 'Adj Close'.
            max (bool, optional): If True, fetches the maximum available data.

        Returns:
            pd.Series: Historical price data for the ticker.
        """
        if max:
            df = yf.download(ticker, period='max')
        else:
            one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            df = yf.download(ticker, start=one_year_ago)

        if retClose:
            df.rename(columns={closeCol: ticker}, inplace=True)
            return df[ticker]
        return df

    def calculate_time_to_expiry(self):
        """
        Computes the number of days until the option contract expires.

        Returns:
            int: Number of days to expiry.
        """
        current_date = datetime.now()
        expiry_date = datetime.strptime(self.date_str, '%Y-%m-%d')
        return (expiry_date - current_date).days

    def compute_stock_volatility(self):
        """
        Computes the stock's annualized volatility based on historical price data.

        Returns:
            float: Annualized volatility of the stock.
        """
        daily_returns = self.hst_prc_stock.pct_change()
        return daily_returns.std() * np.sqrt(252)

    def black_scholes(self):
        """
        Computes the theoretical price of the option using the Black-Scholes model.

        Returns:
            float: Theoretical option price.
        """
        S = self.hst_prc_stock.iloc[-1]  # Current stock price
        K = self.strike_price
        T = self.time_to_expiry / 365
        r = self.risk_free_rate
        sigma = self.implied_volatility / 100

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if self.contract_type == 'calls':
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif self.contract_type == 'puts':
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    def delta(self):
        """
        Computes the option delta, which measures the sensitivity of the option price to changes in stock price.

        Returns:
            float: Delta value.
        """
        d1 = self._d1()
        return norm.cdf(d1) if self.contract_type == 'calls' else -norm.cdf(-d1)

    def gamma(self):
        """
        Computes the option gamma, which measures the rate of change of delta with respect to stock price.

        Returns:
            float: Gamma value.
        """
        d1 = self._d1()
        S = self.hst_prc_stock.iloc[-1]
        sigma = self.implied_volatility / 100
        T = self.time_to_expiry / 365

        return norm.pdf(d1) / (S * sigma * np.sqrt(T))

    def vega(self):
        """
        Computes the option vega, which measures sensitivity to changes in implied volatility.

        Returns:
            float: Vega value.
        """
        d1 = self._d1()
        S = self.hst_prc_stock.iloc[-1]
        T = self.time_to_expiry / 365

        return S * norm.pdf(d1) * np.sqrt(T) * 0.01

    def theta(self):
        """
        Computes the option theta, which measures the rate of decline in option value over time.

        Returns:
            float: Theta value per day.
        """
        d1 = self._d1()
        S = self.hst_prc_stock.iloc[-1]
        K = self.strike_price
        T = self.time_to_expiry / 365
        r = self.risk_free_rate
        sigma = self.implied_volatility / 100

        return (-S * sigma * norm.pdf(d1)) / (2 * np.sqrt(T)) / 365

    def rho(self):
        """
        Computes the option rho, which measures sensitivity to interest rate changes.

        Returns:
            float: Rho value.
        """
        K = self.strike_price
        T = self.time_to_expiry / 365
        r = self.risk_free_rate
        d2 = self._d1() - (self.implied_volatility / 100) * np.sqrt(T)

        return K * T * np.exp(-r * T) * norm.cdf(d2) * 0.01
