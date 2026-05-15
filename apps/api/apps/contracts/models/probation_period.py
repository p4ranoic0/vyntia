"""ProbationPeriod — Module 03.4 período de prueba per régimen laboral (B.11).

Régimen-specific plazos:
- 728 personal común: 3 months
- 728 trabajador calificado (con pacto escrito): 6 months
- 728 dirección / confianza (con pacto escrito): 12 months
- MYPE pequeña: 3 months
- 276 carrera administrativa: 3 years (1095 días)
- CAS DL 1057: no aplica (contrato a plazo)

Lifecycle: pending → in_progress → evaluated → ratified | not_renewed.
Alertas a 30 / 15 días antes de end_date.

See Module 03.4 of docs/modulos/03_gestion_empleo.md and BACKLOG #116.
"""

import uuid
from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


PLAZO_DIAS = {
    '728_comun': 90,
    '728_calificado': 180,
    '728_direccion': 365,
    'mype_pequena': 90,
    '276_carrera': 1095,
    'no_aplica': 0,
}


class ProbationPeriod(models.Model):
    REGIMENES = [
        ('728_comun', '728 — Personal común'),
        ('728_calificado', '728 — Trabajador calificado (con pacto)'),
        ('728_direccion', '728 — Dirección / Confianza (con pacto)'),
        ('mype_pequena', 'MYPE Pequeña'),
        ('276_carrera', '276 — Carrera Administrativa'),
        ('no_aplica', 'No aplica (CAS u otros)'),
    ]
    STATUSES = [
        ('pending', 'Pendiente de inicio'),
        ('in_progress', 'En período de prueba'),
        ('evaluated', 'Evaluado, pendiente decisión'),
        ('ratified', 'Ratificado'),
        ('not_renewed', 'No renovado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='probation_period',
    )

    regimen = models.CharField(
        max_length=20, choices=REGIMENES, default='728_comun',
    )
    plazo_dias = models.PositiveIntegerField(default=90)
    start_date = models.DateField()
    end_date = models.DateField()

    status = models.CharField(
        max_length=20, choices=STATUSES, default='pending', db_index=True,
    )

    evaluation_score = models.PositiveSmallIntegerField(null=True, blank=True)
    evaluation_competencies = models.JSONField(default=dict, blank=True)
    evaluator = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    evaluated_at = models.DateTimeField(null=True, blank=True)

    decision_reason = models.TextField(blank=True)
    decided_by = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    decided_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'probation_period'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['end_date']),
        ]

    def save(self, *args, **kwargs):
        # Auto-derive plazo_dias from regimen + recompute end_date.
        self.plazo_dias = PLAZO_DIAS.get(self.regimen, self.plazo_dias)
        if self.start_date:
            self.end_date = self.start_date + timedelta(days=self.plazo_dias)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Probation {self.regimen} — {self.contract_id}'

    @property
    def days_remaining(self) -> int:
        today = date.today()
        return (self.end_date - today).days

    @property
    def is_within_30_days(self) -> bool:
        return 0 <= self.days_remaining <= 30

    @property
    def is_within_15_days(self) -> bool:
        return 0 <= self.days_remaining <= 15

    def mark_in_progress(self):
        if self.status != 'pending':
            raise ValidationError(
                f'Cannot start probation from status={self.status}'
            )
        self.status = 'in_progress'
        self.save(update_fields=['status', 'updated_at'])

    def mark_evaluated(self, *, score, evaluator, competencies=None, comments=''):
        if self.status not in ('pending', 'in_progress'):
            raise ValidationError(
                f'Cannot evaluate probation from status={self.status}'
            )
        self.status = 'evaluated'
        self.evaluation_score = score
        self.evaluation_competencies = competencies or {}
        self.evaluator = evaluator
        self.evaluated_at = timezone.now()
        if comments:
            self.decision_reason = comments
        self.save()

    def mark_ratified(self, *, user):
        if self.status != 'evaluated':
            raise ValidationError(
                f'Cannot ratify probation from status={self.status}'
            )
        self.status = 'ratified'
        self.decided_by = user
        self.decided_at = timezone.now()
        self.save()

    def mark_not_renewed(self, *, user, reason):
        if self.status != 'evaluated':
            raise ValidationError(
                f'Cannot non-renew probation from status={self.status}'
            )
        if not reason:
            raise ValidationError('reason is required')
        self.status = 'not_renewed'
        self.decision_reason = reason
        self.decided_by = user
        self.decided_at = timezone.now()
        self.save()
