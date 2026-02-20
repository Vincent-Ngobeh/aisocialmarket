from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.exceptions import NotFoundException
from app.core.dependencies import get_api_keys, get_anthropic_key, get_client_ip, check_free_tier_eligible
from app.schemas.campaign import (
    CampaignBrief,
    CopyGenerationResponse,
    ErrorResponse,
    CampaignRecord,
    CampaignListResponse,
    FreeTierStatusResponse,
)
from app.schemas.image import CampaignFullResponse
from app.services.claude_service import generate_copy
from app.services.dalle_service import generate_image
from app.services import campaign_service, free_usage_service


settings = get_settings()
router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.post(
    "/generate-copy",
    response_model=CopyGenerationResponse,
    responses={
        200: {"description": "Copy generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "API key required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Generate social media copy",
)
@limiter.limit("5/minute")
async def generate_campaign_copy(
    request: Request,
    brief: CampaignBrief,
    anthropic_key: str = Depends(get_anthropic_key),
) -> CopyGenerationResponse:
    return await generate_copy(brief, anthropic_key)


@router.post(
    "/generate-full",
    response_model=CampaignFullResponse,
    responses={
        200: {"description": "Campaign generated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        401: {"model": ErrorResponse, "description": "API keys required"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    summary="Generate full campaign with image",
)
@limiter.limit("3/minute")
async def generate_full_campaign(
    request: Request,
    brief: CampaignBrief,
    api_keys: dict = Depends(get_api_keys),
    save: bool = Query(default=True, description="Save campaign to database"),
    db: AsyncSession = Depends(get_db),
) -> CampaignFullResponse:
    copy_result = await generate_copy(brief, api_keys["anthropic_key"])

    image_url = None
    revised_prompt = None

    try:
        image_result = await generate_image(
            prompt=copy_result.image_prompt,
            api_key=api_keys["openai_key"],
        )
        image_url = image_result["image_url"]
        revised_prompt = image_result["revised_prompt"]
    except Exception:
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


@router.post(
    "/generate-free",
    response_model=CampaignFullResponse,
    responses={
        200: {"description": "Campaign generated with free tier"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        429: {"model": ErrorResponse, "description": "Free tier limit reached"},
        503: {"model": ErrorResponse, "description": "Free tier unavailable"},
    },
    summary="Generate full campaign using free tier",
)
@limiter.limit("5/minute")
async def generate_free_campaign(
    request: Request,
    brief: CampaignBrief,
    generate_image_flag: bool = Query(default=False, alias="generate_image"),
    ip: str = Depends(check_free_tier_eligible),
    db: AsyncSession = Depends(get_db),
) -> CampaignFullResponse:
    copy_result = await generate_copy(brief, settings.anthropic_api_key)

    image_url = None
    revised_prompt = None

    if generate_image_flag:
        try:
            image_result = await generate_image(
                prompt=copy_result.image_prompt,
                api_key=settings.openai_api_key,
            )
            image_url = image_result["image_url"]
            revised_prompt = image_result["revised_prompt"]
        except Exception:
            pass

    await free_usage_service.increment_usage(db, ip)
    remaining = await free_usage_service.get_remaining(db, ip)

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
        message=f"Campaign generated successfully ({remaining} free generations remaining today)"
        if image_url
        else f"Copy generated, image generation failed ({remaining} free generations remaining today)",
    )


@router.get(
    "/free-tier-status",
    response_model=FreeTierStatusResponse,
    summary="Check free tier usage status",
)
@limiter.limit("30/minute")
async def free_tier_status(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> FreeTierStatusResponse:
    ip = get_client_ip(request)
    remaining = await free_usage_service.get_remaining(db, ip)
    tomorrow = date.today() + timedelta(days=1)

    return FreeTierStatusResponse(
        remaining=remaining,
        limit=settings.free_tier_daily_limit,
        resets_at=tomorrow.isoformat(),
    )


@router.get(
    "/",
    response_model=CampaignListResponse,
    summary="List saved campaigns",
)
@limiter.limit("30/minute")
async def list_campaigns(
    request: Request,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> CampaignListResponse:
    campaigns, total = await campaign_service.get_campaigns(db, skip, limit)
    return CampaignListResponse(
        success=True,
        campaigns=[CampaignRecord.model_validate(c) for c in campaigns],
        total=total,
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignRecord,
    summary="Get campaign by ID",
)
@limiter.limit("30/minute")
async def get_campaign(
    request: Request,
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
) -> CampaignRecord:
    campaign = await campaign_service.get_campaign_by_id(db, campaign_id)
    if not campaign:
        raise NotFoundException(
            error="Campaign not found",
            detail=f"No campaign exists with ID {campaign_id}",
        )
    return CampaignRecord.model_validate(campaign)
