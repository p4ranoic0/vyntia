# VYNTIA Foundation L4.3 — Identity Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the identity slice (5 user pages + 3 security pages + 4 user modals + 2 services) from the flat layout into a self-contained `features/identity/` bounded context, with all consumer imports redirected via `@/features/identity/*` aliases — preserving every test/lint/build baseline.

**Architecture:** Pure organizational refactor. No behavior changes. `git mv` for rename detection (`features/identity/` does NOT exist yet — must be created first), then a single Python pass updates ~20 import sites across ~16 files. Mirrors the L4.1/L4.2 three-commit pattern: (1) plan, (2) atomic moves, (3) import rewrites + barrel population.

**Tech Stack:** TypeScript, React, Vite, vitest, ESLint, React Router. No backend touched.

**Predecessor:** L4.2 ✅ merged `67ac4346` 2026-05-06 (auth feature migration).

**Branch:** `vyntia/L4.3-feature-identity` (cut from master).

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.3 row.

---

## Scope inventory (verified 2026-05-06 against working tree)

### Files to MOVE (15 files)

| From (current path) | To (target path) |
|---|---|
| `apps/web/src/pages/users/ChangePassword.tsx` | `apps/web/src/features/identity/pages/ChangePassword.tsx` |
| `apps/web/src/pages/users/RoleManagement.tsx` | `apps/web/src/features/identity/pages/RoleManagement.tsx` |
| `apps/web/src/pages/users/UsersForm.tsx` | `apps/web/src/features/identity/pages/UsersForm.tsx` |
| `apps/web/src/pages/users/UsersList.tsx` | `apps/web/src/features/identity/pages/UsersList.tsx` |
| `apps/web/src/pages/users/UsersManagement.tsx` | `apps/web/src/features/identity/pages/UsersManagement.tsx` |
| `apps/web/src/pages/users/index.ts` | `apps/web/src/features/identity/pages/index.ts` |
| `apps/web/src/pages/security/PermissionsPage.tsx` | `apps/web/src/features/identity/pages/PermissionsPage.tsx` |
| `apps/web/src/pages/security/RolePermissionsPage.tsx` | `apps/web/src/features/identity/pages/RolePermissionsPage.tsx` |
| `apps/web/src/pages/security/RolesPage.tsx` | `apps/web/src/features/identity/pages/RolesPage.tsx` |
| `apps/web/src/components/users/modals/ChangePasswordModal.tsx` | `apps/web/src/features/identity/components/modals/ChangePasswordModal.tsx` |
| `apps/web/src/components/users/modals/RoleManagementModal.tsx` | `apps/web/src/features/identity/components/modals/RoleManagementModal.tsx` |
| `apps/web/src/components/users/modals/UserDetailsModal.tsx` | `apps/web/src/features/identity/components/modals/UserDetailsModal.tsx` |
| `apps/web/src/components/users/modals/UserFormModal.tsx` | `apps/web/src/features/identity/components/modals/UserFormModal.tsx` |
| `apps/web/src/services/usersService.ts` | `apps/web/src/features/identity/services/usersService.ts` |
| `apps/web/src/services/securityService.ts` | `apps/web/src/features/identity/services/securityService.ts` |

**Special note:** `pages/users/index.ts` is the EXISTING barrel that consolidates user-page exports + re-exports types from `@/services/usersService`. It moves alongside the page files (the barrel becomes `features/identity/pages/index.ts`). The Python script will rewrite its internal `@/services/usersService` reference to `@/features/identity/services/usersService` automatically.

### Directory creation (BEFORE `git mv`)

`features/identity/` does NOT exist (unlike `features/auth/` which had a pre-built skeleton in L4.2). Must `mkdir -p` these BEFORE git mv:

```
features/identity/
  ├── components/modals/
  ├── pages/
  └── services/
```

**Note:** `features/identity/types/` is intentionally NOT created (no types to move; D1 master roadmap specifies `types/` only when needed).

### Files to CREATE (3 new barrels — fresh files, not stub overwrites)

Unlike L4.2 (which overwrote pre-existing stub `index.ts` files), these are net-new:

