"""Tests for stems_branches module."""

import pytest
from tech_ziwei.engine.constants import Branch, Stem
from tech_ziwei.engine.stems_branches import (
    year_stem, year_branch, hour_branch, palace_stem
)


class TestYearStemBranch:
    def test_2024_is_jiachen(self):
        # 2024 = 甲辰年
        assert year_stem(2024) == Stem.JIA
        assert year_branch(2024) == Branch.CHEN

    def test_1984_is_jiazi(self):
        # 1984 = 甲子年
        assert year_stem(1984) == Stem.JIA
        assert year_branch(1984) == Branch.ZI

    def test_2023_is_guimao(self):
        # 2023 = 癸卯年
        assert year_stem(2023) == Stem.GUI
        assert year_branch(2023) == Branch.MAO

    def test_cycle_repeats_every_60(self):
        assert year_stem(1924) == year_stem(1984)
        assert year_branch(1924) == year_branch(1984)


class TestHourBranch:
    @pytest.mark.parametrize("hour,expected", [
        (0,  Branch.ZI),    # 子時 23:00–01:00
        (23, Branch.ZI),    # 子時
        (1,  Branch.CHOU),  # 丑時 01:00–03:00
        (2,  Branch.CHOU),  # 丑時
        (3,  Branch.YIN),   # 寅時 03:00–05:00
    ])
    def test_hour_to_branch(self, hour: int, expected: Branch):
        assert hour_branch(hour) == expected

    def test_noon_is_wu(self):
        assert hour_branch(12) == Branch.WU

    def test_midnight_is_zi(self):
        assert hour_branch(0) == Branch.ZI

    def test_23_is_zi(self):
        assert hour_branch(23) == Branch.ZI


class TestPalaceStem:
    def test_jia_year_yin_palace_is_bing(self):
        # 甲年: 寅宮 stem = 丙
        assert palace_stem(Branch.YIN, 2024) == Stem.BING  # 2024=甲辰年

    def test_jia_year_mao_palace_is_ding(self):
        # 甲年: 卯宮 stem = 丁
        assert palace_stem(Branch.MAO, 2024) == Stem.DING

    def test_yi_year_yin_palace_is_wu(self):
        # 乙年: 寅宮 stem = 戊
        assert palace_stem(Branch.YIN, 2025) == Stem.WU  # 2025=乙巳年

    def test_bing_year_yin_palace_is_geng(self):
        # 丙年: 寅宮 stem = 庚
        assert palace_stem(Branch.YIN, 2026) == Stem.GENG
