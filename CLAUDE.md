# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **football (soccer) statistics analysis system** that integrates with the VStats API to provide detailed match statistics, team performance analysis, and predictive insights for football betting and analysis.

**Core Purpose:** Enable users to visualize scheduled matches, analyze detailed statistics for each game, and compare home vs. away team performance with stability metrics.

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18 + TypeScript 5 + Vite 5 + TailwindCSS + React Query |
| **Backend** | Python 3.11+ + FastAPI + Pydantic + Redis |
| **External APIs** | VStats API (statistics), TheSportsDB (team logos) |
| **Cache** | Redis (TTLs: schedule 1h, stats 6h, badges 7d) |

## Directory Structure

```
API/
├── backend/                            # FastAPI backend
│   ├── app/
│   │   ├── main.py                     # FastAPI app entry point
│   │   ├── config.py                   # Pydantic settings (env vars, cache)
│   │   ├── models/                     # Pydantic schemas
│   │   │   └── __init__.py             # TimeComEstatisticas, StatsResponse, etc.
│   │   ├── services/                   # Business logic
│   │   │   ├── stats_service.py        # Statistics calculation + recent_form
│   │   │   ├── schedule_service.py     # Match scheduling
│   │   │   └── badge_service.py        # Team logos (TheSportsDB)
│   │   ├── api/                        # FastAPI routes
│   │   │   └── routes.py               # /partidas, /partida/{id}/stats
│   │   └── utils/                      # Helpers (cache, calculations)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                           # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── atoms/                  # Badge, Icon, TeamBadge, LoadingSpinner
│   │   │   ├── molecules/              # StatsCard, PredictionsCard, DisciplineCard
│   │   │   └── organisms/              # StatsPanel (with RaceBadges)
│   │   ├── pages/                      # HomePage, EstatisticasPage
│   │   ├── hooks/                      # usePartidas, useStats (React Query)
│   │   ├── services/                   # API service layer
│   │   ├── types/                      # TypeScript interfaces
│   │   └── utils/                      # predictions.ts, etc.
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                               # Technical documentation
│   ├── MODELOS_DE_DADOS.md             # Pydantic schemas (v1.1)
│   ├── frontend/
│   │   ├── COMPONENTES_REACT.md        # 22 components (v1.1)
│   │   └── INTEGRACAO_API.md           # Services + React Query (v1.1)
│   └── ...
│
├── CLAUDE.md                           # This file
├── README.md                           # Project overview
└── docker-compose.yml                  # Backend + Redis + Frontend
```

## Development Commands

### Backend (FastAPI)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# API available at: http://localhost:8000
# Swagger UI at: http://localhost:8000/docs
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Frontend available at: http://localhost:5173
```

### Docker (Recommended)

```bash
# Start all services (backend + redis + frontend)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## Architecture Overview

### API Integration

**Base URL:** `https://vstats-back-bbdfdf0bfd16.herokuapp.com/api/`

**Key Endpoints Used:**

| Endpoint | Purpose | Key Parameters |
|----------|---------|-----------------|
| `schedule/day` | Get matches for specific date | `tmcl` (tournament ID), `date` (YYYY-MM-DD) |
| `schedule/month` | Get month's matches | `tmcl` |
| `seasonstats` | Team season aggregate statistics | `tmcl`, `ctst` (team ID) |
| `get-match-stats` | Detailed single-match statistics | `Fx` (match ID) |
| `match-preview` | Pre-match analysis & H2H | `Fx` |

**Important Limitations:**

- `schedule/day` with `date` parameter returns empty results; use `schedule/month` and filter client-side
- `seasonstats` doesn't include `lostCorners` (conceded corners); get from `get-match-stats` per match
- No month/year filtering parameters work; API always returns current period data
- All stats endpoints work without authentication

**Authentication Note:** Credentials found in codebase (client_id, client_secret) are for premium features. Basic statistics endpoints don't require auth.

### Data Flow

1. **Match Schedule** → Retrieved via `schedule/month` or `schedule/week`, filtered by date
2. **Team Stats** → Aggregated via `seasonstats` endpoint for season-long metrics
3. **Team Logos** → Retrieved from TheSportsDB API (free service)
4. **Match Details** → Individual match stats via `get-match-stats` for detailed comparison
5. **Stability Metrics** → Coefficient of Variation (CV) calculated from match history

### Key Concepts

**Coefficient of Variation (CV):** Measures team consistency/stability
- Formula: `CV = Standard Deviation / Mean`
- Scale: 0.00-0.15 (very stable) to 0.75+ (very unstable)
- Used to identify predictable vs unpredictable teams

