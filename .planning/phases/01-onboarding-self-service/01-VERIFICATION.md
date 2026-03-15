---
phase: 01-onboarding-self-service
verified: 2026-03-15T13:00:00Z
status: passed
score: 16/16 success criteria verified
re_verification:
  previous_status: gaps_found
  previous_score: 15/16
  gaps_closed:
    - "ONBD-09 through ONBD-15 added to REQUIREMENTS.md (lines 25-31, all marked [x]); traceability table updated lines 159-165"
    - "ROADMAP.md plan markers for 01-08, 01-09, 01-10, 01-11, 01-13 all show [x] (confirmed lines 73-77)"
  gaps_remaining: []
  regressions: []
---

# Phase 01: Onboarding Self-Service — Full Verification Report

**Phase Goal:** Employees in onboarding receive credentials, log in to a restricted view, register all their data (personal, N dependents with required docs per relationship type, N academic records, N courses/diplomados, N work certs, N professional titles, laboral files only), preview documents before submitting with an explicit send button, track per-document approval status, and receive email notifications on approval/rejection — RRHH approves/rejects each document individually and validates or rejects the full onboarding.
**Verified:** 2026-03-15T13:00:00Z
**Status:** passed
**Re-verification:** Yes — third verification; supersedes 2026-03-15T12:00:00Z (gaps_found). Both previously identified documentation gaps confirmed resolved.

---

## Gap Re-verification

### Gap 1: ONBD-09 through ONBD-15 in REQUIREMENTS.md

**Previous status:** ONBD-09 through ONBD-15 absent from REQUIREMENTS.md — orphaned requirements.

**Verified fix:**
- `.planning/REQUIREMENTS.md` lines 25-31: all seven requirements present and marked `[x]`
- Traceability table lines 159-165: all seven mapped to "Phase 1 / Onboarding Self-Service / Complete"
- The requirements body (lines 25-31) defines each requirement in full detail

**Status: CLOSED**

### Gap 2: ROADMAP.md stale plan markers

**Previous status:** Plans 01-08, 01-09, 01-10, 01-11, 01-13 showed `[ ]` (incomplete) despite PASSED summaries.

**Verified fix:**
- `.planning/ROADMAP.md` line 73: `[x] 01-08-PLAN.md`
- `.planning/ROADMAP.md` line 74: `[x] 01-09-PLAN.md`
- `.planning/ROADMAP.md` line 75: `[x] 01-10-PLAN.md`
- `.planning/ROADMAP.md` line 76: `[x] 01-11-PLAN.md`
- `.planning/ROADMAP.md` line 78: `[x] 01-13-PLAN.md`

