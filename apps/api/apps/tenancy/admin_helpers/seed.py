"""Tenant seed helper — minimal default state for newly provisioned tenants.

For C.5 MVP, this just creates a CompanyConfig record bound to the tenant.
HR-level Roles / Permissions / Module bindings are NOT seeded — admins can
run the existing identity management commands per-tenant after provisioning,
or seed via the admin UI in a future sub-layer.

Idempotent: safe to call multiple times for the same tenant (uses get_or_create).
"""

from django.db import transaction


@transaction.atomic
def setup_tenant_seed(tenant):
    """Create the minimal records a new tenant needs to function.

    Currently:
    - One CompanyConfig record bound to the tenant (using the tenant's RUC + name).

    Returns a dict describing what was created/updated.
    """
    from apps.organization.models import Company

    company, created = Company.objects.get_or_create(
        tenant=tenant,
        defaults={
            "ruc": tenant.ruc,
            "nombre": tenant.name,
        },
    )
    return {
        "company_created": created,
        "company_id": company.pk,
    }
