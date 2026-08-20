"""FastAPI router for NLP feedback analysis endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.nlp_service import nlp_service
from app.schemas.nlp import (
    FeedbackAnalysisRequest,
    FeedbackAnalysisResponse,
    StudentSentimentSummaryResponse,
)

router = APIRouter(tags=["NLP & Student Feedback Analysis"])


@router.post(
    "/feedback/analyze",
    response_model=FeedbackAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
def analyze_student_feedback(
    payload: FeedbackAnalysisRequest, db: Session = Depends(get_db)
) -> FeedbackAnalysisResponse:
    """Analyze student feedback text, score sentiment, extract key themes, and save to database."""
    try:
        result = nlp_service.process_and_save_feedback(
            db=db,
            student_id=payload.student_id,
            text=payload.text,
            topic_id=payload.topic_id,
        )
        return FeedbackAnalysisResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing feedback: {e}",
        )


@router.get(
    "/students/{student_id}/sentiment",
    response_model=StudentSentimentSummaryResponse,
    status_code=status.HTTP_200_OK,
)
def get_student_sentiment_analytics(
    student_id: int, db: Session = Depends(get_db)
) -> StudentSentimentSummaryResponse:
    """Retrieve historical sentiment analytics, sentiment breakdown, and recurring themes for a student."""
    try:
        result = nlp_service.get_student_sentiment_summary(db=db, student_id=student_id)
        return StudentSentimentSummaryResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving sentiment analytics: {e}",
        )
