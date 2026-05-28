"""URLs for payroll bounded context.

Order matters: specific routes (catalog, compensations) FIRST, then the D.1a
501 catch-all for any remaining legacy paths.
"""

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.v1.payroll.catalog_views import (
    PayrollConceptViewSet,
    RegimenConfigViewSet,
    TaxParameterViewSet,
)
from api.v1.payroll.compensation_views import CompensationViewSet
from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

catalog_router = DefaultRouter()
catalog_router.register(r"tax-parameters", TaxParameterViewSet, basename="tax-parameter")
catalog_router.register(r"payroll-concepts", PayrollConceptViewSet, basename="payroll-concept")
catalog_router.register(r"regimen-configs", RegimenConfigViewSet, basename="regimen-config")

domain_router = DefaultRouter()
domain_router.register(r"compensations", CompensationViewSet, basename="compensation")

urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    path("", include(domain_router.urls)),
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]
