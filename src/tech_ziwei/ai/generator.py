"""Claude API client with system-prompt caching for report generation."""

import anthropic

from tech_ziwei.config import settings
from tech_ziwei.models.reading import ReadingType
from tech_ziwei.models.chart import Chart
from .prompts import (
    SYSTEM_PROMPT,
    core_prompt, relationship_prompt, career_prompt, annual_prompt,
)
from .serializer import chart_to_context, current_age_from_chart

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 1024


def _build_user_message(chart: Chart, reading_type: ReadingType) -> str:
    context = chart_to_context(chart)
    match reading_type:
        case ReadingType.CORE:
            return core_prompt(context)
        case ReadingType.RELATIONSHIP:
            return relationship_prompt(context)
        case ReadingType.CAREER:
            return career_prompt(context)
        case ReadingType.ANNUAL:
            age = current_age_from_chart(chart)
            return annual_prompt(context, age)


def generate_reading(chart: Chart, reading_type: ReadingType) -> str:
    """
    Call Claude to generate a psychological astrology reading.

    The system prompt is marked with cache_control so subsequent calls for
    different users / reading types share the cached prompt (saves ~90% tokens
    on the system prompt portion after the first call).
    """
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {"role": "user", "content": _build_user_message(chart, reading_type)}
        ],
    )

    return response.content[0].text  # type: ignore[index]
