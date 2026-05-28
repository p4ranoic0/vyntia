"""AuditEvent — single-table domain audit log (ADR-B.2).

Sub-proyecto X will replace this with a full event store. For B, this captures
high-stakes mutations (cese, desvinculación, contract amendments, position
changes) with enough payload to reconstruct what happened.

Each AuditEvent is tenant-scoped. When sub-proyecto X arrives, these rows
migrate to the new event store; the `record_event()` helper call sites are
the only refactor surface.
"""

import uuid

from django.conf import settings
from django.db import models


class AuditEvent(models.Model):
    """A single high-stakes domain event recorded inline with the mutation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="+",
        db_index=True,
    )

    actor_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
        help_text="User who performed the action. Null for system-initiated events.",
    )

    action = models.CharField(
        max_length=128,
        db_index=True,
        help_text='Dotted action name, e.g. "employee.terminated".',
    )

    target_model = models.CharField(
        max_length=128,
        help_text='Dotted model label, e.g. "employees.Employee".',
    )

    target_id = models.CharField(
        max_length=64,
        db_index=True,
        help_text="String form of target's primary key (UUID or int as str).",
    )

    payload_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of the mutation: before/after, reason, etc.",
    )

    schema_version = models.IntegerField(
        default=1,
        help_text="Payload schema version for forward-compat (ADR-D.3).",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_lite_event"
        verbose_name = "Audit event"
        verbose_name_plural = "Audit events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "action", "-created_at"]),
            models.Index(fields=["target_model", "target_id"]),
        ]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action} → {self.target_model}:{self.target_id}"
