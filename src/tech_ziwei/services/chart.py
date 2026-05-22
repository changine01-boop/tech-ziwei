"""Chart calculation and persistence."""

from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tech_ziwei.engine import BirthData, calculate
from tech_ziwei.models.chart import Chart
from tech_ziwei.schemas.chart import ChartRequest


def _chart_from_result(result, user_id: str, req: ChartRequest) -> Chart:
    return Chart(
        user_id=user_id,
        gregorian_date=req.gregorian_date,
        birth_time=req.birth_time,
        is_male=req.is_male,
        timezone_offset=req.timezone_offset,
        lunar_year=result.lunar.year,
        lunar_month=result.lunar.month,
        lunar_day=result.lunar.day,
        is_leap_month=result.lunar.is_leap_month,
        ming_branch=int(result.ming),
        wu_xing_ju=int(result.wu_xing_ju),
        year_stem=int(result.year_stem),
        year_branch=int(result.year_branch),
        star_placements={k: int(v) for k, v in result.star_placements.items()},
        major_periods=[
            {
                "index": p.index,
                "start_age": p.start_age,
                "end_age": p.end_age,
                "palace_branch": int(p.palace_branch),
                "palace_name": p.palace_name,
            }
            for p in result.major_period_list
        ],
    )


async def create_chart(db: AsyncSession, user_id: str, req: ChartRequest) -> Chart:
    birth = BirthData(
        gregorian_date=req.gregorian_date,
        birth_time=req.birth_time,
        is_male=req.is_male,
        timezone_offset=req.timezone_offset,
    )
    result = calculate(birth)
    chart = _chart_from_result(result, user_id, req)
    db.add(chart)
    await db.commit()
    await db.refresh(chart)
    return chart


async def get_chart(db: AsyncSession, chart_id: str, user_id: str) -> Chart | None:
    result = await db.execute(
        select(Chart).where(Chart.id == chart_id, Chart.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def list_charts(db: AsyncSession, user_id: str) -> list[Chart]:
    result = await db.execute(
        select(Chart).where(Chart.user_id == user_id).order_by(Chart.created_at.desc())
    )
    return list(result.scalars().all())
