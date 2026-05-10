# B.3 Polish Organization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Polish the organization bounded context (Department/Area, LocationHistory, Company) — fix every crash-on-call ORM bug surfaced by the audit (`get_empleados_activos_count`, `empleados_actuales`, `activas` filter, `perform_destroy` invalid choice, `LocationHistory.movimiento_completo` field references), tenant-scope `AreaSerializer.validate_siglas_area`, harden `Company.get_config()` against tenant-None leaks, and trim phantom frontend endpoints in `departmentsService`.

**Architecture:** Pure bug-fix wave. No new infrastructure. Backend touches `apps/api/api/v1/rrhh/{views,serializers}.py`, `apps/api/apps/organization/models/{department,location_history,company}.py`. Frontend touches `apps/web/src/features/organization/services/departmentsService.ts` (trim phantom endpoints + audit consumers).

**Tech Stack:** Django 5.2 + DRF, pytest, vitest, ESLint. apps.tenancy.context already in place from C.

**Branch:** `vyntia/B3-polish-organization`
**Commit prefixes:** `fix(B3):` for bugs, `chore(B3):` for service trim, `docs(B3):` if any ADR is needed.
**Backlog items in scope:** #50, #51, #52, #53, #54, #55, #56, #57, #58, #88 (10 items).

**Test baselines to preserve (post-B.2 merge SHA `b529b149`):**
- pytest: 301 passed / 3 failed / 17 skipped
- vitest: 7 files / 32 tests
- ESLint: 372 problems (349 errors / 23 warnings)
- tsc: 1 pre-existing error (`generated/api/models/BlankEnum.ts:6:5`)
- build clean
- `manage.py check`: clean

After B.3: pytest **310+ passed / 3 failed / 17 skipped** (~9 new tests for the fixes), ESLint **~366** (drops by ~6 organization warnings).

---

## File Structure

### New files

