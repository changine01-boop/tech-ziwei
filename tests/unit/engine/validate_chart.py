"""
validate_chart.py — cross-validates iztro_py adapter against iztro JS (authoritative).

Compares for 6 test birth dates:
  - 命宮地支
  - 五行局
  - 14 主星位置（by 地支）
  - 四化落點（star_name → mutagen）

Run:
  cd /path/to/tech-ziwei
  PYTHONPATH=src python tests/unit/engine/validate_chart.py

Requires:
  - iztro-py installed in environment
  - Node.js with iztro installed at /tmp/iztro_verify/node_modules/iztro
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, time

sys.path.insert(0, "src")

from tech_ziwei.engine.iztro_adapter import build_iztro_chart

_JS_REF = "/tmp/iztro_verify/ref_json.js"

# Earthly branch zh-TW → int (canonical order)
_BRANCH_ORDER = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 6 test cases: (label, solar_date, hour, minute, is_male)
TEST_CASES: list[tuple[str, date, int, int, bool]] = [
    ("1990-01-01 08:00 男", date(1990, 1, 1),  8,  0, True),
    ("1985-07-20 14:00 女", date(1985, 7, 20), 14,  0, False),
    ("2000-02-05 02:00 男", date(2000, 2, 5),   2,  0, True),
    ("1975-11-30 20:00 女", date(1975, 11, 30), 20,  0, False),
    ("1998-09-09 00:30 男", date(1998, 9, 9),   0, 30, True),
    ("1965-04-05 06:00 女", date(1965, 4, 5),   6,  0, False),
]

# Mutagen normalisation (simplified → traditional, for JS output)
_MU_NORM = {"禄": "祿", "权": "權", "科": "科", "忌": "忌"}


# ── JS reference helper ────────────────────────────────────────────────────

def _js_chart(solar_date: date, time_index: int, is_male: bool) -> dict:
    gender = "male" if is_male else "female"
    result = subprocess.run(
        ["node", _JS_REF, solar_date.isoformat(), str(time_index), gender, "true"],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def _js_to_branch_stars(js_data: dict) -> dict[str, list[str]]:
    """branch_zh → sorted list of major-star zh names."""
    out: dict[str, list[str]] = {}
    for p in js_data["palaces"]:
        branch = p["earthlyBranch"]  # already zh-TW '酉' etc.
        out[branch] = sorted(s["name"] for s in p["majorStars"])
    return out


def _js_to_mutagens(js_data: dict) -> dict[str, str]:
    """star_name → mutagen (traditional) for all stars with 四化."""
    out: dict[str, str] = {}
    for p in js_data["palaces"]:
        for s in p["majorStars"] + p["minorStars"]:
            if s.get("mutagen"):
                out[s["name"]] = _MU_NORM.get(s["mutagen"], s["mutagen"])
    return out


def _js_to_ming_branch(js_data: dict) -> str:
    for p in js_data["palaces"]:
        if p["name"] == "命宮":
            return p["earthlyBranch"]
    raise ValueError("命宮 not found in JS output")


# ── iztro_py adapter helper ────────────────────────────────────────────────

def _py_to_branch_stars(chart_data) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for branch_int in range(12):
        branch_zh = _BRANCH_ORDER[branch_int]
        stars = sorted(
            n for n, b in chart_data.star_placements.items() if b == branch_int
        )
        out[branch_zh] = stars
    return out


# ── Diff printer ───────────────────────────────────────────────────────────

def _diff_dicts(label: str, expected: dict, actual: dict, key_label: str = "key") -> list[str]:
    diffs = []
    all_keys = sorted(set(expected) | set(actual))
    for k in all_keys:
        e, a = expected.get(k), actual.get(k)
        if e != a:
            diffs.append(f"  {key_label}={k!r}: JS={e!r}  PY={a!r}")
    if diffs:
        print(f"\n  [DIFF] {label}")
        for d in diffs:
            print(d)
    return diffs


# ── Main validation loop ───────────────────────────────────────────────────

def validate() -> bool:
    all_pass = True
    print("=" * 60)
    print("iztro-py adapter validation  (iztro JS = authoritative)")
    print("=" * 60)

    for label, sol_date, hour, minute, is_male in TEST_CASES:
        print(f"\n▶ {label}")

        # ── Python adapter ─────────────────────────────────────────────
        py_chart = build_iztro_chart(
            gregorian_date=sol_date,
            birth_time=time(hour, minute),
            is_male=is_male,
        )
        # time_index for JS = same as what adapter computed internally
        from tech_ziwei.engine.stems_branches import hour_branch
        time_idx = int(hour_branch(hour, minute))

        # ── JS reference ────────────────────────────────────────────────
        js_data = _js_chart(sol_date, time_idx, is_male)

        case_diffs: list[str] = []

        # 1. 五行局
        js_ju = js_data["fiveElementsClass"]
        py_ju = py_chart.five_elements_class
        if js_ju != py_ju:
            case_diffs.append(f"  [DIFF] 五行局: JS={js_ju!r}  PY={py_ju!r}")
            print(case_diffs[-1])
        else:
            print(f"  五行局: {py_ju}  ✓")

        # 2. 命宮地支
        js_ming = _js_to_ming_branch(js_data)
        py_ming = _BRANCH_ORDER[py_chart.ming_branch]
        if js_ming != py_ming:
            case_diffs.append(f"  [DIFF] 命宮: JS={js_ming!r}  PY={py_ming!r}")
            print(case_diffs[-1])
        else:
            print(f"  命宮地支: {py_ming}  ✓")

        # 3. 14 主星位置
        js_stars = _js_to_branch_stars(js_data)
        py_stars = _py_to_branch_stars(py_chart)
        star_diffs = _diff_dicts("主星位置 (branch → stars)", js_stars, py_stars, "地支")
        case_diffs.extend(star_diffs)

        # 4. 四化落點
        js_mu = _js_to_mutagens(js_data)
        py_mu = py_chart.mutagens()
        mu_diffs = _diff_dicts("四化 (star → mutagen)", js_mu, py_mu, "星")
        case_diffs.extend(mu_diffs)

        if not case_diffs:
            print("  → ALL PASS ✓")
        else:
            print(f"  → {len(case_diffs)} difference(s) found ✗")
            all_pass = False

    print("\n" + "=" * 60)
    if all_pass:
        print("RESULT: ALL 6 TEST CASES PASSED ✓")
    else:
        print("RESULT: VALIDATION FAILED — fix adapter before wiring into pipeline ✗")
    print("=" * 60)
    return all_pass


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
