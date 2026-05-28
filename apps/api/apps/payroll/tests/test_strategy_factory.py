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
