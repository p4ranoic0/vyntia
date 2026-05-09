"""Admin user search endpoint."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from apps.core.responses import APIResponse


class UsersSearchView(APIView):
    """GET /api/admin/users/?q=<term>&page=N&page_size=N

    Searches by username, email, or full name (icontains).
    """

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        User = get_user_model()
        q = request.query_params.get("q", "").strip()
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = User.objects.all()
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(email__icontains=q)
                | Q(nombres_usuario__icontains=q)
                | Q(apellidos_usuario__icontains=q)
            )

        qs = qs.order_by("username")
        total = qs.count()
        items = qs[offset : offset + page_size]

        return APIResponse.success(
            data={
                "results": [
                    {
                        "id": str(u.id),
                        "username": u.username,
                        "email": u.email,
                        "is_active": u.is_active,
                        "is_vyntia_staff": u.is_vyntia_staff,
                    }
                    for u in items
                ],
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )


class ImpersonateView(APIView):
    """POST /api/admin/users/<user_id>/impersonate/

    Body: { reason: str, tenant_id: UUID }
    Returns: { access, refresh, support_session_id, expires_at }
    """

    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def post(self, request, user_id):
        from django.contrib.auth import get_user_model
        from apps.tenancy.admin_helpers.impersonation import issue_impersonation_session
        from apps.tenancy.models import Tenant, TenantMembership

        User = get_user_model()
        target = User.objects.filter(pk=user_id, is_active=True).first()
        if target is None:
            return APIResponse.error(message="Usuario no encontrado.", status_code=404)

        reason = (request.data.get("reason") or "").strip()
        if len(reason) < 5:
            return APIResponse.error(
                message="reason es obligatorio (mínimo 5 caracteres).",
                status_code=400,
            )

        tenant_id = request.data.get("tenant_id")
        if not tenant_id:
            return APIResponse.error(message="tenant_id es obligatorio.", status_code=400)

        tenant = Tenant.objects.filter(pk=tenant_id).first()
        if tenant is None:
            return APIResponse.error(message="Tenant no encontrado.", status_code=404)

        # Target must be a member of the tenant (don't impersonate ghosts)
        has_membership = TenantMembership.objects.filter(
            tenant=tenant, user=target
        ).exists()
        if not has_membership:
            return APIResponse.error(
                message=f"El usuario no es miembro del tenant '{tenant.slug}'.",
                status_code=400,
            )

        session, access, refresh = issue_impersonation_session(
            staff_user=request.user,
            target_user=target,
            tenant=tenant,
            reason=reason,
        )

        return APIResponse.success(
            data={
                "access": access,
                "refresh": refresh,
                "support_session_id": str(session.id),
                "tenant_slug": tenant.slug,
                "expires_at": session.expires_at.isoformat(),
            },
            message="Sesión de soporte iniciada.",
        )
