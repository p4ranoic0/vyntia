"""Vistas para las APIs de vacaciones."""

import logging
from datetime import date

from apps.employees.models import Empleado
from apps.time_off.models import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
from apps.time_off.services import (
    VacationAdminService,
    VacationApprovalService,
    VacationReportService,
    VacationService,
)
from apps.core.decorators import (
    cache_response,
    invalidate_cache,
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
)
from apps.core.pagination import StandardResultsSetPagination
from apps.core.responses import APIResponse
from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import (
    ConfiguracionVacacionesFilter,
    GoceVacacionesFilter,
    PeriodoVacacionalFilter,
    SolicitudVacacionesFilter,
)
from .permissions import VacationPermissions
from .serializers import (
    AprobacionSolicitudSerializer,
    ConfiguracionVacacionesSerializer,
    EmpleadoDiasVencidosSerializer,
    GoceVacacionesSerializer,
    HistorialSolicitudVacacionesSerializer,
    PeriodoVacacionalSerializer,
    SolicitudVacacionesCreateSerializer,
    SolicitudVacacionesSerializer,
)

logger = logging.getLogger(__name__)


def _subordinados_del_usuario(user):
    if not getattr(user, "empleado", None):
        return Empleado.objects.none()
    return Empleado.objects.filter(
        datos_laborales__jefe_directo=user.empleado,
        datos_laborales__estado_datos="activo",
    ).distinct()


@extend_schema_view(
    list=extend_schema(
        summary="Listar configuraciones de vacaciones",
        description="Retorna configuraciones activas/inactivas según filtros del usuario RRHH.",
        responses={
            200: OpenApiResponse(description="Listado paginado de configuraciones"),
            401: OpenApiResponse(description="No autenticado"),
            403: OpenApiResponse(description="Sin permisos RRHH"),
        },
    ),
    create=extend_schema(
        summary="Crear configuración de vacaciones",
        description="Crea una nueva configuración por ámbito general, área o empleado.",
        responses={
            201: OpenApiResponse(description="Configuración creada correctamente"),
            400: OpenApiResponse(description="Datos inválidos"),
            401: OpenApiResponse(description="No autenticado"),
            403: OpenApiResponse(description="Sin permisos de administrador"),
        },
    ),
    retrieve=extend_schema(summary="Obtener configuración de vacaciones"),
    update=extend_schema(summary="Actualizar configuración de vacaciones"),
    partial_update=extend_schema(summary="Actualizar parcialmente configuración"),
    destroy=extend_schema(summary="Desactivar configuración de vacaciones"),
)
class ConfiguracionVacacionesViewSet(viewsets.ModelViewSet):
    queryset = ConfiguracionVacaciones.objects.select_related(
        "area", "empleado", "creado_por"
    ).all()
    serializer_class = ConfiguracionVacacionesSerializer
    permission_classes = [permissions.IsAuthenticated, VacationPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConfiguracionVacacionesFilter
    search_fields = ["observaciones"]
    ordering_fields = ["fecha_creacion", "fecha_inicio_vigencia", "tipo_configuracion"]
    ordering = ["-fecha_creacion"]

    @cache_response(timeout=600, key_prefix="vac_config")
    @require_hr()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=600, key_prefix="vac_config_detail")
    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_config:*", "view_cache:vac_config_detail:*"])
    @require_admin()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_config:*", "view_cache:vac_config_detail:*"])
    @require_admin()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_config:*", "view_cache:vac_config_detail:*"])
    @require_admin()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_config:*", "view_cache:vac_config_detail:*"])
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.instance = VacationAdminService.crear_configuracion_vacaciones(
            serializer.validated_data, self.request.user
        )

    def perform_update(self, serializer):
        serializer.instance = VacationAdminService.actualizar_configuracion_vacaciones(
            serializer.instance.configuracion_id,
            serializer.validated_data,
            self.request.user,
        )

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo", "fecha_actualizacion"])


