# B.5 Polish Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Polish the contracts bounded context — fix `ContratosAdendasViewSet` query-param collision and tenant-leak in stats, fix the long list of `DatosLaboralesViewSet`/Filter/Serializer field bugs surfaced by L3.10.x renames, clean stale post-split TS interface fields, fix the stale apps.py docstring, and lint-clean `features/contracts`.

**Architecture:** Pure bug-fix wave on `apps/api/api/v1/rrhh/contratos_views.py` + `apps/api/api/v1/rrhh/serializers.py` + `apps/api/api/v1/rrhh/filters.py` + frontend `apps/web/src/features/contracts/`. No new infrastructure.

**Branch:** `vyntia/B5-polish-contracts`
**Backlog items:** #60, #61, #62, #63, #64, #65, #66, #67, #71, #73 + lint piece of #90 (10 items in scope).
**Out of scope:** #72 (ContractAmendment UI — 1w feature, deferred); #74-#79 (documents) → B.5b; #38, #39 (smoke tests) → B.16.

**Test baselines (post-B.4 SHA `0b3a3c99`):**
- pytest 323/3/17, vitest 7 files / 32, ESLint 291, tsc 1, build clean.

After B.5: pytest **332+/3/17**, ESLint dropped by ~contracts-feature warnings.

---

## Task 1: Branch + plan

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/B5-polish-contracts
git add docs/superpowers/plans/2026-05-10-vyntia-B5-polish-contracts.md
git commit -m "docs(B5): plan for polish contracts (10 backlog items in scope)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
mkdir -p apps/api/apps/contracts/tests
touch apps/api/apps/contracts/tests/__init__.py
```

Capture pytest baseline 323/3/17.

---

## Task 2: Fix `ContratosAdendasViewSet` (#60, #61, #62)

**Files:** `apps/api/api/v1/rrhh/contratos_views.py:87-128, 294+, 365+`

Bugs:
- **#60** (line 94-95): `empleado_id = self.request.query_params.get("id")` and `area_id = self.request.query_params.get("id")` — BOTH read the SAME `id` query param. A request `?id=X` triggers `filter(empleado_id=X, area_id=X)` which intersects (wrong). Fix: read distinct query params (`empleado`, `area`).
- **#60 also**: line 111 `queryset = queryset.filter(estado=estado)` — Contract.estado was renamed to `status` in L3.10.4d. Should filter `status=...`. Also line 149 `estado="ACTIVO"` → `status="activo"` (note the case).
- **#61** (around line 294): `estadisticas` action queries `Contract.objects.<X>` directly without tenant filter — leaks counts cross-tenant. Replace with `self.get_queryset().<X>` (mixin handles tenant).
- **#62** (around line 365): `renovar_contrato` action creates a new Contract via `serializer.save(...)`. Verify it propagates tenant. If it bypasses `perform_create` (uses `serializer.save(tenant=...)` directly), already fixed in B.1. Verify by reading.

Verify Contract field names:

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()
from apps.contracts.models import Contract
print([f.name for f in Contract._meta.fields])
"
```

Expected: `status` (not `estado`) is in the list. `area` (FK) auto-column `area_id`.

**TDD test (apps/api/apps/contracts/tests/test_contratos_adendas_viewset.py):**

```python
"""Tests for ContratosAdendasViewSet bug fixes (B.5 #60, #61)."""

import inspect


class TestQueryParamsDistinct:
    def test_empleado_and_area_use_distinct_query_params(self):
        """get_queryset must read empleado_id and area_id from DISTINCT query
        params, not both from `id` (#60)."""
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet

        src = inspect.getsource(ContratosAdendasViewSet.get_queryset)
        # Bug pattern: two params both reading 'id'
        # The body must NOT have empleado_id and area_id both calling .get("id")
        # Safer assertion: at least 2 distinct param names appear
        assert 'query_params.get("empleado")' in src or 'query_params.get("empleado_id")' in src
        assert 'query_params.get("area")' in src or 'query_params.get("area_id")' in src
        # The bug: both reading "id"
        assert src.count('query_params.get("id")') < 2

    def test_filter_uses_status_not_legacy_estado(self):
        """Contract field is `status` post-L3.10.4d, not legacy `estado`."""
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet

        src = inspect.getsource(ContratosAdendasViewSet.get_queryset)
        assert "filter(estado=" not in src


class TestEstadisticasTenantScope:
    def test_estadisticas_uses_get_queryset_not_global(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet

        src = inspect.getsource(ContratosAdendasViewSet.estadisticas)
        # Should use self.get_queryset() to inherit tenant filter
        assert "Contract.objects.count()" not in src
        assert "self.get_queryset()" in src or "base = " in src or "qs = " in src
```

