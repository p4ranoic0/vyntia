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
