from fastapi import APIRouter, HTTPException, status

from app.schemas.campaign import (
    CampaignBrief,
    CopyGenerationResponse,
    ErrorResponse,
)
from app.schemas.image import CampaignFullResponse
from app.services.claude_service import generate_copy
from app.services.dalle_service import generate_image


router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    "/generate-copy",
    response_model=CopyGenerationResponse,
    responses={
        200: {"description": "Copy generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Generate social media copy",
    description="Generate British English social media marketing copy using AI",
)
async def generate_campaign_copy(brief: CampaignBrief) -> CopyGenerationResponse:
    try:
        result = await generate_copy(brief)
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate copy: {str(e)}",
        )


@router.post(
    "/generate-full",
    response_model=CampaignFullResponse,
    responses={
        200: {"description": "Campaign generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Generate full campaign",
    description="Generate social media copy and promotional image",
)
async def generate_full_campaign(brief: CampaignBrief) -> CampaignFullResponse:
    try:
        copy_result = await generate_copy(brief)

        image_result = None
        image_url = None
        revised_prompt = None

        try:
            image_result = await generate_image(prompt=copy_result.image_prompt)
            image_url = image_result["image_url"]
            revised_prompt = image_result["revised_prompt"]
        except ValueError:
            pass

        return CampaignFullResponse(
            success=True,
            business_name=copy_result.business_name,
            copies=[c.model_dump() for c in copy_result.copies],
            image_prompt=copy_result.image_prompt,
            image_url=image_url,
            revised_image_prompt=revised_prompt,
            message="Campaign generated successfully" if image_url else "Copy generated, image generation failed",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate campaign: {str(e)}",
        )
