"""SuccessionPlan + KeyPosition + SuccessorCandidate — Module 01 § 3.2 (B.15b).

Plan de sucesión: cargos clave + candidatos a sucesores con readiness level.

See BACKLOG #130, Module 01 § 3 of docs/modulos/01_planificacion_politicas.md.
"""

import uuid

from django.db import models


class SuccessionPlan(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('active', 'Activo'),
        ('archived', 'Archivado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    name = models.CharField(max_length=200)
    fiscal_year = models.PositiveIntegerField(db_index=True)
    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=15, choices=STATUSES, default='draft', db_index=True,
    )

    owner_user = models.ForeignKey(
        'identity.User', on_delete=models.PROTECT,
        related_name='succession_plans_owned',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'succession_plan'
        ordering = ['-fiscal_year', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'fiscal_year']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'fiscal_year', 'name'],
                name='unique_succession_plan_per_year_name',
            ),
        ]

    def __str__(self):
        return f'Sucesión {self.name} ({self.fiscal_year})'


class KeyPosition(models.Model):
    CRITICALITY = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        'policies.SuccessionPlan',
        on_delete=models.CASCADE,
        related_name='key_positions',
    )
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='+',
    )
    criticality = models.CharField(
        max_length=10, choices=CRITICALITY, default='media',
    )
    risk_notes = models.TextField(blank=True)
    current_holder = models.ForeignKey(
        'employees.Employee',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'key_position'
        ordering = ['plan', 'criticality', 'position_id']
        constraints = [
            models.UniqueConstraint(
                fields=['plan', 'position'],
                name='unique_key_position_per_plan',
            ),
        ]

    def __str__(self):
        return f'Cargo clave pos={self.position_id} ({self.criticality})'


class SuccessorCandidate(models.Model):
    READINESS = [
        (1, 'Ready now'),
        (2, 'Ready in 1 year'),
        (3, 'Ready in 2 years'),
        (4, 'Development needed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key_position = models.ForeignKey(
        'policies.KeyPosition',
        on_delete=models.CASCADE,
        related_name='candidates',
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='+',
    )
    readiness_level = models.PositiveSmallIntegerField(choices=READINESS, default=4)
    order = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'successor_candidate'
        ordering = ['key_position', 'order', 'readiness_level']
        constraints = [
            models.UniqueConstraint(
                fields=['key_position', 'employee'],
                name='unique_candidate_per_key_position',
            ),
        ]

    def __str__(self):
        return f'Candidato emp={self.employee_id} readiness={self.readiness_level}'
