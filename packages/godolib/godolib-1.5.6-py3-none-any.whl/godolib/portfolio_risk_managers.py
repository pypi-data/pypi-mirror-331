import numpy as np
import pandas as pd
from .fast_transformers import (
    calculate_simple_moving_average,
    calculate_relative_volatility_on_prices,
    calculate_rolling_volatility,
)
from .utilities import apply_function_by_groups, func_by_groups


class TrailingStopSMA:
    """
    Implements a trailing stop strategy using a simple moving average (SMA).
    Evaluates risk and prospects for portfolio management.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing historical asset prices.
        sma_df (pd.DataFrame): A DataFrame storing the SMA values for each asset.
    """

    def __init__(self, period, df):
        """
        Initializes the TrailingStopSMA class.

        Args:
            period (int): The window size for calculating the simple moving average (SMA).
            df (pd.DataFrame): A DataFrame containing historical asset prices with dates as the index
                and asset names as columns.
        """
        self.df = df
        self.sma_df = apply_function_by_groups(
            df=df,
            func=lambda group: func_by_groups(
                group=group,
                func=calculate_simple_moving_average,
                window_size=period,
                min_periods=period,
            ),
        )

    def evaluate_risk(self, simulator, date):
        """
        Evaluates the risk of the current portfolio positions based on SMA strategy.

        Args:
            simulator (object): An object containing the current portfolio positions (assets held).
                Expected to have an attribute `positions` which is a dictionary of asset names as keys.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current price >= SMA (hold).
                    - False: Current price < SMA (sell).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "SMA": The simple moving average of the asset.
        """
        assets = list(simulator.positions.keys())
        current_price = self.df.loc[date]
        current_sma = self.sma_df.loc[date]
        details = {}
        decision = {}

        for asset in assets:
            details[asset] = {
                "Price": current_price.loc[asset],
                "SMA": current_sma.loc[asset],
            }
            decision[asset] = current_price.loc[asset] >= current_sma.loc[asset]

        return decision, details

    def evaluate_prospects(self, simulator, prospects, date):
        """
        Evaluates potential investment prospects based on SMA strategy.

        Args:
            simulator (object): An object representing the portfolio simulator.
            prospects (list): A list of prospective assets to evaluate.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current price >= SMA (consider investing).
                    - False: Current price < SMA (do not invest).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "SMA": The simple moving average of the asset.
        """
        current_price = self.df.loc[date]
        current_sma = self.sma_df.loc[date]
        details = {}
        decision = {}

        for asset in prospects:
            details[asset] = {
                "Price": current_price.loc[asset],
                "SMA": current_sma.loc[asset],
            }
            decision[asset] = current_price.loc[asset] >= current_sma.loc[asset]

        return decision, details


