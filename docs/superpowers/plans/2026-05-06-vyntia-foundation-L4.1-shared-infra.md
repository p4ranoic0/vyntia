# VYNTIA Foundation L4.1 — shared/ Infrastructure Consolidation

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended) to implement task-by-task.

**Goal:** Consolidate cross-feature infrastructure (axios client, React Query setup, normalizers, shadcn primitives, brand components, generic hooks, utilities) under `apps/web/src/shared/`. Foundational refactor — all subsequent L4.X sub-PRs depend on this.

**Architecture:** File moves only — zero behavior changes. Use `git mv` to preserve rename detection. Update import paths in two phases: (1) move files keeping names; (2) update consumer imports via `replace_all` per file. Existing unused `shared/` scaffolding (DocumentStatus, EmpleadoCard, EstadoBadge, StatCard, useToast stub, etc.) is deleted first since it was never adopted.

**Tech Stack:** TypeScript 5 + React 18 + Vite. Path alias `@/* → ./src/*` already configured (no tsconfig changes needed).

**Spec source:** `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md` § L4.1 + § D5.

**Pre-conditions:**
- Branch `master` clean at HEAD = `b58de617 docs(L4): add master roadmap for frontend reorganization`
- Backend pytest baseline: 161 passed, 8 failed, 3 skipped
- Frontend `npm run build` clean, vitest 7 passed (1 file load failure pre-existing)

**Scope:**
- Delete unused `shared/` stub files (never imported except by broken example files)
- Move `lib/api.ts`, `lib/queryClient.ts`, `lib/errorUtils.ts`, `services/normalizers/apiNormalizers.ts` → `shared/api/`
- Move `components/ui/*` (28 shadcn primitives) → `shared/ui/*`
- Move `components/brand/*` (VyntiaLogo, VyntiaWordmark) → `shared/ui/brand/*`
- Move `components/common/*` (DataTable, LoadingX, ProfileImage, DocumentViewer) → `shared/components/*`
- Move `hooks/{useDebounce, use-toast, useAnimations, useScrolled}.ts` → `shared/hooks/*`
- Move `utils/{cookieUtils, iconMapping}.ts` → `shared/utils/*`
- Move `lib/utils.ts` (shadcn `cn` helper) → `shared/utils/cn.ts`
- Move `lib/design-tokens.ts` → `shared/utils/design-tokens.ts`
- Update ~600+ consumer imports
- Add `shared/api/index.ts` barrel re-exports

**Out of scope:**
- `hooks/{useApi, useApi-deprecated, useAuth, useMenu, useEmployeePermissions, useRemuneraciones}` — these are feature-tied, migrate in L4.2-L4.10
- `services/X.ts` (the 13 service files) — migrate in respective L4.X sub-PRs
- `pages/`, `features/` reorganization — L4.2 onwards
- `components/{auth,empleados,modals,users,vacaciones,layout,notifications,areas}/*` — L4.2 onwards
- `utils/autoLogin.js` — legacy JS file, decide later (probably delete in L4.11 cleanup)

---

## File Structure (post-L4.1 target)

```
apps/web/src/shared/
├── api/
│   ├── api.ts              ← from lib/api.ts (axios client + helpers)
│   ├── queryClient.ts      ← from lib/queryClient.ts
│   ├── errorUtils.ts       ← from lib/errorUtils.ts
│   ├── apiNormalizers.ts   ← from services/normalizers/apiNormalizers.ts
│   └── index.ts            ← NEW barrel: re-exports apiClient, queryClient, getErrorMessage, normalizers
├── ui/
│   ├── accordion.tsx, alert.tsx, ... (28 shadcn files)
│   ├── use-toast.ts
│   └── brand/
│       ├── VyntiaLogo.tsx
│       └── VyntiaWordmark.tsx
├── components/
│   ├── DataTable.tsx
│   ├── DocumentViewer.tsx
│   ├── LoadingButton.tsx
│   ├── LoadingDemo.tsx
│   ├── LoadingPage.tsx
│   ├── LoadingSkeleton.tsx
│   ├── LoadingSpinner.tsx
│   ├── ProfileImage.tsx
│   ├── useLoading.ts (+ .tsx)
│   ├── useLoadingWithDelay.ts (+ .tsx)
│   └── index.ts (existing barrel — review and update)
├── hooks/
│   ├── useDebounce.ts        ← from hooks/useDebounce.ts (overwrites stub)
│   ├── use-toast.ts          ← from hooks/use-toast.ts (re-export shim → repoint to shared/ui)
│   ├── useAnimations.ts      ← from hooks/useAnimations.ts
│   └── useScrolled.ts        ← from hooks/useScrolled.ts
├── utils/
│   ├── cookieUtils.ts        ← from utils/cookieUtils.ts
│   ├── iconMapping.ts        ← from utils/iconMapping.ts
│   ├── cn.ts                 ← from lib/utils.ts (shadcn cn helper)
│   └── design-tokens.ts      ← from lib/design-tokens.ts
└── types/, components/index.ts (existing scaffolding — keep; may be refactored in L4.11)
```

