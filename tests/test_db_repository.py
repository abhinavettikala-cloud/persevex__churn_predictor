"""
Unit tests for Database Repository and Persistence operations.
"""

import unittest
import os
import tempfile
from src.db.database import init_db, DB_PATH
from src.db.repository import (
    save_prediction_record,
    get_prediction_history,
    delete_prediction_record,
    get_dashboard_summary,
    get_analytics_summary
)


class TestDatabaseRepository(unittest.TestCase):
    """Test suite for SQLite repository operations."""

    def setUp(self):
        init_db()

    def test_save_and_query_prediction(self):
        record = {
            "id": "PRED-TEST1234",
            "timestamp": "2026-08-03T10:00:00Z",
            "prediction": "Churn",
            "churn_label": 1,
            "probability": 0.7850,
            "confidence_score": 0.7850,
            "risk_level": "High",
            "execution_time_ms": 11.2,
            "model_version": "v1.0.0",
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "No",
            "Dependents": "No",
            "tenure": 2,
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
            "TotalCharges": 171.00,
            "top_positive_factors": [{"factor_name": "Month-to-Month Contract", "impact_level": "High", "description": "Short term"}],
            "top_negative_factors": [],
            "explanation_text": "High churn risk test"
        }

        save_prediction_record(record)

        items, total = get_prediction_history(search_query="PRED-TEST1234")
        self.assertGreaterEqual(total, 1)
        self.assertEqual(items[0]["id"], "PRED-TEST1234")
        self.assertEqual(items[0]["prediction"], "Churn")

    def test_delete_prediction(self):
        record_id = "PRED-DEL1234"
        record = {
            "id": record_id,
            "timestamp": "2026-08-03T10:05:00Z",
            "prediction": "No Churn",
            "churn_label": 0,
            "probability": 0.1200,
            "confidence_score": 0.8800,
            "risk_level": "Low",
            "execution_time_ms": 9.5,
            "model_version": "v1.0.0",
            "Contract": "Two year"
        }
        save_prediction_record(record)
        deleted = delete_prediction_record(record_id)
        self.assertTrue(deleted)

    def test_dashboard_and_analytics_summaries(self):
        dash = get_dashboard_summary()
        self.assertIn("total_predictions", dash)
        self.assertIn("avg_confidence", dash)

        analytics = get_analytics_summary()
        self.assertIn("contract_distribution", analytics)
        self.assertIn("internet_distribution", analytics)


if __name__ == "__main__":
    unittest.main()
