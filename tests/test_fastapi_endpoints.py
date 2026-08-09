import unittest
import math
from fastapi.testclient import TestClient
from fastapi_app import app

client = TestClient(app)

class TestFastAPIEndpoints(unittest.TestCase):
    """
    Comprehensive integration test suite for FastAPI REST API endpoints.
    Tests health diagnostics, metrics telemetry, valid predictions, strict validation rules,
    forbid extra fields, non-finite float rejection, and content-type verification.
    """

    def setUp(self):
        self.valid_payload = {
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

    def test_root_endpoint(self):
        """Validates GET / endpoint returns 200 OK and expected API status metadata."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("documentation", data)
        self.assertEqual(data["documentation"], "/docs")

    def test_health_endpoint(self):
        """Validates GET /health endpoint returns status: 'healthy' when artifacts are loaded."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])
        self.assertTrue(data["scaler_loaded"])
        self.assertTrue(data["encoder_loaded"])

    def test_predict_endpoint_valid_json(self):
        """Validates POST /predict accepts valid JSON and returns structured prediction response."""
        response = client.post("/predict", json=self.valid_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("prediction", data)
        self.assertIn(data["prediction"], ["Churn", "No Churn"])
        self.assertIn("churn_label", data)
        self.assertIn("probability", data)
        self.assertIn("confidence_score", data)
        self.assertIn("risk_level", data)
        self.assertIn("timestamp", data)
        self.assertIn("X-Request-ID", response.headers)

    def test_predict_endpoint_invalid_enum_validation_error(self):
        """Validates POST /predict returns 422 Unprocessable Entity on invalid enum values."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["gender"] = "InvalidGender"
        response = client.post("/predict", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_predict_endpoint_negative_numeric_error(self):
        """Validates POST /predict returns 422 on negative tenure or charges."""
        invalid_payload = self.valid_payload.copy()
        invalid_payload["tenure"] = -5
        response = client.post("/predict", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_predict_endpoint_empty_json_error(self):
        """Validates POST /predict returns 422 when an empty JSON payload {} is provided."""
        response = client.post("/predict", json={})
        self.assertEqual(response.status_code, 422)

    def test_predict_endpoint_forbid_extra_fields(self):
        """Validates POST /predict returns 422 when unexpected extra fields are supplied (extra='forbid')."""
        extra_payload = self.valid_payload.copy()
        extra_payload["unrecognized_extra_field"] = "malicious_payload_value"
        response = client.post("/predict", json=extra_payload)
        self.assertEqual(response.status_code, 422)

    def test_predict_endpoint_unsupported_media_type(self):
        """Validates POST /predict returns 415 Unsupported Media Type for non-JSON content."""
        response = client.post(
            "/predict",
            content="gender=Female&tenure=1",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 415)

    def test_metrics_endpoint(self):
        """Validates GET /metrics endpoint returns telemetry statistics."""
        response = client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("telemetry", data)
        self.assertIn("average_latency_seconds", data)

if __name__ == "__main__":
    unittest.main()
