# -*- coding: utf-8 -*-
"""
Modelo Contract - Sistema unificado de gestión de contratos y adendas

Este modelo maneja tanto contratos iniciales como adendas en una estructura
unificada, facilitando la gestión, reportes y alertas de vencimiento.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError


class Contract(models.Model):
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='contratos_adendas',
        help_text='Employee asociado al contrato/adenda'
    )
    
    area = models.ForeignKey(
        'organization.Department',
        on_delete=models.PROTECT,
        related_name='contratos_adendas_area',
        help_text='Área donde se ejecuta el contrato'
    )

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )

    # Información del documento
    numero_contrato = models.CharField(
        max_length=50,
        help_text='Número del contrato principal'
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
    status = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        db_column='estado',
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
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_creacion',
        help_text='Fecha de creación del registro'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='fecha_modificacion',
        help_text='Fecha de última modificación'
    )

    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='contratos_creados',
        null=True,
        blank=True,
        db_column='creado_por_id',
        help_text='User que creó el registro'
    )

    updated_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='contratos_modificados',
        null=True,
        blank=True,
        db_column='modificado_por_id',
        help_text='User que modificó el registro'
    )
    
    # Manager personalizado se define al final del archivo
    # objects = ContratosAdendasManager()
    
    class Meta:
        db_table = 'contratos_adendas'
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['area']),
            models.Index(fields=['numero_contrato']),
            models.Index(fields=['fecha_fin']),
            models.Index(fields=['status']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['fecha_inicio']),
            models.Index(fields=['created_by']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "numero_contrato"],
                name="unique_contract_number_per_tenant",
            ),
        ]
        ordering = ['-created_at']
        verbose_name = 'Contrato/Adenda'
        verbose_name_plural = 'Contratos/Adendas'
    
    def __str__(self):
        """Representación en string del modelo."""
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
        if self.status != 'ACTIVO':
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
    
    # Métodos de utilidad
    def generar_numero_contrato(self):
        """Genera un número de contrato único."""
        if not self.numero_contrato:
            año = timezone.now().year
            ultimo_numero = Contract.objects.filter(
                numero_contrato__startswith=f'CON-{año}'
            ).count()
            self.numero_contrato = f'CON-{año}-{ultimo_numero + 1:04d}'
    
    def generar_numero_adenda(self):
        """Genera el siguiente numero secuencial de adenda para este contrato."""
        ultima_adenda = self.amendments.count()
        return f'AD-{ultima_adenda + 1:03d}'

    def puede_generar_adenda(self):
        """Verifica si se puede generar una adenda para este contrato."""
        return (
            self.status in ['ACTIVO', 'PENDIENTE'] and
            not self.esta_vencido
        )

    def obtener_adendas(self):
        """Obtiene todas las adendas relacionadas con este contrato."""
        return self.amendments.order_by('created_at')


# Importar y asignar el manager después de la definición del modelo
# from ..managers.contratos_manager import ContratosAdendasManager
# Contract.add_to_class('objects', ContratosAdendasManager())