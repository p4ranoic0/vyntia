"""URLs for documents bounded context — English paths per spec § 3.4 (flat).

B.5b #76: DocumentGenerationViewSet migrated from api/v1/app_rrhh/ to local
api/v1/documents/views.py. The legacy `documents/` re-mount of an external
URL include was replaced by a direct router register here.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.documents.views import DocumentGenerationViewSet
from api.v1.rrhh.views import DocumentosDigitalesViewSet

app_name = "documents"

# Main CRUD router for DigitalDocument
router = DefaultRouter()
router.register(r"documents", DocumentosDigitalesViewSet, basename="document")

# Sub-router for the function-style ViewSet that exposes generar-contrato/
# generar-adenda/generar-certificado/etc. URL prefix kept as `documents/` so
# generated routes stay on `/api/v1/documents/documents/generar-X/` (back-compat
# with frontend service paths).
generation_router = DefaultRouter()
generation_router.register(r"", DocumentGenerationViewSet, basename="document-generation")

urlpatterns = [
    path("", include(router.urls)),
    path("documents/", include(generation_router.urls)),
]
