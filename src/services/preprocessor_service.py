import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple
from src.pipeline.data_cleaner import clean_data
from src.pipeline.feature_engineering import engineer_features

logger = logging.getLogger(__name__)

# Single authoritative source of truth for feature column orders (immutable tuples)
NUMERICAL_FEATURE_COLUMNS: Tuple[str, ...] = (
    'SeniorCitizen', 'tenure', 'MonthlyCharges', 'TotalCharges',
    'total_services', 'monthly_to_total_ratio', 'charge_per_tenure',
    'is_long_term_contract', 'has_tech_support_or_security'
)

CATEGORICAL_FEATURE_COLUMNS: Tuple[str, ...] = (
    'gender', 'Partner', 'Dependents', 'PhoneService', 'MultipleLines',
    'InternetService', 'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
    'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
    'PaperlessBilling', 'PaymentMethod', 'tenure_group'
)


class DataPreprocessingService:
    """
    Service responsible for transforming raw customer data into scaled feature arrays ready for model inference.
    """

    def prepare_features(self, raw_input: Dict[str, Any], encoder: Any, scaler: Any) -> np.ndarray:
        """
        Transforms a raw customer feature dictionary into a scaled 2D NumPy array.

        Parameters:
            raw_input (Dict[str, Any]): Input raw customer feature attributes.
            encoder (Any): Fitted OneHotEncoder instance.
            scaler (Any): Fitted StandardScaler instance.

        Returns:
            np.ndarray: Scaled feature matrix of shape (1, num_features).
        """
        try:
            # 1. Convert to DataFrame (1 row)
            df = pd.DataFrame([raw_input])

            # 2. Clean and apply feature engineering
            cleaned_df = clean_data(df)
            featured_df = engineer_features(cleaned_df)

            # 3. Perform One-Hot Encoding on categorical columns
            cat_cols = list(CATEGORICAL_FEATURE_COLUMNS)
            num_cols = list(NUMERICAL_FEATURE_COLUMNS)

            cat_encoded = encoder.transform(featured_df[cat_cols])

            # 4. Horizontally stack numerical and encoded categorical features
            combined_matrix = np.hstack([
                featured_df[num_cols].values,
                cat_encoded
            ])

            # 5. Apply StandardScaler
            scaled_matrix = scaler.transform(combined_matrix)

            return scaled_matrix

        except Exception as e:
            logger.error(f"Failed to preprocess input features: {str(e)}")
            raise ValueError(f"Feature preprocessing error: {str(e)}")
