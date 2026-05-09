"""Workspaces endpoints — used by app.vyntia.pe.

GET /api/v1/workspaces/                       — list user's tenants
POST /api/v1/workspaces/<slug>/exchange/      — issue cross-subdomain token (Task 5)
"""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.responses import APIResponse


class WorkspacesListView(APIView):
    """List the active tenants the authenticated user is a member of.

    Cross-tenant by design — uses UnsafeManager since the request has no
    tenant context (typically hit on app.vyntia.pe).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.tenancy.models import TenantMembership

        memberships = (
            TenantMembership.objects.filter(user=request.user, status="active")
            .select_related("tenant")
            .order_by("tenant__name")
        )
        data = [
            {
                "tenant_id": str(m.tenant_id),
                "slug": m.tenant.slug,
                "name": m.tenant.name,
                "plan": m.tenant.plan,
                "role": m.role,
            }
            for m in memberships
        ]
        return APIResponse.success(data=data, message="Workspaces obtenidos.")


class WorkspaceExchangeView(APIView):
    """Issue a short-lived exchange token for a cross-subdomain redirect.

    POST /api/v1/workspaces/<slug>/exchange/

    The user must have an active membership in <slug>. Returns a token to be
    forwarded to <slug>.vyntia.pe/auth/exchange?token=<token>.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, slug):
        from apps.tenancy.auth.exchange_token import issue_exchange_token
        from apps.tenancy.models import Tenant, TenantMembership

        try:
            tenant = Tenant.objects.get(slug=slug, status__in=["trial", "active"])
        except Tenant.DoesNotExist:
            return APIResponse.error(message="Workspace no encontrado.", status_code=404)

        has_membership = TenantMembership.objects.filter(
            tenant=tenant, user=request.user, status="active"
        ).exists()
        if not has_membership:
            return APIResponse.error(
                message="No tienes membresía activa en este workspace.",
                status_code=403,
            )

        token = issue_exchange_token(user_id=request.user.id, tenant_id=tenant.id)
        return APIResponse.success(
            data={
                "exchange_token": token,
                "redirect_url": f"https://{slug}.vyntia.pe/auth/exchange?token={token}",
            },
            message="Token de intercambio emitido.",
        )
