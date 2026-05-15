"""Induction models — Module 03.3 RPE 265-2017-SERVIR-PE (B.11).

5-model family integrating the new servidor/trabajador into the institution:
- InductionPlan: per-Employee header with kind (general/específica/técnica/mixta)
- InductionTask: checklist children with kind (day_1 / first_week / first_month / ongoing)
- InductionMaterial: videos/PDFs/interactives attached to plan or task
- InductionMentor: buddy User assigned to the plan (OneToOne)
- InductionEvaluation: post-inducción score + passed flag + competencies (OneToOne)

Sector-agnostic: lengua_originaria field captures the SERVIR public-sector
requirement when the territorial scope demands it; private-sector plans keep
it blank.

See Module 03.3 of docs/modulos/03_gestion_empleo.md and BACKLOG #114, #115.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class InductionPlan(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completada'),
        ('certified', 'Certificada'),
    ]
    KINDS = [
        ('general', 'General (misión/visión/políticas)'),
        ('especifica', 'Específica (funciones del puesto)'),
        ('tecnica', 'Técnica (capacitación específica)'),
        ('mixed', 'Mixta (general + específica)'),
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

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='induction_plans',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='induction_plans',
    )

    title = models.CharField(max_length=200)
    kind = models.CharField(max_length=20, choices=KINDS, default='general')
    status = models.CharField(
        max_length=20, choices=STATUSES, default='draft', db_index=True,
    )

    starts_at = models.DateField(null=True, blank=True)
    ends_at = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    certified_at = models.DateTimeField(null=True, blank=True)
    certificate_pdf = models.FileField(
        upload_to='induccion/certificados/%Y/%m/', null=True, blank=True,
    )

    lengua_originaria = models.CharField(
        max_length=10, blank=True,
        help_text='ISO 639-3 code if applicable (SERVIR territorial scope)',
    )

    created_by = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'induction_plan'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'employee']),
        ]

    def __str__(self):
        return f'Induction {self.get_kind_display()} — {self.title}'

    def mark_in_progress(self):
        if self.status != 'draft':
            raise ValidationError(
                f'Cannot start plan from status={self.status}'
            )
        self.status = 'in_progress'
        if not self.starts_at:
            self.starts_at = timezone.now().date()
        self.save(update_fields=['status', 'starts_at', 'updated_at'])

    def mark_completed(self):
        if self.status != 'in_progress':
            raise ValidationError(
                f'Cannot complete plan from status={self.status}'
            )
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_certified(self):
        if self.status != 'completed':
            raise ValidationError(
                f'Cannot certify plan from status={self.status}'
            )
        self.status = 'certified'
        self.certified_at = timezone.now()
        self.save(update_fields=['status', 'certified_at', 'updated_at'])


class InductionTask(models.Model):
    KINDS = [
        ('day_1', 'Día 1'),
        ('first_week', 'Primera semana'),
        ('first_month', 'Primer mes'),
        ('ongoing', 'Continua'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        'onboarding.InductionPlan',
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    kind = models.CharField(max_length=20, choices=KINDS, default='day_1')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_offset_days = models.PositiveIntegerField(default=0)
    order = models.PositiveSmallIntegerField(default=0)

    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    class Meta:
        db_table = 'induction_task'
        ordering = ['order', 'due_offset_days']

    def __str__(self):
        return f'{self.plan_id}:{self.title}'

    @property
    def is_done(self) -> bool:
        return self.completed_at is not None


class InductionMaterial(models.Model):
    FORMATS = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('interactive', 'Interactivo'),
        ('link', 'Enlace externo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(
        'onboarding.InductionPlan',
        on_delete=models.CASCADE,
        related_name='materials',
    )
    task = models.ForeignKey(
        'onboarding.InductionTask',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='materials',
    )
    title = models.CharField(max_length=200)
    format = models.CharField(max_length=20, choices=FORMATS, default='pdf')
    url = models.URLField(blank=True)
    file = models.FileField(
        upload_to='induccion/materiales/%Y/%m/', null=True, blank=True,
    )
    duration_minutes = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'induction_material'
        ordering = ['plan', 'title']

    def __str__(self):
        return self.title


class InductionMentor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.OneToOneField(
        'onboarding.InductionPlan',
        on_delete=models.CASCADE,
        related_name='mentor',
    )
    mentor = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='+',
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'induction_mentor'

    def __str__(self):
        return f'Mentor {self.mentor_id} for plan {self.plan_id}'


class InductionEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.OneToOneField(
        'onboarding.InductionPlan',
        on_delete=models.CASCADE,
        related_name='evaluation',
    )
    score = models.PositiveSmallIntegerField(default=0)
    passed = models.BooleanField(default=False)
    competencies = models.JSONField(default=dict, blank=True)
    evaluator = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)

    PASSING_SCORE = 60

    class Meta:
        db_table = 'induction_evaluation'

    def save(self, *args, **kwargs):
        # Auto-derive passed from score so callers cannot store inconsistent
        # values; the threshold is RPE 265 typical 60/100.
        if self.score is not None:
            self.passed = self.score >= self.PASSING_SCORE
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'Eval plan {self.plan_id}: {self.score}/100 '
            f'({"passed" if self.passed else "failed"})'
        )
