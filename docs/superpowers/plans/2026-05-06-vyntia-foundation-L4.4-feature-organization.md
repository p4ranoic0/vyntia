# VYNTIA Foundation L4.4 — Organization Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the organization slice (3 area pages + 1 company-config page + 2 area components + 2 services) from the flat layout into a self-contained `features/organization/` bounded context, with all consumer imports redirected via `@/features/organization/*` aliases — preserving every test/lint/build baseline.

**Architecture:** Pure organizational refactor. No behavior changes. `features/organization/` does NOT exist (must `mkdir -p`). 8 file `git mv` commit, then a single Python pass updates ~9 import sites across 6 files. Mirrors the L4.2/L4.3 three-commit pattern.

**Tech Stack:** TypeScript, React, Vite, vitest, ESLint, React Router. No backend touched.

**Predecessor:** L4.3 ✅ merged `30ee57c8` 2026-05-06.

**Branch:** `vyntia/L4.4-feature-organization` (cut from master).

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.4 row.

---

## Scope inventory (verified 2026-05-06)

### Files to MOVE (8 files)

| From | To |
|---|---|
| `apps/web/src/pages/areas/AreaFormPage.tsx` | `apps/web/src/features/organization/pages/AreaFormPage.tsx` |
| `apps/web/src/pages/areas/AreasListPage.tsx` | `apps/web/src/features/organization/pages/AreasListPage.tsx` |
| `apps/web/src/pages/areas/AreasManagementPage.tsx` | `apps/web/src/features/organization/pages/AreasManagementPage.tsx` |
| `apps/web/src/pages/configuracion/ConfiguracionEmpresaPage.tsx` | `apps/web/src/features/organization/pages/ConfiguracionEmpresaPage.tsx` |
| `apps/web/src/components/areas/AreaForm.tsx` | `apps/web/src/features/organization/components/AreaForm.tsx` |
| `apps/web/src/components/areas/DeleteAreaDialog.tsx` | `apps/web/src/features/organization/components/DeleteAreaDialog.tsx` |
| `apps/web/src/services/departmentsService.ts` | `apps/web/src/features/organization/services/departmentsService.ts` |
| `apps/web/src/services/companyService.ts` | `apps/web/src/features/organization/services/companyService.ts` |

### Directory creation (BEFORE `git mv`)

`features/organization/` does NOT exist — same situation as L4.3's `features/identity/`.

```
features/organization/
  ├── components/
  ├── pages/
  └── services/
```

`features/organization/types/` is intentionally omitted (no types to move; D1 master roadmap convention).

### Files to CREATE (4 new barrels)

| Path | Content |
|---|---|
| `apps/web/src/features/organization/index.ts` | Top-level: `export * from './components'`, `export * from './pages'`, `export * from './services'` |
| `apps/web/src/features/organization/components/index.ts` | Named exports for `AreaForm` + `DeleteAreaDialog` |
| `apps/web/src/features/organization/pages/index.ts` | Named exports for the 3 area pages + `ConfiguracionEmpresaPage` |
| `apps/web/src/features/organization/services/index.ts` | `export * from './departmentsService'` + `'./companyService'` |

### Files to LEAVE in place

- `apps/web/src/features/areas/` — Spanish placeholder, deleted in L4.11.
- `apps/web/src/pages/areas/` and `apps/web/src/pages/configuracion/` — empty after moves; L4.11 cleanup.
- `apps/web/src/components/areas/` — empty after moves.
- `apps/web/src/services/` — many other services live here, untouched.

### Consumer files (external) — 1 file with import updates

- `App.tsx` — 4 imports (3 area page direct imports + 1 ConfiguracionEmpresaPage import)

### Consumer files (internal to moved set) — 5 files

These are imports inside the moved files themselves. Python script rewrites them automatically:

- `pages/configuracion/ConfiguracionEmpresaPage.tsx`: `@/services/companyService`
- `pages/areas/AreasManagementPage.tsx`: `@/services/departmentsService`
- `pages/areas/AreasListPage.tsx`: `@/services/departmentsService` + `@/components/areas/AreaForm` (2 sites)
- `pages/areas/AreaFormPage.tsx`: `@/services/departmentsService`
- `components/areas/AreaForm.tsx`: `@/services/departmentsService`

### Total import-update sites: ~10 across 6 files

