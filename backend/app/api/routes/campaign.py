"""
Campaign routes for copy generation.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.campaign import (
    CampaignBrief,
    CopyGenerationResponse,
    ErrorResponse,
)
from app.services.claude_service import generate_copy


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
    """
    Generate social media marketing copy for a UK business.

    This endpoint uses Claude AI to generate platform-specific copy
    in British English, along with an image prompt for DALL-E.

    - **business_name**: Name of the business
    - **business_type**: Type/industry of the business
    - **target_audience**: Who the campaign is targeting
    - **campaign_goal**: What the campaign aims to achieve
    - **key_messages**: Key points to include in the copy
    - **tone**: Desired tone of voice (default: friendly and professional)
    - **platforms**: List of social media platforms to generate for
    - **include_hashtags**: Whether to include hashtags (default: true)
    - **include_emoji**: Whether to include emojis (default: true)
    - **seasonal_hook**: Optional seasonal or event tie-in
    """
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