After L4.1, these directories are emptied or shrunk:
- `lib/` — empty (all 5 files moved)
- `components/ui/` — empty
- `components/brand/` — empty
- `components/common/` — empty
- `hooks/` — keeps useApi, useApi-deprecated, useAuth, useMenu, useEmployeePermissions, useRemuneraciones (feature-tied)
- `utils/` — keeps autoLogin.js (legacy)
- `services/normalizers/` — empty (delete dir)

---

## Definition of Done

- [ ] All target files moved per inventory above
- [ ] `shared/api/index.ts` barrel created
- [ ] All consumer imports updated (`@/lib/api` → `@/shared/api/api`, `@/components/ui/X` → `@/shared/ui/X`, `@/lib/utils` → `@/shared/utils/cn`, etc.)
- [ ] `npm run build` clean
- [ ] `npx tsc --noEmit -p tsconfig.app.json` clean except pre-existing INTEGRATION_EXAMPLE/REACT_QUERY_EXAMPLE/BlankEnum
- [ ] `npm test -- --run` 7 passed
- [ ] pytest 161/8/3 preserved (no backend changes)
- [ ] `npm run lint` 0 net new errors
- [ ] Branch `vyntia/L4.1-shared-infra` merged with `--no-ff`
- [ ] Master roadmap updated: L4.1 ✅, L4.2 NEXT
- [ ] Memory updated

---

## Task 1: Pre-flight + branch

- [ ] **Step 1: Branch + baselines**

```bash
cd D:/VYNTIA
git status --short
git checkout -b vyntia/L4.1-shared-infra
cd apps/web && npm run build 2>&1 | tail -3 && npm test -- --run 2>&1 | grep -E "Tests" | tail -2 && cd D:/VYNTIA
```

Expected: clean working tree, branch created, build success, vitest 7 passed.

- [ ] **Step 2: Snapshot import counts**

```bash
cd D:/VYNTIA/apps/web/src
echo "=== imports from @/components/ui/ ==="
grep -rE "from ['\"]@/components/ui/" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/lib/utils ==="
grep -rE "from ['\"]@/lib/utils['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/lib/api ==="
grep -rE "from ['\"]@/lib/api['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/lib/queryClient ==="
grep -rE "from ['\"]@/lib/queryClient['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/lib/errorUtils ==="
grep -rE "from ['\"]@/lib/errorUtils['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/services/normalizers/ ==="
grep -rE "from ['\"]@/services/normalizers/" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/components/brand/ ==="
grep -rE "from ['\"]@/components/brand/" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/components/common ==="
grep -rE "from ['\"]@/components/common" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/hooks/use-toast ==="
grep -rE "from ['\"]@/hooks/use-toast['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/hooks/useDebounce ==="
grep -rE "from ['\"]@/hooks/useDebounce['\"]" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/utils/ ==="
grep -rE "from ['\"]@/utils/" --include='*.ts' --include='*.tsx' | wc -l
echo "=== imports from @/lib/design-tokens ==="
grep -rE "from ['\"]@/lib/design-tokens['\"]" --include='*.ts' --include='*.tsx' | wc -l
cd D:/VYNTIA
```

Document the baseline counts for verification post-PR.

---

## Task 2: Commit the plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.1-shared-infra.md
git commit -m "$(cat <<'EOF'
docs(L4.1): add shared infra consolidation plan

First sub-PR of L4 frontend reorg. File moves only (no behavior
changes) consolidating axios/React Query/shadcn/brand/generic hooks
under shared/. Existing unused shared/ scaffolding deleted.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Delete unused `shared/` scaffolding

The existing `shared/` files were never adopted (only referenced by broken example files `INTEGRATION_EXAMPLE.ts`, `REACT_QUERY_EXAMPLE.ts` which have parse errors and are deferred deletes for L4.5).

- [ ] **Step 1: List files to delete**

