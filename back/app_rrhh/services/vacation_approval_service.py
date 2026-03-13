"""Servicios para aprobaciones de vacaciones."""

import logging
from typing import List

from app_rrhh.constants import Roles
from app_rrhh.models import Empleado, Usuario
from app_rrhh.models.vacaciones import HistorialSolicitudVacaciones, SolicitudVacaciones
from app_rrhh.permission_service import PermissionService
from core.exceptions import BusinessLogicError
from django.db import transaction
from django.utils import timezone

from .vacation_calculation_service import VacationCalculationService
from .vacation_service import VacationService

logger = logging.getLogger(__name__)


class VacationApprovalService:
    """Flujo de aprobaciones por jefe y RRHH."""

    @staticmethod
    def _usuario_es_rrhh_admin(usuario: Usuario) -> bool:
        return PermissionService.has_any_role(usuario, Roles.HR_ROLES)

    @staticmethod
    def _usuario_es_jefe_del_empleado(usuario: Usuario, empleado: Empleado) -> bool:
        if not hasattr(usuario, "empleado") or not usuario.empleado:
            return False
        return empleado.datos_laborales.filter(
            estado_datos="activo",
            jefe_directo=usuario.empleado,
        ).exists()

    @staticmethod
    def validar_permisos_aprobacion(
        solicitud: SolicitudVacaciones, usuario: Usuario, tipo_aprobacion: str
    ) -> bool:
        if tipo_aprobacion == "jefe":
            if not (
                VacationApprovalService._usuario_es_rrhh_admin(usuario)
                or VacationApprovalService._usuario_es_jefe_del_empleado(
                    usuario, solicitud.empleado
                )
            ):
                raise BusinessLogicError(
                    "No tiene permisos para aprobar como jefe esta solicitud.",
                    error_code="INSUFFICIENT_PERMISSIONS_BOSS",
                )
            if solicitud.estado_solicitud != "en_revision":
                raise BusinessLogicError(
                    "La solicitud no está pendiente de aprobación de jefe.",
                    error_code="INVALID_STATE_FOR_BOSS_APPROVAL",
                )
            return True

        if tipo_aprobacion == "rrhh":
            if not VacationApprovalService._usuario_es_rrhh_admin(usuario):
                raise BusinessLogicError(
                    "No tiene permisos para aprobar como RRHH.",
                    error_code="INSUFFICIENT_PERMISSIONS_RRHH",
                )
            if solicitud.estado_solicitud not in ["aprobada_jefe", "en_revision"]:
                raise BusinessLogicError(
                    "La solicitud no está pendiente de aprobación de RRHH.",
                    error_code="INVALID_STATE_FOR_RRHH_APPROVAL",
                )
            return True

        raise BusinessLogicError(
            "Tipo de aprobación inválido.", error_code="INVALID_APPROVAL_TYPE"
        )

    @staticmethod
    @transaction.atomic
    def aprobar_por_jefe(
        solicitud_id: int, usuario_jefe: Usuario, observaciones: str = ""
    ) -> SolicitudVacaciones:
        solicitud = SolicitudVacaciones.objects.select_for_update().get(
            solicitud_id=solicitud_id
        )
        VacationApprovalService.validar_permisos_aprobacion(
            solicitud, usuario_jefe, "jefe"
        )

        config = VacationCalculationService.obtener_configuracion_aplicable(
            solicitud.empleado, solicitud.fecha_inicio
        )
        if not config:
            raise BusinessLogicError(
                "No hay configuración activa.", error_code="NO_VACATION_CONFIG"
            )

        estado_anterior = solicitud.estado_solicitud
        solicitud.aprobado_por_jefe = True
        solicitud.jefe_aprobador = getattr(usuario_jefe, "empleado", None)
        solicitud.fecha_aprobacion_jefe = timezone.now()
        solicitud.observaciones_jefe = observaciones

        if config.requiere_aprobacion_rrhh:
            solicitud.estado_solicitud = "aprobada_jefe"
        else:
            solicitud.estado_solicitud = "aprobada"
            VacationService.descontar_dias_periodo(
                solicitud.periodo_vacacional, solicitud.dias_solicitados
            )

        solicitud.save()

        HistorialSolicitudVacaciones.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="aprobacion_jefe",
            descripcion_accion=f"Aprobada por jefe: {usuario_jefe.nombre_completo}",
            usuario_accion=usuario_jefe,
            observaciones=observaciones,
            estado_anterior=estado_anterior,
            estado_nuevo=solicitud.estado_solicitud,
        )
        return solicitud

    @staticmethod
    @transaction.atomic
    def aprobar_por_rrhh(
        solicitud_id: int, usuario_rrhh: Usuario, observaciones: str = ""
    ) -> SolicitudVacaciones:
        solicitud = SolicitudVacaciones.objects.select_for_update().get(
            solicitud_id=solicitud_id
        )
        VacationApprovalService.validar_permisos_aprobacion(
            solicitud, usuario_rrhh, "rrhh"
        )

        estado_anterior = solicitud.estado_solicitud
        solicitud.aprobado_por_rrhh = True
        solicitud.rrhh_aprobador = usuario_rrhh
        solicitud.fecha_aprobacion_rrhh = timezone.now()
        solicitud.observaciones_rrhh = observaciones
        solicitud.estado_solicitud = "aprobada"
        solicitud.save()

        VacationService.descontar_dias_periodo(
            solicitud.periodo_vacacional, solicitud.dias_solicitados
        )

        HistorialSolicitudVacaciones.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="aprobacion_rrhh",
            descripcion_accion=f"Aprobada por RRHH: {usuario_rrhh.nombre_completo}",
            usuario_accion=usuario_rrhh,
            observaciones=observaciones,
            estado_anterior=estado_anterior,
            estado_nuevo="aprobada",
        )
        return solicitud

    @staticmethod
    @transaction.atomic
    def rechazar_solicitud(
        solicitud_id: int,
        usuario: Usuario,
        motivo_rechazo: str,
        tipo_rechazo: str = "jefe",
    ) -> SolicitudVacaciones:
        if not motivo_rechazo:
            raise BusinessLogicError(
                "Debe registrar motivo de rechazo.",
                error_code="MISSING_REJECTION_REASON",
            )

        solicitud = SolicitudVacaciones.objects.select_for_update().get(
            solicitud_id=solicitud_id
        )
        VacationApprovalService.validar_permisos_aprobacion(
            solicitud, usuario, "jefe" if tipo_rechazo == "jefe" else "rrhh"
        )

        estado_anterior = solicitud.estado_solicitud
        solicitud.estado_solicitud = "rechazada"
        solicitud.motivo_rechazo = motivo_rechazo
        solicitud.fecha_rechazo = timezone.now()
        if tipo_rechazo == "jefe":
            solicitud.observaciones_jefe = motivo_rechazo
        else:
            solicitud.observaciones_rrhh = motivo_rechazo
        solicitud.save()

        HistorialSolicitudVacaciones.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="rechazo",
            descripcion_accion=f"Solicitud rechazada por {tipo_rechazo}.",
            usuario_accion=usuario,
            observaciones=motivo_rechazo,
            estado_anterior=estado_anterior,
            estado_nuevo="rechazada",
        )
        return solicitud

    @staticmethod
    @transaction.atomic
    def cancelar_solicitud(
        solicitud_id: int, usuario: Usuario, motivo_cancelacion: str
    ) -> SolicitudVacaciones:
        solicitud = SolicitudVacaciones.objects.select_for_update().get(
            solicitud_id=solicitud_id
        )
        if solicitud.estado_solicitud in ["finalizada", "cancelada", "rechazada"]:
            raise BusinessLogicError(
                "La solicitud no puede cancelarse en su estado actual.",
                error_code="CANNOT_CANCEL",
            )

        if (
            solicitud.empleado != getattr(usuario, "empleado", None)
            and not usuario.es_admin_rrhh
        ):
            raise BusinessLogicError(
                "No tiene permisos para cancelar esta solicitud.",
                error_code="PERMISSION_DENIED",
            )

        estado_anterior = solicitud.estado_solicitud
        solicitud.estado_solicitud = "cancelada"
        solicitud.motivo_cancelacion = motivo_cancelacion or ""
        solicitud.fecha_cancelacion = timezone.now()
        solicitud.cancelado_por = usuario
        solicitud.save()

        HistorialSolicitudVacaciones.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion="cancelacion",
            descripcion_accion=f"Solicitud cancelada por {usuario.nombre_completo}.",
            usuario_accion=usuario,
            observaciones=motivo_cancelacion,
            estado_anterior=estado_anterior,
            estado_nuevo="cancelada",
        )
        return solicitud

    @staticmethod
    def obtener_solicitudes_pendientes_jefe(
        usuario_jefe: Usuario,
    ) -> List[SolicitudVacaciones]:
        if VacationApprovalService._usuario_es_rrhh_admin(usuario_jefe):
            return list(
                SolicitudVacaciones.objects.filter(estado_solicitud="en_revision")
                .select_related("empleado", "periodo_vacacional")
                .order_by("-fecha_envio", "-fecha_creacion")
            )

        if not getattr(usuario_jefe, "empleado", None):
            return []

        subordinados = Empleado.objects.filter(
            datos_laborales__jefe_directo=usuario_jefe.empleado,
            datos_laborales__estado_datos="activo",
        ).distinct()
        return list(
            SolicitudVacaciones.objects.filter(
                estado_solicitud="en_revision",
                empleado__in=subordinados,
            )
            .select_related("empleado", "periodo_vacacional")
            .order_by("-fecha_envio", "-fecha_creacion")
        )

    @staticmethod
    def obtener_solicitudes_pendientes_rrhh(
        usuario_rrhh: Usuario,
    ) -> List[SolicitudVacaciones]:
        if not VacationApprovalService._usuario_es_rrhh_admin(usuario_rrhh):
            raise BusinessLogicError(
                "No tiene permisos para ver pendientes RRHH.",
                error_code="PERMISSION_DENIED",
            )
        return list(
            SolicitudVacaciones.objects.filter(estado_solicitud="aprobada_jefe")
            .select_related("empleado", "periodo_vacacional")
            .order_by("-fecha_envio", "-fecha_creacion")
        )

    # Alias para compatibilidad con llamadas existentes en views.
    aprobar_solicitud_jefe = aprobar_por_jefe
    aprobar_solicitud_rrhh = aprobar_por_rrhh
