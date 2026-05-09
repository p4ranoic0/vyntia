"""Tenancy models — re-exported for clean imports.

Usage: `from apps.tenancy.models import Tenant, TenantMembership`
"""

from apps.tenancy.models.tenant import Tenant
from apps.tenancy.models.membership import TenantMembership

__all__ = ["Tenant", "TenantMembership"]
