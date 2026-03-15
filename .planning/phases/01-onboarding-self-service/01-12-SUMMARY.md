---
phase: 01-onboarding-self-service
plan: "12"
subsystem: frontend-onboarding
tags: [react, toast, document-upload, approval, progress-bar, ux]
dependency_graph:
  requires: ["01-09", "01-10", "01-11"]
  provides: ["Corregir y reenviar flow", "dual-value progress bar", "per-doc approval via onboarding endpoints"]
  affects: ["DocumentUploadZone", "OnboardingProgressBar", "OnboardingAdminPage"]
tech_stack:
  added: []
  patterns: ["comprehensive axios error handling", "onboarding-specific approval endpoints", "dual Progress bar display"]
key_files:
  created: []
  modified:
    - front/src/features/onboarding/components/DocumentUploadZone.tsx
    - front/src/features/onboarding/components/OnboardingProgressBar.tsx
    - front/src/features/onboarding/services/onboardingUploadService.ts
    - front/src/features/onboarding/pages/OnboardingEmployeePage.tsx
    - front/src/pages/onboarding/OnboardingAdminPage.tsx
decisions:
  - "OnboardingAdminPage handleValidarDocumento now calls /onboarding/{id}/documentos/{doc_id}/aprobar/ instead of legajoService.validar — ensures backend OnboardingNotificationService triggers email to employee"
  - "OnboardingAdminPage handleRechazarDocumentoConfirm now calls /onboarding/{id}/documentos/{doc_id}/rechazar/ with { motivo } body — triggers notificar_documento_rechazado email"
  - "DocumentUploadZone localOverrideEmpty state added for rejected-doc Corregir flow; existing showReplace kept for non-rejected replace flow"
  - "OnboardingProgressBar made both progreso_porcentaje and porcentaje optional for backward compatibility; uses ?? fallback chain"
  - "subirDocumento added alongside existing uploadDocument — new function includes empleadoId, categoria, nivel_acceso, and extraFields merge"
metrics:
  duration: "18 min"
  completed_date: "2026-03-15"
  tasks_completed: 2
  files_changed: 5
---

# Phase 1 Plan 12: Document Approval UI + Toast Coverage — Summary

## One-liner

Per-document RRHH approval via onboarding-specific endpoints (triggering email notifications), "Corregir y reenviar" flow for rejected docs, dual-value progress bar showing upload% and approved%, and comprehensive toast coverage for all upload error types.

## What Was Built

### Task 1: DocumentUploadZone, OnboardingProgressBar, onboardingUploadService

**DocumentUploadZone.tsx:**
- Added `localOverrideEmpty` state: when `existingDoc.estado_documento === 'rechazado'`, shows a "Corregir y reenviar" button (red outline variant) instead of the generic "Reemplazar" button
- Clicking "Corregir y reenviar" sets `localOverrideEmpty(true)`, rendering the dropzone (preview flow) as if no doc existed; on upload success, `localOverrideEmpty` is reset to false
- Replaced minimal error handling with comprehensive toast coverage: `ERR_NETWORK` code -> `toast.error` with connection message; HTTP 400 -> `toast.warning` with backend message; other -> `toast.error`
- Success upload -> `toast.success('Documento enviado correctamente')`
- Updated `onDropRejected` with specific messages per error code: `file-too-large`, `file-invalid-type` (split by `acceptImages`), and fallback

**OnboardingProgressBar.tsx:**
- Updated props interface to accept `progreso_porcentaje?: number` and `progreso_aprobado?: number` plus legacy `porcentaje?: number` alias
- Renders two separate Progress bars: first with muted/gray styling for "Documentos subidos", second with green styling (`[&>div]:bg-green-500`) for "Documentos aprobados"
- Summary text line below both bars: `{uploaded}% subido — {approved}% aprobado`

**onboardingUploadService.ts:**
- Added `subirDocumento(empleadoId, tipoDocumento, categoria, label, file, extraFields?)` function
- Includes `empleado`, `categoria`, `estado_documento: 'pendiente_revision'`, `nivel_acceso: 'restringido'` fields in FormData
- `extraFields` (optional `Record<string, string | number>`) merged into FormData via `Object.entries()`
- Existing `uploadDocument` and `uploadFoto` kept unchanged

**OnboardingEmployeePage.tsx:**
- Updated `OnboardingProgressBar` call site to pass `progreso_porcentaje` and `progreso_aprobado` props

### Task 2: OnboardingAdminPage per-document approval panel

