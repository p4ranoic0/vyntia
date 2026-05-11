"""SelectionStage — etapas configurables por convocatoria (B.9).

Una JobPosting puede definir N etapas ordenadas (curricular, knowledge,
psycho, interview, technical, reference). Cada etapa tiene:
  - min_score / max_score (rango válido de calificación)
  - is_eliminatoria (failing la elimina del proceso)
  - weight (porcentaje en cuadro de méritos final — solo aplica para
    rankings finales; las eliminatorias actúan como gate antes del weight).

Para SERVIR el flujo típico es: curricular (eliminatoria) → knowledge
(eliminatoria 14/20) → psycho (referencial) → interview (eliminatoria).
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class SelectionStage(models.Model):
    KIND_CHOICES = [
        ('curricular', 'Evaluación curricular'),
        ('knowledge', 'Prueba de conocimientos'),
        ('psycho', 'Evaluación psicolaboral'),
        ('interview', 'Entrevista personal'),
        ('technical', 'Prueba técnica'),
        ('reference', 'Verificación de referencias'),
        ('other', 'Otra'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    posting = models.ForeignKey(
        'employees.JobPosting', on_delete=models.CASCADE,
        related_name='stages',
    )
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    name = models.CharField(
        max_length=100,
        help_text='Custom display name (e.g. "Examen técnico SQL"); defaults to kind label.',
    )
    order = models.PositiveIntegerField(default=0)
    is_eliminatoria = models.BooleanField(
        default=True,
        help_text='Si es eliminatoria, fallar score < min_score quita al candidato.',
    )
    min_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Puntaje mínimo aprobatorio (e.g. 14.00 para SERVIR conocimientos).',
    )
    max_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=20,
    )
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Peso en cuadro de méritos final (0-100). Sumatoria de pesos = 100 en posting.',
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'selection_stage'
        ordering = ['posting', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'order'],
                name='unique_stage_order_per_posting',
            ),
        ]

    def __str__(self):
        return f"{self.posting.title} — #{self.order} {self.name or self.get_kind_display()}"

    def clean(self):
        if self.min_score > self.max_score:
            raise ValidationError("min_score no puede exceder max_score.")
        if self.weight < 0 or self.weight > 100:
            raise ValidationError("weight debe estar entre 0 y 100.")
