import boto3
import os
import json
import pandas as pd
import numpy as np
from io import BytesIO, StringIO
import pickle
import h5py
import requests
from datetime import date
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


class DataExtractor:
    """
    A class to extract financial data from the EOD API for single or multiple symbols,
    with support for both historical and intraday data.

    Parameters
    ----------
    eod_token : str
        The API token required for accessing the EOD API.

    Methods
    -------
    eod_extract(symbol, freq, start_date=None, end_date=None, exchange='US', fmt='csv', intraday_spot, historical_spot)
        Extracts data for a single symbol with specified frequency, date range, and format.
    extract_multiple(symbols, freq='d', start_date=None, end_date=None, exchange='US', fmt='csv', intraday_spot, historical_spot, max_workers=5)
        Extracts data for multiple symbols concurrently.
    _decode_(data)
        Decodes the CSV data returned by the API into a pandas DataFrame.
    _today_date_()
        Returns the current date as a string in "YYYY-MM-DD" format.

    Raises
    ------
    ValueError
        - If the `freq` parameter is not valid.
        - If date range exceeds maximum limits for specific intraday frequencies.

    Notes
    -----
    The class supports different frequencies for data extraction:
    - 'm' (monthly), 'w' (weekly), 'd' (daily) for historical data.
    - '1h' (hourly), '5m' (5 minutes), '1m' (1 minute) for intraday data.
    Custom columns can be specified for intraday and historical data extraction.

    Example
    -------
    >>> extractor = DataExtractor(eod_token='YOUR_API_TOKEN')
    >>> df = extractor.eod_extract(symbol='AAPL', freq='d', start_date='2022-01-01', end_date='2022-12-31')
    >>> multiple_df = extractor.extract_multiple(['AAPL', 'GOOG'], freq='d')
    """

    def __init__(self, eod_token, rate_limit=1000):

        self.eod_token = eod_token
        self.errors = []
        self.rate_limit = rate_limit
        self.call_count = 0
        self.start_time = time.time()

    def _make_request(self, url, max_retries=3):
        """
        Makes a request to the given URL with retry logic.

        Parameters
        ----------
        url : str
            The URL to make the request to.
        max_retries : int, optional
            Maximum number of retry attempts (default is 3).

        Returns
        -------
        bytes
            The content of the response.

        Raises
        ------
        Exception
            If all retry attempts fail.
        """
        retries = 0
        while retries < max_retries:
            try:
                self._check_rate_limit()
                response = requests.get(url, timeout=120)
                response.raise_for_status()
                return response.content
            except (
                requests.exceptions.RequestException,
                requests.exceptions.Timeout,
            ) as e:
                print(f"Request failed: {e}. Retrying ({retries + 1}/{max_retries})...")
                retries += 1
                time.sleep(2**retries)  # Exponential backoff

        print(f"Failed after {max_retries} retries. URL: {url}")
        raise Exception(f"Max retries exceeded for URL: {url}")

    def eod_extract(
        self,
        symbol,
        freq,
        start_date=None,
        end_date=None,
        exchange="US",
        fmt="csv",
        intraday_spot=[
            "Timestamp",
            "Gmtoffset",
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ],
        historical_spot=["Open", "High", "Low", "Close", "Adjusted_close", "Volume"],
    ):
        """
        Extracts data for a single symbol at the specified frequency and date range.

        Parameters
        ----------
        symbol : str
            The stock symbol to fetch data for.
        freq : str
            The data frequency ('m', 'w', 'd', '1h', '5m', '1m').
        start_date : str, optional
            The start date for data extraction (default is None).
        end_date : str, optional
            The end date for data extraction (default is None).
        exchange : str, optional
            The stock exchange code (default is 'US').
        fmt : str, optional
            The format of the returned data ('csv' or 'json', default is 'csv').
        intraday_spot : list, optional
            List of columns to extract for intraday data (default includes common intraday columns).
        historical_spot : list, optional
            List of columns to extract for historical data (default is ['Adjusted_close']).

        Returns
        -------
        pd.DataFrame
            DataFrame containing the extracted data, with intraday or historical columns based on the frequency.
        """
        valid_frequencies = ["m", "w", "d", "1h", "5m", "1m"]
        if freq not in valid_frequencies:
            raise ValueError(f"freq parameter must be one of: {valid_frequencies}")
        if freq in ["1h", "5m", "1m"]:
            if not end_date:
                end_date = int(time.time())
            if not start_date:
                if freq == "1h":
                    start_date = end_date - 7200 * 24 * 60 * 60
                elif freq == "5m":
                    start_date = end_date - 600 * 24 * 60 * 60
                elif freq == "1m":
                    start_date = end_date - 120 * 24 * 60 * 60
            if ((end_date - start_date) / (24 * 3600) > 120) & (freq == "1m"):
                raise ValueError(
                    "maximum periods between dates are 120 days for 1-minute frequency"
                )
            elif ((end_date - start_date) / (24 * 3600) > 600) & (freq == "5m"):
                raise ValueError(
                    "maximum periods between dates are 600 days for 5-minute frequency"
                )
            elif ((end_date - start_date) / (24 * 3600) > 7200) & (freq == "1h"):
                raise ValueError(
                    "maximum periods between dates are 7200 days for 1-hour frequency"
                )
            url = f"https://eodhd.com/api/intraday/{symbol}.{exchange}?from={start_date}&to={end_date}&interval={freq}&api_token={self.eod_token}&fmt={fmt}"
            try:
                data = self._make_request(url)
                df = self._decode_(data)
                df = df[intraday_spot]
                df.rename(
                    columns={column: f"{symbol}_{column}" for column in df.columns},
                    inplace=True,
                )
                return df
            except Exception as e:
                print(f"Extraction failed for {symbol}: {e}")
                self.errors.append(symbol)
                return pd.DataFrame()

            # data = requests.get(url, timeout=120).content
            # df = self._decode_(data)
            # df = df[intraday_spot]
            # df.rename(
            #     columns={column: f"{symbol}_{column}" for column in df.columns},
            #     inplace=True,
            # )
            # return df
        else:
            if not end_date:
                end_date = self._today_date_()
            if not start_date:
                start_date = "1900-01-01"
            url = f"https://eodhd.com/api/eod/{symbol}.{exchange}?from={start_date}&to={end_date}&period={freq}&api_token={self.eod_token}&fmt={fmt}"
            try:
                data = self._make_request(url)
                df = self._decode_(data)
                if "Date" not in df.columns:
                    print(f"Error extracting {symbol}")
                    self.errors.append(symbol)
                    return pd.DataFrame()
                df["Date"] = pd.to_datetime(df["Date"])
                df.set_index("Date", inplace=True)
                df = df[historical_spot]
                df.columns = [f"{symbol}_{column}" for column in df.columns]
                return df
            except Exception as e:
                print(f"Extraction failed for {symbol}: {e}")
                self.errors.append(symbol)
                return pd.DataFrame()

            # data = requests.get(url, timeout=120).content
            # df = self._decode_(data)
            # if "Date" not in df.columns:
            #     # raise ValueError(f"Error extracting: {symbol}")
            #     print(f"Error extracting {symbol}")
            #     self.errors.append(symbol)
            #     return pd.DataFrame()
            # df["Date"] = pd.to_datetime(df["Date"])
            # df.set_index("Date", inplace=True)
            # df = df[historical_spot]
            # df.columns = [f"{symbol}_{column}" for column in df.columns]
            # return df

    def extract_multiple(
        self,
        symbols,
        freq="d",
        start_date=None,
        end_date=None,
        exchange="US",
        fmt="csv",
        intraday_spot=[
            "Timestamp",
            "Gmtoffset",
            "Datetime",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ],
        historical_spot=["Open", "High", "Low", "Close", "Adjusted_close", "Volume"],
        max_workers=5,
    ):
        """
        Extracts data for multiple symbols concurrently using a ThreadPoolExecutor.

        Parameters
        ----------
        symbols : list
            List of stock symbols to fetch data for.
        freq : str, optional
            The data frequency (default is 'd' for daily).
        start_date : str, optional
            The start date for data extraction (default is None).
        end_date : str, optional
            The end date for data extraction (default is None).
        exchange : str, optional
            The stock exchange code (default is 'US').
        fmt : str, optional
            The format of the returned data (default is 'csv').
        intraday_spot : list, optional
            Columns to extract for intraday data.
        historical_spot : list, optional
            Columns to extract for historical data.
        max_workers : int, optional
            The maximum number of threads to use (default is 5).

        Returns
        -------
        pd.DataFrame
            Combined DataFrame containing data for all symbols, with columns specific to each symbol.
        """

        def task(symbol):
            return symbol, self.eod_extract(
                symbol,
                freq,
                start_date,
                end_date,
                exchange,
                fmt,
                intraday_spot,
                historical_spot,
            )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(task, symbols))

        combined_df = pd.concat([df for _, df in results], axis=1)
        return combined_df

    def _check_rate_limit(self):
        """
        Checks if the rate limit is exceeded and waits 60 seconds if necessary.
        """
        self.call_count += 1
        elapsed_time = time.time() - self.start_time

        if self.call_count > self.rate_limit:
            if elapsed_time < 60:
                print("Rate limit exceeded. Waiting for 60 seconds...")
                time.sleep(60 - elapsed_time)
            self.call_count = 0
            self.start_time = time.time()

    def _decode_(self, data):
        """
        Decodes the CSV data returned by the API into a pandas DataFrame.
        """
        decoded_data = data.decode("utf-8")
        if not decoded_data.strip():
            print("Datos vacíos recibidos de la API.")
            return pd.DataFrame()
        try:
            df = pd.read_csv(StringIO(decoded_data))
            return df
        except Exception as e:
            print(f"Error procesando datos: {e}")
            return pd.DataFrame()

    def _today_date_(self):
        """
        Returns the current date in 'YYYY-MM-DD' format.

        Returns
        -------
        str
            Current date as a string.
        """
        return date.today().strftime("%Y-%m-%d")


