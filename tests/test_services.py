import unittest
import numpy as np
from src.services.artifact_loader import ArtifactLoader
from src.services.preprocessor_service import DataPreprocessingService
from src.services.prediction_service import PredictionService, PredictionResult

class TestServiceLayer(unittest.TestCase):
    """
    Validates the decoupled Service Layer (ArtifactLoader, DataPreprocessingService, PredictionService).
    """

    def setUp(self):
        self.sample_input = {
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
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

    def test_artifact_loader_singleton(self):
        """Validates that ArtifactLoader loads model, scaler, and encoder exactly once and returns identical instance."""
        loader1 = ArtifactLoader()
        loader2 = ArtifactLoader()
        self.assertIs(loader1, loader2)
        self.assertTrue(loader1.is_loaded())
        self.assertIsNotNone(loader1.model)
        self.assertIsNotNone(loader1.scaler)
        self.assertIsNotNone(loader1.encoder)

    def test_preprocessing_service_matrix_shape(self):
        """Validates that DataPreprocessingService produces a scaled 2D NumPy matrix with shape (1, 55)."""
        loader = ArtifactLoader()
        preprocessor = DataPreprocessingService()
        scaled = preprocessor.prepare_features(self.sample_input, loader.encoder, loader.scaler)

        self.assertIsInstance(scaled, np.ndarray)
        self.assertEqual(scaled.shape, (1, 55))

    def test_prediction_service_result_contract(self):
        """Validates that PredictionService produces structured PredictionResult with probability & confidence metrics."""
        service = PredictionService()
        result = service.predict(self.sample_input)

        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.prediction, "Churn")
        self.assertEqual(result.churn_label, 1)
        self.assertTrue(0.0 <= result.probability <= 1.0)
        self.assertTrue(0.5 <= result.confidence_score <= 1.0)
        self.assertEqual(result.risk_level, "High")
        self.assertIsNotNone(result.timestamp)

if __name__ == "__main__":
    unittest.main()
