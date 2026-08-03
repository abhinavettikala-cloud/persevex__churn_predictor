import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies feature engineering to enrich the dataset with domain-specific features.

    Engineered Features:
    1. 'tenure_group': Categorical binning of tenure into cohorts ('0-12', '12-24', '24-48', '48-60', '>60').
    2. 'total_services': Total count of subscribed add-on digital services.
    3. 'monthly_to_total_ratio': Ratio of MonthlyCharges relative to TotalCharges.
    4. 'charge_per_tenure': Average charge accumulated per tenure month.
    5. 'is_long_term_contract': Flag indicating if customer has a 1-year or 2-year contract.
    6. 'has_tech_support_or_security': Flag for active Tech Support or Online Security.

    Parameters:
        df (pd.DataFrame): Cleaned DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing engineered features.
    """
    df = df.copy()

    # 1. Bin tenure into customer cohorts
    labels = ["0-12", "12-24", "24-48", "48-60", ">60"]
    bins = [-1, 12, 24, 48, 60, np.inf]
    df["tenure_group"] = pd.cut(df["tenure"], bins=bins, labels=labels).astype(str)

    # 2. Count total subscribed services
    service_cols = [
        "PhoneService", "MultipleLines", "InternetService",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies"
    ]
    
    # Calculate count of active 'Yes' or active Internet services (Fiber/DSL)
    active_count = np.zeros(len(df))
    for col in service_cols:
        if col in df.columns:
            active_count += (df[col].isin(["Yes", "DSL", "Fiber optic"])).astype(int)
    df["total_services"] = active_count

    # 3. MonthlyCharges to TotalCharges ratio
    if "MonthlyCharges" in df.columns and "TotalCharges" in df.columns:
        df["monthly_to_total_ratio"] = df["MonthlyCharges"] / (df["TotalCharges"] + 1.0)

    # 4. Charge per tenure month
    if "TotalCharges" in df.columns and "tenure" in df.columns:
        df["charge_per_tenure"] = df["TotalCharges"] / (df["tenure"] + 1.0)

    # 5. Long-term contract indicator
    if "Contract" in df.columns:
        df["is_long_term_contract"] = df["Contract"].isin(["One year", "Two year"]).astype(int)

    # 6. Tech support or security flag
    if "TechSupport" in df.columns and "OnlineSecurity" in df.columns:
        df["has_tech_support_or_security"] = (
            (df["TechSupport"] == "Yes") | (df["OnlineSecurity"] == "Yes")
        ).astype(int)

    logger.info(f"Feature engineering complete. Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns.")
    return df
