# VYNTIA Foundation L4.10 — Onboarding Feature Completion Plan

**Goal:** Move remaining onboarding files (2 pages + 1 service) into existing `features/onboarding/`. Components already migrated (per L0/early L4 work). Extend existing barrels with new entries.

**Branch:** `vyntia/L4.10-feature-onboarding`. Predecessor L4.9 ✅ `0bfde9be`.

## Files to MOVE (3)

| From | To |
|---|---|
| `pages/onboarding/OnboardingAdminPage.tsx` | `features/onboarding/pages/` |
| `pages/onboarding/OnboardingPage.tsx` | `features/onboarding/pages/` |
| `services/onboardingService.ts` | `features/onboarding/services/` |

`features/onboarding/{pages,services,components}/` ALREADY EXIST and are partially populated. The moves go INTO the existing structure.

## Barrels to UPDATE (extend existing, don't recreate)

- `features/onboarding/pages/index.ts` — extend with 2 new entries (currently exports only `OnboardingEmployeePage`)
- `features/onboarding/services/index.ts` — extend with `onboardingService` (currently exports only `onboardingUploadService`)
- `features/onboarding/components/index.ts` — NO CHANGE (no new components)
- `features/onboarding/index.ts` — NO CHANGE (top-level barrel already re-exports subdirs)

## Mapping table (length-DESC)

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/pages/onboarding/OnboardingAdminPage` | `@/features/onboarding/pages/OnboardingAdminPage` |
| 2 | `@/pages/onboarding/OnboardingPage` | `@/features/onboarding/pages/OnboardingPage` |
| 3 | `@/services/onboardingService` | `@/features/onboarding/services/onboardingService` |

**Consumers (4 sites):**
- App.tsx (3 imports: 2 pages + 1 service)
- pages/onboarding/OnboardingAdminPage.tsx (1 internal)
- features/employees/pages/Empleados.tsx (1 external)
- features/onboarding/pages/OnboardingEmployeePage.tsx (1 — already in features/, uses old @/services/onboardingService alias)

**Sibling sweep:** clean.

**Spanish placeholder:** None (`features/onboarding/` is already English-named).

**Baselines:** carry-over post-L4.9. Expect tsc 1, build clean, vitest 7, eslint 634, pytest 161/8/3.
