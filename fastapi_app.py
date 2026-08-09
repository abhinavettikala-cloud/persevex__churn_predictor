import os
import sys
import uuid
import time
import hashlib
import logging
import anyio
from pathlib import Path
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure local module path resolution
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.api.schemas import ChurnPredictionRequest, ChurnPredictionResponse, HealthResponse
from src.api.inference import ChurnPredictor

# 1. Configure Structured Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - [%(levelname)s] - [ReqID: %(request_id)s] - %(name)s - %(message)s"
)

class RequestIDFilter(logging.Filter):
    """Logging filter ensuring request_id is always available in log formatters."""
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "SYSTEM"
        return True

for handler in logging.root.handlers:
    handler.addFilter(RequestIDFilter())

logger = logging.getLogger("FastAPIApp")

# Telemetry Counters & Metrics
METRICS = {
    "total_requests": 0,
    "total_predictions": 0,
    "churn_predictions": 0,
    "no_churn_predictions": 0,
    "validation_errors": 0,
    "internal_errors": 0,
    "total_latency_seconds": 0.0
}

# Rate Limiting State (Simple sliding window per minute)
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MINUTE", 100))
RATE_LIMIT_WINDOW = 60.0
CLIENT_REQUEST_LOGS = {}

def calculate_sha256(filepath: Path) -> str:
    """Calculates SHA-256 checksum for model artifact verification."""
    if not filepath.exists():
        return "MISSING"
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

# Calculate Artifact Hashes at Startup
ARTIFACT_HASHES = {
    "model.pkl": calculate_sha256(BASE_DIR / "model.pkl"),
    "scaler.pkl": calculate_sha256(BASE_DIR / "scaler.pkl"),
    "encoder.pkl": calculate_sha256(BASE_DIR / "encoder.pkl"),
    "metadata.json": calculate_sha256(BASE_DIR / "metadata.json")
}

logger.info(f"Model Artifact Governance Hashes calculated: {ARTIFACT_HASHES}")

# Global singleton predictor instance
try:
    predictor = ChurnPredictor(
        model_path="model.pkl",
        scaler_path="scaler.pkl",
        encoder_path="encoder.pkl"
    )
    logger.info("ML Predictor initialized successfully upon module load.")
except Exception as e:
    logger.warning(f"Initial model loading failed: {e}. Artifacts will reload upon training completion.")
    predictor = None


