"""Views for the identity bounded context (B.2 #47).

Migrated from api/v1/rrhh/views.py and api/v1/rrhh/usuario_roles_views.py
to live with the identity URL config. Behavior unchanged — only file
location moved.

ViewSets contained:
- UsuarioViewSet
- RolViewSet
- PermisoViewSet
- ModulosViewSet
- RolPermisosViewSet
- UsuarioRolesViewSet
"""

import logging
from datetime import timedelta

from apps.core.decorators import (
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
    require_permissions,
)
from apps.core.exceptions import BusinessLogicError
from apps.core.pagination import StandardResultsSetPagination
from apps.core.permissions import IsAuthenticated
from apps.core.responses import APIResponse
from apps.identity.models import (
    Module,
    Permission,
    Role,
    RolePermission,
    User,
    UserRole,
)
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.rrhh.filters import UsuarioFilter
from api.v1.rrhh.permissions import RRHHPermission, UsuarioPermission
from api.v1.rrhh.serializers import (
    ModulosSerializer,
    PermisoSerializer,
    RolPermisosSerializer,
    RolSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
)
from api.v1.rrhh.usuario_roles_serializers import (
    AsignarRolSerializer,
    UsuarioRolesCreateSerializer,
    UsuarioRolesListSerializer,
    UsuarioRolesSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=["Módulos"],
        summary="Listar módulos",
        description="Obtiene una lista paginada de todos los módulos del sistema con filtros opcionales.",
    ),
    create=extend_schema(
        tags=["Módulos"],
        summary="Crear módulo",
        description="Crea un nuevo módulo en el sistema.",
    ),
    retrieve=extend_schema(
        tags=["Módulos"],
        summary="Obtener módulo",
        description="Obtiene los detalles de un módulo específico por su ID.",
    ),
    update=extend_schema(
        tags=["Módulos"],
        summary="Actualizar módulo",
        description="Actualiza completamente un módulo existente.",
    ),
    partial_update=extend_schema(
        tags=["Módulos"],
        summary="Actualizar módulo parcialmente",
        description="Actualiza parcialmente un módulo existente.",
    ),
    destroy=extend_schema(
        tags=["Módulos"],
        summary="Eliminar módulo",
        description="Elimina un módulo del sistema.",
    ),
)
class ModulosViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de módulos del sistema."""

    queryset = Module.objects.prefetch_related("modulo_permisos")
    serializer_class = ModulosSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["nombre_modulo", "descripcion_modulo", "ruta_modulo"]
    ordering_fields = ["nombre_modulo", "orden_visualizacion", "estado_modulo"]
    ordering = ["orden_visualizacion", "nombre_modulo"]

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar módulos - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener módulo específico - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        """Crear módulo - requiere rol administrador."""
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar módulo - requiere rol administrador."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar módulo parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar módulo - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Obtiene queryset optimizado con filtros de estado."""
        queryset = super().get_queryset()

        # Filtrar módulos activos por defecto
        queryset = queryset.filter(estado_modulo="activo")

        return queryset

    def perform_create(self, serializer):
        """Registra la creación del módulo."""
        logger.info(
            f"Creando nuevo módulo: {serializer.validated_data.get('nombre_modulo')}"
        )
        serializer.save()

    def perform_update(self, serializer):
        """Registra la actualización del módulo."""
        logger.info(f"Actualizando módulo: {serializer.instance.nombre_modulo}")
        serializer.save()

    def perform_destroy(self, instance):
        """Realiza eliminación lógica del módulo."""
        logger.info(f"Eliminando módulo: {instance.nombre_modulo}")
        instance.estado_modulo = "inactivo"
        instance.save()

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activos(self, request):
        """Obtiene solo los módulos activos."""
        queryset = self.get_queryset().filter(estado_modulo="activo")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message="Módulos activos obtenidos exitosamente"
        )