| Path | Content |
|---|---|
| `apps/web/src/features/identity/index.ts` | Top-level: `export * from './components'`, `export * from './pages'`, `export * from './services'` |
| `apps/web/src/features/identity/components/index.ts` | `export * from './modals'` |
| `apps/web/src/features/identity/components/modals/index.ts` | Named exports for 4 modals |
| `apps/web/src/features/identity/services/index.ts` | `export * from './usersService'`, `export * from './securityService'` |

The `features/identity/pages/index.ts` is the MOVED `pages/users/index.ts` — already exists post-move, no action needed beyond Python script rewriting its internal alias.

### Files to LEAVE in place

- `apps/web/src/features/security/` and `apps/web/src/features/usuarios/` — Spanish placeholders. Per L4 master roadmap D1 + L4.11 row, these get DELETED in L4.11 after all features migrated to canonical English names. Don't touch them in L4.3.
- `apps/web/src/components/users/` — directory becomes empty after `modals/` subdir moves out. Leave the empty directory (L4.11 cleanup deletes orphaned empty dirs project-wide).
- `apps/web/src/pages/users/` — directory becomes empty after all 6 files move. Leave it.
- `apps/web/src/pages/security/` — same.
- `apps/web/src/services/` — many other services live here, untouched.

### Consumer files (external) — 1 file with import updates

- `App.tsx` — 4 imports:
  - 3 security page direct imports (`@/pages/security/PermissionsPage`, `@/pages/security/RolePermissionsPage`, `@/pages/security/RolesPage`)
  - 1 barrel import (`from '@/pages/users'` — destructures `RoleManagement`, `ChangePassword as UsersChangePassword`, `UsersForm`, `UsersList`, `UsersManagement`)

### Consumer files (internal to moved set) — 14 files with import updates after move

These are imports inside the 15 moved files themselves. They use `@/...` aliases that get rewritten by the Python script:

- `pages/users/UsersList.tsx` (5 sites): usersService + 4 modals
- `pages/users/UsersManagement.tsx`: usersService
- `pages/users/UsersForm.tsx`: usersService
- `pages/users/RoleManagement.tsx`: usersService
- `pages/users/ChangePassword.tsx`: usersService
- `pages/users/index.ts`: usersService (type re-exports)
- `pages/security/RolesPage.tsx`: securityService
- `pages/security/RolePermissionsPage.tsx`: securityService (×2 imports)
- `pages/security/PermissionsPage.tsx`: securityService
- `components/users/modals/UserFormModal.tsx`: usersService
- `components/users/modals/UserDetailsModal.tsx`: usersService
- `components/users/modals/RoleManagementModal.tsx`: usersService
- `components/users/modals/ChangePasswordModal.tsx`: usersService

### Total import-update sites: ~20 across ~16 files

(Actual file count: 1 external [App.tsx with 4 import statements] + 13 internal-to-moved-set + 0 sibling-relative refs verified absent. Total ~14-16 files modified by Python script.)

**Sibling-relative import audit (LR32 lesson):** verified via `grep "from ['\"]\./usersService\|from ['\"]\./securityService"` — zero matches. Unlike L4.2 (which had `services/menuService.ts` doing `./authService`), no remaining `services/X.ts` references its sibling `usersService.ts` or `securityService.ts` via relative path. Python script's alias-only mapping is sufficient here.

---

## Mapping table (canonical, length-ordered DESC)

The Python script processes mappings serially. Length-DESC order prevents prefix collisions (e.g., `@/services/usersService` is a substring of `@/services/usersServiceX` — none exist, but ordering is defensive).

| # | OLD path | NEW path |
|---:|---|---|
| 1 | `@/components/users/modals/ChangePasswordModal` | `@/features/identity/components/modals/ChangePasswordModal` |
| 2 | `@/components/users/modals/RoleManagementModal` | `@/features/identity/components/modals/RoleManagementModal` |
| 3 | `@/pages/security/RolePermissionsPage` | `@/features/identity/pages/RolePermissionsPage` |
| 4 | `@/components/users/modals/UserDetailsModal` | `@/features/identity/components/modals/UserDetailsModal` |
| 5 | `@/pages/security/PermissionsPage` | `@/features/identity/pages/PermissionsPage` |
| 6 | `@/components/users/modals/UserFormModal` | `@/features/identity/components/modals/UserFormModal` |
| 7 | `@/pages/security/RolesPage` | `@/features/identity/pages/RolesPage` |
| 8 | `@/services/securityService` | `@/features/identity/services/securityService` |
| 9 | `@/services/usersService` | `@/features/identity/services/usersService` |
| 10 | `@/pages/users` | `@/features/identity/pages` |

