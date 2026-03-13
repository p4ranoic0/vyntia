"""Custom managers for app_rrhh models."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from django.db import models
from django.db.models import Avg, Count, Prefetch, Q, Sum
from django.utils import timezone


class AreaManager(models.Manager):
    """Custom manager for Area model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related()

    def activas(self):
        """Get only active areas."""
        return self.filter(estado="activa")

    def inactivas(self):
        """Get only inactive areas."""
        return self.filter(estado="inactiva")

    def con_empleados(self):
        """Get areas that have employees."""
        return self.filter(empleados_count__gt=0)

    def sin_empleados(self):
        """Get areas without employees."""
        return self.filter(empleados_count=0)

    def por_organo(self, organo: str):
        """Filter areas by organo.

        Args:
            organo: Organo name

        Returns:
            QuerySet: Filtered areas
        """
        return self.filter(organo__icontains=organo)

    def buscar(self, termino: str):
        """Search areas by multiple fields.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching areas
        """
        return self.filter(
            Q(organo__icontains=termino)
            | Q(unidad_organica__icontains=termino)
            | Q(siglas__icontains=termino)
            | Q(descripcion__icontains=termino)
        )

    def con_estadisticas(self):
        """Get areas with employee statistics."""
        return self.annotate(
            total_empleados_activos=Count(
                "historialubicaciones__empleado",
                filter=Q(
                    historialubicaciones__empleado__estado=True,
                    historialubicaciones__estado=True,
                    historialubicaciones__fecha_termino__isnull=True,
                ),
            ),
            promedio_remuneracion=Avg(
                "historialubicaciones__empleado__datoslaborales__remuneracion",
                filter=Q(historialubicaciones__empleado__datoslaborales__estado=True),
            ),
        )


