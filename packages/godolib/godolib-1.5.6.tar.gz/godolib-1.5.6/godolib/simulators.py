import numpy as np
import pandas as pd
from .fast_transformers import calculate_log_returns, calculate_returns
from .filing import save_dataframes_to_excel
import random
import string
import matplotlib.pyplot as plt
from .utilities import extract_non_active_since_until


class PortfolioSimulator:
    """
    A simulator for managing and evaluating a financial portfolio.

    Attributes:
        initial_cash (float): Initial cash available for investments.
        target_weight (float): Target allocation weight for the portfolio.
        df (DataFrame): A DataFrame containing historical prices of assets.
        id_structure (str, optional): A template for generating unique trade IDs.
        manager (object, optional): An object responsible for risk management. Must implement `check_prospects` and `check_risk` methods.
        evaluator (object, optional): An object for portfolio evaluation. Must implement `calculate_metrics` and optionally `evaluate_trades` methods.
        seed (int, optional): A seed for random number generation to ensure reproducibility.
        verbose (int): Verbosity level (0 for silent, 1 for monitoring outputs).
        portfolio_id (str, optional): A unique identifier for the portfolio.
        liquid_money (float): Current uninvested cash.
        portfolio_value (float): Total value of the portfolio (cash + investments).
        history (list): A log of all portfolio actions and changes.
        balancing_dates (list): Dates when rebalancing occurred.
        trades (list): A log of trades, including buy and sell actions.
        positions (dict): Current holdings in the portfolio with allocation and amount details.
        holdings (dict): Historical record of holdings for each date.
    """

    def __init__(
        self,
        initial_cash,
        target_weight,
        df,
        id_structure=None,
        manager=None,
        evaluator=None,
        seed=None,
        verbose=1,
        portfolio_id=None,
    ):
        """
        Initialize the PortfolioSimulator.

        Args:
            initial_cash (float): Initial cash for the portfolio.
            target_weight (float): Target allocation weight for the portfolio.
            df (DataFrame): A DataFrame containing historical prices of assets.
            id_structure (str, optional): Template for generating unique trade IDs.
            manager (object, optional): Risk manager object with `check_prospects` and `check_risk` methods.
            evaluator (object, optional): Portfolio evaluator object with a `calculate_metrics` method. Optionally, `evaluate_trades`.
            seed (int, optional): Seed for random number generation.
            verbose (int): Verbosity level (0 for silent, 1 for monitoring outputs).
            portfolio_id (str, optional): Unique identifier for the portfolio.

        Raises:
            ValueError: If required attributes for `manager` or `evaluator` are missing.
        """
        manager_required_attributes = ["evaluate_risk"]
        evaluator_required_attributes = ["calculate_metrics"]
        if manager:
            missing_attributes = [
                attr
                for attr in manager_required_attributes
                if not hasattr(manager, attr)
            ]
            if missing_attributes:
                raise ValueError(
                    f"Manager object is missing required attribtes: {', '.join(missing_attributes)}"
                )
        if evaluator:
            if not portfolio_id:
                raise ValueError("Evaluator object needs a portfolio_id")
            missing_attributes = [
                attr
                for attr in evaluator_required_attributes
                if not hasattr(evaluator, attr)
            ]
            if missing_attributes:
                raise ValueError(
                    f"Evaluator object is missing required attribtes: {', '.join(missing_attributes)}"
                )
        if verbose not in [1, 0]:
            raise ValueError("Verbose parameter must be 0 (silent) or 1 (monitor)")
        self.initial_cash = initial_cash
        self.liquid_money = initial_cash
        self.portfolio_value = initial_cash
        self.target_weight = target_weight

        self.manager = manager
        self.df = df
        self.id_structure = id_structure
        self.verbose = verbose
        self.history = []
        self.balancing_dates = []
        self.trades = []
        self.positions = {}
        self.holdings = {}
        self.portfolio_id = portfolio_id
        self.evaluator = evaluator

        if seed is not None:
            random.seed(seed)

    def simulate(self, signals):
        """
        Simulate portfolio management over time based on buy signals.

        Args:
            signals (dict): A dictionary of buy signals where keys are dates and values are lists of assets to buy on those dates.

        Details:
            - Iterates over provided dates, adjusting the portfolio based on risk evaluation and buy signals.
            - If a `manager` is provided, evaluates risk and determines whether to retain or sell assets.
            - Uses `evaluator` to calculate metrics after simulation.

        Raises:
            ValueError: If manager or evaluator does not have required methods but is used in the simulation process.
        """
        initial_date = list(signals.keys())[0]
        self.dates = [
            date.strftime("%Y-%m-%d")
            for date in self.df.loc[self.df.index >= initial_date].index
        ]
        self.balancing_dates = list(signals.keys())
        self.value = [{"Date": initial_date, "Value": self.portfolio_value}]

        for date_idx, date in enumerate(self.dates):
            if self.verbose == 1:
                print(
                    f"\n\n\n---------------------------------{date}: {self.portfolio_value}-----------------------------------"
                )
            if date_idx == 0:
                self._rebalance(date=date, buy_signals=signals[date])
                self._update_history(date=date, rebalance=True)
            else:
                self._update_portfolio_value(date=date)
                self.value.append({"Date": date, "Value": self.portfolio_value})
                self._refresh_positions(date=date)

                if self.manager:
                    decision, details = self.manager.evaluate_risk(
                        simulator=self, date=date
                    )
                    if self.verbose == 1:
                        if len(decision) == len(details):
                            for key, value in decision.items():

                                print(f"\nDecision")
                                print(key, value)
                                print(f"{details[key]}")
                        else:
                            print("\nDecision:")
                            print(f"{decision}")
                            print(f"\nDetails:")
                            print(f"{details}")

                    sold_assets = []
                    for asset in decision:
                        if not decision[asset]:
                            sold_assets.append(asset)
                            self._sell_(asset=asset, quantity=True, date=date)

                if date in list(signals.keys()):
                    if (self.manager) and (hasattr(self.manager, "evaluate_prospects")):
                        decision, details = self.manager.evaluate_prospects(
                            simulator=self, prospects=signals[date], date=date
                        )
                        accepted_prospects = [
                            asset for asset in decision if decision[asset]
                        ]
                        if self.verbose == 1:
                            print(f"accepted_prospects: {accepted_prospects}")
                        self._rebalance(date=date, buy_signals=accepted_prospects)
                        self._update_history(date=date, rebalance=True)
                    else:
                        self._rebalance(date=date, buy_signals=signals[date])
                        self._update_history(date=date, rebalance=True)
                else:
                    self._update_history(date=date, rebalance=False)
            self.holdings[date] = list(self.positions.keys())
        if self.id_structure:
            self._assign_ids()
        if self.evaluator:
            self.metrics = self.evaluator.calculate_metrics(simulator=self)
            self.trade_metrics = self.evaluator.evaluate_trades(simulator=self)

    def save_to_excel(self, file_path):
        """
        Save the portfolio history, equity, trades, and holdings to an Excel file.

        Args:
            file_path (str): Path to save the Excel file.

        Details:
            - Saves multiple sheets: Logs, Equity, Trades, Holdings, and optionally Metrics and Trade Metrics.
        """
        history = pd.DataFrame(self.history)
        equity = pd.DataFrame(self.value)
        trades = pd.DataFrame(self.trades)
        holdings = (
            pd.DataFrame.from_dict(
                self.holdings,
                orient="index",
                columns=[
                    f"Holding_{i+1}"
                    for i in range(
                        max(len(assets) for assets in self.holdings.values())
                    )
                ],
            )
            .reset_index()
            .rename(columns={"index": "Date"})
        )
        if self.portfolio_id:
            history.insert(0, "portfolio_id", self.portfolio_id)
            equity.insert(0, "portfolio_id", self.portfolio_id)
            trades.insert(0, "portfolio_id", self.portfolio_id)
            holdings.insert(0, "portfolio_id", self.portfolio_id)
        dataframes = [history, equity, trades, holdings]
        sheet_names = ["Logs", "Equity", "Trades", "Holdings"]
        if self.evaluator:
            dataframes.append(self.metrics)
            dataframes.append(self.trade_metrics)
            sheet_names.append("Metrics")
            sheet_names.append("Trades_Metrics")
        save_dataframes_to_excel(
            dataframes=dataframes,
            sheet_names=sheet_names,
            file_name=f"{file_path}",
        )

    def _assign_ids(self):
        _tuples_ = []
        for row in self.trades:
            current_asset = row["Asset"]
            current_entry_date = row["Entry_Date"]
            if (current_asset, current_entry_date) not in _tuples_:
                _tuples_.append((current_asset, current_entry_date))
        ids = {}
        for i, _ in enumerate(_tuples_):
            ids[i] = self._generate_id()

        for row_idx, row in enumerate(self.trades):
            current_tuple = (row["Asset"], row["Entry_Date"])
            idx = _tuples_.index(current_tuple)
            self.trades[row_idx].update({"Trade_ID": ids[idx]})

    def _refresh_positions(self, date):
        date_idx = self.dates.index(date)
        last_date_record = pd.DataFrame(self.history).loc[
            (pd.DataFrame(self.history)["Date"] == self.dates[date_idx - 1])
            & (pd.DataFrame(self.history)["Holding"])
        ]
        assets = last_date_record["Asset"].unique().tolist()
        prices_df = self.df.loc[
            [self.dates[date_idx - 1], self.dates[date_idx]], assets
        ]
        try:
            date_return = (
                calculate_returns(array=prices_df.values, period=1).reshape(
                    -1,
                )
                + 1
            )
        except Exception as e:
            self.error = prices_df.copy()
            raise ValueError(
                f"df contains nans on active dates ({self.dates[date_idx - 1], self.dates[date_idx]})"
            )
        self.positions = {}
        for asset_idx, asset in enumerate(last_date_record["Asset"].unique()):
            self.positions[asset] = {
                "Allocation": last_date_record.loc[last_date_record["Asset"] == asset][
                    "Amount"
                ].values[0]
                * date_return[asset_idx]
                / self.portfolio_value,
                "Amount": last_date_record.loc[last_date_record["Asset"] == asset][
                    "Amount"
                ].values[0]
                * date_return[asset_idx],
            }

    def _update_history(self, date, rebalance):
        if rebalance:
            if len(self.history) == 0:
                for asset in self.positions:
                    self.history.append(
                        {
                            "Date": date,
                            "Asset": asset,
                            "Group": 1,
                            "Holding": True,
                            "Allocation": self.positions[asset]["Allocation"],
                            "Amount": self.positions[asset]["Amount"],
                            "Asset_Price": self.df.loc[date, asset],
                        }
                    )
            else:
                date_idx = self.dates.index(date)
                last_date_record = pd.DataFrame(self.history).loc[
                    (pd.DataFrame(self.history)["Date"] == self.dates[date_idx - 1])
                    & (pd.DataFrame(self.history)["Holding"])
                ]
                if self.dates[date_idx - 1] in self.balancing_dates:
                    last_date_record = last_date_record.loc[
                        last_date_record["Group"] == 1
                    ]
                assets = last_date_record["Asset"].unique().tolist()
                if len(assets) != 0:
                    prices_df = self.df.loc[
                        [self.dates[date_idx - 1], self.dates[date_idx]], assets
                    ]
                    try:
                        date_return = (
                            calculate_returns(array=prices_df.values, period=1).reshape(
                                -1,
                            )
                            + 1
                        )
                    except Exception as e:
                        self.error = prices_df.copy()
                        raise ValueError(
                            f"df contains nans on active dates ({self.dates[date_idx - 1], self.dates[date_idx]})"
                        )
                    for asset_idx, asset in enumerate(assets):
                        self.history.append(
                            {
                                "Date": self.dates[date_idx - 1],
                                "Asset": asset,
                                "Group": 0,
                                "Holding": True if asset in self.positions else False,
                                "Allocation": last_date_record.loc[
                                    last_date_record["Asset"] == asset
                                ]["Amount"].values[0]
                                * date_return[asset_idx]
                                / self.portfolio_value,
                                "Amount": last_date_record.loc[
                                    last_date_record["Asset"] == asset
                                ]["Amount"].values[0]
                                * date_return[asset_idx],
                                "Asset_Price": self.df.loc[date, asset],
                            }
                        )
                    for asset in self.positions:
                        self.history.append(
                            {
                                "Date": date,
                                "Asset": asset,
                                "Group": 1,
                                "Holding": True,
                                "Allocation": self.positions[asset]["Allocation"],
                                "Amount": self.positions[asset]["Amount"],
                                "Asset_Price": self.df.loc[date, asset],
                            }
                        )
                else:
                    for asset in self.positions:
                        self.history.append(
                            {
                                "Date": date,
                                "Asset": asset,
                                "Group": 1,
                                "Holding": True,
                                "Allocation": self.positions[asset]["Allocation"],
                                "Amount": self.positions[asset]["Amount"],
                                "Asset_Price": self.df.loc[date, asset],
                            }
                        )
        else:
            date_idx = self.dates.index(date)
            last_date_record = pd.DataFrame(self.history).loc[
                (pd.DataFrame(self.history)["Date"] == self.dates[date_idx - 1])
                & (pd.DataFrame(self.history)["Holding"])
            ]
            if self.dates[date_idx - 1] in self.balancing_dates:
                last_date_record = last_date_record.loc[last_date_record["Group"] == 1]
            last_date_record_assets = last_date_record["Asset"].unique().tolist()
            if len(last_date_record_assets) == 0:
                self.history.append(
                    {
                        "Date": date,
                        "Asset": np.nan,
                        "Group": np.nan,
                        "Holding": np.nan,
                        "Allocation": np.nan,
                        "Amount": np.nan,
                        "Asset_Price": np.nan,
                    }
                )
            else:
                prices_df = self.df.loc[
                    [self.dates[date_idx - 1], self.dates[date_idx]],
                    last_date_record_assets,
                ]
                try:
                    date_return = (
                        calculate_returns(array=prices_df.values, period=1).reshape(
                            -1,
                        )
                        + 1
                    )
                except Exception as e:
                    self.error = prices_df.copy()
                    raise ValueError(
                        f"df contains nans on active dates ({self.dates[date_idx - 1], self.dates[date_idx]})"
                    )
                sold_assets = []
                for asset in last_date_record_assets:
                    if asset not in self.positions:
                        sold_assets.append(asset)
                if len(sold_assets) == 0:
                    for asset_idx, asset in enumerate(last_date_record_assets):
                        self.history.append(
                            {
                                "Date": date,
                                "Asset": asset,
                                "Group": 0,
                                "Holding": True,
                                "Allocation": last_date_record.loc[
                                    last_date_record["Asset"] == asset
                                ]["Amount"].values[0]
                                * date_return[asset_idx]
                                / self.portfolio_value,
                                "Amount": last_date_record.loc[
                                    last_date_record["Asset"] == asset
                                ]["Amount"].values[0]
                                * date_return[asset_idx],
                                "Asset_Price": self.df.loc[self.dates[date_idx], asset],
                            }
                        )
                else:
                    for asset_idx, asset in enumerate(last_date_record_assets):
                        if asset in sold_assets:
                            self.history.append(
                                {
                                    "Date": date,
                                    "Asset": asset,
                                    "Group": 0,
                                    "Holding": False,
                                    "Allocation": last_date_record.loc[
                                        last_date_record["Asset"] == asset
                                    ]["Amount"].values[0]
                                    * date_return[asset_idx]
                                    / self.portfolio_value,
                                    "Amount": last_date_record.loc[
                                        last_date_record["Asset"] == asset
                                    ]["Amount"].values[0]
                                    * date_return[asset_idx],
                                    "Asset_Price": self.df.loc[
                                        self.dates[date_idx], asset
                                    ],
                                }
                            )
                        else:
                            self.history.append(
                                {
                                    "Date": date,
                                    "Asset": asset,
                                    "Group": 0,
                                    "Holding": True,
                                    "Allocation": last_date_record.loc[
                                        last_date_record["Asset"] == asset
                                    ]["Amount"].values[0]
                                    * date_return[asset_idx]
                                    / self.portfolio_value,
                                    "Amount": last_date_record.loc[
                                        last_date_record["Asset"] == asset
                                    ]["Amount"].values[0]
                                    * date_return[asset_idx],
                                    "Asset_Price": self.df.loc[
                                        self.dates[date_idx], asset
                                    ],
                                }
                            )

    def _update_portfolio_value(self, date):
        date_idx = self.dates.index(date)
        last_date_record = pd.DataFrame(self.history).loc[
            (pd.DataFrame(self.history)["Date"] == self.dates[date_idx - 1])
            & (pd.DataFrame(self.history)["Holding"])
        ]
        assets = last_date_record["Asset"].unique().tolist()
        prices_df = self.df.loc[
            [self.dates[date_idx - 1], self.dates[date_idx]], assets
        ]
        try:
            date_return = (
                calculate_returns(array=prices_df.values, period=1).reshape(
                    -1,
                )
                + 1
            )
        except Exception as e:
            self.error = prices_df.copy()
            raise ValueError(
                f"df contains nans on active dates ({self.dates[date_idx - 1], self.dates[date_idx]})"
            )
        amounts = last_date_record["Amount"].values
        self.portfolio_value = np.dot(amounts, date_return) + self.liquid_money

    def _rebalance(self, date, buy_signals):
        if len(buy_signals) == 0:
            current_positions = list(self.positions.keys())
            for asset in current_positions:
                self._sell_(asset=asset, quantity=True, date=date)
        else:
            target_weights = self._split_number_into_parts(
                number=self.target_weight, n=len(buy_signals)
            )
            current_positions = list(self.positions.keys())
            keeping_positions = list(set(current_positions) & set(buy_signals))
            keeping_target_weights = target_weights[: len(keeping_positions)]
            selling_positions = list(set(current_positions) - set(buy_signals))
            buying_positions = list(set(buy_signals) - set(current_positions))
            buying_target_weights = target_weights[len(keeping_positions) :]
            if len(selling_positions) != 0:
                for asset_to_sell in selling_positions:
                    self._sell_(asset=asset_to_sell, quantity=True, date=date)
            if len(keeping_positions) != 0:
                keeping_selling_positions = []
                keeping_buying_positions = []
                for asset_to_keep, target_weight in zip(
                    keeping_positions, keeping_target_weights
                ):
                    if self.positions[asset_to_keep]["Allocation"] > target_weight:
                        keeping_selling_positions.append(asset_to_keep)
                    else:
                        keeping_buying_positions.append(asset_to_keep)
                keeping_positions = keeping_selling_positions + keeping_buying_positions
                for asset_to_keep, target_weight in zip(
                    keeping_positions, keeping_target_weights
                ):
                    if self.positions[asset_to_keep]["Allocation"] > target_weight:
                        self._sell_(
                            asset=asset_to_keep,
                            quantity=(
                                (
                                    self.positions[asset_to_keep]["Allocation"]
                                    - target_weight
                                )
                                * self.positions[asset_to_keep]["Amount"]
                            )
                            / self.positions[asset_to_keep]["Allocation"],
                            date=date,
                        )
                    elif self.positions[asset_to_keep]["Allocation"] < target_weight:
                        self._buy_(
                            asset=asset_to_keep,
                            quantity=(
                                (
                                    target_weight
                                    * self.positions[asset_to_keep]["Amount"]
                                )
                                / self.positions[asset_to_keep]["Allocation"]
                            )
                            - self.positions[asset_to_keep]["Amount"],
                            date=date,
                        )
            if len(buying_positions) != 0:
                buying_splits = [
                    self.portfolio_value * target_weight
                    for target_weight in buying_target_weights
                ]
                for asset_to_buy, buying_amount in zip(buying_positions, buying_splits):
                    self._buy_(asset=asset_to_buy, quantity=buying_amount, date=date)

    def _sell_(self, asset, quantity, date):
        if asset not in self.positions:
            raise ValueError(
                f"You can't sell {asset} because it's not in the portfolio."
            )
        if quantity is True:
            self.trades.append(
                {
                    "Date": date,
                    "Asset": asset,
                    "Entry_Date": self._calculate_entry_date(asset=asset, date=date),
                    "Rebalance_Day": True if date in self.balancing_dates else False,
                    "Action": "Sell",
                    "Amount": self.positions[asset]["Amount"],
                    "Price": self.df.loc[date, asset],
                    "Shares": self.positions[asset]["Amount"]
                    / self.df.loc[date, asset],
                    "Resulting_Amount": 0,
                }
            )
            if self.verbose == 1:
                print(f"Selling {self.positions[asset]['Amount']} of {asset}")
            self.liquid_money += self.positions[asset]["Amount"]
            del self.positions[asset]
        else:
            if self.positions[asset]["Amount"] < quantity:
                raise ValueError(
                    f"You can't sell ${quantity} of {asset}, you only have ${self.positions[asset]['Amount']}"
                )
            else:
                self.trades.append(
                    {
                        "Date": date,
                        "Asset": asset,
                        "Entry_Date": self._calculate_entry_date(
                            asset=asset, date=date
                        ),
                        "Rebalance_Day": (
                            True if date in self.balancing_dates else False
                        ),
                        "Action": "Sell",
                        "Amount": quantity,
                        "Price": self.df.loc[date, asset],
                        "Shares": quantity / self.df.loc[date, asset],
                        "Resulting_Amount": self.positions[asset]["Amount"] - quantity,
                    }
                )
                self.liquid_money += quantity
                self.positions[asset]["Amount"] -= quantity
                self.positions[asset]["Allocation"] = (
                    self.positions[asset]["Amount"] / self.portfolio_value
                )

    def _buy_(self, asset, quantity, date):
        if self.verbose == 1:
            print(f"Buying {quantity} of {asset}")
        if quantity > self.liquid_money:
            if quantity - self.liquid_money < 0.0001:
                quantity = self.liquid_money
            else:
                raise ValueError(
                    f"Cannot buy {quantity} of {asset} because the liquid money is: {self.liquid_money:.2f}"
                )
        self.trades.append(
            {
                "Date": date,
                "Asset": asset,
                "Entry_Date": self._calculate_entry_date(asset=asset, date=date),
                "Rebalance_Day": True if date in self.balancing_dates else False,
                "Action": "Buy",
                "Amount": quantity,
                "Price": self.df.loc[date, asset],
                "Shares": quantity / self.df.loc[date, asset],
                "Resulting_Amount": (
                    quantity
                    if asset not in self.positions
                    else self.positions[asset]["Amount"] + quantity
                ),
            }
        )
        self.liquid_money -= quantity
        if asset in self.positions:
            self.positions[asset]["Amount"] += quantity
            self.positions[asset]["Allocation"] = (
                self.positions[asset]["Amount"] / self.portfolio_value
            )
        else:
            self.positions[asset] = {
                "Allocation": quantity / self.portfolio_value,
                "Amount": quantity,
            }

    def _generate_id(self):

        possible_replacements = string.digits + string.ascii_lowercase
        modified_string = list(self.id_structure)
        for i, char in enumerate(modified_string):
            if char == "1":
                modified_string[i] = random.choice(possible_replacements)
        return "".join(modified_string)

    def _calculate_entry_date(self, asset, date):
        if date == self.dates[0]:
            return date
        date_idx = self.dates.index(date)
        previous_dates = self.dates[:date_idx]
        reversed_dates = previous_dates[::-1]
        if any(asset in holdings for holdings in self.holdings.values()):
            for date_idx, _date_ in enumerate(reversed_dates):
                date_assets = self.holdings[_date_]
                if (date_idx == 0) & (asset not in date_assets):
                    return date
                if asset not in date_assets:
                    return reversed_dates[date_idx - 1]
                if _date_ == reversed_dates[-1]:
                    return self.dates[0]
        else:
            return date

    def _split_number_into_parts(self, number, n):

        base_part = number / n
        remainder = number - base_part * n
        parts = [base_part] * n
        for i in range(int(remainder * n)):
            parts[i] += 1 / n
        return parts

    def plot_equity(self, figsize=(30, 10)):
        value = pd.DataFrame(self.value)
        value["Date"] = pd.to_datetime(value["Date"])
        value.set_index("Date", inplace=True)
        average_value = value["Value"].mean()
        fig, ax = plt.subplots(figsize=figsize, facecolor="black")
        ax.set_facecolor("black")
        ax.plot(
            value.index, value["Value"], label="Equity Value", color="cyan", linewidth=2
        )
        ax.axhline(
            average_value,
            color="gray",
            linestyle="--",
            linewidth=2,
            label=f"Average Value: {average_value:.2f}",
        )
        ax.set_title(
            f"Portfolio Equity Over Time ({self.portfolio_id})",
            fontsize=20,
            fontweight="bold",
            color="white",
        )
        ax.set_xlabel("Date", fontsize=14, color="white")
        ax.set_ylabel("Equity Value", fontsize=14, color="white")
        ax.grid(True, linestyle="--", alpha=0.6, color="gray")
        fig.autofmt_xdate()
        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.legend(fontsize=12, facecolor="black", edgecolor="white", labelcolor="white")

        plt.show()


