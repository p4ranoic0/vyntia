# -*- coding: utf-8 -*-
"""
Serializers para el módulo de Remuneraciones.

Contiene los serializers para la gestión de planillas mensuales,
boletas de pago, descuentos masivos y reportes de remuneraciones.
"""

from decimal import Decimal

from app_rrhh.models import (
    BoletaPago,
    CalendarioPago,
    ConceptoPlanilla,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    ConfiguracionUit,
    DescuentoMasivo,
    DetallePlanilla,
    PlanillaMensual,
    Usuario,
)
from django.utils import timezone
from rest_framework import serializers

from .serializers import EmpleadoListSerializer, UsuarioSerializer

# ========================================
# Serializers para Configuración
# ========================================


class ConfiguracionAfpSerializer(serializers.ModelSerializer):
    """Serializer para configuración de AFP."""

    es_activo = serializers.ReadOnlyField()
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = ConfiguracionAfp
        fields = [
            "afp_config_id",
            "afp_nombre",
            "vigencia_mes",
            "aporte_obligatorio_pct",
            "comision_flujo_pct",
            "comision_mixta_pct",
            "prima_seguro_pct",
            "remuneracion_max_asegurable",
            "estado",
            "estado_texto",
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["afp_config_id", "fecha_creacion", "fecha_actualizacion"]


class ConfiguracionUitSerializer(serializers.ModelSerializer):
    """Serializer para configuración de UIT (Unidad Impositiva Tributaria)."""

    es_activo = serializers.SerializerMethodField()
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    tope_renta_cuarta_soles = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    essalud_cas_mensual = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    creado_por_nombre = serializers.CharField(
        source="creado_por.nombres_usuario", read_only=True, allow_null=True
    )

    class Meta:
        model = ConfiguracionUit
        fields = [
            "configuracion_uit_id",
            "anio",
            "valor_uit",
            "tope_renta_cuarta_uit",
            "porcentaje_renta_cuarta",
            "estado",
            "estado_texto",
            "es_activo",
            "tope_renta_cuarta_soles",
            "essalud_cas_mensual",
            "creado_por",
            "creado_por_nombre",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "configuracion_uit_id",
            "fecha_creacion",
            "fecha_actualizacion",
            "creado_por",
        ]

    def get_es_activo(self, obj):
        """Retorna si la configuración UIT está activa."""
        return obj.estado == "activo"

    def validate_anio(self, value):
        """Valida que el año sea válido."""
        if value < 2020 or value > 2100:
            raise serializers.ValidationError("El año debe estar entre 2020 y 2100")
        return value

    def validate_valor_uit(self, value):
        """Valida que el valor UIT sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El valor UIT debe ser mayor a 0")
        return value

    def validate(self, attrs):
        """Validaciones a nivel de objeto."""
        # Validar que solo haya una UIT activa por año
        if attrs.get("estado") == "activo":
            anio = attrs.get("anio")
            instance = self.instance

            # Verificar si ya existe otra UIT activa para ese año
            existing = ConfiguracionUit.objects.filter(
                anio=anio, estado="activo"
            ).exclude(
                configuracion_uit_id=instance.configuracion_uit_id if instance else None
            )

            if existing.exists():
                raise serializers.ValidationError(
                    f"Ya existe una configuración UIT activa para el año {anio}"
                )

        return attrs


class ConfiguracionRemuneracionSerializer(serializers.ModelSerializer):
    """Serializer para configuración de conceptos de remuneración."""

    es_activo = serializers.ReadOnlyField()
    tipo_texto = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)

    class Meta:
        model = ConfiguracionRemuneracion
        fields = [
            "configuracion_id",
            "tipo",
            "tipo_texto",
            "codigo",
            "nombre",
            "descripcion",
            "porcentaje",
            "monto_fijo",
            "aplica_base_imponible",
            "orden",
            "estado",
            "estado_texto",
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["configuracion_id", "fecha_creacion", "fecha_actualizacion"]


# ========================================
# Serializers para Planillas Mensuales
# ========================================


class PlanillaMensualListSerializer(serializers.ModelSerializer):
    """Serializer para listar planillas mensuales."""

    modalidad_texto = serializers.CharField(
        source="get_modalidad_display", read_only=True
    )
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    esta_cerrada = serializers.ReadOnlyField()
    puede_generarse = serializers.ReadOnlyField()
    usuario_generacion_nombre = serializers.CharField(
        source="usuario_generacion.nombre_completo", read_only=True, allow_null=True
    )
    usuario_aprobacion_nombre = serializers.CharField(
        source="usuario_aprobacion.nombre_completo", read_only=True, allow_null=True
    )

    class Meta:
        model = PlanillaMensual
        fields = [
            "planilla_id",
            "periodo",
            "modalidad",
            "modalidad_texto",
            "meta_presupuestal",
            "descripcion",
            "estado",
            "estado_texto",
            "total_trabajadores",
            "total_remuneracion_bruta",
            "total_descuentos",
            "total_neto_pagar",
            "total_essalud",
            "total_aporte_afp",
            "total_onp",
            "fecha_generacion",
            "fecha_aprobacion",
            "fecha_pago",
            "usuario_generacion_nombre",
            "usuario_aprobacion_nombre",
            "esta_cerrada",
            "puede_generarse",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "planilla_id",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class PlanillaMensualDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para planilla mensual con relaciones."""

    modalidad_texto = serializers.CharField(
        source="get_modalidad_display", read_only=True
    )
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    esta_cerrada = serializers.ReadOnlyField()
    puede_generarse = serializers.ReadOnlyField()
    usuario_generacion_detalle = UsuarioSerializer(
        source="usuario_generacion", read_only=True
    )
    usuario_aprobacion_detalle = UsuarioSerializer(
        source="usuario_aprobacion", read_only=True
    )

    class Meta:
        model = PlanillaMensual
        fields = [
            "planilla_id",
            "periodo",
            "modalidad",
            "modalidad_texto",
            "meta_presupuestal",
            "descripcion",
            "estado",
            "estado_texto",
            "total_trabajadores",
            "total_remuneracion_bruta",
            "total_descuentos",
            "total_neto_pagar",
            "total_essalud",
            "total_aporte_afp",
            "total_onp",
            "fecha_generacion",
            "fecha_aprobacion",
            "fecha_pago",
            "usuario_generacion",
            "usuario_generacion_detalle",
            "usuario_aprobacion",
            "usuario_aprobacion_detalle",
            "esta_cerrada",
            "puede_generarse",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "planilla_id",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class PlanillaMensualCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear planillas mensuales."""

    class Meta:
        model = PlanillaMensual
        fields = [
            "periodo",
            "modalidad",
            "meta_presupuestal",
            "descripcion",
        ]

    def validate_periodo(self, value):
        """Validar formato de período YYYY-MM."""
        import re

        if not re.match(r"^\d{4}-\d{2}$", value):
            raise serializers.ValidationError("El período debe tener formato YYYY-MM")
        return value

    def validate_modalidad(self, value):
        """Validar y mapear modalidad si es necesario."""
        # Mapeo de modalidades antiguas a nuevas
        modalidad_mapping = {
            "CAS": "plazo_determinado",
            "CAP": "plazo_determinado",
            "NOMBRADO": "plazo_indeterminado",
            "PRACTICANTE": "locacion",
            "TERCERO": "consultoria",
        }

        # Si es un valor antiguo, mapearlo al nuevo
        if value in modalidad_mapping:
            return modalidad_mapping[value]

        # Si ya es un valor válido del modelo, devolverlo
        valid_choices = [choice[0] for choice in PlanillaMensual.MODALIDAD_CHOICES]
        if value in valid_choices:
            return value

        # Si no es válido, lanzar error
        raise serializers.ValidationError(
            f"Modalidad inválida. Valores válidos: {', '.join(valid_choices) + ', CAS, CAP, NOMBRADO, PRACTICANTE, TERCERO'}"
        )


class PlanillaMensualUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar planillas mensuales."""

    class Meta:
        model = PlanillaMensual
        fields = [
            "descripcion",
            "meta_presupuestal",
        ]


# ========================================
# Serializers para Detalle de Planilla
# ========================================


class ConceptoPlanillaSerializer(serializers.ModelSerializer):
    """Serializer para conceptos de planilla."""

    tipo_texto = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = ConceptoPlanilla
        fields = [
            "concepto_planilla_id",
            "detalle_planilla",
            "configuracion_concepto",
            "tipo",
            "tipo_texto",
            "codigo",
            "nombre",
            "monto",
            "observaciones",
            "fecha_creacion",
        ]
        read_only_fields = ["concepto_planilla_id", "fecha_creacion"]


class DetallePlanillaListSerializer(serializers.ModelSerializer):
    """Serializer para listar detalles de planilla."""

    empleado = serializers.SerializerMethodField()
    total_ingresos = serializers.DecimalField(
        source="total_haberes", max_digits=10, decimal_places=2, read_only=True
    )
    estado = serializers.CharField(source="estado_laboral", read_only=True)
    estado_texto = serializers.SerializerMethodField()

    class Meta:
        model = DetallePlanilla
        fields = [
            "detalle_id",
            "planilla",
            "empleado",
            "area_nombre",
            "cargo",
            "dni",
            "sistema_pensiones",
            "tipo_comision_afp",
            "dias_laborados",
            "remuneracion_basica",
            "asignacion_familiar",
            "bonificacion_especial",
            "otras_bonificaciones",
            "total_ingresos",
            "total_haberes",
            "aporte_afp_obligatorio",
            "comision_afp",
            "prima_seguro_afp",
            "total_afp",
            "aporte_onp",
            "essalud",
            "renta_quinta_categoria",
            "total_descuentos",
            "neto_pagar",
            "estado",
            "estado_texto",
            "banco",
            "numero_cuenta",
        ]
        read_only_fields = ["detalle_id"]

    def get_empleado(self, obj):
        """Retorna datos del empleado como objeto anidado."""
        return {
            "empleado_id": obj.empleado_id,
            "dni": obj.dni,
            "nombres_completos": obj.empleado.nombre_completo if obj.empleado else "",
            "area_nombre": obj.area_nombre,
        }

    def get_estado_texto(self, obj):
        """Retorna el texto del estado laboral."""
        return obj.get_estado_laboral_display()


class DetallePlanillaDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para detalle de planilla con todos los conceptos."""

    empleado_detalle = EmpleadoListSerializer(source="empleado", read_only=True)
    conceptos = ConceptoPlanillaSerializer(many=True, read_only=True)
    tiene_boleta = serializers.SerializerMethodField()

    class Meta:
        model = DetallePlanilla
        fields = [
            "detalle_id",
            "planilla",
            "empleado",
            "empleado_detalle",
            "datos_laborales",
            "area_nombre",
            "cargo",
            "dni",
            "sistema_pensiones",
            "tipo_comision_afp",
            "cuspp",
            "dias_laborados",
            "dias_no_laborados",
            "dias_subsidiados",
            "remuneracion_basica",
            "asignacion_familiar",
            "bonificacion_especial",
            "otras_bonificaciones",
            "total_haberes",
            "aporte_afp_obligatorio",
            "comision_afp",
            "prima_seguro_afp",
            "total_afp",
            "aporte_onp",
            "renta_quinta_categoria",
            "descuentos_judiciales",
            "prestamos",
            "otros_descuentos",
            "total_descuentos",
            "essalud",
            "neto_pagar",
            "banco",
            "numero_cuenta",
            "conceptos",
            "tiene_boleta",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["detalle_id", "fecha_creacion", "fecha_actualizacion"]

    def get_tiene_boleta(self, obj):
        """Verificar si el detalle tiene boleta generada."""
        return hasattr(obj, "boleta")


class DetallePlanillaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear detalles de planilla."""

    class Meta:
        model = DetallePlanilla
        fields = [
            "planilla",
            "empleado",
            "datos_laborales",
            "area_nombre",
            "cargo",
            "dni",
            "sistema_pensiones",
            "tipo_comision_afp",
            "cuspp",
            "dias_laborados",
            "dias_no_laborados",
            "dias_subsidiados",
            "remuneracion_basica",
            "asignacion_familiar",
            "bonificacion_especial",
            "otras_bonificaciones",
            "banco",
            "numero_cuenta",
        ]

    def validate_dias_laborados(self, value):
        """Validar que los días laborados sean entre 0 y 31."""
        if value < 0 or value > 31:
            raise serializers.ValidationError(
                "Los días laborados deben estar entre 0 y 31"
            )
        return value


# ========================================
# Serializers para Descuentos Masivos
# ========================================


class DescuentoMasivoListSerializer(serializers.ModelSerializer):
    """Serializer para listar descuentos masivos."""

    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    concepto_nombre = serializers.CharField(
        source="configuracion_concepto.nombre", read_only=True
    )
    usuario_nombre = serializers.CharField(
        source="usuario_carga.nombre_completo", read_only=True
    )

    class Meta:
        model = DescuentoMasivo
        fields = [
            "descuento_masivo_id",
            "periodo",
            "configuracion_concepto",
            "concepto_nombre",
            "archivo_origen",
            "total_registros",
            "registros_procesados",
            "registros_error",
            "monto_total",
            "estado",
            "estado_texto",
            "usuario_nombre",
            "fecha_carga",
            "fecha_procesado",
        ]
        read_only_fields = [
            "descuento_masivo_id",
            "fecha_carga",
            "fecha_procesado",
        ]


class DescuentoMasivoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para descuentos masivos."""

    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    concepto_detalle = ConfiguracionRemuneracionSerializer(
        source="configuracion_concepto", read_only=True
    )
    usuario_detalle = UsuarioSerializer(source="usuario_carga", read_only=True)

    class Meta:
        model = DescuentoMasivo
        fields = [
            "descuento_masivo_id",
            "periodo",
            "configuracion_concepto",
            "concepto_detalle",
            "archivo_origen",
            "total_registros",
            "registros_procesados",
            "registros_error",
            "monto_total",
            "estado",
            "estado_texto",
            "errores_log",
            "usuario_carga",
            "usuario_detalle",
            "fecha_carga",
            "fecha_procesado",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "descuento_masivo_id",
            "fecha_carga",
            "fecha_procesado",
            "fecha_actualizacion",
        ]


class DescuentoMasivoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear carga de descuentos masivos."""

    class Meta:
        model = DescuentoMasivo
        fields = [
            "periodo",
            "configuracion_concepto",
            "archivo_origen",
        ]

    def validate_archivo_origen(self, value):
        """Validar que el archivo sea Excel."""
        if not value.name.endswith((".xlsx", ".xls")):
            raise serializers.ValidationError(
                "El archivo debe ser formato Excel (.xlsx o .xls)"
            )
        return value


# ========================================
# Serializers para Boletas de Pago
# ========================================


class BoletaPagoListSerializer(serializers.ModelSerializer):
    """Serializer para listar boletas de pago."""

    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    empleado_nombre = serializers.CharField(
        source="detalle_planilla.empleado.nombre_completo", read_only=True
    )
    empleado_dni = serializers.CharField(
        source="detalle_planilla.empleado.numero_documento", read_only=True
    )
    periodo = serializers.CharField(
        source="detalle_planilla.planilla.periodo", read_only=True
    )
    total_ingresos = serializers.DecimalField(
        source="detalle_planilla.total_haberes",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    total_descuentos = serializers.DecimalField(
        source="detalle_planilla.total_descuentos",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    neto_pagar = serializers.DecimalField(
        source="detalle_planilla.neto_pagar",
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = BoletaPago
        fields = [
            "boleta_id",
            "detalle_planilla",
            "archivo_pdf",
            "estado",
            "estado_texto",
            "empleado_nombre",
            "empleado_dni",
            "periodo",
            "total_ingresos",
            "total_descuentos",
            "neto_pagar",
            "fecha_generacion",
            "fecha_envio_email",
            "fecha_descarga",
        ]
        read_only_fields = [
            "boleta_id",
            "fecha_generacion",
            "fecha_envio_email",
            "fecha_descarga",
        ]


class BoletaPagoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para boletas de pago."""

    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    detalle_planilla_info = DetallePlanillaDetailSerializer(
        source="detalle_planilla", read_only=True
    )

    class Meta:
        model = BoletaPago
        fields = [
            "boleta_id",
            "detalle_planilla",
            "detalle_planilla_info",
            "archivo_pdf",
            "estado",
            "estado_texto",
            "fecha_generacion",
            "fecha_envio_email",
            "fecha_descarga",
            "hash_documento",
        ]
        read_only_fields = [
            "boleta_id",
            "fecha_generacion",
            "fecha_envio_email",
            "fecha_descarga",
            "hash_documento",
        ]


# ========================================
# Serializers para Calendario de Pagos
# ========================================


class CalendarioPagoListSerializer(serializers.ModelSerializer):
    """Serializer para listar calendarios de pago."""

    tipo_pago_texto = serializers.CharField(
        source="get_tipo_pago_display", read_only=True
    )
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    periodo = serializers.CharField(source="planilla.periodo", read_only=True)
    modalidad_planilla = serializers.CharField(
        source="planilla.get_modalidad_display", read_only=True
    )

    class Meta:
        model = CalendarioPago
        fields = [
            "calendario_id",
            "planilla",
            "periodo",
            "modalidad_planilla",
            "tipo_pago",
            "tipo_pago_texto",
            "fecha_pago_programada",
            "fecha_pago_ejecutada",
            "descripcion",
            "estado",
            "estado_texto",
            "fecha_creacion",
        ]
        read_only_fields = [
            "calendario_id",
            "fecha_creacion",
        ]


class CalendarioPagoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para calendarios de pago."""

    tipo_pago_texto = serializers.CharField(
        source="get_tipo_pago_display", read_only=True
    )
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    planilla_detalle = PlanillaMensualListSerializer(source="planilla", read_only=True)
    usuario_detalle = UsuarioSerializer(source="usuario_programacion", read_only=True)

    class Meta:
        model = CalendarioPago
        fields = [
            "calendario_id",
            "planilla",
            "planilla_detalle",
            "tipo_pago",
            "tipo_pago_texto",
            "fecha_pago_programada",
            "fecha_pago_ejecutada",
            "descripcion",
            "estado",
            "estado_texto",
            "usuario_programacion",
            "usuario_detalle",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "calendario_id",
            "fecha_creacion",
            "fecha_actualizacion",
        ]


class CalendarioPagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear calendarios de pago."""

    class Meta:
        model = CalendarioPago
        fields = [
            "planilla",
            "tipo_pago",
            "fecha_pago_programada",
            "descripcion",
        ]

    def validate_fecha_pago_programada(self, value):
        """Validar que la fecha de pago sea futura."""
        from datetime import date

        if value < date.today():
            raise serializers.ValidationError("La fecha de pago debe ser futura")
        return value
