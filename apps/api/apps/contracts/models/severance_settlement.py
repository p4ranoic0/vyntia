"""SeveranceSettlement + SeveranceLine — minimum legal severance (B.14, ADR-B.9).

Cubre 4 componentes obligatorios al cese (D.S. 003-97-TR; D.S. 001-97-TR;
Ley 27735):
- cts: CTS proporcional del semestre en curso (no incluye saldos históricos
  depositados — eso lo cubre Vyntia Pay D).
- vac_truncas: Vacaciones truncas por días no gozados del último año.
- grat_trunca: Gratificación trunca proporcional al semestre en curso.
- indemnizacion: Indemnización por despido arbitrario / indirecto (1.5 sueldos
  por año, capped 12 sueldos) cuando la causal lo amerite.
- otros: línea genérica para ajustes manuales (vales / bonos / saldos).

Calculations live in severance_service.compute_settlement. Aquí el modelo solo
persiste y permite overrides manuales (no payroll engine).
"""

import uuid
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class SeveranceSettlement(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('computed', 'Calculada'),
        ('paid', 'Pagada'),
        ('void', 'Anulada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    termination = models.OneToOneField(
        'contracts.Termination',
        on_delete=models.CASCADE,
        related_name='settlement',
    )

    status = models.CharField(
        max_length=10, choices=STATUSES, default='draft', db_index=True,
    )

    sueldo_base = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0'),
        help_text='Sueldo bruto mensual de referencia (snapshot al cese)',
    )
    fecha_inicio_contrato = models.DateField(null=True, blank=True)
    fecha_cese = models.DateField(null=True, blank=True)

    total_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0'),
    )
    paid_amount = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0'),
    )

    computed_at = models.DateTimeField(null=True, blank=True)
    computed_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    paid_at = models.DateTimeField(null=True, blank=True)
    paid_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    manual_override = models.JSONField(
        default=dict, blank=True,
        help_text='Overrides manuales por componente (component_code: amount)',
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'severance_settlement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['paid_at']),
        ]

    def __str__(self):
        return f'Liquidación {self.termination_id} — {self.total_amount}'

    def recompute_total(self):
        agg = self.lines.aggregate(t=models.Sum('amount'))
        self.total_amount = agg.get('t') or Decimal('0')
        self.save(update_fields=['total_amount', 'updated_at'])

    def mark_computed(self, *, user=None):
        if self.status not in ('draft', 'computed'):
            raise ValidationError(
                f'Cannot mark computed from status={self.status}'
            )
        self.status = 'computed'
        self.computed_at = timezone.now()
        if user is not None:
            self.computed_by = user
        self.save(update_fields=[
            'status', 'computed_at', 'computed_by', 'updated_at',
        ])

    def mark_paid(self, *, paid_total: Decimal, user=None, paid_at=None):
        if self.status != 'computed':
            raise ValidationError(
                f'Cannot mark paid from status={self.status}'
            )
        # Sanity: paid_total dentro del 5% del total computado.
        if self.total_amount and self.total_amount > 0:
            diff = abs(Decimal(paid_total) - self.total_amount)
            if diff / self.total_amount > Decimal('0.05'):
                raise ValidationError(
                    'paid_total differs more than 5% from computed total; '
                    'use override line or recompute first'
                )
        self.paid_amount = Decimal(paid_total)
        self.paid_at = paid_at or timezone.now()
        if user is not None:
            self.paid_by = user
        self.status = 'paid'
        self.save(update_fields=[
            'paid_amount', 'paid_at', 'paid_by', 'status', 'updated_at',
        ])


class SeveranceLine(models.Model):
    COMPONENTS = [
        ('cts', 'CTS proporcional'),
        ('vac_truncas', 'Vacaciones truncas'),
        ('grat_trunca', 'Gratificación trunca'),
        ('indemnizacion', 'Indemnización despido arbitrario'),
        ('otros', 'Otros / Ajustes manuales'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    settlement = models.ForeignKey(
        'contracts.SeveranceSettlement',
        on_delete=models.CASCADE,
        related_name='lines',
    )

    component = models.CharField(max_length=20, choices=COMPONENTS)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    base_calculation = models.JSONField(
        default=dict, blank=True,
        help_text='Inputs usados para el cómputo (sueldo, días, meses, etc.)',
    )
    formula_note = models.CharField(
        max_length=200, blank=True,
        help_text='Descripción textual de la fórmula aplicada',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'severance_line'
        ordering = ['component']
        constraints = [
            models.UniqueConstraint(
                fields=['settlement', 'component'],
                name='unique_severance_line_component',
            ),
        ]

    def __str__(self):
        return f'{self.get_component_display()}: {self.amount}'

    def clean(self):
        if self.amount is None:
            raise ValidationError('amount is required')
        if self.amount < Decimal('0'):
            raise ValidationError('amount cannot be negative')
