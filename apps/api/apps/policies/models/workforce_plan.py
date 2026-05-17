"""WorkforcePlan + HeadcountProjection — Module 01 § 3.1 (B.15b).

Plan de dotación: proyección de headcount por área/cargo y trimestre. Cada
proyección compara current vs projected y expone delta_required.

See BACKLOG #130, Module 01 § 3 of docs/modulos/01_planificacion_politicas.md.
"""

import uuid

from django.db import models


class WorkforcePlan(models.Model):
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
        related_name='workforce_plans_owned',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workforce_plan'
        ordering = ['-fiscal_year', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'fiscal_year']),
            models.Index(fields=['tenant', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'fiscal_year', 'name'],
                name='unique_workforce_plan_per_year_name',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.fiscal_year})'


class HeadcountProjection(models.Model):
    QUARTERS = [
        ('Q1', 'Q1'),
        ('Q2', 'Q2'),
        ('Q3', 'Q3'),
        ('Q4', 'Q4'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        'policies.WorkforcePlan',
        on_delete=models.CASCADE,
        related_name='projections',
    )
    area = models.ForeignKey(
        'organization.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Si null, proyección global del plan',
    )
    position = models.ForeignKey(
        'organization.Position',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    current_headcount = models.PositiveIntegerField(default=0)
    projected_headcount = models.PositiveIntegerField(default=0)
    target_quarter = models.CharField(
        max_length=2, choices=QUARTERS, default='Q1',
    )
    justification = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'headcount_projection'
        ordering = ['plan', 'target_quarter', 'area_id', 'position_id']
        indexes = [
            models.Index(fields=['plan', 'target_quarter']),
        ]

    def __str__(self):
        return f'Proyección {self.target_quarter} — área {self.area_id} pos {self.position_id}'

    @property
    def delta_required(self) -> int:
        return self.projected_headcount - self.current_headcount
