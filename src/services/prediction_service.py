"""
High-level Prediction Service Orchestrator for Telecom Churn System.
Handles feature transformation, model inference, prediction explainability,
execution timing, and persistent database logging.
"""

import time
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .artifact_loader import ArtifactLoader
from .preprocessor_service import DataPreprocessingService
from src.db.repository import save_prediction_record

logger = logging.getLogger(__name__)


@dataclass
class ExplanationFactor:
    factor_name: str
    impact_level: str  # 'High', 'Medium', 'Low'
    description: str


@dataclass
class PredictionResult:
    """
    Data Transfer Object representing complete prediction output.
    """
    id: str
    prediction: str            # 'Churn' or 'No Churn'
    churn_label: int           # 1 or 0
    probability: float         # 0.0 to 1.0
    confidence_score: float    # 0.5 to 1.0
    risk_level: str            # 'Low', 'Medium', 'High'
    execution_time_ms: float   # Inference latency in ms
    model_version: str         # Version tag
    timestamp: str             # ISO 8601 UTC string
    top_positive_factors: List[Dict[str, str]] = field(default_factory=list)
    top_negative_factors: List[Dict[str, str]] = field(default_factory=list)
    explanation_text: str = ""


class PredictionService:
    """
    Orchestrates preprocessor execution, model inference, explainability generation,
    and automatic database logging.
    """
    def __init__(
        self,
        artifact_loader: Optional[ArtifactLoader] = None,
        preprocessing_service: Optional[DataPreprocessingService] = None
    ):
        self.artifact_loader = artifact_loader or ArtifactLoader()
        self.preprocessor = preprocessing_service or DataPreprocessingService()

    def _generate_explainability(
        self,
        raw_input: Dict[str, Any],
        churn_prob: float
    ) -> tuple[List[Dict[str, str]], List[Dict[str, str]], str]:
        """Generates feature importance & rule-based explainability factors for predictions."""
        positive_factors = []
        negative_factors = []

        contract = raw_input.get("Contract", "Month-to-month")
        tenure = int(raw_input.get("tenure", 0))
        internet = raw_input.get("InternetService", "Fiber optic")
        monthly = float(raw_input.get("MonthlyCharges", 0.0))
        payment = raw_input.get("PaymentMethod", "Electronic check")
        tech_support = raw_input.get("TechSupport", "No")
        security = raw_input.get("OnlineSecurity", "No")

        # Positive Churn Risk Drivers
        if contract == "Month-to-month":
            positive_factors.append({
                "factor_name": "Month-to-Month Contract",
                "impact_level": "High",
                "description": "Short commitment duration significantly increases cancellation flexibility."
            })
        if internet == "Fiber optic":
            positive_factors.append({
                "factor_name": "Fiber Optic Internet",
                "impact_level": "High",
                "description": "Higher cost tier with sensitive market competition."
            })
        if tenure <= 12:
            positive_factors.append({
                "factor_name": f"Low Tenure ({tenure} mos)",
                "impact_level": "High",
                "description": "Newer customers have not established brand loyalty."
            })
        if payment == "Electronic check":
            positive_factors.append({
                "factor_name": "Electronic Check Payment",
                "impact_level": "Medium",
                "description": "Manual payment methods correlate with higher customer turnover."
            })
        if monthly > 75.0:
            positive_factors.append({
                "factor_name": f"High Monthly Charges (${monthly:.2f})",
                "impact_level": "Medium",
                "description": "Higher price point elevates budget sensitivity."
            })

        # Negative / Protective Factors against Churn
        if contract in ["One year", "Two year"]:
            negative_factors.append({
                "factor_name": f"{contract} Contract",
                "impact_level": "High",
                "description": "Long-term contractual commitment provides strong retention stability."
            })
        if tenure > 24:
            negative_factors.append({
                "factor_name": f"High Tenure ({tenure} mos)",
                "impact_level": "High",
                "description": "Established long-term customer relationship."
            })
        if tech_support == "Yes":
            negative_factors.append({
                "factor_name": "Tech Support Subscribed",
                "impact_level": "Medium",
                "description": "Dedicated assistance reduces service frustration."
            })
        if security == "Yes":
            negative_factors.append({
                "factor_name": "Online Security Subscribed",
                "impact_level": "Medium",
                "description": "Value-add security services increase platform stickiness."
            })
        if "automatic" in payment.lower():
            negative_factors.append({
                "factor_name": f"Automatic Payment ({payment})",
                "impact_level": "Medium",
                "description": "Auto-pay reduces payment friction and missed bills."
            })

        # Synthesize plain English summary
        if churn_prob >= 0.50:
            pos_names = [f["factor_name"] for f in positive_factors[:3]]
            explanation = (
                f"Customer has a high churn probability ({churn_prob*100:.1f}%) primarily due to "
                + (", ".join(pos_names) if pos_names else "overall billing profile") + "."
            )
        else:
            neg_names = [f["factor_name"] for f in negative_factors[:3]]
            explanation = (
                f"Customer has a low churn risk ({(1-churn_prob)*100:.1f}% retention probability) supported by "
                + (", ".join(neg_names) if neg_names else "steady account history") + "."
            )

        return positive_factors, negative_factors, explanation

    def predict(self, raw_input: Dict[str, Any]) -> PredictionResult:
        """Executes end-to-end churn prediction, explainability, and database logging."""
        start_time = time.perf_counter()

        if not self.artifact_loader.is_loaded():
            raise RuntimeError("Pipeline artifacts are not loaded.")

        model, scaler, encoder = self.artifact_loader.get_artifacts()

        # 1. Preprocess features using Preprocessing Service
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

        # 3. Risk Level Classification
        if churn_prob >= 0.70:
            risk_level = "High"
        elif churn_prob >= 0.40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # 4. Generate Explainability Factors
        pos_factors, neg_factors, explanation = self._generate_explainability(raw_input, churn_prob)

        execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        prediction_id = f"PRED-{uuid.uuid4().hex[:8].upper()}"

        result = PredictionResult(
            id=prediction_id,
            prediction=prediction_str,
            churn_label=prediction_label,
            probability=round(churn_prob, 4),
            confidence_score=round(confidence_score, 4),
            risk_level=risk_level,
            execution_time_ms=execution_time_ms,
            model_version="v1.0.0-LogisticRegression",
            timestamp=datetime.now(timezone.utc).isoformat(),
            top_positive_factors=pos_factors,
            top_negative_factors=neg_factors,
            explanation_text=explanation
        )

        # 5. Persist Record to Database
        try:
            record_dict = {
                "id": result.id,
                "timestamp": result.timestamp,
                "prediction": result.prediction,
                "churn_label": result.churn_label,
                "probability": result.probability,
                "confidence_score": result.confidence_score,
                "risk_level": result.risk_level,
                "execution_time_ms": result.execution_time_ms,
                "model_version": result.model_version,
                "top_positive_factors": result.top_positive_factors,
                "top_negative_factors": result.top_negative_factors,
                "explanation_text": result.explanation_text,
                **raw_input
            }
            save_prediction_record(record_dict)
        except Exception as db_err:
            logger.warning(f"Could not persist prediction to database: {db_err}")

        logger.info(f"Prediction generated [{result.id}]: {result.prediction} (prob={result.probability}, latency={result.execution_time_ms}ms)")
        return result
