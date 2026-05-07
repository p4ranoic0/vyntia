# VYNTIA Foundation L4.2 — Auth Feature Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the authentication slice (forms, pages, service, context, hook) from the flat `components/`/`pages/`/`services/`/`hooks/`/`context/` layout into a self-contained `features/auth/` bounded context, with all consumer imports redirected via `@/features/auth/*` aliases — preserving every test/lint/build baseline.

**Architecture:** Pure organizational refactor. No behavior changes. `git mv` for rename detection, then a single Python pass updates 30+ import sites across 26 files. Mirrors the proven L4.1 three-commit pattern: (1) plan, (2) atomic moves, (3) import rewrites + barrel population. `ThemeContext.tsx` stays in `context/` (not auth, defer to L4.11).

**Tech Stack:** TypeScript, React, Vite, vitest, ESLint, Tailwind, React Router. No backend touched.

**Predecessor:** L4.1 ✅ merged `07d86d6e` 2026-05-06 (`shared/` infrastructure consolidation).

**Branch:** `vyntia/L4.2-feature-auth` (cut from master).

**Master roadmap:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.2 row.

---

## Scope inventory (verified 2026-05-06 against working tree)

### Files to MOVE (10 files)

| From (current path) | To (target path) |
|---|---|
| `apps/web/src/components/auth/LoginForm.tsx` | `apps/web/src/features/auth/components/LoginForm.tsx` |
| `apps/web/src/components/auth/ChangePasswordForm.tsx` | `apps/web/src/features/auth/components/ChangePasswordForm.tsx` |
| `apps/web/src/components/auth/ResetPasswordForm.tsx` | `apps/web/src/features/auth/components/ResetPasswordForm.tsx` |
| `apps/web/src/context/AuthContext.tsx` | `apps/web/src/features/auth/context/AuthContext.tsx` |
| `apps/web/src/context/AuthContextInstance.ts` | `apps/web/src/features/auth/context/AuthContextInstance.ts` |
| `apps/web/src/context/AuthContextType.ts` | `apps/web/src/features/auth/context/AuthContextType.ts` |
| `apps/web/src/hooks/useAuth.ts` | `apps/web/src/features/auth/hooks/useAuth.ts` |
| `apps/web/src/services/authService.ts` | `apps/web/src/features/auth/services/authService.ts` |
| `apps/web/src/pages/ChangePasswordPage.tsx` | `apps/web/src/features/auth/pages/ChangePasswordPage.tsx` |
| `apps/web/src/pages/ResetPasswordPage.tsx` | `apps/web/src/features/auth/pages/ResetPasswordPage.tsx` |

### Files to STUB OVER (5 barrels — overwrite empty placeholders)

The `features/auth/` skeleton already exists with empty stub `index.ts` files (~15-20 bytes each). After the move we overwrite them with explicit named re-exports:

| Path | Content |
|---|---|
| `apps/web/src/features/auth/components/index.ts` | `export { default as LoginForm } from './LoginForm'` + 2 more |
| `apps/web/src/features/auth/pages/index.ts` | `export { default as ChangePasswordPage } from './ChangePasswordPage'` + 1 more |
| `apps/web/src/features/auth/services/index.ts` | `export * from './authService'` |
| `apps/web/src/features/auth/context/index.ts` | `export * from './AuthContext'`, `export * from './AuthContextInstance'`, `export * from './AuthContextType'` |
| `apps/web/src/features/auth/hooks/index.ts` | `export * from './useAuth'` |

**Top-level `features/auth/index.ts` already re-exports `./components`, `./pages`, etc.** — we leave it as-is.

### Files to LEAVE in place

- `apps/web/src/context/ThemeContext.tsx` — not auth; will move with layouts in L4.11
- `apps/web/src/context/` directory — not deleted (still hosts `ThemeContext.tsx`)
- `apps/web/src/components/auth/` — directory becomes empty after the 3 form moves; **leave the empty directory** (L4.11 cleanup deletes orphaned empty dirs project-wide)
- `apps/web/src/services/` — many other services live here, untouched in this PR
- `apps/web/src/hooks/` — many other hooks live here, untouched in this PR
- `apps/web/src/pages/` — many other pages live here, untouched in this PR
- `apps/web/tests/e2e/auth.test.js` — Playwright test only references API routes (`/api/v1/auth/...`), not source paths — no edit needed

