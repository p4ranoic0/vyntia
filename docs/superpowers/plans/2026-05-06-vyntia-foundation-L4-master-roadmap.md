# VYNTIA Foundation L4 — Frontend Reorganization Master Roadmap

> **Strategy:** Decompose L4 into 11 sub-PRs by bounded context, mirroring the successful L3 sub-PR pattern. Each sub-PR produces a working, testable frontend with baselines preserved.

**Date:** 2026-05-06
**Spec source:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4.4
**Predecessor merge:** L3.11 ✅ `c6839f87` — Foundation L3 fully complete
**Estimated effort:** 5-8 days (per spec) split into 11 PRs of ~half-day each

---

## Goal

Migrate the frontend from its current `pages/` + `components/` + `services/` + `hooks/` flat structure to a feature-based layout where each bounded context is self-contained under `features/<context>/`. Mirror the 8 Django apps split done in L3 (`identity`, `organization`, `employees`, `contracts`, `documents`, `payroll`, `time_off`, `onboarding`) plus frontend-only `auth` and `shared/` infrastructure.

---

## Current state inventory (snapshot 2026-05-06)

```
apps/web/src/
├── pages/                     # 47 files — domain pages organized by Spanish folder names
│   ├── admin/, areas/, configuracion/, contratos/, empleados/
│   ├── legajo/, onboarding/, remuneraciones/, security/, users/, vacaciones/
│   └── (root-level) AccessDeniedPage, ChangePasswordPage, Dashboard, Empleados,
│       HROverviewDashboard, LoadingDemo, PlantillasDocumentosPage, ResetPasswordPage
├── features/                  # 71 files — mostly empty index.ts stubs
│   ├── admin/, areas/, auth/, contratos/, empleados/, legajo/
│   ├── onboarding/  ← only one actually populated (DocumentUploadZone, OnboardingTabX)
│   ├── security/, usuarios/, vacaciones/
├── components/                # 77 files
│   ├── areas/, auth/, brand/, common/, empleados/, layout/
│   ├── modals/ (DatosX modals), notifications/, ui/ (shadcn 30+ components)
│   ├── users/, vacaciones/
├── services/                  # 14 files (renamed in L3.10.4f)
│   ├── authService, companyService, contractsService, departmentsService
│   ├── employeesService, legajoService, menuService, onboardingService
│   ├── payrollService, securityService, templatesService, timeOffService, usersService
│   └── normalizers/apiNormalizers
├── hooks/                     # 10 files
│   ├── useApi, useApi-deprecated, useAuth, useMenu, useRemuneraciones
│   ├── use-toast, useAnimations, useDebounce, useEmployeePermissions, useScrolled
├── lib/                       # 5 files
│   ├── api.ts, design-tokens.ts, errorUtils.ts, queryClient.ts, utils.ts
├── shared/                    # scaffolding (mostly empty)
│   ├── components/ (DocumentStatus, EmpleadoCard, EstadoBadge, StatCard)
│   ├── hooks/ (useDebounce, usePermission, useToast)
│   └── types/, utils/
├── context/                   # 2 files (AuthContext)
├── generated/                 # OpenAPI auto-generated — DO NOT TOUCH
├── styles/                    # tokens.css
├── test/                      # vitest setup
├── utils/                     # cookieUtils, iconMapping
└── App.tsx, main.tsx, index.css
```

**Total: 457 .ts/.tsx files**

---

## Target structure (post-L4)

