import os
import chardet
import pandas as pd
import numpy as np
from datetime import datetime
import json
from .memory_management import gpu_memory
import psutil
import time


def custom_serializer(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def save_dataframes_to_excel(dataframes, sheet_names, file_name):
    """
    Save multiple DataFrames to an Excel file, with each DataFrame written to a separate sheet.

    Parameters:
    ----------
    dataframes : list of pandas.DataFrame
        A list of DataFrames to be saved into the Excel file. Each DataFrame will be written to a separate sheet.
    sheet_names : list of str
        A list of sheet names corresponding to each DataFrame. The length of this list must match the length of `dataframes`.
    file_name : str
        The name of the Excel file to be created (e.g., "output.xlsx").

    Raises:
    -------
    ValueError
        If the number of DataFrames does not match the number of sheet names.

    Notes:
    ------
    - This function uses the `xlsxwriter` engine to create the Excel file.
    - Indexes of the DataFrames are excluded in the output by setting `index=False` in the `to_excel` method.

    Example:
    --------
    >>> import pandas as pd
    >>> df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> df2 = pd.DataFrame({'X': [7, 8, 9], 'Y': [10, 11, 12]})
    >>> save_dataframes_to_excel([df1, df2], ['Sheet1', 'Sheet2'], 'output.xlsx')

    This will create an Excel file named "output.xlsx" with two sheets: "Sheet1" containing `df1` and "Sheet2" containing `df2`.
    """
    if len(dataframes) != len(sheet_names):
        raise ValueError("Each DataFrame must have its own sheet name")
    with pd.ExcelWriter(file_name, engine="xlsxwriter") as writer:
        for df, sheet_name in zip(dataframes, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def general_nested_dict_to_dataframe(nested_dict, parent_keys=None):
    """
    Converts a nested dictionary into a flat pandas DataFrame.

    Each row of the DataFrame represents a unique path from the root to a leaf value in the dictionary.
    The path is split across hierarchical columns, and the values are stored in a separate column.

    Parameters:
    - nested_dict (dict): A dictionary with potentially multiple levels of nesting.
                          The keys at each level represent hierarchical labels,
                          and the leaf nodes contain the values to be extracted.
    - parent_keys (list, optional): A list of keys representing the current path in the recursion.
                                     This is primarily used internally during recursion. Defaults to an empty list.

    Returns:
    - pd.DataFrame: A DataFrame where:
                     - Each row corresponds to a unique path from the root of the dictionary to a leaf value.
                     - The columns `Level_0, Level_1, ..., Level_n` represent the hierarchical keys.
                     - The final column, `Value`, contains the associated values.

    Example:
    nested_dict = {
        "Category A": {
            "Subcategory A1": {
                "Item 1": 10,
                "Item 2": 20,
            },
            "Subcategory A2": {
                "Item 3": 30
            }
        },
        "Category B": {
            "Subcategory B1": {
                "Item 4": 40
            }
        }
    }

    df = general_nested_dict_to_dataframe(nested_dict)
    print(df)
    """

    if parent_keys is None:
        parent_keys = []

    rows = []

    def flatten(current_dict, keys):
        """
        Recursively flattens the nested dictionary and appends the path and value to the `rows` list.

        Parameters:
        - current_dict (dict): The current level of the nested dictionary to flatten.
        - keys (list): The list of keys representing the current path in the recursion.
        """
        for key, value in current_dict.items():
            if isinstance(value, dict):
                flatten(value, keys + [key])
            else:
                rows.append(keys + [key, value])

    flatten(nested_dict, parent_keys)

    column_names = [f"Level_{i}" for i in range(len(rows[0]) - 1)] + ["Value"]

    return pd.DataFrame(rows, columns=column_names)


def convert_keys_to_json_compatible(obj):
    """
    Recursively converts the keys of a dictionary to ensure JSON compatibility.

    This function processes dictionaries and lists, converting keys of type
    `int` or `numpy.integer` to strings, as JSON keys must be strings. Nested
    dictionaries and lists are processed recursively.

    Parameters
    ----------
    obj : dict, list, or any
        The input object to be processed. It can be a dictionary, a list, or
        any other type. If the object is not a dictionary or a list, it is
        returned unchanged.

    Returns
    -------
    dict, list, or any
        The processed object with all dictionary keys converted to strings if
        they were integers (`int` or `numpy.integer`). Lists and nested
        structures are processed recursively.

    Examples
    --------
    >>> import numpy as np
    >>> data = {1: 'a', np.int32(2): {'nested': [3, 4]}, 'key': 'value'}
    >>> convert_keys_to_json_compatible(data)
    {'1': 'a', '2': {'nested': [3, 4]}, 'key': 'value'}

    >>> lst = [{'key': {42: 'answer'}}]
    >>> convert_keys_to_json_compatible(lst)
    [{'key': {'42': 'answer'}}]
    """
    if isinstance(obj, dict):
        return {
            (
                str(k) if isinstance(k, (np.integer, int)) else k
            ): convert_keys_to_json_compatible(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_json_compatible(i) for i in obj]
    else:
        return obj


def create_event(event_path, prefix):
    """
    Crea un evento con un nombre basado en un prefijo y un timestamp actual,
    y genera una carpeta asociada al evento.

    Args:
        event_path (str): La ruta base donde se creará la carpeta del evento.
        prefix (str): El prefijo que se utilizará para nombrar el evento.

    Returns:
        tuple: Una tupla que contiene:
            - event (str): El nombre del evento generado, que consiste en el prefijo
              seguido de un timestamp con el formato 'YYYYMMDD_HHMMSS'.
            - event_folder_path (str): La ruta completa de la carpeta creada para el evento.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event = f"{prefix}_{timestamp}"
    event_folder_path = crear_carpeta(event_path, event)
    return event, event_folder_path


def crear_carpeta(ruta_base, nombre_carpeta):
    """
    Crea una carpeta dada la ruta base y el nombre deseado

    Args:
        ruta_base(str): Ruta de la carpeta raíz
        nombre_carpeta(str): Nombre deseado para la carpeta
    Returns:
        str: Ruta completa de la carpeta creada
    """
    try:
        ruta_completa = os.path.join(ruta_base, nombre_carpeta)
        os.makedirs(ruta_completa, exist_ok=True)
        print(f"Carpeta creada en: {ruta_completa}")
        return ruta_completa
    except Exception as e:
        print(f"Ocurrió un error al crear la carpeta: {e}")


def save_array(path, file_name, array):
    """
    Guarda un array en formato .npy en la ruta especificada.

    Parámetros:
    path (str): La ruta completa, incluyendo el nombre del archivo donde se guardará el array.
    file_name (str): Nombre con el que se desea guardar el archivo
    array (numpy.ndarray): El array que se desea guardar.

    Ejemplo:
    save_array('ruta/al/archivo.npy', mi_array)
    """
    try:
        file_path = os.path.join(path, f"{file_name}.npy")
        np.save(file_path, array)
        print(f"Array guardado exitosamente en: {file_path}")
    except Exception as e:
        print(f"Error al guardar el array: {e}")


def read_codificated_csv(path):
    """
    Detecta la codificación del archivo .csv y lo lee utilizando esa codificación
    Args:
        path(str): Ruta al archivo .csv
    Returns:
        df(pd.DataFrame): Dataframe leído
    """
    with open(rf"{path}", "rb") as f:
        result = chardet.detect(f.read())
    return pd.read_csv(rf"{path}", encoding=result["encoding"])


def centinel(
    centinel_path,
    stats_path,
    sleep_interval=5,
    monitor_gpu_stats=False,
    gpu_indices=[0],
):
    """
    A function that monitors system resource usage (RAM, CPU, and optionally GPU)
    and records the data to a CSV file until a specified file path (`centinel_path`)
    is detected.

    Parameters:
    -----------
    centinel_path : str
        The path to a file that serves as the stop signal. When this file is detected,
        the function stops monitoring and exits the loop.

    stats_path : str
        The path where the collected statistics will be saved as a CSV file.
        If the provided path does not end with ".csv", ".csv" will be appended automatically.

    sleep_interval : int, optional (default=5)
        The time interval (in seconds) between successive resource usage readings.

    monitor_gpu_stats : bool, optional (default=False)
        Indicates whether to monitor GPU usage. If `True`, the function collects GPU
        statistics alongside RAM and CPU usage.

    gpu_indices : list or int, optional (default=[0])
        The indices of the GPUs to monitor. If a single integer is provided, it is converted
        into a list. If `monitor_gpu_stats` is `True`, this parameter must be a list of GPU indices.

    Returns:
    --------
    None
        This function does not return any values. It continuously collects resource usage
        statistics and writes them to the specified CSV file.

    Raises:
    -------
    ValueError
        If `monitor_gpu_stats` is `True` and `gpu_indices` is not a list or integer.

    Behavior:
    ---------
    - The function continuously monitors system resources, collecting CPU and RAM usage.
    - If `monitor_gpu_stats` is `True`, it also collects GPU usage for the specified indices.
    - Resource statistics are written to the CSV file specified by `stats_path` at each interval.
    - The function stops monitoring when the file specified by `centinel_path` is detected.
    """
    if monitor_gpu_stats and isinstance(gpu_indices, int):
        gpu_indices = [gpu_indices]
    elif monitor_gpu_stats and not isinstance(gpu_indices, list):
        raise ValueError("gpu indices must be a list")
    if not stats_path.endswith(".csv"):
        stats_path = stats_path + ".csv"
    collected_data = []
    counter = 0
    while True:
        if os.path.exists(centinel_path):
            break
        if monitor_gpu_stats:
            gpu_stats = gpu_memory(gpu_indices=gpu_indices, display=False)
            for gpu_index in gpu_stats:
                current_gpu_stats = gpu_stats[gpu_index]
                ram_stats = psutil.virtual_memory()
                cpu_stats = psutil.cpu_percent(interval=sleep_interval)
                ram_used_percent = ram_stats.percent
                collected_data.append(
                    {
                        "Tick": counter,
                        "GPU": gpu_index,
                        "VRAM Used": f"{current_gpu_stats['used']/current_gpu_stats['total']:.4%}",
                        "RAM_Used": f"{ram_used_percent:.4f}%",
                        "CPU_Used": f"{cpu_stats:.4f}%",
                    }
                )
        else:
            ram_stats = psutil.virtual_memory()
            cpu_stats = psutil.cpu_percent(interval=sleep_interval)
            ram_used_percent = ram_stats.percent
            collected_data.append(
                {
                    "Tick": counter,
                    "RAM_Used": f"{ram_used_percent:.4f}%",
                    "CPU_Used": f"{cpu_stats:.4f}%",
                }
            )
        time.sleep(sleep_interval)
        counter += 1
        pd.DataFrame(collected_data).to_csv(rf"{stats_path}")
