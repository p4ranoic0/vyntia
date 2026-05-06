# VYNTIA Foundation L3.11 — Cleanup `app_rrhh/` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dead code accumulated in `app_rrhh/` after L3.1–L3.10 split, eliminate legacy URL aliases that the frontend no longer uses, and fix 2 dead-code reverse-accessor refs (`rol_set`, `permiso_set`) that survive from the pre-rename era.

**Architecture:** Single-PR pragmatic cleanup. Discriminate dead vs active modules in `app_rrhh/`: delete the dead (legacy `views.py`/`urls.py`/`serializers.py`/`models.py`/`managers.py`/`admin.py`/`tests.py`/`filters.py`/`models/`/`managers/`), keep the active (`menu_service.py`, `permission_service.py`, `constants.py`, `validators.py`, `tasks.py`, `services/`, `management/commands/`, `apps.py`). Remove legacy URL paths (`/legacy/`, `/api/v1/rrhh/`, `/api/v1/vacaciones/`). Migrate 4 backend test files to new English URLs. Out-of-scope: relocating active `app_rrhh/X` modules to apps/X (deferred).

**Tech Stack:** Django 5.2 + DRF (backend only — no frontend changes).

**Spec source:** `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` row L3.11.

**Pre-conditions:**
- Branch `master` clean at HEAD = `47eaea49 docs(L3.10.4e): mark L3.10.4e merged`
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped
- Frontend build clean (no frontend changes in this PR)
- Frontend already migrated to new English URLs (post-L3.10.4b)
- bd_vyntia provisioned, virtualenv at `D:/VYNTIA/.venv/`

**Scope (this plan only):**
- Fix 2 dead-code refs: `usuario.rol_set.set(...)` in `app_rrhh/services.py:370` and `Module.objects.prefetch_related("permiso_set")` in `api/v1/rrhh/views.py:393`
- Remove `path('legacy/', include('app_rrhh.urls'))` from `vyntia/urls.py`
- Remove `path('rrhh/', ...)` and `path('vacaciones/', ...)` from `api/v1/urls.py`
- Migrate 4 backend test files to use new English URLs
- Delete dead files in `app_rrhh/`: `urls.py`, `views.py`, `serializers.py`, `serializers_optimized.py`, `models.py`, `models/` directory, `managers.py`, `managers/` directory, `admin.py`, `tests.py`, `filters.py`, `services.py` (the `.py` file shadowed by `services/` package)
- Optionally delete `api/v1/rrhh/` and `api/v1/vacaciones/` URL config files (the ViewSets stay in place — only `urls.py` files removed)

**Out of scope (separate sub-PRs / L4):**
- Relocating active `app_rrhh/{menu_service,permission_service,constants,validators,tasks,services}` to appropriate `apps/X/` (e.g., move `permission_service` → `apps/identity/`, `tasks` → `apps/core/`). This is L4 cleanup territory.
- Renaming `api/v1/rrhh/` → `api/v1/_legacy_views/` or refactoring views into per-app structure. The new English URLs (`/identity/`, `/employees/`, etc.) already import these ViewSets — that's working code, not legacy.
- Removing `app_rrhh` from `LOCAL_APPS` in settings (still needed for `management/commands/` to be discovered).
- Frontend changes — none required (already on new URLs since L3.10.4b).
- The 8 pre-existing pytest failures (separate cleanup).

---

## File Structure

Files modified or deleted:

