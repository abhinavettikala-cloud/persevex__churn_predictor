import os
import joblib
import logging
from typing import Any

logger = logging.getLogger(__name__)

def save_artifacts(
    best_model: Any,
    scaler: Any,
    encoder: Any,
    output_dir: str = "."
) -> None:
    """
    Serializes and saves model.pkl, scaler.pkl, and encoder.pkl to specified output directory.

    Parameters:
        best_model (Any): Best trained classifier.
        scaler (Any): Fitted StandardScaler instance.
        encoder (Any): Fitted OneHotEncoder instance.
        output_dir (str): Destination directory path (default: current working directory '.').
    """
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, "model.pkl")
    scaler_path = os.path.join(output_dir, "scaler.pkl")
    encoder_path = os.path.join(output_dir, "encoder.pkl")

    joblib.dump(best_model, model_path)
    logger.info(f"Saved best model artifact to '{model_path}'.")

    joblib.dump(scaler, scaler_path)
    logger.info(f"Saved scaler artifact to '{scaler_path}'.")

    joblib.dump(encoder, encoder_path)
    logger.info(f"Saved encoder artifact to '{encoder_path}'.")

    logger.info("All pipeline artifacts successfully serialized.")
