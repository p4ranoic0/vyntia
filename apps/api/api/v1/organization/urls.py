"""URLs for organization bounded context — English paths per spec § 3.4.

B.6: Position / Plaza / reference-data ViewSets per Module 02.
B.8: PositionRegister (CPE / CAP) + entries + MPP rendering endpoints.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    AreaViewSet,
    ConfiguracionEmpresaViewSet,
)

from .views import (
    CIUOCodeViewSet,
    OccupationalCategoryViewSet,
    PlazaViewSet,
    PositionFunctionViewSet,
    PositionProfileViewSet,
    PositionRegisterEntryViewSet,
    PositionRegisterViewSet,
    PositionRequirementViewSet,
    PositionRiskProfileViewSet,
    PositionViewSet,
)

app_name = "organization"

router = DefaultRouter()
router.register(r"departments", AreaViewSet, basename="department")
router.register(r"companies", ConfiguracionEmpresaViewSet, basename="company")

# B.6 Module 02
router.register(r"positions", PositionViewSet, basename="position")
router.register(r"position-profiles", PositionProfileViewSet, basename="position-profile")
router.register(r"position-functions", PositionFunctionViewSet, basename="position-function")
router.register(r"position-requirements", PositionRequirementViewSet, basename="position-requirement")
router.register(r"position-risk-profiles", PositionRiskProfileViewSet, basename="position-risk-profile")
router.register(r"plazas", PlazaViewSet, basename="plaza")
router.register(r"occupational-categories", OccupationalCategoryViewSet, basename="occupational-category")
router.register(r"ciuo-codes", CIUOCodeViewSet, basename="ciuo-code")

# B.8 — CPE / CAP + MPP
router.register(r"position-registers", PositionRegisterViewSet, basename="position-register")
router.register(r"position-register-entries", PositionRegisterEntryViewSet, basename="position-register-entry")

urlpatterns = [
    path("", include(router.urls)),
]