| File | Action | Why touched |
|---|---|---|
| `apps/api/api/v1/rrhh/views.py` | Modify (line 393) | Fix `permiso_set` → correct reverse-accessor name |
| `apps/api/app_rrhh/services.py` | Delete | Shadowed by `services/` package; contains dead `rol_set` ref |
| `apps/api/vyntia/urls.py` | Modify | Remove `path('legacy/', ...)` |
| `apps/api/api/v1/urls.py` | Modify | Remove `path('rrhh/', ...)` and `path('vacaciones/', ...)` |
| `apps/api/tests/test_documentos_digitales_onboarding.py` | Modify | Migrate URLs |
| `apps/api/tests/test_empleado_update_v2.py` | Modify | Migrate URLs |
| `apps/api/tests/test_onboarding_api.py` | Modify | Migrate URLs |
| `apps/api/tests/test_onboarding_self_update.py` | Modify | Migrate URLs |
| `apps/api/app_rrhh/urls.py` | Delete | No longer included anywhere |
| `apps/api/app_rrhh/views.py` | Delete | Only used by deleted urls.py |
| `apps/api/app_rrhh/serializers.py` | Delete | Only used by deleted views.py |
| `apps/api/app_rrhh/serializers_optimized.py` | Delete | Only used by deleted views.py |
| `apps/api/app_rrhh/models.py` | Delete | Empty re-export shim |
| `apps/api/app_rrhh/models/` | Delete (dir) | `__all__ = []`; nothing inside |
| `apps/api/app_rrhh/managers.py` | Delete | All consumers commented out |
| `apps/api/app_rrhh/managers/` | Delete (dir) | Only used internally by deleted code |
| `apps/api/app_rrhh/admin.py` | Delete | Empty boilerplate |
| `apps/api/app_rrhh/tests.py` | Delete | Legacy test file |
| `apps/api/app_rrhh/filters.py` | Delete | Replaced by `api/v1/rrhh/filters.py` |
| `apps/api/api/v1/rrhh/urls.py` | Delete | No longer included after `api/v1/urls.py` cleanup |
| `apps/api/api/v1/vacaciones/urls.py` | Delete | Same |
| `apps/api/api/v1/vacaciones/tests.py` | Delete | Tests use `/api/v1/vacaciones/` URLs |
| `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` | Modify | Mark L3.11 done |

**Active files KEPT (not touched by this PR):**
- `apps/api/app_rrhh/menu_service.py` — used by `api/v1/auth/views.py`
- `apps/api/app_rrhh/permission_service.py` — used by core/decorators, vacaciones permissions, time_off services
- `apps/api/app_rrhh/constants.py` — Roles enum used by same consumers
- `apps/api/app_rrhh/validators.py` — used by `api/v1/vacaciones/validators.py`
- `apps/api/app_rrhh/tasks.py` — `send_email_html_task` used by onboarding/vacation services
- `apps/api/app_rrhh/services/` (package) — `empleado_report_service` used by `api/v1/rrhh/views.py`
- `apps/api/app_rrhh/management/commands/*` — Django management commands
- `apps/api/app_rrhh/__init__.py`, `apps/api/app_rrhh/apps.py`, `apps/api/app_rrhh/migrations/__init__.py` — Django app boilerplate
- `apps/api/api/v1/rrhh/views.py`, `serializers.py`, etc. — these ARE the canonical implementations imported by the new English URL configs (despite living under `rrhh/` folder name)
- `apps/api/api/v1/vacaciones/views.py`, `serializers.py`, etc. — same — canonical impl reused by `api/v1/time_off/urls.py`
- `apps/api/api/v1/app_rrhh/document_generation_*.py` — canonical impl reused by `api/v1/documents/urls.py` and (legacy) `api/v1/rrhh/urls.py`

---

## Definition of Done

