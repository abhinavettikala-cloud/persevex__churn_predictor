# Telecom Customer Churn Prediction - Render Deployment Guide

This guide provides step-by-step instructions for deploying the **Telecom Customer Churn Machine Learning System** (FastAPI Backend + Streamlit Web App) on **Render**.

---

## 🛠️ Production Startup Commands

| Service | Build Command | Startup Command |
| :--- | :--- | :--- |
| **FastAPI Backend API** | `pip install --upgrade pip && pip install -r requirements.txt` | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Streamlit Frontend App** | `pip install --upgrade pip && pip install -r requirements.txt` | `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0` |

> [!IMPORTANT]
> Always use `$PORT` (capitalized) in Render startup commands. Render automatically assigns a dynamic port number to `$PORT` at container boot time.

---

## 🔑 Environment Variables Reference

| Variable | Description | Recommended Render Value |
| :--- | :--- | :--- |
| `PYTHON_VERSION` | Python runtime version | `3.12.0` |
| `ENVIRONMENT` | Environment mode | `production` |
| `LOG_LEVEL` | Application logging level | `INFO` |
| `API_BASE_URL` | Base URL of deployed FastAPI service | `https://telecom-churn-api.onrender.com` |

---

## 🚀 Deployment Instructions

### Method 1: Automatic Blueprint Deployment (Recommended)

1. Push your project codebase to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> **Blueprints**.
4. Connect your GitHub repository containing [render.yaml](file:///c:/Users/abhic/Downloads/telecom-churn-predictor/render.yaml).
5. Render will automatically detect `render.yaml` and provision both:
   - `telecom-churn-api` (FastAPI backend service)
   - `telecom-churn-frontend` (Streamlit web dashboard)
6. Click **Apply**. Render will build and deploy both services automatically!

---

### Method 2: Manual Web Service Creation

If deploying services manually on Render:

#### 1. Deploy FastAPI Backend:
- Click **New +** -> **Web Service**.
- Select your repository.
- **Name**: `telecom-churn-api`
- **Runtime**: `Python`
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

#### 2. Deploy Streamlit Frontend:
- Click **New +** -> **Web Service**.
- Select your repository.
- **Name**: `telecom-churn-frontend`
- **Runtime**: `Python`
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
- **Environment Variable**: `API_BASE_URL` = `https://telecom-churn-api.onrender.com`

---

## ⚡ Production Settings & Optimizations

1. **Uvicorn Worker Threads**:
   For starter/free tiers (512MB RAM), run a single Uvicorn process per instance (`uvicorn app:app --host 0.0.0.0 --port $PORT`). For upgraded paid tiers (1GB+ RAM), use Gunicorn with 2 workers:
   ```bash
   gunicorn app:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```

2. **Artifact Commit Verification**:
   Ensure `model.pkl`, `scaler.pkl`, and `encoder.pkl` are committed to git so Render builds can load model artifacts instantly upon startup.

---

## ❓ Common Deployment Issues & Troubleshooting Fixes

### 1. Issue: `Error: Address already in use / Connection refused`
- **Cause**: Using hardcoded port (e.g. `--port 8000`) instead of Render's injected `$PORT`.
- **Fix**: Update start command to use `$PORT`:
  ```bash
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```

### 2. Issue: `FileNotFoundError: model.pkl missing`
- **Cause**: `.pkl` artifact files were excluded by `.gitignore` or omitted during git push.
- **Fix**: Check that `model.pkl`, `scaler.pkl`, and `encoder.pkl` exist in the repository root directory before pushing to GitHub.

### 3. Issue: `Out of Memory (OOM) during build or startup`
- **Cause**: Pip caching heavy dependencies (`torch` or unnecessary large packages).
- **Fix**: Ensure `pip install --no-cache-dir` is used in custom build scripts and keep `requirements.txt` minimal.

### 4. Issue: Streamlit Frontend shows `Connection Error` to API
- **Cause**: `API_BASE_URL` is set to `http://localhost:8000` instead of the public Render URL.
- **Fix**: Update the `API_BASE_URL` environment variable on `telecom-churn-frontend` in Render dashboard to point to `https://telecom-churn-api.onrender.com`.

### 5. Issue: Cold Start Latency (Free Tier Spin-Down)
- **Cause**: Render free tier web services spin down after 15 minutes of inactivity.
- **Fix**: The first request after spin-down may take ~30 seconds while Render wakes the container. This is normal behavior on free plans. Upgrade to Starter plan ($7/mo) or use a uptime keep-alive ping service.
