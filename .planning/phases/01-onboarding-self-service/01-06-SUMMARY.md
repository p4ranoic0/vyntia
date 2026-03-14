---
phase: 01-onboarding-self-service
plan: "06"
subsystem: frontend-onboarding-admin
tags: [react, onboarding, rrhh, monitoring, filters, progress-bar, email-correction]
dependency_graph:
  requires:
    - 01-04  # computeAlert and corregirCorreo built in plan 04
    - 01-02  # onboarding endpoints (reenviar-email, corregir-correo, validar)
  provides:
    - Enhanced RRHH monitoring panel with progress bars, alert column, filters, email correction flow
  affects:
    - front/src/pages/onboarding/OnboardingAdminPage.tsx
tech_stack:
  patterns:
    - Shadcn/ui Progress component for inline table progress bars
    - AlertTriangle from lucide-react (TriangleAlert unavailable in installed version)
    - Client-side filtering — no server round-trips for small data sets
    - Dialog-based confirm/reject replacing prompt() usage
    - State-driven email failure banner after onboarding creation
key_files:
  modified:
    - front/src/pages/onboarding/OnboardingAdminPage.tsx
decisions:
  - AlertTriangle used instead of TriangleAlert — TriangleAlert is not exported by this version of lucide-react
  - Both tasks implemented as a single component rewrite since they share state and JSX structure
  - Pre-existing default-import bugs in OnboardingTabPersonal and OnboardingEmployeePage auto-fixed (Rule 3 — blocked build)
metrics:
  duration: 6 min
  completed_date: "2026-03-14T08:35:52Z"
  tasks_completed: 2
  files_modified: 1
  requirements_addressed: [ONBD-01, ONBD-08]
---

# Phase 01 Plan 06: RRHH Onboarding Admin Panel Enhancement Summary

**One-liner:** Enhanced RRHH monitoring table with inline Progress bars, 5-day AlertTriangle detection, 5-filter bar, Dialog-based validation, and email-failure correction banner.

## What Was Built

The existing `OnboardingAdminPage.tsx` was rewritten in-place with the following additions:

### Task 1 — Enhanced monitoring table, progress bars, alert column, filters

- Table columns changed to: Empleado | Estado | Progreso | Fecha inicio | Alerta | Acciones
- Progreso column renders `<Progress value={...} />` component from shadcn/ui + percentage text beside it
- Alerta column shows `<AlertTriangle>` icon when `computeAlert()` returns true (no server round-trip)
- Filters bar with: search input (name or DNI), estado Select dropdown, % range (min/max inputs), "Con alertas" Checkbox, Limpiar filtros button
- Client-side filtering function applied to the full data set (up to 100 rows, per page_size)
- Skeleton loading state: 5 rows with Skeleton placeholders while data loads
- Row actions: Eye (ver detalle), Mail (reenviar correo), ShieldCheck (validar), XCircle (rechazar)
- Validate and Reject actions use Dialog components — no `prompt()` calls remain in the file

### Task 2 — Email failure alert banner and inline correo correction

- State `emailFailedOnboarding` tracks { onboardingId, empleadoNombre } when create response has `email_enviado: false`
- Amber-styled banner renders below filters bar with "Reintentar enviar" and "Corregir correo y reintentar" buttons
- "Corregir correo y reintentar" toggles `showCorreoInput` to reveal an email Input + Enviar button
- On submission, calls `corregirCorreo(id, email)` from `onboardingUploadService`, then refetches list
- "Sin correo" amber Badge shown in Estado column for rows where `email_bienvenida_enviado === false` and not completado
- Document rejection in detail dialog also replaced `prompt()` with a Dialog (motivo input)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] AlertTriangle used instead of TriangleAlert**
- **Found during:** Task 1 build
- **Issue:** `TriangleAlert` is not exported by the installed version of `lucide-react`. Build failed.
- **Fix:** Replaced all occurrences with `AlertTriangle` which provides identical visual output.
- **Files modified:** `front/src/pages/onboarding/OnboardingAdminPage.tsx`
- **Commit:** 34a15fa

**2. [Rule 3 - Blocking] Pre-existing default import errors in plan-04 files**
- **Found during:** Task 1 build verification
- **Issue:** `OnboardingTabPersonal.tsx` used `import apiClient from '@/lib/api'` (default) and `OnboardingEmployeePage.tsx` used `import onboardingService from '@/services/onboardingService'` (default). Both are named exports. Build was failing before my changes.
- **Fix:** Corrected to `{ apiClient }` and `{ onboardingService }` named imports. `OnboardingTabPersonal` was already corrected by linter; `OnboardingEmployeePage` was fixed manually.
- **Files modified:** `front/src/features/onboarding/pages/OnboardingEmployeePage.tsx`
- **Commit:** 34a15fa (same commit — was blocking build verification)

## Self-Check: PASSED

- `front/src/pages/onboarding/OnboardingAdminPage.tsx` — FOUND
- Commit `34a15fa` — FOUND
- Build passes (`vite build` exits 0, dist generated)