### Consumer files (external) — 21 files with import updates

Verified via `grep` over `apps/web/src/`:

1. `App.tsx` — 5 imports (LoginForm, AuthProvider, useAuth, ChangePasswordPage, ResetPasswordPage)
2. `components/notifications/NotificationsBell.tsx` — useAuth
3. `components/modals/DatosFamiliaresModal.tsx` — useAuth
4. `components/modals/DatosAcademicosModal.tsx` — useAuth
5. `components/modals/DatosLaboralesModal.tsx` — useAuth
6. `components/modals/DatosPersonalesModal.tsx` — useAuth
7. `components/layout/Header.tsx` — useAuth
8. `components/layout/Sidebar.tsx` — useAuth + Module from authService (2)
9. `hooks/useEmployeePermissions.ts` — useAuth
10. `hooks/useMenu.ts` — authService + Module (1 import line)
11. `pages/Dashboard.tsx` — useAuth
12. `pages/admin/AdminDashboard.tsx` — useAuth
13. `pages/empleados/DatosPersonalesPage.tsx` — useAuth
14. `pages/empleados/EmpleadosListPage.tsx` — useAuth
15. `pages/legajo/LegajoPage.tsx` — useAuth
16. `pages/vacaciones/VacacionesManagementPage.tsx` — useAuth
17. `pages/vacaciones/SolicitudesPage.tsx` — useAuth
18. `pages/vacaciones/ReportesPage.tsx` — useAuth
19. `pages/vacaciones/PeriodosPage.tsx` — useAuth
20. `pages/vacaciones/NuevaSolicitudPage.tsx` — useAuth
21. `pages/vacaciones/ConfiguracionPage.tsx` — useAuth

### Consumer files (internal to moved set) — 5 files with import updates after move

These are imports inside the moved files themselves. They use `@/...` aliases that get rewritten by the same Python script:

- `features/auth/components/LoginForm.tsx` — `@/hooks/useAuth` → `@/features/auth/hooks/useAuth`
- `features/auth/components/ChangePasswordForm.tsx` — same
- `features/auth/components/ResetPasswordForm.tsx` — same
- `features/auth/context/AuthContext.tsx` — `@/services/authService` → `@/features/auth/services/authService`
- `features/auth/context/AuthContextType.ts` — same
- `features/auth/hooks/useAuth.ts` — `@/context/AuthContextInstance` → `@/features/auth/context/AuthContextInstance`
- `features/auth/pages/ChangePasswordPage.tsx` — `@/components/auth/ChangePasswordForm` → `@/features/auth/components/ChangePasswordForm`
- `features/auth/pages/ResetPasswordPage.tsx` — `@/components/auth/ResetPasswordForm` → `@/features/auth/components/ResetPasswordForm`

**Relative imports inside moved files (UNCHANGED):**
- `AuthContext.tsx` — `./AuthContextInstance`, `./AuthContextType` (same dir, still valid post-move)
- `AuthContextInstance.ts` — `./AuthContextType` (same dir, still valid post-move)

### Total import-update sites: ~30 (Python script handles all)

---

## Mapping table (canonical, length-ordered)

The Python script processes mappings serially. To prevent prefix collisions (e.g., `@/context/AuthContext` is a prefix of `@/context/AuthContextInstance`), longer/more-specific patterns MUST run BEFORE shorter ones:

