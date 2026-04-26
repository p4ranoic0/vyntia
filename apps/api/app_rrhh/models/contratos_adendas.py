# -*- coding: utf-8 -*-
"""
Modelo ContratosAdendas - Sistema unificado de gestión de contratos y adendas

Este modelo maneja tanto contratos iniciales como adendas en una estructura
unificada, facilitando la gestión, reportes y alertas de vencimiento.
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError


class ContratosAdendas(models.Model):
    """
    Modelo unificado para gestión de contratos laborales y adendas.
    
    Permite manejar tanto contratos iniciales como modificaciones (adendas)
    en una sola tabla, facilitando el seguimiento histórico y la gestión
    de documentos contractuales.
    """
    
    # Tipos de documento
    TIPO_DOCUMENTO_CHOICES = [
        # CAS - D.L. 1057
        ('CAS_INDETERMINADO', 'CAS a Plazo Indeterminado'),
        ('CAS_DETERMINADO', 'CAS a Plazo Determinado'),
        ('CAS_SUPLENCIA', 'CAS a Plazo Determinado Suplencia'),
        # D.Leg. 728
        ('LEY_728_FIJO', 'Ley 728 a Plazo Fijo'),
        ('LEY_728_FIJO_SUPLENCIA', 'Ley 728 a Plazo Fijo Suplencia'),
        ('LEY_728_INDETERMINADO', 'Ley 728 a Plazo Indeterminado'),
        # D.Leg. 276
        ('LEY_276_INDETERMINADO', 'Ley 276 a Plazo Indeterminado'),
        # Adendas
        ('ADENDA_SALARIAL', 'Adenda Salarial'),
        ('ADENDA_CARGO', 'Adenda de Cambio de Cargo'),
        ('ADENDA_HORARIO', 'Adenda de Cambio de Horario'),
        ('ADENDA_EXTENSION', 'Adenda de Extension'),
    ]
    
    # Estados del contrato/adenda
    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de Firma'),
        ('ACTIVO', 'Activo'),
        ('VENCIDO', 'Vencido'),
        ('TERMINADO', 'Terminado'),
        ('ANULADO', 'Anulado'),
    ]
    
    # Jornadas laborales
    JORNADA_CHOICES = [
        ('COMPLETA', 'Jornada Completa'),
        ('PARCIAL', 'Jornada Parcial'),
        ('REDUCIDA', 'Jornada Reducida'),
        ('FLEXIBLE', 'Jornada Flexible'),
    ]
    
    # Campos principales
    contrato_id = models.AutoField(primary_key=True)
    
    # Relaciones
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.CASCADE,
        related_name='contratos_adendas',
        help_text='Empleado asociado al contrato/adenda'
    )
    
    area = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='contratos_adendas_area',
        help_text='Área donde se ejecuta el contrato'
    )
    
    # Información del documento
    numero_contrato = models.CharField(
        max_length=50,
        help_text='Número del contrato principal'
    )
    
    numero_adenda = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Número de adenda (NULL si es contrato inicial)'
    )
    
    tipo_documento = models.CharField(
        max_length=25,
        choices=TIPO_DOCUMENTO_CHOICES,
        help_text='Tipo de documento contractual'
    )
    
    # Fechas
    fecha_inicio = models.DateField(
        help_text='Fecha de inicio del contrato/adenda'
    )
    
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de fin del contrato (NULL para indefinidos)'
    )
    
    fecha_firma = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de firma del documento'
    )
    
    # Información salarial
    salario_bruto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Salario bruto mensual'
    )
    
    salario_neto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Salario neto calculado'
    )
    
    # Información laboral
    cargo = models.CharField(
        max_length=100,
        help_text='Cargo o puesto de trabajo'
    )
    
    jornada_laboral = models.CharField(
        max_length=15,
        choices=JORNADA_CHOICES,
        default='COMPLETA',
        help_text='Tipo de jornada laboral'
    )
    
    # Detalles del contrato
    funciones = models.TextField(
        null=True,
        blank=True,
        help_text='Descripción de funciones y responsabilidades'
    )
    
    lugar_trabajo = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Lugar de trabajo'
    )
    
    horario_trabajo = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Horario de trabajo'
    )
    
    # Estado y observaciones
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        help_text='Estado actual del contrato/adenda'
    )
    
    observaciones = models.TextField(
        null=True,
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    # Documento generado
    documento_generado = models.BooleanField(
        default=False,
        help_text='Indica si se ha generado el documento PDF'
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del registro'
    )
    
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        help_text='Fecha de última modificación'
    )
    
    creado_por = models.ForeignKey(
        'identity.Usuario',
        on_delete=models.PROTECT,
        related_name='contratos_creados',
        null=True,
        blank=True,
        help_text='Usuario que creó el registro'
    )

    modificado_por = models.ForeignKey(
        'identity.Usuario',
        on_delete=models.PROTECT,
        related_name='contratos_modificados',
        null=True,
        blank=True,
        help_text='Usuario que modificó el registro'
    )
    
    # Manager personalizado se define al final del archivo
    # objects = ContratosAdendasManager()
    
    class Meta:
        db_table = 'contratos_adendas'
        unique_together = [['numero_contrato', 'numero_adenda']]
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['area']),
            models.Index(fields=['numero_contrato']),
            models.Index(fields=['fecha_fin']),
            models.Index(fields=['estado']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['creado_por']),
        ]
        ordering = ['-fecha_creacion']
        verbose_name = 'Contrato/Adenda'
        verbose_name_plural = 'Contratos/Adendas'
    
    def __str__(self):
        """Representación en string del modelo."""
        if self.numero_adenda:
            return f"{self.numero_contrato}-{self.numero_adenda} - {self.empleado.nombre_completo}"
        return f"{self.numero_contrato} - {self.empleado.nombre_completo}"
    
    def clean(self):
        """Validaciones personalizadas del modelo."""
        super().clean()
        
        # Validar fechas
        if self.fecha_fin and self.fecha_inicio and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
        
        # Validar que contratos indefinidos no tengan fecha de fin
        TIPOS_INDETERMINADO = ('CAS_INDETERMINADO', 'LEY_728_INDETERMINADO', 'LEY_276_INDETERMINADO')
        if self.tipo_documento in TIPOS_INDETERMINADO and self.fecha_fin:
            raise ValidationError({
                'fecha_fin': 'Los contratos a plazo indeterminado no deben tener fecha de fin.'
            })

        # Validar que contratos a plazo fijo/determinado tengan fecha de fin
        TIPOS_DETERMINADO = ('CAS_DETERMINADO', 'CAS_SUPLENCIA', 'LEY_728_FIJO', 'LEY_728_FIJO_SUPLENCIA')
        if self.tipo_documento in TIPOS_DETERMINADO and not self.fecha_fin:
            raise ValidationError({
                'fecha_fin': 'Los contratos a plazo determinado deben tener fecha de fin.'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribe el método save para cálculos automáticos."""
        # Calcular salario neto si no está definido
        if not self.salario_neto and self.salario_bruto:
            # Cálculo básico - se puede mejorar con descuentos reales
            # Redondear a 2 decimales para evitar errores de validación
            self.salario_neto = (self.salario_bruto * Decimal('0.87')).quantize(Decimal('0.01'))
        
        # Validar antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    # Propiedades calculadas
    @property
    def dias_hasta_vencimiento(self):
        """Calcula los días hasta el vencimiento del contrato."""
        if not self.fecha_fin:
            return None
        
        hoy = timezone.now().date()
        if self.fecha_fin > hoy:
            return (self.fecha_fin - hoy).days
        return 0
    
    @property
    def esta_vigente(self):
        """Indica si el contrato está vigente."""
        if self.estado != 'ACTIVO':
            return False
        
        hoy = timezone.now().date()
        if self.fecha_fin:
            return self.fecha_inicio <= hoy <= self.fecha_fin
        return self.fecha_inicio <= hoy
    
    @property
    def esta_vencido(self):
        """Indica si el contrato está vencido."""
        if not self.fecha_fin:
            return False
        
        return timezone.now().date() > self.fecha_fin
    
    def esta_por_vencer(self, dias=30):
        """Indica si el contrato está próximo a vencer."""
        if not self.fecha_fin or self.esta_vencido:
            return False
        
        dias_restantes = self.dias_hasta_vencimiento
        return dias_restantes is not None and 0 < dias_restantes <= dias
    
    @property
    def duracion_dias(self):
        """Calcula la duración del contrato en días."""
        if not self.fecha_fin:
            return None
        
        return (self.fecha_fin - self.fecha_inicio).days
    
    @property
    def duracion_meses(self):
        """Calcula la duración aproximada del contrato en meses."""
        if not self.duracion_dias:
            return None
        
        return round(self.duracion_dias / 30.44, 1)  # Promedio de días por mes
    
    @property
    def es_contrato_inicial(self):
        """Indica si es un contrato inicial (no adenda)."""
        return self.numero_adenda is None or self.numero_adenda == ''
    
    @property
    def es_adenda(self):
        """Indica si es una adenda."""
        return not self.es_contrato_inicial
    
    # Métodos de utilidad
    def generar_numero_contrato(self):
        """Genera un número de contrato único."""
        if not self.numero_contrato:
            año = timezone.now().year
            ultimo_numero = ContratosAdendas.objects.filter(
                numero_contrato__startswith=f'CON-{año}'
            ).count()
            self.numero_contrato = f'CON-{año}-{ultimo_numero + 1:04d}'
    
    def generar_numero_adenda(self):
        """Genera un número de adenda para el contrato."""
        if self.es_contrato_inicial:
            return None
        
        ultima_adenda = ContratosAdendas.objects.filter(
            numero_contrato=self.numero_contrato,
            numero_adenda__isnull=False
        ).count()
        
        return f'AD-{ultima_adenda + 1:03d}'
    
    def puede_generar_adenda(self):
        """Verifica si se puede generar una adenda para este contrato."""
        return (
            self.es_contrato_inicial and
            self.estado in ['ACTIVO', 'PENDIENTE'] and
            not self.esta_vencido
        )
    
    def obtener_adendas(self):
        """Obtiene todas las adendas relacionadas con este contrato."""
        if not self.es_contrato_inicial:
            return ContratosAdendas.objects.none()
        
        return ContratosAdendas.objects.filter(
            numero_contrato=self.numero_contrato,
            numero_adenda__isnull=False
        ).order_by('fecha_creacion')
    
    def obtener_contrato_base(self):
        """Si es una adenda, obtiene el contrato base."""
        if self.es_contrato_inicial:
            return self
        
        try:
            return ContratosAdendas.objects.get(
                numero_contrato=self.numero_contrato,
                numero_adenda__isnull=True
            )
        except ContratosAdendas.DoesNotExist:
            return None


# Importar y asignar el manager después de la definición del modelo
# from ..managers.contratos_manager import ContratosAdendasManager
# ContratosAdendas.add_to_class('objects', ContratosAdendasManager())