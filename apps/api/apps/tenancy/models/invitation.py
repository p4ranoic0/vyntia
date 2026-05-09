"""TenantInvitation — pending invitation to join a tenant.

When Vyntia staff provisions a tenant, a TenantInvitation is created with a
signed token. The invited admin clicks the activation link, which creates
their User (or links existing) and the corresponding TenantMembership, then
sets `accepted_at` on the invitation.
"""

import uuid

from django.db import models

from apps.tenancy.models.membership import ROLE_CHOICES


class TenantInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField()
    token = models.CharField(max_length=512, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="invitations_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenancy_tenantinvitation"
        verbose_name = "Tenant Invitation"
        verbose_name_plural = "Tenant Invitations"
        indexes = [
            models.Index(fields=["email", "tenant"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"{self.email} → {self.tenant.slug} ({self.role})"
