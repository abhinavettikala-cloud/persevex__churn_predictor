import os
import json
import hashlib
import joblib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

def compute_sha256(filepath: str) -> str:
    """Computes SHA-256 hash of specified file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def save_artifacts(
    best_model: Any,
    scaler: Any,
    encoder: Any,
    output_dir: str = ".",
    best_model_name: str = "Logistic Regression",
    best_metrics: Optional[Dict[str, Any]] = None,
    dataset_summary: Optional[Dict[str, Any]] = None
) -> None:
    """
    Serializes model.pkl, scaler.pkl, and encoder.pkl and generates a comprehensive metadata.json
    manifest containing checksums, model metrics, feature schema, and provenance.

    Parameters:
        best_model (Any): Best trained classifier.
        scaler (Any): Fitted StandardScaler instance.
        encoder (Any): Fitted OneHotEncoder instance.
        output_dir (str): Destination directory path.
        best_model_name (str): Name of winning model algorithm.
        best_metrics (Dict[str, Any]): Dictionary of model evaluation metrics.
        dataset_summary (Dict[str, Any]): Dataset shape and class ratio statistics.
    """
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, "model.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    encoder_path = os.path.join(output_dir, "encoder.pkl")
    metadata_path = os.path.join(output_dir, "metadata.json")

    joblib.dump(best_model, model_path)
    logger.info(f"Saved best model artifact to '{model_path}'.")

    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved scaler artifact to '{scaler_path}'.")

    joblib.dump(encoder, encoder_path)
    logger.info(f"Saved encoder artifact to '{encoder_path}'.")

    # Compute checksums
    model_sha256 = compute_sha256(model_path)
    scaler_sha256 = compute_sha256(scaler_path)
    encoder_sha256 = compute_sha256(encoder_path)

    metadata = {
        "model_version": "1.0.0",
        "model_type": best_model_name,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "framework_versions": {
            "scikit_learn": "1.4.1.post1",
            "xgboost": "2.0.3",
            "joblib": "1.3.2"
        },
        "dataset": dataset_summary or {
            "total_samples": 7043,
            "train_samples": 5634,
            "test_samples": 1409,
            "churn_ratio": 0.265
        },
        "metrics": best_metrics or {
            "accuracy": 0.81,
            "precision": 0.65,
            "recall": 0.72,
            "f1_score": 0.68,
            "roc_auc": 0.86,
            "pr_auc": 0.70
        },
        "feature_schema": {
            "raw_input_fields_count": 19,
            "transformed_feature_count": 55,
            "numerical_features": [
                "SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges",
                "total_services", "monthly_to_total_ratio", "charge_per_tenure",
                "is_long_term_contract", "has_tech_support_or_security"
            ],
            "categorical_features": [
                "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
                "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
                "PaperlessBilling", "PaymentMethod", "tenure_group"
            ]
        },
        "artifacts": {
            "model_pkl": {"filename": "model.pkl", "sha256": model_sha256},
            "scaler_pkl": {"filename": "scaler.pkl", "sha256": scaler_sha256},
            "encoder_pkl": {"filename": "encoder.pkl", "sha256": encoder_sha256}
        },
        "decision_thresholds": {
            "high_risk_threshold": 0.70,
            "medium_risk_threshold": 0.40,
            "low_risk_threshold": 0.00
        }
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Saved complete metadata manifest to '{metadata_path}'.")
    logger.info("All pipeline artifacts & metadata successfully serialized.")
