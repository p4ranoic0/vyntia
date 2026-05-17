"""Policy header — Module 01 governance entry point (B.15a).

Each Policy aggregates a versioned content stream (PolicyVersion). The header
holds identity (kind + title), ownership, and current-pointer to the latest
published version.

Lifecycle:
    draft → in_review → approved → published → retired

Status transitions are driven by the underlying PolicyVersion lifecycle and
the policy_service. The header `current_version` is updated when a version
moves to status='published'.

See BACKLOG #128, Module 01 of docs/modulos/01_planificacion_politicas.md.
"""

import uuid

from django.db import models


class Policy(models.Model):
    KINDS = [
        ('rit', 'Reglamento Interno de Trabajo'),
        ('codigo_etica', 'Código de Ética'),
        ('reglamento_sst', 'Reglamento Interno de SST'),
        ('politica_datos', 'Política de Datos Personales'),
        ('manual_funciones', 'Manual de Organización y Funciones'),
        ('procedimiento', 'Procedimiento'),
        ('otro', 'Otro'),
    ]
    STATUSES = [
        ('draft', 'Borrador'),
        ('in_review', 'En revisión'),
        ('approved', 'Aprobado'),
        ('published', 'Publicado'),
        ('retired', 'Retirado'),
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

    kind = models.CharField(max_length=32, choices=KINDS, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    owner_user = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='policies_owned',
    )
    owner_area = models.ForeignKey(
        'organization.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='policies_owned',
    )

    status = models.CharField(
        max_length=15, choices=STATUSES, default='draft', db_index=True,
    )
    current_version = models.ForeignKey(
        'policies.PolicyVersion',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Última versión publicada (apunta al PolicyVersion vigente)',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    updated_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    class Meta:
        db_table = 'policy'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['tenant', 'kind']),
            models.Index(fields=['tenant', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'kind', 'title'],
                name='unique_policy_title_per_kind',
            ),
        ]

    def __str__(self):
        return f'{self.get_kind_display()} — {self.title}'

    def latest_version(self):
        return self.versions.order_by('-version_number').first()

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_active(self):
        return self.status in {'published', 'approved', 'in_review'}
