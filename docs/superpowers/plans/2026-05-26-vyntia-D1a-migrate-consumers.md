# D.1a — Migrate Legacy Payroll Consumers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decouple every active consumer from the legacy `apps.payroll` models + services so that D.1b can drop those models cleanly, while keeping every `/api/v1/payroll/*` URL responding with a structured **HTTP 501** (not 404) during the Vyntia Pay rebuild.

**Architecture:** The legacy payroll API (8 ViewSets in `api/v1/rrhh/remuneraciones_views.py` + `remuneraciones_serializers.py`, registered in `api/v1/payroll/urls.py`) is replaced by a single catch-all 501 stub view that imports nothing from `apps.payroll`. Two orphaned duplicate viewsets/serializers in `views.py`/`serializers.py` (dead since L3.11) are deleted with their legacy imports. The frontend already degrades gracefully on 501 (react-query + toast on all 8 payroll pages); only `HROverviewDashboard`'s dashboard widget gets an explicit empty-state guard. After this phase, `grep "from apps.payroll" apps/api/` outside `apps/payroll/` itself returns zero → D.1b is unblocked.

**Tech Stack:** Django 5.2 + DRF, React 18 + TS + react-query, pytest, vitest.

**Source:** `.planning/audit-D/BACKLOG.md` items #1, #2, #3, #4, #13 ([D.1a] tagged); `.planning/audit-D/ROADMAP-D.md` Adjustment 1; `.planning/audit-D/INVENTORY.md` § 1 + § 3.

---

## Baseline snapshot

| Check | Before D.1a | After D.1a |
|---|---|---|
| Backend pytest | 1058 passed, 1 failed (`test_permisos_debug`), 17 skipped | passing count drops by the # of deleted legacy-endpoint tests; still **1 pre-existing failure, 0 new failures** |
| `grep "from apps.payroll" apps/api/` outside `apps/payroll/` | 4 files (views, serializers, remuneraciones_views, remuneraciones_serializers) | **0 files** |
| `/api/v1/payroll/*` HTTP status | 200/4xx (legacy live) | **501** for every path + verb |
| Frontend vitest | 178 passed / 28 files | ≥ baseline (1 guard test may be added) |
| Frontend build / tsc | clean / 1 pre-existing (`BlankEnum.ts`) | unchanged |
| `manage.py check` | 0 silenced | 0 silenced |

**No legacy MODELS or SERVICES are deleted in D.1a** — only their API-surface consumers. Models + services drop in D.1b (which also adds `AuditEvent.schema_version`).

---

## Branch

