import logging
from typing import Tuple, Dict, Any

from src.api.schemas import ChurnPredictionRequest, ChurnPredictionResponse
from src.services.prediction_service import PredictionService
from src.services.artifact_loader import ArtifactLoader

logger = logging.getLogger(__name__)

class ChurnPredictor:
    """
    Lightweight Adapter bridging FastAPI Pydantic requests to the decoupled PredictionService.
    """
    def __init__(self, model_path: str = "model.pkl", scaler_path: str = "scaler.pkl", encoder_path: str = "encoder.pkl"):
        self.artifact_loader = ArtifactLoader(model_path, scaler_path, encoder_path)
        self.service = PredictionService(artifact_loader=self.artifact_loader)
        self.model_version = "1.0.0"

    def is_healthy(self) -> Tuple[bool, bool, bool]:
        """Checks artifact loading health status."""
        loaded = self.artifact_loader.is_loaded()
        return (loaded, loaded, loaded)

    def predict(self, request: ChurnPredictionRequest) -> ChurnPredictionResponse:
        """
        Delegates prediction to PredictionService and converts result to ChurnPredictionResponse.
        """
        raw_input = request.model_dump()
        result = self.service.predict(raw_input)

        return ChurnPredictionResponse(
            prediction=result.prediction,
            churn_label=result.churn_label,
            probability=result.probability,
            confidence_score=result.confidence_score,
            risk_level=result.risk_level,
            model_version=self.model_version,
            timestamp=result.timestamp
        )
