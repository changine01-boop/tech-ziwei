"""Gregorian to Chinese Lunar Calendar conversion."""

from datetime import date
from dataclasses import dataclass

from lunardate import LunarDate as _LunarDate


@dataclass(frozen=True)
class LunarDate:
    year: int
    month: int
    day: int
    is_leap_month: bool = False


def to_lunar(gregorian: date) -> LunarDate:
    """Convert a Gregorian date to Chinese Lunar date."""
    ld = _LunarDate.fromSolarDate(gregorian.year, gregorian.month, gregorian.day)
    return LunarDate(
        year=ld.year,
        month=ld.month,
        day=ld.day,
        is_leap_month=ld.isLeapMonth,
    )
