"""Filters for RRHH API v1."""

from datetime import timedelta

import django_filters
from app_rrhh.models import Area, DatosLaborales, Empleado, Usuario
from django.db.models import Count, Q
from django.utils import timezone


class AreaFilter(django_filters.FilterSet):
    """Filter for Area model."""

    siglas = django_filters.CharFilter(
        field_name="siglas_area", lookup_expr="icontains"
    )
    unidad_organica = django_filters.CharFilter(
        field_name="nombre_unidad_organica", lookup_expr="icontains"
    )
    organo = django_filters.CharFilter(
        field_name="nombre_organo", lookup_expr="icontains"
    )
    estado = django_filters.ChoiceFilter(
        field_name="estado_area",
        choices=[("activa", "Activa"), ("inactiva", "Inactiva")],
    )

    # Filter by number of employees
    min_empleados = django_filters.NumberFilter(method="filter_min_empleados")
    max_empleados = django_filters.NumberFilter(method="filter_max_empleados")

    class Meta:
        model = Area
        fields = ["siglas", "unidad_organica", "organo", "estado_area"]

    def filter_min_empleados(self, queryset, name, value):
        """Filter areas with minimum number of employees."""
        if value is not None:
            return (
                queryset.filter(
                    ubicaciones_destino__estado_ubicacion="activo",
                    ubicaciones_destino__empleado__estado_empleado="activo",
                )
                .distinct()
                .annotate(empleados_count=Count("ubicaciones_destino"))
                .filter(empleados_count__gte=value)
            )
        return queryset

    def filter_max_empleados(self, queryset, name, value):
        """Filter areas with maximum number of employees."""
        if value is not None:
            return (
                queryset.filter(
                    ubicaciones_destino__estado_ubicacion="activo",
                    ubicaciones_destino__empleado__estado_empleado="activo",
                )
                .distinct()
                .annotate(empleados_count=Count("ubicaciones_destino"))
                .filter(empleados_count__lte=value)
            )
        return queryset


