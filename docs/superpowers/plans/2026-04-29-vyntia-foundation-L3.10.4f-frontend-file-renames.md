# VYNTIA Foundation L3.10.4f — Frontend File Renames Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename 7 frontend service/normalizer files from Spanish to English (`contratosService.ts` → `contractsService.ts`, `areasService.ts` → `departmentsService.ts`, etc.) and update all 35 import refs across consumers, aligning frontend naming with spec § 3.5 rule 6 ("Naming en inglés para todo el código Python y TypeScript").

**Architecture:** Frontend-only mechanical rename. Per service: `git mv` the file, then `replace_all` the bare service identifier in the renamed file + every consumer (covers import path string, import name, and variable usage in a single Edit per file because the identifier is identical to the URL substring). NO logic changes. NO interface/constant renames inside those files (those keep their Spanish names — interface and constant rename is broader scope, deferred to a future cleanup or L3.10.4g).

**Tech Stack:** TypeScript, Vite path aliases (`@/services/*` → `apps/web/src/services/*`).

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.5 rule 6 (Naming convention).

**Pre-condiciones:**
- L3.10.4c mergeada a master (commit `09dec734` "Merge L3.10.4c: frontend audit fields rename") + commit `0f780fb5` (roadmap update)
- Frontend baseline: vitest 7 passed, 1 file load-failure (Playwright e2e capture)
- Frontend `npm run build` passes
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped

**Scope decision (sub-PR de L3.10.4):**
- L3.10.4a ✅ Backend URL refactor
- L3.10.4b ✅ Frontend URL refactor
- L3.10.4c ✅ Frontend audit fields rename
- L3.10.4d ⏸ Frontend state fields (deferred — needs API contract audit)
- L3.10.4e ⏸ Frontend PK type change (deferred — UUID semantic migration)
- **L3.10.4f (este plan)** — Frontend file renames (mechanical, no semantic risk)
- L3.11 ⏳ Cleanup app_rrhh + remove legacy URLs

**Out of scope (NO hacer en L3.10.4f):**
- Interface renames (`Contrato`, `Area`, `Empleado`, `ConfiguracionEmpresa`, etc.) — these stay as-is in this PR
- Constant renames (`TIPO_CONTRATO_LABELS`, `ESTADO_CONTRATO_BADGE`, etc.) — stay
- State field renames (`estado`/`activo`) — deferred to L3.10.4d
- PK type change (`<entity>_id` → `id` UUID) — deferred to L3.10.4e
- Field name renames inside service files — out of scope
- `apps/web/src/generated/api/services/*` — auto-generated, regenerated separately
- Service files that already have English names: `authService.ts`, `employeesService.ts`, `menuService.ts`, `onboardingService.ts`, `securityService.ts`, `usersService.ts`
- `legajoService.ts` — preserved (domain term per Peruvian HR vocabulary, like "DNI", "RUC", "CTS")

---

## Rename table (canonical)

| Old filename | New filename | Old export const | New export const | Consumer files (besides self) |
|---|---|---|---|---|
| `apps/web/src/services/contratosService.ts` | `apps/web/src/services/contractsService.ts` | `contratosService` | `contractsService` | 4 |
| `apps/web/src/services/areasService.ts` | `apps/web/src/services/departmentsService.ts` | `areasService` | `departmentsService` | 4 |
| `apps/web/src/services/empresaService.ts` | `apps/web/src/services/companyService.ts` | `empresaService` | `companyService` | 1 |
| `apps/web/src/services/vacacionesService.ts` | `apps/web/src/services/timeOffService.ts` | `vacacionesService` | `timeOffService` | 14 |
| `apps/web/src/services/remuneracionesService.ts` | `apps/web/src/services/payrollService.ts` | `remuneracionesService` | `payrollService` | 5 |
| `apps/web/src/services/plantillasService.ts` | `apps/web/src/services/templatesService.ts` | `plantillasService` | `templatesService` | 1 |
| `apps/web/src/services/normalizers/rrhhNormalizers.ts` | `apps/web/src/services/normalizers/apiNormalizers.ts` | (no const — only named exports) | (named exports unchanged) | 3 |