```
apps/web/src/
├── shared/                    # Cross-feature infrastructure
│   ├── api/                   # axios client, React Query setup, normalizers
│   ├── ui/                    # shadcn primitives + brand components
│   ├── hooks/                 # generic hooks (useDebounce, useToast, useAnimations, useScrolled)
│   ├── components/            # cross-feature reusables (DocumentStatus, StatCard, etc.)
│   ├── types/                 # cross-feature TS types
│   └── utils/                 # generic utilities (cookieUtils, iconMapping, errorUtils)
├── features/                  # Bounded contexts (one per Django app + auth)
│   ├── auth/                  # login, password reset, change password
│   │   ├── components/        # LoginForm, ChangePasswordForm, ResetPasswordForm
│   │   ├── pages/             # ChangePasswordPage, ResetPasswordPage
│   │   ├── hooks/             # useAuth
│   │   ├── services/          # authService
│   │   ├── context/           # AuthContext
│   │   └── types/, index.ts
│   ├── identity/              # users, roles, permissions, modules
│   │   ├── components/        # UserDetailsModal, UserFormModal, RoleManagementModal, ChangePasswordModal
│   │   ├── pages/             # UsersList, UsersForm, UsersManagement, ChangePassword,
│   │   │                        RoleManagement, RolesPage, PermissionsPage, RolePermissionsPage
│   │   ├── services/          # usersService, securityService
│   │   └── types/, index.ts
│   ├── organization/          # departments (areas), company config
│   │   ├── components/        # AreaForm, DeleteAreaDialog
│   │   ├── pages/             # AreasListPage, AreaFormPage, AreasManagementPage,
│   │   │                        ConfiguracionEmpresaPage
│   │   ├── services/          # departmentsService, companyService
│   │   └── types/, index.ts
│   ├── employees/             # employees, dependents, academic records, certifications
│   │   ├── components/        # AdminDocUpload, TabPersonales, TabLaborales, TabFamiliares, TabAcademicos
│   │   ├── modals/            # DatosPersonalesModal, DatosLaboralesModal, DatosFamiliaresModal, DatosAcademicosModal
│   │   ├── pages/             # Empleados, EmpleadosListPage, DatosPersonalesPage, DatosLaboralesPage,
│   │   │                        DatosFamiliaresPage, DatosAcademicosPage, EmpleadoReportPage,
│   │   │                        HROverviewDashboard
│   │   ├── hooks/             # useEmployeePermissions
│   │   ├── services/          # employeesService
│   │   └── types/, index.ts
│   ├── contracts/             # contracts + amendments
│   │   ├── pages/             # ContratosPage
│   │   ├── services/          # contractsService
│   │   └── types/, index.ts
│   ├── documents/             # legajo (digital documents) + templates
│   │   ├── pages/             # LegajoPage, GestionDocumentosPage, PlantillasDocumentosPage
│   │   ├── services/          # legajoService, templatesService
│   │   └── types/, index.ts
│   ├── payroll/               # payroll (remuneraciones)
│   │   ├── pages/             # RemuneracionesHomePage, BoletasPagoPage, PlanillasMensualesPage,
│   │   │                        ConfiguracionRemuneracionesPage, ConfiguracionUitPage,
│   │   │                        DescuentosMasivosPage, ProcesoPlanillasPage, ReportesRemuneracionesPage
│   │   ├── hooks/             # useRemuneraciones
│   │   ├── services/          # payrollService
│   │   └── types/, index.ts
│   ├── time-off/              # vacations
│   │   ├── components/        # CalendarioVacaciones, ConfiguracionPanel, EstadisticasVacaciones,
│   │   │                        HistorialSolicitudes, NotificacionesVacaciones, PeriodosManagement,
│   │   │                        ResumenDiasVacaciones
│   │   ├── pages/             # ConfiguracionPage, NuevaSolicitudPage, PeriodosPage,
│   │   │                        ReportesPage, SolicitudesPage, VacacionesManagementPage
│   │   ├── services/          # timeOffService
│   │   └── types/, index.ts
│   ├── onboarding/            # onboarding (already partially migrated)
│   │   ├── components/        # DocumentPreviewModal, DocumentUploadZone, OnboardingCompleteBanner,
│   │   │                        OnboardingProgressBar, OnboardingSectionStatus, OnboardingTabX (4)
│   │   ├── pages/             # OnboardingPage, OnboardingAdminPage
│   │   ├── services/          # onboardingService
│   │   └── types/, index.ts
│   └── _layout/               # Cross-feature layout (DECISION: keep at features/_layout or shared/layout?)
│       ├── components/        # Layout, Header, Sidebar, AdminLayout, AreasLayout,
│       │                        EmployeeLayout, UsersLayout, NotificationsBell
│       └── hooks/             # useMenu (menu construction logic)
├── pages/                     # Empty after L4 (or contains only Dashboard, AccessDenied)
├── App.tsx, main.tsx, index.css, vite-env.d.ts
└── (delete) features/admin/, features/areas/ (renamed/merged into the bounded contexts above)
```

---

## Sub-PR roadmap (11 sub-PRs)

