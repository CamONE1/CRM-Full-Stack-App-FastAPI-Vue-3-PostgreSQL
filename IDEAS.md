# IDEAS.md — backlog

Rules: new ideas land here, NOT in the current stage. Review after the minimal showcase is deployed (stages 0–3 done + deploy). One line per idea; promote to PLAN.md when actually scheduled.

## Next up (strong candidates after MVP)
- **Offboarding flow:** deactivate employee (`employees.is_active=False`) + revoke login (`users.is_active=False` or unlink), "Inactive" filter tab on the employees table. Employee record is never deleted — history stays.
- **Candidate questionnaire:** self-service form on the public offer page after acceptance, data flows back into the employee profile (mirrors the real-world flow I built at my last job).
- **Hiring funnel trend over time:** stage 4 shipped a point-in-time snapshot (`GET /stats`); still open — a weekly/monthly trend of offers by status plus a conversion-rate metric.
- **HR leaderboard:** number of offers created/accepted per HR employee, dashboard widget or standalone page.

## Someday / maybe
- **Calendar module:** company events + employee birthdays/anniversaries, matched with news (I rebuilt a calendar like this at my previous company).
- **Events module:** matched with news + calendar (was in my old backlog at work).
- **Audit log ("change history"):** who changed what and when, admin-only page. Table `audit_log`, write on every mutation.
- **CSV export** on the offers table (done for employees in stage 2).
- **Cascading department → position filter** on the employees table (needs a migration for a `department` reference, seed data, and a `/employees/positions?department=` endpoint).
- **Auto-refresh toggle** on tables ("update every N minutes") — pattern from my previous company's system.
- **Notifications:** in-app bell + optional Telegram push on offer status change (reuse my TG-bot experience).
- **AI summary endpoint:** condensed version of long news items for the feed.
- **Dark theme** (if not done in stage 6) — note: ApexCharts (dashboard charts, stage 4) themes via explicit `options` props, not CSS variables, so this needs a small wrapper to re-theme on toggle.
- **Dashboard date-range filter:** scope `/stats` to a period instead of always "current snapshot".
- **Dashboard export:** PDF/report snapshot of the dashboard.
- **Offer templates:** predefined position templates to speed up offer creation.
- **GSAP animations on the public offer page:** motion/micro-interactions for the candidate-facing `/offer/{token}` page — brand moment, not needed for MVP.

## Tech debt
- Fix Pydantic deprecation warning in `app/core/config.py` (class-based `config` → `ConfigDict`).
- Translate remaining Russian code comments to English (seed script, main.py CORS comment).
- Add `Architecture Decisions` section to README and backfill decisions made so far (users vs employees split, token in public offer links, SET NULL on user deletion).
- **BaseIcon component:** props → CSS-variables pattern (`width`, `fill`, `fillHover`, `rotate`), for future status/sort icons.
- **Form validation via vuelidate:** login, `/profile`, and future offer-module forms, with a single shared error-message style under each field.
- **Placeholder text + required-field markers:** meaningful placeholder text on every form input across ALL pages (login, profile, employees, offers, news), plus mark required fields with `*` next to the label — currently ad hoc/missing in places.
- **`/ui-kit` page:** a mini-Storybook listing all `components/base/*` with their prop variants, for visual regression checks during development.
- **Frontend tests in CI:** add a test step to `frontend-ci.yml` once unit/e2e tests exist.
- **`dorny/paths-filter` for CI:** if backend and frontend workflows ever merge into one file, use it for per-job path filtering.
- **Offer editing beyond draft:** allow editing offer fields any time before `accepted` or `expired` (not just while `draft`) — requires reworking the `send_offer`/`update_offer_draft` status gate in `backend/app/offers/service.py`. Changes the offer-creation flow (stage 3).
- **Offer preview available at any status:** the create-form's candidate-view preview should be reachable from the `/offers` table for already-sent/accepted/declined/expired offers too, not only during the draft-creation wizard.
- **Retention policy for archived offers:** auto-cleanup by storage duration (uses `archived_at`); tie into the employee offboarding flow.
- **Eager expiry resolution:** a scheduled job (cron) to flip due `sent` offers to `expired`, instead of relying only on lazy resolution on read (`offers/service.py`, and the bulk resolve added for `GET /stats`).
- **Configurable recent-widget size:** dashboard's "recent offers"/"recent news" limit is hardcoded to 5.