**OnboardingAdminPage.tsx:**
- Added `import { apiClient } from '@/lib/api'` to enable direct API calls
- Updated `handleValidarDocumento` to call `/api/v1/rrhh/onboarding/{onboarding_id}/documentos/{docId}/aprobar/` — this triggers `notificar_onboarding_aprobado` email via backend `OnboardingNotificationService` (ONBD-14)
- Updated `handleRechazarDocumentoConfirm` to call `/api/v1/rrhh/onboarding/{onboarding_id}/documentos/{rechazarDocId}/rechazar/` with `{ motivo }` body — triggers `notificar_documento_rechazado` email
- Toast message for rejection updated to: "Documento rechazado y notificacion enviada al empleado"
- Document list updated: Aprobar (ShieldCheck) button shown for all non-`aprobado` docs; Rechazar (XCircle) button shown for all non-`rechazado` docs (previously both only showed for `pendiente_revision`)
- Existing rejection dialog (motivo textarea) unchanged — already correctly structured

## Deviations from Plan

### Scope Simplifications

**1. [Rule 1 - Adaptation] Reused existing dialog structure in OnboardingAdminPage**
- **Found during:** Task 2
- **Issue:** The plan suggested adding a new `useMutation` from React Query and a new `documentos` useQuery. But OnboardingDetailDialog already had fully functional state-based document loading via `legajoService.getByEmpleado()` and a rejection dialog.
- **Fix:** Rather than duplicating state management with React Query mutations, updated the existing `handleValidarDocumento` and `handleRechazarDocumentoConfirm` functions to call the onboarding-specific endpoints via `apiClient.post()`. The existing pattern (local state + async functions) is consistent with the rest of the component and avoids introducing a second state management system for the same data.
- **Files modified:** `front/src/pages/onboarding/OnboardingAdminPage.tsx`

**2. [Rule 3 - Compat] OnboardingProgressBar props made optional for backward compatibility**
- **Found during:** Task 1
- **Issue:** Changing `progreso_porcentaje` from required to the new interface would break existing call site that used `porcentaje`.
- **Fix:** Made `progreso_porcentaje` optional with `?` and kept `porcentaje` alias; fallback chain `progreso_porcentaje ?? porcentaje ?? 0` handles both.
- **Files modified:** `front/src/features/onboarding/components/OnboardingProgressBar.tsx`

## Success Criteria Verification

- [x] DocumentUploadZone: "Corregir y reenviar" button shown when `estado === 'rechazado'`
- [x] DocumentUploadZone: clicking "Corregir y reenviar" sets `localOverrideEmpty(true)` -> shows dropzone
- [x] DocumentUploadZone: rejection reason (`existingDoc.observaciones`) shown below red badge
- [x] DocumentUploadZone: `handleUpload` has `toast.success` on success, `toast.error`/`toast.warning` on various error codes
- [x] DocumentUploadZone: network error (ERR_NETWORK) shows red toast with connection message
- [x] OnboardingProgressBar: shows `progreso_porcentaje` (gray) AND `progreso_aprobado` (green) as two distinct values
- [x] OnboardingProgressBar: text below shows "{X}% subido — {Y}% aprobado"
- [x] onboardingUploadService.subirDocumento accepts optional `extraFields` merged into FormData
- [x] OnboardingAdminPage: document list shows Aprobar/Rechazar buttons per doc
- [x] OnboardingAdminPage: Rechazar opens existing Dialog with motivo textarea before calling rechazar endpoint
- [x] OnboardingAdminPage: Aprobar calls `/aprobar/` endpoint directly (triggers backend email via ONBD-14)
- [x] OnboardingAdminPage: rejection calls onboarding-specific endpoint with `{ motivo }` body
- [x] TypeScript: no type errors in modified files (manual review confirms correct typing)

## Self-Check

### Files Modified

- `front/src/features/onboarding/components/DocumentUploadZone.tsx` — FOUND
- `front/src/features/onboarding/components/OnboardingProgressBar.tsx` — FOUND
- `front/src/features/onboarding/services/onboardingUploadService.ts` — FOUND
- `front/src/features/onboarding/pages/OnboardingEmployeePage.tsx` — FOUND
- `front/src/pages/onboarding/OnboardingAdminPage.tsx` — FOUND

### Commits

- `6b66d201` — feat(01-12): DocumentUploadZone Corregir flow + dual-value progress bar
- `3a60b0ef` — feat(01-12): OnboardingAdminPage per-doc approval via onboarding endpoints

## Self-Check: PASSED