class TrailingStopVolatility:
    """
    Implements a trailing stop strategy based on asset volatility.
    Evaluates risk and prospects for portfolio management using a volatility threshold.

    Attributes:
        threshold (float): The multiplier for the standard deviation of volatility to set the trailing stop level.
        df (pd.DataFrame): The input DataFrame containing historical asset prices.
        volatility_df (pd.DataFrame): A DataFrame storing the calculated volatility for each asset.
        stds (np.ndarray): An array of standard deviations of the volatility for each asset.
    """

    def __init__(
        self,
        threshold,
        df,
        returns_period,
        window_size,
        returns_method="percentage",
    ):
        """
        Initializes the TrailingStopVolatility class.

        Args:
            threshold (float): The multiplier for standard deviation of volatility to set the stop level.
            df (pd.DataFrame): A DataFrame containing historical asset prices with dates as the index
                and asset names as columns.
            returns_period (int): The period over which returns are calculated.
            window_size (int): The window size for calculating volatility.
            returns_method (str, optional): The method used to calculate returns (e.g., "percentage" or "log").
                Defaults to "percentage".
        """
        self.threshold = threshold
        self.df = df
        self.volatility_df = apply_function_by_groups(
            df=df,
            func=lambda group: func_by_groups(
                group=group,
                func=calculate_relative_volatility_on_prices,
                returns_period=returns_period,
                window_size=window_size,
                returns_method=returns_method,
                min_periods=window_size,
            ),
        )
        self.stds = self.volatility_df.std().values

    def evaluate_risk(self, simulator, date):
        """
        Evaluates the risk of current portfolio positions based on volatility threshold.

        Args:
            simulator (object): An object containing the current portfolio positions (assets held).
                Expected to have an attribute `positions` which is a dictionary of asset names as keys.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current volatility <= threshold (hold).
                    - False: Current volatility > threshold (sell).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "Volatility": The current volatility of the asset.
                    - "Volatility STD": The standard deviation of the asset's volatility.
                    - "Volatility STD * threshold": The calculated trailing stop level.
        """
        assets = list(simulator.positions.keys())
        current_price = self.df.loc[date]
        current_volatility = self.volatility_df.loc[date]
        details = {}
        decision = {}

        for asset_idx, asset in enumerate(assets):
            details[asset] = {
                "Price": current_price.loc[asset],
                "Volatility": current_volatility.loc[asset],
                "Volatility STD": self.stds[asset_idx],
                f"Volatility STD * {self.threshold}": self.stds[asset_idx]
                * self.threshold,
            }
            decision[asset] = (
                current_volatility.loc[asset] <= self.stds[asset_idx] * self.threshold
            )

        return decision, details

    def evaluate_prospects(self, simulator, prospects, date):
        """
        Evaluates potential investment prospects based on volatility threshold.

        Args:
            simulator (object): An object representing the portfolio simulator.
            prospects (list): A list of prospective assets to evaluate.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current volatility <= threshold (consider investing).
                    - False: Current volatility > threshold (do not invest).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "Volatility": The current volatility of the asset.
                    - "Volatility STD": The standard deviation of the asset's volatility.
                    - "Volatility STD * threshold": The calculated trailing stop level.
        """
        current_price = self.df.loc[date]
        current_volatility = self.volatility_df.loc[date]
        details = {}
        decision = {}

        for asset_idx, asset in enumerate(prospects):
            details[asset] = {
                "Price": current_price.loc[asset],
                "Volatility": current_volatility.loc[asset],
                "Volatility STD": self.stds[asset_idx],
                f"Volatility STD * {self.threshold}": self.stds[asset_idx]
                * self.threshold,
            }
            decision[asset] = (
                current_volatility.loc[asset] <= self.stds[asset_idx] * self.threshold
            )

        return decision, details


