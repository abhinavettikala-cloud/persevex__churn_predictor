#!/usr/bin/env python3
"""
Automated Headless Test Suite for Streamlit App Integration.
Verifies payload formatting, schema compatibility, and REST API communication with FastAPI backend.
"""

import unittest
import requests

API_URL = "http://localhost:8000"

class TestStreamlitIntegration(unittest.TestCase):

    def test_api_health_for_streamlit(self):
        """Verify Streamlit app can reach FastAPI /health endpoint."""
        try:
            response = requests.get(f"{API_URL}/health", timeout=3)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn(data["status"], ["healthy", "ok"])
        except requests.exceptions.ConnectionError:
            self.skipTest("FastAPI server not running locally on http://localhost:8000")

    def test_preset_high_risk_payload(self):
        """Verify high risk churn payload construction and API response."""
        payload = {
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
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["prediction"], "Churn")
            self.assertEqual(data["risk_level"], "High")
            self.assertGreaterEqual(data["probability"], 0.70)
            print("\nStreamlit Test Preset High Risk Result:", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("FastAPI server not running locally on http://localhost:8000")

    def test_preset_loyal_customer_payload(self):
        """Verify loyal customer payload construction and API response."""
        payload = {
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
        try:
            response = requests.post(f"{API_URL}/predict", json=payload, timeout=5)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["prediction"], "No Churn")
            self.assertEqual(data["risk_level"], "Low")
            self.assertLess(data["probability"], 0.40)
            print("\nStreamlit Test Preset Loyal Customer Result:", data)
        except requests.exceptions.ConnectionError:
            self.skipTest("FastAPI server not running locally on http://localhost:8000")

if __name__ == "__main__":
    unittest.main()
