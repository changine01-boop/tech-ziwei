"""
iztro_adapter.py — wraps iztro-py as the authoritative chart calculation backend.

The adapter's output is duck-typed to match the ORM Chart model so that
ai/serializer.py and the rest of the pipeline work without modification.
Extended fields (brightness, mutagen) are carried in `star_details` for
future prompt enrichment.

Caller contract:
  - Pass `birth_time` already corrected for true solar time (longitude
    correction must be done upstream; this module does NOT repeat it).
  - Gender is bool (is_male).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time

import iztro_py

from .constants import Branch, Stem, WuXingJu, BRANCHES, STEMS, PALACE_NAMES
from .lunar_calendar import to_lunar
from .periods import major_periods as _calc_major_periods
from .stems_branches import year_stem as _year_stem, year_branch as _year_branch, hour_branch

LANG = "zh-TW"

# iztro-py earthly branch ID → Branch int
_EARTHLY_TO_INT: dict[str, int] = {
    "ziEarthly": 0,
    "chouEarthly": 1,
    "yinEarthly": 2,
    "maoEarthly": 3,
    "chenEarthly": 4,
    "siEarthly": 5,
    "wuEarthly": 6,
    "weiEarthly": 7,
    "shenEarthly": 8,
    "youEarthly": 9,
    "xuEarthly": 10,
    "haiEarthly": 11,
}

# Normalize simplified mutagen chars → traditional
_MUTAGEN_NORM: dict[str, str] = {
    "禄": "祿",
    "权": "權",
    "科": "科",
    "忌": "忌",
}


def _norm_mutagen(m: str | None) -> str | None:
    if m is None:
        return None
    return _MUTAGEN_NORM.get(m, m)


def _parse_wu_xing_ju(five_class: str) -> WuXingJu:
    """'金四局' → WuXingJu.METAL (4), etc."""
    _MAP: dict[str, WuXingJu] = {
        "二": WuXingJu.WATER,
        "三": WuXingJu.WOOD,
        "四": WuXingJu.METAL,
        "五": WuXingJu.EARTH,
        "六": WuXingJu.FIRE,
    }
    for ch, ju in _MAP.items():
        if ch in five_class:
            return ju
    raise ValueError(f"Cannot parse WuXingJu from: {five_class!r}")


@dataclass
class StarDetail:
    """Enriched star record carrying brightness and mutagen for future prompt use."""

    name: str               # Chinese name, e.g. '太陽'
    star_type: str          # 'major' | 'minor' | 'adjective'
    palace_branch: int      # 0–11 (Branch int)
    palace_name: str        # e.g. '命宮'
    brightness: str | None  # '廟'/'旺'/'得'/'利'/'平'/'陷'/None
    mutagen: str | None     # '祿'/'權'/'科'/'忌'/None (traditional chars)


@dataclass
class IztroChartData:
    """
    Output of build_iztro_chart().

    Duck-typed to satisfy all fields that ai/serializer.py reads from the ORM
    Chart model, so no downstream changes are required.
    """

    # ── ORM-compatible fields (serializer reads these) ─────────────────────
    gregorian_date: date
    is_male: bool
    lunar_year: int
    lunar_month: int
    lunar_day: int
    is_leap_month: bool
    ming_branch: int                # Branch int of 命宮
    wu_xing_ju: int                 # WuXingJu int value
    year_stem: int                  # Stem int
    year_branch: int                # Branch int
    star_placements: dict[str, int] # major-star Chinese name → Branch int
    major_periods: list[dict]       # [{start_age, end_age, palace_branch}, ...]

    # ── Extended fields (not used by current serializer; reserved for prompts) ──
    five_elements_class: str        # e.g. '金四局'
    star_details: list[StarDetail] = field(default_factory=list)

    def mutagens(self) -> dict[str, str]:
        """Return {star_name: mutagen} for every star that carries a 四化."""
        return {s.name: s.mutagen for s in self.star_details if s.mutagen}

    def palace_star_details(self, palace_name: str) -> list[StarDetail]:
        return [s for s in self.star_details if s.palace_name == palace_name]


def build_iztro_chart(
    gregorian_date: date,
    birth_time: time,
    is_male: bool,
    *,
    fix_leap: bool = True,
) -> IztroChartData:
    """
    Calculate a full Zi Wei Dou Shu chart using iztro-py.

    Args:
        gregorian_date: Gregorian birth date.
        birth_time:     Birth time already in true solar time (longitude
                        correction must be done by the caller).
        is_male:        True for male, False for female.
        fix_leap:       Whether to shift leap-month births to the first day of
                        the following month (iztro standard behaviour).

    Returns:
        IztroChartData compatible with ai/serializer.py.
    """
    hb = hour_branch(birth_time.hour, birth_time.minute)
    time_index = int(hb)          # Branch int == iztro time index (子=0…亥=11)
    gender = "男" if is_male else "女"

    raw = iztro_py.by_solar(gregorian_date.isoformat(), time_index, gender, fix_leap, LANG)

    # ── Lunar date & year ganzhi ───────────────────────────────────────────
    lunar = to_lunar(gregorian_date)
    ys = _year_stem(lunar.year)
    yb = _year_branch(lunar.year)

    # ── Five-element set ───────────────────────────────────────────────────
    ju = _parse_wu_xing_ju(raw.five_elements_class)

    # ── Find 命宮 branch ───────────────────────────────────────────────────
    ming_palace_raw = next(
        p for p in raw.palaces if p.translate_name(LANG) == "命宮"
    )
    ming_branch_int = _EARTHLY_TO_INT[ming_palace_raw.earthly_branch]

    # ── Build star_details and star_placements from all 12 palaces ─────────
    star_details: list[StarDetail] = []
    star_placements: dict[str, int] = {}

    for palace in raw.palaces:
        branch_int = _EARTHLY_TO_INT[palace.earthly_branch]
        palace_name = palace.translate_name(LANG)

        all_stars = (
            list(palace.major_stars)
            + list(palace.minor_stars)
            + list(palace.adjective_stars)
        )
        for s in all_stars:
            zh_name = s.translate_name(LANG)
            brightness = s.translate_brightness(LANG)  # returns traditional chars
            mutagen = _norm_mutagen(s.mutagen)

            star_details.append(
                StarDetail(
                    name=zh_name,
                    star_type=s.type,
                    palace_branch=branch_int,
                    palace_name=palace_name,
                    brightness=brightness if brightness else None,
                    mutagen=mutagen,
                )
            )
            if s.type == "major":
                star_placements[zh_name] = branch_int

    # ── Major periods (our own engine; iztro-py doesn't expose this) ───────
    periods = _calc_major_periods(
        ming=Branch(ming_branch_int),
        ju=ju,
        lunar_year=lunar.year,
        is_male=is_male,
        first_period_age=int(ju) // 2 or 1,
    )
    major_periods_list = [
        {
            "start_age": p.start_age,
            "end_age": p.end_age,
            "palace_branch": int(p.palace_branch),
        }
        for p in periods
    ]

    return IztroChartData(
        gregorian_date=gregorian_date,
        is_male=is_male,
        lunar_year=lunar.year,
        lunar_month=lunar.month,
        lunar_day=lunar.day,
        is_leap_month=lunar.is_leap_month,
        ming_branch=ming_branch_int,
        wu_xing_ju=int(ju),
        year_stem=int(ys),
        year_branch=int(yb),
        star_placements=star_placements,
        major_periods=major_periods_list,
        five_elements_class=raw.five_elements_class,
        star_details=star_details,
    )