**Justification of order:** Entry 10 (`@/pages/users`) is a substring of any hypothetical `@/pages/users/X` (none exist per `grep "@/pages/users/[A-Z]"` returning empty), so its position is defensive only. All other entries are non-overlapping prefixes.

**LR32 carry-over:** No relative-import sweep needed (audit returned empty above). Python alias-only script is sufficient for L4.3.

---

## Pre-flight (before any commit)

Verify clean state. Baselines from L4.2 merge are still current — no need to re-measure unless something looks off.

- [ ] **Step 1: Confirm clean working tree on master**

```bash
cd D:/VYNTIA && git status --short && git branch --show-current
```

Expected: empty output (clean), branch `master`.

- [ ] **Step 2: Spot-check current baselines**

If you want to re-measure (recommended after a long pause but optional if continuing right after L4.2):

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -3
```

Expected (carry-over from L4.2 merge):
- build: `✓ built in <N>s`
- vitest: `Test Files 2 passed (3)`, `Tests 7 passed (7)`, 1 file load failure
- eslint: `✖ 636 problems (402 errors, 234 warnings)` — `LINT_BASELINE = 636`
- pytest: `8 failed, 161 passed, 3 skipped`
- tsc: 5 pre-existing errors in `features/empleados/REACT_QUERY_EXAMPLE.ts:427-430` + `generated/api/models/BlankEnum.ts:6` (unchanged)

---

## Task 1: Create branch + commit plan

**Files:**
- Modify: none (branch creation only)

- [ ] **Step 1: Create and check out the branch**

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.3-feature-identity
```

Expected: `Switched to a new branch 'vyntia/L4.3-feature-identity'`.

- [ ] **Step 2: Stage and commit the plan**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.3-feature-identity.md
git commit -m "$(cat <<'EOF'
docs(L4.3): add identity feature migration plan

Plan for moving identity slice (5 user pages + 3 security pages + 4 modals
+ 2 services) into features/identity/ bounded context. Mirror L4.2
three-commit pattern (plan, moves, imports). 1 external consumer + ~13
internal import updates via Python script. features/identity/ created
fresh (no skeleton existed). Spanish placeholders features/security/ and
features/usuarios/ stay for L4.11 cleanup.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `1 file changed, NNN insertions(+)`.

---

## Task 2: Create features/identity/ skeleton + git mv all 15 files

**Goal:** Create the destination directory tree, then atomically move all 15 files via `git mv`. Single commit, no body changes — preserves git rename detection (≥95% target) and blame history.

**Files:**
- Create dirs: `features/identity/{components/modals,pages,services}/`
- Move: 15 files per the inventory table

- [ ] **Step 1: Create the destination directory tree**

```bash
cd D:/VYNTIA
mkdir -p apps/web/src/features/identity/components/modals
mkdir -p apps/web/src/features/identity/pages
mkdir -p apps/web/src/features/identity/services
```

