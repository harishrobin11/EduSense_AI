"""Pydantic schemas for recommendation API endpoints."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class LearningResourceSchema(BaseModel):
    id: int
    type: str = Field(..., json_schema_extra={"example": "video"})
    title: str = Field(..., json_schema_extra={"example": "Deep Dive: Logistic Regression Lecture"})
    url_or_path: Optional[str] = Field(None, json_schema_extra={"example": "https://edusense.ai/learn/12/video"})
    difficulty: str = Field(..., json_schema_extra={"example": "medium"})


class RecommendationItemSchema(BaseModel):
    topic_id: int = Field(..., json_schema_extra={"example": 11})
    subject: str = Field(..., json_schema_extra={"example": "Machine Learning"})
    topic_name: str = Field(..., json_schema_extra={"example": "Linear Regression"})
    difficulty: str = Field(..., json_schema_extra={"example": "easy"})
    score: float = Field(..., json_schema_extra={"example": 85.0})
    reason: str = Field(..., json_schema_extra={"example": "Foundational prerequisite recommended before attempting Logistic Regression"})
    is_weak_topic: bool = Field(..., json_schema_extra={"example": False})
    prerequisite_ready: bool = Field(..., json_schema_extra={"example": True})
    unmet_prerequisites: List[str] = Field(default=[], json_schema_extra={"example": []})
    resources: List[LearningResourceSchema] = Field(default=[])


class StudentRecommendationsResponse(BaseModel):
    student_id: int = Field(..., json_schema_extra={"example": 1})
    student_name: str = Field(..., json_schema_extra={"example": "Alex Smith"})
    preferred_difficulty: str = Field(..., json_schema_extra={"example": "medium"})
    weak_topics_detected: List[str] = Field(default=[], json_schema_extra={"example": ["Logistic Regression"]})
    recommendations: List[RecommendationItemSchema]
    generated_at: str


class TopicSchema(BaseModel):
    id: int = Field(..., json_schema_extra={"example": 1})
    subject: str = Field(..., json_schema_extra={"example": "Python Programming"})
    name: str = Field(..., json_schema_extra={"example": "Variables & Data Types"})
    difficulty: str = Field(..., json_schema_extra={"example": "easy"})
    prerequisites: List[int] = Field(default=[], json_schema_extra={"example": []})
