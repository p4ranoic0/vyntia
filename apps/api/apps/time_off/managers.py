# -*- coding: utf-8 -*-
"""
Managers personalizados para los modelos de vacaciones

Contiene managers que proporcionan métodos de consulta optimizados
y funcionalidades específicas para los modelos de vacaciones.
"""

from datetime import date, timedelta

from django.db import models
from django.db.models import Avg, Case, Count, F, Q, Sum, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone


class ConfiguracionVacacionesManager(models.Manager):
    """Manager personalizado para ConfiguracionVacaciones."""

    def activas(self):
        """Retorna configuraciones activas."""
        return self.filter(activo=True)

    def vigentes(self, fecha=None):
        """Retorna configuraciones vigentes en una fecha específica."""
        if fecha is None:
            fecha = date.today()

        return (
            self.activas()
            .filter(fecha_inicio_vigencia__lte=fecha)
            .filter(
                Q(fecha_fin_vigencia__isnull=True) | Q(fecha_fin_vigencia__gte=fecha)
            )
        )

    def para_empleado(self, empleado, fecha=None):
        """Obtiene la configuración aplicable para un empleado específico."""
        if fecha is None:
            fecha = date.today()

        # Buscar configuración específica del empleado
        config_empleado = (
            self.vigentes(fecha)
            .filter(tipo_configuracion="empleado", empleado=empleado)
            .first()
        )

        if config_empleado:
            return config_empleado

        # Buscar configuración por área
        if empleado.datos_laborales.exists():
            area = empleado.datos_laborales.first().area
            config_area = (
                self.vigentes(fecha)
                .filter(tipo_configuracion="area", area=area)
                .first()
            )

            if config_area:
                return config_area

        # Buscar configuración general
        return self.vigentes(fecha).filter(tipo_configuracion="general").first()

    def por_tipo(self, tipo):
        """Filtra configuraciones por tipo."""
        return self.filter(tipo_configuracion=tipo)


class PeriodoVacacionalManager(models.Manager):
    """Manager personalizado para PeriodoVacacional."""

    def activos(self):
        """Retorna períodos activos."""
        return self.filter(estado_periodo="activo")

    def vencidos(self):
        """Retorna períodos vencidos."""
        return self.filter(fecha_vencimiento__lt=date.today(), estado_periodo="activo")

    def por_vencer(self, dias=30):
        """Retorna períodos que vencen en los próximos días especificados."""
        fecha_limite = date.today() + timedelta(days=dias)
        return self.activos().filter(
            fecha_vencimiento__lte=fecha_limite, fecha_vencimiento__gte=date.today()
        )

    def con_dias_pendientes(self):
        """Retorna períodos con días pendientes de usar."""
        return self.activos().filter(dias_pendientes__gt=0)

    def para_empleado(self, empleado):
        """Retorna períodos de un empleado específico."""
        return self.filter(empleado=empleado)

    def del_ano(self, ano):
        """Retorna períodos de un año específico."""
        return self.filter(ano_periodo=ano)

    def estadisticas_por_area(self):
        """Retorna estadísticas de períodos agrupadas por área."""
        return (
            self.prefetch_related("empleado__datos_laborales")
            .values("empleado__datos_laborales__area__nombre_area")
            .annotate(
                total_empleados=Count("empleado", distinct=True),
                total_dias_asignados=Sum("dias_totales"),
                total_dias_gozados=Sum("dias_gozados"),
                total_dias_pendientes=Sum("dias_pendientes"),
                promedio_uso=Avg(
                    Case(
                        When(
                            dias_totales__gt=0,
                            then=F("dias_gozados") * 100.0 / F("dias_totales"),
                        ),
                        default=Value(0),
                        output_field=models.FloatField(),
                    )
                ),
            )
        )


