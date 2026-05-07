# VYNTIA Foundation L4.8 — Payroll Feature Migration Plan

**Goal:** Move payroll slice (8 pages + 1 service + 1 hook = 10 files) into `features/payroll/`. Includes remuneraciones→payroll English rename for the bounded context.

**Branch:** `vyntia/L4.8-feature-payroll`. Predecessor L4.7 ✅ `8a1f884d`.

## Files to MOVE (10)

| From | To |
|---|---|
| `pages/remuneraciones/BoletasPagoPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/ConfiguracionRemuneracionesPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/ConfiguracionUitPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/DescuentosMasivosPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/PlanillasMensualesPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/ProcesoPlanillasPage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/RemuneracionesHomePage.tsx` | `features/payroll/pages/` |
| `pages/remuneraciones/ReportesRemuneracionesPage.tsx` | `features/payroll/pages/` |
| `services/payrollService.ts` | `features/payroll/services/` |
| `hooks/useRemuneraciones.ts` | `features/payroll/hooks/` |

## Files to CREATE (4 NEW barrels)

- `features/payroll/index.ts` (top-level)
- `features/payroll/pages/index.ts` (8 default exports per App.tsx style)
- `features/payroll/services/index.ts` (`export * from './payrollService'`)
- `features/payroll/hooks/index.ts` (`export * from './useRemuneraciones'`)

## Mapping table (length-DESC)

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/pages/remuneraciones/ConfiguracionRemuneracionesPage` | `@/features/payroll/pages/ConfiguracionRemuneracionesPage` |
| 2 | `@/pages/remuneraciones/ReportesRemuneracionesPage` | `@/features/payroll/pages/ReportesRemuneracionesPage` |
| 3 | `@/pages/remuneraciones/RemuneracionesHomePage` | `@/features/payroll/pages/RemuneracionesHomePage` |
| 4 | `@/pages/remuneraciones/PlanillasMensualesPage` | `@/features/payroll/pages/PlanillasMensualesPage` |
| 5 | `@/pages/remuneraciones/DescuentosMasivosPage` | `@/features/payroll/pages/DescuentosMasivosPage` |
| 6 | `@/pages/remuneraciones/ProcesoPlanillasPage` | `@/features/payroll/pages/ProcesoPlanillasPage` |
| 7 | `@/pages/remuneraciones/ConfiguracionUitPage` | `@/features/payroll/pages/ConfiguracionUitPage` |
| 8 | `@/pages/remuneraciones/BoletasPagoPage` | `@/features/payroll/pages/BoletasPagoPage` |
| 9 | `@/hooks/useRemuneraciones` | `@/features/payroll/hooks/useRemuneraciones` |
| 10 | `@/services/payrollService` | `@/features/payroll/services/payrollService` |

## Tasks

Standard 3-commit pattern: branch+plan, mkdir+10 git mv, Python rewrite + 4 barrels.

**Sibling-relative sweep:** clean.

**Consumers:** App.tsx (8) + 7 internal sites = ~15 sites across ~10 files.

**Baselines:** carry-over post-L4.7. Expect tsc 1, build clean, vitest 7, eslint 634, pytest 161/8/3.
