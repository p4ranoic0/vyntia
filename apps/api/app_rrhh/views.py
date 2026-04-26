# from django.shortcuts import render

from apps.core.decorators import (
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
    require_permissions,
)
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .filters import EmpleadoFilter
from .models import (
    DatosAcademicos,
    DatosFamiliares,
    DatosLaborales,
    Empleado,
)
from apps.organization.models import Area, HistorialUbicaciones
from apps.identity.models import (
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
)
from .serializers import (
    AreaSerializer,
    DatosAcademicosSerializer,
    DatosFamiliaresSerializer,
    DatosLaboralesSerializer,
    EmpleadoSerializer,
    HistorialUbicacionesSerializer,
    LoginSerializer,
    PermisoSerializer,
    RolPermisosSerializer,
    RolSerializer,
    UsuarioSerializer,
)

# Importar serializers optimizados
from .serializers_optimized import (
    AreaDetailSerializer,
    AreaListSerializer,
    DatosAcademicosListSerializer,
    DatosFamiliaresListSerializer,
    DatosLaboralesListSerializer,
    EmpleadoDetailSerializer,
    EmpleadoListSerializer,
    PermisoDetailSerializer,
    PermisoListSerializer,
    RolDetailSerializer,
    RolListSerializer,
    RolPermisosDetailSerializer,
    UsuarioDetailSerializer,
    UsuarioListSerializer,
)


