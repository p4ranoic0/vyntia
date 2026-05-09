"""TenantManager and UnsafeManager for tenant-scoped models.

TenantManager is the canonical manager for tenant-scoped data. It auto-filters
queries by the currently-active tenant from the ContextVar.

In C.3, the manager is **lenient**: when no tenant context is set, it returns
all rows (no filter applied). This preserves the 185-test baseline since
existing fixtures don't yet use tenant_context. Production safety is provided
by RLS at the DB layer (the `vyntia_app` user enforces filters cryptographically).

A future sub-layer will tighten this to **strict mode** (raises if no context),
once test fixtures are tenant-aware. The `STRICT_TENANT_FILTERING` setting
controls the mode (default False).

UnsafeManager always returns all rows — used for cross-tenant operations
(workspace switcher, admin UI, ETL).
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from apps.tenancy.context import get_current_tenant


class TenantManager(models.Manager):
    """Auto-filters queries by the active tenant (lenient by default).

    - With tenant context: filters `tenant=current_tenant`
    - Without tenant context + STRICT_TENANT_FILTERING=False: returns all
    - Without tenant context + STRICT_TENANT_FILTERING=True: raises ImproperlyConfigured
    """

    def get_queryset(self):
        tenant = get_current_tenant()
        qs = super().get_queryset()
        if tenant is not None:
            return qs.filter(tenant=tenant)
        if getattr(settings, "STRICT_TENANT_FILTERING", False):
            raise ImproperlyConfigured(
                f"{self.model.__name__}.objects requires tenant context. "
                f"Use {self.model.__name__}.unsafe for cross-tenant access."
            )
        return qs

    # Test helper — bypasses the model.objects attachment requirement
    @staticmethod
    def _lenient_queryset_for_test(model):
        """Build a queryset using TenantManager's filtering, for testing without
        attaching the manager to a model class."""
        manager = TenantManager()
        manager.model = model
        return manager.get_queryset()


class UnsafeManager(models.Manager):
    """Cross-tenant access — bypasses tenant filtering.

    Use only when the operation is intrinsically cross-tenant: workspace
    switcher (user lists their memberships across tenants), admin/staff UI,
    ETL pipelines, support impersonation. Code review must justify every use.
    """

    @staticmethod
    def _lenient_queryset_for_test(model):
        manager = UnsafeManager()
        manager.model = model
        return manager.get_queryset()
