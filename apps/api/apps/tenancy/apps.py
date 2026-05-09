from django.apps import AppConfig


class TenancyConfig(AppConfig):
    """Tenancy app — owns Tenant, TenantMembership, TenantInvitation, SupportSession.

    Boundary:
    - Tenant entity is the SaaS-level subscriber (slug, plan, status).
    - TenantMembership is the M2M between global identity.User and Tenant.
    - SupportSession audits Vyntia staff impersonating tenant users.

    No cross-app FKs except to `identity.User`. Other apps will reference
    Tenant via `'tenancy.Tenant'` string lazy in C.1.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tenancy"
    label = "tenancy"
    verbose_name = "Tenancy"
