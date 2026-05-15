"""probation_service — ProbationPeriod helpers (B.11).

create_for_contract is a service helper (not a Django signal) so the seam is
explicit. The list_alertas_* helpers expose 30d / 15d windows for the dashboard
or future cron infrastructure.

See Module 03.4 and ROADMAP-B.md backlog #116.
"""

from __future__ import annotations

from datetime import date, timedelta

from django.db.models import F, Q
from django.utils import timezone

from apps.contracts.models import ProbationPeriod
from apps.contracts.models.probation_period import PLAZO_DIAS


def create_for_contract(
    *,
    contract,
    regimen: str = '728_comun',
    start_date: date | None = None,
    tenant=None,
) -> ProbationPeriod:
    """Create a ProbationPeriod for a Contract; defaults to regimen 728_comun."""
    if start_date is None:
        start_date = getattr(contract, 'fecha_inicio', None) or date.today()
    if tenant is None:
        tenant = getattr(contract, 'tenant', None)
    return ProbationPeriod.objects.create(
        tenant=tenant,
        contract=contract,
        regimen=regimen,
        start_date=start_date,
    )


def list_overdue(tenant=None):
    """ProbationPeriods whose end_date has passed and decision pending."""
    qs = ProbationPeriod.objects.filter(
        status__in=['pending', 'in_progress', 'evaluated'],
        end_date__lt=date.today(),
    )
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    return qs


def _alertas_window(days: int, tenant=None):
    today = date.today()
    cutoff = today + timedelta(days=days)
    qs = ProbationPeriod.objects.filter(
        status__in=['pending', 'in_progress'],
        end_date__gte=today,
        end_date__lte=cutoff,
    )
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    return qs


def list_alertas_30d(tenant=None):
    return _alertas_window(30, tenant=tenant)


def list_alertas_15d(tenant=None):
    return _alertas_window(15, tenant=tenant)
