import os
import threading
import joblib
import logging
from typing import Tuple, Any

logger = logging.getLogger(__name__)

class ArtifactLoader:
    """
    Thread-safe Singleton artifact loader ensuring model.pkl, scaler.pkl, and encoder.pkl
    are loaded from disk into memory exactly once.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, model_path: str = "model.pkl", scaler_path: str = "scaler.pkl", encoder_path: str = "encoder.pkl"):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ArtifactLoader, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self, model_path: str = "model.pkl", scaler_path: str = "scaler.pkl", encoder_path: str = "encoder.pkl"):
        if self._initialized:
            return

        self.model_path = model_path
        self.scaler_path = scaler_path
        self.encoder_path = encoder_path

        self._model = None
        self._scaler = None
        self._encoder = None

        self.load_all()
        self._initialized = True

    def load_all(self) -> None:
        """Loads model, scaler, and encoder artifacts into memory."""
        logger.info(f"Loading pipeline artifacts from disk (Model: {self.model_path}, Scaler: {self.scaler_path}, Encoder: {self.encoder_path})...")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model artifact missing at path: '{self.model_path}'")
        if not os.path.exists(self.scaler_path):
            raise FileNotFoundError(f"Scaler artifact missing at path: '{self.scaler_path}'")
        if not os.path.exists(self.encoder_path):
            raise FileNotFoundError(f"Encoder artifact missing at path: '{self.encoder_path}'")

        self._model = joblib.load(self.model_path)
        self._scaler = joblib.load(self.scaler_path)
        self._encoder = joblib.load(self.encoder_path)

        logger.info("All pipeline artifacts loaded successfully into memory.")

    @property
    def model(self) -> Any:
        return self._model

    @property
    def scaler(self) -> Any:
        return self._scaler

    @property
    def encoder(self) -> Any:
        return self._encoder

    def get_artifacts(self) -> Tuple[Any, Any, Any]:
        """Returns tuple of (model, scaler, encoder)."""
        return self._model, self._scaler, self._encoder

    def is_loaded(self) -> bool:
        """Returns True if all artifacts are loaded in memory."""
        return self._model is not None and self._scaler is not None and self._encoder is not None
