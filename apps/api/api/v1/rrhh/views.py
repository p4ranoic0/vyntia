"""Views for RRHH API v1."""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict

from apps.payroll.models import AfpConfiguration, CompensationConfiguration
from apps.contracts.models import EmploymentData
from apps.documents.models import DigitalDocument
from apps.employees.models import (
    AcademicRecord,
    FamilyMember,
    Employee,
)
from apps.organization.models import Department

# Importar decoradores de permisos y cache
from apps.core.decorators import (
    cache_response,
    invalidate_cache,
    require_admin,
    require_authenticated,
    require_hr,
    require_permissions,
)
from apps.core.exceptions import BusinessLogicError
from apps.core.pagination import StandardResultsSetPagination
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .filters import AreaFilter, DatosLaboralesFilter, EmpleadoFilter
from .permissions import (
    AreaPermission,
    DocumentosDigitalesPermission,
    EmpleadoPermission,
    RRHHPermission,
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
class AreaViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Department management."""

    queryset = Department.objects.select_related("area_padre").prefetch_related(
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

        return self._filter_by_tenant(queryset)

    def perform_create(self, serializer):
        """Create area with logging — tenant injected by TenantAwareViewSetMixin."""
        super().perform_create(serializer)
        area = serializer.instance
        logger.info(
            f"Área creada: {area.siglas_area}",
            extra={
                "user_id": self.request.user.pk,
                "id": area.pk,
                "action": "create_area",
            },
        )

    def perform_update(self, serializer):
        """Update area with logging."""
        area = serializer.save()
        logger.info(
            f"Área actualizada: {area.siglas_area}",
            extra={
                "user_id": self.request.user.pk,
                "id": area.pk,
                "action": "update_area",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete area by changing status to inactive."""
        instance.estado_area = "inactivo"
        instance.save()
        logger.info(
            f"Área desactivada: {instance.siglas_area}",
            extra={
                "user_id": self.request.user.id,
                "id": instance.pk,
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
            empleados = area.empleados_activos()

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
                    "user_id": request.user.pk,
                    "id": pk,
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
            stats = {
                "total_empleados": EmploymentData.objects.filter(
                    area_id=area.pk, estado_datos="activo"
                ).values("empleado").distinct().count(),
            }

            return APIResponse.success(
                data=stats, message="Estadísticas del área obtenidas exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas del área: {str(e)}",
                extra={
                    "user_id": request.user.pk,
                    "id": pk,
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
            areas_summary = [
                {
                    "id": str(dept.pk),
                    "nombre": dept.nombre_unidad_organica,
                    "siglas": dept.siglas_area,
                    "total_empleados": EmploymentData.objects.filter(
                        area=dept, estado_datos="activo"
                    ).values("empleado").distinct().count(),
                }
                for dept in Department.objects.all().order_by("nombre_unidad_organica")
            ]

            return APIResponse.success(
                data=areas_summary, message="Resumen de áreas obtenido exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo resumen de áreas: {str(e)}",
                extra={"user_id": request.user.pk, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener resumen de áreas",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def activas(self, request):
        """Get only active areas."""
        queryset = self.get_queryset().filter(estado_area="activo")
        serializer = AreaListSerializer(queryset, many=True)
        return APIResponse.success(data=serializer.data, message="Áreas activas")


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
class EmpleadoViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for Employee management."""

    queryset = Employee.objects.prefetch_related(
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

        # B.5b carryover: identity fields (nombres_empleado, apellido_paterno,
        # apellido_materno, numero_documento) and correo_personal are NOT
        # self-editable — they are HR-only. Identity is immutable for the
        # employee; correo_personal change requires HR-validated
        # `corregir-correo` workflow (audit trail). Allowing employee to
        # rename themselves was the security gap caught by
        # test_employee_cannot_patch_restricted_fields.
        _SELF_EDITABLE_FIELDS = {
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
                historial_ubicaciones__area_destino_id=area_id,
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

        # B.1 (#8): apply tenant filter via mixin
        return self._filter_by_tenant(queryset)

    def perform_create(self, serializer):
        """Create employee with logging — tenant injected by TenantAwareViewSetMixin."""
        # B.1 (#8): mixin injects tenant=request.tenant into serializer.save()
        super().perform_create(serializer)
        empleado = serializer.instance
        logger.info(
            f"Employee creado: {empleado.nombre_completo}",
            extra={
                "user_id": self.request.user.pk,
                "id": empleado.pk,
                "action": "create_empleado",
            },
        )

    def perform_update(self, serializer):
        """Update employee with logging."""
        empleado = serializer.save()
        logger.info(
            f"Employee actualizado: {empleado.nombre_completo}",
            extra={
                "user_id": self.request.user.pk,
                "id": empleado.pk,
                "action": "update_empleado",
            },
        )

    def perform_destroy(self, instance):
        """Soft delete employee by changing status to inactive."""
        instance.estado_empleado = "inactivo"
        instance.save()
        logger.info(
            f"Employee desactivado: {instance.nombre_completo}",
            extra={
                "user_id": self.request.user.id,
                "id": instance.pk,
                "action": "soft_delete_empleado",
            },
        )

    @action(detail=True, methods=["get"])
    @require_permissions(["ver_empleados"])
    def datos_completos(self, request, pk=None):
        """Get complete employee data including family and academic info."""
        try:
            return APIResponse.error(
                message="Endpoint not yet implemented — use individual /datos-personales, /datos-laborales, /datos-familiares endpoints",
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo datos completos: {str(e)}",
                extra={
                    "user_id": request.user.pk,
                    "id": pk,
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

            # Update active employment data with new area
            EmploymentData.objects.filter(
                empleado_id=empleado.pk, estado_datos="activo"
            ).update(area_id=area_destino_id)

            logger.info(
                f"Employee transferido: {empleado.nombre_completo}",
                extra={
                    "user_id": request.user.pk,
                    "id": empleado.pk,
                    "area_destino_id": area_destino_id,
                    "action": "transfer_empleado",
                },
            )

            return APIResponse.success(
                message=f"Employee {empleado.nombre_completo} transferido exitosamente"
            )

        except BusinessLogicError as e:
            return APIResponse.error(
                message=str(e), status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Error transfiriendo empleado: {str(e)}",
                extra={
                    "user_id": request.user.pk,
                    "id": pk,
                    "error": str(e),
                },
            )
            return APIResponse.error(
                message="Error al transferir empleado",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # Historial de ubicaciones removido - usar LocationHistory model

    @action(detail=False, methods=["get"])
    @require_hr()
    def estadisticas(self, request):
        """Get employee statistics."""
        try:
            base_qs = self.get_queryset()
            stats = {
                "total": base_qs.count(),
                "activos": base_qs.filter(estado_empleado="activo").count(),
                "inactivos": base_qs.filter(estado_empleado="inactivo").count(),
                "cesados": base_qs.filter(estado_empleado="cesado").count(),
            }
            return APIResponse.success(
                data=stats, message="Estadísticas de empleados obtenidas exitosamente"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas de empleados: {str(e)}",
                extra={"user_id": request.user.pk, "error": str(e)},
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
        from apps.employees.services.employee_report_service import EmpleadoReportService

        try:
            service = EmpleadoReportService()
            pdf_content, nombre_archivo = service.generar_reporte_integral(pk)
            return service.crear_http_response(pdf_content, nombre_archivo)
        except Employee.DoesNotExist:
            return APIResponse.error(message="Employee no encontrado", status_code=404)
        except Exception as e:
            logger.error(f"Error generando reporte integral: {e}")
            return APIResponse.error(
                message="Error al generar el reporte", status_code=500
            )

    @action(detail=True, methods=["get"])
    @require_authenticated()
    def reporte_seccion(self, request, pk=None):
        """Genera un reporte PDF de una seccion del empleado."""
        from apps.employees.services.employee_report_service import EmpleadoReportService

        seccion = request.query_params.get("seccion", "todos")
        if seccion not in ["todos", "personal", "laboral", "academico", "familiar"]:
            return APIResponse.error(message="Seccion no valida", status_code=400)
        try:
            service = EmpleadoReportService()
            pdf_content, nombre_archivo = service.generar_reporte_seccion(pk, seccion)
            return service.crear_http_response(pdf_content, nombre_archivo)
        except Employee.DoesNotExist:
            return APIResponse.error(message="Employee no encontrado", status_code=404)
        except Exception as e:
            logger.error(f"Error generando reporte seccion: {e}")
            return APIResponse.error(
                message="Error al generar el reporte", status_code=500
            )


class DatosFamiliaresViewSet(viewsets.ModelViewSet):
    """ViewSet for FamilyMember management. Employees can manage their own records."""

    queryset = FamilyMember.objects.select_related("empleado")
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
            if not user.empleado or str(user.empleado.pk) != str(empleado_id or ""):
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
    """ViewSet for AcademicRecord management. Employees can manage their own records."""

    queryset = AcademicRecord.objects.select_related("empleado")
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
            if not user.empleado or str(user.empleado.pk) != str(empleado_id or ""):
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

    from apps.employees.models import Certification as _CursosCertificaciones

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
        from apps.employees.models import Certification

        queryset = Certification.objects.select_related(
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
            if not user.empleado or str(user.empleado.pk) != str(empleado_id or ""):
                return APIResponse.error(
                    message="Solo puede registrar cursos para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)


class DatosLaboralesViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for EmploymentData management with optimized queries."""

    queryset = EmploymentData.objects.select_related(
        "empleado",
        "area",
        "jefe_directo",
    ).all()
    serializer_class = DatosLaboralesSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = DatosLaboralesFilter
    search_fields = ["cargo_empleado", "categoria", "regimen_laboral"]
    ordering_fields = ["fecha_ingreso", "fecha_cese", "sueldo_basico"]
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
        """Filter by employee if specified, then by tenant."""
        queryset = super().get_queryset()
        empleado_id = self.request.query_params.get("empleado")
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        return self._filter_by_tenant(queryset)

    @action(detail=False, methods=["get"])
    @require_hr()
    def estadisticas_remuneracion(self, request):
        """Get salary statistics."""
        try:
            queryset = self.get_queryset().filter(estado_datos="activo")
            stats = queryset.aggregate(
                promedio=Avg("sueldo_basico"),
                total_empleados=Count("id"),
            )

            # Group by salary ranges
            rangos = {
                "menos_1000": queryset.filter(sueldo_basico__lt=1000).count(),
                "entre_1000_2000": queryset.filter(
                    sueldo_basico__gte=1000, sueldo_basico__lt=2000
                ).count(),
                "entre_2000_3000": queryset.filter(
                    sueldo_basico__gte=2000, sueldo_basico__lt=3000
                ).count(),
                "mas_3000": queryset.filter(sueldo_basico__gte=3000).count(),
            }

            stats["rangos_salariales"] = rangos

            return APIResponse.success(
                data=stats, message="Estadísticas de remuneración"
            )
        except Exception as e:
            logger.error(
                f"Error obteniendo estadísticas de remuneración: {str(e)}",
                extra={"user_id": request.user.pk, "error": str(e)},
            )
            return APIResponse.error(
                message="Error al obtener estadísticas",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConfiguracionRemuneracionViewSet(viewsets.ModelViewSet):
    """ViewSet para catálogo maestro de conceptos de remuneración."""

    queryset = CompensationConfiguration.objects.all()
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

    queryset = AfpConfiguration.objects.all()
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
class DocumentosDigitalesViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """ViewSet for DigitalDocument management."""

    queryset = DigitalDocument.objects.select_related(
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
            if not user.empleado or user.empleado.pk != int(empleado_id):
                return APIResponse.error(
                    message="Solo puede subir documentos para su propio legajo",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Set subido_por, file metadata, and default estado for employee uploads.

        B.1 (#14): tenant injected via TenantAwareViewSetMixin guarded pattern.
        """
        user = self.request.user
        extra = {"subido_por": user}
        # B.1 (#14): propagate tenant when available
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            extra["tenant"] = tenant
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

        # B.1 (#14): apply tenant filter via mixin
        return self._filter_by_tenant(queryset)

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

        # B.1 (#14): propagate tenant into direct .objects.create() calls
        tenant = getattr(request, "tenant", None)

        documentos_creados = []
        for i, archivo in enumerate(archivos):
            nombre = nombre_documento or archivo.name
            if len(archivos) > 1 and periodo:
                nombre = (
                    f"{nombre} - {periodo}"
                    if i == 0
                    else f"{nombre} ({i+1}) - {periodo}"
                )

            create_kwargs = dict(
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
            if tenant is not None:
                create_kwargs["tenant"] = tenant
            doc = DigitalDocument.objects.create(**create_kwargs)
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

class ConfiguracionEmpresaViewSet(viewsets.ViewSet):
    """ViewSet para gestionar la configuración de la empresa."""

    @require_authenticated()
    def list(self, request):
        """Obtener configuración actual de la empresa."""
        from api.v1.rrhh.serializers import ConfiguracionEmpresaSerializer
        from apps.organization.models import Company

        cfg = Company.get_config(tenant=getattr(request, 'tenant', None))
        serializer = ConfiguracionEmpresaSerializer(cfg, context={"request": request})
        return APIResponse.success(data=serializer.data)

    @require_admin()
    def create(self, request):
        """Actualizar configuración de la empresa (upsert)."""
        from api.v1.rrhh.serializers import ConfiguracionEmpresaSerializer
        from apps.organization.models import Company

        cfg = Company.get_config(tenant=getattr(request, 'tenant', None))
        serializer = ConfiguracionEmpresaSerializer(
            cfg, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data, message="Configuración actualizada"
            )
        return APIResponse.error(message="Datos inválidos", errors=serializer.errors)
