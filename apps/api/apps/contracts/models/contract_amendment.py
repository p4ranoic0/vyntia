# -*- coding: utf-8 -*-
"""
Modelo ContractAmendment — Adendas a contratos laborales

Representa modificaciones a un Contract existente. Cada amendment se asocia
a un parent_contract via FK y captura solo los fields que cambian (salario,
cargo, horario, fecha de fin, etc.) — no duplica todos los campos del contrato.
"""

import uuid

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ContractAmendment(models.Model):
    """
    Adenda a un contrato laboral.

    Una adenda modifica uno o más aspectos de un Contract activo:
    salario, cargo, horario, jornada o fecha de fin. Mantiene FK al
    contrato padre y guarda solo los nuevos valores que cambian.
    """

    TIPO_DOCUMENTO_CHOICES = [
        ('ADENDA_SALARIAL', 'Adenda Salarial'),
        ('ADENDA_CARGO', 'Adenda de Cambio de Cargo'),
        ('ADENDA_HORARIO', 'Adenda de Cambio de Horario'),
        ('ADENDA_EXTENSION', 'Adenda de Extension'),
    ]

    ESTADO_CHOICES = [
        ('BORRADOR', 'Borrador'),
        ('PENDIENTE', 'Pendiente de Firma'),
        ('ACTIVO', 'Activo'),
        ('VENCIDO', 'Vencido'),
        ('TERMINADO', 'Terminado'),
        ('ANULADO', 'Anulado'),
    ]

    JORNADA_CHOICES = [
        ('COMPLETA', 'Jornada Completa'),
        ('PARCIAL', 'Jornada Parcial'),
        ('REDUCIDA', 'Jornada Reducida'),
        ('FLEXIBLE', 'Jornada Flexible'),
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

    parent_contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='amendments',
        help_text='Contrato padre al que esta adenda modifica',
    )

    numero_adenda = models.CharField(
        max_length=20,
        help_text='Numero secuencial de la adenda dentro del parent_contract',
    )

    tipo_documento = models.CharField(
        max_length=25,
        choices=TIPO_DOCUMENTO_CHOICES,
        help_text='Tipo de adenda',
    )

    fecha_inicio = models.DateField(
        help_text='Fecha de inicio de vigencia de la modificacion',
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de fin de vigencia de la modificacion',
    )

    fecha_firma = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de firma de la adenda',
    )

    # Nuevos valores (solo el que aplica al tipo de adenda)
    nuevo_salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Nuevo salario bruto (para ADENDA_SALARIAL)',
    )

    nuevo_cargo = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text='Nuevo cargo (para ADENDA_CARGO)',
    )

    nuevo_horario = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Nuevo horario (para ADENDA_HORARIO)',
    )

    nueva_jornada_laboral = models.CharField(
        max_length=15,
        choices=JORNADA_CHOICES,
        null=True,
        blank=True,
        help_text='Nueva jornada (para ADENDA_HORARIO)',
    )

    nueva_fecha_fin_contrato = models.DateField(
        null=True,
        blank=True,
        help_text='Nueva fecha de fin del contrato padre (para ADENDA_EXTENSION)',
    )

    motivo = models.TextField(
        null=True,
        blank=True,
        help_text='Motivo de la adenda',
    )

    observaciones = models.TextField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='BORRADOR',
        db_column='estado',
        help_text='Estado actual de la adenda',
    )

    documento_generado = models.FileField(
        upload_to='adendas/%Y/',
        null=True,
        blank=True,
        help_text='PDF de la adenda firmada',
    )

    # Auditoria
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='adendas_creadas',
        null=True,
        blank=True,
        db_column='creado_por_id',
    )
    updated_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='adendas_modificadas',
        null=True,
        blank=True,
        db_column='modificado_por_id',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_creacion',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='fecha_modificacion',
    )

    class Meta:
        db_table = 'contract_amendments'
        unique_together = [['parent_contract', 'numero_adenda']]
        indexes = [
            models.Index(fields=['parent_contract']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['status']),
            models.Index(fields=['fecha_inicio']),
        ]
        ordering = ['parent_contract', 'numero_adenda']

    def __str__(self):
        return f"{self.parent_contract.numero_contrato}-{self.numero_adenda} ({self.get_tipo_documento_display()})"
