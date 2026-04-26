"""Serializers for RRHH API v1."""

from datetime import datetime, timedelta
from typing import Any, Dict

from app_rrhh.models import (
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    ContratosAdendas,
    DatosLaborales,
    DocumentosDigitales,
    OnboardingEmpleado,
)
from apps.employees.models import (
    DatosAcademicos,
    DatosFamiliares,
    Empleado,
)
from apps.organization.models import Area
from apps.identity.models import (
    Modulos,
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
    UsuarioRoles,
)
from apps.core.exceptions import BusinessLogicError
from apps.core.validators import EmailDomainValidator, PhoneValidator, RUTValidator
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class AreaSerializer(serializers.ModelSerializer):
    """Serializer for Area model."""

    nombre_completo = serializers.SerializerMethodField()
    es_activa = serializers.SerializerMethodField()
    empleados_activos_count = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = [
            "area_id",
            "nombre_organo",
            "nombre_unidad_organica",
            "siglas_area",
            "descripcion_area",
            "estado_area",
            "nombre_completo",
            "es_activa",
            "empleados_activos_count",
        ]
        read_only_fields = ["area_id"]

    @extend_schema_field(serializers.CharField())
    def get_nombre_completo(self, obj) -> str:
        """Get full name of area."""
        return obj.nombre_completo

    @extend_schema_field(serializers.BooleanField())
    def get_es_activa(self, obj) -> bool:
        """Check if area is active."""
        return obj.es_activa

    @extend_schema_field(serializers.IntegerField())
    def get_empleados_activos_count(self, obj) -> int:
        """Get count of active employees."""
        return obj.get_empleados_activos_count()

    def validate_siglas_area(self, value):
        """Validate siglas uniqueness."""
        if value:
            queryset = Area.objects.filter(siglas_area__iexact=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ya existe un área con estas siglas.")
        return value


class AreaListSerializer(serializers.ModelSerializer):
    """Optimized serializer for area list view."""

    empleados_count = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = [
            "area_id",
            "nombre_organo",
            "nombre_unidad_organica",
            "siglas_area",
            "descripcion_area",
            "empleados_count",
        ]

    def get_empleados_count(self, obj: Area) -> int:
        """Get total number of employees in area."""
        # Use the annotated field if available, otherwise calculate
        if hasattr(obj, "empleados_activos_count"):
            count = getattr(obj, "empleados_activos_count")
            # If it's callable, call it; otherwise return directly
            return count() if callable(count) else count
        # Fallback - should not reach here
        return 0


class DatosFamiliaresSerializer(serializers.ModelSerializer):
    """Serializer for DatosFamiliares model."""

    edad = serializers.SerializerMethodField()
    es_menor_edad = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = DatosFamiliares
        fields = [
            "familiar_id",
            "empleado",
            "parentesco",
            "nombres_familiar",
            "apellido_paterno",
            "apellido_materno",
            "fecha_nacimiento",
            "genero_familiar",
            "edad",
            "es_menor_edad",
            "nombre_completo",
            "numero_documento",
            "tipo_documento",
            "es_beneficiario",
            "es_dependiente",
            "estado_familiar",
        ]
        read_only_fields = ["familiar_id"]
        extra_kwargs = {
            "fecha_nacimiento": {"required": False, "allow_null": True},
            "genero_familiar": {"required": False, "allow_blank": True, "default": ""},
            "tipo_documento": {
                "required": False,
                "allow_blank": True,
                "default": "DNI",
            },
        }

    def get_edad(self, obj) -> int | None:
        """Get age of familiar."""
        return obj.edad

    def get_es_menor_edad(self, obj) -> bool:
        """Check if familiar is minor."""
        return obj.es_menor_edad

    def get_nombre_completo(self, obj) -> str:
        """Get full name of familiar."""
        return obj.nombre_completo

    def validate_fecha_nacimiento(self, value):
        """Validate birth date."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede ser futura."
            )
        return value


class DatosAcademicosSerializer(serializers.ModelSerializer):
    """Serializer for DatosAcademicos model."""

    class Meta:
        model = DatosAcademicos
        fields = [
            "academico_id",
            "empleado",
            "nivel_educativo",
            "nombre_institucion",
            "tipo_institucion",
            "modalidad_estudio",
            "nombre_carrera",
            "codigo_carrera",
            "area_conocimiento",
            "duracion_anos",
            "duracion_semestres",
            "fecha_inicio",
            "fecha_fin",
            "fecha_graduacion",
            "estado_estudios",
            "promedio_ponderado",
            "creditos_aprobados",
            "creditos_totales",
            "numero_titulo",
            "numero_diploma",
            "numero_colegiatura",
            "colegio_profesional",
            "pais_institucion",
            "mencion_especialidad",
            "tesis_titulo",
            "verificado_sunedu",
        ]
        read_only_fields = ["academico_id"]

    def validate(self, data):
        """Validate academic data."""
        fecha_inicio = data.get("fecha_inicio")
        fecha_fin = data.get("fecha_fin")

        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise serializers.ValidationError(
                    {
                        "fecha_fin": "La fecha de fin debe ser posterior a la fecha de inicio."
                    }
                )

        if fecha_inicio and fecha_inicio > timezone.now().date():
            raise serializers.ValidationError(
                {"fecha_inicio": "La fecha de inicio no puede ser futura."}
            )

        return data


class CursosCertificacionesSerializer(serializers.ModelSerializer):
    """Serializer for CursosCertificaciones model."""

    class Meta:
        from apps.employees.models import CursosCertificaciones

        model = CursosCertificaciones
        fields = [
            "curso_id",
            "empleado",
            "nombre_curso",
            "institucion",
            "fecha_inicio",
            "fecha_fin",
            "horas",
            "descripcion",
            "documento",
            "estado_registro",
            "fecha_registro",
            "fecha_actualizacion",
        ]
        read_only_fields = ["curso_id", "fecha_registro", "fecha_actualizacion"]


class DatosLaboralesSerializer(serializers.ModelSerializer):
    """Serializer for DatosLaborales model."""

    empleado_nombre = serializers.CharField(
        source="empleado.nombres_empleado", read_only=True
    )
    area_nombre = serializers.CharField(source="area.nombre_completo", read_only=True)
    es_activo = serializers.ReadOnlyField()
    antiguedad_años = serializers.ReadOnlyField()
    antiguedad_meses = serializers.ReadOnlyField()
    tiempo_servicio = serializers.ReadOnlyField()
    ultimo_login_texto = serializers.SerializerMethodField()
    dias_sin_login = serializers.SerializerMethodField()

    def get_ultimo_login_texto(self, obj):
        """Obtiene el texto del último login del empleado."""
        if (
            hasattr(obj, "empleado")
            and obj.empleado
            and hasattr(obj.empleado, "usuario")
        ):
            usuario = obj.empleado.usuario
            if usuario.last_login:
                return usuario.last_login.strftime("%d/%m/%Y %H:%M")
        return "Nunca"

    def get_dias_sin_login(self, obj):
        """Calcula los días sin login del empleado."""
        if (
            hasattr(obj, "empleado")
            and obj.empleado
            and hasattr(obj.empleado, "usuario")
        ):
            usuario = obj.empleado.usuario
            if usuario.last_login:
                from django.utils import timezone

                return (timezone.now().date() - usuario.last_login.date()).days
        return None

    class Meta:
        model = DatosLaborales
        fields = [
            "dato_laboral_id",
            "empleado",
            "area",
            "fecha_ingreso",
            "cargo_empleado",
            "tipo_contrato",
            "regimen_laboral",
            "modalidad_trabajo",
            "jornada_laboral",
            "fecha_cese",
            "categoria",
            "sueldo_basico",
            "es_activo",
            "antiguedad_años",
            "antiguedad_meses",
            "tiempo_servicio",
            "empleado_nombre",
            "area_nombre",
            "ultimo_login_texto",
            "dias_sin_login",
        ]
        read_only_fields = ["dato_laboral_id", "empleado_nombre", "area_nombre"]

    def validate_remuneracion_mensual(self, value):
        """Validate salary amount."""
        if value is not None and value <= 0:
            raise serializers.ValidationError("La remuneración debe ser mayor a cero.")
        return value

    def validate(self, data):
        """Validate labor data."""
        fecha_ingreso = data.get("fecha_ingreso")
        fecha_cese = data.get("fecha_cese")

        if fecha_ingreso and fecha_cese:
            if fecha_cese <= fecha_ingreso:
                raise serializers.ValidationError(
                    {
                        "fecha_cese": "La fecha de cese debe ser posterior a la fecha de ingreso."
                    }
                )

        if fecha_ingreso and fecha_ingreso > timezone.now().date():
            raise serializers.ValidationError(
                {"fecha_ingreso": "La fecha de ingreso no puede ser futura."}
            )

        return data


class ConfiguracionRemuneracionSerializer(serializers.ModelSerializer):
    """Serializer para tabla maestra de conceptos de remuneración."""

    es_activo = serializers.ReadOnlyField()

    class Meta:
        model = ConfiguracionRemuneracion
        fields = [
            "configuracion_id",
            "tipo",
            "codigo",
            "nombre",
            "descripcion",
            "porcentaje",
            "monto_fijo",
            "aplica_base_imponible",
            "orden",
            "estado",
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "configuracion_id",
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]

    def validate_codigo(self, value):
        """Normaliza el código para evitar duplicados por casing/espacios."""
        value = value.strip().upper()
        queryset = ConfiguracionRemuneracion.objects.filter(
            tipo=self.initial_data.get("tipo"), codigo=value
        )
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un concepto con este código para el tipo seleccionado."
            )
        return value

    def validate(self, data):
        """Valida reglas básicas del concepto."""
        porcentaje = data.get("porcentaje")
        monto_fijo = data.get("monto_fijo")

        if porcentaje is not None and porcentaje < 0:
            raise serializers.ValidationError(
                {"porcentaje": "El porcentaje no puede ser negativo."}
            )

        if monto_fijo is not None and monto_fijo < 0:
            raise serializers.ValidationError(
                {"monto_fijo": "El monto fijo no puede ser negativo."}
            )

        if porcentaje == 0 and monto_fijo == 0:
            raise serializers.ValidationError(
                "Debe definir porcentaje o monto fijo para el concepto."
            )

        return data


class ConfiguracionAfpSerializer(serializers.ModelSerializer):
    """Serializer para configuración de aportes y descuentos AFP."""

    es_activo = serializers.ReadOnlyField()

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
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "afp_config_id",
            "es_activo",
            "fecha_creacion",
            "fecha_actualizacion",
        ]

    def validate_vigencia_mes(self, value):
        if len(value) != 7 or value[4] != "-":
            raise serializers.ValidationError("El formato debe ser YYYY-MM.")
        return value

    def validate(self, data):
        for field in [
            "aporte_obligatorio_pct",
            "comision_flujo_pct",
            "comision_mixta_pct",
            "prima_seguro_pct",
        ]:
            value = data.get(field)
            if value is not None and (value < 0 or value > 100):
                raise serializers.ValidationError(
                    {field: "El porcentaje debe estar entre 0 y 100."}
                )

        if (
            data.get("remuneracion_max_asegurable") is not None
            and data["remuneracion_max_asegurable"] <= 0
        ):
            raise serializers.ValidationError(
                {"remuneracion_max_asegurable": "Debe ser mayor a cero."}
            )

        afp_nombre = data.get("afp_nombre")
        vigencia_mes = data.get("vigencia_mes")
        if afp_nombre and vigencia_mes:
            queryset = ConfiguracionAfp.objects.filter(
                afp_nombre__iexact=afp_nombre.strip(),
                vigencia_mes=vigencia_mes,
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe configuración para esta AFP y vigencia."
                )

        return data


# RegUbicacionSerializer eliminado - modelo legacy


class EmpleadoSerializer(serializers.ModelSerializer):
    """Serializer for Empleado model."""

    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    genero_texto = serializers.ReadOnlyField()
    es_activo = serializers.ReadOnlyField()
    # ubicacion_actual eliminado - modelo legacy
    datos_laborales_actuales = DatosLaboralesSerializer(read_only=True)

    # Nested serializers for related data
    familiares = DatosFamiliaresSerializer(many=True, read_only=True)
    formacion = DatosAcademicosSerializer(
        source="datos_academicos", many=True, read_only=True
    )

    class Meta:
        model = Empleado
        fields = [
            "empleado_id",
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "numero_documento",
            "fecha_nacimiento",
            "genero_empleado",
            "estado_civil",
            "direccion_domicilio",
            "distrito_domicilio",
            "telefono_celular",
            "correo_personal",
            "es_padre_familia",
            "entidad_bancaria",
            "numero_cuenta_bancaria",
            "numero_cci",
            "numero_ruc",
            "provincia_domicilio",
            "departamento_domicilio",
            "sistema_pensiones",
            "tipo_comision",
            "codigo_cuspp",
            "estado_empleado",
            "nombre_completo",
            "edad",
            "genero_texto",
            "es_activo",
            "datos_laborales_actuales",
            "familiares",
            "formacion",
        ]
        read_only_fields = ["empleado_id"]

    def validate_numero_documento(self, value):
        """Validate document number uniqueness and format."""
        if value:
            # Check uniqueness
            queryset = Empleado.objects.filter(numero_documento=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    "Ya existe un empleado con este número de documento."
                )

            # Validate format (8 digits for DNI)
            if not value.isdigit() or len(value) != 8:
                raise serializers.ValidationError(
                    "El número de documento debe tener 8 dígitos."
                )

        return value

    def validate_correo_personal(self, value):
        """Validate email format and domain."""
        if value:
            validator = EmailDomainValidator(
                ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"]
            )
            try:
                validator(value)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_telefono_celular(self, value):
        """Validate phone number."""
        if value:
            validator = PhoneValidator()
            try:
                validator(value)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return value

    def validate_fecha_nacimiento(self, value):
        """Validate birth date."""
        if value:
            if value > timezone.now().date():
                raise serializers.ValidationError(
                    "La fecha de nacimiento no puede ser futura."
                )

            # Check minimum age (18 years)
            edad_minima = timezone.now().date() - timedelta(days=18 * 365)
            if value > edad_minima:
                raise serializers.ValidationError(
                    "El empleado debe ser mayor de 18 años."
                )

        return value


class EmpleadoListSerializer(serializers.ModelSerializer):
    """Simplified serializer for Empleado list views."""

    nombre_completo = serializers.ReadOnlyField()
    edad = serializers.ReadOnlyField()
    ubicacion_actual = serializers.SerializerMethodField()
    datos_laborales_resumen = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = [
            "empleado_id",
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "numero_documento",
            "tipo_documento",
            "genero_empleado",
            "estado_empleado",
            "nombre_completo",
            "edad",
            "ubicacion_actual",
            "datos_laborales_resumen",
            "telefono_celular",
            "correo_personal",
            "estado_civil",
            "fecha_nacimiento",
            "direccion_domicilio",
            "distrito_domicilio",
            "provincia_domicilio",
            "departamento_domicilio",
            "ruta_fotografia",
        ]

    def get_ubicacion_actual(self, obj):
        """Get current location info from HistorialUbicaciones or DatosLaborales."""
        ubicacion = obj.ubicacion_actual()
        if ubicacion:
            return {
                "area_id": ubicacion.area_destino.area_id,
                "area_siglas": ubicacion.area_destino.siglas_area,
                "area_nombre": ubicacion.area_destino.nombre_unidad_organica,
            }
        # Fallback: obtener area desde datos laborales activos
        datos_lab = obj.datos_laborales_actuales()
        if datos_lab and datos_lab.area:
            return {
                "area_id": datos_lab.area.area_id,
                "area_siglas": datos_lab.area.siglas_area,
                "area_nombre": datos_lab.area.nombre_unidad_organica,
            }
        return None

    def get_datos_laborales_resumen(self, obj):
        """Get summary of active datos laborales for list view."""
        datos_lab = obj.datos_laborales_actuales()
        if not datos_lab:
            return None
        return {
            "cargo": datos_lab.cargo_empleado,
            "tipo_contrato": datos_lab.tipo_contrato,
            "tipo_contrato_texto": (
                datos_lab.get_tipo_contrato_display()
                if datos_lab.tipo_contrato
                else None
            ),
            "regimen_laboral": datos_lab.regimen_laboral,
            "fecha_ingreso": datos_lab.fecha_ingreso,
        }


class DatosLaboralesCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DatosLaborales without empleado and area fields."""

    class Meta:
        model = DatosLaborales
        exclude = ["dato_laboral_id", "empleado", "area"]


class EmpleadoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating employees with related data."""

    datos_laborales = DatosLaboralesCreateSerializer(write_only=True)
    area_inicial = serializers.IntegerField(write_only=True)
    datos_familiares = DatosFamiliaresSerializer(
        many=True, write_only=True, required=False
    )
    datos_academicos = DatosAcademicosSerializer(
        many=True, write_only=True, required=False
    )

    class Meta:
        model = Empleado
        fields = [
            "empleado_id",
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "numero_documento",
            "fecha_nacimiento",
            "genero_empleado",
            "estado_civil",
            "direccion_domicilio",
            "distrito_domicilio",
            "provincia_domicilio",
            "departamento_domicilio",
            "telefono_celular",
            "correo_personal",
            "es_padre_familia",
            "sistema_pensiones",
            "tipo_seguro_salud",
            "entidad_bancaria",
            "numero_cuenta_bancaria",
            "numero_cci",
            "estado_empleado",
            "datos_laborales",
            "area_inicial",
            "datos_familiares",
            "datos_academicos",
        ]
        read_only_fields = ["empleado_id"]

    def validate_area_inicial(self, value):
        """Validate initial area exists and is active."""
        try:
            area = Area.objects.get(area_id=value, estado_area="activo")
        except Area.DoesNotExist:
            raise serializers.ValidationError("Área no encontrada o inactiva.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create employee with all related data."""
        datos_laborales = validated_data.pop("datos_laborales")
        area_inicial_id = validated_data.pop("area_inicial")
        datos_familiares = validated_data.pop("datos_familiares", [])
        datos_academicos = validated_data.pop("datos_academicos", [])

        # Create employee
        empleado = Empleado.objects.create(**validated_data)

        # Get area and create labor data
        area = Area.objects.get(area_id=area_inicial_id)

        # Create labor data
        DatosLaborales.objects.create(empleado=empleado, area=area, **datos_laborales)

        # Create family data
        for familiar_data in datos_familiares:
            DatosFamiliares.objects.create(empleado=empleado, **familiar_data)

        # Create academic data
        for academico_data in datos_academicos:
            DatosAcademicos.objects.create(empleado=empleado, **academico_data)

        return empleado


class EmpleadoSimpleCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating employees."""

    class Meta:
        model = Empleado
        fields = [
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "numero_documento",
            "fecha_nacimiento",
            "genero_empleado",
            "estado_civil",
            "direccion_domicilio",
            "distrito_domicilio",
            "telefono_celular",
            "correo_personal",
            "es_padre_familia",
            "entidad_bancaria",
            "numero_cuenta_bancaria",
            "estado_empleado",
        ]

    def validate_correo_personal(self, value):
        """Validate email uniqueness."""
        if value and Empleado.objects.filter(correo_personal=value).exists():
            raise serializers.ValidationError("Ya existe un empleado con este email.")
        return value


# Clase BoletaSerializer removida - reemplazada por DocumentosDigitalesSerializer con tipo_documento='BOLETA_PAGO'


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer for Usuario model."""

    es_activo = serializers.ReadOnlyField()
    nombre_completo = serializers.ReadOnlyField()
    empleado_detalle = EmpleadoSerializer(source="empleado", read_only=True)
    roles_activos = serializers.SerializerMethodField()
    ultimo_login_texto = serializers.SerializerMethodField()
    dias_sin_login = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "usuario_id",
            "username",
            "nombres_usuario",
            "apellidos_usuario",
            "email",
            "tipo_usuario",
            "empleado",
            "empleado_detalle",
            "last_login",
            "estado_usuario",
            "date_joined",
            "es_activo",
            "nombre_completo",
            "roles_activos",
            "ultimo_login_texto",
            "dias_sin_login",
        ]
        read_only_fields = ["usuario_id", "date_joined"]

    def get_roles_activos(self, obj):
        """Obtener roles activos del usuario."""
        try:
            roles = obj.roles_activos()
            if roles.exists():
                return [
                    {
                        "id": rol.rol_id,
                        "nombre": rol.nombre_rol,
                        "descripcion": rol.descripcion_rol,
                    }
                    for rol in roles
                ]
            else:
                return []
        except Exception:
            return []

    def get_ultimo_login_texto(self, obj):
        """Obtiene el texto del último login del usuario."""
        if obj.last_login:
            return obj.last_login.strftime("%d/%m/%Y %H:%M")
        return "Nunca"

    def get_dias_sin_login(self, obj):
        """Calcula los días sin login del usuario."""
        if obj.last_login:
            from django.utils import timezone

            return (timezone.now().date() - obj.last_login.date()).days
        return None


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Usuario
        fields = [
            "username",
            "nombres_usuario",
            "apellidos_usuario",
            "email",
            "tipo_usuario",
            "empleado",
            "password",
            "password_confirm",
            "roles",
            "estado_usuario",
        ]

    def validate(self, data):
        """Validate user creation data."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        """Create user with roles."""
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")
        roles_nombres = validated_data.pop("roles", [])

        # Extract fields for create_user
        username = validated_data.pop("username")
        email = validated_data.pop("email", None)

        # Create user
        usuario = Usuario.objects.create_user(
            username=username, email=email, password=password, **validated_data
        )

        # Assign roles via UsuarioRoles intermediate table
        if roles_nombres:
            roles = Rol.objects.filter(
                nombre_rol__in=roles_nombres, estado_rol="activo"
            )
            for rol in roles:
                UsuarioRoles.objects.create(
                    usuario=usuario,
                    rol=rol,
                    estado_asignacion="activo",
                )

        return usuario


class RolSerializer(serializers.ModelSerializer):
    """Serializer for Rol model."""

    es_activo = serializers.ReadOnlyField()
    total_usuarios = serializers.ReadOnlyField()
    total_permisos = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()

    class Meta:
        model = Rol
        fields = [
            "rol_id",
            "nombre_rol",
            "descripcion_rol",
            "estado_rol",
            "es_activo",
            "total_usuarios",
            "total_permisos",
            "permisos",
        ]
        read_only_fields = ["rol_id"]

    def get_total_permisos(self, obj):
        """Get total count of permissions for role."""
        return obj.permisos_asignados.count()

    def get_permisos(self, obj):
        """Get permissions for role."""
        permisos_asignados = obj.permisos_asignados.select_related("permiso").all()
        return [
            {
                "id": rol_permiso.permiso.permiso_id,
                "nombre": rol_permiso.permiso.nombre_permiso,
                "modulo": rol_permiso.permiso.modulo,
                "tipo": rol_permiso.permiso.tipo_permiso,
                "descripcion": rol_permiso.permiso.descripcion_permiso,
            }
            for rol_permiso in permisos_asignados
        ]


class PermisoSerializer(serializers.ModelSerializer):
    """Serializer for Permiso model."""

    es_activo = serializers.ReadOnlyField()

    class Meta:
        model = Permiso
        fields = [
            "permiso_id",
            "nombre_permiso",
            "descripcion_permiso",
            "modulo",
            "tipo_permiso",
            "estado_permiso",
            "es_activo",
        ]
        read_only_fields = ["permiso_id"]


class ModulosSerializer(serializers.ModelSerializer):
    """Serializer for Modulos model."""

    es_activo = serializers.ReadOnlyField()
    permisos_count = serializers.SerializerMethodField()

    class Meta:
        model = Modulos
        fields = [
            "modulo_id",
            "nombre_modulo",
            "descripcion_modulo",
            "icono_modulo",
            "ruta_modulo",
            "orden_visualizacion",
            "estado_modulo",
            "fecha_creacion",
            "fecha_actualizacion",
            "es_activo",
            "permisos_count",
        ]
        read_only_fields = ["modulo_id", "fecha_creacion", "fecha_actualizacion"]

    def get_permisos_count(self, obj):
        """Obtener el número de permisos asociados al módulo."""
        return obj.permisos.filter(estado_permiso="activo").count()

    def validate_nombre_modulo(self, value):
        """Validar que el nombre del módulo sea único."""
        queryset = Modulos.objects.filter(nombre_modulo__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Ya existe un módulo con este nombre.")
        return value

    def validate_ruta_modulo(self, value):
        """Validar que la ruta del módulo sea única."""
        if value:
            queryset = Modulos.objects.filter(ruta_modulo__iexact=value)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError("Ya existe un módulo con esta ruta.")
        return value


class RolPermisosSerializer(serializers.ModelSerializer):
    """Serializer for RolPermisos model."""

    rol_nombre = serializers.CharField(source="rol.nombre_rol", read_only=True)
    permiso_nombre = serializers.CharField(
        source="permiso.nombre_permiso", read_only=True
    )
    modulo_nombre = serializers.CharField(
        source="permiso.modulo.nombre_modulo", read_only=True
    )
    asignado_por_nombre = serializers.CharField(
        source="asignado_por_usuario.nombre_completo", read_only=True
    )

    class Meta:
        model = RolPermisos
        fields = [
            "rol_permiso_id",
            "rol_id",
            "permiso_id",
            "fecha_asignacion",
            "asignado_por_usuario_id",
            "rol_nombre",
            "permiso_nombre",
            "modulo_nombre",
            "asignado_por_nombre",
        ]
        read_only_fields = ["rol_permiso_id", "fecha_asignacion"]

    def validate(self, data):
        """Validar que no exista ya la asignación de permiso a rol."""
        rol_id = data.get("rol_id")
        permiso_id = data.get("permiso_id")

        if rol_id and permiso_id:
            queryset = RolPermisos.objects.filter(rol_id=rol_id, permiso_id=permiso_id)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise serializers.ValidationError(
                    "Este permiso ya está asignado al rol."
                )

        return data


# RegPermisosSerializer eliminado - modelo legacy


class EmpleadoUpdateSerializer(serializers.ModelSerializer):
    """Specialized serializer for updating employees."""

    class Meta:
        model = Empleado
        fields = [
            "nombres_empleado",
            "apellido_paterno",
            "apellido_materno",
            "correo_personal",
            "telefono_celular",
            "direccion_domicilio",
            "distrito_domicilio",
            "estado_civil",
            "entidad_bancaria",
            "numero_cuenta_bancaria",
            "estado_empleado",
            "fecha_nacimiento",
            "genero_empleado",
            "numero_ruc",
            "provincia_domicilio",
            "departamento_domicilio",
            "sistema_pensiones",
            "tipo_comision",
            "codigo_cuspp",
            "numero_cci",
        ]

    def validate_correo_personal(self, value):
        """Validate email uniqueness excluding current instance."""
        if value and self.instance:
            if (
                Empleado.objects.exclude(pk=self.instance.pk)
                .filter(correo_personal=value)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Ya existe un empleado con este email."
                )
        return value


class DocumentosDigitalesSerializer(serializers.ModelSerializer):
    """Serializer for DocumentosDigitales model."""

    empleado_detalle = EmpleadoListSerializer(source="empleado", read_only=True)
    tamano_mb = serializers.SerializerMethodField()
    archivo_url = serializers.SerializerMethodField()
    tipo_documento_texto = serializers.ReadOnlyField()
    categoria_texto = serializers.ReadOnlyField()
    estado_texto = serializers.ReadOnlyField()
    dias_para_vencimiento = serializers.ReadOnlyField()

    class Meta:
        model = DocumentosDigitales
        fields = [
            "documento_id",
            "empleado",
            "empleado_detalle",
            "tipo_documento",
            "tipo_documento_texto",
            "categoria",
            "categoria_texto",
            "nombre_documento",
            "descripcion",
            "archivo",
            "archivo_url",
            "nombre_archivo_original",
            "formato_archivo",
            "tamano_archivo",
            "tamano_mb",
            "fecha_emision",
            "fecha_vencimiento",
            "fecha_subida",
            "subido_por",
            "estado_documento",
            "estado_texto",
            "nivel_acceso",
            "dias_para_vencimiento",
            "validado_por",
            "fecha_validacion",
            "observaciones_validacion",
        ]
        read_only_fields = [
            "documento_id",
            "fecha_subida",
            "nombre_archivo_original",
            "formato_archivo",
        ]

    def get_tamano_mb(self, obj):
        """Get file size in MB."""
        if obj.tamano_archivo:
            return round(obj.tamano_archivo / 1024 / 1024, 2)
        return 0

    def get_archivo_url(self, obj):
        """Return absolute URL for the document file."""
        if obj.archivo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.archivo.url)
            return obj.archivo.url
        return None

    def validate_fecha_vencimiento(self, value):
        """Validate expiration date."""
        if value and value <= timezone.now().date():
            raise serializers.ValidationError(
                "La fecha de vencimiento debe ser futura."
            )
        return value


class DocumentosDigitalesCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DocumentosDigitales."""

    class Meta:
        model = DocumentosDigitales
        fields = [
            "empleado",
            "tipo_documento",
            "categoria",
            "nombre_documento",
            "descripcion",
            "archivo",
            "fecha_emision",
            "fecha_vencimiento",
            "estado_documento",
            "nivel_acceso",
        ]

    def validate_nombre_documento(self, value):
        """Validate document name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre del documento es requerido.")
        return value.strip()


# Clase BoletaCreateSerializer removida - reemplazada por DocumentosDigitalesSerializer con tipo_documento='BOLETA_PAGO'


# ==========================================
# Serializers de Onboarding
# ==========================================


class OnboardingEmpleadoSerializer(serializers.ModelSerializer):
    """Serializer de lectura para el estado de onboarding."""

    empleado_nombre = serializers.CharField(
        source="empleado.nombre_completo", read_only=True
    )
    empleado_documento = serializers.CharField(
        source="empleado.numero_documento", read_only=True
    )
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    progreso_porcentaje = serializers.ReadOnlyField()
    items_pendientes = serializers.ReadOnlyField()
    documentos_pendientes = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(
        source="usuario.last_login", read_only=True, allow_null=True
    )

    class Meta:
        model = OnboardingEmpleado
        fields = [
            "onboarding_id",
            "empleado",
            "empleado_nombre",
            "empleado_documento",
            "usuario",
            "usuario_username",
            "estado_onboarding",
            "datos_personales_completos",
            "datos_laborales_completos",
            "dni_subido",
            "declaraciones_juradas_subidas",
            "certificados_academicos_subidos",
            "certificados_trabajo_subidos",
            "documentos_familiares_subidos",
            "progreso_porcentaje",
            "items_pendientes",
            "documentos_pendientes",
            "validado_por",
            "fecha_validacion",
            "observaciones",
            "email_bienvenida_enviado",
            "fecha_email_bienvenida",
            "fecha_inicio",
            "fecha_completado",
            "last_login",
        ]
        read_only_fields = ["onboarding_id", "fecha_inicio", "fecha_completado"]

    def get_documentos_pendientes(self, obj):
        from app_rrhh.services.onboarding_service import OnboardingService

        return OnboardingService.obtener_documentos_pendientes(obj.empleado_id)


class OnboardingIniciarSerializer(serializers.Serializer):
    """Serializer para que RRHH inicie un onboarding."""

    nombres_empleado = serializers.CharField(max_length=100)
    apellido_paterno = serializers.CharField(max_length=100)
    apellido_materno = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    numero_documento = serializers.CharField(max_length=20)
    correo_personal = serializers.EmailField()
    genero_empleado = serializers.ChoiceField(
        choices=[("masculino", "Masculino"), ("femenino", "Femenino")],
        required=False,
        default="masculino",
    )
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)

    def validate_numero_documento(self, value):
        if Empleado.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError(
                "Ya existe un empleado con este numero de documento."
            )
        return value

    def validate_correo_personal(self, value):
        if Empleado.objects.filter(correo_personal=value).exists():
            raise serializers.ValidationError("Ya existe un empleado con este correo.")
        return value

    def create(self, validated_data):
        from app_rrhh.services.onboarding_service import OnboardingService

        creado_por = self.context["request"].user
        result = OnboardingService.crear_onboarding_completo(validated_data, creado_por)
        return result


class OnboardingValidacionSerializer(serializers.Serializer):
    """Serializer para que RRHH valide o rechace un onboarding."""

    accion = serializers.ChoiceField(choices=["aprobar", "rechazar"])
    observaciones = serializers.CharField(required=False, default="")

    def validate(self, data):
        if data["accion"] == "rechazar" and not data.get("observaciones"):
            raise serializers.ValidationError(
                {"observaciones": "Las observaciones son requeridas al rechazar."}
            )
        return data


class ConfiguracionEmpresaSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        from apps.organization.models import ConfiguracionEmpresa as _CE

        model = _CE
        fields = [
            "id",
            "nombre",
            "ruc",
            "direccion",
            "distrito",
            "provincia",
            "departamento",
            "telefono",
            "email",
            "web",
            "logo",
            "logo_url",
            "representante_legal",
            "cargo_representante",
            "dni_representante",
            "resolucion_creacion",
        ]

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None
