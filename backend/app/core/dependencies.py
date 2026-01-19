from fastapi import Header, HTTPException, status


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
    return x_anthropic_key


async def get_openai_key(
    x_openai_key: str | None = Header(None, alias="X-OpenAI-Key"),
) -> str:
    if not x_openai_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API key required. Provide X-OpenAI-Key header.",
        )
    return x_openai_key
