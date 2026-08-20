"""Pydantic schemas for LLM tutor endpoints."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessageSchema(BaseModel):
    role: str = Field(..., json_schema_extra={"example": "user"})  # user, assistant
    content: str = Field(..., json_schema_extra={"example": "Can you explain how thresholding works in Logistic Regression?"})
    timestamp: Optional[str] = None


class TutorChatRequest(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    message: str = Field(..., min_length=2, json_schema_extra={"example": "Can you explain how thresholding works in Logistic Regression?"})
    topic_id: Optional[int] = Field(None, json_schema_extra={"example": 12})


class TutorChatResponse(BaseModel):
    student_id: int
    student_name: str
    topic_id: Optional[int] = None
    topic_name: str
    subject: str
    struggle_risk_level: str
    recent_score: Optional[float] = None
    user_message: str
    tutor_response: str
    provider: str
    model_used: str
    chat_history: List[ChatMessageSchema]
    timestamp: str


class TutorHistoryResponse(BaseModel):
    student_id: int
    student_name: str
    total_messages: int
    chat_history: List[ChatMessageSchema]