| Sub-PR | Title | Branch | Scope | Est lines | Risk | Depends on | Status |
|---|---|---|---|---|---|---|:---:|
| **L4.1** | shared/ infrastructure consolidation | `vyntia/L4.1-shared-infra` | Moved `lib/api.ts`+`queryClient.ts`+`errorUtils.ts`+`services/normalizers/apiNormalizers.ts` → `shared/api/` (+ barrel `index.ts`). Moved `components/ui/` (28 shadcn files + `use-toast.ts`) → `shared/ui/`. Moved `components/brand/{VyntiaLogo,VyntiaWordmark}` → `shared/ui/brand/`. Moved `components/common/` (12 files: DataTable, LoadingX, ProfileImage, DocumentViewer, useLoading) → `shared/components/`. Moved `hooks/{useDebounce,use-toast,useAnimations,useScrolled}` → `shared/hooks/`. Moved `utils/{cookieUtils,iconMapping}`+`lib/utils.ts` (→`cn.ts`)+`lib/design-tokens.ts` → `shared/utils/`. Deleted 12 unused `shared/` scaffolding stubs. **Bulk import update via Python script**: 661 `from '@/X'` → `from '@/shared/X'` replacements across 142 files. 3 atomic commits (plan + moves + imports/barrel). Diff: 173 files, 1399+/1386- (net +13 = barrel). Rename detection 96-100% across 53 files. Pytest 161/8/3 + vitest 7 + build clean + TS strict 0 errors + lint delta 0 baselines preservados | ~30 | Medio | L3.11 ✅ | ✅ merged `07d86d6e` |
| **L4.2** | auth feature migration | `vyntia/L4.2-feature-auth` | Move `components/auth/{LoginForm,ChangePasswordForm,ResetPasswordForm}.tsx` → `features/auth/components/`. Move `pages/{ChangePasswordPage,ResetPasswordPage}.tsx` → `features/auth/pages/`. Move `services/authService.ts` → `features/auth/services/`. Move `context/AuthContext.tsx` → `features/auth/context/`. Move `hooks/useAuth.ts` → `features/auth/hooks/`. Update App.tsx routes. ~30-40 import updates | ~12 | Bajo | L4.1 | ⏳ NEXT |
| **L4.3** | identity feature migration | `vyntia/L4.3-feature-identity` | Move `pages/users/*` → `features/identity/pages/`. Move `pages/security/*` → `features/identity/pages/`. Move `components/users/modals/*` → `features/identity/components/modals/`. Move `services/{usersService,securityService}.ts` → `features/identity/services/`. Update App.tsx routes for /usuarios/, /seguridad/. ~50-70 import updates | ~18 | Medio | L4.1 | ⏳ |
| **L4.4** | organization feature migration | `vyntia/L4.4-feature-organization` | Move `pages/areas/*` → `features/organization/pages/`. Move `pages/configuracion/ConfiguracionEmpresaPage.tsx` → `features/organization/pages/`. Move `components/areas/*` → `features/organization/components/`. Move `services/{departmentsService,companyService}.ts` → `features/organization/services/`. Update routes for /areas/, /configuracion/. ~25-35 import updates | ~10 | Bajo | L4.1 | ⏳ |
| **L4.5** | employees feature migration | `vyntia/L4.5-feature-employees` | LARGEST. Move `pages/{Empleados,HROverviewDashboard}.tsx` + `pages/empleados/*` → `features/employees/pages/`. Move `components/empleados/*` → `features/employees/components/`. Move `components/modals/Datos*Modal.tsx` → `features/employees/modals/`. Move `services/employeesService.ts` → `features/employees/services/`. Move `hooks/useEmployeePermissions.ts` → `features/employees/hooks/`. Discard `features/empleados/{INTEGRATION_EXAMPLE,REACT_QUERY_EXAMPLE}.ts` (pre-existing parse errors). Delete `features/empleados/` placeholder. Update routes. ~80-100 import updates | ~30 | Alto | L4.1 | ⏳ |
| **L4.6** | contracts feature migration | `vyntia/L4.6-feature-contracts` | Move `pages/contratos/ContratosPage.tsx` → `features/contracts/pages/`. Move `services/contractsService.ts` → `features/contracts/services/`. Update routes for /contratos/. Delete `features/contratos/` placeholder. ~15-20 import updates | ~8 | Bajo | L4.1 | ⏳ |
| **L4.7** | documents feature migration | `vyntia/L4.7-feature-documents` | Move `pages/legajo/*` → `features/documents/pages/`. Move `pages/PlantillasDocumentosPage.tsx` → `features/documents/pages/`. Move `services/{legajoService,templatesService}.ts` → `features/documents/services/`. Update routes for /legajo/, /plantillas/. Delete `features/legajo/` placeholder. ~25-35 import updates | ~12 | Bajo | L4.1 | ⏳ |
| **L4.8** | payroll feature migration | `vyntia/L4.8-feature-payroll` | Move `pages/remuneraciones/*` (8 pages) → `features/payroll/pages/`. Move `services/payrollService.ts` → `features/payroll/services/`. Move `hooks/useRemuneraciones.ts` → `features/payroll/hooks/`. Update routes for /remuneraciones/. ~40-60 import updates | ~18 | Medio | L4.1 | ⏳ |
| **L4.9** | time-off feature migration | `vyntia/L4.9-feature-time-off` | Move `pages/vacaciones/*` (6 pages) → `features/time-off/pages/`. Move `components/vacaciones/*` (7 components) → `features/time-off/components/`. Move `services/timeOffService.ts` → `features/time-off/services/`. Update routes for /vacaciones/. Delete `features/vacaciones/` placeholder. ~50-70 import updates | ~20 | Medio | L4.1 | ⏳ |
| **L4.10** | onboarding feature completion | `vyntia/L4.10-feature-onboarding` | Move `pages/onboarding/*` (2 pages) → `features/onboarding/pages/`. Move `services/onboardingService.ts` → `features/onboarding/services/`. Already-migrated `components/` retained in place. Update routes. ~15-20 import updates | ~8 | Bajo | L4.1 | ⏳ |
| **L4.11** | layout + final cleanup | `vyntia/L4.11-layout-cleanup` | Move `components/layout/*` (Layout, Header, Sidebar, AdminLayout, AreasLayout, EmployeeLayout, UsersLayout) → decision: `shared/layout/` OR `features/_layout/`. Move `components/notifications/NotificationsBell.tsx` → same destination. Move `hooks/useMenu.ts` to layout location. Delete empty placeholder `features/admin/`, `features/areas/`, `features/empleados/`, `features/legajo/`, `features/security/`, `features/usuarios/`, `features/vacaciones/`, `features/contratos/` (now superseded by canonical English-named features). Delete remaining `pages/admin/`, `pages/users/`, etc empty subdirs. Update CLAUDE.md path references. ~30-40 import updates | ~15 | Medio | L4.2-L4.10 | ⏳ |

