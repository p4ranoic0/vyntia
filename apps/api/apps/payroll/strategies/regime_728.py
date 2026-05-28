"""Régimen 728 strategy (D.4a — monthly REGULAR + stubs)."""

from __future__ import annotations

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from apps.payroll.models import TaxParameter

from .base import (
    CtsResult,
    GratiResult,
    PayrollPeriod,
    PaySlipLine,
    PaySlipSnapshot,
    RegimenStrategy,
    SettleResult,
    UnsupportedRegimen,
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
        rma_sisco_row = TaxParameter.get("RMA_SISCO", end)
        rma_sisco = rma_sisco_row.value if rma_sisco_row else Decimal("999999999")
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


def _register():
    from apps.payroll.strategies import RegimenStrategyFactory
    RegimenStrategyFactory.register("728", Regime728Strategy)