- [ ] 2 dead-code refs fixed (`rol_set` deleted with the file; `permiso_set` corrected)
- [ ] `path('legacy/', ...)` removed from `vyntia/urls.py`
- [ ] `path('rrhh/', ...)` and `path('vacaciones/', ...)` removed from `api/v1/urls.py`
- [ ] 4 backend test files migrated to new English URLs
- [ ] `api/v1/vacaciones/tests.py` migrated or deleted
- [ ] Dead app_rrhh files deleted (10 files + 2 directories)
- [ ] Legacy URL config files deleted (`api/v1/rrhh/urls.py`, `api/v1/vacaciones/urls.py`, `app_rrhh/urls.py`)
- [ ] `manage.py check` clean
- [ ] pytest baseline preserved at 161 passed, 8 failed, 3 skipped (or improved if test migration fixes some failures)
- [ ] frontend `npm run build` clean (regression check; no frontend changes expected)
- [ ] vitest 7 passed preserved
- [ ] runtime smoke: `/api/v1/identity/users/` returns 200 (regression: confirms removing rrhh/ legacy didn't break routing)
- [ ] Branch `vyntia/L3.11-cleanup-app-rrhh` merged to master with `--no-ff`
- [ ] Roadmap updated: L3.11 ✅
- [ ] Memory `active_subproject.md` updated with merge commit + Foundation L3 marked complete

---

## Task 1: Pre-flight — branch + baseline

- [ ] **Step 1: Confirm pwd + master state**

```bash
cd D:/VYNTIA
git status --short
git log --oneline -3
```

Expected: HEAD = `47eaea49 docs(L3.10.4e): mark L3.10.4e merged`. Working tree clean.

- [ ] **Step 2: Backend baseline**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_baseline_311.txt | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues` + `161 passed, 8 failed, 3 skipped`.

- [ ] **Step 3: Frontend baseline**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: build success + `Tests 7 passed (7)`.

- [ ] **Step 4: Snapshot — count app_rrhh files**

```bash
find D:/VYNTIA/apps/api/app_rrhh -type f -name "*.py" -not -path "*__pycache__*" | wc -l
```

Document the count.

- [ ] **Step 5: Create branch**

```bash
cd D:/VYNTIA
git checkout -b vyntia/L3.11-cleanup-app-rrhh
git status --short
```

Expected: on branch `vyntia/L3.11-cleanup-app-rrhh`, clean working tree.

---

## Task 2: Commit the plan

- [ ] **Step 1: Stage the plan file**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-05-vyntia-foundation-L3.11-cleanup-app-rrhh.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
docs(L3.11): add cleanup app_rrhh implementation plan

Step-by-step plan for removing dead app_rrhh files, legacy URL aliases,
and fixing 2 dead-code reverse-accessor refs. Pragmatic scope cuts:
deletes legacy /api/v1/rrhh/ and /api/v1/vacaciones/ URL prefixes (the
new English URLs reuse the same ViewSets); keeps active app_rrhh modules
(menu_service, permission_service, constants, validators, tasks,
services/) — module relocation deferred to L4 cleanup.

Predecessor: L3.10.4e cf9f8aff.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Verify**

```bash
git log --oneline -3
```

Expected: HEAD with `docs(L3.11): add cleanup app_rrhh implementation plan`.

---

## Task 3: Fix `permiso_set` dead-code ref in `api/v1/rrhh/views.py`

**File:** `apps/api/api/v1/rrhh/views.py:393`

**Context:** `ModulosViewSet.queryset = Module.objects.prefetch_related("permiso_set")`. The auto-generated reverse accessor `permiso_set` (from old `Permiso` model name) was renamed when L3.10.1 renamed `Permiso → Permission`. Looking at `apps/identity/models/rbac.py:240-260`, the actual relationships are:
- `ModulePermission.modulo` FK → Module (related_name="modulo_permisos")
- `ModulePermission.permiso` FK → Permission (related_name="modulos_relacionados")

The intent of the original code was likely to prefetch all permissions for a module via the join table. The correct prefetch is `modulo_permisos` (the M2M-through reverse accessor on Module).

- [ ] **Step 1: Read the file region**

```bash
sed -n '388,400p' D:/VYNTIA/apps/api/api/v1/rrhh/views.py
```

Verify line 393 contains `prefetch_related("permiso_set")`.

- [ ] **Step 2: Fix the prefetch**

Edit `apps/api/api/v1/rrhh/views.py`:
- old: `    queryset = Module.objects.prefetch_related("permiso_set")`
- new: `    queryset = Module.objects.prefetch_related("modulo_permisos")`

- [ ] **Step 3: Verify with manage.py check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues`.

- [ ] **Step 4: Run pytest to confirm no regression**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: 161 passed (or potentially 162 if a previously-failing test exercised this path).

- [ ] **Step 5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py
git commit -m "$(cat <<'EOF'
fix(L3.11): correct ModulosViewSet prefetch reverse-accessor name

L3.10.1 renamed Permiso -> Permission, which auto-changed the reverse
accessor on Module from 'permiso_set' to the actual related_name on
ModulePermission ('modulo_permisos'). The ViewSet queryset prefetch
still referenced the dead name; would error at runtime if exercised.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Remove `/legacy/` URL alias

**File:** `apps/api/vyntia/urls.py`

**Context:** `path('legacy/', include('app_rrhh.urls'))` includes `app_rrhh/urls.py` (which routes to legacy `app_rrhh/views.py`). Frontend never used `/legacy/`. The `app_rrhh/urls.py` and `views.py` files will be deleted in Task 7.

- [ ] **Step 1: Read current file**

```bash
cat D:/VYNTIA/apps/api/vyntia/urls.py
```

- [ ] **Step 2: Remove the legacy line**

Edit `apps/api/vyntia/urls.py`:
- old:
  ```
  urlpatterns = [
      path('admin/', admin.site.urls),
      path('api/v1/', include('api.v1.urls')),
      # Mantener compatibilidad con URLs legacy temporalmente
      path('legacy/', include('app_rrhh.urls')),
      
      # API Documentation
  ```
- new:
  ```
  urlpatterns = [
      path('admin/', admin.site.urls),
      path('api/v1/', include('api.v1.urls')),
      
      # API Documentation
  ```

- [ ] **Step 3: Verify**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: clean. (Note: `app_rrhh.urls` still exists but is no longer included; deleted in Task 7.)

- [ ] **Step 4: Don't commit yet** — bundle with Task 5 (related URL cleanup).

---

## Task 5: Remove legacy `/api/v1/rrhh/` and `/api/v1/vacaciones/` paths

**File:** `apps/api/api/v1/urls.py`

**Context:** Frontend migrated to `/api/v1/employees/`, `/api/v1/contracts/`, `/api/v1/identity/`, `/api/v1/time-off/`, etc. in L3.10.4b. Legacy paths are no longer needed for the frontend. Backend tests use them (migrated in Task 6).

- [ ] **Step 1: Read current file**

```bash
cat D:/VYNTIA/apps/api/api/v1/urls.py
```

- [ ] **Step 2: Remove legacy paths**

Edit `apps/api/api/v1/urls.py`:
- old:
  ```
  urlpatterns = [
      # Authentication
      path('auth/', include('api.v1.auth.urls')),

      # Legacy URLs (Spanish paths) — preserved until L3.11 cleanup
      path('rrhh/', include('api.v1.rrhh.urls')),
      path('vacaciones/', include('api.v1.vacaciones.urls')),

      # New canonical URLs (English paths) per spec § 3.4
      path('identity/', include('api.v1.identity.urls')),
  ```
- new:
  ```
  urlpatterns = [
      # Authentication
      path('auth/', include('api.v1.auth.urls')),

      # Canonical URLs (English paths) per spec § 3.4
      path('identity/', include('api.v1.identity.urls')),
  ```

Also update the docstring at the top:
- old:
  ```
  """URLs principales para API v1.

  Estructura:
  - /api/v1/auth/        - autenticación (legacy + canonical)
  - /api/v1/rrhh/...     - LEGACY URLs (preservadas hasta L3.11)
  - /api/v1/vacaciones/  - LEGACY URLs (preservadas hasta L3.11)
  - /api/v1/identity/    - NUEVO (English path) per spec § 3.4
  ```
- new:
  ```
  """URLs principales para API v1.

  Estructura (post-L3.11 — legacy /rrhh/ y /vacaciones/ removidos):
  - /api/v1/auth/        - autenticación
  - /api/v1/identity/    - English path per spec § 3.4
  ```

- [ ] **Step 3: Verify Django check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: clean. Legacy URL config files (`api/v1/rrhh/urls.py`, `api/v1/vacaciones/urls.py`) are no longer included; they'll be deleted in Task 7.

- [ ] **Step 4: Run pytest — expect failures in 4 test files**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: many tests fail because legacy URLs return 404. Documented as INTENTIONAL — Task 6 migrates them.

- [ ] **Step 5: Don't commit yet** — bundle with Task 6 (test migration).

---

## Task 6: Migrate backend tests to new English URLs

**Files:**
- `apps/api/tests/test_documentos_digitales_onboarding.py`
- `apps/api/tests/test_empleado_update_v2.py`
- `apps/api/tests/test_onboarding_api.py`
- `apps/api/tests/test_onboarding_self_update.py`
- `apps/api/api/v1/vacaciones/tests.py` (decision: migrate or delete)

**URL mapping:**
- `/api/v1/rrhh/empleados/` → `/api/v1/employees/`
- `/api/v1/rrhh/datos-familiares/` → `/api/v1/family-members/`
- `/api/v1/rrhh/datos-academicos/` → `/api/v1/academic-records/`
- `/api/v1/rrhh/datos-laborales/` → `/api/v1/employment-data/`
- `/api/v1/rrhh/documentos-digitales/` → `/api/v1/documents/documentos-digitales/` (verify by inspecting `api/v1/documents/urls.py`)
- `/api/v1/rrhh/onboarding/` → `/api/v1/onboarding/processes/`
- `/api/v1/vacaciones/...` → `/api/v1/time-off/...`

- [ ] **Step 1: Inspect `api/v1/documents/urls.py` to confirm document URLs**

```bash
cat D:/VYNTIA/apps/api/api/v1/documents/urls.py
```

Document the actual prefix for `documentos-digitales/` endpoint.

- [ ] **Step 2: Inspect `api/v1/onboarding/urls.py`**

```bash
cat D:/VYNTIA/apps/api/api/v1/onboarding/urls.py
```

Confirm where `corregir-correo/` and `subir-foto/` actions are routed.

- [ ] **Step 3: Migrate `test_documentos_digitales_onboarding.py`**

```bash
grep -n "/api/v1/rrhh/" D:/VYNTIA/apps/api/tests/test_documentos_digitales_onboarding.py
```

For each `/api/v1/rrhh/documentos-digitales/` URL, replace with the canonical English path determined in Step 1.

Edit each occurrence — use Edit with full line context.

- [ ] **Step 4: Migrate `test_empleado_update_v2.py`**

```bash
grep -n "/api/v1/rrhh/" D:/VYNTIA/apps/api/tests/test_empleado_update_v2.py
```

Replace `/api/v1/rrhh/empleados/{id}/` with `/api/v1/employees/{id}/`. Update both test code and docstrings.

- [ ] **Step 5: Migrate `test_onboarding_api.py`**

```bash
grep -n "/api/v1/rrhh/" D:/VYNTIA/apps/api/tests/test_onboarding_api.py
```

Replace `/api/v1/rrhh/onboarding/...` URLs with the canonical English paths from Step 2.

- [ ] **Step 6: Migrate `test_onboarding_self_update.py`**

```bash
grep -n "/api/v1/rrhh/" D:/VYNTIA/apps/api/tests/test_onboarding_self_update.py
```

Replace `/api/v1/rrhh/empleados/`, `/api/v1/rrhh/datos-familiares/` with `/api/v1/employees/`, `/api/v1/family-members/`.

- [ ] **Step 7: Decide on `api/v1/vacaciones/tests.py`**

```bash
ls -la D:/VYNTIA/apps/api/api/v1/vacaciones/tests.py
head -20 D:/VYNTIA/apps/api/api/v1/vacaciones/tests.py
grep -c "/api/v1/vacaciones/" D:/VYNTIA/apps/api/api/v1/vacaciones/tests.py
```

This test file lives co-located with the legacy `api/v1/vacaciones/` URL config. Two options:
- **Migrate**: replace `/api/v1/vacaciones/` → `/api/v1/time-off/` and move the file to `apps/api/tests/test_vacaciones_api.py` (or similar).
- **Delete**: if the tests are duplicates of others or no longer useful.

Inspect the file to choose. **Default**: migrate URLs and move the file to `apps/api/tests/`. If the migration would result in duplicate test coverage with existing `apps/api/tests/test_*vacaciones*` files, delete instead.

- [ ] **Step 8: Run pytest, fix any new failures**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=short -q 2>&1 | tee /tmp/pytest_after_url_migration.txt | tail -15
cd D:/VYNTIA
```

Expected: 161 passed, 8 failed (baseline), 3 skipped. If new failures appear, the URL mapping in Steps 3–7 was incorrect. Fix and re-run.

- [ ] **Step 9: Commit Tasks 4 + 5 + 6 together**

```bash
cd D:/VYNTIA
git add apps/api/vyntia/urls.py apps/api/api/v1/urls.py apps/api/tests/ apps/api/api/v1/vacaciones/tests.py 2>/dev/null || true
git status --short
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L3.11): remove legacy URL aliases + migrate tests to English paths