class S3Touch:
    """
    Clase S3Touch para interactuar con Amazon S3. Permite subir archivos o directorios completos a un bucket de S3
    y leer archivos desde S3 en diferentes formatos como JSON, CSV y Numpy (.npy).

    Atributos:
    ----------
    bucket_name : str
        El nombre del bucket de S3 con el cual se desea interactuar.

    s3 : boto3.client
        El cliente de boto3 que permite realizar operaciones con S3.

    Métodos:
    --------
    __init__(bucket_name, access_key, secret_access_key, region_name):
        Inicializa la clase con las credenciales y la configuración para interactuar con S3.

    _upload_file(file_path, s3_folder=None):
        Sube un archivo único desde el sistema local a un bucket de S3.

    _upload_folder(folder_path, s3_folder=None):
        Sube un directorio completo de archivos desde el sistema local a un bucket de S3.

    write(path, s3_folder=None):
        Detecta si el path es un archivo o directorio y llama a los métodos correspondientes para subirlos a S3.

    read(s3_key, local_path=None):
        Lee un archivo de S3 y lo procesa en base a su extensión (JSON, CSV, Numpy).
    """

    def __init__(self, bucket_name, access_key, secret_access_key, region_name):
        """
        Inicializa la clase S3Touch con las credenciales y configuraciones necesarias para interactuar con S3.

        Parámetros:
        -----------
        bucket_name : str
            El nombre del bucket de S3 al que se subirán o leerán archivos.

        access_key : str
            Clave de acceso (AWS Access Key) para autenticar el cliente S3.

        secret_access_key : str
            Clave secreta (AWS Secret Access Key) asociada al acceso S3.

        region_name : str
            Región de AWS en la que se encuentra el bucket de S3.
        """
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )

    def _upload_file(self, file_path, s3_folder=None):
        """
        Sube un archivo único al bucket de S3.

        Parámetros:
        -----------
        file_path : str
            Ruta completa del archivo en el sistema local que se va a subir.

        s3_folder : str, opcional
            Carpeta dentro del bucket de S3 donde se guardará el archivo. Si no se especifica, se sube a la raíz del bucket.

        Excepciones:
        ------------
        Podría generar excepciones relacionadas con permisos o accesos a S3 si el cliente no tiene acceso adecuado.
        """
        s3_key = (
            f"{s3_folder}/{os.path.basename(file_path)}"
            if s3_folder
            else os.path.basename(file_path)
        )
        s3_key = s3_key.lstrip("/")  # Elimina barra inicial si existe
        self.s3.upload_file(file_path, self.bucket_name, s3_key)

    def _upload_folder(self, folder_path, s3_folder=None):
        """
        Sube todos los archivos dentro de un directorio al bucket de S3, manteniendo la estructura de subcarpetas.

        Parámetros:
        -----------
        folder_path : str
            Ruta del directorio en el sistema local que se va a subir.

        s3_folder : str, opcional
            Carpeta dentro del bucket de S3 donde se guardará la estructura de archivos. Si no se especifica, se suben a la raíz del bucket.

        Excepciones:
        ------------
        Podría generar excepciones si no tiene acceso a S3 o si hay problemas con los permisos.
        """
        if not s3_folder:
            s3_folder = f"{os.path.basename(folder_path)}/"
        else:
            s3_folder = f"{s3_folder}/"
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                s3_key = os.path.join(s3_folder, relative_path).replace("\\", "/")
                self.s3.upload_file(file_path, self.bucket_name, s3_key)
                print(f"{file} succesfully wrote")

    def write(self, path, s3_folder=None):
        """
        Sube un archivo o directorio al bucket de S3. Si la ruta proporcionada es un archivo, lo sube. Si es un directorio, sube todo su contenido.

        Parámetros:
        -----------
        path : str
            Ruta del archivo o directorio que se desea subir.

        s3_folder : str, opcional
            Carpeta dentro del bucket de S3 donde se subirá el archivo o directorio. Si no se especifica, se sube a la raíz del bucket.

        Excepciones:
        ------------
        ValueError: Si la ruta proporcionada no es ni un archivo ni un directorio.
        """
        if os.path.isfile(path):
            self._upload_file(path, s3_folder)
        elif os.path.isdir(path):
            self._upload_folder(path, s3_folder)
        else:
            raise ValueError(
                "La ruta proporcionada no es válida. Debe ser un archivo o un directorio."
            )

    def read(self, s3_key, local_path=None):
        """
        Lee un archivo desde el bucket de S3 y lo procesa según su tipo de archivo.

        Parámetros:
        -----------
        s3_key : str
            Clave (ruta) del archivo dentro del bucket de S3.

        local_path : str, opcional
            Ruta local donde se desea descargar el archivo. Si se especifica, el archivo se guardará localmente en lugar de solo procesarlo.

        Retorno:
        --------
        El archivo procesado, que puede ser:
        - Un diccionario (para archivos JSON).
        - Un array de Numpy (para archivos .npy).
        - Un DataFrame de pandas (para archivos .csv).
        - Un objeto Python (para archivos .pkl).
        - Un objeto h5py.File (para archivos .h5).

        Excepciones:
        ------------
        ValueError: Si el formato del archivo no es soportado.
        """
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            file_content = response["Body"].read()

            if s3_key.endswith(".json"):
                file = json.loads(file_content.decode("utf-8"))
            elif s3_key.endswith(".npy"):
                file = np.load(BytesIO(file_content), allow_pickle=True)
            elif s3_key.endswith(".csv"):
                file = pd.read_csv(StringIO(file_content.decode("utf-8")))
            elif s3_key.endswith(".pkl"):
                file = pickle.loads(file_content)
            elif s3_key.endswith(".h5"):
                # Crear un archivo temporal para poder abrirlo con h5py
                with open("temp_model.h5", "wb") as f:
                    f.write(file_content)
                file = h5py.File("temp_model.h5", "r")
            else:
                raise ValueError(f"Formato de archivo no soportado: {s3_key}")

            if local_path:
                with open(local_path, "wb") as f:
                    f.write(file_content)

            return file

        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
            raise e

    def download_folder(self, s3_folder, local_path):
        """
        Download an entire folder from an S3 bucket to a local directory.

        This method downloads all the files located in a specified folder in S3 to a local directory.
        It checks if the folder path on S3 ends with a '/' and adjusts it if necessary. It then lists all
        objects in the specified S3 folder. If the folder contains any files (not just subdirectories),
        each file is downloaded to the corresponding local path.

        Parameters:
        - s3_folder (str): The folder path in the S3 bucket. Must not be an empty string.
        - local_path (str): The local directory path where the files will be downloaded.

        Notes:
        - This function assumes that 'self.s3' is an initialized boto3 S3 client and 'self.bucket_name'
          is the name of the S3 bucket.
        - The function creates any necessary local directories if they do not exist.
        - Files are saved in the local directory maintaining their relative path as in S3.

        """
        if not s3_folder.endswith("/"):
            s3_folder += "/"
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=s3_folder)
        if "Contents" in response:
            for file in response["Contents"]:
                file_name = file["Key"]
                if not file_name.endswith("/"):
                    local_file_path = os.path.join(
                        local_path, os.path.relpath(file_name, s3_folder)
                    )
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    self.s3.download_file(self.bucket_name, file_name, local_file_path)
                    print(f"Downloaded {file_name} to {local_file_path}")

    def list_folders_in_bucket(self):
        """
        Lists the folder names within an Amazon S3 bucket.

        This function utilizes the AWS S3 `list_objects_v2` API call to retrieve all the
        objects in the specified S3 bucket and groups them by their common prefixes
        (folder names). It uses the '/' delimiter to identify folders and returns a list
        of folder names without the trailing '/'.

        Returns:
        --------
        list:
            A list of folder names (strings) inside the S3 bucket. If no folders
            are found, an empty list is returned.

        Example:
        --------
        If the bucket contains the following keys:
            - 'folder1/file1.txt'
            - 'folder2/file2.txt'
            - 'folder3/'

        The function will return:
            ['folder1', 'folder2', 'folder3']

        Notes:
        ------
        - Folders in S3 are simulated by keys that end with a '/' (e.g., 'folder/').
        - The folder names returned will not include the trailing '/'.

        Raises:
        -------
        No explicit exceptions are raised in this function, but if the S3 bucket
        does not exist or permissions are insufficient, boto3 will raise an appropriate
        exception such as `NoSuchBucket`, `AccessDenied`, etc.

        """
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Delimiter="/")
        if "CommonPrefixes" in response:
            folders = [prefix["Prefix"][:-1] for prefix in response["CommonPrefixes"]]
            return folders
        else:
            return []


