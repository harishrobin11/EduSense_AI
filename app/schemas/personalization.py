"""Pydantic schemas for personalization and learning path endpoints."""

from typing import List, Optional
from pydantic import BaseModel, Field


class LearningPathRequest(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    target_subject: Optional[str] = Field(None, json_schema_extra={"example": "Machine Learning"})


class LearningPathStepSchema(BaseModel):
    step_number: int
    topic_id: int
    subject: str
    topic_name: str
    difficulty: str
    prerequisites: List[str]
    status: str = Field(..., json_schema_extra={"example": "completed"})  # completed, in_progress, locked
    best_score: Optional[float] = None
    estimated_minutes: int


class LearningPathResponse(BaseModel):
    student_id: int
    student_name: str
    target_goal: str
    current_preferred_difficulty: str
    total_steps: int
    completed_steps: int
    completion_percentage: float
    estimated_total_hours: float
    steps: List[LearningPathStepSchema]
    generated_at: str


class QuizAttemptCreate(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    topic_id: int = Field(..., json_schema_extra={"example": 12})
    score: float = Field(..., ge=0.0, le=100.0, json_schema_extra={"example": 88.5})
    time_spent: int = Field(..., ge=1, json_schema_extra={"example": 320})


class QuizAttemptResponse(BaseModel):
    student_id: int
    topic_id: int
    topic_name: str
    score: float
    attempt_number: int
    previous_difficulty: str
    new_difficulty: str
    adaptive_reason: str
    difficulty_changed: bool
    recorded_at: str
