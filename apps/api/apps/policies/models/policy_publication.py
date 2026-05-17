"""PolicyPublication — org-wide release of a PolicyVersion (B.15a).

Each publication targets an audience (all employees / a role / an area /
a list of specific employees). After PolicyAcknowledgmentService seeds the
acuse rows, employees see the publication in their inbox.

Module 01 § 5.4: RIT, Reglamento SST y Código de Ética requieren acuse de
recibido por todo el personal (Art. 27 D.S. 003-97-TR).

See BACKLOG #128.
"""

import uuid

from django.db import models


class PolicyPublication(models.Model):
    TARGET_AUDIENCES = [
        ('all', 'Todos los empleados'),
        ('role', 'Por rol'),
        ('area', 'Por área'),
        ('employee', 'Empleados específicos'),
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

    policy_version = models.OneToOneField(
        'policies.PolicyVersion',
        on_delete=models.PROTECT,
        related_name='publication',
    )

    published_at = models.DateTimeField()
    published_by = models.ForeignKey(
        'identity.User',
        on_delete=models.PROTECT,
        related_name='+',
    )

    target_audience = models.CharField(
        max_length=15, choices=TARGET_AUDIENCES, default='all',
    )
    target_role = models.ForeignKey(
        'identity.Role',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    target_area = models.ForeignKey(
        'organization.Department',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    target_employees = models.ManyToManyField(
        'employees.Employee',
        blank=True,
        related_name='+',
    )

    requires_acknowledgment = models.BooleanField(default=True)
    acknowledgment_deadline = models.DateField(null=True, blank=True)
    notification_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_publication'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['tenant', '-published_at']),
        ]

    def __str__(self):
        return f'Publication of {self.policy_version_id} ({self.target_audience})'

    def expand_target_employees(self):
        """Resolve the target audience into an Employee queryset.

        Lazy import keeps the model loader happy across apps boot order.
        """
        from apps.employees.models import Employee

        qs = Employee.objects.all()
        if self.tenant_id is not None:
            qs = qs.filter(tenant_id=self.tenant_id)

        if self.target_audience == 'all':
            return qs
        if self.target_audience == 'area' and self.target_area_id is not None:
            return qs.filter(
                datos_laborales__area_id=self.target_area_id,
                datos_laborales__estado_datos='activo',
            ).distinct()
        if self.target_audience == 'role' and self.target_role_id is not None:
            return qs.filter(
                usuario__roles_asignados__rol_id=self.target_role_id,
                usuario__roles_asignados__estado_asignacion='activo',
            ).distinct()
        if self.target_audience == 'employee':
            return self.target_employees.all()
        return qs.none()
