"""URLs for identity bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.identity.views import (
    ModulosViewSet,
    PermisoViewSet,
    RolPermisosViewSet,
    RolViewSet,
    UsuarioRolesViewSet,
    UsuarioViewSet,
)

app_name = "identity"

router = DefaultRouter()
router.register(r"users", UsuarioViewSet, basename="user")
router.register(r"roles", RolViewSet, basename="role")
router.register(r"permissions", PermisoViewSet, basename="permission")
router.register(r"modules", ModulosViewSet, basename="module")
router.register(r"role-permissions", RolPermisosViewSet, basename="role-permission")
router.register(r"user-roles", UsuarioRolesViewSet, basename="user-role")

urlpatterns = [
    path("", include(router.urls)),
]
