"""Star placement for the 14 major stars (十四主星)."""

import math
from .constants import Branch, WuXingJu

# Offsets of 紫微 group stars relative to 紫微, going counterclockwise (decreasing branch)
_ZIWEI_GROUP: dict[str, int] = {
    "紫微": 0,
    "天機": -1,
    "太陽": -3,
    "武曲": -4,
    "天同": -5,
    "廉貞": -8,
}

# Offsets of 天府 group stars relative to 天府, going counterclockwise
_TIANFU_GROUP: dict[str, int] = {
    "天府": 0,
    "太陰": -1,
    "貪狼": -2,
    "巨門": -3,
    "天相": -4,
    "天梁": -5,
    "七殺": -6,
    "破軍": -10,
}


def ziwei_branch(birth_day: int, ju: WuXingJu) -> Branch:
    """
    Calculate the branch where 紫微星 resides.

    Algorithm: starting from 辰, move clockwise by ceil(birth_day / N) - 1 steps.
    Days that don't fall exactly on a multiple of N share a palace with the
    preceding exact multiple — this is the traditional behaviour.
    """
    n = int(ju)
    k = math.ceil(birth_day / n)
    return Branch((int(Branch.CHEN) + k - 1) % 12)


def tianfu_branch(ziwei: Branch) -> Branch:
    """
    天府 mirrors 紫微 across the 午-子 axis.
    Formula: (午 - (紫微 - 子)) mod 12 = (6 - ziwei + 12) mod 12
    """
    return Branch((6 - int(ziwei) + 12) % 12)


def place_major_stars(birth_day: int, ju: WuXingJu) -> dict[str, Branch]:
    """Return a mapping of major star name → branch."""
    zw = ziwei_branch(birth_day, ju)
    tf = tianfu_branch(zw)

    result: dict[str, Branch] = {}

    for star, offset in _ZIWEI_GROUP.items():
        result[star] = Branch((int(zw) + offset + 12) % 12)

    for star, offset in _TIANFU_GROUP.items():
        result[star] = Branch((int(tf) + offset + 12) % 12)

    return result
