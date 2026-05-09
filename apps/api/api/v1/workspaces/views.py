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
