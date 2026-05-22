"""Celery task: generate an AI reading and persist it to the database."""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

logger = logging.getLogger(__name__)

from tech_ziwei.config import settings
from tech_ziwei.models.chart import Chart
from tech_ziwei.models.reading import Reading, ReadingStatus, ReadingType
from tech_ziwei.ai.generator import generate_reading
from .celery_app import celery_app


def _make_session():
    engine = create_async_engine(settings.database_url)
    return async_sessionmaker(engine, expire_on_commit=False)


async def _run(reading_id: str) -> None:
    Session = _make_session()
    async with Session() as db:
        result = await db.execute(select(Reading).where(Reading.id == reading_id))
        reading = result.scalar_one_or_none()
        if reading is None:
            return

        # Mark as generating
        reading.status = ReadingStatus.GENERATING
        await db.commit()

        # Load the associated chart
        chart_result = await db.execute(select(Chart).where(Chart.id == reading.chart_id))
        chart = chart_result.scalar_one_or_none()
        if chart is None:
            reading.status = ReadingStatus.FAILED
            await db.commit()
            return

        try:
            content = generate_reading(chart, ReadingType(reading.reading_type))
            reading.content = content
            reading.status = ReadingStatus.COMPLETE
            reading.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            logger.error(
                "Reading generation failed for reading_id=%s: %s",
                reading_id,
                exc,
            )
            reading.status = ReadingStatus.FAILED
            raise  # let Celery handle retry
        finally:
            await db.commit()


@celery_app.task(
    name="tech_ziwei.generate_reading",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    autoretry_for=(Exception,),
)
def generate_reading_task(self, reading_id: str) -> dict:
    """
    Celery task: generate an AI reading for a given reading_id.
    Uses asyncio.run() since Celery workers are synchronous by default.
    """
    asyncio.run(_run(reading_id))
    return {"reading_id": reading_id, "status": "complete"}