**Total estimated:** 11 sub-PRs, ~180 commits worth of cumulative changes, 5-8 days at sustainable pace.

---

## Cross-cutting decisions (locked in this roadmap)

### D1 — Folder naming: English canonical

All feature folders use English bounded-context names (matching the 8 Django apps): `identity/`, `organization/`, `employees/`, `contracts/`, `documents/`, `payroll/`, `time-off/`, `onboarding/`, plus `auth/`. **Existing Spanish placeholders** (`features/empleados/`, `features/areas/`, `features/usuarios/`, `features/contratos/`, `features/vacaciones/`, `features/legajo/`, `features/security/`, `features/admin/`) **are deleted in L4.11** after their content has been migrated to the English equivalents.

**Rejected:** preserving Spanish folder names (`features/empleados/`, `features/vacaciones/`) — would diverge from the backend Django app naming and force a translation table in CLAUDE.md.

### D2 — `time-off/` (kebab-case) vs `time_off/`

Use `features/time-off/` to match the URL path `/api/v1/time-off/` and React Router routes. JavaScript imports tolerate kebab-case in folder names.

**Rejected:** `timeOff/` (camelCase folder unconventional in TS); `time_off/` (underscore inconsistent with kebab-case URLs).

### D3 — Layout components: `shared/layout/` (NOT `features/_layout/`)

Layouts (Layout, Header, Sidebar, AdminLayout, etc.) are infrastructure used by ALL features. Place them in `shared/layout/` rather than `features/_layout/`.

**Rejected:** `features/_layout/` — underscored "feature" implies it's a feature, but it's not (no domain logic; pure UI scaffolding).

### D4 — Path aliases: `@/features/X`, `@/shared/X` only

