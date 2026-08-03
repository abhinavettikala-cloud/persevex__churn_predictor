from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Dict, Any
from datetime import datetime

class ChurnPredictionRequest(BaseModel):
    """
    Pydantic request schema for Telecom Customer Churn prediction input validation.
    Enforces strict field types, value constraints, and provides Swagger documentation examples.
    """
    gender: Literal["Female", "Male"] = Field(
        default="Female",
        description="Customer gender ('Female' or 'Male')"
    )
    SeniorCitizen: Literal[0, 1] = Field(
        default=0,
        description="Senior citizen status (1 for Yes, 0 for No)"
    )
    Partner: Literal["Yes", "No"] = Field(
        default="Yes",
        description="Whether customer has a partner ('Yes' or 'No')"
    )
    Dependents: Literal["Yes", "No"] = Field(
        default="No",
        description="Whether customer has dependents ('Yes' or 'No')"
    )
    tenure: int = Field(
        default=12,
        ge=0,
        le=120,
        description="Number of months customer has stayed with company (0 to 120)"
    )
    PhoneService: Literal["Yes", "No"] = Field(
        default="Yes",
        description="Whether customer has phone service ('Yes' or 'No')"
    )
    MultipleLines: Literal["No phone service", "No", "Yes"] = Field(
        default="No",
        description="Whether customer has multiple lines"
    )
    InternetService: Literal["DSL", "Fiber optic", "No"] = Field(
        default="Fiber optic",
        description="Customer internet service provider ('DSL', 'Fiber optic', or 'No')"
    )
    OnlineSecurity: Literal["No internet service", "No", "Yes"] = Field(
        default="No",
        description="Whether customer has online security add-on"
    )
    OnlineBackup: Literal["No internet service", "No", "Yes"] = Field(
        default="Yes",
        description="Whether customer has online backup add-on"
    )
    DeviceProtection: Literal["No internet service", "No", "Yes"] = Field(
        default="No",
        description="Whether customer has device protection add-on"
    )
    TechSupport: Literal["No internet service", "No", "Yes"] = Field(
        default="No",
        description="Whether customer has tech support add-on"
    )
    StreamingTV: Literal["No internet service", "No", "Yes"] = Field(
        default="Yes",
        description="Whether customer has streaming TV add-on"
    )
    StreamingMovies: Literal["No internet service", "No", "Yes"] = Field(
        default="No",
        description="Whether customer has streaming movies add-on"
    )
    Contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        default="Month-to-month",
        description="Contract type ('Month-to-month', 'One year', 'Two year')"
    )
    PaperlessBilling: Literal["Yes", "No"] = Field(
        default="Yes",
        description="Whether customer has paperless billing ('Yes' or 'No')"
    )
    PaymentMethod: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ] = Field(
        default="Electronic check",
        description="Payment method used by customer"
    )
    MonthlyCharges: float = Field(
        default=70.35,
        ge=0.0,
        description="Monthly charge amount in USD"
    )
    TotalCharges: float = Field(
        default=844.20,
        ge=0.0,
        description="Total charge accumulated in USD"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
                "MonthlyCharges": 85.00,
                "TotalCharges": 85.00
            }
        }
    }


class ChurnPredictionResponse(BaseModel):
    """
    Pydantic response schema for prediction endpoints with explainability metadata.
    """
    id: Optional[str] = Field(default=None, description="Unique prediction record identifier")
    prediction: Literal["Churn", "No Churn"] = Field(
        description="Predicted churn category ('Churn' or 'No Churn')"
    )
    churn_label: int = Field(
        description="Binary label (1 for Churn, 0 for No Churn)"
    )
    probability: float = Field(
        description="Probability of customer churning (0.0 to 1.0)"
    )
    confidence_score: float = Field(
        description="Model confidence score for predicted class (0.5 to 1.0)"
    )
    risk_level: Literal["Low", "Medium", "High"] = Field(
        description="Churn risk tier based on probability threshold ('Low', 'Medium', 'High')"
    )
    execution_time_ms: Optional[float] = Field(default=12.5, description="Inference latency in milliseconds")
    model_version: Optional[str] = Field(default="v1.0.0-LogisticRegression", description="Trained model version tag")
    timestamp: str = Field(
        description="ISO 8601 formatted prediction timestamp"
    )
    top_positive_factors: Optional[List[Dict[str, str]]] = Field(default=[], description="Factors driving churn risk higher")
    top_negative_factors: Optional[List[Dict[str, str]]] = Field(default=[], description="Factors protecting against churn")
    explanation_text: Optional[str] = Field(default="", description="Plain English rule-based explanation summary")


class HealthResponse(BaseModel):
    """
    Pydantic health check status schema.
    """
    status: str = Field(default="ok", description="API health status ('ok')")
    model_loaded: bool = Field(description="Whether ML model artifact is loaded")
    scaler_loaded: bool = Field(description="Whether scaler artifact is loaded")
    encoder_loaded: bool = Field(description="Whether encoder artifact is loaded")
    timestamp: str = Field(description="ISO 8601 server timestamp")


class DashboardStatsResponse(BaseModel):
    total_predictions: int
    today_predictions: int
    churn_predictions: int
    non_churn_predictions: int
    avg_confidence: float
    avg_response_time_ms: float
    model_version: str
    api_status: str
    recent_trends: List[Dict[str, Any]]


class HistoryResponse(BaseModel):
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int


class AnalyticsSummaryResponse(BaseModel):
    contract_distribution: Dict[str, int]
    internet_distribution: Dict[str, int]
    payment_distribution: Dict[str, int]
    risk_metrics: Dict[str, Any]


class ModelPerformanceResponse(BaseModel):
    model_name: str
    algorithm: str
    version: str
    training_date: str
    dataset_name: str
    training_samples: int
    testing_samples: int
    number_of_features: int
    model_size: str
    training_time_seconds: float
    avg_inference_time_ms: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    log_loss: float
    cross_val_score: float
    model_comparison: List[Dict[str, Any]]
    best_model_name: str
    selection_rationale: str


class SystemStatusResponse(BaseModel):
    api_status: str
    backend_status: str
    model_status: str
    database_status: str
    current_model_version: str
    last_prediction_time: str
    average_response_time_ms: float
    application_uptime_hours: float
