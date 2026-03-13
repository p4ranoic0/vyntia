# -*- coding: utf-8 -*-
"""
Views para el módulo de Remuneraciones.

Contiene los ViewSets para gestión de planillas mensuales,
boletas de pago, descuentos masivos y reportes de remuneraciones.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from app_rrhh.models import (
    BoletaPago,
    CalendarioPago,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    ConfiguracionUit,
    DescuentoMasivo,
    DetallePlanilla,
    Empleado,
    PlanillaMensual,
)
from app_rrhh.services import DescuentoMasivoService, PlanillaCalculoService
from core.decorators import require_admin, require_authenticated, require_hr
from core.pagination import StandardResultsSetPagination
from core.responses import APIResponse
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .remuneraciones_serializers import (
    BoletaPagoDetailSerializer,
    BoletaPagoListSerializer,
    CalendarioPagoCreateSerializer,
    CalendarioPagoDetailSerializer,
    CalendarioPagoListSerializer,
    ConfiguracionAfpSerializer,
    ConfiguracionRemuneracionSerializer,
    ConfiguracionUitSerializer,
    DescuentoMasivoCreateSerializer,
    DescuentoMasivoDetailSerializer,
    DescuentoMasivoListSerializer,
    DetallePlanillaCreateSerializer,
    DetallePlanillaDetailSerializer,
    DetallePlanillaListSerializer,
    PlanillaMensualCreateSerializer,
    PlanillaMensualDetailSerializer,
    PlanillaMensualListSerializer,
    PlanillaMensualUpdateSerializer,
)


class ConfiguracionAfpViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de configuración de AFP."""

    queryset = ConfiguracionAfp.objects.all()
    serializer_class = ConfiguracionAfpSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar configuraciones de AFP."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear configuración de AFP - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar configuración de AFP - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar configuración de AFP - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = ConfiguracionAfp.objects.order_by("-vigencia_mes", "afp_nombre")

        # Filtros
        afp_nombre = self.request.query_params.get("afp_nombre")
        vigencia_mes = self.request.query_params.get("vigencia_mes")
        estado = self.request.query_params.get("estado", "activo")

        if afp_nombre:
            queryset = queryset.filter(afp_nombre__icontains=afp_nombre)
        if vigencia_mes:
            queryset = queryset.filter(vigencia_mes=vigencia_mes)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class ConfiguracionUitViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de configuración de UIT (Unidad Impositiva Tributaria)."""

    queryset = ConfiguracionUit.objects.all()
    serializer_class = ConfiguracionUitSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar configuraciones de UIT."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear configuración de UIT - requiere rol RRHH."""
        # Establecer creado_por automáticamente
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creado_por=request.user)

        return APIResponse.success(
            message="Configuración UIT creada exitosamente",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
        )

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar configuración de UIT - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar configuración de UIT - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    @require_hr()
    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        """
        Activa una configuración UIT y desactiva las demás del mismo año.
        """
        uit = self.get_object()

        try:
            # Desactivar todas las configuraciones del mismo año
            ConfiguracionUit.objects.filter(anio=uit.anio).update(estado="inactivo")

            # Activar la seleccionada
            uit.estado = "activo"
            uit.save()

            return APIResponse.success(
                message=f"Configuración UIT {uit.anio} activada exitosamente",
                data=self.get_serializer(uit).data,
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al activar configuración UIT: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = ConfiguracionUit.objects.select_related("creado_por").order_by(
            "-anio"
        )

        # Filtros
        anio = self.request.query_params.get("anio")
        estado = self.request.query_params.get("estado")  # No default para ver todos
        activo = self.request.query_params.get("activo")  # true/false

        if anio:
            queryset = queryset.filter(anio=anio)
        if estado:
            queryset = queryset.filter(estado=estado)
        if activo == "true":
            queryset = queryset.filter(estado="activo")
        elif activo == "false":
            queryset = queryset.filter(estado="inactivo")

        return queryset


class ConfiguracionRemuneracionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de configuración de conceptos de remuneración."""

    queryset = ConfiguracionRemuneracion.objects.all()
    serializer_class = ConfiguracionRemuneracionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar configuraciones de conceptos."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear configuración de concepto - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar configuración de concepto - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar configuración de concepto - requiere rol administrador."""
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = ConfiguracionRemuneracion.objects.order_by("tipo", "orden", "nombre")

        # Filtros
        tipo = self.request.query_params.get("tipo")
        codigo = self.request.query_params.get("codigo")
        estado = self.request.query_params.get("estado", "activo")

        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if codigo:
            queryset = queryset.filter(codigo__icontains=codigo)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class PlanillaMensualViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de planillas mensuales.

    Proporciona operaciones CRUD y funcionalidades específicas como
    generación de planillas, cálculo automático y reportes.
    """

    queryset = PlanillaMensual.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar planillas mensuales."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener planilla específica."""
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear planilla mensual - requiere rol RRHH."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario_generacion=request.user, estado="borrador")
        return APIResponse.success(
            data=serializer.data,
            message="Planilla creada exitosamente",
            status_code=201,
        )

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar planilla mensual - requiere rol RRHH."""
        instance = self.get_object()
        if instance.esta_cerrada:
            return APIResponse.error(
                message="No se puede modificar una planilla cerrada", status_code=400
            )
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar planilla mensual - requiere rol administrador."""
        instance = self.get_object()
        if instance.estado in ["aprobada", "pagada"]:
            return APIResponse.error(
                message="No se puede eliminar una planilla aprobada o pagada",
                status_code=400,
            )
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "create":
            return PlanillaMensualCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PlanillaMensualUpdateSerializer
        elif self.action == "retrieve":
            return PlanillaMensualDetailSerializer
        return PlanillaMensualListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = PlanillaMensual.objects.select_related(
            "usuario_generacion", "usuario_aprobacion"
        ).order_by("-periodo", "modalidad")

        # Filtros
        periodo = self.request.query_params.get("periodo")
        modalidad = self.request.query_params.get("modalidad")
        estado = self.request.query_params.get("estado")
        meta_presupuestal = self.request.query_params.get("meta_presupuestal")

        if periodo:
            queryset = queryset.filter(periodo=periodo)
        if modalidad:
            queryset = queryset.filter(modalidad=modalidad)
        if estado:
            queryset = queryset.filter(estado=estado)
        if meta_presupuestal:
            queryset = queryset.filter(meta_presupuestal__icontains=meta_presupuestal)

        return queryset

    @require_hr()
    @action(detail=True, methods=["post"])
    def generar_planilla(self, request, pk=None):
        """Genera automáticamente la planilla con empleados activos."""
        planilla = self.get_object()

        if planilla.estado not in ["borrador", "procesando"]:
            return APIResponse.error(
                message="Solo se pueden generar planillas en estado borrador o procesando",
                status_code=400,
            )

        try:
            # Obtener empleados activos según modalidad
            empleados = Empleado.objects.filter(
                estado_empleado="activo", datos_laborales__isnull=False
            ).prefetch_related("datos_laborales__area")

            # TODO: Filtrar por modalidad de contrato según planilla.modalidad

            contador = 0
            for empleado in empleados:
                datos_laborales = empleado.datos_laborales.filter(estado_datos="activo").first()
                if not datos_laborales:
                    continue

                # Verificar si ya existe el detalle
                if DetallePlanilla.objects.filter(
                    planilla=planilla, empleado=empleado
                ).exists():
                    continue

                # Crear detalle de planilla
                DetallePlanilla.objects.create(
                    planilla=planilla,
                    empleado=empleado,
                    datos_laborales=datos_laborales,
                    area_nombre=datos_laborales.area.nombre_unidad_organica if datos_laborales.area else "",
                    cargo=datos_laborales.cargo_empleado,
                    dni=empleado.nro_documento,
                    sistema_pensiones=empleado.sistema_pensiones,
                    tipo_comision_afp=empleado.tipo_comision_afp,
                    remuneracion_basica=datos_laborales.sueldo_basico,
                    asignacion_familiar=datos_laborales.asignacion_familiar,
                    bonificacion_especial=datos_laborales.bonificacion_especial,
                    otras_bonificaciones=datos_laborales.otras_bonificaciones,
                )
                contador += 1

            # Actualizar estado de planilla
            planilla.estado = "generada"
            planilla.fecha_generacion = timezone.now()
            planilla.total_trabajadores = DetallePlanilla.objects.filter(
                planilla=planilla
            ).count()
            planilla.save()

            return APIResponse.success(
                message=f"Planilla generada exitosamente con {contador} empleados",
                data={
                    "empleados_agregados": contador,
                    "total_empleados": planilla.total_trabajadores,
                },
            )

        except Exception as e:
            return APIResponse.error(message=f"Error al generar planilla: {str(e)}")

    @require_hr()
    @action(detail=True, methods=["post"])
    def calcular_planilla(self, request, pk=None):
        """
        Calcula los totales de haberes y descuentos de la planilla.

        Utiliza el servicio PlanillaCalculoService que implementa:
        - Verificación de estado laboral
        - Cálculo de ESSALUD (CAS vs estándar)
        - Cálculo de AFP/ONP con tasas vigentes
        - Retención de renta de 4ta categoría con suspensión
        - Actualización de totales consolidados
        """
        planilla = self.get_object()

        if planilla.estado not in ["borrador", "generada", "procesando"]:
            return APIResponse.error(
                message="Solo se pueden calcular planillas en borrador o generadas",
                status_code=400,
            )

        try:
            # Usar el servicio de cálculo de planillas
            servicio = PlanillaCalculoService()
            resultado = servicio.calcular_planilla(planilla_id=planilla.planilla_id)

            # Recargar la planilla actualizada
            planilla.refresh_from_db()

            return APIResponse.success(
                message=resultado.get("message", "Planilla calculada exitosamente"),
                data=PlanillaMensualDetailSerializer(planilla).data,
            )

        except ValueError as e:
            return APIResponse.error(message=str(e), status_code=400)
        except Exception as e:
            return APIResponse.error(
                message=f"Error al calcular planilla: {str(e)}",
                status_code=500,
            )

    @require_authenticated()
    @action(detail=True, methods=["post"])
    def preview(self, request, pk=None):
        """
        Genera una vista previa de la planilla simulando el cálculo.

        No persiste cambios en la base de datos, solo retorna un resumen
        de cómo quedaría la planilla después del cálculo.
        """
        planilla = self.get_object()

        try:
            # Obtener detalles de la planilla
            detalles = DetallePlanilla.objects.filter(planilla=planilla).select_related(
                "empleado", "datos_laborales"
            )

            # Calcular totales agregados para el resumen
            resumen = {
                "planilla_id": planilla.planilla_id,
                "periodo": str(planilla.periodo),
                "modalidad": planilla.modalidad,
                "meta_presupuestal": planilla.meta_presupuestal,
                "estado_actual": planilla.estado,
                "resumen": {
                    "total_trabajadores": detalles.count(),
                    "total_ingresos": float(
                        detalles.aggregate(Sum("total_haberes"))["total_haberes__sum"]
                        or 0
                    ),
                    "total_descuentos": float(
                        detalles.aggregate(Sum("total_descuentos"))[
                            "total_descuentos__sum"
                        ]
                        or 0
                    ),
                    "total_neto": float(
                        detalles.aggregate(Sum("neto_pagar"))["neto_pagar__sum"] or 0
                    ),
                },
                "detalles": [
                    {
                        "empleado_id": detalle.empleado.empleado_id,
                        "nombres": detalle.empleado.nombres_empleado,
                        "apellidos": f"{detalle.empleado.apellido_paterno} {detalle.empleado.apellido_materno or ''}".strip(),
                        "dni": detalle.dni,
                        "cargo": detalle.cargo,
                        "area": detalle.area_nombre,
                        "remuneracion_basica": float(detalle.remuneracion_basica or 0),
                        "total_haberes": float(detalle.total_haberes or 0),
                        "total_descuentos": float(detalle.total_descuentos or 0),
                        "neto_pagar": float(detalle.neto_pagar or 0),
                    }
                    for detalle in detalles[:50]  # Limitar a primeros 50 para preview
                ],
            }

            return APIResponse.success(data=resumen, message="Vista previa generada")

        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar vista previa: {str(e)}",
                status_code=500,
            )

    @require_hr()
    @action(detail=True, methods=["post"])
    def aprobar_planilla(self, request, pk=None):
        """Aprueba la planilla para pago."""
        planilla = self.get_object()

        if planilla.estado != "generada":
            return APIResponse.error(
                message="Solo se pueden aprobar planillas generadas", status_code=400
            )

        planilla.estado = "aprobada"
        planilla.fecha_aprobacion = timezone.now()
        planilla.usuario_aprobacion = request.user
        planilla.save()

        return APIResponse.success(
            message="Planilla aprobada exitosamente",
            data=PlanillaMensualDetailSerializer(planilla).data,
        )

    @require_authenticated()
    @action(detail=True, methods=["get"])
    def estadisticas(self, request, pk=None):
        """Obtiene estadísticas de la planilla."""
        planilla = self.get_object()

        detalles = DetallePlanilla.objects.filter(planilla=planilla)

        estadisticas = {
            "total_empleados": detalles.count(),
            "promedio_remuneracion": detalles.aggregate(Avg("total_haberes"))[
                "total_haberes__avg"
            ]
            or 0,
            "promedio_descuentos": detalles.aggregate(Avg("total_descuentos"))[
                "total_descuentos__avg"
            ]
            or 0,
            "promedio_neto": detalles.aggregate(Avg("neto_pagar"))["neto_pagar__avg"]
            or 0,
            "distribucion_sistema_pensiones": list(
                detalles.values("sistema_pensiones")
                .annotate(cantidad=Count("detalle_id"))
                .order_by("-cantidad")
            ),
        }

        return APIResponse.success(data=estadisticas)


class DetallePlanillaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de detalles de planilla por empleado."""

    queryset = DetallePlanilla.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar detalles de planilla."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener detalle específico."""
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear detalle de planilla - requiere rol RRHH."""
        return super().create(request, *args, **kwargs)

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar detalle de planilla - requiere rol RRHH."""
        instance = self.get_object()
        if instance.planilla.esta_cerrada:
            return APIResponse.error(
                message="No se puede modificar una planilla cerrada", status_code=400
            )
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar detalle de planilla - requiere rol administrador."""
        instance = self.get_object()
        if instance.planilla.esta_cerrada:
            return APIResponse.error(
                message="No se puede eliminar un detalle de planilla cerrada",
                status_code=400,
            )
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "create":
            return DetallePlanillaCreateSerializer
        elif self.action == "retrieve":
            return DetallePlanillaDetailSerializer
        return DetallePlanillaListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = DetallePlanilla.objects.select_related(
            "planilla", "empleado", "datos_laborales"
        ).order_by("area_nombre", "empleado__apellido_paterno")

        # Filtros
        planilla_id = self.request.query_params.get("planilla_id")
        empleado_id = self.request.query_params.get("empleado_id")
        dni = self.request.query_params.get("dni")
        sistema_pensiones = self.request.query_params.get("sistema_pensiones")

        if planilla_id:
            queryset = queryset.filter(planilla_id=planilla_id)
        if empleado_id:
            queryset = queryset.filter(empleado_id=empleado_id)
        if dni:
            queryset = queryset.filter(dni=dni)
        if sistema_pensiones:
            queryset = queryset.filter(sistema_pensiones__icontains=sistema_pensiones)

        return queryset


class DescuentoMasivoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de descuentos masivos."""

    queryset = DescuentoMasivo.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_hr()
    def list(self, request, *args, **kwargs):
        """Listar descuentos masivos."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def retrieve(self, request, *args, **kwargs):
        """Obtener descuento masivo específico."""
        return super().retrieve(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear carga de descuento masivo - requiere rol RRHH."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario_carga=request.user)
        return APIResponse.success(
            data=serializer.data,
            message="Descuento masivo cargado exitosamente",
            status_code=201,
        )

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar descuento masivo - requiere rol administrador."""
        instance = self.get_object()
        if instance.estado == "aplicado":
            return APIResponse.error(
                message="No se puede eliminar un descuento ya aplicado", status_code=400
            )
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "create":
            return DescuentoMasivoCreateSerializer
        elif self.action == "retrieve":
            return DescuentoMasivoDetailSerializer
        return DescuentoMasivoListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = DescuentoMasivo.objects.select_related(
            "configuracion_concepto", "usuario_carga"
        ).order_by("-fecha_carga")

        # Filtros
        periodo = self.request.query_params.get("periodo")
        estado = self.request.query_params.get("estado")

        if periodo:
            queryset = queryset.filter(periodo=periodo)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset

    @action(detail=True, methods=["post"], url_path="procesar")
    @require_hr()
    def procesar(self, request, pk=None):
        """
        Procesa el archivo Excel de descuento masivo.
        Lee el archivo, valida los datos y crea los ConceptoPlanilla correspondientes.
        """
        descuento = self.get_object()

        if descuento.estado != "pendiente":
            return APIResponse.error(
                message=f"El descuento masivo ya fue procesado (estado: {descuento.estado})",
                status_code=400,
            )

        try:
            service = DescuentoMasivoService()
            resultado = service.procesar_descuento_masivo(descuento.descuento_masivo_id)

            if resultado.get("success"):
                return APIResponse.success(
                    data={
                        "total_registros": resultado["total_registros"],
                        "registros_procesados": resultado["registros_procesados"],
                        "registros_error": resultado["registros_error"],
                        "monto_total": resultado["monto_total"],
                        "errores": resultado.get("errores", []),
                    },
                    message=resultado["message"],
                )
            else:
                return APIResponse.error(
                    message=resultado["message"],
                    data={"errores": resultado.get("errores", [])},
                    status_code=400,
                )

        except ValueError as e:
            return APIResponse.error(message=str(e), status_code=400)
        except Exception as e:
            return APIResponse.error(
                message=f"Error al procesar descuento masivo: {str(e)}",
                status_code=500,
            )

    @action(detail=True, methods=["post"], url_path="anular")
    @require_admin()
    def anular(self, request, pk=None):
        """
        Anula el descuento masivo y revierte los conceptos aplicados.
        Solo administradores pueden anular descuentos.
        """
        descuento = self.get_object()

        if descuento.estado == "anulado":
            return APIResponse.error(
                message="El descuento masivo ya está anulado", status_code=400
            )

        try:
            service = DescuentoMasivoService()
            resultado = service.anular_descuento_masivo(descuento.descuento_masivo_id)

            return APIResponse.success(
                data={"conceptos_eliminados": resultado["conceptos_eliminados"]},
                message=resultado["message"],
            )

        except ValueError as e:
            return APIResponse.error(message=str(e), status_code=400)
        except Exception as e:
            return APIResponse.error(
                message=f"Error al anular descuento masivo: {str(e)}",
                status_code=500,
            )


class BoletaPagoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consulta de boletas de pago."""

    queryset = BoletaPago.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar boletas de pago."""
        return super().list(request, *args, **kwargs)

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Obtener boleta específica."""
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "retrieve":
            return BoletaPagoDetailSerializer
        return BoletaPagoListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = BoletaPago.objects.select_related(
            "detalle_planilla__planilla", "detalle_planilla__empleado"
        ).order_by("-fecha_generacion")

        # Si no es RRHH, solo ver sus propias boletas
        user = self.request.user
        if not user.groups.filter(name__in=["RRHH", "Administrador"]).exists():
            queryset = queryset.filter(detalle_planilla__empleado__usuario=user)

        # Filtros
        empleado_id = self.request.query_params.get("empleado_id")
        periodo = self.request.query_params.get("periodo")
        estado = self.request.query_params.get("estado")

        if empleado_id:
            queryset = queryset.filter(detalle_planilla__empleado_id=empleado_id)
        if periodo:
            queryset = queryset.filter(detalle_planilla__planilla__periodo=periodo)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset


class CalendarioPagoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de calendarios de pago."""

    queryset = CalendarioPago.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        """Listar calendarios de pago."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Crear calendario de pago - requiere rol RRHH."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(usuario_programacion=request.user)
        return APIResponse.success(
            data=serializer.data,
            message="Calendario de pago creado exitosamente",
            status_code=201,
        )

    @require_hr()
    def update(self, request, *args, **kwargs):
        """Actualizar calendario de pago - requiere rol RRHH."""
        return super().update(request, *args, **kwargs)

    @require_admin()
    def destroy(self, request, *args, **kwargs):
        """Eliminar calendario de pago - requiere rol administrador."""
        instance = self.get_object()
        if instance.estado == "completado":
            return APIResponse.error(
                message="No se puede eliminar un calendario completado", status_code=400
            )
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "create":
            return CalendarioPagoCreateSerializer
        elif self.action == "retrieve":
            return CalendarioPagoDetailSerializer
        return CalendarioPagoListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = CalendarioPago.objects.select_related(
            "planilla", "usuario_programacion"
        ).order_by("fecha_pago_programada")

        # Filtros
        planilla_id = self.request.query_params.get("planilla_id")
        estado = self.request.query_params.get("estado")
        tipo_pago = self.request.query_params.get("tipo_pago")

        if planilla_id:
            queryset = queryset.filter(planilla_id=planilla_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo_pago:
            queryset = queryset.filter(tipo_pago=tipo_pago)

        return queryset