| # | OLD path (`from '...'`) | NEW path |
|---:|---|---|
| 1 | `@/components/auth/ChangePasswordForm` | `@/features/auth/components/ChangePasswordForm` |
| 2 | `@/components/auth/ResetPasswordForm` | `@/features/auth/components/ResetPasswordForm` |
| 3 | `@/context/AuthContextInstance` | `@/features/auth/context/AuthContextInstance` |
| 4 | `@/context/AuthContextType` | `@/features/auth/context/AuthContextType` |
| 5 | `@/components/auth/LoginForm` | `@/features/auth/components/LoginForm` |
| 6 | `@/pages/ChangePasswordPage` | `@/features/auth/pages/ChangePasswordPage` |
| 7 | `@/pages/ResetPasswordPage` | `@/features/auth/pages/ResetPasswordPage` |
| 8 | `@/services/authService` | `@/features/auth/services/authService` |
| 9 | `@/context/AuthContext` | `@/features/auth/context/AuthContext` |
| 10 | `@/hooks/useAuth` | `@/features/auth/hooks/useAuth` |

**Justification of order:** entries 3 (`AuthContextInstance`) and 4 (`AuthContextType`) MUST run before entry 9 (`AuthContext`) because the latter is a string prefix of the former two. All other entries are non-prefixed (their substrings don't collide).

**Per LR22:** `replace_all` style ops can collapse fallbacks — none expected here because every OLD/NEW pair is a clean rename (not a deletion or merge), but verify `git diff` after the script.

---

## Pre-flight (before any commit)

Verify clean state and capture baselines.

- [ ] **Step 1: Confirm clean working tree on master**

```bash
cd D:/VYNTIA && git status --short && git branch --show-current
```

Expected: empty output (clean), branch `master`.

- [ ] **Step 2: Capture pre-L4.2 build/test/lint baselines**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -10
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | tail -10
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | tail -5
```

Expected (baseline from L4.1 merge):
- build: `✓ built in <N>s`, no errors
- vitest: `Test Files 2 passed (3)`, `Tests 7 passed (7)`, 1 file load failure (Playwright captured — pre-existing)
- tsc: 0 errors
- lint: stable problem count (note exact number for delta comparison)

Record the exact lint problem count — call it `LINT_BASELINE` for Step 19.

- [ ] **Step 3: Capture pytest baseline**

```bash
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -5
```

Expected: `161 passed, 8 failed, 3 skipped` (the L3.10.2-improved baseline).

---

## Task 1: Create branch + commit plan

**Files:**
- Modify: none (branch creation only)

- [ ] **Step 1: Create and check out the branch**

```bash
cd D:/VYNTIA && git checkout -b vyntia/L4.2-feature-auth
```

Expected: `Switched to a new branch 'vyntia/L4.2-feature-auth'`.

- [ ] **Step 2: Stage and commit the plan**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.2-feature-auth.md
git commit -m "$(cat <<'EOF'
docs(L4.2): add auth feature migration plan

Plan for moving auth slice (3 forms + 2 pages + service + 3 context files
+ useAuth hook) from flat layout into features/auth/ bounded context.
Mirror L4.1 three-commit pattern (plan, moves, imports). 21 external
consumers + 8 internal import updates via Python script. ThemeContext
stays in context/ for L4.11.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `1 file changed, NNN insertions(+)`.

---

## Task 2: Move all auth files via `git mv` (no body changes)

**Goal:** Single atomic commit with 100% rename detection. Body of every file is unchanged so git records moves as renames, preserving blame history.

**Files:**
- Move: 10 files per the table above

- [ ] **Step 1: Move the 3 form components**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/auth/LoginForm.tsx          apps/web/src/features/auth/components/LoginForm.tsx
git mv apps/web/src/components/auth/ChangePasswordForm.tsx apps/web/src/features/auth/components/ChangePasswordForm.tsx
git mv apps/web/src/components/auth/ResetPasswordForm.tsx  apps/web/src/features/auth/components/ResetPasswordForm.tsx
```

- [ ] **Step 2: Move the 3 context files**

```bash
cd D:/VYNTIA
git mv apps/web/src/context/AuthContext.tsx          apps/web/src/features/auth/context/AuthContext.tsx
git mv apps/web/src/context/AuthContextInstance.ts   apps/web/src/features/auth/context/AuthContextInstance.ts
git mv apps/web/src/context/AuthContextType.ts       apps/web/src/features/auth/context/AuthContextType.ts
```

- [ ] **Step 3: Move the hook**

```bash
cd D:/VYNTIA
git mv apps/web/src/hooks/useAuth.ts apps/web/src/features/auth/hooks/useAuth.ts
```

- [ ] **Step 4: Move the service**

```bash
cd D:/VYNTIA
git mv apps/web/src/services/authService.ts apps/web/src/features/auth/services/authService.ts
```

- [ ] **Step 5: Move the 2 pages**

```bash
cd D:/VYNTIA
git mv apps/web/src/pages/ChangePasswordPage.tsx apps/web/src/features/auth/pages/ChangePasswordPage.tsx
git mv apps/web/src/pages/ResetPasswordPage.tsx  apps/web/src/features/auth/pages/ResetPasswordPage.tsx
```

- [ ] **Step 6: Verify rename detection (target ≥ 95%)**

```bash
cd D:/VYNTIA && git status && git diff --stat --staged
```

Expected: 10 entries shown as renames (`renamed:` lines in `git status`); `git diff --stat --staged` shows 10 files with 0 line changes (pure renames).

If any file shows as `deleted + new file` instead of `renamed`, ABORT — git failed to detect the rename. Investigate before proceeding.

- [ ] **Step 7: Commit the moves**

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.2): move auth files to features/auth/ (rename only)

