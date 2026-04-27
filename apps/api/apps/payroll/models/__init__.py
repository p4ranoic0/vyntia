"""Payroll models — re-exports for backward-compatible imports."""

from .compensation import (
    AfpConfiguration,
    CompensationConfiguration,
    MassDeduction,
    MonthlyPayroll,
    PaymentSchedule,
    PayrollConcept,
    PayrollDetail,
    PaySlip,
)
from .tax_parameter import TaxParameter

__all__ = [
    "AfpConfiguration",
    "CompensationConfiguration",
    "MassDeduction",
    "MonthlyPayroll",
    "PaymentSchedule",
    "PayrollConcept",
    "PayrollDetail",
    "PaySlip",
    "TaxParameter",
]
