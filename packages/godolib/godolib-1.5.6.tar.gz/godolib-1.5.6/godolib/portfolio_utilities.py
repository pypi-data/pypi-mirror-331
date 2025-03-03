import numpy as np
import pandas as pd
from .fast_transformers import (
    calculate_simple_moving_average,
    calculate_relative_volatility_on_prices,
    calculate_rolling_volatility,
    calculate_returns,
    calculate_log_returns,
)
from .utilities import apply_function_by_groups, func_by_groups, format_datetime_df
import quantstats as qs
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def calculate_sharpe_ratio(equity_records, rfr_records, freq, returns_mehthod):
    valid_returns_methods = ["percentage", "logarithm"]
    if returns_mehthod not in valid_returns_methods:
        raise ValueError(
            f"{returns_mehthod} not a valid returns method. Choose from: {valid_returns_methods}"
        )
    filtered_equity_df = pd.DataFrame(
        [data for i, data in enumerate(equity_records) if i % freq == 0]
    )
    if returns_mehthod == "percentage":
        filtered_equity_df = format_datetime_df(filtered_equity_df)
        rebalance_returns_df = apply_function_by_groups(
            df=filtered_equity_df,
            func=lambda group: func_by_groups(
                group=group, func=calculate_returns, period=1
            ),
        )
    elif returns_mehthod == "logarithm":
        filtered_equity_df = format_datetime_df(filtered_equity_df)
        rebalance_returns_df = apply_function_by_groups(
            df=filtered_equity_df,
            func=lambda group: func_by_groups(
                group=group, func=calculate_log_returns, period=1
            ),
        )
    frfr_array = (
        np.array([data["Value"] for data in rfr_records]).reshape(-1, 1) + 1
    ) ** (1 / (252 // freq)) - 1

    frfr_df = format_datetime_df(
        pd.DataFrame(
            [
                {"Date": data["Date"], "Value": value[0]}
                for data, value in zip(rfr_records, frfr_array)
            ]
        )
    )

    sharpe_df = format_datetime_df(
        pd.merge_asof(
            rebalance_returns_df.reset_index(),
            frfr_df.reset_index(),
            on="Date",
            direction="backward",
        )
    )

    annualized_sharp_ratio = (
        (sharpe_df.values[:, 0] - sharpe_df.values[:, 1]).mean()
        / (sharpe_df.values[:, 0] - sharpe_df.values[:, 1]).std()
    ) * ((252 // freq) ** 0.5)
    return annualized_sharp_ratio


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


class PortfolioEvaluator:
    def __init__(
        self, benchmark_series, risk_free_rate=0.0, confidence_level=0.95, threshold=0
    ):
        self.benchmark_series = benchmark_series
        self.risk_free_rate = risk_free_rate
        self.confidence_level = confidence_level
        self.threshold = threshold

    def evaluate_trades(self, simulator):
        self.equity_data = pd.DataFrame(simulator.value)
        self.equity_data["Date"] = pd.to_datetime(self.equity_data["Date"])
        self.equity_data.set_index("Date", inplace=True)
        self.equity_data = self.equity_data["Value"]
        self.portfolio_id = simulator.portfolio_id
        df_multi = pd.DataFrame(simulator.trades)
        df_logs = pd.DataFrame(simulator.history)
        df_logs["Date"] = pd.to_datetime(df_logs["Date"])
        df_multi["Date"] = pd.to_datetime(df_multi["Date"])
        trades_evaluation = self._trade_metrics(df_multi=df_multi, df_logs=df_logs)
        trades_evaluation.insert(0, "portfolio_id", self.portfolio_id)
        return trades_evaluation

    def calculate_metrics(self, simulator):
        self.portfolio_id = simulator.portfolio_id
        self.equity_data = pd.DataFrame(simulator.value)
        self.equity_data["Date"] = pd.to_datetime(self.equity_data["Date"])
        self.equity_data.set_index("Date", inplace=True)
        self.equity_data = self.equity_data["Value"]
        equity_data = pd.DataFrame(simulator.value)
        equity_data["Date"] = pd.to_datetime(equity_data["Date"])
        equity_data.set_index("Date", inplace=True)
        metrics_df = self._metrics(df=equity_data)
        pivoted_df = metrics_df.T
        pivoted_df.columns = pivoted_df.iloc[0, :]
        pivoted_df = pivoted_df.iloc[1:]
        pivoted_df["Start_Date"] = pd.to_datetime(pivoted_df["Start_Date"])
        pivoted_df["End_Date"] = pd.to_datetime(pivoted_df["End_Date"])
        pivoted_df.reset_index(inplace=True)
        pivoted_df.drop(columns=["index"], inplace=True)
        return pivoted_df

    def plot_vs_benchmark(self, benchmark_label="SPY", single_axis=True):

        series_1 = self.equity_data.copy()
        series_2 = self.benchmark_series.copy()
        if len(series_1) < len(series_2):
            series_2 = series_2.loc[series_2.index >= series_1.index[0]]

        if not single_axis:
            fig, ax1 = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor("black")
            ax1.set_facecolor("black")
            ax1.plot(
                series_1.index,
                series_1.values,
                label="Equity Data",
                color="cyan",
                linewidth=2,
                linestyle="-",
            )
            ax1.set_xlabel("Time", fontsize=12, color="white")
            ax1.set_ylabel("Equity Data", color="cyan", fontsize=12)
            ax1.tick_params(axis="y", labelcolor="cyan", labelsize=10)

            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(
                ax1.xaxis.get_majorticklabels(),
                rotation=45,
                ha="right",
                fontsize=10,
                color="white",
            )

            ax1.grid(
                visible=True,
                which="both",
                linestyle="--",
                linewidth=0.5,
                alpha=0.7,
                color="gray",
            )
            ax2 = ax1.twinx()
            ax2.set_facecolor("black")
            ax2.plot(
                series_2.index,
                series_2.values,
                label=benchmark_label,
                color="magenta",
                linewidth=2,
                linestyle="--",
            )
            ax2.set_ylabel(benchmark_label, color="magenta", fontsize=12)
            ax2.tick_params(axis="y", labelcolor="magenta", labelsize=10)

            plt.title(
                "Performance Comparison: Equity vs Benchmark",
                fontsize=14,
                fontweight="bold",
                pad=20,
                color="white",
            )

            # fig.legend(
            #     loc="upper left",
            #     bbox_to_anchor=(0.1, 0.9),
            #     fontsize=10,
            #     frameon=True,
            #     facecolor="black",
            #     edgecolor="white",
            # )
            # Crear la leyenda
            legend = fig.legend(
                loc="upper left",
                bbox_to_anchor=(0.1, 0.9),
                fontsize=10,
                frameon=True,
                facecolor="black",
                edgecolor="white",
            )

            # Cambiar el color del texto de la leyenda a blanco
            for text in legend.get_texts():
                text.set_color("white")

            fig.tight_layout()

            plt.show()
        else:
            series_2_starting_value = series_2.iat[0]
            series_1_starting_value = series_1.iat[0]
            series_1 = series_1 * (series_2_starting_value / series_1_starting_value)

            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor("black")
            ax.set_facecolor("black")

            ax.plot(
                series_1.index,
                series_1.values,
                label="Equity Data (Scaled)",
                color="cyan",
                linewidth=2,
                linestyle="-",
            )
            ax.plot(
                series_2.index,
                series_2.values,
                label=benchmark_label,
                color="magenta",
                linewidth=2,
                linestyle="--",
            )

            ax.set_xlabel("Time", fontsize=12, color="white")
            ax.set_ylabel("Value", fontsize=12, color="white")
            ax.tick_params(axis="x", labelsize=10, color="white")
            ax.tick_params(axis="y", labelsize=10, color="white")

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            plt.setp(
                ax.xaxis.get_majorticklabels(),
                rotation=45,
                ha="right",
                fontsize=10,
                color="white",
            )

            ax.grid(
                visible=True,
                which="both",
                linestyle="--",
                linewidth=0.5,
                alpha=0.7,
                color="gray",
            )

            plt.title(
                "Performance Comparison: Equity vs Benchmark (Single Axis)",
                fontsize=14,
                fontweight="bold",
                pad=20,
                color="white",
            )

            legend = ax.legend(
                loc="upper left",
                fontsize=10,
                frameon=True,
                facecolor="black",
                edgecolor="white",
            )

            # Cambiar el color del texto de la leyenda a blanco
            for text in legend.get_texts():
                text.set_color("white")

            fig.tight_layout()

            plt.show()

    def _calculate_correct_drawdown_time(
        self, df_logs, retornos_por_trade, df_trade_metrics
    ):
        filtered_logs = []
        for _, row in retornos_por_trade.iterrows():
            logs = df_logs.loc[
                (df_logs["Asset"] == row["Asset"])
                & (df_logs["Date"] >= row["Fecha_inicio"])
                & (df_logs["Date"] <= row["Fecha_salida"])
            ].copy()
            logs.loc[:, "Trade_ID"] = row["Trade_ID"]
            filtered_logs.append(logs)

        filtered_logs_df = pd.concat(filtered_logs)

        filtered_logs_df = filtered_logs_df.merge(
            df_trade_metrics[["Trade_ID", "Trade_avg_buy_price"]],
            on="Trade_ID",
            how="left",
        )

        if (
            "Asset_Price" in filtered_logs_df.columns
            and "Trade_avg_buy_price" in filtered_logs_df.columns
        ):
            filtered_logs_df["Price_Difference"] = (
                filtered_logs_df["Asset_Price"]
                - filtered_logs_df["Trade_avg_buy_price"]
            )
            filtered_logs_df["Drawdown"] = filtered_logs_df["Price_Difference"].clip(
                upper=0
            )
        else:
            raise ValueError(
                "Missing required columns: 'Asset_Price' or 'Trade_avg_buy_price'."
            )

        drawdown_time = (
            filtered_logs_df[filtered_logs_df["Drawdown"] < 0]
            .groupby("Trade_ID")
            .size()
        )
        drawdown_time_df = drawdown_time.reset_index(name="Drawdown_time")

        return drawdown_time_df

    def _mean_buy_price(self, trades_df):
        trade_ids = trades_df["Trade_ID"].unique()
        trade_weighted_avg_buy_price = {}
        for trade_id in trade_ids:
            buy_actions = trades_df.loc[
                (trades_df["Trade_ID"] == trade_id) & (trades_df["Action"] == "Buy")
            ][["Amount", "Price"]]
            weights = buy_actions.values[:, 0] / np.sum(buy_actions.values[:, 0])
            prices = buy_actions.values[:, 1]
            weighted_average = np.dot(weights, prices)
            trade_weighted_avg_buy_price[trade_id] = weighted_average
        return trade_weighted_avg_buy_price

    def _trade_metrics(self, df_multi, df_logs):
        trades_mean_buy_price = self._mean_buy_price(trades_df=df_multi)
        df_multi["Trade_avg_buy_price"] = df_multi["Trade_ID"].map(
            trades_mean_buy_price
        )

        processed_df = df_multi.groupby("Trade_ID", group_keys=False).apply(
            self._process_trade_group
        )
        processed_df.reset_index(drop=True, inplace=True)

        date_differences = df_multi.groupby("Trade_ID")["Date"].agg(["min", "max"])
        date_differences["Days_Difference"] = (
            date_differences["max"] - date_differences["min"]
        ).dt.days
        asset_mapping = df_multi.groupby("Trade_ID")["Asset"].first()
        date_differences["Asset"] = asset_mapping
        date_differences.reset_index(inplace=True)

        max_twr_values = processed_df.loc[
            processed_df.groupby("Trade_ID")["Date"].idxmax(),
            ["Trade_ID", "TWRR_Acumulado"],
        ]
        retornos_por_trade = date_differences.merge(
            max_twr_values, on="Trade_ID", how="left"
        )
        retornos_por_trade.rename(
            columns={
                "min": "Fecha_inicio",
                "max": "Fecha_salida",
                "Days_Difference": "Plazo_dias",
                "TWRR_Acumulado": "TWRR",
            },
            inplace=True,
        )

        amount_summary = []
        for _, row in retornos_por_trade.iterrows():
            filtered_logs = df_logs[
                (df_logs["Asset"] == row["Asset"])
                & (df_logs["Date"] >= row["Fecha_inicio"])
                & (df_logs["Date"] <= row["Fecha_salida"])
            ]
            amount_min = (
                filtered_logs["Amount"].min() if not filtered_logs.empty else None
            )
            amount_max = (
                filtered_logs["Amount"].max() if not filtered_logs.empty else None
            )
            amount_summary.append(
                {
                    "Trade_ID": row["Trade_ID"],
                    "Asset": row["Asset"],
                    "Fecha_inicio": row["Fecha_inicio"],
                    "Fecha_salida": row["Fecha_salida"],
                    "Amount Min": amount_min,
                    "Amount Max": amount_max,
                }
            )

        amount_summary_df = pd.DataFrame(amount_summary)
        retornos_por_trade["MAE"] = round(
            (
                (amount_summary_df["Amount Min"] - processed_df["Valor_Inicial"])
                / processed_df["Valor_Inicial"]
            )
            * 100,
            2,
        )
        retornos_por_trade["MFE"] = round(
            (
                (amount_summary_df["Amount Max"] - processed_df["Valor_Inicial"])
                / processed_df["Valor_Inicial"]
            )
            * 100,
            2,
        )
        retornos_por_trade["TPR"] = round(
            (
                (amount_summary_df["Amount Max"] - amount_summary_df["Amount Min"])
                / amount_summary_df["Amount Min"]
            )
            * 100,
            2,
        )
        retornos_por_trade["Return_to_TPR"] = round(
            (retornos_por_trade["TWRR"] / retornos_por_trade["TPR"]) * 100, 2
        )
        retornos_por_trade["TWRR"] = round((retornos_por_trade["TWRR"]) * 100, 2)

        retornos_por_trade = retornos_por_trade.merge(
            df_multi[["Trade_ID", "Trade_avg_buy_price"]].drop_duplicates(),
            on="Trade_ID",
            how="left",
        )

        drawdown_time_df = self._calculate_correct_drawdown_time(
            df_logs, retornos_por_trade, retornos_por_trade
        )
        retornos_por_trade = retornos_por_trade.merge(
            drawdown_time_df, on="Trade_ID", how="left"
        )
        retornos_por_trade["Drawdown_time"] = (
            retornos_por_trade["Drawdown_time"].fillna(0).astype(int)
        )

        return retornos_por_trade

    def _process_trade_group(self, group):
        results = []
        for i in range(len(group) - 1):
            row = group.iloc[i]
            next_rows = group[group["Date"] > row["Date"]].sort_values(by="Date")
            if next_rows.empty:
                continue
            next_row = next_rows.iloc[0]
            valor_inicial = row["Resulting_Amount"] if i > 0 else row["Amount"]
            valor_final = (
                next_row["Amount"]
                if next_row["Resulting_Amount"] == 0
                else next_row["Resulting_Amount"]
            )
            cash_flow = (
                -next_row["Amount"]
                if next_row["Action"] == "Buy"
                else next_row["Amount"] if next_row["Resulting_Amount"] != 0 else 0
            )
            retorno = (valor_final + cash_flow - valor_inicial) / valor_inicial
            results.append(
                {
                    "Date": row["Date"],
                    "Trade_ID": row["Trade_ID"],
                    "Asset": row["Asset"],
                    "Valor_Inicial": valor_inicial,
                    "Valor_Final": valor_final,
                    "Cash_Flow": cash_flow,
                    "Retorno": retorno,
                }
            )
        result_df = pd.DataFrame(results)
        twrr = []
        for i, row in result_df.iterrows():
            twrr.append(
                (1 + row["Retorno"]) if i == 0 else twrr[i - 1] * (1 + row["Retorno"])
            )
        result_df["TWRR_Acumulado"] = [value - 1 for value in twrr]
        return result_df

    def _metrics(self, df):
        returns = df["Value"].pct_change().dropna()
        start_date = df.index[0]
        end_date = df.index[-1]
        initial_value = df["Value"].iloc[0]
        final_value = df["Value"].iloc[-1]
        days = (end_date - start_date).days
        years = days / 360
        cagr = ((final_value / initial_value) ** (1 / years)) - 1
        cagr_percentage = cagr * 100
        current_year = end_date.year
        max_drawdown = qs.stats.max_drawdown(returns) * 100
        calmar = cagr_percentage / abs(max_drawdown) if max_drawdown != 0 else None
        treynor_index = self._calculate_treynor_index(df_equity=df)
        beta = self._calculate_beta(df_equity=df)
        risk_parity = self._calculate_risk_parity(df_equity=df)
        MDD_mean = self._calculate_MDD_mean(df_equity=df)
        MDD_Recovery_time = self._MDD_Recovery_Time(df_equity=df)
        omega = self._calculate_omega_ratio(df_equity=df)
        ulcer_index = self._calculate_ulcer_index(df_equity=df)
        tail_ratio = self._calculate_tail_ratio(df_equity=df)
        gain_pain = self._calculate_gain_to_pain_ratio(df_equity=df)
        ytd_returns = returns.loc[f"{current_year}-01-01":].sum() * 100  # Year to Date
        one_year_returns = (
            returns.loc[f"{current_year - 1}" :f"{current_year - 1}-12-31"].sum() * 100
        )  # Last Year
        two_year_returns = (
            returns.loc[f"{current_year - 2}" :f"{current_year - 1}-12-31"].sum() * 100
        )  # Two Years
        hit_rate = (returns > 0).sum() / len(returns) * 100
        equity_start_date = self.equity_data.index[0].strftime("%Y-%m-%d")

        benchmark = self.benchmark_series.copy()
        benchmark = benchmark.loc[benchmark.index >= equity_start_date]

        benchmark_cummulative_return = (
            (benchmark.iloc[-1] / benchmark.iloc[0]) - 1
        ) * 100

        metrics = {}
        metrics["portfolio_id"] = self.portfolio_id
        metrics["Start_Date"] = start_date
        metrics["End_Date"] = end_date
        metrics["Average_Daily_Value"] = df["Value"].mean()
        metrics["Median_Daily_Value"] = df["Value"].median()
        metrics["Max_Daily_Value"] = df["Value"].max()
        metrics["Min_Daily_Value"] = df["Value"].min()
        metrics["Cumulative_Return_Percent"] = (
            (final_value - initial_value) / initial_value
        ) * 100
        metrics["CAGR_Percent"] = cagr_percentage
        metrics["Year_To_Date_Percent"] = ytd_returns
        metrics["Last_Year_Percent"] = one_year_returns
        metrics["Two_Years_Percent"] = two_year_returns
        metrics["Hit_Rate_Percent"] = hit_rate
        metrics["Value_at_Risk_VaR"] = qs.stats.value_at_risk(returns)
        metrics["Conditional_VaR_cVaR"] = qs.stats.expected_shortfall(returns)
        metrics["Sharpe_Ratio"] = qs.stats.sharpe(returns)
        metrics["Sortino_Ratio"] = qs.stats.sortino(returns)
        metrics["Max_Drawdown_Percent"] = max_drawdown
        metrics["Volatility_Ann_Percent"] = (
            qs.stats.volatility(returns, annualize=True) * 100
        )
        metrics["Calmar_Ratio"] = calmar
        metrics["Skew"] = qs.stats.skew(returns)
        metrics["Kurtosis"] = qs.stats.kurtosis(returns)
        metrics["Recovery_Factor"] = qs.stats.recovery_factor(returns)
        metrics["SP500_Cumulative_Return_Percent"] = benchmark_cummulative_return
        metrics["Treynor_Index"] = treynor_index
        metrics["Beta"] = beta
        metrics["Risk_Parity"] = risk_parity
        metrics["Mean_Drawdown_Depth"] = MDD_mean
        metrics["Maximum_Drawdown_Recovery_Time"] = MDD_Recovery_time
        metrics["Omega_Ratio"] = omega
        metrics["Ulcer_index"] = ulcer_index
        metrics["Tail_ratio"] = tail_ratio
        metrics["Gain_to_Pain_ratio"] = gain_pain
        return pd.DataFrame(metrics.items(), columns=["Metric", "Value"])

    def _calculate_treynor_index(self, df_equity):

        spy = self.benchmark_series.to_frame()
        spy.index.name = "Date"
        spy.reset_index(inplace=True)

        # Merge the two DataFrames on the "date" column
        merged_data = pd.merge(spy, df_equity, on="Date")

        # Calculate daily returns
        merged_data["return_spy"] = merged_data["SPY"].pct_change()
        merged_data["return_equity"] = merged_data["Value"].pct_change()

        # Drop rows with NaN values (first row will have NaN returns)
        merged_data = merged_data.dropna()

        beta = self._calculate_beta(df_equity)

        # Calculate annualized returns
        equity_return_annualized = (1 + merged_data["return_equity"].mean()) ** 252 - 1

        # Calculate excess return of the equity over the risk-free rate
        excess_return = equity_return_annualized - self.risk_free_rate

        # Calculate the Treynor Index
        treynor_index = excess_return / beta

        return treynor_index

    def _calculate_beta(self, df_equity):

        spy = self.benchmark_series.to_frame()
        spy.index.name = "Date"
        spy.reset_index(inplace=True)

        # Merge the two DataFrames on the "date" column
        merged_data = pd.merge(spy, df_equity, on="Date")

        # Calculate daily returns
        merged_data["return_spy"] = merged_data["SPY"].pct_change()
        merged_data["return_equity"] = merged_data["Value"].pct_change()

        # Drop rows with NaN values (first row will have NaN returns)
        merged_data = merged_data.dropna()

        # Calculate covariance between equity and SPY returns
        covariance = np.cov(merged_data["return_equity"], merged_data["return_spy"])[
            0, 1
        ]

        variance = np.var(merged_data["return_spy"], ddof=1)

        beta = round(covariance / variance, 2)

        return beta

    def _calculate_risk_parity(self, df_equity):

        spy = self.benchmark_series.to_frame()
        spy.index.name = "Date"
        spy.reset_index(inplace=True)

        # Merge the two DataFrames on the "date" column
        merged_data = pd.merge(spy, df_equity, on="Date")

        # Calculate daily returns
        merged_data["return_spy"] = merged_data["SPY"].pct_change()
        merged_data["return_equity"] = merged_data["Value"].pct_change()

        # Drop rows with NaN values (first row will have NaN returns)
        merged_data = merged_data.dropna()

        # Calculate volatility (standard deviation of returns)
        volatility_spy = np.std(merged_data["return_spy"])
        volatility_equity = np.std(merged_data["return_equity"])

        # Calculate Risk Parity weights
        weight_spy = 1 / volatility_spy
        weight_equity = 1 / volatility_equity

        # Normalize weights so they sum to 1
        total_weight = weight_spy + weight_equity
        weight_spy /= total_weight
        weight_equity /= total_weight

        # Return the weights as a dictionary
        return round(weight_equity, 2) * 100
        # "SPY_weight": round(weight_spy,2),
        # "Equity_weight":

    def _MDD_Recovery_Time(self, df_equity):
        # Ensure the DataFrame is sorted by date
        df_equity = df_equity.sort_values(by="Date")

        # Calculate the cumulative maximum value (peak) up to each point
        df_equity["Peak"] = df_equity["Value"].cummax()

        # Calculate the drawdown at each point
        df_equity["Drawdown"] = (df_equity["Value"] - df_equity["Peak"]) / df_equity[
            "Peak"
        ]

        # Find the date of the maximum drawdown
        max_drawdown_date = df_equity["Drawdown"].idxmin()

        # Find the date of the previous peak before the maximum drawdown
        previous_peak_date = df_equity.loc[
            df_equity.index < max_drawdown_date, "Peak"
        ].idxmax()

        # Find the next peak date after the maximum drawdown
        recovery_data = df_equity[df_equity.index > max_drawdown_date]
        new_peak_date = recovery_data[
            recovery_data["Value"] >= df_equity.loc[previous_peak_date, "Peak"]
        ].index.min()

        # Calculate the number of recovery days
        if pd.isna(new_peak_date):
            recovery_days = None  # If recovery hasn't happened yet
        else:
            recovery_days = (
                new_peak_date - previous_peak_date
            ).days  # Difference between previous peak and new peak

        return recovery_days

    def _calculate_MDD_mean(self, df_equity):

        column = "Value"

        serie = df_equity[column]

        rolling_max = serie.expanding(min_periods=1).max()

        # Calcular drawdown en cada punto
        drawdown = serie / rolling_max - 1

        # Identificar períodos de drawdown (cuando el drawdown es negativo)
        drawdown_periods = drawdown < 0

        # Inicializar lista para almacenar los maximum drawdowns individuales
        max_drawdowns = []

        current_drawdown = 0
        in_drawdown = False

        # Iterar sobre la serie de drawdown para detectar cada episodio de drawdown
        for dd in drawdown:
            if dd < 0:
                current_drawdown = min(current_drawdown, dd)
                in_drawdown = True
            else:
                if in_drawdown:  # Si hubo un drawdown, lo guardamos
                    max_drawdowns.append(current_drawdown)
                current_drawdown = 0
                in_drawdown = False

        # Si la serie termina en drawdown, agregamos el último
        if in_drawdown:
            max_drawdowns.append(current_drawdown)

        # Calcular el maximum drawdown promedio
        average_maximum_drawdown = (
            (sum(max_drawdowns) / len(max_drawdowns)) * 100 if max_drawdowns else 0
        )

        return average_maximum_drawdown

    def _calculate_omega_ratio(self, df_equity):

        # Calculate daily returns
        df_equity["Return"] = df_equity["Value"].pct_change().dropna()

        # Calculate gains and losses relative to the threshold
        gains = df_equity["Return"][df_equity["Return"] > self.threshold].sum()
        losses = abs(df_equity["Return"][df_equity["Return"] < self.threshold].sum())

        # Handle edge case where there are no losses
        if losses == 0:
            return np.inf  # Infinite Omega Ratio if there are no losses

        # Calculate the Omega Ratio
        omega_ratio = gains / losses

        return omega_ratio

    def _calculate_ulcer_index(self, df_equity):
        column = "Value"  # Assuming 'Value' is always the column of interest

        # Calculate the running maximum
        running_max = df_equity[column].cummax()

        # Calculate percentage drawdown
        drawdowns = ((df_equity[column] - running_max) / running_max) * 100

        # Square the drawdowns
        squared_drawdowns = drawdowns**2

        # Calculate the Ulcer Index
        ulcer_index = round(np.sqrt(squared_drawdowns.mean()), 2)

        return ulcer_index

    def _calculate_tail_ratio(self, df_equity):
        column = "Value"  # Assuming 'Value' is the column of interest

        # Calculate returns
        df_equity["Returns"] = df_equity[column].pct_change()

        # Remove NaN values from the returns column
        returns = df_equity["Returns"].dropna()

        # Determine the 90th and 10th percentiles
        positive_tail_threshold = np.percentile(returns, 90)
        negative_tail_threshold = np.percentile(returns, 10)

        # Extract positive and negative tails
        positive_tail = returns[returns > positive_tail_threshold]
        negative_tail = returns[returns < negative_tail_threshold]

        # Calculate average positive and average absolute negative tails
        avg_positive_tail = positive_tail.mean()
        avg_negative_tail = abs(negative_tail.mean())

        # Calculate Tail Ratio
        tail_ratio = round(
            avg_positive_tail / avg_negative_tail if avg_negative_tail != 0 else np.nan,
            2,
        )

        return tail_ratio

    def _calculate_gain_to_pain_ratio(self, df_equity):

        # Calculate daily returns
        column = "Value"

        df_equity["Returns"] = df_equity[column].pct_change()

        # Remove NaN values
        returns = df_equity["Returns"].dropna()

        # Calculate the sum of positive and negative returns
        sum_positive = returns[returns > 0].sum()
        sum_negative = abs(returns[returns < 0].sum())

        # Calculate Gain to Pain Ratio
        gain_to_pain_ratio = round(
            sum_positive / sum_negative if sum_negative != 0 else np.nan, 2
        )

        return gain_to_pain_ratio
