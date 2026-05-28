# D.2 — Catálogo Regulatorio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the three vendor-managed catalog models (`TaxParameter`, `PayrollConcept`, `RegimenConfig`) with date-versioned lookups, seed them with the real Peruvian regulatory values (UIT/RMV/asig 2024-2026, renta-5ta brackets, AFP/ONP/EsSalud rates, ~25 Tabla-22 concepts, régimen 728 config) via an idempotent `seed_payroll_catalog` command, and expose read-only API endpoints — so D.3/D.4 can compute payroll against a single source of regulatory truth.

**Architecture:** Greenfield models in the now-empty `apps.payroll` app (`models/catalog.py`). Per D-E the catalog is vendor-managed and **global** (no tenant FK) — except `PayrollConcept`, which is vendor-seeded (`tenant=NULL`) with optional per-tenant custom concepts (`tenant` not-null + `parent_concept` FK that inherits flags via `clean()`). Versioning is `(valid_from, valid_to)` with `Model.get(code, as_of_date)` classmethod lookups (ADR-D.6 tax-year cutoff). Decimals follow ADR-D.2 (`14,4` for rates/values). Read-only `ReadOnlyModelViewSet`s are registered under `/api/v1/payroll/catalog/` ahead of the D.1a 501 catch-all.

**Tech Stack:** Django 5.2 + DRF, pytest. No frontend code (the read-only API has no UI consumer until a later config-page rebuild).

**Source:** spec `2026-05-23-vyntia-D-vyntia-pay-design.md` § 4.1 + § 5 (D.2 row); ADR-D.2 (decimals), ADR-D.6 (tax-year cutoff); `.planning/audit-D/BACKLOG.md` #15-#17, #19-#21, #23-#31; INVENTORY § 5 (N06-20..N06-39 concept flags, N07 rates, N09 brackets).

---

## Scope decision (read before planning)

The spec § 4.1 + § 5 scope D.2 to **exactly three catalog models + seed + read-only admin + tests**. Several BACKLOG items the D.0 audit tagged `D.2` are **re-assigned to their consuming phases** because they are export/declaration concerns the spec does not place in D.2:

| Backlog item | Re-assigned to | Why |
|---|---|---|
| #18 `SunatTable` parametric tables (Tabla 1/8/9/11/12/13/17/18) | D.9 (PLAME) / D.10 (T-Registro) | Only consumed by PLAME/T-Registro file generation; spec § 4.1 lists no such model |
| #22 Tabla 19 Tipo Suspensión | D.9 (PLAME JORNA) | Needed by the PLAME JORNA file |
| #32-#38 Tabla mappings (régimen pensionario, tipo contrato, CIUO-08, tipo doc, jornada, tipo trabajador, régimen salud) | D.9 / D.10 | Mapping utilities consumed at export/declaration time |
| #118 Motivo cese Tabla 17 | D.12 (liquidación) | Consumed by severance/baja flow |

**In D.2 (this plan):** #15, #16, #17, #19, #20, #21, #23, #24, #25, #26, #27, #28, #29, #30, #31. These are the catalog models + their seed.

Model extensions beyond the spec's literal § 4.1 field list, justified by backlog/normativa: `PayrollConcept.is_remunerative` (#23 / N08-37), `PayrollConcept.is_variable` + `cts_min_frequency` (#28, #29 / N08-03) — these are concept-catalog attributes the seed sets once, avoiding a later D.7 migration.

---

## Baseline snapshot

| Check | Before D.2 | After D.2 |
|---|---|---|
| Backend pytest | 1064 passed, 1 failed (`test_permisos_debug`), 17 skipped | **1064 + N_new passed** (new model/seed/API tests), still 1 pre-existing failure, 17 skipped |
| `apps.payroll` models | 0 | 3 (`TaxParameter`, `PayrollConcept`, `RegimenConfig`) |
| `apps.payroll` migrations | 0001, 0002, 0003 | + `0004_catalog_models` |
| `seed_payroll_catalog` | absent | present + idempotent |
| `/api/v1/payroll/catalog/*` | 501 (catch-all) | read-only 200 (registered before catch-all) |
| `manage.py check` | 0 silenced | 0 silenced |

---

## Branch

