# D.4a — Engine 728 Monthly (Strategy Pattern + compute_payslip core) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Strategy Pattern engine skeleton (`RegimenStrategy` ABC + `RegimenStrategyFactory`) and implement `Regime728Strategy.compute_payslip` for the **monthly REGULAR period**, covering income lines (basic salary + asignación familiar, proportional to days worked), AFP fondo/prima-SISCO/comisión, ONP (with RMV minimum base), EsSalud 9% (with RMV minimum base), and EPS credit 2.25%. Validated against 10 hand-computed golden cases. **Renta 5ta, vacaciones, subsidios, extranjeros, practicantes, and the regulatory sign-off gate are explicitly OUT — they are D.4b's scope.**

**Architecture:** Pure-Python compute layer in `apps/payroll/strategies/{base,regime_728}.py` + factory `apps/payroll/strategies/__init__.py`. Compute is a function over immutable inputs (`Employee` + `Compensation` + `PayrollPeriod`) reading catalog values via `TaxParameter.get(code, period.end_date)` and `RegimenConfig.get(regimen, period.end_date)`. Returns an immutable `PaySlipSnapshot` dataclass (no DB writes from compute — persistence is D.5's `PayrollRun` lifecycle). Decimals follow ADR-D.2 (intermediate `14,4`, finals quantized `12,2 ROUND_HALF_UP`). `compute_cts`, `compute_gratification`, `compute_severance`, `compute_renta_5ta` are present on the ABC but raise `NotImplementedError` from `Regime728Strategy` — they are the integration points for D.7, D.8, D.12, and D.4b respectively.

**Tech Stack:** Python 3, Django ORM read-only (no migrations), pytest. No frontend.

**Source:** spec `2026-05-23-vyntia-D-vyntia-pay-design.md` § 3.1 (Strategy Pattern) + § 4 (data); ADR-D.1 (Strategy interface), ADR-D.2 (Decimal policy); `.planning/audit-D/BACKLOG.md` items #43 (728-only filter), #49 (AFP fondo), #50 (prima SISCO + RMA), #51 (AFP commission), #52 (ONP + RMV), #53 (EsSalud + RMV), #54 (EPS credit), #55 (asig familiar); INVENTORY § 5 N07 (rates).

---

## Scope decision (read first)

D.4 was originally one phase but contains two natural sub-engines:
| Sub-phase | Scope | Sign-off? |
|---|---|---|
| **D.4a (this plan)** | Strategy Pattern + monthly REGULAR `compute_payslip` (no Renta 5ta) + 10 golden cases | **NO** — engine internally consistent but incomplete |
| **D.4b (next)** | Renta 5ta 4-step engine (RBA→RNAP→IAP→denominador→Dec adjustment) + vacaciones récord + subsidios incapacidad/maternidad + extranjeros + practicantes + AFP licitación validator + full ~30-case cartilla + `REGULATORY-SIGNOFF.md` | **YES** ⚠️ — user signs before merge |

Items **deferred from D.4a → D.4b**: #44, #45, #46, #47, #48 (Renta 5ta), #56, #57, #58 (vacaciones), #59 (suspensiones), #60, #61 (subsidios), #62 (extranjeros), #63 (practicantes), #64 (licitación AFP), #65 (SNP→SPP), #66 (UIT validator), #67 (vacaciones acumuladas), #68 (data retention), #69 (SCTR flag — already covered by D.2's `is_active=False` seed). D.4a backlog items satisfied: #43, #49, #50, #51, #52, #53, #54, #55.

---

## Baseline snapshot

| Check | Before D.4a | After D.4a |
|---|---|---|
| Backend pytest | 1081 passed, 1 failed (`test_permisos_debug`), 17 skipped | **1081 + N_new passed**, still 1 pre-existing failure, 17 skipped |
| `apps.payroll.strategies/` | absent | present (`base.py`, `regime_728.py`, `__init__.py`) |
| `Regime728Strategy.compute_payslip` | absent | works for REGULAR period; 10 golden cases pass |
| `compute_cts` / `compute_gratification` / `compute_severance` / `compute_renta_5ta` | absent | abstract on ABC; raise NotImplementedError on Regime728 |
| `manage.py check` | 0 silenced | 0 silenced |

---

## Branch

`vyntia/D4a-engine-728-monthly` — from `master` HEAD (D.3 merge `de2dd362`).

```bash
git -C D:/VYNTIA checkout master
git -C D:/VYNTIA checkout -b vyntia/D4a-engine-728-monthly
```

---

## File structure

**Create:**
- `apps/api/apps/payroll/strategies/__init__.py` — `RegimenStrategyFactory` + `get_strategy()` helper
- `apps/api/apps/payroll/strategies/base.py` — `RegimenStrategy` ABC + `PayrollPeriod` + `PaySlipLine` + `PaySlipSnapshot` + `CtsResult` + `GratiResult` + `SettleResult` dataclasses + custom exceptions
- `apps/api/apps/payroll/strategies/regime_728.py` — `Regime728Strategy` (implements `compute_payslip`; stubs the rest)
- `apps/api/apps/payroll/tests/test_strategy_factory.py`
- `apps/api/apps/payroll/tests/test_regime_728_payslip.py` — 10 golden cartilla cases + property tests
- `apps/api/apps/payroll/tests/_engine_helpers.py` — small helper factories (employee + compensation + seed-the-catalog) shared by the engine tests

**Do NOT touch:** any model, migration, view, or frontend file. This phase is pure compute. The persistence of a `PaySlip` row is D.6.

---

## Decisions locked in this plan

1. **Pure compute, no DB writes.** `compute_payslip` reads from `Employee`/`Compensation`/`TaxParameter`/`RegimenConfig`/`PayrollConcept` and returns an immutable `PaySlipSnapshot`. D.5's `PayrollRunService` is the only writer.
2. **Caller resolves `Compensation`.** The compute method accepts an already-resolved `Compensation` instance, not an employee + date. Keeps compute deterministic and testable without DB for unit tests. (The factory + thin wrapper in D.5 will fetch `Compensation.current_for(employee, period.end_date)` and inject it.)
3. **Catalog reads use `period.end_date`** per ADR-D.6 (tax-year cutoff). All `TaxParameter.get`/`RegimenConfig.get` calls anchor on the period's last day.
4. **Decimal policy (ADR-D.2):**
   - Intermediate computations: `Decimal` arithmetic at native precision (≥ 14,4).
   - Each `PaySlipLine.amount` is quantized to `Decimal("0.01")` with `ROUND_HALF_UP` at the moment the line is added.
   - Totals are computed by summing already-quantized line amounts (no further rounding).
5. **Day-of-month proration.** Income lines (basic + asig fam) scale by `days_worked / 30` when `days_worked < 30`. Aporte/descuento bases use the *prorated* asegurable. RMV minimum base is NOT prorated (per N07-13: "base mínima = RMV aunque ganó menos").
6. **AFP commission rate sourcing.** D.4a covers FLUJO only. Read from `TaxParameter.get("AFP_{INTEGRA|PRIMA|PROFUTURO|HABITAT}_FLUJO", period.end_date)`. MIXTA is a TODO comment + raise for D.4b.
7. **EPS credit handling.** If `health_regime == "EPS"`: employer pays `(0.0675) × base_essalud` to EsSalud + `EPS_CREDIT_RATE × base_essalud` as the EPS credit line. The credit-cap (`10 RMV × workers_covered`) is **not enforced in D.4a** (no tenant-wide worker count available in compute scope) — a TODO comment cites N07-20 and defers to D.4b/D.5 (run-level cap).
8. **Régimen 728 only.** If the resolved `Compensation.regimen_laboral != "728"`, raise `UnsupportedRegimen`. The factory enforces this too.
9. **Stubs raise, do not silently return.** `compute_cts/_gratification/_severance/_renta_5ta` raise `NotImplementedError("D.<phase> implements this")` with the phase number — surfaces accidental cross-phase calls immediately.

---

## Task 1: Strategy Pattern ABC + dataclasses + factory + factory test (TDD)

**Files:**
- Create: `apps/api/apps/payroll/strategies/{__init__.py,base.py}`
- Create: `apps/api/apps/payroll/tests/test_strategy_factory.py`

- [ ] **Step 1.1: Write the failing factory test**

Create `apps/api/apps/payroll/tests/test_strategy_factory.py`:

```python
"""D.4a — RegimenStrategyFactory routes by code; rejects unknown / non-728."""

from datetime import date

import pytest

from apps.payroll.strategies import RegimenStrategyFactory, UnsupportedRegimen


def test_factory_returns_728_strategy_for_code_728(db):
    from apps.payroll.strategies.regime_728 import Regime728Strategy
    # 728 needs a RegimenConfig row; reuse the D.2 seed
    from django.core.management import call_command
    call_command("seed_payroll_catalog")

    strategy = RegimenStrategyFactory.get("728", as_of_date=date(2026, 5, 1))
    assert isinstance(strategy, Regime728Strategy)


def test_factory_rejects_unknown_regimen():
    with pytest.raises(UnsupportedRegimen):
        RegimenStrategyFactory.get("MYPE_PEQUENA", as_of_date=date(2026, 5, 1))


def test_factory_rejects_276(db):
    with pytest.raises(UnsupportedRegimen):
        RegimenStrategyFactory.get("276", as_of_date=date(2026, 5, 1))
```

- [ ] **Step 1.2: Run to confirm failure**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
pytest apps/payroll/tests/test_strategy_factory.py -v
```
Expected: FAIL with `ImportError`.

- [ ] **Step 1.3: Create the ABC + dataclasses**

Create `apps/api/apps/payroll/strategies/base.py`:

```python
"""Strategy Pattern interfaces + immutable result dataclasses (D.4a).

Per ADR-D.1: `RegimenStrategy` is an ABC; each régimen registers its concrete
class with `RegimenStrategyFactory`. `compute_payslip` is the only method
implemented in D.4a; `compute_cts/_gratification/_severance/_renta_5ta` are
abstract on this base and raise `NotImplementedError` from `Regime728Strategy`
until D.4b/D.7/D.8/D.12 implement them.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from calendar import monthrange
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


class UnsupportedRegimen(ValueError):
    """Raised when no strategy is registered for a regimen_code."""


class RegimenConfigMissing(ValueError):
    """Raised when `RegimenConfig.get(regimen_code, as_of_date)` returns None."""


@dataclass(frozen=True)
class PayrollPeriod:
    year: int
    month: int
    period_type: str = "REGULAR"
    days_worked: int = 30  # convention: 30-day month even in Feb (LPCL Art. 1)

    @property
    def end_date(self) -> date:
        return date(self.year, self.month, monthrange(self.year, self.month)[1])


@dataclass(frozen=True)
class PaySlipLine:
    concept_code: str           # e.g. "BASIC_SALARY"
    sunat_code: str             # e.g. "0101"
    category: str               # INCOME / DEDUCTION / CONTRIBUTION_EMPLOYER / TAX
    amount: Decimal             # quantized to 0.01 ROUND_HALF_UP
    base: Decimal = Decimal("0.00")
    rate: Decimal | None = None


@dataclass(frozen=True)
class PaySlipSnapshot:
    employee_id: str
    period: PayrollPeriod
    regimen_laboral: str
    lines: tuple[PaySlipLine, ...]
    total_gross: Decimal
    total_deductions: Decimal
    total_employer_contributions: Decimal
    net_pay: Decimal
    metadata: dict[str, Any] = field(default_factory=dict)


# Stub dataclasses for downstream phases (D.7/D.8/D.12)
@dataclass(frozen=True)
class CtsResult:
    employee_id: str
    semester: str
    amount: Decimal


@dataclass(frozen=True)
class GratiResult:
    employee_id: str
    semester: str
    amount: Decimal
    bonificacion_extra: Decimal


@dataclass(frozen=True)
class SettleResult:
    employee_id: str
    fecha_cese: date
    total: Decimal
    breakdown: dict[str, Decimal]


class RegimenStrategy(ABC):
    """Per-régimen compute interface (one concrete class per régimen).

    Instances are bound to a `RegimenConfig` snapshot resolved at factory time
    so the strategy never reads catalog versioning by itself — it sees only the
    config valid for the period being computed.
    """

    regimen_code: str = ""  # set by subclass

    def __init__(self, regimen_config):
        self.regimen_config = regimen_config

    @abstractmethod
    def compute_payslip(self, employee, compensation, period: PayrollPeriod) -> PaySlipSnapshot: ...

    @abstractmethod
    def compute_cts(self, employee, semester) -> CtsResult: ...

    @abstractmethod
    def compute_gratification(self, employee, semester) -> GratiResult: ...

    @abstractmethod
    def compute_severance(self, employee, termination_date: date, cause: str) -> SettleResult: ...

    @abstractmethod
    def compute_renta_5ta(self, employee, period: PayrollPeriod, accumulated: Decimal) -> Decimal: ...
```

- [ ] **Step 1.4: Create the factory + Regime728Strategy stub**

Create `apps/api/apps/payroll/strategies/__init__.py`:

```python
"""Strategy factory for régimen-specific payroll engines (D.4a).

Concrete strategies self-register via `RegimenStrategyFactory.register("CODE", Cls)`
at module-import time (see `regime_728.py`). The factory binds the strategy
to its `RegimenConfig` row valid at `as_of_date` so the strategy itself never
re-reads versioning.
"""

from __future__ import annotations

from datetime import date

from .base import (
    PayrollPeriod,
    PaySlipLine,
    PaySlipSnapshot,
    RegimenConfigMissing,
    RegimenStrategy,
    UnsupportedRegimen,
    CtsResult,
    GratiResult,
    SettleResult,
)


class RegimenStrategyFactory:
    _registry: dict[str, type[RegimenStrategy]] = {}

    @classmethod
    def register(cls, regimen_code: str, strategy_cls: type[RegimenStrategy]) -> None:
        cls._registry[regimen_code] = strategy_cls

    @classmethod
    def get(cls, regimen_code: str, as_of_date: date) -> RegimenStrategy:
        from apps.payroll.models import RegimenConfig

        if regimen_code not in cls._registry:
            raise UnsupportedRegimen(
                f"No strategy registered for regimen_code={regimen_code!r}. "
                f"D-A ships 728 only in MVP; other regímenes are post-D."
            )
        regimen_config = RegimenConfig.get(regimen_code, as_of_date)
        if regimen_config is None:
            raise RegimenConfigMissing(
                f"No RegimenConfig row valid for {regimen_code} at {as_of_date}. "
                f"Run `seed_payroll_catalog`."
            )
        return cls._registry[regimen_code](regimen_config)


# Eager import of concrete strategies so factory registry is populated.
from . import regime_728  # noqa: E402, F401
```

Create `apps/api/apps/payroll/strategies/regime_728.py` (minimal — Task 2 fills `compute_payslip`):

```python
"""Régimen 728 strategy (D.4a — monthly REGULAR + stubs for the rest)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from . import RegimenStrategyFactory  # circular but works due to import order in __init__
from .base import (
    PayrollPeriod,
    PaySlipSnapshot,
    RegimenStrategy,
    UnsupportedRegimen,
    CtsResult,
    GratiResult,
    SettleResult,
)


class Regime728Strategy(RegimenStrategy):
    regimen_code = "728"

    def compute_payslip(self, employee, compensation, period: PayrollPeriod) -> PaySlipSnapshot:
        raise NotImplementedError("Task 2 of this plan fills compute_payslip")

    def compute_cts(self, employee, semester) -> CtsResult:
        raise NotImplementedError("D.7 implements compute_cts")

    def compute_gratification(self, employee, semester) -> GratiResult:
        raise NotImplementedError("D.8 implements compute_gratification")

    def compute_severance(self, employee, termination_date: date, cause: str) -> SettleResult:
        raise NotImplementedError("D.12 implements compute_severance")

    def compute_renta_5ta(self, employee, period: PayrollPeriod, accumulated: Decimal) -> Decimal:
        raise NotImplementedError("D.4b implements compute_renta_5ta")


RegimenStrategyFactory.register("728", Regime728Strategy)
```

> NOTE on the circular import: the `from . import RegimenStrategyFactory` in `regime_728.py` works because Python's module-import already partially-initialised `__init__.py` before reaching `from . import regime_728`. If pytest collection fails with `ImportError`, restructure: move `RegimenStrategyFactory` into `factory.py` and have both `regime_728.py` and `__init__.py` import it from there.

- [ ] **Step 1.5: Run the factory test → PASS**

```bash
pytest apps/payroll/tests/test_strategy_factory.py -v --create-db
```
Expected: 3 tests PASS.

- [ ] **Step 1.6: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/strategies/ apps/api/apps/payroll/tests/test_strategy_factory.py
git -C D:/VYNTIA commit -m "feat(D4a): RegimenStrategy ABC + factory + Regime728Strategy skeleton (ADR-D.1)"
```

---

## Task 2: `Regime728Strategy.compute_payslip` for REGULAR period (TDD with 10 golden cases)

**Files:**
- Create: `apps/api/apps/payroll/tests/_engine_helpers.py`
- Create: `apps/api/apps/payroll/tests/test_regime_728_payslip.py`
- Modify: `apps/api/apps/payroll/strategies/regime_728.py` (fill `compute_payslip`)

### Step 2.1: Engine helpers

Create `apps/api/apps/payroll/tests/_engine_helpers.py`:

```python
"""Shared fixtures + builders for D.4a engine tests."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.contracts.models import EmploymentData
from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


@pytest.fixture
def seeded_catalog(db):
    """Run `seed_payroll_catalog` once per test that needs it."""
    call_command("seed_payroll_catalog")


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="t1", name="T1", ruc="20111111111", plan="starter", status="active",
    )


def make_employee(
    tenant,
    *,
    sistema_pensiones="ONP",
    tipo_comision="",
    codigo_cuspp="",
    tipo_seguro_salud="ESSALUD",
    es_padre_familia=False,
    doc="11111111",
):
    return Employee.objects.create(
        tenant=tenant,
        numero_documento=doc, tipo_documento="DNI",
        nombres_empleado="A", apellido_paterno="B", apellido_materno="C",
        sistema_pensiones=sistema_pensiones,
        tipo_comision=tipo_comision or None,
        codigo_cuspp=codigo_cuspp or None,
        tipo_seguro_salud=tipo_seguro_salud,
        es_padre_familia=es_padre_familia,
    )


def make_compensation(
    tenant, employee,
    *,
    base_salary,
    has_family_allowance=False,
    pension_regime=None,  # inferred from employee.sistema_pensiones if None
    afp_commission_type=None,
    health_regime=None,
):
    if pension_regime is None:
        # employee.sistema_pensiones uses spaces ("AFP INTEGRA") — strategy snapshot uses underscores
        v = (employee.sistema_pensiones or "ONP").upper().replace(" ", "_")
        pension_regime = v if v.startswith("AFP_") or v == "ONP" else "ONP"
    if afp_commission_type is None:
        afp_commission_type = (employee.tipo_comision or "") if employee.tipo_comision else ""
    if health_regime is None:
        health_regime = "EPS" if (employee.tipo_seguro_salud or "").upper() == "EPS" else "ESSALUD"

    return Compensation.objects.create(
        tenant=tenant, employee=employee, valid_from=date(2024, 1, 1), valid_to=None,
        base_salary=Decimal(base_salary), has_family_allowance=has_family_allowance,
        regimen_laboral="728", pension_regime=pension_regime,
        afp_commission_type=afp_commission_type, cuspp=employee.codigo_cuspp or "",
        health_regime=health_regime, source="MIGRATION",
    )
```

> NOTE: if `EmploymentData` is needed by `compute_payslip` (it should NOT be — the strategy reads from `Compensation`, not `EmploymentData`), this helper does not create it. If the strategy implementation accidentally queries EmploymentData, refactor it back into Compensation reads.

### Step 2.2: Write the golden-cartilla test (failing)

Create `apps/api/apps/payroll/tests/test_regime_728_payslip.py`:

```python
"""D.4a — 10 hand-computed golden cases for Regime728Strategy.compute_payslip (REGULAR period).

Sources: INVENTORY § 5 N07 rates (UIT 2026=5500, RMV 1130, asig 113, AFP fondo 10%,
prima SISCO 1.37%, RMA Abr-Jun 2026 = 12598.91, AFP Integra FLUJO 1.55%,
Profuturo FLUJO 1.69%, Habitat FLUJO 1.47%, ONP 13%, EsSalud 9%, EPS credit 2.25%).

All amounts in PEN, quantized to 0.01 ROUND_HALF_UP per ADR-D.2.
"""

from datetime import date
from decimal import Decimal

import pytest

from apps.payroll.strategies import RegimenStrategyFactory, UnsupportedRegimen
from apps.payroll.strategies.base import PayrollPeriod

from ._engine_helpers import (  # noqa: F401
    make_compensation,
    make_employee,
    seeded_catalog,
    tenant,
)

PERIOD = PayrollPeriod(year=2026, month=5, period_type="REGULAR", days_worked=30)


def _strategy():
    return RegimenStrategyFactory.get("728", as_of_date=PERIOD.end_date)


def _amount(snapshot, concept_code):
    for ln in snapshot.lines:
        if ln.concept_code == concept_code:
            return ln.amount
    return Decimal("0.00")


@pytest.mark.django_db
class TestRegime728PayslipGolden:
    def test_01_sueldo_3000_onp_essalud(self, seeded_catalog, tenant):
        emp = make_employee(tenant, sistema_pensiones="ONP", tipo_seguro_salud="ESSALUD")
        comp = make_compensation(tenant, emp, base_salary="3000.00")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        assert s.total_gross == Decimal("3000.00")
        assert _amount(s, "ONP") == Decimal("390.00")
        assert s.total_deductions == Decimal("390.00")
        assert _amount(s, "ESSALUD") == Decimal("270.00")
        assert s.total_employer_contributions == Decimal("270.00")
        assert s.net_pay == Decimal("2610.00")

    def test_02_sueldo_3000_afp_integra_flujo_essalud(self, seeded_catalog, tenant):
        emp = make_employee(tenant, sistema_pensiones="AFP INTEGRA", tipo_comision="FLUJO",
                            codigo_cuspp="A00000000001")
        comp = make_compensation(tenant, emp, base_salary="3000.00", pension_regime="AFP_INTEGRA")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        assert s.total_gross == Decimal("3000.00")
        assert _amount(s, "AFP_FONDO") == Decimal("300.00")
        assert _amount(s, "AFP_COMISION_PRIMA").quantize(Decimal("0.01")) == \
               (Decimal("3000") * Decimal("0.0155") + Decimal("3000") * Decimal("0.0137")).quantize(Decimal("0.01"))
        assert _amount(s, "ESSALUD") == Decimal("270.00")
        assert s.net_pay == (Decimal("3000.00") - s.total_deductions).quantize(Decimal("0.01"))

    def test_03_sueldo_5000_afp_profuturo_eps(self, seeded_catalog, tenant):
        emp = make_employee(tenant, sistema_pensiones="AFP PROFUTURO", tipo_comision="FLUJO",
                            tipo_seguro_salud="EPS", codigo_cuspp="P00000000001")
        comp = make_compensation(tenant, emp, base_salary="5000.00",
                                 pension_regime="AFP_PROFUTURO", health_regime="EPS")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        # AFP fondo 500 + Profuturo FLUJO 1.69%*5000=84.50 + Prima 1.37%*5000=68.50
        assert _amount(s, "AFP_FONDO") == Decimal("500.00")
        # Employer EsSalud effective 6.75% + EPS credit 2.25%
        assert _amount(s, "ESSALUD") == Decimal("337.50")
        assert _amount(s, "EPS_CREDIT") == Decimal("112.50")
        assert s.total_employer_contributions == Decimal("450.00")

    def test_04_sueldo_rmv_1130_onp(self, seeded_catalog, tenant):
        emp = make_employee(tenant)
        comp = make_compensation(tenant, emp, base_salary="1130.00")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        assert s.total_gross == Decimal("1130.00")
        assert _amount(s, "ONP") == Decimal("146.90")
        assert _amount(s, "ESSALUD") == Decimal("101.70")

    def test_05_sueldo_2500_con_asignacion_familiar(self, seeded_catalog, tenant):
        emp = make_employee(tenant, es_padre_familia=True)
        comp = make_compensation(tenant, emp, base_salary="2500.00", has_family_allowance=True)
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        # 2500 + 113 (asig fam 2025-2026 = 10% RMV)
        assert _amount(s, "BASIC_SALARY") == Decimal("2500.00")
        assert _amount(s, "ASIG_FAMILIAR") == Decimal("113.00")
        assert s.total_gross == Decimal("2613.00")
        assert _amount(s, "ONP") == (Decimal("2613.00") * Decimal("0.13")).quantize(Decimal("0.01"))

    def test_06_sueldo_15000_afp_habitat_prima_capped_at_rma(self, seeded_catalog, tenant):
        emp = make_employee(tenant, sistema_pensiones="AFP HABITAT", tipo_comision="FLUJO",
                            codigo_cuspp="H00000000001")
        comp = make_compensation(tenant, emp, base_salary="15000.00", pension_regime="AFP_HABITAT")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        # Prima SISCO base = min(15000, 12598.91) = 12598.91; rate 1.37%
        expected_prima = (Decimal("12598.91") * Decimal("0.0137")).quantize(Decimal("0.01"))
        # Comisión 1.47% on full 15000
        expected_comision = (Decimal("15000") * Decimal("0.0147")).quantize(Decimal("0.01"))
        comision_prima = _amount(s, "AFP_COMISION_PRIMA")
        assert comision_prima == (expected_comision + expected_prima).quantize(Decimal("0.01"))
        assert _amount(s, "AFP_FONDO") == Decimal("1500.00")

    def test_07_sueldo_800_under_rmv_uses_rmv_as_base_for_aportes(self, seeded_catalog, tenant):
        """N07-10/N07-13: ONP/EsSalud base mínima = RMV aunque rem real < RMV."""
        emp = make_employee(tenant)
        comp = make_compensation(tenant, emp, base_salary="800.00")
        s = _strategy().compute_payslip(emp, comp, PERIOD)
        # Gross is what the worker actually receives
        assert s.total_gross == Decimal("800.00")
        # But ONP/EsSalud are calculated on RMV minimum (1130)
        assert _amount(s, "ONP") == (Decimal("1130") * Decimal("0.13")).quantize(Decimal("0.01"))
        assert _amount(s, "ESSALUD") == (Decimal("1130") * Decimal("0.09")).quantize(Decimal("0.01"))

    def test_08_non_728_regimen_rejected(self, seeded_catalog, tenant):
        with pytest.raises(UnsupportedRegimen):
            RegimenStrategyFactory.get("276", as_of_date=PERIOD.end_date)

    def test_09_15_dias_trabajados_prorrata_ingresos(self, seeded_catalog, tenant):
        emp = make_employee(tenant)
        comp = make_compensation(tenant, emp, base_salary="3000.00", has_family_allowance=True)
        period_15 = PayrollPeriod(year=2026, month=5, days_worked=15)
        s = _strategy().compute_payslip(emp, comp, period_15)
        # Basic prorated: 3000 * 15/30 = 1500
        assert _amount(s, "BASIC_SALARY") == Decimal("1500.00")
        # Asig fam prorated: 113 * 15/30 = 56.50
        assert _amount(s, "ASIG_FAMILIAR") == Decimal("56.50")
        assert s.total_gross == Decimal("1556.50")

    def test_10_dias_cero_todo_cero(self, seeded_catalog, tenant):
        emp = make_employee(tenant)
        comp = make_compensation(tenant, emp, base_salary="3000.00")
        period_0 = PayrollPeriod(year=2026, month=5, days_worked=0)
        s = _strategy().compute_payslip(emp, comp, period_0)
        assert s.total_gross == Decimal("0.00")
        assert s.total_deductions == Decimal("0.00")
        assert s.total_employer_contributions == Decimal("0.00")
        assert s.net_pay == Decimal("0.00")
```

- [ ] **Step 2.3: Run to confirm failure**

```bash
pytest apps/payroll/tests/test_regime_728_payslip.py -v --create-db
```
Expected: all 10 FAIL with `NotImplementedError` (from the Task 1 stub).

### Step 2.4: Implement `compute_payslip`

Replace `compute_payslip` in `apps/api/apps/payroll/strategies/regime_728.py` with the full implementation (and add the required imports at the top of the file):

```python
"""Régimen 728 strategy (D.4a — monthly REGULAR + stubs)."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from apps.payroll.models import TaxParameter

from . import RegimenStrategyFactory
from .base import (
    CtsResult, GratiResult, PayrollPeriod, PaySlipLine, PaySlipSnapshot,
    RegimenStrategy, SettleResult, UnsupportedRegimen,
)

_CENTS = Decimal("0.01")


def _q(x: Decimal) -> Decimal:
    """Quantize to centavos per ADR-D.2."""
    return Decimal(x).quantize(_CENTS, rounding=ROUND_HALF_UP)


class Regime728Strategy(RegimenStrategy):
    regimen_code = "728"

    # ------------------------------------------------------------------
    # compute_payslip
    # ------------------------------------------------------------------
    def compute_payslip(self, employee, compensation, period: PayrollPeriod) -> PaySlipSnapshot:
        if compensation.regimen_laboral != "728":
            raise UnsupportedRegimen(
                f"Regime728Strategy received compensation with regimen_laboral="
                f"{compensation.regimen_laboral!r}; expected '728'."
            )

        end = period.end_date
        days_factor = Decimal(period.days_worked) / Decimal(30)

        # ----- catalog reads (period-end anchored) -----
        rmv = TaxParameter.get("RMV", end).value
        asig_fam_amt = TaxParameter.get("ASIG_FAMILIAR", end).value
        afp_fondo_rate = TaxParameter.get("AFP_FONDO_RATE", end).value
        prima_sisco_rate = TaxParameter.get("PRIMA_SISCO_RATE", end).value
        rma_sisco = TaxParameter.get("RMA_SISCO", end).value if TaxParameter.get("RMA_SISCO", end) else Decimal("999999999")
        onp_rate = TaxParameter.get("ONP_RATE", end).value
        essalud_rate = TaxParameter.get("ESSALUD_RATE", end).value
        eps_credit_rate = TaxParameter.get("EPS_CREDIT_RATE", end).value

        lines: list[PaySlipLine] = []

        # ----- INCOMES -----
        basic = _q(compensation.base_salary * days_factor)
        if basic > 0:
            lines.append(PaySlipLine(
                concept_code="BASIC_SALARY", sunat_code="0101", category="INCOME",
                amount=basic, base=basic,
            ))

        # asignación familiar (régimen-conditional + employee-conditional)
        asig_amount = Decimal("0.00")
        if (
            self.regimen_config.applies_asignacion_familiar
            and compensation.has_family_allowance
        ):
            asig_amount = _q(asig_fam_amt * days_factor)
            if asig_amount > 0:
                lines.append(PaySlipLine(
                    concept_code="ASIG_FAMILIAR", sunat_code="0104", category="INCOME",
                    amount=asig_amount, base=asig_amount,
                ))

        total_gross = sum((ln.amount for ln in lines if ln.category == "INCOME"), Decimal("0.00"))

        # asegurable = sum of income lines that affect AFP/ONP/EsSalud
        # (in D.4a, BASIC_SALARY + ASIG_FAMILIAR both do per N06-20/23)
        asegurable = total_gross

        # ----- DEDUCTIONS (worker-paid) -----
        pension = compensation.pension_regime
        if pension.startswith("AFP_"):
            fondo = _q(asegurable * afp_fondo_rate)
            if fondo > 0:
                lines.append(PaySlipLine(
                    concept_code="AFP_FONDO", sunat_code="0601", category="DEDUCTION",
                    amount=fondo, base=asegurable, rate=afp_fondo_rate,
                ))
            commission_rate = self._afp_commission_rate(pension, compensation.afp_commission_type, end)
            commission = _q(asegurable * commission_rate)
            prima_base = min(asegurable, rma_sisco)
            prima = _q(prima_base * prima_sisco_rate)
            comision_prima = _q(commission + prima)
            if comision_prima > 0:
                lines.append(PaySlipLine(
                    concept_code="AFP_COMISION_PRIMA", sunat_code="0606", category="DEDUCTION",
                    amount=comision_prima, base=asegurable,
                ))
        elif pension == "ONP":
            base_onp = max(asegurable, rmv) if total_gross > 0 else Decimal("0.00")
            onp = _q(base_onp * onp_rate)
            if onp > 0:
                lines.append(PaySlipLine(
                    concept_code="ONP", sunat_code="0601", category="DEDUCTION",
                    amount=onp, base=base_onp, rate=onp_rate,
                ))

        total_deductions = sum(
            (ln.amount for ln in lines if ln.category == "DEDUCTION"), Decimal("0.00")
        )

        # ----- EMPLOYER CONTRIBUTIONS -----
        base_essalud = max(asegurable, rmv) if total_gross > 0 else Decimal("0.00")
        if compensation.health_regime == "EPS":
            essalud_amt = _q(base_essalud * (essalud_rate - eps_credit_rate))
            eps_credit_amt = _q(base_essalud * eps_credit_rate)
            if essalud_amt > 0:
                lines.append(PaySlipLine(
                    concept_code="ESSALUD", sunat_code="0801", category="CONTRIBUTION_EMPLOYER",
                    amount=essalud_amt, base=base_essalud, rate=essalud_rate - eps_credit_rate,
                ))
            if eps_credit_amt > 0:
                lines.append(PaySlipLine(
                    concept_code="EPS_CREDIT", sunat_code="0802", category="CONTRIBUTION_EMPLOYER",
                    amount=eps_credit_amt, base=base_essalud, rate=eps_credit_rate,
                ))
        else:
            essalud_amt = _q(base_essalud * essalud_rate)
            if essalud_amt > 0:
                lines.append(PaySlipLine(
                    concept_code="ESSALUD", sunat_code="0801", category="CONTRIBUTION_EMPLOYER",
                    amount=essalud_amt, base=base_essalud, rate=essalud_rate,
                ))

        total_employer = sum(
            (ln.amount for ln in lines if ln.category == "CONTRIBUTION_EMPLOYER"), Decimal("0.00")
        )

        net_pay = _q(total_gross - total_deductions)

        return PaySlipSnapshot(
            employee_id=str(employee.id),
            period=period,
            regimen_laboral="728",
            lines=tuple(lines),
            total_gross=total_gross,
            total_deductions=total_deductions,
            total_employer_contributions=total_employer,
            net_pay=net_pay,
            metadata={
                "pension_regime": pension,
                "health_regime": compensation.health_regime,
                "days_worked": period.days_worked,
                "rmv_at_period": str(rmv),
            },
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _afp_commission_rate(pension_regime: str, commission_type: str, as_of_date: date) -> Decimal:
        """D.4a covers FLUJO only. MIXTA → D.4b (raise)."""
        if commission_type and commission_type.upper() == "MIXTA":
            raise NotImplementedError("AFP comisión MIXTA → D.4b")
        # Map AFP_INTEGRA → "AFP_INTEGRA_FLUJO", etc.
        code = f"{pension_regime}_FLUJO"
        param = TaxParameter.get(code, as_of_date)
        if param is None:
            raise ValueError(f"No TaxParameter row for {code} at {as_of_date}")
        return param.value

    # ------------------------------------------------------------------
    # Stubs for downstream phases — raise to surface accidental cross-phase calls
    # ------------------------------------------------------------------
    def compute_cts(self, employee, semester) -> CtsResult:
        raise NotImplementedError("D.7 implements compute_cts")

    def compute_gratification(self, employee, semester) -> GratiResult:
        raise NotImplementedError("D.8 implements compute_gratification")

    def compute_severance(self, employee, termination_date: date, cause: str) -> SettleResult:
        raise NotImplementedError("D.12 implements compute_severance")

    def compute_renta_5ta(self, employee, period: PayrollPeriod, accumulated: Decimal) -> Decimal:
        raise NotImplementedError("D.4b implements compute_renta_5ta")


RegimenStrategyFactory.register("728", Regime728Strategy)
```

- [ ] **Step 2.5: Run the golden cases → PASS**

```bash
pytest apps/payroll/tests/test_regime_728_payslip.py -v --create-db
```
Expected: 10 tests PASS.

- [ ] **Step 2.6: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/strategies/regime_728.py apps/api/apps/payroll/tests/_engine_helpers.py apps/api/apps/payroll/tests/test_regime_728_payslip.py
git -C D:/VYNTIA commit -m "feat(D4a): Regime728Strategy.compute_payslip REGULAR (income + AFP/ONP/EsSalud/EPS + asig fam) + 10 golden cases"
```

---

## Task 3: Full regression + close-out

- [ ] **Step 3.1: Full backend suite**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
python manage.py check --settings=vyntia.settings.development
pytest --tb=short -q --create-db 2>&1 | tail -8
```
Expected: check 0 silenced; **1081 + 13 = 1094 passed, 1 failed (`test_permisos_debug`), 17 skipped**, 0 new failures.

- [ ] **Step 3.2: Confirm no migrations were added**

```bash
python manage.py makemigrations --check --dry-run --settings=vyntia.settings.development
```
Expected: "No changes detected" (D.4a is compute-only).

- [ ] **Step 3.3: Check off backlog items**

In `.planning/audit-D/BACKLOG.md`, prefix `✅` to **#43, #49, #50, #51, #52, #53, #54, #55**. For **#44, #45, #46, #47, #48, #56, #57, #58, #62, #63, #64** (and others in D.4 originally) append ` _(→ D.4b)_` to the Item cell so it's clear they moved to the sibling sub-phase.

- [ ] **Step 3.4: Final commit**

```bash
git -C D:/VYNTIA add -f .planning/audit-D/BACKLOG.md
git -C D:/VYNTIA commit -m "docs(D4a): mark BACKLOG #43,#49-55 complete; flag Renta-5ta/edge items → D.4b"
git -C D:/VYNTIA log --oneline master..HEAD
```
Expected: ~4 commits on `vyntia/D4a-engine-728-monthly`.

---

## D.4a Done — Handoff to D.4b

`Regime728Strategy.compute_payslip(employee, compensation, period)` returns a complete `PaySlipSnapshot` for a REGULAR monthly period covering income lines, AFP/ONP, EsSalud/EPS, and asignación familiar — 10 hand-computed cases pass against the seeded catalog. D.5's `PayrollRunService` will iterate active employees in a tenant + period and call `compute_payslip` for each.

D.4b (`vyntia/D4b-engine-728-renta-5ta`) extends the engine with: 4-step Renta 5ta projection (#44-48) including December final adjustment, vacaciones récord/remuneración (#56,#57), subsidios incapacidad/maternidad (#60,#61), extranjeros no domiciliados 30% (#62), practicantes (#63), AFP licitación validator (#64), full ~30-case cartilla, and a **`REGULATORY-SIGNOFF.md`** artifact the user signs `APPROVED` before merge (ADR-D.8). Plan source: BACKLOG #44-48, #56-63, #66, #67; ADR-D.5 (Renta 5ta correction al cese — only the monthly part in D.4b; cese is D.12).