class TrailingStopBollinger:
    """
    Implements a trailing stop strategy using Bollinger Bands.
    Evaluates risk and prospects for portfolio management based on the lower Bollinger Band.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing historical asset prices.
        bollinger_factor (float): The multiplier for the rolling volatility to calculate the Bollinger Bands.
        sma_df (pd.DataFrame): A DataFrame storing the simple moving average (SMA) for each asset.
        roll_vol_df (pd.DataFrame): A DataFrame storing the rolling volatility for each asset.
        lower_bband_df (pd.DataFrame): A DataFrame storing the calculated lower Bollinger Band for each asset.
    """

    def __init__(self, df, window_size, bollinger_factor):
        """
        Initializes the TrailingStopBollinger class.

        Args:
            df (pd.DataFrame): A DataFrame containing historical asset prices with dates as the index
                and asset names as columns.
            window_size (int): The window size for calculating the SMA and rolling volatility.
            bollinger_factor (float): The multiplier for the rolling volatility to calculate the Bollinger Bands.
        """
        self.df = df
        self.bollinger_factor = bollinger_factor
        self.sma_df = apply_function_by_groups(
            df=df,
            func=lambda group: func_by_groups(
                group=group,
                func=calculate_simple_moving_average,
                window_size=window_size,
                min_periods=window_size,
            ),
        )
        self.roll_vol_df = apply_function_by_groups(
            df=df,
            func=lambda group: func_by_groups(
                group=group, func=calculate_rolling_volatility, window_size=window_size
            ),
        )

        lower_bband_array = (
            self.sma_df.values - bollinger_factor * self.roll_vol_df.values
        )

        self.lower_bband_df = pd.DataFrame(
            lower_bband_array,
            index=df.index[-lower_bband_array.shape[0] :],
            columns=df.columns,
        )

    def evaluate_risk(self, simulator, date):
        """
        Evaluates the risk of current portfolio positions based on the lower Bollinger Band.

        Args:
            simulator (object): An object containing the current portfolio positions (assets held).
                Expected to have an attribute `positions` which is a dictionary of asset names as keys.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current price >= lower Bollinger Band (hold).
                    - False: Current price < lower Bollinger Band (sell).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "SMA": The simple moving average of the asset.
                    - "Absolute Volatility": The rolling volatility of the asset.
                    - "Bollinger Lower Band": The calculated lower Bollinger Band of the asset.
        """
        assets = list(simulator.positions.keys())
        current_price = self.df.loc[date]
        current_sma = self.sma_df.loc[date]
        current_abs_vol = self.roll_vol_df.loc[date]
        current_lower_bband = self.lower_bband_df.loc[date]
        details = {}
        decision = {}

        for asset in assets:
            details[asset] = {
                "Price": current_price.loc[asset],
                "SMA": current_sma.loc[asset],
                "Absolute Volatility": current_abs_vol.loc[asset],
                f"Bollinger Lower Band (f={self.bollinger_factor})": current_lower_bband.loc[
                    asset
                ],
            }
            decision[asset] = current_price.loc[asset] >= current_lower_bband.loc[asset]

        return decision, details

    def evaluate_prospects(self, simulator, prospects, date):
        """
        Evaluates potential investment prospects based on the lower Bollinger Band.

        Args:
            simulator (object): An object representing the portfolio simulator.
            prospects (list): A list of prospective assets to evaluate.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current price >= lower Bollinger Band (consider investing).
                    - False: Current price < lower Bollinger Band (do not invest).
                details (dict): A dictionary containing details of each asset's evaluation with keys:
                    - "Price": The current price of the asset.
                    - "SMA": The simple moving average of the asset.
                    - "Absolute Volatility": The rolling volatility of the asset.
                    - "Bollinger Lower Band": The calculated lower Bollinger Band of the asset.
        """
        current_price = self.df.loc[date]
        current_sma = self.sma_df.loc[date]
        current_abs_vol = self.roll_vol_df.loc[date]
        current_lower_bband = self.lower_bband_df.loc[date]

        details = {}
        decision = {}

        for asset in prospects:
            details[asset] = {
                "Price": current_price.loc[asset],
                "SMA": current_sma.loc[asset],
                "Absolute Volatility": current_abs_vol.loc[asset],
                f"Bollinger Lower Band (f={self.bollinger_factor})": current_lower_bband.loc[
                    asset
                ],
            }
            decision[asset] = current_price.loc[asset] >= current_lower_bband.loc[asset]

        return decision, details


class TrailingStopEquitySMA:
    """
    Implements a trailing stop strategy for portfolio equity based on a simple moving average (SMA).
    Evaluates the portfolio's risk by comparing its equity value against the SMA of its historical values.

    Attributes:
        window_size (int): The window size used for calculating the equity SMA.
    """

    def __init__(self, window_size):
        """
        Initializes the TrailingStopEquitySMA class.

        Args:
            window_size (int): The window size for calculating the equity SMA.
        """
        self.window_size = window_size

    def evaluate_risk(self, simulator, date):
        """
        Evaluates the portfolio's risk based on the SMA of its equity.

        Args:
            simulator (object): An object containing the current state of the portfolio.
                Expected to have an attribute `value` which is a DataFrame with columns "Date" and "Value".
                Also expected to have an attribute `positions` which is a dictionary of assets currently held.
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Keep the asset (equity >= SMA).
                    - False: Sell the asset (equity < SMA).
                details (dict): A dictionary containing details of the portfolio's evaluation with keys:
                    - "Portfolio": A sub-dictionary with keys:
                        - "Equity": The current equity value of the portfolio.
                        - "Equity SMA": The calculated SMA of the portfolio's equity.
        """
        # Convert portfolio value to DataFrame and set the index to dates
        equity_df = pd.DataFrame(simulator.value)
        equity_df["Date"] = pd.to_datetime(equity_df["Date"])
        equity_df.set_index("Date", inplace=True)

        # Handle the case where there are insufficient data points for the SMA calculation
        if equity_df.shape[0] <= self.window_size:
            details = {
                "Portfolio": {
                    "Equity": equity_df.loc[date, "Value"],
                    "Equity SMA": np.nan,
                }
            }
            decision = {asset: True for asset in simulator.positions}
            return decision, details

        # Calculate the SMA for equity values
        equity_sma = calculate_simple_moving_average(
            array=equity_df["Value"].values.reshape(-1, 1),
            window_size=self.window_size,
            min_periods=self.window_size,
        )
        sma_df = pd.DataFrame(
            equity_sma, index=equity_df.index[-equity_sma.shape[0] :], columns=["SMA"]
        )

        # Gather details of the portfolio's current equity and SMA
        details = {
            "Portfolio": {
                "Equity": equity_df.loc[date, "Value"],
                "Equity SMA": sma_df.loc[date, "SMA"],
            }
        }

        # Determine whether to keep or sell assets based on the equity comparison to the SMA
        keeping = equity_df.loc[date, "Value"] >= sma_df.loc[date, "SMA"]
        decision = {asset: keeping for asset in simulator.positions}

        return decision, details


