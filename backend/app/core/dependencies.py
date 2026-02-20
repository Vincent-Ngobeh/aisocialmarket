import re
from fastapi import Header, HTTPException, Request, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import APIException, RateLimitException, ServiceUnavailableException
from app.services import free_usage_service


settings = get_settings()


def validate_anthropic_key(key: str) -> bool:
    return bool(re.match(r'^sk-ant-[a-zA-Z0-9-_]{20,}$', key))


def validate_openai_key(key: str) -> bool:
    return bool(re.match(r'^sk-[a-zA-Z0-9-_]{20,}$', key))


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def check_free_tier_eligible(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> str:
    if not settings.free_tier_enabled:
        raise APIException(
            status_code=status.HTTP_403_FORBIDDEN,
            error="free_tier_disabled",
            detail="Free tier is currently disabled.",
        )

    if not settings.anthropic_api_key or not settings.openai_api_key:
        raise ServiceUnavailableException(
            error="free_tier_unavailable",
            detail="Free tier is not configured. Please use your own API keys.",
        )

    ip = get_client_ip(request)
    can_use = await free_usage_service.can_generate(db, ip)

    if not can_use:
        remaining = await free_usage_service.get_remaining(db, ip)
        raise RateLimitException(
            error="free_tier_limit_reached",
            detail=f"Daily free tier limit of {settings.free_tier_daily_limit} generations reached. Try again tomorrow or use your own API keys.",
            remaining=remaining,
            limit=settings.free_tier_daily_limit,
        )

    return ip


async def get_api_keys(
    x_anthropic_key: str | None = Header(None, alias="X-Anthropic-Key"),
    x_openai_key: str | None = Header(None, alias="X-OpenAI-Key"),
) -> dict:
    if not x_anthropic_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Anthropic API key required. Provide X-Anthropic-Key header.",
        )
    if not x_openai_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API key required. Provide X-OpenAI-Key header.",
        )

    if not validate_anthropic_key(x_anthropic_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Anthropic API key format. Key should start with 'sk-ant-'.",
        )

    if not validate_openai_key(x_openai_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OpenAI API key format. Key should start with 'sk-'.",
        )

    return {
        "anthropic_key": x_anthropic_key,
        "openai_key": x_openai_key,
    }


async def get_anthropic_key(
    x_anthropic_key: str | None = Header(None, alias="X-Anthropic-Key"),
) -> str:
    if not x_anthropic_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Anthropic API key required. Provide X-Anthropic-Key header.",
        )

    if not validate_anthropic_key(x_anthropic_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Anthropic API key format. Key should start with 'sk-ant-'.",
        )

    return x_anthropic_key


async def get_openai_key(
    x_openai_key: str | None = Header(None, alias="X-OpenAI-Key"),
) -> str:
    if not x_openai_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API key required. Provide X-OpenAI-Key header.",
        )

    if not validate_openai_key(x_openai_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OpenAI API key format. Key should start with 'sk-'.",
        )

    return x_openai_key
