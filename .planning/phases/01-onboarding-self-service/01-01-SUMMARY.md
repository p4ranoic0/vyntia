---
phase: 01-onboarding-self-service
plan: "01"
subsystem: testing
tags: [pytest, django, rest-framework, onboarding, tdd, red-green]

requires:
  - phase: 00-infrastructure-fixes
    provides: Working test settings (testing.py with SQLite in-memory DB)

provides:
  - conftest.py with onboarding_factory, hr_client, onboarding_client fixtures
  - test_onboarding_service.py with 5 RED tests targeting ONBD-01, ONBD-04 to ONBD-07
  - test_onboarding_api.py with 3 RED tests targeting ONBD-01, ONBD-03, ONBD-08
  - SQLite-compatible migration (NOW() -> CURRENT_TIMESTAMP in migration 0020)

affects:
  - 01-02 (Wave 1 — will turn service tests GREEN)
  - 01-03 (Wave 1 — will turn API tests GREEN)
  - 01-04 (Wave 1 — photo upload GREEN)
  - 01-05 (Wave 1 — last_login serializer GREEN)

tech-stack:
  added: []
  patterns:
    - "conftest.py fixture pattern: onboarding_factory accepts **kwargs for OnboardingEmpleado field overrides"
    - "hr_client fixture: APIClient with JWT Bearer token from RefreshToken.for_user()"
    - "onboarding_client fixture: carries _onboarding attribute for test access to the onboarding instance"

key-files:
  created:
    - back/tests/conftest.py
    - back/tests/test_onboarding_service.py
    - back/tests/test_onboarding_api.py
  modified:
    - back/app_rrhh/migrations/0020_configuracion_uit_suspension_renta.py

key-decisions:
  - "Service RED tests assert dict return type from actualizar_estado_onboarding — Wave 1 must change method signature to return enriched dict with historial_cambio, notificacion_enviada, progreso_porcentaje"
  - "NOW() replaced with CURRENT_TIMESTAMP in migration 0020 — works on SQLite (test) and PostgreSQL/MySQL (prod)"
  - "onboarding_factory fixture separates onboarding field kwargs from general kwargs, passes only known onboarding fields to OnboardingEmpleado.objects.create()"

patterns-established:
  - "Wave 0 RED pattern: tests import existing models/services correctly but assert behaviors not yet implemented"
  - "JWT fixture pattern: use RefreshToken.for_user(user) to get bearer token, set via client.credentials(HTTP_AUTHORIZATION=)"

requirements-completed:
  - ONBD-01
  - ONBD-03
  - ONBD-04
  - ONBD-05
  - ONBD-06
  - ONBD-07
  - ONBD-08

duration: 15min
completed: 2026-03-14
---

# Phase 01 Plan 01: Test Scaffold for Onboarding Self-Service Summary

**Wave 0 RED test scaffold — 8 failing pytest tests covering 7 onboarding requirements, with shared fixtures in conftest.py and a SQLite migration fix**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-14T04:52:21Z
- **Completed:** 2026-03-14T05:07:00Z
- **Tasks:** 1 (single TDD RED task)
- **Files modified:** 4

## Accomplishments

- Created `conftest.py` with three shared pytest fixtures: `onboarding_factory`, `hr_client`, `onboarding_client`
- Created `test_onboarding_service.py` with 5 RED tests covering service-level behaviors for ONBD-01, ONBD-04 through ONBD-07
- Created `test_onboarding_api.py` with 3 RED tests covering API endpoints for ONBD-01 (corregir-correo), ONBD-03 (photo upload), ONBD-08 (last_login in list)
- Fixed migration 0020 to use CURRENT_TIMESTAMP instead of NOW() — enables SQLite test DB to run migrations

## Task Commits

1. **Task 1: Wave 0 RED test scaffold** - `bd4d3c7` (test)

## Files Created/Modified

- `back/tests/conftest.py` — Shared fixtures: onboarding_factory (creates Empleado+Usuario+OnboardingEmpleado), hr_client (RRHH JWT client), onboarding_client (employee JWT client with _onboarding attribute)
- `back/tests/test_onboarding_service.py` — 5 RED tests: 4 for actualizar_estado_onboarding asserting enriched dict return, 1 for corregir_correo_personal (AttributeError RED)
- `back/tests/test_onboarding_api.py` — 3 RED tests: corregir-correo 404, photo upload tipo=foto, last_login in serializer
- `back/app_rrhh/migrations/0020_configuracion_uit_suspension_renta.py` — Replaced MySQL NOW() with CURRENT_TIMESTAMP for SQLite compatibility

## Decisions Made

- Wave 1 implementation of `actualizar_estado_onboarding` must change its return type from `OnboardingEmpleado` to a `dict` containing `historial_cambio`, `notificacion_enviada`, and `progreso_porcentaje` keys — this is what the RED tests assert
- `CURRENT_TIMESTAMP` is ANSI SQL and works on SQLite, PostgreSQL, and MySQL — safe cross-engine replacement for `NOW()`
- The `onboarding_factory` fixture separates onboarding-specific kwargs from general ones to avoid passing invalid fields to `OnboardingEmpleado.objects.create()`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed MySQL-only NOW() in migration 0020**
- **Found during:** Task 1 (running tests — collection hit migration failure)
- **Issue:** `migrations/0020_configuracion_uit_suspension_renta.py` used `NOW()` in a RunSQL INSERT. SQLite test DB raised `OperationalError: no such function: NOW`
- **Fix:** Replaced `NOW()` with `CURRENT_TIMESTAMP` (ANSI SQL, supported by SQLite + PostgreSQL + MySQL)
- **Files modified:** `back/app_rrhh/migrations/0020_configuracion_uit_suspension_renta.py`
- **Verification:** All 8 tests collected and failed RED (exit code 1, 0 collection errors)
- **Committed in:** `bd4d3c7` (Task 1 commit)

**2. [Rule 1 - Bug] Rewrote service tests to actually fail RED**
- **Found during:** Task 1 (first test run showed 4 service tests PASSING unexpectedly)
- **Issue:** Initial `TestActualizarEstado` tests set model flags then called `actualizar_estado_onboarding`, but the service overwrites those flags from actual DB documents. With a fully-populated Empleado, `datos_personales_completos` became True and estado moved to `pendiente_documentos` — satisfying `!= 'pendiente_datos'` assertion
- **Fix:** Rewrote service tests to assert that `actualizar_estado_onboarding` returns a `dict` with specific keys (`historial_cambio`, `notificacion_enviada`, `progreso_porcentaje`) — these don't exist yet, so all 4 fail RED
- **Files modified:** `back/tests/test_onboarding_service.py`
- **Verification:** All 8 tests FAILED (not PASSED or ERROR)
- **Committed in:** `bd4d3c7` (same task commit)

---

**Total deviations:** 2 auto-fixed (1 blocking migration fix, 1 test correctness bug)
**Impact on plan:** Both fixes necessary for RED scaffold to work correctly. No scope creep.

## Issues Encountered

- `actualizar_estado_onboarding` already exists and correctly handles state transitions, making naive "set flag + call service" tests pass instead of fail. Resolution: test for new return type shape that Wave 1 must implement.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All 8 RED tests are in place, discoverable, and failing correctly
- Wave 1 plans (02-05) can now turn specific tests GREEN as they implement each feature
- Migration 0020 fix applies to all existing tests — run full test suite to confirm no regressions

---
*Phase: 01-onboarding-self-service*
*Completed: 2026-03-14*
