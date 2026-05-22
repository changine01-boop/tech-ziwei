"""Tests for palace positioning logic."""

import pytest
from tech_ziwei.engine.constants import Branch, WuXingJu
from tech_ziwei.engine.palace import ming_branch, build_palaces, ming_wu_xing_ju


class TestMingBranch:
    def test_month1_zi_hour_is_yin(self):
        # 寅月(month=1) 子時(hour_branch=子=0) → 命宮=寅
        result = ming_branch(lunar_month=1, hour_branch=Branch.ZI)
        assert result == Branch.YIN

    def test_month1_wu_hour_is_zi(self):
        # 月1 午時 → (寅+0 - 午6 +12)%12 = (2-6+12)%12 = 8 = 申?
        # Let's compute: (2 + 1 - 1 - 6 + 12) % 12 = (8) % 12 = 8 = 申
        result = ming_branch(lunar_month=1, hour_branch=Branch.WU)
        assert result == Branch.SHEN

    def test_month6_zi_hour(self):
        # (2 + 6 - 1 - 0) % 12 = 7 = 未
        result = ming_branch(lunar_month=6, hour_branch=Branch.ZI)
        assert result == Branch.WEI

    def test_ming_covers_all_12_branches(self):
        results = set()
        for month in range(1, 13):
            for hour_b in Branch:
                results.add(ming_branch(month, hour_b))
        assert len(results) == 12


class TestBuildPalaces:
    def test_twelve_palaces_built(self):
        palaces = build_palaces(Branch.YIN, 2024)
        assert len(palaces) == 12

    def test_ming_at_yin_is_ming_gong(self):
        palaces = build_palaces(Branch.YIN, 2024)
        assert palaces[Branch.YIN].name == "命宮"

    def test_counterclockwise_order(self):
        # 命宮=寅, 兄弟宮=(寅-1)=丑, 夫妻宮=(寅-2)=子
        palaces = build_palaces(Branch.YIN, 2024)
        assert palaces[Branch.CHOU].name == "兄弟宮"
        assert palaces[Branch.ZI].name == "夫妻宮"
        assert palaces[Branch.MAO].name == "父母宮"

    def test_all_palace_names_assigned(self):
        palaces = build_palaces(Branch.ZI, 2024)
        names = {p.name for p in palaces.values()}
        from tech_ziwei.engine.constants import PALACE_NAMES
        assert names == set(PALACE_NAMES)


class TestMingWuXingJu:
    def test_returns_wu_xing_ju_instance(self):
        # 命宮=寅, 甲年 → stem=丙, branch=寅 → 丙寅 爐中火 → 火六局
        ju = ming_wu_xing_ju(Branch.YIN, 2024)
        assert ju == WuXingJu.FIRE

    def test_different_years_give_different_ju(self):
        # Different year stems produce different palace stems → different 五行局
        ju_2024 = ming_wu_xing_ju(Branch.YIN, 2024)
        ju_2025 = ming_wu_xing_ju(Branch.YIN, 2025)
        assert ju_2024 != ju_2025