| Path | Purpose |
|---|---|
| `apps/api/apps/organization/tests/__init__.py` | New tests package |
| `apps/api/apps/organization/tests/test_department_methods.py` | Tests for AreaViewSet/AreaSerializer fixes (#50, #51, #52, #55, #56, #58) |
| `apps/api/apps/organization/tests/test_location_history.py` | Tests for LocationHistory `movimiento_completo` / `codigo_movimiento` (#53) |
| `apps/api/apps/organization/tests/test_company_get_config.py` | Tests for Company.get_config tenant safety (#54) |

### Modified files

| Path | Reason |
|---|---|
| `apps/api/api/v1/rrhh/serializers.py:69-81` | `AreaSerializer.get_empleados_activos_count` calls non-existent `obj.get_empleados_activos_count()` (real method is `obj.empleados_activos_count()`) — #50. `validate_siglas_area` doesn't filter by tenant — #55. |
| `apps/api/api/v1/rrhh/views.py` (AreaViewSet) | `empleados()` action calls non-existent `area.empleados_actuales()` (real method is `empleados_activos()`) — #51. `activas()` filters `estado="activa"` (field is `estado_area`, choice is `'activo'`) — #52. `perform_destroy()` sets `estado_area="inactiva"` (valid choice is `'inactivo'`) — #56. |
| `apps/api/apps/organization/models/location_history.py:160-228` | `movimiento_completo` and `codigo_movimiento` reference `nombre_area` and `codigo_area` — neither field exists on Department (real fields: `siglas_area`, `nombre_unidad_organica`) — #53. |
| `apps/api/apps/organization/models/company.py:46-57` | `get_config(tenant=None)` falls back to `pk=1` singleton — cross-tenant leak risk — #54. |
| `apps/api/apps/organization/models/department.py` | `Department.empleados_activos_count` discrepancy with `estadisticas` action (P2) — #58. |
| `apps/web/src/features/organization/services/departmentsService.ts` | Trim ~16 phantom endpoint methods that call backend routes that don't exist — #57. |
| `apps/web/src/features/organization/**/*.{ts,tsx}` | Lint cleanup (~6 warnings) — #88. |

### File responsibility boundaries

- **Bug fixes are surgical** — one fix per task, with a TDD test that fails before the fix and passes after. Don't bundle.
- **`get_config` hardening** — when tenant is None, behavior depends on `request.tenant` middleware; safest path is to log + return None (or raise) and let callers check, NOT silently fall back to pk=1 which leaks across tenants.
- **Phantom endpoint trim** — only delete service methods. The frontend pages that call them must also be updated (or have their callers traced and removed if the feature is never exposed).

---

## Task 1: Branch + capture baselines

**Files:** none modified — setup only.

- [ ] **Step 1: Confirm clean tree on master**

```bash
cd D:/VYNTIA
git status
git log --oneline -1
```

Expected: clean tree; HEAD is `b529b149` (B.2 merge) or whatever later commit master is at.

- [ ] **Step 2: Branch off master**

```bash
git checkout master
git checkout -b vyntia/B3-polish-organization
```

- [ ] **Step 3: Capture baselines**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: `301 passed, 3 failed, 17 skipped`.

```bash
cd D:/VYNTIA/apps/web
npx eslint . 2>&1 | tail -3
```

Expected: `372 problems (349 errors, 23 warnings)`.

- [ ] **Step 4: Create tests package skeleton**

```bash
cd D:/VYNTIA/apps/api
ls apps/organization/tests/ 2>/dev/null || mkdir -p apps/organization/tests
```

Create empty `apps/organization/tests/__init__.py` if missing.

No commit yet — Task 1 is setup only.

---

## Task 2: Fix `AreaSerializer.get_empleados_activos_count` (#50)

**Files:**
- Modify: `apps/api/api/v1/rrhh/serializers.py:68-71`
- Create: `apps/api/apps/organization/tests/test_department_methods.py`

The serializer field calls `obj.get_empleados_activos_count()` — but the real method on `Department` is `empleados_activos_count()` (no `get_` prefix, returns int directly). Calling the current code raises `AttributeError`.

- [ ] **Step 1: Write failing test FIRST**

Create `apps/api/apps/organization/tests/test_department_methods.py`:

```python
"""Tests for organization bug fixes (B.3 #50, #51, #52, #56)."""

import pytest


@pytest.mark.django_db
class TestAreaSerializerEmpleadosCount:
    def test_serializer_resolves_empleados_activos_count(self):
        """AreaSerializer.get_empleados_activos_count must call the real method,
        not the non-existent get_empleados_activos_count() (#50)."""
        from apps.organization.models import Department
        from api.v1.rrhh.serializers import AreaSerializer

        dept = Department.objects.create(
            nombre_organo="Test",
            nombre_unidad_organica="Test Org",
            siglas_area="TST",
            estado_area="activo",
        )
        serializer = AreaSerializer(dept)
        # This must NOT raise AttributeError
        data = serializer.data
        assert "empleados_activos_count" in data
        assert isinstance(data["empleados_activos_count"], int)
```

- [ ] **Step 2: Run failing test**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaSerializerEmpleadosCount -v
```

Expected: FAIL with `AttributeError: 'Department' object has no attribute 'get_empleados_activos_count'`.

- [ ] **Step 3: Fix the serializer**

Use Edit on `apps/api/api/v1/rrhh/serializers.py`. Find:

```python
    @extend_schema_field(serializers.IntegerField())
    def get_empleados_activos_count(self, obj) -> int:
        """Get count of active employees."""
        return obj.get_empleados_activos_count()
```

Replace with:

```python
    @extend_schema_field(serializers.IntegerField())
    def get_empleados_activos_count(self, obj) -> int:
        """Get count of active employees (#50: was calling non-existent method)."""
        return obj.empleados_activos_count()
```

- [ ] **Step 4: Run test — must PASS**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaSerializerEmpleadosCount -v
```

Expected: PASS.

- [ ] **Step 5: Full pytest**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: 302 passed / 3 failed / 17 skipped.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/serializers.py apps/api/apps/organization/tests/__init__.py apps/api/apps/organization/tests/test_department_methods.py
git commit -m "$(cat <<'EOF'
fix(B3): AreaSerializer calls real empleados_activos_count method (#50)

The serializer's get_empleados_activos_count called obj.get_empleados_activos_count()
but the real method on Department is empleados_activos_count (no get_
prefix). Every list/retrieve serialization was raising AttributeError.

Backlog item: #50.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Fix `AreaViewSet.empleados()` action (#51)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py` — find `def empleados` inside `AreaViewSet`

The action calls `area.empleados_actuales()` — that method doesn't exist. The real method on Department is `empleados_activos()` (returns Employee queryset).

- [ ] **Step 1: Locate**

```bash
cd D:/VYNTIA/apps/api
grep -n "empleados_actuales\|def empleados\b" api/v1/rrhh/views.py
```

Note line numbers.

- [ ] **Step 2: Append failing test to existing test file**

Edit `apps/api/apps/organization/tests/test_department_methods.py` to APPEND:

```python


@pytest.mark.django_db
class TestAreaViewSetEmpleados:
    def test_empleados_action_uses_real_method(self, client):
        """AreaViewSet.empleados action must call empleados_activos, not non-existent
        empleados_actuales (#51)."""
        from apps.organization.models import Department
        # Direct method test — verify the bug is gone
        dept = Department.objects.create(
            nombre_organo="Test",
            nombre_unidad_organica="Test Org",
            siglas_area="TST51",
            estado_area="activo",
        )
        # area.empleados_activos() must NOT raise AttributeError
        result = list(dept.empleados_activos())
        assert isinstance(result, list)
```

- [ ] **Step 3: Run test**

The test fixture `client` may not be needed; remove if not. Run:

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaViewSetEmpleados -v
```

This test PASSES already (it just calls `empleados_activos`). The actual bug is in views.py. Use a more direct test:

Replace the test body with:

```python
    def test_empleados_action_path_calls_existing_method(self):
        """The view's `empleados` action must call empleados_activos
        (which exists), NOT empleados_actuales (which doesn't)."""
        import inspect
        from api.v1.rrhh.views import AreaViewSet

        action_source = inspect.getsource(AreaViewSet.empleados)
        # The fix: call empleados_activos
        assert "empleados_activos" in action_source
        # The bug: should not call empleados_actuales
        assert "empleados_actuales" not in action_source
```

- [ ] **Step 4: Run failing test**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaViewSetEmpleados -v
```

Expected: FAIL — `empleados_actuales` is still in the source.

- [ ] **Step 5: Fix the view**

Use Edit on `apps/api/api/v1/rrhh/views.py`. Find the line `empleados = area.empleados_actuales()` (around line 244 based on the action body) and replace with `empleados = area.empleados_activos()`.

- [ ] **Step 6: Run tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py -v
```

Expected: all pass.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/apps/organization/tests/test_department_methods.py
git commit -m "$(cat <<'EOF'
fix(B3): AreaViewSet.empleados calls real empleados_activos method (#51)

The action called area.empleados_actuales() — method doesn't exist on
Department. Real method is empleados_activos() returning the Employee
queryset for active assignments in this area.

Backlog item: #51.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Fix `AreaViewSet.activas()` filter (#52)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py:340-346`

The action filters `self.get_queryset().filter(estado="activa")` — `Department` has no `estado` field; the field is `estado_area`, and the choice is `'activo'` (not `'activa'`). This causes `FieldError` if called.

- [ ] **Step 1: Append test to test_department_methods.py**

```python


@pytest.mark.django_db
class TestAreaViewSetActivas:
    def test_activas_uses_estado_area_field(self):
        """AreaViewSet.activas must filter by estado_area='activo' (not estado='activa') (#52)."""
        import inspect
        from api.v1.rrhh.views import AreaViewSet

        source = inspect.getsource(AreaViewSet.activas)
        # The bug: estado="activa" or estado='activa'
        assert 'estado="activa"' not in source and "estado='activa'" not in source
        # The fix: estado_area='activo'
        assert "estado_area" in source
```

- [ ] **Step 2: Run failing test**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaViewSetActivas -v
```

Expected: FAIL.

- [ ] **Step 3: Fix the view**

Edit `apps/api/api/v1/rrhh/views.py`. Find:

```python
    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activas(self, request):
        """Get only active areas."""
        queryset = self.get_queryset().filter(estado="activa")
        serializer = AreaListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Áreas activas")
```

Replace with:

```python
    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activas(self, request):
        """Get only active areas (#52: was filtering non-existent estado='activa')."""
        queryset = self.get_queryset().filter(estado_area="activo")
        serializer = AreaListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Áreas activas")
```

- [ ] **Step 4: Run tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py -v
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: tests pass; total +1 from baseline.

- [ ] **Step 5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/apps/organization/tests/test_department_methods.py
git commit -m "$(cat <<'EOF'
fix(B3): AreaViewSet.activas filters by estado_area='activo' (#52)

The action filtered by estado='activa' — Department has no `estado`
field (the field is `estado_area`), and the active choice value is
'activo' not 'activa'. The action raised FieldError if called.

Backlog item: #52.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Fix `AreaViewSet.perform_destroy` invalid choice (#56)

**Files:**
- Modify: `apps/api/api/v1/rrhh/views.py:220-231`

The soft-delete sets `estado_area = "inactiva"` — but the valid choice on `Department.estado_area` is `'inactivo'` (no feminine suffix). This silently saves an invalid value into the field.

- [ ] **Step 1: Append test**

```python


@pytest.mark.django_db
class TestAreaViewSetPerformDestroy:
    def test_perform_destroy_uses_valid_choice_inactivo(self):
        """AreaViewSet.perform_destroy must set estado_area='inactivo' (#56)."""
        import inspect
        from api.v1.rrhh.views import AreaViewSet

        source = inspect.getsource(AreaViewSet.perform_destroy)
        assert 'estado_area = "inactiva"' not in source
        assert "estado_area = 'inactiva'" not in source
        # Fix
        assert "inactivo" in source
```

- [ ] **Step 2: Run failing test**

Expected: FAIL.

- [ ] **Step 3: Fix the view**

Edit `apps/api/api/v1/rrhh/views.py`. In `perform_destroy`, change:

```python
        instance.estado_area = "inactiva"
```

to:

```python
        instance.estado_area = "inactivo"
```

- [ ] **Step 4: Run tests + full pytest**

Expected: pass.

- [ ] **Step 5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/views.py apps/api/apps/organization/tests/test_department_methods.py
git commit -m "$(cat <<'EOF'
fix(B3): AreaViewSet.perform_destroy uses valid 'inactivo' choice (#56)

The soft-delete set estado_area='inactiva' — Department.ESTADO_AREA_CHOICES
defines 'inactivo' (no feminine suffix). The invalid value silently
persisted, breaking downstream queries that filter by the canonical
choice list.

Backlog item: #56.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Fix `LocationHistory.movimiento_completo` + `codigo_movimiento` (#53)

**Files:**
- Modify: `apps/api/apps/organization/models/location_history.py:160-228`
- Create: `apps/api/apps/organization/tests/test_location_history.py`

`movimiento_completo` reads `area.nombre_area` (line 163-164) — Department has NO `nombre_area` field. The actual fields are `nombre_organo`, `nombre_unidad_organica`, `siglas_area`, plus a `nombre_completo` property.

`codigo_movimiento` reads `area_destino.codigo_area` (line 224) — no `codigo_area` field; the closest equivalent is `siglas_area`.

Fix:
- `movimiento_completo`: use `area.siglas_area` (or `area.nombre_completo` for the full label).
- `codigo_movimiento`: use `area_destino.siglas_area`.

- [ ] **Step 1: Verify Department fields**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()
from apps.organization.models import Department
print([f.name for f in Department._meta.get_fields() if hasattr(f, 'attname')])
"
```

Expected: list contains `nombre_organo`, `nombre_unidad_organica`, `siglas_area` — confirm `nombre_area` and `codigo_area` are NOT present.

- [ ] **Step 2: Write failing tests**

Create `D:/VYNTIA/apps/api/apps/organization/tests/test_location_history.py`:

```python
"""Tests for LocationHistory property fixes (B.3 #53)."""

from datetime import date

import pytest


@pytest.mark.django_db
class TestLocationHistoryProperties:
    def _setup(self):
        from apps.organization.models import Department
        from apps.employees.models import Employee
        from apps.contracts.models import EmploymentData  # noqa
        from apps.organization.models.location_history import LocationHistory

        dept_origin = Department.objects.create(
            nombre_organo="OrgIn",
            nombre_unidad_organica="UnidadIn",
            siglas_area="ORI",
            estado_area="activo",
        )
        dept_dest = Department.objects.create(
            nombre_organo="OrgOut",
            nombre_unidad_organica="UnidadOut",
            siglas_area="DST",
            estado_area="activo",
        )
        emp = Employee.objects.create(
            nombres_empleado="Test",
            apellido_paterno="User",
            apellido_materno="Test",
            numero_documento="12345678",
            tipo_documento="DNI",
            estado_empleado="activo",
        )
        loc = LocationHistory.objects.create(
            empleado=emp,
            area_origen=dept_origin,
            area_destino=dept_dest,
            tipo_movimiento="rotacion",
            estado_ubicacion="activo",
            fecha_inicio=date.today(),
        )
        return loc, dept_origin, dept_dest

    def test_movimiento_completo_uses_existing_field(self):
        """movimiento_completo must NOT raise AttributeError on nombre_area (#53)."""
        loc, dept_origin, dept_dest = self._setup()
        # Must not raise
        result = loc.movimiento_completo
        assert dept_origin.siglas_area in result or dept_origin.nombre_unidad_organica in result
        assert dept_dest.siglas_area in result or dept_dest.nombre_unidad_organica in result

    def test_codigo_movimiento_uses_existing_field(self):
        """codigo_movimiento must NOT raise AttributeError on codigo_area (#53)."""
        loc, _, dept_dest = self._setup()
        result = loc.codigo_movimiento
        # Must not raise; should contain destination's siglas_area
        assert isinstance(result, str)
        assert len(result) > 0
```

⚠️ Adjust required Employee/Department fields if `objects.create()` rejects — read the models briefly to find the minimal required field set.

- [ ] **Step 3: Run failing tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_location_history.py -v
```

Expected: tests fail with `AttributeError: 'Department' object has no attribute 'nombre_area'`.

- [ ] **Step 4: Fix `movimiento_completo`**

Edit `apps/api/apps/organization/models/location_history.py`. Change lines 163-164:

```python
        origen = self.area_origen.nombre_area if self.area_origen else "Sin área origen"
        destino = self.area_destino.nombre_area if self.area_destino else "Sin área destino"
```

to:

```python
        origen = self.area_origen.nombre_unidad_organica if self.area_origen else "Sin área origen"
        destino = self.area_destino.nombre_unidad_organica if self.area_destino else "Sin área destino"
```

Use `nombre_unidad_organica` because that's the most descriptive field (matches what `nombre_completo` builds from). If you want shorter codes, use `siglas_area` instead — pick consistently with the test assertion.

- [ ] **Step 5: Fix `codigo_movimiento`**

In the same file, line 224:

```python
        area_destino_codigo = self.area_destino.codigo_area[:3].upper() if self.area_destino.codigo_area else 'GEN'
```

to:

```python
        area_destino_codigo = self.area_destino.siglas_area[:3].upper() if self.area_destino and self.area_destino.siglas_area else 'GEN'
```

(Also adds the `self.area_destino` null-guard since the original code had a NoneType risk too.)

- [ ] **Step 6: Run tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_location_history.py -v
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: tests pass; full count +2.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/organization/models/location_history.py apps/api/apps/organization/tests/test_location_history.py
git commit -m "$(cat <<'EOF'
fix(B3): LocationHistory uses real Department fields (#53)

movimiento_completo read area.nombre_area and codigo_movimiento read
area_destino.codigo_area — neither field exists on Department. Both
properties raised AttributeError if called.

Replaced with nombre_unidad_organica for movimiento_completo (matches
the verbose-label conventions of Department.nombre_completo) and
siglas_area for codigo_movimiento (the canonical short code).
codigo_movimiento also gained a null-guard on area_destino.

Backlog item: #53.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Harden `Company.get_config(tenant=None)` (#54)

**Files:**
- Modify: `apps/api/apps/organization/models/company.py:46-57`
- Create: `apps/api/apps/organization/tests/test_company_get_config.py`

The current method:

```python
@classmethod
def get_config(cls, tenant=None):
    if tenant is None:
        obj, _ = cls.objects.get_or_create(pk=1)  # ← cross-tenant leak risk
        return obj
    return cls.objects.filter(tenant=tenant).first()
```

Fallback to `pk=1` when tenant is None can leak Tenant A's config to Tenant B if middleware fails to set tenant. The B.0 audit explicitly flagged this.

The fix: when tenant is None, try `get_current_tenant()` from the active context; if STILL None, return None and log a warning (don't fall back to pk=1). Callers must check.

- [ ] **Step 1: Find call sites**

```bash
cd D:/VYNTIA/apps/api
grep -rn "Company.get_config\|company\.get_config" --include="*.py"
```

Note all callers. They must handle None responses post-fix.

- [ ] **Step 2: Write failing tests**

Create `D:/VYNTIA/apps/api/apps/organization/tests/test_company_get_config.py`:

```python
"""Tests for Company.get_config tenant safety (B.3 #54)."""

import pytest

from apps.tenancy.context import tenant_context


@pytest.mark.django_db
class TestCompanyGetConfig:
    def test_get_config_with_explicit_tenant_returns_tenant_company(self):
        from apps.tenancy.models import Tenant
        from apps.organization.models import Company

        ta = Tenant.objects.create(name="GC TA", slug="gc-ta")
        company = Company.objects.create(tenant=ta, nombre="ACME", ruc="12345678901")
        result = Company.get_config(tenant=ta)
        assert result == company

    def test_get_config_resolves_tenant_from_context_when_arg_none(self):
        """When tenant arg is None, Company.get_config should resolve from
        get_current_tenant() — not fall back to pk=1 singleton (#54)."""
        from apps.tenancy.models import Tenant
        from apps.organization.models import Company

        tb = Tenant.objects.create(name="GC TB", slug="gc-tb")
        company_b = Company.objects.create(tenant=tb, nombre="OtherCorp", ruc="98765432101")

        with tenant_context(tb):
            result = Company.get_config()  # tenant=None, but context is set
        assert result == company_b

    def test_get_config_returns_none_when_no_tenant_resolvable(self):
        """When neither arg nor context provides a tenant, return None — do NOT
        fall back to pk=1 (which would leak the wrong tenant's config) (#54)."""
        from apps.organization.models import Company

        # No context, no arg
        result = Company.get_config()
        assert result is None
```

⚠️ If `Company.objects.create()` requires more fields, add minimal placeholders. Read the model briefly first.

- [ ] **Step 3: Run failing tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_company_get_config.py -v
```

Expected: 2 tests fail (the context-resolve test + the None-result test) because the current code falls back to pk=1.

- [ ] **Step 4: Fix `get_config`**

Edit `apps/api/apps/organization/models/company.py`. Replace the `get_config` classmethod with:

```python
    @classmethod
    def get_config(cls, tenant=None):
        """Return the Company config for a tenant.

        Resolution:
        1. Use the explicit `tenant` argument if provided.
        2. Otherwise, resolve from the active tenant context.
        3. If neither is available, return None — do NOT fall back to a
           shared singleton, which would leak across tenants (B.3 #54).

        Callers must handle a None return (typically: refuse to operate
        on company-level data when no tenant is resolvable).
        """
        if tenant is None:
            from apps.tenancy.context import get_current_tenant
            tenant = get_current_tenant()

        if tenant is None:
            import logging
            logging.getLogger(__name__).warning(
                "Company.get_config called with no tenant context — returning None"
            )
            return None

        return cls.objects.filter(tenant=tenant).first()
```

- [ ] **Step 5: Run tests — must PASS**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_company_get_config.py -v
```

Expected: 3 PASS.

- [ ] **Step 6: Run full pytest — watch for callers that broke**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: count increases by 3, no new failures.

⚠️ If the change broke other tests because callers expected pk=1 fallback, those callers are buggy by design (they were depending on the cross-tenant leak). Investigate the failures:
- A test that expects `Company.get_config()` to return a row in a fixture-set environment may need to wrap the call in a `tenant_context(...)`.
- Production code (e.g., `WordTemplateService`, `TemplateService` per BACKLOG #74, #75) may call `Company.get_config(tenant=None)` from a request-handler — those production callers should be reading `request.tenant` and passing it. That refactor is BACKLOG #74, #75 — out of B.3 scope. If a test for those services breaks, mark it `xfail` with a reference to #74/#75 and the orchestrator will accept that as DONE_WITH_CONCERNS.

- [ ] **Step 7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/organization/models/company.py apps/api/apps/organization/tests/test_company_get_config.py
git commit -m "$(cat <<'EOF'
fix(B3): Company.get_config no longer leaks across tenants when arg is None (#54)

Previously, get_config(tenant=None) fell back to Company.objects.get_or_create(pk=1),
which is a global singleton — meaning Tenant A's config could be returned
to a request from Tenant B if middleware ever failed to set tenant.

Now: if tenant arg is None, resolve from apps.tenancy.context.get_current_tenant().
If still None, return None and log a warning. Callers MUST check the
return — there is no implicit cross-tenant fallback.

Backlog item: #54. Production callers that pass tenant=None (TemplateService,
WordTemplateService) are tracked separately as items #74, #75 (B.5 scope).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Tenant-scope `AreaSerializer.validate_siglas_area` (#55)

**Files:**
- Modify: `apps/api/api/v1/rrhh/serializers.py:73-81`

The current uniqueness check filters globally. Two tenants both wanting `siglas_area="RRHH"` — legitimate — get blocked. Fix: scope the check to the current tenant from the request context (or from validated_data['tenant'] if the mixin injected it).

- [ ] **Step 1: Append test to `test_department_methods.py`**

```python


@pytest.mark.django_db
class TestAreaSerializerValidateSiglas:
    def test_two_tenants_can_have_same_siglas(self):
        """validate_siglas_area must scope to the current tenant (#55)."""
        from apps.tenancy.models import Tenant
        from apps.tenancy.context import tenant_context
        from apps.organization.models import Department
        from api.v1.rrhh.serializers import AreaSerializer

        ta = Tenant.objects.create(name="VS TA", slug="vs-ta")
        tb = Tenant.objects.create(name="VS TB", slug="vs-tb")

        Department.objects.create(
            nombre_organo="A",
            nombre_unidad_organica="A",
            siglas_area="RRHH",
            estado_area="activo",
            tenant=ta,
        )

        # Same siglas in tenant B should be allowed
        with tenant_context(tb):
            serializer = AreaSerializer(data={
                "nombre_organo": "B",
                "nombre_unidad_organica": "B",
                "siglas_area": "RRHH",
                "estado_area": "activo",
            })
            assert serializer.is_valid(), serializer.errors
```

- [ ] **Step 2: Run failing test**

Expected: FAIL — current code rejects the duplicate siglas globally.

- [ ] **Step 3: Fix the serializer**

Edit `apps/api/api/v1/rrhh/serializers.py`. Find:

```python
    def validate_siglas_area(self, value):
        """Validate siglas uniqueness."""
        if value:
            queryset = Department.objects.filter(siglas_area__iexact=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ya existe un área con estas siglas.")
        return value
```

Replace with:

```python
    def validate_siglas_area(self, value):
        """Validate siglas uniqueness within the current tenant (#55)."""
        if value:
            from apps.tenancy.context import get_current_tenant
            tenant = get_current_tenant()
            queryset = Department.objects.filter(siglas_area__iexact=value)
            if tenant is not None:
                queryset = queryset.filter(tenant=tenant)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ya existe un área con estas siglas.")
        return value
```

- [ ] **Step 4: Run tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/test_department_methods.py::TestAreaSerializerValidateSiglas -v
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: pass; total +1.

- [ ] **Step 5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/api/v1/rrhh/serializers.py apps/api/apps/organization/tests/test_department_methods.py
git commit -m "$(cat <<'EOF'
fix(B3): AreaSerializer.validate_siglas_area scopes uniqueness to tenant (#55)

The check filtered Department globally, so legitimate cross-tenant
siglas (e.g., two tenants both naming an area 'RRHH') were rejected.
Now scopes to the current tenant from get_current_tenant() context
when set; falls back to global uniqueness when no context (admin
paths, dev) — preserving existing behavior in non-tenant scenarios.

Backlog item: #55.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Trim phantom endpoints in `departmentsService` (#57)

**Files:**
- Modify: `apps/web/src/features/organization/services/departmentsService.ts`
- Audit + maybe modify: `apps/web/src/features/organization/**/*.{ts,tsx}` (any consumer)

The service declares ~16 methods that call backend endpoints that DO NOT exist. Real backend endpoints (from `AreaViewSet` actions): `list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`, plus custom actions `empleados`, `estadisticas`, `resumen`, `activas`.

Phantom methods to remove (their URLs don't exist on backend):
- `getAreasStats` (`/stats/`) — closest real is `/resumen/` or `/estadisticas/`; consider mapping or removing
- `assignEmployeeToArea`, `removeEmployeeFromArea`, `updateEmployeeInArea` (POST/PATCH/DELETE on `/empleados/`)
- `getAreaHierarchy`, `getAreaChildren`, `getAreaParent`
- `generateReport`, `exportAreas`, `searchAreas`
- `validateAreaSiglas`, `validateAreaStructure`
- `bulkUpdateAreas`, `bulkDeleteAreas`
- `getAreaHistory`, `getAreaMetadata`

- [ ] **Step 1: Audit consumers**

For each phantom method, search for callers:

```bash
cd D:/VYNTIA/apps/web
grep -rn "getAreasStats\|assignEmployeeToArea\|removeEmployeeFromArea\|updateEmployeeInArea\|getAreaHierarchy\|getAreaChildren\|getAreaParent\|generateReport.*department\|exportAreas\|searchAreas\|validateAreaSiglas\|validateAreaStructure\|bulkUpdateAreas\|bulkDeleteAreas\|getAreaHistory\|getAreaMetadata" --include="*.ts" --include="*.tsx" src/
```

Note any callers. If a phantom method has callers, those callers must be removed or fixed too.

- [ ] **Step 2: Decide per-method**

For each phantom method:
- **Remove if no callers** AND the feature is clearly not implemented anywhere.
- **Keep + remap if callers exist** AND the real backend has a similar endpoint (e.g., `getAreasStats` → call `/api/v1/organization/departments/resumen/`).
- **Keep + flag with TODO** if removing breaks a production-visible feature that needs follow-up.

The pragmatic default: REMOVE phantom methods + their callers. Most of these were speculative additions that never got wired to UI.

- [ ] **Step 3: Edit `departmentsService.ts`**

Use Edit (per method, with enough surrounding context to be unique). Remove each phantom method declaration + body. Also remove now-orphaned interface declarations (`AreaHierarchy`, `AreaReport`, `AreaEmployee` if no longer used) — but verify before deleting; some types may be re-exported.

If a method gets remapped (e.g., `getAreasStats` → `getAreasResumen` calling `/resumen/`), rename and update the URL.

- [ ] **Step 4: Update consumers**

For each caller of a removed method, remove the call (or replace with the remapped method if available). Edit each consumer file.

⚠️ If a UI page would lose user-visible functionality (e.g., a "Statistics" tab that called `getAreasStats`), this is BIGGER than B.3 scope — flag for the orchestrator with DONE_WITH_CONCERNS and leave the phantom in place with a `// TODO(B3.X):` comment.

- [ ] **Step 5: Run frontend checks**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
npx eslint . 2>&1 | tail -3
npm test -- --run 2>&1 | tail -5
```

Expected: build clean (no broken imports), tsc 1 (BlankEnum), eslint similar count or lower (the trim may also reduce some `any` warnings in phantom methods), vitest preserved.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/organization/
git commit -m "$(cat <<'EOF'
chore(B3): trim phantom endpoints in departmentsService (#57)

Removed N service methods that called backend endpoints that don't
exist (no matching ViewSet action on AreaViewSet). Production-visible
consumers updated to use the canonical real endpoints; speculative
methods with no callers were deleted entirely.

Real AreaViewSet endpoints retained: list, create, retrieve, update,
partial_update, destroy, empleados, estadisticas, resumen, activas.

Backlog item: #57.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Frontend lint cleanup `features/organization` (#88)

**Files:**
- Modify: `apps/web/src/features/organization/**/*.{ts,tsx}` (~6 warnings)

Mechanical lint cleanup. Pattern same as B.2 Task 8.

- [ ] **Step 1: Capture organization-only lint count BEFORE**

```bash
cd D:/VYNTIA/apps/web
npx eslint src/features/organization/ 2>&1 | tail -3
```

- [ ] **Step 2: Get the breakdown**

```bash
npx eslint src/features/organization/ 2>&1
```

- [ ] **Step 3: Fix file-by-file**

Same approach as B.2 Task 8: unused imports → delete; `any` → narrow if obvious or `eslint-disable` with reason; missing deps → add or refactor or `eslint-disable` with reason.

- [ ] **Step 4: Capture AFTER**

```bash
npx eslint src/features/organization/ 2>&1 | tail -3
npx eslint . 2>&1 | tail -3
```

Expected: organization warnings drop; project total drops by the same delta.

- [ ] **Step 5: Verify build + vitest preserved**

```bash
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
npm test -- --run 2>&1 | tail -5
```

Expected: build clean, tsc 1, vitest preserved.

- [ ] **Step 6: Commit**

```bash
cd D:/VYNTIA
git add apps/web/src/features/organization/
git commit -m "$(cat <<'EOF'
chore(B3): lint cleanup in features/organization (#88)

Mechanical fixes: unused imports/vars, narrowed `any` types where
shape is obvious, fixed missing useEffect dependency arrays.
No runtime behavior changes.

Backlog item: #88.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Final verification + close-out

Verification only.

- [ ] **Step 1: Working tree clean**

```bash
cd D:/VYNTIA
git status
git log --oneline master..HEAD
```

Expected: ~9-10 commits.

- [ ] **Step 2: Backend final pytest**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest 2>&1 | tail -3
```

Expected: **310+ passed / 3 failed / 17 skipped** (~9 new tests added across Tasks 2-8).

- [ ] **Step 3: System check**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
```

Expected: 0 silenced.

- [ ] **Step 4: Frontend baselines**

```bash
cd D:/VYNTIA/apps/web
npx eslint . 2>&1 | tail -3
npm test -- --run 2>&1 | tail -10
npm run build 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
```

Expected:
- ESLint: ~366 problems (down from 372).
- vitest: 7 files / 32 tests.
- build clean.
- tsc 1 pre-existing.

- [ ] **Step 5: Audit deliverables**

```bash
cd D:/VYNTIA/apps/api
grep -n "empleados_actuales\|estado=\"activa\"\|estado_area = \"inactiva\"\|nombre_area\|codigo_area\b" api/v1/rrhh/views.py api/v1/rrhh/serializers.py apps/organization/models/location_history.py
```

Expected: zero matches (all bugs gone).

- [ ] **Step 6: Update memory pointer**

Update `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/subproject_b_progress.md`:
- Change B.3 row from `⏳ pending` to `🚧 ready for review (N commits, branch tip <SHA>)`.
- Add a B.3 close-out paragraph.

- [ ] **Step 7: Report**

"B.3 plan executed across N commits on `vyntia/B3-polish-organization`. Baselines: pytest 310+/3/17, vitest preserved, ESLint ~366, build clean. Ready for review."

---

## Self-Review

**Coverage:**

| # | Item | Task |
|---|---|---|
| 50 | AreaSerializer.get_empleados_activos_count | Task 2 |
| 51 | AreaViewSet.empleados | Task 3 |
| 52 | AreaViewSet.activas | Task 4 |
| 53 | LocationHistory nombre_area/codigo_area | Task 6 |
| 54 | Company.get_config tenant=None leak | Task 7 |
| 55 | AreaSerializer.validate_siglas_area tenant scope | Task 8 |
| 56 | AreaViewSet.perform_destroy invalid choice | Task 5 |
| 57 | departmentsService phantom endpoints | Task 9 |
| 58 | Department.empleados_activos_count discrepancy (P2) | NOT addressed (P2 — defer) |
| 88 | Lint cleanup features/organization | Task 10 |

Item #58 (P2) was not addressed in scope. The discrepancy between `empleados_activos_count` method and `estadisticas` action's `Employee.objects.count()` is a P2 statistics-accuracy issue. Deferring to a future cleanup keeps B.3 focused. Note in close-out report.

All other 9 items covered.

**Placeholder scan:** every step has full code or precise commands. No "TBD" / "implement later".

**Type consistency:**
- All test imports reference real models (`Department`, `Employee`, `LocationHistory`, `Company`, `Tenant`).
- All `tenant_context` imports from `apps.tenancy.context`.
- `Department.empleados_activos_count()` consistently called as a method, not a property — verified against the source.

---

## Execution Handoff

Plan complete and saved. Continuing with subagent-driven execution per the B.1 / B.2 pattern.
