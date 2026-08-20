"""Health check router for FastAPI backend."""

from datetime import datetime
from fastapi import APIRouter, status
from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse, DatabaseHealth

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """Check backend service and database health."""
    db_ok = check_db_connection()
    db_type = "sqlite" if settings.is_sqlite else "postgresql"

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        version="0.1.0",
        database=DatabaseHealth(
            status="healthy" if db_ok else "unhealthy",
            database_type=db_type,
            connected=db_ok,
        ),
        timestamp=datetime.utcnow().isoformat(),
    )
