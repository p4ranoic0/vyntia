# -*- coding: utf-8 -*-
"""
Modelos de Vacaciones - Gestión completa del sistema de vacaciones

Contiene la definición de todos los modelos relacionados con la gestión
de vacaciones: configuración, períodos, solicitudes, goce e historial.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date, timedelta
from decimal import Decimal
from ..managers import (
    ConfiguracionVacacionesManager,
    PeriodoVacacionalManager,
    SolicitudVacacionesManager,
    GoceVacacionesManager,
    HistorialSolicitudVacacionesManager
)


class VacationConfiguration(models.Model):
    """Modelo para configurar las reglas de vacaciones por área o empleado."""
    
    TIPO_CONFIGURACION_CHOICES = [
        ('general', 'General'),
        ('area', 'Por Área'),
        ('empleado', 'Por Employee'),
        ('cargo', 'Por Cargo'),
    ]
    
    TIPO_CALCULO_CHOICES = [
        ('dias_calendario', 'Días Calendario'),
        ('dias_habiles', 'Días Hábiles'),
        ('proporcional', 'Proporcional'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo_configuracion = models.CharField(max_length=15, choices=TIPO_CONFIGURACION_CHOICES)
    
    # Relaciones opcionales
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    area = models.ForeignKey(
        'organization.Department',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='configuraciones_vacaciones'
    )
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='configuracion_vacaciones'
    )
    
    # Configuración de días
    dias_por_ano = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    dias_adicionales_antiguedad = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(30)]
    )
    anos_para_adicional = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    
    # Configuración de acumulación
    permite_acumulacion = models.BooleanField(default=True)
    max_dias_acumulables = models.IntegerField(
        default=60,
        validators=[MinValueValidator(0), MaxValueValidator(365)]
    )
    
    # Configuración de solicitudes
    dias_minimos_solicitud = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    dias_maximos_solicitud = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(365)]
    )
    dias_anticipacion_minima = models.IntegerField(
        default=15,
        validators=[MinValueValidator(0), MaxValueValidator(365)]
    )
    
    # Configuración de períodos
    tipo_calculo = models.CharField(max_length=20, choices=TIPO_CALCULO_CHOICES, default='dias_calendario')
    incluye_feriados = models.BooleanField(default=True)
    incluye_fines_semana = models.BooleanField(default=True)
    
    # Configuración de aprobación
    requiere_aprobacion_jefe = models.BooleanField(default=True)
    requiere_aprobacion_rrhh = models.BooleanField(default=True)
    niveles_aprobacion = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Configuración de fraccionamiento
    permite_fraccionamiento = models.BooleanField(default=True)
    min_dias_por_fraccion = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    max_fracciones_por_ano = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    
    # Campos de control
    is_active = models.BooleanField(default=True, db_column='activo')
    fecha_inicio_vigencia = models.DateField()
    fecha_fin_vigencia = models.DateField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configuraciones_vacaciones_creadas',
        db_column='creado_por',
    )
    
    # Manager personalizado
    objects = ConfiguracionVacacionesManager()
    
    class Meta:
        db_table = 'configuracion_vacaciones'
        indexes = [
            models.Index(fields=['tipo_configuracion']),
            models.Index(fields=['area']),
            models.Index(fields=['empleado']),
            models.Index(fields=['is_active']),
            models.Index(fields=['fecha_inicio_vigencia']),
            models.Index(fields=['fecha_fin_vigencia']),
        ]
        unique_together = [['tenant', 'tipo_configuracion', 'area', 'empleado', 'fecha_inicio_vigencia']]
    
    def __str__(self):
        if self.tipo_configuracion == 'area' and self.area:
            return f"Configuración {self.area.nombre_area} - {self.dias_por_ano} días"
        elif self.tipo_configuracion == 'empleado' and self.empleado:
            return f"Configuración {self.empleado.nombre_completo} - {self.dias_por_ano} días"
        else:
            return f"Configuración {self.tipo_configuracion} - {self.dias_por_ano} días"


class VacationPeriod(models.Model):
    """Modelo para gestionar los períodos vacacionales de los empleados."""
    
    ESTADO_PERIODO_CHOICES = [
        ('activo', 'Activo'),
        ('cerrado', 'Cerrado'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='periodos_vacacionales'
    )
    contrato = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='periodos_vacacionales',
        null=True,
        blank=True,
    )
    
    # Información del período
    ano_periodo = models.IntegerField()
    fecha_inicio_periodo = models.DateField()
    fecha_fin_periodo = models.DateField()
    fecha_vencimiento = models.DateField()
    
    # Días de vacaciones
    dias_correspondientes = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('365.0'))],
    )
    dias_adicionales = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('30.0'))],
    )
    dias_totales = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('365.0'))],
    )
    
    # Control de uso
    dias_gozados = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
    )
    dias_pendientes = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0'))],
    )
    dias_vencidos = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
    )
    
    # Estado y configuración
    estado_periodo = models.CharField(max_length=15, choices=ESTADO_PERIODO_CHOICES, default='activo')
    configuracion = models.ForeignKey(
        VacationConfiguration,
        on_delete=models.PROTECT,
        related_name='periodos'
    )
    
    # Información adicional
    observaciones = models.TextField(null=True, blank=True)
    motivo_cancelacion = models.TextField(null=True, blank=True)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='periodos_vacacionales_creados',
        db_column='creado_por',
    )
    
    # Manager personalizado
    objects = PeriodoVacacionalManager()
    
    class Meta:
        db_table = 'periodos_vacacionales'
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['contrato']),
            models.Index(fields=['ano_periodo']),
            models.Index(fields=['estado_periodo']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['fecha_inicio_periodo']),
            models.Index(fields=['fecha_fin_periodo']),
        ]
        unique_together = [['tenant', 'empleado', 'ano_periodo', 'contrato']]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - Período {self.ano_periodo}"
    
    @property
    def porcentaje_uso(self):
        """Calcula el porcentaje de uso de vacaciones."""
        if self.dias_totales > 0:
            return round((self.dias_gozados / self.dias_totales) * 100, 2)
        return 0
    
    @property
    def esta_vencido(self):
        """Verifica si el período está vencido."""
        return date.today() > self.fecha_vencimiento
    
    @property
    def dias_para_vencimiento(self):
        """Calcula los días restantes para el vencimiento."""
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - date.today()
            return delta.days
        return None


class VacationRequest(models.Model):
    """Modelo para gestionar las solicitudes de vacaciones."""
    
    ESTADO_SOLICITUD_CHOICES = [
        ('borrador', 'Borrador'),
        ('enviada', 'Enviada'),
        ('en_revision', 'En Revisión'),
        ('aprobada_jefe', 'Aprobada por Jefe'),
        ('aprobada_rrhh', 'Aprobada por RRHH'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
        ('en_goce', 'En Goce'),
        ('finalizada', 'Finalizada'),
    ]
    
    TIPO_SOLICITUD_CHOICES = [
        ('vacaciones', 'Vacaciones'),
        ('adelanto_vacaciones', 'Adelanto de Vacaciones'),
        ('fraccionamiento', 'Fraccionamiento'),
        ('postergacion', 'Postergación'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='solicitudes_vacaciones'
    )
    periodo_vacacional = models.ForeignKey(
        VacationPeriod,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )
    
    # Información de la solicitud
    tipo_solicitud = models.CharField(max_length=25, choices=TIPO_SOLICITUD_CHOICES, default='vacaciones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('365.0'))],
    )
    medio_dia = models.BooleanField(default=False)
    
    # Motivo y justificación
    motivo_solicitud = models.TextField()
    observaciones_empleado = models.TextField(null=True, blank=True)
    
    # Estado y aprobaciones
    estado_solicitud = models.CharField(max_length=20, choices=ESTADO_SOLICITUD_CHOICES, default='borrador')
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    # Aprobación del jefe
    aprobado_por_jefe = models.BooleanField(default=False)
    jefe_aprobador = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas_como_jefe'
    )
    fecha_aprobacion_jefe = models.DateTimeField(null=True, blank=True)
    observaciones_jefe = models.TextField(null=True, blank=True)
    
    # Aprobación de RRHH
    aprobado_por_rrhh = models.BooleanField(default=False)
    rrhh_aprobador = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas_rrhh'
    )
    fecha_aprobacion_rrhh = models.DateTimeField(null=True, blank=True)
    observaciones_rrhh = models.TextField(null=True, blank=True)
    
    # Información de rechazo
    motivo_rechazo = models.TextField(null=True, blank=True)
    rechazado_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_rechazadas'
    )
    fecha_rechazo = models.DateTimeField(null=True, blank=True)
    
    # Información de cancelación
    motivo_cancelacion = models.TextField(null=True, blank=True)
    cancelado_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_canceladas'
    )
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')

    # Manager personalizado
    objects = SolicitudVacacionesManager()
    
    class Meta:
        db_table = 'solicitudes_vacaciones'
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['periodo_vacacional']),
            models.Index(fields=['estado_solicitud']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['fecha_fin']),
            models.Index(fields=['fecha_envio']),
            models.Index(fields=['tipo_solicitud']),
            models.Index(fields=['aprobado_por_jefe']),
            models.Index(fields=['aprobado_por_rrhh']),
        ]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin}"
    
    @property
    def estado_texto(self):
        """Retorna el estado en formato texto."""
        return dict(self.ESTADO_SOLICITUD_CHOICES).get(self.estado_solicitud, self.estado_solicitud)
    
    @property
    def puede_ser_aprobada(self):
        """Verifica si puede ser aprobada."""
        return self.estado_solicitud in ['enviada', 'en_revision']
    
    @property
    def puede_ser_cancelada(self):
        """Verifica si puede ser cancelada."""
        return self.estado_solicitud not in ['finalizada', 'cancelada', 'rechazada']


class VacationGrant(models.Model):
    """Modelo para registrar el goce efectivo de vacaciones."""
    
    ESTADO_GOCE_CHOICES = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('finalizado', 'Finalizado'),
        ('interrumpido', 'Interrumpido'),
        ('cancelado', 'Cancelado'),
    ]
    
    MOTIVO_INTERRUPCION_CHOICES = [
        ('emergencia_laboral', 'Emergencia Laboral'),
        ('emergencia_familiar', 'Emergencia Familiar'),
        ('enfermedad', 'Enfermedad'),
        ('accidente', 'Accidente'),
        ('otros', 'Otros'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    solicitud_vacaciones = models.OneToOneField(
        VacationRequest,
        on_delete=models.CASCADE,
        related_name='goce'
    )
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='goces_vacaciones'
    )
    periodo_vacacional = models.ForeignKey(
        VacationPeriod,
        on_delete=models.CASCADE,
        related_name='goces'
    )
    
    # Fechas del goce
    fecha_inicio_real = models.DateField()
    fecha_fin_real = models.DateField()
    fecha_reincorporacion = models.DateField(null=True, blank=True)
    
    # Información del goce
    dias_gozados = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('365.0'))],
    )
    estado_goce = models.CharField(max_length=15, choices=ESTADO_GOCE_CHOICES, default='programado')
    
    # Información de interrupción
    fecha_interrupcion = models.DateField(null=True, blank=True)
    motivo_interrupcion = models.CharField(
        max_length=25,
        choices=MOTIVO_INTERRUPCION_CHOICES,
        null=True,
        blank=True
    )
    descripcion_interrupcion = models.TextField(null=True, blank=True)
    dias_no_gozados = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        validators=[MinValueValidator(Decimal('0.0'))],
    )
    
    # Información de reincorporación
    reincorporado = models.BooleanField(default=False)
    fecha_reincorporacion_real = models.DateField(null=True, blank=True)
    observaciones_reincorporacion = models.TextField(null=True, blank=True)
    
    # Campos de control
    observaciones = models.TextField(null=True, blank=True)
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    registrado_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='goces_registrados'
    )
    
    # Manager personalizado
    objects = GoceVacacionesManager()
    
    class Meta:
        db_table = 'goces_vacaciones'
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['periodo_vacacional']),
            models.Index(fields=['estado_goce']),
            models.Index(fields=['fecha_inicio_real']),
            models.Index(fields=['fecha_fin_real']),
            models.Index(fields=['fecha_reincorporacion']),
            models.Index(fields=['reincorporado']),
        ]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - Goce {self.fecha_inicio_real} a {self.fecha_fin_real}"
    
    @property
    def esta_en_curso(self):
        """Verifica si está en curso."""
        hoy = date.today()
        return (
            self.estado_goce == 'en_curso' and
            self.fecha_inicio_real <= hoy <= self.fecha_fin_real
        )
    
    @property
    def dias_transcurridos(self):
        """Calcula los días transcurridos del goce."""
        if self.estado_goce == 'en_curso':
            hoy = date.today()
            if hoy >= self.fecha_inicio_real:
                dias = (min(hoy, self.fecha_fin_real) - self.fecha_inicio_real).days + 1
                return max(0, dias)
        elif self.estado_goce == 'finalizado':
            return self.dias_gozados
        return 0


class VacationRequestHistory(models.Model):
    """Modelo para registrar el historial de cambios en las solicitudes."""
    
    TIPO_ACCION_CHOICES = [
        ('creacion', 'Creación'),
        ('envio', 'Envío'),
        ('aprobacion_jefe', 'Aprobación Jefe'),
        ('aprobacion_rrhh', 'Aprobación RRHH'),
        ('rechazo', 'Rechazo'),
        ('cancelacion', 'Cancelación'),
        ('modificacion', 'Modificación'),
        ('inicio_goce', 'Inicio de Goce'),
        ('fin_goce', 'Fin de Goce'),
        ('interrupcion', 'Interrupción'),
        ('reincorporacion', 'Reincorporación'),
    ]
    
    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )
    solicitud_vacaciones = models.ForeignKey(
        VacationRequest,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    
    # Información de la acción
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCION_CHOICES)
    descripcion_accion = models.TextField()
    estado_anterior = models.CharField(max_length=20, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=20, null=True, blank=True)
    
    # User que realizó la acción
    usuario_accion = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_vacaciones'
    )
    
    # Información adicional
    observaciones = models.TextField(null=True, blank=True)
    datos_adicionales = models.JSONField(null=True, blank=True)
    
    # Campos de auditoría
    fecha_accion = models.DateTimeField(auto_now_add=True)
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)
    
    # Manager personalizado
    objects = HistorialSolicitudVacacionesManager()
    
    class Meta:
        db_table = 'historial_solicitudes_vacaciones'
        indexes = [
            models.Index(fields=['solicitud_vacaciones']),
            models.Index(fields=['tipo_accion']),
            models.Index(fields=['usuario_accion']),
            models.Index(fields=['fecha_accion']),
        ]
    
    def __str__(self):
        return f"Solicitud {self.solicitud_vacaciones.id} - {self.tipo_accion}"
    
    @property
    def tipo_accion_texto(self):
        """Retorna el tipo de acción en formato texto."""
        return dict(self.TIPO_ACCION_CHOICES).get(self.tipo_accion, self.tipo_accion)
    
    @classmethod
    def registrar_accion(cls, solicitud, tipo_accion, usuario, descripcion, observaciones=None, datos_adicionales=None):
        """Registra una nueva acción en el historial."""
        return cls.objects.create(
            solicitud_vacaciones=solicitud,
            tipo_accion=tipo_accion,
            descripcion_accion=descripcion,
            estado_anterior=solicitud.estado_solicitud,
            usuario_accion=usuario,
            observaciones=observaciones,
            datos_adicionales=datos_adicionales
        )
