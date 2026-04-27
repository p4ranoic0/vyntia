# -*- coding: utf-8 -*-
"""
Views para el módulo de Remuneraciones.

Contiene los ViewSets para gestión de planillas mensuales,
boletas de pago, descuentos masivos y reportes de remuneraciones.
"""

from datetime import datetime, timedelta
from decimal import Decimal

from apps.payroll.models import (
    PaySlip,
    PaymentSchedule,
    AfpConfiguration,
    CompensationConfiguration,
    TaxParameter,
    MassDeduction,
    PayrollDetail,
    MonthlyPayroll,
)
from apps.employees.models import Employee
from apps.payroll.services import DescuentoMasivoService, PlanillaCalculoService
from apps.core.decorators import require_admin, require_authenticated, require_hr
from apps.core.pagination import StandardResultsSetPagination
from apps.core.responses import APIResponse
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

    queryset = AfpConfiguration.objects.all()
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
        queryset = AfpConfiguration.objects.order_by("-vigencia_mes", "afp_nombre")

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

    queryset = TaxParameter.objects.all()
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
        # Establecer created_by automáticamente
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)

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
            TaxParameter.objects.filter(anio=uit.anio).update(estado="inactivo")

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
        queryset = TaxParameter.objects.select_related("created_by").order_by(
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

    queryset = CompensationConfiguration.objects.all()
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
        queryset = CompensationConfiguration.objects.order_by("tipo", "orden", "nombre")

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

    queryset = MonthlyPayroll.objects.all()
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
        queryset = MonthlyPayroll.objects.select_related(
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
        import logging

        logger = logging.getLogger(__name__)
        planilla = self.get_object()

        if planilla.estado not in ["borrador", "procesando"]:
            return APIResponse.error(
                message="Solo se pueden generar planillas en estado borrador o procesando",
                status_code=400,
            )

        try:
            # Mapeo de modalidad de planilla a tipo_contrato de EmploymentData
            # Los datos reales en BD usan: CAS, CAP, locacion, consultoria
            MODALIDAD_A_TIPO_CONTRATO = {
                "plazo_indeterminado": ["CAP"],
                "plazo_determinado": ["CAS"],
                "subsidio": ["CAS", "CAP"],
                "locacion": ["locacion"],
                "consultoria": ["consultoria"],
            }

            # Obtener empleados activos con datos laborales
            empleados_qs = (
                Employee.objects.filter(
                    estado_empleado="activo",
                    datos_laborales__estado_datos="activo",
                )
                .prefetch_related("datos_laborales__area")
                .distinct()
            )

            # Filtrar por modalidad de contrato según planilla.modalidad
            tipos_contrato = MODALIDAD_A_TIPO_CONTRATO.get(planilla.modalidad)
            if tipos_contrato:
                empleados_qs = empleados_qs.filter(
                    datos_laborales__tipo_contrato__in=tipos_contrato,
                    datos_laborales__estado_datos="activo",
                )

            empleados = list(empleados_qs)
            logger.info(
                f"generar_planilla: modalidad={planilla.modalidad}, "
                f"tipos_contrato={tipos_contrato}, "
                f"empleados encontrados={len(empleados)}"
            )

            contador = 0
            for empleado in empleados:
                # Filtrar datos laborales activos por tipo de contrato
                dl_filter = empleado.datos_laborales.filter(estado_datos="activo")
                if tipos_contrato:
                    dl_filter = dl_filter.filter(tipo_contrato__in=tipos_contrato)
                datos_laborales = dl_filter.first()

                if not datos_laborales:
                    continue

                # Verificar si ya existe el detalle
                if PayrollDetail.objects.filter(
                    planilla=planilla, empleado=empleado
                ).exists():
                    continue

                # Crear detalle de planilla
                PayrollDetail.objects.create(
                    planilla=planilla,
                    empleado=empleado,
                    datos_laborales=datos_laborales,
                    area_nombre=(
                        datos_laborales.area.nombre_unidad_organica
                        if datos_laborales.area
                        else ""
                    ),
                    cargo=datos_laborales.cargo_empleado,
                    dni=empleado.numero_documento,
                    sistema_pensiones=empleado.sistema_pensiones,
                    tipo_comision_afp=empleado.tipo_comision or "",
                    remuneracion_basica=datos_laborales.sueldo_basico,
                    asignacion_familiar=datos_laborales.asignacion_familiar,
                    bonificacion_especial=datos_laborales.bonificacion_especial,
                    otras_bonificaciones=datos_laborales.otras_bonificaciones,
                )
                contador += 1

            if contador == 0:
                return APIResponse.error(
                    message="No se encontraron empleados activos para la modalidad seleccionada",
                    status_code=400,
                )

            # Actualizar estado de planilla
            planilla.estado = "generada"
            planilla.fecha_generacion = timezone.now()
            planilla.total_trabajadores = PayrollDetail.objects.filter(
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
            import traceback

            logger.error(f"Error generando planilla: {traceback.format_exc()}")
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
            detalles = PayrollDetail.objects.filter(planilla=planilla).select_related(
                "empleado", "datos_laborales"
            )

            # Calcular totales agregados para el resumen
            resumen = {
                "id": planilla.planilla_id,
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
                        "id": detalle.empleado.pk,
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

    @require_hr()
    @action(detail=True, methods=["post"])
    def generar_boletas(self, request, pk=None):
        """Genera boletas de pago para todos los detalles de una planilla aprobada."""
        planilla = self.get_object()

        if planilla.estado not in ["generada", "aprobada"]:
            return APIResponse.error(
                message="Solo se pueden generar boletas de planillas generadas o aprobadas",
                status_code=400,
            )

        detalles = PayrollDetail.objects.filter(planilla=planilla).select_related(
            "empleado"
        )

        if not detalles.exists():
            return APIResponse.error(
                message="La planilla no tiene detalles generados", status_code=400
            )

        creadas = 0
        existentes = 0
        for detalle in detalles:
            _, created = PaySlip.objects.get_or_create(
                detalle_planilla=detalle,
                defaults={"estado": "generada"},
            )
            if created:
                creadas += 1
            else:
                existentes += 1

        return APIResponse.success(
            message=f"Boletas generadas: {creadas} nuevas, {existentes} ya existían.",
            data={
                "id": planilla.planilla_id,
                "periodo": planilla.periodo,
                "boletas_creadas": creadas,
                "boletas_existentes": existentes,
                "total": creadas + existentes,
            },
        )

    @require_hr()
    @action(detail=True, methods=["post"])
    def regenerar(self, request, pk=None):
        """Resetea una planilla generada a borrador, elimina sus detalles y permite regenerar."""
        planilla = self.get_object()

        if planilla.estado in ["aprobada", "pagada"]:
            return APIResponse.error(
                message="No se puede regenerar una planilla aprobada o pagada",
                status_code=400,
            )

        # Eliminar detalles existentes
        eliminados = PayrollDetail.objects.filter(planilla=planilla).delete()[0]

        # Resetear estado
        planilla.estado = "borrador"
        planilla.total_trabajadores = 0
        planilla.total_remuneracion_bruta = Decimal("0.00")
        planilla.total_descuentos = Decimal("0.00")
        planilla.total_neto_pagar = Decimal("0.00")
        planilla.total_essalud = Decimal("0.00")
        planilla.total_aporte_afp = Decimal("0.00")
        planilla.total_onp = Decimal("0.00")
        planilla.fecha_generacion = None
        planilla.save()

        return APIResponse.success(
            message=f"Planilla reseteada. Se eliminaron {eliminados} detalles.",
            data=PlanillaMensualDetailSerializer(planilla).data,
        )

    @require_hr()
    @action(detail=False, methods=["get"])
    def diagnostico(self, request):
        """Endpoint temporal de diagnóstico para verificar datos de empleados."""
        from apps.contracts.models import EmploymentData

        total_empleados = Employee.objects.count()
        empleados_activos = Employee.objects.filter(estado_empleado="activo").count()
        dl_total = EmploymentData.objects.count()
        dl_activos = EmploymentData.objects.filter(estado_datos="activo").count()

        # Empleados activos con DL activos
        activos_con_dl = (
            Employee.objects.filter(
                estado_empleado="activo",
                datos_laborales__estado_datos="activo",
            )
            .distinct()
            .count()
        )

        # Estados únicos
        estados_emp = list(
            Employee.objects.values_list("estado_empleado", flat=True).distinct()
        )
        estados_dl = list(
            EmploymentData.objects.values_list("estado_datos", flat=True).distinct()
        )

        # Tipos de contrato con count
        tipos_contrato = list(
            EmploymentData.objects.filter(estado_datos="activo")
            .values("tipo_contrato")
            .annotate(cantidad=Count("id"))
            .order_by("tipo_contrato")
        )

        # Muestra de empleados activos
        muestra = list(
            Employee.objects.filter(estado_empleado="activo")[:5].values(
                "id",
                "numero_documento",
                "nombres_empleado",
                "apellido_paterno",
                "estado_empleado",
            )
        )

        # Planillas existentes
        planillas = list(
            MonthlyPayroll.objects.all()
            .values(
                "id",
                "periodo",
                "modalidad",
                "estado",
                "total_trabajadores",
                "total_remuneracion_bruta",
            )
            .order_by("-periodo")
        )

        # EmploymentData detalle con sueldo
        dl_detalle = list(
            EmploymentData.objects.filter(estado_datos="activo").values(
                "id",
                "id",
                "tipo_contrato",
                "sueldo_basico",
                "cargo_empleado",
            )
        )

        return APIResponse.success(
            data={
                "total_empleados": total_empleados,
                "empleados_activos": empleados_activos,
                "datos_laborales_total": dl_total,
                "datos_laborales_activos": dl_activos,
                "activos_con_dl_activos": activos_con_dl,
                "estados_empleado": estados_emp,
                "estados_datos_laborales": estados_dl,
                "tipos_contrato_activos": tipos_contrato,
                "muestra_empleados_activos": muestra,
                "planillas": planillas,
                "datos_laborales_activos_detalle": dl_detalle,
            }
        )

    @require_authenticated()
    @action(detail=True, methods=["get"])
    def estadisticas(self, request, pk=None):
        """Obtiene estadísticas de la planilla."""
        planilla = self.get_object()

        detalles = PayrollDetail.objects.filter(planilla=planilla)

        estadisticas = {
            "total_empleados": detalles.count(),
            "total_trabajadores": detalles.count(),
            "total_ingresos": float(planilla.total_remuneracion_bruta or 0),
            "total_descuentos": float(planilla.total_descuentos or 0),
            "total_neto": float(planilla.total_neto_pagar or 0),
            "total_essalud": float(planilla.total_essalud or 0),
            "total_afp": float(planilla.total_aporte_afp or 0),
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
                .annotate(cantidad=Count("id"))
                .order_by("-cantidad")
            ),
        }

        return APIResponse.success(data=estadisticas)


class DetallePlanillaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de detalles de planilla por empleado."""

    queryset = PayrollDetail.objects.all()
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
        queryset = PayrollDetail.objects.select_related(
            "planilla", "empleado", "datos_laborales"
        ).order_by("area_nombre", "empleado__apellido_paterno")

        # Filtros (acepta tanto planilla_id como planilla)
        planilla_id = self.request.query_params.get(
            "id"
        ) or self.request.query_params.get("planilla")
        empleado_id = self.request.query_params.get(
            "id"
        ) or self.request.query_params.get("empleado")
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

    queryset = MassDeduction.objects.all()
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
        queryset = MassDeduction.objects.select_related(
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
        Lee el archivo, valida los datos y crea los PayrollConcept correspondientes.
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

    queryset = PaySlip.objects.all()
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

    @require_authenticated()
    @action(detail=True, methods=["get"], url_path="pdf")
    def pdf(self, request, pk=None):
        """Descargar el PDF de una boleta de pago."""
        from django.http import HttpResponse

        boleta = self.get_object()

        if not boleta.archivo_pdf:
            # Generar un PDF básico con los datos de la boleta
            detalle = boleta.detalle_planilla
            empleado = detalle.empleado
            planilla = detalle.planilla

            content = (
                f"BOLETA DE PAGO\n"
                f"{'=' * 40}\n"
                f"Employee: {empleado.nombre_completo}\n"
                f"DNI: {empleado.numero_documento}\n"
                f"Periodo: {planilla.periodo}\n"
                f"{'=' * 40}\n"
                f"Remuneracion Basica: S/ {detalle.remuneracion_basica}\n"
                f"Total Ingresos: S/ {detalle.total_haberes}\n"
                f"Total Descuentos: S/ {detalle.total_descuentos}\n"
                f"Neto a Pagar: S/ {detalle.neto_pagar}\n"
            )
            response = HttpResponse(content.encode("utf-8"), content_type="text/plain")
            response["Content-Disposition"] = (
                f'attachment; filename="boleta-{boleta.boleta_id}.txt"'
            )

            boleta.estado = "descargada"
            boleta.fecha_descarga = timezone.now()
            boleta.save(update_fields=["estado", "fecha_descarga"])

            return response

        response = HttpResponse(
            boleta.archivo_pdf.read(), content_type="application/pdf"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="boleta-{boleta.boleta_id}.pdf"'
        )

        boleta.estado = "descargada"
        boleta.fecha_descarga = timezone.now()
        boleta.save(update_fields=["estado", "fecha_descarga"])

        return response

    @require_hr()
    @action(detail=False, methods=["get"], url_path="descarga-masiva")
    def descarga_masiva(self, request):
        """
        Descarga masiva de boletas de pago como ZIP.
        Parámetros: planilla_id (requerido), formato (opcional: pdf|txt, default txt).
        """
        import io
        import zipfile

        from django.http import HttpResponse

        planilla_id = request.query_params.get("id")
        if not planilla_id:
            return APIResponse.error(
                message="Se requiere el parámetro planilla_id", status_code=400
            )

        boletas = PaySlip.objects.filter(
            detalle_planilla__planilla_id=planilla_id
        ).select_related("detalle_planilla__empleado", "detalle_planilla__planilla")

        if not boletas.exists():
            return APIResponse.error(
                message="No se encontraron boletas para esta planilla",
                status_code=404,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for boleta in boletas:
                detalle = boleta.detalle_planilla
                empleado = detalle.empleado
                planilla = detalle.planilla
                nombre_archivo = (
                    f"boleta_{empleado.numero_documento}_"
                    f"{planilla.periodo.replace('-', '')}"
                )

                if boleta.archivo_pdf:
                    zf.writestr(f"{nombre_archivo}.pdf", boleta.archivo_pdf.read())
                else:
                    content = (
                        f"BOLETA DE PAGO\n"
                        f"{'=' * 50}\n"
                        f"Employee: {empleado.nombre_completo}\n"
                        f"DNI: {empleado.numero_documento}\n"
                        f"Periodo: {planilla.periodo}\n"
                        f"Modalidad: {planilla.get_modalidad_display()}\n"
                        f"{'=' * 50}\n\n"
                        f"INGRESOS\n"
                        f"{'-' * 50}\n"
                        f"Remuneración Básica:     S/ {detalle.remuneracion_basica:>10,.2f}\n"
                        f"Asignación Familiar:     S/ {detalle.asignacion_familiar:>10,.2f}\n"
                        f"Bonificación Especial:   S/ {detalle.bonificacion_especial:>10,.2f}\n"
                        f"Otras Bonificaciones:    S/ {detalle.otras_bonificaciones:>10,.2f}\n"
                        f"TOTAL INGRESOS:          S/ {detalle.total_haberes:>10,.2f}\n\n"
                        f"DESCUENTOS\n"
                        f"{'-' * 50}\n"
                        f"Sistema Pensiones: {detalle.sistema_pensiones}\n"
                        f"AFP Obligatorio:         S/ {detalle.aporte_afp_obligatorio:>10,.2f}\n"
                        f"Comisión AFP:            S/ {detalle.comision_afp:>10,.2f}\n"
                        f"Prima Seguro AFP:        S/ {detalle.prima_seguro_afp:>10,.2f}\n"
                        f"Total AFP:               S/ {detalle.total_afp:>10,.2f}\n"
                        f"Aporte ONP:              S/ {detalle.aporte_onp:>10,.2f}\n"
                        f"Renta 5ta Categoría:     S/ {detalle.renta_quinta_categoria:>10,.2f}\n"
                        f"TOTAL DESCUENTOS:        S/ {detalle.total_descuentos:>10,.2f}\n\n"
                        f"{'=' * 50}\n"
                        f"ESSALUD (empleador):     S/ {detalle.essalud:>10,.2f}\n"
                        f"NETO A PAGAR:            S/ {detalle.neto_pagar:>10,.2f}\n"
                    )
                    zf.writestr(f"{nombre_archivo}.txt", content.encode("utf-8"))

                # Marcar como descargada
                boleta.estado = "descargada"
                boleta.fecha_descarga = timezone.now()

            PaySlip.objects.filter(detalle_planilla__planilla_id=planilla_id).update(
                estado="descargada", fecha_descarga=timezone.now()
            )

        buffer.seek(0)
        planilla_obj = boletas.first().detalle_planilla.planilla
        filename = f"boletas_{planilla_obj.periodo}_{planilla_obj.modalidad}.zip"

        response = HttpResponse(buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "retrieve":
            return BoletaPagoDetailSerializer
        return BoletaPagoListSerializer

    def get_queryset(self):
        """Optimiza las consultas y aplica filtros."""
        queryset = PaySlip.objects.select_related(
            "detalle_planilla__planilla", "detalle_planilla__empleado"
        ).order_by("-fecha_generacion")

        # Si no es RRHH, solo ver sus propias boletas
        user = self.request.user
        if not user.groups.filter(name__in=["RRHH", "Administrador"]).exists():
            queryset = queryset.filter(detalle_planilla__empleado__usuario=user)

        # Filtros
        empleado_id = self.request.query_params.get("id")
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

    queryset = PaymentSchedule.objects.all()
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
        queryset = PaymentSchedule.objects.select_related(
            "planilla", "usuario_programacion"
        ).order_by("fecha_pago_programada")

        # Filtros
        planilla_id = self.request.query_params.get("id")
        estado = self.request.query_params.get("estado")
        tipo_pago = self.request.query_params.get("tipo_pago")

        if planilla_id:
            queryset = queryset.filter(planilla_id=planilla_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if tipo_pago:
            queryset = queryset.filter(tipo_pago=tipo_pago)

        return queryset