@extend_schema_view(
    list=extend_schema(
        tags=["Role-Permisos"],
        summary="Listar asignaciones rol-permiso",
        description="Obtiene una lista paginada de todas las asignaciones de permisos a roles.",
    ),
    create=extend_schema(
        tags=["Role-Permisos"],
        summary="Asignar permiso a rol",
        description="Asigna un permiso específico a un rol.",
    ),
    retrieve=extend_schema(
        tags=["Role-Permisos"],
        summary="Obtener asignación rol-permiso",
        description="Obtiene los detalles de una asignación específica por su ID.",
    ),
    destroy=extend_schema(
        tags=["Role-Permisos"],
        summary="Remover permiso de rol",
        description="Remueve un permiso específico de un rol.",
    ),
)
class RolPermisosViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de asignaciones de permisos a roles."""

    queryset = RolePermission.objects.select_related(
        "rol", "permiso", "asignado_por_usuario"
    )
    serializer_class = RolPermisosSerializer
    permission_classes = [UsuarioPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["rol__nombre_rol", "permiso__nombre_permiso"]
    ordering_fields = ["fecha_asignacion", "rol__nombre_rol", "permiso__nombre_permiso"]
    ordering = ["-fecha_asignacion"]

    # Only allow GET, POST, DELETE methods
    http_method_names = ["get", "post", "delete", "head", "options"]

    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar asignaciones rol-permiso - requiere rol administrador."""
        return super().list(request, *args, **kwargs)

    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener asignación específica - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        """Crear asignación rol-permiso - requiere rol administrador."""
        return super().create(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar asignación rol-permiso - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Obtiene queryset con filtros opcionales."""
        queryset = super().get_queryset()

        # Filtrar por rol si se especifica
        rol_id = self.request.query_params.get("id")
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)

        # Filtrar por permiso si se especifica
        permiso_id = self.request.query_params.get("id")
        if permiso_id:
            queryset = queryset.filter(permiso_id=permiso_id)

        return queryset

    def perform_create(self, serializer):
        """Registra la asignación del permiso al rol."""
        # Asignar el usuario que realiza la asignación
        serializer.save(asignado_por_usuario=self.request.user)

        logger.info(
            f"Permission {serializer.instance.permiso.nombre_permiso} "
            f"asignado al rol {serializer.instance.rol.nombre_rol} "
            f"por {self.request.user.nombres_usuario}"
        )

    def perform_destroy(self, instance):
        """Registra la eliminación de la asignación."""
        logger.info(
            f"Removiendo permiso {instance.permiso.nombre_permiso} "
            f"del rol {instance.rol.nombre_rol} "
            f"por {self.request.user.nombres_usuario}"
        )
        super().perform_destroy(instance)

    @action(detail=False, methods=["get"])
    @require_admin()
    def por_rol(self, request):
        """Obtiene todos los permisos asignados a un rol específico."""
        rol_id = request.query_params.get("id")
        if not rol_id:
            return APIResponse.error(
                message="Se requiere el parámetro rol_id",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(rol_id=rol_id)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message=f"Permisos del rol obtenidos exitosamente"
        )

    @action(detail=False, methods=["get"])
    @require_admin()
    def por_permiso(self, request):
        """Obtiene todos los roles que tienen un permiso específico."""
        permiso_id = request.query_params.get("id")
        if not permiso_id:
            return APIResponse.error(
                message="Se requiere el parámetro permiso_id",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(permiso_id=permiso_id)
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message=f"Roles con el permiso obtenidos exitosamente"
        )


# RegUbicacionViewSet removido - usar LocationHistory model


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet for User management."""

    queryset = User.objects.select_related("empleado")
    permission_classes = [UsuarioPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = UsuarioFilter
    search_fields = [
        "nombres_usuario",
        "correo_institucional",
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
    ]
    ordering_fields = ["nombres_usuario", "created_at", "ultimo_acceso"]
    ordering = ["nombres_usuario"]

    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar usuarios - requiere rol administrador."""
        return super().list(request, *args, **kwargs)

    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener usuario específico - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        """Crear usuario - requiere rol administrador."""
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar usuario - requiere rol administrador."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar usuario parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar usuario - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        queryset = super().get_queryset()

        # Soft delete: Filter out inactive users by default
        incluir_inactivos = (
            self.request.query_params.get("incluir_inactivos", "false").lower()
            == "true"
        )
        if not incluir_inactivos:
            queryset = queryset.filter(estado_usuario="activo")

        # Filter by status
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado_usuario=estado)

        return queryset

    def perform_create(self, serializer):
        """Create user with logging."""
        usuario = serializer.save()
        logger.info(
            f"User creado: {usuario.nombres_usuario}",
            extra={
                "user_id": self.request.user.pk,
                "new_user_id": usuario.pk,
                "action": "create_usuario",
            },
        )

    def perform_update(self, serializer):
        """Update user with logging."""
        usuario = serializer.save()
        logger.info(
            f"User actualizado: {usuario.nombres_usuario}",
            extra={
                "user_id": self.request.user.pk,
                "updated_user_id": usuario.pk,
                "action": "update_usuario",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete user by changing status to inactive."""
        instance.estado_usuario = "inactivo"
        instance.save()
        logger.info(
            f"User desactivado: {instance.nombres_usuario}",
            extra={
                "user_id": self.request.user.pk,
                "deactivated_user_id": instance.pk,
                "action": "soft_delete_usuario",
            },
        )

    @action(detail=False, methods=["get"])
    @require_admin()
    def sin_login_reciente(self, request):
        """Get users without recent login."""
        try:
            dias = int(request.query_params.get("dias", 30))
            threshold = timezone.now() - timedelta(days=dias)
            usuarios = User.objects.filter(
                is_active=True,
                last_login__lt=threshold,
            ).order_by("last_login")

            serializer = self.get_serializer(usuarios, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Usuarios sin login en los últimos {dias} días",
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo usuarios sin login reciente: {str(e)}",
                extra={"user_id": request.user.pk, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener usuarios",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"])
    @require_permissions(["gestionar_usuarios"])
    def roles(self, request, pk=None):
        """
        Obtiene los roles asignados a un usuario específico
        """
        try:
            usuario = self.get_object()
            roles_asignados = UserRole.objects.activos().por_usuario(usuario)

            serializer = UsuarioRolesListSerializer(roles_asignados, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Roles del usuario {usuario.username} obtenidos exitosamente",
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener roles del usuario", errors={"detail": str(e)}
            )

    @action(detail=True, methods=["post"])
    @require_admin()
    def asignar_rol(self, request, pk=None):
        """
        Asigna uno o múltiples roles a un usuario específico
        """
        try:
            usuario = self.get_object()
            serializer = AsignarRolSerializer(data=request.data)

            if serializer.is_valid():
                roles_ids = serializer.validated_data["roles"]
                fecha_expiracion = serializer.validated_data.get("fecha_expiracion")

                asignaciones_creadas = []
                errores = []

                for rol_id in roles_ids:
                    # Verificar si ya existe una asignación activa
                    asignacion_existente = UserRole.objects.filter(
                        usuario=usuario, rol_id=rol_id, estado_asignacion="activo"
                    ).first()

                    if asignacion_existente:
                        errores.append(
                            f"El usuario ya tiene asignado el rol con ID {rol_id}"
                        )
                        continue

                    # Crear nueva asignación
                    try:
                        usuario_rol = UserRole.objects.create(
                            usuario=usuario,
                            rol_id=rol_id,
                            fecha_asignacion=timezone.now(),
                            fecha_expiracion=fecha_expiracion,
                            estado_asignacion="activo",
                            asignado_por_usuario=request.user,
                        )
                        asignaciones_creadas.append(usuario_rol)
                    except Exception as e:
                        errores.append(f"Error asignando rol {rol_id}: {str(e)}")

                if asignaciones_creadas:
                    response_serializer = UsuarioRolesSerializer(
                        asignaciones_creadas, many=True
                    )
                    response_data = {
                        "asignaciones": response_serializer.data,
                        "total_asignadas": len(asignaciones_creadas),
                        "errores": errores,
                    }
                    return APIResponse.success(
                        data=response_data,
                        message=f"Se asignaron {len(asignaciones_creadas)} roles exitosamente",
                    )
                else:
                    return APIResponse.error(
                        message="No se pudo asignar ningún rol",
                        errors={"detail": errores},
                    )
            else:
                return APIResponse.error(
                    message="Datos inválidos para asignar rol", errors=serializer.errors
                )
        except Exception as e:
            return APIResponse.error(
                message="Error al asignar rol al usuario", errors={"detail": str(e)}
            )

    @action(detail=True, methods=["post"])
    @require_admin()
    def remover_rol(self, request, pk=None):
        """
        Remueve un rol de un usuario específico
        """
        try:
            usuario = self.get_object()
            rol_id = request.data.get("id")

            if not rol_id:
                return APIResponse.error(
                    message="ID del rol es requerido",
                    errors={"id": ["Este campo es requerido"]},
                )

            # Buscar asignación activa
            asignacion = UserRole.objects.filter(
                usuario=usuario, rol_id=rol_id, estado_asignacion="activo"
            ).first()

            if not asignacion:
                return APIResponse.error(
                    message="No se encontró asignación activa para este rol",
                    errors={"rol": ["El usuario no tiene este rol asignado"]},
                )

            # Marcar como inactivo en lugar de eliminar
            asignacion.estado_asignacion = "inactivo"
            asignacion.fecha_expiracion = timezone.now()
            asignacion.save()

            return APIResponse.success(message="Role removido exitosamente del usuario")
        except Exception as e:
            return APIResponse.error(
                message="Error al remover rol del usuario", errors={"detail": str(e)}
            )


class RolViewSet(viewsets.ModelViewSet):
    """ViewSet for Role management."""

    queryset = Role.objects.prefetch_related(
        "usuarios_asignados__usuario", "permisos_asignados__permiso"
    )
    serializer_class = RolSerializer
    permission_classes = [UsuarioPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["nombre_rol", "descripcion_rol"]
    ordering_fields = ["nombre_rol", "estado_rol"]
    ordering = ["nombre_rol"]

    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar roles - requiere rol administrador."""
        return super().list(request, *args, **kwargs)

    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener rol específico - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        """Crear rol - requiere rol administrador."""
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar rol - requiere rol administrador."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar rol parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar rol - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filter by status if specified."""
        queryset = super().get_queryset()

        # Soft delete: Filter out inactive roles by default
        incluir_inactivos = (
            self.request.query_params.get("incluir_inactivos", "false").lower()
            == "true"
        )
        if not incluir_inactivos:
            queryset = queryset.filter(estado_rol="activo")

        # Filter by status
        estado_rol = self.request.query_params.get("estado_rol")
        if estado_rol:
            queryset = queryset.filter(estado_rol=estado_rol)

        return queryset

    def perform_destroy(self, instance):
        """Soft delete role by changing status to inactive."""
        instance.estado_rol = "inactivo"
        instance.save()
        logger.info(
            f"Role desactivado: {instance.nombre_rol}",
            extra={
                "user_id": self.request.user.pk,
                "id": instance.pk,
                "action": "soft_delete_rol",
            },
        )

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activos(self, request):
        """Get only active roles."""
        queryset = self.get_queryset().filter(estado_rol="activo")
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Roles activos")


class PermisoViewSet(viewsets.ModelViewSet):
    """ViewSet for Permission management."""

    queryset = Permission.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["nombre_permiso", "descripcion_permiso"]
    ordering_fields = ["nombre_permiso", "descripcion_permiso"]
    ordering = ["nombre_permiso"]

    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar permisos - requiere rol administrador."""
        return super().list(request, *args, **kwargs)

    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener permiso específico - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def create(self, request, *args, **kwargs):
        """Crear permiso - requiere rol administrador."""
        return super().create(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar permiso - requiere rol administrador."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar permiso parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar permiso - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filter by status if specified."""
        queryset = super().get_queryset()

        # Soft delete: Filter out inactive permissions by default
        incluir_inactivos = (
            self.request.query_params.get("incluir_inactivos", "false").lower()
            == "true"
        )
        if not incluir_inactivos:
            queryset = queryset.filter(estado_permiso="activo")

        # Filter by status
        estado_permiso = self.request.query_params.get("estado_permiso")
        if estado_permiso:
            queryset = queryset.filter(estado_permiso=estado_permiso)

        return queryset

    def perform_destroy(self, instance):
        """Soft delete: change estado_permiso to 'inactivo' instead of physical deletion."""
        try:
            instance.estado_permiso = "inactivo"
            instance.save(update_fields=["estado_permiso"])
            logger.info(
                f"Permission {instance.pk} soft deleted by changing estado_permiso to 'inactivo'"
            )
        except Exception as e:
            logger.error(
                f"Error performing soft delete on Permission {instance.pk}: {str(e)}"
            )
            raise BusinessLogicError(f"Error al desactivar el permiso: {str(e)}")


class UsuarioRolesViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las asignaciones de roles a usuarios
    """
    queryset = UserRole.objects.all()
    serializer_class = UsuarioRolesSerializer
    permission_classes = [IsAuthenticated, RRHHPermission]

    @require_admin()
    def list(self, request, *args, **kwargs):
        """Listar asignaciones de roles - requiere rol administrador."""
        return super().list(request, *args, **kwargs)

    @require_admin()
    def retrieve(self, request, *args, **kwargs):
        """Obtener asignación específica - requiere rol administrador."""
        return super().retrieve(request, *args, **kwargs)

    @require_admin()
    def update(self, request, *args, **kwargs):
        """Actualizar asignación - requiere rol administrador."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar asignación parcialmente - requiere rol administrador."""
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        """
        Retorna la clase de serializer apropiada según la acción
        """
        if self.action == 'create':
            return UsuarioRolesCreateSerializer
        elif self.action == 'list':
            return UsuarioRolesListSerializer
        return UsuarioRolesSerializer

    def get_queryset(self):
        """
        Filtra el queryset según los parámetros de consulta
        """
        queryset = UserRole.objects.select_related('usuario', 'rol', 'asignado_por_usuario')

        # Filtrar por usuario
        usuario_id = self.request.query_params.get('id')
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)

        # Filtrar por rol
        rol_id = self.request.query_params.get('id')
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)

        # Filtrar por estado
        estado = self.request.query_params.get('estado', 'activo')
        if estado:
            queryset = queryset.filter(estado_asignacion=estado)

        return queryset.order_by('-fecha_asignacion')

    @require_admin()
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva asignación de rol a usuario - requiere rol administrador.
        """
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Verificar si ya existe una asignación activa
                usuario_id = serializer.validated_data['usuario'].usuario_id
                rol_id = serializer.validated_data['rol'].rol_id

                asignacion_existente = UserRole.objects.filter(
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    estado_asignacion='activo'
                ).first()

                if asignacion_existente:
                    return APIResponse.error(
                        message="El usuario ya tiene este rol asignado",
                        errors={"rol": ["Ya existe una asignación activa para este rol"]}
                    )

                # Crear la asignación
                usuario_rol = serializer.save(
                    asignado_por_usuario=request.user,
                    fecha_asignacion=timezone.now(),
                    estado_asignacion='activo'
                )

                response_serializer = UsuarioRolesSerializer(usuario_rol)
                return APIResponse.success(
                    data=response_serializer.data,
                    message="Role asignado exitosamente al usuario"
                )
            else:
                return APIResponse.error(
                    message="Datos inválidos para asignar rol",
                    errors=serializer.errors
                )
        except Exception as e:
            return APIResponse.error(
                message="Error al asignar rol al usuario",
                errors={"detail": str(e)}
            )

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """
        Marca una asignación como inactiva en lugar de eliminarla - requiere rol administrador.
        """
        try:
            instance = self.get_object()

            if instance.estado_asignacion == 'inactivo':
                return APIResponse.error(
                    message="Esta asignación ya está inactiva",
                    errors={"estado": ["La asignación ya fue removida"]}
                )

            # Marcar como inactivo
            instance.estado_asignacion = 'inactivo'
            instance.fecha_expiracion = timezone.now()
            instance.save()

            return APIResponse.success(
                message="Asignación de rol removida exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al remover asignación de rol",
                errors={"detail": str(e)}
            )

    @require_authenticated()
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """
        Obtiene todas las asignaciones de roles activas
        """
        try:
            asignaciones = self.get_queryset().filter(estado_asignacion='activo')
            serializer = UsuarioRolesListSerializer(asignaciones, many=True)

            return APIResponse.success(
                data=serializer.data,
                message="Asignaciones activas obtenidas exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener asignaciones activas",
                errors={"detail": str(e)}
            )

    @require_admin()
    @action(detail=False, methods=['get'])
    def por_usuario(self, request):
        """
        Obtiene las asignaciones de roles para un usuario específico
        """
        try:
            usuario_id = request.query_params.get('id')
            if not usuario_id:
                return APIResponse.error(
                    message="ID del usuario es requerido",
                    errors={"id": ["Este parámetro es requerido"]}
                )

            asignaciones = self.get_queryset().filter(
                usuario_id=usuario_id,
                estado_asignacion='activo'
            )

            serializer = UsuarioRolesListSerializer(asignaciones, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Roles del usuario obtenidos exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener roles del usuario",
                errors={"detail": str(e)}
            )

    @require_admin()
    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        """
        Obtiene los usuarios que tienen un rol específico
        """
        try:
            rol_id = request.query_params.get('id')
            if not rol_id:
                return APIResponse.error(
                    message="ID del rol es requerido",
                    errors={"id": ["Este parámetro es requerido"]}
                )

            asignaciones = self.get_queryset().filter(
                rol_id=rol_id,
                estado_asignacion='activo'
            )

            serializer = UsuarioRolesListSerializer(asignaciones, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Usuarios con el rol obtenidos exitosamente"
            )
        except Exception as e:
            return APIResponse.error(
                message="Error al obtener usuarios con el rol",
                errors={"detail": str(e)}
            )

    @require_admin()
    @action(detail=False, methods=['post'])
    def asignar_multiple(self, request):
        """
        Asigna múltiples roles a un usuario o un rol a múltiples usuarios
        """
        try:
            usuario_ids = request.data.get('usuario_ids', [])
            rol_ids = request.data.get('rol_ids', [])
            fecha_expiracion = request.data.get('fecha_expiracion')

            if not usuario_ids or not rol_ids:
                return APIResponse.error(
                    message="Se requieren IDs de usuarios y roles",
                    errors={
                        "usuario_ids": ["Este campo es requerido"] if not usuario_ids else [],
                        "rol_ids": ["Este campo es requerido"] if not rol_ids else []
                    }
                )

            asignaciones_creadas = []
            errores = []

            for usuario_id in usuario_ids:
                for rol_id in rol_ids:
                    # Verificar si ya existe
                    if UserRole.objects.filter(
                        usuario_id=usuario_id,
                        rol_id=rol_id,
                        estado_asignacion='activo'
                    ).exists():
                        errores.append(f"User {usuario_id} ya tiene el rol {rol_id}")
                        continue

                    # Crear asignación
                    try:
                        usuario_rol = UserRole.objects.create(
                            usuario_id=usuario_id,
                            rol_id=rol_id,
                            fecha_asignacion=timezone.now(),
                            fecha_expiracion=fecha_expiracion,
                            estado_asignacion='activo',
                            asignado_por_usuario=request.user
                        )
                        asignaciones_creadas.append(usuario_rol)
                    except Exception as e:
                        errores.append(f"Error asignando rol {rol_id} a usuario {usuario_id}: {str(e)}")

            if asignaciones_creadas:
                serializer = UsuarioRolesSerializer(asignaciones_creadas, many=True)
                response_data = {
                    "asignaciones": serializer.data,
                    "total_creadas": len(asignaciones_creadas),
                    "errores": errores
                }
                return APIResponse.success(
                    data=response_data,
                    message=f"Se crearon {len(asignaciones_creadas)} asignaciones exitosamente"
                )
            else:
                return APIResponse.error(
                    message="No se pudo crear ninguna asignación",
                    errors={"detail": errores}
                )
        except Exception as e:
            return APIResponse.error(
                message="Error en asignación múltiple",
                errors={"detail": str(e)}
            )

    @require_hr()
    @action(detail=False, methods=['get'])
    def buscar_usuarios_por_roles(self, request):
        """
        Busca usuarios que tienen roles específicos asignados
        Parámetros de consulta:
        - rol_ids: Lista de IDs de roles separados por coma
        - nombres: Filtro por nombres de usuario (búsqueda parcial)
        - estado: Estado de la asignación (activo, inactivo, expirado)
        - operador: 'AND' o 'OR' para múltiples roles (por defecto 'OR')
        """
        try:
            # Obtener parámetros de consulta
            rol_ids_param = request.query_params.get('rol_ids', '')
            nombres_filtro = request.query_params.get('nombres', '')
            estado_asignacion = request.query_params.get('estado', 'activo')
            operador = request.query_params.get('operador', 'OR').upper()

            if not rol_ids_param:
                return APIResponse.error(
                    message="Se requiere al menos un ID de rol",
                    errors={"rol_ids": ["Este parámetro es requerido"]}
                )

            # Convertir rol_ids a lista de enteros
            try:
                rol_ids = [int(id.strip()) for id in rol_ids_param.split(',') if id.strip()]
            except ValueError:
                return APIResponse.error(
                    message="IDs de roles inválidos",
                    errors={"rol_ids": ["Deben ser números enteros separados por coma"]}
                )

            # Construir consulta base
            queryset = User.objects.select_related('empleado').prefetch_related(
                'roles_asignados__rol'
            )

            # Filtrar por nombres si se proporciona
            if nombres_filtro:
                queryset = queryset.filter(
                    Q(nombres_usuario__icontains=nombres_filtro) |
                    Q(empleado__nombres_empleado__icontains=nombres_filtro) |
                    Q(empleado__apellido_paterno__icontains=nombres_filtro) |
                    Q(empleado__apellido_materno__icontains=nombres_filtro)
                )

            # Filtrar por roles asignados
            if operador == 'AND':
                # User debe tener TODOS los roles especificados
                for rol_id in rol_ids:
                    queryset = queryset.filter(
                        roles_asignados__rol_id=rol_id,
                        roles_asignados__estado_asignacion=estado_asignacion
                    )
            else:
                # User debe tener AL MENOS UNO de los roles especificados
                queryset = queryset.filter(
                    roles_asignados__rol_id__in=rol_ids,
                    roles_asignados__estado_asignacion=estado_asignacion
                ).distinct()

            # Serializar resultados
            usuarios_data = []
            for usuario in queryset:
                # Obtener roles activos del usuario
                roles_activos = UserRole.objects.filter(
                    usuario=usuario,
                    estado_asignacion=estado_asignacion
                ).select_related('rol')

                usuario_data = {
                    'id': usuario.usuario_id,
                    'nombres_usuario': usuario.nombres_usuario,
                    'correo_institucional': usuario.correo_institucional,
                    'empleado': {
                        'nombres_empleado': usuario.empleado.nombres_empleado if usuario.empleado else None,
                        'apellido_paterno': usuario.empleado.apellido_paterno if usuario.empleado else None,
                        'apellido_materno': usuario.empleado.apellido_materno if usuario.empleado else None,
                    } if usuario.empleado else None,
                    'roles_asignados': [
                        {
                            'id': ur.rol.rol_id,
                            'nombre_rol': ur.rol.nombre_rol,
                            'descripcion_rol': ur.rol.descripcion_rol,
                            'fecha_asignacion': ur.fecha_asignacion,
                            'fecha_expiracion': ur.fecha_expiracion,
                            'estado_asignacion': ur.estado_asignacion
                        }
                        for ur in roles_activos
                    ]
                }
                usuarios_data.append(usuario_data)

            # Información adicional
            total_usuarios = len(usuarios_data)
            roles_info = Role.objects.filter(rol_id__in=rol_ids).values('id', 'nombre_rol')

            response_data = {
                'usuarios': usuarios_data,
                'total_usuarios': total_usuarios,
                'filtros_aplicados': {
                    'rol_ids': rol_ids,
                    'roles_nombres': list(roles_info),
                    'nombres_filtro': nombres_filtro,
                    'estado_asignacion': estado_asignacion,
                    'operador': operador
                }
            }

            return APIResponse.success(
                data=response_data,
                message=f"Se encontraron {total_usuarios} usuarios con los roles especificados"
            )

        except Exception as e:
            return APIResponse.error(
                message="Error al buscar usuarios por roles",
                errors={"detail": str(e)}
            )
