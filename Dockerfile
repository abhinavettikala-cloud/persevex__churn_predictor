# ==============================================================================
# Production Dockerfile for Telecom Customer Churn FastAPI Microservice
# Base Image: Official Lightweight Python 3.12 Slim Linux Image
# ==============================================================================
FROM python:3.12-slim

# ------------------------------------------------------------------------------
# 1. Set Environment Variables for Python Performance & Size Optimization
# ------------------------------------------------------------------------------
# PYTHONDONTWRITEBYTECODE=1: Prevents Python from writing .pyc files to disk, saving space.
# PYTHONUNBUFFERED=1: Forces stdout/stderr logs to be sent straight to terminal without buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ------------------------------------------------------------------------------
# 2. Set Working Directory inside the Container
# ------------------------------------------------------------------------------
# WORKDIR /app: Sets the default execution path inside the container for all subsequent commands.
WORKDIR /app

# ------------------------------------------------------------------------------
# 3. Install System Dependencies & Upgrade pip
# ------------------------------------------------------------------------------
# --no-cache-dir: Optimizes image size by skipping pip's HTTP download cache storing.
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# 4. Copy Application Source Code & Trained Model Artifacts
# ------------------------------------------------------------------------------
# Copy pipeline source code, API handlers, service modules, and serialized artifacts (.pkl)
COPY src/ /app/src/
COPY app.py /app/app.py
COPY train_pipeline.py /app/train_pipeline.py
COPY model.pkl /app/model.pkl
COPY scaler.pkl /app/scaler.pkl
COPY encoder.pkl /app/encoder.pkl

# ------------------------------------------------------------------------------
# 5. Expose Application Port
# ------------------------------------------------------------------------------
# EXPOSE 8000: Documents that the FastAPI service inside container listens on port 8000.
EXPOSE 8000

# ------------------------------------------------------------------------------
# 6. Container Entrypoint & Default Execution Command
# ------------------------------------------------------------------------------
# CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]:
# Uses shell execution so Render's dynamic $PORT environment variable is resolved automatically.
CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