class EmpleadoManager(models.Manager):
    """Custom manager for Empleado model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related()

    def activos(self):
        """Get only active employees."""
        return self.filter(estado=True)

    def inactivos(self):
        """Get only inactive employees."""
        return self.filter(estado=False)

    def masculinos(self):
        """Get male employees."""
        return self.filter(genero_empleado="masculino")

    def femeninos(self):
        """Get female employees."""
        return self.filter(genero_empleado="femenino")

    def con_hijos(self):
        """Get employees with children."""
        return self.filter(es_padre_familia=True)

    def por_edad(self, edad_min: int = None, edad_max: int = None):
        """Filter employees by age range.

        Args:
            edad_min: Minimum age
            edad_max: Maximum age

        Returns:
            QuerySet: Filtered employees
        """
        today = timezone.now().date()
        filters = Q()

        if edad_min is not None:
            fecha_max = today - timedelta(days=edad_min * 365)
            filters &= Q(fecha_nac__lte=fecha_max)

        if edad_max is not None:
            fecha_min = today - timedelta(days=edad_max * 365)
            filters &= Q(fecha_nac__gte=fecha_min)

        return self.filter(filters)

    def por_distrito(self, distrito: str):
        """Filter employees by district.

        Args:
            distrito: District name

        Returns:
            QuerySet: Filtered employees
        """
        return self.filter(distrito__icontains=distrito)

    def por_banco(self, banco: str):
        """Filter employees by bank.

        Args:
            banco: Bank name

        Returns:
            QuerySet: Filtered employees
        """
        return self.filter(banco__icontains=banco)

    def buscar(self, termino: str):
        """Search employees by multiple fields.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching employees
        """
        return self.filter(
            Q(nombres_empleado__icontains=termino)
            | Q(apellido_paterno__icontains=termino)
            | Q(apellido_materno__icontains=termino)
            | Q(numero_documento__icontains=termino)
            | Q(correo_personal__icontains=termino)
        )

    def con_datos_completos(self):
        """Get employees with complete profile data."""
        return self.prefetch_related(
            "familiares",
            "datos_academicos",
            "datoslaborales_set",
            "ubicaciones__area_destino",
        )

    def con_ubicacion_actual(self):
        """Get employees with their current location."""
        from .models import HistorialUbicaciones

        return self.prefetch_related(
            Prefetch(
                "ubicaciones",
                queryset=HistorialUbicaciones.objects.filter(
                    estado_ubicacion="activo", fecha_termino__isnull=True
                ),
                to_attr="ubicacion_actual",
            )
        )

    def estadisticas_demograficas(self):
        """Get demographic statistics."""
        return self.aggregate(
            total=Count("id"),
            hombres=Count("id", filter=Q(genero_empleado="masculino")),
            mujeres=Count("id", filter=Q(genero_empleado="femenino")),
            con_hijos=Count("id", filter=Q(es_padre_familia=True)),
            edad_promedio=Avg(
                models.functions.Extract(
                    timezone.now().date() - models.F("fecha_nac"), "days"
                )
                / 365
            ),
        )


class DatosLaboralesManager(models.Manager):
    """Custom manager for DatosLaborales model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def activos(self):
        """Get active labor data."""
        return self.filter(estado=True)

    def cesados(self):
        """Get employees who have left."""
        return self.filter(fecha_cese__isnull=False)

    def vigentes(self):
        """Get current active employees."""
        return self.filter(estado=True, fecha_cese__isnull=True)

    def por_regimen(self, regimen: str):
        """Filter by labor regime.

        Args:
            regimen: Labor regime

        Returns:
            QuerySet: Filtered labor data
        """
        return self.filter(reg_laboral__icontains=regimen)

    def por_condicion(self, condicion: str):
        """Filter by employment condition.

        Args:
            condicion: Employment condition

        Returns:
            QuerySet: Filtered labor data
        """
        return self.filter(condicion__icontains=condicion)

    def por_categoria(self, categoria: str):
        """Filter by category.

        Args:
            categoria: Employee category

        Returns:
            QuerySet: Filtered labor data
        """
        return self.filter(categoria__icontains=categoria)

    def por_rango_salarial(self, salario_min: float = None, salario_max: float = None):
        """Filter by salary range.

        Args:
            salario_min: Minimum salary
            salario_max: Maximum salary

        Returns:
            QuerySet: Filtered labor data
        """
        filters = Q()

        if salario_min is not None:
            filters &= Q(remuneracion__gte=salario_min)

        if salario_max is not None:
            filters &= Q(remuneracion__lte=salario_max)

        return self.filter(filters)

    def antiguedad_mayor_a(self, años: int):
        """Get employees with seniority greater than specified years.

        Args:
            años: Years of seniority

        Returns:
            QuerySet: Filtered labor data
        """
        fecha_limite = timezone.now().date() - timedelta(days=años * 365)
        return self.filter(fecha_ingreso__lte=fecha_limite)

    def estadisticas_salariales(self):
        """Get salary statistics."""
        return self.aggregate(
            salario_promedio=Avg("remuneracion"),
            salario_minimo=models.Min("remuneracion"),
            salario_maximo=models.Max("remuneracion"),
            total_planilla=Sum("remuneracion"),
        )

    def por_meta(self, meta: str):
        """Filter by budget meta.

        Args:
            meta: Budget meta

        Returns:
            QuerySet: Filtered labor data
        """
        return self.filter(meta=meta)


# BoletaManager eliminado - reemplazado por DocumentosDigitalesManager con filtros por tipo_documento='BOLETA_PAGO'


