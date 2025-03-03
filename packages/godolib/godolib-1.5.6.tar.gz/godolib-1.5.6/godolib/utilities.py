import pandas as pd
import random
import string
from functools import reduce


def split_df_by_nan_config(df):
    """
    Splits a DataFrame into groups of columns based on their NaN configurations.

    This function analyzes the NaN (missing values) patterns across columns in the input DataFrame,
    groups columns with identical NaN patterns, and returns a list of smaller DataFrames.
    Each returned DataFrame corresponds to a unique NaN configuration and has no missing values.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame to split into groups based on NaN configurations.

    Returns:
    --------
    groups : list of pandas.DataFrame
        A list of DataFrames, where each DataFrame contains columns that share the same
        NaN configuration (i.e., the same pattern of missing values). All NaN values are
        dropped from these DataFrames.

    Example:
    --------
    >>> import pandas as pd
    >>> data = {
    ...     'A': [1, 2, None],
    ...     'B': [4, None, None],
    ...     'C': [1, 2, 3],
    ...     'D': [None, None, None]
    ... }
    >>> df = pd.DataFrame(data)
    >>> groups = split_df_by_nan_config(df)
    >>> for group in groups:
    ...     print(group)

    Output:
    --------
       A
    0  1.0
    1  2.0

       B
    0  4.0

       C
    0  1
    1  2
    2  3
    """

    # Create a dictionary to store the NaN pattern for each column
    nan_config = {}
    for column_idx, column in enumerate(df):
        nan_config[column] = df.isna().iloc[:, column_idx].tolist()

    # Group columns by their NaN patterns
    grouped = {}
    for key, value in nan_config.items():
        value_tuple = tuple(value)  # Convert the NaN pattern to a tuple for hashing
        if value_tuple not in grouped:
            grouped[value_tuple] = []
        grouped[value_tuple].append(key)

    # Extract groups of columns and drop NaN values
    grouped_columns = list(grouped.values())
    groups = [df[current_group].dropna().copy() for current_group in grouped_columns]

    return groups


def apply_function_by_groups(df, func):
    """
    Applies a given function to groups of columns in a DataFrame, grouped by their NaN configurations.

    This function uses `split_df_by_nan_config` to split the input DataFrame into groups of columns
    that share the same NaN pattern. It then applies the provided function to each group and
    concatenates the results into a single DataFrame.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame on which to apply the function.

    func : callable
        A function that takes a DataFrame as input and returns a DataFrame as output.
        This function will be applied to each group of columns with the same NaN configuration.

    Returns:
    --------
    result : pandas.DataFrame
        A DataFrame obtained by concatenating the results of applying `func` to each group.

    Example:
    --------
    >>> import pandas as pd
    >>> data = {
    ...     'A': [1, 2, None],
    ...     'B': [4, None, None],
    ...     'C': [1, 2, 3],
    ...     'D': [None, None, None]
    ... }
    >>> df = pd.DataFrame(data)
    >>> def custom_func(group):
    ...     return group.fillna(0)
    >>> result = apply_function_by_groups(df, custom_func)
    >>> print(result)

    Output:
    --------
         A    B  C    D
    0  1.0  4.0  1  0.0
    1  2.0  0.0  2  0.0
    2  0.0  0.0  3  0.0
    """
    groups = split_df_by_nan_config(df)
    result = [func(group) for group in groups]
    return pd.concat(result, axis=1)


def split_df_by_nan_config(df):
    """
    Splits a DataFrame into groups of columns based on their NaN configurations.

    This function analyzes the NaN (missing values) patterns across columns in the input DataFrame,
    groups columns with identical NaN patterns, and returns a list of smaller DataFrames.
    Each returned DataFrame corresponds to a unique NaN configuration and has no missing values.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame to split into groups based on NaN configurations.

    Returns:
    --------
    groups : list of pandas.DataFrame
        A list of DataFrames, where each DataFrame contains columns that share the same
        NaN configuration (i.e., the same pattern of missing values). All NaN values are
        dropped from these DataFrames.

    Example:
    --------
    >>> import pandas as pd
    >>> data = {
    ...     'A': [1, 2, None],
    ...     'B': [4, None, None],
    ...     'C': [1, 2, 3],
    ...     'D': [None, None, None]
    ... }
    >>> df = pd.DataFrame(data)
    >>> groups = split_df_by_nan_config(df)
    >>> for group in groups:
    ...     print(group)

    Output:
    --------
       A
    0  1.0
    1  2.0

       B
    0  4.0

       C
    0  1
    1  2
    2  3
    """

    # Create a dictionary to store the NaN pattern for each column
    nan_config = {}
    for column_idx, column in enumerate(df.columns):
        nan_config[column] = df.isna().iloc[:, column_idx].tolist()

    # Group columns by their NaN patterns
    grouped = {}
    for key, value in nan_config.items():
        value_tuple = tuple(value)  # Convert the NaN pattern to a tuple for hashing
        if value_tuple not in grouped:
            grouped[value_tuple] = []
        grouped[value_tuple].append(key)

    # Extract groups of columns and drop NaN values
    grouped_columns = list(grouped.values())
    groups = [df[current_group].dropna().copy() for current_group in grouped_columns]
    groups = [group for group in groups if not group.empty]

    return groups