Removes:
- path('legacy/', include('app_rrhh.urls')) from vyntia/urls.py
- path('rrhh/', ...) and path('vacaciones/', ...) from api/v1/urls.py

Migrates 4 backend test files from legacy /api/v1/rrhh/ and
/api/v1/vacaciones/ URLs to canonical English paths (/employees/,
/family-members/, /academic-records/, /employment-data/, /documents/,
/onboarding/processes/, /time-off/). Frontend already migrated in
L3.10.4b — backend tests were the last consumers.

Pytest baseline 161/8/3 preserved. ViewSet implementations untouched
(api/v1/rrhh/views.py, api/v1/vacaciones/views.py — these are the
canonical impls that the new English URL configs already import).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -3
```

---

## Task 7: Delete dead `app_rrhh/` files

**Files to delete:**
1. `apps/api/app_rrhh/urls.py`
2. `apps/api/app_rrhh/views.py`
3. `apps/api/app_rrhh/serializers.py`
4. `apps/api/app_rrhh/serializers_optimized.py`
5. `apps/api/app_rrhh/services.py` (the `.py` file shadowed by `services/` package — contains the `rol_set` dead-code ref)
6. `apps/api/app_rrhh/models.py` (re-export shim)
7. `apps/api/app_rrhh/models/` (directory with `__all__ = []`)
8. `apps/api/app_rrhh/managers.py` (1366 lines, all consumers commented)
9. `apps/api/app_rrhh/managers/` (directory used only internally by deleted code)
10. `apps/api/app_rrhh/admin.py` (empty boilerplate)
11. `apps/api/app_rrhh/tests.py` (legacy)
12. `apps/api/app_rrhh/filters.py` (replaced by `api/v1/rrhh/filters.py`)
13. `apps/api/api/v1/rrhh/urls.py` (no longer included after Task 5)
14. `apps/api/api/v1/vacaciones/urls.py` (same)

- [ ] **Step 1: Pre-delete safety check — confirm no external refs to deleted files**

For each file/module, confirm no consumers exist:

```bash
cd D:/VYNTIA/apps/api