**Consumer files total (deduped across services):** 32 unique files. (Some consumers import from multiple services.)

**`rrhhNormalizers.ts` special case:** This file exports only named functions (`extractCollection`, `normalizeRole`, `normalizeSecurityRole`, `normalizeUser`, `normalizeEmployee`) which are already in English. The rename is **path-only**: only the import path string changes (`'@/services/normalizers/rrhhNormalizers'` → `'@/services/normalizers/apiNormalizers'`). No identifier renames inside the file or in consumers.

**Why `git mv`:** Preserves git history showing the rename rather than delete+create. Use `git mv old new` (not `mv` followed by `git add/rm`).

**Why `replace_all` is safe per-file for the 6 service consts:** Each Spanish identifier (`contratosService`, `areasService`, `empresaService`, `vacacionesService`, `remuneracionesService`, `plantillasService`) is a unique substring with no false-positive collisions. The same string appears in:
- The export declaration (`export const contratosService = { ... }`)
- The import path (`from '@/services/contratosService'`)
- The import name (`import { contratosService } from ...`)
- The variable usage (`contratosService.getAll()`)

A single `replace_all` of the bare token covers ALL four cases per file because the import path string contains the identifier as substring (`'@/services/<identifier>'`).

---

## Files inventory

### Files renamed (7)
1. `contratosService.ts` → `contractsService.ts`
2. `areasService.ts` → `departmentsService.ts`
3. `empresaService.ts` → `companyService.ts`
4. `vacacionesService.ts` → `timeOffService.ts`
5. `remuneracionesService.ts` → `payrollService.ts`
6. `plantillasService.ts` → `templatesService.ts`
7. `normalizers/rrhhNormalizers.ts` → `normalizers/apiNormalizers.ts`

### Consumer files updated (deduped: 32)

**contratosService consumers (4):**
- `src/pages/contratos/ContratosPage.tsx`
- `src/pages/Empleados.tsx`
- `src/pages/HROverviewDashboard.tsx`
- `src/pages/legajo/LegajoPage.tsx`

**areasService consumers (4):**
- `src/components/areas/AreaForm.tsx`
- `src/pages/areas/AreaFormPage.tsx`
- `src/pages/areas/AreasListPage.tsx`
- `src/pages/areas/AreasManagementPage.tsx`

**empresaService consumer (1):**
- `src/pages/configuracion/ConfiguracionEmpresaPage.tsx`

**vacacionesService consumers (14):**
- `src/components/notifications/NotificationsBell.tsx`
- `src/components/vacaciones/CalendarioVacaciones.tsx`
- `src/components/vacaciones/ConfiguracionPanel.tsx`
- `src/components/vacaciones/EstadisticasVacaciones.tsx`
- `src/components/vacaciones/HistorialSolicitudes.tsx`
- `src/components/vacaciones/NotificacionesVacaciones.tsx`
- `src/components/vacaciones/PeriodosManagement.tsx`
- `src/components/vacaciones/ResumenDiasVacaciones.tsx`
- `src/pages/vacaciones/ConfiguracionPage.tsx`
- `src/pages/vacaciones/NuevaSolicitudPage.tsx`
- `src/pages/vacaciones/PeriodosPage.tsx`
- `src/pages/vacaciones/ReportesPage.tsx`
- `src/pages/vacaciones/SolicitudesPage.tsx`
- `src/pages/vacaciones/VacacionesManagementPage.tsx`

**remuneracionesService consumers (5):**
- `src/hooks/useRemuneraciones.ts`
- `src/pages/remuneraciones/ConfiguracionRemuneracionesPage.tsx`
- `src/pages/remuneraciones/ConfiguracionUitPage.tsx`
- `src/pages/remuneraciones/DescuentosMasivosPage.tsx`
- `src/pages/remuneraciones/PlanillasMensualesPage.tsx`

