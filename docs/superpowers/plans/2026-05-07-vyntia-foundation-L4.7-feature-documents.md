# VYNTIA Foundation L4.7 — Documents Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the documents slice (3 pages + 2 services) into `features/documents/`. Includes the legajo→documents English rename for the bounded context.

**Architecture:** `features/documents/` does NOT exist (mkdir). 5 file `git mv`, then Python pass updates ~10 import sites across 9 files.

**Predecessor:** L4.6 ✅ merged `f51d257d` 2026-05-07.

**Branch:** `vyntia/L4.7-feature-documents`.

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.7.

---

## Scope inventory (verified 2026-05-07)

### Files to MOVE (5)

| From | To |
|---|---|
| `apps/web/src/pages/PlantillasDocumentosPage.tsx` | `apps/web/src/features/documents/pages/PlantillasDocumentosPage.tsx` |
| `apps/web/src/pages/legajo/GestionDocumentosPage.tsx` | `apps/web/src/features/documents/pages/GestionDocumentosPage.tsx` |
| `apps/web/src/pages/legajo/LegajoPage.tsx` | `apps/web/src/features/documents/pages/LegajoPage.tsx` |
| `apps/web/src/services/legajoService.ts` | `apps/web/src/features/documents/services/legajoService.ts` |
| `apps/web/src/services/templatesService.ts` | `apps/web/src/features/documents/services/templatesService.ts` |

### Files to CREATE (3 NEW barrels)

| Path | Content |
|---|---|
| `apps/web/src/features/documents/index.ts` | `export * from './pages'`, `export * from './services'` |
| `apps/web/src/features/documents/pages/index.ts` | 3 default-export pages |
| `apps/web/src/features/documents/services/index.ts` | `export * from './legajoService'` + `'./templatesService'` |

### Files to LEAVE in place

- `features/legajo/` — Spanish placeholder, deleted in L4.11
- `pages/legajo/`, `pages/onboarding/` — pages/legajo/ becomes empty (L4.11); pages/onboarding/ has other files
- `services/` — many other services live here

### Consumer files — ~10 sites across 9 files

External (6 files):
- `App.tsx` — 3 page direct imports
- `pages/onboarding/OnboardingAdminPage.tsx` — `@/services/legajoService`
- `features/employees/components/AdminDocUpload.tsx` — `@/services/legajoService`
- `features/employees/components/TabAcademicos.tsx` — `@/services/legajoService`
- `features/employees/components/TabFamiliares.tsx` — `@/services/legajoService`
- `features/employees/components/TabLaborales.tsx` — `@/services/legajoService`

Internal to moved set (3 files):
- `pages/legajo/GestionDocumentosPage.tsx` — `@/services/legajoService`
- `pages/legajo/LegajoPage.tsx` — `@/services/legajoService`
- `pages/PlantillasDocumentosPage.tsx` — `@/services/templatesService`

**Sibling-relative sweep (LR32):** clean.

---

## Mapping table (length-DESC)

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/pages/legajo/GestionDocumentosPage` | `@/features/documents/pages/GestionDocumentosPage` |
| 2 | `@/pages/PlantillasDocumentosPage` | `@/features/documents/pages/PlantillasDocumentosPage` |
| 3 | `@/services/templatesService` | `@/features/documents/services/templatesService` |
| 4 | `@/pages/legajo/LegajoPage` | `@/features/documents/pages/LegajoPage` |
| 5 | `@/services/legajoService` | `@/features/documents/services/legajoService` |

---

## Task 1: Branch + plan commit

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.7-feature-documents
git add docs/superpowers/plans/2026-05-07-vyntia-foundation-L4.7-feature-documents.md
git commit -m "$(cat <<'EOF'
docs(L4.7): add documents feature migration plan

Plan for moving documents slice (3 pages + 2 services) into
features/documents/. Includes legajo->documents English rename. ~10
import sites across 9 files. 3 new barrels.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

## Task 2: mkdir + git mv 5 files

```bash
cd D:/VYNTIA
mkdir -p apps/web/src/features/documents/pages
mkdir -p apps/web/src/features/documents/services

git mv apps/web/src/pages/PlantillasDocumentosPage.tsx       apps/web/src/features/documents/pages/PlantillasDocumentosPage.tsx
git mv apps/web/src/pages/legajo/GestionDocumentosPage.tsx   apps/web/src/features/documents/pages/GestionDocumentosPage.tsx
git mv apps/web/src/pages/legajo/LegajoPage.tsx              apps/web/src/features/documents/pages/LegajoPage.tsx
git mv apps/web/src/services/legajoService.ts                apps/web/src/features/documents/services/legajoService.ts
git mv apps/web/src/services/templatesService.ts             apps/web/src/features/documents/services/templatesService.ts

