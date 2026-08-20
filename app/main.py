"""FastAPI application entrypoint for EduSense AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db
from app.api.routes import health, prediction, recommendations, personalization, nlp, tutor, quiz, auth
from app.core.middleware import RequestIDMiddleware, RateLimiterMiddleware, global_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    init_db()
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Personalized Learning & Student Intelligence SaaS API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Custom Exception Handler
app.add_exception_handler(Exception, global_exception_handler)

# Configure Middlewares
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(prediction.router)
app.include_router(recommendations.router)
app.include_router(personalization.router)
app.include_router(nlp.router)
app.include_router(tutor.router)
app.include_router(quiz.router)


@app.api_route("/", methods=["GET", "HEAD"])
def root():
    """Root endpoint redirecting to docs or health summary."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health",
        "version": "0.1.0",
    }
