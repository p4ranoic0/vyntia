"""Plaza — actual occupied/vacant position slot."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Plaza(models.Model):
    """A specific instance of a Position.

    Position is the catalog ("Analista de Sistemas exists"); Plaza is the
    instance ("there are 3 Analista plazas: ANA-001 is occupied by Juan,
    ANA-002 is vacant, ANA-003 is frozen pending budget").

    Lifecycle states (Maestro Module 02 § 2.3):
    - VACANTE — open, ready for assignment
    - OCUPADA — currently assigned to current_employee
    - CONGELADA — temporarily frozen (budget / restructure)
    - ELIMINADA — soft-delete (kept for history)
    """

    STATUS_CHOICES = [
        ('vacante', 'Vacante'),
        ('ocupada', 'Ocupada'),
        ('congelada', 'Congelada'),
        ('eliminada', 'Eliminada'),
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

    code = models.CharField(max_length=30)
    position = models.ForeignKey(
        'organization.Position',
        on_delete=models.PROTECT,
        related_name='plazas',
    )
    current_employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plazas',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='vacante',
        db_index=True,
    )

    opened_at = models.DateField(null=True, blank=True)
    closed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plaza'
        ordering = ['code']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['position', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_plaza_code_per_tenant',
            ),
        ]

    def __str__(self):
        return f"{self.code} ({self.get_status_display()})"

    def occupy(self, employee):
        """Assign an employee — moves OCUPADA. Idempotent on same employee."""
        if self.status == 'eliminada':
            raise ValidationError("No se puede ocupar una plaza eliminada.")
        if self.status == 'ocupada' and self.current_employee_id == employee.pk:
            # Idempotent: already assigned to this employee
            return
        if self.status == 'ocupada':
            raise ValidationError(
                f"La plaza ya está ocupada por otro empleado "
                f"({self.current_employee}). Vacate first."
            )
        self.current_employee = employee
        self.status = 'ocupada'
        self.save(update_fields=['current_employee', 'status', 'updated_at'])

    def vacate(self):
        """Unassign current employee — moves to VACANTE."""
        if self.status == 'eliminada':
            raise ValidationError("No se puede vacar una plaza eliminada.")
        self.current_employee = None
        self.status = 'vacante'
        self.save(update_fields=['current_employee', 'status', 'updated_at'])

    def freeze(self):
        """Freeze the plaza (budget / restructure)."""
        if self.status == 'eliminada':
            raise ValidationError("No se puede congelar una plaza eliminada.")
        self.status = 'congelada'
        self.save(update_fields=['status', 'updated_at'])

    def soft_delete(self):
        """Soft delete — keeps history but removes from active reports."""
        self.current_employee = None
        self.status = 'eliminada'
        self.save(update_fields=['current_employee', 'status', 'updated_at'])
