---
phase: 01-onboarding-self-service
plan: "05"
subsystem: frontend-onboarding
tags: [react, typescript, onboarding, tabs, forms, file-upload]
dependency_graph:
  requires:
    - 01-04  # DocumentUploadZone, OnboardingProgressBar, types
    - 01-03  # backend upload actions
    - 01-02  # PATCH /api/v1/rrhh/empleados/{id}/
  provides:
    - OnboardingEmployeePage (tabbed self-service UI)
    - OnboardingTabPersonal (avatar + form + docs)
    - OnboardingTabFamiliar (family doc zones)
    - OnboardingTabAcademico (academic doc zones)
    - OnboardingTabLaboral (read-only RRHH data + labor docs)
    - OnboardingCompleteBanner (completion screen)
  affects:
    - front/src/pages/onboarding/OnboardingPage.tsx (replaced)
tech_stack:
  added: []
  patterns:
    - react-hook-form + zod for personal data form
    - useQuery for onboarding status and legajo docs
    - DocumentUploadZone composition pattern across all tabs
key_files:
  created:
    - front/src/features/onboarding/components/OnboardingTabFamiliar.tsx
    - front/src/features/onboarding/components/OnboardingTabAcademico.tsx
    - front/src/features/onboarding/components/OnboardingTabLaboral.tsx
    - front/src/features/onboarding/components/OnboardingCompleteBanner.tsx
    - front/src/features/onboarding/components/OnboardingTabPersonal.tsx
    - front/src/features/onboarding/pages/OnboardingEmployeePage.tsx
  modified:
    - front/src/pages/onboarding/OnboardingPage.tsx (replaced with thin wrapper)
    - front/src/features/onboarding/components/index.ts (added 5 new exports)
    - front/src/features/onboarding/pages/index.ts (added OnboardingEmployeePage export)
decisions:
  - "Used named import { apiClient } from '@/lib/api' — file has no default export (class instance exported as const)"
  - "Used named import { onboardingService } — service is exported as const, not default"
  - "apiClient.get() takes params as second arg directly (not wrapped in { params: {} }) per ApiClient class signature"
metrics:
  duration: 15 min
  completed_date: "2026-03-14"
  tasks_completed: 3
  files_created: 6
  files_modified: 3
---

# Phase 01 Plan 05: Employee Self-Service Onboarding Page Summary

**One-liner:** Tabbed onboarding self-service UI with progress bar, 4 document-upload tabs, personal data form, and completion banner replacing the old linear step layout.

## What Was Built

Complete employee-facing onboarding interface. An onboarding employee now sees:

1. **Progress bar** (OnboardingProgressBar) showing `progreso_porcentaje` above all tabs
2. **Tab: Personal** — Avatar display, `foto` upload zone, editable form (telefono_celular, direccion_domicilio, fecha_nacimiento via PATCH /api/v1/rrhh/empleados/{id}/), plus DNI and carnet_extranjeria upload zones
3. **Tab: Familiar** — DNI familiar + partida de nacimiento upload zones
4. **Tab: Academico** — certificado_estudios, titulo_profesional, diploma upload zones
5. **Tab: Laboral** — Read-only RRHH data card (cargo, area, regimen with lock icon) + declaracion_jurada, cv, certificado_trabajo, carta_recomendacion upload zones
6. **Completion banner** — Shown when `estado_onboarding === 'completado'`; invalidates auth-user cache and provides portal navigation button

**OnboardingPage.tsx** replaced: old linear step card layout (manually managed useState, dialog upload flow) replaced by thin wrapper rendering `OnboardingEmployeePage`.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Build OnboardingTabFamiliar, Academico, Laboral, CompleteBanner | ccb4fe9 | 4 created + index.ts |
| 2 | Build OnboardingTabPersonal | ee316ac | 1 created + index.ts |
| 3 | Wire OnboardingEmployeePage + replace OnboardingPage | 549b161 | 2 created + 3 modified |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed default import for apiClient**
- **Found during:** Task 3 build
- **Issue:** Plan spec used `import apiClient from '@/lib/api'` but api.ts has no default export — exports `const apiClient` (named)
- **Fix:** Changed to `import { apiClient } from '@/lib/api'` in both OnboardingTabPersonal.tsx and OnboardingEmployeePage.tsx
- **Files modified:** Both new files at creation time

**2. [Rule 1 - Bug] Fixed default import for onboardingService**
- **Found during:** Task 3 build
- **Issue:** Plan spec used `import onboardingService from '@/services/onboardingService'` but service uses named export
- **Fix:** Changed to `import { onboardingService }` — linter auto-applied this correction
- **Files modified:** OnboardingEmployeePage.tsx

**3. [Rule 1 - Bug] Fixed apiClient.get() params format**
- **Found during:** Task 3 review
- **Issue:** Plan spec passed `{ params: { ... } }` but ApiClient.get() signature takes params directly as second arg
- **Fix:** Changed to `apiClient.get('/api/v1/rrhh/legajo/', { empleado: ..., es_version_actual: true, page_size: 50 })`
- **Files modified:** OnboardingEmployeePage.tsx

## Self-Check: PASSED

All 6 created files confirmed present on disk. All 3 task commits confirmed in git log (ccb4fe9, ee316ac, 549b161). Build passes with 0 TypeScript errors.
