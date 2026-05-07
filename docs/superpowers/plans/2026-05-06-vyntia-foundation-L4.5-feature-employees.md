# VYNTIA Foundation L4.5 — Employees Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the employees slice — the LARGEST in L4 — into a self-contained `features/employees/` bounded context. Includes 8 pages, 5 components + barrel, 4 Datos* modals, 1 service, 1 hook = 20 files. Also DELETES the Spanish placeholder `features/empleados/` directory entirely (whose 2 example files account for ~177 of the 178 pre-existing tsc errors).

**Architecture:** Pure organizational refactor. No behavior changes. `features/employees/` does NOT exist (must `mkdir -p`). Spanish placeholder `features/empleados/` is REMOVED (decision per master roadmap L4.5 row — only sub-PR that explicitly deletes a placeholder before L4.11). 20 file `git mv` commit, then Python pass updates ~30 import sites across ~17 files.

**Tech Stack:** TypeScript, React, Vite, vitest, ESLint, React Router. No backend touched.

**Predecessor:** L4.4 ✅ merged `8422e5bf` 2026-05-06.

**Branch:** `vyntia/L4.5-feature-employees` (cut from master).

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.5 row.

---

## Scope inventory (verified 2026-05-06)

### Files to MOVE (20 files)

**Pages (8 files):**

| From | To |
|---|---|
| `apps/web/src/pages/Empleados.tsx` | `apps/web/src/features/employees/pages/Empleados.tsx` |
| `apps/web/src/pages/HROverviewDashboard.tsx` | `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` |
| `apps/web/src/pages/empleados/DatosAcademicosPage.tsx` | `apps/web/src/features/employees/pages/DatosAcademicosPage.tsx` |
| `apps/web/src/pages/empleados/DatosFamiliaresPage.tsx` | `apps/web/src/features/employees/pages/DatosFamiliaresPage.tsx` |
| `apps/web/src/pages/empleados/DatosLaboralesPage.tsx` | `apps/web/src/features/employees/pages/DatosLaboralesPage.tsx` |
| `apps/web/src/pages/empleados/DatosPersonalesPage.tsx` | `apps/web/src/features/employees/pages/DatosPersonalesPage.tsx` |
| `apps/web/src/pages/empleados/EmpleadoReportPage.tsx` | `apps/web/src/features/employees/pages/EmpleadoReportPage.tsx` |
| `apps/web/src/pages/empleados/EmpleadosListPage.tsx` | `apps/web/src/features/employees/pages/EmpleadosListPage.tsx` |

**Components (6 files — 5 .tsx + 1 existing barrel):**

| From | To |
|---|---|
| `apps/web/src/components/empleados/AdminDocUpload.tsx` | `apps/web/src/features/employees/components/AdminDocUpload.tsx` |
| `apps/web/src/components/empleados/TabAcademicos.tsx` | `apps/web/src/features/employees/components/TabAcademicos.tsx` |
| `apps/web/src/components/empleados/TabFamiliares.tsx` | `apps/web/src/features/employees/components/TabFamiliares.tsx` |
| `apps/web/src/components/empleados/TabLaborales.tsx` | `apps/web/src/features/employees/components/TabLaborales.tsx` |
| `apps/web/src/components/empleados/TabPersonales.tsx` | `apps/web/src/features/employees/components/TabPersonales.tsx` |
| `apps/web/src/components/empleados/index.ts` | `apps/web/src/features/employees/components/index.ts` |

**Modals (4 files — go to `features/employees/modals/` per roadmap, NOT `components/modals/`):**

| From | To |
|---|---|
| `apps/web/src/components/modals/DatosAcademicosModal.tsx` | `apps/web/src/features/employees/modals/DatosAcademicosModal.tsx` |
| `apps/web/src/components/modals/DatosFamiliaresModal.tsx` | `apps/web/src/features/employees/modals/DatosFamiliaresModal.tsx` |
| `apps/web/src/components/modals/DatosLaboralesModal.tsx` | `apps/web/src/features/employees/modals/DatosLaboralesModal.tsx` |
| `apps/web/src/components/modals/DatosPersonalesModal.tsx` | `apps/web/src/features/employees/modals/DatosPersonalesModal.tsx` |

**Service (1 file):**

