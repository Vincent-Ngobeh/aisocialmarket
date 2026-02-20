from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

def _cors_headers(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "")
    settings = get_settings()
    if origin in settings.cors_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {}

async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": "rate_limit_exceeded",
            "detail": f"Too many requests. Limit: {exc.detail}. Please wait before trying again.",
            "retry_after": 60,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if request.app.debug else "An unexpected error occurred",
        },
    )
