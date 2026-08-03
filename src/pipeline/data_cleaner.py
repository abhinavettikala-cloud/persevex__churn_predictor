import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Performs data cleaning and missing value handling on the dataset.

    Steps:
    1. Strip leading/trailing whitespace from string columns and column names.
    2. Convert 'TotalCharges' column from object/string to float64.
    3. Handle missing values: Fill 11 missing 'TotalCharges' values (for new customers where tenure=0) with 0.0.
    4. Remove non-predictive identifier column 'customerID'.

    Parameters:
        df (pd.DataFrame): Raw DataFrame.

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for feature engineering and EDA.
    """
    df = df.copy()

    # 1. Clean column names
    df.columns = [col.strip() for col in df.columns]

    # 2. Clean string values in object columns
    string_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()

    # 3. Handle TotalCharges numeric conversion & missing values
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        missing_count = df["TotalCharges"].isnull().sum()
        if missing_count > 0:
            logger.info(f"Handling missing values: Found {missing_count} missing entries in 'TotalCharges'. Imputing with 0.0 (tenure=0).")
            df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    # 4. Remove customerID if present
    if "customerID" in df.columns:
        df = df.drop(columns=["customerID"])
        logger.info("Removed non-predictive column 'customerID'.")

    # 5. Check for any remaining nulls across all columns
    total_nulls = df.isnull().sum().sum()
    if total_nulls > 0:
        logger.warning(f"Remaining null values found: {total_nulls}. Filling with column medians/modes.")
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])

    logger.info(f"Data cleaning complete. Cleaned shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df