**Status: CLOSED**

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | Welcome email sent when onboarding user created; RRHH can correct wrong email and resend | VERIFIED | `corregir_correo` action in OnboardingViewSet (views.py line 2258); `reenviar_email_bienvenida` wired; amber banner in OnboardingAdminPage.tsx |
| 2  | Employee sees only own data sections; cannot access admin panel | VERIFIED | `OnboardingRoute` in App.tsx wraps `/` and `/dashboard`; `AdminRoute` blocks all `/admin*` routes; Plan 07 human verification Step 8 confirmed |
| 3  | Employee fills personal data fields (telefono, direccion, fecha_nacimiento, foto) | VERIFIED | `OnboardingTabPersonal.tsx` has react-hook-form with `telefono_celular`, `direccion_domicilio`, `fecha_nacimiento`; PATCH to `/api/v1/rrhh/empleados/{id}/`; `DocumentUploadZone` with `acceptImages=true` for photo |
| 4  | Employee registers N family dependents with required docs per parentesco | VERIFIED | `OnboardingTabFamiliar.tsx` rewritten with "Agregar dependiente" dialog; `createFamiliar()` from `onboardingDataService.ts`; per-parentesco upload zones (hijo: DNI+partida; conyuge: DNI+acta matrimonio; padre: DNI+partida) |
| 5  | Employee uploads own DNI/carnet de extranjeria | VERIFIED | `subir_documento` action on OnboardingViewSet; `DocumentUploadZone` for `dni` and `carnet_extranjeria` in Personal tab |
| 6  | Employee registers N certificados de estudio each with file upload | VERIFIED | `OnboardingTabAcademico.tsx` "Certificados de Estudio" accordion section; `createAcademico()` from `onboardingDataService.ts`; upload zone per item |
| 7  | Employee registers N cursos/diplomados each with file upload | VERIFIED | `OnboardingTabAcademico.tsx` "Cursos y Diplomados" accordion section; `createCurso()` from `onboardingDataService.ts`; upload zone per curso |
| 8  | Employee registers N constancias/certificados de trabajo each with file upload | VERIFIED | `OnboardingTabLaboral.tsx` "Experiencia Laboral" section; `getConstanciasTrabajo` from `onboardingDataService.ts`; `tipo_documento='constancia_trabajo'` upload zone per entry |
| 9  | Employee registers N titulos profesionales each with file upload | VERIFIED | `OnboardingTabAcademico.tsx` "Titulos Profesionales" accordion section; `createAcademico()` with nivel_educativo options; upload zone per titulo |
| 10 | Laboral tab: employee uploads files only, cannot edit RRHH-managed fields | VERIFIED | `OnboardingTabLaboral.tsx` read-only RRHH fields card with `LockKeyhole` icon; static upload zones for DDJJ, CV, carta de recomendacion |
| 11 | Before submitting any file: employee sees preview and confirms with explicit Enviar button | VERIFIED | `DocumentPreviewModal.tsx` — `URL.createObjectURL`, iframe for PDF, img for images; `DocumentUploadZone.tsx` `onDropAccepted` sets `pendingFile+isPreviewOpen` instead of calling upload directly; "Enviar documento" and "Cancelar" buttons; `revokeObjectURL` in useEffect cleanup |
| 12 | Each uploaded doc shows individual status; rejected docs show reason + Corregir y reenviar | VERIFIED | `DocumentUploadZone.tsx` `localOverrideEmpty` state; "Corregir y reenviar" button shown when `estado_documento === 'rechazado'`; rejection reason rendered below badge |
| 13 | Progress bar updates as documents are approved (not just uploaded) | VERIFIED | `OnboardingProgressBar.tsx` renders two Progress bars: uploaded% (gray) and `progreso_aprobado`% (green); `OnboardingEmpleado.progreso_aprobado` property in `onboarding.py` line 97 counts `estado_documento='aprobado'` documents |
| 14 | Employee receives email on onboarding approval; receives email with observations when observed | VERIFIED | `OnboardingNotificationService.notificar_onboarding_aprobado()` and `notificar_onboarding_observado()` in `onboarding_service.py` lines 588, 606; wired into `validar` action at views.py lines 2282, 2293; templates `onboarding_aprobado.html/txt` and `onboarding_observado.html/txt` exist; Plan 13 human verification Steps 14-15 confirmed |
| 15 | RRHH approves or rejects each document individually; can approve/reject full onboarding | VERIFIED | `aprobar_documento` action (views.py line 2304) and `rechazar_documento` action (line 2325) on OnboardingViewSet; `OnboardingAdminPage.tsx` calls `apiClient.post(.../documentos/{docId}/aprobar/)` and `apiClient.post(.../documentos/{rechazarDocId}/rechazar/)`; rejection Dialog with motivo textarea |
| 16 | Toast/notification feedback on every action: success, error, too-large, invalid format, network error | VERIFIED | `DocumentUploadZone.tsx` comprehensive error handling: `ERR_NETWORK` red toast; HTTP 400 `toast.warning`; other `toast.error`; `toast.success('Documento enviado correctamente')` on success; `onDropRejected` with specific messages per error code |

**Score:** 16/16 success criteria verified

---

