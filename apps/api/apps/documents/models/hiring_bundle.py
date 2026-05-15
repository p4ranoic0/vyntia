"""HiringDocumentBundle + HiringBundleItem — vinculación document bundle (B.10).

Tracks the set of obligatory hiring documents an employee must receive and
acknowledge at vinculación per Module 03.2 § 3.2:
- Contrato
- Reglamento Interno de Trabajo (RIT)
- Reglamento Interno de SST
- Código de Ética
- Política de Protección de Datos
- Manual de Funciones del Puesto

Each item points (optionally) to a DigitalDocument (the actual file) and a
DocumentSignature (the acuse de recibo from the employee). Bundle lifecycle:
draft → sent → acknowledged.

See ROADMAP-B.md backlog #113.
"""

import uuid

from django.db import models


class HiringDocumentBundle(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('sent', 'Enviado al colaborador'),
        ('acknowledged', 'Acusado'),
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
        related_name='hiring_bundles',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='hiring_bundles',
    )

    title = models.CharField(
        max_length=200, default='Documentos de vinculación',
    )
    status = models.CharField(
        max_length=20, choices=STATUSES, default='draft', db_index=True,
    )

    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

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
        db_table = 'hiring_document_bundle'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['employee']),
        ]

    def __str__(self):
        return f'Bundle {self.title} — {self.get_status_display()}'


class HiringBundleItem(models.Model):
    ITEM_KINDS = [
        ('contrato', 'Contrato'),
        ('rit', 'Reglamento Interno de Trabajo'),
        ('reglamento_sst', 'Reglamento Interno de SST'),
        ('codigo_etica', 'Código de Ética'),
        ('politica_datos', 'Política de Protección de Datos'),
        ('manual_funciones', 'Manual de Funciones del Puesto'),
        ('otro', 'Otro'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bundle = models.ForeignKey(
        'documents.HiringDocumentBundle',
        on_delete=models.CASCADE,
        related_name='items',
    )
    kind = models.CharField(max_length=30, choices=ITEM_KINDS)
    document = models.ForeignKey(
        'documents.DigitalDocument',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    signature = models.OneToOneField(
        'documents.DocumentSignature',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bundle_item',
    )
    required = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'hiring_bundle_item'
        ordering = ['order', 'kind']
        constraints = [
            models.UniqueConstraint(
                fields=['bundle', 'kind'],
                name='unique_bundle_kind',
            ),
        ]

    def __str__(self):
        return f'{self.bundle_id}:{self.kind}'
