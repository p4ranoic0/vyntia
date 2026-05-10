"""PositionRiskProfile — SST risk profile stub model (B.6).

Full risk catalog comes with the SST module (M07, scope post-B Core). This
stub captures the minimum needed by Position pages: overall risk level +
whether the position requires medical exam / IPERC.
"""
import uuid

from django.db import models


class PositionRiskProfile(models.Model):
    LEVEL_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('very_high', 'Muy alto'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.OneToOneField(
        'organization.Position',
        on_delete=models.CASCADE,
        related_name='risk_profile',
    )

    overall_level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='low',
    )
    risk_factors = models.JSONField(
        default=list,
        blank=True,
        help_text='Placeholder for SST module M07 — list of risk-factor tags.',
    )
    notes = models.TextField(blank=True)
    requires_medical_exam = models.BooleanField(default=False)
    requires_iperc = models.BooleanField(
        default=False,
        help_text='IPERC = Identificación de Peligros, Evaluación de Riesgos y Control.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position_risk_profile'

    def __str__(self):
        return f"Risk {self.get_overall_level_display()} for {self.position}"
