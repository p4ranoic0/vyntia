"""OccupationalCategory — SUNAT Tabla 10 reference data (system-wide)."""
import uuid

from django.db import models


class OccupationalCategory(models.Model):
    """SUNAT Tabla 10 — ocupational category (ejecutivo / empleado / obrero).

    System-wide reference data (no tenant FK). Shared across all tenants;
    seeded by `seed_occupational_data` management command.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'occupational_category'
        ordering = ['code']
        verbose_name = 'Occupational Category'
        verbose_name_plural = 'Occupational Categories'

    def __str__(self):
        return f"{self.code} - {self.name}"