class HistorialUbicacionesManager(models.Manager):
    """Custom manager for HistorialUbicaciones model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado", "area_destino")

    def activas(self):
        """Get active location records."""
        return self.filter(estado=True)

    def vigentes(self):
        """Get current location records."""
        return self.filter(estado=True, fecha_termino__isnull=True)

    def historicas(self):
        """Get historical location records."""
        return self.filter(fecha_termino__isnull=False)

    def por_area(self, area_id: int):
        """Filter by area.

        Args:
            area_id: Area ID

        Returns:
            QuerySet: Filtered location records
        """
        return self.filter(area_id=area_id)

    def por_empleado(self, empleado_id: int):
        """Get location history for employee.

        Args:
            empleado_id: Employee ID

        Returns:
            QuerySet: Employee location history
        """
        return self.filter(empleado_id=empleado_id).order_by("-fecha_inicio")

    def ubicacion_actual_empleado(self, empleado_id: int):
        """Get current location for employee.

        Args:
            empleado_id: Employee ID

        Returns:
            HistorialUbicaciones: Current location or None
        """
        return self.filter(
            empleado_id=empleado_id, estado=True, fecha_termino__isnull=True
        ).first()


class UsuarioManager(models.Manager):
    """Custom manager for Usuario model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def get_by_natural_key(self, username):
        """Get user by username (natural key)."""
        return self.get(username=username)

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create and return a regular user."""
        if not username:
            raise ValueError("El username es obligatorio")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)

    def activos(self):
        """Get active users."""
        return self.filter(estado=True)

    def inactivos(self):
        """Get inactive users."""
        return self.filter(estado=False)

    def con_roles(self):
        """Get users with their roles."""
        return self.prefetch_related("rol_set")

    def por_rol(self, nombre_rol: str):
        """Filter users by role.

        Args:
            nombre_rol: Role name

        Returns:
            QuerySet: Users with specified role
        """
        return self.filter(rol__nombre__icontains=nombre_rol)

    def login_reciente(self, dias: int = 30):
        """Get users with recent login.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Users with recent login
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_ult_login__gte=fecha_limite)

    def buscar(self, termino: str):
        """Search users by username or employee data.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching users
        """
        return self.filter(
            Q(nombres_usuario__icontains=termino)
            | Q(empleado__nombres_empleado__icontains=termino)
            | Q(empleado__apellido_paterno__icontains=termino)
            | Q(empleado__apellido_materno__icontains=termino)
        )


class DatosFamiliaresManager(models.Manager):
    """Custom manager for DatosFamiliares model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def activos(self):
        """Get active family records."""
        return self.filter(estado_familiar="activo")

    def por_parentesco(self, parentesco: str):
        """Filter by relationship type.

        Args:
            parentesco: Type of relationship

        Returns:
            QuerySet: Filtered family data
        """
        return self.filter(parentesco__icontains=parentesco)

    def hijos(self):
        """Get children records."""
        return self.filter(parentesco__in=["hijo", "hija"])

    def conyuges(self):
        """Get spouse records."""
        return self.filter(parentesco__in=["esposo", "esposa", "conviviente"])

    def menores_edad(self):
        """Get minors."""
        fecha_limite = timezone.now().date() - timedelta(days=18 * 365)
        return self.filter(fecha_nacimiento_familiar__gte=fecha_limite)

    def beneficiarios_seguro(self):
        """Get insurance beneficiaries."""
        return self.filter(es_beneficiario_seguro=True)

    def dependientes_economicos(self):
        """Get economic dependents."""
        return self.filter(es_dependiente_economico=True)

    def por_genero(self, genero: str):
        """Filter by gender.

        Args:
            genero: Gender

        Returns:
            QuerySet: Filtered family data
        """
        return self.filter(genero_familiar=genero)

    def buscar(self, termino: str):
        """Search family members by name or document.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching family members
        """
        return self.filter(
            Q(nombres_familiar__icontains=termino)
            | Q(apellido_paterno_familiar__icontains=termino)
            | Q(apellido_materno_familiar__icontains=termino)
            | Q(numero_documento_familiar__icontains=termino)
        )


class DatosAcademicosManager(models.Manager):
    """Custom manager for DatosAcademicos model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def por_tipo_formacion(self, tipo_formacion: str):
        """Filter by formation type.

        Args:
            tipo_formacion: Formation type

        Returns:
            QuerySet: Filtered academic data
        """
        return self.filter(tipo_formacion=tipo_formacion)

    def universitarios(self):
        """Get university records."""
        return self.filter(tipo_formacion="UNIVERSITARIO")

    def postgrados(self):
        """Get postgraduate records."""
        return self.filter(tipo_formacion__in=["POSTGRADO", "MAESTRIA", "DOCTORADO"])

    def cursos(self):
        """Get course records."""
        return self.filter(tipo_formacion="CURSO")

    def certificaciones(self):
        """Get certification records."""
        return self.filter(tipo_formacion="CERTIFICACION")

    def completados(self):
        """Get completed studies."""
        return self.filter(estado_estudios="completado")

    def en_curso(self):
        """Get ongoing studies."""
        return self.filter(estado_estudios="en_curso")

    def recientes(self, años: int = 5):
        """Get recent academic records.

        Args:
            años: Number of years

        Returns:
            QuerySet: Recent academic records
        """
        fecha_limite = timezone.now().date() - timedelta(days=años * 365)
        return self.filter(fecha_inicio_estudios__gte=fecha_limite)

    def por_institucion(self, institucion: str):
        """Filter by educational institution.

        Args:
            institucion: Institution name

        Returns:
            QuerySet: Filtered academic data
        """
        return self.filter(nombre_institucion__icontains=institucion)

    def con_titulo(self):
        """Get records with title."""
        return self.filter(titulo_obtenido__isnull=False)

    def por_pais(self, pais: str):
        """Filter by country of studies.

        Args:
            pais: Country name

        Returns:
            QuerySet: Filtered academic data
        """
        return self.filter(pais_estudios__icontains=pais)

    def buscar(self, termino: str):
        """Search academic records by multiple fields.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching academic records
        """
        return self.filter(
            Q(nombre_institucion__icontains=termino)
            | Q(carrera_especialidad__icontains=termino)
            | Q(titulo_obtenido__icontains=termino)
        )