After L4, all imports use either:
- `@/features/<context>/...` for feature-internal files
- `@/shared/...` for shared infrastructure
- `@/App`, `@/main` only in the root

**Eliminate:** `@/components/`, `@/services/`, `@/hooks/`, `@/lib/`, `@/utils/`, `@/pages/` aliases (deprecated; they would be valid only for files NOT yet migrated, which is a hazard during the transition).

**During L4.1 → L4.10 transition:** `@/components/`, `@/services/`, etc. still resolve as long as the directories exist with files. As each L4.X PR moves files, those aliases naturally resolve to fewer files. L4.11 enforces the final state by removing empty dirs.

### D5 — `shared/api/` consolidation strategy

`lib/api.ts` is currently a 200+-line axios client + helpers. `lib/queryClient.ts` is the React Query setup. `services/normalizers/apiNormalizers.ts` is the normalizer module. After L4.1:
- `shared/api/client.ts` ← from `lib/api.ts`
- `shared/api/queryClient.ts` ← from `lib/queryClient.ts`
- `shared/api/normalizers.ts` ← from `services/normalizers/apiNormalizers.ts`
- `shared/api/errors.ts` ← from `lib/errorUtils.ts`
- `shared/api/index.ts` ← re-export public surface

### D6 — Each sub-PR is INDEPENDENT and uses the same workflow