for module in "app_rrhh.urls" "app_rrhh.views" "app_rrhh.serializers" "app_rrhh.serializers_optimized" "app_rrhh.models" "app_rrhh.managers" "app_rrhh.admin" "app_rrhh.filters" "api.v1.rrhh.urls" "api.v1.vacaciones.urls"; do
  count=$(grep -rE "from $module|import $module|$module" --include='*.py' . 2>/dev/null | grep -v __pycache__ | grep -v "^./app_rrhh/$(echo $module | sed 's|app_rrhh\.||').py" | grep -v "^./api/v1/$(echo $module | sed 's|api\.v1\.||;s|\.|/|g')" | wc -l)
  echo "$module: $count external refs"
done
```

Expected: 0 external refs for each. If non-zero, investigate before deleting.

Note: `app_rrhh.services.py` (the .py file) is shadowed by `app_rrhh/services/` package, so `from app_rrhh import services` always resolves to the package, never the file. Safe to delete `services.py`.

- [ ] **Step 2: Delete the files**

```bash
cd D:/VYNTIA
git rm apps/api/app_rrhh/urls.py
git rm apps/api/app_rrhh/views.py
git rm apps/api/app_rrhh/serializers.py
git rm apps/api/app_rrhh/serializers_optimized.py
git rm apps/api/app_rrhh/services.py
git rm apps/api/app_rrhh/models.py
git rm -r apps/api/app_rrhh/models/
git rm apps/api/app_rrhh/managers.py
git rm -r apps/api/app_rrhh/managers/
git rm apps/api/app_rrhh/admin.py
git rm apps/api/app_rrhh/tests.py
git rm apps/api/app_rrhh/filters.py
git rm apps/api/api/v1/rrhh/urls.py
git rm apps/api/api/v1/vacaciones/urls.py
git status --short | head -20
```

- [ ] **Step 3: Verify Django startup**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: clean. If imports fail, find the rogue consumer and either delete it or update the import.

- [ ] **Step 4: Run pytest**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=short -q 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: baseline preserved (161 passed, 8 failed, 3 skipped).

- [ ] **Step 5: Commit deletions**

```bash
cd D:/VYNTIA
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L3.11): delete dead app_rrhh files + legacy URL configs

