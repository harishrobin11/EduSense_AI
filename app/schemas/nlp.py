"""Pydantic schemas for NLP feedback analysis endpoints."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FeedbackAnalysisRequest(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    text: str = Field(..., min_length=3, json_schema_extra={"example": "The explanation of logistic regression pace was a bit too fast, but the practice problems were great!"})
    topic_id: Optional[int] = Field(None, json_schema_extra={"example": 12})


class FeedbackAnalysisResponse(BaseModel):
    feedback_id: int
    student_id: int
    student_name: str
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    original_text: str
    cleaned_text: str
    sentiment_score: float = Field(..., json_schema_extra={"example": 0.45})
    sentiment_label: str = Field(..., json_schema_extra={"example": "positive"})  # positive, neutral, negative
    keywords_extracted: List[str] = Field(default=[], json_schema_extra={"example": ["logistic regression", "fast pace", "great practice"]})
    submitted_at: str


class FeedbackItemSchema(BaseModel):
    feedback_id: int
    topic_id: Optional[int] = None
    text: str
    sentiment_score: float
    sentiment_label: str
    timestamp: str


class StudentSentimentSummaryResponse(BaseModel):
    student_id: int
    student_name: str
    total_feedback_count: int
    average_sentiment_score: float
    overall_sentiment_status: str  # positive, neutral, negative
    sentiment_breakdown: Dict[str, int]  # {"positive": X, "neutral": Y, "negative": Z}
    recurring_themes: List[str]
    recent_feedbacks: List[FeedbackItemSchema]
