"""SalaryBand — banda salarial mín/medio/máx per Category (Ley 30709 § 4.1)."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class SalaryBand(models.Model):
    """1-to-1 with Category. Holds min/mid/max salaries and placement criteria.

    Ley 30709 § 4.1 mandates that every Category have a published salary band.
    `placement_criteria` documents the objective rules used to place a worker
    within the band (experiencia, desempeño, formación adicional).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.OneToOneField(
        'compensation.Category',
        on_delete=models.CASCADE,
        related_name='salary_band',
    )

    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    mid_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='PEN')

    placement_criteria = models.TextField(
        blank=True,
        help_text='Criterios para ubicar al trabajador en la banda (experiencia, desempeño, etc.).',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_band'

    def __str__(self):
        return (
            f"{self.category.code}: {self.currency} "
            f"{self.min_salary}-{self.max_salary}"
        )

    def clean(self):
        if self.min_salary >= self.mid_salary:
            raise ValidationError("min_salary debe ser < mid_salary")
        if self.mid_salary >= self.max_salary:
            raise ValidationError("mid_salary debe ser < max_salary")