Run failing tests, then fix:

1. In `get_queryset` (around line 94-95): change to read distinct query params:
   ```python
   empleado_id = self.request.query_params.get("empleado")
   area_id = self.request.query_params.get("area")
   ```
2. Line 111: change `queryset.filter(estado=estado)` → `queryset.filter(status=estado)` (the variable name `estado` can stay).
3. Line 149: `estado="ACTIVO"` → `status="activo"`.
4. In `estadisticas`: replace `Contract.objects.<X>` with `self.get_queryset().<X>`.

For #62, verify `renovar_contrato` in the source. The B.1 audit (in B.1 Task 10 reporting) already showed renovar_contrato had explicit tenant injection. Verify it's still there. If not, add the guarded pattern.

Commit:

```
fix(B5): ContratosAdendasViewSet query-param collision + tenant scope (#60, #61, #62)
```

---

## Task 3: Fix `DatosLaboralesViewSet` field bugs + queryset duplicate (#63, #64, #67)

**Files:** `apps/api/api/v1/rrhh/contratos_views.py` — `DatosLaboralesViewSet` (search/grep)

Bugs:
- **#63** `search_fields` and `ordering_fields` reference non-existent fields. Inventory said: `DatosLaboralesViewSet.search_fields/ordering_fields reference non-existent fields`. Need to identify which are bad. Likely culprits: `regimen_laboral`, `puesto`, `categoria` may not exist as direct fields (could be on related Contract or computed). Verify per-field.
- **#64** `estadisticas_remuneracion` action uses non-existent `estado_laboral` and `remuneracion_mensual` fields. Real fields likely `estado_datos` and `sueldo_basico`.
- **#67** queryset is declared TWICE on the class (the first JOINs are dead code) — remove the dead first declaration.

**Verify EmploymentData fields:**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()
from apps.contracts.models import EmploymentData
print([f.name for f in EmploymentData._meta.fields])
"
```

Read the class definition (`class DatosLaboralesViewSet`) — note both `queryset = ...` declarations and which is which.

For each bad field name, replace with the real field. If the field is conceptually intended (e.g., `regimen_laboral`) but doesn't exist on the model, comment out the search_field entry with a TODO referencing this task.

**TDD test (test_datos_laborales_viewset.py):**

```python
"""Tests for DatosLaboralesViewSet field bug fixes (B.5 #63, #64, #67)."""

import inspect


class TestDatosLaboralesViewSetFieldRefs:
    def test_estadisticas_remuneracion_uses_real_fields(self):
        """estadisticas_remuneracion must NOT reference non-existent fields (#64)."""
        from api.v1.rrhh.contratos_views import DatosLaboralesViewSet

        src = inspect.getsource(DatosLaboralesViewSet.estadisticas_remuneracion)
        # Bugs: stale field names
        assert "estado_laboral" not in src
        assert "remuneracion_mensual" not in src

    def test_class_does_not_declare_queryset_twice(self):
        """Class body must not have two `queryset = ...` declarations (#67)."""
        from api.v1.rrhh.contratos_views import DatosLaboralesViewSet

        src = inspect.getsource(DatosLaboralesViewSet)
        # Count top-level queryset assignments — should be exactly 1
        # (anything containing 'queryset = ' that's not a method body)
        # Loose assertion: rare case where queryset = appears more than once at class level
        # Simpler: split lines and count "    queryset = " (4 spaces indent = class body)
        class_level_assigns = sum(1 for line in src.split("\n")
                                   if line.startswith("    queryset = "))
        assert class_level_assigns == 1, f"Found {class_level_assigns} queryset class-level assignments"