git status && git diff --stat --staged
```

Expected: 5 `renamed:` entries, 0 line changes.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.7): move documents files to features/documents/ (rename only)

git mv 5 files into features/documents/{pages,services}/ with file bodies
100% unchanged.

Files moved:
- pages/PlantillasDocumentosPage.tsx → features/documents/pages/
- pages/legajo/{GestionDocumentos,Legajo}Page.tsx → features/documents/pages/
- services/{legajo,templates}Service.ts → features/documents/services/

Spanish placeholder features/legajo/ stays (L4.11 cleanup).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Sanity:

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "Cannot find module.*@/(pages/(legajo/|PlantillasDocumentosPage)|services/(legajo|templates)Service)" | head -10
```

Expected: errors for moved aliases.

## Task 3: Imports + 3 barrels

### Step 3a: Write Python script `D:/VYNTIA/scripts/L4.7-rewrite-imports.py`:

```python
"""L4.7 import path rewriter — documents feature migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

MAPPINGS = [
    ("@/pages/legajo/GestionDocumentosPage", "@/features/documents/pages/GestionDocumentosPage"),
    ("@/pages/PlantillasDocumentosPage",     "@/features/documents/pages/PlantillasDocumentosPage"),
    ("@/services/templatesService",          "@/features/documents/services/templatesService"),
    ("@/pages/legajo/LegajoPage",            "@/features/documents/pages/LegajoPage"),
    ("@/services/legajoService",             "@/features/documents/services/legajoService"),
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

### Step 3b: Run

```bash
cd D:/VYNTIA && python scripts/L4.7-rewrite-imports.py
```

Expected: ~9 files updated.

### Step 3c: Verify zero stale + sibling sweep

```bash
cd D:/VYNTIA && grep -rn "@/pages/legajo/\|@/pages/PlantillasDocumentosPage\|@/services/legajoService\|@/services/templatesService" apps/web/src/ apps/web/tests/ 2>/dev/null
echo "--- sibling ---"
cd D:/VYNTIA && grep -rn "from ['\"]\./legajoService\|from ['\"]\./templatesService\|from ['\"]\.\./services/legajoService\|from ['\"]\.\./services/templatesService" apps/web/src/ 2>/dev/null
```

Both: empty.

### Step 3d: Verify export styles

```bash
cd D:/VYNTIA && grep -E "^export" apps/web/src/features/documents/pages/*.tsx
```

Per App.tsx (`import X from`), all 3 expected as `export default`. If any is named-only, switch barrel template.

### Step 3e: Create 3 NEW barrels (Write tool)

**`apps/web/src/features/documents/pages/index.ts`** (3 defaults expected):
```typescript
export { default as GestionDocumentosPage } from './GestionDocumentosPage'
export { default as LegajoPage } from './LegajoPage'
export { default as PlantillasDocumentosPage } from './PlantillasDocumentosPage'
```

**`apps/web/src/features/documents/services/index.ts`:**
```typescript
export * from './legajoService'
export * from './templatesService'
```

**`apps/web/src/features/documents/index.ts`:**
```typescript
// Documents Feature Exports
export * from './pages'
export * from './services'
```

### Step 3f: All baseline checks

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | grep -E "Tests|Test Files"
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -3
```

Expected: tsc 1 (BlankEnum.ts), build clean, vitest 7, eslint 634, pytest 161/8/3.

### Step 3g: Delete script + commit

```bash
cd D:/VYNTIA && rm scripts/L4.7-rewrite-imports.py
cd D:/VYNTIA && git add -A && git status --short
```

Expected: ~9 modified .ts/.tsx + 3 new barrels.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.7): update consumer imports + create features/documents/ barrels

Python script with 5 mappings rewrites ~10 import sites across 9 files.
3 new barrels created.

External consumers (6):
- App.tsx (3 page imports), pages/onboarding/OnboardingAdminPage,
  features/employees/components/{AdminDocUpload,TabAcademicos,TabFamiliares,TabLaborales}

Internal updates inside moved files (3):
- features/documents/pages/{GestionDocumentos,Legajo}Page: legajoService alias
- features/documents/pages/PlantillasDocumentosPage: templatesService alias

LR32 carry-over: sibling-relative sweep clean.

Verified:
- tsc: 0 new errors (1 pre-existing BlankEnum.ts)
- build clean, vitest 7, lint 634, pytest 161/8/3

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Tasks 4-6: Smoke (skip), PAUSE, merge

Same pattern as L4.2-L4.6.

Merge message:
```
Merge L4.7: features/documents/ migration

Documents slice consolidated under features/documents/ — 3 pages
(GestionDocumentos, Legajo, PlantillasDocumentos) + 2 services
(legajoService, templatesService) + 3 new barrels. 6 external consumers
+ 3 internal imports redirected. Spanish placeholder features/legajo/
stays (L4.11). Includes legajo→documents English rename. Baselines
preserved: pytest 161/8/3, vitest 7, build clean, tsc 0 new, lint 634.
```

Update L4 master roadmap row to ✅ with merge hash. Mark L4.8 as ⏳ NEXT.
