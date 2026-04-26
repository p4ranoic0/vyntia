"""Servicios de cálculo para el módulo de vacaciones."""

import logging
from datetime import date, timedelta
from typing import Dict, Optional, Any, Tuple

from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Q, Sum

from app_rrhh.models import ContratosAdendas, Empleado
from app_rrhh.models.vacaciones import ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones
from apps.core.exceptions import BusinessLogicError

logger = logging.getLogger(__name__)


class VacationCalculationService:
    """Motor de cálculo de periodos, días solicitados y adelantos."""

    DIAS_ANUALES_DEFAULT = 30
    DIAS_ADELANTO_POR_MES = 2.5

    @staticmethod
    def obtener_contrato_activo(empleado: Empleado) -> Optional[ContratosAdendas]:
        """Retorna el contrato activo más reciente del empleado."""
        return (
            ContratosAdendas.objects.filter(
                empleado=empleado,
                tipo_documento__startswith='CONTRATO',
                estado='ACTIVO',
            )
            .order_by('-fecha_inicio', '-contrato_id')
            .first()
        )

    @staticmethod
    def obtener_contrato_para_fecha(empleado: Empleado, fecha_ref: date) -> Optional[ContratosAdendas]:
        """Retorna el contrato que cubre una fecha dada."""
        return (
            ContratosAdendas.objects.filter(
                empleado=empleado,
                tipo_documento__startswith='CONTRATO',
                fecha_inicio__lte=fecha_ref,
            )
            .filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_ref))
            .order_by('-fecha_inicio', '-contrato_id')
            .first()
        )

    @staticmethod
    def obtener_configuracion_aplicable(empleado: Empleado, fecha_ref: date) -> Optional[ConfiguracionVacaciones]:
        """Obtiene configuración aplicable con prioridad empleado > área > general."""
        config = (
            ConfiguracionVacaciones.objects.filter(
                empleado=empleado,
                activo=True,
                fecha_inicio_vigencia__lte=fecha_ref,
            )
            .filter(Q(fecha_fin_vigencia__isnull=True) | Q(fecha_fin_vigencia__gte=fecha_ref))
            .first()
        )
        if config:
            return config

        datos_laborales = empleado.datos_laborales_actuales()
        if datos_laborales and datos_laborales.area:
            config = (
                ConfiguracionVacaciones.objects.filter(
                    area=datos_laborales.area,
                    empleado__isnull=True,
                    activo=True,
                    fecha_inicio_vigencia__lte=fecha_ref,
                )
                .filter(Q(fecha_fin_vigencia__isnull=True) | Q(fecha_fin_vigencia__gte=fecha_ref))
                .first()
            )
            if config:
                return config

        return (
            ConfiguracionVacaciones.objects.filter(
                area__isnull=True,
                empleado__isnull=True,
                activo=True,
                fecha_inicio_vigencia__lte=fecha_ref,
            )
            .filter(Q(fecha_fin_vigencia__isnull=True) | Q(fecha_fin_vigencia__gte=fecha_ref))
            .first()
        )

    @staticmethod
    def construir_periodo_aniversario(fecha_inicio_base: date, fecha_ref: date) -> Tuple[date, date]:
        """
        Calcula el periodo anual por aniversario.
        Ejemplo: ingreso 2025-04-15 => periodo 2025-04-15 a 2026-04-14.
        """
        aniversario_ref = date(fecha_ref.year, fecha_inicio_base.month, fecha_inicio_base.day)
        if fecha_ref < aniversario_ref:
            inicio = date(fecha_ref.year - 1, fecha_inicio_base.month, fecha_inicio_base.day)
        else:
            inicio = aniversario_ref
        fin = (inicio + relativedelta(years=1)) - timedelta(days=1)
        return inicio, fin

    @staticmethod
    def calcular_dias_habiles(
        fecha_inicio: date,
        fecha_fin: date,
        incluye_feriados: bool = True,
        incluye_fines_semana: bool = True,
    ) -> int:
        """Calcula días descontables, incluyendo la regla especial de viernes."""
        if fecha_inicio > fecha_fin:
            return 0

        if incluye_fines_semana:
            dias = (fecha_fin - fecha_inicio).days + 1
        else:
            dias = 0
            fecha = fecha_inicio
            while fecha <= fecha_fin:
                if fecha.weekday() < 5:
                    dias += 1
                fecha += timedelta(days=1)

        # Regla de negocio: si inicia o termina viernes, se contabiliza sábado y domingo.
        extra_dates = []
        if fecha_inicio.weekday() == 4:
            extra_dates.extend([fecha_inicio + timedelta(days=1), fecha_inicio + timedelta(days=2)])
        if fecha_fin.weekday() == 4 and fecha_fin != fecha_inicio:
            extra_dates.extend([fecha_fin + timedelta(days=1), fecha_fin + timedelta(days=2)])

        extra = 0
        for extra_date in extra_dates:
            in_range = fecha_inicio <= extra_date <= fecha_fin
            if in_range and incluye_fines_semana:
                continue
            if in_range and not incluye_fines_semana and extra_date.weekday() < 5:
                continue
            extra += 1

        return dias + extra

    @staticmethod
    def calcular_dias_correspondientes(
        empleado: Empleado,
        fecha_ref: date,
        configuracion: Optional[ConfiguracionVacaciones] = None,
    ) -> int:
        """Días anuales de vacaciones por periodo. Base 30, configurable."""
        if not configuracion:
            configuracion = VacationCalculationService.obtener_configuracion_aplicable(empleado, fecha_ref)
        if not configuracion:
            return VacationCalculationService.DIAS_ANUALES_DEFAULT
        return int(configuracion.dias_por_ano or VacationCalculationService.DIAS_ANUALES_DEFAULT)

    @staticmethod
    def calcular_adelanto_disponible(empleado: Empleado, fecha_ref: date, contrato: Optional[ContratosAdendas] = None) -> float:
        """
        Adelanto vacacional: 2.5 días por mes cumplido en el contrato vigente.
        Descuenta los adelantos ya aprobados.
        """
        contrato_ref = contrato or VacationCalculationService.obtener_contrato_para_fecha(empleado, fecha_ref)
        if not contrato_ref:
            return 0.0

        if fecha_ref < contrato_ref.fecha_inicio:
            return 0.0

        delta = relativedelta(fecha_ref, contrato_ref.fecha_inicio)
        meses_completos = max(0, (delta.years * 12) + delta.months)
        acumulado = Decimal(str(meses_completos)) * Decimal(str(VacationCalculationService.DIAS_ADELANTO_POR_MES))

        usados = (
            SolicitudVacaciones.objects.filter(
                empleado=empleado,
                tipo_solicitud='adelanto_vacaciones',
                estado_solicitud__in=['aprobada_jefe', 'aprobada_rrhh', 'aprobada', 'en_goce', 'finalizada'],
            ).aggregate(total=Sum('dias_solicitados'))['total']
            or 0
        )
        return max(Decimal('0.0'), acumulado - Decimal(str(usados)))

    @staticmethod
    def verificar_solapamiento(
        empleado: Empleado,
        fecha_inicio: date,
        fecha_fin: date,
        excluir_solicitud_id: Optional[int] = None,
    ) -> bool:
        """Verifica solapamiento con solicitudes no canceladas/rechazadas."""
        qs = SolicitudVacaciones.objects.filter(
            empleado=empleado,
            fecha_inicio__lte=fecha_fin,
            fecha_fin__gte=fecha_inicio,
        ).exclude(estado_solicitud__in=['cancelada', 'rechazada'])
        if excluir_solicitud_id:
            qs = qs.exclude(solicitud_id=excluir_solicitud_id)
        return qs.exists()

    @staticmethod
    def validar_fechas_solicitud(
        fecha_inicio: date,
        fecha_fin: date,
        empleado: Empleado,
        configuracion: Optional[ConfiguracionVacaciones] = None,
        tipo_solicitud: str = 'vacaciones',
        medio_dia: bool = False,
    ) -> Dict[str, Any]:
        """Valida fechas y calcula días solicitados/disponibilidad."""
        errores = []
        advertencias = []
        hoy = date.today()

        if fecha_inicio > fecha_fin:
            errores.append('La fecha de inicio no puede ser posterior a la fecha de fin.')
        if fecha_inicio < hoy:
            errores.append('No se pueden solicitar vacaciones para fechas pasadas.')

        if not configuracion:
            configuracion = VacationCalculationService.obtener_configuracion_aplicable(empleado, fecha_inicio)

        incluye_fines_semana = True if not configuracion else bool(configuracion.incluye_fines_semana)
        incluye_feriados = True if not configuracion else bool(configuracion.incluye_feriados)
        if medio_dia:
            if fecha_inicio != fecha_fin:
                errores.append('La opción de medio día solo aplica cuando la fecha de inicio y fin son iguales.')
            dias_solicitados = Decimal('0.5')
        else:
            dias_solicitados = Decimal(
                str(
                    VacationCalculationService.calcular_dias_habiles(
                        fecha_inicio=fecha_inicio,
                        fecha_fin=fecha_fin,
                        incluye_feriados=incluye_feriados,
                        incluye_fines_semana=incluye_fines_semana,
                    )
                )
            )

        if configuracion:
            if dias_solicitados < configuracion.dias_minimos_solicitud:
                if not medio_dia:
                    errores.append(f'Debe solicitar al menos {configuracion.dias_minimos_solicitud} días.')
            if dias_solicitados > configuracion.dias_maximos_solicitud:
                errores.append(f'No puede solicitar más de {configuracion.dias_maximos_solicitud} días.')
            anticipacion = (fecha_inicio - hoy).days
            if anticipacion < configuracion.dias_anticipacion_minima:
                errores.append(
                    f'Debe solicitar con al menos {configuracion.dias_anticipacion_minima} días de anticipación.'
                )

        if VacationCalculationService.verificar_solapamiento(empleado, fecha_inicio, fecha_fin):
            errores.append('Existe una solicitud que se solapa en el rango de fechas.')

        # Validación de feriados desde settings (lista de fechas YYYY-MM-DD)
        feriados = getattr(settings, 'VACATION_HOLIDAYS', [])
        if feriados:
            feriados_set = {date.fromisoformat(f) for f in feriados}
            if any(fecha_inicio <= f <= fecha_fin for f in feriados_set):
                errores.append('El rango solicitado incluye feriados.')

        # Validación de descanso médico desde settings (lista de dicts)
        # Ejemplo: VACATION_MEDICAL_LEAVES = [{"empleado_id": 1, "inicio": "2025-06-01", "fin": "2025-06-10"}]
        medical_leaves = getattr(settings, 'VACATION_MEDICAL_LEAVES', [])
        for leave in medical_leaves:
            if leave.get('empleado_id') != getattr(empleado, 'empleado_id', None):
                continue
            try:
                leave_inicio = date.fromisoformat(leave.get('inicio'))
                leave_fin = date.fromisoformat(leave.get('fin'))
            except Exception:
                continue
            if fecha_inicio <= leave_fin and fecha_fin >= leave_inicio:
                errores.append('El rango solicitado coincide con un descanso médico.')
                break

        disponibilidad = {'suficientes': False, 'disponibles': Decimal('0.0')}
        if tipo_solicitud == 'adelanto_vacaciones':
            disponibles = VacationCalculationService.calcular_adelanto_disponible(empleado, fecha_inicio)
            disponibilidad = {
                'suficientes': disponibles >= dias_solicitados,
                'disponibles': round(float(disponibles), 2),
            }
            if not disponibilidad['suficientes']:
                errores.append(
                    f'Adelanto insuficiente. Disponible: {disponibilidad["disponibles"]}, solicitado: {dias_solicitados}.'
                )
        else:
            contrato = VacationCalculationService.obtener_contrato_para_fecha(empleado, fecha_inicio)
            periodo = None
            if contrato:
                periodo = PeriodoVacacional.objects.filter(
                    empleado=empleado,
                    contrato=contrato,
                    fecha_inicio_periodo__lte=fecha_inicio,
                    fecha_fin_periodo__gte=fecha_inicio,
                ).first()
            if periodo:
                disponibles = periodo.dias_pendientes
            else:
                disponibles = Decimal(
                    str(
                        VacationCalculationService.calcular_dias_correspondientes(
                            empleado=empleado,
                            fecha_ref=fecha_inicio,
                            configuracion=configuracion,
                        )
                    )
                )
            disponibilidad = {'suficientes': disponibles >= dias_solicitados, 'disponibles': float(disponibles)}
            if not disponibilidad['suficientes']:
                errores.append(f'Saldo insuficiente. Disponible: {disponibles}, solicitado: {dias_solicitados}.')

        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'advertencias': advertencias,
            'dias_solicitados': dias_solicitados,
            'disponibilidad': disponibilidad,
        }
