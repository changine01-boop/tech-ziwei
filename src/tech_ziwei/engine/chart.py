"""Top-level Chart class — entry point for all Zi Wei Dou Shu calculations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time, timedelta

from .constants import Branch, Stem, WuXingJu, BRANCHES, STEMS
from .lunar_calendar import LunarDate
from .stems_branches import hour_branch, branch_name, stem_name
from .palace import build_palaces, Palace
from .periods import major_periods, MajorPeriod
from .iztro_adapter import build_iztro_chart, StarDetail


@dataclass
class BirthData:
    gregorian_date: date
    birth_time: time
    is_male: bool
    timezone_offset: float = 8.0   # hours ahead of UTC; default CST (UTC+8)
    longitude: float | None = None  # geographic longitude in degrees E (positive) / W (negative)
                                    # None → no true-solar-time correction applied


@dataclass
class Chart:
    birth: BirthData
    lunar: LunarDate

    year_stem: Stem
    year_branch: Branch
    hour_branch: Branch

    ming: Branch           # 命宮 branch
    wu_xing_ju: WuXingJu   # 五行局

    palaces: dict[Branch, Palace]       # branch → Palace (with stars attached)
    star_placements: dict[str, Branch]  # major-star name → branch
    major_period_list: list[MajorPeriod]

    # Enriched star data from iztro-py (brightness + 四化)
    star_details: list[StarDetail] = field(default_factory=list)

    @property
    def ming_palace(self) -> Palace:
        return self.palaces[self.ming]

    @property
    def year_stem_name(self) -> str:
        return stem_name(self.year_stem)

    @property
    def year_branch_name(self) -> str:
        return branch_name(self.year_branch)

    def palace_stars(self, branch: Branch) -> list[str]:
        return [s for s, b in self.star_placements.items() if b == branch]

    def mutagens(self) -> dict[str, str]:
        """Return {star_name: mutagen_type} for every star that carries a 四化."""
        return {s.name: s.mutagen for s in self.star_details if s.mutagen}

    def summary(self) -> str:
        lines = [
            f"生日: {self.birth.gregorian_date}  農曆: {self.lunar.year}/{self.lunar.month}/{self.lunar.day}",
            f"年干支: {self.year_stem_name}{self.year_branch_name}",
            f"命宮: {self.ming_palace.stem_name}{self.ming_palace.branch_name}  五行局: {self.wu_xing_ju.name}({int(self.wu_xing_ju)})",
            "",
            "十四主星分佈:",
        ]
        for branch in Branch:
            stars = self.palace_stars(branch)
            palace = self.palaces[branch]
            if stars:
                lines.append(f"  {palace.name:6s} [{branch.name}] {' '.join(stars)}")
        mu = self.mutagens()
        if mu:
            lines.append("")
            lines.append("四化:")
            for star, m in mu.items():
                lines.append(f"  {m} : {star}")
        return "\n".join(lines)


def _apply_true_solar_time(
    clock_time: time,
    longitude: float,
    timezone_offset: float,
) -> time:
    """
    Adjust clock time to true solar time (真太陽時).

    Formula:
        standard_meridian  = timezone_offset × 15°
        correction_minutes = (longitude − standard_meridian) × 4 min/°
        true_solar_time    = clock_time + correction_minutes

    Example — Taipei (121.5°E, CST UTC+8):
        standard_meridian = 8 × 15 = 120°
        correction = (121.5 − 120) × 4 = +6 min
        08:55 → 09:01  (crosses 辰/巳 boundary)
    """
    standard_meridian = timezone_offset * 15.0
    correction_minutes = (longitude - standard_meridian) * 4.0
    total_minutes = clock_time.hour * 60 + clock_time.minute + round(correction_minutes)
    total_minutes = total_minutes % (24 * 60)  # wrap around midnight
    return time(total_minutes // 60, total_minutes % 60)


def calculate(birth: BirthData) -> Chart:
    """
    Calculate a full Zi Wei Dou Shu chart.

    True-solar-time correction (真太陽時):
        If birth.longitude is provided, the raw birth_time is adjusted
        BEFORE the time-branch (時辰) index is computed.  The corrected
        time is then forwarded to iztro_adapter — no second correction
        is applied there.

    Star placement:
        Delegated entirely to iztro_adapter (iztro-py).
        stars.py place_major_stars() is NOT called anywhere in this function.
    """
    # ── Step 1: Apply true-solar-time correction if longitude is supplied ──
    if birth.longitude is not None:
        corrected_time = _apply_true_solar_time(
            birth.birth_time, birth.longitude, birth.timezone_offset
        )
    else:
        corrected_time = birth.birth_time

    # ── Step 2: iztro-py — star placement, lunar date, 五行局 ──────────────
    # corrected_time is passed; adapter does NOT redo longitude correction.
    iztro_data = build_iztro_chart(
        birth.gregorian_date,
        corrected_time,
        birth.is_male,
    )

    # ── Step 3: Reconstruct typed values for Chart dataclass ───────────────
    lunar = LunarDate(
        year=iztro_data.lunar_year,
        month=iztro_data.lunar_month,
        day=iztro_data.lunar_day,
        is_leap_month=iztro_data.is_leap_month,
    )
    ys   = Stem(iztro_data.year_stem)
    yb   = Branch(iztro_data.year_branch)
    hb   = hour_branch(corrected_time.hour, corrected_time.minute)
    ming = Branch(iztro_data.ming_branch)
    ju   = WuXingJu(iztro_data.wu_xing_ju)

    # ── Step 4: Palace structure (stem/branch names; stars attached below) ─
    palaces = build_palaces(ming, lunar.year)

    # ── Step 5: Attach iztro-py star placements ────────────────────────────
    # stars.py place_major_stars() is NOT called.  iztro_data.star_placements
    # is the sole source of truth for star locations.
    star_placements: dict[str, Branch] = {
        name: Branch(b) for name, b in iztro_data.star_placements.items()
    }
    for star, branch in star_placements.items():
        palaces[branch].stars.append(star)

    # ── Step 6: Major periods (our engine; matches adapter's internal calc) ─
    periods = major_periods(
        ming=ming,
        ju=ju,
        lunar_year=lunar.year,
        is_male=birth.is_male,
        first_period_age=int(ju) // 2 or 1,
    )

    return Chart(
        birth=birth,
        lunar=lunar,
        year_stem=ys,
        year_branch=yb,
        hour_branch=hb,
        ming=ming,
        wu_xing_ju=ju,
        palaces=palaces,
        star_placements=star_placements,
        major_period_list=periods,
        star_details=iztro_data.star_details,
    )