def func_by_groups(group, func, *args, **kwargs):
    applied_func_array = func(array=group.values, *args, **kwargs)
    if len(applied_func_array) == 0:
        return pd.DataFrame()
    return pd.DataFrame(
        applied_func_array,
        index=group.index[-applied_func_array.shape[0] :],
        columns=group.columns,
    )


def remove_holdings(holdings, to_remove_holdings):
    """
    Removes specified elements from the lists in a dictionary.

    This function takes a dictionary where each key is associated with a list of elements
    and removes specified elements from these lists.

    Parameters:
    -----------
    holdings : dict
        A dictionary where keys are categories (e.g., ETF names) and values are lists of holdings.

    to_remove_holdings : iterable
        An iterable containing elements to be removed from the lists in the dictionary.

    Returns:
    --------
    new_holdings : dict
        A new dictionary with the same keys as the input, but with the specified elements
        removed from the lists.

    Example:
    --------
    >>> holdings = {
    ...     'ETF1': ['AAPL', 'GOOG', 'MSFT'],
    ...     'ETF2': ['GOOG', 'AMZN', 'NFLX']
    ... }
    >>> to_remove_holdings = ['GOOG', 'NFLX']
    >>> result = remove_holdings(holdings, to_remove_holdings)
    >>> print(result)

    Output:
    --------
    {'ETF1': ['AAPL', 'MSFT'], 'ETF2': ['AMZN']}
    """
    new_holdings = {}
    for etf in holdings:
        new_holdings[etf] = [
            holding for holding in holdings[etf] if holding not in to_remove_holdings
        ]
    return new_holdings


# def nans_per_idx(df):
#     """
#     Identifies missing values (NaNs) for each index in a DataFrame.

#     This function iterates through the indices of the DataFrame and identifies
#     the columns with NaN values for each index. The results are stored in a dictionary
#     where the keys are the string representations of the indices and the values are
#     lists of column names with NaN values.

#     Parameters:
#     -----------
#     df : pandas.DataFrame
#         The input DataFrame to analyze for missing values.

#     Returns:
#     --------
#     indices_nans : dict
#         A dictionary where keys are string representations of the DataFrame indices,
#         and values are lists of column names with NaN values for each index.

#     Example:
#     --------
#     >>> import pandas as pd
#     >>> data = {
#     ...     'A': [1, None, 3],
#     ...     'B': [4, 5, None],
#     ...     'C': [None, None, 9]
#     ... }
#     >>> df = pd.DataFrame(data, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
#     >>> result = nans_per_idx(df)
#     >>> print(result)

#     Output:
#     --------
#     {
#         '2023-01-01': ['C'],
#         '2023-01-02': ['A', 'C'],
#         '2023-01-03': ['B']
#     }
#     """
#     indices_nans = {}
#     for idx in df.index:
#         series = df.loc[idx]
#         indices_nans[idx.strftime("%Y-%m-%d")] = (
#             series.isna().loc[series.isna()].index.tolist()
#         )
#     return indices_nans


def extract_non_active_since_until(df, since, until):
    """
    Identifies columns and indices in a DataFrame with missing values within a specified date range.

    This function uses `nans_per_idx` to find missing values (NaNs) for each index in the DataFrame,
    filters the results based on a date range, and returns the columns and indices with missing values.

    Parameters:
    -----------
    df : pandas.DataFrame
        The input DataFrame to analyze.

    since : str
        The start date (inclusive) of the date range to consider. Should be in a format parsable by pandas.

    until : str
        The end date (inclusive) of the date range to consider. Should be in a format parsable by pandas.

    Returns:
    --------
    nan_columns : list
        A list of column names with missing values within the specified date range.

    nan_indices : list
        A list of string representations of indices where all columns have missing values.

    Example:
    --------
    >>> import pandas as pd
    >>> data = {
    ...     'A': [1, None, 3],
    ...     'B': [4, 5, None],
    ...     'C': [None, None, 9]
    ... }
    >>> df = pd.DataFrame(data, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
    >>> nan_columns, nan_indices = extract_non_active_since_until(df, '2023-01-01', '2023-01-03')
    >>> print(nan_columns)
    >>> print(nan_indices)

    Output:
    --------
    ['C', 'A', 'B']
    ['2023-01-02']
    """
    date_nans = {
        date.strftime("%Y-%m-%d"): [
            column
            for column in df.loc[date].isna().loc[df.loc[date].isna()].index.tolist()
        ]
        for date in df.index
    }
    # date_nans = nans_per_idx(df)
    nan_columns = []
    nan_indices = []
    for str_date, nan_holdings in date_nans.items():
        if len(nan_holdings) == df.shape[1]:
            nan_indices.append(str_date)
            continue
        if not (
            pd.to_datetime(since) <= pd.to_datetime(str_date) <= pd.to_datetime(until)
        ):
            continue
        for holding in nan_holdings:
            if holding not in nan_columns:
                nan_columns.append(holding)
    return nan_columns, nan_indices