**Sibling-relative import audit (LR32 lesson):** verified via `grep "from ['\"]\./departmentsService\|from ['\"]\./companyService"` — zero matches. Python alias-only script sufficient.

---

## Mapping table (length-DESC)

| # | OLD path | NEW path |
|---:|---|---|
| 1 | `@/pages/configuracion/ConfiguracionEmpresaPage` | `@/features/organization/pages/ConfiguracionEmpresaPage` |
| 2 | `@/components/areas/DeleteAreaDialog` | `@/features/organization/components/DeleteAreaDialog` |
| 3 | `@/pages/areas/AreasManagementPage` | `@/features/organization/pages/AreasManagementPage` |
| 4 | `@/services/departmentsService` | `@/features/organization/services/departmentsService` |
| 5 | `@/pages/areas/AreasListPage` | `@/features/organization/pages/AreasListPage` |
| 6 | `@/components/areas/AreaForm` | `@/features/organization/components/AreaForm` |
| 7 | `@/pages/areas/AreaFormPage` | `@/features/organization/pages/AreaFormPage` |
| 8 | `@/services/companyService` | `@/features/organization/services/companyService` |

**Prefix collision audit:** `@/components/areas/AreaForm` (27 chars) is NOT a prefix of `@/pages/areas/AreaFormPage` (different roots `@/components/` vs `@/pages/`). All siblings under `@/pages/areas/` are non-overlapping. Length-DESC ordering is defensive only.

---

## Pre-flight

- [ ] **Step 1: Confirm clean working tree on master**

```bash
cd D:/VYNTIA && git status --short && git branch --show-current
```

Expected: empty output (clean) plus the new untracked plan file; branch `master`.

- [ ] **Step 2: Spot-check baselines** (carry-over from L4.3 merge):

`LINT_BASELINE = 636 problems`. Pre-existing tsc errors = 178 (all in `features/empleados/{INTEGRATION_EXAMPLE,REACT_QUERY_EXAMPLE}.ts` + `generated/api/models/BlankEnum.ts`). pytest = 161/8/3. vitest = 7 passed (1 file load failure).

---

## Task 1: Create branch + commit plan

- [ ] **Step 1: Branch + plan commit**

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.4-feature-organization
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.4-feature-organization.md
git commit -m "$(cat <<'EOF'
docs(L4.4): add organization feature migration plan

Plan for moving organization slice (3 area pages + 1 company-config page
+ 2 area components + 2 services) into features/organization/ bounded
context. Mirror L4.3 pattern: features/organization/ created fresh,
4 new barrels, single Python pass for ~10 imports across 6 files.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: mkdir + git mv 8 files

- [ ] **Step 1: Create destination dirs**

```bash
cd D:/VYNTIA
mkdir -p apps/web/src/features/organization/components
mkdir -p apps/web/src/features/organization/pages
mkdir -p apps/web/src/features/organization/services
```

- [ ] **Step 2: Move 4 pages (3 areas + 1 configuracion)**

```bash
cd D:/VYNTIA
git mv apps/web/src/pages/areas/AreaFormPage.tsx        apps/web/src/features/organization/pages/AreaFormPage.tsx
git mv apps/web/src/pages/areas/AreasListPage.tsx       apps/web/src/features/organization/pages/AreasListPage.tsx
git mv apps/web/src/pages/areas/AreasManagementPage.tsx apps/web/src/features/organization/pages/AreasManagementPage.tsx
git mv apps/web/src/pages/configuracion/ConfiguracionEmpresaPage.tsx apps/web/src/features/organization/pages/ConfiguracionEmpresaPage.tsx
```

- [ ] **Step 3: Move 2 components**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/areas/AreaForm.tsx         apps/web/src/features/organization/components/AreaForm.tsx
git mv apps/web/src/components/areas/DeleteAreaDialog.tsx apps/web/src/features/organization/components/DeleteAreaDialog.tsx
```

- [ ] **Step 4: Move 2 services**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/departmentsService.ts apps/web/src/features/organization/services/departmentsService.ts
git mv apps/web/src/services/companyService.ts     apps/web/src/features/organization/services/companyService.ts
```

- [ ] **Step 5: Verify rename detection (≥95%)**

```bash
cd D:/VYNTIA && git status && git diff --stat --staged
```

Expected: 8 `renamed:` entries, 0 line changes. If any is `deleted + new file`, ABORT.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.4): move organization files to features/organization/ (rename only)

