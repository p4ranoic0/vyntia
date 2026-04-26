# -*- coding: utf-8 -*-
"""
Serializers para el modulo de Contratos y Adendas.

Contiene los serializers para la gestion de contratos laborales,
adendas, renovaciones y reportes contractuales.
"""

from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any

from app_rrhh.models import ContratosAdendas, Empleado, DocumentosDigitales
from apps.organization.models import Area
from .serializers import EmpleadoListSerializer, AreaSerializer


class ContratosAdendasSerializer(serializers.ModelSerializer):
    """Serializer principal para contratos y adendas."""

    empleado_detalle = EmpleadoListSerializer(source='empleado', read_only=True)
    area_detalle = AreaSerializer(source='area', read_only=True)

    # Campos calculados
    dias_hasta_vencimiento = serializers.ReadOnlyField()
    esta_vigente = serializers.ReadOnlyField()
    esta_vencido = serializers.ReadOnlyField()
    duracion_dias = serializers.ReadOnlyField()
    duracion_meses = serializers.ReadOnlyField()
    es_contrato_inicial = serializers.ReadOnlyField()
    es_adenda = serializers.ReadOnlyField()

    # Campos de texto para choices
    tipo_documento_texto = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)
    jornada_texto = serializers.CharField(source='get_jornada_laboral_display', read_only=True)

    class Meta:
        model = ContratosAdendas
        fields = [
            'contrato_id', 'empleado', 'empleado_detalle', 'area', 'area_detalle',
            'numero_contrato', 'numero_adenda', 'tipo_documento',
            'fecha_inicio', 'fecha_fin', 'fecha_firma',
            'salario_bruto', 'salario_neto',
            'cargo', 'jornada_laboral', 'funciones',
            'lugar_trabajo', 'horario_trabajo',
            'observaciones', 'estado', 'documento_generado',
            'fecha_creacion', 'fecha_modificacion',
            'creado_por', 'modificado_por',
            # Campos calculados
            'dias_hasta_vencimiento', 'esta_vigente', 'esta_vencido',
            'duracion_dias', 'duracion_meses', 'es_contrato_inicial', 'es_adenda',
            # Campos de texto
            'tipo_documento_texto', 'estado_texto', 'jornada_texto',
        ]
        read_only_fields = [
            'contrato_id', 'fecha_creacion', 'fecha_modificacion',
            'creado_por', 'modificado_por',
        ]

    def validate_fecha_fin(self, value):
        """Validar que la fecha de fin sea posterior a la fecha de inicio."""
        fecha_inicio = self.initial_data.get('fecha_inicio')
        if fecha_inicio and value:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            if value <= fecha_inicio:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
        return value

    def validate_salario_bruto(self, value):
        """Validar que el salario bruto sea positivo."""
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El salario bruto debe ser mayor a cero."
            )
        return value


class ContratosAdendasCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear contratos y adendas."""

    numero_contrato = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = ContratosAdendas
        fields = [
            'empleado', 'area', 'numero_contrato', 'numero_adenda',
            'tipo_documento', 'fecha_inicio', 'fecha_fin',
            'fecha_firma', 'salario_bruto',
            'cargo', 'jornada_laboral', 'funciones',
            'lugar_trabajo', 'horario_trabajo', 'observaciones',
        ]

    def validate(self, data):
        """Validar reglas de negocio antes de guardar."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        tipo = data.get('tipo_documento')

        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError(
                {'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'}
            )

        TIPOS_INDETERMINADO = ('CAS_INDETERMINADO', 'LEY_728_INDETERMINADO', 'LEY_276_INDETERMINADO')
        if tipo in TIPOS_INDETERMINADO and fecha_fin:
            raise serializers.ValidationError(
                {'fecha_fin': 'Los contratos a plazo indeterminado no deben tener fecha de fin.'}
            )

        TIPOS_DETERMINADO = ('CAS_DETERMINADO', 'CAS_SUPLENCIA', 'LEY_728_FIJO', 'LEY_728_FIJO_SUPLENCIA')
        if tipo in TIPOS_DETERMINADO and not fecha_fin:
            raise serializers.ValidationError(
                {'fecha_fin': 'Los contratos a plazo determinado requieren fecha de fin.'}
            )

        return data

    def create(self, validated_data):
        """Crear contrato/adenda con calculo automatico del salario neto."""
        from django.utils import timezone
        # Auto-generar numero_contrato si no se proporcionó
        if not validated_data.get('numero_contrato'):
            tipo = validated_data.get('tipo_documento', 'CONT')[:4]
            ts = timezone.now().strftime('%Y%m%d%H%M%S')
            validated_data['numero_contrato'] = f"{tipo}-{ts}"

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creado_por'] = request.user

        return super().create(validated_data)


class ContratosAdendasUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar contratos y adendas."""

    class Meta:
        model = ContratosAdendas
        fields = [
            'fecha_inicio', 'fecha_fin', 'fecha_firma', 'salario_bruto',
            'cargo', 'jornada_laboral', 'funciones',
            'lugar_trabajo', 'horario_trabajo',
            'observaciones', 'estado',
        ]

    def update(self, instance, validated_data):
        """Actualizar contrato/adenda con recalculo del salario neto."""
        # Si cambia salario_bruto, recalcular neto
        if 'salario_bruto' in validated_data:
            salario_bruto = validated_data['salario_bruto']
            validated_data['salario_neto'] = (salario_bruto * Decimal('0.87')).quantize(Decimal('0.01'))

        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['modificado_por'] = request.user

        return super().update(instance, validated_data)


class ContratosAdendasListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de contratos."""

    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    area_nombre = serializers.CharField(source='area.nombre_completo', read_only=True)
    tipo_documento_texto = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    estado_texto = serializers.CharField(source='get_estado_display', read_only=True)

    # Campos calculados
    dias_hasta_vencimiento = serializers.ReadOnlyField()
    esta_vigente = serializers.ReadOnlyField()

    class Meta:
        model = ContratosAdendas
        fields = [
            'contrato_id', 'numero_contrato', 'numero_adenda',
            'empleado', 'empleado_nombre', 'area_nombre',
            'tipo_documento', 'tipo_documento_texto',
            'fecha_inicio', 'fecha_fin',
            'salario_bruto', 'salario_neto',
            'cargo', 'estado', 'estado_texto',
            'dias_hasta_vencimiento', 'esta_vigente',
        ]


class ContratoReporteSerializer(serializers.Serializer):
    """Serializer para parametros de reportes de contratos."""

    area_id = serializers.IntegerField(required=False, help_text="ID del area para filtrar")
    fecha_inicio = serializers.DateField(required=False, help_text="Fecha de inicio del periodo")
    fecha_fin = serializers.DateField(required=False, help_text="Fecha de fin del periodo")
    tipo_documento = serializers.ChoiceField(
        choices=ContratosAdendas.TIPO_DOCUMENTO_CHOICES,
        required=False,
        help_text="Tipo de contrato a filtrar"
    )
    estado = serializers.ChoiceField(
        choices=ContratosAdendas.ESTADO_CHOICES,
        required=False,
        help_text="Estado del contrato a filtrar"
    )

    def validate(self, data):
        """Validar parametros del reporte."""
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )
        return data


class AlertaVencimientoSerializer(serializers.ModelSerializer):
    """Serializer para alertas de vencimiento de contratos."""

    empleado_nombre = serializers.CharField(source='empleado.nombre_completo', read_only=True)
    tipo_documento_texto = serializers.CharField(source='get_tipo_documento_display', read_only=True)
    dias_hasta_vencimiento = serializers.ReadOnlyField()

    class Meta:
        model = ContratosAdendas
        fields = [
            'contrato_id', 'numero_contrato', 'empleado', 'empleado_nombre',
            'tipo_documento', 'tipo_documento_texto',
            'fecha_inicio', 'fecha_fin', 'estado',
            'cargo', 'dias_hasta_vencimiento',
        ]


class DocumentoGeneracionSerializer(serializers.Serializer):
    """Serializer para parametros de generacion de documentos."""

    contrato_id = serializers.IntegerField(help_text="ID del contrato/adenda")
    tipo_documento = serializers.ChoiceField(
        choices=[
            ('contrato', 'Contrato'),
            ('adenda', 'Adenda'),
            ('certificado', 'Certificado Laboral')
        ],
        help_text="Tipo de documento a generar"
    )
    formato = serializers.ChoiceField(
        choices=[('pdf', 'PDF'), ('html', 'HTML')],
        default='pdf',
        help_text="Formato del documento"
    )