`vyntia/D2-catalogo-regulatorio` — branched from `master` (HEAD `0a6fbdff`, the D.1b merge).

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/D2-catalogo-regulatorio
```

---

## File structure

**Create:**
- `apps/api/apps/payroll/models/catalog.py` — `TaxParameter`, `PayrollConcept`, `RegimenConfig`
- `apps/api/apps/payroll/migrations/0004_catalog_models.py` (generated)
- `apps/api/apps/payroll/management/__init__.py`, `apps/api/apps/payroll/management/commands/__init__.py`
- `apps/api/apps/payroll/management/commands/seed_payroll_catalog.py`
- `apps/api/api/v1/payroll/catalog_serializers.py` — 3 read-only serializers
- `apps/api/api/v1/payroll/catalog_views.py` — 3 `ReadOnlyModelViewSet`
- `apps/api/apps/payroll/tests/__init__.py`, `apps/api/apps/payroll/tests/test_catalog_models.py`, `test_seed_payroll_catalog.py`, `test_catalog_api.py`

**Modify:**
- `apps/api/apps/payroll/models/__init__.py` — re-export the 3 models
- `apps/api/api/v1/payroll/urls.py` — register catalog router BEFORE the 501 catch-all

**Do NOT touch:** the D.1a 501 stub behavior for non-catalog legacy paths; frontend; `audit_actions.py`.

---

## Task 1: Catalog models + migration (TDD)

**Files:**
- Create: `apps/api/apps/payroll/models/catalog.py`, `apps/api/apps/payroll/tests/{__init__.py,test_catalog_models.py}`
- Modify: `apps/api/apps/payroll/models/__init__.py`
- Create: `apps/api/apps/payroll/migrations/0004_catalog_models.py` (generated)

- [ ] **Step 1.1: Write failing model tests**

Create `apps/api/apps/payroll/tests/__init__.py` (empty) and `apps/api/apps/payroll/tests/test_catalog_models.py`:

```python
"""D.2 — catalog model behavior: date-versioned lookups + concept flag inheritance."""

from datetime import date
from decimal import Decimal

import pytest

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter


@pytest.mark.django_db
class TestTaxParameterLookup:
    def test_get_returns_row_valid_at_date(self):
        TaxParameter.objects.create(
            code="UIT", value=Decimal("5150"), unit="PEN",
            valid_from=date(2024, 1, 1), valid_to=date(2024, 12, 31),
        )
        TaxParameter.objects.create(
            code="UIT", value=Decimal("5500"), unit="PEN",
            valid_from=date(2026, 1, 1), valid_to=None,
        )
        assert TaxParameter.get("UIT", date(2024, 6, 15)).value == Decimal("5150")
        assert TaxParameter.get("UIT", date(2026, 6, 15)).value == Decimal("5500")
        # open-ended latest row covers forward dates
        assert TaxParameter.get("UIT", date(2027, 3, 1)).value == Decimal("5500")

    def test_get_returns_none_when_no_row_valid(self):
        assert TaxParameter.get("UIT", date(2020, 1, 1)) is None


@pytest.mark.django_db
class TestRegimenConfigLookup:
    def test_get_returns_active_config(self):
        RegimenConfig.objects.create(
            regimen_code="728", valid_from=date(2024, 1, 1), valid_to=None,
            vacation_days_annual=30, applies_asignacion_familiar=True,
            applies_cts=True, applies_gratification=True,
            cts_deposit_months=[5, 11], gratification_months=[7, 12],
            severance_indemnization_formula="1_5_SALARIES_PER_YEAR_CAPPED_12",
        )
        cfg = RegimenConfig.get("728", date(2026, 5, 1))
        assert cfg.vacation_days_annual == 30
        assert cfg.cts_deposit_months == [5, 11]


@pytest.mark.django_db
class TestPayrollConceptFlagInheritance:
    def test_custom_concept_inherits_parent_flags_on_clean(self):
        official = PayrollConcept.objects.create(
            code="BASIC_SALARY", sunat_code="0101", name="Remuneración básica",
            category="INCOME", subcategory="BASIC",
            affects_income_tax=True, affects_afp_onp=True, affects_essalud=True,
            affects_cts=True, affects_gratification=True, is_remunerative=True,
            tenant=None,
        )
        custom = PayrollConcept(
            code="BONO_X", sunat_code="0101", name="Bono interno",
            category="INCOME", subcategory="VARIABLE", parent_concept=official,
            # deliberately set conflicting flags — clean() must overwrite from parent
            affects_income_tax=False, affects_cts=False, is_remunerative=False,
            tenant_id=official.tenant_id,
        )
        custom.clean()
        assert custom.affects_income_tax is True
        assert custom.affects_cts is True
        assert custom.is_remunerative is True
