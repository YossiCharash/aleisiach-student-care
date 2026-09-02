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

Demo seed (idempotent — dev/E2E only, never real data):

```bash
uv run alembic upgrade head        # tables must exist first
uv run python -m backend.app.seed  # run from the repo root
```

Seeds one user per role (`mor` / `dana` / `yoav`, password `demo1234`), two classes,
three students, a full taxonomy tree, and a sample meeting + details + social note for
student "נועה כהן". Re-running detects existing data and does nothing.

## Checks run in CI

All checks run in **GitHub Actions** on every push and PR — backend (ruff · black · mypy · pytest)
and frontend (lint · typecheck · Vitest · build · Playwright E2E). There are **no local git hooks**;
CI is the enforcement point. Run the quality-gate command above (and `pnpm test` / `pnpm typecheck`
in `frontend/`) yourself when you want fast local feedback.

## Frontend (`frontend/`)

Scaffolded next — Vite + React + TypeScript SPA (pnpm).

## Deployment (Render)

Production runs on **Render**: a Docker web service for the backend, a Docker (nginx) web
service for the SPA, and a managed PostgreSQL instance. `render.yaml` is the blueprint for
that infrastructure — it documents every environment variable the production guard requires.

Deploys are **automatic but gated**: `.github/workflows/deploy.yml` runs only after the CI
workflow finishes successfully on `main`, then calls each service's **Render Deploy Hook** with
`ref` set to the exact commit CI tested — backend first, then the frontend. A red suite never
reaches production. Render's own auto-deploy stays off (`autoDeploy: false`) so this workflow is
the only path in.

A deploy hook is fire-and-forget: Render accepts the request and builds asynchronously. **The
workflow reports that the deploy was accepted, not that it succeeded** — a build or start failure
shows up in Render's dashboard and its notification emails, not as a red pipeline. Trading that
feedback away buys a much narrower credential: a hook URL can only deploy its one service, while
an API key can act on the whole Render account.

### One-time setup

1. **Services.** For a fresh environment, point Render at `render.yaml` (New → Blueprint).
   If the services already exist, leave them as they are — only steps 2–4 are needed.
2. **Environment variables.** Fill every `sync: false` value in the Render dashboard. Two are
   easy to get wrong:
   - `DATABASE_URL` must carry the psycopg v3 driver — take Render's *Internal Database URL*
     and change `postgresql://` to `postgresql+psycopg://`.
   - `BACKEND_ORIGIN` (frontend) and `APP_CORS_ORIGINS` / `EMAIL_*_BASE_URL` (backend) are the
     services' public origins, known only after the first deploy.
3. **Turn off auto-deploy** on both services (Settings → Build & Deploy) so CI stays the gate.
4. **Repository secrets** (Settings → Secrets and variables → Actions). Each service's hook URL
   is under Settings → Deploy Hook; it embeds its own key, so treat it as a password:

   | Secret | Value |
   |---|---|
   | `RENDER_BACKEND_DEPLOY_HOOK` | the backend service's Deploy Hook URL |
   | `RENDER_FRONTEND_DEPLOY_HOOK` | the frontend service's Deploy Hook URL |

### Notes

- Migrations need no deploy step: `backend/docker-entrypoint.sh` runs `alembic upgrade head`
  before the app boots, on every container start.
- `plan: free` in the blueprint is a prototype default — free services sleep when idle and a
  free PostgreSQL instance expires. Raise both plans before real use.
- `APP_TRUSTED_PROXY_COUNT=2` assumes browser → nginx → Render load balancer → backend. It only
  affects which IP the auth rate limiter attributes a request to; verify it against a real
  request before relying on lockouts.
- The demo seeder is never run in production — `docker-compose.yml` seeds it for local use only.
