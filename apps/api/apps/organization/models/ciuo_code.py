"""CIUOCode — SUNAT Tabla 9 reference (CIUO-08 OIT). System-wide."""
import uuid

from django.db import models


class CIUOCode(models.Model):
    """CIUO-08 (OIT) occupational classification — SUNAT Tabla 9.

    System-wide reference data (no tenant FK). The `big_group` field captures
    the CIUO-08 1-digit main group ('1' Directors, '2' Professionals,
    '3' Technicians, etc.). Seeded with the ~80 most-used 4-digit codes for
    Peru via `seed_occupational_data` management command — full list (~430
    codes) can be added in B.6.1 if needed.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    big_group = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ciuo_code'
        ordering = ['code']
        indexes = [
            models.Index(fields=['big_group']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'CIUO Code'
        verbose_name_plural = 'CIUO Codes'

    def __str__(self):
        return f"{self.code} - {self.name}"