git mv 8 files into features/organization/{components,pages,services}/
with file bodies 100% unchanged. Rename detection ≥95% expected.

Files moved:
- pages/areas/{AreaFormPage,AreasListPage,AreasManagementPage}.tsx
  → features/organization/pages/
- pages/configuracion/ConfiguracionEmpresaPage.tsx
  → features/organization/pages/
- components/areas/{AreaForm,DeleteAreaDialog}.tsx
  → features/organization/components/
- services/{departmentsService,companyService}.ts
  → features/organization/services/

Spanish placeholder features/areas/ stays (L4.11 cleanup).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `8 files changed, 0 insertions(+), 0 deletions(-)`.

- [ ] **Step 7: Sanity check broken imports**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "Cannot find module.*@/(pages/areas|pages/configuracion|components/areas|services/(departments|company)Service)" | head -20
```

Expected: TypeScript errors for the moved aliases. If zero errors, BLOCKED.

---

## Task 3: Rewrite imports + create barrels

- [ ] **Step 1: Write Python script** at `D:/VYNTIA/scripts/L4.4-rewrite-imports.py`:

```python
"""L4.4 import path rewriter — organization feature migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

MAPPINGS = [
    ("@/pages/configuracion/ConfiguracionEmpresaPage", "@/features/organization/pages/ConfiguracionEmpresaPage"),
    ("@/components/areas/DeleteAreaDialog",            "@/features/organization/components/DeleteAreaDialog"),
    ("@/pages/areas/AreasManagementPage",              "@/features/organization/pages/AreasManagementPage"),
    ("@/services/departmentsService",                  "@/features/organization/services/departmentsService"),
    ("@/pages/areas/AreasListPage",                    "@/features/organization/pages/AreasListPage"),
    ("@/components/areas/AreaForm",                    "@/features/organization/components/AreaForm"),
    ("@/pages/areas/AreaFormPage",                     "@/features/organization/pages/AreaFormPage"),
    ("@/services/companyService",                      "@/features/organization/services/companyService"),
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
cd D:/VYNTIA && python scripts/L4.4-rewrite-imports.py
```

Expected: ~6 files updated (App.tsx + 5 internal-to-moved-set).

- [ ] **Step 3: Verify zero stale paths**

```bash
cd D:/VYNTIA && grep -rn "@/pages/areas/\|@/pages/configuracion/\|@/components/areas/\|@/services/departmentsService\|@/services/companyService" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty.

- [ ] **Step 4: Sibling-relative sweep**

```bash
cd D:/VYNTIA && grep -rn "from ['\"]\./departmentsService\|from ['\"]\./companyService\|from ['\"]\.\./services/departmentsService\|from ['\"]\.\./services/companyService" apps/web/src/ 2>/dev/null
```

Expected: empty.

- [ ] **Step 5: Verify component export style**

```bash
cd D:/VYNTIA && grep -E "^export" apps/web/src/features/organization/components/*.tsx | head -8
```

Pages: check the export style of each (some `export default X`, some `export const X` / `export function X`):

```bash
cd D:/VYNTIA && grep -E "^export" apps/web/src/features/organization/pages/*.tsx | head -10
```

The barrel files in Step 6 must match the actual export style of each file.

- [ ] **Step 6: Create 4 barrels**

Use Write. Match the export style discovered in Step 5.

**`apps/web/src/features/organization/components/index.ts`** — adjust based on Step 5 (likely named export per convention):

```typescript
export { AreaForm } from './AreaForm'
export { DeleteAreaDialog } from './DeleteAreaDialog'
```

If `export default X` is used, switch to: `export { default as AreaForm } from './AreaForm'` etc.

**`apps/web/src/features/organization/pages/index.ts`** — adjust based on Step 5. Looking at App.tsx, the area pages use named-import (`import { AreaFormPage } from ...`), suggesting named exports. ConfiguracionEmpresaPage uses default-import (`import ConfiguracionEmpresaPage from ...`), suggesting default export.

```typescript
export { AreaFormPage } from './AreaFormPage'
export { AreasListPage } from './AreasListPage'
export { AreasManagementPage } from './AreasManagementPage'
export { default as ConfiguracionEmpresaPage } from './ConfiguracionEmpresaPage'
```

If Step 5 contradicts these assumptions, adjust accordingly.

**`apps/web/src/features/organization/services/index.ts`:**

```typescript
export * from './departmentsService'
export * from './companyService'
```

**`apps/web/src/features/organization/index.ts`:**

```typescript
// Organization Feature Exports
export * from './components'
export * from './pages'
export * from './services'
```

- [ ] **Step 7: TypeScript strict check**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v "REACT_QUERY_EXAMPLE\|INTEGRATION_EXAMPLE\|BlankEnum" | head -20
```

Expected: empty output (no L4.4-related errors). The 178 pre-existing errors are filtered out.

- [ ] **Step 8: Build, vitest, lint, pytest**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | grep -E "Tests|Test Files"
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -3
```

Expected: build clean, vitest 7 passed, eslint 636/636, pytest 161/8/3.

- [ ] **Step 9: Delete script and commit**

```bash
cd D:/VYNTIA && rm scripts/L4.4-rewrite-imports.py
cd D:/VYNTIA && git add -A && git status --short
```

Expected: ~6 modified .ts/.tsx + 4 new barrels.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.4): update consumer imports + create features/organization/ barrels

Bulk import rewrite via Python script (8 length-DESC mappings).
~10 import sites across 6 files redirected to @/features/organization/* aliases.

External consumers updated (1 file):
- App.tsx: 4 page imports (3 areas + 1 configuracion)

Internal updates inside moved files (5 sites):
- ConfiguracionEmpresaPage: companyService alias
- 3 area pages + AreaForm component: departmentsService alias
- AreasListPage: AreaForm component alias

New barrels created (4):
- features/organization/index.ts (top-level)
- features/organization/components/index.ts
- features/organization/pages/index.ts (mixed named + default exports)
- features/organization/services/index.ts

LR32 carry-over: sibling-relative sweep clean.

Verified:
- tsc: 0 new errors (178 pre-existing baseline preserved)
- build clean, vitest 7 passed, lint 636/636, pytest 161/8/3

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Smoke test (optional, skip per L4.2/L4.3 precedent)

Static checks all green = trust. If user wants browser walkthrough, start dev server.

---

## Task 5: PAUSE for merge authorization

Display branch summary, ask user explicitly.

```bash
cd D:/VYNTIA && git log --oneline master..vyntia/L4.4-feature-organization
cd D:/VYNTIA && git diff --stat master..vyntia/L4.4-feature-organization | tail -5
```

---

## Task 6: Merge + roadmap update (after user approves)

```bash
cd D:/VYNTIA && git checkout master && git merge --no-ff vyntia/L4.4-feature-organization -m "Merge L4.4: features/organization/ migration

Organization slice consolidated under features/organization/ — 3 area pages
+ 1 company-config page + 2 components + 2 services + 4 new barrels.
1 external consumer (App.tsx) + 5 internal imports redirected. Spanish
placeholder features/areas/ stays (L4.11 cleanup). Baselines preserved:
pytest 161/8/3, vitest 7, build clean, tsc 0 new errors, lint delta 0."
```

Update `2026-05-06-vyntia-foundation-L4-master-roadmap.md` L4.4 row to ✅ with merge hash. Mark L4.5 as ⏳ NEXT.

```bash
cd D:/VYNTIA && git commit -am "$(cat <<'EOF'
docs(L4.4): mark L4.4 merged — organization feature consolidated

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Final post-merge: build, vitest, pytest. Delete branch with `-d`.

---

## Definition of done

- [ ] `apps/web/src/features/organization/` contains: 4 pages, 2 components, 2 services, 4 barrels
- [ ] `pages/areas/`, `pages/configuracion/`, `components/areas/` are empty (L4.11 cleanup)
- [ ] `services/{departmentsService,companyService}.ts` no longer exist
- [ ] `grep` for old aliases returns 0 lines
- [ ] tsc: only 178 pre-existing errors
- [ ] build clean, vitest 7, lint 636, pytest 161/8/3
- [ ] Merged to master with `--no-ff`, roadmap row updated, L4.5 marked NEXT

---

## Risk register (L4.4-specific)

Same 8 risks as L4.3 — all low. Smallest L4 sub-PR yet (8 files, ~10 imports).

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Mixed export styles in pages barrel | Med | Low | Step 5 verifies actual style; Step 6 template branches on it |
| Anything else | Low | Low | All other risks per L4.2/L4.3 carry-over |