class SolicitudVacacionesManager(models.Manager):
    """Manager personalizado para SolicitudVacaciones."""

    def pendientes(self):
        """Retorna solicitudes pendientes de aprobación."""
        return self.filter(
            estado_solicitud__in=["enviada", "en_revision", "aprobada_jefe"]
        )

    def pendientes_jefe(self):
        """Retorna solicitudes pendientes de aprobación del jefe."""
        return self.filter(
            estado_solicitud__in=["enviada", "en_revision"], aprobado_por_jefe=False
        )

    def pendientes_rrhh(self):
        """Retorna solicitudes pendientes de aprobación de RRHH."""
        return self.filter(estado_solicitud="aprobada_jefe", aprobado_por_rrhh=False)

    def aprobadas(self):
        """Retorna solicitudes completamente aprobadas."""
        return self.filter(estado_solicitud="aprobada")

    def en_goce(self):
        """Retorna solicitudes en goce actualmente."""
        return self.filter(estado_solicitud="en_goce")

    def para_empleado(self, empleado):
        """Retorna solicitudes de un empleado específico."""
        return self.filter(empleado=empleado)

    def en_rango_fechas(self, fecha_inicio, fecha_fin):
        """Retorna solicitudes en un rango de fechas."""
        return self.filter(
            Q(fecha_inicio__range=[fecha_inicio, fecha_fin])
            | Q(fecha_fin__range=[fecha_inicio, fecha_fin])
            | Q(fecha_inicio__lte=fecha_inicio, fecha_fin__gte=fecha_fin)
        )

    def solapan_con(self, empleado, fecha_inicio, fecha_fin, excluir_solicitud=None):
        """Verifica si hay solicitudes que solapan con las fechas dadas."""
        queryset = self.filter(
            empleado=empleado, estado_solicitud__in=["aprobada", "en_goce"]
        ).filter(
            Q(fecha_inicio__range=[fecha_inicio, fecha_fin])
            | Q(fecha_fin__range=[fecha_inicio, fecha_fin])
            | Q(fecha_inicio__lte=fecha_inicio, fecha_fin__gte=fecha_fin)
        )

        if excluir_solicitud:
            queryset = queryset.exclude(solicitud_id=excluir_solicitud.solicitud_id)

        return queryset

    def del_periodo(self, periodo):
        """Retorna solicitudes de un período específico."""
        return self.filter(periodo_vacacional=periodo)

    def estadisticas_por_estado(self):
        """Retorna estadísticas agrupadas por estado."""
        return (
            self.values("estado_solicitud")
            .annotate(total=Count("solicitud_id"), dias_totales=Sum("dias_solicitados"))
            .order_by("estado_solicitud")
        )


class GoceVacacionesManager(models.Manager):
    """Manager personalizado para GoceVacaciones."""

    def en_curso(self):
        """Retorna goces en curso actualmente."""
        hoy = date.today()
        return self.filter(
            estado_goce="en_curso", fecha_inicio_real__lte=hoy, fecha_fin_real__gte=hoy
        )

    def finalizados(self):
        """Retorna goces finalizados."""
        return self.filter(estado_goce="finalizado")

    def interrumpidos(self):
        """Retorna goces interrumpidos."""
        return self.filter(estado_goce="interrumpido")

    def para_empleado(self, empleado):
        """Retorna goces de un empleado específico."""
        return self.filter(empleado=empleado)

    def del_periodo(self, periodo):
        """Retorna goces de un período específico."""
        return self.filter(periodo_vacacional=periodo)

    def en_rango_fechas(self, fecha_inicio, fecha_fin):
        """Retorna goces en un rango de fechas."""
        return self.filter(
            Q(fecha_inicio_real__range=[fecha_inicio, fecha_fin])
            | Q(fecha_fin_real__range=[fecha_inicio, fecha_fin])
            | Q(fecha_inicio_real__lte=fecha_inicio, fecha_fin_real__gte=fecha_fin)
        )

    def pendientes_reincorporacion(self):
        """Retorna goces pendientes de reincorporación."""
        return self.filter(
            estado_goce__in=["finalizado", "interrumpido"], reincorporado=False
        )

    def estadisticas_por_mes(self, ano=None):
        """Retorna estadísticas de goces agrupadas por mes."""
        queryset = self.finalizados()

        if ano:
            queryset = queryset.filter(fecha_inicio_real__year=ano)

        return (
            queryset.extra(select={"mes": "EXTRACT(month FROM fecha_inicio_real)"})
            .values("mes")
            .annotate(
                total_goces=Count("goce_id"),
                total_dias=Sum("dias_gozados"),
                empleados_unicos=Count("empleado", distinct=True),
            )
            .order_by("mes")
        )


class HistorialSolicitudVacacionesManager(models.Manager):
    """Manager personalizado para HistorialSolicitudVacaciones."""

    def para_solicitud(self, solicitud):
        """Retorna historial de una solicitud específica."""
        return self.filter(solicitud_vacaciones=solicitud).order_by("fecha_accion")

    def por_tipo_accion(self, tipo_accion):
        """Filtra por tipo de acción."""
        return self.filter(tipo_accion=tipo_accion)

    def por_usuario(self, usuario):
        """Filtra por usuario que realizó la acción."""
        return self.filter(usuario_accion=usuario)

    def en_rango_fechas(self, fecha_inicio, fecha_fin):
        """Retorna historial en un rango de fechas."""
        return self.filter(fecha_accion__date__range=[fecha_inicio, fecha_fin])

    def acciones_recientes(self, dias=7):
        """Retorna acciones de los últimos días especificados."""
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_accion__gte=fecha_limite)

    def estadisticas_por_accion(self):
        """Retorna estadísticas agrupadas por tipo de acción."""
        return (
            self.values("tipo_accion")
            .annotate(
                total=Count("historial_id"),
                usuarios_unicos=Count("usuario_accion", distinct=True),
            )
            .order_by("tipo_accion")
        )

    def auditoria_empleado(self, empleado):
        """Retorna auditoría completa de un empleado."""
        return (
            self.filter(solicitud_vacaciones__empleado=empleado)
            .select_related("solicitud_vacaciones", "usuario_accion")
            .order_by("-fecha_accion")
        )
