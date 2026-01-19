from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.sql import func

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignBrief, PlatformCopy


async def save_campaign(
    db: AsyncSession,
    brief: CampaignBrief,
    copies: list[PlatformCopy],
    image_prompt: str,
    image_url: str | None = None,
) -> Campaign:
    campaign = Campaign(
        business_name=brief.business_name,
        business_type=brief.business_type,
        target_audience=brief.target_audience,
        campaign_goal=brief.campaign_goal,
        key_messages=brief.key_messages,
        tone=brief.tone,
        platforms=brief.platforms,
        include_hashtags=brief.include_hashtags,
        include_emoji=brief.include_emoji,
        seasonal_hook=brief.seasonal_hook,
        generated_copies=[c.model_dump() for c in copies],
        image_prompt=image_prompt,
        image_url=image_url,
    )

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return campaign


async def get_campaigns(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
) -> tuple[list[Campaign], int]:
    count_query = select(func.count()).select_from(Campaign)
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = (
        select(Campaign)
        .order_by(desc(Campaign.created_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    campaigns = result.scalars().all()

    return list(campaigns), total


async def get_campaign_by_id(db: AsyncSession, campaign_id: int) -> Campaign | None:
    query = select(Campaign).where(Campaign.id == campaign_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
