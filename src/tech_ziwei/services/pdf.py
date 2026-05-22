"""PDF report generation using fpdf2."""

import io
from pathlib import Path

from fpdf import FPDF

from tech_ziwei.engine.constants import BRANCHES, PALACE_NAMES, STEMS, WuXingJu
from tech_ziwei.engine.stems_branches import palace_stem
from tech_ziwei.engine.constants import Branch
from tech_ziwei.models.chart import Chart
from tech_ziwei.models.reading import Reading

_CJK_FONT_PATH = "/System/Library/Fonts/PingFang.ttc"
_HAS_CJK = Path(_CJK_FONT_PATH).exists()

_WU_XING_LABELS: dict[int, str] = {
    2: "Water 2  (水二局)",
    3: "Wood 3   (木三局)",
    4: "Metal 4  (金四局)",
    5: "Earth 5  (土五局)",
    6: "Fire 6   (火六局)",
}

_READING_LABELS: dict[str, str] = {
    "core":         "Core Personality",
    "relationship": "Relationship Patterns",
    "career":       "Career & Purpose",
    "annual":       "Current Period",
}

# Violet-700 used throughout
_VIOLET = (109, 40, 217)
_VIOLET_LIGHT = (237, 233, 254)
_GRAY = (243, 244, 246)


class _PDF(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(20, 20, 20)
        if _HAS_CJK:
            self.add_font("CJK", "", _CJK_FONT_PATH)

    def _font(self, size: int) -> None:
        if _HAS_CJK:
            self.set_font("CJK", "", size)
        else:
            self.set_font("Helvetica", "", size)

    def header(self) -> None:
        # Purple header band
        self.set_fill_color(*_VIOLET)
        self.rect(0, 0, 210, 26, style="F")
        self.set_text_color(255, 255, 255)
        self._font(15)
        self.set_xy(20, 6)
        self.cell(0, 8, "Tech Zi Wei")
        self._font(8)
        self.set_xy(20, 15)
        self.cell(0, 5, "Zi Wei Dou Shu  |  Psychological Astrology Report")
        self.set_text_color(0, 0, 0)
        self.set_xy(20, 30)

    def footer(self) -> None:
        self.set_y(-14)
        self._font(8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def section_header(self, title: str) -> None:
        self.ln(3)
        self.set_fill_color(*_VIOLET_LIGHT)
        self.set_text_color(*_VIOLET)
        self._font(10)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self._font(9)
        self.ln(2)

    def kv_row(self, label: str, value: str) -> None:
        self._font(8)
        self.set_text_color(100, 100, 100)
        self.cell(52, 6, label)
        self.set_text_color(30, 30, 30)
        self._font(9)
        self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")

    def th(self, *cols: tuple[str, float]) -> None:
        self.set_fill_color(*_GRAY)
        self._font(8)
        self.set_text_color(80, 80, 80)
        for text, w in cols:
            self.cell(w, 7, text, border=1, fill=True)
        self.ln()
        self.set_text_color(0, 0, 0)
        self._font(9)

    def td(self, *cols: tuple[str, float]) -> None:
        for text, w in cols:
            self.cell(w, 6.5, text, border="LRB")
        self.ln()


def _year_ganzhi(chart: Chart) -> str:
    return f"{STEMS[chart.year_stem]}{BRANCHES[chart.year_branch]}"


def _ming_ganzhi(chart: Chart) -> str:
    stem = palace_stem(Branch(chart.ming_branch), chart.lunar_year)
    return f"{STEMS[stem]}{BRANCHES[chart.ming_branch]}"


def _build_palaces(chart: Chart) -> list[dict]:
    """Return list of palace dicts in counterclockwise order from 命宮."""
    branch_stars: dict[int, list[str]] = {}
    for star, branch in chart.star_placements.items():
        branch_stars.setdefault(branch, []).append(star)

    result = []
    for i, name in enumerate(PALACE_NAMES):
        branch = (chart.ming_branch - i) % 12
        stem = palace_stem(Branch(branch), chart.lunar_year)
        result.append({
            "name": name,
            "branch": branch,
            "ganzhi": f"{STEMS[stem]}{BRANCHES[branch]}",
            "stars": "  ".join(branch_stars.get(branch, [])) or "—",
        })
    return result


def _birth_info(pdf: _PDF, chart: Chart, email: str) -> None:
    lunar_date = (
        f"{chart.lunar_year}/{chart.lunar_month}/{chart.lunar_day}"
        + ("  (leap month)" if chart.is_leap_month else "")
    )
    pdf.kv_row("Email:", email)
    pdf.kv_row("Date of Birth:", str(chart.gregorian_date))
    pdf.kv_row("Time of Birth:", str(chart.birth_time)[:5])
    pdf.kv_row("Gender:", "Male" if chart.is_male else "Female")
    pdf.kv_row("Lunar Date:", lunar_date)
    pdf.kv_row("Year (年):", _year_ganzhi(chart))
    pdf.kv_row("Five Element Set (五行局):", _WU_XING_LABELS.get(chart.wu_xing_ju, str(chart.wu_xing_ju)))
    pdf.kv_row("Life Palace (命宮):", f"{_ming_ganzhi(chart)}  {PALACE_NAMES[0]}")


def _palace_table(pdf: _PDF, chart: Chart) -> None:
    pdf.th(("Palace (宮)", 42), ("Ganzhi (干支)", 22), ("Stars (主星)", 106))
    for p in _build_palaces(chart):
        is_ming = p["name"] == "命宮"
        if is_ming:
            pdf.set_fill_color(*_VIOLET_LIGHT)
        pdf.cell(42, 6.5, p["name"], border="LRB", fill=is_ming)
        pdf.cell(22, 6.5, p["ganzhi"], border="LRB", fill=is_ming)
        pdf.cell(106, 6.5, p["stars"], border="LRB", fill=is_ming)
        pdf.ln()
        if is_ming:
            pdf.set_fill_color(*_GRAY)


def _periods_table(pdf: _PDF, chart: Chart) -> None:
    pdf.th(("Period (大限)", 30), ("Age Range", 30), ("Palace", 50), ("Branch (宮位)", 60))
    for p in chart.major_periods:
        palace_name = p.get("palace_name", "")
        branch = p.get("palace_branch", 0)
        pdf.td(
            (f"#{p.get('index', 0) + 1}", 30),
            (f"{p.get('start_age')}–{p.get('end_age')}", 30),
            (palace_name, 50),
            (BRANCHES[branch], 60),
        )


def generate_chart_pdf(chart: Chart, readings: list[Reading], email: str) -> bytes:
    """Generate a complete PDF report. Returns raw bytes."""
    pdf = _PDF()
    pdf.add_page()

    pdf.section_header("Birth Information")
    _birth_info(pdf, chart, email)

    pdf.section_header("The 12 Palaces  (十二宮)")
    _palace_table(pdf, chart)

    if chart.major_periods:
        pdf.section_header("Major Life Periods  (大限)")
        _periods_table(pdf, chart)

    for reading in readings:
        if not reading.content:
            continue
        label = _READING_LABELS.get(reading.reading_type.value, reading.reading_type.value)
        pdf.add_page()
        pdf.section_header(label)
        pdf._font(9)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 5.5, reading.content, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)

    return bytes(pdf.output())
