"""URLs para las APIs de vacaciones."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ConfiguracionVacacionesViewSet,
    PeriodoVacacionalViewSet,
    SolicitudVacacionesViewSet,
    GoceVacacionesViewSet,
    HistorialSolicitudVacacionesViewSet,
    VacacionesReportesViewSet
)

# Router para ViewSets
router = DefaultRouter()
router.register(
    r'configuraciones',
    ConfiguracionVacacionesViewSet,
    basename='configuracion-vacaciones'
)
router.register(
    r'periodos',
    PeriodoVacacionalViewSet,
    basename='periodo-vacacional'
)
router.register(
    r'solicitudes',
    SolicitudVacacionesViewSet,
    basename='solicitud-vacaciones'
)
router.register(
    r'goces',
    GoceVacacionesViewSet,
    basename='goce-vacaciones'
)
router.register(
    r'historial',
    HistorialSolicitudVacacionesViewSet,
    basename='historial-solicitudes'
)
router.register(
    r'reportes',
    VacacionesReportesViewSet,
    basename='vacaciones-reportes'
)

# URLs del módulo de vacaciones
urlpatterns = [
    # Incluir todas las rutas del router
    path('', include(router.urls)),
]

# Documentación de endpoints disponibles:
# 
# Configuraciones de Vacaciones:
# GET    /api/v1/vacaciones/configuraciones/           - Listar configuraciones
# POST   /api/v1/vacaciones/configuraciones/           - Crear configuración
# GET    /api/v1/vacaciones/configuraciones/{id}/      - Obtener configuración
# PUT    /api/v1/vacaciones/configuraciones/{id}/      - Actualizar configuración
# PATCH  /api/v1/vacaciones/configuraciones/{id}/      - Actualizar parcialmente
# DELETE /api/v1/vacaciones/configuraciones/{id}/      - Desactivar configuración
#
# Períodos Vacacionales:
# GET    /api/v1/vacaciones/periodos/                  - Listar períodos
# GET    /api/v1/vacaciones/periodos/{id}/             - Obtener período
# POST   /api/v1/vacaciones/periodos/generar-masivo/   - Generar períodos masivos
# POST   /api/v1/vacaciones/periodos/{id}/ajustar-dias/ - Ajustar días de período
#
# Solicitudes de Vacaciones:
# GET    /api/v1/vacaciones/solicitudes/               - Listar solicitudes
# POST   /api/v1/vacaciones/solicitudes/               - Crear solicitud
# GET    /api/v1/vacaciones/solicitudes/{id}/          - Obtener solicitud
# PUT    /api/v1/vacaciones/solicitudes/{id}/          - Actualizar solicitud
# PATCH  /api/v1/vacaciones/solicitudes/{id}/          - Actualizar parcialmente
# POST   /api/v1/vacaciones/solicitudes/{id}/aprobar-jefe/  - Aprobar como jefe
# POST   /api/v1/vacaciones/solicitudes/{id}/aprobar-rrhh/  - Aprobar como RRHH
# POST   /api/v1/vacaciones/solicitudes/{id}/cancelar/      - Cancelar solicitud
# GET    /api/v1/vacaciones/solicitudes/pendientes-jefe/    - Solicitudes pendientes jefe
# GET    /api/v1/vacaciones/solicitudes/pendientes-rrhh/    - Solicitudes pendientes RRHH
# GET    /api/v1/vacaciones/solicitudes/mis-solicitudes/    - Mis solicitudes de vacaciones
#
# Goces de Vacaciones:
# GET    /api/v1/vacaciones/goces/                     - Listar goces
# GET    /api/v1/vacaciones/goces/{id}/                - Obtener goce
#
# Historial de Solicitudes:
# GET    /api/v1/vacaciones/historial/                 - Listar historial
# GET    /api/v1/vacaciones/historial/{id}/            - Obtener entrada de historial
#
# Reportes y Estadísticas:
# GET    /api/v1/vacaciones/reportes/estadisticas/     - Estadísticas de vacaciones
# GET    /api/v1/vacaciones/reportes/dias-vencidos/    - Empleados con días vencidos
# GET    /api/v1/vacaciones/reportes/reporte-solicitudes/ - Reporte de solicitudes