def invoke_lambda_to_stop_instance(
    access_key, secret_access_key, region_name, instance_id
):
    """
    Invoca una función Lambda de AWS para detener una instancia EC2 específica.

    Esta función utiliza las credenciales de AWS y los parámetros proporcionados para invocar
    una función Lambda que está configurada para detener una instancia EC2. La invocación
    se realiza de manera asíncrona (InvocationType='Event').

    Parámetros:
    -----------
    access_key : str
        Clave de acceso de AWS (AWS access key) necesaria para autenticarse en los servicios de AWS.

    secret_access_key : str
        Clave secreta de AWS (AWS secret access key) asociada al acceso.

    region_name : str
        Nombre de la región de AWS en la que se encuentra la función Lambda y la instancia EC2.

    instance_id : str
        ID de la instancia EC2 que se desea detener mediante la función Lambda.

    Retorna:
    --------
    response : dict
        Respuesta del cliente de Lambda de AWS, que contiene información sobre el resultado de la invocación.
    """
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region_name,
    )

    payload = {"instance_id": instance_id}

    response = lambda_client.invoke(
        FunctionName="stop_instance_after_executed",  # Nombre de la función Lambda que detiene la instancia.
        InvocationType="Event",  # 'Event' significa que la invocación es asíncrona.
        Payload=json.dumps(payload),  # Cargar el ID de la instancia como un JSON.
    )
    print("lambda invoked")
    return response


