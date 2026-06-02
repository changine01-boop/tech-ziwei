"""System prompt and per-reading-type user prompt templates.

Master File is the sole source of truth for module 3/4/5 content.
Do not rename archetypes or edit shadow-work / catalyst copy here —
update the Master File and re-run alignment instead.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Module 3 — Star archetype vocabulary (Master File sole source of truth)
# Short-form used in serializer display; full attrs carried in SYSTEM_PROMPT.
# ---------------------------------------------------------------------------
STAR_ARCHETYPES: dict[str, str] = {
    "紫微": "The Sovereign — Visionary Leadership, High Emotional Resilience, Uncompromised Standards; shadows: Imposter Syndrome, Isolation at the Top",
    "天機": "The Strategist — Hyper-Analytical Processing, Agile Adaptability, Intellectual Curiosity; shadows: Analysis Paralysis, Cognitive Exhaustion",
    "太陽": "The Luminary — Magnetic Charisma, Altruistic Impact, Radical Transparency; shadows: People-Pleasing, Validation Addiction, Burnout",
    "武曲": "The Architect — Unrivaled Execution, Financial Intelligence, Unwavering Integrity; shadows: Emotional Flatness, Rigid Perfectionism",
    "天同": "The Harmonizer — Empathy, Diplomacy, Flow State; shadows: Conflict Avoidance, Complacency, Boundary Erosion",
    "廉貞": "The Maverick — Unconventional Thinking, Intense Passion, Boundary-Pushing; shadows: Volatility, Addiction to Intensity",
    "天府": "The Steward — Resource Management, Risk Mitigation, Operational Excellence; shadows: Hyper-Conservatism, Resource Hoarding",
    "太陰": "The Mystic — Subconscious Depth, Intuition, Aesthetic Appreciation; shadows: Emotional Volatility, Retreating into Fantasy",
    "貪狼": "The Alchemist — Multi-Passionate, Charisma, Desire-Driven Manifestation; shadows: Shiny Object Syndrome, Chronic Dissatisfaction",
    "巨門": "The Analyst — Deep Investigation, Articulate Communication, Radical Skepticism; shadows: Cynicism, Harsh Communication",
    "天相": "The Diplomat — Service-Oriented, Image-Conscious, Loyal; shadows: Identity Chameleon, Indecisiveness",
    "天梁": "The Sage — Mentorship, Crisis Resolution, Traditional Wisdom; shadows: Unsolicited Advice, Martyr Complex",
    "七殺": "The Pioneer — Decisiveness, Courage under Fire, Independent Action; shadows: Impulsivity, Lone-Wolf Syndrome",
    "破軍": "The Catalyst — Destructive Innovation, Fearless Reinvention, Thriving in Chaos; shadows: Reckless Abandonment, Self-Sabotage",
}

# ---------------------------------------------------------------------------
# Palace psychological domain mapping
# ---------------------------------------------------------------------------
PALACE_DOMAINS: dict[str, str] = {
    "命宮":  "core identity and personality foundation",
    "兄弟宮": "sibling dynamics and peer relationships",
    "夫妻宮": "romantic partnerships and attachment patterns",
    "子女宮": "creative legacy and relationship to nurturing",
    "財帛宮": "relationship with resources and abundance mindset",
    "疾厄宮": "body-mind relationship and stress-response style",
    "遷移宮": "adaptability and response to new environments",
    "交友宮": "social patterns and friendship style",
    "官祿宮": "career calling and public role",
    "田宅宮": "sense of home, roots, and psychological safety",
    "福德宮": "inner life, spiritual orientation, and sources of joy",
    "父母宮": "early conditioning and parental imprints",
}

# ---------------------------------------------------------------------------
# Module 4 — Shadow Work lookup table (化忌 → palace → Friction + Advice)
# Source: Master File Spec Pack, 模組四. Do not edit copy here.
# ---------------------------------------------------------------------------
_SHADOW_WORK: dict[str, dict[str, str]] = {
    "命宮": {
        "friction": "Imposter Syndrome, chronic self-doubt",
        "advice": "Practice radical self-acceptance. Write down 3 objective facts daily about what you did well, shifting from 'Am I good enough?' to 'What did I experience?'",
    },
    "財帛宮": {
        "friction": "Scarcity Anxiety, tying self-worth to bank balance",
        "advice": "Build an Abundance Mindset. Make one weekly experiential purchase not tied to ROI",
    },
    "夫妻宮": {
        "friction": "Insecure Attachment Styles, magnifying a partner's flaws out of fear",
        "advice": "Practice Emotional Boundaries. When anxious, pause 10 minutes and ask 'Is this my partner's issue, or my unhealed projection?'",
    },
    "官祿宮": {
        "friction": "Chronic Career Burnout, obsession with finding the 'perfect' vocation",
        "advice": "Start a hobby that cannot be monetized; reclaim your work-life ecosystem",
    },
    "兄弟宮": {
        "friction": "The Comparison Trap, vague boundaries in partnerships",
        "advice": "Practice Compersion (joy for others' success). Always sign clear legal contracts before partnering",
    },
    "子女宮": {
        "friction": "Creation Anxiety, over-controlling projects or children",
        "advice": "Adopt 'Ship it before it's perfect.' Practice emotional detachment from your creations",
    },
    "疾厄宮": {
        "friction": "Somatic Symptom Manifestation from chronic stress",
        "advice": "Stop optimizing your body like a machine. Schedule 15 minutes of daily Nervous System Regulation (e.g. breathwork)",
    },
    "遷移宮": {
        "friction": "Social Evaluation Anxiety, fear of Cancel Culture",
        "advice": "Regular digital detox. Before public speaking, shift from 'How will they judge me?' to 'What value can I provide them?'",
    },
    "交友宮": {
        "friction": "Savior Complex, attracting Energy Vampires",
        "advice": "Filter your network. Tell your team 'This is your task, I trust you can solve it'",
    },
    "田宅宮": {
        "friction": "Anxiety of Belonging, inability to disconnect from work at home",
        "advice": "Create strict Sanctuary Zones (no screens in the bedroom). Declutter physical space to clear mental blocks",
    },
    "福德宮": {
        "friction": "High-Functioning Depression, Arrival Fallacy",
        "advice": "Practice 20 minutes of 'Doing Nothing' daily. Sit with anxiety without trying to solve it",
    },
    "父母宮": {
        "friction": "Authority Projection, rebelling against or over-pleasing bosses",
        "advice": "Reparent your inner child. Remind yourself 'My boss is not my parent; I am an empowered adult'",
    },
}

# ---------------------------------------------------------------------------
# Module 5 — Positive Catalysts lookup tables (化祿 / 化權 / 化科 → palace)
# Source: Master File Spec Pack, 模組五. Do not edit copy here.
# ---------------------------------------------------------------------------
_CATALYSTS_LU: dict[str, str] = {
    "命宮":  "Extreme likability and optimism. You attract opportunities simply by being yourself.",
    "財帛宮": "Effortless monetization. Money flows through networking and joyful creation rather than grueling work.",
    "官祿宮": "Deep passion in your work. You attract mentors and enjoy a smooth career trajectory.",
    "夫妻宮": "Harmonious, expansive relationships. Your partner brings emotional joy and potentially financial luck.",
    "兄弟宮": "Collaboration comes easily — peers want you to win, and your best opportunities arrive through warm introductions.",
    "子女宮": "A natural, generative flow of creative output. What you make delights others; projects bring lightness and joy.",
    "疾厄宮": "A resilient, forgiving constitution. You find ease in rest, pleasure, and sensory enjoyment without guilt.",
    "遷移宮": "The world opens doors when you step out. Travel and new environments bring luck; strangers warm to you fast.",
    "交友宮": "You magnetize a generous, supportive circle. Your network is a source of joy rather than obligation.",
    "田宅宮": "Home and property come with ease and warmth. Family or real estate is a quiet, steady source of fortune.",
    "福德宮": "A baseline of contentment. You find genuine pleasure in small things and recover inner equilibrium faster than most.",
    "父母宮": "Authority figures and mentors are kind to you. Support, blessings, and opportunities come from elders and institutions with surprising ease.",
}

_CATALYSTS_QUAN: dict[str, str] = {
    "命宮":  "A commanding presence. Fierce independence and a subconscious need to dominate your environment.",
    "財帛宮": "Aggressive wealth building. You desire absolute control over your financial assets.",
    "官祿宮": "The drive to be the boss. Rapid climbing, but often clashes with authority above you.",
    "夫妻宮": "Power struggles in romance. You seek a capable partner but risk turning the relationship into a competition.",
    "兄弟宮": "You take the lead among peers and become the organizing force in partnerships — powerful when channeled, controlling when not.",
    "子女宮": "A forceful creative will. You drive projects to completion with strong intention, but watch for over-control.",
    "疾厄宮": "Intense physical drive, but your wellbeing demands the same discipline you give your ambitions — burnout is the failure mode.",
    "遷移宮": "You command rooms and shape situations. You bend environments toward you rather than adapt to them.",
    "交友宮": "You naturally lead your circle and attract people who look to you for direction — watch the line between leading and dominating.",
    "田宅宮": "A drive to build and control your own domain — property, home, the family base. You hold the keys and set the rules.",
    "福德宮": "A powerful inner will and high standards for your own mind, but risk being as hard on yourself as you are driven.",
    "父母宮": "You assert yourself with authority rather than defer. Challenging bosses earns respect when measured, friction when not.",
}

_CATALYSTS_KE: dict[str, str] = {
    "命宮":  "A refined, scholarly aura. Perceived as intellectual, elegant, and highly credible.",
    "財帛宮": "Earning through expertise, teaching, consulting, or personal brand reputation.",
    "官祿宮": "Academic or industry recognition. The 'Subject Matter Expert' in your field.",
    "夫妻宮": "A relationship built on intellectual respect and a refined social image. Your partner elevates your public standing.",
    "兄弟宮": "Known and respected among peers as the credible, articulate one. Your reputation opens doors before you arrive.",
    "子女宮": "Your creative work earns tasteful acclaim. What you produce carries a quality that gets you noticed and quoted.",
    "疾厄宮": "A graceful, composed presence even under strain. You handle health setbacks with dignity; crises rarely dent your image.",
    "遷移宮": "A polished reputation precedes you everywhere. Seen as cultured and trustworthy; your name becomes your passport.",
    "交友宮": "The respected figure others vouch for. Your standing protects you and quietly elevates everyone you associate with.",
    "田宅宮": "Your home and family carry a tasteful, respectable reputation — quiet prestige rather than display.",
    "福德宮": "An inner refinement and a reputation for wisdom. Seen as having depth; that perception becomes a shield in hard times.",
    "父母宮": "You earn the regard of authority figures and carry the credibility of good credentials, lineage, or institutional backing.",
}

# ---------------------------------------------------------------------------
# System prompt (cached with Claude API cache_control)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a psychological astrology interpreter specialising in Zi Wei Dou Shu \
(Purple Star Astrology), translated into the language of contemporary Western \
psychology. Your purpose is to help English-speaking readers in North America \
understand their psychological patterns, strengths, and growth edges through \
the lens of this ancient Chinese system — without mysticism, fatalism, or \
cultural inaccessibility.

## LANGUAGE RULES (non-negotiable)

1. NEVER use fatalistic or deterministic language:
   ✗ "Your destiny is…", "You will definitely…", "This means you are…"
   ✓ "There's a tendency toward…", "You may find that…", "This pattern often \
shows up as…", "One way this energy can express…"

2. Frame every challenge as a growth edge, not a flaw.
3. Use second-person ("you", "your") throughout.
4. Write in warm, accessible English — intelligent but never academic.
5. Avoid Chinese transliterations unless immediately followed by a plain-English \
explanation in parentheses.

## PSYCHOLOGICAL FRAMEWORKS TO DRAW ON

- Jungian archetypes: Shadow, Anima/Animus, Persona, Self-realisation
- Attachment theory: secure, anxious-preoccupied, dismissive-avoidant styles
- Growth-mindset framing (Dweck): fixed vs. growth orientations
- Internal Family Systems: parts, protectors, exiles
- Positive psychology: strengths-based, self-compassion, values clarification

## STAR ARCHETYPES (Module 3 — Master File)

""" + "\n".join(f"- {star}: {desc}" for star, desc in STAR_ARCHETYPES.items()) + """

## PALACE PSYCHOLOGICAL DOMAINS

""" + "\n".join(f"- {palace}: {domain}" for palace, domain in PALACE_DOMAINS.items()) + """

## OUTPUT REQUIREMENTS

- 350–500 words per reading section
- One concrete **Reflection Question** at the end (italicised, starting with \
"*Reflection:*")
- No bullet lists in the main narrative — flowing prose only
- End on an empowering, forward-looking note
"""