| From | To |
|---|---|
| `apps/web/src/services/employeesService.ts` | `apps/web/src/features/employees/services/employeesService.ts` |

**Hook (1 file):**

| From | To |
|---|---|
| `apps/web/src/hooks/useEmployeePermissions.ts` | `apps/web/src/features/employees/hooks/useEmployeePermissions.ts` |

### Directory creation (BEFORE `git mv`)

`features/employees/` does NOT exist.

```
features/employees/
  ├── components/
  ├── hooks/
  ├── modals/         ← top-level under features/employees/, NOT under components/
  ├── pages/
  └── services/
```

`features/employees/types/` is intentionally omitted (no types to move). Note `modals/` is a **TOP-LEVEL** directory under `features/employees/`, separate from `components/` — this matches the L4 master roadmap row `features/employees/modals/`.

### Files to CREATE (5 NEW barrels — `components/index.ts` is MOVED, not created)

| Path | Content |
|---|---|
| `apps/web/src/features/employees/index.ts` | Top-level: `export * from './components'`, `export * from './hooks'`, `export * from './modals'`, `export * from './pages'`, `export * from './services'` |
| `apps/web/src/features/employees/hooks/index.ts` | `export * from './useEmployeePermissions'` |
| `apps/web/src/features/employees/modals/index.ts` | 4 default-export modal re-exports |
| `apps/web/src/features/employees/pages/index.ts` | Mixed: `Empleados` named + 7 defaults |
| `apps/web/src/features/employees/services/index.ts` | `export * from './employeesService'` |

`apps/web/src/features/employees/components/index.ts` is the MOVED `components/empleados/index.ts` — already populated with 5 named exports. The Python script does NOT touch its content (it uses relative imports `./AdminDocUpload` etc., which remain valid post-move).

### Files/dirs to DELETE (the entire `features/empleados/` placeholder)

The Spanish placeholder is removed in this same atomic commit (Task 3). Deleting the 2 example files removes ~177 of the 178 pre-existing tsc errors — a major side-effect cleanup.

```
features/empleados/                     ← entire directory
  ├── INTEGRATION_EXAMPLE.ts            ← parse errors
  ├── REACT_QUERY_EXAMPLE.ts            ← parse errors
  ├── index.ts                          ← stub barrel referencing all subdirs
  ├── components/index.ts               ← stub
  ├── hooks/index.ts                    ← stub
  ├── pages/index.ts                    ← stub
  ├── services/index.ts                 ← stub
  └── types/index.ts                    ← stub (if exists)
```

Pre-flight check: verify nothing imports from `@/features/empleados/*`. Per grep, only `apps/web/src/generated/api/README.md:87` references `@/features/empleados/hooks` — that's a markdown documentation file, not code. The Python script doesn't scan `.md` files; the README will retain a stale code example that points to a non-existent path. Acceptable: `generated/` is auto-generated and out-of-scope for L4 per the master roadmap.

### Files to LEAVE in place

- `apps/web/src/pages/empleados/` — empty after moves (L4.11 cleanup deletes orphaned empty dirs)
- `apps/web/src/components/empleados/` — empty after moves
- `apps/web/src/components/modals/` — directory still exists (Datos* moved out, but the dir might host other modals; verify in Task 2)
- `apps/web/src/services/` — many other services live here, untouched
- `apps/web/src/hooks/` — many other hooks live here, untouched
- `apps/web/src/pages/Empleados.tsx`, `HROverviewDashboard.tsx` — top-level pages MOVE OUT (no, they are MOVED, see above table — leave nothing in `pages/` for these)
- `apps/web/src/generated/` — out of scope per master roadmap (untouched even if it contains a stale doc reference)

### Consumer files (external) — 6 files with import updates

| File | Imports to redirect |
|---|---|
| `App.tsx` | 7 imports: `Empleados` (named), `HROverviewDashboard` (default), 5 `Datos*Page` defaults |
| `pages/contratos/ContratosPage.tsx` | `@/services/employeesService` |
| `pages/legajo/GestionDocumentosPage.tsx` | `@/services/employeesService` |
| `pages/legajo/LegajoPage.tsx` | `@/services/employeesService` |
| `features/identity/pages/UsersForm.tsx` | `@/hooks/useEmployeePermissions` |
| `features/identity/components/modals/UserFormModal.tsx` | `@/hooks/useEmployeePermissions` |