### Required Artifacts — New Artifacts (Plans 08-13)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `back/app_rrhh/models/cursos_certificaciones.py` | CursosCertificaciones model | VERIFIED | 33 lines, `class CursosCertificaciones` at line 12, correct FK to Empleado and DocumentosDigitales |
| `back/app_rrhh/migrations/0025_datosacademicos_documento_and_more.py` | Migration for new model + FK additions | VERIFIED | File exists |
| `back/app_rrhh/models/__init__.py` | CursosCertificaciones exported | VERIFIED | Line 16: `from .cursos_certificaciones import CursosCertificaciones`; in `__all__` at line 55 |
| `back/app_rrhh/models/documentos_digitales.py` | `familiar` FK (SET_NULL to DatosFamiliares) | VERIFIED | Line 152: `familiar = models.ForeignKey(...)` |
| `back/app_rrhh/models/datos_academicos.py` | `documento` FK (SET_NULL to DocumentosDigitales) | VERIFIED | Line 117: `documento = models.ForeignKey(...)` |
| `back/app_rrhh/models/onboarding.py` | `progreso_aprobado` property | VERIFIED | Line 97: `def progreso_aprobado(self)` |
| `back/api/v1/rrhh/views.py` | `CursosCertificacionesViewSet` with ownership scope | VERIFIED | Line 1083; `get_queryset()` scopes to own employee; `create()` ownership check |
| `back/api/v1/rrhh/views.py` | `DatosFamiliaresViewSet` employee write enabled | VERIFIED | Lines 969-998; `get_permissions()` allows authenticated for CRUD; ownership check in `create()` |
| `back/api/v1/rrhh/views.py` | `DatosAcademicosViewSet` employee write enabled | VERIFIED | Lines 1036-1064; same pattern as DatosFamiliares |
| `back/api/v1/rrhh/views.py` | `aprobar_documento` and `rechazar_documento` nested actions | VERIFIED | Lines 2304, 2325; URL pattern `r"documentos/(?P<doc_id>[^/.]+)/aprobar"` and equivalent rechazar |
| `back/api/v1/rrhh/serializers.py` | `CursosCertificacionesSerializer` | VERIFIED | Line 215 |
| `back/api/v1/rrhh/urls.py` | `cursos-certificaciones` registered in router | VERIFIED | Line 63 |
| `back/app_rrhh/services/onboarding_service.py` | `OnboardingNotificationService` with 3 methods | VERIFIED | Lines 564, 568, 588, 606 |
| `back/templates/emails/documento_rechazado.html` | Rejection email template | VERIFIED | File exists, contains `nombre_documento` and `motivo` |
| `back/templates/emails/documento_rechazado.txt` | Plain text version | VERIFIED | File exists |
| `back/templates/emails/onboarding_aprobado.html` | Approval email template | VERIFIED | File exists, contains `nombre_empleado` |
| `back/templates/emails/onboarding_aprobado.txt` | Plain text version | VERIFIED | File exists |
| `back/templates/emails/onboarding_observado.html` | Observed email template | VERIFIED | File exists |
| `back/templates/emails/onboarding_observado.txt` | Plain text version | VERIFIED | File exists |
| `front/src/components/ui/accordion.tsx` | Accordion, AccordionItem, AccordionTrigger, AccordionContent | VERIFIED | 45 lines; all 4 components exported |
| `front/src/features/onboarding/services/onboardingDataService.ts` | 12 exported async functions | VERIFIED | 57 lines; `getFamiliares`, `createFamiliar`, `getAcademicos`, `createAcademico`, `getCursos`, `createCurso`, `getConstanciasTrabajo` + delete/update variants |
| `front/src/features/onboarding/components/DocumentPreviewModal.tsx` | Preview modal with iframe/img + Enviar/Cancelar | VERIFIED | 86 lines; `URL.createObjectURL` at line 31; `revokeObjectURL` at line 35; "Enviar documento" at line 87 |
| `front/src/features/onboarding/components/DocumentUploadZone.tsx` | Preview-before-upload + Corregir y reenviar + toasts | VERIFIED | `pendingFile` state (line 28); `isPreviewOpen` (line 29); `localOverrideEmpty` (line 27); "Corregir y reenviar" button (line 141); `DocumentPreviewModal` rendered (line 155) |
| `front/src/features/onboarding/components/OnboardingProgressBar.tsx` | Dual-value progress bar | VERIFIED | Props `progreso_porcentaje` and `progreso_aprobado` (lines 4-5); two Progress bars rendered |
| `front/src/features/onboarding/components/OnboardingTabFamiliar.tsx` | N-item familiar form with per-parentesco upload zones | VERIFIED | `getFamiliares`, `createFamiliar` imported; "Agregar dependiente" at line 139; parentesco-conditional upload zones |
| `front/src/features/onboarding/components/OnboardingTabAcademico.tsx` | 3 Accordion sections with N-item forms | VERIFIED | "Certificados de Estudio" (line 162), "Cursos y Diplomados" (line 212), accordion sections present |
| `front/src/features/onboarding/components/OnboardingTabLaboral.tsx` | N-item Experiencia Laboral + read-only RRHH fields + static zones | VERIFIED | "Experiencia Laboral" at line 163; `getConstanciasTrabajo` imported; RRHH read-only section present |
| `front/src/features/onboarding/services/onboardingUploadService.ts` | `subirDocumento` with `extraFields` param | VERIFIED | `subirDocumento` at line 24; `extraFields?: Record<string, string | number>` at line 30 |
| `front/src/pages/onboarding/OnboardingAdminPage.tsx` | Per-document approval panel calling onboarding-specific endpoints | VERIFIED | Lines 820-839; calls `/onboarding/{id}/documentos/{docId}/aprobar/` and `/documentos/{rechazarDocId}/rechazar/` |

