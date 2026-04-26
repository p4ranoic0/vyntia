"""Views for RRHH API v1."""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

from app_rrhh import services
from app_rrhh.models import (
    Area,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    DatosAcademicos,
    DatosFamiliares,
    DatosLaborales,
    DocumentosDigitales,
    Empleado,
    Modulos,
    OnboardingEmpleado,
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
    UsuarioRoles,
)

# Importar decoradores de permisos y cache
from apps.core.decorators import (
    cache_response,
    invalidate_cache,
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
    require_permissions,
    require_roles,
)
from apps.core.exceptions import BusinessLogicError
from apps.core.pagination import StandardResultsSetPagination
from apps.core.responses import APIResponse
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .filters import AreaFilter, DatosLaboralesFilter, EmpleadoFilter, UsuarioFilter
from .permissions import (
    AreaPermission,
    DocumentosDigitalesPermission,
    EmpleadoPermission,
    RRHHPermission,
    UsuarioPermission,
)
from .serializers import (
    AreaListSerializer,
    AreaSerializer,
    ConfiguracionAfpSerializer,
    ConfiguracionRemuneracionSerializer,
    DatosAcademicosSerializer,
    DatosFamiliaresSerializer,
    DatosLaboralesSerializer,
    DocumentosDigitalesCreateSerializer,
    DocumentosDigitalesSerializer,
    EmpleadoCreateSerializer,
    EmpleadoListSerializer,
    EmpleadoSerializer,
    EmpleadoUpdateSerializer,
    ModulosSerializer,
    OnboardingEmpleadoSerializer,
    OnboardingIniciarSerializer,
    OnboardingValidacionSerializer,
    PermisoSerializer,
    RolPermisosSerializer,
    RolSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,
)
from .usuario_roles_serializers import (
    AsignarRolSerializer,
    UsuarioRolesCreateSerializer,
    UsuarioRolesListSerializer,
    UsuarioRolesSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        tags=["Areas"],
        summary="Listar áreas",
        description="Obtiene una lista paginada de todas las áreas organizacionales con filtros opcionales.",
    ),
    create=extend_schema(
        tags=["Areas"],
        summary="Crear área",
        description="Crea una nueva área organizacional.",
    ),
    retrieve=extend_schema(
        tags=["Areas"],
        summary="Obtener área",
        description="Obtiene los detalles de un área específica por su ID.",
    ),
    update=extend_schema(
        tags=["Areas"],
        summary="Actualizar área",
        description="Actualiza completamente un área existente.",
    ),
    partial_update=extend_schema(
        tags=["Areas"],
        summary="Actualizar área parcialmente",
        description="Actualiza parcialmente un área existente.",
    ),
    destroy=extend_schema(
        tags=["Areas"],
        summary="Eliminar área",
        description="Elimina un área del sistema.",
    ),
)
class AreaViewSet(viewsets.ModelViewSet):
    """ViewSet for Area management."""

    queryset = Area.objects.select_related("area_padre").prefetch_related(
        "ubicaciones_destino__empleado",
        "empleados_laborales__empleado",
    )
    permission_classes = [AreaPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = AreaFilter
    search_fields = ["siglas_area", "nombre_unidad_organica", "nombre_organo"]
    ordering_fields = ["siglas_area", "nombre_unidad_organica", "estado_area"]
    ordering = ["siglas_area"]

    @cache_response(timeout=600, key_prefix="areas")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar áreas - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=600, key_prefix="area_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener área específica - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache(["view_cache:areas:*", "view_cache:area_detail:*"])
    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear área - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @invalidate_cache(["view_cache:areas:*", "view_cache:area_detail:*"])
    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar área - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:areas:*", "view_cache:area_detail:*"])
    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar área parcialmente - requiere rol RRHH."""
        return super().partial_update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:areas:*", "view_cache:area_detail:*"])
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar área - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return AreaListSerializer
        return AreaSerializer

    def get_queryset(self):
        """Get optimized queryset with annotations for list view."""
        queryset = super().get_queryset()

        # Filter out inactive areas by default (soft delete)
        queryset = queryset.filter(estado_area="activo")

        if self.action == "list":
            # Add employee count annotation for list view
            queryset = queryset.annotate(
                empleados_activos_count=Count(
                    "ubicaciones_destino",
                    filter=Q(ubicaciones_destino__estado_ubicacion="activo"),
                )
            )

        # Allow showing all areas including inactive if explicitly requested
        incluir_inactivas = (
            self.request.query_params.get("incluir_inactivas", "false").lower()
            == "true"
        )
        if incluir_inactivas:
            queryset = super().get_queryset()  # Remove the estado_area filter
            if self.action == "list":
                queryset = queryset.annotate(
                    empleados_activos_count=Count(
                        "ubicaciones_destino",
                        filter=Q(ubicaciones_destino__estado_ubicacion="activo"),
                    )
                )

        return queryset

    def perform_create(self, serializer):
        """Create area with logging."""
        area = serializer.save()
        logger.info(
            f"Área creada: {area.siglas_area}",
            extra={
                "user_id": self.request.user.usuario_id,
                "area_id": area.area_id,
                "action": "create_area",
            },
        )

    def perform_update(self, serializer):
        """Update area with logging."""
        area = serializer.save()
        logger.info(
            f"Área actualizada: {area.siglas_area}",
            extra={
                "user_id": self.request.user.usuario_id,
                "area_id": area.area_id,
                "action": "update_area",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete area by changing status to inactive."""
        instance.estado_area = "inactiva"
        instance.save()
        logger.info(
            f"Área desactivada: {instance.siglas_area}",
            extra={
                "user_id": self.request.user.id,
                "area_id": instance.area_id,
                "action": "soft_delete_area",
            },
        )

    @extend_schema(
        tags=["Areas"],
        summary="Obtener empleados del área",
        description="Obtiene una lista de todos los empleados que pertenecen a un área específica.",
    )
    @action(detail=True, methods=["get"])
    @require_permissions(["ver_empleados"])
    def empleados(self, request, pk=None):
        """Get employees in this area."""
        try:
            area = self.get_object()
            empleados = area.empleados_actuales()

            # Apply pagination
            page = self.paginate_queryset(empleados)
            if page is not None:
                serializer = EmpleadoListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = EmpleadoListSerializer(empleados, many=True)
            return APIResponse.success(
                data=serializer.data,
                message="Empleados del área obtenidos exitosamente",
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo empleados del área: {str(e)}",
                extra={
                    "user_id": request.user.usuario_id,
                    "area_id": pk,
                    "error": str(e),
                },
            )
            return APIResponse.error(
                message="Error al obtener empleados del área",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Areas"],
        summary="Obtener estadísticas del área",
        description="Obtiene estadísticas detalladas de un área específica incluyendo métricas de empleados.",
    )
    @action(detail=True, methods=["get"])
    @require_hr()
    def estadisticas(self, request, pk=None):
        """Get area statistics."""
        try:
            area = self.get_object()
            stats = services.AreaService.get_area_statistics(area.area_id)

            return APIResponse.success(
                data=stats, message="Estadísticas del área obtenidas exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas del área: {str(e)}",
                extra={
                    "user_id": request.user.usuario_id,
                    "area_id": pk,
                    "error": str(e),
                },
            )
            return APIResponse.error(
                message="Error al obtener estadísticas del área",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Areas"],
        summary="Obtener resumen de todas las áreas",
        description="Obtiene un resumen estadístico de todas las áreas del sistema.",
    )
    @action(detail=False, methods=["get"])
    @require_hr()
    def resumen(self, request):
        """Get summary of all areas."""
        try:
            areas_summary = services.AreaService.get_areas_summary()

            return APIResponse.success(
                data=areas_summary, message="Resumen de áreas obtenido exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo resumen de áreas: {str(e)}",
                extra={"user_id": request.user.usuario_id, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener resumen de áreas",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activas(self, request):
        """Get only active areas."""
        queryset = self.get_queryset().filter(estado="activa")
        serializer = AreaListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Áreas activas")


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

    queryset = Modulos.objects.prefetch_related("permiso_set")
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
        tags=["Rol-Permisos"],
        summary="Listar asignaciones rol-permiso",
        description="Obtiene una lista paginada de todas las asignaciones de permisos a roles.",
    ),
    create=extend_schema(
        tags=["Rol-Permisos"],
        summary="Asignar permiso a rol",
        description="Asigna un permiso específico a un rol.",
    ),
    retrieve=extend_schema(
        tags=["Rol-Permisos"],
        summary="Obtener asignación rol-permiso",
        description="Obtiene los detalles de una asignación específica por su ID.",
    ),
    destroy=extend_schema(
        tags=["Rol-Permisos"],
        summary="Remover permiso de rol",
        description="Remueve un permiso específico de un rol.",
    ),
)
class RolPermisosViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de asignaciones de permisos a roles."""

    queryset = RolPermisos.objects.select_related(
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
        rol_id = self.request.query_params.get("rol_id")
        if rol_id:
            queryset = queryset.filter(rol_id=rol_id)

        # Filtrar por permiso si se especifica
        permiso_id = self.request.query_params.get("permiso_id")
        if permiso_id:
            queryset = queryset.filter(permiso_id=permiso_id)

        return queryset

    def perform_create(self, serializer):
        """Registra la asignación del permiso al rol."""
        # Asignar el usuario que realiza la asignación
        serializer.save(asignado_por_usuario=self.request.user)

        logger.info(
            f"Permiso {serializer.instance.permiso.nombre_permiso} "
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
        rol_id = request.query_params.get("rol_id")
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
        permiso_id = request.query_params.get("permiso_id")
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


@extend_schema_view(
    list=extend_schema(
        tags=["Empleados"],
        summary="Listar empleados",
        description="Obtiene una lista paginada de todos los empleados con filtros opcionales.",
    ),
    create=extend_schema(
        tags=["Empleados"],
        summary="Crear empleado",
        description="Crea un nuevo empleado en el sistema.",
    ),
    retrieve=extend_schema(
        tags=["Empleados"],
        summary="Obtener empleado",
        description="Obtiene los detalles de un empleado específico por su ID.",
    ),
    update=extend_schema(
        tags=["Empleados"],
        summary="Actualizar empleado",
        description="Actualiza completamente un empleado existente.",
    ),
    partial_update=extend_schema(
        tags=["Empleados"],
        summary="Actualizar empleado parcialmente",
        description="Actualiza parcialmente un empleado existente.",
    ),
    destroy=extend_schema(
        tags=["Empleados"],
        summary="Eliminar empleado",
        description="Elimina un empleado del sistema.",
    ),
)
class EmpleadoViewSet(viewsets.ModelViewSet):
    """ViewSet for Empleado management."""

    queryset = Empleado.objects.prefetch_related(
        "datos_laborales__area",
        "datos_laborales__jefe_directo",
        "familiares",
        "formacion_academica",
        "historial_ubicaciones__area_origen",
        "historial_ubicaciones__area_destino",
    ).all()
    permission_classes = [EmpleadoPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmpleadoFilter
    search_fields = [
        "nombres_empleado",
        "apellido_paterno",
        "apellido_materno",
        "numero_documento",
    ]
    ordering_fields = [
        "nombres_empleado",
        "apellido_paterno",
        "fecha_nacimiento",
        "estado_empleado",
    ]
    ordering = ["apellido_paterno", "apellido_materno", "nombres_empleado"]

    def get_permissions(self):
        """Allow authenticated employees to PATCH their own personal data."""
        if self.action == "partial_update":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @cache_response(timeout=300, key_prefix="empleados")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar empleados - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=600, key_prefix="empleado_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener empleado específico - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache(["view_cache:empleados:*", "view_cache:empleado_detail:*"])
    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear empleado - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @invalidate_cache(["view_cache:empleados:*", "view_cache:empleado_detail:*"])
    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar empleado - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:empleados:*", "view_cache:empleado_detail:*"])
    def partial_update(self, request, *args, **kwargs):
        """Actualizar empleado parcialmente.

        RRHH puede actualizar cualquier campo.
        Empleados solo pueden actualizar sus propios datos personales/bancarios/previsionales.
        """
        instance = self.get_object()
        user = request.user

        _SELF_EDITABLE_FIELDS = {
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "numero_documento",
            "correo_personal",
            "telefono_celular",
            "telefono_fijo",
            "direccion_domicilio",
            "fecha_nacimiento",
            "genero_empleado",
            "estado_civil",
            "numero_ruc",
            "distrito_domicilio",
            "provincia_domicilio",
            "departamento_domicilio",
            "entidad_bancaria",
            "numero_cuenta_bancaria",
            "numero_cci",
            "sistema_pensiones",
            "tipo_comision",
            "codigo_cuspp",
            "tipo_sangre",
            "talla_empleado",
            "peso_empleado",
        }

        is_own = hasattr(user, "empleado") and user.empleado == instance
        requested_fields = set(request.data.keys())
        is_safe_self_update = is_own and requested_fields.issubset(
            _SELF_EDITABLE_FIELDS
        )

        if not is_safe_self_update:
            can_write = (
                getattr(user, "is_superuser", False)
                or getattr(user, "es_administrador", False)
                or getattr(user, "es_rrhh", False)
                or getattr(user, "es_admin_rrhh", False)
            )
            if not can_write:
                return APIResponse.error(
                    message="No tiene permisos para actualizar este empleado",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        # Bypass self.update() which has @require_hr() — execute serializer directly
        from rest_framework.response import Response as DRFResponse

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return DRFResponse(serializer.data)

    @invalidate_cache(["view_cache:empleados:*", "view_cache:empleado_detail:*"])
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar empleado - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return EmpleadoListSerializer
        elif self.action == "create":
            return EmpleadoCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return EmpleadoUpdateSerializer
        return EmpleadoSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions and parameters."""
        queryset = super().get_queryset()

        # Soft delete: Filter out inactive employees by default
        incluir_inactivos = (
            self.request.query_params.get("incluir_inactivos", "false").lower()
            == "true"
        )
        if not incluir_inactivos:
            queryset = queryset.filter(estado_empleado="activo")

        # Filter by status
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado_empleado=estado)

        # Filter by area
        area_id = self.request.query_params.get("area")
        if area_id:
            queryset = queryset.filter(
                historial_ubicaciones__area_destino__area_id=area_id,
                historial_ubicaciones__estado_ubicacion="activo",
            )

        # Filter by age range
        edad_min = self.request.query_params.get("edad_min")
        edad_max = self.request.query_params.get("edad_max")
        if edad_min or edad_max:
            today = timezone.now().date()
            if edad_max:
                fecha_min = today - timedelta(days=int(edad_max) * 365)
                queryset = queryset.filter(fecha_nacimiento__gte=fecha_min)
            if edad_min:
                fecha_max = today - timedelta(days=int(edad_min) * 365)
                queryset = queryset.filter(fecha_nacimiento__lte=fecha_max)

        return queryset

    def perform_create(self, serializer):
        """Create employee with logging."""
        empleado = serializer.save()
        logger.info(
            f"Empleado creado: {empleado.nombre_completo}",
            extra={
                "user_id": self.request.user.usuario_id,
                "empleado_id": empleado.empleado_id,
                "action": "create_empleado",
            },
        )

    def perform_update(self, serializer):
        """Update employee with logging."""
        empleado = serializer.save()
        logger.info(
            f"Empleado actualizado: {empleado.nombre_completo}",
            extra={
                "user_id": self.request.user.usuario_id,
                "empleado_id": empleado.empleado_id,
                "action": "update_empleado",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete employee by changing status to inactive."""
        instance.estado_empleado = "inactivo"
        instance.save()
        logger.info(
            f"Empleado desactivado: {instance.nombre_completo}",
            extra={
                "user_id": self.request.user.id,
                "empleado_id": instance.empleado_id,
                "action": "soft_delete_empleado",
            },
        )

    @action(detail=True, methods=["get"])
    @require_permissions(["ver_empleados"])
    def datos_completos(self, request, pk=None):
        """Get complete employee data including family and academic info."""
        try:
            empleado = self.get_object()
            complete_data = services.EmpleadoService.get_complete_employee_data(
                empleado.empleado_id
            )

            return APIResponse.success(
                data=complete_data,
                message="Datos completos del empleado obtenidos exitosamente",
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo datos completos: {str(e)}",
                extra={
                    "user_id": request.user.usuario_id,
                    "empleado_id": pk,
                    "error": str(e),
                },
            )
            return APIResponse.error(
                message="Error al obtener datos completos",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    @require_hr()
    def transferir(self, request, pk=None):
        """Transfer employee to another area."""
        try:
            empleado = self.get_object()
            area_destino_id = request.data.get("area_destino")
            fecha_inicio = request.data.get("fecha_inicio", timezone.now().date())

            if not area_destino_id:
                return APIResponse.error(
                    message="Debe especificar el área de destino",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Use service to handle transfer
            services.EmpleadoService.transferir_empleado(
                empleado.empleado_id, area_destino_id, fecha_inicio
            )

            logger.info(
                f"Empleado transferido: {empleado.nombre_completo}",
                extra={
                    "user_id": request.user.usuario_id,
                    "empleado_id": empleado.empleado_id,
                    "area_destino_id": area_destino_id,
                    "action": "transfer_empleado",
                },
            )

            return APIResponse.success(
                message=f"Empleado {empleado.nombre_completo} transferido exitosamente"
            )

        except BusinessLogicError as e:
            return APIResponse.error(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error transfiriendo empleado: {str(e)}",
                extra={
                    "user_id": request.user.usuario_id,
                    "empleado_id": pk,
                    "error": str(e),
                },
            )
            return APIResponse.error(
                message="Error al transferir empleado",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Historial de ubicaciones removido - usar HistorialUbicaciones model

    @action(detail=False, methods=["get"])
    @require_hr()
    def estadisticas(self, request):
        """Get employee statistics."""
        try:
            stats = services.EmpleadoService.get_employee_statistics()
            return APIResponse.success(
                data=stats, message="Estadísticas de empleados obtenidas exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas de empleados: {str(e)}",
                extra={"user_id": request.user.usuario_id, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener estadísticas",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    @require_permissions(["ver_empleados"])
    def activos(self, request):
        """Get only active employees."""
        queryset = self.get_queryset().filter(estado_empleado="activo")

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmpleadoListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EmpleadoListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Empleados activos")

    @action(detail=True, methods=["get"])
    @require_authenticated()
    def reporte_integral(self, request, pk=None):
        """Genera y devuelve el reporte integral del empleado en PDF."""
        from app_rrhh.services.empleado_report_service import EmpleadoReportService

        try:
            service = EmpleadoReportService()
            pdf_content, nombre_archivo = service.generar_reporte_integral(pk)
            return service.crear_http_response(pdf_content, nombre_archivo)
        except Empleado.DoesNotExist:
            return APIResponse.error(message="Empleado no encontrado", status_code=404)
        except Exception as e:
            logger.error(f"Error generando reporte integral: {e}")
            return APIResponse.error(
                message="Error al generar el reporte", status_code=500
            )

    @action(detail=True, methods=["get"])
    @require_authenticated()
    def reporte_seccion(self, request, pk=None):
        """Genera un reporte PDF de una seccion del empleado."""
        from app_rrhh.services.empleado_report_service import EmpleadoReportService

        seccion = request.query_params.get("seccion", "todos")
        if seccion not in ["todos", "personal", "laboral", "academico", "familiar"]:
            return APIResponse.error(message="Seccion no valida", status_code=400)
        try:
            service = EmpleadoReportService()
            pdf_content, nombre_archivo = service.generar_reporte_seccion(pk, seccion)
            return service.crear_http_response(pdf_content, nombre_archivo)
        except Empleado.DoesNotExist:
            return APIResponse.error(message="Empleado no encontrado", status_code=404)
        except Exception as e:
            logger.error(f"Error generando reporte seccion: {e}")
            return APIResponse.error(
                message="Error al generar el reporte", status_code=500
            )


class DatosFamiliaresViewSet(viewsets.ModelViewSet):
    """ViewSet for DatosFamiliares management. Employees can manage their own records."""

    queryset = DatosFamiliares.objects.select_related("empleado")
    serializer_class = DatosFamiliaresSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "nombres_familiar",
        "apellido_paterno",
        "apellido_materno",
    ]
    ordering_fields = ["nombres_familiar", "fecha_nacimiento", "parentesco"]
    ordering = ["parentesco", "nombres_familiar"]

    def get_permissions(self):
        if self.action in (
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter by employee — employees see only their own records."""
        queryset = super().get_queryset()
        user = self.request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if user.empleado:
                queryset = queryset.filter(empleado=user.empleado)
            else:
                queryset = queryset.none()
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Crear datos familiares — empleado solo puede crear para su propio legajo."""
        empleado_id = request.data.get("empleado")
        user = request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if not user.empleado or user.empleado.empleado_id != int(empleado_id or 0):
                return APIResponse.error(
                    message="Solo puede registrar familiares para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Actualizar datos familiares — empleado puede editar los suyos; RRHH/admin edita cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede actualizar familiares de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Actualizar datos familiares parcialmente — empleado puede editar los suyos; RRHH/admin edita cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede actualizar familiares de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Eliminar datos familiares — empleado puede eliminar los suyos; RRHH/admin elimina cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede eliminar familiares de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class DatosAcademicosViewSet(viewsets.ModelViewSet):
    """ViewSet for DatosAcademicos management. Employees can manage their own records."""

    queryset = DatosAcademicos.objects.select_related("empleado")
    serializer_class = DatosAcademicosSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["nivel_educativo", "nombre_institucion", "nombre_carrera"]
    ordering_fields = [
        "fecha_inicio_estudios",
        "fecha_termino_estudios",
        "tipo_formacion",
    ]
    ordering = ["-fecha_inicio_estudios"]

    def get_permissions(self):
        if self.action in (
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        """Filter by employee — employees see only their own records."""
        queryset = super().get_queryset()
        user = self.request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if user.empleado:
                queryset = queryset.filter(empleado=user.empleado)
            else:
                queryset = queryset.none()
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Crear datos académicos — empleado solo puede crear para su propio legajo."""
        empleado_id = request.data.get("empleado")
        user = request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if not user.empleado or user.empleado.empleado_id != int(empleado_id or 0):
                return APIResponse.error(
                    message="Solo puede registrar datos academicos para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Actualizar datos académicos — empleado puede editar los suyos; RRHH/admin edita cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede actualizar datos academicos de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Actualizar datos académicos parcialmente — empleado puede editar los suyos; RRHH/admin edita cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede actualizar datos academicos de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Eliminar datos académicos — empleado puede eliminar los suyos; RRHH/admin elimina cualquiera."""
        instance = self.get_object()
        user = request.user
        is_own = hasattr(user, "empleado") and instance.empleado == user.empleado
        if not is_own and not (
            user.es_administrador or user.es_rrhh or user.es_admin_rrhh
        ):
            return APIResponse.error(
                message="Solo puede eliminar datos academicos de su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CursosCertificacionesViewSet(viewsets.ModelViewSet):
    """CRUD for employee courses and certifications. Employees manage own records."""

    from app_rrhh.models import CursosCertificaciones as _CursosCertificaciones

    queryset = _CursosCertificaciones.objects.select_related(
        "empleado", "documento"
    ).all()
    permission_classes = [RRHHPermission]

    def get_serializer_class(self):
        from .serializers import CursosCertificacionesSerializer

        return CursosCertificacionesSerializer

    def get_permissions(self):
        if self.action in (
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        from app_rrhh.models import CursosCertificaciones

        queryset = CursosCertificaciones.objects.select_related(
            "empleado", "documento"
        ).all()
        user = self.request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if user.empleado:
                queryset = queryset.filter(empleado=user.empleado)
            else:
                queryset = queryset.none()
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return queryset

    def create(self, request, *args, **kwargs):
        """Employee can only create curso records for their own legajo."""
        empleado_id = request.data.get("empleado")
        user = request.user
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if not user.empleado or user.empleado.empleado_id != int(empleado_id or 0):
                return APIResponse.error(
                    message="Solo puede registrar cursos para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)


class DatosLaboralesViewSet(viewsets.ModelViewSet):
    """ViewSet for DatosLaborales management with optimized queries."""

    queryset = DatosLaborales.objects.select_related(
        "empleado",
        "area",
        "jefe_directo",
    ).all()

    queryset = DatosLaborales.objects.select_related("empleado")
    serializer_class = DatosLaboralesSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DatosLaboralesFilter
    search_fields = ["puesto_trabajo", "categoria_laboral", "regimen_laboral"]
    ordering_fields = ["fecha_ingreso", "fecha_cese", "remuneracion_mensual"]
    ordering = ["-fecha_ingreso"]

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar datos laborales - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener datos laborales específicos - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear datos laborales - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar datos laborales - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar datos laborales parcialmente - requiere rol RRHH."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar datos laborales - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filter by employee if specified."""
        queryset = super().get_queryset()
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return queryset

    @action(detail=False, methods=["get"])
    @require_hr()
    def estadisticas_remuneracion(self, request):
        """Get salary statistics."""
        try:
            queryset = self.get_queryset().filter(estado_laboral="activo")
            stats = queryset.aggregate(
                promedio=Avg("remuneracion_mensual"),
                total_empleados=Count("dato_laboral_id"),
            )

            # Group by salary ranges
            rangos = {
                "menos_1000": queryset.filter(remuneracion_mensual__lt=1000).count(),
                "entre_1000_2000": queryset.filter(
                    remuneracion_mensual__gte=1000, remuneracion_mensual__lt=2000
                ).count(),
                "entre_2000_3000": queryset.filter(
                    remuneracion_mensual__gte=2000, remuneracion_mensual__lt=3000
                ).count(),
                "mas_3000": queryset.filter(remuneracion_mensual__gte=3000).count(),
            }

            stats["rangos_salariales"] = rangos

            return APIResponse.success(
                data=stats, message="Estadísticas de remuneración"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas de remuneración: {str(e)}",
                extra={"user_id": request.user.usuario_id, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener estadísticas",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConfiguracionRemuneracionViewSet(viewsets.ModelViewSet):
    """ViewSet para catálogo maestro de conceptos de remuneración."""

    queryset = ConfiguracionRemuneracion.objects.all()
    serializer_class = ConfiguracionRemuneracionSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["codigo", "nombre", "descripcion"]
    ordering_fields = ["tipo", "orden", "nombre", "estado"]
    ordering = ["tipo", "orden", "nombre"]

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar conceptos de remuneración - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener concepto específico - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear concepto de remuneración - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar concepto de remuneración - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar parcialmente - requiere rol RRHH."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar concepto - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        tipo = self.request.query_params.get("tipo")
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class ConfiguracionAfpViewSet(viewsets.ModelViewSet):
    """ViewSet para parámetros AFP de planilla."""

    queryset = ConfiguracionAfp.objects.all()
    serializer_class = ConfiguracionAfpSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["afp_nombre", "vigencia_mes"]
    ordering_fields = ["vigencia_mes", "afp_nombre", "estado"]
    ordering = ["-vigencia_mes", "afp_nombre"]

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

    def get_queryset(self):
        queryset = super().get_queryset()

        afp_nombre = self.request.query_params.get("afp_nombre")
        if afp_nombre:
            queryset = queryset.filter(afp_nombre__icontains=afp_nombre)

        vigencia_mes = self.request.query_params.get("vigencia_mes")
        if vigencia_mes:
            queryset = queryset.filter(vigencia_mes=vigencia_mes)

        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


# RegUbicacionViewSet removido - usar HistorialUbicaciones model


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet for Usuario management."""

    queryset = Usuario.objects.select_related("empleado")
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
    ordering_fields = ["nombres_usuario", "fecha_creacion", "ultimo_acceso"]
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
            f"Usuario creado: {usuario.nombres_usuario}",
            extra={
                "user_id": self.request.user.usuario_id,
                "new_user_id": usuario.usuario_id,
                "action": "create_usuario",
            },
        )

    def perform_update(self, serializer):
        """Update user with logging."""
        usuario = serializer.save()
        logger.info(
            f"Usuario actualizado: {usuario.nombres_usuario}",
            extra={
                "user_id": self.request.user.usuario_id,
                "updated_user_id": usuario.usuario_id,
                "action": "update_usuario",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete user by changing status to inactive."""
        instance.estado_usuario = "inactivo"
        instance.save()
        logger.info(
            f"Usuario desactivado: {instance.nombres_usuario}",
            extra={
                "user_id": self.request.user.usuario_id,
                "deactivated_user_id": instance.usuario_id,
                "action": "soft_delete_usuario",
            },
        )

    @action(detail=False, methods=["get"])
    @require_admin()
    def sin_login_reciente(self, request):
        """Get users without recent login."""
        try:
            dias = int(request.query_params.get("dias", 30))
            usuarios = services.UsuarioService.usuarios_sin_login_reciente(dias)

            serializer = self.get_serializer(usuarios, many=True)
            return APIResponse.success(
                data=serializer.data,
                message=f"Usuarios sin login en los últimos {dias} días",
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo usuarios sin login reciente: {str(e)}",
                extra={"user_id": request.user.usuario_id, "error": str(e)},
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
            roles_asignados = UsuarioRoles.objects.activos().por_usuario(usuario)

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
                    asignacion_existente = UsuarioRoles.objects.filter(
                        usuario=usuario, rol_id=rol_id, estado_asignacion="activo"
                    ).first()

                    if asignacion_existente:
                        errores.append(
                            f"El usuario ya tiene asignado el rol con ID {rol_id}"
                        )
                        continue

                    # Crear nueva asignación
                    try:
                        usuario_rol = UsuarioRoles.objects.create(
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
            rol_id = request.data.get("rol_id")

            if not rol_id:
                return APIResponse.error(
                    message="ID del rol es requerido",
                    errors={"rol_id": ["Este campo es requerido"]},
                )

            # Buscar asignación activa
            asignacion = UsuarioRoles.objects.filter(
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

            return APIResponse.success(message="Rol removido exitosamente del usuario")
        except Exception as e:
            return APIResponse.error(
                message="Error al remover rol del usuario", errors={"detail": str(e)}
            )


class RolViewSet(viewsets.ModelViewSet):
    """ViewSet for Rol management."""

    queryset = Rol.objects.prefetch_related(
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
            f"Rol desactivado: {instance.nombre_rol}",
            extra={
                "user_id": self.request.user.usuario_id,
                "rol_id": instance.rol_id,
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
    """ViewSet for Permiso management."""

    queryset = Permiso.objects.all()
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
                f"Permiso {instance.permiso_id} soft deleted by changing estado_permiso to 'inactivo'"
            )
        except Exception as e:
            logger.error(
                f"Error performing soft delete on Permiso {instance.permiso_id}: {str(e)}"
            )
            raise BusinessLogicError(f"Error al desactivar el permiso: {str(e)}")


# RegPermisosViewSet removido - modelo legacy eliminado


@extend_schema_view(
    list=extend_schema(
        tags=["Documentos Digitales"],
        summary="Listar documentos digitales",
        description="Obtiene una lista paginada de todos los documentos digitales con filtros opcionales.",
    ),
    create=extend_schema(
        tags=["Documentos Digitales"],
        summary="Crear documento digital",
        description="Crea un nuevo documento digital en el sistema.",
    ),
    retrieve=extend_schema(
        tags=["Documentos Digitales"],
        summary="Obtener documento digital",
        description="Obtiene los detalles de un documento digital específico por su ID.",
    ),
    update=extend_schema(
        tags=["Documentos Digitales"],
        summary="Actualizar documento digital",
        description="Actualiza completamente un documento digital existente.",
    ),
    partial_update=extend_schema(
        tags=["Documentos Digitales"],
        summary="Actualizar documento digital parcialmente",
        description="Actualiza parcialmente un documento digital existente.",
    ),
    destroy=extend_schema(
        tags=["Documentos Digitales"],
        summary="Eliminar documento digital",
        description="Elimina un documento digital del sistema.",
    ),
)
class DocumentosDigitalesViewSet(viewsets.ModelViewSet):
    """ViewSet for DocumentosDigitales management."""

    queryset = DocumentosDigitales.objects.select_related(
        "empleado", "subido_por", "validado_por"
    )
    permission_classes = [DocumentosDigitalesPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "nombre_documento",
        "descripcion",
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
    ]
    ordering_fields = [
        "fecha_subida",
        "fecha_emision",
        "fecha_vencimiento",
        "tipo_documento",
    ]
    ordering = ["-fecha_subida"]

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar documentos digitales - requiere autenticación."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener documento digital específico - requiere autenticación."""
        return super().retrieve(request, *args, **kwargs)

    @require_authenticated()
    def create(self, request, *args, **kwargs):
        """Crear documento digital - autenticado (empleados solo para su propio legajo)."""
        empleado_id = request.data.get("empleado")
        user = request.user
        # Non-HR users can only upload for themselves
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if not user.empleado or user.empleado.empleado_id != int(empleado_id):
                return APIResponse.error(
                    message="Solo puede subir documentos para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set subido_por, file metadata, and default estado for employee uploads."""
        user = self.request.user
        extra = {"subido_por": user}
        # If non-HR user uploads, set as pending review
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            extra["estado_documento"] = "pendiente_revision"
        # Extract file metadata from uploaded file
        archivo = serializer.validated_data.get("archivo")
        if archivo:
            extra["nombre_archivo_original"] = archivo.name
            extra["formato_archivo"] = (
                os.path.splitext(archivo.name)[1].lower().replace(".", "")
            )
            extra["tamano_archivo"] = archivo.size
        serializer.save(**extra)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar documento digital - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        """Actualizar documento digital parcialmente - requiere rol RRHH."""
        return super().partial_update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar documento digital - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return DocumentosDigitalesCreateSerializer
        return DocumentosDigitalesSerializer

    def get_queryset(self):
        """Filter documents based on query parameters."""
        queryset = super().get_queryset()
        user = self.request.user

        # Non-HR users can only see their own documents
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if hasattr(user, "empleado") and user.empleado:
                queryset = queryset.filter(empleado=user.empleado)
            else:
                return queryset.none()

        # Filter by employee
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)

        # Filter by document type
        tipo_documento = self.request.query_params.get("tipo_documento")
        if tipo_documento:
            queryset = queryset.filter(tipo_documento=tipo_documento)

        # Filter by category
        categoria = self.request.query_params.get("categoria")
        if categoria:
            queryset = queryset.filter(categoria=categoria)

        # Filter by status
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado_documento=estado)

        # Filter by active status
        activos = self.request.query_params.get("activos")
        if activos == "true":
            queryset = queryset.filter(estado_documento="activo")

        # Filter by origin: institutional documents (generated by the entity)
        TIPOS_INSTITUCIONALES = [
            "boleta_pago",
            "contrato_trabajo",
            "adenda_contrato",
            "constancia_trabajo",
            "constancia_participacion",
            "constancia_haberes",
            "resolucion_encargatura",
            "resolucion_licencia",
            "resolucion_sancion",
            "memorandum",
            "carta_amonestacion",
            "carta_cese",
            "evaluacion_desempeno",
        ]
        origen = self.request.query_params.get("origen")
        if origen == "institucional":
            queryset = queryset.filter(tipo_documento__in=TIPOS_INSTITUCIONALES)
        elif origen == "personal":
            queryset = queryset.exclude(tipo_documento__in=TIPOS_INSTITUCIONALES)

        # Filter by version status
        es_version_actual = self.request.query_params.get("es_version_actual")
        if es_version_actual == "true":
            queryset = queryset.filter(es_version_actual=True)
        elif es_version_actual == "false":
            queryset = queryset.filter(es_version_actual=False)

        return queryset

    @action(detail=False, methods=["get"])
    @require_hr()
    def por_tipo(self, request):
        """Get documents grouped by type."""
        tipo = request.query_params.get("tipo")
        if not tipo:
            return APIResponse.error(
                message="El parámetro 'tipo' es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(tipo_documento=tipo)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message=f"Documentos de tipo {tipo}"
        )

    @action(detail=False, methods=["get"])
    @require_permissions(["ver_boletas_pago"])
    def boletas_pago(self, request):
        """Get pay slips (boletas de pago) - replaces old Boleta endpoint."""
        queryset = self.get_queryset().filter(tipo_documento="boleta_pago")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Boletas de pago")

    @action(detail=False, methods=["get"])
    @require_hr()
    def proximos_vencer(self, request):
        """Get documents that will expire soon."""
        dias = int(request.query_params.get("dias", 30))
        fecha_limite = timezone.now().date() + timedelta(days=dias)

        queryset = self.get_queryset().filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
            estado_documento="activo",
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(
            data=serializer.data, message=f"Documentos que vencen en {dias} días"
        )

    @action(detail=True, methods=["post"])
    @require_hr()
    def validar(self, request, pk=None):
        """Validar un documento - requiere rol RRHH."""
        documento = self.get_object()
        observaciones = request.data.get("observaciones", "")
        documento.validar_documento(request.user, observaciones)
        serializer = self.get_serializer(documento)
        return APIResponse.success(
            data=serializer.data, message="Documento validado exitosamente"
        )

    @action(detail=True, methods=["post"])
    @require_hr()
    def rechazar(self, request, pk=None):
        """Rechazar un documento - requiere rol RRHH."""
        documento = self.get_object()
        motivo = request.data.get("motivo", "")
        if not motivo:
            return APIResponse.error(
                message="El motivo de rechazo es requerido",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        documento.rechazar_documento(request.user, motivo)
        serializer = self.get_serializer(documento)
        return APIResponse.success(data=serializer.data, message="Documento rechazado")

    @action(detail=False, methods=["post"])
    @require_hr()
    def subir_institucional(self, request):
        """Subir documento institucional al legajo de un empleado.

        Permite a RRHH subir boletas, constancias, resoluciones, etc.
        Acepta un archivo o multiples archivos para subida masiva.
        """
        empleado_id = request.data.get("empleado")
        tipo_documento = request.data.get("tipo_documento")
        nombre_documento = request.data.get("nombre_documento", "")
        descripcion = request.data.get("descripcion", "")
        fecha_emision = request.data.get("fecha_emision")
        periodo = request.data.get("periodo", "")  # e.g. "2026-01" para boletas

        if not empleado_id or not tipo_documento:
            return APIResponse.error(
                message="empleado y tipo_documento son requeridos",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Determinar categoria automaticamente segun tipo
        TIPO_CATEGORIA_MAP = {
            "boleta_pago": "remuneraciones",
            "constancia_trabajo": "laboral",
            "constancia_participacion": "laboral",
            "constancia_haberes": "remuneraciones",
            "resolucion_encargatura": "administrativo",
            "resolucion_licencia": "administrativo",
            "resolucion_sancion": "administrativo",
            "contrato_trabajo": "laboral",
            "adenda_contrato": "laboral",
            "memorandum": "administrativo",
            "carta_amonestacion": "administrativo",
            "carta_cese": "administrativo",
            "evaluacion_desempeno": "evaluacion",
        }
        categoria = TIPO_CATEGORIA_MAP.get(tipo_documento, "administrativo")

        archivos = request.FILES.getlist("archivos") or []
        archivo_unico = request.FILES.get("archivo")
        if archivo_unico and not archivos:
            archivos = [archivo_unico]

        if not archivos:
            return APIResponse.error(
                message="Se requiere al menos un archivo",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        documentos_creados = []
        for i, archivo in enumerate(archivos):
            nombre = nombre_documento or archivo.name
            if len(archivos) > 1 and periodo:
                nombre = (
                    f"{nombre} - {periodo}"
                    if i == 0
                    else f"{nombre} ({i+1}) - {periodo}"
                )

            doc = DocumentosDigitales.objects.create(
                empleado_id=empleado_id,
                tipo_documento=tipo_documento,
                categoria=categoria,
                nombre_documento=nombre,
                descripcion=(
                    descripcion or f"{nombre} - {periodo}" if periodo else descripcion
                ),
                archivo=archivo,
                nombre_archivo_original=archivo.name,
                formato_archivo=os.path.splitext(archivo.name)[1]
                .lower()
                .replace(".", ""),
                tamano_archivo=archivo.size,
                fecha_emision=fecha_emision,
                estado_documento="activo",
                nivel_acceso="restringido",
                subido_por=request.user,
                es_documento_oficial=True,
            )
            documentos_creados.append(doc)

        serializer = self.get_serializer(documentos_creados, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f"{len(documentos_creados)} documento(s) subido(s) exitosamente",
            status_code=status.HTTP_201_CREATED,
        )


# ==========================================
# OnboardingViewSet
# ==========================================


@extend_schema_view(
    list=extend_schema(
        tags=["Onboarding"],
        summary="Listar onboardings",
        description="Obtiene la lista de procesos de onboarding.",
    ),
    create=extend_schema(
        tags=["Onboarding"],
        summary="Iniciar onboarding",
        description="Inicia un nuevo proceso de onboarding para un empleado.",
    ),
    retrieve=extend_schema(
        tags=["Onboarding"],
        summary="Detalle de onboarding",
        description="Obtiene el detalle de un proceso de onboarding.",
    ),
)
class OnboardingViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar el proceso de onboarding de nuevos empleados."""

    queryset = OnboardingEmpleado.objects.select_related(
        "empleado", "usuario", "validado_por"
    )
    serializer_class = OnboardingEmpleadoSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
        "empleado__numero_documento",
    ]
    ordering_fields = ["fecha_inicio", "estado_onboarding", "fecha_completado"]
    ordering = ["-fecha_inicio"]

    def get_permissions(self):
        """Allow authenticated employees to use upload actions."""
        if self.action in (
            "subir_foto",
            "subir_documento",
            "mi_onboarding",
            "retrieve",
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return OnboardingIniciarSerializer
        if self.action in ["validar", "rechazar"]:
            return OnboardingValidacionSerializer
        return OnboardingEmpleadoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado_onboarding=estado)
        return queryset

    @require_hr()
    def list(self, request, *args, **kwargs):
        """Listar onboardings - requiere rol RRHH."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Iniciar onboarding - requiere rol RRHH."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        onboarding = result["onboarding"]
        response_serializer = OnboardingEmpleadoSerializer(onboarding)

        return APIResponse.success(
            data={
                **response_serializer.data,
                "username": result["usuario"].username,
                "email_enviado": result["email_enviado"],
            },
            message=f"Onboarding iniciado para {result['empleado'].nombre_completo}",
            status_code=status.HTTP_201_CREATED,
        )

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de onboarding - empleado solo ve el suyo."""
        from app_rrhh.services.onboarding_service import OnboardingService

        onboarding = self.get_object()
        user = request.user
        # Non-HR users can only see their own onboarding
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if onboarding.usuario_id != user.usuario_id:
                return APIResponse.error(
                    message="No tiene permisos para ver este onboarding",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        # Recalcular estado si no está completado
        if onboarding.estado_onboarding != "completado":
            resultado = OnboardingService.actualizar_estado_onboarding(
                onboarding.empleado_id
            )
            onboarding = (
                resultado["onboarding"] if isinstance(resultado, dict) else resultado
            ) or onboarding
        serializer = self.get_serializer(onboarding)
        return APIResponse.success(data=serializer.data)

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def mi_onboarding(self, request):
        """Obtener el onboarding del usuario actual, recalculando el estado al momento."""
        from app_rrhh.services.onboarding_service import OnboardingService

        try:
            onboarding = OnboardingEmpleado.objects.select_related(
                "empleado", "usuario", "validado_por"
            ).get(usuario=request.user)
            # Recalcular estado en cada consulta para reflejar datos actualizados
            if onboarding.estado_onboarding != "completado":
                resultado = OnboardingService.actualizar_estado_onboarding(
                    onboarding.empleado_id
                )
                onboarding = (
                    resultado["onboarding"]
                    if isinstance(resultado, dict)
                    else resultado
                ) or onboarding
            serializer = self.get_serializer(onboarding)
            return APIResponse.success(data=serializer.data)
        except OnboardingEmpleado.DoesNotExist:
            return APIResponse.error(
                message="No tiene un proceso de onboarding activo",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"])
    @require_hr()
    def validar(self, request, pk=None):
        """Validar el onboarding y aprobar todos los documentos."""
        from app_rrhh.services.onboarding_service import (
            OnboardingNotificationService,
            OnboardingService,
        )

        serializer = OnboardingValidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accion = serializer.validated_data["accion"]
        observaciones = serializer.validated_data.get("observaciones", "")

        onboarding = self.get_object()

        if accion == "aprobar":
            result = OnboardingService.validar_onboarding(
                onboarding.onboarding_id, request.user, observaciones
            )
            if not result:
                return APIResponse.error(
                    message="Onboarding no encontrado", status_code=404
                )
            try:
                OnboardingNotificationService.notificar_onboarding_aprobado(result)
            except Exception:
                pass
            response_serializer = OnboardingEmpleadoSerializer(result)
            return APIResponse.success(
                data=response_serializer.data,
                message="Onboarding validado y completado exitosamente",
            )
        else:
            onboarding.marcar_observado(observaciones)
            try:
                OnboardingNotificationService.notificar_onboarding_observado(
                    onboarding, observaciones
                )
            except Exception:
                pass
            response_serializer = OnboardingEmpleadoSerializer(onboarding)
            return APIResponse.success(
                data=response_serializer.data,
                message="Onboarding observado - se requieren correcciones",
            )

    @action(
        detail=True, methods=["post"], url_path=r"documentos/(?P<doc_id>[^/.]+)/aprobar"
    )
    @require_hr()
    def aprobar_documento(self, request, pk=None, doc_id=None):
        """RRHH approves a specific document from the onboarding legajo."""
        from app_rrhh.services.onboarding_service import OnboardingService

        onboarding = self.get_object()
        try:
            doc = DocumentosDigitales.objects.get(
                documento_id=doc_id,
                empleado=onboarding.empleado,
                es_version_actual=True,
            )
        except DocumentosDigitales.DoesNotExist:
            return APIResponse.error(
                message="Documento no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        doc.validar_documento(request.user)
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message=f"Documento '{doc.nombre_documento}' aprobado",
            data={
                "documento_id": doc.documento_id,
                "estado_documento": doc.estado_documento,
            },
        )

    @action(
        detail=True,
        methods=["post"],
        url_path=r"documentos/(?P<doc_id>[^/.]+)/rechazar",
    )
    @require_hr()
    def rechazar_documento(self, request, pk=None, doc_id=None):
        """RRHH rejects a specific document with a mandatory motivo."""
        from app_rrhh.services.onboarding_service import (
            OnboardingNotificationService,
            OnboardingService,
        )

        motivo = request.data.get("motivo", "").strip()
        if not motivo:
            return APIResponse.error(
                message="El campo motivo es requerido para rechazar un documento"
            )
        onboarding = self.get_object()
        try:
            doc = DocumentosDigitales.objects.get(
                documento_id=doc_id,
                empleado=onboarding.empleado,
                es_version_actual=True,
            )
        except DocumentosDigitales.DoesNotExist:
            return APIResponse.error(
                message="Documento no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        doc.rechazar_documento(request.user, motivo)
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        try:
            OnboardingNotificationService.notificar_documento_rechazado(
                onboarding, doc, motivo
            )
        except Exception:
            pass
        return APIResponse.success(
            message=f"Documento '{doc.nombre_documento}' rechazado",
            data={
                "documento_id": doc.documento_id,
                "estado_documento": doc.estado_documento,
            },
        )

    @action(detail=True, methods=["post"])
    @require_hr()
    def reenviar_email(self, request, pk=None):
        """Reenviar email de bienvenida."""
        from app_rrhh.services.onboarding_service import OnboardingService

        onboarding = self.get_object()
        result = OnboardingService.reenviar_email_bienvenida(onboarding.onboarding_id)

        if not result:
            return APIResponse.error(
                message="Onboarding no encontrado", status_code=404
            )

        if result["email_enviado"]:
            return APIResponse.success(
                message="Email de bienvenida reenviado exitosamente"
            )
        else:
            return APIResponse.error(
                message="Error al reenviar el email", status_code=500
            )

    @action(detail=True, methods=["post"], url_path="corregir-correo")
    @require_hr()
    def corregir_correo(self, request, pk=None):
        """Actualiza el correo del empleado y reenvía el email de bienvenida."""
        from app_rrhh.services.onboarding_service import OnboardingService

        nuevo_correo = request.data.get("correo_personal", "").strip()
        if not nuevo_correo:
            return APIResponse.error(message="correo_personal es requerido")
        try:
            onboarding = self.get_object()
            onboarding.empleado.correo_personal = nuevo_correo
            onboarding.empleado.save(update_fields=["correo_personal"])
            onboarding.usuario.email = nuevo_correo
            onboarding.usuario.save(update_fields=["email"])
            result = OnboardingService.reenviar_email_bienvenida(
                onboarding.onboarding_id
            )
            if result and result.get("email_enviado"):
                return APIResponse.success(
                    message="Correo actualizado y email de bienvenida reenviado",
                    data={"email_enviado": True, "correo_personal": nuevo_correo},
                )
            return APIResponse.error(
                message="Correo actualizado pero el email no pudo enviarse. Revise la configuración SMTP.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return APIResponse.error(message=str(e))

    @action(detail=True, methods=["post"], url_path="actualizar-estado")
    @require_hr()
    def actualizar_estado(self, request, pk=None):
        """Recalcula el estado del checklist de onboarding basado en documentos y datos actuales."""
        from app_rrhh.services.onboarding_service import OnboardingService

        onboarding = self.get_object()
        resultado = OnboardingService.actualizar_estado_onboarding(
            onboarding.empleado_id
        )
        if not resultado:
            return APIResponse.error(
                message="No se encontró el onboarding", status_code=404
            )
        updated = resultado["onboarding"] if isinstance(resultado, dict) else resultado
        serializer = OnboardingEmpleadoSerializer(updated)
        return APIResponse.success(
            data=serializer.data,
            message="Estado de onboarding actualizado",
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="subir-foto",
        parser_classes=[MultiPartParser],
    )
    @require_authenticated()
    def subir_foto(self, request):
        """El empleado en onboarding sube su foto de perfil (JPG o PNG)."""
        from app_rrhh.services.onboarding_service import OnboardingService

        archivo = request.FILES.get("archivo")
        if not archivo:
            return APIResponse.error(message="Se requiere el archivo de foto")
        if archivo.content_type not in ("image/jpeg", "image/png"):
            return APIResponse.error(message="Solo se permiten imágenes JPG o PNG")
        try:
            onboarding = OnboardingEmpleado.objects.get(usuario=request.user)
        except OnboardingEmpleado.DoesNotExist:
            return APIResponse.error(message="No tiene un proceso de onboarding activo")
        empleado = onboarding.empleado
        # Usar crear_nueva_version si ya existe una foto, o crear nueva
        doc_existente = DocumentosDigitales.objects.filter(
            empleado=empleado,
            tipo_documento="foto",
            es_version_actual=True,
        ).first()
        if doc_existente:
            doc = doc_existente.crear_nueva_version(
                archivo=archivo, usuario=request.user
            )
        else:
            doc = DocumentosDigitales.objects.create(
                empleado=empleado,
                tipo_documento="foto",
                categoria="personal",
                nombre_documento="Foto de perfil",
                archivo=archivo,
                nombre_archivo_original=archivo.name,
                formato_archivo=(
                    archivo.name.rsplit(".", 1)[-1].lower()
                    if "." in archivo.name
                    else ""
                ),
                tamano_archivo=archivo.size,
                estado_documento="pendiente_revision",
                nivel_acceso="restringido",
                subido_por=request.user,
            )
        empleado.ruta_fotografia = doc.archivo.name
        empleado.save(update_fields=["ruta_fotografia"])
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message="Foto subida exitosamente",
            data={
                "documento_id": doc.pk,
                "archivo_url": (
                    request.build_absolute_uri(doc.archivo.url) if doc.archivo else None
                ),
                "estado_documento": doc.estado_documento,
                "fecha_subida": (
                    doc.fecha_subida.isoformat() if doc.fecha_subida else None
                ),
            },
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="subir-documento",
        parser_classes=[MultiPartParser],
    )
    @require_authenticated()
    def subir_documento(self, request):
        """El empleado en onboarding sube un documento PDF a su legajo."""
        from app_rrhh.services.onboarding_service import OnboardingService

        _TIPO_CATEGORIA_MAP = {
            "dni": "personal",
            "carnet_extranjeria": "personal",
            "dni_familiar": "familiar",
            "certificado_nacimiento": "familiar",
            "acta_matrimonio": "familiar",
            "certificado_union_hecho": "familiar",
            "partida_nacimiento": "familiar",
            "certificado_estudios": "academico",
            "titulo_profesional": "academico",
            "diploma": "academico",
            "certificado_capacitacion": "academico",
            "declaracion_jurada": "laboral",
            "cv": "laboral",
            "certificado_trabajo": "laboral",
            "constancia_trabajo": "laboral",
            "carta_recomendacion": "laboral",
        }

        archivo = request.FILES.get("archivo")
        tipo_documento = request.data.get("tipo_documento", "").strip()
        if not archivo:
            return APIResponse.error(message="Se requiere el archivo")
        if archivo.content_type != "application/pdf":
            return APIResponse.error(message="Solo se permiten archivos PDF")
        if tipo_documento not in _TIPO_CATEGORIA_MAP:
            return APIResponse.error(
                message=f"Tipo de documento no válido. Opciones: {', '.join(_TIPO_CATEGORIA_MAP.keys())}"
            )
        try:
            onboarding = OnboardingEmpleado.objects.get(usuario=request.user)
        except OnboardingEmpleado.DoesNotExist:
            return APIResponse.error(message="No tiene un proceso de onboarding activo")
        empleado = onboarding.empleado
        categoria = _TIPO_CATEGORIA_MAP[tipo_documento]
        nombre_documento = request.data.get(
            "nombre_documento", tipo_documento.replace("_", " ").title()
        )
        # Usar crear_nueva_version si ya existe el mismo tipo_documento
        doc_existente = DocumentosDigitales.objects.filter(
            empleado=empleado,
            tipo_documento=tipo_documento,
            es_version_actual=True,
        ).first()
        if doc_existente:
            doc = doc_existente.crear_nueva_version(
                archivo=archivo, usuario=request.user
            )
        else:
            doc = DocumentosDigitales.objects.create(
                empleado=empleado,
                tipo_documento=tipo_documento,
                categoria=categoria,
                nombre_documento=nombre_documento,
                archivo=archivo,
                nombre_archivo_original=archivo.name,
                formato_archivo=(
                    archivo.name.rsplit(".", 1)[-1].lower()
                    if "." in archivo.name
                    else ""
                ),
                tamano_archivo=archivo.size,
                estado_documento="pendiente_revision",
                nivel_acceso="restringido",
                subido_por=request.user,
            )
        # Optional FK linking: attach document to academico/curso record
        # Note: DatosFamiliares does not have a documento FK — familiar_id param is accepted
        # but only used to tag the doc's category context (no DB link on familiar itself)
        familiar_id = request.data.get(
            "familiar_id"
        )  # accepted, reserved for future use

        academico_id = request.data.get("academico_id")
        if academico_id:
            try:
                from app_rrhh.models import DatosAcademicos

                academico = DatosAcademicos.objects.get(
                    academico_id=int(academico_id), empleado=onboarding.empleado
                )
                academico.documento = doc
                academico.save(update_fields=["documento"])
            except (DatosAcademicos.DoesNotExist, ValueError, AttributeError):
                pass

        curso_id = request.data.get("curso_id")
        if curso_id:
            try:
                from app_rrhh.models import CursosCertificaciones

                curso = CursosCertificaciones.objects.get(
                    curso_id=int(curso_id), empleado=onboarding.empleado
                )
                curso.documento = doc
                curso.save(update_fields=["documento"])
            except (CursosCertificaciones.DoesNotExist, ValueError):
                pass

        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message="Documento subido exitosamente",
            data={
                "documento_id": doc.pk,
                "tipo_documento": doc.tipo_documento,
                "estado_documento": doc.estado_documento,
                "fecha_subida": (
                    doc.fecha_subida.isoformat() if doc.fecha_subida else None
                ),
                "nombre_documento": doc.nombre_documento,
                "archivo_url": (
                    request.build_absolute_uri(doc.archivo.url) if doc.archivo else None
                ),
            },
        )


class ConfiguracionEmpresaViewSet(viewsets.ViewSet):
    """ViewSet para gestionar la configuración de la empresa."""

    @require_authenticated()
    def list(self, request):
        """Obtener configuración actual de la empresa."""
        from api.v1.rrhh.serializers import ConfiguracionEmpresaSerializer
        from app_rrhh.models.configuracion_empresa import ConfiguracionEmpresa

        cfg = ConfiguracionEmpresa.get_config()
        serializer = ConfiguracionEmpresaSerializer(cfg, context={"request": request})
        return APIResponse.success(data=serializer.data)

    @require_admin()
    def create(self, request):
        """Actualizar configuración de la empresa (upsert)."""
        from api.v1.rrhh.serializers import ConfiguracionEmpresaSerializer
        from app_rrhh.models.configuracion_empresa import ConfiguracionEmpresa

        cfg = ConfiguracionEmpresa.get_config()
        serializer = ConfiguracionEmpresaSerializer(
            cfg, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data, message="Configuración actualizada"
            )
        return APIResponse.error(message="Datos inválidos", errors=serializer.errors)