# ---------------------------------------------------------------------------
# Per-reading-type user prompt templates
# ---------------------------------------------------------------------------

def core_prompt(context: str) -> str:
    return f"""\
Using the chart context below, write a Core Personality Profile for this person.

Focus on:
1. The energy of the Life Palace (命宮) and its major stars — what psychological \
drives and default patterns do these archetypes suggest?
2. The Five-Element Set (五行局) as a temperament signature — how does this \
shape their fundamental rhythm and pace?
3. Two or three key strengths visible in the chart.
4. One primary growth edge — framed constructively, not as criticism.

CHART CONTEXT:
{context}
"""


def relationship_prompt(context: str) -> str:
    return f"""\
Using the chart context below, write a Relationship Patterns reading.

Focus on:
1. The Spouse/Partnership Palace (夫妻宮) — what energies does this person \
tend to attract or project onto intimate partners?
2. The Friends Palace (交友宮) — social style, what they offer and seek in \
friendship.
3. Attachment style tendencies suggested by the chart.
4. One growth edge around relating — how might they deepen connection?

CHART CONTEXT:
{context}
"""


def career_prompt(context: str) -> str:
    return f"""\
Using the chart context below, write a Career & Life Purpose reading.

Focus on:
1. The Career Palace (官祿宮) — what professional environments and roles \
allow this person to flourish?
2. The Wealth Palace (財帛宮) — their relationship with material resources \
and financial decision-making style.
3. The Fortune/Inner Life Palace (福德宮) — what intrinsic motivations give \
their work meaning beyond status or income?
4. One practical suggestion for aligning current work with their deeper calling.

CHART CONTEXT:
{context}
"""


