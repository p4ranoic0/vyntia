"""PositionRegisterEntry — rows of a PositionRegister (CPE or CAP).

A single entry table serves both CPE (Ley 30057) and CAP (DL 276/728) variants.
Type-specific fields are nullable/blank and populated based on
`register.register_type`:

- CPE entries use `nivel_organizacional` and `nivel_remunerativo`.
- CAP entries use `clasificacion_cap` (FP/EC/SP-DS/SP-EJ/SP-ES/SP-AP/RE).
- Generic fields (`plaza_code`, `plaza_count`, `situacion`) apply to both.
"""
import uuid

from django.db import models


class PositionRegisterEntry(models.Model):
    CAP_CLASSIFICATION_CHOICES = [
        ('fp', 'FP - Funcionario Público'),
        ('ec', 'EC - Empleado de Confianza'),
        ('sp_ds', 'SP-DS - Directivo Superior'),
        ('sp_ej', 'SP-EJ - Ejecutivo'),
        ('sp_es', 'SP-ES - Especialista'),
        ('sp_ap', 'SP-AP - Apoyo'),
        ('re', 'RE - Régimen Especial'),
    ]
    SITUATION_CHOICES = [
        ('ocupada', 'Ocupada'),
        ('vacante', 'Vacante'),
        ('prevista', 'Prevista'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    register = models.ForeignKey(
        'organization.PositionRegister',
        on_delete=models.CASCADE,
        related_name='entries',
    )
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='register_entries',
    )

    # Generic entry metadata
    sequence = models.PositiveIntegerField(default=0)
    plaza_code = models.CharField(max_length=30, blank=True)
    plaza_count = models.PositiveIntegerField(default=1)
    situacion = models.CharField(
        max_length=20,
        choices=SITUATION_CHOICES,
        default='vacante',
    )

    # CPE-specific (when register.register_type='cpe')
    nivel_organizacional = models.CharField(max_length=100, blank=True)
    nivel_remunerativo = models.CharField(max_length=50, blank=True)

    # CAP-specific (when register.register_type='cap')
    clasificacion_cap = models.CharField(
        max_length=10,
        choices=CAP_CLASSIFICATION_CHOICES,
        blank=True,
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position_register_entry'
        ordering = ['register', 'sequence', 'plaza_code']
        indexes = [
            models.Index(fields=['register', 'sequence']),
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"{self.register.title} #{self.sequence} — {self.position.code}"
