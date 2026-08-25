# Aleisiach — Cloud Student Care System

Cloud system for managing student care at Aleisiach (עלי שיח). Hebrew RTL, desktop-only.
Two apps: a **Vite React SPA** (`frontend/`) and a **FastAPI** backend (`backend/`).

- **Vision, rules, permissions:** [`CLAUDE.md`](CLAUDE.md)
- **Architecture, data model, flows:** [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Decision log (ADRs):** [`DECISIONS.md`](DECISIONS.md)

## Backend (`backend/`)

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cd backend
uv sync --all-extras --dev
cp .env.example .env
uv run uvicorn backend.app.main:app --reload --app-dir ..
```

> Code is imported as `backend.app.*` (import root = repo root).

Quality gates (also enforced in CI and via pre-commit):

```bash
cd backend
uv run ruff check . && uv run black --check . && uv run mypy -p backend.app && uv run pytest -q
```

Database migrations (Alembic):

```bash
cd backend
uv run alembic revision --autogenerate -m "message"
uv run alembic upgrade head
```

## Git hooks

```bash
uv tool install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
```

## Frontend (`frontend/`)

Scaffolded next — Vite + React + TypeScript SPA (pnpm).
