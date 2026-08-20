"""FastAPI router for personalization and learning path endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.personalization_service import personalization_service
from app.schemas.personalization import (
    LearningPathRequest,
    LearningPathResponse,
    QuizAttemptCreate,
    QuizAttemptResponse,
)

router = APIRouter(tags=["Personalization & Learning Paths"])


@router.post(
    "/learning-path",
    response_model=LearningPathResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_learning_path(
    payload: LearningPathRequest, db: Session = Depends(get_db)
) -> LearningPathResponse:
    """Generate a topologically sorted, step-by-step learning path for a student."""
    try:
        result = personalization_service.generate_learning_path(
            db=db,
            student_id=payload.student_id,
            target_subject=payload.target_subject,
        )
        return LearningPathResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating learning path: {e}",
        )


@router.get(
    "/students/{student_id}/learning-path",
    response_model=LearningPathResponse,
    status_code=status.HTTP_200_OK,
)
def get_student_learning_path(
    student_id: int, db: Session = Depends(get_db)
) -> LearningPathResponse:
    """Retrieve active step-by-step learning path for a student."""
    try:
        result = personalization_service.generate_learning_path(
            db=db, student_id=student_id
        )
        return LearningPathResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving learning path: {e}",
        )


@router.post(
    "/quiz-attempts",
    response_model=QuizAttemptResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_quiz_attempt(
    payload: QuizAttemptCreate, db: Session = Depends(get_db)
) -> QuizAttemptResponse:
    """Submit quiz attempt, execute adaptive difficulty adjustment, and update student profile."""
    try:
        result = personalization_service.process_quiz_attempt(
            db=db,
            student_id=payload.student_id,
            topic_id=payload.topic_id,
            score=payload.score,
            time_spent=payload.time_spent,
        )
        return QuizAttemptResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording quiz attempt: {e}",
        )
