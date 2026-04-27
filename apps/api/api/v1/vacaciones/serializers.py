"""Serializadores para las APIs de vacaciones."""

from rest_framework import serializers

from apps.time_off.models import (
    VacationConfiguration,
    VacationGrant,
    VacationRequestHistory,
    VacationPeriod,
    VacationRequest,
)
from apps.time_off.services import VacationService


def _nombre_area(area):
    if not area:
        return None
    if hasattr(area, "nombre_area") and area.nombre_area:
        return area.nombre_area
    if hasattr(area, "nombre_organo") and area.nombre_organo:
        return area.nombre_organo
    if hasattr(area, "nombre_unidad_organica") and area.nombre_unidad_organica:
        return area.nombre_unidad_organica
    if hasattr(area, "siglas_area") and area.siglas_area:
        return area.siglas_area
    return None


class ConfiguracionVacacionesSerializer(serializers.ModelSerializer):
    area_nombre = serializers.SerializerMethodField()
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    creado_por_nombre = serializers.CharField(source='created_by.nombre_completo', read_only=True)
    tipo_configuracion_display = serializers.CharField(source='get_tipo_configuracion_display', read_only=True)
    tipo_calculo_display = serializers.CharField(source='get_tipo_calculo_display', read_only=True)

    def get_area_nombre(self, obj):
        area = getattr(obj, 'area', None)
        if not area:
            return None
        if hasattr(area, "nombre_area") and area.nombre_area:
            return area.nombre_area
        if hasattr(area, "nombre_organo") and area.nombre_organo:
            return area.nombre_organo
        if hasattr(area, "nombre_unidad_organica") and area.nombre_unidad_organica:
            return area.nombre_unidad_organica
        if hasattr(area, "siglas_area") and area.siglas_area:
            return area.siglas_area
        return None

    class Meta:
        model = VacationConfiguration
        fields = [
            'id',
            'tipo_configuracion',
            'tipo_configuracion_display',
            'area',
            'area_nombre',
            'empleado',
            'empleado_nombre',
            'dias_por_ano',
            'dias_adicionales_antiguedad',
            'anos_para_adicional',
            'permite_acumulacion',
            'max_dias_acumulables',
            'dias_minimos_solicitud',
            'dias_maximos_solicitud',
            'dias_anticipacion_minima',
            'tipo_calculo',
            'tipo_calculo_display',
            'incluye_feriados',
            'incluye_fines_semana',
            'requiere_aprobacion_jefe',
            'requiere_aprobacion_rrhh',
            'niveles_aprobacion',
            'permite_fraccionamiento',
            'min_dias_por_fraccion',
            'max_fracciones_por_ano',
            'activo',
            'fecha_inicio_vigencia',
            'fecha_fin_vigencia',
            'observaciones',
            'created_by',
            'creado_por_nombre',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class PeriodoVacacionalSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_rut = serializers.CharField(source='empleado.numero_documento', read_only=True)
    area_nombre = serializers.SerializerMethodField()
    contrato_id = serializers.IntegerField(source='contrato.contrato_id', read_only=True)
    contrato_numero = serializers.CharField(source='contrato.numero_contrato', read_only=True)
    contrato_fecha_inicio = serializers.DateField(source='contrato.fecha_inicio', read_only=True)
    contrato_fecha_fin = serializers.DateField(source='contrato.fecha_fin', read_only=True)
    contrato_estado = serializers.CharField(source='contrato.estado', read_only=True)
    configuracion_tipo = serializers.CharField(source='configuracion.get_tipo_configuracion_display', read_only=True)
    porcentaje_uso = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()
    dias_para_vencimiento = serializers.ReadOnlyField()
    periodo_label = serializers.SerializerMethodField()

    def get_area_nombre(self, obj):
        datos = obj.empleado.datos_laborales_actuales()
        if not datos or not datos.area:
            return "Sin area asignada"
        return _nombre_area(datos.area) or "Sin area asignada"

    def get_periodo_label(self, obj):
        return f"{obj.fecha_inicio_periodo.year}-{obj.fecha_fin_periodo.year}"

    class Meta:
        model = VacationPeriod
        fields = [
            'id',
            'empleado',
            'empleado_nombre',
            'empleado_rut',
            'area_nombre',
            'contrato',
            'id',
            'contrato_numero',
            'contrato_fecha_inicio',
            'contrato_fecha_fin',
            'contrato_estado',
            'ano_periodo',
            'periodo_label',
            'fecha_inicio_periodo',
            'fecha_fin_periodo',
            'fecha_vencimiento',
            'dias_correspondientes',
            'dias_adicionales',
            'dias_totales',
            'dias_gozados',
            'dias_pendientes',
            'dias_vencidos',
            'estado_periodo',
            'configuracion',
            'configuracion_tipo',
            'porcentaje_uso',
            'esta_vencido',
            'dias_para_vencimiento',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SolicitudVacacionesSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    empleado_rut = serializers.CharField(source='empleado.numero_documento', read_only=True)
    area_nombre = serializers.SerializerMethodField()
    jefe_aprobador_nombre = serializers.CharField(source='jefe_aprobador.nombre_completo', read_only=True)
    rrhh_aprobador_nombre = serializers.CharField(source='rrhh_aprobador.nombre_completo', read_only=True)
    tipo_solicitud_display = serializers.CharField(source='get_tipo_solicitud_display', read_only=True)
    estado_solicitud_display = serializers.CharField(source='get_estado_solicitud_display', read_only=True)
    dias_calendario = serializers.SerializerMethodField()
    dias_habiles = serializers.SerializerMethodField()
    periodo_label = serializers.SerializerMethodField()
    contrato_id = serializers.SerializerMethodField()
    contrato_numero = serializers.SerializerMethodField()

    def get_area_nombre(self, obj):
        datos = obj.empleado.datos_laborales_actuales()
        if not datos or not datos.area:
            return "Sin area asignada"
        return _nombre_area(datos.area) or "Sin area asignada"

    def get_dias_calendario(self, obj):
        return (obj.fecha_fin - obj.fecha_inicio).days + 1

    def get_dias_habiles(self, obj):
        # En este proyecto se usa cálculo descontable (incluye regla de viernes) ya almacenado en dias_solicitados.
        return obj.dias_solicitados

    def get_periodo_label(self, obj):
        return f"{obj.periodo_vacacional.fecha_inicio_periodo.year}-{obj.periodo_vacacional.fecha_fin_periodo.year}"

    def get_contrato_id(self, obj):
        return getattr(obj.periodo_vacacional.contrato, 'id', None)

    def get_contrato_numero(self, obj):
        return getattr(obj.periodo_vacacional.contrato, 'numero_contrato', None)

    class Meta:
        model = VacationRequest
        fields = [
            'id',
            'empleado',
            'empleado_nombre',
            'empleado_rut',
            'area_nombre',
            'periodo_vacacional',
            'periodo_label',
            'id',
            'contrato_numero',
            'tipo_solicitud',
            'tipo_solicitud_display',
            'fecha_inicio',
            'fecha_fin',
            'dias_solicitados',
            'medio_dia',
            'dias_calendario',
            'dias_habiles',
            'motivo_solicitud',
            'observaciones_empleado',
            'estado_solicitud',
            'estado_solicitud_display',
            'fecha_envio',
            'aprobado_por_jefe',
            'jefe_aprobador',
            'jefe_aprobador_nombre',
            'fecha_aprobacion_jefe',
            'observaciones_jefe',
            'aprobado_por_rrhh',
            'rrhh_aprobador',
            'rrhh_aprobador_nombre',
            'fecha_aprobacion_rrhh',
            'observaciones_rrhh',
            'motivo_rechazo',
            'rechazado_por',
            'fecha_rechazo',
            'motivo_cancelacion',
            'cancelado_por',
            'fecha_cancelacion',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'estado_solicitud',
            'fecha_envio',
            'aprobado_por_jefe',
            'jefe_aprobador',
            'fecha_aprobacion_jefe',
            'aprobado_por_rrhh',
            'rrhh_aprobador',
            'fecha_aprobacion_rrhh',
            'rechazado_por',
            'fecha_rechazo',
            'cancelado_por',
            'fecha_cancelacion',
            'created_at',
            'updated_at',
        ]


class SolicitudVacacionesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacationRequest
        fields = [
            'empleado',
            'periodo_vacacional',
            'tipo_solicitud',
            'fecha_inicio',
            'fecha_fin',
            'motivo_solicitud',
            'observaciones_empleado',
            'medio_dia',
        ]
        extra_kwargs = {
            'empleado': {'required': False},
            'periodo_vacacional': {'required': False},
            'tipo_solicitud': {'required': False},
            'motivo_solicitud': {'required': False},
            'observaciones_empleado': {'required': False},
            'medio_dia': {'required': False},
        }

    def validate(self, attrs):
        request = self.context['request']
        empleado = attrs.get('empleado') or getattr(request.user, 'empleado', None)
        if not empleado:
            raise serializers.ValidationError({'empleado': 'El usuario no tiene empleado asociado.'})
        attrs['empleado'] = empleado
        return attrs

    def create(self, validated_data):
        usuario = self.context['request'].user
        solicitud = VacationService.crear_solicitud_vacaciones(validated_data, usuario)
        # Al crear desde API de empleado se envía de inmediato para aprobación.
        return VacationService.enviar_solicitud(solicitud.solicitud_id, usuario)


class AprobacionSolicitudSerializer(serializers.Serializer):
    accion = serializers.ChoiceField(choices=['aprobar', 'rechazar'], required=True)
    motivo = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, data):
        if data['accion'] == 'rechazar' and not data.get('motivo'):
            raise serializers.ValidationError({'motivo': 'El motivo es obligatorio para rechazar una solicitud.'})
        return data


class GoceVacacionesSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    solicitud_id = serializers.IntegerField(source='solicitud_vacaciones.solicitud_id', read_only=True)
    estado_goce_display = serializers.CharField(source='get_estado_goce_display', read_only=True)
    contrato_id = serializers.IntegerField(source='periodo_vacacional.contrato.contrato_id', read_only=True)
    contrato_numero = serializers.CharField(source='periodo_vacacional.contrato.numero_contrato', read_only=True)

    class Meta:
        model = VacationGrant
        fields = [
            'id',
            'empleado',
            'empleado_nombre',
            'solicitud_vacaciones',
            'id',
            'periodo_vacacional',
            'id',
            'contrato_numero',
            'fecha_inicio_real',
            'fecha_fin_real',
            'fecha_reincorporacion',
            'dias_gozados',
            'estado_goce',
            'estado_goce_display',
            'fecha_interrupcion',
            'motivo_interrupcion',
            'descripcion_interrupcion',
            'dias_no_gozados',
            'reincorporado',
            'fecha_reincorporacion_real',
            'observaciones_reincorporacion',
            'observaciones',
            'registrado_por',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class HistorialSolicitudVacacionesSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario_accion.nombre_completo', read_only=True)
    tipo_accion_display = serializers.CharField(source='get_tipo_accion_display', read_only=True)

    class Meta:
        model = VacationRequestHistory
        fields = [
            'id',
            'solicitud_vacaciones',
            'tipo_accion',
            'tipo_accion_display',
            'descripcion_accion',
            'estado_anterior',
            'estado_nuevo',
            'usuario_accion',
            'usuario_nombre',
            'observaciones',
            'datos_adicionales',
            'fecha_accion',
            'ip_usuario',
        ]
        read_only_fields = ['id', 'fecha_accion']


class EstadisticasVacacionesSerializer(serializers.Serializer):
    ano = serializers.IntegerField()
    area_id = serializers.IntegerField(allow_null=True)
    periodos = serializers.DictField()
    solicitudes = serializers.DictField()
    goces = serializers.DictField()
    fecha_generacion = serializers.CharField()


class EmpleadoDiasVencidosSerializer(serializers.Serializer):
    empleado_id = serializers.IntegerField()
    empleado_nombre = serializers.CharField()
    empleado_rut = serializers.CharField()
    area_nombre = serializers.CharField()
    ano_periodo = serializers.IntegerField()
    dias_correspondientes = serializers.IntegerField()
    dias_gozados = serializers.IntegerField()
    dias_vencidos = serializers.IntegerField()
    fecha_vencimiento = serializers.DateField()
    porcentaje_uso = serializers.DecimalField(max_digits=5, decimal_places=2)


class ResumenPeriodoSerializer(serializers.Serializer):
    empleado_id = serializers.IntegerField()
    empleado_nombre = serializers.CharField()
    periodo_id = serializers.IntegerField()
    periodo = serializers.CharField()
    dias_correspondientes = serializers.IntegerField()
    dias_gozados = serializers.IntegerField()
    dias_pendientes = serializers.IntegerField()
    dias_vencidos = serializers.IntegerField()
    porcentaje_uso = serializers.DecimalField(max_digits=5, decimal_places=2)
    fecha_vencimiento = serializers.DateField()
    esta_vencido = serializers.BooleanField()
