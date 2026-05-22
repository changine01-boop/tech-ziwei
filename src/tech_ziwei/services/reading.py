"""Reading (AI report) creation and retrieval."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from tech_ziwei.models.reading import Reading, ReadingStatus, ReadingType


async def get_or_create_reading(
    db: AsyncSession, chart_id: str, reading_type: ReadingType
) -> tuple[Reading, bool]:
    """
    Return (reading, created).
    If a complete reading already exists, return it.
    Otherwise create a new PENDING reading to be picked up by the AI worker.
    """
    result = await db.execute(
        select(Reading)
        .where(Reading.chart_id == chart_id, Reading.reading_type == reading_type)
        .order_by(Reading.created_at.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()

    if existing and existing.status in (ReadingStatus.PENDING, ReadingStatus.GENERATING, ReadingStatus.COMPLETE):
        return existing, False

    reading = Reading(chart_id=chart_id, reading_type=reading_type)
    db.add(reading)
    await db.commit()
    await db.refresh(reading)
    return reading, True


async def get_reading(db: AsyncSession, reading_id: str) -> Reading | None:
    result = await db.execute(select(Reading).where(Reading.id == reading_id))
    return result.scalar_one_or_none()


async def get_reading_by_type(
    db: AsyncSession, chart_id: str, reading_type: ReadingType
) -> Reading | None:
    result = await db.execute(
        select(Reading)
        .where(Reading.chart_id == chart_id, Reading.reading_type == reading_type)
        .order_by(Reading.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_complete_readings(db: AsyncSession, chart_id: str) -> list[Reading]:
    result = await db.execute(
        select(Reading)
        .where(Reading.chart_id == chart_id, Reading.status == ReadingStatus.COMPLETE)
        .order_by(Reading.reading_type)
    )
    return list(result.scalars().all())
