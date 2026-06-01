from datetime import date, datetime, time

from pydantic import BaseModel, Field


class ChartRequest(BaseModel):
    gregorian_date: date
    birth_time: time
    is_male: bool
    timezone_offset: float = Field(default=8.0, ge=-12, le=14)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class StarPlacement(BaseModel):
    branch: int
    branch_name: str


class PeriodResponse(BaseModel):
    index: int
    start_age: int
    end_age: int
    palace_branch: int
    palace_name: str


class ChartResponse(BaseModel):
    id: str
    gregorian_date: date
    birth_time: time
    is_male: bool

    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool

    year_stem: int
    year_branch: int
    ming_branch: int
    wu_xing_ju: int

    star_placements: dict[str, int]
    major_periods: list[dict]

    created_at: datetime

    model_config = {"from_attributes": True}