```

Apply fixes after running failing tests. Commit:

```
fix(B5): DatosLaboralesViewSet stale field refs + dedup queryset (#63, #64, #67)
```

---

## Task 4: Fix `DatosLaboralesFilter` non-existent field references (#65)

**Files:** `apps/api/api/v1/rrhh/filters.py` — `DatosLaboralesFilter`

Inventory said: 5 filters reference non-existent fields (reg_laboral, condicion, grupo_ocupacional, puesto, estado, remuneracion). For each:
- Verify if the field exists on EmploymentData.
- If it does, the filter is fine.
- If it doesn't, either:
  - Remove the filter (if the feature is not used).
  - Map to a related-model field if the intent is clear (e.g., `puesto` might map to Contract.cargo or EmploymentData.cargo_empleado).

Read the current filter:

```bash
grep -n "class DatosLaboralesFilter\|reg_laboral\|condicion\|grupo_ocupacional\|estado.*Filter\|remuneracion.*Filter" apps/api/api/v1/rrhh/filters.py
```

Apply fixes per-filter. TDD test verifies no `__non_existent_field` patterns remain.

Commit:

```
fix(B5): DatosLaboralesFilter removes/remaps stale field paths (#65)
```

---

## Task 5: Fix `DatosLaboralesSerializer` (#66)

**Files:** `apps/api/api/v1/rrhh/serializers.py` — `DatosLaboralesSerializer`

Bugs:
- `antiguedad_años` field name has tilde `ñ` — Python identifier OK but breaks if there's a typo. Verify the EmploymentData model has `antiguedad_anos` (no tilde) or `antiguedad`. The serializer ReadOnlyField may not resolve.
- `tiempo_servicio` ReadOnlyField — may not resolve (no such property on the model).

Read the model:

```bash
grep -n "antiguedad\|tiempo_servicio" apps/api/apps/contracts/models/employment_data.py
```

Find the EmploymentData properties or methods. Map the serializer fields correctly. If a field is purely computed and the model doesn't expose it, add a `@property` to the model OR change the serializer to use `SerializerMethodField`.

Commit:

```
fix(B5): DatosLaboralesSerializer maps to real model properties (#66)
```

---

## Task 6: Cleanup stale Contrato TS interface fields (#71)

**Files:** `apps/web/src/features/contracts/services/contractsService.ts` (or wherever the Contract interface lives)

The Contract TS interface still has:
- `numero_adenda?: ...`
- `es_contrato_inicial?: ...`
- `es_adenda?: ...`

These fields don't exist on the backend Contract model post-L3.10.3 split. Remove them from the interface. Also audit consumers — any code that reads `contract.numero_adenda` etc. should be updated to use the ContractAmendment relation instead, OR removed if speculative.

Capture frontend tsc + lint before. Apply fix. Verify build clean.

Commit:

```
chore(B5): remove stale Contract TS fields post-L3.10.3 (#71)
```

---

## Task 7: Fix stale `apps/contracts/apps.py` docstring (#73)

**Files:** `apps/api/apps/contracts/apps.py`

Read the file. Find the docstring describing the pre-split unified Contract model. Replace with a docstring that reflects the post-split state (Contract + ContractAmendment as separate models).

Single-commit P3 cleanup.

```
chore(B5): update apps/contracts/apps.py docstring post-split (#73)
```

---

## Task 8: Frontend lint cleanup `features/contracts` (part of #90)

Same pattern as B.2/B.3/B.4. Capture before, fix, verify build/tsc/vitest preserved, commit.

```
chore(B5): lint cleanup features/contracts (#90 partial)
```

---

## Task 9: Final verification + close-out

- Capture final baselines.
- Audit no stale field refs remain.
- Update memory pointer.
- Report status.

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 60 | ContratosAdendasViewSet query-param collision | Task 2 |
| 61 | ContratosAdendasViewSet.estadisticas tenant | Task 2 |
| 62 | ContratosAdendasViewSet.renovar_contrato | Task 2 (verify; B.1 may have addressed) |
| 63 | DatosLaboralesViewSet search_fields/ordering_fields | Task 3 |
| 64 | DatosLaboralesViewSet.estadisticas_remuneracion | Task 3 |
| 65 | DatosLaboralesFilter | Task 4 |
| 66 | DatosLaboralesSerializer antiguedad/tiempo_servicio | Task 5 |
| 67 | DatosLaboralesViewSet queryset declared twice | Task 3 |
| 71 | Stale Contrato TS interface fields | Task 6 |
| 73 | apps.py stale docstring | Task 7 |
| 90 (contracts piece) | Lint cleanup | Task 8 |

Out of scope: #72 (ContractAmendment UI — 1w feature, defer). #38, #39 smoke tests → B.16. #74-#79, #80-#86 → B.5b.

Coverage: 10 of 10 in-scope items.