### Previously Verified Artifacts (Plans 01-07) — Regression Check

All artifacts from the previous verification remain present and wired. No regressions detected.

---

### Key Link Verification — New Links (Plans 08-13)

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `cursos_certificaciones.py` | `DocumentosDigitales` | `documento FK (SET_NULL)` | WIRED | Pattern `ForeignKey.*DocumentosDigitales.*SET_NULL` confirmed at line 142 of cursos_certificaciones.py |
| `documentos_digitales.py` | `DatosFamiliares` | `familiar FK (SET_NULL)` | WIRED | Line 152 in documentos_digitales.py |
| `views.py` (OnboardingViewSet) | `onboarding_service.py` (OnboardingNotificationService) | `notificar_documento_rechazado` in `rechazar_documento` action | WIRED | views.py line 2343 calls `OnboardingNotificationService.notificar_documento_rechazado(...)` |
| `views.py` (validar action) | `onboarding_service.py` (OnboardingNotificationService) | `notificar_onboarding_aprobado` and `notificar_onboarding_observado` | WIRED | views.py lines 2282 and 2293 |
| `urls.py` | `CursosCertificacionesViewSet` | `router.register('cursos-certificaciones', ...)` | WIRED | urls.py line 63 |
| `DocumentUploadZone.tsx` | `DocumentPreviewModal.tsx` | `isPreviewOpen` state drives modal open prop | WIRED | Line 11 import; line 155 render; `isPreviewOpen` drives `isOpen` prop |
| `DocumentPreviewModal.tsx` | `URL.createObjectURL` | blob URL created on file prop + isOpen=true | WIRED | Line 31: `const url = URL.createObjectURL(file)` inside useEffect |
| `OnboardingTabFamiliar.tsx` | `onboardingDataService.ts` | `createFamiliar()` called on form submit | WIRED | Line 25 import; mutation at line 83 calls `createFamiliar(data)` |
| `OnboardingTabAcademico.tsx` | `onboardingDataService.ts` | `createCurso()` and `createAcademico()` on form submit | WIRED | Lines 32, 34 imports; mutations at lines 108, 119 |
| `OnboardingAdminPage.tsx` | `/api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/aprobar/` | `apiClient.post()` in approval handler | WIRED | Line 824: `apiClient.post(\`/api/v1/rrhh/onboarding/${onboarding.onboarding_id}/documentos/${docId}/aprobar/\`)` |
| `OnboardingAdminPage.tsx` | `/api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/rechazar/` | `apiClient.post()` with `{motivo}` in reject handler | WIRED | Line 839 with `{ motivo }` body |

---

### Requirements Coverage

