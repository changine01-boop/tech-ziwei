"""Palace (宮位) positioning logic."""

from dataclasses import dataclass, field

from .constants import Branch, Stem, WuXingJu, PALACE_NAMES, BRANCHES, STEMS
from .stems_branches import palace_stem, year_stem
from .nayin import wu_xing_ju


@dataclass
class Palace:
    branch: Branch
    stem: Stem
    name: str
    stars: list[str] = field(default_factory=list)

    @property
    def branch_name(self) -> str:
        return BRANCHES[self.branch]

    @property
    def stem_name(self) -> str:
        return STEMS[self.stem]

    def __repr__(self) -> str:
        return f"Palace({self.name} @ {self.stem_name}{self.branch_name}, stars={self.stars})"


def ming_branch(lunar_month: int, hour_branch: Branch) -> Branch:
    """
    Calculate the 命宮 (Life Palace) branch.

    Rule: from 寅 count forward by lunar month, then backward by hour branch.
    Formula: (寅 + month - 1 - hour_branch) mod 12
    """
    return Branch((int(Branch.YIN) + lunar_month - 1 - int(hour_branch) + 12) % 12)


def build_palaces(ming: Branch, lunar_year: int) -> dict[Branch, Palace]:
    """
    Build all 12 palaces, assigning names counterclockwise from 命宮
    and stems based on the year's 寅宮 starting stem.
    """
    palaces: dict[Branch, Palace] = {}
    for i, name in enumerate(PALACE_NAMES):
        branch = Branch((int(ming) - i + 12) % 12)
        stem = palace_stem(branch, lunar_year)
        palaces[branch] = Palace(branch=branch, stem=stem, name=name)
    return palaces


def ming_wu_xing_ju(ming: Branch, lunar_year: int) -> WuXingJu:
    """Return the 五行局 for the 命宮."""
    stem = palace_stem(ming, lunar_year)
    return wu_xing_ju(stem, ming)
