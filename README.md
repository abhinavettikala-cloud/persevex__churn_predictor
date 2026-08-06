# 📡 Telecom Customer Churn AI Predictor

[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Render Deployable](https://img.shields.io/badge/Render-Deployable-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

An enterprise-grade, full-stack Machine Learning application predicting telecom customer churn probabilities using trained XGBoost/Scikit-Learn models, complete with real-time interactive Plotly dashboards, dynamic light/dark UI themes, persistent customer evaluation history, and dual deployment modes (FastAPI + React or Standalone Streamlit Web Service).

---

## 🚀 Quick Start (Local Streamlit Web Service)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit Application**:
   ```bash
   streamlit run streamlit_app.py
   ```
   Open `http://localhost:8501` in your browser.

3. **Run Automated Test Suite (28/28 System Tests)**:
   ```bash
   python run_all_tests.py
   ```

---

## 🌐 Deploy to Render (Web Service)

### Option 1: Native Python Runtime (Recommended)

1. Connect your GitHub repository to [Render.com](https://render.com).
2. Create a new **Web Service**.
3. Configure the following deployment settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. Deploy! Streamlit will automatically launch with `$PORT` binding.

### Option 2: 1-Click Blueprint Deploy

1. In Render, select **Blueprints** ➔ **New Blueprint Instance**.
2. Select your repository. Render will automatically detect `render.yaml` and provision the web service.

---

## 🏗️ Architecture & Project Structure

```
telecom-churn-predictor/
├── app.py                     # FastAPI REST API Backend
├── streamlit_app.py           # Unified Streamlit Web Service Application
├── render.yaml                # Render Blueprint Deployment Spec
├── evaluations_history.json   # Persistent evaluation log storage
├── model.pkl                  # Trained Machine Learning Model
├── scaler.pkl                 # StandardScaler Artifact
├── encoder.pkl                # OneHotEncoder Artifact
├── .streamlit/
│   └── config.toml            # Streamlit Render Server Configuration
├── src/
│   ├── api/                   # Inference Engine & Schemas
│   ├── pipeline/              # Cleaning, Feature Engineering & Serializer
│   └── services/              # Artifact Loader & Prediction Service
├── tests/                     # Unit, Endpoint & Integration Tests
└── requirements.txt           # Python Dependencies
```

---

## 📊 Features & UI Capabilities

- **Executive Dashboard**: Key performance metrics (Total Customers, Session Churn Rate %, Risk Tiers, Real-time Customer Evaluations Table).
- **Single Customer Prediction Form**: Interactive input fields for all 19 customer features with preset shortcuts (`High Risk`, `Loyal Customer`).
- **Interactive Visualizations**: Speedometer gauge charts, feature importance bar charts, risk tier distribution pie charts, confusion matrix heatmaps, and ROC curves.
- **Dual Engine Architecture**: Automatically connects to FastAPI backend (`/predict`) if available, or falls back seamlessly to the in-memory `ChurnPredictor` engine for 1-click standalone web deployments.
