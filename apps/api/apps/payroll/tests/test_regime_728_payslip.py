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
