#!/usr/bin/env python3
"""
Automated Integration Test Suite for Telecom Churn FastAPI Application.
Tests GET /, GET /health, POST /predict (valid request and invalid payload edge cases).
"""

import unittest
from fastapi.testclient import TestClient
from fastapi_app import app

client = TestClient(app)

class TestFastAPIBackend(unittest.TestCase):
    
    def test_root_endpoint(self):
        """Test GET / returns 200 OK and expected welcome payload."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["status"], "online")

    def test_health_endpoint(self):
        """Test GET /health returns status 200 OK and diagnostic flags."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])
        self.assertTrue(data["scaler_loaded"])
        self.assertTrue(data["encoder_loaded"])

    def test_predict_endpoint_valid_payload(self):
        """Test POST /predict with valid customer payload."""
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
        
        # Verify response schema fields
        self.assertIn("prediction", data)
        self.assertIn(data["prediction"], ["Churn", "No Churn"])
        self.assertIn("churn_label", data)
        self.assertIn("probability", data)
        self.assertTrue(0.0 <= data["probability"] <= 1.0)
        self.assertIn("confidence_score", data)
        self.assertIn("risk_level", data)
        self.assertIn(data["risk_level"], ["Low", "Medium", "High"])
        self.assertIn("timestamp", data)
        print("\nPrediction API Response:", data)

    def test_predict_endpoint_invalid_payload(self):
        """Test POST /predict with invalid enum value returns 422 Unprocessable Entity."""
        payload = {
            "gender": "InvalidGender",  # Invalid enum value
            "tenure": -5                 # Invalid negative tenure
        }
        response = client.post("/predict", json=payload)
        self.assertEqual(response.status_code, 422)

if __name__ == "__main__":
    unittest.main()
