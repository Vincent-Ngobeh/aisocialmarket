import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.exceptions import APIException

logger = logging.getLogger(__name__)


def _cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "")
    settings = get_settings()
    if origin in settings.cors_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Return APIException detail dict directly as the response body,
    avoiding FastAPI's default wrapping under a 'detail' key."""
    content = exc.detail if isinstance(exc.detail, dict) else {
        "success": False,
        "error": "error",
        "detail": str(exc.detail),
    }
    return JSONResponse(
        status_code=exc.status_code,
        headers=_cors_headers(request),
        content=content,
    )


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        headers=_cors_headers(request),
        content={
            "success": False,
            "error": "rate_limit_exceeded",
            "detail": f"Too many requests. Limit: {exc.detail}. Please wait before trying again.",
            "retry_after": 60,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s: %s: %s",
        request.method,
        request.url.path,
        type(exc).__name__,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        headers=_cors_headers(request),
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if request.app.debug else "An unexpected error occurred",
        },
    )
