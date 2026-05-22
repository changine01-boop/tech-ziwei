"""Tests for star placement — verified against reference charts."""

import pytest
from tech_ziwei.engine.constants import Branch, WuXingJu, MAJOR_STARS
from tech_ziwei.engine.stars import ziwei_branch, tianfu_branch, place_major_stars


class TestZiweiPosition:
    """
    Reference: 水二局 starting from 辰, moving clockwise one step per
    two birth days.
    """

    @pytest.mark.parametrize("day,ju,expected", [
        (1, WuXingJu.WATER, Branch.CHEN),   # ceil(1/2)=1 → 辰+0=辰
        (2, WuXingJu.WATER, Branch.CHEN),   # ceil(2/2)=1 → 辰+0=辰
        (3, WuXingJu.WATER, Branch.SI),     # ceil(3/2)=2 → 辰+1=巳
        (4, WuXingJu.WATER, Branch.SI),
        (1, WuXingJu.WOOD,  Branch.CHEN),   # ceil(1/3)=1 → 辰
        (3, WuXingJu.WOOD,  Branch.CHEN),   # ceil(3/3)=1 → 辰
        (4, WuXingJu.WOOD,  Branch.SI),     # ceil(4/3)=2 → 巳
        (1, WuXingJu.FIRE,  Branch.CHEN),   # ceil(1/6)=1 → 辰
        (6, WuXingJu.FIRE,  Branch.CHEN),   # ceil(6/6)=1 → 辰
        (7, WuXingJu.FIRE,  Branch.SI),     # ceil(7/6)=2 → 巳
        (15, WuXingJu.EARTH, Branch.WU),    # ceil(15/5)=3 → 辰+2=午
    ])
    def test_ziwei_position(self, day: int, ju: WuXingJu, expected: Branch):
        assert ziwei_branch(day, ju) == expected


class TestTianfuPosition:
    """天府 mirrors 紫微 across the 午-子 axis: 天府 = (6 - ziwei) % 12"""

    @pytest.mark.parametrize("ziwei,expected_tianfu", [
        (Branch.ZI, Branch.WU),    # 子 → 午
        (Branch.CHOU, Branch.SI),  # 丑 → 巳
        (Branch.YIN, Branch.CHEN), # 寅 → 辰
        (Branch.MAO, Branch.MAO),  # 卯 → 卯
        (Branch.CHEN, Branch.YIN), # 辰 → 寅
        (Branch.WU, Branch.ZI),    # 午 → 子
        (Branch.SHEN, Branch.XU),  # 申 → 戌
    ])
    def test_tianfu_position(self, ziwei: Branch, expected_tianfu: Branch):
        assert tianfu_branch(ziwei) == expected_tianfu


class TestMajorStarPlacements:
    def test_returns_all_14_stars(self):
        placements = place_major_stars(15, WuXingJu.WATER)
        assert set(placements.keys()) == set(MAJOR_STARS)

    def test_ziwei_at_zi_reference_chart(self):
        """
        Reference: when 紫微=子(0), well-known star layout.
        紫微 group: 子=紫微, 亥=天機, 酉=太陽, 申=武曲, 未=天同, 辰=廉貞
        天府 group (天府=午): 午=天府, 巳=太陰, 辰=貪狼, 卯=巨門,
                              寅=天相, 丑=天梁, 子=七殺, 申=破軍
        """
        # birth_day=17, 水二局: ceil(17/2)=9 → 辰+8=子(0)
        p = place_major_stars(17, WuXingJu.WATER)
        assert p["紫微"] == Branch.ZI
        assert p["天機"] == Branch.HAI
        assert p["太陽"] == Branch.YOU
        assert p["武曲"] == Branch.SHEN
        assert p["天同"] == Branch.WEI
        assert p["廉貞"] == Branch.CHEN
        assert p["天府"] == Branch.WU
        assert p["太陰"] == Branch.SI
        assert p["貪狼"] == Branch.CHEN
        assert p["巨門"] == Branch.MAO
        assert p["天相"] == Branch.YIN
        assert p["天梁"] == Branch.CHOU
        assert p["七殺"] == Branch.ZI
        assert p["破軍"] == Branch.SHEN

    def test_no_star_placed_outside_12_branches(self):
        for day in range(1, 31):
            for ju in WuXingJu:
                p = place_major_stars(day, ju)
                for branch in p.values():
                    assert 0 <= int(branch) <= 11
