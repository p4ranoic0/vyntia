"""URLs para módulo RRHH API v1."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .contratos_views import ContratosAdendasViewSet
from .remuneraciones_views import (
    BoletaPagoViewSet,
    CalendarioPagoViewSet,
    ConfiguracionAfpViewSet,
    ConfiguracionRemuneracionViewSet,
    ConfiguracionUitViewSet,
    DescuentoMasivoViewSet,
    DetallePlanillaViewSet,
    PlanillaMensualViewSet,
)
from .usuario_roles_views import UsuarioRolesViewSet
from .views import (
    AreaViewSet,
    ConfiguracionEmpresaViewSet,
    DatosAcademicosViewSet,
    DatosFamiliaresViewSet,
    DatosLaboralesViewSet,
    DocumentosDigitalesViewSet,
    EmpleadoViewSet,
    ModulosViewSet,
    OnboardingViewSet,
    PermisoViewSet,
    RolPermisosViewSet,
    RolViewSet,
    UsuarioViewSet,
)

app_name = "rrhh"

# Router para ViewSets
router = DefaultRouter()
router.register(r"areas", AreaViewSet, basename="area")
router.register(r"empleados", EmpleadoViewSet, basename="empleado")
router.register(
    r"datos-familiares", DatosFamiliaresViewSet, basename="datos-familiares"
)
router.register(
    r"datos-academicos", DatosAcademicosViewSet, basename="datos-academicos"
)
router.register(r"datos-laborales", DatosLaboralesViewSet, basename="datos-laborales")
router.register(
    r"documentos-digitales", DocumentosDigitalesViewSet, basename="documento-digital"
)
# router.register(r'boletas', BoletaViewSet, basename='boleta') - removed, replaced by DocumentosDigitalesViewSet
router.register(
    r"contratos-adendas", ContratosAdendasViewSet, basename="contrato-adenda"
)
# router.register(r'historial-ubicaciones', HistorialUbicacionesViewSet, basename='historial-ubicaciones')  # Temporalmente deshabilitado
router.register(r"usuarios", UsuarioViewSet, basename="usuario")
router.register(r"roles", RolViewSet, basename="rol")
router.register(r"permisos", PermisoViewSet, basename="permiso")
router.register(r"modulos", ModulosViewSet, basename="modulo")
router.register(r"rol-permisos", RolPermisosViewSet, basename="rol-permiso")
router.register(r"usuario-roles", UsuarioRolesViewSet, basename="usuario-rol")
router.register(r"onboarding", OnboardingViewSet, basename="onboarding")
router.register(r'configuracion-empresa', ConfiguracionEmpresaViewSet, basename='configuracion-empresa')

# Remuneraciones
router.register(r'planillas-mensuales', PlanillaMensualViewSet, basename='planilla-mensual')
router.register(r'detalles-planilla', DetallePlanillaViewSet, basename='detalle-planilla')
router.register(r'descuentos-masivos', DescuentoMasivoViewSet, basename='descuento-masivo')
router.register(r'boletas-pago', BoletaPagoViewSet, basename='boleta-pago')
router.register(r'calendarios-pago', CalendarioPagoViewSet, basename='calendario-pago')
router.register(r'configuracion-afp', ConfiguracionAfpViewSet, basename='configuracion-afp')
router.register(r'configuracion-uit', ConfiguracionUitViewSet, basename='configuracion-uit')
router.register(r'configuracion-remuneraciones', ConfiguracionRemuneracionViewSet, basename='configuracion-remuneracion')

urlpatterns = [
    path("", include(router.urls)),
    # URLs para generación de documentos
    path("documentos/", include("api.v1.app_rrhh.document_generation_urls")),
]
