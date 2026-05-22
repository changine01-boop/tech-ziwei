"""Unit tests for chart service helper — engine integration."""

from datetime import date, time

import pytest

from tech_ziwei.engine import BirthData, calculate
from tech_ziwei.schemas.chart import ChartRequest
from tech_ziwei.services.chart import _chart_from_result


class TestChartFromResult:
    def _make_req(self) -> ChartRequest:
        return ChartRequest(
            gregorian_date=date(1990, 5, 15),
            birth_time=time(14, 30),
            is_male=True,
        )

    def test_chart_orm_fields_populated(self):
        req = self._make_req()
        birth = BirthData(
            gregorian_date=req.gregorian_date,
            birth_time=req.birth_time,
            is_male=req.is_male,
        )
        result = calculate(birth)
        chart = _chart_from_result(result, "user-1", req)

        assert chart.user_id == "user-1"
        assert chart.gregorian_date == date(1990, 5, 15)
        assert chart.lunar_year == 1990
        assert isinstance(chart.star_placements, dict)
        assert len(chart.star_placements) == 14
        assert isinstance(chart.major_periods, list)
        assert len(chart.major_periods) > 0

    def test_star_placements_are_ints(self):
        req = self._make_req()
        birth = BirthData(
            gregorian_date=req.gregorian_date,
            birth_time=req.birth_time,
            is_male=req.is_male,
        )
        result = calculate(birth)
        chart = _chart_from_result(result, "user-1", req)
        for key, val in chart.star_placements.items():
            assert isinstance(key, str)
            assert isinstance(val, int)
            assert 0 <= val <= 11
