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
