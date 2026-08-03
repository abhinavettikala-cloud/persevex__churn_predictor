import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def perform_eda(df: pd.DataFrame, target_col: str = "Churn") -> Dict[str, Any]:
    """
    Performs Exploratory Data Analysis (EDA) on the processed dataset.

    Parameters:
        df (pd.DataFrame): Dataset DataFrame.
        target_col (str): Target column name for classification.

    Returns:
        Dict[str, Any]: Comprehensive EDA results dictionary containing statistics, churn distribution, and correlations.
    """
    logger.info("--- Exploratory Data Analysis (EDA) Summary ---")
    
    eda_results = {}

    # 1. Basic Dimensions & Missing Values
    eda_results["num_rows"] = len(df)
    eda_results["num_columns"] = len(df.columns)
    eda_results["missing_values"] = df.isnull().sum().to_dict()

    logger.info(f"Dataset Overview: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # 2. Target Variable Class Distribution
    if target_col in df.columns:
        churn_counts = df[target_col].value_counts()
        churn_pct = df[target_col].value_counts(normalize=True) * 100
        churn_summary = pd.DataFrame({"Count": churn_counts, "Percentage (%)": churn_pct.round(2)})
        eda_results["churn_distribution"] = churn_summary.to_dict()
        
        logger.info(f"Target Variable '{target_col}' Class Distribution:\n{churn_summary}")

    # 3. Numerical Features Summary
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    num_summary = df[num_cols].describe().T
    eda_results["numerical_summary"] = num_summary.to_dict()
    
    logger.info(f"Numerical Features Summary Statistics:\n{num_summary[['mean', 'std', 'min', '50%', 'max']]}")

    # 4. Categorical Features Summary
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    cat_summary = {}
    for col in cat_cols:
        cat_summary[col] = {
            "unique_values": df[col].nunique(),
            "top_category": df[col].mode()[0] if not df[col].empty else None,
            "top_freq": int(df[col].value_counts().iloc[0]) if not df[col].empty else 0
        }
    eda_results["categorical_summary"] = cat_summary
    logger.info(f"Categorical Features Summary: {len(cat_cols)} categorical columns found.")

    # 5. Correlation with Numerical Features (if target is binary string or numeric)
    if target_col in df.columns:
        binary_target = df[target_col].map({"Yes": 1, "No": 0, 1: 1, 0: 0})
        corr_series = df[num_cols].apply(lambda col: col.corr(binary_target))
        corr_df = corr_series.sort_values(ascending=False)
        eda_results["correlations_with_target"] = corr_df.to_dict()
        logger.info(f"Feature Correlations with Target '{target_col}':\n{corr_df}")

    return eda_results