class MonteCarloSimulator:
    """
    A class for simulating scenarios using the Monte Carlo method on a dataset. This simulator
    generates paths based on the mean and standard deviation of an input array and optionally
    updates the statistics of each feature after every simulation step.

    Attributes
    ----------
    steps : int
        Number of simulation steps (time steps) to generate.
    paths : int
        Number of Monte Carlo simulation paths (scenarios) to generate.

    Methods
    -------
    simulate(X, axis=0, update=False):
        Runs the Monte Carlo simulation on the input data array `X`.
    """

    def __init__(self, steps, paths):
        """
        Initializes the MonteCarloSimulator with the specified number of steps and paths.

        Parameters
        ----------
        steps : int
            The number of time steps in each simulation.
        paths : int
            The number of simulation paths to generate.
        """
        self.steps = steps
        self.paths = paths

    def simulate(self, X, axis=0, update=False):
        """
        Performs Monte Carlo simulations based on the statistics (mean and standard deviation) of the input array `X`.

        If `update` is True, the mean and standard deviation are recalculated for each feature at every simulation step.

        Parameters
        ----------
        X : np.ndarray
            The input data array used to initialize the simulation's statistics. Must be a 2D array.
        axis : int, optional
            The axis along which to calculate the statistics. Default is 0 (rows).
        update : bool, optional
            If True, updates the mean and standard deviation after each simulation step. Default is False.

        Returns
        -------
        simulations : np.ndarray
            A 3D array of shape (steps, paths, features) representing the simulated paths.

        Raises
        ------
        ValueError
            If `X` is not a 2D numpy array, contains NaNs, or if `axis` is not 0 or 1.
        """

        axles = [0, 1]
        if not isinstance(X, np.ndarray):
            raise ValueError("X must be an array")
        if X.ndim != 2:
            raise ValueError("Array must be bidimensional")
        if np.isnan(X).any():
            raise ValueError("Array contains NaNs")
        if axis not in axles:
            raise ValueError("Axis out of range")
        axles.remove(axis)
        if update not in [True, False]:
            raise ValueError("update not a boolean parameter")

        if update:
            std = np.zeros((1, self.paths, X.shape[axles[0]]))
            mean = np.zeros((1, self.paths, X.shape[axles[0]]))
            for feature in range(X.shape[axles[0]]):
                std[0, :, feature] = np.repeat(
                    np.std(np.take(X, feature, axis=axles[0])), self.paths
                )
                mean[0, :, feature] = np.repeat(
                    np.mean(np.take(X, feature, axis=axles[0])), self.paths
                )

            simulations = np.zeros((self.steps, self.paths, X.shape[axles[0]]))
            for step in range(self.steps):
                current_simulations = np.random.normal(
                    loc=mean, scale=std, size=(1, self.paths, X.shape[axles[0]])
                )
                for feature in range(X.shape[axles[0]]):
                    std[0, :, feature] = np.std(
                        np.concatenate(
                            [
                                np.tile(
                                    np.take(X, feature, axis=axles[0]).reshape(-1, 1),
                                    self.paths,
                                ),
                                np.take(
                                    current_simulations[0, :, :], feature, axis=1
                                ).reshape(1, -1),
                            ],
                            axis=0,
                        ),
                        axis=0,
                    )
                    mean[0, :, feature] = np.mean(
                        np.concatenate(
                            [
                                np.tile(
                                    np.take(X, feature, axis=axles[0]).reshape(-1, 1),
                                    self.paths,
                                ),
                                np.take(
                                    current_simulations[0, :, :], feature, axis=1
                                ).reshape(1, -1),
                            ],
                            axis=0,
                        ),
                        axis=0,
                    )
                simulations[step, :, :] = current_simulations[0, :, :]

        else:
            std = np.std(X, axis=axis)
            mean = np.mean(X, axis=axis)
            simulations = np.random.normal(
                loc=mean, scale=std, size=(self.steps, self.paths, X.shape[axles[0]])
            )

        return simulations
