"""ComplianceMatrix + ComplianceObligation + Evidence — Module 01 § 4 (B.15b).

Matriz de cumplimiento: obligaciones legales/normativas (SUNAT, SUNAFIL,
MINTRA, MTPE, SERVIR, ESSALUD, ONP, AFP, internas) con vencimientos
recurrentes (mensual/trimestral/semestral/anual/única). Cada obligación
acumula Evidence (archivos + URLs + notas) que prueban su cumplimiento.

See BACKLOG #131, Module 01 § 4 of docs/modulos/01_planificacion_politicas.md.
"""

import uuid
from datetime import date

from django.db import models


class ComplianceMatrix(models.Model):
    STATUSES = [
        ('active', 'Activa'),
        ('archived', 'Archivada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )

    name = models.CharField(max_length=200)
    fiscal_year = models.PositiveIntegerField(db_index=True)
    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=15, choices=STATUSES, default='active', db_index=True,
    )

    owner_user = models.ForeignKey(
        'identity.User', on_delete=models.PROTECT,
        related_name='compliance_matrices_owned',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_matrix'
        ordering = ['-fiscal_year', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'fiscal_year']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'fiscal_year', 'name'],
                name='unique_matrix_per_year_name',
            ),
        ]

    def __str__(self):
        return f'Matriz {self.name} ({self.fiscal_year})'


class ComplianceObligation(models.Model):
    SOURCES = [
        ('sunat', 'SUNAT'),
        ('sunafil', 'SUNAFIL'),
        ('mintra', 'MINTRA'),
        ('mtpe', 'MTPE'),
        ('servir', 'SERVIR'),
        ('essalud', 'EsSalud'),
        ('onp', 'ONP'),
        ('afp', 'AFP'),
        ('interno', 'Interno'),
        ('otro', 'Otro'),
    ]
    FREQUENCIES = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
        ('unica', 'Única'),
        ('ad_hoc', 'Ad-hoc'),
    ]
    STATUSES = [
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('cumplido', 'Cumplido'),
        ('vencido', 'Vencido'),
    ]
    SEVERITIES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matrix = models.ForeignKey(
        'policies.ComplianceMatrix',
        on_delete=models.CASCADE,
        related_name='obligations',
    )

    code = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=15, choices=SOURCES, default='otro')
    frequency = models.CharField(max_length=15, choices=FREQUENCIES, default='mensual')
    severity = models.CharField(max_length=10, choices=SEVERITIES, default='media')

    next_due_date = models.DateField()
    last_completed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=15, choices=STATUSES, default='pendiente', db_index=True,
    )

    responsible_user = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_obligation'
        ordering = ['next_due_date', 'severity']
        indexes = [
            models.Index(fields=['matrix', 'status']),
            models.Index(fields=['next_due_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['matrix', 'code'],
                name='unique_obligation_code_per_matrix',
            ),
        ]

    def __str__(self):
        return f'{self.code} — {self.title} ({self.status})'

    def days_to_due(self) -> int:
        return (self.next_due_date - date.today()).days

    def is_overdue(self) -> bool:
        return self.status not in {'cumplido'} and self.days_to_due() < 0


class Evidence(models.Model):
    KINDS = [
        ('archivo', 'Archivo'),
        ('link', 'Enlace'),
        ('nota', 'Nota'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenancy.Tenant', on_delete=models.PROTECT,
        null=True, blank=True, db_index=True, related_name='+',
    )
    obligation = models.ForeignKey(
        'policies.ComplianceObligation',
        on_delete=models.CASCADE,
        related_name='evidences',
    )
    kind = models.CharField(max_length=10, choices=KINDS, default='archivo')
    file = models.FileField(
        upload_to='compliance/%Y/%m/',
        null=True, blank=True,
    )
    url = models.URLField(blank=True)
    note = models.TextField(blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)
    captured_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )

    class Meta:
        db_table = 'compliance_evidence'
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['obligation', '-captured_at']),
        ]

    def __str__(self):
        return f'Evidencia {self.kind} para {self.obligation_id}'
