from datetime import date, time

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tech_ziwei.database import Base
from .base import TimestampMixin, new_uuid


class Chart(Base, TimestampMixin):
    __tablename__ = "charts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Birth data
    gregorian_date: Mapped[date] = mapped_column(Date, nullable=False)
    birth_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_male: Mapped[bool] = mapped_column(Boolean, nullable=False)
    timezone_offset: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)

    # Computed lunar fields
    lunar_year: Mapped[int] = mapped_column(Integer, nullable=False)
    lunar_month: Mapped[int] = mapped_column(Integer, nullable=False)
    lunar_day: Mapped[int] = mapped_column(Integer, nullable=False)
    is_leap_month: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Chart results (JSON)
    ming_branch: Mapped[int] = mapped_column(Integer, nullable=False)
    wu_xing_ju: Mapped[int] = mapped_column(Integer, nullable=False)
    year_stem: Mapped[int] = mapped_column(Integer, nullable=False)
    year_branch: Mapped[int] = mapped_column(Integer, nullable=False)
    star_placements: Mapped[dict] = mapped_column(JSONB, nullable=False)
    major_periods: Mapped[list] = mapped_column(JSONB, nullable=False)
    # {star_name: "祿"|"權"|"科"|"忌"} — populated by iztro-py adapter
    mutagens: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")

    user: Mapped["User"] = relationship(back_populates="charts")  # type: ignore[name-defined]
    readings: Mapped[list["Reading"]] = relationship(back_populates="chart", lazy="raise")  # type: ignore[name-defined]
