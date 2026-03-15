---
phase: 01-onboarding-self-service
plan: "08"
subsystem: backend-models
tags: [models, migration, onboarding, cursos-certificaciones, wave-5]
dependency_graph:
  requires: []
  provides:
    - CursosCertificaciones model (db_table: cursos_certificaciones)
    - DocumentosDigitales.familiar FK to DatosFamiliares
    - DatosAcademicos.documento FK to DocumentosDigitales
    - OnboardingEmpleado.progreso_aprobado property
    - Migration 0025 applied to development DB
  affects:
    - plan 01-09 (CursosCertificaciones ViewSet endpoints depend on this model)
    - plan 01-10 (frontend forms depend on new FK fields)
tech_stack:
  added: []
  patterns:
    - AutoField PK pattern (curso_id) matching existing models
    - SET_NULL FK pattern for optional document linkage
    - Lazy import inside property to avoid circular imports
key_files:
  created:
    - back/app_rrhh/models/cursos_certificaciones.py
    - back/app_rrhh/migrations/0025_datosacademicos_documento_and_more.py
  modified:
    - back/app_rrhh/models/documentos_digitales.py
    - back/app_rrhh/models/datos_academicos.py
    - back/app_rrhh/models/onboarding.py
    - back/app_rrhh/models/__init__.py
    - back/tests/test_onboarding_service.py
decisions:
  - "CursosCertificaciones unique_together on [empleado, nombre_curso, institucion, fecha_inicio] prevents duplicate course entries per employee"
  - "progreso_aprobado uses lazy import of DocumentosDigitales inside property to avoid circular import with onboarding.py"
  - "Test stubs use onboarding_factory fixture (not onboarding) — the latter does not exist in conftest.py"
metrics:
  duration: "12 min"
  completed_date: "2026-03-15"
  tasks_completed: 2
  files_changed: 7
---

# Phase 01 Plan 08: CursosCertificaciones Model + DB Migration Summary

**One-liner:** CursosCertificaciones model with Empleado/DocumentosDigitales FKs, nullable FKs on DocumentosDigitales and DatosAcademicos, progreso_aprobado property, and migration 0025.

## What Was Built

Provides the data layer foundation for Wave 5 N-item forms:

1. **CursosCertificaciones model** (`cursos_certificaciones` table): Tracks employee courses and certifications with optional link to a DocumentosDigitales record (curso certificate scan). Fields: `curso_id`, `empleado`, `nombre_curso`, `institucion`, `fecha_inicio`, `fecha_fin`, `horas`, `descripcion`, `documento`, `estado_registro`, timestamps.

2. **DocumentosDigitales.familiar FK**: Nullable FK to DatosFamiliares (SET_NULL on delete). Allows a digital document to be associated with a specific family member.

3. **DatosAcademicos.documento FK**: Nullable FK to DocumentosDigitales (SET_NULL on delete). Allows linking an academic record to its scanned certificate/diploma.

4. **OnboardingEmpleado.progreso_aprobado property**: Returns int 0-100 representing percentage of employee's current documents with `estado_documento='aprobado'`. Separate from `progreso_porcentaje` (upload checklist).

5. **Migration 0025** (`0025_datosacademicos_documento_and_more.py`): Applied cleanly to development PostgreSQL database.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create CursosCertificaciones model + FK fields | bb5ab3f | cursos_certificaciones.py, documentos_digitales.py, datos_academicos.py, __init__.py |
| 2 | Generate migration 0025, add progreso_aprobado, test stubs | 2c5d76b | migrations/0025_*.py, onboarding.py, test_onboarding_service.py |

## Verification

```
10 passed, 1 warning in 6.80s
```
All tests in `test_onboarding_service.py` and `test_onboarding_api.py` GREEN.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed fixture reference in test stub**
- **Found during:** Task 2 test run
- **Issue:** Plan specified `def test_progreso_aprobado_property_exists(self, onboarding)` but `onboarding` fixture does not exist in conftest.py — only `onboarding_factory` is available
- **Fix:** Changed parameter to `onboarding_factory` and added `onboarding = onboarding_factory()` call inside the test
- **Files modified:** `back/tests/test_onboarding_service.py`
- **Commit:** 2c5d76b

## Self-Check: PASSED

- FOUND: back/app_rrhh/models/cursos_certificaciones.py
- FOUND: back/app_rrhh/migrations/0025_datosacademicos_documento_and_more.py
- FOUND: .planning/phases/01-onboarding-self-service/01-08-SUMMARY.md
- FOUND commit bb5ab3f: Task 1 — model files
- FOUND commit 2c5d76b: Task 2 — migration, property, test stubs
