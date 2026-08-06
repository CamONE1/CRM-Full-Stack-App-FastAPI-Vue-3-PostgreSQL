# HR Portal (pet project)

Mini HR portal with role-based access (admin / hr / user). The flagship feature — still ahead, Stage 3 — is a **job-offer lifecycle module**: draft → sent → accepted/declined/expired, including a public candidate-facing page.

Built solo as a portfolio project; the codebase is written to a production-like quality bar. Detailed architecture rules, conventions and the stage-by-stage roadmap live in [`CLAUDE.md`](./CLAUDE.md).

**Progress:** Stages 0–2 done (backend foundation, frontend skeleton, employees module). Offers module (Stage 3) is next.

## Features

- **Auth & access control** — JWT (access + refresh), role-based route guards on the frontend and `require_roles(...)` on every private backend endpoint. Users land on a dedicated `/403` page rather than a silent redirect when they're logged in but not allowed somewhere.
- **Employees module** — searchable, filterable (position, status), paginated table with CSV export; an employee card (profile fields, offers section reserved for Stage 3); a self-service `/profile` page where any user can update their own phone/Telegram. Filters and pagination are kept in the URL (`route.query`), so a reload or a shared link restores the exact same view.

  <img src="docs/screenshots/employees-table.png" alt="Employees table with search, position/status filters and CSV export" width="800">
  <img src="docs/screenshots/employee-card.png" alt="Employee card with profile fields" width="800">

- **News feed** — list (any role) + creation (hr/admin), authored by the linked employee record.
- **User management** (admin) — list users, change role and active status.

## Tech stack

**Backend**
- FastAPI
- SQLAlchemy 2.0 (typed `Mapped[]` style)
- PostgreSQL + Alembic migrations
- JWT auth (access + refresh tokens)
- pytest + httpx (`TestClient`) for integration tests
- GitHub Actions CI (`.github/workflows/backend-ci.yml`)

**Frontend**
- Vue 3 `<script setup>` + TypeScript, Vite, Pinia, Vue Router, Tailwind CSS, axios
- A small base-component layer (`BaseTable`, `BaseInput`, `BaseSelect`, `BasePagination`, `StatusBadge`, `PageHeader`, ...) that pages compose — no domain logic inside the components themselves.

**Infra**
- Docker Compose for local PostgreSQL

## Project structure

```
backend/
  app/
    auth/        # login, refresh, /me; security.py holds JWT logic
    common/      # rbac.py: get_current_user_payload, require_roles(*roles)
    users/       # User model — auth only (email, password_hash, role, is_active)
    employees/   # Employee model — single source of truth for a person's profile
    news/        # News model + CRUD
    core/        # config.py (env settings), db.py (Base, session)
    migrations/  # Alembic env + versions
  tests/         # integration tests (httpx TestClient + real test DB)
  seed_admin.py  # creates a single admin user
  seed_data.py   # seeds 3 role users + 6 employees for local development
frontend/
  src/
    api/         # axios client + one module per entity (auth, employees, ...)
    components/
      base/      # BaseTable, BaseInput, BaseSelect, BasePagination, StatusBadge, PageHeader, ...
    layouts/     # AppLayout (sidebar + header), BlankLayout (login, public pages)
    stores/      # one Pinia store per entity (auth, employees, ...)
    views/       # pages, composed from base components + store calls
    router/      # route table, role guards, layout selection via route.meta
    types/       # shared TS types per entity
docker-compose.yml
```

## Getting started

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for local PostgreSQL)

### 2. Start PostgreSQL

```bash
docker compose up -d
```

This starts a `postgres:16` container (`crm_postgres`) on `localhost:5432` with the credentials already wired into the backend's default config (db `crm_db`, user `crm`, password `crm_password`).

### 3. Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn "sqlalchemy>=2.0" psycopg2-binary alembic pydantic-settings "pydantic[email]" \
    "bcrypt<4.0" "passlib[bcrypt]==1.7.4" "python-jose[cryptography]" pytest httpx
```

By default the app connects to `postgresql+psycopg2://crm:crm_password@127.0.0.1:5432/crm_db` (see `app/core/config.py`). To override, create `backend/.env`:

```
DATABASE_URL=postgresql+psycopg2://crm:crm_password@127.0.0.1:5432/crm_db
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Seed local data (optional but recommended)

```bash
python seed_data.py
```

Creates 3 users (one per role) and 6 employees (3 linked to a login, 3 without one — HR-only records):

| Email | Password | Role |
|---|---|---|
| admin@crm.com | admin12345 | admin |
| hr@crm.com | hr12345678 | hr |
| user@crm.com | user12345 | user |

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

### 7. Run backend tests

```bash
pytest
```

Tests run against the same PostgreSQL instance (via `DATABASE_URL`), so the DB from step 2–4 must be up and migrated first.

### 8. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173 (proxies API calls to the backend per `VITE_API_URL` in `frontend/.env`)
- Log in with any of the seeded accounts above.

## Roadmap

Stage-by-stage plan (current stage, architecture principles, conventions) is tracked in [`CLAUDE.md`](./CLAUDE.md) rather than duplicated here, to avoid the two drifting out of sync.

## Architecture Decisions

- `employees` is the single source of truth for a person's profile; `users` stays auth-only (email/password/role). The link is `employees.user_id`, a nullable unique FK — an employee may exist without ever getting a login.
- CORS is restricted to `http://localhost:5173` (Vite dev server) with credentials allowed, since the frontend sends the JWT via `Authorization` header and will later need cookies-free credentialed requests.
- Frontend keeps tokens in `localStorage` (not cookies) and attaches them via an `Authorization` header, matching the backend's bearer-only auth; the axios response interceptor retries once after a silent `/auth/refresh` on a 401, queuing any requests that 401 while a refresh is already in flight.
- Route guards read role from the JWT-derived `AuthUser` in the Pinia auth store, not from a separate call; unknown/insufficient roles land on `/403` rather than a silent redirect to `/login`, so the distinction between "not logged in" and "logged in but not allowed" stays visible to the user.
- Stage-2/3 pages still pending a real implementation are stubbed via a single `PlaceholderView` component driven by route `props`, so the full nav/route structure from `PLAN.md` exists from stage 1 without building throwaway per-page files ahead of schedule.
- The active layout (sidebar app shell vs. a blank full-screen wrapper for login/future public pages) is picked in `App.vue` from `route.meta.layout`, not from a hardcoded list of route names — adding a new public page is a one-line route change, not an edit to the layout-selection logic.
- Table filters and pagination (currently the employees table) live in `route.query`, written via `router.replace` (so filtering never spams browser history) and read back on mount — a reload or a shared link reproduces the exact same filtered view.
- A small base-component layer (`BaseTable`, `BaseInput`, `BaseSelect`, `BasePagination`, `StatusBadge`, `PageHeader`, ...) forms the start of a design system: components take generic props/slots only and hold no domain vocabulary, so the same `BaseTable` will back the offers table in Stage 3 without modification.
