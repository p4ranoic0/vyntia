"""Strategy factory for régimen-specific payroll engines (D.4a).

Concrete strategies self-register via `RegimenStrategyFactory.register("CODE", Cls)`
at module-import time (see `regime_728.py`). The factory binds the strategy
to its `RegimenConfig` row valid at `as_of_date` so the strategy itself never
re-reads versioning.
"""

from __future__ import annotations

from datetime import date

from .base import (
    CtsResult,
    GratiResult,
    PayrollPeriod,
    PaySlipLine,
    PaySlipSnapshot,
    RegimenConfigMissing,
    RegimenStrategy,
    SettleResult,
    UnsupportedRegimen,
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
from .regime_728 import Regime728Strategy  # noqa: E402, F401
RegimenStrategyFactory.register("728", Regime728Strategy)
