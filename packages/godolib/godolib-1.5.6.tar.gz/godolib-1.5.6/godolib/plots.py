import numpy as np
import matplotlib.pyplot as plt
import math
import pandas as pd


def plot_histograms_with_stats(data, figsize=(15, 5)):
    """
    Plots histograms for each column in a given array or DataFrame, highlighting statistical metrics.

    If the input has only one column, the histogram spans the entire figure.

    Parameters:
    -----------
    data : pd.DataFrame or np.ndarray
        The input data for which histograms will be generated. Each column in the data is plotted as a separate histogram.
        If a DataFrame is passed, column names are used in the plot titles. If a NumPy array is provided, generic column
        names ('Column 1', 'Column 2', etc.) are used.
    figsize : tuple, optional
        The size of the figure (width, height). Default is (15, 5).

    Returns:
    --------
    None
        Displays a grid of histogram plots.

    Notes:
    ------
    - For each column, the function calculates:
        - Mean: Displayed with a gold dashed line.
        - Standard deviation intervals: Displayed as light green dotted lines around the mean.
        - Furthest point: Marked with a red solid line, representing the data point furthest from the mean.
    - Unused subplots (if the number of columns is not a multiple of 3) are hidden.
    """

    # Si el input es un DataFrame, obtener los nombres de las columnas y convertirlo a array
    if isinstance(data, pd.DataFrame):
        column_names = data.columns
        data = data.values
    else:
        # Si es un array, usar nombres de columnas genéricos
        column_names = [f"Column {i+1}" for i in range(data.shape[1])]

    num_columns = 3  # Número de columnas en la cuadrícula
    num_plots = data.shape[1]
    num_rows = math.ceil(num_plots / num_columns)  # Número de filas necesarias

    # Manejo especial para una sola columna
    if num_plots == 1:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=figsize)

        # Eliminar NaNs de la columna actual
        column_data = data[:, 0]
        valid_data = column_data[~np.isnan(column_data)]

        # Si no hay datos válidos, no graficar
        if valid_data.size == 0:
            print("No valid data to plot.")
            return

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)
        furthest_point = valid_data[np.argmax(abs(valid_data - mean))]
        furthest_point_dev = abs(furthest_point - mean) / std

        # Histograma en el gráfico único
        ax.hist(valid_data, bins=50, color="cyan", edgecolor="white", alpha=0.7)
        ax.axvline(
            x=mean,
            color="gold",
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, math.ceil(furthest_point_dev) + 1):
            ax.axvline(
                x=mean + i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )
            ax.axvline(
                x=mean - i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )

        # Destacar el punto más lejano
        ax.axvline(
            x=furthest_point,
            color="tomato",
            linestyle="-",
            linewidth=2,
            label=f"Furthest Point = {furthest_point:.2f}",
        )

        # Formato del gráfico
        ax.set_title(f"Histogram of {column_names[0]}", color="white")
        ax.set_xlabel("Values", color="white")
        ax.set_ylabel("Frequency", color="white")
        ax.legend(loc="upper right", facecolor="black", framealpha=0.9)
        ax.grid(True, linestyle="--", alpha=0.4, color="gray")

        plt.tight_layout()
        plt.show()
        return

    # Configuración general para múltiples columnas
    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_columns, figsize=figsize)
    axes = axes.flatten()  # Aplanar los ejes para facilitar la iteración

    # Generar los gráficos para cada columna
    for idx in range(num_plots):
        # Eliminar NaNs de la columna actual
        column_data = data[:, idx]
        valid_data = column_data[~np.isnan(column_data)]

        # Si no hay datos válidos después de eliminar NaNs, pasar al siguiente gráfico
        if valid_data.size == 0:
            axes[idx].axis("off")  # Desactivar subplot
            continue

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)
        furthest_point = valid_data[np.argmax(abs(valid_data - mean))]
        furthest_point_dev = abs(furthest_point - mean) / std

        # Histograma en cada subplot
        axes[idx].hist(valid_data, bins=50, color="cyan", edgecolor="white", alpha=0.7)
        axes[idx].axvline(
            x=mean,
            color="gold",
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, math.ceil(furthest_point_dev) + 1):
            axes[idx].axvline(
                x=mean + i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )
            axes[idx].axvline(
                x=mean - i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )

        # Destacar el punto más lejano
        axes[idx].axvline(
            x=furthest_point,
            color="tomato",
            linestyle="-",
            linewidth=2,
            label=f"Furthest Point = {furthest_point:.2f}",
        )

        # Formato del gráfico
        axes[idx].set_title(f"Histogram of {column_names[idx]}", color="white")
        axes[idx].set_xlabel("Values", color="white")
        axes[idx].set_ylabel("Frequency", color="white")
        axes[idx].legend(loc="upper right", facecolor="black", framealpha=0.9)
        axes[idx].grid(True, linestyle="--", alpha=0.4, color="gray")

    # Apagar subplots extra
    for idx in range(num_plots, len(axes)):
        axes[idx].axis("off")  # Ocultar ejes sobrantes

    plt.tight_layout()
    plt.show()