```bash
cd D:/VYNTIA/apps/web/src
ls -la shared/components/ shared/hooks/ shared/types/ shared/utils/
```

- [ ] **Step 2: Delete unused stubs**

```bash
cd D:/VYNTIA
git rm apps/web/src/shared/components/DocumentStatus.tsx
git rm apps/web/src/shared/components/EmpleadoCard.tsx
git rm apps/web/src/shared/components/EstadoBadge.tsx
git rm apps/web/src/shared/components/StatCard.tsx
git rm apps/web/src/shared/components/index.ts
git rm apps/web/src/shared/hooks/useDebounce.ts
git rm apps/web/src/shared/hooks/usePermission.ts
git rm apps/web/src/shared/hooks/useToast.ts
git rm apps/web/src/shared/hooks/index.ts
git rm apps/web/src/shared/types/index.ts
git rm apps/web/src/shared/utils/index.ts
git rm apps/web/src/shared/index.ts
```

- [ ] **Step 3: Verify build still clean**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && cd D:/VYNTIA
```

Expected: build success. The deleted files were never imported (except by broken example files).

- [ ] **Step 4: Don't commit yet** — bundle with file moves in next task.

---

## Task 4: Move files to `shared/`

Use `git mv` to preserve rename detection. Files keep their original names; barrel `index.ts` files are added later.

- [ ] **Step 1: Move shared/api/**

```bash
cd D:/VYNTIA
git mv apps/web/src/lib/api.ts                               apps/web/src/shared/api/api.ts
git mv apps/web/src/lib/queryClient.ts                       apps/web/src/shared/api/queryClient.ts
git mv apps/web/src/lib/errorUtils.ts                        apps/web/src/shared/api/errorUtils.ts
git mv apps/web/src/services/normalizers/apiNormalizers.ts   apps/web/src/shared/api/apiNormalizers.ts
```

- [ ] **Step 2: Move shared/ui/ (shadcn primitives)**

```bash
cd D:/VYNTIA
for f in accordion alert-dialog alert avatar badge button calendar card checkbox dialog dropdown-menu input label popover progress select separator sheet skeleton status-badge switch table tabs textarea toast toaster tooltip; do
  git mv "apps/web/src/components/ui/$f.tsx" "apps/web/src/shared/ui/$f.tsx"
done
git mv apps/web/src/components/ui/use-toast.ts apps/web/src/shared/ui/use-toast.ts
```

- [ ] **Step 3: Move shared/ui/brand/**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/brand/VyntiaLogo.tsx     apps/web/src/shared/ui/brand/VyntiaLogo.tsx
git mv apps/web/src/components/brand/VyntiaWordmark.tsx apps/web/src/shared/ui/brand/VyntiaWordmark.tsx
```

