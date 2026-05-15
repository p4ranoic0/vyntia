"""URLs for documents bounded context — English paths per spec § 3.4 (flat).

B.5b #76: DocumentGenerationViewSet migrated from api/v1/app_rrhh/ to local
api/v1/documents/views.py. The legacy `documents/` re-mount of an external
URL include was replaced by a direct router register here.

B.10: signatures + hiring-bundles + hiring-bundle-items routers added (Module
03.2 backlog #112, #113).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.documents.bundle_views import (
    HiringBundleItemViewSet,
    HiringDocumentBundleViewSet,
)
from api.v1.documents.signature_views import DocumentSignatureViewSet
from api.v1.documents.views import DocumentGenerationViewSet
from api.v1.rrhh.views import DocumentosDigitalesViewSet

app_name = "documents"

# Main CRUD router for DigitalDocument + B.10 additions
router = DefaultRouter()
router.register(r"documents", DocumentosDigitalesViewSet, basename="document")
router.register(r"signatures", DocumentSignatureViewSet, basename="document-signature")
router.register(r"hiring-bundles", HiringDocumentBundleViewSet, basename="hiring-bundle")
router.register(r"hiring-bundle-items", HiringBundleItemViewSet, basename="hiring-bundle-item")

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