class DocumentosDigitalesManager(models.Manager):
    """Custom manager for DocumentosDigitales model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado", "subido_por_usuario")

    def activos(self):
        """Get active documents."""
        return self.filter(estado_documento="activo")

    def vencidos(self):
        """Get expired documents."""
        return self.filter(
            fecha_vencimiento__lt=timezone.now().date(), estado_documento="activo"
        )

    def por_vencer(self, dias: int = 30):
        """Get documents expiring soon.

        Args:
            dias: Days until expiration

        Returns:
            QuerySet: Documents expiring soon
        """
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        return self.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=timezone.now().date(),
            estado_documento="activo",
        )

    def por_tipo(self, tipo_documento: str):
        """Filter by document type.

        Args:
            tipo_documento: Document type

        Returns:
            QuerySet: Filtered documents
        """
        return self.filter(tipo_documento=tipo_documento)

    def obligatorios(self):
        """Get mandatory documents."""
        return self.filter(es_documento_obligatorio=True)

    def confidenciales(self):
        """Get confidential documents."""
        return self.filter(es_documento_confidencial=True)

    def recientes(self, dias: int = 30):
        """Get recently uploaded documents.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent documents
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_subida__gte=fecha_limite)

    def buscar(self, termino: str):
        """Search documents by name or description.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching documents
        """
        return self.filter(
            Q(nombre_archivo__icontains=termino)
            | Q(descripcion_documento__icontains=termino)
        )