class EmpleadoFilter(django_filters.FilterSet):
    """Filter for Empleado model."""

    nombres = django_filters.CharFilter(
        field_name="nombres_empleado", lookup_expr="icontains"
    )
    ape_paterno = django_filters.CharFilter(
        field_name="apellido_paterno", lookup_expr="icontains"
    )
    ape_materno = django_filters.CharFilter(
        field_name="apellido_materno", lookup_expr="icontains"
    )
    dni = django_filters.CharFilter(field_name="numero_documento", lookup_expr="exact")
    genero = django_filters.ChoiceFilter(
        field_name="genero_empleado",
        choices=[
            ("masculino", "Masculino"),
            ("femenino", "Femenino"),
            ("otro", "Otro"),
            ("no_especifica", "No especifica"),
        ],
    )
    estado_civil = django_filters.ChoiceFilter(
        choices=[
            ("soltero", "Soltero"),
            ("casado", "Casado"),
            ("divorciado", "Divorciado"),
            ("viudo", "Viudo"),
            ("conviviente", "Conviviente"),
        ]
    )
    estado = django_filters.ChoiceFilter(
        field_name="estado_empleado",
        choices=[("activo", "Activo"), ("inactivo", "Inactivo"), ("cesado", "Cesado")],
    )
    distrito = django_filters.CharFilter(lookup_expr="icontains")

    # Date range filters
    fecha_nac_desde = django_filters.DateFilter(
        field_name="fecha_nacimiento", lookup_expr="gte"
    )
    fecha_nac_hasta = django_filters.DateFilter(
        field_name="fecha_nacimiento", lookup_expr="lte"
    )

    # Age range filters
    edad_min = django_filters.NumberFilter(method="filter_edad_min")
    edad_max = django_filters.NumberFilter(method="filter_edad_max")

    # Area filter
    area = django_filters.NumberFilter(method="filter_area")
    area_siglas = django_filters.CharFilter(method="filter_area_siglas")

    # Labor data filters
    puesto = django_filters.CharFilter(method="filter_puesto")
    categoria = django_filters.CharFilter(method="filter_categoria")
    reg_laboral = django_filters.CharFilter(method="filter_reg_laboral")

    # Salary range filters
    remuneracion_min = django_filters.NumberFilter(method="filter_remuneracion_min")
    remuneracion_max = django_filters.NumberFilter(method="filter_remuneracion_max")

    # Family filters
    tiene_hijos = django_filters.BooleanFilter(method="filter_tiene_hijos")
    tiene_conyuge = django_filters.BooleanFilter(method="filter_tiene_conyuge")

    class Meta:
        model = Empleado
        fields = [
            "nombres",
            "ape_paterno",
            "ape_materno",
            "dni",
            "genero",
            "estado_civil",
            "estado",
            "distrito",
        ]

    def filter_edad_min(self, queryset, name, value):
        """Filter by minimum age."""
        if value is not None:
            fecha_max = timezone.now().date() - timedelta(days=value * 365)
            return queryset.filter(fecha_nacimiento__lte=fecha_max)
        return queryset

    def filter_edad_max(self, queryset, name, value):
        """Filter by maximum age."""
        if value is not None:
            fecha_min = timezone.now().date() - timedelta(days=value * 365)
            return queryset.filter(fecha_nacimiento__gte=fecha_min)
        return queryset

    def filter_area(self, queryset, name, value):
        """Filter by current area."""
        if value is not None:
            return queryset.filter(
                ubicaciones_destino__area_id=value,
                ubicaciones_destino__estado_ubicacion="activo",
            )
        return queryset

    def filter_area_siglas(self, queryset, name, value):
        """Filter by area siglas."""
        if value:
            return queryset.filter(
                ubicaciones_destino__area_destino__siglas_area__icontains=value,
                ubicaciones_destino__estado_ubicacion="activo",
            )
        return queryset

    def filter_puesto(self, queryset, name, value):
        """Filter by job position."""
        if value:
            return queryset.filter(
                datos_laborales__cargo_empleado__icontains=value,
                datos_laborales__estado_datos="activo",
            )
        return queryset

    def filter_categoria(self, queryset, name, value):
        """Filter by job category."""
        if value:
            return queryset.filter(
                datos_laborales__categoria__icontains=value,
                datos_laborales__estado_datos="activo",
            )
        return queryset

    def filter_reg_laboral(self, queryset, name, value):
        """Filter by labor regime."""
        if value:
            return queryset.filter(
                datos_laborales__regimen_laboral__icontains=value,
                datos_laborales__estado_datos="activo",
            )
        return queryset

    def filter_remuneracion_min(self, queryset, name, value):
        """Filter by minimum salary."""
        if value is not None:
            return queryset.filter(
                datos_laborales__sueldo_basico__gte=value,
                datos_laborales__estado_datos="activo",
            )
        return queryset

    def filter_remuneracion_max(self, queryset, name, value):
        """Filter by maximum salary."""
        if value is not None:
            return queryset.filter(
                datos_laborales__sueldo_basico__lte=value,
                datos_laborales__estado_datos="activo",
            )
        return queryset

    def filter_tiene_hijos(self, queryset, name, value):
        """Filter employees with children."""
        if value is not None:
            if value:
                return queryset.filter(
                    familiares__parentesco__in=["hijo", "hija"]
                ).distinct()
            else:
                return queryset.exclude(
                    familiares__parentesco__in=["hijo", "hija"]
                ).distinct()
        return queryset

    def filter_tiene_conyuge(self, queryset, name, value):
        """Filter employees with spouse."""
        if value is not None:
            if value:
                return queryset.filter(
                    familiares__parentesco__in=["esposo", "esposa", "conviviente"]
                ).distinct()
            else:
                return queryset.exclude(
                    familiares__parentesco__in=["esposo", "esposa", "conviviente"]
                ).distinct()
        return queryset


