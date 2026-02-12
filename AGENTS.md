# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/`: FastAPI code split into `api/routes`, `services`, `repositories`, `models`, `utils`; entrypoint `backend/app/main.py`.
- `backend/tests/`: pytest suites (unit/integration); root `tests/README.md` is documentation only.
- `frontend/src/`: React + TS UI (`components/atoms|molecules|organisms|layout`, `pages`, `hooks`, `services`, `stores`); build output in `frontend/dist/`.
- `docs/`, `openapi.yaml`, `data/samples/`, `scripts/` for specs, API contract, sample JSON, and validation utilities.

## Key Backend Endpoints

### VStats API (External)
- **Base:** `https://vstats-back-bbdfdf0bfd16.herokuapp.com/api`
- `/stats/tournament/v1/calendar` → Dynamic competition IDs
- `/stats/tournament/v1/schedule?tmcl={id}` → Full season matches
- `/stats/matchstats/v1/get-match-stats?Fx={id}` → Match statistics
- `/stats/seasonstats/v1/team?ctst={id}&tmcl={id}` → Season aggregates
- `/stats/referees/v1/get-by-prsn?Prsn={id}` → Referee stats
- `/stats/match/v1/preview?Fx={id}` → Match preview (H2H, standings)
- `/stats/standings/v1/season?tmcl={id}` → League standings

### Internal API (FastAPI)
- `GET /api/partidas?data={YYYY-MM-DD}` → Matches for date
- `GET /api/partida/{id}/stats?filtro={geral|5|10}&periodo={integral|1T|2T}&home_mando={casa|fora}&away_mando={casa|fora}` → Match stats
- `GET /api/partida/{id}/analysis?filtro={geral|5|10}&debug={0|1}` → Full analysis with predictions + over/under
- `GET /api/competicoes` → All competitions
- `GET /api/time/{id}/escudo` → Team badge

## Important Paths
- Backend services: `backend/app/services/`
- Repositories (API clients): `backend/app/repositories/`
- Known competitions fallback: `backend/app/known_competitions.py`
- Frontend API service: `frontend/src/services/api.ts`
- Frontend timeout: `frontend/.env` (`VITE_API_TIMEOUT`)

## Build, Test, and Development Commands
- Backend (run from `backend`): `python -m venv .venv`, `pip install -r requirements.txt -r requirements-dev.txt`, `uvicorn app.main:app --reload --port 8000`.
- Frontend (run from `frontend`): `npm install`, `npm run dev`, `npm run build`, `npm run preview`, `npm run lint`, `npm run clean`.
- Windows convenience: `dev.bat` starts backend + frontend on ports 8000/5173.
- Testing: `pytest` (backend), `pytest --cov=app --cov-report=html` (with coverage).

## Coding Style & Naming Conventions
- Python: Black + Ruff, type hints, Google-style docstrings; import order is stdlib, third-party, local.
- Naming: `snake_case` for modules/functions, `PascalCase` for classes and React components, `UPPER_SNAKE_CASE` for constants; hooks use `useX` in `frontend/src/hooks/`.

## Testing Guidelines
- Frameworks: pytest for backend; frontend tests are planned (no npm test script yet).
- Tests live in `backend/tests/unit` and `backend/tests/integration`; name files `test_<module>.py`.
- Coverage target: 80% minimum; run `pytest --cov=app --cov-report=html`.

## Commit & Pull Request Guidelines
- Git history follows Conventional Commits in Portuguese (e.g., `docs: atualizar ...`); keep that format (`feat:`, `fix:`, `docs:`).
- PRs should include a clear summary, linked issues, and screenshots for UI changes; run `pytest`, `black`, and `ruff` before opening.

## Configuration & Security Notes
- Backend reads `.env` from the current working directory; copy `.env.example` to `backend/.env` and keep secrets out of git.
- If API schemas change, update `openapi.yaml` and relevant docs in `docs/`.

## Agent Notes
- For automation guidance, read `CLAUDE.md`.
- Analysis service implements Poisson + Dixon-Coles for goals, Negative Binomial for other metrics.
- Time-weighting uses Dixon-Coles decay (0.0065) for recent matches.
- Context extraction includes rest days, standings, H2H from match preview.