def annual_prompt(context: str, current_age: int) -> str:
    return f"""\
Using the chart context below, write a Current Period Focus reading for a \
person currently aged {current_age}.

Focus on:
1. The active Major Period (大限) palace and stars — what developmental theme \
is this decade asking them to engage with?
2. How this period differs from (or builds on) their core personality pattern.
3. Two or three practical areas of life where this energy is most likely to \
manifest in concrete ways.
4. An empowering reframe of any challenging aspects of this period.

CHART CONTEXT:
{context}
"""


def shadow_work_prompt(context: str, ji_star: str, ji_palace: str) -> str:
    """Module 4 — Shadow Work section driven by the 化忌 palace."""
    sw = _SHADOW_WORK.get(ji_palace, {})
    friction = sw.get("friction", "unexamined relational patterns")
    advice   = sw.get("advice",   "Bring gentle, daily awareness to this area without forcing resolution")
    domain   = PALACE_DOMAINS.get(ji_palace, ji_palace)

    return f"""\
Using the chart context below, write a Shadow Work section for this person.

The 化忌 (Friction / Growth activation) this year: {ji_star} falls in the \
{ji_palace} palace ({domain}).

Master File Shadow Work framework for {ji_palace}:
  Core Friction : {friction}
  Actionable Advice : {advice}

Write a 350–500 word Shadow Work section that:
1. Opens with the heading "Shadow Work: The {ji_palace} Field" and immediately \
names the palace and its psychological domain.
2. Describes the specific friction pattern in warm, non-judgmental prose — \
use the Core Friction above as the anchor but expand it into lived human experience.
3. Traces the underlying unmet need or unconscious belief driving this pattern.
4. Closes with the Actionable Advice reframed as a concrete, compassionate \
practice the reader can begin this week — specific, not vague.
5. Ends with a *Reflection:* question.

CHART CONTEXT:
{context}
"""


