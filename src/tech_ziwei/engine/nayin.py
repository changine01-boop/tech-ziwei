"""Nayin (納音) five-element lookup and 五行局 determination."""

from .constants import Branch, Stem, WuXingJu, NAYIN_TO_JU

# Nayin element for each (stem_index, branch_index) pair.
# Only valid stem-branch pairings (same parity) are included.
# Format: (stem % 2, branch % 2) → row pattern; exact mapping below.
_NAYIN_TABLE: dict[tuple[int, int], str] = {
    (0, 0): "金",   # 甲子 海中金
    (1, 1): "金",   # 乙丑
    (2, 2): "火",   # 丙寅 爐中火
    (3, 3): "火",   # 丁卯
    (4, 4): "木",   # 戊辰 大林木
    (5, 5): "木",   # 己巳
    (6, 6): "土",   # 庚午 路旁土
    (7, 7): "土",   # 辛未
    (8, 8): "金",   # 壬申 劍鋒金
    (9, 9): "金",   # 癸酉
    (0, 10): "火",  # 甲戌 山頭火
    (1, 11): "火",  # 乙亥
    (2, 0): "水",   # 丙子 澗下水
    (3, 1): "水",   # 丁丑
    (4, 2): "土",   # 戊寅 城頭土
    (5, 3): "土",   # 己卯
    (6, 4): "金",   # 庚辰 白蠟金
    (7, 5): "金",   # 辛巳
    (8, 6): "木",   # 壬午 楊柳木
    (9, 7): "木",   # 癸未
    (0, 8): "水",   # 甲申 泉中水
    (1, 9): "水",   # 乙酉
    (2, 10): "土",  # 丙戌 屋上土
    (3, 11): "土",  # 丁亥
    (4, 0): "火",   # 戊子 霹靂火
    (5, 1): "火",   # 己丑
    (6, 2): "木",   # 庚寅 松柏木
    (7, 3): "木",   # 辛卯
    (8, 4): "水",   # 壬辰 長流水
    (9, 5): "水",   # 癸巳
    (0, 6): "金",   # 甲午 沙中金
    (1, 7): "金",   # 乙未
    (2, 8): "火",   # 丙申 山下火
    (3, 9): "火",   # 丁酉
    (4, 10): "木",  # 戊戌 平地木
    (5, 11): "木",  # 己亥
    (6, 0): "土",   # 庚子 壁上土
    (7, 1): "土",   # 辛丑
    (8, 2): "金",   # 壬寅 金箔金
    (9, 3): "金",   # 癸卯
    (0, 4): "火",   # 甲辰 覆燈火
    (1, 5): "火",   # 乙巳
    (2, 6): "水",   # 丙午 天河水
    (3, 7): "水",   # 丁未
    (4, 8): "土",   # 戊申 大驛土
    (5, 9): "土",   # 己酉
    (6, 10): "金",  # 庚戌 釵釧金
    (7, 11): "金",  # 辛亥
    (8, 0): "木",   # 壬子 桑柘木
    (9, 1): "木",   # 癸丑
    (0, 2): "水",   # 甲寅 大溪水
    (1, 3): "水",   # 乙卯
    (2, 4): "土",   # 丙辰 沙中土
    (3, 5): "土",   # 丁巳
    (4, 6): "火",   # 戊午 天上火
    (5, 7): "火",   # 己未
    (6, 8): "木",   # 庚申 石榴木
    (7, 9): "木",   # 辛酉
    (8, 10): "水",  # 壬戌 大海水
    (9, 11): "水",  # 癸亥
}


def nayin_element(stem: Stem, branch: Branch) -> str:
    key = (int(stem), int(branch))
    if key not in _NAYIN_TABLE:
        raise ValueError(f"Invalid stem-branch pair: {stem!r} {branch!r}")
    return _NAYIN_TABLE[key]


def wu_xing_ju(stem: Stem, branch: Branch) -> WuXingJu:
    """Return the 五行局 for the 命宮's stem-branch combination."""
    element = nayin_element(stem, branch)
    return NAYIN_TO_JU[element]
