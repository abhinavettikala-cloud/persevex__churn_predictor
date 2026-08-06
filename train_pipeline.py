#!/usr/bin/env python3
"""
Telecom Customer Churn - End-to-End Machine Learning Pipeline Execution Script.

Tasks Executed:
1. Load Dataset ('data/telecom_churn.csv')
2. Data Cleaning & Type Conversion
3. Missing Value Handling (TotalCharges imputation)
4. Feature Engineering (tenure_group, total_services, charge_per_tenure, etc.)
5. Exploratory Data Analysis (EDA Summary Statistics & Target Distribution)
6. Train/Test Split (Stratified 80/20 split)
7. Categorical Encoding (OneHotEncoder) & Scaling (StandardScaler)
8. Train Logistic Regression, Random Forest, and XGBoost models with class balancing
9. Evaluation & Comparison across Accuracy, Precision, Recall, F1 Score, ROC-AUC, and PR-AUC
10. Model Selection & Exporting model.pkl, scaler.pkl, encoder.pkl, and metadata.json
11. End-to-End Inference Test Verification
"""

import os
import sys
import logging
import joblib
import pandas as pd
import numpy as np

# Ensure local src module imports work seamlessly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from pipeline.data_loader import load_data
from pipeline.data_cleaner import clean_data
from pipeline.feature_engineering import engineer_features
from pipeline.eda import perform_eda
from pipeline.preprocessor import split_and_preprocess
from pipeline.model_trainer import train_and_evaluate_models
from pipeline.serializer import save_artifacts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("TrainPipeline")

def main():
    logger.info("==================================================================")
    logger.info(" Starting Telecom Customer Churn Machine Learning Pipeline ")
    logger.info("==================================================================")

    # 1. Load Dataset
    logger.info("\n--- Step 1: Loading Dataset ---")
    raw_df = load_data()

    # 2. Data Cleaning & Missing Value Handling
    logger.info("\n--- Step 2: Data Cleaning & Missing Value Handling ---")
    cleaned_df = clean_data(raw_df)

    # 3. Feature Engineering
    logger.info("\n--- Step 3: Feature Engineering ---")
    featured_df = engineer_features(cleaned_df)

    # 4. Exploratory Data Analysis (EDA)
    logger.info("\n--- Step 4: Exploratory Data Analysis ---")
    eda_summary = perform_eda(featured_df, target_col="Churn")

    # 5. Train/Test Split, Encoding, and Scaling
    logger.info("\n--- Step 5: Train/Test Split, Encoding, & Scaling ---")
    (
        X_train_scaled,
        X_test_scaled,
        y_train,
        y_test,
        scaler,
        encoder,
        feature_names
    ) = split_and_preprocess(featured_df, target_col="Churn", test_size=0.2, random_state=42)

    # 6. Train Models & Evaluate
    logger.info("\n--- Step 6: Model Training, Evaluation & Comparison ---")
    trained_models, metrics_df, best_model, best_model_name, best_metrics = train_and_evaluate_models(
        X_train_scaled, X_test_scaled, y_train, y_test, random_state=42
    )

    print("\n" + "="*70)
    print("                MODEL PERFORMANCE COMPARISON TABLE               ")
    print("="*70)
    print(metrics_df.to_string(index=False))
    print("="*70 + "\n")

    logger.info(f"Selected Best Model: '{best_model_name}'")

    # 7. Save Pipeline Artifacts & Metadata
    logger.info("\n--- Step 7: Saving Model Artifacts & Metadata ---")
    dataset_summary = {
        "total_samples": len(featured_df),
        "train_samples": len(X_train_scaled),
        "test_samples": len(X_test_scaled),
        "churn_ratio": float((featured_df["Churn"] == "Yes").mean())
    }
    save_artifacts(
        best_model=best_model,
        scaler=scaler,
        encoder=encoder,
        output_dir=".",
        best_model_name=best_model_name,
        best_metrics=best_metrics,
        dataset_summary=dataset_summary
    )

    # 8. Verify Artifact Reload & Sample Inference
    logger.info("\n--- Step 8: End-to-End Artifact Verification & Sample Inference ---")
    loaded_model = joblib.load("model.pkl")
    loaded_scaler = joblib.load("scaler.pkl")
    loaded_encoder = joblib.load("encoder.pkl")

    # Test sample inference on first row of test features
    sample_input = X_test_scaled[0:1]
    sample_pred = loaded_model.predict(sample_input)[0]
    sample_prob = loaded_model.predict_proba(sample_input)[0][1] if hasattr(loaded_model, "predict_proba") else None

    logger.info("Verification Successful!")
    logger.info(f"Sample Test Prediction: {'Churn' if sample_pred == 1 else 'No Churn'} (Class: {sample_pred})")
    if sample_prob is not None:
        logger.info(f"Sample Churn Probability: {sample_prob:.4f}")

    logger.info("==================================================================")
    logger.info(" ML Pipeline Executed & Artifacts Saved Successfully ")
    logger.info("==================================================================")

if __name__ == "__main__":
    main()
