"""Tests for generator — mocks the Claude API."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from tech_ziwei.engine import BirthData, calculate
from tech_ziwei.schemas.chart import ChartRequest
from tech_ziwei.services.chart import _chart_from_result
from tech_ziwei.models.reading import ReadingType
from tech_ziwei.ai.generator import generate_reading, _build_user_message


def _make_chart():
    req = ChartRequest(gregorian_date=date(1990, 5, 15), birth_time=time(14, 30), is_male=True)
    birth = BirthData(gregorian_date=req.gregorian_date, birth_time=req.birth_time, is_male=req.is_male)
    return _chart_from_result(calculate(birth), "user-1", req)


class TestBuildUserMessage:
    def test_core_message_includes_chart_context(self):
        chart = _make_chart()
        msg = _build_user_message(chart, ReadingType.CORE)
        assert "BIRTH DATA" in msg
        assert "Core Personality" in msg

    def test_relationship_message_correct_type(self):
        chart = _make_chart()
        msg = _build_user_message(chart, ReadingType.RELATIONSHIP)
        assert "Relationship" in msg

    def test_career_message_correct_type(self):
        chart = _make_chart()
        msg = _build_user_message(chart, ReadingType.CAREER)
        assert "Career" in msg

    def test_annual_message_includes_age(self):
        chart = _make_chart()
        msg = _build_user_message(chart, ReadingType.ANNUAL)
        assert "aged" in msg


class TestGenerateReading:
    def test_calls_claude_api_with_cache_control(self):
        chart = _make_chart()
        mock_text = MagicMock()
        mock_text.text = "Your core personality reflects..."

        mock_response = MagicMock()
        mock_response.content = [mock_text]

        with patch("tech_ziwei.ai.generator.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            result = generate_reading(chart, ReadingType.CORE)

        assert result == "Your core personality reflects..."

        # Verify cache_control was set on the system prompt
        call_kwargs = MockClient.return_value.messages.create.call_args.kwargs
        system_blocks = call_kwargs["system"]
        assert isinstance(system_blocks, list)
        assert system_blocks[0]["cache_control"] == {"type": "ephemeral"}

    def test_returns_string(self):
        chart = _make_chart()
        mock_text = MagicMock()
        mock_text.text = "A meaningful reading."
        mock_response = MagicMock()
        mock_response.content = [mock_text]

        with patch("tech_ziwei.ai.generator.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            result = generate_reading(chart, ReadingType.CAREER)

        assert isinstance(result, str)
        assert len(result) > 0
