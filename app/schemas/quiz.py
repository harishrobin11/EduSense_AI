"""Pydantic schemas for AI Quiz Generator & Closed Learning Loop endpoints."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class QuizGenerateRequest(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    topic_id: int = Field(..., json_schema_extra={"example": 12})
    question_count: Optional[int] = Field(3, ge=1, le=10, json_schema_extra={"example": 3})


class QuizQuestionStudentSchema(BaseModel):
    question_id: int
    question_text: str
    options: List[str]


class QuizGenerateResponse(BaseModel):
    quiz_session_id: str
    student_id: int
    student_name: str
    topic_id: int
    topic_name: str
    subject: str
    difficulty: str
    question_count: int
    questions: List[QuizQuestionStudentSchema]
    generated_at: str


class QuizSubmitRequest(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    topic_id: int = Field(..., json_schema_extra={"example": 12})
    quiz_session_id: str = Field(..., json_schema_extra={"example": "quiz_1_12_1700000000"})
    answers: List[int] = Field(..., json_schema_extra={"example": [0, 0, 0]})
    time_spent: Optional[int] = Field(180, ge=1, json_schema_extra={"example": 180})


class QuestionBreakdownSchema(BaseModel):
    question_id: int
    question_text: str
    user_selected_index: int
    user_selected_option: str
    correct_option_index: int
    correct_option_text: str
    is_correct: bool
    explanation: str


class ClosedLoopUpdatesSchema(BaseModel):
    quiz_attempt_recorded: bool
    struggle_risk_level: str
    struggle_probability: float
    previous_difficulty: str
    new_difficulty: str
    adaptive_reason: str
    difficulty_changed: bool
    learning_path_updated: bool
    learning_path_completion_pct: float


class QuizSubmitResponse(BaseModel):
    quiz_session_id: str
    student_id: int
    topic_id: int
    topic_name: str
    score_percentage: float
    correct_answers: int
    total_questions: int
    is_passed: bool
    question_breakdown: List[QuestionBreakdownSchema]
    closed_loop_updates: ClosedLoopUpdatesSchema
    evaluated_at: str
