import re
from fastapi import Header, HTTPException, status


def validate_anthropic_key(key: str) -> bool:
    return bool(re.match(r'^sk-ant-[a-zA-Z0-9-_]{20,}$', key))


def validate_openai_key(key: str) -> bool:
    return bool(re.match(r'^sk-[a-zA-Z0-9-_]{20,}$', key))


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
