# CLAUDE.md — HR Portal (pet project)

## What this is
Detailed page map and stages: see PLAN.md. Idea backlog: IDEAS.md.
Mini HR portal: role-based internal system (admin / hr / user) with a **job-offer lifecycle module** as the flagship feature. Built solo as a portfolio project; quality bar = production-like. Author: frontend developer (Vue) re-entering hands-on work — explain non-trivial backend decisions briefly when making them.

## Stack
- **Backend:** FastAPI, SQLAlchemy 2.0 (typed `Mapped[]` style), PostgreSQL, Alembic, JWT auth (access+refresh), pytest, GitHub Actions CI (`.github/workflows/backend-ci.yml`)
- **Frontend (to be created in `frontend/`):** Vue 3 `<script setup>` + TypeScript, Vite, Pinia, Vue Router, Tailwind CSS, axios
- Docker Compose for local PostgreSQL

## Structure
```
backend/app/
  auth/      # login, refresh, me; security.py holds JWT logic
  common/    # rbac.py: get_current_user_payload, require_roles(*roles)
  users/     # User model: email, password_hash, role(user|hr|admin), is_active
  news/      # News model + CRUD (partially built)
  core/      # config.py (env), db.py (Base, session)
  migrations/  # Alembic
backend/tests/ # integration tests, httpx AsyncClient + test DB
```

## Architecture principles (non-negotiable)
1. **Single source of truth.** `employees` table is the core entity. Every module references `employee_id` (FK); NEVER duplicate profile fields (name, phone, etc.) into other tables. `users` is auth-only (email/password/role); `employees` is the person (1:1 via `user_id`, nullable — an employee may have no login).
2. **RBAC on every private endpoint** via `require_roles(...)` dependency. Public endpoints exist ONLY under `/public/*` (offer pages by token).
3. **Offers lifecycle:** draft → sent (generates `public_token` uuid) → accepted | declined (candidate action, idempotent) | expired (checked against `expires_at` on read). Public link uses token, never numeric id.
4. One Pinia store per entity on the frontend; pages read stores, no local data copies.

## Frontend code style (non-negotiable)
- Component-first: build small, universal, reusable components (BaseButton,
  BaseTable, BaseModal, StatusBadge, FormField...) and compose pages from them.
  Before creating a new component, check if an existing one can be reused or
  slightly extended (props/slots) instead.
- Simplicity over cleverness: prefer the simplest solution that works; no
  premature abstractions, no over-engineering. Code must stay easy to read,
  extend, and scale.
- Pages = composition + store calls; heavy logic lives in stores/composables,
  not inside page components.

## Conventions
- Code, comments, docstrings, commit messages: **English**. UI strings: Russian.
- Commits: conventional (`feat:`, `fix:`, `chore:`, `docs:`, `test:`). Small, per-feature.
- Every backend change → run `pytest` before committing. New endpoints need tests (follow `tests/test_auth_rbac_news.py` patterns).
- Migrations via Alembic only (`alembic revision --autogenerate`), never manual schema edits.
- Secrets in `.env` (gitignored). Anthropic API key (stage 5) lives backend-side only.
- Record notable design choices in README "Architecture Decisions" section, one line each.
- New feature ideas go to `IDEAS.md`, not into the current stage.
- Branching: one branch per stage, classic format `type/short-name`
  (feature/, fix/, docs/, chore/ — e.g. feature/frontend-skeleton).
  Create the branch BEFORE starting any stage work; never commit to main directly.
- Commit small and often: one logical change = one commit (added a doc — commit;
  created a script — commit; finished a component — commit). Do not batch
  unrelated changes into one commit.
- Git boundaries: Claude commits locally only. Pull, merge, and push are done
  by the author personally — never run `git push`, `git pull`, or `git merge`.

## Roadmap (work stage by stage; don't jump ahead)
- **Stage 0 (current):** CORS for Vite (localhost:5173); `employees` table + migration + seeds (3 role users, 5–6 employees, incl. 1–2 without user accounts); protect news endpoints with roles + add `author_id`; `GET /users` + `PATCH /users/{id}` (admin).
- **Stage 1:** frontend skeleton — login, axios interceptor with refresh-retry, role route guards, layout with role-filtered sidebar.
- **Stage 2:** employees table page (search, filters, CSV export) + employee card (profile + their offers) + /profile self-edit.
- **Stage 3:** offers module — backend CRUD + statuses, table UI, create form, public candidate page `/offer/{token}` with accept/decline.
- **Stage 4:** dashboard — `/stats` endpoint, offer-funnel + employee charts, recent widgets.
- **Stage 5:** AI — `POST /ai/draft` (bullet points → offer/news text), key in backend `.env`.
- **Stage 6:** polish — news CRUD UI, dark theme, responsive, README with demo GIF, deploy (Vercel + Render/Railway).

## Commands
```
docker compose up -d           # local PostgreSQL
cd backend && uvicorn app.main:app --reload
cd backend && pytest
cd backend && alembic upgrade head
cd frontend && npm run dev     # after stage 1
```