**Recent Form (Race):** Sequence of recent results
- `W` = Win (Vitória), `D` = Draw (Empate), `L` = Loss (Derrota)
- Calculated from `goals` vs `goalsConceded` per match
- Display limit: 5 results for Temporada/Últimos 5, 10 for Últimos 10

**Statistics Categories:**

- **Feitos (Made):** Goals scored, corners won, shots on target, yellow/red cards, fouls committed
- **Sofridos (Conceded):** Goals against, corners conceded, shots conceded, defensive metrics

**Referee Data (Árbitro):** Cards statistics per referee
- `media_amarelos`: Average yellow cards per match
- `media_vermelhos`: Average red cards per match
- `total_jogos`: Total matches refereed in competition

**Tournament IDs (Global Competitions):**

> **Note:** IDs change each season! Use `/stats/tournament/v1/calendar` endpoint to get all current competition IDs dynamically. See `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 4.17.

Examples (2025/26 season):
- Premier League: `51r6ph2woavlbbpk8f29nynf8`
- La Liga: `80zg2v1cuqcfhphn56u4qpyqc`
- Serie A: `emdmtfr1v8rey2qru3xzfwges`
- Bundesliga: `2bchmrj23l9u42d68ntcekob8`
- Ligue 1: `dbxs75cag7zyip5re0ppsanmc`
- All 33+ competitions documented in `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 3

## System Design

### User Workflow

```
Home (Date Selection)
    ↓
Match List (Cards with Teams, Time, Competition)
    ↓
Statistics Panel (Home vs Away Team Comparison)
    ├─ Filter Options (All Season | Last 5 | Last 10)
    ├─ Sub-Filter Casa/Fora (per team, independent)
    ├─ Recent Form Badges (V/E/D sequence)
    ├─ CV Legend (expandable explanation)
    ├─ Predictions Card (calculated insights)
    ├─ Team Stats (Goals, Corners, Shots, etc.)
    ├─ Discipline Card (Cards, Fouls + Referee data)
    └─ Stability Metrics (CV for predictability)
```

### Data Required Per Component

**Match Card:**
- Team names, logos, IDs
- Match time, date, venue
- Competition name

**Statistics Panel:**
- Season-long aggregates (from `seasonstats`)
- Recent match details (filtered from `get-match-stats`)
- CV calculations (from utility scripts)
- Home/Away breakdowns

## Important Notes

### File Organization

- **Documentation files are the single source of truth** for API endpoints, IDs, and structure
  - `DOCUMENTACAO_VSTATS_COMPLETA.md` - VStats API reference (v5.5)
  - `PROJETO_SISTEMA_ANALISE.md` - System design & implementation guide
  - `ALINHAMENTO_DOCUMENTACAO.md` - Cross-reference consistency analysis

- **Technical documentation** in `docs/` folder:
  - Backend architecture and models (`docs/ARQUITETURA_BACKEND.md`, `docs/MODELOS_DE_DADOS.md`)
  - Frontend architecture and components (`docs/frontend/`)
  - Testing strategy and local setup

- **Python scripts are reference implementations** for:
  - Data validation (confirming API response structure)
  - Calculations (CV, statistics filtering)
  - Data extraction (field mapping)

### Cache Strategy

- Schedule data: Cache for 1 hour (matches don't change frequently)
- Season stats: Cache for 6 hours
- Team logos: Cache indefinitely (TheSportsDB data is stable)

### Testing Data

Sample JSON files in `data/samples/` represent real API responses:
- `arsenal_detailed_true.json` - Detailed match data
- `arsenal_full_data.json` - Complete dataset
- `arsenal_seasonstats.json` - Aggregated season statistics
- `premier_league_teams.json` - Team listings

These are used for:
- Script validation without live API calls
- Understanding response structure
- Testing data transformation logic

## Development Notes

### Common Tasks

1. **Understanding API Structure:** Reference `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 6 (Data Structure)
2. **Finding Team/Tournament IDs:** See `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 12 (Reference IDs)
3. **Implementing New Features:** Check `PROJETO_SISTEMA_ANALISE.md` for requirements
4. **Validating Implementation:** Run scripts in `validacao/` directory
5. **Debugging API Issues:** Common issues documented in `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 13

### Code Patterns

- Python scripts use `requests` library with `BASE_URL` constant
- JSON response parsing expects specific field names (documented in dataclass fields)
- Match filtering is always client-side due to API limitations
- Statistics calculations leverage pandas/statistics libraries where needed

### Performance Considerations

- Minimize API calls via caching strategy
- Filter large match arrays on client-side to reduce data transfer
- Pre-calculate CVs for frequently-accessed teams
- Use date filtering to reduce response sizes

## Related Resources

- **VStats API:** Opta/Stats Perform football data provider
- **TheSportsDB:** Free API for team logos and metadata
- **Sample Data:** Located in `data/samples/` for testing without API calls
