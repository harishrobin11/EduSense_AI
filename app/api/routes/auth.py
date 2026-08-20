"""FastAPI router for Authentication & Authorization endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, StudentProfile, UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication & JWT Authorization"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new student or instructor user account with hashed password."""
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{payload.email}' already exists.",
        )

    role_val = payload.role if payload.role in [r.value for r in UserRole] else UserRole.STUDENT.value

    # Create User
    new_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=role_val,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create default StudentProfile if student
    if role_val == UserRole.STUDENT.value:
        profile = StudentProfile(
            user_id=new_user.id,
            education_level="Undergraduate",
            goals="AI Mastery",
            preferred_difficulty="medium",
        )
        db.add(profile)
        db.commit()

    # Generate JWT Token
    access_token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        name=new_user.name,
        email=new_user.email,
        role=new_user.role,
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_user(payload: UserLoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user credentials and issue signed JWT bearer token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_authenticated_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Retrieve authenticated user details from valid JWT Bearer header."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at.isoformat() if current_user.created_at else datetime.utcnow().isoformat(),
    )
