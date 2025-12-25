# Repository Guidelines

## Project Structure & Module Organization
- `backend/app/`: FastAPI code split into `api/routes`, `services`, `repositories`, `models`, `utils`; entrypoint `backend/app/main.py`.
- `backend/tests/`: pytest suites (unit/integration); root `tests/README.md` is documentation only.
- `frontend/src/`: React + TS UI (`components/atoms|molecules|organisms|layout`, `pages`, `hooks`, `services`, `stores`); build output in `frontend/dist/`.
- `docs/`, `openapi.yaml`, `data/samples/`, `scripts/` for specs, API contract, sample JSON, and validation utilities.

## Build, Test, and Development Commands
- Backend (run from `backend`): `python -m venv .venv`, `pip install -r requirements.txt -r requirements-dev.txt`, `uvicorn app.main:app --reload --port 8000`.
- Frontend (run from `frontend`): `npm install`, `npm run dev`, `npm run build`, `npm run preview`, `npm run lint`.
- Windows convenience: `dev.bat` starts backend + frontend on ports 8000/5173.

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
- Backend reads `.env` from the working directory; copy `/.env.example` to `backend/.env` and keep secrets out of git.
- If API schemas change, update `openapi.yaml` and relevant docs in `docs/`.

## Agent Notes
- For automation guidance, read `CLAUDE.md`.