| Requirement | Source Plans | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| ONBD-01 | 01-01, 01-02, 01-06, 01-07 | Welcome email + email correction + resend | SATISFIED | `corregir_correo` + `reenviar_email_bienvenida` wired; amber banner in admin |
| ONBD-02 | 01-04, 01-05, 01-07 | Employee restricted view, no admin panel | SATISFIED | `OnboardingRoute` + `AdminRoute`; Plan 07 human verification passed |
| ONBD-03 | 01-03, 01-04, 01-05, 01-07 | Employee uploads profile photo | SATISFIED | `subir_foto` action + `DocumentUploadZone acceptImages=true` in Personal tab |
| ONBD-04 | 01-03, 01-04, 01-05, 01-07 | Employee uploads personal PDF (DNI, carnet) | SATISFIED | `subir_documento` + DNI/carnet zones in Personal tab |
| ONBD-05 | 01-03, 01-04, 01-05, 01-07 | Employee uploads familiar PDFs | SATISFIED | `OnboardingTabFamiliar` N-item form with per-parentesco upload zones |
| ONBD-06 | 01-03, 01-04, 01-05, 01-07 | Employee uploads academic PDFs | SATISFIED | `OnboardingTabAcademico` with certificados, cursos, titulos accordion |
| ONBD-07 | 01-03, 01-04, 01-05, 01-07 | Employee uploads laboral PDFs without editing RRHH fields | SATISFIED | `OnboardingTabLaboral` read-only RRHH section + static upload zones + Experiencia Laboral |
| ONBD-08 | 01-01, 01-02, 01-06, 01-07 | RRHH sees completion percentage per employee | SATISFIED | `progreso_porcentaje` + dual-value `OnboardingProgressBar`; `computeAlert` for 5-day alert |
| ONBD-09 | 01-09, 01-10 | Employee can register N familiares with per-parentesco docs | SATISFIED | `DatosFamiliaresViewSet` employee write + `OnboardingTabFamiliar` N-item form; Plan 13 human verification passed |
| ONBD-10 | 01-08, 01-09, 01-10 | CursosCertificaciones CRUD + academic N-item forms | SATISFIED | `CursosCertificaciones` model + `CursosCertificacionesViewSet` + `OnboardingTabAcademico`; Plan 13 Steps 4, 7 passed |
| ONBD-11 | 01-09, 01-10 | Constancias de trabajo (N-item work history) | SATISFIED | `OnboardingTabLaboral` Experiencia Laboral; `getConstanciasTrabajo` + `constancia_trabajo` tipo_documento; Plan 13 Step 5 passed |
| ONBD-12 | 01-11, 01-12 | Document preview modal before upload; Corregir y reenviar | SATISFIED | `DocumentPreviewModal.tsx` + `DocumentUploadZone.tsx` `pendingFile` intercept + `localOverrideEmpty`; Plan 13 Steps 3, 12 passed |
| ONBD-13 | 01-08, 01-09, 01-12 | Per-document RRHH approval; progreso_aprobado | SATISFIED | `aprobar_documento` + `rechazar_documento` actions; dual-value progress bar; Plan 13 Steps 9-11 passed |
| ONBD-14 | 01-09, 01-12 | Email notifications for rejection, approval, observed | SATISFIED | `OnboardingNotificationService` with 3 methods + 6 templates; wired into `validar` and `rechazar_documento`; Plan 13 Steps 13-15 passed |
| ONBD-15 | 01-12 | Toast/notification coverage for all action types | SATISFIED | Comprehensive `toast.success/error/warning` in `DocumentUploadZone.tsx` handleUpload and onDropRejected; Plan 13 Step 7 passed |

All 15 requirements (ONBD-01 through ONBD-15) are SATISFIED. No orphaned requirements remain — ONBD-09 through ONBD-15 are now formally registered in REQUIREMENTS.md.

---

### Anti-Patterns Found

No stubs, empty implementations, placeholder returns, or TODO/FIXME comments found in any of the key onboarding implementation files across all 13 plans.

No documentation anti-patterns remain — both REQUIREMENTS.md and ROADMAP.md are now up to date.

---

### Human Verification Already Completed

**Plan 07 (Wave 4) — RRHH confirmed "aprobado" (15/15 steps):**
All baseline employee and RRHH flows verified including upload, progress bar, email correction, admin panel, and Dialog-based rejection.

**Plan 13 (Wave 8) — RRHH confirmed "aprobado" (16/16 steps):**
All expanded features verified including N-item familiar/academic/laboral forms, document preview modal, Corregir y reenviar flow, dual progress bar, RRHH per-document approval, and email notifications for all three notification types (rejection, approval, observed).

No additional human verification is required.

---

### Verification Summary

Phase 01: Onboarding Self-Service is fully complete.

- All 16 ROADMAP success criteria verified in code
- All 15 requirements (ONBD-01 through ONBD-15) satisfied and formally registered in REQUIREMENTS.md
- All plan markers in ROADMAP.md show `[x]` complete
- Two human verification checkpoints (Plan 07 and Plan 13) both passed
- No stubs, placeholders, or broken wiring found
- No remaining documentation gaps

The two previously identified documentation gaps (REQUIREMENTS.md missing ONBD-09 through ONBD-15, and ROADMAP.md stale plan markers) have both been confirmed resolved in this re-verification.

---

_Verified: 2026-03-15T13:00:00Z_
_Verifier: Claude (gsd-verifier)_