class ModulosManager(models.Manager):
    """Custom manager for Modulos model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().order_by("orden_visualizacion")

    def activos(self):
        """Get active modules."""
        return self.filter(estado_modulo="activo")

    def inactivos(self):
        """Get inactive modules."""
        return self.filter(estado_modulo="inactivo")

    def en_mantenimiento(self):
        """Get modules in maintenance."""
        return self.filter(estado_modulo="mantenimiento")

    def ordenados(self):
        """Get modules ordered by visualization order."""
        return self.order_by("orden_visualizacion")

    def buscar(self, termino: str):
        """Search modules by name or description.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching modules
        """
        return self.filter(
            Q(nombre_modulo__icontains=termino)
            | Q(descripcion_modulo__icontains=termino)
        )


class RolPermisosManager(models.Manager):
    """Custom manager for RolPermisos model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return (
            super()
            .get_queryset()
            .select_related("rol", "permiso", "asignado_por_usuario")
        )

    def por_rol(self, rol_id: int):
        """Get permissions for specific role.

        Args:
            rol_id: Role ID

        Returns:
            QuerySet: Role permissions
        """
        return self.filter(rol_id=rol_id)

    def por_permiso(self, permiso_id: int):
        """Get roles with specific permission.

        Args:
            permiso_id: Permission ID

        Returns:
            QuerySet: Role permissions
        """
        return self.filter(permiso_id=permiso_id)

    def recientes(self, dias: int = 30):
        """Get recently assigned permissions.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent assignments
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_asignacion__gte=fecha_limite)

    def por_usuario_asignador(self, usuario_id: int):
        """Get permissions assigned by specific user.

        Args:
            usuario_id: User ID

        Returns:
            QuerySet: Assigned permissions
        """
        return self.filter(asignado_por_usuario_id=usuario_id)


class UsuarioRolesManager(models.Manager):
    """Custom manager for UsuarioRoles model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return (
            super()
            .get_queryset()
            .select_related("usuario", "rol", "asignado_por_usuario")
        )

    def activos(self):
        """Get active role assignments."""
        return self.filter(estado_asignacion="activo")

    def vigentes(self):
        """Get current valid role assignments."""
        return self.filter(
            Q(estado_asignacion="activo")
            & (
                Q(fecha_expiracion__isnull=True)
                | Q(fecha_expiracion__gt=timezone.now())
            )
        )

    def expirados(self):
        """Get expired role assignments."""
        return self.filter(
            fecha_expiracion__lt=timezone.now(), estado_asignacion="activo"
        )

    def por_expirar(self, dias: int = 30):
        """Get role assignments expiring soon.

        Args:
            dias: Days until expiration

        Returns:
            QuerySet: Assignments expiring soon
        """
        fecha_limite = timezone.now() + timedelta(days=dias)
        return self.filter(
            fecha_expiracion__lte=fecha_limite,
            fecha_expiracion__gt=timezone.now(),
            estado_asignacion="activo",
        )

    def por_usuario(self, usuario_id: int):
        """Get role assignments for specific user.

        Args:
            usuario_id: User ID

        Returns:
            QuerySet: User role assignments
        """
        return self.filter(usuario_id=usuario_id)

    def por_rol(self, rol_id: int):
        """Get users with specific role.

        Args:
            rol_id: Role ID

        Returns:
            QuerySet: Role assignments
        """
        return self.filter(rol_id=rol_id)

    def recientes(self, dias: int = 30):
        """Get recently assigned roles.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent assignments
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_asignacion__gte=fecha_limite)

    def por_usuario_asignador(self, usuario_id: int):
        """Get roles assigned by specific user.

        Args:
            usuario_id: User ID

        Returns:
            QuerySet: Assigned roles
        """
        return self.filter(asignado_por_usuario_id=usuario_id)


# ============================================================================
# MANAGERS DEL MÓDULO DE VACACIONES
# ============================================================================


class ConfiguracionVacacionesManager(models.Manager):
    """Custom manager for ConfiguracionVacaciones model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().order_by("parametro_config")

    def editables(self):
        """Get only editable configurations."""
        return self.filter(es_editable=True)

    def por_tipo(self, tipo_dato: str):
        """Filter configurations by data type.

        Args:
            tipo_dato: Data type

        Returns:
            QuerySet: Filtered configurations
        """
        return self.filter(tipo_dato=tipo_dato)

    def obtener_valor(self, parametro: str, default=None):
        """Get configuration value by parameter.

        Args:
            parametro: Parameter name
            default: Default value if not found

        Returns:
            Any: Configuration value
        """
        try:
            config = self.get(parametro_config=parametro)
            return config.valor_convertido
        except self.model.DoesNotExist:
            return default

    def establecer_valor(
        self,
        parametro: str,
        valor: str,
        descripcion: str = None,
        tipo_dato: str = "texto",
    ):
        """Set configuration value.

        Args:
            parametro: Parameter name
            valor: Parameter value
            descripcion: Parameter description
            tipo_dato: Data type

        Returns:
            ConfiguracionVacaciones: Configuration instance
        """
        config, created = self.update_or_create(
            parametro_config=parametro,
            defaults={
                "valor_config": valor,
                "descripcion_config": descripcion,
                "tipo_dato": tipo_dato,
            },
        )
        return config


