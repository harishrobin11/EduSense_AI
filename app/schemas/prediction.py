"""Pydantic schemas for struggle prediction API endpoints."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class StrugglePredictionRequest(BaseModel):
    student_id: Optional[int] = Field(None, json_schema_extra={"example": 1})
    topic_id: Optional[int] = Field(None, json_schema_extra={"example": 12})
    
    # Optional raw feature overrides
    recent_quiz_score: Optional[float] = Field(None, json_schema_extra={"example": 62.5})
    historical_topic_score: Optional[float] = Field(None, json_schema_extra={"example": 68.0})
    attempts_count: Optional[int] = Field(None, json_schema_extra={"example": 2})
    total_time_spent: Optional[int] = Field(None, json_schema_extra={"example": 350})
    prerequisite_completion_rate: Optional[float] = Field(None, json_schema_extra={"example": 0.5})
    score_trend: Optional[float] = Field(None, json_schema_extra={"example": -5.5})
    engagement_frequency: Optional[int] = Field(None, json_schema_extra={"example": 4})
    topic_difficulty_numeric: Optional[int] = Field(None, json_schema_extra={"example": 2})
    model_type: Optional[str] = Field("random_forest", json_schema_extra={"example": "pytorch_nn"})


class StrugglePredictionResponse(BaseModel):
    struggle_probability: float = Field(..., json_schema_extra={"example": 0.725})
    is_struggling: bool = Field(..., json_schema_extra={"example": True})
    risk_level: str = Field(..., json_schema_extra={"example": "high"})
    risk_factors: List[str] = Field(default=[], json_schema_extra={"example": ["Low recent quiz score (62.5%)"]})
    features_used: Optional[Dict[str, Any]] = None
    model_version: str = Field(..., json_schema_extra={"example": "v1.0.0"})


class ModelRunMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    brier_score: float
    confusion_matrix: List[List[int]]


class ModelMetadataResponse(BaseModel):
    model_name: str = Field(..., json_schema_extra={"example": "RandomForestClassifier"})
    version: str = Field(..., json_schema_extra={"example": "v1.0.0"})
    trained_at: str = Field(..., json_schema_extra={"example": "2026-08-19 22:30:00"})
    feature_names: List[str]
    metrics_test: ModelRunMetrics
    metrics_baseline_logistic_regression: ModelRunMetrics
    feature_importances: Dict[str, float]
