"""FastAPI router for ML prediction endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.prediction_service import prediction_service
from app.schemas.prediction import (
    StrugglePredictionRequest,
    StrugglePredictionResponse,
    ModelMetadataResponse,
)

router = APIRouter(tags=["ML Prediction"])


@router.post("/predict/struggle", response_model=StrugglePredictionResponse, status_code=status.HTTP_200_OK)
def predict_struggle(
    payload: StrugglePredictionRequest,
    db: Session = Depends(get_db),
) -> StrugglePredictionResponse:
    """Predict whether a student is likely to struggle with a target learning topic."""
    # Option 1: Predict from explicit raw features provided in payload
    if payload.recent_quiz_score is not None:
        result = prediction_service.predict_from_features(
            recent_quiz_score=payload.recent_quiz_score,
            historical_topic_score=payload.historical_topic_score if payload.historical_topic_score is not None else 70.0,
            attempts_count=payload.attempts_count if payload.attempts_count is not None else 1,
            total_time_spent=payload.total_time_spent if payload.total_time_spent is not None else 120,
            prerequisite_completion_rate=payload.prerequisite_completion_rate if payload.prerequisite_completion_rate is not None else 1.0,
            score_trend=payload.score_trend if payload.score_trend is not None else 0.0,
            engagement_frequency=payload.engagement_frequency if payload.engagement_frequency is not None else 5,
            topic_difficulty_numeric=payload.topic_difficulty_numeric if payload.topic_difficulty_numeric is not None else 2,
            model_type=payload.model_type or "random_forest",
        )
        return StrugglePredictionResponse(**result)

    # Option 2: Predict dynamically by looking up student_id and topic_id in DB
    if payload.student_id is not None and payload.topic_id is not None:
        try:
            result = prediction_service.predict_from_db(
                db=db,
                student_id=payload.student_id,
                topic_id=payload.topic_id,
                model_type=payload.model_type or "random_forest",
            )
            return StrugglePredictionResponse(**result)
        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Prediction error: {e}")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Must provide either (student_id and topic_id) or explicit raw features (recent_quiz_score, etc.).",
    )


@router.get("/models", response_model=ModelMetadataResponse, status_code=status.HTTP_200_OK)
def get_model_metadata() -> ModelMetadataResponse:
    """Retrieve metadata, version history, and evaluation metrics for active ML models."""
    metadata = prediction_service.get_model_metadata()
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics metadata file not found. Please train models first.",
        )
    return ModelMetadataResponse(**metadata)