Deletes 14 dead/shadowed files no longer referenced anywhere:
- app_rrhh/urls.py + views.py + serializers.py + serializers_optimized.py
  (legacy ViewSets superseded by api/v1/rrhh/views.py used via new
  /api/v1/identity/, /employees/, /contracts/, etc routes)
- app_rrhh/services.py (.py file shadowed by services/ package; held
  the dead rol_set reverse-accessor ref from pre-L3.10.1 era)
- app_rrhh/models.py + models/ directory (empty __all__ post-L3.9)
- app_rrhh/managers.py (1366 lines, all consumers commented out)
  + managers/ directory (only used internally by deleted code)
- app_rrhh/admin.py + tests.py + filters.py (boilerplate / legacy)
- api/v1/rrhh/urls.py + api/v1/vacaciones/urls.py (no longer included
  in api/v1/urls.py after Task 5)

Active app_rrhh modules retained (still imported externally):
- menu_service.py, permission_service.py, constants.py, validators.py
- tasks.py, services/empleado_report_service.py, management/commands/

Module relocation to apps/X is deferred to L4 cleanup.

Pytest baseline 161/8/3 preserved.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -5
```

---

## Task 8: Final verification suite

- [ ] **Step 1: Full pytest**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tee /tmp/pytest_311_final.txt | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped` (baseline preserved).