- [ ] **Step 4: Move shared/components/**

```bash
cd D:/VYNTIA
git mv apps/web/src/components/common/DataTable.tsx           apps/web/src/shared/components/DataTable.tsx
git mv apps/web/src/components/common/DocumentViewer.tsx       apps/web/src/shared/components/DocumentViewer.tsx
git mv apps/web/src/components/common/LoadingButton.tsx        apps/web/src/shared/components/LoadingButton.tsx
git mv apps/web/src/components/common/LoadingDemo.tsx          apps/web/src/shared/components/LoadingDemo.tsx
git mv apps/web/src/components/common/LoadingPage.tsx          apps/web/src/shared/components/LoadingPage.tsx
git mv apps/web/src/components/common/LoadingSkeleton.tsx      apps/web/src/shared/components/LoadingSkeleton.tsx
git mv apps/web/src/components/common/LoadingSpinner.tsx       apps/web/src/shared/components/LoadingSpinner.tsx
git mv apps/web/src/components/common/ProfileImage.tsx         apps/web/src/shared/components/ProfileImage.tsx
git mv apps/web/src/components/common/useLoading.ts            apps/web/src/shared/components/useLoading.ts
git mv apps/web/src/components/common/useLoading.tsx           apps/web/src/shared/components/useLoading.tsx
git mv apps/web/src/components/common/useLoadingWithDelay.ts   apps/web/src/shared/components/useLoadingWithDelay.ts
git mv apps/web/src/components/common/useLoadingWithDelay.tsx  apps/web/src/shared/components/useLoadingWithDelay.tsx
git mv apps/web/src/components/common/index.ts                 apps/web/src/shared/components/index.ts
```

- [ ] **Step 5: Move shared/hooks/**

```bash
cd D:/VYNTIA
git mv apps/web/src/hooks/useDebounce.ts   apps/web/src/shared/hooks/useDebounce.ts
git mv apps/web/src/hooks/use-toast.ts     apps/web/src/shared/hooks/use-toast.ts
git mv apps/web/src/hooks/useAnimations.ts apps/web/src/shared/hooks/useAnimations.ts
git mv apps/web/src/hooks/useScrolled.ts   apps/web/src/shared/hooks/useScrolled.ts
```

- [ ] **Step 6: Move shared/utils/**

```bash
cd D:/VYNTIA
git mv apps/web/src/utils/cookieUtils.ts    apps/web/src/shared/utils/cookieUtils.ts
git mv apps/web/src/utils/iconMapping.ts    apps/web/src/shared/utils/iconMapping.ts
git mv apps/web/src/lib/utils.ts            apps/web/src/shared/utils/cn.ts
git mv apps/web/src/lib/design-tokens.ts    apps/web/src/shared/utils/design-tokens.ts
```

- [ ] **Step 7: Verify status**

```bash
cd D:/VYNTIA && git status --short | head -40
```

Expected: ~50+ renames (plus 12 deletions from Task 3). Check for `R` (rename) prefix in git status.

```bash
cd D:/VYNTIA && git status | grep "renamed:" | wc -l
```

Expected: ~50.

---

## Task 5: Update imports — phase 1 (high-volume aliases)

Use `replace_all` per file. Order matters: do the most common patterns first.

- [ ] **Step 1: `@/components/ui/` → `@/shared/ui/`** (528 imports)

For each file with `@/components/ui/X` import, replace with `@/shared/ui/X`.

Strategy: walk all files in `apps/web/src/`, run `Edit replace_all` on the substring `@/components/ui/` → `@/shared/ui/`. Affects 50+ consumer files.

- [ ] **Step 2: `@/lib/utils` → `@/shared/utils/cn`** (50 imports)

Replace `from '@/lib/utils'` → `from '@/shared/utils/cn'`. Affects 50 files (mostly shadcn UI component internal imports + some pages using cn).

- [ ] **Step 3: `@/lib/api` → `@/shared/api/api`** (22 imports)

Replace `from '@/lib/api'` → `from '@/shared/api/api'`.

- [ ] **Step 4: `@/lib/queryClient` → `@/shared/api/queryClient`**

- [ ] **Step 5: `@/lib/errorUtils` → `@/shared/api/errorUtils`**

- [ ] **Step 6: `@/services/normalizers/apiNormalizers` → `@/shared/api/apiNormalizers`**

- [ ] **Step 7: `@/components/brand/` → `@/shared/ui/brand/`**

- [ ] **Step 8: `@/components/common/` → `@/shared/components/`**

Be aware of barrel imports like `from '@/components/common'` (no trailing path) which should also be updated.

- [ ] **Step 9: `@/hooks/use-toast` → `@/shared/hooks/use-toast`**

- [ ] **Step 10: `@/hooks/useDebounce` → `@/shared/hooks/useDebounce`**

- [ ] **Step 11: `@/hooks/useAnimations` → `@/shared/hooks/useAnimations`**

- [ ] **Step 12: `@/hooks/useScrolled` → `@/shared/hooks/useScrolled`**

- [ ] **Step 13: `@/utils/cookieUtils` → `@/shared/utils/cookieUtils`**

- [ ] **Step 14: `@/utils/iconMapping` → `@/shared/utils/iconMapping`**

- [ ] **Step 15: `@/lib/design-tokens` → `@/shared/utils/design-tokens`**

- [ ] **Step 16: Verify no stale imports**

```bash
cd D:/VYNTIA/apps/web/src
echo "=== should be 0: ==="
for pattern in "@/components/ui/" "@/components/brand/" "@/components/common" "@/lib/api" "@/lib/queryClient" "@/lib/errorUtils" "@/lib/utils" "@/lib/design-tokens" "@/hooks/use-toast" "@/hooks/useDebounce" "@/hooks/useAnimations" "@/hooks/useScrolled" "@/utils/cookieUtils" "@/utils/iconMapping" "@/services/normalizers/"; do
  count=$(grep -rE "from ['\"]$pattern" --include='*.ts' --include='*.tsx' | wc -l)
  echo "$pattern: $count"
done
cd D:/VYNTIA
```

Expected: all 0. Any non-zero indicates a missed import.

---

## Task 6: Internal imports inside moved files (cn, etc.)

Files moved into `shared/ui/` previously imported `@/lib/utils` for the `cn` helper. After Task 5 those are now `@/shared/utils/cn`. Verify:

```bash
cd D:/VYNTIA/apps/web/src/shared/ui
grep -rE "from ['\"]@/" --include='*.tsx' --include='*.ts' | grep -v "@/shared/" | head -10
```

Expected: empty. If any non-shared `@/X` imports remain inside `shared/ui`, fix them.

Same check for `shared/components/` and `shared/hooks/`:

```bash
cd D:/VYNTIA/apps/web/src
for d in shared/components shared/hooks shared/api; do
  echo "=== $d ==="
  grep -rE "from ['\"]@/" "$d" --include='*.tsx' --include='*.ts' 2>/dev/null | grep -v "from ['\"]@/shared/" | head -5
done
cd D:/VYNTIA
```

Fix any remaining cross-references that point outside `shared/`.

---

## Task 7: Add `shared/api/index.ts` barrel

```bash
cd D:/VYNTIA
cat > apps/web/src/shared/api/index.ts <<'EOF'
/**
 * Shared API infrastructure barrel.
 *
 * Re-exports the canonical axios client, React Query setup, normalizers,
 * and error utilities. Consumers should import from `@/shared/api`.
 */
