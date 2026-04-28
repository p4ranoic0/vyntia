"""URLs for employees bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    CursosCertificacionesViewSet,
    DatosAcademicosViewSet,
    DatosFamiliaresViewSet,
    EmpleadoViewSet,
)

app_name = "employees"

router = DefaultRouter()
router.register(r"employees", EmpleadoViewSet, basename="employee")
router.register(r"family-members", DatosFamiliaresViewSet, basename="family-member")
router.register(r"academic-records", DatosAcademicosViewSet, basename="academic-record")
router.register(r"certifications", CursosCertificacionesViewSet, basename="certification")

urlpatterns = [
    path("", include(router.urls)),
]