`vyntia/D1a-migrate-consumers` — branched from `master` (HEAD `ccecddc7`, the D-prep-foundation + D.0 merge).

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/D1a-migrate-consumers
```

---

## File structure

**Create:**
- `apps/api/api/v1/payroll/stub_views.py` — `PayrollUnavailableView` (501 catch-all, no `apps.payroll` import)
- `apps/api/tests/test_payroll_legacy_stub.py` — asserts 501 + URL routing

**Modify:**
- `apps/api/api/v1/payroll/urls.py` — replace router with catch-all → stub view
- `apps/api/api/v1/rrhh/views.py` — delete 2 dead viewsets + remove `apps.payroll` import (line 8)
- `apps/api/api/v1/rrhh/serializers.py` — delete 2 dead serializers + remove `apps.payroll` import (line 7)
- `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` — guard `usePlanillasMes` queryFn

**Delete:**
- `apps/api/api/v1/rrhh/remuneraciones_views.py` — 8 legacy viewsets (no longer imported after urls rewrite)
- `apps/api/api/v1/rrhh/remuneraciones_serializers.py` — legacy serializers (imported only by the deleted views)
- Legacy payroll **endpoint** test files identified in Task 1 (they exercise removed API surface)

**Do NOT touch:**
- `apps/api/apps/payroll/` (models, services, migrations, `seed_remuneraciones_config`) — D.1b scope
- `apps/web/src/features/payroll/services/payrollService.ts` (verified: degrades gracefully on 501)
- The 8 `apps/web/src/features/payroll/pages/*` (rebuilt per-phase in D.2/D.5/D.6)

---

## Task 1: Recon — confirm dead code + locate legacy payroll tests (no code change)

**Files:** none modified. This task locks the exact deletion targets and protects against stale assumptions before any edit.

- [ ] **Step 1.1: Confirm the 2 viewsets in `views.py` are dead (registered nowhere)**

```bash
# Use Grep tool — search ALL urls.py for the duplicate viewset names
pattern: "ConfiguracionAfpViewSet|ConfiguracionRemuneracionViewSet"
path: apps/api
glob: "**/urls.py"
output_mode: content
```

Expected: matches ONLY in `apps/api/api/v1/payroll/urls.py`, which imports them `from api.v1.rrhh.remuneraciones_views import ...`. If any `urls.py` imports them from `api.v1.rrhh.views`, STOP — they are not dead; escalate.

- [ ] **Step 1.2: Confirm `serializers.py`'s 2 serializers back only the dead viewsets**

```bash
# Use Grep tool
pattern: "ConfiguracionAfpSerializer|ConfiguracionRemuneracionSerializer"
path: apps/api
output_mode: content
-n: true
```

Expected: definitions in `serializers.py` (~L361, ~L427) + usage only in `views.py` dead viewsets (~L1186, ~L1246). `remuneraciones_views.py` uses its OWN serializers from `remuneraciones_serializers.py` (different module). If `serializers.py`'s versions are imported by `remuneraciones_views.py` or elsewhere active, note it and adjust Task 4.

- [ ] **Step 1.3: Confirm `remuneraciones_serializers.py` is imported only by `remuneraciones_views.py`**

```bash
# Use Grep tool
pattern: "remuneraciones_serializers"
path: apps/api
output_mode: content
-n: true
```

Expected: imported only inside `remuneraciones_views.py`. If imported elsewhere, that consumer must also be migrated — escalate before deleting the file.

- [ ] **Step 1.4: Enumerate every legacy `apps.payroll` consumer outside `apps/payroll/`**

```bash
# Use Grep tool
pattern: "from apps\\.payroll|apps\\.payroll\\.|['\"]payroll\\."
path: apps/api
output_mode: files_with_matches
```

Expected exactly these 4 files outside `apps/api/apps/payroll/`: `api/v1/rrhh/views.py`, `api/v1/rrhh/serializers.py`, `api/v1/rrhh/remuneraciones_views.py`, `api/v1/rrhh/remuneraciones_serializers.py`. Record the list — Task 6 re-runs this and expects **0**.

- [ ] **Step 1.5: Locate legacy payroll ENDPOINT tests (to delete) vs MODEL/SERVICE tests (to keep)**

```bash
# Use Grep tool — endpoint tests (delete in Task 3)
pattern: "/api/v1/payroll/|monthly-runs|mass-deductions|tax-parameters|afp-configurations|compensation-configurations|payslips|payment-schedules|payroll/details"
path: apps/api
glob: "**/test_*.py"
output_mode: files_with_matches
```

```bash
# Use Grep tool — model/service tests (KEEP — drop in D.1b)
pattern: "PlanillaCalculoService|DescuentoMasivoService|MonthlyPayroll|PayrollDetail|MassDeduction\\b"
path: apps/api
glob: "**/test_*.py"
output_mode: files_with_matches
```

Record both lists. Endpoint-test files/cases get deleted in Task 3. Model/service-test files stay untouched (they still pass — models/services live until D.1b). A test file that mixes both: delete only the endpoint cases, keep model/service cases.

- [ ] **Step 1.6: Capture the exact baseline**

```bash
cd D:/VYNTIA && source .venv/Scripts/activate && cd apps/api
pytest --tb=no -q 2>&1 | tail -3
```

Expected: `1058 passed, 1 failed, 17 skipped`. Record the passed count `N_before`. After Task 3 deletes E endpoint tests, the new expected passing = `N_before − E` (record E from Step 1.5). No NEW failures allowed.

---

## Task 2: Backend 501 stub for the legacy payroll URL surface (TDD)

**Files:**
- Create: `apps/api/api/v1/payroll/stub_views.py`
- Create: `apps/api/tests/test_payroll_legacy_stub.py`
- Modify: `apps/api/api/v1/payroll/urls.py`

- [ ] **Step 2.1: Write the failing test**

Create `apps/api/tests/test_payroll_legacy_stub.py`:

```python
"""D.1a — legacy /api/v1/payroll/* surface must return structured 501, not 404."""

from django.urls import resolve
from rest_framework.test import APIRequestFactory

from api.v1.payroll.stub_views import PayrollUnavailableView


def test_stub_view_returns_501_for_every_verb():
    factory = APIRequestFactory()
    view = PayrollUnavailableView.as_view()
    for method in ("get", "post", "put", "patch", "delete"):
        request = getattr(factory, method)("/api/v1/payroll/monthly-runs/")
        response = view(request)
        assert response.status_code == 501, f"{method} returned {response.status_code}"
        assert response.data["success"] is False
        assert response.data["error_code"] == "payroll_rebuilding"


