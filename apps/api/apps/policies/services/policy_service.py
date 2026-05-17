"""Policy lifecycle service (B.15a).

Public API:
- create_policy(*, tenant, kind, title, ...) -> Policy
- create_version(*, policy, content_html, ..., user) -> PolicyVersion
- submit_for_review(*, version, approvers, user) -> PolicyApprovalFlow
- register_approval_decision(*, flow, step_order, approver, decision, comment) -> PolicyApprovalStep
- publish(*, version, target_audience, ..., user) -> PolicyPublication
- retire(policy, user) -> Policy

Transitions are atomic at the service boundary; callers should not toggle
status fields directly on the models.
"""

from __future__ import annotations

from typing import Iterable, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.policies.models import (
    Policy,
    PolicyApprovalFlow,
    PolicyApprovalStep,
    PolicyPublication,
    PolicyVersion,
)


def create_policy(
    *,
    tenant,
    kind: str,
    title: str,
    owner_user,
    description: str = '',
    owner_area=None,
    user=None,
) -> Policy:
    if kind not in dict(Policy.KINDS):
        raise ValidationError('kind inválido.')
    policy = Policy.objects.create(
        tenant=tenant,
        kind=kind,
        title=title.strip(),
        description=description,
        owner_user=owner_user,
        owner_area=owner_area,
        status='draft',
        created_by=user,
        updated_by=user,
    )
    return policy


def create_version(
    *,
    policy: Policy,
    content_html: str = '',
    pdf_file=None,
    change_summary: str = '',
    effective_date=None,
    user=None,
) -> PolicyVersion:
    if policy.status == 'retired':
        raise ValidationError('No se pueden crear versiones en políticas retiradas.')
    last = policy.latest_version()
    next_number = (last.version_number + 1) if last else 1
    version = PolicyVersion.objects.create(
        tenant=policy.tenant,
        policy=policy,
        version_number=next_number,
        content_html=content_html or '',
        pdf_file=pdf_file,
        change_summary=change_summary or '',
        effective_date=effective_date,
        status='draft',
        created_by=user,
    )
    return version


@transaction.atomic
def submit_for_review(
    *,
    version: PolicyVersion,
    approvers: Iterable,
    user=None,
) -> PolicyApprovalFlow:
    approver_list = list(approvers)
    if not approver_list:
        raise ValidationError('Se requiere al menos un aprobador.')

    # If a prior flow exists (e.g., resubmit after rejection), wipe it.
    PolicyApprovalFlow.objects.filter(policy_version=version).delete()

    version.mark_under_review(user=user)

    flow = PolicyApprovalFlow.objects.create(
        tenant=version.tenant,
        policy_version=version,
        status='pending',
    )
    for index, approver_user in enumerate(approver_list, start=1):
        PolicyApprovalStep.objects.create(
            flow=flow,
            order=index,
            approver_user=approver_user,
        )

    # Reflect on policy header.
    if version.policy.status == 'draft':
        version.policy.status = 'in_review'
        version.policy.updated_by = user
        version.policy.save(update_fields=['status', 'updated_by', 'updated_at'])

    return flow


@transaction.atomic
def register_approval_decision(
    *,
    flow: PolicyApprovalFlow,
    step_order: int,
    approver,
    decision: str,
    comment: str = '',
) -> PolicyApprovalStep:
    try:
        step = flow.steps.get(order=step_order)
    except PolicyApprovalStep.DoesNotExist:
        raise ValidationError('Paso de aprobación inexistente.')
    if step.approver_user_id != getattr(approver, 'pk', None):
        raise ValidationError('Solo el aprobador asignado puede decidir este paso.')
    step.record_decision(decision=decision, user=approver, comment=comment)
    flow.recompute_status()

    version = flow.policy_version
    if flow.status == 'approved':
        # All steps approved → mark version approved + bubble header.
        version.mark_approved()
        version.policy.status = 'approved'
        version.policy.save(update_fields=['status', 'updated_at'])
    elif flow.status == 'rejected':
        # Any rejection → revert version + header to draft.
        version.revert_to_draft()
        version.policy.status = 'draft'
        version.policy.save(update_fields=['status', 'updated_at'])

    return step


@transaction.atomic
def publish(
    *,
    version: PolicyVersion,
    target_audience: str = 'all',
    target_role=None,
    target_area=None,
    target_employees=None,
    requires_acknowledgment: bool = True,
    deadline=None,
    user=None,
) -> PolicyPublication:
    if version.status != 'approved':
        raise ValidationError('Solo versiones aprobadas pueden publicarse.')
    if target_audience not in dict(PolicyPublication.TARGET_AUDIENCES):
        raise ValidationError('target_audience inválido.')
    if target_audience == 'role' and target_role is None:
        raise ValidationError('target_role requerido cuando target_audience=role.')
    if target_audience == 'area' and target_area is None:
        raise ValidationError('target_area requerido cuando target_audience=area.')

    publication = PolicyPublication.objects.create(
        tenant=version.tenant,
        policy_version=version,
        published_at=timezone.now(),
        published_by=user,
        target_audience=target_audience,
        target_role=target_role,
        target_area=target_area,
        requires_acknowledgment=requires_acknowledgment,
        acknowledgment_deadline=deadline,
    )
    if target_audience == 'employee' and target_employees:
        publication.target_employees.set(target_employees)

    version.mark_published()

    policy = version.policy
    policy.status = 'published'
    policy.current_version = version
    policy.updated_by = user
    policy.save(update_fields=['status', 'current_version', 'updated_by', 'updated_at'])

    return publication


@transaction.atomic
def retire(policy: Policy, user=None) -> Policy:
    if policy.status == 'retired':
        return policy
    current = policy.current_version
    if current is not None and current.status == 'published':
        current.mark_retired()
    policy.status = 'retired'
    policy.updated_by = user
    policy.save(update_fields=['status', 'updated_by', 'updated_at'])
    return policy


def list_pending_approvals_for_user(user):
    """Steps awaiting `user`'s decision."""
    return (
        PolicyApprovalStep.objects.select_related('flow', 'flow__policy_version', 'flow__policy_version__policy')
        .filter(approver_user=user, decision='pending', flow__status='pending')
        .order_by('flow__created_at', 'order')
    )
