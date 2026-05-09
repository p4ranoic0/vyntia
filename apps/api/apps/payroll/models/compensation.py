# -*- coding: utf-8 -*-
"""Modelos para configuración maestra de remuneraciones."""

import uuid
from decimal import Decimal

from django.db import models


class AfpConfiguration(models.Model):
    """Parámetros de AFP para cálculo de descuentos por planilla."""

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    afp_nombre = models.CharField(max_length=80)
    vigencia_mes = models.CharField(max_length=7, help_text="Formato YYYY-MM")
    aporte_obligatorio_pct = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("10.000")
    )
    comision_flujo_pct = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("0.000")
    )
    comision_mixta_pct = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("0.000")
    )
    prima_seguro_pct = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("1.370")
    )
    remuneracion_max_asegurable = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo", db_column="estado")
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "configuracion_afp"
        indexes = [
            models.Index(fields=["afp_nombre"]),
            models.Index(fields=["vigencia_mes"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "afp_nombre", "vigencia_mes"],
                name="uniq_config_afp_nombre_vigencia_per_tenant",
            ),
        ]
        ordering = ["-vigencia_mes", "afp_nombre"]

    def __str__(self):
        return f"{self.afp_nombre} ({self.vigencia_mes})"

    @property
    def es_activo(self):
        return self.status == "activo"


