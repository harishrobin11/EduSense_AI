"""FastAPI router for LLM Conversational Tutor endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.tutor_service import tutor_service
from app.schemas.tutor import (
    TutorChatRequest,
    TutorChatResponse,
    TutorHistoryResponse,
)

router = APIRouter(tags=["LLM Conversational Tutor"])


@router.post(
    "/tutor/chat",
    response_model=TutorChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat_with_ai_tutor(
    payload: TutorChatRequest, db: Session = Depends(get_db)
) -> TutorChatResponse:
    """Send message to Socratic LLM AI Tutor incorporating student risk context and target topic."""
    try:
        result = tutor_service.chat_with_tutor(
            db=db,
            student_id=payload.student_id,
            user_message=payload.message,
            topic_id=payload.topic_id,
        )
        return TutorChatResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in tutor chat: {e}",
        )


@router.get(
    "/students/{student_id}/tutor-history",
    response_model=TutorHistoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_tutor_conversation_history(
    student_id: int, db: Session = Depends(get_db)
) -> TutorHistoryResponse:
    """Retrieve historical Socratic AI tutor chat log for a student."""
    try:
        result = tutor_service.get_student_tutor_history(db=db, student_id=student_id)
        return TutorHistoryResponse(**result)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tutor history: {e}",
        )