### Consumer files (internal to moved set) — ~11 files with import updates

These are imports inside the 20 moved files. Python script rewrites them automatically.

- `pages/Empleados.tsx` (2 sites): `@/components/empleados` (barrel) + `@/services/employeesService`
- 4 `Datos*Modal.tsx` (8 sites): `@/services/employeesService` + `@/hooks/useEmployeePermissions` each
- 6 `pages/empleados/*` files (~10 sites): mostly `@/services/employeesService`; `EmpleadosListPage.tsx` has 6 imports (4 modals + service + hook)
- 5 `components/empleados/Tab*.tsx` files (5 sites): `@/services/employeesService` each

### Total import-update sites: ~30 across ~17 files

**Sibling-relative import audit (LR32):** `grep "from ['\"]\./employeesService\|from ['\"]\./useEmployeePermissions"` returned EMPTY. No relative-import surprises.

---

## Mapping table (canonical, length-DESC)

| # | OLD path | NEW path |
|---:|---|---|
| 1 | `@/components/modals/DatosAcademicosModal` | `@/features/employees/modals/DatosAcademicosModal` |
| 2 | `@/components/modals/DatosFamiliaresModal` | `@/features/employees/modals/DatosFamiliaresModal` |
| 3 | `@/components/modals/DatosPersonalesModal` | `@/features/employees/modals/DatosPersonalesModal` |
| 4 | `@/components/modals/DatosLaboralesModal` | `@/features/employees/modals/DatosLaboralesModal` |
| 5 | `@/pages/empleados/DatosAcademicosPage` | `@/features/employees/pages/DatosAcademicosPage` |
| 6 | `@/pages/empleados/DatosFamiliaresPage` | `@/features/employees/pages/DatosFamiliaresPage` |
| 7 | `@/pages/empleados/DatosPersonalesPage` | `@/features/employees/pages/DatosPersonalesPage` |
| 8 | `@/pages/empleados/DatosLaboralesPage` | `@/features/employees/pages/DatosLaboralesPage` |
| 9 | `@/pages/empleados/EmpleadoReportPage` | `@/features/employees/pages/EmpleadoReportPage` |
| 10 | `@/pages/empleados/EmpleadosListPage` | `@/features/employees/pages/EmpleadosListPage` |
| 11 | `@/hooks/useEmployeePermissions` | `@/features/employees/hooks/useEmployeePermissions` |
| 12 | `@/pages/HROverviewDashboard` | `@/features/employees/pages/HROverviewDashboard` |
| 13 | `@/services/employeesService` | `@/features/employees/services/employeesService` |
| 14 | `@/components/empleados` | `@/features/employees/components` |
| 15 | `@/pages/Empleados` | `@/features/employees/pages/Empleados` |

**Prefix collision audit:**
- `@/pages/Empleados` (uppercase 'E') vs `@/pages/empleados/X` (lowercase 'e'): case-sensitive, no collision.
- `@/components/empleados` (entry 14) vs `@/components/empleados/X`: there are NO direct file imports from this dir (only the bare barrel). The bare-barrel string is the entire match — no risk of accidentally matching a longer path.
- All Datos*Modal entries (1-4) are distinct strings (the suffix `Academicos`/`Familiares`/`Personales`/`Laborales` differs).

**Confirmation:** `Datos*Modal` lengths — Academicos (38), Familiares (38), Personales (38), Laborales (37). Same prefix `@/components/modals/Datos`, distinct suffix. No collision.

---

## Pre-flight

- [ ] **Step 1: Confirm clean working tree on master**

```bash
cd D:/VYNTIA && git status --short && git branch --show-current
```

Expected: empty (clean) plus the new untracked plan file; branch `master`.

- [ ] **Step 2: Carry-over baselines from L4.4**

`LINT_BASELINE = 636 problems`. tsc baseline = 178 pre-existing errors (177 in INTEGRATION_EXAMPLE/REACT_QUERY_EXAMPLE + 1 in BlankEnum.ts). pytest = 161/8/3. vitest = 7 passed. **L4.5 will likely change the tsc baseline by deleting the 2 example files** — new baseline expected ~1 error (just BlankEnum.ts).

