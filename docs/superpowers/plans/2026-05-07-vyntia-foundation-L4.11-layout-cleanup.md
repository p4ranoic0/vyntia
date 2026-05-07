# VYNTIA Foundation L4.11 — Layout + Final Cleanup Plan

**Goal:** Final L4 sub-PR. Move 7 layout components + NotificationsBell to `shared/layout/`, useMenu to `shared/hooks/`, menuService to `shared/api/`. Delete 7 Spanish placeholder feature dirs and 10 empty pages/ subdirs. Update CLAUDE.md.

**Branch:** `vyntia/L4.11-layout-cleanup`. Predecessor L4.10 ✅ `4eb162a9`.

## Files to MOVE (10)

**To `shared/layout/`** (8 files — flat, no barrel per shared/ convention):

| From | To |
|---|---|
| `components/layout/AdminLayout.tsx` | `shared/layout/AdminLayout.tsx` |
| `components/layout/AreasLayout.tsx` | `shared/layout/AreasLayout.tsx` |
| `components/layout/EmployeeLayout.tsx` | `shared/layout/EmployeeLayout.tsx` |
| `components/layout/Header.tsx` | `shared/layout/Header.tsx` |
| `components/layout/Layout.tsx` | `shared/layout/Layout.tsx` |
| `components/layout/Sidebar.tsx` | `shared/layout/Sidebar.tsx` |
| `components/layout/UsersLayout.tsx` | `shared/layout/UsersLayout.tsx` |
| `components/notifications/NotificationsBell.tsx` | `shared/layout/NotificationsBell.tsx` |

**To `shared/hooks/`** (1 file):

| From | To |
|---|---|
| `hooks/useMenu.ts` | `shared/hooks/useMenu.ts` |

**To `shared/api/`** (1 file):

| From | To |
|---|---|
| `services/menuService.ts` | `shared/api/menuService.ts` |

## Files/dirs to DELETE

**Spanish placeholder feature dirs** (`rm -rf` each — 7 total):
- `features/admin/`
- `features/areas/`
- `features/contratos/`
- `features/legajo/`
- `features/security/`
- `features/usuarios/`
- `features/vacaciones/`

(`features/empleados/` was deleted in L4.5.)

**Empty pages/ subdirs** (10 total — all empty after prior moves):
- `pages/areas/`
- `pages/configuracion/`
- `pages/contratos/`
- `pages/empleados/`
- `pages/legajo/`
- `pages/onboarding/`
- `pages/remuneraciones/`
- `pages/security/`
- `pages/users/`
- `pages/vacaciones/`

(`pages/admin/AdminDashboard.tsx` stays — it's a top-level admin page used by App.tsx.)

**Old source dirs** (now empty, from prior PRs):
- `services/` (only menuService — moves out, dir becomes empty → delete)
- `components/layout/` (becomes empty after moves → delete)
- `components/notifications/` (becomes empty after move → delete)
- `components/` (becomes empty → delete)

## Files to UPDATE

- `shared/api/index.ts` — extend with menuService export (optional; consumers import direct path is fine)
- `CLAUDE.md` — update path references where outdated

## Mapping table (length-DESC)

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/components/notifications/NotificationsBell` | `@/shared/layout/NotificationsBell` |
| 2 | `@/components/layout/EmployeeLayout` | `@/shared/layout/EmployeeLayout` |
| 3 | `@/components/layout/AreasLayout` | `@/shared/layout/AreasLayout` |
| 4 | `@/components/layout/UsersLayout` | `@/shared/layout/UsersLayout` |
| 5 | `@/components/layout/AdminLayout` | `@/shared/layout/AdminLayout` |
| 6 | `@/components/layout/Sidebar` | `@/shared/layout/Sidebar` |
| 7 | `@/components/layout/Header` | `@/shared/layout/Header` |
| 8 | `@/components/layout/Layout` | `@/shared/layout/Layout` |
| 9 | `@/services/menuService` | `@/shared/api/menuService` |
| 10 | `@/hooks/useMenu` | `@/shared/hooks/useMenu` |

**Consumers:** App.tsx (2 layouts) + 12 feature pages (Datos*Page Employee + Areas* + Users* + Identity*) + Header (NotificationsBell) + Sidebar (menuService) + AuthContext (menuService) + 2 internal moved files = ~20 import sites.

**Sibling sweep:** clean.

## Tasks

### Task 1: Branch + plan commit (standard)

### Task 2: 10 git mv (single commit, pure renames)

### Task 3: Imports + barrel update + dir deletions + CLAUDE.md update

Single atomic commit with:
- Python script rewriting 10 mappings (~20 sites)
- Sibling-relative sweep (must be empty)
- Optional: extend `shared/api/index.ts` with menuService re-export
- `rm -rf` 7 Spanish placeholder dirs + 10 empty pages/ subdirs + components/layout/ + components/notifications/ + components/ (if empty) + services/ (if empty)
- Update CLAUDE.md path references

**Baselines:** carry-over post-L4.10. Expect tsc 1, build clean, vitest 7, eslint 634, pytest 161/8/3.
