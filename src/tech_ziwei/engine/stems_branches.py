"""干支 (Heavenly Stems and Earthly Branches) calculations."""

from .constants import Branch, Stem, STEMS, BRANCHES

# Year stem at 寅宮 based on year stem (甲/己→丙, 乙/庚→戊, 丙/辛→庚, 丁/壬→壬, 戊/癸→甲)
_YIN_STEM_BY_YEAR_STEM: list[int] = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]


def year_stem(lunar_year: int) -> Stem:
    return Stem((lunar_year - 4) % 10)


def year_branch(lunar_year: int) -> Branch:
    return Branch((lunar_year - 4) % 12)


def hour_branch(hour: int, minute: int = 0) -> Branch:
    """Convert local time hour to 時辰 branch (子時 spans 23:00–01:00)."""
    total_minutes = hour * 60 + minute
    # Normalise into 0–1439; 子時 starts at 23:00 = 1380 min
    shi_index = (total_minutes + 60) // 120 % 12
    return Branch(shi_index)


def palace_stem(branch: Branch, lunar_year: int) -> Stem:
    """Return the Heavenly Stem assigned to a given palace branch for a lunar year."""
    ys = year_stem(lunar_year)
    yin_stem = _YIN_STEM_BY_YEAR_STEM[ys]
    # Stems go clockwise (increasing branch) from 寅
    offset = (int(branch) - int(Branch.YIN) + 12) % 12
    return Stem((yin_stem + offset) % 10)


def stem_name(stem: Stem) -> str:
    return STEMS[stem]


def branch_name(branch: Branch) -> str:
    return BRANCHES[branch]


def jiazi_name(stem: Stem, branch: Branch) -> str:
    return f"{stem_name(stem)}{branch_name(branch)}"