Expected: silent success. (`mkdir -p` is idempotent; if dirs exist they're a no-op.)

Note: empty directories don't get committed by git. They exist only to host the moved files in Step 2-5 below; they'll be auto-included in the commit because they contain files post-move.

- [ ] **Step 2: Move the 6 user pages (5 .tsx + 1 index.ts)**

```bash
cd D:/VYNTIA
git mv apps/web/src/pages/users/ChangePassword.tsx    apps/web/src/features/identity/pages/ChangePassword.tsx
git mv apps/web/src/pages/users/RoleManagement.tsx    apps/web/src/features/identity/pages/RoleManagement.tsx
git mv apps/web/src/pages/users/UsersForm.tsx         apps/web/src/features/identity/pages/UsersForm.tsx
git mv apps/web/src/pages/users/UsersList.tsx         apps/web/src/features/identity/pages/UsersList.tsx
git mv apps/web/src/pages/users/UsersManagement.tsx   apps/web/src/features/identity/pages/UsersManagement.tsx
git mv apps/web/src/pages/users/index.ts              apps/web/src/features/identity/pages/index.ts
```

- [ ] **Step 3: Move the 3 security pages**

```bash
cd D:/VYNTIA
git mv apps/web/src/pages/security/PermissionsPage.tsx     apps/web/src/features/identity/pages/PermissionsPage.tsx
git mv apps/web/src/pages/security/RolePermissionsPage.tsx apps/web/src/features/identity/pages/RolePermissionsPage.tsx
git mv apps/web/src/pages/security/RolesPage.tsx           apps/web/src/features/identity/pages/RolesPage.tsx
```

- [ ] **Step 4: Move the 4 user modals**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/users/modals/ChangePasswordModal.tsx  apps/web/src/features/identity/components/modals/ChangePasswordModal.tsx
git mv apps/web/src/components/users/modals/RoleManagementModal.tsx  apps/web/src/features/identity/components/modals/RoleManagementModal.tsx
git mv apps/web/src/components/users/modals/UserDetailsModal.tsx     apps/web/src/features/identity/components/modals/UserDetailsModal.tsx
git mv apps/web/src/components/users/modals/UserFormModal.tsx        apps/web/src/features/identity/components/modals/UserFormModal.tsx
```

- [ ] **Step 5: Move the 2 services**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/usersService.ts    apps/web/src/features/identity/services/usersService.ts
git mv apps/web/src/services/securityService.ts apps/web/src/features/identity/services/securityService.ts
```

- [ ] **Step 6: Verify rename detection (target ≥ 95%)**

```bash
cd D:/VYNTIA && git status && git diff --stat --staged
```

Expected:
- `git status` shows 15 entries as `renamed:` (NOT `deleted:` + `new file:`)
- `git diff --stat --staged` shows 15 files with 0 line changes (pure renames)
- Source dirs `apps/web/src/{pages/users,pages/security,components/users/modals}/` will be empty (their contents moved)
- `apps/web/src/services/` still has many other files (only 2 services moved out)

If ANY of the 15 shows as `deleted + new file`, ABORT and report BLOCKED.

- [ ] **Step 7: Commit the moves**

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.3): move identity files to features/identity/ (rename only)

git mv 15 files into features/identity/{components/modals,pages,services}/
with file bodies 100% unchanged. Rename detection ≥95% expected — preserves
blame history. Imports updated in next commit (separate atomic step per
LR31).

Files moved:
- pages/users/{ChangePassword,RoleManagement,UsersForm,UsersList,UsersManagement,index}.tsx|ts
  → features/identity/pages/
- pages/security/{PermissionsPage,RolePermissionsPage,RolesPage}.tsx
  → features/identity/pages/
- components/users/modals/{ChangePasswordModal,RoleManagementModal,UserDetailsModal,UserFormModal}.tsx
  → features/identity/components/modals/
- services/{usersService,securityService}.ts
  → features/identity/services/

Spanish placeholders features/security/ + features/usuarios/ stay
(L4.11 deletion scope).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `15 files changed, 0 insertions(+), 0 deletions(-)`.

