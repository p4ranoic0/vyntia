---
phase: 00-infrastructure-fixes
plan: 02
subsystem: database
tags: [django, model, property, bug-fix, testing, pytest]

requires: []
provides:
  - "Fixed tamano_archivo_legible property on DocumentosDigitales — reads file size without mutating instance"
  - "Unit test suite (6 tests) proving property is idempotent and non-mutating"
affects: [any-phase-using-DocumentosDigitales]

tech-stack:
  added: []
  patterns:
    - "Use local variable `size = float(self.field)` in read-only property loops — never write back to instance attributes"

key-files:
  created:
    - back/tests/test_documentos_model.py
  modified:
    - back/app_rrhh/models/documentos_digitales.py

key-decisions:
  - "Use DocumentosDigitales.__new__() to test properties without DB dependency — avoids FK constraints during unit tests"

patterns-established:
  - "Property correctness: any property that divides a numeric field in a loop must copy to a local variable first"

requirements-completed: [INFRA-04]

duration: 12min
completed: 2026-03-13
---

# Phase 0 Plan 02: tamano_archivo_legible Mutation Bug Fix Summary

**Fixed silent data-corruption bug in DocumentosDigitales.tamano_archivo_legible where reading the property overwrote the stored byte count with a float (e.g., 2097152 -> 2.0), risking corrupt saves on any subsequent model.save() call**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-13T00:00:00Z
- **Completed:** 2026-03-13T00:12:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments

- Identified and fixed the mutation bug in `tamano_archivo_legible` (lines 242-252 of documentos_digitales.py)
- Introduced `size = float(self.tamano_archivo)` as a local variable so the division loop never writes back to `self.tamano_archivo`
- Wrote 6 pytest tests covering: no-mutation, idempotency, zero/None, bytes, KB, and GB boundary values
- Confirmed RED phase (tests caught the original bug: `assert 2.0 == 2097152` failure)
- Confirmed GREEN phase (all 6 tests pass after fix)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write failing test then fix tamano_archivo_legible (INFRA-04)** - `ee14f79` (feat)

**Plan metadata:** (to be committed with docs)

_Note: TDD task — tests written first (RED), then fix applied (GREEN) in single commit_

## Files Created/Modified

- `back/tests/test_documentos_model.py` - 6 unit tests proving tamano_archivo_legible is idempotent and non-mutating
- `back/app_rrhh/models/documentos_digitales.py` - Fixed tamano_archivo_legible property (lines 242-252)

### Exact Lines Changed in documentos_digitales.py

**Before (broken — mutates self.tamano_archivo):**
```python
@property
def tamano_archivo_legible(self):
    """Retorna el tamaño del archivo en formato legible."""
    if not self.tamano_archivo:
        return "0 B"

    for unidad in ['B', 'KB', 'MB', 'GB']:
        if self.tamano_archivo < 1024.0:
            return f"{self.tamano_archivo:.1f} {unidad}"
        self.tamano_archivo /= 1024.0      # BUG: mutates instance attribute
    return f"{self.tamano_archivo:.1f} TB"
```

**After (fixed — local variable, self.tamano_archivo never touched):**
```python
@property
def tamano_archivo_legible(self):
    """Retorna el tamaño del archivo en formato legible (solo lectura)."""
    if not self.tamano_archivo:
        return "0 B"

    size = float(self.tamano_archivo)
    for unidad in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unidad}"
        size /= 1024.0
    return f"{size:.1f} TB"
```

### Test Output (6 passed)

```
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_no_muta PASSED
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_idempotent PASSED
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_zero PASSED
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_bytes PASSED
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_kb PASSED
tests/test_documentos_model.py::TestTamanoArchivoLegible::test_tamano_legible_gb PASSED
======================== 6 passed, 1 warning in 0.12s =========================
```

### Confirmation: tamano_archivo Unchanged After Property Access

The test `test_tamano_legible_no_muta` directly asserts:
- Before fix: `doc.tamano_archivo` was `2.0` after reading the property (corrupted)
- After fix: `doc.tamano_archivo` remains `2097152` after both calls to `tamano_archivo_legible`

## Decisions Made

- Used `DocumentosDigitales.__new__(DocumentosDigitales)` to instantiate without DB: the model has mandatory FKs (Empleado, Usuario) so normal instantiation would require DB fixtures. `__new__` + direct attribute assignment tests the property logic in pure Python without DB connectivity.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- INFRA-04 complete: DocumentosDigitales.tamano_archivo_legible is safe to call at any point in a request/save cycle
- Methods that call `self.save()` after business logic (validar_documento, rechazar_documento, crear_nueva_version, marcar_como_vencido, renovar_documento, archivar_documento, cambiar_nivel_acceso, agregar_palabras_clave) can no longer persist a corrupted file size due to this property

---
*Phase: 00-infrastructure-fixes*
*Completed: 2026-03-13*