class FixedStopLoss:
    """
    Implements a fixed stop-loss strategy based on a predefined threshold.
    Evaluates whether to hold or sell assets by comparing current prices to entry prices adjusted by the threshold.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing historical asset prices.
        threshold (float): The percentage threshold for the stop-loss level.
    """

    def __init__(self, df, threshold):
        """
        Initializes the FixedStopLoss class.

        Args:
            df (pd.DataFrame): A DataFrame containing historical asset prices with dates as the index
                and asset names as columns.
            threshold (float): The stop-loss threshold as a percentage (e.g., 0.05 for 5%).
        """
        self.df = df
        self.threshold = threshold

    def evaluate_risk(self, simulator, date):
        """
        Evaluates the risk of current portfolio positions based on the stop-loss threshold.

        Args:
            simulator (object): An object containing the current portfolio positions and trade history.
                Expected to have attributes `positions` (a dictionary of assets currently held),
                `trades` (a record of trades), and `history` (a log of asset prices and actions).
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            tuple:
                decision (dict): A dictionary where keys are asset names and values are booleans:
                    - True: Current price > entry price * (1 - threshold) (hold).
                    - False: Current price <= entry price * (1 - threshold) (sell).
                details (dict): A dictionary containing details of the evaluation with keys:
                    - "date": The entry date for the asset.
                    - "price": The entry price for the asset.
        """
        assets = list(simulator.positions.keys())
        current_price = self.df.loc[date]
        trades_df = pd.DataFrame(simulator.trades)
        logs_df = pd.DataFrame(simulator.history)

        entry_data = self._read_entry_prices(
            assets=assets, trades_df=trades_df, logs_df=logs_df, date=date
        )

        decision = {}
        details = {}

        for asset in assets:
            details[asset] = entry_data[asset]
            decision[asset] = current_price.loc[asset] > entry_data[asset]["price"] * (
                1 - self.threshold
            )

        return decision, details

    def _read_entry_prices(self, assets, trades_df, logs_df, date):
        """
        Retrieves the entry prices for the given assets from the trade and log history.

        Args:
            assets (list): List of asset names currently held in the portfolio.
            trades_df (pd.DataFrame): A DataFrame containing the trade history with columns "Date", "Action", and "Asset".
            logs_df (pd.DataFrame): A DataFrame containing the log history with columns "Date", "Asset", and "Asset_Price".
            date (str or datetime): The date for which the evaluation is performed.

        Returns:
            dict: A dictionary where keys are asset names and values are dictionaries with keys:
                - "date": The entry date for the asset.
                - "price": The entry price for the asset.
        """
        dates = trades_df["Date"].unique().tolist()[::-1]
        assets_entry_dates = {}

        # Find the most recent entry date for each asset
        for asset in assets:
            for i_date in dates:
                i_date_trade_assets = trades_df.loc[
                    (trades_df["Action"] == "Buy") & (trades_df["Date"] == i_date)
                ]["Asset"].unique()
                if asset not in i_date_trade_assets:
                    continue
                assets_entry_dates[asset] = trades_df.loc[
                    (trades_df["Date"] == i_date) & (trades_df["Asset"] == asset)
                ]["Entry_Date"].iloc[0]

        entry_prices = {}

        # Retrieve the entry price for each asset
        for asset in assets:
            entry_prices[asset] = logs_df.loc[
                (logs_df["Asset"] == asset)
                & (logs_df["Date"] == assets_entry_dates[asset])
            ]["Asset_Price"].iloc[0]

        return {
            asset: {"date": assets_entry_dates[asset], "price": entry_prices[asset]}
            for asset in assets
        }
