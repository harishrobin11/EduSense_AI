"""Pydantic schemas for Authentication endpoints."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Alex Taylor"})
    email: str = Field(..., json_schema_extra={"example": "alex.taylor@example.com"})
    password: str = Field(..., min_length=6, json_schema_extra={"example": "SecurePass123!"})
    role: Optional[str] = Field("student", json_schema_extra={"example": "student"})


class UserLoginRequest(BaseModel):
    email: str = Field(..., json_schema_extra={"example": "alex.taylor@example.com"})
    password: str = Field(..., json_schema_extra={"example": "SecurePass123!"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: str
