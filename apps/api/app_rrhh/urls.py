from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_rrhh.views import (
    AreaViewSet, EmpleadoViewSet, DatosFamiliaresViewSet,
    DatosAcademicosViewSet, DatosLaboralesViewSet,
    HistorialUbicacionesViewSet, UsuarioViewSet, RolViewSet,
    PermisoViewSet, RolPermisosViewSet, login_view,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'areas', AreaViewSet)
router.register(r'empleados', EmpleadoViewSet)
router.register(r'datos-familiares', DatosFamiliaresViewSet)
router.register(r'datos-academicos', DatosAcademicosViewSet)
router.register(r'datos-laborales', DatosLaboralesViewSet)
# router.register(r'boletas', BoletaViewSet) - removed, replaced by DocumentosDigitalesViewSet
router.register(r'ubicaciones', HistorialUbicacionesViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'roles', RolViewSet)
router.register(r'permisos', PermisoViewSet)
router.register(r'rol-permisos', RolPermisosViewSet)
# router.register(r'reg-permisos', RegPermisosViewSet)  # Eliminado - modelo legacy

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view,name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

