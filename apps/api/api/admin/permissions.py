"""DRF permissions for the /api/admin/* namespace."""

from rest_framework.permissions import BasePermission


class IsVyntiaStaff(BasePermission):
    """Allow only authenticated users with `is_vyntia_staff=True`.

    Used by every endpoint under /api/admin/. Combine with IsAuthenticated
    (or rely on this class doing both checks: anonymous users never have
    is_vyntia_staff=True, so unauthenticated requests are rejected).
    """

    message = "Only Vyntia staff can access this endpoint."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        return bool(getattr(user, "is_vyntia_staff", False))
