# -*- coding: utf-8 -*-
"""Modelos para configuración maestra de remuneraciones."""

from decimal import Decimal

from django.db import models


class ConfiguracionAfp(models.Model):
    """Parámetros de AFP para cálculo de descuentos por planilla."""

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    afp_config_id = models.AutoField(primary_key=True)
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
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "configuracion_afp"
        indexes = [
            models.Index(fields=["afp_nombre"]),
            models.Index(fields=["vigencia_mes"]),
            models.Index(fields=["estado"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["afp_nombre", "vigencia_mes"],
                name="uniq_config_afp_nombre_vigencia",
            ),
        ]
        ordering = ["-vigencia_mes", "afp_nombre"]

    def __str__(self):
        return f"{self.afp_nombre} ({self.vigencia_mes})"

    @property
    def es_activo(self):
        return self.estado == "activo"


class ConfiguracionRemuneracion(models.Model):
    """Catálogo de conceptos para planilla: ingresos y descuentos."""

    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("descuento", "Descuento"),
    ]

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    configuracion_id = models.AutoField(primary_key=True)
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
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "configuracion_remuneracion"
        indexes = [
            models.Index(fields=["tipo"]),
            models.Index(fields=["codigo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["orden"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tipo", "codigo"],
                name="uniq_config_remuneracion_tipo_codigo",
            ),
        ]
        ordering = ["tipo", "orden", "nombre"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    @property
    def es_activo(self):
        return self.estado == "activo"


class PlanillaMensual(models.Model):
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

    planilla_id = models.AutoField(primary_key=True)
    periodo = models.CharField(max_length=7, help_text="Formato YYYY-MM")
    modalidad = models.CharField(max_length=30, choices=MODALIDAD_CHOICES)
    meta_presupuestal = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)

    # Control de estado y totales
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="borrador")
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
        "Usuario",
        on_delete=models.PROTECT,
        related_name="planillas_generadas",
        null=True,
        blank=True,
    )
    usuario_aprobacion = models.ForeignKey(
        "Usuario",
        on_delete=models.PROTECT,
        related_name="planillas_aprobadas",
        null=True,
        blank=True,
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "planilla_mensual"
        indexes = [
            models.Index(fields=["periodo"]),
            models.Index(fields=["modalidad"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["meta_presupuestal"]),
            models.Index(fields=["-fecha_creacion"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["periodo", "modalidad", "meta_presupuestal"],
                name="uniq_planilla_periodo_modalidad_meta",
            ),
        ]
        ordering = ["-periodo", "modalidad"]

    def __str__(self):
        return f"Planilla {self.get_modalidad_display()} - {self.periodo}"

    @property
    def esta_cerrada(self):
        """Indica si la planilla ya no puede modificarse."""
        return self.estado in ["aprobada", "pagada", "anulada"]

    @property
    def puede_generarse(self):
        """Indica si la planilla puede procesarse."""
        return self.estado in ["borrador", "procesando"]


class DetallePlanilla(models.Model):
    """Detalle de planilla mensual por empleado."""

    detalle_id = models.AutoField(primary_key=True)
    planilla = models.ForeignKey(
        PlanillaMensual,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    empleado = models.ForeignKey(
        "Empleado",
        on_delete=models.PROTECT,
        related_name="detalles_planilla",
    )
    datos_laborales = models.ForeignKey(
        "DatosLaborales",
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

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
                fields=["planilla", "empleado"],
                name="uniq_detalle_planilla_empleado",
            ),
        ]
        ordering = ["area_nombre", "empleado__apellido_paterno"]

    def __str__(self):
        return f"{self.planilla.periodo} - {self.empleado}"


class ConceptoPlanilla(models.Model):
    """Conceptos adicionales aplicados a empleados en planilla (haberes/descuentos variables)."""

    TIPO_CHOICES = [
        ("ingreso", "Ingreso"),
        ("descuento", "Descuento"),
    ]

    concepto_planilla_id = models.AutoField(primary_key=True)
    detalle_planilla = models.ForeignKey(
        DetallePlanilla,
        on_delete=models.CASCADE,
        related_name="conceptos",
    )
    configuracion_concepto = models.ForeignKey(
        ConfiguracionRemuneracion,
        on_delete=models.PROTECT,
        related_name="aplicaciones_planilla",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=30)
    nombre = models.CharField(max_length=120)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

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


class DescuentoMasivo(models.Model):
    """Registro de descuentos masivos cargados para aplicar en planilla."""

    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("procesado", "Procesado"),
        ("aplicado", "Aplicado"),
        ("anulado", "Anulado"),
    ]

    descuento_masivo_id = models.AutoField(primary_key=True)
    periodo = models.CharField(max_length=7, help_text="Formato YYYY-MM")
    configuracion_concepto = models.ForeignKey(
        ConfiguracionRemuneracion,
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
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )
    errores_log = models.TextField(null=True, blank=True)

    # Auditoría
    usuario_carga = models.ForeignKey(
        "Usuario",
        on_delete=models.PROTECT,
        related_name="descuentos_masivos_cargados",
    )
    fecha_carga = models.DateTimeField(auto_now_add=True)
    fecha_procesado = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "descuento_masivo"
        indexes = [
            models.Index(fields=["periodo"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["-fecha_carga"]),
        ]
        ordering = ["-fecha_carga"]

    def __str__(self):
        return f"Descuento Masivo {self.configuracion_concepto.nombre} - {self.periodo}"


class BoletaPago(models.Model):
    """Boletas de pago generadas para empleados."""

    ESTADO_CHOICES = [
        ("generada", "Generada"),
        ("enviada", "Enviada"),
        ("descargada", "Descargada"),
    ]

    boleta_id = models.AutoField(primary_key=True)
    detalle_planilla = models.OneToOneField(
        DetallePlanilla,
        on_delete=models.CASCADE,
        related_name="boleta",
    )
    archivo_pdf = models.FileField(
        upload_to="boletas_pago/%Y/%m/",
        help_text="Archivo PDF de la boleta",
        null=True,
        blank=True,
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="generada")
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
            models.Index(fields=["estado"]),
            models.Index(fields=["-fecha_generacion"]),
        ]
        ordering = ["-fecha_generacion"]

    def __str__(self):
        return f"Boleta {self.detalle_planilla.empleado} - {self.detalle_planilla.planilla.periodo}"


class CalendarioPago(models.Model):
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

    calendario_id = models.AutoField(primary_key=True)
    planilla = models.ForeignKey(
        PlanillaMensual,
        on_delete=models.CASCADE,
        related_name="calendarios_pago",
    )
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES)
    fecha_pago_programada = models.DateField()
    fecha_pago_ejecutada = models.DateField(null=True, blank=True)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo")

    # Auditoría
    usuario_programacion = models.ForeignKey(
        "Usuario",
        on_delete=models.PROTECT,
        related_name="calendarios_programados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendario_pago"
        indexes = [
            models.Index(fields=["planilla"]),
            models.Index(fields=["fecha_pago_programada"]),
            models.Index(fields=["estado"]),
            models.Index(fields=["-fecha_creacion"]),
        ]
        ordering = ["fecha_pago_programada"]

    def __str__(self):
        return f"Pago {self.get_tipo_pago_display()} - {self.fecha_pago_programada}"
