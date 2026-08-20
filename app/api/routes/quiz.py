"""FastAPI router for AI Quiz Generator & Closed Learning Loop endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.quiz_service import quiz_service
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizGenerateResponse,
    QuizSubmitRequest,
    QuizSubmitResponse,
)

router = APIRouter(tags=["AI Quiz Generator & Closed Learning Loop"])


@router.post(
    "/quiz/generate",
    response_model=QuizGenerateResponse,
    status_code=status.HTTP_200_OK,
)
def generate_topic_quiz(
    payload: QuizGenerateRequest, db: Session = Depends(get_db)
) -> QuizGenerateResponse:
    """Generate dynamic multiple-choice quiz questions tailored to student target difficulty."""
    try:
        result = quiz_service.generate_quiz_session(
            db=db,
            student_id=payload.student_id,
            topic_id=payload.topic_id,
            question_count=payload.question_count or 3,
        )
        return QuizGenerateResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating quiz: {e}",
        )


@router.post(
    "/quiz/submit",
    response_model=QuizSubmitResponse,
    status_code=status.HTTP_200_OK,
)
def submit_quiz_and_trigger_closed_loop(
    payload: QuizSubmitRequest, db: Session = Depends(get_db)
) -> QuizSubmitResponse:
    """Evaluate student quiz answers, score percentage, and trigger closed learning loop state updates."""
    try:
        result = quiz_service.submit_quiz_and_run_closed_loop(
            db=db,
            student_id=payload.student_id,
            topic_id=payload.topic_id,
            quiz_session_id=payload.quiz_session_id,
            user_answers=payload.answers,
            time_spent=payload.time_spent or 180,
        )
        return QuizSubmitResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating quiz submission: {e}",
        )
