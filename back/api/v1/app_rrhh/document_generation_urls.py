# -*- coding: utf-8 -*-
"""
URLs para la generación de documentos desde plantillas.

Este módulo define las rutas para los endpoints de generación
de contratos, adendas, certificados y reportes.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .document_generation_views import DocumentGenerationViewSet

# Router para las vistas de generación de documentos
router = DefaultRouter()
router.register(r"", DocumentGenerationViewSet, basename="document-generation")

# URLs de la aplicación
urlpatterns = [
    # Endpoints de generación de documentos
    path("", include(router.urls)),
]

# Nombres de las URLs para referencia
# Ejemplos de URLs generadas:
# /api/v1/rrhh/documentos/generar-contrato/
# /api/v1/rrhh/documentos/generar-adenda/
# /api/v1/rrhh/documentos/generar-certificado/
# /api/v1/rrhh/documentos/generar-reporte/
# /api/v1/rrhh/documentos/plantillas-disponibles/
