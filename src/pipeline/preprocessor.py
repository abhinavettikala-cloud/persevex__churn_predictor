import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import logging
from typing import Tuple, List, Dict, Any

logger = logging.getLogger(__name__)

def split_and_preprocess(
    df: pd.DataFrame,
    target_col: str = "Churn",
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler, OneHotEncoder, List[str]]:
    """
    Performs train/test split, categorical encoding, and numerical scaling following strict ML best practices.

    Rules Enforced:
    1. Stratified 80/20 train/test split performed BEFORE fitting encoders or scalers to prevent data leakage.
    2. Target column mapped to binary integers (1 for 'Yes', 0 for 'No').
    3. Nominal categorical variables encoded using OneHotEncoder(handle_unknown='ignore', sparse_output=False).
    4. Numerical features standardized using StandardScaler().
    5. Returns transformed training and test feature arrays, fitted scaler, fitted encoder, and encoded feature names.

    Parameters:
        df (pd.DataFrame): Processed DataFrame with features.
        target_col (str): Target column name.
        test_size (float): Proportion of dataset for test split (default 0.2).
        random_state (int): Seed for reproducible random splitting.

    Returns:
        Tuple containing:
        - X_train_scaled (np.ndarray): Preprocessed training features.
        - X_test_scaled (np.ndarray): Preprocessed test features.
        - y_train (pd.Series): Training target labels.
        - y_test (pd.Series): Test target labels.
        - scaler (StandardScaler): Fitted numerical scaler object.
        - encoder (OneHotEncoder): Fitted categorical encoder object.
        - feature_names (List[str]): List of all processed feature column names.
    """
    df = df.copy()

    # 1. Target Encoding
    if target_col not in df.columns:
        raise KeyError(f"Target column '{target_col}' not found in DataFrame.")

    # Encode target: Yes -> 1, No -> 0
    y = df[target_col].map({"Yes": 1, "No": 0, 1: 1, 0: 0})
    X = df.drop(columns=[target_col])

    logger.info(f"Target distribution: {y.value_counts().to_dict()} (1: Churn, 0: No Churn)")

    # 2. Stratified Train/Test Split (Strict Featurization Ordering)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    logger.info(f"Train/Test split complete: Train shape = {X_train.shape}, Test shape = {X_test.shape}")

    # Identify categorical and numerical columns
    cat_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
    num_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()

    logger.info(f"Numerical features ({len(num_cols)}): {num_cols}")
    logger.info(f"Categorical features ({len(cat_cols)}): {cat_cols}")

    # 3. Fit OneHotEncoder ONLY on X_train categorical columns
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_train_cat_encoded = encoder.fit_transform(X_train[cat_cols])
    X_test_cat_encoded = encoder.transform(X_test[cat_cols])

    cat_feature_names = encoder.get_feature_names_out(cat_cols).tolist()

    # 4. Combine Numerical features + Encoded Categorical features
    X_train_combined = np.hstack([X_train[num_cols].values, X_train_cat_encoded])
    X_test_combined = np.hstack([X_test[num_cols].values, X_test_cat_encoded])

    feature_names = num_cols + cat_feature_names

    # 5. Fit StandardScaler ONLY on X_train_combined
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_combined)
    X_test_scaled = scaler.transform(X_test_combined)

    logger.info(f"Preprocessing complete. Total features after One-Hot Encoding: {len(feature_names)}")

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, encoder, feature_names
