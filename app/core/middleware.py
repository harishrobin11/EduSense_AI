"""Production middleware: Request ID injection, rate-limiting, and exception handling."""

import uuid
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import logger

# Sliding window rate limiter state: IP -> list of timestamps
REQUEST_TIMESTAMPS: Dict[str, List[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60.0  # 60 seconds
RATE_LIMIT_MAX_REQUESTS = 120  # Max 120 requests per minute per IP


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware injecting X-Request-ID UUID into every request state and response header."""

    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window IP rate limiting middleware."""

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Clean timestamps older than window
        timestamps = REQUEST_TIMESTAMPS[client_ip]
        REQUEST_TIMESTAMPS[client_ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]

        if len(REQUEST_TIMESTAMPS[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Maximum 120 requests per minute allowed.",
                    "status_code": 429,
                },
                headers={"Retry-After": "60"},
            )

        REQUEST_TIMESTAMPS[client_ip].append(now)
        response = await call_next(request)
        return response


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler converting uncaught exceptions into clean JSON error envelopes."""
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Uncaught Server Exception [ReqID: {req_id}]: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error occurred.",
            "error_type": type(exc).__name__,
            "request_id": req_id,
            "status_code": 500,
        },
    )
