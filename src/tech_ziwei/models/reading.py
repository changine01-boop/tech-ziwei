import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tech_ziwei.database import Base
from .base import TimestampMixin, new_uuid


class ReadingType(str, enum.Enum):
    CORE = "core"           # Core personality (命宮 + major stars)
    RELATIONSHIP = "relationship"  # 夫妻宮, 交友宮
    CAREER = "career"       # 官祿宮, 事業
    ANNUAL = "annual"       # 流年 overlay


class ReadingStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"


class Reading(Base, TimestampMixin):
    __tablename__ = "readings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    chart_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("charts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reading_type: Mapped[ReadingType] = mapped_column(
        Enum(ReadingType), nullable=False
    )
    status: Mapped[ReadingStatus] = mapped_column(
        Enum(ReadingStatus), default=ReadingStatus.PENDING, nullable=False
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    chart: Mapped["Chart"] = relationship(back_populates="readings")  # type: ignore[name-defined]
