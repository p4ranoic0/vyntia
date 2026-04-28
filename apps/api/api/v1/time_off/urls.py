"""URLs for time-off bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Import viewsets from existing vacaciones module (preserve original location)
from api.v1.vacaciones.views import (
    ConfiguracionVacacionesViewSet,
    GoceVacacionesViewSet,
    HistorialSolicitudVacacionesViewSet,
    PeriodoVacacionalViewSet,
    SolicitudVacacionesViewSet,
    VacacionesReportesViewSet,
)

app_name = "time_off"

router = DefaultRouter()
router.register(r"configurations", ConfiguracionVacacionesViewSet, basename="vacation-configuration")
router.register(r"periods", PeriodoVacacionalViewSet, basename="vacation-period")
router.register(r"requests", SolicitudVacacionesViewSet, basename="vacation-request-en")
router.register(r"grants", GoceVacacionesViewSet, basename="vacation-grant")
router.register(r"history", HistorialSolicitudVacacionesViewSet, basename="vacation-history")
router.register(r"reports", VacacionesReportesViewSet, basename="vacation-report")

urlpatterns = [
    path("", include(router.urls)),
]