def save_plot_histograms_with_stats(file_path, data, figsize=(15, 5)):
    """
    Save the 'plot_histograms_with_stats' result.

    Plots histograms for each column in a given array or DataFrame, highlighting statistical metrics.

    If the input has only one column, the histogram spans the entire figure.

    Parameters:
    -----------
    data : pd.DataFrame or np.ndarray
        The input data for which histograms will be generated. Each column in the data is plotted as a separate histogram.
        If a DataFrame is passed, column names are used in the plot titles. If a NumPy array is provided, generic column
        names ('Column 1', 'Column 2', etc.) are used.
    figsize : tuple, optional
        The size of the figure (width, height). Default is (15, 5).

    Returns:
    --------
    None
        Displays a grid of histogram plots.

    Notes:
    ------
    - For each column, the function calculates:
        - Mean: Displayed with a gold dashed line.
        - Standard deviation intervals: Displayed as light green dotted lines around the mean.
        - Furthest point: Marked with a red solid line, representing the data point furthest from the mean.
    - Unused subplots (if the number of columns is not a multiple of 3) are hidden.
    """

    # Si el input es un DataFrame, obtener los nombres de las columnas y convertirlo a array
    if isinstance(data, pd.DataFrame):
        column_names = data.columns
        data = data.values
    else:
        # Si es un array, usar nombres de columnas genéricos
        column_names = [f"Column {i+1}" for i in range(data.shape[1])]

    num_columns = 3  # Número de columnas en la cuadrícula
    num_plots = data.shape[1]
    num_rows = math.ceil(num_plots / num_columns)  # Número de filas necesarias

    # Manejo especial para una sola columna
    if num_plots == 1:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=figsize)

        # Eliminar NaNs de la columna actual
        column_data = data[:, 0]
        valid_data = column_data[~np.isnan(column_data)]

        # Si no hay datos válidos, no graficar
        if valid_data.size == 0:
            print("No valid data to plot.")
            return

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)
        furthest_point = valid_data[np.argmax(abs(valid_data - mean))]
        furthest_point_dev = abs(furthest_point - mean) / std

        # Histograma en el gráfico único
        ax.hist(valid_data, bins=50, color="cyan", edgecolor="white", alpha=0.7)
        ax.axvline(
            x=mean,
            color="gold",
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, math.ceil(furthest_point_dev) + 1):
            ax.axvline(
                x=mean + i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )
            ax.axvline(
                x=mean - i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )

        # Destacar el punto más lejano
        ax.axvline(
            x=furthest_point,
            color="tomato",
            linestyle="-",
            linewidth=2,
            label=f"Furthest Point = {furthest_point:.2f}",
        )

        # Formato del gráfico
        ax.set_title(f"Histogram of {column_names[0]}", color="white")
        ax.set_xlabel("Values", color="white")
        ax.set_ylabel("Frequency", color="white")
        ax.legend(loc="upper right", facecolor="black", framealpha=0.9)
        ax.grid(True, linestyle="--", alpha=0.4, color="gray")

        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches="tight")
        plt.close()
        return

    # Configuración general para múltiples columnas
    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_columns, figsize=figsize)
    axes = axes.flatten()  # Aplanar los ejes para facilitar la iteración

    # Generar los gráficos para cada columna
    for idx in range(num_plots):
        # Eliminar NaNs de la columna actual
        column_data = data[:, idx]
        valid_data = column_data[~np.isnan(column_data)]

        # Si no hay datos válidos después de eliminar NaNs, pasar al siguiente gráfico
        if valid_data.size == 0:
            axes[idx].axis("off")  # Desactivar subplot
            continue

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)
        furthest_point = valid_data[np.argmax(abs(valid_data - mean))]
        furthest_point_dev = abs(furthest_point - mean) / std

        # Histograma en cada subplot
        axes[idx].hist(valid_data, bins=50, color="cyan", edgecolor="white", alpha=0.7)
        axes[idx].axvline(
            x=mean,
            color="gold",
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, math.ceil(furthest_point_dev) + 1):
            axes[idx].axvline(
                x=mean + i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )
            axes[idx].axvline(
                x=mean - i * std, color="lightgreen", linestyle=":", linewidth=1.5
            )

        # Destacar el punto más lejano
        axes[idx].axvline(
            x=furthest_point,
            color="tomato",
            linestyle="-",
            linewidth=2,
            label=f"Furthest Point = {furthest_point:.2f}",
        )

        # Formato del gráfico
        axes[idx].set_title(f"Histogram of {column_names[idx]}", color="white")
        axes[idx].set_xlabel("Values", color="white")
        axes[idx].set_ylabel("Frequency", color="white")
        axes[idx].legend(loc="upper right", facecolor="black", framealpha=0.9)
        axes[idx].grid(True, linestyle="--", alpha=0.4, color="gray")

    # Apagar subplots extra
    for idx in range(num_plots, len(axes)):
        axes[idx].axis("off")  # Ocultar ejes sobrantes

    plt.tight_layout()
    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_time_series_with_std(data, figsize=(15, 5), positive_std_only=False):
    """
    Plots time series for each column in a given DataFrame or array, highlighting standard deviation bands.

    If the input has only one column, the plot spans the entire figure. Displays dates on the X-axis if the index is a pandas DatetimeIndex.

    Parameters:
    -----------
    data : pd.DataFrame or np.ndarray
        The input data for which time series will be generated. Each column in the data is plotted as a separate time series.
        If a DataFrame is passed, column names are used in the plot titles. If a NumPy array is provided, generic column
        names ('Column 1', 'Column 2', etc.) are used.
    figsize : tuple, optional
        The size of the figure (width, height). Default is (15, 5).
    positive_std_only : bool, optional
        If True, only positive standard deviation bands are plotted. Default is False.

    Returns:
    --------
    None
        Displays a grid of time series plots.

    Notes:
    ------
    - Dates are displayed on the X-axis if the input is a DataFrame with a DatetimeIndex.
    """

    # Si el input es un DataFrame, obtener los nombres de las columnas y los índices
    if isinstance(data, pd.DataFrame):
        column_names = data.columns
        index = data.index
        data = data.values
    else:
        # Si es un array, usar nombres de columnas genéricos y un índice por defecto
        column_names = [f"Column {i+1}" for i in range(data.shape[1])]
        index = range(data.shape[0])  # Índice genérico

    num_columns = 3  # Número de columnas en la cuadrícula
    num_plots = data.shape[1]
    num_rows = math.ceil(num_plots / num_columns)  # Número de filas necesarias

    # Manejo especial para una sola columna
    if num_plots == 1:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=figsize)

        # Eliminar NaNs de la columna actual
        column_data = data[:, 0]
        valid_data = column_data[~np.isnan(column_data)]
        valid_index = index[~np.isnan(column_data)]

        # Si no hay datos válidos, no graficar
        if valid_data.size == 0:
            print("No valid data to plot.")
            return

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data, ddof=1)

        # Graficar serie de tiempo
        ax.plot(
            valid_index, valid_data, color="cyan", linewidth=1.5, label="Time Series"
        )
        ax.axhline(
            y=mean,
            color="white",
            linestyle="-",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        max_value = np.max(valid_data)

        # Líneas de desviación estándar
        for i in range(
            1, math.ceil((max_value - mean) / std) + 1
        ):  # Mostrar 3 bandas de desviaciones estándar
            if not positive_std_only:
                ax.axhline(
                    y=mean - i * std,
                    color="yellow",
                    linestyle=":",
                    linewidth=1.5,
                    label=f"-{i} Std" if i == 1 else None,
                )
            ax.axhline(
                y=mean + i * std,
                color="yellow",
                linestyle=":",
                linewidth=1.5,
                label=f"+{i} Std" if i == 1 else None,
            )

        # Formato del gráfico
        ax.set_title(f"Time Series of {column_names[0]}", color="white")
        ax.set_xlabel("Time", color="white")
        ax.set_ylabel("Value", color="white")
        ax.legend(loc="upper right", facecolor="black", framealpha=0.9)
        ax.grid(True, linestyle="--", alpha=0.4, color="gray")

        # Ajustar formato de fechas si el índice es un DatetimeIndex
        if isinstance(index, pd.DatetimeIndex):
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()  # Rotar etiquetas de fecha

        plt.tight_layout()
        plt.show()
        return

    # Configuración general para múltiples columnas
    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_columns, figsize=figsize)
    axes = axes.flatten()  # Aplanar los ejes para facilitar la iteración

    # Generar los gráficos para cada columna
    for idx in range(num_plots):
        # Eliminar NaNs de la columna actual
        column_data = data[:, idx]
        valid_data = column_data[~np.isnan(column_data)]
        valid_index = index[~np.isnan(column_data)]

        # Si no hay datos válidos después de eliminar NaNs, pasar al siguiente gráfico
        if valid_data.size == 0:
            axes[idx].axis("off")  # Desactivar subplot
            continue

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)

        # Graficar serie de tiempo
        axes[idx].plot(
            valid_index, valid_data, color="cyan", linewidth=1.5, label="Time Series"
        )
        axes[idx].axhline(
            y=mean,
            color="white",
            linestyle="-",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, 4):  # Mostrar 3 bandas de desviaciones estándar
            if not positive_std_only:
                axes[idx].axhline(
                    y=mean - i * std,
                    color="yellow",
                    linestyle=":",
                    linewidth=1.5,
                    label=f"-{i} Std" if i == 1 else None,
                )
            axes[idx].axhline(
                y=mean + i * std,
                color="yellow",
                linestyle=":",
                linewidth=1.5,
                label=f"+{i} Std" if i == 1 else None,
            )

        # Formato del gráfico
        axes[idx].set_title(f"Time Series of {column_names[idx]}", color="white")
        axes[idx].set_xlabel("Time", color="white")
        axes[idx].set_ylabel("Value", color="white")
        axes[idx].legend(loc="upper right", facecolor="black", framealpha=0.9)
        axes[idx].grid(True, linestyle="--", alpha=0.4, color="gray")

        # Ajustar formato de fechas si el índice es un DatetimeIndex
        if isinstance(index, pd.DatetimeIndex):
            axes[idx].xaxis.set_major_formatter(
                plt.matplotlib.dates.DateFormatter("%Y-%m-%d")
            )
            fig.autofmt_xdate()  # Rotar etiquetas de fecha

    # Apagar subplots extra
    for idx in range(num_plots, len(axes)):
        axes[idx].axis("off")  # Ocultar ejes sobrantes

    plt.tight_layout()
    plt.show()


