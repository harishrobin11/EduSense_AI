"""Pydantic schemas for health endpoint."""

from typing import Dict, Any
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    database_type: str = Field(..., json_schema_extra={"example": "sqlite"})
    connected: bool = Field(..., json_schema_extra={"example": True})


class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app_name: str = Field(..., json_schema_extra={"example": "EduSense AI"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})
    database: DatabaseHealth
    timestamp: str
