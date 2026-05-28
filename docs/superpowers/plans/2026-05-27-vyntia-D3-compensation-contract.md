# D.3 — Compensation Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the tenant-scoped `Compensation` model as the **single source of truth** for an employee's salary + régimen + pension + health + banking snapshot, versioned by `(valid_from, valid_to)`. Migrate every active employee's current state from `EmploymentData`/`Contract` into an initial `Compensation` row, expose CRUD endpoints at `/api/v1/payroll/compensations/`, and add the HR admin page "Estructura salarial" so HR can view + create new compensation versions.

**Architecture:** Greenfield model in `apps.payroll` (`models/domain.py`) using `TenantScopedModel` abstract base. Read snapshot fields from `apps.contracts.EmploymentData` + `apps.employees.Employee` at creation (no FK by lifecycle — Compensation owns its own data once created). `Compensation.current_for(employee, as_of_date)` is the canonical reader D.4 will call. `migrate_employment_to_compensation` reconciles the known divergence between `Contract.salario_bruto`, `EmploymentData.sueldo_basico`, and the most recent `ContractAmendment.nuevo_salario` per INVENTORY § 2 (BACKLOG #40), creating one initial row per active employee + audit-logging any divergence. ViewSet uses `TenantAwareViewSetMixin + ModelViewSet + RRHHPermission`. Frontend: a single admin page under `features/payroll/pages/` consuming the new CRUD service.

**Tech Stack:** Django 5.2 + DRF, React 18 + TS + react-query, pytest, vitest.

**Source:** spec § 4.2 (`Compensation` field list) + § 5 D.3 row; ADR-D.2 (decimals); `.planning/audit-D/BACKLOG.md` #39, #40, #42 (#41 is a D.4 consumer-side change, noted not built here); INVENTORY § 2 (EmploymentData + Employee + Contract fields, salary-divergence warning).

---

## Baseline snapshot

| Check | Before D.3 | After D.3 |
|---|---|---|
| Backend pytest | 1073 passed, 1 failed (`test_permisos_debug`), 17 skipped | **1073 + N_new passed**, still 1 pre-existing failure, 17 skipped |
| `apps.payroll` models | 3 (catalog) | **4** (+ `Compensation`) |
| `apps.payroll` migrations | 0001-0004 | + `0005_compensation` |
| `/api/v1/payroll/compensations/` | 501 (catch-all) | CRUD 200/201/204 + `/history/{employee_id}/` 200 |
| Frontend vitest | 205 passed | **205 + N_new** |
| Frontend build / tsc / lint | clean / 1 pre-existing / ≤ 278 | unchanged |
| `manage.py check` | 0 silenced | 0 silenced |

---

## Branch

`vyntia/D3-compensation-contract` — from `master` HEAD (D.2 merge `1f0706a9`).

```bash
git -C D:/VYNTIA checkout master
git -C D:/VYNTIA checkout -b vyntia/D3-compensation-contract
```

---

## File structure

**Create (backend):**
- `apps/api/apps/payroll/models/domain.py` — `Compensation`
- `apps/api/apps/payroll/migrations/0005_compensation.py` (generated)
- `apps/api/apps/payroll/management/commands/migrate_employment_to_compensation.py`
- `apps/api/api/v1/payroll/compensation_serializers.py`
- `apps/api/api/v1/payroll/compensation_views.py`
- `apps/api/apps/payroll/tests/test_compensation_model.py`
- `apps/api/apps/payroll/tests/test_migrate_employment_to_compensation.py`
- `apps/api/apps/payroll/tests/test_compensation_api.py`

**Modify (backend):**
- `apps/api/apps/payroll/models/__init__.py` — re-export `Compensation`
- `apps/api/api/v1/payroll/urls.py` — add `compensations/` route BEFORE the catch-all

**Create (frontend):**
- `apps/web/src/features/payroll/services/compensationsService.ts`
- `apps/web/src/features/payroll/hooks/useCompensations.ts`
- `apps/web/src/features/payroll/pages/EstructuraSalarialPage.tsx`
- `apps/web/src/features/payroll/services/__tests__/compensationsService.test.ts`

**Modify (frontend):**
- `apps/web/src/features/payroll/pages/index.ts` — barrel export the new page
- `apps/web/src/features/payroll/services/index.ts` — barrel export the service
- `apps/web/src/App.tsx` — add `/estructura-salarial` route (AdminRoute + AdminLayout)

**Do NOT touch:** the 8 existing legacy `features/payroll/pages/*` (still 501-bound from D.1a — rebuilt in D.5/D.6); `api/v1/compensation/` (that's B.7 CCF, unrelated to D.3).

---

## Decisions locked in this plan

1. **Field list per spec § 4.2** (broader than BACKLOG #39's narrower interpretation): `Compensation` carries the full snapshot — salary + régimen + pension + AFP + health + banking — not just `base_salary + asignacion_familiar`. This matches the spec's design: Compensation is the per-employee versioned source-of-truth.
2. **Source-of-provenance tagged via `source` enum** (BACKLOG #39): `MIGRATION` (set by the migrate command), `MANUAL` (HR creates via UI), `CONTRACT_AMENDMENT` (later integration — not implemented in D.3, the choice exists for forward-compat).
3. **No-FK snapshots:** `regimen_laboral`, `pension_regime`, `cuspp`, etc. are CharField snapshots at create. If the underlying `EmploymentData`/`Employee` later changes, the existing `Compensation` row is unaffected (correct: this is a payroll-period-stable snapshot). A new compensation row is created when HR records a change.
4. **`contract_snapshot` is FK to `Contract` nullable** (per BACKLOG #39). Set by the migrate command if the source value came from `Contract.salario_bruto`/`ContractAmendment.nuevo_salario`; null for manual rows.
5. **Reconciliation rule for the migration** (per BACKLOG #40 + INVENTORY § 2 divergence warning): take `max(EmploymentData.sueldo_basico, Contract.salario_bruto, latest ContractAmendment.nuevo_salario)` per active employee; if the three values diverge by more than 0.01 PEN, write an `audit_lite.AuditEvent` with `action="payroll.compensation.migrated_with_divergence"` and the three values in `payload_json`. Conservative (HR adjusts down if wrong; never under-pay during migration).
6. **CCI/banking masking deferred:** spec § 4.2 mentions `permission_level=6` for "HR sees, employee doesn't see CCI". D.3's admin page is HR-only (`RRHHPermission`) — no employee-self-view yet. The field is stored; serializer-level masking is a future concern (D.6 employee portal or a dedicated self-view phase).
7. **#41 (`Regime728Strategy.compute_payslip` reads `Compensation.base_salary`) is D.4 scope, not D.3** — D.3 only delivers the data + readers; D.4 wires the engine to consume them.

---

## Task 1: `Compensation` model + lookup + migration (TDD)

**Files:**
- Create: `apps/api/apps/payroll/models/domain.py`, `apps/api/apps/payroll/tests/test_compensation_model.py`
- Modify: `apps/api/apps/payroll/models/__init__.py`
- Generated: `apps/api/apps/payroll/migrations/0005_compensation.py`

- [ ] **Step 1.1: Write failing model tests**

Create `apps/api/apps/payroll/tests/test_compensation_model.py`:

```python
"""D.3 — Compensation versioned tenant-scoped snapshot."""

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="t1", name="T1", ruc="20111111111", plan="starter", status="active",
    )


@pytest.fixture
def employee(db, tenant):
    return Employee.objects.create(
        tenant=tenant,
        numero_documento="11111111", tipo_documento="DNI",
        nombres_empleado="Ana", apellido_paterno="Pérez", apellido_materno="Lopez",
    )


@pytest.mark.django_db
class TestCompensationLookup:
    def test_current_for_returns_active_version(self, tenant, employee):
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31), base_salary=Decimal("2500.00"),
            regimen_laboral="728", pension_regime="ONP", health_regime="ESSALUD",
            source="MIGRATION",
        )
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
            valid_to=None, base_salary=Decimal("3000.00"),
            regimen_laboral="728", pension_regime="ONP", health_regime="ESSALUD",
            source="MANUAL",
        )
        assert Compensation.current_for(employee, date(2024, 6, 1)).base_salary == Decimal("2500.00")
        assert Compensation.current_for(employee, date(2026, 6, 1)).base_salary == Decimal("3000.00")

    def test_current_for_returns_none_when_no_row(self, employee):
        assert Compensation.current_for(employee, date(2024, 6, 1)) is None


@pytest.mark.django_db
class TestCompensationConstraints:
    def test_unique_employee_valid_from(self, tenant, employee):
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
            base_salary=Decimal("3000.00"), regimen_laboral="728",
            pension_regime="ONP", health_regime="ESSALUD", source="MANUAL",
        )
        with pytest.raises(IntegrityError):
            Compensation.objects.create(
                tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
                base_salary=Decimal("3500.00"), regimen_laboral="728",
                pension_regime="ONP", health_regime="ESSALUD", source="MANUAL",
            )
```

> NOTE for implementer: the Employee.create fields above mirror the minimum required; adapt to the project's Employee factory if one exists (search `apps/api/tests/` or `apps/api/apps/employees/tests/` for a factory before writing). The tenant fixture mirrors the one already in `apps/api/conftest.py` (`tenant_a`).

- [ ] **Step 1.2: Run to confirm failure**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
pytest apps/payroll/tests/test_compensation_model.py -v
```
Expected: FAIL with `ImportError: cannot import name 'Compensation'`.

- [ ] **Step 1.3: Create the model**

Create `apps/api/apps/payroll/models/domain.py`:

```python
"""Domain (tenant-scoped) models for Vyntia Pay.

`Compensation` is the per-employee versioned salary+régimen+pension+banking
snapshot — the single source of truth D.4's engine reads via
`Compensation.current_for(employee, as_of_date)`. Snapshots are immutable in
practice: when an employee's situation changes (raise, AFP switch, banking
update), HR creates a new row with the new `valid_from` and the previous row's
`valid_to` is closed off.
"""

import uuid
from datetime import date

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class Compensation(TenantScopedModel):
    SOURCE_CHOICES = [
        ("MIGRATION", "Migración inicial desde EmploymentData/Contract"),
        ("MANUAL", "Creado manualmente por RRHH"),
        ("CONTRACT_AMENDMENT", "Generado por adenda de contrato"),
    ]

    PENSION_REGIME_CHOICES = [
        ("ONP", "ONP"),
        ("AFP_INTEGRA", "AFP Integra"),
        ("AFP_PRIMA", "AFP Prima"),
        ("AFP_PROFUTURO", "AFP Profuturo"),
        ("AFP_HABITAT", "AFP Hábitat"),
    ]

    AFP_COMMISSION_CHOICES = [
        ("FLUJO", "Flujo"),
        ("MIXTA", "Mixta"),
        ("SALDO", "Saldo"),
    ]

    HEALTH_REGIME_CHOICES = [
        ("ESSALUD", "EsSalud"),
        ("EPS", "EPS"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.PROTECT, related_name="compensations"
    )

    # versioning
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    # salary
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    has_family_allowance = models.BooleanField(default=False)

    # snapshots (string, no FK by lifecycle)
    regimen_laboral = models.CharField(max_length=20)
    pension_regime = models.CharField(max_length=20, choices=PENSION_REGIME_CHOICES)
    afp_commission_type = models.CharField(
        max_length=8, choices=AFP_COMMISSION_CHOICES, blank=True, default=""
    )
    cuspp = models.CharField(max_length=12, blank=True, default="")
    health_regime = models.CharField(max_length=16, choices=HEALTH_REGIME_CHOICES)
    eps_provider = models.CharField(max_length=64, blank=True, default="")

    # banking
    cci = models.CharField(max_length=20, blank=True, default="")
    bank_code = models.CharField(max_length=8, blank=True, default="")
    bank_account = models.CharField(max_length=20, blank=True, default="")
    permission_level = models.IntegerField(default=6)

    # provenance
    source = models.CharField(max_length=24, choices=SOURCE_CHOICES)
    contract_snapshot = models.ForeignKey(
        "contracts.Contract", null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    # audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    class Meta(TenantScopedModel.Meta):
        db_table = "payroll_compensation"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "valid_from"], name="uniq_compensation_employee_validfrom"
            ),
        ]
        ordering = ["-valid_from"]
        indexes = [
            models.Index(fields=["tenant", "employee", "-valid_from"]),
        ]

    def __str__(self):
        return f"{self.employee_id} {self.base_salary} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def current_for(cls, employee, as_of_date: date):
        """Return the Compensation row valid for `employee` on `as_of_date`, or None."""
        return (
            cls.objects.filter(employee=employee, valid_from__lte=as_of_date)
            .filter(models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=as_of_date))
            .order_by("-valid_from")
            .first()
        )
```

- [ ] **Step 1.4: Re-export**

In `apps/api/apps/payroll/models/__init__.py`, add `Compensation` to the imports + `__all__`:

```python
"""Payroll models — greenfield Vyntia Pay catalog + domain (D.2+)."""

from .catalog import PayrollConcept, RegimenConfig, TaxParameter
from .domain import Compensation

__all__ = ["Compensation", "PayrollConcept", "RegimenConfig", "TaxParameter"]
```

- [ ] **Step 1.5: Generate migration**

```bash
cd D:/VYNTIA/apps/api
python manage.py makemigrations payroll --name compensation --settings=vyntia.settings.development
```
Expected: `0005_compensation.py` with one `CreateModel` for Compensation + the unique constraint + index. Dependencies include `('payroll', '0004_catalog_models')`, `('employees', ...)`, `('contracts', ...)`, `('tenancy', ...)`.

- [ ] **Step 1.6: Run model tests + check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
pytest apps/payroll/tests/test_compensation_model.py -v --create-db
```
Expected: check 0 silenced; all tests PASS.

- [ ] **Step 1.7: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/models/ apps/api/apps/payroll/migrations/0005_compensation.py apps/api/apps/payroll/tests/test_compensation_model.py
git -C D:/VYNTIA commit -m "feat(D3): Compensation model (versioned tenant-scoped snapshot)"
```

---

## Task 2: `migrate_employment_to_compensation` command (TDD)

**Files:**
- Create: `.../management/commands/migrate_employment_to_compensation.py`
- Create: `apps/api/apps/payroll/tests/test_migrate_employment_to_compensation.py`

- [ ] **Step 2.1: Write failing seed test**

Create `apps/api/apps/payroll/tests/test_migrate_employment_to_compensation.py`:

```python
"""D.3 — migrate_employment_to_compensation: one snapshot per active employee."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.audit_lite.models import AuditEvent
from apps.contracts.models import Contract, EmploymentData
from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="t1", name="T1", ruc="20111111111", plan="starter", status="active",
    )


@pytest.mark.django_db
class TestMigrateEmploymentToCompensation:
    def test_creates_one_compensation_per_active_employee_from_max_value(self, tenant):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="11111111", tipo_documento="DNI",
            nombres_empleado="Ana", apellido_paterno="Pérez", apellido_materno="Lopez",
            sistema_pensiones="ONP", tipo_seguro_salud="ESSALUD",
        )
        ed = EmploymentData.objects.create(
            tenant=tenant, empleado=emp, regimen_laboral="728",
            sueldo_basico=Decimal("2800.00"), estado_datos="activo",
            fecha_ingreso=date(2024, 1, 15), jornada_laboral="completa",
            # ... fill the minimum required EmploymentData fields per the model
        )
        Contract.objects.create(
            tenant=tenant, empleado=emp, numero_contrato="C-001",
            tipo_documento="LEY_728_INDETERMINADO",
            fecha_inicio=date(2024, 1, 15), salario_bruto=Decimal("3000.00"),
            status="ACTIVO",
        )

        call_command("migrate_employment_to_compensation")

        comp = Compensation.objects.get(employee=emp)
        assert comp.base_salary == Decimal("3000.00")  # max of 2800 vs 3000
        assert comp.regimen_laboral == "728"
        assert comp.pension_regime == "ONP"
        assert comp.health_regime == "ESSALUD"
        assert comp.source == "MIGRATION"
        assert comp.valid_from == date(2024, 1, 15)

        # Divergence (2800 vs 3000) → audit event
        event = AuditEvent.objects.get(action="payroll.compensation.migrated_with_divergence")
        assert event.target_id == str(emp.id)
        assert Decimal(event.payload_json["sueldo_basico"]) == Decimal("2800.00")
        assert Decimal(event.payload_json["salario_bruto"]) == Decimal("3000.00")

    def test_idempotent_skips_employees_with_existing_compensation(self, tenant):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="22222222", tipo_documento="DNI",
            nombres_empleado="Luis", apellido_paterno="Soto", apellido_materno="Diaz",
            sistema_pensiones="AFP INTEGRA", tipo_seguro_salud="ESSALUD",
            tipo_comision="FLUJO",
        )
        EmploymentData.objects.create(
            tenant=tenant, empleado=emp, regimen_laboral="728",
            sueldo_basico=Decimal("3500.00"), estado_datos="activo",
            fecha_ingreso=date(2025, 1, 1), jornada_laboral="completa",
        )

        call_command("migrate_employment_to_compensation")
        before = Compensation.objects.filter(employee=emp).count()

        call_command("migrate_employment_to_compensation")
        after = Compensation.objects.filter(employee=emp).count()
        assert before == after == 1

    def test_skips_employees_without_active_employment_data(self, tenant):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="33333333", tipo_documento="DNI",
            nombres_empleado="Sin", apellido_paterno="Datos", apellido_materno="X",
        )
        call_command("migrate_employment_to_compensation")
        assert not Compensation.objects.filter(employee=emp).exists()
```

> NOTE for implementer: the fixture for `EmploymentData.objects.create(...)` above lists the minimum fields; the real model may require more (`area`, `cargo_empleado`, etc.). Inspect `apps/api/apps/contracts/models/employment_data.py` and add whichever fields are non-nullable / no-default. Same for `Contract`. The test should compile + run; if it errors with "field X required", just add a sensible test value.

- [ ] **Step 2.2: Run to confirm failure**

```bash
pytest apps/payroll/tests/test_migrate_employment_to_compensation.py -v --create-db
```
Expected: FAIL with `CommandError: Unknown command 'migrate_employment_to_compensation'`.

- [ ] **Step 2.3: Implement the command**

Create `apps/api/apps/payroll/management/commands/migrate_employment_to_compensation.py`:

```python
"""Snapshot active employees' current state into an initial Compensation row (D.3 / BACKLOG #40).

Reconciliation per INVENTORY § 2 salary-divergence warning:
take max(EmploymentData.sueldo_basico, Contract.salario_bruto,
        latest ContractAmendment.nuevo_salario)
and audit-log when those values diverge by > 0.01 PEN.

Idempotent: employees that already have any Compensation row are skipped.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.audit_lite.models import AuditEvent
from apps.contracts.models import Contract, ContractAmendment, EmploymentData
from apps.employees.models import Employee
from apps.payroll.models import Compensation

DIVERGENCE_THRESHOLD = Decimal("0.01")


class Command(BaseCommand):
    help = "Snapshot active employees into an initial Compensation row (D.3)."

    @transaction.atomic
    def handle(self, *args, **options):
        created = skipped_existing = skipped_no_data = divergences = 0
        for emp in Employee.objects.select_related("tenant").iterator():
            if Compensation.objects.filter(employee=emp).exists():
                skipped_existing += 1
                continue
            ed = (
                EmploymentData.objects.filter(empleado=emp, estado_datos="activo")
                .order_by("-fecha_inicio_contrato").first()
            )
            if ed is None:
                skipped_no_data += 1
                continue

            contract = (
                Contract.objects.filter(empleado=emp, status="ACTIVO")
                .order_by("-fecha_inicio").first()
            )
            latest_amendment = None
            if contract is not None:
                latest_amendment = (
                    ContractAmendment.objects.filter(
                        parent_contract=contract,
                        tipo_documento="ADENDA_SALARIAL",
                        nuevo_salario__isnull=False,
                    ).order_by("-fecha_inicio").first()
                )

            values = {"sueldo_basico": Decimal(ed.sueldo_basico or 0)}
            if contract is not None:
                values["salario_bruto"] = Decimal(contract.salario_bruto or 0)
            if latest_amendment is not None:
                values["amendment_nuevo_salario"] = Decimal(latest_amendment.nuevo_salario)

            base_salary = max(values.values())

            non_zero = [v for v in values.values() if v > 0]
            if non_zero and (max(non_zero) - min(non_zero)) > DIVERGENCE_THRESHOLD:
                divergences += 1
                AuditEvent.objects.create(
                    tenant=emp.tenant, actor_user=None,
                    action="payroll.compensation.migrated_with_divergence",
                    target_model="payroll.Compensation", target_id=str(emp.id),
                    payload_json={k: str(v) for k, v in values.items()},
                )

            Compensation.objects.create(
                tenant=emp.tenant, employee=emp,
                valid_from=ed.fecha_ingreso or timezone.now().date(),
                valid_to=None,
                base_salary=base_salary,
                has_family_allowance=bool(getattr(emp, "es_padre_familia", False)),
                regimen_laboral=ed.regimen_laboral,
                pension_regime=self._normalize_pension(emp.sistema_pensiones),
                afp_commission_type=(emp.tipo_comision or "") if emp.tipo_comision else "",
                cuspp=emp.codigo_cuspp or "",
                health_regime=self._normalize_health(emp.tipo_seguro_salud),
                eps_provider="",
                cci=emp.numero_cci or "",
                bank_code="",
                bank_account=emp.numero_cuenta_bancaria or "",
                source="MIGRATION",
                contract_snapshot=contract,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Compensation migration: created={created} "
            f"skipped_existing={skipped_existing} skipped_no_data={skipped_no_data} "
            f"divergences_logged={divergences}"
        ))

    @staticmethod
    def _normalize_pension(value):
        """Map Employee.sistema_pensiones string to Compensation.pension_regime choice."""
        if not value:
            return "ONP"
        v = value.upper().replace(" ", "_")
        if v.startswith("AFP_"):
            return v  # AFP_INTEGRA / AFP_PRIMA / AFP_PROFUTURO / AFP_HABITAT
        if v == "ONP":
            return "ONP"
        return "ONP"  # SIN PENSION / PENSIONISTA-* default to ONP for the snapshot

    @staticmethod
    def _normalize_health(value):
        if value and value.upper() == "EPS":
            return "EPS"
        return "ESSALUD"
```

- [ ] **Step 2.4: Run + verify idempotency**

```bash
pytest apps/payroll/tests/test_migrate_employment_to_compensation.py -v --create-db
```
Expected: all 3 tests PASS.

- [ ] **Step 2.5: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/management/commands/migrate_employment_to_compensation.py apps/api/apps/payroll/tests/test_migrate_employment_to_compensation.py
git -C D:/VYNTIA commit -m "feat(D3): migrate_employment_to_compensation idempotent command + divergence audit"
```

---

## Task 3: `CompensationViewSet` + serializer + URL + tests (TDD)

**Files:**
- Create: `apps/api/api/v1/payroll/compensation_serializers.py`, `compensation_views.py`
- Modify: `apps/api/api/v1/payroll/urls.py`
- Create: `apps/api/apps/payroll/tests/test_compensation_api.py`

- [ ] **Step 3.1: Write failing API test**

Create `apps/api/apps/payroll/tests/test_compensation_api.py`:

```python
"""D.3 — Compensation CRUD API + history per employee."""

from datetime import date
from decimal import Decimal

import pytest

from apps.contracts.models import EmploymentData
from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


@pytest.fixture
def tenant_with_hr(db):
    """Tenant + HR user. Uses the auth fixture pattern: see apps/api/conftest.py."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    tenant = Tenant.objects.create(
        slug="t1", name="T1", ruc="20111111111", plan="starter", status="active",
    )
    user = User.objects.create_user(
        username="hr_user", email="hr@x.pe", password="pw",
        nombres_usuario="HR", apellidos_usuario="User", tenant=tenant,
    )
    return tenant, user


@pytest.mark.django_db
class TestCompensationApi:
    def test_list_create_history(self, tenant_with_hr, api_client):
        tenant, user = tenant_with_hr
        # The implementer must arrange whatever the project requires to mark a user
        # as RRHH (e.g. group / role / permission). Mirror an existing test under
        # `apps/api/api/v1/rrhh/` or `apps/api/api/v1/employees/` that calls a
        # RRHH-permission-gated endpoint, and replicate its setup here.
        api_client.force_authenticate(user=user)
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="11111111", tipo_documento="DNI",
            nombres_empleado="A", apellido_paterno="B", apellido_materno="C",
        )
        Compensation.objects.create(
            tenant=tenant, employee=emp, valid_from=date(2025, 1, 1),
            base_salary=Decimal("3000.00"), regimen_laboral="728",
            pension_regime="ONP", health_regime="ESSALUD", source="MIGRATION",
        )

        resp = api_client.get("/api/v1/payroll/compensations/")
        assert resp.status_code == 200
        assert len(resp.data["data"] if "data" in resp.data else resp.data) >= 1

        # history endpoint
        hist = api_client.get(f"/api/v1/payroll/compensations/history/{emp.id}/")
        assert hist.status_code == 200

        # create new version
        new = api_client.post("/api/v1/payroll/compensations/", {
            "employee": str(emp.id), "valid_from": "2026-01-01",
            "base_salary": "3500.00", "regimen_laboral": "728",
            "pension_regime": "ONP", "health_regime": "ESSALUD",
            "source": "MANUAL",
        }, format="json")
        assert new.status_code == 201, new.data
        assert Compensation.objects.filter(employee=emp).count() == 2

    def test_unauthenticated_rejected(self, api_client):
        assert api_client.get("/api/v1/payroll/compensations/").status_code in (401, 403)
```

> NOTE for implementer: the HR-permission setup will differ. Find an existing `RRHHPermission`-gated endpoint test (search `apps/api/` for `RRHHPermission` + a passing test), and mirror its user/role setup before running.

- [ ] **Step 3.2: Run to confirm failure**

Run: `pytest apps/payroll/tests/test_compensation_api.py -v --create-db`
Expected: FAIL (URL 501 via catch-all or import error).

- [ ] **Step 3.3: Create the serializer**

Create `apps/api/api/v1/payroll/compensation_serializers.py`:

```python
"""Compensation serializer (D.3)."""

from rest_framework import serializers

from apps.payroll.models import Compensation


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = [
            "id", "employee", "valid_from", "valid_to", "base_salary",
            "has_family_allowance", "regimen_laboral", "pension_regime",
            "afp_commission_type", "cuspp", "health_regime", "eps_provider",
            "cci", "bank_code", "bank_account", "permission_level",
            "source", "contract_snapshot", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
```

- [ ] **Step 3.4: Create the viewset**

Create `apps/api/api/v1/payroll/compensation_views.py`:

```python
"""Compensation CRUD viewset (D.3)."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.payroll.models import Compensation

from .compensation_serializers import CompensationSerializer


class CompensationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """HR-only CRUD over per-employee compensation snapshots."""

    queryset = Compensation.objects.select_related("employee").all()
    serializer_class = CompensationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["employee", "source", "valid_from"]
    ordering_fields = ["valid_from", "created_at"]
    ordering = ["-valid_from"]

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        kwargs = {"created_by": self.request.user}
        if tenant is not None:
            kwargs["tenant"] = tenant
        serializer.save(**kwargs)

    @action(detail=False, methods=["get"], url_path="history/(?P<employee_id>[^/.]+)")
    def history(self, request, employee_id=None):
        """All compensation versions for one employee, newest first (BACKLOG #42)."""
        qs = self._filter_by_tenant(
            Compensation.objects.filter(employee_id=employee_id).order_by("-valid_from")
        )
        return Response(self.get_serializer(qs, many=True).data)
```

- [ ] **Step 3.5: Register the URL ahead of the catch-all**

Replace `apps/api/api/v1/payroll/urls.py` with:

```python
"""URLs for payroll bounded context.

Order matters: specific routes (catalog, compensations) FIRST, then the D.1a
501 catch-all for any remaining legacy paths.
"""

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.v1.payroll.catalog_views import (
    PayrollConceptViewSet,
    RegimenConfigViewSet,
    TaxParameterViewSet,
)
from api.v1.payroll.compensation_views import CompensationViewSet
from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

catalog_router = DefaultRouter()
catalog_router.register(r"tax-parameters", TaxParameterViewSet, basename="tax-parameter")
catalog_router.register(r"payroll-concepts", PayrollConceptViewSet, basename="payroll-concept")
catalog_router.register(r"regimen-configs", RegimenConfigViewSet, basename="regimen-config")

domain_router = DefaultRouter()
domain_router.register(r"compensations", CompensationViewSet, basename="compensation")

urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    path("", include(domain_router.urls)),
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]
```

- [ ] **Step 3.6: Run API tests**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
pytest apps/payroll/tests/test_compensation_api.py -v --create-db
```
Expected: tests PASS.

- [ ] **Step 3.7: Commit**

```bash
git -C D:/VYNTIA add apps/api/api/v1/payroll/ apps/api/apps/payroll/tests/test_compensation_api.py
git -C D:/VYNTIA commit -m "feat(D3): CompensationViewSet CRUD + history endpoint at /api/v1/payroll/compensations/"
```

---

## Task 4: Frontend — "Estructura salarial" admin page (TDD service first)

**Files:**
- Create: `apps/web/src/features/payroll/services/compensationsService.ts`
- Create: `apps/web/src/features/payroll/services/__tests__/compensationsService.test.ts`
- Create: `apps/web/src/features/payroll/hooks/useCompensations.ts`
- Create: `apps/web/src/features/payroll/pages/EstructuraSalarialPage.tsx`
- Modify: `apps/web/src/features/payroll/pages/index.ts`, `services/index.ts`
- Modify: `apps/web/src/App.tsx`

- [ ] **Step 4.1: Create the service**

Create `apps/web/src/features/payroll/services/compensationsService.ts`:

```typescript
import { apiClient } from '@/shared/api'

export interface Compensation {
  id: string
  employee: string
  valid_from: string
  valid_to: string | null
  base_salary: string
  has_family_allowance: boolean
  regimen_laboral: string
  pension_regime: string
  afp_commission_type: string
  cuspp: string
  health_regime: string
  eps_provider: string
  cci: string
  bank_code: string
  bank_account: string
  permission_level: number
  source: 'MIGRATION' | 'MANUAL' | 'CONTRACT_AMENDMENT'
  contract_snapshot: string | null
  created_at: string
  updated_at: string
}

export type CompensationCreate = Omit<Compensation, 'id' | 'created_at' | 'updated_at'>

const BASE = '/api/v1/payroll/compensations/'

function unwrap<T>(raw: any): T {
  return raw?.data ?? raw?.results ?? raw
}

export const compensationsService = {
  async list(filters?: { employee?: string; source?: string }) {
    const response = await apiClient.get<{ data?: Compensation[]; results?: Compensation[] }>(BASE, filters)
    return unwrap<Compensation[]>(response.data) ?? []
  },

  async history(employeeId: string) {
    const response = await apiClient.get<{ data?: Compensation[] }>(`${BASE}history/${employeeId}/`)
    return unwrap<Compensation[]>(response.data) ?? []
  },

  async create(payload: CompensationCreate) {
    const response = await apiClient.post<Compensation>(BASE, payload)
    return unwrap<Compensation>(response.data)
  },

  async update(id: string, payload: Partial<CompensationCreate>) {
    const response = await apiClient.patch<Compensation>(`${BASE}${id}/`, payload)
    return unwrap<Compensation>(response.data)
  },

  async remove(id: string) {
    await apiClient.delete(`${BASE}${id}/`)
  },
}
```

> NOTE: confirm `apiClient` exports the verbs `get/post/patch/delete` with the project's exact signatures (look at any other `*Service.ts` under `features/`). Adapt argument order if needed (e.g. some services pass query params as the 2nd arg with key `params`).

- [ ] **Step 4.2: Vitest for the service**

Create `apps/web/src/features/payroll/services/__tests__/compensationsService.test.ts`:

```typescript
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/shared/api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { apiClient } from '@/shared/api'
import { compensationsService } from '../compensationsService'

describe('compensationsService', () => {
  it('list unwraps {data: [...]} envelope', async () => {
    (apiClient.get as any).mockResolvedValueOnce({ data: { data: [{ id: '1' }] } })
    const res = await compensationsService.list()
    expect(res).toEqual([{ id: '1' }])
  })

  it('history calls /history/{employeeId}/', async () => {
    (apiClient.get as any).mockResolvedValueOnce({ data: { data: [] } })
    await compensationsService.history('abc')
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/payroll/compensations/history/abc/')
  })

  it('create POSTs the payload', async () => {
    (apiClient.post as any).mockResolvedValueOnce({ data: { data: { id: '2' } } })
    const res = await compensationsService.create({
      employee: 'e1', valid_from: '2026-01-01', valid_to: null,
      base_salary: '3000.00', has_family_allowance: false,
      regimen_laboral: '728', pension_regime: 'ONP', afp_commission_type: '',
      cuspp: '', health_regime: 'ESSALUD', eps_provider: '',
      cci: '', bank_code: '', bank_account: '', permission_level: 6,
      source: 'MANUAL', contract_snapshot: null,
    })
    expect(res).toEqual({ id: '2' })
  })
})
```

- [ ] **Step 4.3: Create the react-query hook**

Create `apps/web/src/features/payroll/hooks/useCompensations.ts`:

```typescript
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  Compensation,
  CompensationCreate,
  compensationsService,
} from '../services/compensationsService'

const KEY = ['payroll', 'compensations'] as const

export function useCompensationsList(filters?: { employee?: string }) {
  return useQuery<Compensation[]>({
    queryKey: [...KEY, filters],
    queryFn: () => compensationsService.list(filters),
  })
}

export function useCompensationHistory(employeeId: string | undefined) {
  return useQuery<Compensation[]>({
    queryKey: [...KEY, 'history', employeeId],
    queryFn: () => compensationsService.history(employeeId!),
    enabled: !!employeeId,
  })
}

export function useCreateCompensation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: CompensationCreate) => compensationsService.create(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: KEY }),
  })
}
```

- [ ] **Step 4.4: Create the page**

Create `apps/web/src/features/payroll/pages/EstructuraSalarialPage.tsx`. Use the EXISTING admin-page conventions in the repo — read at least one current admin page first (e.g. `apps/web/src/features/employees/pages/Empleados.tsx` or `features/contracts/pages/ContratosPage.tsx`) and mirror its layout/imports (PageHeader, Card, Table, Dialog, react-hook-form + zod, shadcn ui components, toast on error). Implement these features:

- List view: table grouped by employee, columns `Empleado`, `Vigencia desde`, `Sueldo`, `Régimen`, `Pensión`, `Fuente`. Show only the latest 1-2 versions per employee; clicking opens a detail/history dialog.
- "Nueva versión" button → opens a Dialog with a react-hook-form form (zod-validated). Required: `employee`, `valid_from`, `base_salary`, `regimen_laboral`, `pension_regime`, `health_regime`, `source` (defaults to `MANUAL`). Optional: AFP commission, CUSPP, EPS provider, banking.
- On submit: call `useCreateCompensation().mutate(payload)`; toast on success/error.
- History dialog (when clicking an employee row): list all versions via `useCompensationHistory`.
- Loading skeleton + empty state ("No hay registros de estructura salarial") + error toast.

Keep the page under ~250 lines. The implementer SHOULD NOT invent new UI primitives — use what's already in `@/shared/ui/*`.

Default export the page component. Update `apps/web/src/features/payroll/pages/index.ts` to also export it.

- [ ] **Step 4.5: Register the route**

In `apps/web/src/App.tsx`, add (mirror the existing AdminRoute + AdminLayout pattern visible in nearby routes — do NOT invent a new layout). Example:

```typescript
import EstructuraSalarialPage from '@/features/payroll/pages/EstructuraSalarialPage'

// ... inside the routes JSX, alongside other Admin routes:
<Route path="/estructura-salarial" element={
  <AdminRoute>
    <AdminLayout>
      <EstructuraSalarialPage />
    </AdminLayout>
  </AdminRoute>
} />
```

Place the route adjacent to existing admin payroll/employee routes for diff locality.

- [ ] **Step 4.6: Verify frontend gates**

```bash
cd D:/VYNTIA/apps/web
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
npm run build 2>&1 | tail -3
npm run lint 2>&1 | tail -3
npm test -- --run 2>&1 | tail -5
```
Expected: tsc 1 pre-existing (`BlankEnum.ts`); build clean; lint ≤ 278; vitest ≥ 205 + the 3 new service tests.

- [ ] **Step 4.7: Commit**

```bash
git -C D:/VYNTIA add apps/web/src/features/payroll/ apps/web/src/App.tsx
git -C D:/VYNTIA commit -m "feat(D3): frontend Estructura salarial admin page + compensationsService + useCompensations"
```

---

## Task 5: Full regression + close-out

- [ ] **Step 5.1: Full backend suite**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
python manage.py check --settings=vyntia.settings.development
python manage.py makemigrations --check --dry-run --settings=vyntia.settings.development
pytest --tb=short -q --create-db 2>&1 | tail -8
```
Expected: check 0 silenced; `makemigrations --check` "No changes detected"; **1073 + N_new passed, 1 failed (`test_permisos_debug`), 17 skipped**. 0 new failures.

- [ ] **Step 5.2: Frontend gates**

(already exercised in Step 4.6 — confirm here once more after the route addition.)

- [ ] **Step 5.3: Check off backlog items**

In `.planning/audit-D/BACKLOG.md`, prefix `✅` to items **#39, #40, #42**. For **#41** append ` _(consumer wiring → D.4)_` to indicate it's not closed by D.3 (it's a D.4 engine concern).

- [ ] **Step 5.4: Final commit**

```bash
git -C D:/VYNTIA add -f .planning/audit-D/BACKLOG.md
git -C D:/VYNTIA commit -m "docs(D3): mark BACKLOG #39,#40,#42 complete; note #41 deferred to D.4"
git -C D:/VYNTIA log --oneline master..HEAD
```
Expected: ~5 commits on `vyntia/D3-compensation-contract`.

---

## D.3 Done — Handoff to D.4

D.4 (`vyntia/D4-engine-728`) is the regulatory engine: it builds `Regime728Strategy.compute_payslip(employee, period)` reading `Compensation.current_for(employee, period_end_date)` + `TaxParameter.get` + `RegimenConfig.get` + `PayrollConcept` flags, producing a `PaySlipSnapshot` dataclass validated against a golden cartilla SUNAT corpus. D.4 is a **regulatory sign-off gate** ⚠️. Source: BACKLOG #43-#69, ADRs D.1/D.2/D.5/D.6/D.7.