If REGRESSED, BLOCK. Compare:

```bash
diff /tmp/pytest_baseline_311.txt /tmp/pytest_311_final.txt | head -30
```

- [ ] **Step 2: Frontend regression check**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: build success + `Tests 7 passed (7)`. (No frontend changes in this PR; sanity check.)

- [ ] **Step 3: Runtime smoke — confirm new URLs still work, legacy URLs return 404**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_311.log 2>&1 &
sleep 4

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123@"}' | grep -oE '"access":"[^"]+"' | sed 's/"access":"//;s/"$//')

echo "=== New canonical URL (should 200) ==="
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/v1/identity/users/"
echo ""

echo "=== Legacy URL (should 404 post-cleanup) ==="
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/v1/rrhh/usuarios/"
echo ""

curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/api/v1/vacaciones/configuraciones/"
echo " <- vacaciones legacy"

curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8000/legacy/areas/"
echo " <- /legacy/ alias"

# Stop the server
pkill -f "manage.py runserver" 2>/dev/null || true
cd D:/VYNTIA
```

Expected:
- `200` for `/api/v1/identity/users/`
- `404` for `/api/v1/rrhh/usuarios/`
- `404` for `/api/v1/vacaciones/configuraciones/`
- `404` for `/legacy/areas/`

- [ ] **Step 4: Confirm app_rrhh inventory shrank**

```bash
find D:/VYNTIA/apps/api/app_rrhh -type f -name "*.py" -not -path "*__pycache__*" | sort
```

Expected files (only):
- `app_rrhh/__init__.py`
- `app_rrhh/apps.py`
- `app_rrhh/constants.py`
- `app_rrhh/menu_service.py`
- `app_rrhh/permission_service.py`
- `app_rrhh/tasks.py`
- `app_rrhh/validators.py`
- `app_rrhh/migrations/__init__.py`
- `app_rrhh/management/__init__.py`
- `app_rrhh/management/commands/__init__.py`
- `app_rrhh/management/commands/audit_rbac.py`
- `app_rrhh/management/commands/seed_menu.py`
- `app_rrhh/management/commands/seed_plantillas_default.py`
- `app_rrhh/management/commands/seed_remuneraciones_config.py`
- `app_rrhh/management/commands/setup_roles_permisos.py`
- `app_rrhh/services/__init__.py`
- `app_rrhh/services/empleado_report_service.py`

- [ ] **Step 5: Confirm legacy URL config files are gone**

```bash
test -f D:/VYNTIA/apps/api/api/v1/rrhh/urls.py && echo "ERROR: still exists" || echo "OK: api/v1/rrhh/urls.py deleted"
test -f D:/VYNTIA/apps/api/api/v1/vacaciones/urls.py && echo "ERROR: still exists" || echo "OK: api/v1/vacaciones/urls.py deleted"
test -f D:/VYNTIA/apps/api/app_rrhh/urls.py && echo "ERROR: still exists" || echo "OK: app_rrhh/urls.py deleted"
```

Expected: 3 × "OK".

---

## Task 9: Merge to master

- [ ] **Step 1: Confirm user authorization**

PAUSE. Show user the branch state and request explicit merge approval. Do not proceed until approved.

```bash
cd D:/VYNTIA
git log --oneline master..vyntia/L3.11-cleanup-app-rrhh
git diff --stat master vyntia/L3.11-cleanup-app-rrhh | tail -10
```

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.11-cleanup-app-rrhh -m "Merge L3.11: cleanup app_rrhh — remove legacy URLs + dead files + dead-code refs"
git log --oneline -7
```

- [ ] **Step 3: Post-merge smoke**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: all baselines preserved.

---

## Task 10: Update roadmap + memory

- [ ] **Step 1: Update master roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.11 ✅ with merge commit hash
- Update L3.11 row description with actual outcomes (file count, lessons)

- [ ] **Step 2: Update memory `active_subproject.md`**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- Mark L3.11 ✅ with merge commit
- Mark L3 as fully complete (all sub-PRs done)
- Document any new lessons learned (LR28+)
- Update "How to apply" footer: Foundation L3 done — next is L4 (frontend reorganization by feature) or another sub-project

- [ ] **Step 3: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git diff --cached --stat
git commit -m "$(cat <<'EOF'
docs(L3.11): mark L3.11 merged — Foundation L3 complete

L3.11 cleanup shipped — 14 dead files deleted, 3 legacy URL aliases
removed, 2 dead-code reverse-accessor refs fixed (rol_set deleted with
the file; permiso_set corrected to modulo_permisos), 4 backend test
files migrated to English URLs.

Pytest 161/8/3 + vitest 7 + build clean baselines preserved.

Foundation L3 (Spanish→English split) is now FULLY complete:
L3.1-L3.9 (8 Django apps split), L3.10 (rename in 4 sub-PRs),
L3.11 (cleanup). Next: L4 (frontend reorganization by feature)
or another sub-project.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
git log --oneline -3
```

(Memory file is outside the repo, no commit needed — Edit tool persists it directly.)

---

## Notas para el ejecutor

- **Pragmatic scope**: This is a CLEANUP PR, not a refactor. Module relocation (moving `permission_service` to `apps/identity/`, etc.) is explicitly OUT OF SCOPE — that's L4 territory. Goal: smaller surface area for `app_rrhh/`, no behavior change.
- **The `services.py` shadowing trap**: Python resolves `app_rrhh/services/` (package) before `app_rrhh/services.py` (module). The .py file at line 370 has `usuario.rol_set.set(...)` which would error at runtime, but it's never called because the package shadow makes the file unreachable. Deleting the file IS the fix for the dead-code ref.
- **`api/v1/rrhh/views.py` is NOT deleted**: despite the folder name, this file contains the canonical ViewSet implementations imported by the new `/api/v1/identity/`, `/employees/`, `/contracts/` URL configs. Renaming `api/v1/rrhh/` → `api/v1/_canonical_views/` (or per-app organization) is L4 scope.
- **Legacy test migration**: 4 test files use `/api/v1/rrhh/` URLs. Migration is mechanical (URL string replacement). The new English URL prefixes are documented in this plan's URL mapping table. Custom action suffixes (`/aprobar/`, `/cancelar/`, `/mi-onboarding/`, `/corregir-correo/`, `/subir-foto/`) preserve verbatim.
- **Risk level: LOW**. No model changes, no migrations, no behavior change. Build + pytest baselines tell us everything we need to know. Curl smoke confirms URL routing works post-cleanup.
- **Two atomic commits expected**: (1) prefetch fix, (2) URL cleanup + test migration, (3) file deletions. Plan commit + roadmap commit bracket. Total 4-5 commits.
