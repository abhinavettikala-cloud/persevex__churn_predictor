import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Tuple

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

logger = logging.getLogger(__name__)

def train_and_evaluate_models(
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: pd.Series,
    y_test: pd.Series,
    random_state: int = 42
) -> Tuple[Dict[str, Any], pd.DataFrame, Any, str, Dict[str, Any]]:
    """
    Trains Logistic Regression, Random Forest, and XGBoost models with class imbalance mitigation
    and probability calibration. Evaluates performance across key metrics.

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
        - best_model (Any): Best trained and calibrated model instance.
        - best_model_name (str): Name of the best performing model.
        - best_metrics (Dict[str, Any]): Dictionary of metrics for the best model.
    """
    logger.info("Initializing models with class imbalance mitigation...")

    # Calculate class weight ratio for XGBoost (num_negative / num_positive)
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = float(neg_count / max(1, pos_count))

    # Define base model instances with explicit class weighting for minority churn class
    base_models = {
        "Logistic Regression": LogisticRegression(
            C=1.0, max_iter=1000, class_weight="balanced", random_state=random_state
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=10, class_weight="balanced", random_state=random_state, n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=5,
            scale_pos_weight=scale_pos_weight, eval_metric="logloss", random_state=random_state
        )
    }

    trained_models = {}
    metrics_list = []

    for name, base_model in base_models.items():
        logger.info(f"Training and calibrating {name}...")
        
        # Train calibrated classifier with 5-fold cross-validation
        calibrated_model = CalibratedClassifierCV(estimator=base_model, cv=5, method="sigmoid")
        calibrated_model.fit(X_train, y_train)
        
        trained_models[name] = calibrated_model

        # Predict on test set
        y_pred = calibrated_model.predict(X_test)
        y_proba = calibrated_model.predict_proba(X_test)[:, 1]

        # Compute metrics
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, zero_division=0))
        rec = float(recall_score(y_test, y_pred, zero_division=0))
        f1 = float(f1_score(y_test, y_pred, zero_division=0))
        auc = float(roc_auc_score(y_test, y_proba))
        pr_auc = float(average_precision_score(y_test, y_proba))
        cm = confusion_matrix(y_test, y_pred).tolist()

        logger.info(f"--- {name} Results ---")
        logger.info(f"Accuracy:  {acc:.4f}")
        logger.info(f"Precision: {prec:.4f}")
        logger.info(f"Recall:    {rec:.4f}")
        logger.info(f"F1 Score:  {f1:.4f}")
        logger.info(f"ROC-AUC:   {auc:.4f}")
        logger.info(f"PR-AUC:    {pr_auc:.4f}")

        metrics_list.append({
            "Model": name,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1 Score": f1,
            "ROC-AUC": auc,
            "PR-AUC": pr_auc,
            "ConfusionMatrix": cm
        })

    metrics_df = pd.DataFrame(metrics_list).sort_values(by="ROC-AUC", ascending=False).reset_index(drop=True)

    # Select best model based on ROC-AUC (and F1 Score as tiebreaker)
    best_row = metrics_df.iloc[0]
    best_model_name = str(best_row["Model"])
    best_model = trained_models[best_model_name]
    
    best_metrics = {
        "accuracy": float(best_row["Accuracy"]),
        "precision": float(best_row["Precision"]),
        "recall": float(best_row["Recall"]),
        "f1_score": float(best_row["F1 Score"]),
        "roc_auc": float(best_row["ROC-AUC"]),
        "pr_auc": float(best_row["PR-AUC"]),
        "confusion_matrix": best_row["ConfusionMatrix"]
    }

    logger.info("--- Best Model Selection ---")
    logger.info(f"Selected Best Model: {best_model_name} with ROC-AUC: {best_metrics['roc_auc']:.4f} and F1 Score: {best_metrics['f1_score']:.4f}")

    return trained_models, metrics_df, best_model, best_model_name, best_metrics