class PeriodoVacacionalManager(models.Manager):
    """Custom manager for PeriodoVacacional model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related("empleado")

    def vigentes(self):
        """Get only active vacation periods."""
        return self.filter(estado_periodo="vigente")

    def vencidos(self):
        """Get expired vacation periods."""
        return self.filter(estado_periodo="vencido")

    def por_vencer(self, dias: int = 30):
        """Get periods expiring soon.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Periods expiring soon
        """
        fecha_limite = timezone.now().date() + timedelta(days=dias)
        return self.vigentes().filter(fecha_vencimiento__lte=fecha_limite)

    def por_empleado(self, empleado_id: int):
        """Get periods for specific employee.

        Args:
            empleado_id: Employee ID

        Returns:
            QuerySet: Employee periods
        """
        return self.filter(empleado_id=empleado_id)

    def por_anio(self, anio: int):
        """Get periods for specific year.

        Args:
            anio: Year

        Returns:
            QuerySet: Year periods
        """
        return self.filter(anio_periodo=anio)

    def con_saldo_disponible(self):
        """Get periods with available vacation days."""
        return self.vigentes().extra(where=["dias_generados > dias_gozados"])

    def estadisticas_por_anio(self, anio: int):
        """Get statistics for specific year.

        Args:
            anio: Year

        Returns:
            Dict: Statistics
        """
        periodos = self.por_anio(anio)
        return {
            "total_periodos": periodos.count(),
            "vigentes": periodos.filter(estado_periodo="vigente").count(),
            "vencidos": periodos.filter(estado_periodo="vencido").count(),
            "total_dias_generados": periodos.aggregate(Sum("dias_generados"))[
                "dias_generados__sum"
            ]
            or 0,
            "total_dias_gozados": periodos.aggregate(Sum("dias_gozados"))[
                "dias_gozados__sum"
            ]
            or 0,
        }


class SolicitudVacacionesManager(models.Manager):
    """Custom manager for SolicitudVacaciones model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return (
            super()
            .get_queryset()
            .select_related("empleado", "periodo", "revisado_por_usuario")
        )

    def borradores(self):
        """Get draft requests."""
        return self.filter(estado_solicitud="borrador")

    def enviadas(self):
        """Get sent requests."""
        return self.filter(estado_solicitud="enviada")

    def pendientes(self):
        """Get pending requests."""
        return self.filter(estado_solicitud__in=["enviada", "en_revision"])

    def aprobadas(self):
        """Get approved requests."""
        return self.filter(estado_solicitud="aprobada")

    def rechazadas(self):
        """Get rejected requests."""
        return self.filter(estado_solicitud="rechazada")

    def fraccionadas(self):
        """Get fractional requests."""
        return self.filter(tipo_solicitud="fraccionada")

    def completas(self):
        """Get complete requests."""
        return self.filter(tipo_solicitud="completa")

    def por_empleado(self, empleado_id: int):
        """Get requests for specific employee.

        Args:
            empleado_id: Employee ID

        Returns:
            QuerySet: Employee requests
        """
        return self.filter(empleado_id=empleado_id)

    def por_periodo(self, periodo_id: int):
        """Get requests for specific period.

        Args:
            periodo_id: Period ID

        Returns:
            QuerySet: Period requests
        """
        return self.filter(periodo_id=periodo_id)

    def por_revisor(self, usuario_id: int):
        """Get requests reviewed by specific user.

        Args:
            usuario_id: User ID

        Returns:
            QuerySet: Reviewed requests
        """
        return self.filter(revisado_por_usuario_id=usuario_id)

    def por_fechas(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Get requests within date range.

        Args:
            fecha_inicio: Start date
            fecha_fin: End date

        Returns:
            QuerySet: Requests in date range
        """
        return self.filter(
            fecha_inicio_solicitud__gte=fecha_inicio, fecha_fin_solicitud__lte=fecha_fin
        )

    def recientes(self, dias: int = 30):
        """Get recent requests.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent requests
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_registro__gte=fecha_limite)

    def estadisticas_por_estado(self):
        """Get statistics by status.

        Returns:
            Dict: Statistics
        """
        return (
            self.values("estado_solicitud")
            .annotate(total=Count("solicitud_id"))
            .order_by("estado_solicitud")
        )


