import os
import sys
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure local module path resolution
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.api.schemas import ChurnPredictionRequest, ChurnPredictionResponse, HealthResponse
from src.api.inference import ChurnPredictor

# 1. Configure Logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
logger = logging.getLogger("FastAPIApp")

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
        "using trained Machine Learning models (Logistic Regression / XGBoost / Random Forest)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 4. Configurable CORS Security
raw_origins = os.getenv("CORS_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 5. Global Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    logger.error(f"Validation Error on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred during prediction processing.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# 6. API Endpoints
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
    return HealthResponse(
        status="ok" if (m_ok and s_ok and e_ok) else "degraded",
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
async def predict_churn(request: ChurnPredictionRequest):
    if predictor is None or not all(predictor.is_healthy()):
        raise HTTPException(
            status_code=status.HTTP_533_SERVICE_UNAVAILABLE if hasattr(status, "HTTP_533_SERVICE_UNAVAILABLE") else 503,
            detail="Model artifacts are not loaded or initialized on the server."
        )
    
    try:
        response = predictor.predict(request)
        logger.info(f"Processed prediction for tenure={request.tenure}, Contract='{request.Contract}': {response.prediction} (prob={response.probability})")
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction process failed.")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
