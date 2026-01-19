from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.campaign import (
    CampaignBrief,
    CopyGenerationResponse,
    ErrorResponse,
    CampaignRecord,
    CampaignListResponse,
)
from app.schemas.image import CampaignFullResponse
from app.services.claude_service import generate_copy
from app.services.dalle_service import generate_image
from app.services import campaign_service


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
    summary="Generate full campaign with image",
)
async def generate_full_campaign(
    brief: CampaignBrief,
    save: bool = Query(default=True, description="Save campaign to database"),
    db: AsyncSession = Depends(get_db),
) -> CampaignFullResponse:
    try:
        copy_result = await generate_copy(brief)

        image_url = None
        revised_prompt = None

        try:
            image_result = await generate_image(prompt=copy_result.image_prompt)
            image_url = image_result["image_url"]
            revised_prompt = image_result["revised_prompt"]
        except ValueError:
            pass

        if save:
            await campaign_service.save_campaign(
                db=db,
                brief=brief,
                copies=copy_result.copies,
                image_prompt=copy_result.image_prompt,
                image_url=image_url,
            )

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


@router.get(
    "/",
    response_model=CampaignListResponse,
    summary="List saved campaigns",
)
async def list_campaigns(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CampaignListResponse:
    try:
        campaigns, total = await campaign_service.get_campaigns(db, skip, limit)
        return CampaignListResponse(
            success=True,
            campaigns=[CampaignRecord.model_validate(c) for c in campaigns],
            total=total,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch campaigns: {str(e)}",
        )


@router.get(
    "/{campaign_id}",
    response_model=CampaignRecord,
    summary="Get campaign by ID",
)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> CampaignRecord:
    campaign = await campaign_service.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    return CampaignRecord.model_validate(campaign)
