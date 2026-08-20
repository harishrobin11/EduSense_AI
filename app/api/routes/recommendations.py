"""FastAPI router for recommendation endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.recommendation_service import recommendation_service
from app.schemas.recommendations import StudentRecommendationsResponse, TopicSchema

router = APIRouter(tags=["Recommendations"])


@router.get(
    "/students/{student_id}/recommendations",
    response_model=StudentRecommendationsResponse,
    status_code=status.HTTP_200_OK,
)
def get_recommendations_for_student(
    student_id: int,
    top_n: int = Query(5, ge=1, le=20, description="Number of recommendations to return"),
    db: Session = Depends(get_db),
) -> StudentRecommendationsResponse:
    """Retrieve ranked explainable personalized recommendations for a student."""
    try:
        result = recommendation_service.get_student_recommendations(
            db=db, student_id=student_id, top_n=top_n
        )
        return StudentRecommendationsResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation error: {e}",
        )


@router.get(
    "/topics",
    response_model=List[TopicSchema],
    status_code=status.HTTP_200_OK,
)
def get_topics_catalog(db: Session = Depends(get_db)) -> List[TopicSchema]:
    """Retrieve complete topic catalog with prerequisite structures."""
    try:
        topics = recommendation_service.get_all_topics(db=db)
        return [TopicSchema(**t) for t in topics]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching topics catalog: {e}",
        )
