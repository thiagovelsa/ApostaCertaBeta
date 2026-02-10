# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **football (soccer) statistics analysis system** that integrates with the VStats API to provide detailed match statistics, team performance analysis, and predictive insights.

**Core Purpose:** Enable users to visualize scheduled matches, analyze detailed statistics for each game, and compare home vs. away team performance with stability metrics (CV - Coefficient of Variation).

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 19 + TypeScript 5 + Vite 7 + TailwindCSS + Zustand + React Query |
| **Backend** | Python 3.11+ + FastAPI + Pydantic + Redis |
| **External APIs** | VStats API (statistics), TheSportsDB (team logos) |
| **Cache** | Redis (TTLs: schedule 1h, stats 6h, badges 7d) |

## Development Commands

### Backend (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt          # Production only
pip install -r requirements-dev.txt      # Development (includes testing, linting)

# Run development server
uvicorn app.main:app --reload --port 8000

# Testing
pytest                                   # Run all tests
pytest tests/unit/                       # Unit tests only
pytest tests/unit/test_analysis_service.py -v   # Single test file
pytest tests/unit/test_analysis_service.py::test_specific_function -v  # Single test
pytest -v -s                            # Verbose with output
pytest --cov=app --cov-report=html      # With coverage report

# Code Quality (requires requirements-dev.txt)
black app/ tests/                        # Format code
ruff check app/ tests/                   # Lint code
mypy app/                                # Type checking

# API Documentation (when running)
# Swagger UI: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

### Frontend (React)

```bash
cd frontend

# Install dependencies (requires Node.js 20.19+)
npm install

# Run development server
npm run dev

# Build and lint
npm run build       # TypeScript compile + Vite build
npm run lint        # ESLint check
npm run clean       # Clean dist folder

# Preview production build
npm run preview
```

## Architecture Overview

### Layered Architecture (Backend)

```
API Layer (app/api/routes/)
├── partidas.py      # GET /api/partidas - List matches by date
├── stats.py         # GET /api/partida/{id}/stats - Match statistics
├── competicoes.py   # GET /api/competicoes - List competitions
└── escudos.py       # GET /api/time/{id}/escudo - Team badges

Business Logic (app/services/)
├── partidas_service.py    # Match filtering and scheduling logic
├── stats_service.py       # Statistics calculation, CV, predictions
├── analysis_service.py    # Match analysis and opportunity detection
├── cache_service.py       # Redis caching layer
└── vstats_repository.py   # VStats API HTTP client

Models (app/models/)
├── partida.py        # TimeInfo, PartidaResumo
├── estatisticas.py   # EstatisticaMetrica, EstatisticasTime
├── analysis.py       # AnalysisResponse, Opportunity detection
└── contexto.py       # ContextoVStats, match context metadata

Utils (app/utils/)
├── cv_calculator.py      # Coefficient of Variation calculation
├── league_params.py      # League-specific adjustment parameters
└── contexto_vstats.py    # Context enrichment utilities
```

### Key API Endpoints

| Endpoint | Description | Key Params |
|----------|-------------|------------|
| `GET /api/partidas?data=YYYY-MM-DD` | List matches for date | `data` (required) |
| `GET /api/partida/{id}/stats` | Match statistics | `filtro=geral\|5\|10`, `periodo=integral\|1T\|2T`, `home_mando=casa\|fora`, `away_mando=casa\|fora` |
| `GET /api/partida/{id}/analysis` | Full analysis with predictions | Same as stats |
| `GET /api/competicoes` | List all competitions | - |
| `GET /api/time/{id}/escudo` | Team badge/logo | - |

### Statistics Filter Parameters

- **`filtro`**: `geral` (up to 50 matches), `5` (last 5), `10` (last 10)
- **`periodo`**: `integral` (full match), `1T` (first half), `2T` (second half)
- **`home_mando`/`away_mando`**: Filter sample by home/away performance. When used, automatic home-field advantage adjustment is disabled.

### Data Flow for Statistics

1. **Route** validates input parameters
2. **StatsService** checks cache, then calls VStatsRepository
3. **VStatsRepository** fetches from external API (with retry logic)
4. **StatsService** calculates metrics:
   - Time-weighted averages (Dixon-Coles decay: recent matches weigh more)
   - Weighted CV (coefficient of variation)
   - Predictions with Poisson distribution + Dixon-Coles adjustment
5. Response includes `contexto` field explaining data sources and any fallbacks applied

### Key Concepts

**Coefficient of Variation (CV):** Measures team consistency
- Formula: `CV = Standard Deviation / Mean`
- Scale: 0.00-0.15 (very stable) to 0.75+ (very unstable)
- Calculated with time-weighting: recent matches have higher weight

**Time-Weighting (Dixon-Coles Decay):**
- Weight formula: `e^(-0.0065 × days_ago)`
- 30 days ago = 82% weight, 60 days = 68%, 90 days = 56%

