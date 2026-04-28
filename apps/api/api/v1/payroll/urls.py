"""URLs for payroll bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.remuneraciones_views import (
    BoletaPagoViewSet,
    CalendarioPagoViewSet,
    ConfiguracionAfpViewSet,
    ConfiguracionRemuneracionViewSet,
    ConfiguracionUitViewSet,
    DescuentoMasivoViewSet,
    DetallePlanillaViewSet,
    PlanillaMensualViewSet,
)

app_name = "payroll"

router = DefaultRouter()
router.register(r"monthly-runs", PlanillaMensualViewSet, basename="monthly-run")
router.register(r"details", DetallePlanillaViewSet, basename="payroll-detail")
router.register(r"mass-deductions", DescuentoMasivoViewSet, basename="mass-deduction")
router.register(r"payslips", BoletaPagoViewSet, basename="payslip")
router.register(r"payment-schedules", CalendarioPagoViewSet, basename="payment-schedule")
router.register(r"afp-configurations", ConfiguracionAfpViewSet, basename="afp-configuration")
router.register(r"tax-parameters", ConfiguracionUitViewSet, basename="tax-parameter")
router.register(r"compensation-configurations", ConfiguracionRemuneracionViewSet, basename="compensation-configuration")

urlpatterns = [
    path("", include(router.urls)),
]
