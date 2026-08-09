# Model Card — Persevex Telecom Customer Churn Predictor

## Model Details
- **Model Name**: Persevex Telecom Customer Churn Classifier
- **Model Version**: `1.0.0`
- **Model Type**: Calibrated Logistic Regression Classifier (`sklearn.calibration.CalibratedClassifierCV`) wrapping `LogisticRegression(class_weight='balanced')`
- **Developer**: Persevex AI Telemetry Team
- **Release Date**: August 2026
- **License**: Proprietary / Enterprise

## Intended Use
- **Primary Use Case**: Autonomous real-time telemetry and risk assessment of customer churn probability for telecommunications subscribers.
- **Intended Users**: Enterprise telecom retention specialists, customer success managers, executive analytics teams.
- **Out-of-Scope Use Cases**: Automated account cancellation without human review, credit scoring, non-telecom domain applications.

## Model Architecture & Pipeline
1. **Data Cleaning & Imputation**: Continuous numerical features imputed with column medians; categorical strings normalized.
2. **Feature Engineering**: Ratio features derived (e.g. `TotalCharges / (tenure + 1)`), contract group indicators, streaming bundle indicators.
3. **Preprocessing**:
   - `StandardScaler` fitted on 3 continuous numerical features (`tenure`, `MonthlyCharges`, `TotalCharges`).
   - `OneHotEncoder` fitted on 16 categorical features with `handle_unknown='ignore'`.
4. **Calibrated Inference**: Produces well-calibrated class probabilities ($P(\text{Churn} \mid X)$) mapped to risk tiers:
   - **Low Risk**: $P(\text{Churn}) < 40\%$
   - **Medium Risk**: $40\% \le P(\text{Churn}) < 70\%$
   - **High Risk**: $P(\text{Churn}) \ge 70\%$

## Training Data & Performance Metrics
- **Dataset**: Telco Customer Churn Benchmark Dataset (7,043 subscriber records).
- **Test Evaluation Split**: 20% Stratified Holdout Test Set.

### Performance Metrics Manifest
- **Accuracy**: 79.2%
- **Precision**: 66.8%
- **Recall**: 51.6%
- **F1 Score**: 0.5822
- **ROC-AUC**: 0.8436
- **PR-AUC**: 0.6577

### Confusion Matrix (Test Set)
| Actual \ Predicted | Predicted No Churn | Predicted Churn |
| :--- | :--- | :--- |
| **Actual No Churn** | 939 (TN) | 96 (FP) |
| **Actual Churn** | 181 (FN) | 193 (TP) |

## Artifact Governance Hashes (SHA-256)
- `model.pkl`: Verified at startup
- `scaler.pkl`: Verified at startup
- `encoder.pkl`: Verified at startup
- `metadata.json`: Verified at startup

## Risk & Governance Considerations
- **Demographic Bias**: The model contains `SeniorCitizen` and `gender` features. Demographic features should be monitored to prevent unintended bias in promotional offerings.
- **Drift Monitoring**: Telemetry counters track prediction distributions ($P(\text{Churn})$ mean & risk tier percentages) to detect distribution drift over time.
