# Tech Zi Wei — CLAUDE.md

## Project Overview

**Tech Zi Wei** is a modern psychological astrology SaaS platform that bridges Eastern and Western wisdom traditions. It translates traditional Zi Wei Dou Shu (紫微斗數, Purple Star Astrology) into contemporary Western psychological language, making Chinese astrology accessible and actionable for the North American English-speaking market.

### Core Value Proposition
- Accurate Zi Wei Dou Shu chart calculation from birth data
- Psychological reframing of traditional Chinese astrological archetypes (e.g., "命宮主星" → personality core, "財帛宮" → resource relationship)
- AI-generated narrative reports in empathetic, non-deterministic language consistent with modern psychology
- Subscription-based access to personal chart insights, transits, and period analysis (大限/流年)

### Target Market
- English-speaking users in North America with interest in astrology, self-discovery, or alternative psychology
- Users familiar with Western astrology (birth charts, houses, archetypes) looking for depth
- Chinese diaspora seeking a culturally authentic but psychologically modern experience

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend API | Python 3.12 + FastAPI | Async, type-annotated, OpenAPI auto-docs |
| Database | PostgreSQL 16 | Via SQLAlchemy 2.0 (async) + Alembic migrations |
| AI/LLM | Anthropic Claude API | Prompt engineering for report generation |
| Auth | JWT + OAuth2 (Google) | FastAPI-Users or custom |
| Cache | Redis | Session cache, rate limiting, report caching |
| Task Queue | Celery + Redis | Async chart calculation and report generation |
| Frontend | TBD (Phase 4) | Likely Next.js or SvelteKit |
| Hosting | TBD | Railway / Render / AWS |
| Testing | pytest + pytest-asyncio | Coverage enforced |

### Key Python Libraries
- `fastapi`, `uvicorn` — API server
- `sqlalchemy[asyncio]`, `alembic` — ORM and migrations
- `asyncpg` — async PostgreSQL driver
- `pydantic v2` — data validation and serialization
- `anthropic` — Claude API client (with prompt caching)
- `ephem` or custom ephemeris — astronomical calculations
- `python-jose` / `passlib` — JWT auth
- `celery`, `redis` — background task processing

---

## Repository Structure (Target)

```
tech-ziwei/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── .env.example
├── alembic/                    # DB migrations
├── src/
│   └── tech_ziwei/
│       ├── main.py             # FastAPI app entry point
│       ├── config.py           # Settings via pydantic-settings
│       ├── database.py         # Async DB session
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       ├── routers/            # FastAPI route modules
│       ├── services/           # Business logic layer
│       ├── engine/             # Phase 1: chart calculation engine
│       ├── ai/                 # Phase 3: prompt engine
│       └── workers/            # Celery tasks
└── tests/
    ├── unit/
    └── integration/
```

---

## Development Phases

### Phase 1 — Chart Calculation Engine (`src/tech_ziwei/engine/`)

**Goal:** Implement a correct, tested Zi Wei Dou Shu chart calculation engine in pure Python.

**Scope:**
- Convert Gregorian birth date/time to Chinese Lunar Calendar (農曆)
- Determine the year's 天干地支 (Heavenly Stems and Earthly Branches)
- Calculate the 命宮 (Life Palace / Ascendant) from birth time
- Place the 14 major stars (十四主星: 紫微, 天機, 太陽, 武曲, 天同, 廉貞, 天府, 太陰, 貪狼, 巨門, 天相, 天梁, 七殺, 破軍)
- Place auxiliary stars (輔星, 煞星, 雜曜)
- Calculate the 12 Palaces (十二宮) with their assigned stars
- Calculate 大限 (10-year Major Periods) and 流年 (Annual Periods)
- Output a structured `Chart` object (Pydantic model)

**Deliverables:**
- `engine/lunar_calendar.py` — Gregorian → Lunar conversion
- `engine/stems_branches.py` — 干支 system
- `engine/palace.py` — Palace positioning logic
- `engine/stars.py` — Star placement algorithms
- `engine/periods.py` — 大限/流年 calculation
- `engine/chart.py` — Top-level `Chart` class
- Unit tests with known-correct reference charts

**Acceptance Criteria:**
- Chart output matches verified reference charts from established Zi Wei software
- All 14 main stars correctly placed for at least 20 test birth dates
- Calculation completes in < 100ms

---

### Phase 2 — Data Layer & API (`models/`, `routers/`, `services/`)

