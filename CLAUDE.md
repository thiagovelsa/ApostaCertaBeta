# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **football (soccer) statistics analysis system** that integrates with the VStats API to provide detailed match statistics, team performance analysis, and predictive insights for football betting and analysis.

**Core Purpose:** Enable users to visualize scheduled matches, analyze detailed statistics for each game, and compare home vs. away team performance with stability metrics.

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML/CSS (static pages), React + TypeScript (planned) |
| **Backend** | Python + FastAPI (planned) |
| **External APIs** | VStats API (statistics), TheSportsDB (team logos) |
| **Data** | JSON samples for testing/documentation |

## Directory Structure

```
API/
├── DOCUMENTACAO_VSTATS_COMPLETA.md    # Complete VStats API documentation
├── PROJETO_SISTEMA_ANALISE.md         # System design & requirements
├── ballerside_ui_replica/              # Static HTML/CSS UI prototypes
│   ├── index.html
│   ├── home.html
│   └── styles.css
├── stitch_football_statistics_dashboard/   # Dashboard prototype
│   ├── code.html                       # Full statistics dashboard UI
│   └── screen.png
├── stitch_football_statistics_dashboard2/  # Another dashboard variant
│   ├── code.html
│   └── screen.png
├── scripts/
│   ├── validacao/                      # API validation scripts
│   │   ├── validar_seasonstats_geral.py
│   │   ├── validar_get_match_stats.py
│   │   └── validar_descobertas.py
│   └── utilitarios/                    # Data calculation utilities
│       ├── calcular_coeficiente_variacao.py  # Stability metric calculations
│       ├── calcular_estatisticas_sofridas.py # Defensive stats
│       ├── calcular_corners_sofridos.py      # Corner calculations
│       ├── compare_detailed.py               # Data comparison
│       └── extract_arsenal_fields.py         # Field extraction
└── data/
    └── samples/                        # Sample JSON data for testing
        ├── arsenal_detailed_true.json
        ├── arsenal_full_data.json
        ├── arsenal_seasonstats.json
        ├── arsenal_vs_crystal_palace.json
        ├── premier_league_teams.json
        └── ...
```

## Development Commands

### Running Python Scripts

```bash
# Validate API responses (seasonal statistics)
python scripts/validacao/validar_seasonstats_geral.py

# Validate match statistics endpoint
python scripts/validacao/validar_get_match_stats.py

# Calculate coefficient of variation (CV) for team stability
python scripts/utilitarios/calcular_coeficiente_variacao.py

# Extract specific statistics fields
python scripts/utilitarios/extract_arsenal_fields.py

# Compare detailed data from different API responses
python scripts/utilitarios/compare_detailed.py
```

### Frontend Development

```bash
# Static HTML pages - Open in browser
# ballerside_ui_replica/index.html
# stitch_football_statistics_dashboard/code.html

# For React development (when implementing frontend):
npm install
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
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

**Statistics Categories:**

- **Feitos (Made):** Goals scored, corners won, shots on target, yellow/red cards, fouls committed
- **Sofridos (Conceded):** Goals against, corners conceded, shots conceded, defensive metrics

**Tournament IDs (Global Competitions):**

- Premier League 2024-25: `51r6ph2woavlbbpk8f29nynf8`
- Multiple other competitions documented in `DOCUMENTACAO_VSTATS_COMPLETA.md` Section 3

## System Design

### User Workflow

```
Home (Date Selection)
    ↓
Match List (Cards with Teams, Time, Competition)
    ↓
Statistics Panel (Home vs Away Team Comparison)
    ├─ Filter Options (All Season | Last 5 | Last 10)
    ├─ Team Stats (Goals, Corners, Shots, etc.)
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
  - `DOCUMENTACAO_VSTATS_COMPLETA.md` - API reference (v5.5)
  - `PROJETO_SISTEMA_ANALISE.md` - System design & implementation guide

- **Python scripts are reference implementations** for:
  - Data validation (confirming API response structure)
  - Calculations (CV, statistics filtering)
  - Data extraction (field mapping)

- **HTML prototypes show UI/UX design** but are static; actual frontend will use React + TypeScript

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
