import os
import pandas as pd
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_DATASET_URL = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
DEFAULT_LOCAL_PATH = os.path.join("data", "telecom_churn.csv")

def load_data(file_path: str = DEFAULT_LOCAL_PATH, download_if_missing: bool = True) -> pd.DataFrame:
    """
    Loads the Telecom Customer Churn dataset from a local CSV file or downloads it if missing.

    Parameters:
        file_path (str): Path to the local CSV dataset.
        download_if_missing (bool): Whether to download the dataset if not found locally.

    Returns:
        pd.DataFrame: The loaded raw pandas DataFrame.
    """
    if not os.path.exists(file_path):
        if download_if_missing:
            logger.info(f"Local file '{file_path}' not found. Downloading dataset...")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            urllib.request.urlretrieve(DEFAULT_DATASET_URL, file_path)
            logger.info(f"Dataset successfully downloaded to '{file_path}'.")
        else:
            raise FileNotFoundError(f"Dataset file not found at path: {file_path}")

    df = pd.read_csv(file_path)
    logger.info(f"Data loaded successfully. Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df