git mv 10 files into features/auth/{components,context,hooks,pages,services}/
with file bodies 100% unchanged. Rename detection ≥95% expected — preserves
blame history. Imports updated in next commit (separate atomic step per
L4.1 LR31 lesson: mixing moves + edits drops similarity).

Files moved:
- components/auth/{LoginForm,ChangePasswordForm,ResetPasswordForm}.tsx
  → features/auth/components/
- context/{AuthContext,AuthContextInstance,AuthContextType}.{tsx,ts}
  → features/auth/context/
- hooks/useAuth.ts → features/auth/hooks/
- services/authService.ts → features/auth/services/
- pages/{ChangePasswordPage,ResetPasswordPage}.tsx → features/auth/pages/

ThemeContext.tsx stays in context/ (not auth — L4.11 scope).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: `10 files changed, 0 insertions(+), 0 deletions(-)`.

- [ ] **Step 8: Sanity check — build will fail at this point**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -20
```

Expected: TypeScript errors about missing modules (`Cannot find module '@/components/auth/LoginForm'` etc.). This is **expected and intentional** — the next commit fixes them. If tsc PASSES at this point, something is wrong (perhaps the renames didn't happen).

---

## Task 3: Rewrite import paths via Python script + populate barrels

**Goal:** Single atomic commit that fixes every broken import (internal + external) and populates the 5 feature subdir barrels with named exports.

**Files:**
- Modify: ~26 .ts/.tsx files (import path updates)
- Modify: 5 `features/auth/*/index.ts` barrel files (overwrite stubs)

- [ ] **Step 1: Write the Python rewrite script**

Create `D:/VYNTIA/scripts/L4.2-rewrite-imports.py`:

```python
"""L4.2 import path rewriter — auth feature migration.

Walks apps/web/src/ + apps/web/tests/, applies 10 OLD→NEW prefix mappings to
every .ts/.tsx file, prints a per-file edit count.

Mappings are length-ordered DESCENDING so that longer prefixes are processed
before shorter ones (avoids @/context/AuthContext catching @/context/AuthContextInstance).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "apps" / "web"
SCAN_DIRS = [ROOT / "src", ROOT / "tests"]
EXTS = {".ts", ".tsx"}

# OLD → NEW. Length-DESC order is critical — see plan § Mapping table.
MAPPINGS = [
    ("@/components/auth/ChangePasswordForm", "@/features/auth/components/ChangePasswordForm"),
    ("@/components/auth/ResetPasswordForm",  "@/features/auth/components/ResetPasswordForm"),
    ("@/context/AuthContextInstance",        "@/features/auth/context/AuthContextInstance"),
    ("@/context/AuthContextType",            "@/features/auth/context/AuthContextType"),
    ("@/components/auth/LoginForm",          "@/features/auth/components/LoginForm"),
    ("@/pages/ChangePasswordPage",           "@/features/auth/pages/ChangePasswordPage"),
    ("@/pages/ResetPasswordPage",            "@/features/auth/pages/ResetPasswordPage"),
    ("@/services/authService",               "@/features/auth/services/authService"),
    ("@/context/AuthContext",                "@/features/auth/context/AuthContext"),
    ("@/hooks/useAuth",                      "@/features/auth/hooks/useAuth"),
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
cd D:/VYNTIA && python scripts/L4.2-rewrite-imports.py
```

Expected output: ~26 lines of `updated: ...` followed by `Total files updated: 26` (give or take 2). Should include `App.tsx`, all 10 moved files, all 21 listed external consumers.

- [ ] **Step 3: Verify no stale OLD paths remain**

```bash
cd D:/VYNTIA && grep -rn "@/components/auth/\|@/context/AuthContext\|@/hooks/useAuth\|@/services/authService\|@/pages/ChangePasswordPage\|@/pages/ResetPasswordPage" apps/web/src/ apps/web/tests/ 2>/dev/null
```

Expected: empty output (zero matches). If any line is returned, those imports were missed — investigate (likely a typo in the script or a path not in the mapping table).

- [ ] **Step 4: Verify NEW paths exist (sanity)**

```bash
cd D:/VYNTIA && grep -rn "@/features/auth/" apps/web/src/App.tsx | head -10
```

Expected: 5 lines showing App.tsx now imports from `@/features/auth/components/LoginForm`, `@/features/auth/context/AuthContext`, `@/features/auth/hooks/useAuth`, `@/features/auth/pages/ChangePasswordPage`, `@/features/auth/pages/ResetPasswordPage`.

- [ ] **Step 5: Populate the 5 feature subdir barrels**

Overwrite each stub `index.ts` with explicit exports.

Write `apps/web/src/features/auth/components/index.ts`:

```typescript
export { default as LoginForm } from './LoginForm'
export { default as ChangePasswordForm } from './ChangePasswordForm'
export { default as ResetPasswordForm } from './ResetPasswordForm'
```

Write `apps/web/src/features/auth/context/index.ts`:

```typescript
export * from './AuthContext'
export * from './AuthContextInstance'
export * from './AuthContextType'
```

Write `apps/web/src/features/auth/hooks/index.ts`:

```typescript
export * from './useAuth'
```

Write `apps/web/src/features/auth/pages/index.ts`:

```typescript
export { default as ChangePasswordPage } from './ChangePasswordPage'
export { default as ResetPasswordPage } from './ResetPasswordPage'
```

Write `apps/web/src/features/auth/services/index.ts`:

```typescript
export * from './authService'
```

**Note:** `features/auth/index.ts` and `features/auth/types/index.ts` are left as-is (already correct stubs).

- [ ] **Step 6: TypeScript strict check**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -10
```

Expected: 0 errors. If errors appear, read them carefully — they will name the bad import path. Common fixes:
- A consumer file Python missed → add the file to a re-scan
- A circular re-export → an `export *` collision; switch to named export

- [ ] **Step 7: Build check**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -10
```

Expected: `✓ built in <N>s`, no errors.

- [ ] **Step 8: Vitest check**

```bash
cd D:/VYNTIA/apps/web && npx vitest run 2>&1 | tail -10
```

Expected: `Test Files 2 passed (3)`, `Tests 7 passed (7)`, 1 file load failure (Playwright pre-existing).

- [ ] **Step 9: Lint delta check**

```bash
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | tail -5
```

Expected: problem count equals `LINT_BASELINE` from Pre-flight Step 2 (delta = 0).

- [ ] **Step 10: pytest baseline check**

```bash
source D:/VYNTIA/.venv/Scripts/activate && cd D:/VYNTIA/apps/api && pytest 2>&1 | tail -5
```

Expected: `161 passed, 8 failed, 3 skipped` (frontend changes shouldn't affect backend, but verify).

- [ ] **Step 11: Delete the throwaway script**

The script was a one-shot tool, not a reusable utility. Delete it before committing.

```bash
cd D:/VYNTIA && rm scripts/L4.2-rewrite-imports.py
```

- [ ] **Step 12: Commit imports + barrels**

```bash
cd D:/VYNTIA && git add -A && git status --short
```

Expected: ~26 modified `.ts`/`.tsx` files + 5 modified `features/auth/*/index.ts` barrels. NO `scripts/L4.2-rewrite-imports.py` (already deleted in Step 11).

```bash
cd D:/VYNTIA && git commit -m "$(cat <<'EOF'
chore(L4.2): update consumer imports + populate features/auth/ barrels