---

## Task 1: Create branch + commit plan

- [ ] **Step 1: Branch + plan commit**

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.5-feature-employees
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.5-feature-employees.md
git commit -m "$(cat <<'EOF'
docs(L4.5): add employees feature migration plan (LARGEST L4 sub-PR)

Plan for moving employees slice (8 pages + 5 components + 4 modals + 1
service + 1 hook = 20 files) into features/employees/. Also DELETES
features/empleados/ Spanish placeholder entirely — eliminating 2 example
files that account for ~177 of 178 pre-existing tsc errors. Mirror L4.4
pattern: features/employees/ created fresh, 5 new barrels (components
barrel MOVED), single Python pass for ~30 imports across ~17 files.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: mkdir + git mv 20 files

- [ ] **Step 1: Create destination dirs**

```bash
cd D:/VYNTIA
mkdir -p apps/web/src/features/employees/components
mkdir -p apps/web/src/features/employees/hooks
mkdir -p apps/web/src/features/employees/modals
mkdir -p apps/web/src/features/employees/pages
mkdir -p apps/web/src/features/employees/services
```

- [ ] **Step 2: Move 8 pages (2 root-level + 6 from pages/empleados/)**

```bash
cd D:/VYNTIA
git mv apps/web/src/pages/Empleados.tsx              apps/web/src/features/employees/pages/Empleados.tsx
git mv apps/web/src/pages/HROverviewDashboard.tsx    apps/web/src/features/employees/pages/HROverviewDashboard.tsx
git mv apps/web/src/pages/empleados/DatosAcademicosPage.tsx apps/web/src/features/employees/pages/DatosAcademicosPage.tsx
git mv apps/web/src/pages/empleados/DatosFamiliaresPage.tsx apps/web/src/features/employees/pages/DatosFamiliaresPage.tsx
git mv apps/web/src/pages/empleados/DatosLaboralesPage.tsx  apps/web/src/features/employees/pages/DatosLaboralesPage.tsx
git mv apps/web/src/pages/empleados/DatosPersonalesPage.tsx apps/web/src/features/employees/pages/DatosPersonalesPage.tsx
git mv apps/web/src/pages/empleados/EmpleadoReportPage.tsx  apps/web/src/features/employees/pages/EmpleadoReportPage.tsx
git mv apps/web/src/pages/empleados/EmpleadosListPage.tsx   apps/web/src/features/employees/pages/EmpleadosListPage.tsx
```

- [ ] **Step 3: Move 6 components (5 .tsx + 1 existing barrel)**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/empleados/AdminDocUpload.tsx apps/web/src/features/employees/components/AdminDocUpload.tsx
git mv apps/web/src/components/empleados/TabAcademicos.tsx  apps/web/src/features/employees/components/TabAcademicos.tsx
git mv apps/web/src/components/empleados/TabFamiliares.tsx  apps/web/src/features/employees/components/TabFamiliares.tsx
git mv apps/web/src/components/empleados/TabLaborales.tsx   apps/web/src/features/employees/components/TabLaborales.tsx
git mv apps/web/src/components/empleados/TabPersonales.tsx  apps/web/src/features/employees/components/TabPersonales.tsx
git mv apps/web/src/components/empleados/index.ts           apps/web/src/features/employees/components/index.ts
```

- [ ] **Step 4: Move 4 Datos* modals (to features/employees/modals/, top-level under features/employees/)**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/modals/DatosAcademicosModal.tsx apps/web/src/features/employees/modals/DatosAcademicosModal.tsx
git mv apps/web/src/components/modals/DatosFamiliaresModal.tsx apps/web/src/features/employees/modals/DatosFamiliaresModal.tsx
git mv apps/web/src/components/modals/DatosLaboralesModal.tsx  apps/web/src/features/employees/modals/DatosLaboralesModal.tsx
git mv apps/web/src/components/modals/DatosPersonalesModal.tsx apps/web/src/features/employees/modals/DatosPersonalesModal.tsx
```

