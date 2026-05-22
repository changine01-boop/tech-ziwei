"""Public preview endpoint — no auth required."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import date, time

from tech_ziwei.engine import BirthData, calculate
from tech_ziwei.engine.constants import BRANCHES, STEMS
from tech_ziwei.ai.prompts import STAR_ARCHETYPES

router = APIRouter(prefix="/preview", tags=["preview"])

_WU_XING_JU_LABELS: dict[int, str] = {
    2: "水二局",
    3: "木三局",
    4: "金四局",
    5: "土五局",
    6: "火六局",
}

_HOOKS: dict[str, str] = {
    "紫微": (
        "Your Life Palace holds the Authority Archetype — a natural centre of gravity that "
        "draws others toward your leadership energy, whether or not you actively seek it. "
        "Unlock your full reading to discover how this shapes every domain of your life."
    ),
    "天機": (
        "Your Life Palace carries the Strategic Mind — a restless, pattern-sensing intelligence "
        "that sees systems and possibilities others routinely miss. "
        "Your full reading reveals how to channel this gift without burning out on over-analysis."
    ),
    "太陽": (
        "Your Life Palace radiates the Solar Drive — an energy oriented toward public contribution, "
        "visibility, and meaningful impact. "
        "Your full reading maps where this radiance shines brightest and where it may need tending."
    ),
    "武曲": (
        "Your Life Palace holds the Boundary-Setter — decisive, results-focused, and deeply honest "
        "about accountability and resources. "
        "Your full reading shows how this energy shapes your finances, career, and closest relationships."
    ),
    "天同": (
        "Your Life Palace carries the Harmony-Seeker — an empathic, pleasure-oriented energy that "
        "values ease, authenticity, and genuine relational warmth. "
        "Unlock your full reading to understand both the gift and the growth edge of this pattern."
    ),
    "廉貞": (
        "Your Life Palace holds the Integrity Fire — a principled, passionate energy that cannot "
        "easily compromise its core values, even when that would be simpler. "
        "Your full reading explores how this fire can illuminate rather than consume."
    ),
    "天府": (
        "Your Life Palace carries the Secure Base — a nurturing, resource-holding energy that "
        "naturally models stability and abundance for those around you. "
        "Your full reading reveals how this pattern plays out in love, work, and your inner world."
    ),
    "太陰": (
        "Your Life Palace holds the Lunar Depth — an intuitive, emotionally intelligent energy "
        "that processes inwardly and finds richness in privacy and reflection. "
        "Your full reading uncovers the extraordinary sensitivity and gifts beneath this quiet surface."
    ),
    "貪狼": (
        "Your Life Palace carries the Appetite for Experience — a creative, multifaceted energy "
        "drawn to beauty, learning, pleasure, and the full spectrum of what life offers. "
        "Your full reading maps how to direct this wide-ranging curiosity toward lasting fulfilment."
    ),
    "巨門": (
        "Your Life Palace holds the Verbal Intelligence — a sharp, truth-seeking communicator with "
        "a gift for cutting through surface appearances to what actually matters. "
        "Your full reading shows how this discernment can be your greatest strength in every arena."
    ),
    "天相": (
        "Your Life Palace carries the Collaborative Diplomat — graceful, empathic, gifted at "
        "facilitating connection and navigating the complexity of relationships. "
        "Unlock your full reading to see how this talent for bridging shapes your deepest patterns."
    ),
    "天梁": (
        "Your Life Palace holds the Elder Wisdom — a philosophically grounded energy that holds "
        "long perspective and naturally guides others toward integrity. "
        "Your full reading reveals the depth of this protective, mentoring quality within you."
    ),
    "七殺": (
        "Your Life Palace carries the Transformative Edge — an intense, action-oriented energy "
        "that breaks old patterns and initiates the changes others hesitate to make. "
        "Your full reading maps how to wield this transformative force with precision and care."
    ),
    "破軍": (
        "Your Life Palace holds the Pioneer Spirit — a boundary-dissolving energy that dismantles "
        "what no longer serves and opens genuinely new frontiers. "
        "Your full reading explores how to work with this fearless energy without destabilising what matters."
    ),
}

_DEFAULT_HOOK = (
    "Your Life Palace reveals a layered, multifaceted personality with rich strengths waiting to be fully understood. "
    "Unlock your complete reading to explore every dimension of who you are."
)


class PreviewRequest(BaseModel):
    gregorian_date: date
    birth_time: time
    is_male: bool
    timezone_offset: float = Field(default=-5.0, ge=-12, le=14)


class PreviewResponse(BaseModel):
    ming_branch: int
    ming_palace_name: str
    ming_ganzhi: str
    main_stars: list[str]
    wu_xing_ju: int
    wu_xing_ju_label: str
    year_ganzhi: str
    hook: str


@router.post("", response_model=PreviewResponse)
async def preview(req: PreviewRequest) -> PreviewResponse:
    try:
        birth = BirthData(
            gregorian_date=req.gregorian_date,
            birth_time=req.birth_time,
            is_male=req.is_male,
            timezone_offset=req.timezone_offset,
        )
        chart = calculate(birth)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chart calculation failed: {exc}",
        )

    ming_branch = int(chart.ming)
    ming_palace = chart.palaces[chart.ming]
    ming_ganzhi = f"{ming_palace.stem_name}{ming_palace.branch_name}"

    main_stars = [s for s, b in chart.star_placements.items() if int(b) == ming_branch]

    wu_xing_ju = int(chart.wu_xing_ju)
    year_ganzhi = f"{STEMS[int(chart.year_stem)]}{BRANCHES[int(chart.year_branch)]}"

    hook = _DEFAULT_HOOK
    for star in main_stars:
        if star in _HOOKS:
            hook = _HOOKS[star]
            break

    return PreviewResponse(
        ming_branch=ming_branch,
        ming_palace_name=ming_palace.name,
        ming_ganzhi=ming_ganzhi,
        main_stars=main_stars,
        wu_xing_ju=wu_xing_ju,
        wu_xing_ju_label=_WU_XING_JU_LABELS.get(wu_xing_ju, ""),
        year_ganzhi=year_ganzhi,
        hook=hook,
    )
