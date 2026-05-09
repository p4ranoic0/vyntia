"""GET /api/admin/support-sessions/ — list SupportSession audit log."""

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.admin.permissions import IsVyntiaStaff
from apps.core.responses import APIResponse
from apps.tenancy.models import SupportSession


class SupportSessionsListView(APIView):
    permission_classes = [IsAuthenticated, IsVyntiaStaff]

    def get(self, request):
        page = max(int(request.query_params.get("page", 1)), 1)
        page_size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        offset = (page - 1) * page_size

        qs = SupportSession.objects.select_related(
            "staff_user", "target_user", "tenant"
        ).order_by("-started_at")
        total = qs.count()
        items = qs[offset : offset + page_size]

        return APIResponse.success(
            data={
                "results": [
                    {
                        "id": str(s.id),
                        "staff_user": s.staff_user.username,
                        "target_user": s.target_user.username,
                        "tenant_slug": s.tenant.slug,
                        "reason": s.reason,
                        "started_at": s.started_at.isoformat(),
                        "expires_at": s.expires_at.isoformat(),
                        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                        "actions_count": s.actions_count,
                    }
                    for s in items
                ],
                "pagination": {
                    "total_items": total,
                    "current_page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                },
            },
        )