def test_all_legacy_payroll_paths_resolve_to_stub():
    paths = [
        "/api/v1/payroll/monthly-runs/",
        "/api/v1/payroll/monthly-runs/abc-123/calcular_planilla/",
        "/api/v1/payroll/tax-parameters/",
        "/api/v1/payroll/payslips/abc-123/pdf/",
        "/api/v1/payroll/mass-deductions/abc-123/anular/",
        "/api/v1/payroll/compensation-configurations/",
    ]
    for path in paths:
        match = resolve(path)
        assert getattr(match.func, "cls", None) is PayrollUnavailableView, path
```

- [ ] **Step 2.2: Run it to confirm it fails**

Run: `pytest tests/test_payroll_legacy_stub.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'api.v1.payroll.stub_views'` (module not created yet).

- [ ] **Step 2.3: Create the stub view**

Create `apps/api/api/v1/payroll/stub_views.py`:

```python
"""Stub for the legacy payroll API surface during the Vyntia Pay migration.

The legacy `apps.payroll` models + services are dropped in D.1b and rebuilt
greenfield across D.2-D.6. During the transition every legacy
`/api/v1/payroll/*` URL must keep returning a structured HTTP 501 (not a 404)
so existing frontend consumers degrade gracefully.

This module imports NOTHING from `apps.payroll` — that is what lets D.1b drop
those models without breaking the URL conf.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.responses import APIResponse

_MESSAGE = (
    "El módulo de planilla está en reconstrucción (Vyntia Pay). "
    "Este endpoint estará disponible en una próxima fase."
)


class PayrollUnavailableView(APIView):
    """Catch-all 501 for every legacy /api/v1/payroll/* route + verb."""

    permission_classes = [AllowAny]

    def _gone(self, request, *args, **kwargs):
        return APIResponse.error(
            message=_MESSAGE,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code="payroll_rebuilding",
        )

    get = _gone
    post = _gone
    put = _gone
    patch = _gone
    delete = _gone
```

- [ ] **Step 2.4: Rewrite the URL conf to a catch-all**

Replace the entire contents of `apps/api/api/v1/payroll/urls.py` with:

```python
"""URLs for payroll bounded context.

Legacy payroll API is stubbed during the Vyntia Pay migration (D.1a). A
catch-all routes every /api/v1/payroll/* path + verb to a 501 so frontend
consumers degrade gracefully until each endpoint family is rebuilt
(D.2 config, D.5 runs, D.6 boletas).
"""

from django.urls import re_path

from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

urlpatterns = [
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]
```

- [ ] **Step 2.5: Run the test to confirm it passes**

Run: `pytest tests/test_payroll_legacy_stub.py -v`
Expected: PASS (2 tests).

- [ ] **Step 2.6: Confirm `manage.py check` still clean**

Run: `python manage.py check --settings=vyntia.settings.development`
Expected: `System check identified no issues (0 silenced).` (Note: `remuneraciones_views.py` is still imported nowhere-but-itself now that urls.py no longer imports it; it is deleted in Task 3.)

- [ ] **Step 2.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/payroll/stub_views.py apps/api/api/v1/payroll/urls.py apps/api/tests/test_payroll_legacy_stub.py
git commit -m "feat(D1a): 501 stub for legacy /api/v1/payroll/* surface"
```

---

## Task 3: Delete the active legacy payroll API implementation + its endpoint tests

**Files:**
- Delete: `apps/api/api/v1/rrhh/remuneraciones_views.py`
- Delete: `apps/api/api/v1/rrhh/remuneraciones_serializers.py`
- Delete/trim: legacy payroll **endpoint** test files from Task 1 Step 1.5

- [ ] **Step 3.1: Delete the two legacy API modules**

```bash
cd D:/VYNTIA
git rm apps/api/api/v1/rrhh/remuneraciones_views.py apps/api/api/v1/rrhh/remuneraciones_serializers.py
```

(Safe: Task 1 Step 1.3 confirmed `remuneraciones_serializers` is imported only by `remuneraciones_views`, and Task 2.4 removed the only import of `remuneraciones_views` from `urls.py`.)

- [ ] **Step 3.2: Delete the legacy payroll ENDPOINT tests identified in Step 1.5**

For each endpoint-test file from Step 1.5's FIRST grep (those hitting `/api/v1/payroll/*` or the deleted viewsets/serializers):

```bash
# Example — use the actual paths recorded in Step 1.5
git rm apps/api/<path>/test_<legacy_payroll_endpoint>.py
```

For a file mixing endpoint + model/service cases: open it and delete only the endpoint test functions/classes (those using `APIClient`/`reverse` against `/api/v1/payroll/*` or importing the deleted viewsets/serializers); keep the model/service cases. Do NOT delete tests that import only `apps.payroll.models` / services (those stay green until D.1b).

- [ ] **Step 3.3: Run check + targeted pytest to confirm no import errors**

```bash
cd D:/VYNTIA && source .venv/Scripts/activate && cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/test_payroll_legacy_stub.py -v
```

Expected: check clean (0 silenced); stub tests still PASS. No `ImportError`/`ModuleNotFoundError` from the deletions.

- [ ] **Step 3.4: Commit**

```bash
cd D:/VYNTIA
git add -A apps/api/api/v1/rrhh/ apps/api/
git commit -m "refactor(D1a): drop legacy payroll viewsets/serializers + endpoint tests (URIs now 501)"
```

---

## Task 4: Remove dead duplicate viewsets/serializers + legacy imports in views.py/serializers.py

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py`
- Modify: `apps/api/api/v1/rrhh/serializers.py`

(Task 1 Steps 1.1–1.2 confirmed these are orphaned — registered/used nowhere after L3.11.)

- [ ] **Step 4.1: Delete the 2 dead viewsets + import in `views.py`**

In `apps/api/api/v1/rrhh/views.py`:
1. Delete the entire `class ConfiguracionRemuneracionViewSet(viewsets.ModelViewSet):` block (starts ~L1182).
2. Delete the entire `class ConfiguracionAfpViewSet(viewsets.ModelViewSet):` block (starts ~L1242).
3. Delete the import line (~L8): `from apps.payroll.models import AfpConfiguration, CompensationConfiguration`

Use Read to view the exact current line ranges first (they may have shifted), then Edit to remove each class block and the import.

- [ ] **Step 4.2: Delete the 2 dead serializers + import in `serializers.py`**

In `apps/api/api/v1/rrhh/serializers.py`:
1. Delete the entire `class ConfiguracionRemuneracionSerializer` block (~L361–424).
2. Delete the entire `class ConfiguracionAfpSerializer` block (~L427–495).
3. Delete the import line (~L7): `from apps.payroll.models import AfpConfiguration, CompensationConfiguration`

- [ ] **Step 4.3: Confirm nothing referenced the deleted symbols**

```bash
# Use Grep tool — must be 0 matches now
pattern: "ConfiguracionRemuneracionSerializer|ConfiguracionAfpSerializer|ConfiguracionRemuneracionViewSet|ConfiguracionAfpViewSet"
path: apps/api
output_mode: content
-n: true
```

Expected: 0 matches (all definitions + references removed). If any remain, fix the dangling reference before continuing.

- [ ] **Step 4.4: Run check + commit**

```bash
cd D:/VYNTIA && source .venv/Scripts/activate && cd apps/api
python manage.py check --settings=vyntia.settings.development
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/api/v1/rrhh/serializers.py
git commit -m "refactor(D1a): remove dead duplicate Configuracion* viewsets/serializers + apps.payroll imports"
```

Expected: check clean.

---

## Task 5: Frontend — guard HROverviewDashboard dashboard widget

**Files:**
- Modify: `apps/web/src/features/employees/pages/HROverviewDashboard.tsx`

- [ ] **Step 5.1: Guard the `usePlanillasMes` queryFn**

In `apps/web/src/features/employees/pages/HROverviewDashboard.tsx`, the `usePlanillasMes` hook (~L139–153) calls `/api/v1/payroll/monthly-runs/`. Wrap the fetch so a 501 yields an empty list instead of an error state, and stop react-query from retrying the stub. Replace the `useQuery({...})` body with:

```typescript
function usePlanillasMes() {
  return useQuery<PlanillaMensual[]>({
    queryKey: ['dashboard', 'planillas-mes'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<{ data?: PlanillaMensual[]; results?: PlanillaMensual[] }>(
          '/api/v1/payroll/monthly-runs/',
          { page_size: 6, ordering: '-periodo' },
        )
        const raw = response.data as any
        return raw?.data ?? raw?.results ?? []
      } catch {
        // Payroll module is being rebuilt in Vyntia Pay (D); endpoint returns 501
        // until D.5. Show an empty widget instead of an error state.
        return []
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}
```

(Match the exact existing import names for `apiClient` / `useQuery` / `PlanillaMensual` already present in the file — do not add new imports.)

- [ ] **Step 5.2: Verify build + tsc + lint + vitest**

```bash
cd D:/VYNTIA/apps/web
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
npm run build 2>&1 | tail -3
npm run lint 2>&1 | tail -3
npm test -- --run 2>&1 | tail -5
```

Expected: tsc 1 pre-existing (`BlankEnum.ts`) only; build clean; lint ≤ 278; vitest ≥ 178 passed (no regressions).

- [ ] **Step 5.3: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/employees/pages/HROverviewDashboard.tsx
git commit -m "fix(D1a): HROverviewDashboard payroll widget degrades to empty on 501"
```

---

## Task 6: Full decoupling verification + baselines + close-out

**Files:** `.planning/audit-D/BACKLOG.md` (check off D.1a items)

- [ ] **Step 6.1: Confirm zero legacy `apps.payroll` consumers remain outside `apps/payroll/`**

```bash
# Use Grep tool
pattern: "from apps\\.payroll|apps\\.payroll\\.|['\"]payroll\\."
path: apps/api
output_mode: files_with_matches
```

Expected: matches ONLY inside `apps/api/apps/payroll/` itself (models, services, `seed_remuneraciones_config`). **Zero** matches under `apps/api/api/`. This is the gate that unblocks D.1b.

- [ ] **Step 6.2: Full backend test suite**

```bash
cd D:/VYNTIA && source .venv/Scripts/activate && cd apps/api
pytest --tb=short -q 2>&1 | tail -8
```

Expected: `(N_before − E) passed, 1 failed (test_permisos_debug), 17 skipped` where E = number of legacy endpoint tests deleted in Task 3. **0 new failures, 0 errors.** If any new failure/error: investigate (likely a missed reference to a deleted symbol or a model/service test wrongly deleted).

- [ ] **Step 6.3: Frontend full gate**

```bash
cd D:/VYNTIA/apps/web
npm run build && npx tsc --noEmit -p tsconfig.app.json && npm run lint && npm test -- --run
```

Expected: build clean; tsc 1 pre-existing; lint ≤ 278; vitest ≥ 178.

- [ ] **Step 6.4: Manual smoke (optional but recommended)**

If a dev server + DB are available, curl two legacy endpoints and confirm 501 JSON:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/v1/payroll/monthly-runs/
curl -s http://127.0.0.1:8000/api/v1/payroll/tax-parameters/ | head -c 200
```

Expected: `501`; body `{"success": false, "message": "El módulo de planilla está en reconstrucción ...", "error_code": "payroll_rebuilding"}`. (Skip if local `runserver` is blocked by the known psycopg2 UnicodeDecodeError — the stub unit tests in Task 2 already prove the behavior.)

- [ ] **Step 6.5: Check off the D.1a backlog items**

In `.planning/audit-D/BACKLOG.md`, mark items #1, #2, #3, #4 as done (e.g., prefix the Item cell with `✅`). Item #13 (document D.1a/D.1b split) is already satisfied by ROADMAP-D Adjustment 1 — mark it done too.

- [ ] **Step 6.6: Final commit**

```bash
cd D:/VYNTIA
git add .planning/audit-D/BACKLOG.md
git commit -m "docs(D1a): mark D.1a backlog items #1-4,#13 complete"
git log --oneline master..HEAD
```

Expected: ~6 commits on `vyntia/D1a-migrate-consumers`.

---

## D.1a Done — Handoff to D.1b

D.1b can now safely:
- Drop the 9 legacy `apps.payroll` models + 2 services + `seed_remuneraciones_config` (zero external consumers — verified Step 6.1).
- Squash the 2 legacy payroll migrations.
- Add `AuditEvent.schema_version` field (ADR-D.3 / BACKLOG #9).

Generate `2026-05-XX-vyntia-D1b-drop-legacy.md` with `writing-plans` when D.1b starts, using BACKLOG items #5, #6, #7, #8, #9, #10 (and #12 regression suite) as source.

---

## Notes / decisions locked in this plan

1. **501 (not 410/404):** "Not Implemented" matches the semantic "endpoint exists, rebuild in progress". Catch-all `re_path` guarantees custom actions (`calcular_planilla`, `pdf`, `anular`, …) also return 501, never 404 — satisfying BACKLOG #4.
2. **Legacy payroll UI goes dark, gracefully:** consistent with the locked D-I greenfield decision. The 8 payroll admin pages already handle 501 via react-query + toast (verified in audit recon); they are rebuilt per-phase (D.2 config, D.5 runs, D.6 boletas). Only the always-on dashboard widget needed an explicit empty-state guard.
3. **Models/services stay until D.1b:** D.1a removes only API-surface consumers. This keeps the change reviewable and lets model/service unit tests stay green through D.1a.
