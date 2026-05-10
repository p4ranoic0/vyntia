"""URLs for compensation bounded context (B.7)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryFactorScoreViewSet,
    CategoryFunctionTableViewSet,
    CategoryViewSet,
    CCFExcelImportView,
    CCFExcelTemplateView,
    JobFactorViewSet,
    JobSubfactorViewSet,
    SalaryBandViewSet,
    SalaryGapAuditView,
)

app_name = "compensation"

router = DefaultRouter()
router.register(r"job-factors", JobFactorViewSet, basename="job-factor")
router.register(r"job-subfactors", JobSubfactorViewSet, basename="job-subfactor")
router.register(r"ccfs", CategoryFunctionTableViewSet, basename="ccf")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"factor-scores", CategoryFactorScoreViewSet, basename="factor-score")
router.register(r"salary-bands", SalaryBandViewSet, basename="salary-band")

urlpatterns = [
    path("", include(router.urls)),
    path("audit/salary-gap/", SalaryGapAuditView.as_view(), name="audit-salary-gap"),
    path("ccf/template-excel/", CCFExcelTemplateView.as_view(), name="ccf-template-excel"),
    path("ccf/import-excel/", CCFExcelImportView.as_view(), name="ccf-import-excel"),
]
