import unittest
from src.services.prediction_service import PredictionService, PredictionResult

class TestEdgeCases(unittest.TestCase):
    """
    Edge-case and boundary value test suite.
    """

    def setUp(self):
        self.service = PredictionService()

    def test_tenure_zero_new_customer_boundary(self):
        """
        Validates new customer boundary case (tenure=0, TotalCharges=0.0).
        Ensures ratios do not raise ZeroDivisionError and prediction completes cleanly.
        """
        payload = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 0,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "No",
            "OnlineBackup": "No",
            "DeviceProtection": "No",
            "TechSupport": "No",
            "StreamingTV": "No",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "No",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 20.00,
            "TotalCharges": 0.00
        }
        result = self.service.predict(payload)
        self.assertIsInstance(result, PredictionResult)
        self.assertTrue(0.0 <= result.probability <= 1.0)
        self.assertIn(result.prediction, ["Churn", "No Churn"])

    def test_maximum_value_boundaries(self):
        """
        Validates maximum boundary conditions (tenure=120 months, MonthlyCharges=$300.0, TotalCharges=$10,000.0).
        """
        payload = {
            "gender": "Female",
            "SeniorCitizen": 1,
            "Partner": "Yes",
            "Dependents": "Yes",
            "tenure": 120,
            "PhoneService": "Yes",
            "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "Yes",
            "DeviceProtection": "Yes",
            "TechSupport": "Yes",
            "StreamingTV": "Yes",
            "StreamingMovies": "Yes",
            "Contract": "Two year",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 300.00,
            "TotalCharges": 10000.00
        }
        result = self.service.predict(payload)
        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.prediction, "No Churn")
        self.assertEqual(result.risk_level, "Low")

    def test_all_services_no_internet_boundary(self):
        """
        Validates boundary case where customer has no internet service.
        """
        payload = {
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 24,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "No",
            "OnlineSecurity": "No internet service",
            "OnlineBackup": "No internet service",
            "DeviceProtection": "No internet service",
            "TechSupport": "No internet service",
            "StreamingTV": "No internet service",
            "StreamingMovies": "No internet service",
            "Contract": "One year",
            "PaperlessBilling": "No",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 19.85,
            "TotalCharges": 476.40
        }
        result = self.service.predict(payload)
        self.assertIsInstance(result, PredictionResult)
        self.assertTrue(0.0 <= result.probability <= 1.0)

if __name__ == "__main__":
    unittest.main()