**Goal:** Persist charts, users, and readings; expose them via a clean REST API.

**Scope:**
- User model: registration, login, JWT auth, subscription tier
- Chart model: store calculated charts linked to users
- Reading model: store generated AI reports linked to charts
- API endpoints:
  - `POST /auth/register`, `POST /auth/login`
  - `POST /charts` — calculate and persist chart from birth data
  - `GET /charts/{id}` — retrieve chart with star placements
  - `GET /charts/{id}/report` — trigger or retrieve AI report
  - `GET /users/me` — profile and subscription status
- Alembic migrations for all models
- Rate limiting and auth middleware

**Deliverables:**
- SQLAlchemy models for User, Chart, Reading
- Alembic migration scripts
- FastAPI routers with Pydantic schemas
- Service layer separating business logic from route handlers
- Integration tests against a real test database

---

### Phase 3 — AI Prompt Engine (`src/tech_ziwei/ai/`)

**Goal:** Generate psychologically-framed, personalized narrative reports using Claude.

**Scope:**
- System prompt defining the psychological astrology persona and language rules
  - Avoid fatalistic or deterministic language
  - Use Jungian archetypes, attachment theory, and growth-oriented framing
  - Maintain consistent mapping: Zi Wei terms → English psychological equivalents
- Chart-to-context serializer: convert `Chart` object into structured prompt context
- Report types:
  - Core personality profile (命宮 + major stars)
  - Relationship patterns (夫妻宮, 交友宮)
  - Career and life purpose (官祿宮, 事業宮)
  - Current period focus (流年 overlay)
- Prompt caching for system prompt (Claude API `cache_control`)
- Celery worker for async report generation
- Report stored to DB on completion; webhook/polling for client

**Deliverables:**
- `ai/prompts.py` — system prompt and prompt templates
- `ai/serializer.py` — Chart → prompt context
- `ai/generator.py` — Claude API call with caching
- `workers/report_worker.py` — Celery task
- Prompt test suite: validate output tone and required fields

---

### Phase 4 — Frontend

**Goal:** A polished, conversion-optimized web UI targeting North American users.

**Scope (TBD, to be designed in Phase 4):**
- Landing page with value proposition and demo chart
- Onboarding flow: birth data input → instant chart preview
- Chart visualization: interactive 12-palace grid
- Report display: structured narrative with section navigation
- Account management: subscription, saved charts, history
- Internationalization: English primary, Traditional Chinese secondary

**Framework Decision (deferred):** Next.js (React ecosystem, SSR/SEO) vs. SvelteKit (lighter, faster) — decide based on team skills and SEO requirements at start of Phase 4.

---

## Development Conventions

### Code Style
- Python: `ruff` for linting and formatting (replaces black + flake8 + isort)
- Type annotations required on all function signatures
- No `Any` unless justified with a comment
- Pydantic models for all API boundaries; never pass raw dicts between layers

### Testing
- All business logic in `services/` and `engine/` must have unit tests
- API routes tested via `httpx.AsyncClient` with `pytest-asyncio`
- Never mock the database in integration tests — use a real test PostgreSQL instance
- Target: > 80% coverage on `engine/` and `services/`

### Database
- Always use Alembic for schema changes; never edit the DB directly
- Use async SQLAlchemy sessions throughout; no sync DB calls in async context
- Foreign keys enforced at DB level, not just ORM level

### AI / Claude API
- Always use prompt caching for the system prompt (reduces cost ~90% on repeated calls)
- Never hardcode API keys; load from environment via `pydantic-settings`
- Log token usage per request for cost monitoring
- Reports are generated asynchronously; never block an API response on LLM calls

### Git
- Branch naming: `phase1/feature-name`, `phase2/feature-name`, etc.
- Commits: imperative mood, present tense ("Add lunar calendar converter")
- PRs require passing tests before merge

---

## Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tech_ziwei
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/tech_ziwei_test

# Auth
SECRET_KEY=<random-64-char-string>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Claude API
ANTHROPIC_API_KEY=<your-key>

# Redis
REDIS_URL=redis://localhost:6379/0

# App
ENVIRONMENT=development  # development | staging | production
```

---

## Current Status

| Phase | Status |
|-------|--------|
| Phase 1 — Chart Engine | Not started |
| Phase 2 — Data & API | Not started |
| Phase 3 — AI Prompt Engine | Not started |
| Phase 4 — Frontend | Not started |

Last updated: 2026-05-21
