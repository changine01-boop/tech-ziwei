"""大限 (Major Period) and 流年 (Annual Period) calculations."""

from dataclasses import dataclass

from .constants import Branch, WuXingJu, Stem, PALACE_NAMES, BRANCHES
from .stems_branches import year_stem


@dataclass(frozen=True)
class MajorPeriod:
    index: int           # 0-based period number
    start_age: int       # age at which this period begins
    end_age: int         # age at which this period ends (inclusive)
    palace_branch: Branch
    palace_name: str

    @property
    def branch_name(self) -> str:
        return BRANCHES[self.palace_branch]


def _is_clockwise(lunar_year: int, is_male: bool) -> bool:
    """
    Determine if the major periods progress clockwise (順行) or not.

    Rules:
    - 陽年 (even stem) male  → clockwise (順)
    - 陽年 female            → counterclockwise (逆)
    - 陰年 male              → counterclockwise (逆)
    - 陰年 female            → clockwise (順)
    """
    yang_year = int(year_stem(lunar_year)) % 2 == 0
    return yang_year == is_male


def major_periods(
    ming: Branch,
    ju: WuXingJu,
    lunar_year: int,
    is_male: bool,
    first_period_age: int = 2,
    count: int = 12,
) -> list[MajorPeriod]:
    """
    Generate a list of 大限 periods.

    first_period_age: approximated starting age of the first period.
    Exact calculation requires solar-term distance; this defaults to N//2
    for simplicity and should be overridden when the caller supplies the
    real value from solar-term counting.
    """
    n = int(ju)
    clockwise = _is_clockwise(lunar_year, is_male)
    direction = 1 if clockwise else -1

    periods: list[MajorPeriod] = []
    # First period starts at the palace AFTER 命宮 in the chosen direction
    start_branch = Branch((int(ming) + direction + 12) % 12)

    for i in range(count):
        branch = Branch((int(start_branch) + direction * i + 12) % 12)
        # Determine palace name by finding the offset from 命宮
        offset = (int(ming) - int(branch) + 12) % 12
        name = PALACE_NAMES[offset]
        age_start = first_period_age + i * n
        age_end = age_start + n - 1
        periods.append(MajorPeriod(
            index=i,
            start_age=age_start,
            end_age=age_end,
            palace_branch=branch,
            palace_name=name,
        ))

    return periods


def annual_palace(ming: Branch, current_age: int, is_male: bool, lunar_year: int) -> Branch:
    """
    Return the 流年命宮 branch for a given age.

    The annual life palace cycles from the first major period palace forward
    by one palace per year.
    """
    clockwise = _is_clockwise(lunar_year, is_male)
    direction = 1 if clockwise else -1
    start_branch = Branch((int(ming) + direction + 12) % 12)
    return Branch((int(start_branch) + direction * (current_age - 1) + 12) % 12)
