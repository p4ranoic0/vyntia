"""JobApplication — postulación de un Candidate a una JobPosting (B.9).

State machine:
  received → reviewing → in_evaluation → finalist → offered → accepted → hired
                                       ↘ eliminated
                                       ↘ rejected
                                       ↘ withdrawn
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('received', 'Recibida'),
        ('reviewing', 'En revisión'),
        ('in_evaluation', 'En evaluación'),
        ('eliminated', 'Eliminada'),
        ('finalist', 'Finalista'),
        ('offered', 'Oferta enviada'),
        ('accepted', 'Aceptada'),
        ('hired', 'Contratada'),
        ('rejected', 'Rechazada'),
        ('withdrawn', 'Retirada por candidato'),
    ]

    # Forward transitions allowed via advance_to(); terminal states block.
    ADVANCE_TRANSITIONS = {
        'received': {'reviewing', 'eliminated', 'rejected', 'withdrawn'},
        'reviewing': {'in_evaluation', 'eliminated', 'rejected', 'withdrawn'},
        'in_evaluation': {'finalist', 'eliminated', 'rejected', 'withdrawn'},
        'finalist': {'offered', 'eliminated', 'rejected', 'withdrawn'},
        'offered': {'accepted', 'rejected', 'withdrawn'},
        'accepted': {'hired', 'withdrawn'},
        # Terminal:
        'eliminated': set(),
        'hired': set(),
        'rejected': set(),
        'withdrawn': set(),
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    posting = models.ForeignKey(
        'employees.JobPosting', on_delete=models.PROTECT,
        related_name='applications',
    )
    candidate = models.ForeignKey(
        'employees.Candidate', on_delete=models.PROTECT,
        related_name='applications',
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='received', db_index=True,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    eliminated_at_stage = models.ForeignKey(
        'employees.SelectionStage', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    elimination_reason = models.TextField(blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    cover_letter = models.TextField(blank=True)
    custom_cv_file = models.FileField(
        upload_to='applications/cv/%Y/%m/', null=True, blank=True,
        help_text='Posting-specific CV; falls back to candidate.cv_file when null.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_application'
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['posting', 'status']),
            models.Index(fields=['candidate']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'candidate'],
                name='unique_application_per_posting_candidate',
            ),
        ]

    def __str__(self):
        return f"{self.candidate.full_name} → {self.posting.title} ({self.get_status_display()})"

    @transaction.atomic
    def advance_to(self, new_status):
        """Move forward through the state machine. Validates legality."""
        valid_targets = self.ADVANCE_TRANSITIONS.get(self.status, set())
        if new_status not in valid_targets:
            raise ValidationError(
                f"Transición inválida: {self.status} → {new_status}. "
                f"Permitidas: {sorted(valid_targets) or '(estado terminal)'}"
            )
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])

    @transaction.atomic
    def eliminate(self, *, stage=None, reason=''):
        """Mark application as eliminated (optionally tagged with stage)."""
        if self.status in ('eliminated', 'hired', 'rejected', 'withdrawn'):
            raise ValidationError("La postulación ya está en estado terminal.")
        self.status = 'eliminated'
        self.eliminated_at_stage = stage
        self.elimination_reason = reason
        self.save(update_fields=[
            'status', 'eliminated_at_stage', 'elimination_reason', 'updated_at',
        ])

    @transaction.atomic
    def withdraw(self):
        if self.status in ('hired', 'rejected', 'withdrawn'):
            raise ValidationError("La postulación ya está en estado terminal.")
        self.status = 'withdrawn'
        self.withdrawn_at = timezone.now()
        self.save(update_fields=['status', 'withdrawn_at', 'updated_at'])
