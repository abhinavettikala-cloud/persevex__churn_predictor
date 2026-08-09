import os
import sys
import uuid
import time
import logging
import anyio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure local module path resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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
    lifespan=lifespan
)

# 4. Configurable CORS Security
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8501")
if raw_origins.strip() == "*":
    allowed_origins = ["*"]
    allow_credentials = False  # Security fix: Never combine wildcard origins with credentials
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


# 5. Custom Middleware: Request ID, Correlation Tracking & Body Size Limit
MAX_PAYLOAD_SIZE = int(os.getenv("MAX_PAYLOAD_SIZE_BYTES", 1048576))  # 1 MB

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = req_id
    
    start_time = time.time()
    METRICS["total_requests"] += 1

    # Check Content-Type for POST prediction requests
    if request.method == "POST" and request.url.path == "/predict":
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
    response.headers["X-Request-ID"] = req_id
    return response


# 6. Global Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    req_id = getattr(request.state, "request_id", "N/A")
    METRICS["validation_errors"] += 1
    logger.error(f"Validation Error on {request.url}: {str(exc)}", extra={"request_id": req_id})
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
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
            "message": "An unexpected error occurred during processing.",
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
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check Endpoint",
    description="Diagnostics check indicating API health and status of loaded ML artifacts."
)
async def health_check():
    if predictor is None:
        return HealthResponse(
            status="degraded",
            model_loaded=False,
            scaler_loaded=False,
            encoder_loaded=False,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    m_ok, s_ok, e_ok = predictor.is_healthy()
    is_healthy = m_ok and s_ok and e_ok
    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        model_loaded=m_ok,
        scaler_loaded=s_ok,
        encoder_loaded=e_ok,
        timestamp=datetime.now(timezone.utc).isoformat()
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
        # Offload synchronous ML inference to worker thread pool to prevent blocking asyncio event loop
        response = await anyio.to_thread.run_sync(predictor.predict, request)
        
        METRICS["total_predictions"] += 1
        if response.prediction == "Churn":
            METRICS["churn_predictions"] += 1
        else:
            METRICS["no_churn_predictions"] += 1

        logger.info(
            f"Processed prediction for tenure={request.tenure}, Contract='{request.Contract}': {response.prediction} (prob={response.probability})",
            extra={"request_id": req_id}
        )
        return response
    except ValueError as ve:
        METRICS["validation_errors"] += 1
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        METRICS["internal_errors"] += 1
        logger.error(f"Inference error: {str(e)}", extra={"request_id": req_id})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction process failed.")


@app.get(
    "/metrics",
    summary="Telemetry & Observability Metrics",
    description="Returns runtime system metrics including throughput, prediction counts, latency, and error counts."
)
async def get_metrics():
    total_req = METRICS["total_requests"]
    avg_latency = (METRICS["total_latency_seconds"] / total_req) if total_req > 0 else 0.0
    return {
        "telemetry": METRICS,
        "average_latency_seconds": round(avg_latency, 4),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=port, reload=False)
