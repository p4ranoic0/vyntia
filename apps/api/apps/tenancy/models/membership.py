"""TenantMembership — the M2M between identity.User (global) and Tenant.

A user can be a member of multiple tenants with different roles in each.
The role here is the *SaaS-level* role (owner/admin/member), distinct from
HR-level roles (Empleado, Jefe de Area, etc.) which live in identity.Role.
"""

import uuid

from django.db import models


ROLE_CHOICES = [
    ("owner", "Owner"),
    ("admin", "Admin"),
    ("member", "Member"),
]

STATUS_CHOICES = [
    ("invited", "Invited"),
    ("active", "Active"),
    ("suspended", "Suspended"),
]


class TenantMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        "identity.User",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    invited_at = models.DateTimeField(auto_now_add=True)
    joined_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        "identity.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memberships_invited",
    )

    class Meta:
        db_table = "tenancy_tenantmembership"
        verbose_name = "Tenant Membership"
        verbose_name_plural = "Tenant Memberships"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "user"],
                name="unique_tenant_user_membership",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["tenant", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.tenant.slug} ({self.role})"
