"""Category — a row inside a CCF (Ley 30709 § 4.1)."""
import uuid
from decimal import Decimal

from django.db import models


class Category(models.Model):
    """A categoría inside a CCF.

    Holds denomination (code + name), description of functions, objective
    minimum requirements (Ley 30709 § 4.1), and computed total_score
    aggregated from CategoryFactorScore rows. Each Category has a 1-to-1
    SalaryBand. Position.category points back here (set in B.7 Task 5).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )
    ccf = models.ForeignKey(
        'compensation.CategoryFunctionTable',
        on_delete=models.CASCADE,
        related_name='categories',
    )

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    functions_summary = models.TextField(
        blank=True,
        help_text='Funciones generales de la categoría (Ley 30709 § 4.1).',
    )

    # Minimum requirements (objetivos per Ley 30709)
    min_education = models.CharField(max_length=200, blank=True)
    min_experience_years = models.PositiveIntegerField(default=0)
    technical_competencies = models.JSONField(default=list, blank=True)
    soft_competencies = models.JSONField(default=list, blank=True)
    physical_conditions = models.TextField(blank=True)

    # Computed score (sum of factor scores × factor weight); written by service layer.
    total_score = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Total puntaje (computed from CategoryFactorScore × JobFactor.weight).',
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compensation_category'
        ordering = ['ccf', 'code']
        indexes = [
            models.Index(fields=['tenant', 'ccf']),
            models.Index(fields=['ccf', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'ccf', 'code'],
                name='unique_category_code_per_ccf_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
