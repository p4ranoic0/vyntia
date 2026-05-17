"""PolicyAcknowledgment — per-employee acuse de recibido (B.15a).

When a PolicyPublication is created with requires_acknowledgment=True, the
service seeds one PolicyAcknowledgment row per affected employee (status
pending). Employees see them in their inbox and capture a digital signature
(canvas / typed / checkbox). The IP, UA and timestamp are persisted as audit
trail per Ley 29733 + Art. 27 LPCL.

See BACKLOG #128.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class PolicyAcknowledgment(models.Model):
    SIGNATURE_KINDS = [
        ('canvas', 'Firma manuscrita digital'),
        ('typed', 'Firma escrita'),
        ('checkbox', 'Aceptación con checkbox'),
        ('none', 'Sin firma'),
    ]
    STATUSES = [
        ('pending', 'Pendiente'),
        ('acknowledged', 'Acusada'),
        ('expired', 'Vencida'),
        ('declined', 'Rechazada por empleado'),
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

    publication = models.ForeignKey(
        'policies.PolicyPublication',
        on_delete=models.CASCADE,
        related_name='acknowledgments',
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='policy_acknowledgments',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='pending', db_index=True,
    )

    acknowledged_at = models.DateTimeField(null=True, blank=True)
    signature_kind = models.CharField(
        max_length=15, choices=SIGNATURE_KINDS, blank=True,
    )
    signature_payload = models.TextField(
        blank=True,
        help_text='Canvas base64 / texto firma / "true" para checkbox. Max ~200KB.',
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    declined_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_acknowledgment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'employee', 'status']),
            models.Index(fields=['publication', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['publication', 'employee'],
                name='unique_acknowledgment_per_publication_employee',
            ),
        ]

    def __str__(self):
        return f'Ack {self.publication_id} ← emp {self.employee_id} ({self.status})'

    def is_overdue(self):
        deadline = self.publication.acknowledgment_deadline
        if deadline is None:
            return False
        return self.status == 'pending' and timezone.now().date() > deadline

    def mark_acknowledged(self, *, signature_kind, signature_payload, ip=None, user_agent=''):
        if self.status not in {'pending'}:
            raise ValidationError('Solo acuses pendientes pueden marcarse como acusados.')
        if signature_kind not in dict(self.SIGNATURE_KINDS):
            raise ValidationError('signature_kind inválido.')
        if signature_kind != 'none' and not signature_payload:
            raise ValidationError('signature_payload requerido salvo signature_kind=none.')
        self.status = 'acknowledged'
        self.acknowledged_at = timezone.now()
        self.signature_kind = signature_kind
        self.signature_payload = signature_payload or ''
        self.ip = ip
        self.user_agent = user_agent or ''
        self.save(update_fields=[
            'status', 'acknowledged_at', 'signature_kind', 'signature_payload',
            'ip', 'user_agent', 'updated_at',
        ])

    def mark_declined(self, *, reason, ip=None, user_agent=''):
        if self.status not in {'pending'}:
            raise ValidationError('Solo acuses pendientes pueden rechazarse.')
        if not reason:
            raise ValidationError('reason requerido para rechazar.')
        self.status = 'declined'
        self.declined_reason = reason
        self.ip = ip
        self.user_agent = user_agent or ''
        self.save(update_fields=[
            'status', 'declined_reason', 'ip', 'user_agent', 'updated_at',
        ])

    def mark_expired(self):
        if self.status != 'pending':
            return
        self.status = 'expired'
        self.save(update_fields=['status', 'updated_at'])
