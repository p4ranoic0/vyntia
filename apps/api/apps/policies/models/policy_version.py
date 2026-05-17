"""PolicyVersion — immutable versioned content for a Policy (B.15a).

Each Policy has 1..N PolicyVersion rows. A version is created in 'draft',
submitted for review (transition triggers creation of PolicyApprovalFlow),
moves to 'approved' once all flow steps approve, then 'published' on release.

The PDF attachment is optional (the platform stores the rendered HTML in
`content_html`; PDFs can be generated on demand). When a PDF is uploaded
it lands under `policies/<YYYY>/<MM>/` via TenantStorage prefix (ADR-B.4).

Versions are immutable post-approval — re-edits create a new version.

See BACKLOG #128.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class PolicyVersion(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('under_review', 'En revisión'),
        ('approved', 'Aprobada'),
        ('published', 'Publicada'),
        ('retired', 'Retirada'),
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

    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.CASCADE,
        related_name='versions',
    )
    version_number = models.PositiveIntegerField()

    content_html = models.TextField(
        blank=True,
        help_text='Cuerpo HTML de la versión (renderizable a PDF)',
    )
    pdf_file = models.FileField(
        upload_to='policies/%Y/%m/',
        null=True, blank=True,
        help_text='PDF rendereado o subido manualmente (max ~10 MB)',
    )
    change_summary = models.TextField(
        blank=True,
        help_text='Qué cambia respecto a la versión anterior',
    )
    effective_date = models.DateField(
        null=True, blank=True,
        help_text='Fecha en que entra en vigencia (puede ser futura)',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='draft', db_index=True,
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    retired_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    class Meta:
        db_table = 'policy_version'
        ordering = ['policy', '-version_number']
        indexes = [
            models.Index(fields=['tenant', 'policy']),
            models.Index(fields=['status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['policy', 'version_number'],
                name='unique_policy_version_number',
            ),
        ]

    def __str__(self):
        return f'{self.policy.title} v{self.version_number} ({self.status})'

    def mark_under_review(self, *, user=None):
        if self.status != 'draft':
            raise ValidationError('Solo versiones en borrador pueden enviarse a revisión.')
        self.status = 'under_review'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.save(update_fields=['status', 'submitted_at', 'submitted_by', 'updated_at'])

    def mark_approved(self):
        if self.status != 'under_review':
            raise ValidationError('Solo versiones en revisión pueden aprobarse.')
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_at', 'updated_at'])

    def revert_to_draft(self):
        if self.status not in {'under_review', 'approved'}:
            raise ValidationError('Solo versiones en revisión o aprobadas pueden volver a borrador.')
        self.status = 'draft'
        self.submitted_at = None
        self.approved_at = None
        self.save(update_fields=['status', 'submitted_at', 'approved_at', 'updated_at'])

    def mark_published(self):
        if self.status != 'approved':
            raise ValidationError('Solo versiones aprobadas pueden publicarse.')
        self.status = 'published'
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at', 'updated_at'])

    def mark_retired(self):
        if self.status not in {'published', 'approved'}:
            raise ValidationError('Solo versiones publicadas o aprobadas pueden retirarse.')
        self.status = 'retired'
        self.retired_at = timezone.now()
        self.save(update_fields=['status', 'retired_at', 'updated_at'])
