"""MeritRanking — cuadro de méritos final por JobPosting (B.9).

Snapshot calculado por `ranking_service.compute_merit_ranking(posting=...)`.
Ranking 1 → ganador; 2..N → lista de espera (limitada por
posting.requisition.requested_count). Eliminados aparecen al final con
outcome='eliminated' para auditoría / transparencia SERVIR.

Cada recompute borra y recrea las filas atómicamente: el snapshot refleja
el estado actual de evaluaciones.
"""
import uuid

from django.db import models


class MeritRanking(models.Model):
    OUTCOME_CHOICES = [
        ('winner', 'Ganador'),
        ('waiting_list', 'Lista de espera'),
        ('eliminated', 'Eliminado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    posting = models.ForeignKey(
        'employees.JobPosting', on_delete=models.CASCADE,
        related_name='rankings',
    )
    application = models.ForeignKey(
        'employees.JobApplication', on_delete=models.CASCADE,
        related_name='rankings',
    )

    rank = models.PositiveIntegerField(
        help_text='1 = ganador; 2..N = lista de espera; ≥N+1 con outcome="eliminated".',
    )
    total_score = models.DecimalField(max_digits=6, decimal_places=2)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    snapshot_at = models.DateTimeField(auto_now_add=True)

    score_breakdown = models.JSONField(
        default=dict, blank=True,
        help_text='Per-stage detail: {stage_id: {name, score, weight, weighted}}',
    )

    class Meta:
        db_table = 'merit_ranking'
        ordering = ['posting', 'rank']
        indexes = [
            models.Index(fields=['posting', 'outcome']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'application'],
                name='unique_ranking_per_posting_application',
            ),
        ]

    def __str__(self):
        return f"{self.posting.title} #{self.rank} {self.application.candidate.full_name} ({self.total_score})"
