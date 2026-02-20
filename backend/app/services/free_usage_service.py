from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.config import get_settings
from app.models.free_usage import FreeUsage


settings = get_settings()


async def get_usage_today(db: AsyncSession, ip_address: str) -> FreeUsage | None:
    query = select(FreeUsage).where(
        FreeUsage.ip_address == ip_address,
        FreeUsage.usage_date == date.today(),
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def increment_usage(db: AsyncSession, ip_address: str) -> int:
    stmt = pg_insert(FreeUsage).values(
        ip_address=ip_address,
        usage_date=date.today(),
        generation_count=1,
    ).on_conflict_do_update(
        constraint="uq_ip_date",
        set_={"generation_count": FreeUsage.generation_count + 1,
              "updated_at": datetime.utcnow()},
    ).returning(FreeUsage.generation_count)

    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()


async def get_remaining(db: AsyncSession, ip_address: str) -> int:
    usage = await get_usage_today(db, ip_address)
    if usage is None:
        return settings.free_tier_daily_limit
    return max(0, settings.free_tier_daily_limit - usage.generation_count)


async def can_generate(db: AsyncSession, ip_address: str) -> bool:
    return (await get_remaining(db, ip_address)) > 0
