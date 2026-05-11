"""CandidateEvaluation — calificación de un Candidate en una SelectionStage (B.9).

Una evaluación por (application, stage) es única — el evaluador (User)
califica un candidato en una etapa, registrando score + notas. `passed`
se deriva automáticamente: passed = score >= stage.min_score.

Para SERVIR conocimientos con min_score=14, una nota 13.99 marca passed=False
y debe disparar JobApplication.eliminate(stage=...) — orquestado en service
layer (Task 8) o vía signal en API.
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class CandidateEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(
        'employees.JobApplication', on_delete=models.CASCADE,
        related_name='evaluations',
    )
    stage = models.ForeignKey(
        'employees.SelectionStage', on_delete=models.PROTECT,
        related_name='evaluations',
    )
    evaluator = models.ForeignKey(
        'identity.User', on_delete=models.PROTECT,
        related_name='evaluations_authored',
    )

    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    evaluated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_evaluation'
        ordering = ['stage__order', 'application']
        indexes = [
            models.Index(fields=['application', 'stage']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'stage'],
                name='unique_evaluation_per_application_stage',
            ),
        ]

    def __str__(self):
        return f"{self.application} @ {self.stage} = {self.score} ({'✓' if self.passed else '✗'})"

    def clean(self):
        if not (self.stage.min_score <= self.score <= self.stage.max_score):
            raise ValidationError(
                f"Puntaje {self.score} fuera de rango "
                f"[{self.stage.min_score}, {self.stage.max_score}]"
            )

    def save(self, *args, **kwargs):
        # Auto-derive passed from score vs stage.min_score
        self.passed = self.score >= self.stage.min_score
        super().save(*args, **kwargs)
