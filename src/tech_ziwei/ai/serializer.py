"""Convert a Chart ORM model into a structured, prompt-ready context string."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from tech_ziwei.engine.constants import BRANCHES, STEMS, PALACE_NAMES, WuXingJu
from .prompts import STAR_ARCHETYPES, PALACE_DOMAINS

if TYPE_CHECKING:
    from tech_ziwei.models.chart import Chart

_WU_XING_JU_NAMES: dict[int, str] = {
    2: "Water-2 (水二局) — fluid, adaptive, fast-cycle energy",
    3: "Wood-3 (木三局) — growing, expansive, upward-reaching energy",
    4: "Metal-4 (金四局) — decisive, refining, boundary-aware energy",
    5: "Earth-5 (土五局) — grounded, stabilising, patient energy",
    6: "Fire-6 (火六局) — intense, transformative, high-amplitude energy",
}


def _branch_str(idx: int) -> str:
    return BRANCHES[idx]


def _stem_str(idx: int) -> str:
    return STEMS[idx]


def _palace_name_for_offset(ming_branch: int, target_branch: int) -> str:
    offset = (ming_branch - target_branch + 12) % 12
    return PALACE_NAMES[offset]


def _current_major_period(major_periods: list[dict], birth_year: int) -> dict | None:
    from datetime import datetime
    current_year = datetime.now().year
    # Approximate current age (no month adjustment needed here)
    approx_age = current_year - birth_year
    for period in major_periods:
        if period["start_age"] <= approx_age <= period["end_age"]:
            return period
    # Fall back to last period if beyond the listed range
    return major_periods[-1] if major_periods else None


def chart_to_context(chart: Chart) -> str:
    """Render a chart as a structured plain-text block for the AI prompt."""
    ming = chart.ming_branch
    ming_stem = chart.year_stem  # This is the year stem; palace stem is computed in engine
    # We store year_stem in chart, but palace stem for 命宮 is what matters for 五行局
    # For the prompt we just describe the key facts

    # Build palace → stars mapping
    palace_stars: dict[str, list[str]] = {name: [] for name in PALACE_NAMES}
    for star_name, branch_idx in chart.star_placements.items():
        palace_name = _palace_name_for_offset(ming, branch_idx)
        palace_stars[palace_name].append(star_name)

    # Year ganzhi
    year_ganzhi = f"{_stem_str(chart.year_stem)}{_branch_str(chart.year_branch)}"
    lunar_date_str = (
        f"{chart.lunar_year}/{chart.lunar_month}/{chart.lunar_day}"
        + (" (leap month)" if chart.is_leap_month else "")
    )

    wu_xing_label = _WU_XING_JU_NAMES.get(chart.wu_xing_ju, str(chart.wu_xing_ju))

    lines = [
        "=== BIRTH DATA ===",
        f"Gregorian date : {chart.gregorian_date}",
        f"Lunar date     : {lunar_date_str}",
        f"Year cycle     : {year_ganzhi} year",
        f"Gender         : {'Male' if chart.is_male else 'Female'}",
        "",
        "=== CHART FOUNDATION ===",
        f"Life Palace (命宮) branch : {_branch_str(ming)}",
        f"Five-Element Set          : {wu_xing_label}",
        "",
        "=== PALACE STAR LAYOUT ===",
    ]

    for name in PALACE_NAMES:
        stars = palace_stars[name]
        domain = PALACE_DOMAINS.get(name, "")
        star_list = ", ".join(stars) if stars else "—"
        archetype_notes = []
        for s in stars:
            if s in STAR_ARCHETYPES:
                short = STAR_ARCHETYPES[s].split("—")[0].strip()
                archetype_notes.append(f"{s} ({short})")
        star_display = ", ".join(archetype_notes) if archetype_notes else "—"
        lines.append(f"  {name:6s} [{domain}]")
        lines.append(f"    Stars: {star_display}")

    # Current major period
    current = _current_major_period(chart.major_periods, chart.lunar_year)
    if current:
        period_palace = _palace_name_for_offset(ming, current["palace_branch"])
        period_stars = palace_stars.get(period_palace, [])
        lines += [
            "",
            "=== CURRENT MAJOR PERIOD (大限) ===",
            f"  Age range  : {current['start_age']}–{current['end_age']}",
            f"  Palace     : {period_palace}",
            f"  Domain     : {PALACE_DOMAINS.get(period_palace, '')}",
            f"  Stars      : {', '.join(period_stars) or '—'}",
        ]

    # Year mutagen (四化) — from iztro-py, stored in chart.mutagens
    # Format: {star_name: {"type": "祿"|"權"|"科"|"忌", "branch": int}}
    # (minor stars such as 文曲/文昌/左輔/右弼 carry branch so palace is always shown)
    raw_mutagens: dict = getattr(chart, "mutagens", None) or {}
    if raw_mutagens:
        _MUTAGEN_LABELS = {
            "祿": "祿 (Abundance Flow)    ",
            "權": "權 (Power Activation)  ",
            "科": "科 (Scholarly Clarity)  ",
            "忌": "忌 (Friction / Growth)  ",
        }
        lines += ["", "=== YEAR MUTAGEN (四化) ==="]
        for mutagen_type in ("祿", "權", "科", "忌"):
            for star, info in raw_mutagens.items():
                # Support both dict format {type, branch} and legacy plain-string format
                if isinstance(info, dict):
                    mt = info.get("type")
                    branch_idx = info.get("branch")
                else:
                    mt = info
                    branch_idx = chart.star_placements.get(star)
                if mt != mutagen_type:
                    continue
                if branch_idx is not None:
                    offset = (ming - branch_idx + 12) % 12
                    palace = PALACE_NAMES[offset]
                    domain = PALACE_DOMAINS.get(palace, "")
                    lines.append(
                        f"  {_MUTAGEN_LABELS.get(mutagen_type, mutagen_type)}: "
                        f"{star} → {palace} [{domain}]"
                    )
                else:
                    lines.append(f"  {_MUTAGEN_LABELS.get(mutagen_type, mutagen_type)}: {star}")

    return "\n".join(lines)


def current_age_from_chart(chart: Chart) -> int:
    from datetime import datetime
    return datetime.now().year - chart.lunar_year
