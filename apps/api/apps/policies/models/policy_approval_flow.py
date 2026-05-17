"""PolicyApprovalFlow + PolicyApprovalStep — multi-step approval (B.15a).

Each PolicyVersion submitted for review gets a PolicyApprovalFlow with one or
more ordered PolicyApprovalStep rows (one per required approver). The flow
completes when all steps approve (→ PolicyVersion goes 'approved') or when
any step rejects (→ PolicyVersion reverts to 'draft').

Re-submitting a PolicyVersion replaces the previous flow (OneToOne semantics
preserved via cascade).

See BACKLOG #128.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class PolicyApprovalFlow(models.Model):
    STATUSES = [
        ('pending', 'En curso'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    policy_version = models.OneToOneField(
        'policies.PolicyVersion',
        on_delete=models.CASCADE,
        related_name='approval_flow',
    )
    status = models.CharField(
        max_length=15, choices=STATUSES, default='pending', db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'policy_approval_flow'
        ordering = ['-created_at']

    def __str__(self):
        return f'Approval flow for version {self.policy_version_id} ({self.status})'

    def next_pending_step(self):
        return self.steps.filter(decision='pending').order_by('order').first()

    def recompute_status(self):
        """Aggregate step decisions into flow status.

        Called by service after each step decision lands.
        """
        decisions = list(self.steps.values_list('decision', flat=True))
        if 'rejected' in decisions:
            self.status = 'rejected'
            self.completed_at = timezone.now()
        elif decisions and all(d == 'approved' for d in decisions):
            self.status = 'approved'
            self.completed_at = timezone.now()
        else:
            self.status = 'pending'
            self.completed_at = None
        self.save(update_fields=['status', 'completed_at'])


class PolicyApprovalStep(models.Model):
    DECISIONS = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow = models.ForeignKey(
        'policies.PolicyApprovalFlow',
        on_delete=models.CASCADE,
        related_name='steps',
    )
    order = models.PositiveIntegerField()
    approver_user = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='policy_approval_steps',
    )
    role_hint = models.CharField(
        max_length=64, blank=True,
        help_text='Etiqueta opcional del rol esperado (RRHH, Legal, Gerencia, etc.)',
    )

    decision = models.CharField(
        max_length=15, choices=DECISIONS, default='pending', db_index=True,
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'policy_approval_step'
        ordering = ['flow', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['flow', 'order'],
                name='unique_step_order_per_flow',
            ),
        ]

    def __str__(self):
        return f'Step {self.order} ({self.decision}) by {self.approver_user_id}'

    def record_decision(self, *, decision, user, comment=''):
        if self.decision != 'pending':
            raise ValidationError('Este paso ya fue decidido.')
        if decision not in {'approved', 'rejected'}:
            raise ValidationError('decision debe ser approved o rejected.')
        self.decision = decision
        self.decided_at = timezone.now()
        self.decided_by = user
        self.comment = comment or ''
        self.save(update_fields=['decision', 'decided_at', 'decided_by', 'comment'])
