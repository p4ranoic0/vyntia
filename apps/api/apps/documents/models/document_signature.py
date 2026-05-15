"""DocumentSignature — electronic signature record for DigitalDocument (B.10).

Generic signature record attachable to any DigitalDocument. Lifecycle:
requested → signed | rejected | expired. Three signature kinds:
  - canvas   — base64-encoded canvas PNG (manuscript stroke)
  - typed    — typed full name as signature
  - checkbox — acuse simple (e.g., "I accept the terms")

Signer metadata (name, doc number, IP, UA, timestamp) is captured at sign time.
Full PKI digital certificate signing per DS 052-2008-PCM is deferred to a
later module.

See Module 03.2 § 3.2 and ROADMAP-B.md backlog #112.
"""

import uuid

from django.db import models


class DocumentSignature(models.Model):
    STATUSES = [
        ('requested', 'Solicitada'),
        ('signed', 'Firmada'),
        ('rejected', 'Rechazada'),
        ('expired', 'Vencida'),
    ]
    SIGNATURE_KINDS = [
        ('canvas', 'Trazo manuscrito'),
        ('checkbox', 'Acuse simple'),
        ('typed', 'Nombre tipeado'),
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

    document = models.ForeignKey(
        'documents.DigitalDocument',
        on_delete=models.CASCADE,
        related_name='signatures',
    )

    signer_user = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    signer_name = models.CharField(max_length=200)
    signer_doc_number = models.CharField(max_length=20)
    signer_email = models.EmailField(blank=True)

    kind = models.CharField(
        max_length=20, choices=SIGNATURE_KINDS, default='canvas',
    )
    status = models.CharField(
        max_length=20, choices=STATUSES, default='requested', db_index=True,
    )

    canvas_base64 = models.TextField(
        blank=True, help_text='base64 PNG payload when kind=canvas',
    )
    typed_name = models.CharField(max_length=200, blank=True)
    checkbox_text = models.CharField(max_length=500, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    signer_ip = models.GenericIPAddressField(null=True, blank=True)
    signer_user_agent = models.CharField(max_length=400, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document_signature'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['document']),
        ]

    def __str__(self):
        return (
            f'Signature {self.get_kind_display()} — '
            f'{self.signer_name} ({self.get_status_display()})'
        )