def extract_holdings(api_token, etf, currency="US"):
    """
    Extracts the holdings of a specified ETF (Exchange Traded Fund) in a given currency.

    Parameters:
    ----------
    etf : str
        The ticker symbol of the ETF whose holdings are to be extracted.
    currency : str, optional
        The currency filter for the holdings (default is "US").

    Returns:
    -------
    list
        A list of holdings (ticker symbols) for the ETF that match the specified currency.
        Returns an empty list if no holdings are found or if the ETF data is unavailable.

    Description:
    ------------
    This function uses the EOD Historical Data API to fetch the fundamentals of the specified ETF.
    It parses the JSON response to extract the holdings of the ETF, filtering them based on the specified
    currency (e.g., "US"). If the ETF data does not include the "ETF_Data" key, the function returns an
    empty list.

    Notes:
    ------
    - Requires a valid API token (`api_token`) for the EOD Historical Data API.
    - Ensure that the `requests` library is installed and accessible.
    - The timeout for the API request is set to 30 seconds.
    - If the `ETF_Data` or `Holdings` keys are missing in the response, the function assumes no holdings
      are available and returns an empty list.

    Example:
    --------
    >>> etf = "SPY"
    >>> extract_holdings(etf)
    ['AAPL', 'MSFT', 'GOOGL', 'AMZN', ...]

    >>> extract_holdings(etf, currency="CA")
    ['TD', 'RY', 'BNS', ...]
    """
    url = f"https://eodhd.com/api/fundamentals/{etf}?api_token={api_token}&fmt=json"
    data = requests.get(url, timeout=30).json()
    if "ETF_Data" not in data:
        return []
    all_holdings = [
        holding.split(".")[0]
        for holding in list(data["ETF_Data"]["Holdings"].keys())
        if holding.endswith(currency)
    ]
    return all_holdings


