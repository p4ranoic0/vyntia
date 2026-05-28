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
