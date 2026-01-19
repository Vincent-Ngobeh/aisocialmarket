from fastapi import APIRouter, HTTPException, status

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
async def generate_marketing_image(request: ImageGenerationRequest) -> ImageGenerationResponse:
    try:
        result = await generate_image(prompt=request.prompt, size=request.size)
        return ImageGenerationResponse(
            success=True,
            image_url=result["image_url"],
            revised_prompt=result["revised_prompt"],
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image: {str(e)}",
        )