**plantillasService consumer (1):**
- `src/pages/PlantillasDocumentosPage.tsx`

**rrhhNormalizers consumers (3):**
- `src/services/employeesService.ts`
- `src/services/securityService.ts`
- `src/services/usersService.ts`

**Note:** The folder paths `pages/contratos/`, `pages/areas/`, `pages/vacaciones/`, `pages/remuneraciones/`, `components/areas/`, `components/vacaciones/` keep their Spanish names. Folder reorganization is L4 scope (frontend reorg by feature). This PR only renames service files, NOT folders.

---

## Definition of Done

- [ ] 7 files renamed via `git mv` (preserving git history with rename detection)
- [ ] 6 export constants renamed inside their files (`contratosService` → `contractsService`, etc.); `rrhhNormalizers.ts` has no const rename (only path)
- [ ] 32 consumer files updated to use new import paths + new identifier names
- [ ] `grep -rn "contratosService\|areasService\|empresaService\|vacacionesService\|remuneracionesService\|plantillasService\|rrhhNormalizers" apps/web/src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated` returns **0 matches**
- [ ] `grep -rn "contractsService\|departmentsService\|companyService\|timeOffService\|payrollService\|templatesService\|apiNormalizers" apps/web/src/ --include="*.ts" --include="*.tsx" --exclude-dir=generated` returns refs in expected files (sum should approximate the legacy ref count — ~190+)
- [ ] `npm run lint` clean (no net new warnings/errors vs master)
- [ ] `npm run build` passes
- [ ] `npm test` (vitest) preserves baseline: 7 passed, 1 file load-failure
- [ ] Backend pytest baseline preserved: 161 passed, 8 failed, 3 skipped (no backend changes)
- [ ] Branch `vyntia/L3.10.4f-frontend-file-renames` merged to master with `--no-ff`
- [ ] Roadmap updated: L3.10.4f ✅ merged
- [ ] Memory updated

---

## Task 1: Pre-flight — branch, baseline, snapshot

- [ ] **Step 1: Confirm pwd and master clean post-L3.10.4c**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `0f780fb5 docs(L3.10.4c): mark L3.10.4c merged, L3.10.4d (frontend state fields) as next` or later. `git status` shows ONLY the new plan file untracked.

- [ ] **Step 2: Confirm backend baseline**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `System check identified no issues` + `161 passed, 8 failed, 3 skipped`.

