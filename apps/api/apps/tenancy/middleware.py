"""Tenancy middleware stack.

Three classes (registered in MIDDLEWARE in this order):

1. TenantMiddleware — resolves subdomain → Tenant, sets request.tenant + ContextVar
2. TenantAuthMiddleware — validates JWT.tenant_id matches request.tenant.id
3. RLSMiddleware — sets app.tenant_id and app.user_id on the DB connection

All three are tolerant: if request.tenant is None (reserved subdomains, dev),
they skip their work and pass through to get_response.
"""

from django.db import connection

from apps.tenancy.constants import RESERVED_SUBDOMAINS
from apps.tenancy.context import (
    set_current_tenant,
    set_current_user_id,
    _current_tenant,
    _current_user_id,
)


class TenantMiddleware:
    """Resolve the tenant from the Host header subdomain.

    Sets:
        request.tenant : Tenant | None
        ContextVar: vyntia_current_tenant

    Reserved subdomains and unknown slugs both yield request.tenant = None
    (silent fallback — downstream views can choose to 404 or behave as
    workspace-less endpoints).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self._resolve_tenant(request)
        request.tenant = tenant

        if tenant is not None:
            token = set_current_tenant(tenant)
            try:
                return self.get_response(request)
            finally:
                _current_tenant.reset(token)
        else:
            return self.get_response(request)

    @staticmethod
    def _resolve_tenant(request):
        host = request.META.get("HTTP_HOST", "")
        if not host:
            return None

        # Strip port (acme.vyntia.pe:8000 → acme.vyntia.pe)
        hostname = host.split(":", 1)[0]

        # Extract subdomain (first label)
        parts = hostname.split(".")
        if not parts:
            return None
        subdomain = parts[0].lower()

        if subdomain in RESERVED_SUBDOMAINS:
            return None

        # Lazy import — avoids circular import at module load time
        from apps.tenancy.models import Tenant

        try:
            return Tenant.objects.get(
                slug=subdomain,
                status__in=["trial", "active"],
            )
        except Tenant.DoesNotExist:
            return None
