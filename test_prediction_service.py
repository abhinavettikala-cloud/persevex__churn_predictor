#!/usr/bin/env python3
"""
Unit Test Suite for Modular Prediction Service Layer.
Tests ArtifactLoader Singleton behavior, DataPreprocessingService transformations,
and PredictionService execution.
"""

import unittest
import numpy as np
from src.services.artifact_loader import ArtifactLoader
from src.services.preprocessor_service import DataPreprocessingService
from src.services.prediction_service import PredictionService, PredictionResult

class TestPredictionServiceLayer(unittest.TestCase):

    def setUp(self):
        self.sample_churn_customer = {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 1,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 85.50,
            "TotalCharges": 85.50
        }

        self.sample_loyal_customer = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "Yes",
            "tenure": 65,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "Yes",
            "DeviceProtection": "Yes",
            "TechSupport": "Yes",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Two year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 60.00,
            "TotalCharges": 3900.00
        }

    def test_artifact_loader_singleton(self):
        """Verify ArtifactLoader operates as a Singleton and loads artifacts only once."""
        loader1 = ArtifactLoader()
        loader2 = ArtifactLoader()
        self.assertIs(loader1, loader2)
        self.assertTrue(loader1.is_loaded())
        self.assertIsNotNone(loader1.model)
        self.assertIsNotNone(loader1.scaler)
        self.assertIsNotNone(loader1.encoder)

    def test_preprocessing_service(self):
        """Verify DataPreprocessingService produces scaled NumPy matrix of correct shape."""
        loader = ArtifactLoader()
        preprocessor = DataPreprocessingService()
        scaled_features = preprocessor.prepare_features(
            self.sample_churn_customer,
            encoder=loader.encoder,
            scaler=loader.scaler
        )
        self.setIsInstance = self.assertIsInstance(scaled_features, np.ndarray)
        self.assertEqual(scaled_features.shape[0], 1)
        self.assertEqual(scaled_features.shape[1], 55)

    def test_prediction_service_churn_result(self):
        """Verify PredictionService returns structured PredictionResult for churn-prone customer."""
        service = PredictionService()
        result = service.predict(self.sample_churn_customer)

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.prediction, "Churn")
        self.assertEqual(result.churn_label, 1)
        self.assertTrue(0.0 <= result.probability <= 1.0)
        self.assertTrue(0.5 <= result.confidence_score <= 1.0)
        self.assertIn(result.risk_level, ["Medium", "High"])
        print("\nTest Prediction Result (Churn):", result)

    def test_prediction_service_loyal_result(self):
        """Verify PredictionService returns 'No Churn' and Low risk for loyal customer."""
        service = PredictionService()
        result = service.predict(self.sample_loyal_customer)

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.prediction, "No Churn")
        self.assertEqual(result.churn_label, 0)
        self.assertLess(result.probability, 0.40)
        self.assertEqual(result.risk_level, "Low")
        print("\nTest Prediction Result (Loyal):", result)


if __name__ == "__main__":
    unittest.main()