Bulk import rewrite via Python script (single-pass, length-DESC mapping
order to avoid @/context/AuthContext catching AuthContextInstance/Type).
~30 import sites across 26 files redirected to @/features/auth/* aliases.

Internal moves (relative imports preserved):
- features/auth/context/{AuthContext,AuthContextInstance}: ./AuthContextX
  remain valid (same dir post-move)

External consumers updated (21 files):
- App.tsx (5 imports), 4 modals, layout/{Header,Sidebar}, NotificationsBell,
  hooks/{useEmployeePermissions,useMenu}, 9 pages

Internal import updates inside moved files (8 sites):
- 3 forms: @/hooks/useAuth → @/features/auth/hooks/useAuth
- AuthContext.tsx + AuthContextType.ts: @/services/authService → @/features/auth/services/authService
- useAuth.ts: @/context/AuthContextInstance → @/features/auth/context/AuthContextInstance
- 2 pages: @/components/auth/X → @/features/auth/components/X

Barrels populated:
- features/auth/{components,pages}/index.ts: named default exports
- features/auth/{context,hooks,services}/index.ts: export * from './X'

Verified:
- npx tsc --noEmit: 0 errors
- npm run build: clean
- vitest: 7 passed (1 file load failure pre-existing)
- npm run lint: 0 net new (matches LINT_BASELINE)
- pytest: 161/8/3 baseline preserved

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: ~31 files changed (26 imports + 5 barrels).

---

## Task 4: Smoke test — manual UI walkthrough

Per LR26 (TS strict doesn't catch `any`-typed runtime breaks), build success ≠ working app.

**Files:** none

- [ ] **Step 1: Start dev server**

```bash
cd D:/VYNTIA/apps/web && npm run dev
```

Wait for `VITE v… ready in <N> ms` and the local URL (typically `http://localhost:5173/`).

- [ ] **Step 2: Verify the auth flow paths render**

Open the dev URL in a browser and check:

1. `/` (root, unauthenticated) → renders `LoginForm` (the moved component)
2. Submit valid credentials → lands on Dashboard (verifies `AuthProvider` wired correctly)
3. Visit `/cambiar-password` → renders `ChangePasswordPage` → shows `ChangePasswordForm` with the 3 password fields
4. Sidebar/Header render the user menu (verifies `useAuth` hook works in layout)
5. Open browser devtools console → no red errors related to module resolution

**If backend is not running** (or the local PostgreSQL UnicodeDecodeError reappears), the login submit will fail with a network error — this is acceptable. The criterion is that the FORM renders and React doesn't crash; backend connectivity is out of scope for L4.2.

- [ ] **Step 3: Stop the dev server**

`Ctrl+C` in the terminal running `npm run dev`.

- [ ] **Step 4: No commit needed for smoke test**

Smoke test does not produce code changes. If a defect is found, return to Task 3 to fix and amend or add a follow-up commit.

---

## Task 5: PAUSE — request user authorization to merge

**Files:** none

- [ ] **Step 1: Push branch state for review (optional, no remote in solo workflow)**

```bash
cd D:/VYNTIA && git log --oneline master..vyntia/L4.2-feature-auth
```

Expected: 3 commits on the branch (plan, moves, imports/barrels).

- [ ] **Step 2: Display final branch summary**

```bash
cd D:/VYNTIA && git diff --stat master..vyntia/L4.2-feature-auth | tail -10
```

Expected: ~36 files changed (10 renames + 26 modifications + 5 barrels). The renames show as 0+/0- per file; modifications show actual line deltas.

- [ ] **Step 3: ASK USER: "L4.2 ready to merge?"**

Wait for explicit user authorization before Task 6. Do NOT auto-merge.

---

## Task 6: Merge to master with `--no-ff` (only after user approval)

**Files:** none

- [ ] **Step 1: Switch to master and merge**

```bash
cd D:/VYNTIA && git checkout master && git merge --no-ff vyntia/L4.2-feature-auth -m "Merge L4.2: features/auth/ migration

Auth slice consolidated under features/auth/ — 3 forms + 2 pages + service +
3 context files + useAuth hook + 5 barrels. 21 external consumers + 8
internal imports redirected to @/features/auth/* aliases. ThemeContext stays
in context/ for L4.11. Baselines preserved: pytest 161/8/3, vitest 7,
build clean, tsc 0 errors, lint delta 0."
```

Expected: `Merge made by the 'recursive' strategy.` plus file change summary.

- [ ] **Step 2: Verify merge integrity**

```bash
cd D:/VYNTIA && git log --oneline -5
```

Expected: top entry is the merge commit; 3 prior entries are the L4.2 sub-commits (or visible via `--graph`).

- [ ] **Step 3: Update L4 master roadmap status row**

Edit `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md`. Find the L4.2 row in the sub-PR table (line ~146). Change:

```
| **L4.2** | auth feature migration | `vyntia/L4.2-feature-auth` | Move ... ~30-40 import updates | ~12 | Bajo | L4.1 | ⏳ NEXT |
```

To:

```
| **L4.2** | auth feature migration | `vyntia/L4.2-feature-auth` | Moved 10 files (3 forms + 2 pages + service + 3 context + useAuth) → features/auth/. 5 subdir barrels populated. ~30 import updates across 26 files via Python script (length-DESC mapping). ThemeContext.tsx stays in context/ for L4.11. 3 atomic commits. Pytest 161/8/3 + vitest 7 + build clean + tsc 0 + lint delta 0 baselines preservados. | ~12 | Bajo | L4.1 | ✅ merged `<HASH>` |
```

Replace `<HASH>` with the actual merge commit short hash from Step 2.

Mark L4.3 as `⏳ NEXT` (was just `⏳`).

- [ ] **Step 4: Commit the roadmap update**

```bash
cd D:/VYNTIA && git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md
git commit -m "$(cat <<'EOF'
docs(L4.2): mark L4.2 merged — auth feature consolidated

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
cd D:/VYNTIA && git branch -d vyntia/L4.2-feature-auth
```

Expected: `Deleted branch vyntia/L4.2-feature-auth (was <HASH>).`

(`-d` is safe — refuses if unmerged. Use `-D` only if you're sure.)

---

## Definition of done

- [ ] `apps/web/src/features/auth/` contains: `components/{LoginForm,ChangePasswordForm,ResetPasswordForm}.tsx`, `pages/{ChangePasswordPage,ResetPasswordPage}.tsx`, `context/{AuthContext,AuthContextInstance,AuthContextType}.{tsx,ts}`, `hooks/useAuth.ts`, `services/authService.ts`, populated barrels in 5 subdirs
- [ ] `apps/web/src/components/auth/` is an empty directory (deletion deferred to L4.11)
- [ ] `apps/web/src/context/` contains only `ThemeContext.tsx`
- [ ] `apps/web/src/hooks/useAuth.ts` no longer exists
- [ ] `apps/web/src/services/authService.ts` no longer exists
- [ ] `apps/web/src/pages/ChangePasswordPage.tsx` no longer exists
- [ ] `apps/web/src/pages/ResetPasswordPage.tsx` no longer exists
- [ ] `grep -rn "@/components/auth/\|@/context/AuthContext\|@/hooks/useAuth\|@/services/authService\|@/pages/ChangePasswordPage\|@/pages/ResetPasswordPage" apps/web/src/ apps/web/tests/` returns 0 lines
- [ ] `npx tsc --noEmit -p tsconfig.app.json` returns 0 errors
- [ ] `npm run build` succeeds
- [ ] `npx vitest run` shows 7 tests passed
- [ ] `npm run lint` problem count equals pre-L4.2 baseline (delta = 0)
- [ ] `pytest` shows 161 passed / 8 failed / 3 skipped
- [ ] Manual smoke: dev server, login form renders, ChangePasswordPage renders, no console errors
- [ ] Branch `vyntia/L4.2-feature-auth` merged to master with `--no-ff`
- [ ] Master roadmap row for L4.2 updated to ✅ with merge hash
- [ ] L4.3 marked as ⏳ NEXT in the roadmap

---

## Risk register (L4.2-specific)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `git mv` rename detection drops below 95% | Low | Med | Move + commit in dedicated commit, NO body changes (Task 2). Verify in Step 6. |
| Python script misses a consumer file (typo or new file) | Low | Med | Step 3 grep verification — zero stale OLD paths must remain. |
| Prefix collision: `@/context/AuthContext` catches `AuthContextInstance` | Low | High | Mappings are length-DESC ordered. AuthContextInstance/Type are processed BEFORE AuthContext. |
| LR22 collapse: `replace_all` simplifies a fallback to self-tautology | Very Low | Low | No fallback patterns expected here (clean renames, not merges). Verify via `git diff` before commit. |
| LR26 silent runtime break: `any`-typed consumer compiles but fails at runtime | Med | Med | Manual smoke test in Task 4 — actually load the login page in a browser. |
| LR27 Vite esbuild not strict: `npm run build` passes even with type errors | Med | Low | Step 6 explicitly runs `npx tsc --noEmit -p tsconfig.app.json`, NOT just `npm run build`. |
| Empty barrel `export *` causes circular re-export warning | Very Low | Low | Each barrel re-exports a single co-located file; no cycles possible. |
| Backend pytest regresses (no backend changes expected) | Very Low | Low | Step 10 verification. If it fails, the failure is unrelated to L4.2 — investigate as a separate issue. |

---

## Lessons learned to record after merge (LR32+)

Add to `active_subproject.md` under L4.2 row, depending on what surfaces:

- LR32 candidate: any new auth-specific patterns discovered during the rewrite (e.g., `localStorage` keys hardcoded in `authService.ts` that should now be feature-scoped — defer to a future cleanup if found)
- LR33 candidate: barrel `export *` from a `.tsx` (with React component default export) needs `export { default } from './X'` not `export *` — verify if any subdir mixes named + default exports

If neither surfaces, no new lessons are recorded — that's fine.

---

## Self-review

**1. Spec coverage:** Every file in the L4.2 row of the master roadmap (3 forms + 2 pages + service + AuthContext + useAuth + App.tsx routes) is covered by Task 2's `git mv` list and Task 3's Python script mapping. Bonus: AuthContextInstance + AuthContextType (sibling files of AuthContext) and barrel population are covered — these are needed for completeness even though the roadmap row only named "AuthContext.tsx". ThemeContext correctly excluded.

**2. Placeholder scan:** No "TBD", "TODO" (other than naming the candidate LR codes which is intentional optionality), or "implement later" tokens. Every step has an exact command or exact code.

**3. Type consistency:** Function/method names referenced (`AuthProvider`, `useAuth`, `LoginForm`, `ChangePasswordForm`, `ResetPasswordForm`, `ChangePasswordPage`, `ResetPasswordPage`) are exactly the symbol names exported from the moved files (verified by reading each file in the inventory phase).
