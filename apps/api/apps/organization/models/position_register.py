"""PositionRegister — CPE (Ley 30057 SERVIR) + CAP (DL 276/728) container.

Single tenant-scoped, versioned model with a `register_type` discriminator that
serves both Cuadro de Puestos de la Entidad (CPE — Ley 30057) and Cuadro de
Asignación de Personal (CAP — DL 276/728 transitional). Versioning follows
ADR-B.7 (inline `version` + `parent_version` + `status`).

CPE is registered externally in SERVIR after approval (manual process today —
see `register_in_servir`). CAP is the transitional régimen instrument and never
registers in SERVIR.
"""
import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class PositionRegister(models.Model):
    REGISTER_TYPE_CHOICES = [
        ('cpe', 'Cuadro de Puestos de la Entidad (Ley 30057 SERVIR)'),
        ('cap', 'Cuadro de Asignación de Personal (DL 276/728)'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('registered_servir', 'Registrado SERVIR'),
        ('superseded', 'Reemplazado'),
        ('archived', 'Archivado'),
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

    register_type = models.CharField(
        max_length=10,
        choices=REGISTER_TYPE_CHOICES,
        db_index=True,
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Versioning per ADR-B.7
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='successors',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
    )
    effective_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    # SERVIR external registration tracking (CPE only; manual process today)
    servir_registered_at = models.DateTimeField(null=True, blank=True)
    servir_registration_ref = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )

    class Meta:
        db_table = 'position_register'
        ordering = ['-effective_date', '-version']
        indexes = [
            models.Index(fields=['tenant', 'register_type', 'status']),
            models.Index(fields=['tenant', 'register_type', 'version']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'register_type', 'title', 'version'],
                name='unique_position_register_title_version_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.get_register_type_display()} — {self.title} v{self.version}"

    @transaction.atomic
    def approve(self, *, user, effective_date=None):
        """Mark register as approved. Idempotent on re-approval."""
        if self.status == 'archived':
            raise ValidationError("No se puede aprobar un registro archivado.")
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.approved_by = user
        if effective_date is not None:
            self.effective_date = effective_date
        elif not self.effective_date:
            self.effective_date = timezone.now().date()
        self.save(update_fields=[
            'status', 'approved_at', 'approved_by', 'effective_date', 'updated_at',
        ])

    @transaction.atomic
    def register_in_servir(self, *, reference):
        """Mark CPE as externally registered in SERVIR (manual process)."""
        if self.register_type != 'cpe':
            raise ValidationError("Solo CPE se registra en SERVIR.")
        if self.status not in ('approved', 'registered_servir'):
            raise ValidationError(
                "El registro debe estar aprobado antes de marcarlo como registrado en SERVIR."
            )
        self.status = 'registered_servir'
        self.servir_registered_at = timezone.now()
        self.servir_registration_ref = reference
        self.save(update_fields=[
            'status', 'servir_registered_at', 'servir_registration_ref', 'updated_at',
        ])
