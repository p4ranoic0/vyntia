"""Legajo content models — WorkExperience + SwornDeclaration + JobHistory (B.12).

Three missing legajo-content models per maestro § 03.5 items #3, #5, #7. They
complement the existing Employee/AcademicRecord/Certification/FamilyMember/
Contract chain and produce the full 15-section picture for the legajo.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models


class WorkExperience(models.Model):
    """Experiencia laboral previa — maestro § 03.5 #3."""

    SECTOR_CHOICES = [
        ('privado', 'Privado'),
        ('publico', 'Público'),
        ('ong', 'ONG / Tercer sector'),
        ('autonomo', 'Trabajo autónomo / freelance'),
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
        on_delete=models.CASCADE,
        related_name='work_experiences',
    )

    employer = models.CharField(max_length=200)
    position_title = models.CharField(max_length=200)
    sector = models.CharField(max_length=20, choices=SECTOR_CHOICES, default='privado')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    responsibilities = models.TextField(blank=True)
    reference_name = models.CharField(max_length=200, blank=True)
    reference_phone = models.CharField(max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'work_experience'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['tenant', 'employee']),
        ]

    def __str__(self):
        return f'{self.position_title} @ {self.employer}'

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('end_date must be after start_date')
        if self.is_current and self.end_date:
            raise ValidationError('Cannot be is_current with end_date set')


class SwornDeclaration(models.Model):
    """Declaración jurada — maestro § 03.5 #5 + N03 sector público.

    4 kinds:
    - no_parentesco: Ley de nepotismo
    - no_incompatibilidad: doble percepción / incompatibilidad de cargos
    - intereses: declaración de intereses (DJI)
    - impedimentos: impedimentos para contratar (RNSDD)
    """

    KINDS = [
        ('no_parentesco', 'No parentesco (Ley de nepotismo)'),
        ('no_incompatibilidad', 'No incompatibilidad / doble percepción'),
        ('intereses', 'Declaración de intereses'),
        ('impedimentos', 'Impedimentos para contratar'),
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
        on_delete=models.CASCADE,
        related_name='sworn_declarations',
    )
    kind = models.CharField(max_length=30, choices=KINDS)
    declared_at = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    document = models.ForeignKey(
        'documents.DigitalDocument',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sworn_declaration'
        ordering = ['-declared_at']
        indexes = [
            models.Index(fields=['tenant', 'employee', 'kind']),
        ]

    def __str__(self):
        return f'DJ {self.kind} — {self.employee_id}'


class JobHistory(models.Model):
    """Historial de puestos ocupados en la entidad — maestro § 03.5 #7."""

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
        on_delete=models.CASCADE,
        related_name='job_history',
    )
    position = models.ForeignKey(
        'organization.Position',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    position_label = models.CharField(
        max_length=200,
        help_text='Snapshot of position name for historical accuracy',
    )
    department_label = models.CharField(max_length=200, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    motive = models.CharField(
        max_length=50, blank=True,
        help_text='hiring | promotion | rotation | encargatura | designation | end',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_history'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['tenant', 'employee', 'start_date']),
        ]

    def __str__(self):
        return f'{self.employee_id}: {self.position_label} ({self.start_date}—{self.end_date or "presente"})'
