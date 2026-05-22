from enum import IntEnum

STEMS: list[str] = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES: list[str] = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# Palace names in counterclockwise order starting from 命宮
PALACE_NAMES: list[str] = [
    "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
    "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
]

# 14 major star names
MAJOR_STARS: list[str] = [
    "紫微", "天機", "太陽", "武曲", "天同", "廉貞",
    "天府", "太陰", "貪狼", "巨門", "天相", "天梁", "七殺", "破軍",
]


class Branch(IntEnum):
    ZI = 0
    CHOU = 1
    YIN = 2
    MAO = 3
    CHEN = 4
    SI = 5
    WU = 6
    WEI = 7
    SHEN = 8
    YOU = 9
    XU = 10
    HAI = 11


class Stem(IntEnum):
    JIA = 0
    YI = 1
    BING = 2
    DING = 3
    WU = 4
    JI = 5
    GENG = 6
    XIN = 7
    REN = 8
    GUI = 9


class WuXingJu(IntEnum):
    WATER = 2   # 水二局
    WOOD = 3    # 木三局
    METAL = 4   # 金四局
    EARTH = 5   # 土五局
    FIRE = 6    # 火六局


# Nayin element → 五行局 value
NAYIN_TO_JU: dict[str, WuXingJu] = {
    "水": WuXingJu.WATER,
    "木": WuXingJu.WOOD,
    "金": WuXingJu.METAL,
    "土": WuXingJu.EARTH,
    "火": WuXingJu.FIRE,
}
