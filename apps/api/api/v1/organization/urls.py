"""URLs for organization bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    AreaViewSet,
    ConfiguracionEmpresaViewSet,
)

app_name = "organization"

router = DefaultRouter()
router.register(r"departments", AreaViewSet, basename="department")
router.register(r"companies", ConfiguracionEmpresaViewSet, basename="company")

urlpatterns = [
    path("", include(router.urls)),
]
