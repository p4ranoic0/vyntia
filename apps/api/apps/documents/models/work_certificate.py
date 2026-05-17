"""WorkCertificate — Constancia de Trabajo Art. 45 LPCL (B.14).

Documento de entrega obligatoria al cese (D.S. 003-97-TR Art. 45):
debe contener cargo, tiempo de servicio, último sueldo, motivo del cese.
Se genera vía PDFGenerator chain (xhtml2pdf → WeasyPrint → ReportLab) y
queda como `DigitalDocument` adjunto al dossier digital del empleado.

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #125.
"""

import uuid

from django.db import models


class WorkCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    termination = models.OneToOneField(
        'contracts.Termination',
        on_delete=models.PROTECT,
        related_name='work_certificate',
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='work_certificates',
    )
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='work_certificates',
    )

    numero_constancia = models.CharField(
        max_length=64,
        help_text='Número correlativo de la constancia',
    )
    fecha_emision = models.DateField()

    cargo_snapshot = models.CharField(max_length=200, blank=True)
    area_snapshot = models.CharField(max_length=200, blank=True)
    fecha_inicio_snapshot = models.DateField(null=True, blank=True)
    fecha_fin_snapshot = models.DateField(null=True, blank=True)
    sueldo_snapshot = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    motivo_cese_textual = models.TextField(
        blank=True,
        help_text='Descripción textual del motivo del cese para el cuerpo',
    )

    signed_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text='Firma del responsable RRHH que emite',
    )
    pdf_file = models.FileField(
        upload_to='cese/constancias_trabajo/%Y/%m/',
        null=True, blank=True,
    )
    digital_document = models.OneToOneField(
        'documents.DigitalDocument',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Documento digital adjunto al legajo (opcional)',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'work_certificate'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'employee']),
            models.Index(fields=['fecha_emision']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'numero_constancia'],
                name='unique_work_certificate_number',
            ),
        ]

    def __str__(self):
        return f'Constancia {self.numero_constancia} — emp={self.employee_id}'
