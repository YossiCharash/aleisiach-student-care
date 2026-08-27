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

Quality gates (enforced in **CI**; run locally for fast feedback before pushing):

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

## Checks run in CI

All checks run in **GitHub Actions** on every push and PR — backend (ruff · black · mypy · pytest)
and frontend (lint · typecheck · Vitest · build · Playwright E2E). There are **no local git hooks**;
CI is the enforcement point. Run the quality-gate command above (and `pnpm test` / `pnpm typecheck`
in `frontend/`) yourself when you want fast local feedback.

## Frontend (`frontend/`)

Scaffolded next — Vite + React + TypeScript SPA (pnpm).
