import os
from pathlib import Path
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

    def _resolve_path(self, path_str: str) -> str:
        """Resolves artifact file paths robustly across OS environments."""
        path = Path(path_str)
        if path.is_absolute() and path.exists():
            return str(path)
        if path.exists():
            return str(path)
        
        base_dir = Path(__file__).resolve().parent.parent.parent
        rel_root = base_dir / path_str
        if rel_root.exists():
            return str(rel_root)
        
        rel_model_dir = base_dir / "model" / Path(path_str).name
        if rel_model_dir.exists():
            return str(rel_model_dir)
            
        return str(path)

    def load_all(self) -> None:
        """Loads model, scaler, and encoder artifacts into memory."""
        resolved_model = self._resolve_path(self.model_path)
        resolved_scaler = self._resolve_path(self.scaler_path)
        resolved_encoder = self._resolve_path(self.encoder_path)

        logger.info(f"Loading pipeline artifacts from disk (Model: {resolved_model}, Scaler: {resolved_scaler}, Encoder: {resolved_encoder})...")

        if not os.path.exists(resolved_model):
            raise FileNotFoundError(f"Model artifact missing at path: '{self.model_path}' (resolved: '{resolved_model}')")
        if not os.path.exists(resolved_scaler):
            raise FileNotFoundError(f"Scaler artifact missing at path: '{self.scaler_path}' (resolved: '{resolved_scaler}')")
        if not os.path.exists(resolved_encoder):
            raise FileNotFoundError(f"Encoder artifact missing at path: '{self.encoder_path}' (resolved: '{resolved_encoder}')")

        self._model = joblib.load(resolved_model)
        self._scaler = joblib.load(resolved_scaler)
        self._encoder = joblib.load(resolved_encoder)

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