Like L3 sub-PRs, each L4.X sub-PR:
1. Branches from master
2. Moves files (preferring `git mv` for rename detection)
3. Updates imports (TS-driven where possible; `replace_all` per consumer file)
4. Verifies pytest baseline preserved (frontend changes shouldn't affect backend, but check)
5. Verifies `npm run build` clean + vitest 7 passed + lint delta 0
6. Optional curl smoke if URL routing affected (mostly not in L4 since URLs are stable post-L3.10.4b)
7. Merges to master with `--no-ff`

### D7 — Out-of-scope deferrals

Explicitly NOT in L4 (deferred to L5 or future sub-projects):
- Backend module relocation (`app_rrhh/{menu_service,permission_service,constants,validators,tasks}` → `apps/X/`) — L5
- Renaming `api/v1/rrhh/views.py` → `api/v1/_canonical_views/` — L5 or later
- `packages/shared/src/types/` package extraction — defer until packages/ is actively used (currently only design-tokens lives there)
- Splitting `App.tsx` into route-config files — future enhancement
- Migrating `useApi.ts` and `useApi-deprecated.ts` to React Query patterns — separate refactor sub-project
- Extracting OpenAPI client (currently in `generated/`) into `@vyntia/api-client` package — separate sub-project

---

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `shared/api` consolidation breaks all features simultaneously | Med | High | L4.1 is a foundational change; verify build between each path-alias update; commit each batch atomically |
| `git mv` rename detection drops below 50% (file becomes "delete + create") | Low | Medium | Keep file body 100% unchanged on the rename commit; update imports in a SEPARATE commit (preserves rename detection) |
| Routes break in App.tsx (route → page mapping) | Med | High | After each feature migration, run dev server + click through routes manually OR include curl smoke for SPA routes (limited) |
| Tests in `tests/` reference old import paths | Low | Low | vitest tests use `@/services/X` aliases; after L4 those paths still work via re-export shims OR tests get migrated alongside features |
| `App.tsx` becomes a coordination point that gets touched in every sub-PR (merge conflicts) | High | Low | Each sub-PR ONLY touches its own routes block in App.tsx; mark sections clearly with comments |
| Empty placeholder `features/empleados/` etc. still imported via barrel `index.ts` somewhere | Low | Low | Pre-flight grep for `from '@/features/empleados'` style imports in L4.5; resolve before deletion |
| Lint delta increases from auto-fix of new file paths | Low | Low | `npm run lint` baseline measured pre-L4 (target: 636 problems); each sub-PR confirms 0 net new |
| Frontend build chunk warning grows beyond current 1.5MB (size warnings) | Low | Low | Already pre-existing; out of scope for L4 |

---

## Definition of done (L4 fully complete)

- [ ] All 11 sub-PRs merged to master with `--no-ff`
- [ ] `apps/web/src/pages/` is empty or contains only top-level pages (Dashboard, AccessDeniedPage, LoadingDemo)
- [ ] `apps/web/src/components/` no longer has feature-specific subdirs (only `shared/` namespaced under `shared/components/`)
- [ ] `apps/web/src/services/` is empty (all moved to `features/X/services/`)
- [ ] `apps/web/src/hooks/` only has `useApi.ts` (deprecated, marked for L5 cleanup); rest moved to features or `shared/`
- [ ] `apps/web/src/lib/` is empty (consolidated into `shared/api/` and `shared/utils/`)
- [ ] `apps/web/src/shared/` populated with infrastructure (api, ui, hooks, components, types, utils, layout)
- [ ] All 8 bounded contexts populated under `features/<context>/` (identity, organization, employees, contracts, documents, payroll, time-off, onboarding) + `auth/`
- [ ] Spanish-named placeholder feature folders (`features/empleados/`, `features/vacaciones/`, etc.) deleted
- [ ] `npm run build` clean
- [ ] `npm test` (vitest) 7 passed (1 file load failure pre-existing)
- [ ] Backend pytest baseline 161/8/3 preserved (no backend changes expected)
- [ ] `npm run lint` 0 net new errors vs L3.11 baseline
- [ ] Manual smoke: dev server starts, all routes load, key flows work (login, list employees, create contract, view payroll, request vacation)
- [ ] CLAUDE.md updated with new path layout
- [ ] Memory `active_subproject.md` updated with L4 completion + lessons learned (LR30+)

---

## Execution model

**Each sub-PR follows the pattern proven in L3:**

1. Read this roadmap to scope the work
2. Spec/plan: write a detailed sub-PR plan as `docs/superpowers/plans/2026-05-XX-vyntia-foundation-L4.X-<short-name>.md` covering tasks, file mappings, verification commands
3. Execute via `superpowers:executing-plans` with TaskCreate tracking
4. Atomic commits: 1 commit for the plan, N commits for moves + import updates, 1 commit to mark roadmap done
5. PAUSE at end of each sub-PR for user authorization before merge to master

**The user can pause/resume between any two sub-PRs.** L4 is purely organizational; no sub-PR is half-done state. Each sub-PR returns the codebase to a fully-working green state.

---

## Lecciones acumuladas L3 → L4 carry-over

Lessons from L3 sub-PRs that apply to L4:

- **LR1-LR16** (model split, FK strings, migrations) — backend-only, not relevant to L4
- **LR17 (serializer Meta.fields hardcoded)** — N/A (no backend changes)
- **LR18-LR20 (PK/audit fields)** — N/A
- **LR21 (model splits, choice list audit)** — N/A
- **LR22 (replace_all collapses fallbacks)** — RELEVANT. When updating import paths, watch for `from '@/services/X'` AND `from '@/components/X'` co-existing — replace_all of one might wrongly catch the other if substring overlap.
- **LR23 (field READ vs query PARAM)** — N/A (no API contract changes)
- **LR24 (suffix _texto rename)** — N/A
- **LR25 (silent serializer Meta bugs)** — N/A
- **LR26 (TS strict doesn't catch `any` consumers)** — RELEVANT. Build can pass while runtime breaks. After each sub-PR, run dev server in browser AND check key flows. Don't trust build alone.
- **LR27 (Vite esbuild not strict-check)** — RELEVANT. Use `npx tsc --noEmit -p tsconfig.app.json` for true type checking.
- **LR28 (claim of "empty folder" was wrong)** — RELEVANT. Don't trust this roadmap's "empty placeholder features/X/" claim — verify with `ls features/X/` before deletion in each sub-PR.
- **LR29 (Python package shadowing)** — N/A (frontend only)

**New lessons expected during L4 (LR30+):**
- TS path alias resolution edge cases when both old and new paths exist
- React Router route registration patterns (centralized App.tsx vs distributed)
- shadcn component `cn()` import path migration
- `@vyntia/design-tokens` package re-import after `lib/design-tokens.ts` → `shared/utils/design-tokens.ts` move

---

## Inmediate next step

Once user approves this roadmap, execute **L4.1 (shared infrastructure consolidation)** as the first sub-PR. L4.1 is the foundation for all other migrations — no other sub-PR can complete cleanly without it.

L4.1 plan to be drafted as `docs/superpowers/plans/2026-05-06-vyntia-foundation-L4.1-shared-infra.md` with detailed task breakdown.