class GoceVacacionesManager(models.Manager):
    """Custom manager for GoceVacaciones model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return (
            super()
            .get_queryset()
            .select_related(
                "solicitud", "empleado", "periodo", "registrado_por_usuario"
            )
        )

    def fraccionados(self):
        """Get fractional enjoyments."""
        return self.filter(tipo_goce="fraccionado")

    def completos(self):
        """Get complete enjoyments."""
        return self.filter(tipo_goce="completo")

    def medio_dia(self):
        """Get half-day enjoyments."""
        return self.filter(tipo_goce="medio_dia")

    def por_empleado(self, empleado_id: int):
        """Get enjoyments for specific employee.

        Args:
            empleado_id: Employee ID

        Returns:
            QuerySet: Employee enjoyments
        """
        return self.filter(empleado_id=empleado_id)

    def por_periodo(self, periodo_id: int):
        """Get enjoyments for specific period.

        Args:
            periodo_id: Period ID

        Returns:
            QuerySet: Period enjoyments
        """
        return self.filter(periodo_id=periodo_id)

    def por_solicitud(self, solicitud_id: int):
        """Get enjoyments for specific request.

        Args:
            solicitud_id: Request ID

        Returns:
            QuerySet: Request enjoyments
        """
        return self.filter(solicitud_id=solicitud_id)

    def por_fechas(self, fecha_inicio: datetime, fecha_fin: datetime):
        """Get enjoyments within date range.

        Args:
            fecha_inicio: Start date
            fecha_fin: End date

        Returns:
            QuerySet: Enjoyments in date range
        """
        return self.filter(
            fecha_inicio_goce__gte=fecha_inicio, fecha_fin_goce__lte=fecha_fin
        )

    def con_documento(self):
        """Get enjoyments with authorization document."""
        return self.exclude(documento_autorizacion__isnull=True).exclude(
            documento_autorizacion=""
        )

    def sin_documento(self):
        """Get enjoyments without authorization document."""
        return self.filter(
            Q(documento_autorizacion__isnull=True) | Q(documento_autorizacion="")
        )

    def recientes(self, dias: int = 30):
        """Get recent enjoyments.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent enjoyments
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_registro__gte=fecha_limite)

    def estadisticas_por_tipo(self):
        """Get statistics by type.

        Returns:
            Dict: Statistics
        """
        return (
            self.values("tipo_goce")
            .annotate(total=Count("goce_id"), total_dias=Sum("dias_gozados"))
            .order_by("tipo_goce")
        )


