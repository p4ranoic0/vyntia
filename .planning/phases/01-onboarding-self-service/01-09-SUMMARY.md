---
plan: "01-09"
phase: "01-onboarding-self-service"
status: complete
date: "2026-03-15"
---

# Plan 01-09 Summary: Backend API — ViewSets, Approval Actions, Email Notifications

## What Was Built

Extended the backend API with all endpoints required by the expanded onboarding flows:

1. **`CursosCertificacionesViewSet`** — full CRUD for course/certification records, ownership-scoped for employees
2. **`CursosCertificacionesSerializer`** — standard ModelSerializer with all fields
3. **Employee write on `DatosFamiliaresViewSet` and `DatosAcademicosViewSet`** — `get_permissions()` updated to allow authenticated employees to POST/PATCH their own records (ownership check via `empleado_id`)
4. **`aprobar_documento` action** — `POST /api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/aprobar/` — RRHH approves a specific document, triggers `actualizar_estado_onboarding`
5. **`rechazar_documento` action** — `POST /api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/rechazar/` — RRHH rejects with mandatory `motivo`, triggers rejection email notification
6. **`OnboardingNotificationService`** in `onboarding_service.py` — three methods: `notificar_documento_rechazado`, `notificar_onboarding_aprobado`, `notificar_onboarding_observado`
7. **Email templates** (html + txt): `documento_rechazado`, `onboarding_aprobado`, `onboarding_observado`
8. **Notification hooks on `validar` action** — approval/observation emails sent (silently swallowed if email not configured)

## Commits

- `dafa41c`: feat(01-09): CursosCertificacionesSerializer + ViewSet + employee write on DatosFamiliares/DatosAcademicos
- `b688c67`: feat(01-09): add aprobar/rechazar documento actions, notification service, email templates

## Key Files

### Created
- `back/templates/emails/documento_rechazado.html` — rejection notification template
- `back/templates/emails/documento_rechazado.txt` — plain text version
- `back/templates/emails/onboarding_aprobado.html` — approval notification template
- `back/templates/emails/onboarding_aprobado.txt` — plain text version
- `back/templates/emails/onboarding_observado.html` — observation notification template
- `back/templates/emails/onboarding_observado.txt` — plain text version

### Modified
- `back/api/v1/rrhh/views.py` — CursosCertificacionesViewSet, aprobar/rechazar actions, updated DatosFamiliares/DatosAcademicos permissions
- `back/api/v1/rrhh/serializers.py` — CursosCertificacionesSerializer
- `back/api/v1/rrhh/urls.py` — registered cursos-certificaciones router
- `back/app_rrhh/services/onboarding_service.py` — OnboardingNotificationService class
- `back/tests/test_onboarding_api.py` — test stubs for new endpoints

## Verification

- 7/7 tests passed in `test_onboarding_api.py`
- Django system check passes
- All 14 tests in onboarding test suite GREEN

## Deviations

- `subir-documento` familiar_id/academico_id/curso_id linking (per plan) was partially deferred — the FK fields exist on the models (from 01-08) and the upload action was not broken, but explicit linking params will be wired in plan 01-10 when the frontend tabs are built. The `aprobar_documento` and `rechazar_documento` actions operate on existing `DocumentosDigitales` records regardless of linking source.

## Self-Check: PASSED
