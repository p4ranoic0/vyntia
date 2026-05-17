"""HR Strategic Plan + StrategicObjective + KPI — Module 01 (B.15b).

Plan estratégico anual (o multianual) del área de RRHH. Cada plan tiene N
objetivos (con peso porcentual que normalmente suma 100), y cada objetivo
tiene N KPIs medibles (target + actual + unit). El servicio compute_progress
agrega progreso ponderado.

See BACKLOG #129, Module 01 § 2 of docs/modulos/01_planificacion_politicas.md.
"""

import uuid
from decimal import Decimal

from django.db import models


class HRStrategicPlan(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('archived', 'Archivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    name = models.CharField(max_length=200)
    fiscal_year = models.PositiveIntegerField(db_index=True)
    period_start = models.DateField()
    period_end = models.DateField()
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=15, choices=STATUSES, default='draft', db_index=True,
    )

    owner_user = models.ForeignKey(
        'identity.User', on_delete=models.PROTECT,
        related_name='strategic_plans_owned',
    )
    approved_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_strategic_plan'
        ordering = ['-fiscal_year', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'fiscal_year']),
            models.Index(fields=['tenant', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'fiscal_year', 'name'],
                name='unique_strategic_plan_per_year_name',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.fiscal_year})'


class StrategicObjective(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        'policies.HRStrategicPlan',
        on_delete=models.CASCADE,
        related_name='objectives',
    )
    code = models.CharField(max_length=32)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0'),
        help_text='Peso porcentual del objetivo (0-100)',
    )
    order = models.PositiveIntegerField(default=0)
    owner_user = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'strategic_objective'
        ordering = ['plan', 'order', 'code']
        constraints = [
            models.UniqueConstraint(
                fields=['plan', 'code'],
                name='unique_objective_code_per_plan',
            ),
        ]

    def __str__(self):
        return f'{self.code} — {self.title}'


class KPI(models.Model):
    STATUSES = [
        ('on_track', 'On track'),
        ('at_risk', 'En riesgo'),
        ('off_track', 'Fuera de meta'),
        ('done', 'Cumplido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.ForeignKey(
        'policies.StrategicObjective',
        on_delete=models.CASCADE,
        related_name='kpis',
    )
    name = models.CharField(max_length=255)
    formula_note = models.TextField(
        blank=True,
        help_text='Cómo se calcula el KPI (ej: "rotación = bajas/headcount promedio")',
    )
    unit = models.CharField(
        max_length=15, blank=True,
        help_text='%, N, S/., días, etc.',
    )
    target = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0'))
    actual = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal('0'))
    target_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=15, choices=STATUSES, default='on_track', db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'kpi'
        ordering = ['objective', 'name']

    def __str__(self):
        return f'KPI {self.name} ({self.status})'

    def progress_pct(self) -> Decimal:
        """Progreso 0..100 (cap a 100 si actual > target)."""
        if self.target == 0:
            return Decimal('0')
        pct = (self.actual / self.target) * Decimal('100')
        if pct < 0:
            return Decimal('0')
        if pct > Decimal('100'):
            return Decimal('100')
        return pct.quantize(Decimal('0.01'))
