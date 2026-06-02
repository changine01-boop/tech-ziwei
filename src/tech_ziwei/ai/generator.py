"""Claude API client with system-prompt caching for report generation."""

import anthropic

from tech_ziwei.config import settings
from tech_ziwei.models.reading import ReadingType
from tech_ziwei.models.chart import Chart
from tech_ziwei.engine.constants import PALACE_NAMES
from .prompts import (
    SYSTEM_PROMPT,
    core_prompt, relationship_prompt, career_prompt, annual_prompt,
    shadow_work_prompt, positive_catalysts_prompt,
)
from .serializer import chart_to_context, current_age_from_chart

_MODEL = "claude-sonnet-4-6"
_MAX_TOKENS = 1500


def _mutagen_activations(chart: Chart) -> dict[str, tuple[str, str]]:
    """Return {type: (star, palace_name)} for each 四化 on the chart."""
    raw: dict = getattr(chart, "mutagens", None) or {}
    ming = chart.ming_branch
    result: dict[str, tuple[str, str]] = {}
    for star, info in raw.items():
        if not isinstance(info, dict):
            continue
        mt = info.get("type")
        b  = info.get("branch")
        if mt and b is not None:
            offset = (ming - b + 12) % 12
            palace = PALACE_NAMES[offset]
            result[mt] = (star, palace)
    return result


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
        case ReadingType.SHADOW_WORK:
            acts = _mutagen_activations(chart)
            ji_star, ji_palace = acts.get("忌", (None, None))
            if ji_star and ji_palace:
                return shadow_work_prompt(context, ji_star, ji_palace)
            return core_prompt(context)  # fallback: no 化忌 this year
        case ReadingType.POSITIVE_CATALYSTS:
            acts = _mutagen_activations(chart)
            activations = [
                (mt, star, palace)
                for mt in ("祿", "權", "科")
                if (pair := acts.get(mt)) and (star := pair[0]) and (palace := pair[1])
            ]
            return positive_catalysts_prompt(context, activations)


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