```

- [ ] **Step 1.2: Run to confirm failure**

Run: `cd D:/VYNTIA/apps/api && pytest apps/payroll/tests/test_catalog_models.py -v`
Expected: FAIL with `ImportError`/`cannot import name 'TaxParameter'`.

- [ ] **Step 1.3: Create the models**

Create `apps/api/apps/payroll/models/catalog.py`:

```python
"""Vendor-managed regulatory catalog (D.2).

Global (no tenant FK) per decision D-E — except PayrollConcept, which is
vendor-seeded (tenant=NULL) with optional per-tenant custom concepts that
inherit their parent's affectation flags. All rows are date-versioned with
(valid_from, valid_to); lookups resolve the row valid at a given date
(ADR-D.6 tax-year cutoff). Decimals follow ADR-D.2.
"""

import uuid

from django.db import models


class _VersionedQuerySet(models.QuerySet):
    def valid_at(self, as_of_date):
        return self.filter(valid_from__lte=as_of_date).filter(
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=as_of_date)
        )


class TaxParameter(models.Model):
    """Date-versioned regulatory scalar (UIT, RMV, rates, renta-5ta brackets)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, db_index=True)
    value = models.DecimalField(max_digits=14, decimal_places=4)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    unit = models.CharField(
        max_length=8,
        choices=[("PEN", "Soles"), ("RATE", "Tasa"), ("UIT", "Múltiplo UIT")],
    )
    source_law = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    objects = _VersionedQuerySet.as_manager()

    class Meta:
        db_table = "payroll_tax_parameter"
        constraints = [
            models.UniqueConstraint(fields=["code", "valid_from"], name="uniq_taxparam_code_validfrom"),
        ]
        ordering = ["code", "-valid_from"]

    def __str__(self):
        return f"{self.code}={self.value} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def get(cls, code, as_of_date):
        """Return the TaxParameter for `code` valid on `as_of_date`, or None."""
        return cls.objects.filter(code=code).valid_at(as_of_date).order_by("-valid_from").first()


class PayrollConcept(models.Model):
    """SUNAT Tabla 22 concept (vendor) or tenant custom concept (parent-inherited)."""

    CATEGORY_CHOICES = [
        ("INCOME", "Ingreso"),
        ("DEDUCTION", "Descuento"),
        ("CONTRIBUTION_EMPLOYER", "Aporte empleador"),
        ("TAX", "Tributo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64)
    sunat_code = models.CharField(max_length=4, blank=True, default="")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=24, blank=True, default="")
    affects_income_tax = models.BooleanField(default=False)
    affects_afp_onp = models.BooleanField(default=False)
    affects_essalud = models.BooleanField(default=False)
    affects_cts = models.BooleanField(default=False)
    affects_gratification = models.BooleanField(default=False)
    is_remunerative = models.BooleanField(default=True)
    is_variable = models.BooleanField(default=False)
    cts_min_frequency = models.IntegerField(default=3)
    formula_code = models.CharField(max_length=64, blank=True, default="")
    parent_concept = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="custom_children"
    )
    tenant = models.ForeignKey(
        "tenancy.Tenant", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    is_active = models.BooleanField(default=True)

    _INHERITED_FLAGS = (
        "affects_income_tax", "affects_afp_onp", "affects_essalud",
        "affects_cts", "affects_gratification", "is_remunerative",
    )

    class Meta:
        db_table = "payroll_concept"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="uniq_concept_tenant_code"),
        ]
        ordering = ["sunat_code", "code"]

    def __str__(self):
        return f"{self.sunat_code or '----'} {self.code}"

    def clean(self):
        """Custom concepts inherit affectation flags from their parent (no override)."""
        if self.parent_concept_id:
            for flag in self._INHERITED_FLAGS:
                setattr(self, flag, getattr(self.parent_concept, flag))
            if not self.sunat_code:
                self.sunat_code = self.parent_concept.sunat_code


class RegimenConfig(models.Model):
    """Date-versioned per-régimen-laboral configuration (728 in MVP)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regimen_code = models.CharField(max_length=24, db_index=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    vacation_days_annual = models.IntegerField()
    applies_asignacion_familiar = models.BooleanField(default=True)
    applies_cts = models.BooleanField(default=True)
    applies_gratification = models.BooleanField(default=True)
    cts_deposit_months = models.JSONField(default=list)
    gratification_months = models.JSONField(default=list)
    severance_indemnization_formula = models.CharField(max_length=64)
    essalud_rate_override = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    policy_notes = models.TextField(blank=True, default="")

    objects = _VersionedQuerySet.as_manager()

    class Meta:
        db_table = "payroll_regimen_config"
        constraints = [
            models.UniqueConstraint(fields=["regimen_code", "valid_from"], name="uniq_regimen_code_validfrom"),
        ]
        ordering = ["regimen_code", "-valid_from"]

    def __str__(self):
        return f"{self.regimen_code} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def get(cls, regimen_code, as_of_date):
        return cls.objects.filter(regimen_code=regimen_code).valid_at(as_of_date).order_by("-valid_from").first()
```

- [ ] **Step 1.4: Re-export from the models package**

Replace `apps/api/apps/payroll/models/__init__.py` with:

```python
"""Payroll models — greenfield Vyntia Pay catalog (D.2 onward)."""

from .catalog import PayrollConcept, RegimenConfig, TaxParameter

__all__ = ["PayrollConcept", "RegimenConfig", "TaxParameter"]
```

- [ ] **Step 1.5: Generate the migration**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
python manage.py makemigrations payroll --name catalog_models --settings=vyntia.settings.development
```
Expected: `0004_catalog_models.py` with `CreateModel` for the 3 models + the unique constraints. Confirm `dependencies` includes `('payroll', '0003_drop_legacy_payroll')` and the tenant FK dependency on `tenancy`.

- [ ] **Step 1.6: Run model tests + check**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
pytest apps/payroll/tests/test_catalog_models.py -v --create-db
```
Expected: check 0 silenced; all tests PASS.

- [ ] **Step 1.7: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/models/ apps/api/apps/payroll/migrations/0004_catalog_models.py apps/api/apps/payroll/tests/
git -C D:/VYNTIA commit -m "feat(D2): catalog models TaxParameter + PayrollConcept + RegimenConfig"
```

---

## Task 2: `seed_payroll_catalog` management command (TDD)

**Files:**
- Create: `apps/api/apps/payroll/management/__init__.py`, `.../commands/__init__.py`, `.../commands/seed_payroll_catalog.py`
- Create: `apps/api/apps/payroll/tests/test_seed_payroll_catalog.py`

- [ ] **Step 2.1: Write failing seed test**

Create `apps/api/apps/payroll/tests/test_seed_payroll_catalog.py`:

```python
"""D.2 — seed_payroll_catalog seeds regulatory values and is idempotent."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter


@pytest.mark.django_db
class TestSeedPayrollCatalog:
    def test_seeds_key_regulatory_values(self):
        call_command("seed_payroll_catalog")

        # UIT 2026 = S/5,500 (N09-01)
        assert TaxParameter.get("UIT", date(2026, 6, 1)).value == Decimal("5500.0000")
        # ONP 13% and EsSalud 9% as RATE
        assert TaxParameter.get("ONP_RATE", date(2026, 6, 1)).value == Decimal("0.1300")
        assert TaxParameter.get("ESSALUD_RATE", date(2026, 6, 1)).value == Decimal("0.0900")
        # Concept 0101 basic salary affects everything
        basic = PayrollConcept.objects.get(sunat_code="0101", tenant__isnull=True)
        assert (basic.affects_income_tax, basic.affects_afp_onp, basic.affects_essalud,
                basic.affects_cts, basic.affects_gratification) == (True, True, True, True, True)
        # Concept 0109 grati FP: NO EsSalud (Ley 30334), NO CTS
        grati = PayrollConcept.objects.get(sunat_code="0109", tenant__isnull=True)
        assert grati.affects_essalud is False and grati.affects_cts is False
        assert grati.affects_income_tax is True
        # Concept 0120 CTS: affects nothing
        cts = PayrollConcept.objects.get(sunat_code="0120", tenant__isnull=True)
        assert not any([cts.affects_income_tax, cts.affects_afp_onp, cts.affects_essalud,
                        cts.affects_cts, cts.affects_gratification])
        # Régimen 728
        cfg = RegimenConfig.get("728", date(2026, 6, 1))
        assert cfg.vacation_days_annual == 30 and cfg.cts_deposit_months == [5, 11]

    def test_idempotent(self):
        call_command("seed_payroll_catalog")
        tp1, pc1, rc1 = TaxParameter.objects.count(), PayrollConcept.objects.count(), RegimenConfig.objects.count()
        call_command("seed_payroll_catalog")
        assert (TaxParameter.objects.count(), PayrollConcept.objects.count(), RegimenConfig.objects.count()) == (tp1, pc1, rc1)
```

- [ ] **Step 2.2: Run to confirm failure**

Run: `pytest apps/payroll/tests/test_seed_payroll_catalog.py -v`
Expected: FAIL with `CommandError: Unknown command 'seed_payroll_catalog'`.

- [ ] **Step 2.3: Create the seed command**

Create the package markers `apps/api/apps/payroll/management/__init__.py` and `apps/api/apps/payroll/management/commands/__init__.py` (both empty), then `apps/api/apps/payroll/management/commands/seed_payroll_catalog.py`:

```python
"""Seed the vendor regulatory catalog (TaxParameter + PayrollConcept + RegimenConfig).

Idempotent: upserts by the model's natural key. Values cite Peruvian normativa
(INVENTORY § 5 N06/N07/N09). NOT a regulatory sign-off gate — D.4's golden
cartilla validates the numbers downstream.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter

D = Decimal

# (code, value, unit, valid_from, valid_to, source_law, metadata)
# UIT/RMV/asig: latest known year (2026) has valid_to=None so forward dates resolve
# until the next D.S. is published and seeded (ADR-D.6).
TAX_PARAMETERS = [
    ("UIT", D("5150"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "D.S. 309-2023-EF", {}),
    ("UIT", D("5350"), "PEN", date(2025, 1, 1), date(2025, 12, 31), "D.S. 260-2024-EF", {}),
    ("UIT", D("5500"), "PEN", date(2026, 1, 1), None, "D.S. 2026 (pending cite)", {}),
    ("RMV", D("1025"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "D.S. 003-2022-TR", {}),
    ("RMV", D("1130"), "PEN", date(2025, 1, 1), None, "D.S. 2024-TR", {}),
    ("ASIG_FAMILIAR", D("102.50"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "10% RMV (N08-33)", {}),
    ("ASIG_FAMILIAR", D("113.00"), "PEN", date(2025, 1, 1), None, "10% RMV (N08-33)", {}),
    ("ONP_RATE", D("0.1300"), "RATE", date(2024, 1, 1), None, "N07-10", {}),
    ("ESSALUD_RATE", D("0.0900"), "RATE", date(2024, 1, 1), None, "N07-13", {}),
    ("EPS_CREDIT_RATE", D("0.0225"), "RATE", date(2024, 1, 1), None, "N07-19", {}),
    ("AFP_FONDO_RATE", D("0.1000"), "RATE", date(2024, 1, 1), None, "N07-01", {}),
    ("PRIMA_SISCO_RATE", D("0.0137"), "RATE", date(2026, 1, 1), None, "N07-02", {}),
    ("RMA_SISCO", D("12598.91"), "PEN", date(2026, 4, 1), date(2026, 6, 30), "SBS Abr-Jun 2026 (N07-03)", {}),
    # AFP commission rates (flujo) — N07-04
    ("AFP_INTEGRA_FLUJO", D("0.0155"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_PRIMA_FLUJO", D("0.0160"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_PROFUTURO_FLUJO", D("0.0169"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_HABITAT_FLUJO", D("0.0147"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    # Renta 5ta progressive brackets 2026 (N09-04/05) — metadata holds soles bounds
    ("RENTA_5TA_TRAMO_1", D("0.08"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_max": 5}),
    ("RENTA_5TA_TRAMO_2", D("0.14"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 5, "uit_max": 20}),
    ("RENTA_5TA_TRAMO_3", D("0.17"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 20, "uit_max": 35}),
    ("RENTA_5TA_TRAMO_4", D("0.20"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 35, "uit_max": 45}),
    ("RENTA_5TA_TRAMO_5", D("0.30"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 45}),
    ("RENTA_5TA_DEDUCCION_UIT", D("7"), "UIT", date(2024, 1, 1), None, "N09-02", {}),
]

# (code, sunat_code, name, category, subcategory, IT, AFP, ES, CTS, GRA, remun, variable)
# Flags per INVENTORY § 5 N06-20..N06-39 + Ley 30334 (grati no EsSalud).
CONCEPTS = [
    ("BASIC_SALARY", "0101", "Remuneración básica", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("ALIMENTACION_ESPECIE", "0102", "Alimentación principal en especie", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("COMISIONES", "0103", "Comisiones regulares", "INCOME", "VARIABLE", 1, 1, 1, 1, 1, 1, 1),
    ("ASIG_FAMILIAR", "0104", "Asignación familiar", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("OVERTIME", "0106", "Horas extras", "INCOME", "VARIABLE", 1, 1, 1, 1, 1, 1, 1),
    ("VACATION_PAY", "0107", "Vacaciones", "INCOME", "BASIC", 1, 1, 1, 0, 1, 1, 0),
    ("REINTEGROS", "0108", "Reintegros", "INCOME", "VARIABLE", 1, 1, 1, 0, 1, 1, 1),
    ("GRATI_FP", "0109", "Gratificación Fiestas Patrias", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("GRATI_NAV", "0110", "Gratificación Navidad", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("GRATI_TRUNCA", "0111", "Gratificación trunca", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("BONIF_EXTRA_30334", "0121", "Bonificación extraordinaria Ley 30334", "INCOME", "EXTRAORDINARY", 1, 0, 0, 0, 0, 0, 0),
    ("MOVILIDAD_SUPEDITADA", "0115", "Movilidad supeditada a asistencia", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("REFRIGERIO", "0116", "Refrigerio no principal", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("CTS", "0120", "Compensación por Tiempo de Servicios", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("INDEM_VAC_NO_GOZADAS", "0501", "Indemnización vacaciones no gozadas", "INCOME", "EXTRAORDINARY", 1, 0, 0, 0, 0, 0, 0),
    ("INDEM_DESPIDO", "0503", "Indemnización por despido arbitrario", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_FONDO", "0601", "Aporte obligatorio AFP (fondo)", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("RENTA_5TA", "0605", "Retención Renta 5ta categoría", "TAX", "INCOME_TAX", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_COMISION_PRIMA", "0606", "Comisión + Prima AFP", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_VOLUNTARIO", "0607", "Aporte voluntario AFP", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("ESSALUD", "0801", "Aporte EsSalud 9%", "CONTRIBUTION_EMPLOYER", "HEALTH", 0, 0, 0, 0, 0, 0, 0),
    # Present but not applicable for MVP 728 oficinas (#24, #25) — is_active=False handled below
    ("SCTR_SALUD", "0803", "SCTR Salud", "CONTRIBUTION_EMPLOYER", "HEALTH", 0, 0, 0, 0, 0, 0, 0),
    ("SCTR_PENSION", "0804", "SCTR Pensiones", "CONTRIBUTION_EMPLOYER", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("SENATI", "0805", "SENATI", "CONTRIBUTION_EMPLOYER", "BASIC", 0, 0, 0, 0, 0, 0, 0),
    ("SENCICO", "0806", "SENCICO", "CONTRIBUTION_EMPLOYER", "BASIC", 0, 0, 0, 0, 0, 0, 0),
]
_INACTIVE_CODES = {"SCTR_SALUD", "SCTR_PENSION", "SENATI", "SENCICO"}  # #24, #25

REGIMEN_728 = dict(
    regimen_code="728", valid_from=date(2024, 1, 1), valid_to=None,
    vacation_days_annual=30, applies_asignacion_familiar=True,
    applies_cts=True, applies_gratification=True,
    cts_deposit_months=[5, 11], gratification_months=[7, 12],
    severance_indemnization_formula="1_5_SALARIES_PER_YEAR_CAPPED_12",
    policy_notes="Régimen laboral privado D.Leg. 728 (N01).",
)


class Command(BaseCommand):
    help = "Seed the vendor regulatory catalog (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        tp = self._seed_tax_parameters()
        pc = self._seed_concepts()
        rc = self._seed_regimen()
        self.stdout.write(self.style.SUCCESS(
            f"Catalog seeded: {tp} tax params, {pc} concepts, {rc} régimen configs."
        ))

    def _seed_tax_parameters(self):
        n = 0
        for code, value, unit, vfrom, vto, law, meta in TAX_PARAMETERS:
            TaxParameter.objects.update_or_create(
                code=code, valid_from=vfrom,
                defaults=dict(value=value, unit=unit, valid_to=vto, source_law=law, metadata=meta),
            )
            n += 1
        return n

    def _seed_concepts(self):
        n = 0
        for code, sunat, name, cat, sub, it, afp, es, cts, gra, remun, var in CONCEPTS:
            PayrollConcept.objects.update_or_create(
                tenant=None, code=code,
                defaults=dict(
                    sunat_code=sunat, name=name, category=cat, subcategory=sub,
                    affects_income_tax=bool(it), affects_afp_onp=bool(afp),
                    affects_essalud=bool(es), affects_cts=bool(cts),
                    affects_gratification=bool(gra), is_remunerative=bool(remun),
                    is_variable=bool(var), is_active=code not in _INACTIVE_CODES,
                ),
            )
            n += 1
        return n

    def _seed_regimen(self):
        RegimenConfig.objects.update_or_create(
            regimen_code="728", valid_from=REGIMEN_728["valid_from"],
            defaults={k: v for k, v in REGIMEN_728.items() if k not in ("regimen_code", "valid_from")},
        )
        return 1
```

- [ ] **Step 2.4: Run seed tests + verify idempotency**

```bash
cd D:/VYNTIA/apps/api
pytest apps/payroll/tests/test_seed_payroll_catalog.py -v --create-db
```
Expected: both tests PASS.

- [ ] **Step 2.5: Commit**

```bash
git -C D:/VYNTIA add apps/api/apps/payroll/management/ apps/api/apps/payroll/tests/test_seed_payroll_catalog.py
git -C D:/VYNTIA commit -m "feat(D2): seed_payroll_catalog idempotent command (UIT/RMV/AFP/renta-5ta/Tabla22/728)"
```

---

## Task 3: Read-only catalog API (TDD)

**Files:**
- Create: `apps/api/api/v1/payroll/catalog_serializers.py`, `catalog_views.py`
- Modify: `apps/api/api/v1/payroll/urls.py`
- Create: `apps/api/apps/payroll/tests/test_catalog_api.py`

- [ ] **Step 3.1: Write failing API test**

Create `apps/api/apps/payroll/tests/test_catalog_api.py`:

```python
"""D.2 — read-only catalog endpoints registered before the legacy 501 catch-all."""

import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.identity.models import User  # adjust import if User lives elsewhere


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username="cat_admin", password="x")  # adapt to project factory
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
class TestCatalogApi:
    def test_tax_parameters_list_read_only(self, auth_client):
        call_command("seed_payroll_catalog")
        resp = auth_client.get("/api/v1/payroll/catalog/tax-parameters/")
        assert resp.status_code == 200
        # write is not allowed (ReadOnlyModelViewSet → 405)
        assert auth_client.post("/api/v1/payroll/catalog/tax-parameters/", {}).status_code == 405

    def test_legacy_path_still_501(self, auth_client):
        # non-catalog legacy path still hits the D.1a stub
        assert auth_client.get("/api/v1/payroll/monthly-runs/").status_code == 501
```

> NOTE for implementer: confirm the project's actual User model + test auth helper (look at an existing API test, e.g. `apps/api/tests/` or `apps/api/api/v1/auth/test_views.py`) and mirror its authentication/tenant setup. Adapt the `auth_client` fixture accordingly before running.

- [ ] **Step 3.2: Run to confirm failure**

Run: `pytest apps/payroll/tests/test_catalog_api.py -v --create-db`
Expected: FAIL (catalog routes 501 via catch-all, or import error).

- [ ] **Step 3.3: Create serializers**

Create `apps/api/api/v1/payroll/catalog_serializers.py`:

```python
"""Read-only serializers for the vendor regulatory catalog (D.2)."""

from rest_framework import serializers

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter


class TaxParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxParameter
        fields = ["id", "code", "value", "unit", "valid_from", "valid_to", "source_law", "metadata"]


class PayrollConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollConcept
        fields = [
            "id", "code", "sunat_code", "name", "category", "subcategory",
            "affects_income_tax", "affects_afp_onp", "affects_essalud",
            "affects_cts", "affects_gratification", "is_remunerative",
            "is_variable", "cts_min_frequency", "formula_code",
            "parent_concept", "tenant", "is_active",
        ]


class RegimenConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegimenConfig
        fields = [
            "id", "regimen_code", "valid_from", "valid_to", "vacation_days_annual",
            "applies_asignacion_familiar", "applies_cts", "applies_gratification",
            "cts_deposit_months", "gratification_months",
            "severance_indemnization_formula", "essalud_rate_override", "policy_notes",
        ]
```

- [ ] **Step 3.4: Create read-only viewsets**

Create `apps/api/api/v1/payroll/catalog_views.py`:

```python
"""Read-only catalog viewsets (D.2). Catalog is vendor-managed (seed only)."""

from rest_framework import viewsets

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter

from .catalog_serializers import (
    PayrollConceptSerializer,
    RegimenConfigSerializer,
    TaxParameterSerializer,
)


class TaxParameterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaxParameter.objects.all()
    serializer_class = TaxParameterSerializer
    filterset_fields = ["code", "unit"]


class PayrollConceptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PayrollConcept.objects.all()
    serializer_class = PayrollConceptSerializer
    filterset_fields = ["category", "sunat_code", "is_active"]


class RegimenConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegimenConfig.objects.all()
    serializer_class = RegimenConfigSerializer
    filterset_fields = ["regimen_code"]
```

> NOTE for implementer: if the project's default `filter_backends` does not include `DjangoFilterBackend` globally, either add `filter_backends = [DjangoFilterBackend]` per viewset or drop `filterset_fields`. Verify against an existing viewset before finalizing.

- [ ] **Step 3.5: Register catalog routes BEFORE the 501 catch-all**

Replace `apps/api/api/v1/payroll/urls.py` with:

```python
"""URLs for payroll bounded context.

D.2 registers read-only catalog endpoints under /catalog/. Every OTHER legacy
/api/v1/payroll/* path still returns the D.1a 501 stub (catch-all is LAST).
"""

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.v1.payroll.catalog_views import (
    PayrollConceptViewSet,
    RegimenConfigViewSet,
    TaxParameterViewSet,
)
from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

catalog_router = DefaultRouter()
catalog_router.register(r"tax-parameters", TaxParameterViewSet, basename="tax-parameter")
catalog_router.register(r"payroll-concepts", PayrollConceptViewSet, basename="payroll-concept")
catalog_router.register(r"regimen-configs", RegimenConfigViewSet, basename="regimen-config")

urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]
```

- [ ] **Step 3.6: Run API tests**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development
pytest apps/payroll/tests/test_catalog_api.py -v --create-db
```
Expected: check clean; tests PASS (catalog 200/405; legacy 501).

- [ ] **Step 3.7: Commit**

```bash
git -C D:/VYNTIA add apps/api/api/v1/payroll/ apps/api/apps/payroll/tests/test_catalog_api.py
git -C D:/VYNTIA commit -m "feat(D2): read-only catalog API under /api/v1/payroll/catalog/ (legacy stays 501)"
```

---

## Task 4: Full regression + close-out

- [ ] **Step 4.1: Full backend suite**

```bash
cd D:/VYNTIA/apps/api && source D:/VYNTIA/.venv/Scripts/activate
python manage.py check --settings=vyntia.settings.development
pytest --tb=short -q --create-db 2>&1 | tail -8
```
Expected: check 0 silenced; **1064 + N_new passed, 1 failed (`test_permisos_debug`), 17 skipped**, 0 new failures. (N_new = the D.2 tests added.)

- [ ] **Step 4.2: Migration sanity — no missing migrations**

```bash
cd D:/VYNTIA/apps/api
python manage.py makemigrations --check --dry-run --settings=vyntia.settings.development
```
Expected: "No changes detected" (the model + migration are in sync).

- [ ] **Step 4.3: Check off backlog items**

In `.planning/audit-D/BACKLOG.md`, mark done (prefix `✅`): #15, #16, #17, #19, #20, #21, #23, #24, #25, #26, #27, #28, #29, #30, #31. For #18, #22, #32-#38, #118: leave unchecked but append `→ re-scoped to D.9/D.10/D.12 (see D2 plan Scope decision)` to each Item cell.

- [ ] **Step 4.4: Final commit**

```bash
git -C D:/VYNTIA add -f .planning/audit-D/BACKLOG.md
git -C D:/VYNTIA commit -m "docs(D2): mark catalog backlog items complete + re-scope parametric tables to D.9/D.10"
git -C D:/VYNTIA log --oneline master..HEAD
```
Expected: ~5 commits on `vyntia/D2-catalogo-regulatorio`.

---

## D.2 Done — Handoff to D.3

The regulatory catalog exists, is seeded, and is queryable (`TaxParameter.get`, `RegimenConfig.get`, `PayrollConcept` by sunat_code). D.3 (`vyntia/D3-compensation-contract`) adds the tenant-scoped `Compensation` model (§ 4.2) + `migrate_employment_to_compensation` command + `/api/v1/payroll/compensations/`, reading régimen/UIT from this catalog. Generate `2026-05-XX-vyntia-D3-compensation-contract.md` with `writing-plans` using BACKLOG #39-#42.

---

## Decisions locked in this plan

1. **Scope = spec § 4.1 (3 catalog models), not the full audit D.2 tag.** `SunatTable` (#18), Tabla-19 (#22), Tabla mappings (#32-#38), Tabla-17 (#118) are re-scoped to their consuming phases (D.9/D.10/D.12). The spec is the authoritative design contract; those parametric tables are export/declaration concerns.
2. **Model extensions beyond spec § 4.1 field list:** `is_remunerative`, `is_variable`, `cts_min_frequency` added to `PayrollConcept` per BACKLOG #23/#28/#29 (N08-37/N08-03) — set once by the seed, avoids a D.7 migration.
3. **Open-ended latest version:** the most recent year's `TaxParameter`/`RegimenConfig` rows use `valid_to=NULL` so forward dates resolve until the next D.S. is published and seeded (ADR-D.6). UIT 2027 / RMA future quarters are added when published.
4. **Catalog is read-only over the API + vendor-seeded.** No create/update endpoints (D-E: tenants must not edit UIT). Tenant *custom* `PayrollConcept` creation (parent-inherited) is a later config-phase concern, not D.2.
5. **Seed values are best-known, not sign-off-gated.** D.2 has no ⚠️ gate; D.4's golden cartilla SUNAT validates the numbers. Source-law cites with "(pending cite)" are flagged for the D.4 sign-off to confirm.
