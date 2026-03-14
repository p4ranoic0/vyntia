---
phase: 01-onboarding-self-service
plan: "02"
subsystem: backend-api
tags: [serializer, viewset, onboarding, email-correction, last-login]
dependency_graph:
  requires: [01-01]
  provides: [last_login field in onboarding list, corregir-correo endpoint, fecha_nacimiento in employee update]
  affects: [front/src/features/onboarding, Plan 05 personal tab]
tech_stack:
  added: []
  patterns: [DRF SerializerMethodField, DRF @action decorator, @require_hr() decorator]
key_files:
  modified:
    - back/api/v1/rrhh/serializers.py
    - back/api/v1/rrhh/views.py
    - back/tests/conftest.py
decisions:
  - conftest hr_usuario fixture must assign Administrador RRHH role via UsuarioRoles — tipo_usuario field alone is not checked by RRHHPermission or @require_hr()
metrics:
  duration: 6 min
  completed_date: "2026-03-14"
  tasks_completed: 3
  files_modified: 3
---

# Phase 01 Plan 02: Backend Serializer and Endpoint Additions Summary

**One-liner:** Added last_login to OnboardingEmpleadoSerializer, corregir-correo action on OnboardingViewSet, and fecha_nacimiento to EmpleadoUpdateSerializer — enabling RRHH to correct employee emails with auto-resend and the frontend to calculate no-response alerts.

## What Was Built

Three focused backend changes:

1. **last_login field** — `OnboardingEmpleadoSerializer` now exposes `usuario.last_login` as a nullable DateTimeField. Enables the frontend 5-day alert calculation on the RRHH onboarding panel.

2. **corregir-correo endpoint** — `POST /api/v1/rrhh/onboarding/{id}/corregir-correo/` updates `Empleado.correo_personal` and `Usuario.email` atomically, then reenvoys the welcome email. Returns 400 if `correo_personal` is missing, 403 if caller lacks RRHH role, 500 if SMTP fails.

3. **fecha_nacimiento in EmpleadoUpdateSerializer** — `PATCH /api/v1/rrhh/empleados/{id}/` now accepts `fecha_nacimiento`. Needed by Plan 05's personal tab form.

## Tasks

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add last_login to OnboardingEmpleadoSerializer | 7806afc | serializers.py, conftest.py |
| 2 | Add fecha_nacimiento to EmpleadoUpdateSerializer | 97d19e5 | serializers.py |
| 3 | Implement corregir-correo action on OnboardingViewSet | 88448c4 | views.py |

## Verification

- `TestOnboardingList::test_list_includes_last_login` — PASSED GREEN
- `TestCorregirCorreo::test_corregir_correo_updates_email` — PASSED GREEN
- `manage.py check --settings=config.settings.development` — 0 issues
- 6 remaining RED tests are Wave 0 scaffold tests for future plans (expected, in-scope)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed conftest hr_usuario missing role assignment**
- **Found during:** Task 1 verification (TestOnboardingList)
- **Issue:** `hr_usuario` fixture created a user with `tipo_usuario="rrhh"` but did not assign any `Rol` via `UsuarioRoles`. Both `RRHHPermission.has_permission()` (class-level) and `@require_hr()` decorator check `roles_activos()` which queries `UsuarioRoles`. Without a role assignment, both checks fail with PermissionDenied — the test got 403 before even reaching the serializer.
- **Fix:** Added `_assign_rrhh_role()` helper to conftest that creates/gets "Administrador RRHH" Rol and assigns it via `UsuarioRoles`. Updated `hr_usuario` fixture to call this helper.
- **Files modified:** `back/tests/conftest.py`
- **Commit:** 7806afc

## Decisions Made

- conftest hr_usuario fixture must assign Administrador RRHH role via UsuarioRoles — tipo_usuario field alone is not checked by RRHHPermission or @require_hr()

## Self-Check: PASSED
