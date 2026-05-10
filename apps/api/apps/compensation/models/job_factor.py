"""JobFactor + JobSubfactor reference data per R.M. 243-2018-TR (Ley 30709).

The 4 factors are mandated by the guía metodológica for objective category
valorization. Subfactors are seeded with the canonical list; tenants can
extend with their own subfactors in B.7.1 if needed.

System-wide (no tenant FK) — same as SUNAT tables in B.6.
"""
import uuid
from decimal import Decimal

from django.db import models


class JobFactor(models.Model):
    """One of the 4 master factors per R.M. 243-2018-TR.

    The 4 mandatory factors are:
    - COMPETENCIAS — conocimientos, habilidades, experiencia
    - RESPONSABILIDAD — por personas, bienes, decisiones, resultados
    - ESFUERZO — físico, mental, visual, emocional
    - CONDICIONES — ambiente, riesgo, disponibilidad

    Weight is the % of total score this factor contributes (sums to 100 across
    all 4). Default 25% each; tenants can adjust per their own methodology.
    """

    KIND_CHOICES = [
        ('competencias', 'Competencias'),
        ('responsabilidad', 'Responsabilidad'),
        ('esfuerzo', 'Esfuerzo'),
        ('condiciones', 'Condiciones de Trabajo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('25.00'),
        help_text='% weight of this factor (sums to 100 across all 4).',
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_factor'
        ordering = ['kind']

    def __str__(self):
        return f"{self.kind.upper()} - {self.name}"


class JobSubfactor(models.Model):
    """A subfactor under one of the 4 JobFactors per R.M. 243-2018-TR.

    Seeded with the canonical list from the guía metodológica. Each
    Category × Subfactor combination receives a score (0..max_score) in
    CategoryFactorScore, and the weighted sum produces Category.total_score.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    factor = models.ForeignKey(
        'compensation.JobFactor',
        on_delete=models.CASCADE,
        related_name='subfactors',
    )
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(
        default=100,
        help_text='Maximum allowed score for this subfactor on any Category.',
    )
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_subfactor'
        ordering = ['factor', 'code']
        indexes = [models.Index(fields=['factor', 'is_active'])]

    def __str__(self):
        return f"{self.code} - {self.name}"
