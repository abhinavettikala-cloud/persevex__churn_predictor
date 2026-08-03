import unittest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestFastAPIEndpoints(unittest.TestCase):
    """
    Integration tests for FastAPI REST API endpoints (GET /, GET /health, POST /predict).
    """

    def test_root_endpoint(self):
        """Validates GET / endpoint returns 200 OK and expected API status metadata."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("documentation", data)
        self.assertEqual(data["documentation"], "/docs")

    def test_health_endpoint(self):
        """Validates GET /health endpoint returns 200 OK and confirms all ML artifacts are loaded."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["model_loaded"])
        self.assertTrue(data["scaler_loaded"])
        self.assertTrue(data["encoder_loaded"])

    def test_predict_endpoint_valid_json(self):
        """Validates POST /predict accepts valid JSON and returns structured prediction response."""
        payload = {
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
        response = client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("prediction", data)
        self.assertIn(data["prediction"], ["Churn", "No Churn"])
        self.assertIn("churn_label", data)
        self.assertIn("probability", data)
        self.assertIn("confidence_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("timestamp", data)

    def test_predict_endpoint_validation_error(self):
        """Validates POST /predict returns 422 Unprocessable Entity on invalid input payload."""
        invalid_payload = {
            "gender": "InvalidGenderOption",  # Invalid enum
            "tenure": -10                     # Invalid negative tenure
        }
        response = client.post("/predict", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
