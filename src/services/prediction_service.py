import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from .artifact_loader import ArtifactLoader
from .preprocessor_service import DataPreprocessingService

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """
    Data Transfer Object representing prediction output.
    """
    prediction: str            # 'Churn' or 'No Churn'
    churn_label: int           # 1 or 0
    probability: float         # 0.0 to 1.0
    confidence_score: float    # 0.5 to 1.0
    risk_level: str            # 'Low', 'Medium', 'High'
    timestamp: str             # ISO 8601 string


class PredictionService:
    """
    High-level Prediction Service orchestrator.
    Manages single-load artifact lifecycle, invokes preprocessing, and produces predictions.
    """
    def __init__(
        self,
        artifact_loader: Optional[ArtifactLoader] = None,
        preprocessing_service: Optional[DataPreprocessingService] = None
    ):
        self.artifact_loader = artifact_loader or ArtifactLoader()
        self.preprocessor = preprocessing_service or DataPreprocessingService()

    def predict(self, raw_input: Dict[str, Any]) -> PredictionResult:
        """
        Executes end-to-end churn prediction for a given customer feature payload.

        Parameters:
            raw_input (Dict[str, Any]): Raw feature key-value pairs.

        Returns:
            PredictionResult: Structured prediction result containing label, probability, confidence, and risk level.
        """
        if not self.artifact_loader.is_loaded():
            raise RuntimeError("Pipeline artifacts are not loaded.")

        model, scaler, encoder = self.artifact_loader.get_artifacts()

        # 1. Preprocess features using dedicated Preprocessing Service
        scaled_features = self.preprocessor.prepare_features(raw_input, encoder, scaler)

        # 2. Evaluate Model Prediction
        prediction_label = int(model.predict(scaled_features)[0])

        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(scaled_features)[0][1])
        else:
            prob = float(prediction_label)

        churn_prob = max(0.0, min(1.0, prob))
        prediction_str = "Churn" if prediction_label == 1 else "No Churn"
        confidence_score = churn_prob if prediction_label == 1 else 1.0 - churn_prob

        # 3. Determine Risk Classification Level
        if churn_prob >= 0.70:
            risk_level = "High"
        elif churn_prob >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        result = PredictionResult(
            prediction=prediction_str,
            churn_label=prediction_label,
            probability=round(churn_prob, 4),
            confidence_score=round(confidence_score, 4),
            risk_level=risk_level,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

        logger.info(f"Prediction generated: {result.prediction} (prob={result.probability}, risk={result.risk_level})")
        return result
