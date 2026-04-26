"""Servicios administrativos del módulo de vacaciones."""

import logging
from datetime import date
from typing import Any, Dict, List, Optional

from django.db import transaction
from django.db.models import Avg, Case, Count, F, FloatField, Q, Sum, Value, When
from django.utils import timezone

from app_rrhh.models import Empleado
from apps.identity.models import Usuario
from app_rrhh.models.vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
from apps.core.exceptions import BusinessLogicError

from .vacation_service import VacationService
from decimal import Decimal

logger = logging.getLogger(__name__)


class VacationAdminService:
    """Operaciones administrativas: configuración, reportes y ajustes."""

    @staticmethod
    @transaction.atomic
    def crear_configuracion_vacaciones(data: Dict[str, Any], usuario_creador: Usuario) -> ConfiguracionVacaciones:
        if not usuario_creador.es_admin_rrhh:
            raise BusinessLogicError("No tiene permisos para crear configuraciones.", error_code="PERMISSION_DENIED")

        if not data.get('tipo_configuracion'):
            raise BusinessLogicError("tipo_configuracion es obligatorio.", error_code="MISSING_REQUIRED_FIELD")

        return ConfiguracionVacaciones.objects.create(
            tipo_configuracion=data['tipo_configuracion'],
            area=data.get('area'),
            empleado=data.get('empleado'),
            dias_por_ano=int(data.get('dias_por_ano', 30)),
            dias_adicionales_antiguedad=int(data.get('dias_adicionales_antiguedad', 0)),
            anos_para_adicional=int(data.get('anos_para_adicional', 5)),
            permite_acumulacion=bool(data.get('permite_acumulacion', True)),
            max_dias_acumulables=int(data.get('max_dias_acumulables', 60)),
            dias_minimos_solicitud=int(data.get('dias_minimos_solicitud', 1)),
            dias_maximos_solicitud=int(data.get('dias_maximos_solicitud', 30)),
            dias_anticipacion_minima=int(data.get('dias_anticipacion_minima', 0)),
            tipo_calculo=data.get('tipo_calculo', 'dias_calendario'),
            incluye_feriados=bool(data.get('incluye_feriados', True)),
            incluye_fines_semana=bool(data.get('incluye_fines_semana', True)),
            requiere_aprobacion_jefe=bool(data.get('requiere_aprobacion_jefe', True)),
            requiere_aprobacion_rrhh=bool(data.get('requiere_aprobacion_rrhh', True)),
            niveles_aprobacion=int(data.get('niveles_aprobacion', 2)),
            permite_fraccionamiento=bool(data.get('permite_fraccionamiento', True)),
            min_dias_por_fraccion=int(data.get('min_dias_por_fraccion', 5)),
            max_fracciones_por_ano=int(data.get('max_fracciones_por_ano', 3)),
            activo=bool(data.get('activo', True)),
            fecha_inicio_vigencia=data.get('fecha_inicio_vigencia') or date.today(),
            fecha_fin_vigencia=data.get('fecha_fin_vigencia'),
            observaciones=data.get('observaciones'),
            creado_por=usuario_creador,
        )

    @staticmethod
    @transaction.atomic
    def actualizar_configuracion_vacaciones(
        configuracion_id: int,
        data: Dict[str, Any],
        usuario: Usuario,
    ) -> ConfiguracionVacaciones:
        if not usuario.es_admin_rrhh:
            raise BusinessLogicError("No tiene permisos para actualizar configuraciones.", error_code="PERMISSION_DENIED")
        config = ConfiguracionVacaciones.objects.get(configuracion_id=configuracion_id)

        campos = [
            'dias_por_ano',
            'dias_adicionales_antiguedad',
            'anos_para_adicional',
            'permite_acumulacion',
            'max_dias_acumulables',
            'dias_minimos_solicitud',
            'dias_maximos_solicitud',
            'dias_anticipacion_minima',
            'tipo_calculo',
            'incluye_feriados',
            'incluye_fines_semana',
            'requiere_aprobacion_jefe',
            'requiere_aprobacion_rrhh',
            'niveles_aprobacion',
            'permite_fraccionamiento',
            'min_dias_por_fraccion',
            'max_fracciones_por_ano',
            'activo',
            'fecha_fin_vigencia',
            'observaciones',
        ]
        for campo in campos:
            if campo in data:
                setattr(config, campo, data[campo])
        config.save()
        return config

    @staticmethod
    @transaction.atomic
    def generar_periodos_masivos(ano: int, empleados_ids: List[int], usuario: Usuario) -> Dict[str, Any]:
        if not usuario.es_admin_rrhh:
            raise BusinessLogicError("No tiene permisos para generar periodos masivos.", error_code="PERMISSION_DENIED")

        resultados = {
            'exitosos': [],
            'errores': [],
            'total_procesados': 0,
            'total_exitosos': 0,
            'total_errores': 0,
        }

        fecha_ref = date(ano, 1, 1)
        for empleado in Empleado.objects.filter(empleado_id__in=empleados_ids, estado_empleado='activo'):
            resultados['total_procesados'] += 1
            try:
                periodo = VacationService.obtener_o_crear_periodo(empleado, fecha_ref)
                resultados['exitosos'].append(
                    {
                        'empleado_id': empleado.empleado_id,
                        'empleado_nombre': empleado.nombre_completo,
                        'periodo_id': periodo.periodo_id,
                        'periodo': f"{periodo.fecha_inicio_periodo:%Y-%m-%d} / {periodo.fecha_fin_periodo:%Y-%m-%d}",
                    }
                )
                resultados['total_exitosos'] += 1
            except Exception as exc:
                resultados['errores'].append(
                    {
                        'empleado_id': empleado.empleado_id,
                        'empleado_nombre': empleado.nombre_completo,
                        'error': str(exc),
                    }
                )
                resultados['total_errores'] += 1
        return resultados

    @staticmethod
    def obtener_estadisticas_vacaciones(ano: Optional[int] = None, area_id: Optional[int] = None) -> Dict[str, Any]:
        ano_ref = ano or date.today().year
        filtros = {'ano_periodo': ano_ref}

        if area_id:
            filtros['empleado__datos_laborales__area_id'] = area_id
            filtros['empleado__datos_laborales__estado_datos'] = 'activo'

        periodos = PeriodoVacacional.objects.filter(**filtros).distinct()
        solicitudes = SolicitudVacaciones.objects.filter(periodo_vacacional__in=periodos)
        goces = GoceVacaciones.objects.filter(periodo_vacacional__in=periodos)

        resumen_periodos = periodos.aggregate(
            total_empleados=Count('empleado', distinct=True),
            total_dias_correspondientes=Sum('dias_correspondientes'),
            total_dias_gozados=Sum('dias_gozados'),
            total_dias_pendientes=Sum('dias_pendientes'),
            total_dias_vencidos=Sum('dias_vencidos'),
            promedio_uso=Avg(
                Case(
                    When(dias_totales__gt=0, then=F('dias_gozados') * 100.0 / F('dias_totales')),
                    default=Value(0),
                    output_field=FloatField(),
                )
            ),
        )

        return {
            'ano': ano_ref,
            'area_id': area_id,
            'periodos': {
                'total_empleados': resumen_periodos['total_empleados'] or 0,
                'total_dias_correspondientes': resumen_periodos['total_dias_correspondientes'] or 0,
                'total_dias_gozados': resumen_periodos['total_dias_gozados'] or 0,
                'total_dias_pendientes': resumen_periodos['total_dias_pendientes'] or 0,
                'total_dias_vencidos': resumen_periodos['total_dias_vencidos'] or 0,
                'promedio_uso_porcentaje': round(resumen_periodos['promedio_uso'] or 0, 2),
            },
            'solicitudes': {
                'total_solicitudes': solicitudes.count(),
                'por_estado': {
                    fila['estado_solicitud']: fila['total']
                    for fila in solicitudes.values('estado_solicitud').annotate(total=Count('solicitud_id'))
                },
            },
            'goces': {
                'total_goces': goces.count(),
                'por_estado': {
                    fila['estado_goce']: fila['total']
                    for fila in goces.values('estado_goce').annotate(total=Count('goce_id'))
                },
            },
            'fecha_generacion': timezone.now().isoformat(),
        }

    @staticmethod
    def obtener_empleados_con_dias_vencidos(ano: Optional[int] = None) -> List[Dict[str, Any]]:
        ano_ref = ano or (date.today().year - 1)
        hoy = date.today()

        periodos = (
            PeriodoVacacional.objects.filter(ano_periodo=ano_ref)
            .filter(Q(fecha_vencimiento__lt=hoy) | Q(dias_vencidos__gt=0) | Q(dias_pendientes__gt=0))
            .select_related('empleado')
            .order_by('-dias_pendientes', '-dias_vencidos')
        )

        resultado: List[Dict[str, Any]] = []
        for periodo in periodos:
            datos_laborales = periodo.empleado.datos_laborales_actuales()
            dias_vencidos = periodo.dias_vencidos or (periodo.dias_pendientes if periodo.fecha_vencimiento < hoy else 0)
            resultado.append(
                {
                    'empleado_id': periodo.empleado.empleado_id,
                    'empleado_nombre': periodo.empleado.nombre_completo,
                    'empleado_rut': periodo.empleado.numero_documento,
                    'area_nombre': datos_laborales.area.nombre_area if datos_laborales and datos_laborales.area else 'Sin área',
                    'ano_periodo': periodo.ano_periodo,
                    'dias_correspondientes': periodo.dias_correspondientes,
                    'dias_gozados': periodo.dias_gozados,
                    'dias_vencidos': dias_vencidos,
                    'fecha_vencimiento': periodo.fecha_vencimiento,
                    'porcentaje_uso': periodo.porcentaje_uso,
                }
            )
        return resultado

    @staticmethod
    @transaction.atomic
    def ajustar_dias_periodo(periodo_id: int, nuevos_dias: Decimal, motivo: str, usuario: Usuario) -> PeriodoVacacional:
        if not usuario.es_admin_rrhh:
            raise BusinessLogicError("No tiene permisos para ajustar periodos.", error_code="PERMISSION_DENIED")
        periodo = PeriodoVacacional.objects.select_for_update().get(periodo_id=periodo_id)
        if nuevos_dias < periodo.dias_gozados:
            raise BusinessLogicError(
                f"Los días no pueden ser menores a los ya gozados ({periodo.dias_gozados}).",
                error_code="INVALID_DAYS_VALUE",
            )

        periodo.dias_correspondientes = nuevos_dias
        periodo.dias_totales = nuevos_dias + (periodo.dias_adicionales or Decimal('0.0'))
        periodo.dias_pendientes = max(0, periodo.dias_totales - periodo.dias_gozados)
        observacion = f"{timezone.now():%Y-%m-%d %H:%M} | Ajuste a {nuevos_dias} días. Motivo: {motivo}"
        periodo.observaciones = f"{(periodo.observaciones or '').strip()}\n{observacion}".strip()
        periodo.save()
        return periodo

    @staticmethod
    def obtener_reporte_solicitudes(
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
        estado: Optional[str] = None,
        area_id: Optional[int] = None,
        empleado_id: Optional[int] = None,
        contrato_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        qs = SolicitudVacaciones.objects.select_related('empleado', 'periodo_vacacional', 'jefe_aprobador', 'rrhh_aprobador')

        if fecha_inicio:
            qs = qs.filter(fecha_envio__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_envio__date__lte=fecha_fin)
        if estado:
            qs = qs.filter(estado_solicitud=estado)
        if area_id:
            qs = qs.filter(
                empleado__datos_laborales__area_id=area_id,
                empleado__datos_laborales__estado_datos='activo',
            )
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)
        if contrato_id:
            qs = qs.filter(periodo_vacacional__contrato__contrato_id=contrato_id)

        reporte = []
        for solicitud in qs.order_by('-fecha_envio', '-fecha_creacion').distinct():
            datos_laborales = solicitud.empleado.datos_laborales_actuales()
            reporte.append(
                {
                    'solicitud_id': solicitud.solicitud_id,
                    'empleado_nombre': solicitud.empleado.nombre_completo,
                    'empleado_rut': solicitud.empleado.numero_documento,
                    'area_nombre': datos_laborales.area.nombre_area if datos_laborales and datos_laborales.area else 'Sin área',
                    'contrato_id': getattr(solicitud.periodo_vacacional.contrato, 'contrato_id', None),
                    'contrato_numero': getattr(solicitud.periodo_vacacional.contrato, 'numero_contrato', None),
                    'tipo_solicitud': solicitud.get_tipo_solicitud_display(),
                    'fecha_inicio': solicitud.fecha_inicio,
                    'fecha_fin': solicitud.fecha_fin,
                    'dias_solicitados': solicitud.dias_solicitados,
                    'estado_solicitud': solicitud.get_estado_solicitud_display(),
                    'fecha_envio': solicitud.fecha_envio,
                    'fecha_aprobacion_jefe': solicitud.fecha_aprobacion_jefe,
                    'fecha_aprobacion_rrhh': solicitud.fecha_aprobacion_rrhh,
                    'jefe_aprobador': solicitud.jefe_aprobador.nombre_completo if solicitud.jefe_aprobador else None,
                    'rrhh_aprobador': solicitud.rrhh_aprobador.nombre_completo if solicitud.rrhh_aprobador else None,
                    'motivo_solicitud': solicitud.motivo_solicitud,
                    'motivo_rechazo': solicitud.motivo_rechazo,
                    'periodo': f"{solicitud.periodo_vacacional.fecha_inicio_periodo:%Y-%m-%d} / {solicitud.periodo_vacacional.fecha_fin_periodo:%Y-%m-%d}",
                }
            )
        return reporte
