"""DocumentAccessLog — audit trail per Ley 29733 + SUNAFIL (B.12, backlog #121).

Every access to a DigitalDocument generates a log entry. Used for compliance
audits (Ley 29733 protección de datos, SUNAFIL inspections) and intrusion-
detection signals.
"""

import uuid

from django.db import models


class DocumentAccessLog(models.Model):
    ACTIONS = [
        ('view', 'View'),
        ('download', 'Download'),
        ('preview', 'Preview'),
        ('print', 'Print'),
        ('share', 'Share'),
        ('denied', 'Denied (insufficient permission)'),
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

    # null=True so dossier-level events (consolidated_pdf aggregate) can be
    # logged without a single DigitalDocument as target. Per-document
    # accesses still set this FK normally.
    document = models.ForeignKey(
        'documents.DigitalDocument',
        on_delete=models.CASCADE,
        related_name='access_logs',
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    action = models.CharField(max_length=20, choices=ACTIONS)

    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=400, blank=True)
    required_permission_level = models.PositiveSmallIntegerField(default=0)
    user_permission_level = models.PositiveSmallIntegerField(default=0)
    notes = models.CharField(max_length=300, blank=True)

    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'document_access_log'
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['document', 'occurred_at']),
            models.Index(fields=['tenant', 'action']),
        ]

    def __str__(self):
        return f'{self.action} doc={self.document_id} by={self.user_id} at {self.occurred_at}'