class AreaViewSet(viewsets.ModelViewSet):
    """
    Gestión de Áreas Organizacionales.

    Lista, crea, actualiza y elimina áreas de la organización.
    Incluye filtros por órgano y siglas.
    """

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nombre_organo", "siglas_area", "estado_area"]
    tags = ["Áreas"]

    def get_serializer_class(self):
        """Usar serializer optimizado según la acción."""
        if self.action == "list":
            return AreaListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return AreaDetailSerializer
        return AreaSerializer  # Ajusta esto según los campos que tenga tu modelo Area

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    Gestión de Empleados.

    CRUD completo de empleados incluyendo:
    - Datos personales (nombres, documentos, contacto)
    - Datos familiares, académicos y laborales
    - Historial de ubicaciones (departamentos/cargos)

    Soporta filtros avanzados y búsqueda por nombre/documento.
    """

    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmpleadoFilter
    tags = ["Empleados"]

    def get_serializer_class(self):
        """Usar serializer optimizado según la acción."""
        if self.action == "list":
            return EmpleadoListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return EmpleadoDetailSerializer
        return EmpleadoSerializer

    def get_queryset(self):
        """
        Por defecto muestra solo empleados activos,
        a menos que se especifique explícitamente el parámetro estado=false.
        Optimizado con select_related y prefetch_related para reducir queries.
        """
        queryset = Empleado.objects.all()

        # Si no se especifica el parámetro estado, mostrar solo activos
        estado_param = self.request.query_params.get("estado", None)
        if estado_param is None:
            queryset = queryset.filter(estado=True)

        # Optimizaciones según la acción
        if self.action == "list":
            # Para listado, solo cargar el área (ForeignKey)
            queryset = queryset.select_related("area")
        elif self.action == "retrieve":
            # Para detalle, cargar área y todas las relaciones inversas
            queryset = queryset.select_related("area").prefetch_related(
                "datosfamiliares_set",
                "datosacademicos_set",
                "datoslaborales_set",
                "historialubicaciones_set",
            )

        return queryset.order_by(
            "apellido_paterno", "apellido_materno", "nombres_empleado"
        )

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DatosFamiliaresViewSet(viewsets.ModelViewSet):
    """Datos Familiares de Empleados."""

    queryset = DatosFamiliares.objects.all()
    serializer_class = DatosFamiliaresSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Empleados"]

    def get_serializer_class(self):
        """Usar serializer optimizado para listados."""
        if self.action == "list":
            return DatosFamiliaresListSerializer
        return DatosFamiliaresSerializer

    def get_queryset(self):
        """Optimizar con select_related para empleado."""
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related("empleado")
        return queryset

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DatosAcademicosViewSet(viewsets.ModelViewSet):
    """Datos Académicos de Empleados."""

    queryset = DatosAcademicos.objects.all()
    serializer_class = DatosAcademicosSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Empleados"]

    def get_serializer_class(self):
        """Usar serializer optimizado para listados."""
        if self.action == "list":
            return DatosAcademicosListSerializer
        return DatosAcademicosSerializer

    def get_queryset(self):
        """Optimizar con select_related para empleado."""
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related("empleado")
        return queryset

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DatosLaboralesViewSet(viewsets.ModelViewSet):
    """Datos Laborales de Empleados."""

    queryset = DatosLaborales.objects.all()
    serializer_class = DatosLaboralesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Empleados"]

    def get_serializer_class(self):
        """Usar serializer optimizado para listados."""
        if self.action == "list":
            return DatosLaboralesListSerializer
        return DatosLaboralesSerializer

    def get_queryset(self):
        """Optimizar con select_related para empleado y area."""
        queryset = super().get_queryset()
        if self.action in ["list", "retrieve"]:
            queryset = queryset.select_related("empleado", "area")
        return queryset

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class HistorialUbicacionesViewSet(viewsets.ModelViewSet):
    """Historial de Ubicaciones (Departamentos/Cargos) de Empleados."""

    queryset = HistorialUbicaciones.objects.all()
    serializer_class = HistorialUbicacionesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Empleados"]

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UsuarioViewSet(viewsets.ModelViewSet):
    """Gestión de Usuarios del Sistema.

    Usuarios con autenticación y roles de acceso.
    Cada usuario se asocia a un empleado y puede tener múltiples roles.
    """

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Usuarios"]

    def get_serializer_class(self):
        """Usar serializers optimizados según la acción."""
        if self.action == "list":
            return UsuarioListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return UsuarioDetailSerializer
        return UsuarioSerializer

    def get_queryset(self):
        """Optimizar queryset con relaciones."""
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.select_related("empleado")
        elif self.action == "retrieve":
            queryset = queryset.select_related("empleado").prefetch_related(
                "usuarioroles_set__rol"
            )
        return queryset

    @require_hr()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RolViewSet(viewsets.ModelViewSet):
    """Gestión de Roles (RBAC).

    Roles control de acceso basado en roles.
    Cada rol contiene múltiples permisos.
    """

    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Roles y Permisos"]

    def get_serializer_class(self):
        """Usar serializers optimizados según la acción."""
        if self.action == "list":
            return RolListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return RolDetailSerializer
        return RolSerializer

    def get_queryset(self):
        """Optimizar queryset con permisos."""
        queryset = super().get_queryset()
        if self.action == "list":
            queryset = queryset.prefetch_related("rolpermisos_set")
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related("rolpermisos_set__permiso")
        return queryset

    @require_hr()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PermisoViewSet(viewsets.ModelViewSet):
    """Gestión de Permisos.

    Permisos del sistema organizados por módulo.
    Utiliza módulos estáticos configurados en config.modules_config.
    """

    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    tags = ["Roles y Permisos"]

    def get_serializer_class(self):
        """Usar serializers optimizados según la acción."""
        if self.action == "list":
            return PermisoListSerializer
        elif self.action in ["retrieve", "create", "update", "partial_update"]:
            return PermisoDetailSerializer
        return PermisoSerializer

    @require_hr()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RolPermisosViewSet(viewsets.ModelViewSet):
    """Asignación de Permisos a Roles.

    Gestiona la relación muchos-a-muchos entre Roles y Permisos.
    Permite filtrar por rol específico.
    """

    queryset = RolPermisos.objects.all().select_related(
        "rol", "permiso", "asignado_por_usuario"
    )
    serializer_class = RolPermisosSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["rol", "permiso"]
    tags = ["Roles y Permisos"]

    def get_serializer_class(self):
        """Usar serializer detallado optimizado."""
        if self.action in ["list", "retrieve"]:
            return RolPermisosDetailSerializer
        return RolPermisosSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        rol_id = self.request.query_params.get("rol", None)
        if rol_id is not None:
            queryset = queryset.filter(rol_id=rol_id)
        return queryset.order_by("-fecha_asignacion")

    @require_hr()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


from .serializers import LoginSerializer

# Autenticar al usuario y generar tokens
# Este código se debería implementar en la lógica de negocio de su proyecto
# Actualmente, se simula autenticación con la misma contraseña para este ejemplo
# En una implementación real, debería consultar a un servicio de autenticación externo

# Simular autenticación y generación de tokens
# Aquí se simula el uso de Django's authenticate y RefreshToken
# En una implementación real, debería usar un método de autenticación más seguro y robusto


# Simular autenticación y generación de tokens
# Aquí se simula el uso de Django's authenticate y RefreshToken
# En una implementación real, debería usar un método de autenticación más seguro y robusto
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        print(f"Usuario: {username}")
        print(f"Contraseña: {password}")
        print(f"Intentando autenticar usuario: {username}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)

            # Obtener datos del empleado asociado
            empleado = user.empleado

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": {
                        "id": user.usuario_id,
                        "username": user.username,
                        "empleado": {
                            "id": empleado.empleado_id,
                            "nombres": empleado.nombres,
                            "ape_paterno": empleado.ape_paterno,
                            "ape_materno": empleado.ape_materno,
                            "dni": empleado.dni,
                        },
                    },
                }
            )
        else:
            print(f"Autenticación fallida para usuario: {username}")
            return Response(
                {"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
