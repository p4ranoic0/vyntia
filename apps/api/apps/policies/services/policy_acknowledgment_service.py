"""Policy acknowledgment service (B.15a).

Public API:
- seed_acknowledgments_for_publication(publication) -> int (count created)
- capture(*, acknowledgment, signature_kind, signature_payload, ip, user_agent)
- decline(*, acknowledgment, reason, ip, user_agent)
- expire_overdue(tenant=None) -> int (count expired)
- list_pending_for_employee(employee) -> QuerySet

Idempotent at seed boundary — re-running seed only adds missing rows for
employees not yet seeded.
"""

from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.policies.models import PolicyAcknowledgment, PolicyPublication


def seed_acknowledgments_for_publication(publication: PolicyPublication) -> int:
    if not publication.requires_acknowledgment:
        return 0
    employees = publication.expand_target_employees()
    existing = set(
        PolicyAcknowledgment.objects.filter(publication=publication)
        .values_list('employee_id', flat=True)
    )
    created = 0
    for emp in employees:
        if emp.pk in existing:
            continue
        PolicyAcknowledgment.objects.create(
            tenant=publication.tenant,
            publication=publication,
            employee=emp,
            status='pending',
        )
        created += 1
    return created


def capture(
    *,
    acknowledgment: PolicyAcknowledgment,
    signature_kind: str,
    signature_payload: str,
    ip=None,
    user_agent: str = '',
) -> PolicyAcknowledgment:
    acknowledgment.mark_acknowledged(
        signature_kind=signature_kind,
        signature_payload=signature_payload,
        ip=ip,
        user_agent=user_agent,
    )
    return acknowledgment


def decline(
    *,
    acknowledgment: PolicyAcknowledgment,
    reason: str,
    ip=None,
    user_agent: str = '',
) -> PolicyAcknowledgment:
    acknowledgment.mark_declined(
        reason=reason,
        ip=ip,
        user_agent=user_agent,
    )
    return acknowledgment


def expire_overdue(tenant=None) -> int:
    today = timezone.now().date()
    qs = PolicyAcknowledgment.objects.filter(
        status='pending',
        publication__acknowledgment_deadline__isnull=False,
        publication__acknowledgment_deadline__lt=today,
    )
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    count = qs.count()
    qs.update(status='expired', updated_at=timezone.now())
    return count


def list_pending_for_employee(employee):
    return (
        PolicyAcknowledgment.objects.select_related(
            'publication', 'publication__policy_version', 'publication__policy_version__policy',
        )
        .filter(employee=employee, status='pending')
        .order_by('publication__acknowledgment_deadline', 'publication__published_at')
    )
