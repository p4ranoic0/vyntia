"""TRegistroDeclaration — SUNAT T-Registro declaration data + lifecycle (B.10).

Captures the data needed to prepare an Anexo 3 plain-text declaration to SUNAT
for an employee's alta, baja, or modificación in T-Registro. The actual wire-
level submission to SUNAT is out-of-scope; this model owns the prepared payload
and tracks the lifecycle (draft → validated → submitted → accepted | rejected)
plus the SUNAT response artifacts (reference, response timestamp, rejection
reason).

See Module 03.2 § 3.4 of docs/modulos/03_gestion_empleo.md and ROADMAP-B.md
backlog #111.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TRegistroDeclaration(models.Model):
    DECLARATION_TYPES = [
        ('alta', 'Alta'),
        ('baja', 'Baja'),
        ('modificacion', 'Modificación'),
    ]
    STATUSES = [
        ('draft', 'Borrador'),
        ('validated', 'Validado PVS'),
        ('submitted', 'Enviado SUNAT'),
        ('accepted', 'Aceptado'),
        ('rejected', 'Rechazado'),
    ]
    REGIMEN_PENSIONARIO = [
        ('snp', 'SNP (ONP)'),
        ('spp', 'SPP (AFP)'),
        ('decreto_19990', 'DL 19990'),
        ('decreto_20530', 'DL 20530'),
        ('sin_regimen', 'Sin régimen'),
    ]
    REGIMEN_SALUD = [
        ('essalud', 'EsSalud'),
        ('eps', 'EPS'),
        ('sctr', 'SCTR'),
        ('ninguno', 'Ninguno'),
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

    declaration_type = models.CharField(
        max_length=20, choices=DECLARATION_TYPES, default='alta',
    )
    status = models.CharField(
        max_length=20, choices=STATUSES, default='draft', db_index=True,
    )

    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.PROTECT,
        related_name='t_registro_declarations',
    )
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.PROTECT,
        related_name='t_registro_declarations',
    )

    employer_ruc = models.CharField(max_length=11)
    employer_razon_social = models.CharField(max_length=200)

    worker_doc_type = models.CharField(
        max_length=4, default='01',
        help_text='SUNAT Tabla 2: 01=DNI 04=CE 07=Pasaporte',
    )
    worker_doc_number = models.CharField(max_length=20)
    worker_apellido_paterno = models.CharField(max_length=80)
    worker_apellido_materno = models.CharField(max_length=80, blank=True)
    worker_nombres = models.CharField(max_length=100)
    worker_birth_date = models.DateField()
    worker_gender = models.CharField(max_length=1, default='M')
    worker_nationality_code = models.CharField(
        max_length=3, default='604',
        help_text='ISO 3166 country code (numeric). 604=PER.',
    )
    worker_address = models.CharField(max_length=300, blank=True)

    contract_start_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    work_modality_code = models.CharField(
        max_length=3, help_text='SUNAT modalidad code per Tabla 8',
    )
    occupation_code = models.CharField(
        max_length=6, blank=True,
        help_text='CIUO-08 per Tabla 24',
    )

    regimen_laboral_code = models.CharField(max_length=3, default='728')
    regimen_pensionario = models.CharField(
        max_length=20, choices=REGIMEN_PENSIONARIO, default='snp',
    )
    pension_provider_code = models.CharField(
        max_length=10, blank=True, help_text='AFP code if SPP',
    )
    cuspp = models.CharField(
        max_length=20, blank=True, help_text='CUSPP del trabajador SPP',
    )
    regimen_salud = models.CharField(
        max_length=20, choices=REGIMEN_SALUD, default='essalud',
    )
    eps_code = models.CharField(max_length=10, blank=True)

    remuneracion_basica = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
    )
    jornada_horas_semanales = models.PositiveSmallIntegerField(default=48)

    anexo3_txt = models.TextField(
        blank=True, help_text='Generated Anexo 3 plain text payload',
    )
    pvs_errors = models.JSONField(default=list, blank=True)
    sunat_reference = models.CharField(
        max_length=64, blank=True,
        help_text='Número de constancia SUNAT',
    )
    sunat_response_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        'identity.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_registro_declaration'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'declaration_type']),
            models.Index(fields=['contract']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'contract', 'declaration_type'],
                condition=models.Q(status__in=['submitted', 'accepted']),
                name='unique_active_t_registro_per_contract',
            ),
        ]

    def __str__(self):
        return (
            f'T-Registro {self.get_declaration_type_display()} — '
            f'{self.worker_doc_number}'
        )

    def mark_validated(self):
        """Promote draft → validated. Requires pvs_errors=[]."""
        if self.pvs_errors:
            raise ValidationError(
                'Cannot mark validated while pvs_errors is non-empty.'
            )
        self.status = 'validated'
        self.save(update_fields=['status', 'updated_at'])

    def mark_submitted(self, *, user, reference=''):
        """Promote draft|validated → submitted. Stamps user + reference + timestamp."""
        if self.status not in ('draft', 'validated'):
            raise ValidationError(
                f'Cannot submit from status={self.status}'
            )
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.submitted_by = user
        self.sunat_reference = reference
        self.save(update_fields=[
            'status', 'submitted_at', 'submitted_by',
            'sunat_reference', 'updated_at',
        ])

    def mark_accepted(self, *, reference=''):
        """Submitted → accepted. Stamps response timestamp + optional reference."""
        if self.status != 'submitted':
            raise ValidationError(
                f'Cannot mark accepted from status={self.status}'
            )
        self.status = 'accepted'
        self.sunat_response_at = timezone.now()
        if reference:
            self.sunat_reference = reference
        self.save(update_fields=[
            'status', 'sunat_response_at', 'sunat_reference', 'updated_at',
        ])

    def mark_rejected(self, *, reason):
        """Submitted → rejected. Records rejection_reason."""
        if self.status != 'submitted':
            raise ValidationError(
                f'Cannot mark rejected from status={self.status}'
            )
        if not reason:
            raise ValidationError('rejection reason is required')
        self.status = 'rejected'
        self.rejection_reason = reason
        self.sunat_response_at = timezone.now()
        self.save(update_fields=[
            'status', 'rejection_reason', 'sunat_response_at', 'updated_at',
        ])