class HistorialSolicitudVacacionesManager(models.Manager):
    """Custom manager for HistorialSolicitudVacaciones model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return (
            super()
            .get_queryset()
            .select_related("solicitud", "usuario_cambio")
            .order_by("-fecha_cambio")
        )

    def por_solicitud(self, solicitud_id: int):
        """Get history for specific request.

        Args:
            solicitud_id: Request ID

        Returns:
            QuerySet: Request history
        """
        return self.filter(solicitud_id=solicitud_id)

    def por_usuario(self, usuario_id: int):
        """Get changes made by specific user.

        Args:
            usuario_id: User ID

        Returns:
            QuerySet: User changes
        """
        return self.filter(usuario_cambio_id=usuario_id)

    def aprobaciones(self):
        """Get approval changes."""
        return self.filter(estado_nuevo="aprobada")

    def rechazos(self):
        """Get rejection changes."""
        return self.filter(estado_nuevo="rechazada")

    def cambios_iniciales(self):
        """Get initial state changes."""
        return self.filter(estado_anterior__isnull=True)

    def recientes(self, dias: int = 30):
        """Get recent changes.

        Args:
            dias: Number of days

        Returns:
            QuerySet: Recent changes
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return self.filter(fecha_cambio__gte=fecha_limite)

    def estadisticas_por_estado(self):
        """Get statistics by new state.

        Returns:
            Dict: Statistics
        """
        return (
            self.values("estado_nuevo")
            .annotate(total=Count("historial_id"))
            .order_by("estado_nuevo")
        )


class RolManager(models.Manager):
    """Custom manager for Rol model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related()

    def activos(self):
        """Get only active roles."""
        return self.filter(estado_rol="activo")

    def inactivos(self):
        """Get only inactive roles."""
        return self.filter(estado_rol="inactivo")

    def sistema(self):
        """Get system roles."""
        return self.filter(es_rol_sistema=True)

    def personalizados(self):
        """Get custom roles."""
        return self.filter(es_rol_sistema=False)

    def por_nivel(self, nivel: int):
        """Filter roles by hierarchical level.

        Args:
            nivel: Hierarchical level

        Returns:
            QuerySet: Filtered roles
        """
        return self.filter(nivel_jerarquico=nivel)

    def buscar(self, termino: str):
        """Search roles by name or description.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching roles
        """
        return self.filter(
            Q(nombre_rol__icontains=termino) | Q(descripcion_rol__icontains=termino)
        )


class PermisoManager(models.Manager):
    """Custom manager for Permiso model."""

    def get_queryset(self):
        """Override queryset to optimize default queries."""
        return super().get_queryset().select_related()

    def activos(self):
        """Get only active permissions."""
        return self.filter(estado_permiso="activo")

    def inactivos(self):
        """Get only inactive permissions."""
        return self.filter(estado_permiso="inactivo")

    def por_tipo(self, tipo: str):
        """Filter permissions by type.

        Args:
            tipo: Permission type

        Returns:
            QuerySet: Filtered permissions
        """
        return self.filter(tipo_permiso=tipo)

    def por_modulo(self, modulo_id: int):
        """Filter permissions by module.

        Args:
            modulo_id: Module ID

        Returns:
            QuerySet: Filtered permissions
        """
        return self.filter(modulo__modulo_id=modulo_id)

    def crear(self):
        """Get create permissions."""
        return self.filter(tipo_permiso="crear")

    def leer(self):
        """Get read permissions."""
        return self.filter(tipo_permiso="leer")

    def actualizar(self):
        """Get update permissions."""
        return self.filter(tipo_permiso="actualizar")

    def eliminar(self):
        """Get delete permissions."""
        return self.filter(tipo_permiso="eliminar")

    def ejecutar(self):
        """Get execute permissions."""
        return self.filter(tipo_permiso="ejecutar")

    def aprobar(self):
        """Get approve permissions."""
        return self.filter(tipo_permiso="aprobar")

    def buscar(self, termino: str):
        """Search permissions by name or description.

        Args:
            termino: Search term

        Returns:
            QuerySet: Matching permissions
        """
        return self.filter(
            Q(nombre_permiso__icontains=termino)
            | Q(descripcion_permiso__icontains=termino)
        )
