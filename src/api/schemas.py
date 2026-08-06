import math
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

class ChurnPredictionRequest(BaseModel):
    """
    Pydantic request schema for Telecom Customer Churn prediction input validation.
    Enforces strict field requirements, forbidding unexpected extra fields, validating
    non-finite float values, and ensuring exact schema contracts.
    """
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
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
    )

    gender: Literal["Female", "Male"] = Field(
        ...,
        description="Customer gender ('Female' or 'Male')"
    )
    SeniorCitizen: Literal[0, 1] = Field(
        ...,
        description="Senior citizen status (1 for Yes, 0 for No)"
    )
    Partner: Literal["Yes", "No"] = Field(
        ...,
        description="Whether customer has a partner ('Yes' or 'No')"
    )
    Dependents: Literal["Yes", "No"] = Field(
        ...,
        description="Whether customer has dependents ('Yes' or 'No')"
    )
    tenure: int = Field(
        ...,
        ge=0,
        le=120,
        description="Number of months customer has stayed with company (0 to 120)"
    )
    PhoneService: Literal["Yes", "No"] = Field(
        ...,
        description="Whether customer has phone service ('Yes' or 'No')"
    )
    MultipleLines: Literal["No phone service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has multiple lines"
    )
    InternetService: Literal["DSL", "Fiber optic", "No"] = Field(
        ...,
        description="Customer internet service provider ('DSL', 'Fiber optic', or 'No')"
    )
    OnlineSecurity: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has online security add-on"
    )
    OnlineBackup: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has online backup add-on"
    )
    DeviceProtection: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has device protection add-on"
    )
    TechSupport: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has tech support add-on"
    )
    StreamingTV: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has streaming TV add-on"
    )
    StreamingMovies: Literal["No internet service", "No", "Yes"] = Field(
        ...,
        description="Whether customer has streaming movies add-on"
    )
    Contract: Literal["Month-to-month", "One year", "Two year"] = Field(
        ...,
        description="Contract type ('Month-to-month', 'One year', 'Two year')"
    )
    PaperlessBilling: Literal["Yes", "No"] = Field(
        ...,
        description="Whether customer has paperless billing ('Yes' or 'No')"
    )
    PaymentMethod: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ] = Field(
        ...,
        description="Payment method used by customer"
    )
    MonthlyCharges: float = Field(
        ...,
        ge=0.0,
        description="Monthly charge amount in USD"
    )
    TotalCharges: float = Field(
        ...,
        ge=0.0,
        description="Total charge accumulated in USD"
    )

    @field_validator("MonthlyCharges", "TotalCharges")
    @classmethod
    def validate_finite_number(cls, value: float) -> float:
        """Ensures floating-point numeric fields do not accept NaN or Infinity."""
        if math.isnan(value) or math.isinf(value):
            raise ValueError("Numeric charges must be finite numbers (cannot be NaN or Infinity)")
        return value


class ChurnPredictionResponse(BaseModel):
    """
    Pydantic response schema for prediction endpoints.
    """
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
    timestamp: str = Field(
        description="ISO 8601 formatted prediction timestamp"
    )


class HealthResponse(BaseModel):
    """
    Pydantic health check status schema.
    """
    status: str = Field(default="healthy", description="API health status ('healthy')")
    model_loaded: bool = Field(description="Whether ML model artifact is loaded")
    scaler_loaded: bool = Field(description="Whether scaler artifact is loaded")
    encoder_loaded: bool = Field(description="Whether encoder artifact is loaded")
    timestamp: str = Field(description="ISO 8601 server timestamp")
