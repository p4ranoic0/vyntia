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