**Home-Field Advantage Adjustment:**
- Automatically applied unless `home_mando`/`away_mando` filters are used
- Increases home team expected goals by ~10%, decreases away team

**Period Extraction:**
- When `periodo=1T|2T` requested, attempts to extract half-time stats
- Falls back to `integral` with `periodo_fallback_integral: true` in contexto

### Cache Strategy

- **Schedule data**: 1 hour (matches don't change frequently)
- **Season stats**: 6 hours
- **Match stats**: 6 hours
- **Team logos**: 7 days (TheSportsDB data is stable)
- **Calendar/competitions**: 24 hours (IDs change seasonally)

### External API Integration (VStats)

**Base URL:** `https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/`

**Key Endpoints:**
- `/stats/tournament/v1/calendar` - Competition IDs (change each season!)
- `/stats/tournament/v1/schedule` - Full season schedule (preferred over /schedule/day)
- `/stats/matchstats/v1/get-match-stats` - Match stats via `liveData.lineUp[].stat[]`
- `/stats/seasonstats/v1/team` - Season aggregates
- `/stats/referees/v1/get-by-prsn` - Referee statistics

**Important Limitations:**
- `/schedule/day?date=` often returns empty - use `/schedule` + client filter
- `/schedule/month` only returns current month, ignores parameters
- Tournament IDs change each season - use `/calendar` dynamically

### Team Logos System

Local logos preferred over external APIs. Located at `frontend/public/logos/` (13 leagues, 350+ logos).

**Mapping:** `frontend/src/utils/teamLogos.ts` (636+ entries with aliases)

External sources (fallback):
- Opta image endpoint (VStats-covered leagues)
- TheSportsDB API (non-VStats leagues)

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Pydantic settings
│   │   ├── dependencies.py         # DI container
│   │   ├── api/routes/             # HTTP routes
│   │   ├── services/               # Business logic
│   │   ├── models/                 # Pydantic schemas
│   │   ├── repositories/           # External API clients
│   │   └── utils/                  # Helpers
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures
│   │   └── unit/                   # Unit tests
│   ├── requirements.txt            # Production deps
│   └── requirements-dev.txt        # Development deps
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Atomic design (atoms, molecules, organisms)
│   │   ├── pages/                  # Route pages
│   │   ├── hooks/                  # React Query hooks
│   │   ├── services/               # API clients
│   │   ├── stores/                 # Zustand stores
│   │   ├── types/                  # TypeScript interfaces
│   │   └── utils/                  # Helpers (predictions, smart search)
│   └── package.json
│
└── docs/                           # Technical documentation
    ├── ARQUITETURA_BACKEND.md
    ├── MODELOS_DE_DADOS.md
    ├── API_SPECIFICATION.md
    ├── TESTING_STRATEGY.md
    └── frontend/
```

## Testing

The project uses pytest with the following structure:
- **Unit tests**: `tests/unit/` - Test business logic in isolation (with mocks)
- **Fixtures**: `tests/conftest.py` - Shared test data and fixtures

Key fixtures available:
- `sample_match_data` - Sample match dictionary
- `sample_stats_values` - CV test values (stable, moderate, unstable)
- `vstats_schedule_response` - Mock VStats schedule response
- `vstats_seasonstats_response` - Mock VStats season stats response

Test naming convention: `test_<function>_<behavior>()` or `test_<Class>_<method>_<behavior>()`

## Environment Configuration

Backend reads `.env` from the current working directory. When running from `backend/`, place `.env` there.

Key variables:
- `VSTATS_API_URL` - VStats API base URL
- `REDIS_URL` - Redis connection string (optional, disables cache if not set)
- `CORS_ORIGINS` - Allowed origins for CORS
- `DEBUG` - Enable debug mode (shows docs, detailed errors)

Template at `.env.example` (copy to `backend/.env`).

## Common Issues

| Problem | Solution |
|---------|----------|
| Stats endpoint timeout | Frontend `.env` with `VITE_API_TIMEOUT=60000` |
| `/schedule/day?date=` empty | Use `/schedule` and filter client-side |
| Tournament IDs invalid | Call `/competicoes` to get current IDs |
| Redis connection error | Set `REDIS_URL=` empty to disable cache, or run `docker run -d -p 6379:6379 redis` |
| CORS error | Add origin to `CORS_ORIGINS` in `.env` |
| Test fails with import error | Run `pip install -r requirements-dev.txt` |

## Documentation References

- `docs/ARQUITETURA_BACKEND.md` - Detailed backend architecture
- `docs/MODELOS_DE_DADOS.md` - Pydantic schemas and validation
- `docs/API_SPECIFICATION.md` - Complete API documentation
- `docs/TESTING_STRATEGY.md` - Testing patterns and best practices
- `docs/DOCUMENTACAO_VSTATS_COMPLETA.md` - VStats API reference
