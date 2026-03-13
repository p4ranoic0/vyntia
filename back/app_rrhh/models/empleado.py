# -*- coding: utf-8 -*-
"""
Modelo Empleado - Gestión de información personal de empleados

Contiene la definición del modelo Empleado que almacena toda la información
personal, de contacto y básica de los empleados de la institución.
"""

from datetime import date

from django.db import models
from django.utils import timezone

# from ..managers import EmpleadoManager  # Comentado temporalmente para evitar error de importación


class Empleado(models.Model):
    """Modelo para gestionar la información personal de los empleados."""

    TIPO_DOCUMENTO_CHOICES = [
        ("DNI", "DNI"),
        ("CE", "Carné de Extranjería"),
        ("PASAPORTE", "Pasaporte"),
        ("OTROS", "Otros"),
    ]

    GENERO_CHOICES = [
        ("masculino", "Masculino"),
        ("femenino", "Femenino"),
        ("otro", "Otro"),
        ("no_especifica", "No especifica"),
    ]

    SISTEMA_PENSIONES_CHOICES = [
        ("ONP", "ONP"),
        ("AFP PRIMA", "AFP PRIMA"),
        ("AFP INTEGRA", "AFP INTEGRA"),
        ("AFP PROFUTURO", "AFP PROFUTURO"),
        ("AFP HABITAT", "AFP HABITAT"),
        ("PENSIONISTA-SPP", "PENSIONISTA-SPP"),
        ("PENSIONISTA-CMP", "PENSIONISTA-CMP"),
        ("PENSIONISTA-OTRO", "PENSIONISTA-OTRO"),
    ]

    TIPO_COMISION_CHOICES = [
        ("FLUJO", "FLUJO"),
        ("MIXTA", "MIXTA"),
    ]

    TIPO_SEGURO_CHOICES = [
        ("ESSALUD", "EsSalud"),
        ("EPS", "EPS"),
        ("PRIVADO", "Privado"),
        ("NINGUNO", "Ninguno"),
    ]

    ESTADO_CIVIL_CHOICES = [
        ("soltero", "Soltero"),
        ("casado", "Casado"),
        ("divorciado", "Divorciado"),
        ("viudo", "Viudo"),
        ("conviviente", "Conviviente"),
    ]

    TIPO_SANGRE_CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

    ESTADO_EMPLEADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("suspendido", "Suspendido"),
        ("cesado", "Cesado"),
    ]

    VIGENCIA_ESTADO_SEGURO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    # Campos principales
    empleado_id = models.AutoField(primary_key=True)
    numero_documento = models.CharField(max_length=20, unique=True)
    tipo_documento = models.CharField(
        max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default="DNI"
    )
    nombres_empleado = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    numero_ruc = models.CharField(max_length=20, null=True, blank=True)
    genero_empleado = models.CharField(max_length=15, choices=GENERO_CHOICES, default="masculino")
    fecha_nacimiento = models.DateField(null=True, blank=True)
    es_padre_familia = models.BooleanField(default=False)
    es_militar = models.BooleanField(default=False)
    sistema_pensiones = models.CharField(
        max_length=20, choices=SISTEMA_PENSIONES_CHOICES, default="ONP"
    )
    tipo_comision = models.CharField(
        max_length=10, choices=TIPO_COMISION_CHOICES, null=True, blank=True
    )
    codigo_cuspp = models.CharField(max_length=20, null=True, blank=True)
    tipo_seguro_salud = models.CharField(
        max_length=10, choices=TIPO_SEGURO_CHOICES, default="ESSALUD"
    )
    centro_salud = models.CharField(max_length=50, null=True, blank=True)
    direccion_centro_salud = models.CharField(max_length=150, null=True, blank=True)
    departamento_centro_salud = models.CharField(max_length=20, null=True, blank=True)
    vigencia_estado_seguro = models.CharField(
        max_length=10, choices=VIGENCIA_ESTADO_SEGURO_CHOICES, default="activo"
    )

    # Suspensión de renta de 4ta categoría
    tiene_suspension_renta_cuarta_vigente = models.BooleanField(
        default=False,
        help_text="Indica si tiene suspensión de renta de 4ta categoría vigente",
    )
    fecha_inicio_suspension_renta = models.DateField(
        null=True, blank=True, help_text="Fecha inicio de suspensión de renta 4ta"
    )
    fecha_fin_suspension_renta = models.DateField(
        null=True, blank=True, help_text="Fecha fin de suspensión de renta 4ta"
    )
    documento_suspension_renta = models.FileField(
        upload_to="suspensiones_renta/%Y/",
        null=True,
        blank=True,
        help_text="Documento de suspensión de retención SUNAT",
    )

    # Información de contacto
    telefono_fijo = models.CharField(max_length=20, null=True, blank=True)
    telefono_celular = models.CharField(max_length=20, blank=True, default='')
    correo_personal = models.EmailField(max_length=150, unique=True)

    # Información personal
    estado_civil = models.CharField(max_length=15, choices=ESTADO_CIVIL_CHOICES, blank=True, default='')
    direccion_domicilio = models.CharField(max_length=200, blank=True, default='')
    distrito_domicilio = models.CharField(max_length=100, blank=True, default='')
    provincia_domicilio = models.CharField(max_length=100, blank=True, default='')
    departamento_domicilio = models.CharField(max_length=100, blank=True, default='')

    # Información bancaria
    entidad_bancaria = models.CharField(max_length=100, blank=True, default='')
    numero_cuenta_bancaria = models.CharField(max_length=30, blank=True, default='')
    numero_cci = models.CharField(max_length=30, blank=True, default='')

    # Información física y médica
    tipo_sangre = models.CharField(
        max_length=3, choices=TIPO_SANGRE_CHOICES, null=True, blank=True
    )
    talla_empleado = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    peso_empleado = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    ruta_fotografia = models.CharField(max_length=255, null=True, blank=True)

    # Campos de control
    estado_empleado = models.CharField(
        max_length=15, choices=ESTADO_EMPLEADO_CHOICES, default="activo"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Manager personalizado
    # objects = EmpleadoManager()  # Comentado temporalmente

    class Meta:
        db_table = "empleado"  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=["numero_documento"]),
            models.Index(fields=["nombres_empleado"]),
            models.Index(fields=["estado_empleado"]),
            models.Index(fields=["fecha_nacimiento"]),
            models.Index(fields=["correo_personal"]),
            models.Index(fields=["genero_empleado"]),
            models.Index(fields=["tipo_documento"]),
            models.Index(fields=["sistema_pensiones"]),
            models.Index(fields=["tipo_comision"]),
            models.Index(fields=["estado_civil"]),
            models.Index(fields=["tipo_sangre"]),
            models.Index(fields=["es_padre_familia"]),
            models.Index(fields=["es_militar"]),
        ]

    def __str__(self):
        return f"{self.numero_documento} - {self.nombre_completo}"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del empleado."""
        return (
            f"{self.nombres_empleado} {self.apellido_paterno} {self.apellido_materno}"
        )

    @property
    def edad(self):
        """Calcula la edad del empleado."""
        if self.fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - self.fecha_nacimiento.year
            if hoy.month < self.fecha_nacimiento.month or (
                hoy.month == self.fecha_nacimiento.month
                and hoy.day < self.fecha_nacimiento.day
            ):
                edad -= 1
            return edad
        return None

    @property
    def genero_texto(self):
        """Retorna el género en formato texto."""
        return dict(self.GENERO_CHOICES).get(self.genero_empleado, self.genero_empleado)

    @property
    def es_activo(self):
        """Verifica si el empleado está activo."""
        return self.estado_empleado == "activo"

    @property
    def documento_completo(self):
        """Retorna el documento completo con tipo."""
        return f"{self.tipo_documento}: {self.numero_documento}"

    @property
    def contacto_principal(self):
        """Retorna el contacto principal (celular o fijo)."""
        return self.telefono_celular or self.telefono_fijo

    @property
    def direccion_completa(self):
        """Retorna la dirección completa."""
        return f"{self.direccion_domicilio}, {self.distrito_domicilio}, {self.provincia_domicilio}, {self.departamento_domicilio}"

    @property
    def imc(self):
        """Calcula el Índice de Masa Corporal."""
        if self.peso_empleado and self.talla_empleado and self.talla_empleado > 0:
            return round(
                float(self.peso_empleado) / (float(self.talla_empleado) ** 2), 2
            )
        return None

    def ubicacion_actual(self):
        """Obtiene la ubicación actual del empleado."""
        from .ubicacion import HistorialUbicaciones

        return HistorialUbicaciones.objects.filter(
            empleado=self, estado_ubicacion="activo"
        ).first()

    def datos_laborales_actuales(self):
        """Obtiene los datos laborales actuales del empleado."""
        from .datos_laborales import DatosLaborales

        return DatosLaborales.objects.filter(
            empleado=self, estado_datos="activo"
        ).first()

    def historial_ubicaciones(self):
        """Obtiene el historial de ubicaciones del empleado."""
        from .ubicacion import HistorialUbicaciones

        return HistorialUbicaciones.objects.filter(empleado=self).order_by(
            "-fecha_inicio"
        )

    def familiares_activos(self):
        """Obtiene los familiares activos del empleado."""
        from .datos_familiares import DatosFamiliares

        return DatosFamiliares.objects.filter(empleado=self, estado_familiar="activo")

    def formacion_academica(self):
        """Obtiene la formación académica del empleado."""
        from .datos_academicos import DatosAcademicos

        return DatosAcademicos.objects.filter(empleado=self).order_by(
            "-fecha_graduacion"
        )

    def boletas_recientes(self, meses=6):
        """Obtiene las boletas de pago recientes."""
        from datetime import timedelta

        fecha_limite = timezone.now().date() - timedelta(days=meses * 30)
        # Aquí se implementaría la lógica para obtener boletas
        # return BoletaPago.objects.filter(
        #     empleado=self,
        #     fecha_pago__gte=fecha_limite
        # ).order_by('-fecha_pago')
        return []  # ).order_by('-fecha_pago')
        return []
