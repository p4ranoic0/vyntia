"""URLs for contracts bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.contratos_views import (
    ContractAmendmentViewSet,
    ContratosAdendasViewSet,
)
from api.v1.rrhh.views import DatosLaboralesViewSet

app_name = "contracts"

router = DefaultRouter()
router.register(r"contracts", ContratosAdendasViewSet, basename="contract")
router.register(r"contract-amendments", ContractAmendmentViewSet, basename="contract-amendment-en")
router.register(r"employment-data", DatosLaboralesViewSet, basename="employment-data")

urlpatterns = [
    path("", include(router.urls)),
]
