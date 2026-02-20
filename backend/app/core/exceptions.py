from fastapi import HTTPException, status


class APIException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error: str,
        detail: str | None = None,
        **extra,
    ):
        body = {
            "success": False,
            "error": error,
            "detail": detail,
            **extra,
        }
        super().__init__(
            status_code=status_code,
            detail=body,
        )


class BadRequestException(APIException):
    def __init__(self, error: str, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=error,
            detail=detail,
        )


class NotFoundException(APIException):
    def __init__(self, error: str = "Resource not found", detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error=error,
            detail=detail,
        )


class RateLimitException(APIException):
    def __init__(self, error: str = "rate_limit_exceeded", detail: str | None = None, **extra):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error=error,
            detail=detail or "Please wait before making another request",
            **extra,
        )


class ServiceUnavailableException(APIException):
    def __init__(self, error: str, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error=error,
            detail=detail,
        )


class AIServiceException(APIException):
    def __init__(self, service: str, detail: str | None = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            error=f"{service} service error",
            detail=detail,
        )
