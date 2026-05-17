"""Workforce + Succession plan service (B.15b)."""

from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.policies.models import (
    HeadcountProjection,
    KeyPosition,
    SuccessionPlan,
    SuccessorCandidate,
    WorkforcePlan,
)


def create_plan(
    *,
    tenant,
    name: str,
    fiscal_year: int,
    period_start,
    period_end,
    owner_user,
    description: str = '',
) -> WorkforcePlan:
    if period_end < period_start:
        raise ValidationError('period_end debe ser >= period_start.')
    return WorkforcePlan.objects.create(
        tenant=tenant,
        name=name.strip(),
        fiscal_year=fiscal_year,
        period_start=period_start,
        period_end=period_end,
        owner_user=owner_user,
        description=description,
        status='draft',
    )


def add_projection(
    *,
    plan: WorkforcePlan,
    current_headcount: int,
    projected_headcount: int,
    area=None,
    position=None,
    justification: str = '',
    target_quarter: str = 'Q1',
) -> HeadcountProjection:
    if current_headcount < 0 or projected_headcount < 0:
        raise ValidationError('Headcount no puede ser negativo.')
    if target_quarter not in dict(HeadcountProjection.QUARTERS):
        raise ValidationError('target_quarter inválido.')
    return HeadcountProjection.objects.create(
        plan=plan,
        area=area,
        position=position,
        current_headcount=current_headcount,
        projected_headcount=projected_headcount,
        justification=justification,
        target_quarter=target_quarter,
    )


def create_succession_plan(
    *,
    tenant,
    name: str,
    fiscal_year: int,
    owner_user,
    notes: str = '',
) -> SuccessionPlan:
    return SuccessionPlan.objects.create(
        tenant=tenant,
        name=name.strip(),
        fiscal_year=fiscal_year,
        owner_user=owner_user,
        notes=notes,
        status='draft',
    )


def add_key_position(
    *,
    succession_plan: SuccessionPlan,
    position,
    criticality: str = 'media',
    current_holder=None,
    risk_notes: str = '',
) -> KeyPosition:
    if criticality not in dict(KeyPosition.CRITICALITY):
        raise ValidationError('criticality inválida.')
    key_pos, _created = KeyPosition.objects.get_or_create(
        plan=succession_plan,
        position=position,
        defaults={
            'criticality': criticality,
            'current_holder': current_holder,
            'risk_notes': risk_notes,
        },
    )
    return key_pos


def add_successor(
    *,
    key_position: KeyPosition,
    employee,
    readiness_level: int = 4,
    order: int = 0,
    notes: str = '',
) -> SuccessorCandidate:
    if readiness_level not in {1, 2, 3, 4}:
        raise ValidationError('readiness_level debe ser 1..4.')
    candidate, _created = SuccessorCandidate.objects.update_or_create(
        key_position=key_position,
        employee=employee,
        defaults={
            'readiness_level': readiness_level,
            'order': order,
            'notes': notes,
        },
    )
    return candidate
