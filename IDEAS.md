# IDEAS.md — backlog

Rules: new ideas land here, NOT in the current stage. Review after the minimal showcase is deployed (stages 0–3 done + deploy). One line per idea; promote to PLAN.md when actually scheduled.

## Next up (strong candidates after MVP)
- **Offboarding flow:** deactivate employee (`employees.is_active=False`) + revoke login (`users.is_active=False` or unlink), "Inactive" filter tab on the employees table. Employee record is never deleted — history stays.
- **Candidate questionnaire:** self-service form on the public offer page after acceptance, data flows back into the employee profile (mirrors the real-world flow I built at my last job).
- **Hiring funnel dashboard widget:** offers by status over time (sent → accepted / declined / expired), conversion rate.

## Someday / maybe
- **Calendar module:** company events + employee birthdays/anniversaries, matched with news (I rebuilt a calendar like this at my previous company).
- **Events module:** matched with news + calendar (was in my old backlog at work).
- **Audit log ("change history"):** who changed what and when, admin-only page. Table `audit_log`, write on every mutation.
- **CSV export** on employees and offers tables.
- **Auto-refresh toggle** on tables ("update every N minutes") — pattern from my previous company's system.
- **Notifications:** in-app bell + optional Telegram push on offer status change (reuse my TG-bot experience).
- **AI summary endpoint:** condensed version of long news items for the feed.
- **Dark theme** (if not done in stage 6).
- **Offer templates:** predefined position templates to speed up offer creation.

## Tech debt
- Fix Pydantic deprecation warning in `app/core/config.py` (class-based `config` → `ConfigDict`).
- Translate remaining Russian code comments to English (seed script, main.py CORS comment).
- Add `Architecture Decisions` section to README and backfill decisions made so far (users vs employees split, token in public offer links, SET NULL on user deletion).
