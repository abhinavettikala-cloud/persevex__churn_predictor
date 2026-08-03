import unittest
import pandas as pd
import numpy as np
from src.pipeline.data_cleaner import clean_data
from src.pipeline.feature_engineering import engineer_features

class TestPipelineUnit(unittest.TestCase):
    """
    Unit tests for core data cleaning, missing value handling, and feature engineering logic.
    """

    def setUp(self):
        # Raw mock dataset with missing TotalCharges whitespace, untrimmed strings, and customerID
        self.mock_df = pd.DataFrame([{
            "customerID": "7590-VHVEG ",
            "gender": "Female ",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 0,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "No",
            "DeviceProtection": "Yes",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 50.0,
            "TotalCharges": " ",  # Blank whitespace missing value
            "Churn": "No"
        }])

    def test_clean_data_whitespace_and_null_imputation(self):
        """Validates that clean_data handles string trimming, missing TotalCharges imputation, and drops customerID."""
        cleaned = clean_data(self.mock_df)

        # Assert customerID is removed
        self.assertNotIn("customerID", cleaned.columns)

        # Assert whitespace is stripped
        self.assertEqual(cleaned["gender"].iloc[0], "Female")

        # Assert TotalCharges converted to float64 and missing value imputed to 0.0
        self.assertEqual(cleaned["TotalCharges"].iloc[0], 0.0)
        self.assertTrue(pd.api.types.is_float_dtype(cleaned["TotalCharges"]))

    def test_engineer_features_calculations(self):
        """Validates engineered features: tenure_group, total_services, charge ratios, and contract flags."""
        cleaned = clean_data(self.mock_df)
        featured = engineer_features(cleaned)

        # Assert engineered columns exist
        expected_cols = [
            "tenure_group", "total_services", "monthly_to_total_ratio",
            "charge_per_tenure", "is_long_term_contract", "has_tech_support_or_security"
        ]
        for col in expected_cols:
            self.assertIn(col, featured.columns)

        # Assert tenure_group for tenure=0 is '0-12'
        self.assertEqual(featured["tenure_group"].iloc[0], "0-12")

        # Assert active services count (PhoneService=Yes, InternetService=DSL, OnlineSecurity=Yes, DeviceProtection=Yes -> total=4)
        self.assertEqual(featured["total_services"].iloc[0], 4)

        # Assert has_tech_support_or_security flag is 1 (OnlineSecurity=Yes)
        self.assertEqual(featured["has_tech_support_or_security"].iloc[0], 1)

        # Assert is_long_term_contract flag is 0 (Month-to-month)
        self.assertEqual(featured["is_long_term_contract"].iloc[0], 0)

if __name__ == "__main__":
    unittest.main()
