from fastapi import APIRouter, Request, Depends

from app.core.rate_limit import limiter
from app.core.dependencies import get_openai_key
from app.schemas.image import (
    ImageGenerationRequest,
    ImageGenerationResponse,
)
from app.services.dalle_service import generate_image


router = APIRouter(prefix="/images", tags=["images"])


@router.post(
    "/generate",
    response_model=ImageGenerationResponse,
    summary="Generate marketing image",
    description="Generate a promotional image using DALL-E",
)
@limiter.limit("3/minute")
async def generate_marketing_image(
    request: Request,
    image_request: ImageGenerationRequest,
    openai_key: str = Depends(get_openai_key),
) -> ImageGenerationResponse:
    result = await generate_image(
        prompt=image_request.prompt,
        api_key=openai_key,
        size=image_request.size,
    )
    return ImageGenerationResponse(
        success=True,
        image_url=result["image_url"],
        revised_prompt=result["revised_prompt"],
    )
