"""SupportSession — audit trail of Vyntia staff impersonating tenant users.

Created when Vyntia staff opens a support session for a tenant user (typically
in response to a ticket). The session token grants temporary access (default
2h) with elevated audit trail. Every mutation in this session increments
actions_count. The customer can review all support sessions touching their
tenant — required for SERVIR / public-sector compliance.
"""

import uuid

from django.db import models


class SupportSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="support_sessions_initiated",
    )
    target_user = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="support_sessions_received",
    )
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="support_sessions",
    )
    reason = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    actions_count = models.IntegerField(default=0)

    class Meta:
        db_table = "tenancy_supportsession"
        verbose_name = "Support Session"
        verbose_name_plural = "Support Sessions"
        indexes = [
            models.Index(fields=["tenant", "started_at"]),
            models.Index(fields=["staff_user", "started_at"]),
        ]

    def __str__(self):
        return (
            f"{self.staff_user.username} impersonating "
            f"{self.target_user.username} @ {self.tenant.slug}"
        )