def extract_common_signal(signals):
    """
    Extracts the common elements across multiple dictionaries of signals.

    This function checks that all dictionaries in the input list have the same keys,
    then finds the common elements for each key across all dictionaries.

    Parameters:
    -----------
    signals : list of dict
        A list of dictionaries where each key maps to a list or set of elements.

    Returns:
    --------
    common_signal : dict
        A dictionary with the same keys as the input dictionaries, where each key maps
        to the list of common elements across all dictionaries for that key.

    Raises:
    -------
    ValueError
        If the dictionaries in the input list do not have identical keys.

    Example:
    --------
    >>> signals = [
    ...     {'2023-01-01': ['A', 'B'], '2023-01-02': ['C', 'D']},
    ...     {'2023-01-01': ['B', 'A'], '2023-01-02': ['D', 'C']},
    ...     {'2023-01-01': ['A', 'B'], '2023-01-02': ['C']}
    ... ]
    >>> result = extract_common_signal(signals)
    >>> print(result)

    Output:
    --------
    {
        '2023-01-01': ['A', 'B'],
        '2023-01-02': ['C']
    }
    """
    reference_keys = set(signals[0].keys())
    if not all(set(d.keys()) == reference_keys for d in signals):
        raise ValueError("Dictionaries keys must be the same")
    common_signal = {}
    for date in signals[0].keys():
        all_signals = [set(s[date]) for s in signals]
        common_elements = reduce(lambda x, y: x & y, all_signals)
        common_signal[date] = list(common_elements)
    return common_signal


def match_keys(signals):
    unique_keys = []
    for signal in signals:
        for current_key in signal.keys():
            if current_key not in unique_keys:
                unique_keys.append(current_key)
    filtered_keys = [
        current_key
        for current_key in unique_keys
        if all(current_key in signal for signal in signals)
    ]
    return [
        {
            signal_key: signal_value
            for signal_key, signal_value in signal.items()
            if signal_key in filtered_keys
        }
        for signal in signals
    ]


def clean_signal(signal):
    """
    Filters a signal dictionary to include only entries from the first non-empty list of assets onward.

    Parameters:
    ----------
    signal : dict
        A dictionary where:
        - Keys are dates represented as strings (e.g., 'YYYY-MM-DD').
        - Values are lists of assets associated with the corresponding dates.

    Returns:
    -------
    dict
        A filtered dictionary that includes only the entries where the date is
        greater than or equal to the first date with a non-empty list of assets.

    Example:
    --------
    >>> signal = {
    ...     "2025-01-01": [],
    ...     "2025-01-02": [],
    ...     "2025-01-03": ["AAPL", "TSLA"],
    ...     "2025-01-04": ["GOOGL"],
    ... }
    >>> clean_signal(signal)
    {'2025-01-03': ['AAPL', 'TSLA'], '2025-01-04': ['GOOGL']}

    Notes:
    ------
    - If all values in the dictionary are empty lists, the function will return an empty dictionary.
    - Dates are converted to pandas datetime objects for robust comparison.
    """
    if all(len(s) == 0 for s in signal.values()):
        print("Empty signal")
        return signal
    # if len([v for vs in signal.values() for v in vs]) == 0:
    #     raise ValueError("Empty signal")
    # Identify the first date with a non-empty list of assets
    for date, assets in signal.items():
        if len(assets) != 0:
            starting_date = date  # Save the starting date
            break

    # Filter the dictionary to include only entries from the starting date onward
    cleaned_signal = {
        date: assets
        for date, assets in signal.items()
        if pd.to_datetime(date) >= pd.to_datetime(starting_date)
    }

    return cleaned_signal


