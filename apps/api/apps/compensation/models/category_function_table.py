"""CategoryFunctionTable (CCF) — Ley 30709 versioned document container."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class CategoryFunctionTable(models.Model):
    """Cuadro de Categorías y Funciones — Ley 30709 § 4.

    Tenant-scoped, versioned per ADR-B.7 pattern (inline `version` + `parent_version`
    + `status`). A CCF aggregates Category rows for the tenant. Ley 30709
    mandates revision at least annually; the version chain captures historical
    CCFs for SUNAFIL audit.
    """

    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
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
        related_name='approved_ccfs',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_ccfs',
    )

    class Meta:
        db_table = 'category_function_table'
        ordering = ['-effective_date', '-version']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'version']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'title', 'version'],
                name='unique_ccf_title_version_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.title} v{self.version} ({self.get_status_display()})"

    @transaction.atomic
    def approve(self, *, user, effective_date=None):
        """Mark the CCF as approved. Idempotent on re-approval."""
        if self.status == 'archived':
            raise ValidationError("No se puede aprobar un CCF archivado.")
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
