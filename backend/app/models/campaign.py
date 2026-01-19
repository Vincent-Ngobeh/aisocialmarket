from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    business_name: Mapped[str] = mapped_column(String(100), nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_audience: Mapped[str] = mapped_column(Text, nullable=False)
    campaign_goal: Mapped[str] = mapped_column(Text, nullable=False)
    key_messages: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(200), nullable=False)
    platforms: Mapped[dict] = mapped_column(JSON, nullable=False)
    include_hashtags: Mapped[bool] = mapped_column(Boolean, default=True)
    include_emoji: Mapped[bool] = mapped_column(Boolean, default=True)
    seasonal_hook: Mapped[str | None] = mapped_column(String(200), nullable=True)

    generated_copies: Mapped[dict] = mapped_column(JSON, nullable=False)
    image_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