- [ ] **Step 5: Move service + hook**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/employeesService.ts        apps/web/src/features/employees/services/employeesService.ts
git mv apps/web/src/hooks/useEmployeePermissions.ts     apps/web/src/features/employees/hooks/useEmployeePermissions.ts
```

- [ ] **Step 6: Verify rename detection (≥95%)**

```bash
cd D:/VYNTIA && git status && git diff --stat --staged | tail -25
```

Expected: 20 `renamed:` entries, 0 line changes. If any `deleted + new file`, ABORT.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.5): move employees files to features/employees/ (rename only)

git mv 20 files into features/employees/{components,hooks,modals,pages,services}/
with file bodies 100% unchanged. Rename detection ≥95% expected.

Files moved:
- pages/{Empleados,HROverviewDashboard}.tsx + pages/empleados/*.tsx (8)
  → features/employees/pages/
- components/empleados/* (5 .tsx + 1 existing barrel index.ts)
  → features/employees/components/
- components/modals/Datos{Academicos,Familiares,Laborales,Personales}Modal.tsx (4)
  → features/employees/modals/
- services/employeesService.ts → features/employees/services/
- hooks/useEmployeePermissions.ts → features/employees/hooks/

Spanish placeholder features/empleados/ deletion deferred to next commit
(Task 3) so this commit is pure renames for clean rename detection.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `20 files changed, 0 insertions(+), 0 deletions(-)`.

- [ ] **Step 8: Sanity broken-import check**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "Cannot find module.*@/(pages/(Empleados|HROverviewDashboard|empleados/)|components/(empleados|modals/Datos)|services/employeesService|hooks/useEmployeePermissions)" | head -20
```

Expected: many TypeScript errors — at least one per moved alias. If zero, BLOCKED.

---

## Task 3: Rewrite imports + create barrels + DELETE features/empleados/

This task does THREE things atomically: (1) Python rewrite of imports, (2) create 5 new barrels, (3) `rm -rf features/empleados/`. All in a single commit.

- [ ] **Step 1: Write Python script** at `D:/VYNTIA/scripts/L4.5-rewrite-imports.py`:

```python
"""L4.5 import path rewriter — employees feature migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

# OLD -> NEW. Length-DESC order is critical.
MAPPINGS = [
    ("@/components/modals/DatosAcademicosModal", "@/features/employees/modals/DatosAcademicosModal"),
    ("@/components/modals/DatosFamiliaresModal", "@/features/employees/modals/DatosFamiliaresModal"),
    ("@/components/modals/DatosPersonalesModal", "@/features/employees/modals/DatosPersonalesModal"),
    ("@/components/modals/DatosLaboralesModal",  "@/features/employees/modals/DatosLaboralesModal"),
    ("@/pages/empleados/DatosAcademicosPage",    "@/features/employees/pages/DatosAcademicosPage"),
    ("@/pages/empleados/DatosFamiliaresPage",    "@/features/employees/pages/DatosFamiliaresPage"),
    ("@/pages/empleados/DatosPersonalesPage",    "@/features/employees/pages/DatosPersonalesPage"),
    ("@/pages/empleados/DatosLaboralesPage",     "@/features/employees/pages/DatosLaboralesPage"),
    ("@/pages/empleados/EmpleadoReportPage",     "@/features/employees/pages/EmpleadoReportPage"),
    ("@/pages/empleados/EmpleadosListPage",      "@/features/employees/pages/EmpleadosListPage"),
    ("@/hooks/useEmployeePermissions",           "@/features/employees/hooks/useEmployeePermissions"),
    ("@/pages/HROverviewDashboard",              "@/features/employees/pages/HROverviewDashboard"),
    ("@/services/employeesService",              "@/features/employees/services/employeesService"),
    ("@/components/empleados",                   "@/features/employees/components"),
    ("@/pages/Empleados",                        "@/features/employees/pages/Empleados"),
]

def rewrite(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in MAPPINGS:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding="utf-8")
        return 1
    return 0

def main():
    total = 0
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in EXTS:
                if rewrite(p):
                    print(f"updated: {p.relative_to(ROOT)}")
                    total += 1
    print(f"\nTotal files updated: {total}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run script**

```bash
cd D:/VYNTIA && python scripts/L4.5-rewrite-imports.py
```

Expected: ~17 files updated.

- [ ] **Step 3: Verify zero stale OLD paths remain**

```bash
cd D:/VYNTIA && grep -rn "@/components/modals/Datos\|@/pages/empleados/\|@/components/empleados\|@/services/employeesService\|@/hooks/useEmployeePermissions\|@/pages/HROverviewDashboard\|@/pages/Empleados\b" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty.

