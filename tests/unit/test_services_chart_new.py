"""Unit tests for the delete_chart service function.

All tests use a mocked async SQLAlchemy session — no DB required.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tech_ziwei.services.chart import delete_chart
from tech_ziwei.models.chart import Chart


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chart(chart_id: str, user_id: str) -> MagicMock:
    """Return a MagicMock that looks like a Chart ORM object."""
    c = MagicMock(spec=Chart)
    c.id = chart_id
    c.user_id = user_id
    return c


def _make_db() -> AsyncMock:
    return AsyncMock()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDeleteChart:
    @pytest.mark.asyncio
    async def test_returns_true_when_chart_exists_and_belongs_to_user(self):
        chart = _make_chart("chart-1", "user-1")
        db = _make_db()

        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=chart),
        ):
            result = await delete_chart(db, "chart-1", "user-1")

        assert result is True

    @pytest.mark.asyncio
    async def test_deletes_chart_from_db_when_found(self):
        chart = _make_chart("chart-1", "user-1")
        db = _make_db()

        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=chart),
        ):
            await delete_chart(db, "chart-1", "user-1")

        db.delete.assert_called_once_with(chart)
        db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_chart_not_found(self):
        db = _make_db()

        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=None),
        ):
            result = await delete_chart(db, "non-existent", "user-1")

        assert result is False

    @pytest.mark.asyncio
    async def test_does_not_delete_when_chart_not_found(self):
        db = _make_db()

        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=None),
        ):
            await delete_chart(db, "non-existent", "user-1")

        db.delete.assert_not_called()
        db.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_returns_false_when_chart_belongs_to_different_user(self):
        """get_chart already enforces user_id; if it returns None the chart is
        either missing or owned by another user — delete_chart should return False."""
        db = _make_db()

        # Simulate get_chart returning None for the wrong user_id
        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=None),
        ):
            result = await delete_chart(db, "chart-1", "wrong-user")

        assert result is False

    @pytest.mark.asyncio
    async def test_passes_correct_ids_to_get_chart(self):
        db = _make_db()

        mock_get_chart = AsyncMock(return_value=None)
        with patch("tech_ziwei.services.chart.get_chart", new=mock_get_chart):
            await delete_chart(db, "chart-abc", "user-xyz")

        mock_get_chart.assert_called_once_with(db, "chart-abc", "user-xyz")

    @pytest.mark.asyncio
    async def test_delete_and_commit_called_in_order(self):
        """db.delete must be called before db.commit."""
        chart = _make_chart("chart-1", "user-1")
        db = _make_db()
        call_order: list[str] = []

        async def record_delete(obj):
            call_order.append("delete")

        async def record_commit():
            call_order.append("commit")

        db.delete.side_effect = record_delete
        db.commit.side_effect = record_commit

        with patch(
            "tech_ziwei.services.chart.get_chart",
            new=AsyncMock(return_value=chart),
        ):
            await delete_chart(db, "chart-1", "user-1")

        assert call_order == ["delete", "commit"]
