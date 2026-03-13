# -*- coding: utf-8 -*-
"""
URLs principales para la API de Recursos Humanos.

Este módulo define las rutas principales para todos los endpoints
relacionados con la gestión de recursos humanos.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Importar ViewSets existentes (cuando estén disponibles)
# from .views import (
#     EmpleadoViewSet,
#     ContratoAdendaViewSet,
#     DatosLaboralesViewSet,
#     DocumentosDigitalesViewSet
# )

# Router principal para la API de RRHH
router = DefaultRouter()

# Registrar ViewSets cuando estén disponibles
# router.register(r'empleados', EmpleadoViewSet, basename='empleados')
# router.register(r'contratos', ContratoAdendaViewSet, basename='contratos')
# router.register(r'datos-laborales', DatosLaboralesViewSet, basename='datos-laborales')
# router.register(r'documentos-digitales', DocumentosDigitalesViewSet, basename='documentos-digitales')

# URLs de la aplicación
urlpatterns = [
    # Endpoints principales de RRHH
    path('', include(router.urls)),
    
    # Endpoints de generación de documentos
    path('generacion/', include('api.v1.app_rrhh.document_generation_urls')),
    
    # Endpoints adicionales específicos
    # path('reportes/', include('api.v1.app_rrhh.reportes_urls')),
    # path('alertas/', include('api.v1.app_rrhh.alertas_urls')),
]

# Estructura de URLs resultante:
# /api/v1/app_rrhh/ - Endpoints principales de RRHH
# /api/v1/app_rrhh/generacion/ - Endpoints de generación de documentos
# /api/v1/app_rrhh/generacion/documentos/generar-contrato/
# /api/v1/app_rrhh/generacion/documentos/generar-adenda/
# /api/v1/app_rrhh/generacion/documentos/generar-certificado/
# /api/v1/app_rrhh/generacion/documentos/generar-reporte/
# /api/v1/app_rrhh/generacion/documentos/plantillas-disponibles/