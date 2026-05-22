"""JobPosting — convocatoria pública o privada (B.9).

Discriminator `sector_mode`:
  - 'private'      → flujo Ley 728 / DL 1057-CAS; plazos opcionales.
  - 'public_servir'→ flujo SERVIR Ley 30057; plazos legales obligatorios
                     (≥7 días hábiles entre apertura y cierre), bases
                     publicadas, transparencia, opcional FK al CPE entry
                     (B.8).

Lifecycle: draft → published → in_evaluation → closed | declared_void.
'cancelled' available before publication.
"""
import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class JobPosting(models.Model):
    SECTOR_MODE_CHOICES = [
        ('private', 'Sector privado'),
        ('public_servir', 'Sector público — concurso SERVIR (Ley 30057)'),
    ]
    POSTING_KIND_CHOICES = [
        ('internal', 'Interna'),
        ('external', 'Externa'),
        ('mixed', 'Mixta'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicada'),
        ('in_evaluation', 'En evaluación'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
        ('declared_void', 'Declarada desierta'),
    ]

    # SERVIR Art. 5 — minimum business days between opening and closing
    # applications for a public concurso.
    MIN_PUBLIC_OPEN_BUSINESS_DAYS = 7

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    requisition = models.ForeignKey(
        'employees.PersonnelRequisition', on_delete=models.PROTECT,
        related_name='postings',
    )
    code = models.CharField(max_length=30, blank=True)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)

    sector_mode = models.CharField(
        max_length=20, choices=SECTOR_MODE_CHOICES,
        default='private', db_index=True,
    )
    posting_kind = models.CharField(
        max_length=20, choices=POSTING_KIND_CHOICES,
        default='external',
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='draft', db_index=True,
    )

    published_at = models.DateTimeField(null=True, blank=True)
    applications_open_at = models.DateField(null=True, blank=True)
    applications_close_at = models.DateField(null=True, blank=True)
    results_announce_at = models.DateField(null=True, blank=True)

    # SERVIR-specific
    bases_url = models.URLField(blank=True, help_text='URL pública a las bases del concurso.')
    bases_file = models.FileField(
        upload_to='postings/bases/%Y/%m/', null=True, blank=True,
    )
    cpe_entry = models.ForeignKey(
        'organization.PositionRegisterEntry',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='postings',
        help_text='Plaza del CPE (Ley 30057, B.8) que esta convocatoria cubre.',
    )
    transparency_published = models.BooleanField(
        default=False,
        help_text='SERVIR Art. 5: publicación obligatoria en portal institucional + SERVIR.',
    )

    closed_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )

    class Meta:
        db_table = 'job_posting'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'sector_mode', 'status']),
            models.Index(fields=['requisition']),
        ]

    def __str__(self):
        return f"{self.code or self.id} — {self.title} [{self.get_sector_mode_display()}]"

    @staticmethod
    def _business_days_between(start, end):
        """Count Mon-Fri days in [start, end] inclusive of start, exclusive of end.

        Hot-fix interino (2026-05-22): no considera feriados peruanos. Sub-proyecto
        D agregará un catálogo de feriados nacionales + regionales (Ley 29408 y
        leyes regionales) para descontarlos también.
        """
        if start is None or end is None or end <= start:
            return 0
        count = 0
        cur = start
        while cur < end:
            if cur.weekday() < 5:  # 0=lunes ... 4=viernes
                count += 1
            cur += timedelta(days=1)
        return count

    def _validate_servir_publication_requirements(self):
        """Hard checks for sector_mode='public_servir' before publishing."""
        errors = []
        if not (self.bases_url or self.bases_file):
            errors.append("SERVIR exige publicar las bases (bases_url o bases_file).")
        if not self.applications_open_at or not self.applications_close_at:
            errors.append("SERVIR exige plazos de apertura y cierre de postulaciones.")
        else:
            business_days = self._business_days_between(
                self.applications_open_at, self.applications_close_at
            )
            if business_days < self.MIN_PUBLIC_OPEN_BUSINESS_DAYS:
                errors.append(
                    f"SERVIR Art. 5: la convocatoria debe estar abierta al menos "
                    f"{self.MIN_PUBLIC_OPEN_BUSINESS_DAYS} días hábiles "
                    f"(actual: {business_days})."
                )
        if not self.transparency_published:
            errors.append(
                "SERVIR exige marcar transparency_published al publicar en el portal institucional."
            )
        if errors:
            raise ValidationError(errors)

    def clean(self):
        if (
            self.applications_open_at
            and self.applications_close_at
            and self.applications_close_at < self.applications_open_at
        ):
            raise ValidationError("La fecha de cierre no puede ser anterior a la de apertura.")

    @transaction.atomic
    def publish(self, *, user):
        """draft → published. Hard validation for SERVIR."""
        if self.status != 'draft':
            raise ValidationError(
                f"Solo se publican convocatorias en borrador (estado actual: {self.status})."
            )
        if self.sector_mode == 'public_servir':
            self._validate_servir_publication_requirements()
        if self.requisition.status != 'approved':
            raise ValidationError(
                "La requisición debe estar aprobada antes de publicar la convocatoria."
            )
        self.status = 'published'
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at', 'updated_at'])

    @transaction.atomic
    def start_evaluation(self):
        """published → in_evaluation. Used after applications_close_at passes."""
        if self.status != 'published':
            raise ValidationError("Solo se evalúan convocatorias publicadas.")
        self.status = 'in_evaluation'
        self.save(update_fields=['status', 'updated_at'])

    @transaction.atomic
    def close(self, *, reason=''):
        """Close the posting (success path: someone hired)."""
        if self.status not in ('published', 'in_evaluation'):
            raise ValidationError("Solo se cierran convocatorias publicadas o en evaluación.")
        self.status = 'closed'
        self.closed_reason = reason
        self.save(update_fields=['status', 'closed_reason', 'updated_at'])

    @transaction.atomic
    def declare_void(self, *, reason):
        """Declare the posting void (no suitable candidate)."""
        if self.status not in ('published', 'in_evaluation'):
            raise ValidationError("Solo se declaran desiertas convocatorias publicadas o en evaluación.")
        if not reason:
            raise ValidationError("Se requiere motivo para declarar desierta.")
        self.status = 'declared_void'
        self.closed_reason = reason
        self.save(update_fields=['status', 'closed_reason', 'updated_at'])

    @transaction.atomic
    def cancel(self):
        if self.status != 'draft':
            raise ValidationError("Solo se cancelan convocatorias en borrador.")
        self.status = 'cancelled'
        self.save(update_fields=['status', 'updated_at'])
