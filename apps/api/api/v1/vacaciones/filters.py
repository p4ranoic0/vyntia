"""Filtros para las APIs de vacaciones."""

from django.utils import timezone
from django_filters import rest_framework as filters

from app_rrhh.models import Empleado
from apps.organization.models import Area
from app_rrhh.models.vacaciones import ConfiguracionVacaciones, GoceVacaciones, PeriodoVacacional, SolicitudVacaciones


class ConfiguracionVacacionesFilter(filters.FilterSet):
    fecha_inicio_vigencia_desde = filters.DateFilter(field_name='fecha_inicio_vigencia', lookup_expr='gte')
    fecha_inicio_vigencia_hasta = filters.DateFilter(field_name='fecha_inicio_vigencia', lookup_expr='lte')
    fecha_fin_vigencia_desde = filters.DateFilter(field_name='fecha_fin_vigencia', lookup_expr='gte')
    fecha_fin_vigencia_hasta = filters.DateFilter(field_name='fecha_fin_vigencia', lookup_expr='lte')

    class Meta:
        model = ConfiguracionVacaciones
        fields = ['tipo_configuracion', 'activo', 'area', 'empleado']


class PeriodoVacacionalFilter(filters.FilterSet):
    ano_periodo_desde = filters.NumberFilter(field_name='ano_periodo', lookup_expr='gte')
    ano_periodo_hasta = filters.NumberFilter(field_name='ano_periodo', lookup_expr='lte')
    fecha_inicio_desde = filters.DateFilter(field_name='fecha_inicio_periodo', lookup_expr='gte')
    fecha_inicio_hasta = filters.DateFilter(field_name='fecha_inicio_periodo', lookup_expr='lte')
    fecha_vencimiento_desde = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='gte')
    fecha_vencimiento_hasta = filters.DateFilter(field_name='fecha_vencimiento', lookup_expr='lte')
    dias_pendientes_min = filters.NumberFilter(field_name='dias_pendientes', lookup_expr='gte')
    dias_pendientes_max = filters.NumberFilter(field_name='dias_pendientes', lookup_expr='lte')
    area = filters.ModelChoiceFilter(
        queryset=Area.objects.filter(estado_area='activo'),
        method='filter_area',
    )
    vencido = filters.BooleanFilter(method='filter_vencido')
    contrato_id = filters.NumberFilter(field_name='contrato__contrato_id')

    def filter_area(self, queryset, name, value):
        return queryset.filter(
            empleado__datos_laborales__area=value,
            empleado__datos_laborales__estado_datos='activo',
        ).distinct()

    def filter_vencido(self, queryset, name, value):
        hoy = timezone.now().date()
        return queryset.filter(fecha_vencimiento__lt=hoy) if value else queryset.filter(fecha_vencimiento__gte=hoy)

    class Meta:
        model = PeriodoVacacional
        fields = ['ano_periodo', 'empleado', 'estado_periodo', 'contrato_id']


class SolicitudVacacionesFilter(filters.FilterSet):
    fecha_envio_desde = filters.DateFilter(field_name='fecha_envio', lookup_expr='gte')
    fecha_envio_hasta = filters.DateFilter(field_name='fecha_envio', lookup_expr='lte')
    fecha_inicio_desde = filters.DateFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_inicio_hasta = filters.DateFilter(field_name='fecha_inicio', lookup_expr='lte')
    fecha_fin_desde = filters.DateFilter(field_name='fecha_fin', lookup_expr='gte')
    fecha_fin_hasta = filters.DateFilter(field_name='fecha_fin', lookup_expr='lte')
    dias_solicitados_min = filters.NumberFilter(field_name='dias_solicitados', lookup_expr='gte')
    dias_solicitados_max = filters.NumberFilter(field_name='dias_solicitados', lookup_expr='lte')
    area = filters.ModelChoiceFilter(
        queryset=Area.objects.filter(estado_area='activo'),
        method='filter_area',
    )
    ano_periodo = filters.NumberFilter(field_name='periodo_vacacional__ano_periodo')
    pendiente_jefe = filters.BooleanFilter(method='filter_pendiente_jefe')
    pendiente_rrhh = filters.BooleanFilter(method='filter_pendiente_rrhh')
    contrato_id = filters.NumberFilter(field_name='periodo_vacacional__contrato__contrato_id')

    def filter_area(self, queryset, name, value):
        return queryset.filter(
            empleado__datos_laborales__area=value,
            empleado__datos_laborales__estado_datos='activo',
        ).distinct()

    def filter_pendiente_jefe(self, queryset, name, value):
        return queryset.filter(estado_solicitud='en_revision') if value else queryset.exclude(estado_solicitud='en_revision')

    def filter_pendiente_rrhh(self, queryset, name, value):
        return queryset.filter(estado_solicitud='aprobada_jefe') if value else queryset.exclude(estado_solicitud='aprobada_jefe')

    class Meta:
        model = SolicitudVacaciones
        fields = ['empleado', 'estado_solicitud', 'tipo_solicitud', 'ano_periodo', 'contrato_id']


class GoceVacacionesFilter(filters.FilterSet):
    fecha_inicio_real_desde = filters.DateFilter(field_name='fecha_inicio_real', lookup_expr='gte')
    fecha_inicio_real_hasta = filters.DateFilter(field_name='fecha_inicio_real', lookup_expr='lte')
    fecha_fin_real_desde = filters.DateFilter(field_name='fecha_fin_real', lookup_expr='gte')
    fecha_fin_real_hasta = filters.DateFilter(field_name='fecha_fin_real', lookup_expr='lte')
    area = filters.ModelChoiceFilter(
        queryset=Area.objects.filter(estado_area='activo'),
        method='filter_area',
    )
    ano_periodo = filters.NumberFilter(field_name='periodo_vacacional__ano_periodo')
    en_curso = filters.BooleanFilter(method='filter_en_curso')
    contrato_id = filters.NumberFilter(field_name='periodo_vacacional__contrato__contrato_id')

    def filter_area(self, queryset, name, value):
        return queryset.filter(
            empleado__datos_laborales__area=value,
            empleado__datos_laborales__estado_datos='activo',
        ).distinct()

    def filter_en_curso(self, queryset, name, value):
        hoy = timezone.now().date()
        if value:
            return queryset.filter(estado_goce='en_curso', fecha_inicio_real__lte=hoy, fecha_fin_real__gte=hoy)
        return queryset.exclude(estado_goce='en_curso', fecha_inicio_real__lte=hoy, fecha_fin_real__gte=hoy)

    class Meta:
        model = GoceVacaciones
        fields = ['empleado', 'estado_goce', 'ano_periodo', 'contrato_id']
