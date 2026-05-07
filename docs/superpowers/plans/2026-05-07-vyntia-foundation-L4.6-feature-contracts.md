# VYNTIA Foundation L4.6 — Contracts Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the contracts slice (1 page + 1 service) into `features/contracts/`. Smallest L4 sub-PR.

**Architecture:** Pure organizational refactor. `features/contracts/` does NOT exist (mkdir). 2 file `git mv`, then Python pass updates 5 import sites across 5 files.

**Predecessor:** L4.5 ✅ merged `128ba3c1` 2026-05-06.

**Branch:** `vyntia/L4.6-feature-contracts`.

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.6.

---

## Scope inventory (verified 2026-05-07)

### Files to MOVE (2)

| From | To |
|---|---|
| `apps/web/src/pages/contratos/ContratosPage.tsx` | `apps/web/src/features/contracts/pages/ContratosPage.tsx` |
| `apps/web/src/services/contractsService.ts` | `apps/web/src/features/contracts/services/contractsService.ts` |

### Files to CREATE (3 NEW barrels)

| Path | Content |
|---|---|
| `apps/web/src/features/contracts/index.ts` | `export * from './pages'`, `export * from './services'` |
| `apps/web/src/features/contracts/pages/index.ts` | `export { default as ContratosPage } from './ContratosPage'` (verify default export) |
| `apps/web/src/features/contracts/services/index.ts` | `export * from './contractsService'` |

### Files to LEAVE in place

- `features/contratos/` — Spanish placeholder, deleted in L4.11
- `pages/contratos/` — empty after move (L4.11 cleanup)
- `services/` — many other services live here

### Consumer files — 5 sites across 5 files

| File | Imports |
|---|---|
| `App.tsx` | `@/pages/contratos/ContratosPage` (default) |
| `pages/contratos/ContratosPage.tsx` (will be moved) | `@/services/contractsService` |
| `pages/legajo/LegajoPage.tsx` | `@/services/contractsService` |
| `features/employees/pages/HROverviewDashboard.tsx` | `@/services/contractsService` |
| `features/employees/pages/Empleados.tsx` | `@/services/contractsService` |

**Sibling-relative sweep (LR32):** clean — no `./contractsService` references.

---

## Mapping table

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/pages/contratos/ContratosPage` | `@/features/contracts/pages/ContratosPage` |
| 2 | `@/services/contractsService` | `@/features/contracts/services/contractsService` |

---

## Task 1: Branch + plan commit

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.6-feature-contracts
git add docs/superpowers/plans/2026-05-07-vyntia-foundation-L4.6-feature-contracts.md
git commit -m "$(cat <<'EOF'
docs(L4.6): add contracts feature migration plan

Plan for moving contracts slice (1 page + 1 service) into
features/contracts/. Smallest L4 sub-PR — 2 files, 5 import sites,
3 new barrels.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: mkdir + git mv 2 files

```bash
cd D:/VYNTIA
mkdir -p apps/web/src/features/contracts/pages
mkdir -p apps/web/src/features/contracts/services

git mv apps/web/src/pages/contratos/ContratosPage.tsx apps/web/src/features/contracts/pages/ContratosPage.tsx
git mv apps/web/src/services/contractsService.ts      apps/web/src/features/contracts/services/contractsService.ts

git status && git diff --stat --staged
```

Expected: 2 `renamed:` entries, 0 line changes.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.6): move contracts files to features/contracts/ (rename only)

git mv 2 files into features/contracts/{pages,services}/ with file bodies
100% unchanged.

Files moved:
- pages/contratos/ContratosPage.tsx → features/contracts/pages/
- services/contractsService.ts → features/contracts/services/

Spanish placeholder features/contratos/ stays (L4.11 cleanup).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Sanity check broken imports:

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "Cannot find module.*@/(pages/contratos|services/contractsService)" | head -10
```

Expected: errors for the moved aliases. If zero, BLOCKED.

---

## Task 3: Imports + 3 barrels

### Step 1: Write Python script `D:/VYNTIA/scripts/L4.6-rewrite-imports.py`:

```python
"""L4.6 import path rewriter — contracts feature migration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

MAPPINGS = [
    ("@/pages/contratos/ContratosPage", "@/features/contracts/pages/ContratosPage"),
    ("@/services/contractsService",     "@/features/contracts/services/contractsService"),
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

### Step 2: Run

```bash
cd D:/VYNTIA && python scripts/L4.6-rewrite-imports.py
```

Expected: 5 files updated.

### Step 3: Verify zero stale paths

```bash
cd D:/VYNTIA && grep -rn "@/pages/contratos/\|@/services/contractsService" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty.

### Step 4: Sibling-relative sweep

```bash
cd D:/VYNTIA && grep -rn "from ['\"]\./contractsService\|from ['\"]\.\./services/contractsService" apps/web/src/ 2>/dev/null
```

Expected: empty.

### Step 5: Verify export style

```bash
cd D:/VYNTIA && grep -E "^export" apps/web/src/features/contracts/pages/ContratosPage.tsx
```

Per App.tsx (`import ContratosPage from`), expect `export default`. If different, adjust Step 6.

### Step 6: Create 3 NEW barrels (Write tool)

**`apps/web/src/features/contracts/pages/index.ts`** (default export per App.tsx consumer):
```typescript
export { default as ContratosPage } from './ContratosPage'
```

If Step 5 shows `export function ContratosPage` instead, use:
```typescript
export { ContratosPage } from './ContratosPage'
```

**`apps/web/src/features/contracts/services/index.ts`:**
```typescript
export * from './contractsService'
```

**`apps/web/src/features/contracts/index.ts`:**
```typescript
// Contracts Feature Exports
export * from './pages'
export * from './services'
```

### Step 7: TypeScript strict check

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Expected: only `BlankEnum.ts` error (post-L4.5 baseline = 1 pre-existing).

### Step 8: Build, vitest, lint, pytest

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | grep -E "Tests|Test Files"
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -3
```

Expected: build clean, vitest 7, eslint 634 (post-L4.5 baseline), pytest 161/8/3.

### Step 9: Delete script + commit

```bash
cd D:/VYNTIA && rm scripts/L4.6-rewrite-imports.py
cd D:/VYNTIA && git add -A && git status --short
```

Expected: 5 modified .ts/.tsx + 3 new barrels.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.6): update consumer imports + create features/contracts/ barrels

Python script with 2 mappings rewrites 5 import sites across 5 files.
3 new barrels created.

External consumers (4):
- App.tsx, pages/legajo/LegajoPage,
- features/employees/pages/{HROverviewDashboard,Empleados}

Internal updates inside moved files (1):
- features/contracts/pages/ContratosPage: contractsService alias

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

Same pattern as L4.2-L4.5.

Merge message:
```
Merge L4.6: features/contracts/ migration

Contracts slice consolidated under features/contracts/ — 1 page + 1 service
+ 3 new barrels. 4 external consumers + 1 internal import redirected.
Spanish placeholder features/contratos/ stays (L4.11 cleanup). Baselines
preserved: pytest 161/8/3, vitest 7, build clean, tsc 0 new errors,
lint delta 0.
```

Update L4 master roadmap row to ✅ with merge hash. Mark L4.7 as ⏳ NEXT.
