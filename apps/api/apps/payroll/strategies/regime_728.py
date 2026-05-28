"""Régimen 728 strategy (D.4a — monthly REGULAR + stubs for the rest)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from .base import (
    CtsResult,
    GratiResult,
    PayrollPeriod,
    PaySlipSnapshot,
    RegimenStrategy,
    SettleResult,
    UnsupportedRegimen,
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


def _register():
    from apps.payroll.strategies import RegimenStrategyFactory
    RegimenStrategyFactory.register("728", Regime728Strategy)