class DatosLaboralesFilter(django_filters.FilterSet):
    """Filter for DatosLaborales model."""

    reg_laboral = django_filters.CharFilter(lookup_expr="icontains")
    condicion = django_filters.CharFilter(lookup_expr="icontains")
    categoria = django_filters.CharFilter(lookup_expr="icontains")
    grupo_ocupacional = django_filters.CharFilter(lookup_expr="icontains")
    puesto = django_filters.CharFilter(lookup_expr="icontains")
    estado = django_filters.BooleanFilter()

    # Date range filters
    fecha_ingreso_desde = django_filters.DateFilter(
        field_name="fecha_ingreso", lookup_expr="gte"
    )
    fecha_ingreso_hasta = django_filters.DateFilter(
        field_name="fecha_ingreso", lookup_expr="lte"
    )
    fecha_cese_desde = django_filters.DateFilter(
        field_name="fecha_cese", lookup_expr="gte"
    )
    fecha_cese_hasta = django_filters.DateFilter(
        field_name="fecha_cese", lookup_expr="lte"
    )

    # Salary range filters
    remuneracion_min = django_filters.NumberFilter(
        field_name="remuneracion", lookup_expr="gte"
    )
    remuneracion_max = django_filters.NumberFilter(
        field_name="remuneracion", lookup_expr="lte"
    )

    # Seniority filters
    antiguedad_min_años = django_filters.NumberFilter(method="filter_antiguedad_min")
    antiguedad_max_años = django_filters.NumberFilter(method="filter_antiguedad_max")

    class Meta:
        model = DatosLaborales
        fields = [
            "reg_laboral",
            "condicion",
            "categoria",
            "grupo_ocupacional",
            "puesto",
            "estado",
        ]

    def filter_antiguedad_min(self, queryset, name, value):
        """Filter by minimum seniority in years."""
        if value is not None:
            fecha_max = timezone.now().date() - timedelta(days=value * 365)
            return queryset.filter(fecha_ingreso__lte=fecha_max)
        return queryset

    def filter_antiguedad_max(self, queryset, name, value):
        """Filter by maximum seniority in years."""
        if value is not None:
            fecha_min = timezone.now().date() - timedelta(days=value * 365)
            return queryset.filter(fecha_ingreso__gte=fecha_min)
        return queryset


# RegUbicacionFilter removed - legacy model


class UsuarioFilter(django_filters.FilterSet):
    """Filter for Usuario model."""

    username = django_filters.CharFilter(lookup_expr="icontains")
    email = django_filters.CharFilter(lookup_expr="icontains")
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter()
    estado = django_filters.BooleanFilter()

    # Date range filters
    date_joined_desde = django_filters.DateFilter(
        field_name="date_joined", lookup_expr="gte"
    )
    date_joined_hasta = django_filters.DateFilter(
        field_name="date_joined", lookup_expr="lte"
    )
    fecha_ult_login_desde = django_filters.DateFilter(
        field_name="fecha_ult_login", lookup_expr="gte"
    )
    fecha_ult_login_hasta = django_filters.DateFilter(
        field_name="fecha_ult_login", lookup_expr="lte"
    )

    # Employee filters
    empleado_dni = django_filters.CharFilter(
        field_name="empleado__dni", lookup_expr="exact"
    )
    empleado_area = django_filters.NumberFilter(method="filter_empleado_area")

    # Role filters
    rol = django_filters.CharFilter(method="filter_rol")
    tiene_roles = django_filters.BooleanFilter(method="filter_tiene_roles")

    # Login activity filters
    sin_login_dias = django_filters.NumberFilter(method="filter_sin_login_dias")
    login_reciente_dias = django_filters.NumberFilter(
        method="filter_login_reciente_dias"
    )

    class Meta:
        model = Usuario
        fields = ["username", "email", "is_active", "estado"]

    def filter_empleado_area(self, queryset, name, value):
        """Filter by employee's current area."""
        if value is not None:
            return queryset.filter(
                empleado__ubicaciones_destino__area_id=value,
                empleado__ubicaciones_destino__estado_ubicacion="activo",
            )
        return queryset

    def filter_rol(self, queryset, name, value):
        """Filter by role name."""
        if value:
            return queryset.filter(
                rol_set__nombre__icontains=value, rol_set__estado=True
            ).distinct()
        return queryset

    def filter_tiene_roles(self, queryset, name, value):
        """Filter users with or without roles."""
        if value is not None:
            if value:
                return queryset.filter(rol_set__estado=True).distinct()
            else:
                return queryset.filter(
                    Q(rol_set__isnull=True) | Q(rol_set__estado=False)
                ).distinct()
        return queryset

    def filter_sin_login_dias(self, queryset, name, value):
        """Filter users without login for specified days."""
        if value is not None:
            fecha_limite = timezone.now().date() - timedelta(days=value)
            return queryset.filter(
                Q(fecha_ult_login__lt=fecha_limite) | Q(fecha_ult_login__isnull=True)
            )
        return queryset

    def filter_login_reciente_dias(self, queryset, name, value):
        """Filter users with recent login within specified days."""
        if value is not None:
            fecha_limite = timezone.now().date() - timedelta(days=value)
            return queryset.filter(fecha_ult_login__gte=fecha_limite)
        return queryset
