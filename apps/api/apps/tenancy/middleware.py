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


class RLSMiddleware:
    """Set PostgreSQL session variables for RLS enforcement.

    For each request:
    - If request.tenant is set → SET LOCAL app.tenant_id
    - If request.user is authenticated → SET LOCAL app.user_id

    Both are SET LOCAL → reset at end of transaction (request boundary).
    Safe even on SQLite or other backends — silently skipped.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only PostgreSQL supports current_setting() / SET LOCAL.
        # On SQLite (tests), skip this entirely.
        if connection.vendor != "postgresql":
            return self.get_response(request)

        tenant = getattr(request, "tenant", None)
        user = getattr(request, "user", None)
        user_id = user.id if (user is not None and user.is_authenticated) else None

        if tenant is None and user_id is None:
            return self.get_response(request)

        with connection.cursor() as cur:
            if tenant is not None:
                cur.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant.id)])
            if user_id is not None:
                cur.execute("SELECT set_config('app.user_id', %s, true)", [str(user_id)])

        # Also propagate to the user_id ContextVar so managers can read it
        if user_id is not None:
            user_token = set_current_user_id(user_id)
            try:
                return self.get_response(request)
            finally:
                _current_user_id.reset(user_token)
        return self.get_response(request)


class TenantAuthMiddleware:
    """Validate that JWT.tenant_id matches request.tenant.id.

    Prevents replay of a token issued for tenant A against tenant B.

    When the JWT does NOT contain a `tenant_id` claim (e.g., legacy tokens
    issued before C.4 ships), validation is SKIPPED. C.4 will issue tokens
    with the claim, at which point this middleware will start enforcing.

    When request.tenant is None (reserved subdomain) or request.user is
    anonymous, this middleware is a no-op.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, "tenant", None)
        user = getattr(request, "user", None)

        if tenant is None or user is None or not getattr(user, "is_authenticated", False):
            return self.get_response(request)

        token_tenant_id = self._extract_tenant_id_from_jwt(request)
        if token_tenant_id is None:
            # Pre-C.4 token without tenant_id claim — skip validation
            return self.get_response(request)

        if str(token_tenant_id) != str(tenant.id):
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed(
                f"JWT tenant_id mismatch: token issued for {token_tenant_id}, "
                f"request is for {tenant.id}"
            )

        return self.get_response(request)

    @staticmethod
    def _extract_tenant_id_from_jwt(request):
        """Read tenant_id from the JWT, if present.

        Tries the auth attribute that simplejwt sets, then falls back to
        decoding from the Authorization header. Returns None if not present.
        """
        # simplejwt sets request.auth to the validated token (a dict-like)
        auth = getattr(request, "auth", None)
        if auth is not None:
            try:
                return auth.get("tenant_id")
            except (AttributeError, TypeError):
                pass

        # Fallback: try to read from request.user attributes (some custom auth flows)
        user = getattr(request, "user", None)
        if user is not None and hasattr(user, "_jwt_tenant_id"):
            return user._jwt_tenant_id

        return None
