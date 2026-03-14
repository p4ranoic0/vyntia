---
phase: 01-onboarding-self-service
plan: "04"
subsystem: frontend
tags: [react, typescript, dropzone, routing, onboarding]
dependency_graph:
  requires: [01-02, 01-03]
  provides: [OnboardingRoute, DocumentUploadZone, OnboardingProgressBar, onboardingUploadService, onboarding-types]
  affects: [App.tsx, front/src/features/onboarding]
tech_stack:
  added: [react-dropzone@15.0.0]
  patterns: [React Query guard, drag-and-drop upload, FormData multipart]
key_files:
  created:
    - front/src/features/onboarding/types/onboarding.ts
    - front/src/features/onboarding/services/onboardingUploadService.ts
    - front/src/features/onboarding/components/DocumentUploadZone.tsx
    - front/src/features/onboarding/components/OnboardingProgressBar.tsx
  modified:
    - front/src/App.tsx
    - front/src/features/onboarding/types/index.ts
    - front/src/features/onboarding/services/index.ts
    - front/src/features/onboarding/components/index.ts
decisions:
  - "OnboardingRoute uses enabled: user?.tipo_usuario === 'empleado' to skip query for admin/RRHH users entirely"
  - "empleadoId prop kept in DocumentUploadZoneProps interface for future consumers (Plan 05) but not used internally yet"
  - "api.ts FormData guard was already present — no modification needed"
metrics:
  duration: 15
  completed_date: "2026-03-14"
  tasks_completed: 2
  files_created: 4
  files_modified: 4
requirements_completed: [ONBD-02, ONBD-03, ONBD-04, ONBD-05, ONBD-06, ONBD-07]
---

# Phase 01 Plan 04: Frontend Foundation — Routing Guard, Upload Service, Components Summary

**One-liner:** React-dropzone-powered upload components with OnboardingRoute guard redirecting employees to /onboarding, all wired to backend endpoints from Plans 02-03.

## What Was Built

### Task 1: react-dropzone + TypeScript contracts
- Installed `react-dropzone@15.0.0` (date-fns@4.1.0 was already present)
- Created `front/src/features/onboarding/types/onboarding.ts` exporting:
  - `EstadoOnboarding` union type (5 states)
  - `TipoDocumento` union type (12 document types)
  - `DocumentInfo` interface (per-document state with approval status)
  - `OnboardingStatus` interface (full employee onboarding state)
  - `UploadDocumentResponse` interface (upload result from backend)
  - `computeAlert()` pure function (5-day no-login alert logic)

### Task 2: Routing guard + upload service + shared components

**App.tsx — OnboardingRoute guard:**
- Added `OnboardingRoute` component that calls `onboardingService.getMiOnboarding()` via React Query
- Guard is enabled only for `tipo_usuario === 'empleado'` — RRHH/admin users bypass it completely
- `retry: false` ensures 404 (no onboarding) does not redirect
- "/" and "/dashboard" routes wrapped with `<OnboardingRoute>`
- `/onboarding`, `/cambiar-password`, and `/login` routes intentionally excluded

**onboardingUploadService.ts:**
- `uploadFoto(archivo)` — POST to `/api/v1/rrhh/onboarding/subir-foto/` with FormData
- `uploadDocument(tipo, archivo, nombre?)` — POST to `/api/v1/rrhh/onboarding/subir-documento/`
- `corregirCorreo(id, correo)` — POST to `/api/v1/rrhh/onboarding/{id}/corregir-correo/`
- FormData Content-Type override already handled by existing api.ts interceptor (no changes needed)

**DocumentUploadZone.tsx:**
- Drag-and-drop zone using `useDropzone` from react-dropzone
- Accepts PDF only (or JPG/PNG when `acceptImages=true`)
- Enforces 10 MB limit with user-facing error via sonner toast
- When `existingDoc` is provided: renders file-info card with status badge + "Reemplazar" button
- Rejection reasons: file-too-large vs wrong MIME type — separate error messages
- On success: invalidates `['mi-onboarding']` React Query key to trigger progress bar refresh

**OnboardingProgressBar.tsx:**
- Simple wrapper around shadcn `<Progress>` component
- Displays `{porcentaje}%` label and progress bar
- Reads `progreso_porcentaje` field from OnboardingStatus

## Decisions Made

1. **OnboardingRoute guard uses `tipo_usuario` field**, not role names — this is a direct field on the User object from authService, making it the simplest check.
2. **empleadoId in DocumentUploadZoneProps** is kept as a required prop for interface completeness; Plan 05 (tab pages) will pass it. Not used internally — not destructured.
3. **api.ts FormData guard already existed** (lines 149-151 in api.ts) — no modification required, deviation logged as N/A.

## Deviations from Plan

None — plan executed exactly as written. FormData guard in api.ts was already present as noted in the plan's "Check" instruction.

## Self-Check

Files created:
- front/src/features/onboarding/types/onboarding.ts: FOUND
- front/src/features/onboarding/services/onboardingUploadService.ts: FOUND
- front/src/features/onboarding/components/DocumentUploadZone.tsx: FOUND
- front/src/features/onboarding/components/OnboardingProgressBar.tsx: FOUND

Commits:
- d20ed7d: feat(01-04): install react-dropzone and define onboarding TypeScript types
- eddf5b9: feat(01-04): add OnboardingRoute guard, upload service, and shared UI components

Build: PASSED (npm run build succeeds, 2748 modules transformed)
Lint: PASSED (no ESLint errors in new files)

## Self-Check: PASSED