@extend_schema_view(
    list=extend_schema(summary="Listar períodos vacacionales"),
    retrieve=extend_schema(summary="Obtener período vacacional"),
)
class PeriodoVacacionalViewSet(viewsets.ModelViewSet):
    queryset = PeriodoVacacional.objects.select_related(
        "empleado", "configuracion", "contrato"
    ).all()
    serializer_class = PeriodoVacacionalSerializer
    permission_classes = [permissions.IsAuthenticated, VacationPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PeriodoVacacionalFilter
    search_fields = [
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
        "empleado__numero_documento",
    ]
    ordering_fields = ["ano_periodo", "fecha_creacion", "dias_pendientes"]
    ordering = ["-ano_periodo"]

    @cache_response(timeout=300, key_prefix="vac_periodos")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=300, key_prefix="vac_periodo_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.es_admin_rrhh:
            return queryset
        if user.es_jefe:
            return queryset.filter(
                Q(empleado=user.empleado)
                | Q(empleado__in=_subordinados_del_usuario(user))
            ).distinct()
        if getattr(user, "empleado", None):
            return queryset.filter(empleado=user.empleado)
        return queryset.none()

    @invalidate_cache(["view_cache:vac_periodos:*", "view_cache:vac_periodo_detail:*"])
    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-masivo")
    def generar_masivo(self, request):
        try:
            ano = int(request.data.get("ano"))
            empleados_ids = request.data.get("empleados_ids") or []
            if not empleados_ids:
                return APIResponse.error(
                    "Debe enviar al menos un empleado.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            result = VacationAdminService.generar_periodos_masivos(
                ano, empleados_ids, request.user
            )
            return APIResponse.success(result, "Generación de periodos completada.")
        except Exception as exc:
            logger.error("Error en generar_masivo: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @invalidate_cache(["view_cache:vac_periodos:*", "view_cache:vac_periodo_detail:*"])
    @require_hr()
    @action(detail=True, methods=["post"], url_path="ajustar-dias")
    def ajustar_dias(self, request, pk=None):
        try:
            periodo = self.get_object()
            from decimal import Decimal

            nuevos_dias = Decimal(str(request.data.get("nuevos_dias")))
            motivo = (request.data.get("motivo") or "").strip()
            if not motivo:
                return APIResponse.error(
                    "El motivo es obligatorio.", status_code=status.HTTP_400_BAD_REQUEST
                )
            actualizado = VacationAdminService.ajustar_dias_periodo(
                periodo.periodo_id, nuevos_dias, motivo, request.user
            )
            return APIResponse.success(
                self.get_serializer(actualizado).data, "Período ajustado."
            )
        except Exception as exc:
            logger.error("Error en ajustar_dias: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary="Listar solicitudes de vacaciones"),
    create=extend_schema(summary="Crear solicitud de vacaciones"),
    retrieve=extend_schema(summary="Obtener solicitud de vacaciones"),
)
class SolicitudVacacionesViewSet(viewsets.ModelViewSet):
    queryset = SolicitudVacaciones.objects.select_related(
        "empleado",
        "periodo_vacacional",
        "jefe_aprobador",
        "rrhh_aprobador",
        "rechazado_por",
        "cancelado_por",
    ).all()
    permission_classes = [permissions.IsAuthenticated, VacationPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SolicitudVacacionesFilter
    search_fields = [
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
        "empleado__numero_documento",
        "motivo_solicitud",
    ]
    ordering_fields = [
        "fecha_envio",
        "fecha_inicio",
        "estado_solicitud",
        "fecha_creacion",
    ]
    ordering = ["-fecha_creacion"]

    @cache_response(timeout=180, key_prefix="vac_solicitudes")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=180, key_prefix="vac_solicitud_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return SolicitudVacacionesCreateSerializer
        return SolicitudVacacionesSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.es_admin_rrhh:
            return queryset
        if user.es_jefe:
            return queryset.filter(
                Q(empleado=user.empleado)
                | Q(empleado__in=_subordinados_del_usuario(user))
            ).distinct()
        if getattr(user, "empleado", None):
            return queryset.filter(empleado=user.empleado)
        return queryset.none()

    @invalidate_cache(
        ["view_cache:vac_solicitudes:*", "view_cache:vac_solicitud_detail:*"]
    )
    @require_authenticated()
    @action(detail=True, methods=["post"], url_path="enviar")
    def enviar(self, request, pk=None):
        try:
            solicitud = self.get_object()
            updated = VacationService.enviar_solicitud(
                solicitud.solicitud_id, request.user
            )
            return APIResponse.success(
                SolicitudVacacionesSerializer(updated).data, "Solicitud enviada."
            )
        except Exception as exc:
            logger.error("Error al enviar solicitud: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @invalidate_cache(
        ["view_cache:vac_solicitudes:*", "view_cache:vac_solicitud_detail:*"]
    )
    @extend_schema(request=AprobacionSolicitudSerializer)
    @require_manager()
    @action(detail=True, methods=["post"], url_path="aprobar-jefe")
    def aprobar_jefe(self, request, pk=None):
        try:
            solicitud = self.get_object()
            serializer = AprobacionSolicitudSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            accion = serializer.validated_data["accion"]
            motivo = serializer.validated_data.get("motivo", "")
            if accion == "aprobar":
                updated = VacationApprovalService.aprobar_por_jefe(
                    solicitud.solicitud_id, request.user, motivo
                )
                message = "Solicitud aprobada por jefe."
            else:
                updated = VacationApprovalService.rechazar_solicitud(
                    solicitud.solicitud_id, request.user, motivo, "jefe"
                )
                message = "Solicitud rechazada por jefe."
            return APIResponse.success(
                SolicitudVacacionesSerializer(updated).data, message
            )
        except Exception as exc:
            logger.error("Error en aprobar_jefe: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @invalidate_cache(
        ["view_cache:vac_solicitudes:*", "view_cache:vac_solicitud_detail:*"]
    )
    @extend_schema(request=AprobacionSolicitudSerializer)
    @require_hr()
    @action(detail=True, methods=["post"], url_path="aprobar-rrhh")
    def aprobar_rrhh(self, request, pk=None):
        try:
            solicitud = self.get_object()
            serializer = AprobacionSolicitudSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            accion = serializer.validated_data["accion"]
            motivo = serializer.validated_data.get("motivo", "")
            if accion == "aprobar":
                updated = VacationApprovalService.aprobar_por_rrhh(
                    solicitud.solicitud_id, request.user, motivo
                )
                message = "Solicitud aprobada por RRHH."
            else:
                updated = VacationApprovalService.rechazar_solicitud(
                    solicitud.solicitud_id, request.user, motivo, "rrhh"
                )
                message = "Solicitud rechazada por RRHH."
            return APIResponse.success(
                SolicitudVacacionesSerializer(updated).data, message
            )
        except Exception as exc:
            logger.error("Error en aprobar_rrhh: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @invalidate_cache(
        ["view_cache:vac_solicitudes:*", "view_cache:vac_solicitud_detail:*"]
    )
    @require_authenticated()
    @action(detail=True, methods=["post"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        try:
            solicitud = self.get_object()
            motivo = (request.data.get("motivo") or "").strip()
            if not motivo:
                return APIResponse.error(
                    "Debe ingresar motivo de cancelación.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            updated = VacationApprovalService.cancelar_solicitud(
                solicitud.solicitud_id, request.user, motivo
            )
            return APIResponse.success(
                SolicitudVacacionesSerializer(updated).data, "Solicitud cancelada."
            )
        except Exception as exc:
            logger.error("Error en cancelar: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @require_manager()
    @action(detail=False, methods=["get"], url_path="pendientes-jefe")
    def pendientes_jefe(self, request):
        try:
            solicitudes = VacationApprovalService.obtener_solicitudes_pendientes_jefe(
                request.user
            )
            return APIResponse.success(
                SolicitudVacacionesSerializer(solicitudes, many=True).data,
                "Pendientes del jefe.",
            )
        except Exception as exc:
            logger.error("Error pendientes_jefe: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @require_hr()
    @action(detail=False, methods=["get"], url_path="pendientes-rrhh")
    def pendientes_rrhh(self, request):
        try:
            solicitudes = VacationApprovalService.obtener_solicitudes_pendientes_rrhh(
                request.user
            )
            return APIResponse.success(
                SolicitudVacacionesSerializer(solicitudes, many=True).data,
                "Pendientes de RRHH.",
            )
        except Exception as exc:
            logger.error("Error pendientes_rrhh: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @require_authenticated()
    @action(detail=False, methods=["get"], url_path="mis-solicitudes")
    def mis_solicitudes(self, request):
        if not getattr(request.user, "empleado", None):
            return APIResponse.error(
                "Usuario no tiene empleado asociado.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        qs = self.get_queryset().filter(empleado=request.user.empleado)
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                SolicitudVacacionesSerializer(page, many=True).data
            )
        return APIResponse.success(
            SolicitudVacacionesSerializer(qs, many=True).data, "Mis solicitudes."
        )


@extend_schema_view(
    list=extend_schema(summary="Listar goces de vacaciones"),
    retrieve=extend_schema(summary="Obtener goce de vacaciones"),
)
class GoceVacacionesViewSet(viewsets.ModelViewSet):
    queryset = GoceVacaciones.objects.select_related(
        "empleado", "solicitud_vacaciones", "periodo_vacacional"
    ).all()
    serializer_class = GoceVacacionesSerializer
    permission_classes = [permissions.IsAuthenticated, VacationPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GoceVacacionesFilter
    search_fields = [
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
        "empleado__numero_documento",
    ]
    ordering_fields = ["fecha_inicio_real", "fecha_creacion"]
    ordering = ["-fecha_inicio_real", "-fecha_creacion"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.es_admin_rrhh:
            return queryset
        if user.es_jefe:
            return queryset.filter(
                Q(empleado=user.empleado)
                | Q(empleado__in=_subordinados_del_usuario(user))
            ).distinct()
        if getattr(user, "empleado", None):
            return queryset.filter(empleado=user.empleado)
        return queryset.none()

    @cache_response(timeout=180, key_prefix="vac_goces")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=180, key_prefix="vac_goce_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_goces:*", "view_cache:vac_goce_detail:*"])
    @require_hr()
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_goces:*", "view_cache:vac_goce_detail:*"])
    @require_hr()
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_goces:*", "view_cache:vac_goce_detail:*"])
    @require_hr()
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @invalidate_cache(["view_cache:vac_goces:*", "view_cache:vac_goce_detail:*"])
    @require_admin()
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class HistorialSolicitudVacacionesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HistorialSolicitudVacaciones.objects.select_related(
        "solicitud_vacaciones", "usuario_accion"
    ).all()
    serializer_class = HistorialSolicitudVacacionesSerializer
    permission_classes = [permissions.IsAuthenticated, VacationPermissions]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ["fecha_accion"]
    ordering = ["-fecha_accion"]

    @cache_response(timeout=180, key_prefix="vac_historial")
    @require_authenticated()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response(timeout=180, key_prefix="vac_historial_detail")
    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.es_admin_rrhh:
            return queryset
        if user.es_jefe:
            return queryset.filter(
                Q(solicitud_vacaciones__empleado=user.empleado)
                | Q(solicitud_vacaciones__empleado__in=_subordinados_del_usuario(user))
            ).distinct()
        if getattr(user, "empleado", None):
            return queryset.filter(solicitud_vacaciones__empleado=user.empleado)
        return queryset.none()


@extend_schema(exclude=True)
class VacacionesReportesViewSet(viewsets.GenericViewSet):
    """
    ViewSet para reportes y analíticas de vacaciones.

    NOTA: Excluido del schema OpenAPI porque retorna datos dinámicos
    sin un serializer fijo.
    """

    permission_classes = [permissions.IsAuthenticated, VacationPermissions]

    @cache_response(timeout=300, key_prefix="vac_reporte_estadisticas")
    @extend_schema(
        summary="Obtener estadísticas de vacaciones",
        parameters=[
            OpenApiParameter(
                "ano", OpenApiTypes.INT, description="Año para estadísticas"
            ),
            OpenApiParameter(
                "area_id", OpenApiTypes.INT, description="Área (opcional)"
            ),
        ],
    )
    @require_hr()
    @action(detail=False, methods=["get"], url_path="estadisticas")
    def estadisticas(self, request):
        try:
            ano = request.query_params.get("ano")
            area_id = request.query_params.get("area_id")
            result = VacationAdminService.obtener_estadisticas_vacaciones(
                int(ano) if ano else None,
                int(area_id) if area_id else None,
            )
            return APIResponse.success(result, "Estadísticas generadas.")
        except Exception as exc:
            logger.error("Error en estadisticas: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @cache_response(timeout=300, key_prefix="vac_reporte_dias_vencidos")
    @extend_schema(
        summary="Obtener empleados con días vencidos",
        parameters=[
            OpenApiParameter("ano", OpenApiTypes.INT, description="Año de consulta")
        ],
    )
    @require_hr()
    @action(detail=False, methods=["get"], url_path="dias-vencidos")
    def dias_vencidos(self, request):
        try:
            ano = request.query_params.get("ano")
            result = VacationAdminService.obtener_empleados_con_dias_vencidos(
                int(ano) if ano else None
            )
            return APIResponse.success(
                EmpleadoDiasVencidosSerializer(result, many=True).data, "Días vencidos."
            )
        except Exception as exc:
            logger.error("Error en dias_vencidos: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @cache_response(timeout=180, key_prefix="vac_reporte_solicitudes")
    @extend_schema(
        summary="Obtener reporte de solicitudes",
        parameters=[
            OpenApiParameter("fecha_inicio", OpenApiTypes.DATE),
            OpenApiParameter("fecha_fin", OpenApiTypes.DATE),
            OpenApiParameter("estado", OpenApiTypes.STR),
            OpenApiParameter("area_id", OpenApiTypes.INT),
            OpenApiParameter("empleado_id", OpenApiTypes.INT),
            OpenApiParameter("contrato_id", OpenApiTypes.INT),
        ],
    )
    @require_hr()
    @action(detail=False, methods=["get"], url_path="reporte-solicitudes")
    def reporte_solicitudes(self, request):
        try:
            fecha_inicio = request.query_params.get("fecha_inicio")
            fecha_fin = request.query_params.get("fecha_fin")
            estado = request.query_params.get("estado")
            area_id = request.query_params.get("area_id")
            empleado_id = request.query_params.get("empleado_id")
            contrato_id = request.query_params.get("contrato_id")

            result = VacationAdminService.obtener_reporte_solicitudes(
                date.fromisoformat(fecha_inicio) if fecha_inicio else None,
                date.fromisoformat(fecha_fin) if fecha_fin else None,
                estado or None,
                int(area_id) if area_id else None,
                int(empleado_id) if empleado_id else None,
                int(contrato_id) if contrato_id else None,
            )
            return APIResponse.success(result, "Reporte generado.")
        except Exception as exc:
            logger.error("Error en reporte_solicitudes: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Generar reporte de vacaciones por empleado (PDF)",
        parameters=[
            OpenApiParameter(
                "empleado_id", OpenApiTypes.INT, description="Empleado ID"
            ),
            OpenApiParameter(
                "contrato_id", OpenApiTypes.INT, description="Contrato ID (opcional)"
            ),
        ],
    )
    @require_hr()
    @action(detail=False, methods=["get"], url_path="reporte-empleado")
    def reporte_empleado(self, request):
        try:
            empleado_id = request.query_params.get("empleado_id")
            contrato_id = request.query_params.get("contrato_id")
            if not empleado_id:
                return APIResponse.error(
                    "empleado_id es obligatorio.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            service = VacationReportService()
            pdf_content, nombre_archivo = service.generar_reporte_empleado(
                int(empleado_id),
                int(contrato_id) if contrato_id else None,
            )
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = f'inline; filename="{nombre_archivo}"'
            return response
        except Exception as exc:
            logger.error("Error en reporte_empleado: %s", exc)
            return APIResponse.error(str(exc), status_code=status.HTTP_400_BAD_REQUEST)
