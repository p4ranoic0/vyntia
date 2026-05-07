# VYNTIA Foundation L4.9 — Time-off Feature Migration Plan

**Goal:** Move time-off slice (6 pages + 7 components + 1 service = 14 files) into `features/time-off/`. Includes vacaciones→time-off English rename. Folder uses kebab-case per master roadmap D2.

**Branch:** `vyntia/L4.9-feature-time-off`. Predecessor L4.8 ✅ `3c5bed9a`.

## Files to MOVE (14)

**Pages (6):** ConfiguracionPage, NuevaSolicitudPage, PeriodosPage, ReportesPage, SolicitudesPage, VacacionesManagementPage — from `pages/vacaciones/` to `features/time-off/pages/`

**Components (7):** CalendarioVacaciones, ConfiguracionPanel, EstadisticasVacaciones, HistorialSolicitudes, NotificacionesVacaciones, PeriodosManagement, ResumenDiasVacaciones — from `components/vacaciones/` to `features/time-off/components/`

**Service (1):** `services/timeOffService.ts` → `features/time-off/services/`

## Files to CREATE (4 NEW barrels)

- `features/time-off/index.ts` (top-level)
- `features/time-off/pages/index.ts` (6 default exports)
- `features/time-off/components/index.ts` (7 default exports)
- `features/time-off/services/index.ts` (`export * from './timeOffService'`)

## Mapping table (length-DESC)

| # | OLD | NEW |
|---:|---|---|
| 1 | `@/components/vacaciones/NotificacionesVacaciones` | `@/features/time-off/components/NotificacionesVacaciones` |
| 2 | `@/components/vacaciones/EstadisticasVacaciones` | `@/features/time-off/components/EstadisticasVacaciones` |
| 3 | `@/components/vacaciones/ResumenDiasVacaciones` | `@/features/time-off/components/ResumenDiasVacaciones` |
| 4 | `@/components/vacaciones/HistorialSolicitudes` | `@/features/time-off/components/HistorialSolicitudes` |
| 5 | `@/components/vacaciones/CalendarioVacaciones` | `@/features/time-off/components/CalendarioVacaciones` |
| 6 | `@/pages/vacaciones/VacacionesManagementPage` | `@/features/time-off/pages/VacacionesManagementPage` |
| 7 | `@/components/vacaciones/PeriodosManagement` | `@/features/time-off/components/PeriodosManagement` |
| 8 | `@/components/vacaciones/ConfiguracionPanel` | `@/features/time-off/components/ConfiguracionPanel` |
| 9 | `@/pages/vacaciones/NuevaSolicitudPage` | `@/features/time-off/pages/NuevaSolicitudPage` |
| 10 | `@/pages/vacaciones/ConfiguracionPage` | `@/features/time-off/pages/ConfiguracionPage` |
| 11 | `@/pages/vacaciones/SolicitudesPage` | `@/features/time-off/pages/SolicitudesPage` |
| 12 | `@/pages/vacaciones/PeriodosPage` | `@/features/time-off/pages/PeriodosPage` |
| 13 | `@/pages/vacaciones/ReportesPage` | `@/features/time-off/pages/ReportesPage` |
| 14 | `@/services/timeOffService` | `@/features/time-off/services/timeOffService` |

**Consumers:** App.tsx (6) + 1 NotificationsBell external + 7 internal pages/components ≈ 28 import sites across 14 files.

**Spanish placeholder:** `features/vacaciones/` exists, kept for L4.11.

**Sibling sweep:** clean.

**Baselines:** carry-over post-L4.8. Expect tsc 1, build clean, vitest 7, eslint 634, pytest 161/8/3.
