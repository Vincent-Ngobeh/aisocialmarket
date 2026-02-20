from datetime import date, datetime
from sqlalchemy import String, Integer, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FreeUsage(Base):
    __tablename__ = "free_usage"
    __table_args__ = (
        UniqueConstraint("ip_address", "usage_date", name="uq_ip_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    generation_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