The `\b` after `@/pages/Empleados` is a word boundary so it doesn't accidentally match `@/pages/empleados/X` (lowercase) or `@/features/employees/pages/Empleados` (already-mapped).

- [ ] **Step 4: Sibling-relative sweep (LR32)**

```bash
cd D:/VYNTIA && grep -rn "from ['\"]\./employeesService\|from ['\"]\./useEmployeePermissions\|from ['\"]\.\./services/employeesService\|from ['\"]\.\./hooks/useEmployeePermissions" apps/web/src/ 2>/dev/null
```

Expected: empty.

- [ ] **Step 5: Verify export styles**

```bash
cd D:/VYNTIA && echo "--- pages ---" && grep -E "^export" apps/web/src/features/employees/pages/*.tsx
echo "--- components ---" && grep -E "^export" apps/web/src/features/employees/components/*.tsx
echo "--- modals ---" && grep -E "^export" apps/web/src/features/employees/modals/*.tsx
echo "--- service ---" && grep -E "^export" apps/web/src/features/employees/services/*.ts
echo "--- hook ---" && grep -E "^export" apps/web/src/features/employees/hooks/*.ts
```

Expected (per pre-flight inspection):
- Pages: `Empleados.tsx` named export (`export function Empleados`); 7 others default (`export default function`)
- Components: 5 named exports (per current barrel)
- Modals: all 4 default exports (per `EmpleadosListPage.tsx` consumers using `import DatosAcademicosModal from`)
- Service/hook: named exports

If reality differs, adjust Step 6 templates.

- [ ] **Step 6: Create 5 NEW barrels**

`apps/web/src/features/employees/components/index.ts` is the MOVED barrel — already populated, do NOT recreate. The Python script in Step 2 left its content unchanged because it uses relative `./AdminDocUpload` style imports (no `@/` aliases to rewrite).

Use Write tool to create:

**`apps/web/src/features/employees/hooks/index.ts`:**
```typescript
export * from './useEmployeePermissions'
```

**`apps/web/src/features/employees/services/index.ts`:**
```typescript
export * from './employeesService'
```

**`apps/web/src/features/employees/modals/index.ts`** (default exports):
```typescript
export { default as DatosAcademicosModal } from './DatosAcademicosModal'
export { default as DatosFamiliaresModal } from './DatosFamiliaresModal'
export { default as DatosLaboralesModal } from './DatosLaboralesModal'
export { default as DatosPersonalesModal } from './DatosPersonalesModal'
```

**`apps/web/src/features/employees/pages/index.ts`** (mixed: Empleados named + 7 defaults):
```typescript
export { Empleados } from './Empleados'
export { default as HROverviewDashboard } from './HROverviewDashboard'
export { default as DatosAcademicosPage } from './DatosAcademicosPage'
export { default as DatosFamiliaresPage } from './DatosFamiliaresPage'
export { default as DatosLaboralesPage } from './DatosLaboralesPage'
export { default as DatosPersonalesPage } from './DatosPersonalesPage'
export { default as EmpleadoReportPage } from './EmpleadoReportPage'
export { default as EmpleadosListPage } from './EmpleadosListPage'
```

**`apps/web/src/features/employees/index.ts`** (top-level):
```typescript
// Employees Feature Exports
export * from './components'
export * from './hooks'
export * from './modals'
export * from './pages'
export * from './services'
```

Adjust if Step 5 contradicts the assumed export styles.

