"""Top-level Chart class — entry point for all Zi Wei Dou Shu calculations."""

from dataclasses import dataclass, field
from datetime import date, time

from .constants import Branch, Stem, WuXingJu, BRANCHES, STEMS
from .lunar_calendar import to_lunar, LunarDate
from .stems_branches import year_stem, year_branch, hour_branch, branch_name, stem_name
from .palace import ming_branch, ming_wu_xing_ju, build_palaces, Palace
from .stars import place_major_stars
from .periods import major_periods, MajorPeriod


@dataclass
class BirthData:
    gregorian_date: date
    birth_time: time
    is_male: bool
    timezone_offset: float = 8.0  # hours ahead of UTC; default CST


@dataclass
class Chart:
    birth: BirthData
    lunar: LunarDate

    year_stem: Stem
    year_branch: Branch
    hour_branch: Branch

    ming: Branch           # 命宮 branch
    wu_xing_ju: WuXingJu   # 五行局

    palaces: dict[Branch, Palace]     # branch → Palace
    star_placements: dict[str, Branch]  # star name → branch
    major_period_list: list[MajorPeriod]

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
        return "\n".join(lines)


def calculate(birth: BirthData) -> Chart:
    """Calculate a full Zi Wei Dou Shu chart from birth data."""
    lunar = to_lunar(birth.gregorian_date)

    ys = year_stem(lunar.year)
    yb = year_branch(lunar.year)
    hb = hour_branch(birth.birth_time.hour, birth.birth_time.minute)

    ming = ming_branch(lunar.month, hb)
    ju = ming_wu_xing_ju(ming, lunar.year)

    palaces = build_palaces(ming, lunar.year)
    star_placements = place_major_stars(lunar.day, ju)

    # Attach stars to palaces
    for star, branch in star_placements.items():
        palaces[branch].stars.append(star)

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
    )
