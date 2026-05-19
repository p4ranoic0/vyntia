# Run the Employment Lifecycle E2E

> Manual runbook for the opt-in Playwright lifecycle suite (ADR-B.5,
> backlog item #132). This test exercises the full Module 03 happy path:
> hire → contract → onboarding → desplazamiento → cese with liquidation.
> It is **release-gate-only** — run before promoting any release branch
> that touches Vyntia Core.

## When to run

- Before tagging a Vyntia Core release.
- After any change that touches contracts, onboarding, desplazamiento, or
  desvinculación flows (front or back).
- Periodic smoke before customer demos that walk the full lifecycle.

Default CI does **not** run this — too heavy and seed-dependent.

## Prerequisites

1. **Local Postgres** with database `bd_vyntia` migrated to head.
2. **Backend dev server** running on `:8000`:
   ```bash
   cd apps/api
   python manage.py runserver --settings=vyntia.settings.development
   ```
3. **Frontend dev server** running on `:5173`:
   ```bash
   cd apps/web
   npm run dev
   ```
4. **Seeded tenant** (idempotent — run before every session):
   ```bash
   cd apps/api
   python manage.py seed_lifecycle_e2e --settings=vyntia.settings.development
   ```
   The command prints a `SEED_OUTPUT: {...}` line on stdout with the
   admin credentials and the tenant slug — keep it for reference but
   the test hardcodes them so you don't have to wire anything.

## Run the test

```bash
cd apps/web
RUN_LIFECYCLE_E2E=1 npx playwright test tests/e2e/employment-lifecycle.test.js
```

Expected duration: < 3 minutes on a warm cache. On first run Playwright
may install the chromium binary.

## Interpreting results

- **Pass:** test exits 0; nothing else needed.
- **Fail:** Playwright writes `apps/web/playwright-report/` with a full
  trace, screenshots at failure, and a video on retry. Open the HTML
  report:
  ```bash
  npx playwright show-report
  ```
- **Skipped:** `RUN_LIFECYCLE_E2E` was not set (or the test guard
  triggered). Re-run with the env var.

## Cleanup

The seed is idempotent — re-running it is a no-op. To fully reset:

```bash
cd apps/api
python manage.py shell --settings=vyntia.settings.development <<'PY'
from apps.tenancy.models import Tenant
Tenant.objects.filter(slug="lifecycle").delete()
PY
```

(Cascading deletes via FKs remove the membership + scoped catalog.)

## Why it is opt-in

Per ADR-B.5 we deliberately keep this suite out of default CI:

- Mutates DB state — unsafe to run in a shared environment.
- Requires both dev servers + DB on the runner — too heavy for per-phase CI.
- Doubles as a sales-friendly walkthrough script. Keeping it as a manual
  release gate means it gets regular eyeball checks rather than rotting
  into a green-but-broken CI artifact.

## Related

- ADR: `.planning/audit-B/ADRS.md` § ADR-B.5
- Backlog: `.planning/audit-B/BACKLOG.md` item #132
- Seed command: `apps/api/apps/tenancy/management/commands/seed_lifecycle_e2e.py`
- Test: `apps/web/tests/e2e/employment-lifecycle.test.js`
- Sibling opt-in suite: `apps/web/tests/e2e/tenant-isolation.test.js`