- [ ] **Step 7: Pre-flight check before deleting features/empleados/**

```bash
cd D:/VYNTIA && grep -rn "@/features/empleados" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty (the only known reference is in `apps/web/src/generated/api/README.md` which we're NOT scanning since it's a `.md` file in the OUT-OF-SCOPE `generated/` dir).

If any `.ts`/`.tsx` line is returned, STOP and investigate before deletion.

- [ ] **Step 8: Delete `features/empleados/` entirely**

```bash
cd D:/VYNTIA && rm -rf apps/web/src/features/empleados
```

Verify it's gone:

```bash
cd D:/VYNTIA && ls apps/web/src/features/ | grep -E "empleados|employees"
```

Expected: only `employees`. No `empleados`.

- [ ] **Step 9: TypeScript strict check**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -20
```

**Expected: tsc baseline DROPS DRAMATICALLY** — from 178 pre-existing errors to ~1 (just BlankEnum.ts) because the 2 example files in features/empleados/ are now deleted.

If you see ANY new error in a file path containing `employees`, `empleados`, `Datos`, `useEmployeePermissions`, `employeesService`, `Tab*`, `EmpleadosListPage`, `EmpleadoReportPage`, `HROverviewDashboard`, `Empleados.tsx` — that's a NEW error from L4.5 and MUST be fixed.

Capture the new tsc count for the commit message.

- [ ] **Step 10: Build, vitest, lint, pytest**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | grep -E "Tests|Test Files"
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -3
```

Expected: build clean, vitest 7 passed, **eslint may DROP from 636** (since 2 example files with lint errors are gone), pytest 161/8/3.

Capture the new lint count if it changed. Update LINT_BASELINE for future sub-PRs accordingly.

- [ ] **Step 11: Delete script + commit**

```bash
cd D:/VYNTIA && rm scripts/L4.5-rewrite-imports.py
cd D:/VYNTIA && git add -A && git status --short
```

Expected: ~17 modified .ts/.tsx + 5 new barrels + ~7 deletions (features/empleados/ tree).

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.5): update imports + create barrels + remove features/empleados/

THREE atomic changes:
1. Bulk import rewrite via Python script (15 length-DESC mappings).
   ~30 import sites across ~17 files redirected to @/features/employees/* aliases.
2. Created 5 new barrels (components/index.ts was MOVED, not created).
3. Deleted entire features/empleados/ Spanish placeholder — eliminating
   INTEGRATION_EXAMPLE.ts + REACT_QUERY_EXAMPLE.ts + 5 stub index.ts files.

External consumers updated (6 files):
- App.tsx: 7 page imports (Empleados barrel + HROverviewDashboard +
  5 Datos*Page defaults)
- pages/contratos/ContratosPage: employeesService alias
- pages/legajo/{GestionDocumentos,Legajo}Page: employeesService aliases
- features/identity/{pages/UsersForm,components/modals/UserFormModal}:
  useEmployeePermissions aliases

Internal updates inside moved files (~24 sites):
- pages/Empleados: barrel + service
- 4 Datos*Modal: service + hook each
- 6 empleados pages: service + (EmpleadosListPage: 4 modals + service + hook)
- 5 Tab* components: service each

New barrels created (5):
- features/employees/index.ts (top-level)
- features/employees/hooks/index.ts
- features/employees/modals/index.ts (4 default-export modals)
- features/employees/pages/index.ts (1 named + 7 default)
- features/employees/services/index.ts

Side-effect: tsc baseline DROPS from 178 -> ~1 errors (only BlankEnum.ts
remains). The 2 example files with parse errors are gone.

LR32 carry-over: sibling-relative sweep clean.

Verified:
- tsc: 0 new errors (ONLY BlankEnum.ts remains pre-existing)
- build clean, vitest 7 passed, lint <= 636, pytest 161/8/3

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 12: Final verification**

```bash
cd D:/VYNTIA && git log --oneline master..HEAD && git show --stat HEAD | tail -8
```

Expected: 3 commits ahead of master.

---

## Task 4: Smoke test (skip per L4.2/L4.3/L4.4 precedent)

Static checks all green = trust. Highest-risk sub-PR but pattern is well-trodden.

---

## Task 5: PAUSE for merge authorization

Display branch summary, ask user explicitly.

```bash
cd D:/VYNTIA && git log --oneline master..vyntia/L4.5-feature-employees
cd D:/VYNTIA && git diff --stat master..vyntia/L4.5-feature-employees | tail -5
```

---

## Task 6: Merge + roadmap update

```bash
cd D:/VYNTIA && git checkout master && git merge --no-ff vyntia/L4.5-feature-employees -m "Merge L4.5: features/employees/ migration (LARGEST L4 sub-PR)

Employees slice consolidated under features/employees/ — 8 pages + 5
components + 1 moved barrel + 4 modals + 1 service + 1 hook = 20 files.
5 new barrels (components/index.ts moved). 6 external consumers + ~24
internal imports redirected. Spanish placeholder features/empleados/
removed entirely (INTEGRATION_EXAMPLE.ts + REACT_QUERY_EXAMPLE.ts +
5 stub index.ts), dropping tsc baseline from 178 -> ~1 errors. Baselines
preserved: pytest 161/8/3, vitest 7, build clean, lint delta 0 or improved."
```

Update `2026-05-06-vyntia-foundation-L4-master-roadmap.md` L4.5 row to ✅ with merge hash. Mark L4.6 as ⏳ NEXT.

```bash
cd D:/VYNTIA && git commit -am "$(cat <<'EOF'
docs(L4.5): mark L4.5 merged — employees feature consolidated, features/empleados/ removed

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Final post-merge: build, vitest, pytest. Delete branch with `-d`.

---

## Definition of done

- [ ] `apps/web/src/features/employees/` contains: 8 pages + 6 components (5 .tsx + barrel) + 4 modals + 1 service + 1 hook + 5 NEW barrels (top-level, hooks, modals, pages, services)
- [ ] `apps/web/src/features/empleados/` is GONE entirely
- [ ] Source dirs (`pages/empleados/`, `components/empleados/`) are empty (L4.11 cleanup)
- [ ] `pages/Empleados.tsx`, `pages/HROverviewDashboard.tsx` no longer exist
- [ ] `services/employeesService.ts` no longer exists
- [ ] `hooks/useEmployeePermissions.ts` no longer exists
- [ ] All 4 `components/modals/Datos*Modal.tsx` no longer exist
- [ ] tsc baseline DROPS to ~1 error (just BlankEnum.ts)
- [ ] `grep` for old aliases returns 0 lines
- [ ] build clean, vitest 7, lint ≤ 636, pytest 161/8/3
- [ ] Merged to master, roadmap updated, L4.6 marked NEXT

---

## Risk register (L4.5-specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 20 files = highest rename-detection failure surface | Low | Med | Move + commit in dedicated commit, NO body changes (Task 2). Verify in Step 6. |
| Mixed export styles in pages barrel | Med | Low | Step 5 verifies actual styles; Step 6 template branches on each |
| `@/components/empleados` (bare barrel) prefix collision with `@/components/empleados/X` | Low | Med | Pre-flight grep verified zero direct file imports — only the bare barrel exists. Mapping is clean substring. |
| `@/pages/Empleados` (uppercase) vs `@/pages/empleados/X` (lowercase) | Low | Med | Case-sensitive `str.replace` — no collision. Verified by pre-flight inventory. |
| Deleting features/empleados/ breaks something we missed | Low | High | Step 7 pre-flight grep ensures no `.ts`/`.tsx` references. README in `generated/` is acceptable stale doc. |
| LR26 silent runtime break | Med | Med | Smoke test optional in Task 4 (skipped per precedent — user comfortable with static checks) |
| pytest unexpected regression | Very Low | Low | Step 10 verification |
| Modals barrel uses wrong export style | Low | Med | Step 5 verifies; consumers already use `import DatosAcademicosModal from` (default style) per `EmpleadosListPage.tsx` — barrel template matches |

---

## Self-review

**1. Spec coverage:** Every file in the L4.5 row of the master roadmap (Empleados/HROverviewDashboard pages + pages/empleados/* + components/empleados/* + Datos*Modals + employeesService + useEmployeePermissions) is in the move table. The "Discard `features/empleados/{INTEGRATION_EXAMPLE,REACT_QUERY_EXAMPLE}.ts`" requirement is implemented in Task 3 Step 8 (entire `features/empleados/` removed). The "Delete `features/empleados/` placeholder" requirement is also handled in Step 8. EmpleadosListPage included even though App.tsx doesn't import it (it lives in pages/empleados/, so it moves with its peers).

**2. Placeholder scan:** No "TBD" or "fill in later" tokens. Step 6 template has explicit branching note for export-style adjustments.

**3. Type consistency:** Pages barrel exports match consumer styles verified in pre-flight grep — `Empleados` is named (App.tsx uses `import { Empleados }`); 7 others are default. Modals all default (per `EmpleadosListPage.tsx` consumers). Components all named (per existing barrel). Service/hook are namespaced re-exports.