export { apiClient } from "./api";
export type { ApiError } from "./api";
export { queryClient } from "./queryClient";
export { getErrorMessage } from "./errorUtils";
export {
  asArray,
  asRecord,
  extractCollection,
  normalizeEmployee,
  normalizeRole,
  normalizeSecurityRole,
  normalizeUser,
} from "./apiNormalizers";
EOF
```

(Inspect actual exports first by reading each file; adjust `export { ... }` lists accordingly. The barrel should match the actual public surface.)

---

## Task 8: Verify build + tests

- [ ] **Step 1: TS strict check**

```bash
cd D:/VYNTIA/apps/web
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "error TS" | grep -v "INTEGRATION_EXAMPLE\|REACT_QUERY_EXAMPLE\|BlankEnum" | head -30
```

Expected: empty or only pre-existing errors.

- [ ] **Step 2: Vite build**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -5
```

Expected: build success.

- [ ] **Step 3: Vitest**

```bash
cd D:/VYNTIA/apps/web && npm test -- --run 2>&1 | grep -E "Tests|Test Files" | tail -3
```

Expected: 7 passed (1 file load failure pre-existing).

- [ ] **Step 4: Lint delta**

```bash
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep -E "✖|problems" | tail -3
```

Expected: 636 problems (baseline) ± 0.

- [ ] **Step 5: pytest sanity check (no backend changes expected)**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api && PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3 && cd D:/VYNTIA
```

Expected: 161 passed, 8 failed, 3 skipped.

---

## Task 9: Commit moves + import updates

Two commits for clarity:

- [ ] **Commit 1: file moves + scaffolding cleanup**

```bash
cd D:/VYNTIA
git status --short | head -20
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L4.1): consolidate shared infrastructure (file moves)

Moves cross-feature infrastructure into shared/:
- shared/api/: axios client, React Query setup, normalizers, error utils
  (from lib/api.ts, lib/queryClient.ts, lib/errorUtils.ts,
  services/normalizers/apiNormalizers.ts)
- shared/ui/: 28 shadcn primitives + use-toast (from components/ui/)
- shared/ui/brand/: VyntiaLogo, VyntiaWordmark (from components/brand/)
- shared/components/: DataTable, LoadingX, ProfileImage, DocumentViewer
  (from components/common/)
- shared/hooks/: useDebounce, use-toast, useAnimations, useScrolled
  (from hooks/, generic non-feature hooks only)
- shared/utils/: cookieUtils, iconMapping, cn (shadcn helper),
  design-tokens (from utils/, lib/utils.ts, lib/design-tokens.ts)

Deletes 12 unused shared/ scaffolding files (DocumentStatus,
EmpleadoCard, EstadoBadge, StatCard, useToast stub, etc) — never
imported except by broken INTEGRATION_EXAMPLE.ts/REACT_QUERY_EXAMPLE.ts
files (deferred deletes for L4.5).

File body unchanged in all moves — git rename detection should be
~100%. Consumer imports updated in follow-up commit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Wait — to get clean rename detection, the file body must be UNCHANGED in this commit. But Task 5 will modify some files (the moved ones whose internal imports point to `@/lib/utils` etc). So **Step 7 of Task 5 (internal imports)** must happen in the imports-update commit, not the moves commit.