# 2. Modern FastAPI Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    Verifies ML pipeline artifacts during startup.
    """
    global predictor
    if predictor is None or not all(predictor.is_healthy()):
        try:
            predictor = ChurnPredictor("model.pkl", "scaler.pkl", "encoder.pkl")
            logger.info("ML Predictor re-initialized during lifespan startup.")
        except Exception as e:
            logger.warning(f"Lifespan artifact load error: {e}")
    yield
    logger.info("Shutting down FastAPI application.")


# 3. Instantiate FastAPI Application
app = FastAPI(
    title="Telecom Customer Churn Prediction API",
    description=(
        "Production-ready FastAPI backend for predicting telecom customer churn probabilities "
        "using trained Machine Learning models with strict validation, telemetry, and security."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 4. Configurable CORS Security
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8501,http://127.0.0.1:8501,https://persevex-churn-predictor-ui.onrender.com,https://persevex-churn-predictor-frontend.onrender.com"
    )
)
if raw_origins.strip() == "*":
    allowed_origins = ["*"]
    allow_credentials = False
else:
    allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# 5. Security Headers & Rate Limiting Middleware
MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE_BYTES", 1048576))  # 1 MB

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    
    start_time = time.time()
    METRICS["total_requests"] += 1

    # Rate Limiting Check for POST /predict
    if request.method == "POST" and request.url.path == "/predict":
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Clean old timestamps
        timestamps = [t for t in CLIENT_REQUEST_LOGS.get(client_ip, []) if now - t < RATE_LIMIT_WINDOW]
        if len(timestamps) >= RATE_LIMIT_PER_MIN:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}", extra={"request_id": req_id})
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": f"Rate limit of {RATE_LIMIT_PER_MIN} requests per minute exceeded.",
                    "request_id": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                headers={"X-Request-ID": req_id, "Retry-After": "60"}
            )
        timestamps.append(now)
        CLIENT_REQUEST_LOGS[client_ip] = timestamps

        # Payload Content-Type Validation
        content_type = request.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            return JSONResponse(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                content={
                    "error": "Unsupported Media Type",
                    "message": "Content-Type must be 'application/json'.",
                    "request_id": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                headers={"X-Request-ID": req_id}
            )

        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": "Payload Too Large",
                    "message": f"Request body exceeds maximum allowed size of {MAX_PAYLOAD_SIZE} bytes.",
                    "request_id": req_id,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                headers={"X-Request-ID": req_id}
            )

    response = await call_next(request)
    latency = time.time() - start_time
    METRICS["total_latency_seconds"] += latency
    
    # Inject Production Security Headers
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# 6. Global Exception Handlers (Clean JSON, No Tracebacks)
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    req_id = getattr(request.state, "request_id", "N/A")
    METRICS["validation_errors"] += 1
    logger.error(f"Validation Error on {request.url}: {str(exc)}", extra={"request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": "Invalid prediction payload parameters provided.",
            "request_id": req_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        headers={"X-Request-ID": req_id}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "N/A")
    METRICS["internal_errors"] += 1
    logger.error(f"Unhandled Exception on {request.url}: {str(exc)}", exc_info=True, extra={"request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected server error occurred during processing. Please try again later.",
            "request_id": req_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        headers={"X-Request-ID": req_id}
    )


# 7. API Endpoints
@app.get(
    "/",
    summary="Root Endpoint",
    description="Returns welcome message, API version, status, and Swagger docs link."
)
async def root():
    return {
        "message": "Welcome to the Telecom Customer Churn Prediction API",
        "status": "online",
        "service": "telecom-churn-predictor-api",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get(
    "/health",
    summary="Health Check Endpoint",
    description="Diagnostics check indicating API health and status of loaded ML artifacts."
)
async def health_check():
    if predictor is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "degraded",
                "service": "telecom-churn-predictor-api",
                "model_loaded": False,
                "scaler_loaded": False,
                "encoder_loaded": False,
                "model_version": "1.0.0",
                "sha256_hashes": ARTIFACT_HASHES,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    m_ok, s_ok, e_ok = predictor.is_healthy()
    is_healthy = m_ok and s_ok and e_ok
    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_533_SERVICE_UNAVAILABLE if hasattr(status, "HTTP_533_SERVICE_UNAVAILABLE") else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if is_healthy else "degraded",
            "service": "telecom-churn-predictor-api",
            "model_loaded": m_ok,
            "scaler_loaded": s_ok,
            "encoder_loaded": e_ok,
            "model_version": "1.0.0",
            "sha256_hashes": ARTIFACT_HASHES,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.post(
    "/predict",
    response_model=ChurnPredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict Customer Churn",
    description="Accepts customer subscription features, processes inputs through pipeline, and returns churn prediction probability and risk classification."
)
async def predict_churn(request: ChurnPredictionRequest, req: Request):
    req_id = getattr(req.state, "request_id", "N/A")
    if predictor is None or not all(predictor.is_healthy()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifacts are not loaded or initialized on the server."
        )
    
    try:
        # Offload synchronous ML inference to worker thread pool
        response = await anyio.to_thread.run_sync(predictor.predict, request)
        
        METRICS["total_predictions"] += 1
        if response.prediction == "Churn":
            METRICS["churn_predictions"] += 1
        else:
            METRICS["no_churn_predictions"] += 1

        logger.info(
            f"Processed prediction for tenure={request.tenure}, Contract='{request.Contract}': {response.prediction} (prob={response.probability:.4f})",
            extra={"request_id": req_id}
        )
        return response
    except ValueError as ve:
        METRICS["validation_errors"] += 1
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prediction payload parameters provided.")
    except Exception as e:
        METRICS["internal_errors"] += 1
        logger.error(f"Inference error: {str(e)}", extra={"request_id": req_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction process failed. Please try again later.")


@app.get(
    "/metrics",
    summary="Telemetry & Observability Metrics",
    description="Returns runtime system metrics including throughput, prediction counts, latency, and error counts."
)
async def get_metrics():
    total_req = METRICS["total_requests"]
    avg_latency = (METRICS["total_latency_seconds"] / total_req) if total_req > 0 else 0.0
    return {
        "service": "telecom-churn-predictor-api",
        "telemetry": METRICS,
        "average_latency_seconds": round(avg_latency, 4),
        "sha256_hashes": ARTIFACT_HASHES,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=port, reload=False)
