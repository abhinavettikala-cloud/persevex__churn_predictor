# Persevex — Telecom Customer Churn Predictor & Telemetry Engine

Production-grade enterprise platform for real-time customer attrition telemetry, machine learning prediction, and prescriptive retention analytics.

---

## 🏗️ Deployment & System Architecture

```text
                  ┌─────────────────────────────────┐
                  │          End User               │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │    Streamlit UI Frontend        │
                  │        (Port 8501)              │
                  └────────────────┬────────────────┘
                                   │ HTTP POST /predict
                                   ▼
                  ┌─────────────────────────────────┐
                  │     FastAPI REST API Backend    │
                  │        (Port 8000)              │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │   Data Preprocessing Pipeline   │
                  │   (Scaler.pkl + Encoder.pkl)    │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │  Calibrated Logistic Regression │
                  │          (Model.pkl)            │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │   Structured JSON Telemetry     │
                  │   (Probability & Risk Level)    │
                  └─────────────────────────────────┘
```

The application is deployed as **two independent microservices**:
1. **FastAPI REST API Backend (`Dockerfile.api`)**: Port `8000` (runs `uvicorn fastapi_app:app --host 0.0.0.0 --port $PORT`).
2. **Streamlit UI Frontend (`Dockerfile.ui`)**: Port `8501` (runs `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`).

---

## 🛠️ Local Development & Quickstart

### Prerequisites
- Python 3.11+
- Virtual Environment (`venv` or `conda`)

### 1. Launch FastAPI Backend
```bash
# Navigate to project root
cd telecom-churn-predictor

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI backend
python -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```
- **API Base URL**: `http://localhost:8000`
- **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### 2. Launch Streamlit UI Frontend
Open a separate terminal:
```bash
# Set environment variable pointing to API backend
export API_BASE_URL=http://localhost:8000   # On Windows PowerShell: $env:API_BASE_URL="http://localhost:8000"

# Start Streamlit application
streamlit run app.py
```
- **Streamlit Localhost**: [http://localhost:8501](http://localhost:8501)

---

## 🐳 Docker & Docker Compose Deployment

### Option A: Launch Full Stack via Docker Compose
```bash
docker-compose up --build
```
- Streamlit UI: `http://localhost:8501`
- FastAPI REST API: `http://localhost:8000`

### Option B: Build & Run Individual Containers

#### 1. Backend API Container
```bash
docker build -f Dockerfile.api -t churn-predictor-api .
docker run --rm -p 8000:8000 -e PORT=8000 churn-predictor-api
```

#### 2. Frontend UI Container
```bash
docker build -f Dockerfile.ui -t churn-predictor-ui .
docker run --rm -p 8501:8501 -e PORT=8501 -e API_BASE_URL=http://host.docker.internal:8000 churn-predictor-ui
```

---

## ☁️ Render Deployment Instructions

Deploy two separate **Render Web Services**:

### 1. Render Backend Web Service (`churn-predictor-api`)
- **Service Type**: Web Service
- **Environment**: Docker
- **Dockerfile Path**: `Dockerfile.api`
- **Port**: Render automatically injects `$PORT`.
- **Start Command**: `uvicorn fastapi_app:app --host 0.0.0.0 --port $PORT`

### 2. Render Frontend Web Service (`churn-predictor-ui`)
- **Service Type**: Web Service
- **Environment**: Docker
- **Dockerfile Path**: `Dockerfile.ui`
- **Environment Variables**:
  - `API_BASE_URL`: `https://YOUR-BACKEND-API-SERVICE.onrender.com`
  - `ENABLE_FALLBACK`: `false`
- **Start Command**: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

---

## 📡 API Usage & cURL Examples

### Health Check
```bash
curl http://localhost:8000/health
```
**Response**:
```json
{
  "status": "healthy",
  "service": "telecom-churn-predictor-api",
  "model_loaded": true,
  "scaler_loaded": true,
  "encoder_loaded": true,
  "model_version": "1.0.0",
  "sha256_hashes": { ... },
  "timestamp": "2026-08-09T19:22:00.000Z"
}
```

### Predict Customer Churn
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 1,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.0,
    "TotalCharges": 85.0
  }'
```
**Response**:
```json
{
  "prediction": "Churn",
  "churn_label": 1,
  "probability": 0.7177,
  "confidence_score": 0.7177,
  "risk_level": "High",
  "model_version": "1.0.0",
  "timestamp": "2026-08-09T19:22:00.000Z"
}
```

---

## 🔧 Environment Variables Reference

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `API_BASE_URL` | `http://localhost:8000` | Target URL of deployed FastAPI backend service |
| `ENABLE_FALLBACK` | `false` | Enable/disable in-memory fallback model if API fails |
| `ALLOWED_ORIGINS` | `http://localhost:8501...` | Comma-separated CORS allowed origin URLs |
| `RATE_LIMIT_PER_MINUTE` | `100` | Rate limit threshold per client IP on `/predict` |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `MODEL_VERSION` | `1.0.0` | Model version indicator |

---

## ❓ Troubleshooting Guide

### 1. Streamlit UI displays "● API Unavailable"
- Check that the FastAPI backend server is running.
- Verify `API_BASE_URL` environment variable matches your running API address.
- Verify CORS allowed origins in `fastapi_app.py` includes your Streamlit host address.

### 2. Plotly Charts fail to render
- Ensure Plotly annotation layout configs do not pass unsupported `font_weight` kwargs.

### 3. Model artifact loading error
- Ensure `model.pkl`, `scaler.pkl`, `encoder.pkl`, and `metadata.json` are present in the project root directory.

---

## 🧪 Testing
Run the comprehensive master automated test runner:
```bash
python run_all_tests.py
```
