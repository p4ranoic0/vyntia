"""Modelo para gestionar el proceso de onboarding de nuevos empleados."""

from django.db import models
from django.utils import timezone


class OnboardingEmpleado(models.Model):
    """Modelo para rastrear el estado de incorporacion de nuevos empleados."""

    ESTADO_ONBOARDING_CHOICES = [
        ('pendiente_datos', 'Pendiente de Datos Personales'),
        ('pendiente_documentos', 'Pendiente de Documentos'),
        ('pendiente_validacion', 'Pendiente de Validacion RRHH'),
        ('observado', 'Observado - Requiere Correccion'),
        ('completado', 'Completado'),
    ]

    # Primary key
    onboarding_id = models.AutoField(primary_key=True)

    # Relaciones principales
    empleado = models.OneToOneField(
        'Empleado',
        on_delete=models.CASCADE,
        related_name='onboarding',
    )
    usuario = models.OneToOneField(
        'Usuario',
        on_delete=models.CASCADE,
        related_name='onboarding',
    )

    # Estado del onboarding
    estado_onboarding = models.CharField(
        max_length=25,
        choices=ESTADO_ONBOARDING_CHOICES,
        default='pendiente_datos',
    )

    # Checklist de completitud
    datos_personales_completos = models.BooleanField(default=False)
    datos_laborales_completos = models.BooleanField(default=False)
    dni_subido = models.BooleanField(default=False)
    declaraciones_juradas_subidas = models.BooleanField(default=False)
    certificados_academicos_subidos = models.BooleanField(default=False)
    certificados_trabajo_subidos = models.BooleanField(default=False)
    documentos_familiares_subidos = models.BooleanField(default=False)

    # Validacion por RRHH
    validado_por = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='onboardings_validados',
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)

    # Email de bienvenida
    email_bienvenida_enviado = models.BooleanField(default=False)
    fecha_email_bienvenida = models.DateTimeField(null=True, blank=True)

    # Timestamps
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'onboarding_empleado'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['estado_onboarding']),
            models.Index(fields=['empleado']),
            models.Index(fields=['usuario']),
        ]

    def __str__(self):
        return f"Onboarding {self.empleado} - {self.get_estado_onboarding_display()}"

    @property
    def progreso_porcentaje(self):
        """Calcula el porcentaje de progreso del onboarding."""
        checks = [
            self.datos_personales_completos,
            self.datos_laborales_completos,
            self.dni_subido,
            self.declaraciones_juradas_subidas,
            self.certificados_academicos_subidos,
            self.certificados_trabajo_subidos,
            self.documentos_familiares_subidos,
        ]
        completados = sum(1 for c in checks if c)
        return round((completados / len(checks)) * 100)

    @property
    def progreso_aprobado(self):
        """
        Porcentaje de documentos aprobados individualmente por RRHH.
        Separate from progreso_porcentaje (which tracks upload completion).
        Returns int 0-100.
        """
        from app_rrhh.models.documentos_digitales import DocumentosDigitales
        total = DocumentosDigitales.objects.filter(
            empleado=self.empleado, es_version_actual=True
        ).count()
        if total == 0:
            return 0
        aprobados = DocumentosDigitales.objects.filter(
            empleado=self.empleado,
            es_version_actual=True,
            estado_documento='aprobado',
        ).count()
        return round((aprobados / total) * 100)

    @property
    def items_pendientes(self):
        """Retorna lista de items pendientes."""
        pendientes = []
        if not self.datos_personales_completos:
            pendientes.append('Datos personales')
        if not self.datos_laborales_completos:
            pendientes.append('Datos laborales')
        if not self.dni_subido:
            pendientes.append('Copia de DNI')
        if not self.declaraciones_juradas_subidas:
            pendientes.append('Declaraciones juradas')
        if not self.certificados_academicos_subidos:
            pendientes.append('Certificados academicos')
        if not self.certificados_trabajo_subidos:
            pendientes.append('Certificados de trabajo')
        if not self.documentos_familiares_subidos:
            pendientes.append('Documentos familiares')
        return pendientes

    @property
    def esta_completo(self):
        """Verifica si todos los items del checklist estan completos."""
        return all([
            self.datos_personales_completos,
            self.datos_laborales_completos,
            self.dni_subido,
            self.declaraciones_juradas_subidas,
            self.certificados_academicos_subidos,
            self.certificados_trabajo_subidos,
            self.documentos_familiares_subidos,
        ])

    def marcar_completado(self, validado_por):
        """Marca el onboarding como completado."""
        self.estado_onboarding = 'completado'
        self.validado_por = validado_por
        self.fecha_validacion = timezone.now()
        self.fecha_completado = timezone.now()
        self.save()

    def marcar_observado(self, observaciones):
        """Marca el onboarding como observado."""
        self.estado_onboarding = 'observado'
        self.observaciones = observaciones
        self.save()

    def actualizar_estado(self):
        """Recalcula el estado del onboarding segun el checklist."""
        if self.estado_onboarding == 'completado':
            return

        if not self.datos_personales_completos:
            self.estado_onboarding = 'pendiente_datos'
        elif not self.esta_completo:
            self.estado_onboarding = 'pendiente_documentos'
        else:
            self.estado_onboarding = 'pendiente_validacion'
        self.save()
