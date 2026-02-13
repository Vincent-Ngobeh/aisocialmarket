import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


def get_database_url() -> str:
    url = settings.database_url
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable is not set. "
            "Please set it in your .env file or environment. "
            "Example: DATABASE_URL=postgresql://user:password@host:port/database"
        )
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not url.startswith("postgresql+asyncpg://"):
        raise ValueError(
            f"DATABASE_URL must start with 'postgresql://' or 'postgresql+asyncpg://', got: {url[:20]}..."
        )
    return url


engine = create_async_engine(
    get_database_url(),
    echo=settings.debug,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

