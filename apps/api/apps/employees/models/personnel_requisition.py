"""PersonnelRequisition — alta autorizada para iniciar proceso de selección (B.9).

Workflow: draft → pending_approval → approved | rejected | cancelled → fulfilled.
Approval requires BOTH HR (`approved_by_hr`) and Finance (`approved_by_finance`)
to set their respective FKs. Status transitions to 'approved' only when both
are set. Rejection from any approver during 'pending_approval' moves to
'rejected'. Once approved, JobPosting may be created against this requisition.
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class PersonnelRequisition(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending_approval', 'Pendiente de aprobación'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
        ('fulfilled', 'Cubierta'),
    ]
    JUSTIFICATION_CHOICES = [
        ('new_position', 'Plaza nueva'),
        ('replacement', 'Reemplazo por baja'),
        ('expansion', 'Crecimiento del área'),
        ('temporary', 'Cobertura temporal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    code = models.CharField(
        max_length=30, blank=True,
        help_text='Display code, e.g. REQ-2026-0001. Auto-generation deferred.',
    )
    position = models.ForeignKey(
        'organization.Position', on_delete=models.PROTECT,
        related_name='requisitions',
    )
    plaza = models.ForeignKey(
        'organization.Plaza', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='requisitions',
        help_text='Optional concrete plaza being filled. Null = new plaza.',
    )
    department = models.ForeignKey(
        'organization.Department', on_delete=models.PROTECT,
        related_name='requisitions',
    )
    justification = models.CharField(
        max_length=20, choices=JUSTIFICATION_CHOICES,
    )
    justification_notes = models.TextField(blank=True)

    requested_count = models.PositiveIntegerField(default=1)
    requested_start_date = models.DateField(null=True, blank=True)
    estimated_monthly_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', db_index=True,
    )

    requested_by = models.ForeignKey(
        'identity.User', on_delete=models.PROTECT,
        related_name='requisitions_requested',
    )
    approved_by_hr = models.ForeignKey(
        'identity.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    approved_by_finance = models.ForeignKey(
        'identity.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        'identity.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personnel_requisition'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['position']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"{self.code or self.id} — {self.position} ({self.get_status_display()})"

    @property
    def is_fully_approved(self):
        return bool(self.approved_by_hr_id and self.approved_by_finance_id)

    @transaction.atomic
    def submit_for_approval(self):
        """draft → pending_approval."""
        if self.status != 'draft':
            raise ValidationError(
                f"Solo requisiciones en borrador pueden enviarse a aprobación (estado actual: {self.status})."
            )
        self.status = 'pending_approval'
        self.save(update_fields=['status', 'updated_at'])

    @transaction.atomic
    def approve_hr(self, *, user):
        """Mark HR approval. Flips to 'approved' if Finance also approved.

        Dual control: rejects if `user` already approved this requisition as
        Finance (segregation of duties — same person cannot wear both hats).
        """
        if self.status not in ('draft', 'pending_approval'):
            raise ValidationError("La requisición no está en estado aprobable.")
        if self.approved_by_finance_id and self.approved_by_finance_id == user.pk:
            raise ValidationError(
                "Control dual: el mismo usuario no puede aprobar como RRHH y como Finanzas."
            )
        self.approved_by_hr = user
        if self.status == 'draft':
            self.status = 'pending_approval'
        if self.is_fully_approved:
            self.status = 'approved'
            self.approved_at = timezone.now()
        self.save(update_fields=[
            'approved_by_hr', 'status', 'approved_at', 'updated_at',
        ])

    @transaction.atomic
    def approve_finance(self, *, user):
        """Mark Finance approval. Flips to 'approved' if HR also approved.

        Dual control: rejects if `user` already approved this requisition as
        HR (segregation of duties).
        """
        if self.status not in ('draft', 'pending_approval'):
            raise ValidationError("La requisición no está en estado aprobable.")
        if self.approved_by_hr_id and self.approved_by_hr_id == user.pk:
            raise ValidationError(
                "Control dual: el mismo usuario no puede aprobar como Finanzas y como RRHH."
            )
        self.approved_by_finance = user
        if self.status == 'draft':
            self.status = 'pending_approval'
        if self.is_fully_approved:
            self.status = 'approved'
            self.approved_at = timezone.now()
        self.save(update_fields=[
            'approved_by_finance', 'status', 'approved_at', 'updated_at',
        ])

    @transaction.atomic
    def reject(self, *, user, reason):
        if self.status not in ('draft', 'pending_approval'):
            raise ValidationError("Solo se puede rechazar una requisición pendiente.")
        if not reason:
            raise ValidationError("Se requiere motivo de rechazo.")
        self.status = 'rejected'
        self.rejected_by = user
        self.rejected_at = timezone.now()
        self.rejected_reason = reason
        self.save(update_fields=[
            'status', 'rejected_by', 'rejected_at', 'rejected_reason', 'updated_at',
        ])

    @transaction.atomic
    def cancel(self, *, user):
        if self.status in ('approved', 'fulfilled'):
            raise ValidationError(
                "No se puede cancelar una requisición ya aprobada o cubierta."
            )
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])

    @transaction.atomic
    def mark_fulfilled(self):
        if self.status != 'approved':
            raise ValidationError("Solo requisiciones aprobadas pueden marcarse como cubiertas.")
        self.status = 'fulfilled'
        self.save(update_fields=['status', 'updated_at'])
