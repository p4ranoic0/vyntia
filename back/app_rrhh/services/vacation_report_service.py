"""Servicio para generar reportes PDF de vacaciones."""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, List, Optional, Tuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from app_rrhh.models import Empleado
from app_rrhh.models.vacaciones import GoceVacaciones, PeriodoVacacional, SolicitudVacaciones


@dataclass
class VacacionesResumenPeriodo:
    periodo_label: str
    fecha_inicio: date
    fecha_fin: date
    dias_correspondientes: int
    dias_gozados: int
    dias_pendientes: int
    estado_periodo: str
    contrato_numero: Optional[str]


@dataclass
class VacacionesDetalleGoce:
    solicitud_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_gozados: int
    estado: str


class VacationReportService:
    """Genera reportes de vacaciones por empleado en PDF."""

    def __init__(self):
        self._pdf_generator = None

    @property
    def pdf_generator(self):
        if self._pdf_generator is None:
            from .pdf_generator import PDFGenerator
            self._pdf_generator = PDFGenerator()
        return self._pdf_generator

    def generar_reporte_empleado(
        self,
        empleado_id: int,
        contrato_id: Optional[int] = None,
    ) -> Tuple[bytes, str]:
        empleado = Empleado.objects.get(empleado_id=empleado_id)
        context = self._obtener_contexto_reporte(empleado, contrato_id)
        html_content = render_to_string('reportes/reporte_vacaciones_empleado.html', context)
        pdf_content = self.pdf_generator._html_to_pdf(html_content)
        nombre_archivo = f"reporte_vacaciones_{empleado.numero_documento}_{timezone.now():%Y%m%d}.pdf"
        return pdf_content, nombre_archivo

    def _obtener_contexto_reporte(self, empleado: Empleado, contrato_id: Optional[int]) -> Dict[str, Any]:
        datos_laborales = empleado.datos_laborales_actuales()

        periodos_qs = PeriodoVacacional.objects.filter(empleado=empleado).select_related('contrato')
        if contrato_id:
            periodos_qs = periodos_qs.filter(contrato__contrato_id=contrato_id)
        periodos = list(periodos_qs.order_by('-fecha_inicio_periodo'))

        resumen_periodos: List[VacacionesResumenPeriodo] = []
        for periodo in periodos:
            resumen_periodos.append(
                VacacionesResumenPeriodo(
                    periodo_label=f"{periodo.fecha_inicio_periodo.year}-{periodo.fecha_fin_periodo.year}",
                    fecha_inicio=periodo.fecha_inicio_periodo,
                    fecha_fin=periodo.fecha_fin_periodo,
                    dias_correspondientes=periodo.dias_correspondientes,
                    dias_gozados=periodo.dias_gozados,
                    dias_pendientes=periodo.dias_pendientes,
                    estado_periodo=periodo.estado_periodo,
                    contrato_numero=getattr(periodo.contrato, 'numero_contrato', None),
                )
            )

        total_pendientes = sum(p.dias_pendientes for p in periodos)
        total_gozados = sum(p.dias_gozados for p in periodos)

        goces_qs = GoceVacaciones.objects.filter(empleado=empleado).select_related('solicitud_vacaciones')
        if periodos:
            goces_qs = goces_qs.filter(periodo_vacacional__in=periodos)
        goces = list(goces_qs.order_by('-fecha_inicio_real'))

        detalle_goces: List[VacacionesDetalleGoce] = []
        for goce in goces:
            detalle_goces.append(
                VacacionesDetalleGoce(
                    solicitud_id=goce.solicitud_vacaciones.solicitud_id,
                    fecha_inicio=goce.fecha_inicio_real,
                    fecha_fin=goce.fecha_fin_real,
                    dias_gozados=goce.dias_gozados,
                    estado=goce.estado_goce,
                )
            )

        if not detalle_goces:
            solicitudes = SolicitudVacaciones.objects.filter(
                empleado=empleado,
                estado_solicitud__in=['aprobada', 'en_goce', 'finalizada'],
            )
            if periodos:
                solicitudes = solicitudes.filter(periodo_vacacional__in=periodos)
            for solicitud in solicitudes.order_by('-fecha_inicio'):
                detalle_goces.append(
                    VacacionesDetalleGoce(
                        solicitud_id=solicitud.solicitud_id,
                        fecha_inicio=solicitud.fecha_inicio,
                        fecha_fin=solicitud.fecha_fin,
                        dias_gozados=solicitud.dias_solicitados,
                        estado=solicitud.estado_solicitud,
                    )
                )

        foto_url = empleado.ruta_fotografia or ''
        if foto_url and not foto_url.startswith(('http://', 'https://', 'file://')):
            media_root = getattr(settings, 'MEDIA_ROOT', '')
            if media_root and not foto_url.startswith('/'):
                root = str(media_root).rstrip('/\\')
                path = str(foto_url).lstrip('/\\')
                foto_url = f"file:///{root}/{path}"
        elif foto_url and foto_url.startswith('/'):
            media_root = getattr(settings, 'MEDIA_ROOT', '')
            if media_root:
                root = str(media_root).rstrip('/\\')
                foto_url = f"file:///{root}{foto_url}"

        return {
            'empleado': empleado,
            'datos_laborales': datos_laborales,
            'fecha_generacion': timezone.now(),
            'reporte_nombre': 'Reporte de Vacaciones',
            'foto_url': foto_url or None,
            'resumen': {
                'dias_pendientes': total_pendientes,
                'dias_gozados': total_gozados,
                'cantidad_periodos': len(periodos),
            },
            'resumen_periodos': resumen_periodos,
            'detalle_goces': detalle_goces,
        }
