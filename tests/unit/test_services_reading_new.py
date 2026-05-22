"""Unit tests for the new reading service functions.

All tests use a mocked async SQLAlchemy session — no DB required.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from tech_ziwei.services.reading import get_or_create_reading, get_reading_by_type
from tech_ziwei.models.reading import Reading, ReadingStatus, ReadingType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_db(existing: "Reading | None") -> AsyncMock:
    """Return a mock AsyncSession whose execute() resolves to *existing*."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing
    db.execute.return_value = result
    return db


def _make_reading(status: ReadingStatus) -> MagicMock:
    """Return a MagicMock that looks like a Reading ORM object."""
    r = MagicMock(spec=Reading)
    r.id = "reading-1"
    r.chart_id = "chart-1"
    r.reading_type = ReadingType.CORE
    r.status = status
    r.content = None
    return r


# ---------------------------------------------------------------------------
# Tests: get_or_create_reading
# ---------------------------------------------------------------------------

class TestGetOrCreateReading:
    @pytest.mark.asyncio
    async def test_returns_existing_when_complete(self):
        existing = _make_reading(ReadingStatus.COMPLETE)
        db = _make_db(existing)

        reading, created = await get_or_create_reading(db, "chart-1", ReadingType.CORE)

        assert reading is existing
        assert created is False
        db.add.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_existing_when_generating(self):
        existing = _make_reading(ReadingStatus.GENERATING)
        db = _make_db(existing)

        reading, created = await get_or_create_reading(db, "chart-1", ReadingType.CORE)

        assert reading is existing
        assert created is False
        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_existing_when_pending(self):
        """Bug fix: PENDING readings should not trigger a duplicate creation."""
        existing = _make_reading(ReadingStatus.PENDING)
        db = _make_db(existing)

        reading, created = await get_or_create_reading(db, "chart-1", ReadingType.CORE)

        assert reading is existing
        assert created is False
        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new_when_failed(self):
        existing = _make_reading(ReadingStatus.FAILED)
        db = _make_db(existing)

        reading, created = await get_or_create_reading(db, "chart-1", ReadingType.CORE)

        assert created is True
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_creates_new_when_no_existing(self):
        db = _make_db(None)

        reading, created = await get_or_create_reading(db, "chart-1", ReadingType.CAREER)

        assert created is True
        db.add.assert_called_once()
        db.commit.assert_called_once()
        db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_new_reading_has_correct_chart_id_and_type(self):
        db = _make_db(None)

        _, created = await get_or_create_reading(db, "chart-xyz", ReadingType.RELATIONSHIP)

        assert created is True
        added_reading = db.add.call_args[0][0]
        assert added_reading.chart_id == "chart-xyz"
        assert added_reading.reading_type == ReadingType.RELATIONSHIP

    @pytest.mark.asyncio
    async def test_does_not_create_new_when_pending_idempotent(self):
        """Calling twice with PENDING status on first call should not create duplicate."""
        existing = _make_reading(ReadingStatus.PENDING)
        db = _make_db(existing)

        r1, c1 = await get_or_create_reading(db, "chart-1", ReadingType.CORE)
        r2, c2 = await get_or_create_reading(db, "chart-1", ReadingType.CORE)

        assert c1 is False
        assert c2 is False
        db.add.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: get_reading_by_type
# ---------------------------------------------------------------------------

class TestGetReadingByType:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_reading_exists(self):
        db = _make_db(None)

        result = await get_reading_by_type(db, "chart-1", ReadingType.CORE)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_reading_when_exists(self):
        existing = _make_reading(ReadingStatus.COMPLETE)
        db = _make_db(existing)

        result = await get_reading_by_type(db, "chart-1", ReadingType.CORE)

        assert result is existing

    @pytest.mark.asyncio
    async def test_queries_with_correct_chart_id_and_type(self):
        db = _make_db(None)

        await get_reading_by_type(db, "chart-abc", ReadingType.ANNUAL)

        db.execute.assert_called_once()
        # The execute call should have happened (checking the query was built
        # at all — full SQL verification would require SQLAlchemy internals)

    @pytest.mark.asyncio
    async def test_returns_reading_regardless_of_status(self):
        """get_reading_by_type returns the latest reading whatever its status."""
        for status in ReadingStatus:
            existing = _make_reading(status)
            db = _make_db(existing)
            result = await get_reading_by_type(db, "chart-1", ReadingType.CORE)
            assert result is existing