def fetch_exchange(api_token, symbol):
    """
    Fetches the exchange associated with a given stock symbol.

    Parameters:
    ----------
    symbol : str
        The ticker symbol of the stock whose exchange information is to be retrieved.

    Returns:
    -------
    tuple
        A tuple containing:
        - The stock symbol (str)
        - The name of the exchange (str) where the stock is listed, or `None` if not found.

    Description:
    ------------
    This function uses the EOD Historical Data API to fetch fundamental data for the given stock symbol.
    It retrieves the exchange name from the "General" section of the JSON response. If any errors occur
    (e.g., network issues or invalid API responses), the function logs the error and returns the stock
    symbol with `None` for the exchange.

    Notes:
    ------
    - Requires a valid API token (`api_token`) for the EOD Historical Data API.
    - Ensure that the `requests` library is installed and accessible.
    - The `symbol` parameter is assumed to be a U.S.-listed stock (".US" is appended to the symbol in the API call).
    - Handles exceptions gracefully and prints an error message to the console in case of failures.

    Example:
    --------
    >>> fetch_exchange("AAPL")
    ('AAPL', 'NASDAQ')

    >>> fetch_exchange("XYZ")
    Error fetching data for XYZ: ...
    ('XYZ', None)
    """
    try:
        url = f"https://eodhd.com/api/fundamentals/{symbol}.US?api_token={api_token}&fmt=json"
        data = requests.get(url).json()
        return symbol, data.get("General", {}).get("Exchange")
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return symbol, None