def randomize_string(input_string):
    """
    Randomizes an input string based on specific character rules.

    This function processes each character in the input string and substitutes it
    according to the following rules:
    - 'n': Replaced with a random digit (0-9).
    - 'l': Replaced with a random lowercase letter (a-z).
    - '0': Replaced randomly with either a digit (0-9) or a lowercase letter (a-z).
    - Any other character remains unchanged.

    Parameters:
    -----------
    input_string : str
        The input string to be randomized.

    Returns:
    --------
    result : str
        A new string with characters randomized based on the above rules.

    Example:
    --------
    >>> import random
    >>> import string
    >>> randomize_string("nl0-nl0")
    '4gq-8w2'  # Example output (randomized)
    """
    result = []
    for char in input_string:
        if char == "n":
            result.append(str(random.randint(0, 9)))
        elif char == "l":
            result.append(random.choice(string.ascii_lowercase))
        elif char == "0":
            if random.choice([True, False]):
                result.append(str(random.randint(0, 9)))
            else:
                result.append(random.choice(string.ascii_lowercase))
        else:
            result.append(char)
    return "".join(result)


def spot_on(df, ending_string):
    """
    Filters and renames columns of a DataFrame based on a specified suffix.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame containing columns to be filtered.
    ending_string : str
        The suffix to search for in the column names of the DataFrame.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame containing only the columns whose names end with `ending_string`.
        The columns in the returned DataFrame have the specified suffix removed from their names.

    Description:
    -----------
    The function performs the following steps:
    1. Creates a copy of the input DataFrame to avoid modifying the original data.
    2. Filters the columns of the DataFrame to include only those that end with the specified `ending_string`.
    3. Removes the specified suffix (`ending_string`) from the names of the filtered columns.
    4. Returns the filtered and renamed DataFrame.

    Example:
    -------
    >>> import pandas as pd
    >>> data = {
    ...     'sales_2021': [100, 200, 150],
    ...     'sales_2022': [120, 210, 180],
    ...     'profit_2021': [50, 80, 70],
    ...     'profit_2022': [60, 90, 85]
    ... }
    >>> df = pd.DataFrame(data)
    >>> print(df)
       sales_2021  sales_2022  profit_2021  profit_2022
    0         100         120           50           60
    1         200         210           80           90
    2         150         180           70           85

    >>> spot_on(df, '_2022')
       sales  profit
    0    120      60
    1    210      90
    2    180      85
    """
    filtered_df = df.copy()
    target_columns = [column for column in df if column.endswith(ending_string)]
    filtered_df = filtered_df[target_columns]
    filtered_df.columns = [column.removesuffix(ending_string) for column in filtered_df]
    return filtered_df


def format_datetime_df(df):
    formatted_df = df.copy()
    if ("date" in df.columns) and ("Date" not in df.columns):
        formatted_df.rename(columns={"date": "Date"}, inplace=True)
    elif ("Date" not in df.columns) and ("date" not in df.columns):
        raise ValueError("No date columns")
    formatted_df["Date"] = pd.to_datetime(formatted_df["Date"])
    formatted_df.set_index("Date", inplace=True)
    return formatted_df


def clean_df(df, since, until, insignificance_percentage=0.01):
    if len(df.columns.tolist()) != len(list(set(df.columns.tolist()))):
        raise ValueError("Columns must not repeat")
    cleaned_df = df.loc[(df.index >= since) & (df.index <= until)].copy()
    nans_per_idx = {
        date.strftime("%Y-%m-%d"): [
            column
            for column in cleaned_df.loc[date]
            .isna()
            .loc[cleaned_df.loc[date].isna()]
            .index.tolist()
        ]
        for date in cleaned_df.index
    }
    nan_indices = [
        idx
        for idx in nans_per_idx
        if cleaned_df.shape[1] * insignificance_percentage
        >= len(list(set(cleaned_df.columns.tolist()) - set(nans_per_idx[idx])))
    ]
    cleaned_df.drop(index=nan_indices, inplace=True)
    nans_per_column = {
        column: [
            date
            for date in cleaned_df[column]
            .isna()
            .loc[cleaned_df[column].isna()]
            .index.tolist()
        ]
        for column in cleaned_df
    }
    nan_columns = [
        column for column in nans_per_column if len(nans_per_column[column]) >= 1
    ]
    cleaned_df.drop(columns=nan_columns, inplace=True)
    return cleaned_df


# def clean_df(df, since, until, insignificance_percentage=0.01):
#     cleaned_df = df.copy()
#     _, nan_indices = extract_non_active_since_until(df, since=since, until=until)
#     cleaned_df.drop(index=nan_indices, inplace=True)
#     nan_cols, _ = extract_non_active_since_until(df, since=since, until=until)
#     cleaned_df.drop(columns=nan_cols, inplace=True)
#     return cleaned_df.loc[(since <= cleaned_df.index) & (cleaned_df.index <= until)]
