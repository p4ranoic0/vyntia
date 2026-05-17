"""Compliance matrix + obligation + evidence service (B.15b)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone

from apps.policies.models import (
    ComplianceMatrix,
    ComplianceObligation,
    Evidence,
)


FREQUENCY_TO_DELTA = {
    'mensual': timedelta(days=30),
    'trimestral': timedelta(days=90),
    'semestral': timedelta(days=182),
    'anual': timedelta(days=365),
}


def create_matrix(
    *,
    tenant,
    name: str,
    fiscal_year: int,
    owner_user,
    description: str = '',
) -> ComplianceMatrix:
    return ComplianceMatrix.objects.create(
        tenant=tenant,
        name=name.strip(),
        fiscal_year=fiscal_year,
        owner_user=owner_user,
        description=description,
        status='active',
    )


def add_obligation(
    *,
    matrix: ComplianceMatrix,
    code: str,
    title: str,
    source: str,
    frequency: str,
    next_due_date,
    description: str = '',
    severity: str = 'media',
    responsible_user=None,
) -> ComplianceObligation:
    if source not in dict(ComplianceObligation.SOURCES):
        raise ValidationError('source inválida.')
    if frequency not in dict(ComplianceObligation.FREQUENCIES):
        raise ValidationError('frequency inválida.')
    if severity not in dict(ComplianceObligation.SEVERITIES):
        raise ValidationError('severity inválida.')
    return ComplianceObligation.objects.create(
        matrix=matrix,
        code=code,
        title=title.strip(),
        description=description,
        source=source,
        frequency=frequency,
        severity=severity,
        next_due_date=next_due_date,
        responsible_user=responsible_user,
        status='pendiente',
    )


def attach_evidence(
    *,
    obligation: ComplianceObligation,
    kind: str,
    file=None,
    url: str = '',
    note: str = '',
    captured_by=None,
) -> Evidence:
    if kind not in dict(Evidence.KINDS):
        raise ValidationError('kind inválido.')
    if kind == 'archivo' and not file:
        raise ValidationError('file requerido cuando kind=archivo.')
    if kind == 'link' and not url:
        raise ValidationError('url requerida cuando kind=link.')
    if kind == 'nota' and not note:
        raise ValidationError('note requerida cuando kind=nota.')
    return Evidence.objects.create(
        tenant=obligation.matrix.tenant,
        obligation=obligation,
        kind=kind,
        file=file,
        url=url,
        note=note,
        captured_by=captured_by,
    )


def mark_obligation_completed(
    *,
    obligation: ComplianceObligation,
    completed_at=None,
    evidence_kwargs: Optional[dict] = None,
) -> ComplianceObligation:
    completed_at = completed_at or timezone.now()
    obligation.last_completed_at = completed_at
    # Recompute next_due_date according to frequency.
    delta = FREQUENCY_TO_DELTA.get(obligation.frequency)
    if delta is not None:
        obligation.next_due_date = completed_at.date() + delta
        obligation.status = 'pendiente'
    else:
        # unica / ad_hoc: queda cumplido sin recurrencia.
        obligation.status = 'cumplido'
    obligation.save(update_fields=[
        'last_completed_at', 'next_due_date', 'status', 'updated_at',
    ])

    if evidence_kwargs:
        attach_evidence(obligation=obligation, **evidence_kwargs)
    return obligation


def recompute_due_dates(tenant=None) -> int:
    """Re-apply frequency delta from last_completed_at. Returns rows touched."""
    qs = ComplianceObligation.objects.filter(last_completed_at__isnull=False)
    if tenant is not None:
        qs = qs.filter(matrix__tenant=tenant)
    touched = 0
    for o in qs:
        delta = FREQUENCY_TO_DELTA.get(o.frequency)
        if delta is None:
            continue
        new_due = o.last_completed_at.date() + delta
        if new_due != o.next_due_date:
            o.next_due_date = new_due
            o.save(update_fields=['next_due_date', 'updated_at'])
            touched += 1
    return touched


def list_alerts(tenant=None, days_ahead: int = 30) -> dict:
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    base = ComplianceObligation.objects.exclude(status='cumplido')
    if tenant is not None:
        base = base.filter(matrix__tenant=tenant)

    overdue = list(base.filter(next_due_date__lt=today).order_by('next_due_date'))
    due_soon = list(
        base.filter(next_due_date__gte=today, next_due_date__lte=cutoff)
        .order_by('next_due_date')
    )
    return {'overdue': overdue, 'due_soon': due_soon, 'cutoff_date': cutoff}


def mark_overdue_obligations(tenant=None) -> int:
    today = date.today()
    qs = ComplianceObligation.objects.filter(
        ~Q(status='cumplido'),
        next_due_date__lt=today,
    ).exclude(status='vencido')
    if tenant is not None:
        qs = qs.filter(matrix__tenant=tenant)
    count = qs.count()
    qs.update(status='vencido', updated_at=timezone.now())
    return count