def positive_catalysts_prompt(
    context: str,
    activations: list[tuple[str, str, str]],
) -> str:
    """Module 5 — Positive Catalysts section driven by 化祿/化權/化科 palace activations.

    activations: list of (mutagen_type_zh, star_name, palace_name)
    e.g. [("祿", "武曲", "兄弟宮"), ("權", "貪狼", "子女宮"), ("科", "天梁", "命宮")]
    """
    _LABELS = {"祿": "化祿 (Abundance Catalyst)", "權": "化權 (Power Catalyst)", "科": "化科 (Fame Catalyst)"}
    _TABLE  = {"祿": _CATALYSTS_LU, "權": _CATALYSTS_QUAN, "科": _CATALYSTS_KE}

    lines: list[str] = []
    for mt, star, palace in activations:
        copy = _TABLE.get(mt, {}).get(palace, "")
        if copy:
            label = _LABELS.get(mt, mt)
            domain = PALACE_DOMAINS.get(palace, palace)
            lines.append(f"{label} — {star} → {palace} ({domain}):\n  {copy}")

    catalyst_block = "\n\n".join(lines) if lines else "(No active positive catalysts)"

    return f"""\
Using the chart context below, write a Positive Catalysts section for this person.

Active catalyst activations this year (palace placement from engine — authoritative):
{catalyst_block}

Write a unified 350–500 word Positive Catalysts section that:
1. Opens with a one-sentence orienting statement: what 化祿/化權/化科 collectively \
represent as a year's activation layer.
2. Devotes one clear, flowing paragraph to each active catalyst in the order \
shown above (祿 → 權 → 科), naming the palace, its domain, and the specific gift \
described in the framework above.
3. Closes with an integrating insight — how these three activations might \
reinforce each other or create a coherent developmental theme.
4. Ends with a *Reflection:* question.

CHART CONTEXT:
{context}
"""


PROMPT_BUILDERS: dict[str, object] = {
    "core": core_prompt,
    "relationship": relationship_prompt,
    "career": career_prompt,
    "annual": annual_prompt,
    "shadow_work": shadow_work_prompt,
    "positive_catalysts": positive_catalysts_prompt,
}
