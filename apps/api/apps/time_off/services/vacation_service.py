"""Servicios principales del módulo de vacaciones."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from apps.employees.models import Employee
from apps.identity.models import User
from ..models import (
    VacationConfiguration,
    VacationRequestHistory,
    VacationPeriod,
    VacationRequest,
)
from apps.core.tasks import send_email_html_task
from apps.core.exceptions import BusinessLogicError
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from .vacation_calculation_service import VacationCalculationService

logger = logging.getLogger(__name__)


class VacationService:
    """Servicio de solicitudes y periodos de vacaciones."""

    @staticmethod
    def _obtener_email_jefe(jefe: Employee) -> Optional[str]:
        usuario = User.objects.filter(empleado=jefe).first()
        if usuario and usuario.email:
            return usuario.email
        return jefe.correo_personal

    @staticmethod
    def _enviar_notificacion_jefe(solicitud: VacationRequest) -> bool:
        jefe = solicitud.jefe_aprobador
        if not jefe:
            return False

        destinatario = VacationService._obtener_email_jefe(jefe)
        if not destinatario:
            logger.warning("Jefe sin email para solicitud %s", solicitud.solicitud_id)
            return False

        empleado = solicitud.empleado
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        url_solicitudes = f"{frontend_url}/vacaciones/solicitudes"

        context = {
            "jefe_nombre": jefe.nombre_completo,
            "empleado_nombre": empleado.nombre_completo,
            "fecha_inicio": solicitud.fecha_inicio,
            "fecha_fin": solicitud.fecha_fin,
            "dias_solicitados": solicitud.dias_solicitados,
            "medio_dia": solicitud.medio_dia,
            "motivo": solicitud.motivo_solicitud or "",
            "url_solicitudes": url_solicitudes,
        }

        subject = "Nueva solicitud de vacaciones"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@vyntia.pe")
        text_content = render_to_string("emails/vacaciones_solicitud.txt", context)
        html_content = render_to_string("emails/vacaciones_solicitud.html", context)

        try:
            send_email_html_task.delay(
                subject=subject,
                from_email=from_email,
                recipients=[destinatario],
                text_content=text_content,
                html_content=html_content,
            )
            logger.info("Notificación encolada para %s", destinatario)
            return True
        except Exception as exc:
            logger.error("Error encolando notificación de solicitud: %s", exc)
            return False

    @staticmethod
    def obtener_configuracion_activa(
        empleado: Optional[Employee] = None,
    ) -> Optional[VacationConfiguration]:
        fecha_ref = date.today()
        if empleado:
            return VacationCalculationService.obtener_configuracion_aplicable(
                empleado, fecha_ref
            )
        return (
            VacationConfiguration.objects.filter(
                area__isnull=True,
                empleado__isnull=True,
                activo=True,
                fecha_inicio_vigencia__lte=fecha_ref,
            )
            .filter(
                Q(fecha_fin_vigencia__isnull=True)
                | Q(fecha_fin_vigencia__gte=fecha_ref)
            )
            .first()
        )

    @staticmethod
    def _generar_periodo_para_fecha(
        empleado: Employee, fecha_ref: date
    ) -> VacationPeriod:
        contrato = VacationCalculationService.obtener_contrato_para_fecha(
            empleado, fecha_ref
        )
        if not contrato:
            raise BusinessLogicError(
                "El empleado no tiene contrato activo para la fecha solicitada.",
                error_code="CONTRACT_NOT_FOUND",
            )

        inicio, fin = VacationCalculationService.construir_periodo_aniversario(
            contrato.fecha_inicio, fecha_ref
        )
        ano_periodo = inicio.year

        config = VacationCalculationService.obtener_configuracion_aplicable(
            empleado, fecha_ref
        )
        if not config:
            raise BusinessLogicError(
                "No existe configuración de vacaciones activa.",
                error_code="NO_VACATION_CONFIG",
            )

        periodo, created = VacationPeriod.objects.get_or_create(
            empleado=empleado,
            ano_periodo=ano_periodo,
            contrato=contrato,
            defaults={
                "fecha_inicio_periodo": inicio,
                "fecha_fin_periodo": fin,
                "fecha_vencimiento": fin + timedelta(days=365),
                "dias_correspondientes": Decimal(str(config.dias_por_ano or 30)),
                "dias_adicionales": Decimal("0.0"),
                "dias_totales": Decimal(str(config.dias_por_ano or 30)),
                "dias_gozados": Decimal("0.0"),
                "dias_pendientes": Decimal(str(config.dias_por_ano or 30)),
                "dias_vencidos": Decimal("0.0"),
                "estado_periodo": "activo",
                "configuracion": config,
                "contrato": contrato,
            },
        )

        if created:
            logger.info(
                "Período vacacional creado para %s (%s-%s)",
                empleado.nombre_completo,
                inicio,
                fin,
            )
        return periodo

    @staticmethod
    def obtener_o_crear_periodo(
        empleado: Employee, fecha_ref: Optional[date] = None
    ) -> VacationPeriod:
        """Obtiene o crea periodo por aniversario según contrato activo en fecha."""
        return VacationService._generar_periodo_para_fecha(
            empleado, fecha_ref or date.today()
        )

    @staticmethod
    def validar_solicitud_vacaciones(data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y normaliza una solicitud de vacaciones."""
        empleado: Employee = data.get("empleado")
        fecha_inicio: date = data.get("fecha_inicio")
        fecha_fin: date = data.get("fecha_fin")
        tipo_solicitud = data.get("tipo_solicitud") or "vacaciones"

        if not empleado or not fecha_inicio or not fecha_fin:
            raise BusinessLogicError(
                "Employee, fecha de inicio y fecha de fin son obligatorios.",
                error_code="MISSING_REQUIRED_DATA",
            )

        configuracion = VacationCalculationService.obtener_configuracion_aplicable(
            empleado, fecha_inicio
        )
        if not configuracion:
            raise BusinessLogicError(
                "No existe configuración de vacaciones activa para el empleado.",
                error_code="NO_VACATION_CONFIG",
            )

        validacion = VacationCalculationService.validar_fechas_solicitud(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            empleado=empleado,
            configuracion=configuracion,
            tipo_solicitud=tipo_solicitud,
            medio_dia=bool(data.get("medio_dia")),
        )
        if not validacion["valido"]:
            raise BusinessLogicError(
                " | ".join(validacion["errores"]),
                error_code="INVALID_REQUEST",
            )

        periodo_vacacional = data.get("periodo_vacacional")
        if not periodo_vacacional:
            periodo_vacacional = VacationService.obtener_o_crear_periodo(
                empleado, fecha_inicio
            )

        contrato = periodo_vacacional.contrato
        if not contrato:
            raise BusinessLogicError(
                "El período vacacional no tiene contrato asociado.",
                error_code="CONTRACT_NOT_LINKED",
            )
        if contrato.status != "ACTIVO":
            raise BusinessLogicError(
                "El contrato asociado al período no está activo.",
                error_code="CONTRACT_NOT_ACTIVE",
            )
        if fecha_inicio < contrato.fecha_inicio or (
            contrato.fecha_fin and fecha_inicio > contrato.fecha_fin
        ):
            raise BusinessLogicError(
                "La fecha de solicitud no corresponde al contrato activo.",
                error_code="CONTRACT_DATE_MISMATCH",
            )

        if not (
            periodo_vacacional.fecha_inicio_periodo
            <= fecha_inicio
            <= periodo_vacacional.fecha_fin_periodo
        ):
            raise BusinessLogicError(
                "La fecha de inicio no corresponde al período vacacional seleccionado.",
                error_code="PERIOD_MISMATCH",
            )

        return {
            "empleado": empleado,
            "periodo_vacacional": periodo_vacacional,
            "tipo_solicitud": tipo_solicitud,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "dias_solicitados": validacion["dias_solicitados"],
            "motivo_solicitud": data.get("motivo_solicitud", ""),
            "observaciones_empleado": data.get("observaciones_empleado", ""),
            "configuracion": configuracion,
            "medio_dia": bool(data.get("medio_dia")),
        }

    @staticmethod
    @transaction.atomic
    def crear_solicitud_vacaciones(
        data: Dict[str, Any], usuario_creador: User
    ) -> VacationRequest:
        """Crea solicitud en borrador."""
        datos = VacationService.validar_solicitud_vacaciones(data)

        solicitud = VacationRequest.objects.create(
            empleado=datos["empleado"],
            periodo_vacacional=datos["periodo_vacacional"],
            tipo_solicitud=datos["tipo_solicitud"],
            fecha_inicio=datos["fecha_inicio"],
            fecha_fin=datos["fecha_fin"],
            dias_solicitados=datos["dias_solicitados"],
            motivo_solicitud=datos["motivo_solicitud"],
            observaciones_empleado=datos["observaciones_empleado"],
            estado_solicitud="borrador",
            medio_dia=datos.get("medio_dia", False),
        )

        VacationRequestHistory.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="creacion",
            descripcion_accion=f"Solicitud creada por {usuario_creador.nombre_completo}",
            usuario_accion=usuario_creador,
            estado_nuevo="borrador",
        )
        return solicitud

    @staticmethod
    @transaction.atomic
    def enviar_solicitud(solicitud_id: int, usuario: User) -> VacationRequest:
        """Envía solicitud a flujo de aprobación."""
        try:
            solicitud = VacationRequest.objects.select_for_update().get(
                solicitud_id=solicitud_id
            )
        except VacationRequest.DoesNotExist as exc:
            raise BusinessLogicError(
                "Solicitud no encontrada.", error_code="REQUEST_NOT_FOUND"
            ) from exc

        if solicitud.estado_solicitud != "borrador":
            raise BusinessLogicError(
                "Solo se puede enviar una solicitud en borrador.",
                error_code="INVALID_STATE",
            )

        if (
            solicitud.empleado != getattr(usuario, "empleado", None)
            and not usuario.es_admin_rrhh
        ):
            raise BusinessLogicError(
                "No tiene permisos para enviar esta solicitud.",
                error_code="PERMISSION_DENIED",
            )

        config = VacationCalculationService.obtener_configuracion_aplicable(
            solicitud.empleado, solicitud.fecha_inicio
        )
        if not config:
            raise BusinessLogicError(
                "No hay configuración activa.", error_code="NO_VACATION_CONFIG"
            )

        estado_anterior = solicitud.estado_solicitud
        if config.requiere_aprobacion_jefe:
            solicitud.estado_solicitud = "en_revision"
            datos_laborales = solicitud.empleado.datos_laborales_actuales()
            solicitud.jefe_aprobador = (
                datos_laborales.jefe_directo if datos_laborales else None
            )
        elif config.requiere_aprobacion_rrhh:
            solicitud.estado_solicitud = "aprobada_jefe"
        else:
            solicitud.estado_solicitud = "aprobada"
            VacationService.descontar_dias_periodo(
                solicitud.periodo_vacacional, solicitud.dias_solicitados
            )

        solicitud.fecha_envio = timezone.now()
        solicitud.save()

        VacationRequestHistory.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="envio",
            descripcion_accion=f"Solicitud enviada. Estado: {estado_anterior} -> {solicitud.estado_solicitud}",
            usuario_accion=usuario,
            estado_anterior=estado_anterior,
            estado_nuevo=solicitud.estado_solicitud,
        )

        if solicitud.estado_solicitud == "en_revision" and solicitud.jefe_aprobador:
            VacationService._enviar_notificacion_jefe(solicitud)

        return solicitud

    @staticmethod
    def descontar_dias_periodo(periodo: VacationPeriod, dias: Decimal) -> None:
        """Descuenta días al confirmar aprobación final."""
        if dias <= 0:
            return
        periodo.dias_gozados = max(Decimal("0.0"), periodo.dias_gozados + dias)
        periodo.dias_pendientes = max(
            Decimal("0.0"), periodo.dias_totales - periodo.dias_gozados
        )
        periodo.save(
            update_fields=["dias_gozados", "dias_pendientes", "updated_at"]
        )
