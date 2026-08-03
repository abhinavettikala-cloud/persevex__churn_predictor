import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Tuple

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

logger = logging.getLogger(__name__)

def train_and_evaluate_models(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: pd.Series,
    y_test: pd.Series,
    random_state: int = 42
) -> Tuple[Dict[str, Any], pd.DataFrame, Any, str]:
    """
    Trains Logistic Regression, Random Forest, and XGBoost models, evaluates performance metrics,
    compares results, and selects the best performing model based on ROC-AUC and F1 Score.

    Metrics computed for each model:
    - Accuracy
    - Precision
    - Recall
    - F1 Score
    - ROC-AUC

    Parameters:
        X_train (np.ndarray): Scaled training features.
        X_test (np.ndarray): Scaled test features.
        y_train (pd.Series): Training target labels.
        y_test (pd.Series): Test target labels.
        random_state (int): Random seed for reproducibility.

    Returns:
        Tuple containing:
        - trained_models (Dict[str, Any]): Dictionary of trained model instances.
        - metrics_df (pd.DataFrame): Comparison DataFrame of metrics across models.
        - best_model (Any): Best trained model instance.
        - best_model_name (str): Name of the best performing model.
    """
    logger.info("Initializing models for training...")

    # Define model instances
    models = {
        "Logistic Regression": LogisticRegression(
            C=1.0, max_iter=1000, random_state=random_state
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=random_state, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=5,
            eval_metric="logloss", random_state=random_state
        )
    }

    trained_models = {}
    metrics_list = []

    for name, model in models.items():
        logger.info(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model

        # Predict on test set
        y_pred = model.predict(X_test)
        
        # Predict probabilities for ROC-AUC calculation
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = y_pred

        # Compute classification metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred)

        logger.info(f"--- {name} Results ---")
        logger.info(f"Accuracy:  {acc:.4f}")
        logger.info(f"Precision: {prec:.4f}")
        logger.info(f"Recall:    {rec:.4f}")
        logger.info(f"F1 Score:  {f1:.4f}")
        logger.info(f"ROC-AUC:   {auc:.4f}")
        logger.info(f"Confusion Matrix:\n{cm}")

        metrics_list.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1 Score": f1,
            "ROC-AUC": auc
        })

    metrics_df = pd.DataFrame(metrics_list).sort_values(by="ROC-AUC", ascending=False).reset_index(drop=True)

    # Select best model based on highest ROC-AUC (and F1 Score as tiebreaker)
    best_row = metrics_df.iloc[0]
    best_model_name = best_row["Model"]
    best_model = trained_models[best_model_name]

    logger.info(f"--- Best Model Selection ---")
    logger.info(f"Selected Best Model: {best_model_name} with ROC-AUC: {best_row['ROC-AUC']:.4f} and F1 Score: {best_row['F1 Score']:.4f}")

    return trained_models, metrics_df, best_model, best_model_name
