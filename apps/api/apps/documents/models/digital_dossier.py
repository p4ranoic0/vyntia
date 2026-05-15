"""DigitalDossier + DossierSection — legajo digital (B.12, Module 03.5).

Per maestro § 6.2 the legajo has 15 obligatory sections. We model it as a
header (DigitalDossier, OneToOne with Employee) + 15 section rows seeded at
creation, each carrying a permission_level (PL 1-9 per § 6.3) so that
sensitive sections (médicos = 9, accidentes = 9) are gated separately from
the standard HR view (PL 3).
"""

import uuid

from django.db import models


SECTION_DEFAULTS = [
    # (key, label, permission_level)
    ('datos_personales', 'Datos personales', 3),
    ('datos_academicos', 'Datos académicos', 3),
    ('experiencia_laboral', 'Experiencia laboral previa', 3),
    ('contratos', 'Contrato vigente y adendas', 3),
    ('declaraciones_juradas', 'Declaraciones juradas', 3),
    ('identidad_cuspp', 'Documentos de identidad y CUSPP', 3),
    ('historial_puestos', 'Historial de puestos ocupados', 3),
    ('evaluaciones', 'Evaluaciones de desempeño', 4),
    ('capacitaciones', 'Capacitaciones recibidas', 3),
    ('reconocimientos', 'Reconocimientos y felicitaciones', 3),
    ('sanciones', 'Sanciones disciplinarias', 5),
    ('licencias', 'Licencias otorgadas', 3),
    ('medicos', 'Exámenes médicos ocupacionales', 9),
    ('accidentes', 'Accidentes laborales', 9),
    ('cese', 'Documentos de cese', 5),
]


class DigitalDossier(models.Model):
    """Expediente digital permanente del trabajador.

    Retention: 5 years minimum post-cese per maestro § 6.3. Closing the
    dossier sets `is_closed=True` + closed_at; the file remains queryable
    for the retention window.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_index=True,
        related_name='+',
    )

    employee = models.OneToOneField(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='digital_dossier',
    )

    is_closed = models.BooleanField(default=False, db_index=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    retention_until = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha mínima de conservación (5 años post-cese).',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'digital_dossier'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_closed']),
        ]

    def __str__(self):
        return f'Legajo {self.employee_id}'


class DossierSection(models.Model):
    """A single section of the legajo (15 per dossier per maestro § 6.2)."""

    SECTION_KINDS = [(k, l) for k, l, _ in SECTION_DEFAULTS]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        'documents.DigitalDossier',
        on_delete=models.CASCADE,
        related_name='sections',
    )
    kind = models.CharField(max_length=30, choices=SECTION_KINDS)
    label = models.CharField(max_length=120)
    permission_level = models.PositiveSmallIntegerField(default=3)
    order = models.PositiveSmallIntegerField(default=0)

    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'dossier_section'
        ordering = ['order', 'kind']
        constraints = [
            models.UniqueConstraint(
                fields=['dossier', 'kind'],
                name='unique_dossier_section_kind',
            ),
        ]

    def __str__(self):
        return f'{self.dossier_id}:{self.kind}'
