"""Cross-cutting abstract models for tenant-scoped data.

`TenantScopedModel` is the canonical base for NEW models created after C.1.
Existing models are retrofitted with `tenant = FK(...)` directly via migration
(rather than refactoring class hierarchies) — see C.1 plan § "Architecture".

The retrofit uses `null=True, blank=True` transitionally; this base class uses
NOT NULL semantics. After C.3 introduces tenant context middleware and the
backfill migration completes, both will converge on NOT NULL.
"""

from django.db import models


class TenantScopedModel(models.Model):
    """Abstract base for models scoped to a single tenant.

    Use for any new model where every row belongs to exactly one tenant.
    The `tenant` FK uses `on_delete=PROTECT` to prevent cascade deletes
    when a tenant is removed (use the soft-delete admin flow instead).

    Example:
        class Project(TenantScopedModel):
            name = models.CharField(max_length=200)
            class Meta(TenantScopedModel.Meta):
                db_table = "myapp_project"
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )

    class Meta:
        abstract = True