def save_plot_time_series_with_std(
    file_path, data, figsize=(15, 5), positive_std_only=False
):
    """
    Saves the 'plot_time_series_with_std' result.

    Plots time series for each column in a given DataFrame or array, highlighting standard deviation bands.

    If the input has only one column, the plot spans the entire figure. Displays dates on the X-axis if the index is a pandas DatetimeIndex.

    Parameters:
    -----------
    data : pd.DataFrame or np.ndarray
        The input data for which time series will be generated. Each column in the data is plotted as a separate time series.
        If a DataFrame is passed, column names are used in the plot titles. If a NumPy array is provided, generic column
        names ('Column 1', 'Column 2', etc.) are used.
    figsize : tuple, optional
        The size of the figure (width, height). Default is (15, 5).
    positive_std_only : bool, optional
        If True, only positive standard deviation bands are plotted. Default is False.

    Returns:
    --------
    None
        Displays a grid of time series plots.

    Notes:
    ------
    - Dates are displayed on the X-axis if the input is a DataFrame with a DatetimeIndex.
    """

    # Si el input es un DataFrame, obtener los nombres de las columnas y los índices
    if isinstance(data, pd.DataFrame):
        column_names = data.columns
        index = data.index
        data = data.values
    else:
        # Si es un array, usar nombres de columnas genéricos y un índice por defecto
        column_names = [f"Column {i+1}" for i in range(data.shape[1])]
        index = range(data.shape[0])  # Índice genérico

    num_columns = 3  # Número de columnas en la cuadrícula
    num_plots = data.shape[1]
    num_rows = math.ceil(num_plots / num_columns)  # Número de filas necesarias

    # Manejo especial para una sola columna
    if num_plots == 1:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=figsize)

        # Eliminar NaNs de la columna actual
        column_data = data[:, 0]
        valid_data = column_data[~np.isnan(column_data)]
        valid_index = index[~np.isnan(column_data)]

        # Si no hay datos válidos, no graficar
        if valid_data.size == 0:
            print("No valid data to plot.")
            return

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data, ddof=1)

        # Graficar serie de tiempo
        ax.plot(
            valid_index, valid_data, color="cyan", linewidth=1.5, label="Time Series"
        )
        ax.axhline(
            y=mean,
            color="white",
            linestyle="-",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        max_value = np.max(valid_data)

        # Líneas de desviación estándar
        for i in range(
            1, math.ceil((max_value - mean) / std) + 1
        ):  # Mostrar 3 bandas de desviaciones estándar
            if not positive_std_only:
                ax.axhline(
                    y=mean - i * std,
                    color="yellow",
                    linestyle=":",
                    linewidth=1.5,
                    label=f"-{i} Std" if i == 1 else None,
                )
            ax.axhline(
                y=mean + i * std,
                color="yellow",
                linestyle=":",
                linewidth=1.5,
                label=f"+{i} Std" if i == 1 else None,
            )

        # Formato del gráfico
        ax.set_title(f"Time Series of {column_names[0]}", color="white")
        ax.set_xlabel("Time", color="white")
        ax.set_ylabel("Value", color="white")
        ax.legend(loc="upper right", facecolor="black", framealpha=0.9)
        ax.grid(True, linestyle="--", alpha=0.4, color="gray")

        # Ajustar formato de fechas si el índice es un DatetimeIndex
        if isinstance(index, pd.DatetimeIndex):
            ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y-%m-%d"))
            fig.autofmt_xdate()  # Rotar etiquetas de fecha

        plt.tight_layout()
        plt.savefig(file_path, dpi=300, bbox_inches="tight")
        plt.close()
        return

    # Configuración general para múltiples columnas
    plt.style.use("dark_background")
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_columns, figsize=figsize)
    axes = axes.flatten()  # Aplanar los ejes para facilitar la iteración

    # Generar los gráficos para cada columna
    for idx in range(num_plots):
        # Eliminar NaNs de la columna actual
        column_data = data[:, idx]
        valid_data = column_data[~np.isnan(column_data)]
        valid_index = index[~np.isnan(column_data)]

        # Si no hay datos válidos después de eliminar NaNs, pasar al siguiente gráfico
        if valid_data.size == 0:
            axes[idx].axis("off")  # Desactivar subplot
            continue

        # Calcular estadísticas
        mean = np.mean(valid_data)
        std = np.std(valid_data)

        # Graficar serie de tiempo
        axes[idx].plot(
            valid_index, valid_data, color="cyan", linewidth=1.5, label="Time Series"
        )
        axes[idx].axhline(
            y=mean,
            color="white",
            linestyle="-",
            linewidth=2,
            label=f"Mean = {mean:.2f}",
        )

        # Líneas de desviación estándar
        for i in range(1, 4):  # Mostrar 3 bandas de desviaciones estándar
            if not positive_std_only:
                axes[idx].axhline(
                    y=mean - i * std,
                    color="yellow",
                    linestyle=":",
                    linewidth=1.5,
                    label=f"-{i} Std" if i == 1 else None,
                )
            axes[idx].axhline(
                y=mean + i * std,
                color="yellow",
                linestyle=":",
                linewidth=1.5,
                label=f"+{i} Std" if i == 1 else None,
            )

        # Formato del gráfico
        axes[idx].set_title(f"Time Series of {column_names[idx]}", color="white")
        axes[idx].set_xlabel("Time", color="white")
        axes[idx].set_ylabel("Value", color="white")
        axes[idx].legend(loc="upper right", facecolor="black", framealpha=0.9)
        axes[idx].grid(True, linestyle="--", alpha=0.4, color="gray")

        # Ajustar formato de fechas si el índice es un DatetimeIndex
        if isinstance(index, pd.DatetimeIndex):
            axes[idx].xaxis.set_major_formatter(
                plt.matplotlib.dates.DateFormatter("%Y-%m-%d")
            )
            fig.autofmt_xdate()  # Rotar etiquetas de fecha

    # Apagar subplots extra
    for idx in range(num_plots, len(axes)):
        axes[idx].axis("off")  # Ocultar ejes sobrantes

    plt.tight_layout()
    plt.savefig(file_path, dpi=300, bbox_inches="tight")
    plt.close()