Strategy:
1. Commit 1 = git mv only (no edits to moved files) → preserves rename detection
2. Commit 2 = all import updates including internal imports inside moved files
3. Commit 3 = barrel `shared/api/index.ts` (new file)

Adjust the workflow:
- Before committing Commit 1, verify no edits have leaked into moved files: `git diff --cached --stat` should show all moves as 0 lines changed.

- [ ] **Commit 2: import path updates**

```bash
cd D:/VYNTIA
git add apps/web/
git diff --cached --stat | tail -10
git commit -m "$(cat <<'EOF'
chore(L4.1): update consumer imports to @/shared/* paths

Updates 600+ import statements across consumer files to use the new
shared/ infrastructure paths:
- @/components/ui/X → @/shared/ui/X (528 imports)
- @/lib/utils → @/shared/utils/cn (50 imports)
- @/lib/api → @/shared/api/api (22 imports)
- @/lib/queryClient → @/shared/api/queryClient
- @/lib/errorUtils → @/shared/api/errorUtils
- @/services/normalizers/apiNormalizers → @/shared/api/apiNormalizers
- @/components/brand/X → @/shared/ui/brand/X
- @/components/common(/X) → @/shared/components(/X)
- @/hooks/{useDebounce,use-toast,useAnimations,useScrolled} → @/shared/hooks/X
- @/utils/{cookieUtils,iconMapping} → @/shared/utils/X
- @/lib/design-tokens → @/shared/utils/design-tokens

Internal imports inside moved files (cn helper, etc.) also updated.

Build clean, vitest 7 passed, lint delta 0, pytest 161/8/3 preserved.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Commit 3: shared/api/index.ts barrel**

```bash
cd D:/VYNTIA
git add apps/web/src/shared/api/index.ts
git commit -m "$(cat <<'EOF'
chore(L4.1): add shared/api/index.ts barrel re-exports

Allows consumers to write `import { apiClient } from '@/shared/api'`
instead of `import { apiClient } from '@/shared/api/api'`. The longer
path remains valid; barrel is a convenience.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Merge to master

- [ ] **Step 1: PAUSE for user authorization**

```bash
cd D:/VYNTIA && git log --oneline master..vyntia/L4.1-shared-infra && git diff --shortstat master vyntia/L4.1-shared-infra
```

Show user. Don't merge until approved.

- [ ] **Step 2: Merge --no-ff**

```bash
git checkout master
git merge --no-ff vyntia/L4.1-shared-infra -m "Merge L4.1: shared/ infrastructure consolidation"
git log --oneline -7
```

- [ ] **Step 3: Post-merge smoke**

```bash
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3 && npm test -- --run 2>&1 | grep Tests | tail -3
```

---

## Task 11: Update master roadmap + memory

- [ ] **Step 1: Mark L4.1 done in roadmap**

Edit `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md`:
- Update L4.1 row status: `⏳ NEXT` → `✅ merged <hash>`
- Update L4.2 row status: `⏳` → `⏳ NEXT`
- Add brief outcome summary in description

- [ ] **Step 2: Update memory**

Edit `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3 fully done (already noted)
- L4.1 ✅ merged
- L4.2 (auth feature) is next
- Document any new lessons (LR30+)

- [ ] **Step 3: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-06-vyntia-foundation-L4-master-roadmap.md
git commit -m "docs(L4.1): mark L4.1 merged"
```

---

## Notas para el ejecutor

- **Two-phase commit pattern**: file moves first (clean rename detection), import updates second. Don't conflate — git's similarity index works best with empty diffs on renames.
- **528 ui imports**: this is the big one. Consider scripting with `find ... -exec sed -i ...` if Edit tool is too slow per file. But verify result with grep counts before commit.
- **Barrel export edge cases**: `from '@/components/common'` (no trailing) imports default exports / barrel. After move, becomes `from '@/shared/components'` (the existing index.ts re-exports the canonical surface).
- **Risk of breaking shadcn `cn()` helper**: most shadcn primitives import `cn` from `@/lib/utils`. After move to `@/shared/utils/cn`, ALL of them need internal updates. Verify with grep inside `shared/ui/`.
- **No frontend route changes**: this is purely a folder reorg. App.tsx routes don't change in L4.1.
- **No `useLoading.ts` consolidation**: there are duplicates `useLoading.ts` and `useLoading.tsx` in `components/common/`. Move both as-is; consolidation is L4.11 cleanup territory.
