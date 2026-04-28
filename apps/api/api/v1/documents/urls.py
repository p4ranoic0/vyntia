"""URLs for documents bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import DocumentosDigitalesViewSet

app_name = "documents"

router = DefaultRouter()
router.register(r"documents", DocumentosDigitalesViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    # Document generation function-based views (re-mount at /api/v1/documents/)
    path("documents/", include("api.v1.app_rrhh.document_generation_urls")),
]
