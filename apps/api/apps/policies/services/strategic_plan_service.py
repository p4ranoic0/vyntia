"""Strategic plan lifecycle service (B.15b)."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.policies.models import HRStrategicPlan, KPI, StrategicObjective


def create_plan(
    *,
    tenant,
    name: str,
    fiscal_year: int,
    period_start,
    period_end,
    owner_user,
    description: str = '',
) -> HRStrategicPlan:
    if period_end < period_start:
        raise ValidationError('period_end debe ser >= period_start.')
    return HRStrategicPlan.objects.create(
        tenant=tenant,
        name=name.strip(),
        fiscal_year=fiscal_year,
        period_start=period_start,
        period_end=period_end,
        owner_user=owner_user,
        description=description,
        status='draft',
    )


def add_objective(
    *,
    plan: HRStrategicPlan,
    code: str,
    title: str,
    weight: Decimal | float | int,
    description: str = '',
    owner_user=None,
    order: int = 0,
) -> StrategicObjective:
    if Decimal(str(weight)) < 0:
        raise ValidationError('weight no puede ser negativo.')
    return StrategicObjective.objects.create(
        plan=plan,
        code=code,
        title=title.strip(),
        description=description,
        weight=Decimal(str(weight)),
        order=order,
        owner_user=owner_user,
    )


def add_kpi(
    *,
    objective: StrategicObjective,
    name: str,
    target: Decimal | float | int,
    target_date=None,
    unit: str = '',
    formula_note: str = '',
) -> KPI:
    return KPI.objects.create(
        objective=objective,
        name=name.strip(),
        target=Decimal(str(target)),
        target_date=target_date,
        unit=unit,
        formula_note=formula_note,
        actual=Decimal('0'),
        status='on_track',
    )


def update_kpi_actual(
    *,
    kpi: KPI,
    actual: Decimal | float | int,
    status: Optional[str] = None,
) -> KPI:
    kpi.actual = Decimal(str(actual))
    if status is not None:
        if status not in dict(KPI.STATUSES):
            raise ValidationError('status inválido.')
        kpi.status = status
    else:
        kpi.status = _derive_kpi_status(kpi)
    kpi.save(update_fields=['actual', 'status', 'updated_at'])
    return kpi


def _derive_kpi_status(kpi: KPI) -> str:
    if kpi.target == 0:
        return 'on_track'
    pct = (kpi.actual / kpi.target) * Decimal('100')
    if pct >= Decimal('100'):
        return 'done'
    if pct >= Decimal('80'):
        return 'on_track'
    if pct >= Decimal('50'):
        return 'at_risk'
    return 'off_track'


@transaction.atomic
def mark_active(plan: HRStrategicPlan, user=None) -> HRStrategicPlan:
    if plan.status != 'draft':
        raise ValidationError('Solo planes en borrador pueden activarse.')
    plan.status = 'active'
    plan.approved_by = user
    plan.approved_at = timezone.now()
    plan.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
    return plan


def mark_completed(plan: HRStrategicPlan) -> HRStrategicPlan:
    if plan.status not in {'active'}:
        raise ValidationError('Solo planes activos pueden completarse.')
    plan.status = 'completed'
    plan.save(update_fields=['status', 'updated_at'])
    return plan


def archive(plan: HRStrategicPlan) -> HRStrategicPlan:
    plan.status = 'archived'
    plan.save(update_fields=['status', 'updated_at'])
    return plan


def compute_progress(plan: HRStrategicPlan) -> dict:
    """Returns {objectives: [...], overall_pct: Decimal}.

    Cada objective contribuye con `weight * avg(kpi.progress_pct) / 100`.
    """
    objectives = []
    total_weight = Decimal('0')
    weighted_sum = Decimal('0')

    for obj in plan.objectives.all().prefetch_related('kpis'):
        kpi_progress = [k.progress_pct() for k in obj.kpis.all()]
        avg = (
            sum(kpi_progress, Decimal('0')) / len(kpi_progress)
            if kpi_progress
            else Decimal('0')
        )
        weight = Decimal(str(obj.weight))
        weighted_sum += avg * weight / Decimal('100')
        total_weight += weight
        objectives.append({
            'id': str(obj.id),
            'code': obj.code,
            'title': obj.title,
            'weight': str(weight),
            'avg_progress_pct': str(avg.quantize(Decimal('0.01'))),
            'kpi_count': len(kpi_progress),
        })

    overall = (weighted_sum.quantize(Decimal('0.01'))) if total_weight else Decimal('0')
    return {
        'objectives': objectives,
        'overall_pct': str(overall),
        'total_weight': str(total_weight),
    }
