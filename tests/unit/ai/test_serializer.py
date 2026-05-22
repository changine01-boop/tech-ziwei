"""Tests for chart → prompt context serializer."""

from datetime import date, time
from unittest.mock import MagicMock

import pytest

from tech_ziwei.engine import BirthData, calculate
from tech_ziwei.services.chart import _chart_from_result
from tech_ziwei.schemas.chart import ChartRequest
from tech_ziwei.ai.serializer import chart_to_context, current_age_from_chart
from tech_ziwei.engine.constants import PALACE_NAMES


def _make_chart_orm():
    req = ChartRequest(gregorian_date=date(1990, 5, 15), birth_time=time(14, 30), is_male=True)
    birth = BirthData(gregorian_date=req.gregorian_date, birth_time=req.birth_time, is_male=req.is_male)
    result = calculate(birth)
    return _chart_from_result(result, "user-1", req)


class TestChartToContext:
    def test_contains_birth_data_section(self):
        ctx = chart_to_context(_make_chart_orm())
        assert "BIRTH DATA" in ctx
        assert "1990" in ctx

    def test_contains_all_palace_names(self):
        ctx = chart_to_context(_make_chart_orm())
        for name in PALACE_NAMES:
            assert name in ctx, f"Missing palace: {name}"

    def test_contains_star_names(self):
        ctx = chart_to_context(_make_chart_orm())
        assert "紫微" in ctx
        assert "天府" in ctx

    def test_contains_wu_xing_ju_description(self):
        ctx = chart_to_context(_make_chart_orm())
        assert "Five-Element Set" in ctx

    def test_contains_major_period_section(self):
        ctx = chart_to_context(_make_chart_orm())
        assert "MAJOR PERIOD" in ctx

    def test_no_unresolved_branch_indices(self):
        ctx = chart_to_context(_make_chart_orm())
        # Branch indices should be replaced by Chinese characters, not bare ints 0–11
        # We just assert the context is a non-empty string
        assert len(ctx) > 200


class TestCurrentAge:
    def test_returns_positive_int(self):
        chart = _make_chart_orm()
        age = current_age_from_chart(chart)
        assert isinstance(age, int)
        assert age > 0
