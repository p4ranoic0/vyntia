"""URLs for payroll bounded context.

D.2 registers read-only catalog endpoints under /catalog/. Every OTHER legacy
/api/v1/payroll/* path still returns the D.1a 501 stub (catch-all is LAST).
"""

from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.v1.payroll.catalog_views import (
    PayrollConceptViewSet,
    RegimenConfigViewSet,
    TaxParameterViewSet,
)
from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

catalog_router = DefaultRouter()
catalog_router.register(r"tax-parameters", TaxParameterViewSet, basename="tax-parameter")
catalog_router.register(r"payroll-concepts", PayrollConceptViewSet, basename="payroll-concept")
catalog_router.register(r"regimen-configs", RegimenConfigViewSet, basename="regimen-config")

urlpatterns = [
    path("catalog/", include(catalog_router.urls)),
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]