- [ ] **Step 8: Sanity check — confirm imports are now broken**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "Cannot find module|@/components/users/|@/pages/users|@/pages/security|@/services/usersService|@/services/securityService" | head -20
```

Expected: TypeScript errors about missing modules — at least one referencing each moved alias. This confirms the moves happened and imports are broken (intentional). If tsc shows ZERO errors for moved files, something is wrong.

---

## Task 3: Rewrite import paths via Python script + create barrels

**Goal:** Single atomic commit that fixes every broken import (external + internal) and CREATES the new barrel files for `features/identity/`.

**Files:**
- Modify: ~14-16 .ts/.tsx files (import path updates)
- Create: 4 new barrel files (`features/identity/index.ts` + `components/index.ts` + `components/modals/index.ts` + `services/index.ts`)

(`features/identity/pages/index.ts` already exists — it was moved from `pages/users/index.ts` in Task 2 and gets its internal `@/services/usersService` reference rewritten by the Python script.)

- [ ] **Step 1: Write the Python rewrite script**

Create `D:/VYNTIA/scripts/L4.3-rewrite-imports.py`:

```python
"""L4.3 import path rewriter — identity feature migration.

Walks apps/web/src/ + apps/web/tests/, applies 10 OLD->NEW prefix mappings to
every .ts/.tsx file, prints a per-file edit count.

Mappings are length-ordered DESCENDING (defensive — no actual prefix collisions
in this PR per pre-flight grep).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

# OLD -> NEW. Length-DESC order is defensive — see plan section "Mapping table".
MAPPINGS = [
    ("@/components/users/modals/ChangePasswordModal", "@/features/identity/components/modals/ChangePasswordModal"),
    ("@/components/users/modals/RoleManagementModal", "@/features/identity/components/modals/RoleManagementModal"),
    ("@/pages/security/RolePermissionsPage",          "@/features/identity/pages/RolePermissionsPage"),
    ("@/components/users/modals/UserDetailsModal",    "@/features/identity/components/modals/UserDetailsModal"),
    ("@/pages/security/PermissionsPage",              "@/features/identity/pages/PermissionsPage"),
    ("@/components/users/modals/UserFormModal",       "@/features/identity/components/modals/UserFormModal"),
    ("@/pages/security/RolesPage",                    "@/features/identity/pages/RolesPage"),
    ("@/services/securityService",                    "@/features/identity/services/securityService"),
    ("@/services/usersService",                       "@/features/identity/services/usersService"),
    ("@/pages/users",                                 "@/features/identity/pages"),
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
    total_files = 0
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in EXTS:
                if rewrite(p):
                    rel = p.relative_to(ROOT)
                    print(f"updated: {rel}")
                    total_files += 1
    print(f"\nTotal files updated: {total_files}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the script**

```bash
cd D:/VYNTIA && python scripts/L4.3-rewrite-imports.py
```

Expected output: ~14-16 lines of `updated: ...` followed by `Total files updated: 14` (give or take 2).
Files that should appear:
- `src/App.tsx` (4 import sites)
- All 9 moved page files (their internal usersService/securityService refs)
- All 4 moved modals (their usersService refs)
- The moved barrel `src/features/identity/pages/index.ts` (its usersService re-export)

- [ ] **Step 3: Verify no stale OLD paths remain**

```bash
cd D:/VYNTIA && grep -rn "@/components/users/modals/\|@/pages/users\b\|@/pages/security/\|@/services/usersService\|@/services/securityService" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty output (zero matches). If any line is returned, those imports were missed — investigate (likely a typo in the script or a path not in the mapping table).

**Note:** The `\b` word boundary in `@/pages/users\b` prevents catching `@/pages/users/X` style strings (none exist anyway, but defensive).

- [ ] **Step 4: Verify NEW paths exist (sanity)**

```bash
cd D:/VYNTIA && grep -rn "@/features/identity/" apps/web/src/App.tsx | head -10
```

Expected: 4 lines showing App.tsx now imports from `@/features/identity/pages/PermissionsPage`, `@/features/identity/pages/RolePermissionsPage`, `@/features/identity/pages/RolesPage`, and `@/features/identity/pages` (barrel).

- [ ] **Step 5: Sibling-relative import sweep (LR32 carry-over)**

```bash
cd D:/VYNTIA && grep -rn "from ['\"]\./usersService\|from ['\"]\./securityService\|from ['\"]\.\./services/usersService\|from ['\"]\.\./services/securityService" apps/web/src/ 2>/dev/null
```

Expected: empty output. If any match appears, it's a sibling that needs manual fix (per LR32 lesson from L4.2).

- [ ] **Step 6: Create the 4 NEW barrel files**

Use the Write tool to create each (these don't exist — `features/identity/` was created fresh).

**`apps/web/src/features/identity/components/modals/index.ts`:**
```typescript
export { ChangePasswordModal } from './ChangePasswordModal'
export { RoleManagementModal } from './RoleManagementModal'
export { UserDetailsModal } from './UserDetailsModal'
export { UserFormModal } from './UserFormModal'
```

**Note:** Modal exports are NAMED (not `default as X`) — verified by grepping `import { UserFormModal }` etc. in current consumers. Modals export named, not default.

**`apps/web/src/features/identity/components/index.ts`:**
```typescript
export * from './modals'
```

**`apps/web/src/features/identity/services/index.ts`:**
```typescript
export * from './usersService'
export * from './securityService'
```

**`apps/web/src/features/identity/index.ts`:**
```typescript
// Identity Feature Exports
export * from './components'
export * from './pages'
export * from './services'
```

NOTE: `features/identity/pages/index.ts` already exists (moved from `pages/users/index.ts` in Task 2). It already exports the 5 user pages + re-exports types from `@/services/usersService` (now rewritten by Python script to `@/features/identity/services/usersService`). The 3 security pages are NOT added to the barrel because App.tsx imports them directly (`@/features/identity/pages/PermissionsPage`), not via barrel — keep YAGNI.

- [ ] **Step 7: Verify modal export style assumption**

Quick spot-check that modals really do use named exports (not default):

```bash
cd D:/VYNTIA && grep -E "^export " apps/web/src/features/identity/components/modals/*.tsx | head -8
```

Expected: each modal has an `export const X` or `export function X` or `export { X }` — confirming the named-export barrel above is correct. If you see `export default X` instead, switch the modal barrel to `export { default as X } from './X'` style.

- [ ] **Step 8: TypeScript strict check**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -15
```

**Pre-existing tsc errors (MUST remain — NOT introduced by L4.3):**
- `src/features/empleados/REACT_QUERY_EXAMPLE.ts` lines 427-430: 4 errors
- `src/generated/api/models/BlankEnum.ts:6,5`: 1 error

**Total expected: 5 pre-existing errors, 0 new errors.**

If you see ANY error in a file path containing `identity`, `users`, `security`, `usersService`, `securityService`, `UserFormModal`, `UserDetailsModal`, `ChangePasswordModal`, `RoleManagementModal`, `UsersList`, `UsersForm`, `UsersManagement`, `ChangePassword.tsx`, `RoleManagement.tsx`, `PermissionsPage`, `RolePermissionsPage`, or `RolesPage` — that's a NEW error introduced by L4.3 and MUST be fixed.

- [ ] **Step 9: Build check**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -10
```

Expected: `✓ built in <N>s`.

- [ ] **Step 10: Vitest check**

```bash
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | tail -10
```

Expected: `Tests 7 passed (7)`, 1 file load failure pre-existing.

- [ ] **Step 11: Lint delta check**

```bash
cd D:/VYNTIA/apps/web && npx eslint . 2>&1 | tail -3
```

**LINT_BASELINE = 636 problems (402 errors, 234 warnings)**

Expected: same exact count. Delta of 0 is success.

- [ ] **Step 12: pytest baseline check**

```bash
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -5
```

Expected: `8 failed, 161 passed, 3 skipped`.

- [ ] **Step 13: Delete the throwaway script**

```bash
cd D:/VYNTIA && rm scripts/L4.3-rewrite-imports.py
```

- [ ] **Step 14: Commit imports + barrels**

```bash
cd D:/VYNTIA && git add -A && git status --short
```

Expected: ~14-16 modified .ts/.tsx files + 4 new barrel files. NO `scripts/L4.3-rewrite-imports.py`.

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.3): update consumer imports + create features/identity/ barrels

Bulk import rewrite via Python script (single-pass, length-DESC mapping
order). ~20 import sites across ~14 files redirected to
@/features/identity/* aliases.

External consumers updated (1 file):
- App.tsx: 3 security page direct imports + 1 users barrel import

Internal import updates inside moved files (~13 sites):
- 4 modals: @/services/usersService -> @/features/identity/services/usersService
- 5 user pages: @/services/usersService -> @/features/identity/services/usersService
- 3 security pages: @/services/securityService -> @/features/identity/services/securityService
- pages/index.ts (the moved barrel): @/services/usersService re-export updated

New barrels created:
- features/identity/index.ts (top-level: re-exports components/pages/services)
- features/identity/components/index.ts (re-exports modals)
- features/identity/components/modals/index.ts (4 named modal exports)
- features/identity/services/index.ts (re-exports usersService + securityService)

Pre-existing barrel features/identity/pages/index.ts (moved from
pages/users/index.ts) had its internal alias rewritten — NOT recreated.

LR32 carry-over: sibling-relative import sweep returned empty (no
services/X.ts referenced its sibling usersService/securityService via
relative path). Python alias-only script sufficient.

Verified:
- npx tsc --noEmit: 0 new errors (5 pre-existing in REACT_QUERY_EXAMPLE.ts + BlankEnum.ts)
- npm run build: clean
- vitest: 7 passed (1 file load failure pre-existing)
- npx eslint: 636 problems (matches LINT_BASELINE — delta 0)
- pytest: 161/8/3 baseline preserved

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: ~18-20 files changed (14-16 imports + 4 new barrels).

- [ ] **Step 15: Final post-commit verification**

```bash
cd D:/VYNTIA && git log --oneline master..HEAD && git show --stat HEAD | tail -5
```

Expected: 3 commits ahead of master; the new commit shows ~18-20 files changed.

---

## Task 4: Smoke test — manual UI walkthrough

Per LR26 (TS strict doesn't catch `any`-typed runtime breaks).

**Files:** none

- [ ] **Step 1: Start dev server**

```bash
cd D:/VYNTIA/apps/web && npm run dev
```

Wait for `VITE v… ready in <N> ms` and the local URL.

- [ ] **Step 2: Verify the identity flow paths render**

Open the dev URL in a browser and check:

1. Log in (uses moved authService) → reaches Dashboard
2. Visit `/usuarios/` (or whatever route App.tsx defines for UsersManagement) → renders UsersList
3. Click into a user → opens UserDetailsModal / UserFormModal
4. Visit `/seguridad/roles/` → renders RolesPage
5. Visit `/seguridad/permisos/` → renders PermissionsPage
6. Visit `/seguridad/role-permissions/` → renders RolePermissionsPage
7. Browser devtools console → no red errors related to module resolution

**If backend not running:** form-fetch errors are acceptable. Criterion: components render and React doesn't crash.

User can SKIP this step if comfortable trusting static checks (build/tsc/lint/vitest/pytest all green).

- [ ] **Step 3: Stop the dev server**

`Ctrl+C` in the terminal.

- [ ] **Step 4: No commit needed for smoke test**

If a defect is found, return to Task 3 to fix.

---

## Task 5: PAUSE — request user authorization to merge

**Files:** none

- [ ] **Step 1: Display final branch summary**

```bash
cd D:/VYNTIA && git log --oneline master..vyntia/L4.3-feature-identity
cd D:/VYNTIA && git diff --stat master..vyntia/L4.3-feature-identity | tail -10
```

Expected: 3 commits on the branch (plan, moves, imports/barrels). Diff: ~33-35 files (15 renames + 14-16 modifications + 4 new barrels).

- [ ] **Step 2: ASK USER: "L4.3 ready to merge?"**

Wait for explicit user authorization before Task 6. Do NOT auto-merge.

---

## Task 6: Merge to master with `--no-ff` (only after user approval)

**Files:** none

- [ ] **Step 1: Switch to master and merge**

```bash
cd D:/VYNTIA && git checkout master && git merge --no-ff vyntia/L4.3-feature-identity -m "Merge L4.3: features/identity/ migration

Identity slice consolidated under features/identity/ — 5 user pages + 3
security pages + 4 modals + 2 services + 4 new barrels (top-level +
components/ + components/modals/ + services/). Pre-existing pages/users/index.ts
moved alongside the pages and serves as features/identity/pages/index.ts.
1 external consumer (App.tsx) + ~13 internal imports redirected to
@/features/identity/* aliases. Spanish placeholders features/security/ and
features/usuarios/ stay (L4.11 cleanup). Baselines preserved: pytest 161/8/3,
vitest 7, build clean, tsc 0 new errors, lint delta 0."
```

Expected: `Merge made by the 'ort' strategy.` plus file change summary.

- [ ] **Step 2: Capture merge commit hash**

```bash
cd D:/VYNTIA && git log --oneline -1
```

Note the short hash for the roadmap update.

- [ ] **Step 3: Update L4 master roadmap status row**

Edit `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md`. Find the L4.3 row in the sub-PR table. Change:

```
| **L4.3** | identity feature migration | `vyntia/L4.3-feature-identity` | Move ... ~50-70 import updates | ~18 | Medio | L4.1 | ⏳ NEXT |
```

To:

```
| **L4.3** | identity feature migration | `vyntia/L4.3-feature-identity` | Moved 15 files (5 user pages + 3 security pages + 4 modals + 2 services + pre-existing users barrel) → features/identity/{components/modals,pages,services}/. 4 new barrels created (top-level + components + components/modals + services). ~20 import updates across ~14 files via Python script. Spanish placeholders features/security/ + features/usuarios/ kept (L4.11 cleanup). 3 atomic commits. Pytest 161/8/3 + vitest 7 + build clean + tsc 0 + lint delta 0 baselines preservados. | ~18 | Medio | L4.1 | ✅ merged `<HASH>` |
```

Replace `<HASH>` with the actual merge commit short hash.

Mark L4.4 as `⏳ NEXT`.

- [ ] **Step 4: Commit the roadmap update**

```bash
cd D:/VYNTIA && git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md
git commit -m "$(cat <<'EOF'
docs(L4.3): mark L4.3 merged — identity feature consolidated

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 5: Final post-merge verification**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -5
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | tail -5
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -5
```

Expected: build clean, vitest 7 passed, pytest 161/8/3.

- [ ] **Step 6: Optional — delete the merged branch**

```bash
cd D:/VYNTIA && git branch -d vyntia/L4.3-feature-identity
```

---

## Definition of done

- [ ] `apps/web/src/features/identity/` contains: `pages/{ChangePassword,RoleManagement,UsersForm,UsersList,UsersManagement,PermissionsPage,RolePermissionsPage,RolesPage}.tsx + index.ts`, `components/modals/{ChangePasswordModal,RoleManagementModal,UserDetailsModal,UserFormModal}.tsx`, `services/{usersService,securityService}.ts`, populated barrels at all 4 new index.ts files
- [ ] `apps/web/src/pages/users/` is empty (deletion deferred to L4.11)
- [ ] `apps/web/src/pages/security/` is empty
- [ ] `apps/web/src/components/users/modals/` is empty
- [ ] `apps/web/src/services/usersService.ts` no longer exists
- [ ] `apps/web/src/services/securityService.ts` no longer exists
- [ ] `grep -rn "@/components/users/modals/\|@/pages/users\b\|@/pages/security/\|@/services/usersService\|@/services/securityService" apps/web/src/ apps/web/tests/` returns 0 lines
- [ ] `npx tsc --noEmit -p tsconfig.app.json` returns only the 5 pre-existing errors
- [ ] `npm run build` succeeds
- [ ] `npx vitest run` shows 7 tests passed
- [ ] `npm run lint` problem count = 636 (LINT_BASELINE)
- [ ] `pytest` shows 161/8/3
- [ ] Branch `vyntia/L4.3-feature-identity` merged to master with `--no-ff`
- [ ] Master roadmap row for L4.3 updated to ✅ with merge hash
- [ ] L4.4 marked as ⏳ NEXT in the roadmap

---

## Risk register (L4.3-specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `git mv` rename detection drops below 95% | Low | Med | Move + commit in dedicated commit, NO body changes (Task 2). Verify in Step 6. |
| Python script misses a consumer file | Low | Med | Step 3 grep verification — zero stale OLD paths must remain. |
| Modal barrel uses wrong export style (default vs named) | Low | Med | Step 7 spot-check verifies consumers use `import { X }` style; if `export default` is found in modals, switch the barrel format. |
| LR26 silent runtime break: `any`-typed consumer compiles but fails at runtime | Med | Med | Manual smoke test in Task 4. |
| LR27 Vite esbuild not strict | Med | Low | Step 8 explicitly runs `npx tsc --noEmit -p tsconfig.app.json`. |
| LR32: relative import of moved file from a sibling | Very Low | Med | Pre-flight grep verified 0 such cases. Step 5 re-verification post-script. |
| Backend pytest regresses | Very Low | Low | Step 12 verification. |
| App.tsx barrel import `from '@/pages/users'` ambiguity | Low | Low | Mapping table entry 10 catches the bare barrel form. No `@/pages/users/X` exists per Pre-flight grep, so no collision. |

---

## Self-review

**1. Spec coverage:** Every file in the L4.3 row of the master roadmap (`pages/users/*` + `pages/security/*` + `components/users/modals/*` + `usersService` + `securityService` + App.tsx routes) is covered by Task 2's `git mv` list and Task 3's Python script mapping. The pre-existing `pages/users/index.ts` barrel is also moved (not mentioned in roadmap row but logically required).

**2. Placeholder scan:** No "TBD", "TODO", or "fill in later" tokens. Every step has an exact command or exact code.

**3. Type consistency:** Modal export style is verified in Task 3 Step 7 (defensive — assumes named, switches if default). Barrel exports match what App.tsx imports (`UsersList`, `UsersForm`, `UsersManagement`, `ChangePassword as UsersChangePassword`, `RoleManagement` — 5 default exports from the user pages, preserved by the moved `pages/users/index.ts` → `features/identity/pages/index.ts`).