def filter_symbols_by_exchange(
    symbols, filter_exchange=["NASDAQ", "NYSE ARCA", "NYSE"], num_threads=10
):
    """
    Filters a list of stock symbols based on their associated exchange.

    Parameters:
    ----------
    symbols : list
        A list of stock symbols (str) to be filtered based on their exchange.
    filter_exchange : list, optional
        A list of exchange names (str) to filter the symbols by. Only symbols listed on these exchanges
        will be included in the output (default is ["NASDAQ", "NYSE ARCA", "NYSE"]).
    num_threads : int, optional
        The number of threads to use for concurrent API requests (default is 10).

    Returns:
    -------
    list
        A list of symbols (str) that are listed on the specified exchanges.

    Description:
    ------------
    This function uses the `fetch_exchange` function to retrieve the exchange information for each symbol
    in the input list. It performs the API calls concurrently using a thread pool to improve performance.
    The function filters symbols based on whether their exchange is in the `filter_exchange` list.

    The results are aggregated, and any errors encountered during the execution are logged to the console.

    Notes:
    ------
    - Relies on the `fetch_exchange` function to retrieve exchange data for each symbol.
    - Uses Python's `concurrent.futures.ThreadPoolExecutor` for concurrent execution.
    - Exception handling ensures that errors with individual symbols do not interrupt the entire process.

    Example:
    --------
    >>> symbols = ["AAPL", "TSLA", "MSFT", "XYZ"]
    >>> filter_symbols_by_exchange(symbols)
    ['AAPL', 'TSLA', 'MSFT']

    >>> filter_symbols_by_exchange(symbols, filter_exchange=["NYSE"])
    ['XYZ']
    """
    filtered_symbols = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {
            executor.submit(fetch_exchange, symbol): symbol for symbol in symbols
        }
        for future in as_completed(futures):
            try:
                symbol, exchange = future.result()
                if exchange in filter_exchange:
                    filtered_symbols.append(symbol)
            except Exception as e:
                print(f"Error processing symbol {futures[future]}: {e}")

    return filtered_symbols
