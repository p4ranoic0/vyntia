"""Displacement + DisplacementExtension — Module 03.6 (B.13).

Cubre los 7 tipos de desplazamiento per DL 276 y normas SERVIR:
- rotacion: cambio dentro de la misma entidad
- encargatura: asumir temporalmente otro puesto (hasta 1 año)
- destaque: prestación de servicios en otra entidad (hasta 12m prorrogable)
- comision: comisión de servicios (según comisión + viáticos)
- designacion: cargo de confianza (mientras dure)
- transferencia: cambio definitivo a otra entidad
- permuta: intercambio entre servidores

Lifecycle: draft → pending_supervisor → pending_hr → pending_titular →
approved → active → completed | cancelled. Cada step registra el approver +
timestamp. La resolution puede generarse en PDF tras `approved`.
"""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Displacement(models.Model):
    KINDS = [
        ('rotacion', 'Rotación'),
        ('encargatura', 'Encargatura'),
        ('destaque', 'Destaque'),
        ('comision', 'Comisión de servicios'),
        ('designacion', 'Designación'),
        ('transferencia', 'Transferencia'),
        ('permuta', 'Permuta'),
    ]
    STATUSES = [
        ('draft', 'Borrador'),
        ('pending_supervisor', 'Pendiente jefe directo'),
        ('pending_hr', 'Pendiente RRHH'),
        ('pending_titular', 'Pendiente titular'),
        ('approved', 'Aprobado'),
        ('active', 'En ejecución'),
        ('completed', 'Concluido'),
        ('cancelled', 'Cancelado'),
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
        related_name='displacements',
    )

    kind = models.CharField(max_length=20, choices=KINDS, db_index=True)
    status = models.CharField(
        max_length=20, choices=STATUSES, default='draft', db_index=True,
    )

    # Origen y destino (campos snapshot — los FKs se resuelven a Departments).
    origen_department = models.ForeignKey(
        'organization.Department',
        on_delete=models.PROTECT,
        related_name='displacements_origen',
    )
    destino_department = models.ForeignKey(
        'organization.Department',
        on_delete=models.PROTECT,
        related_name='displacements_destino',
    )
    origen_position = models.ForeignKey(
        'organization.Position',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    destino_position = models.ForeignKey(
        'organization.Position',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    # Para destaque / transferencia inter-entidad
    destino_entidad_externa = models.CharField(
        max_length=200, blank=True,
        help_text='Razón social de la entidad destino si el desplazamiento es externo',
    )

    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    justification = models.TextField(blank=True)
    resolution_number = models.CharField(
        max_length=64, blank=True,
        help_text='Número de resolución administrativa (opaco; puede generarse externamente)',
    )

    # Approval audit
    requested_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_by_supervisor = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_by_supervisor_at = models.DateTimeField(null=True, blank=True)
    approved_by_hr = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_by_hr_at = models.DateTimeField(null=True, blank=True)
    approved_by_titular = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    approved_by_titular_at = models.DateTimeField(null=True, blank=True)

    cancelled_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    resolution_pdf = models.FileField(
        upload_to='desplazamiento/resoluciones/%Y/%m/',
        null=True, blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'displacement'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'kind']),
            models.Index(fields=['employee']),
        ]

    def __str__(self):
        return f'{self.get_kind_display()} — emp={self.employee_id} ({self.get_status_display()})'

    # ----------------------- Lifecycle -----------------------

    def submit(self):
        if self.status != 'draft':
            raise ValidationError(f'Cannot submit from status={self.status}')
        self.status = 'pending_supervisor'
        self.save(update_fields=['status', 'updated_at'])

    def approve_supervisor(self, *, user):
        if self.status != 'pending_supervisor':
            raise ValidationError(f'Cannot approve_supervisor from status={self.status}')
        self.status = 'pending_hr'
        self.approved_by_supervisor = user
        self.approved_by_supervisor_at = timezone.now()
        self.save(update_fields=[
            'status', 'approved_by_supervisor', 'approved_by_supervisor_at',
            'updated_at',
        ])

    def approve_hr(self, *, user):
        if self.status != 'pending_hr':
            raise ValidationError(f'Cannot approve_hr from status={self.status}')
        self.status = 'pending_titular'
        self.approved_by_hr = user
        self.approved_by_hr_at = timezone.now()
        self.save(update_fields=[
            'status', 'approved_by_hr', 'approved_by_hr_at', 'updated_at',
        ])

    def approve_titular(self, *, user):
        if self.status != 'pending_titular':
            raise ValidationError(f'Cannot approve_titular from status={self.status}')
        self.status = 'approved'
        self.approved_by_titular = user
        self.approved_by_titular_at = timezone.now()
        self.save(update_fields=[
            'status', 'approved_by_titular', 'approved_by_titular_at',
            'updated_at',
        ])

    def activate(self):
        if self.status != 'approved':
            raise ValidationError(f'Cannot activate from status={self.status}')
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save(update_fields=['status', 'activated_at', 'updated_at'])

    def complete(self):
        if self.status != 'active':
            raise ValidationError(f'Cannot complete from status={self.status}')
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def cancel(self, *, reason):
        if self.status in ('completed', 'cancelled'):
            raise ValidationError(f'Cannot cancel from status={self.status}')
        if not reason:
            raise ValidationError('reason is required to cancel')
        self.status = 'cancelled'
        self.cancelled_reason = reason
        self.cancelled_at = timezone.now()
        self.save(update_fields=[
            'status', 'cancelled_reason', 'cancelled_at', 'updated_at',
        ])


class DisplacementExtension(models.Model):
    """Renovación / prórroga de un desplazamiento activo."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    displacement = models.ForeignKey(
        'organization.Displacement',
        on_delete=models.CASCADE,
        related_name='extensions',
    )

    previous_end_date = models.DateField()
    new_end_date = models.DateField()
    reason = models.TextField()
    resolution_number = models.CharField(max_length=64, blank=True)
    granted_by = models.ForeignKey(
        'identity.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'displacement_extension'
        ordering = ['-granted_at']

    def __str__(self):
        return f'Extension {self.displacement_id}: {self.previous_end_date}→{self.new_end_date}'

    def clean(self):
        if self.new_end_date <= self.previous_end_date:
            raise ValidationError('new_end_date must be after previous_end_date')
