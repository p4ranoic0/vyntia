"""Termination — Module 03.7 desvinculación per régimen (B.14).

Captures the cese event for a Contract: causal per régimen, fechas, anexos
documentales y workflow draft → in_progress → completed → liquidated →
baja_t_registro_done | cancelled. The settlement (SeveranceSettlement) y la
baja T-Registro (TRegistroDeclaration de B.10 con declaration_type='baja')
son entidades hermanas — Termination es el header que las une.

Causales soportados (régimen-aware):
- 728 LPCL: renuncia, despido_justificado, despido_arbitrario, despido_indirecto,
  mutuo_acuerdo, vencimiento_plazo, jubilacion, fallecimiento.
- 276 carrera: renuncia, destitucion, cese_definitivo, jubilacion, fallecimiento.
- CAS DL 1057: vencimiento_plazo, renuncia, resolucion_anticipada, mutuo_acuerdo,
  fallecimiento.

Out of scope per ADR-B.9: AFP/ONP detractions, retención de Renta 5ta,
multi-régimen severance variants.

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #123.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Termination(models.Model):
    REGIMENES = [
        ('728', 'D.Leg. 728 LPCL'),
        ('276', 'D.Leg. 276 carrera administrativa'),
        ('cas', 'D.L. 1057 CAS'),
        ('mype', 'MYPE'),
        ('otros', 'Otros'),
    ]
    CAUSALES = [
        # Comunes
        ('renuncia', 'Renuncia voluntaria'),
        ('mutuo_acuerdo', 'Mutuo acuerdo'),
        ('jubilacion', 'Jubilación'),
        ('fallecimiento', 'Fallecimiento'),
        # 728
        ('despido_justificado', 'Despido justificado (falta grave)'),
        ('despido_arbitrario', 'Despido arbitrario'),
        ('despido_indirecto', 'Hostilidad / despido indirecto'),
        ('vencimiento_plazo', 'Vencimiento del plazo (contrato fijo / CAS)'),
        # 276
        ('destitucion', 'Destitución (PAD)'),
        ('cese_definitivo', 'Cese definitivo'),
        # CAS
        ('resolucion_anticipada', 'Resolución anticipada CAS'),
        # Catch-all
        ('otros', 'Otros'),
    ]
    STATUSES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En trámite'),
        ('completed', 'Cese completado'),
        ('liquidated', 'Liquidación pagada'),
        ('baja_t_registro_done', 'Baja T-Registro realizada'),
        ('cancelled', 'Cancelado'),
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

    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='termination',
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='terminations',
    )

    regimen = models.CharField(max_length=10, choices=REGIMENES, default='728')
    causal = models.CharField(max_length=30, choices=CAUSALES, db_index=True)
    status = models.CharField(
        max_length=30, choices=STATUSES, default='draft', db_index=True,
    )

    fecha_cese = models.DateField(help_text='Último día con vínculo formal')
    last_day_worked = models.DateField(
        null=True, blank=True,
        help_text='Último día efectivo trabajado (puede preceder fecha_cese si hubo vacaciones)',
    )
    motivo = models.TextField(
        blank=True,
        help_text='Justificación textual del cese (citar artículo si aplica)',
    )

    # Anexos documentales
    carta_renuncia_file = models.FileField(
        upload_to='cese/cartas_renuncia/%Y/%m/',
        null=True, blank=True,
    )
    acta_cese_file = models.FileField(
        upload_to='cese/actas_cese/%Y/%m/',
        null=True, blank=True,
    )

    # Vínculo con la baja T-Registro (B.10)
    baja_t_registro = models.OneToOneField(
        'contracts.TRegistroDeclaration',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='termination_baja',
    )

    # Audit trail
    initiated_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    initiated_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    liquidated_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    liquidated_at = models.DateTimeField(null=True, blank=True)
    cancelled_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'termination'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'causal']),
            models.Index(fields=['employee']),
            models.Index(fields=['fecha_cese']),
        ]

    def __str__(self):
        return (
            f'Cese {self.get_causal_display()} — emp={self.employee_id} '
            f'({self.get_status_display()})'
        )

    # ----------------------- Lifecycle -----------------------

    def mark_in_progress(self, *, user=None):
        if self.status != 'draft':
            raise ValidationError(
                f'Cannot start termination from status={self.status}'
            )
        self.status = 'in_progress'
        self.initiated_by = user
        self.initiated_at = timezone.now()
        self.save(update_fields=[
            'status', 'initiated_by', 'initiated_at', 'updated_at',
        ])

    def mark_completed(self, *, user):
        if self.status not in ('draft', 'in_progress'):
            raise ValidationError(
                f'Cannot complete termination from status={self.status}'
            )
        self.status = 'completed'
        self.completed_by = user
        self.completed_at = timezone.now()
        self.save(update_fields=[
            'status', 'completed_by', 'completed_at', 'updated_at',
        ])

    def mark_liquidated(self, *, user):
        if self.status != 'completed':
            raise ValidationError(
                f'Cannot liquidate termination from status={self.status}'
            )
        self.status = 'liquidated'
        self.liquidated_by = user
        self.liquidated_at = timezone.now()
        self.save(update_fields=[
            'status', 'liquidated_by', 'liquidated_at', 'updated_at',
        ])

    def mark_baja_tregistro_done(self, *, declaration):
        if self.status not in ('liquidated', 'completed'):
            raise ValidationError(
                f'Cannot mark baja T-Registro from status={self.status}'
            )
        self.baja_t_registro = declaration
        self.status = 'baja_t_registro_done'
        self.save(update_fields=[
            'baja_t_registro', 'status', 'updated_at',
        ])

    def cancel(self, *, reason, user):
        if self.status in ('baja_t_registro_done', 'cancelled'):
            raise ValidationError(
                f'Cannot cancel termination from status={self.status}'
            )
        if not reason:
            raise ValidationError('reason is required to cancel a termination')
        self.status = 'cancelled'
        self.cancelled_reason = reason
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.save(update_fields=[
            'status', 'cancelled_reason', 'cancelled_at',
            'cancelled_by', 'updated_at',
        ])

    # ----------------------- Helpers -----------------------

    @property
    def hours_since_completion(self) -> float | None:
        if not self.completed_at:
            return None
        delta = timezone.now() - self.completed_at
        return delta.total_seconds() / 3600.0

    @property
    def baja_tregistro_overdue_48h(self) -> bool:
        """Termination completada hace más de 48h sin baja T-Registro enviada."""
        hours = self.hours_since_completion
        if hours is None or hours <= 48:
            return False
        return self.status in ('completed', 'liquidated')