class CompensationConfiguration(models.Model):
    """Catálogo de conceptos para planilla: ingresos y descuentos."""

    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("descuento", "Descuento"),
    ]

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(null=True, blank=True)
    porcentaje = models.DecimalField(
        max_digits=6, decimal_places=3, default=Decimal("0.000")
    )
    monto_fijo = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    aplica_base_imponible = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo", db_column="estado")
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "configuracion_remuneracion"
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["status"]),
            models.Index(fields=["orden"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "tipo", "codigo"],
                name="uniq_config_remuneracion_tipo_codigo_per_tenant",
            ),
        ]
        ordering = ["tipo", "orden", "nombre"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    @property
    def es_activo(self):
        return self.status == "activo"


class MonthlyPayroll(models.Model):
    """Cabecera de planilla mensual por período y modalidad."""

    MODALIDAD_CHOICES = [
        ("plazo_indeterminado", "Plazo Indeterminado"),
        ("plazo_determinado", "Plazo Determinado"),
        ("subsidio", "Subsidio"),
        ("locacion", "Locación de Servicios"),
        ("consultoria", "Consultoría"),
    ]

    ESTADO_CHOICES = [
        ("borrador", "Borrador"),
        ("procesando", "En Proceso"),
        ("generada", "Generada"),
        ("aprobada", "Aprobada"),
        ("pagada", "Pagada"),
        ("anulada", "Anulada"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    periodo = models.CharField(max_length=7, help_text="Formato YYYY-MM")
    modalidad = models.CharField(max_length=30, choices=MODALIDAD_CHOICES)
    meta_presupuestal = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    # Control de estado y totales
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="borrador", db_column="estado")
    total_trabajadores = models.PositiveIntegerField(default=0)
    total_remuneracion_bruta = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_descuentos = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_neto_pagar = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_essalud = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_aporte_afp = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    total_onp = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )

    # Fechas de proceso
    fecha_generacion = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    fecha_pago = models.DateField(null=True, blank=True)

    # Auditoría
    usuario_generacion = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="planillas_generadas",
        null=True,
        blank=True,
    )
    usuario_aprobacion = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="planillas_aprobadas",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "planilla_mensual"
        indexes = [
            models.Index(fields=["periodo"]),
            models.Index(fields=["modalidad"]),
            models.Index(fields=["status"]),
            models.Index(fields=["meta_presupuestal"]),
            models.Index(fields=["-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "periodo", "modalidad", "meta_presupuestal"],
                name="uniq_planilla_periodo_modalidad_meta_per_tenant",
            ),
        ]
        ordering = ["-periodo", "modalidad"]

    def __str__(self):
        return f"Planilla {self.get_modalidad_display()} - {self.periodo}"

    @property
    def esta_cerrada(self):
        """Indica si la planilla ya no puede modificarse."""
        return self.status in ["aprobada", "pagada", "anulada"]

    @property
    def puede_generarse(self):
        """Indica si la planilla puede procesarse."""
        return self.status in ["borrador", "procesando"]


class PayrollDetail(models.Model):
    """Detalle de planilla mensual por empleado."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    planilla = models.ForeignKey(
        MonthlyPayroll,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    empleado = models.ForeignKey(
        "employees.Employee",
        on_delete=models.PROTECT,
        related_name="detalles_planilla",
    )
    datos_laborales = models.ForeignKey(
        "contracts.EmploymentData",
        on_delete=models.PROTECT,
        related_name="detalles_planilla",
        null=True,
        blank=True,
    )

    # Información laboral al momento del cálculo
    area_nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    dni = models.CharField(max_length=20)
    sistema_pensiones = models.CharField(max_length=30)
    tipo_comision_afp = models.CharField(max_length=10, null=True, blank=True)
    cuspp = models.CharField(max_length=30, null=True, blank=True)

    # Control de estado laboral en el periodo
    estado_laboral = models.CharField(
        max_length=20,
        choices=[
            ("activo", "Activo"),
            ("licencia", "De Licencia"),
            ("suspendido", "Suspendido"),
            ("descanso_medico", "Descanso Médico"),
        ],
        default="activo",
        help_text="Estado laboral del empleado en el periodo",
    )

    # Días y valores base
    dias_laborados = models.PositiveIntegerField(default=30)
    dias_no_laborados = models.PositiveIntegerField(default=0)
    dias_subsidiados = models.PositiveIntegerField(default=0)

    # Remuneraciones y haberes
    remuneracion_basica = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    asignacion_familiar = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    bonificacion_especial = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    otras_bonificaciones = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_haberes = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Descuentos sistema pensiones
    aporte_afp_obligatorio = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    comision_afp = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    prima_seguro_afp = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_afp = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    aporte_onp = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Otros descuentos
    renta_quinta_categoria = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    tiene_suspension_renta_cuarta = models.BooleanField(
        default=False,
        help_text="Indica si el empleado presentó suspensión de retención de renta de 4ta categoría",
    )
    tope_suspension_anual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Monto acumulado anual para control de tope de suspensión",
    )
    descuentos_judiciales = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    prestamos = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    otros_descuentos = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    total_descuentos = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Aportes del empleador
    essalud = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Neto a pagar
    neto_pagar = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Información bancaria
    banco = models.CharField(max_length=100, null=True, blank=True)
    numero_cuenta = models.CharField(max_length=50, null=True, blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "detalle_planilla"
        indexes = [
            models.Index(fields=["planilla"]),
            models.Index(fields=["empleado"]),
            models.Index(fields=["dni"]),
            models.Index(fields=["sistema_pensiones"]),
            models.Index(fields=["banco"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "planilla", "empleado"],
                name="uniq_detalle_planilla_empleado_per_tenant",
            ),
        ]
        ordering = ["area_nombre", "empleado__apellido_paterno"]

    def __str__(self):
        return f"{self.planilla.periodo} - {self.empleado}"


class PayrollConcept(models.Model):
    """Conceptos adicionales aplicados a empleados en planilla (haberes/descuentos variables)."""

    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("descuento", "Descuento"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    detalle_planilla = models.ForeignKey(
        PayrollDetail,
        on_delete=models.CASCADE,
        related_name="conceptos",
    )
    configuracion_concepto = models.ForeignKey(
        CompensationConfiguration,
        on_delete=models.PROTECT,
        related_name="aplicaciones_planilla",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=120)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")

    class Meta:
        db_table = "concepto_planilla"
        indexes = [
            models.Index(fields=["detalle_planilla"]),
            models.Index(fields=["tipo"]),
            models.Index(fields=["codigo"]),
        ]
        ordering = ["tipo", "codigo"]

    def __str__(self):
        return f"{self.nombre} - {self.monto}"


class MassDeduction(models.Model):
    """Registro de descuentos masivos cargados para aplicar en planilla."""

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("procesado", "Procesado"),
        ("aplicado", "Aplicado"),
        ("anulado", "Anulado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    periodo = models.CharField(max_length=7, help_text="Formato YYYY-MM")
    configuracion_concepto = models.ForeignKey(
        CompensationConfiguration,
        on_delete=models.PROTECT,
        related_name="descuentos_masivos",
        limit_choices_to={"tipo": "descuento"},
    )
    archivo_origen = models.FileField(
        upload_to="descuentos_masivos/%Y/%m/",
        help_text="Archivo Excel con descuentos masivos",
    )
    total_registros = models.PositiveIntegerField(default=0)
    registros_procesados = models.PositiveIntegerField(default=0)
    registros_error = models.PositiveIntegerField(default=0)
    monto_total = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente", db_column="estado"
    )
    errores_log = models.TextField(null=True, blank=True)

    # Auditoría
    usuario_carga = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="descuentos_masivos_cargados",
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)
    fecha_procesado = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "descuento_masivo"
        indexes = [
            models.Index(fields=["periodo"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-fecha_carga"]),
        ]
        ordering = ["-fecha_carga"]

    def __str__(self):
        return f"Descuento Masivo {self.configuracion_concepto.nombre} - {self.periodo}"


class PaySlip(models.Model):
    """Boletas de pago generadas para empleados."""

    ESTADO_CHOICES = [
        ("generada", "Generada"),
        ("enviada", "Enviada"),
        ("descargada", "Descargada"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    detalle_planilla = models.OneToOneField(
        PayrollDetail,
        on_delete=models.CASCADE,
        related_name="boleta",
    )
    archivo_pdf = models.FileField(
        upload_to="boletas_pago/%Y/%m/",
        help_text="Archivo PDF de la boleta",
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="generada", db_column="estado")
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_envio_email = models.DateTimeField(null=True, blank=True)
    fecha_descarga = models.DateTimeField(null=True, blank=True)
    hash_documento = models.CharField(
        max_length=64, null=True, blank=True, help_text="SHA-256 del PDF"
    )

    class Meta:
        db_table = "boleta_pago"
        indexes = [
            models.Index(fields=["detalle_planilla"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-fecha_generacion"]),
        ]
        ordering = ["-fecha_generacion"]

    def __str__(self):
        return f"Boleta {self.detalle_planilla.empleado} - {self.detalle_planilla.planilla.periodo}"


class PaymentSchedule(models.Model):
    """Calendarios de pago programados para liquidaciones automáticas."""

    TIPO_PAGO_CHOICES = [
        ("mensual", "Mensual"),
        ("quincenal", "Quincenal"),
        ("semanal", "Semanal"),
        ("extraordinario", "Extraordinario"),
    ]

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("completado", "Completado"),
        ("cancelado", "Cancelado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    planilla = models.ForeignKey(
        MonthlyPayroll,
        on_delete=models.CASCADE,
        related_name="calendarios_pago",
    )
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    fecha_pago_programada = models.DateField()
    fecha_pago_ejecutada = models.DateField(null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo", db_column="estado")

    # Auditoría
    usuario_programacion = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="calendarios_programados",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")

    class Meta:
        db_table = "calendario_pago"
        indexes = [
            models.Index(fields=["planilla"]),
            models.Index(fields=["fecha_pago_programada"]),
            models.Index(fields=["status"]),
            models.Index(fields=["-created_at"]),
        ]
        ordering = ["fecha_pago_programada"]

    def __str__(self):
        return f"Pago {self.get_tipo_pago_display()} - {self.fecha_pago_programada}"