- [ ] **Step 3: Confirm frontend baseline build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
cd D:/VYNTIA
```

Expected: build success.

- [ ] **Step 4: Confirm frontend baseline tests**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 5: Snapshot of legacy ref counts (target: each → 0 after refactor)**

```bash
cd D:/VYNTIA/apps/web
echo "=== Legacy service identifiers (target: 0 after refactor) ==="
echo "contratosService: $(grep -rEn 'contratosService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "areasService: $(grep -rEn 'areasService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "empresaService: $(grep -rEn 'empresaService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "vacacionesService: $(grep -rEn 'vacacionesService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "remuneracionesService: $(grep -rEn 'remuneracionesService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "plantillasService: $(grep -rEn 'plantillasService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "rrhhNormalizers: $(grep -rEn 'rrhhNormalizers' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
cd D:/VYNTIA
```

REPORT THESE NUMBERS. Sum target ≈ 190+. After refactor, all 7 should be 0 in `src/` (excluding generated).

- [ ] **Step 6: Verify new names don't yet exist**

```bash
cd D:/VYNTIA/apps/web
for new in contractsService departmentsService companyService timeOffService payrollService templatesService apiNormalizers; do
  count=$(grep -rln "$new" src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)
  echo "$new: $count existing matches (must be 0)"
done
cd D:/VYNTIA
```

Expected: each shows `0`. If any shows non-zero, there's a naming collision — investigate before proceeding.

- [ ] **Step 7: Create branch**

```bash
git checkout -b vyntia/L3.10.4f-frontend-file-renames
git status --short
```

---

## Task 2: Commit the plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-29-vyntia-foundation-L3.10.4f-frontend-file-renames.md
git commit -m "$(cat <<'EOF'
docs(L3.10.4f): add frontend file renames plan

Frontend-only sub-PR of L3.10.4. Renames 7 service/normalizer files
from Spanish to English (contratosService -> contractsService,
areasService -> departmentsService, empresaService -> companyService,
vacacionesService -> timeOffService, remuneracionesService -> payrollService,
plantillasService -> templatesService, rrhhNormalizers -> apiNormalizers).
Updates ~190 import refs across 32 consumer files.

Mechanical, no semantic risk. Legajo preserved (domain term).
Interface/constant renames inside files OUT of scope.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Rename `contratosService` → `contractsService`

**Files:**
- Rename: `apps/web/src/services/contratosService.ts` → `apps/web/src/services/contractsService.ts`
- Modify (renamed file): export const rename
- Modify (4 consumers): `src/pages/contratos/ContratosPage.tsx`, `src/pages/Empleados.tsx`, `src/pages/HROverviewDashboard.tsx`, `src/pages/legajo/LegajoPage.tsx`

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/contratosService.ts apps/web/src/services/contractsService.ts
git status --short | head -3
cd D:/VYNTIA
```

Expected: shows `R  apps/web/src/services/{contratosService.ts → contractsService.ts}` or `R apps/web/src/services/contratosService.ts -> apps/web/src/services/contractsService.ts`.

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/contractsService.ts`
- old: `contratosService`
- new: `contractsService`
- replace_all: true

- [ ] **Step 3: Replace identifier in `ContratosPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/contratos/ContratosPage.tsx`
- old: `contratosService`
- new: `contractsService`
- replace_all: true

- [ ] **Step 4: Replace identifier in `Empleados.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/Empleados.tsx`
- old: `contratosService`
- new: `contractsService`
- replace_all: true

- [ ] **Step 5: Replace identifier in `HROverviewDashboard.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/HROverviewDashboard.tsx`
- old: `contratosService`
- new: `contractsService`
- replace_all: true

- [ ] **Step 6: Replace identifier in `legajo/LegajoPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/legajo/LegajoPage.tsx`
- old: `contratosService`
- new: `contractsService`
- replace_all: true

- [ ] **Step 7: Verify zero `contratosService` refs remain**

```bash
grep -rEn "contratosService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no contratosService refs"
```

Expected: `OK`.

---

## Task 4: Rename `areasService` → `departmentsService`

**Files:**
- Rename: `apps/web/src/services/areasService.ts` → `apps/web/src/services/departmentsService.ts`
- Modify (renamed file): export const rename
- Modify (4 consumers): `src/components/areas/AreaForm.tsx`, `src/pages/areas/AreaFormPage.tsx`, `src/pages/areas/AreasListPage.tsx`, `src/pages/areas/AreasManagementPage.tsx`

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/areasService.ts apps/web/src/services/departmentsService.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/departmentsService.ts`
- old: `areasService`
- new: `departmentsService`
- replace_all: true

- [ ] **Step 3: Replace identifier in `components/areas/AreaForm.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/components/areas/AreaForm.tsx`
- old: `areasService`
- new: `departmentsService`
- replace_all: true

- [ ] **Step 4: Replace identifier in `pages/areas/AreaFormPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/areas/AreaFormPage.tsx`
- old: `areasService`
- new: `departmentsService`
- replace_all: true

- [ ] **Step 5: Replace identifier in `pages/areas/AreasListPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/areas/AreasListPage.tsx`
- old: `areasService`
- new: `departmentsService`
- replace_all: true

- [ ] **Step 6: Replace identifier in `pages/areas/AreasManagementPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/areas/AreasManagementPage.tsx`
- old: `areasService`
- new: `departmentsService`
- replace_all: true

- [ ] **Step 7: Verify**

```bash
grep -rEn "areasService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no areasService refs"
```

Expected: `OK`.

---

## Task 5: Rename `empresaService` → `companyService`

**Files:**
- Rename: `apps/web/src/services/empresaService.ts` → `apps/web/src/services/companyService.ts`
- Modify (renamed file): export const rename
- Modify (1 consumer): `src/pages/configuracion/ConfiguracionEmpresaPage.tsx`

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/empresaService.ts apps/web/src/services/companyService.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/companyService.ts`
- old: `empresaService`
- new: `companyService`
- replace_all: true

- [ ] **Step 3: Replace identifier in `ConfiguracionEmpresaPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/configuracion/ConfiguracionEmpresaPage.tsx`
- old: `empresaService`
- new: `companyService`
- replace_all: true

- [ ] **Step 4: Verify**

```bash
grep -rEn "empresaService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no empresaService refs"
```

Expected: `OK`.

---

## Task 6: Rename `vacacionesService` → `timeOffService`

**Files:**
- Rename: `apps/web/src/services/vacacionesService.ts` → `apps/web/src/services/timeOffService.ts`
- Modify (renamed file): export const rename
- Modify (14 consumers — all listed below)

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/vacacionesService.ts apps/web/src/services/timeOffService.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/timeOffService.ts`
- old: `vacacionesService`
- new: `timeOffService`
- replace_all: true

- [ ] **Step 3: Replace identifier in 14 consumer files**

Apply the same Edit (`old: vacacionesService`, `new: timeOffService`, `replace_all: true`) to each of these files:

1. `apps/web/src/components/notifications/NotificationsBell.tsx`
2. `apps/web/src/components/vacaciones/CalendarioVacaciones.tsx`
3. `apps/web/src/components/vacaciones/ConfiguracionPanel.tsx`
4. `apps/web/src/components/vacaciones/EstadisticasVacaciones.tsx`
5. `apps/web/src/components/vacaciones/HistorialSolicitudes.tsx`
6. `apps/web/src/components/vacaciones/NotificacionesVacaciones.tsx`
7. `apps/web/src/components/vacaciones/PeriodosManagement.tsx`
8. `apps/web/src/components/vacaciones/ResumenDiasVacaciones.tsx`
9. `apps/web/src/pages/vacaciones/ConfiguracionPage.tsx`
10. `apps/web/src/pages/vacaciones/NuevaSolicitudPage.tsx`
11. `apps/web/src/pages/vacaciones/PeriodosPage.tsx`
12. `apps/web/src/pages/vacaciones/ReportesPage.tsx`
13. `apps/web/src/pages/vacaciones/SolicitudesPage.tsx`
14. `apps/web/src/pages/vacaciones/VacacionesManagementPage.tsx`

- [ ] **Step 4: Verify**

```bash
grep -rEn "vacacionesService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no vacacionesService refs"
```

Expected: `OK`.

---

## Task 7: Rename `remuneracionesService` → `payrollService`

**Files:**
- Rename: `apps/web/src/services/remuneracionesService.ts` → `apps/web/src/services/payrollService.ts`
- Modify (renamed file): export const rename
- Modify (5 consumers)

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/remuneracionesService.ts apps/web/src/services/payrollService.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/payrollService.ts`
- old: `remuneracionesService`
- new: `payrollService`
- replace_all: true

- [ ] **Step 3: Replace identifier in 5 consumer files**

Apply the same Edit (`old: remuneracionesService`, `new: payrollService`, `replace_all: true`) to each:

1. `apps/web/src/hooks/useRemuneraciones.ts`
2. `apps/web/src/pages/remuneraciones/ConfiguracionRemuneracionesPage.tsx`
3. `apps/web/src/pages/remuneraciones/ConfiguracionUitPage.tsx`
4. `apps/web/src/pages/remuneraciones/DescuentosMasivosPage.tsx`
5. `apps/web/src/pages/remuneraciones/PlanillasMensualesPage.tsx`

- [ ] **Step 4: Verify**

```bash
grep -rEn "remuneracionesService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no remuneracionesService refs"
```

Expected: `OK`.

---

## Task 8: Rename `plantillasService` → `templatesService`

**Files:**
- Rename: `apps/web/src/services/plantillasService.ts` → `apps/web/src/services/templatesService.ts`
- Modify (renamed file): export const rename
- Modify (1 consumer): `src/pages/PlantillasDocumentosPage.tsx`

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/plantillasService.ts apps/web/src/services/templatesService.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Replace identifier in renamed file**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/templatesService.ts`
- old: `plantillasService`
- new: `templatesService`
- replace_all: true

- [ ] **Step 3: Replace identifier in `PlantillasDocumentosPage.tsx`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/pages/PlantillasDocumentosPage.tsx`
- old: `plantillasService`
- new: `templatesService`
- replace_all: true

- [ ] **Step 4: Verify**

```bash
grep -rEn "plantillasService" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no plantillasService refs"
```

Expected: `OK`.

---

## Task 9: Rename `normalizers/rrhhNormalizers.ts` → `normalizers/apiNormalizers.ts`

**Special case:** This file has no const named `rrhhNormalizers`. It only exports named functions (`extractCollection`, `normalizeRole`, `normalizeSecurityRole`, `normalizeUser`, `normalizeEmployee`) which are already in English. Only the import path string needs updating in consumers — no identifier renames anywhere.

**Files:**
- Rename: `apps/web/src/services/normalizers/rrhhNormalizers.ts` → `apps/web/src/services/normalizers/apiNormalizers.ts`
- Modify (3 consumers): `src/services/employeesService.ts`, `src/services/securityService.ts`, `src/services/usersService.ts`

- [ ] **Step 1: `git mv` the file**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/normalizers/rrhhNormalizers.ts apps/web/src/services/normalizers/apiNormalizers.ts
git status --short | head -3
cd D:/VYNTIA
```

- [ ] **Step 2: Update import path in `employeesService.ts`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/employeesService.ts`
- old: `@/services/normalizers/rrhhNormalizers`
- new: `@/services/normalizers/apiNormalizers`
- replace_all: true

- [ ] **Step 3: Update import path in `securityService.ts`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/securityService.ts`
- old: `@/services/normalizers/rrhhNormalizers`
- new: `@/services/normalizers/apiNormalizers`
- replace_all: true

- [ ] **Step 4: Update import path in `usersService.ts`**

Use Edit tool with `replace_all: true`:
- File: `apps/web/src/services/usersService.ts`
- old: `@/services/normalizers/rrhhNormalizers`
- new: `@/services/normalizers/apiNormalizers`
- replace_all: true

- [ ] **Step 5: Verify**

```bash
grep -rEn "rrhhNormalizers" D:/VYNTIA/apps/web/src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated || echo "OK: no rrhhNormalizers refs"
```

Expected: `OK`.

---

## Task 10: Global verification — zero legacy refs

- [ ] **Step 1: Confirm zero legacy refs across entire frontend**

```bash
cd D:/VYNTIA/apps/web
echo "=== Legacy service identifiers (target: 0) ==="
echo "contratosService: $(grep -rEn 'contratosService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "areasService: $(grep -rEn 'areasService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "empresaService: $(grep -rEn 'empresaService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "vacacionesService: $(grep -rEn 'vacacionesService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "remuneracionesService: $(grep -rEn 'remuneracionesService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "plantillasService: $(grep -rEn 'plantillasService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "rrhhNormalizers: $(grep -rEn 'rrhhNormalizers' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
cd D:/VYNTIA
```

Expected: every count = `0`.

- [ ] **Step 2: Confirm new identifiers present**

```bash
cd D:/VYNTIA/apps/web
echo "=== New service identifiers (sum should ≈ pre-flight legacy total) ==="
echo "contractsService: $(grep -rEn 'contractsService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "departmentsService: $(grep -rEn 'departmentsService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "companyService: $(grep -rEn 'companyService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "timeOffService: $(grep -rEn 'timeOffService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "payrollService: $(grep -rEn 'payrollService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "templatesService: $(grep -rEn 'templatesService' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
echo "apiNormalizers: $(grep -rEn 'apiNormalizers' src/ --include='*.ts' --include='*.tsx' --exclude-dir=generated | wc -l)"
cd D:/VYNTIA
```

Expected: counts roughly match pre-flight legacy totals (per-service).

- [ ] **Step 3: Confirm git rename detection**

```bash
cd D:/VYNTIA
git status --short | head -20
git diff --stat HEAD | tail -10
```

Expected: status shows `R` (rename) lines for the 7 files. `git diff --stat HEAD` should reflect rename detection (not `delete + new file`).

- [ ] **Step 4: Confirm `generated/` NOT modified**

```bash
git diff --name-only HEAD | grep "src/generated/" || echo "OK: generated/ untouched"
```

Expected: `OK`.

---

## Task 11: Frontend smoke — lint, build, vitest

- [ ] **Step 1: ESLint delta check**

```bash
cd D:/VYNTIA/apps/web
ERRORS_NOW=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash push --include-untracked -m "lint-baseline-check" 2>&1 | tail -2
ERRORS_BASELINE=$(npm run lint 2>&1 | grep -E "^\s*[0-9]+:[0-9]+" | wc -l)
git stash pop 2>&1 | tail -2
echo "Lint errors now: $ERRORS_NOW"
echo "Lint errors on master: $ERRORS_BASELINE"
echo "Delta: $((ERRORS_NOW - ERRORS_BASELINE))"
cd D:/VYNTIA
```

Expected delta: `0`. If positive, BLOCK and report new errors.

- [ ] **Step 2: TypeScript build**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: build success. Any TS error here (especially "Cannot find module '@/services/contratosService'") means a consumer was missed — find it, update, re-run build.

- [ ] **Step 3: Vitest**

```bash
cd D:/VYNTIA/apps/web
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: `Tests 7 passed (7)`, `Test Files 1 failed | 2 passed (3)`.

- [ ] **Step 4: Backend pytest baseline preserved**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped`.

---

## Task 12: Atomic commit

- [ ] **Step 1: Stage frontend changes**

```bash
cd D:/VYNTIA
git status --short | head -40
git add apps/web/
```

- [ ] **Step 2: Confirm staged delta**

```bash
git diff --cached --stat | tail -25
```

Expected: 7 file renames (shown as `R` or rename pairs) + ~25 modified consumer files. Insertions + deletions roughly balanced (1:1 per identifier replacement, roughly).

- [ ] **Step 3: Commit**

```bash
git commit -m "$(cat <<'EOF'
chore(L3.10.4f): frontend file renames — service files Spanish to English

Renames 7 frontend service/normalizer files via `git mv` (preserves rename
history) and updates ~190 import refs across 32 consumer files.

File renames:
- contratosService.ts -> contractsService.ts
- areasService.ts -> departmentsService.ts
- empresaService.ts -> companyService.ts
- vacacionesService.ts -> timeOffService.ts
- remuneracionesService.ts -> payrollService.ts
- plantillasService.ts -> templatesService.ts
- normalizers/rrhhNormalizers.ts -> normalizers/apiNormalizers.ts

Export const renames (the bare service identifier inside each file):
- contratosService -> contractsService
- areasService -> departmentsService
- empresaService -> companyService
- vacacionesService -> timeOffService
- remuneracionesService -> payrollService
- plantillasService -> templatesService
- (rrhhNormalizers has no const — only path changed)

Preserved (not renamed):
- authService.ts, employeesService.ts, menuService.ts, onboardingService.ts,
  securityService.ts, usersService.ts (already English)
- legajoService.ts (Peruvian HR domain term per spec § 3.5 rule 7)

Out of scope (deferred):
- Interface renames (Contrato, Area, Empleado, ConfiguracionEmpresa, etc.)
- Constant renames (TIPO_CONTRATO_LABELS, ESTADO_CONTRATO_BADGE, etc.)
- State field renames (estado/activo) -> L3.10.4d
- PK type change -> L3.10.4e
- Folder reorganization (pages/contratos/, pages/areas/, etc.) -> L4
- generated/api/services/* -> auto-regenerated separately

Verification:
- grep "contratosService|areasService|empresaService|vacacionesService|
  remuneracionesService|plantillasService|rrhhNormalizers" apps/web/src/
  excluding generated/ -> 0 matches
- npm run lint: 0 net new errors vs master
- npm run build: success
- npm test: 7 passed (baseline preserved)
- Backend pytest: 161/8/3 (untouched)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 4: Verify branch state**

```bash
git log --oneline vyntia/L3.10.4f-frontend-file-renames ^master
git status --short
```

Expected: 2 commits on branch (`docs(L3.10.4f) plan` + `chore(L3.10.4f)`), clean working tree.

---

## Task 13: Merge to master + roadmap update

- [ ] **Step 1: Confirm user authorization**

PAUSE before merge. Only proceed if user approves.

- [ ] **Step 2: Merge --no-ff**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/L3.10.4f-frontend-file-renames -m "Merge L3.10.4f: frontend file renames (services Spanish to English)"
git log --oneline -5
```

- [ ] **Step 3: Post-merge smoke**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -5
npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
cd D:/VYNTIA
```

Expected: backend baseline preserved, frontend build success, tests pass.

- [ ] **Step 4: Update roadmap**

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- Mark L3.10.4f ✅ merged with commit hash
- Note that L3.10.4d (state fields) and L3.10.4e (PK type change) remain deferred pending API contract audit

- [ ] **Step 5: Update memory**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.4f ✅ merged
- Next: depends on user direction — could be L3.10.4d (state fields, requires API contract audit), L3.10.4e (PK UUID migration), or L3.11 (cleanup app_rrhh + remove legacy URLs)

- [ ] **Step 6: Commit roadmap**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.4f): mark L3.10.4f merged"
```

---

## Notas para el ejecutor

- **Frontend-only refactor.** Backend never touched; pytest baseline 161/8/3 must remain identical.
- **`git mv` preserves rename history** — git's `--find-renames` (default 50% similarity) detects each renamed file. After Step 2 of each task (Edit the renamed file), the file body changes by 1 identifier rename out of ~hundreds of lines, well above the rename threshold.
- **`replace_all` is safe** for the bare service identifiers because each (`contratosService`, `areasService`, etc.) is a unique substring with no false-positive matches. Pre-flight Step 6 verifies no naming collisions.
- **Folder paths stay Spanish in this PR.** Do NOT rename `pages/contratos/`, `pages/areas/`, `pages/vacaciones/`, etc. — folder reorganization is L4 scope.
- **`legajoService.ts` is preserved** per spec § 3.5 rule 7 (Peruvian HR domain term). Don't rename it.
- **Interfaces and constants inside renamed files keep Spanish names** in this PR — `Contrato`, `Area`, `Empleado`, `TIPO_CONTRATO_LABELS`, etc. unchanged. That's a future scope (potentially L3.10.4d/e or a dedicated PR).
- **`apps/web/src/generated/` is NOT touched.** Auto-generated from OpenAPI schema.
- **Risk profile:** Same as L3.10.4b URL refactor — pure mechanical replace, no semantic change. Build success + vitest baseline = sufficient verification.
