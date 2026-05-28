"""Domain (tenant-scoped) models for Vyntia Pay.

`Compensation` is the per-employee versioned salary+régimen+pension+banking
snapshot — the single source of truth D.4's engine reads via
`Compensation.current_for(employee, as_of_date)`. Snapshots are immutable in
practice: when an employee's situation changes (raise, AFP switch, banking
update), HR creates a new row with the new `valid_from` and the previous row's
`valid_to` is closed off.
"""

import uuid
from datetime import date

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class Compensation(TenantScopedModel):
    SOURCE_CHOICES = [
        ("MIGRATION", "Migración inicial desde EmploymentData/Contract"),
        ("MANUAL", "Creado manualmente por RRHH"),
        ("CONTRACT_AMENDMENT", "Generado por adenda de contrato"),
    ]

    PENSION_REGIME_CHOICES = [
        ("ONP", "ONP"),
        ("AFP_INTEGRA", "AFP Integra"),
        ("AFP_PRIMA", "AFP Prima"),
        ("AFP_PROFUTURO", "AFP Profuturo"),
        ("AFP_HABITAT", "AFP Hábitat"),
    ]

    AFP_COMMISSION_CHOICES = [
        ("FLUJO", "Flujo"),
        ("MIXTA", "Mixta"),
        ("SALDO", "Saldo"),
    ]

    HEALTH_REGIME_CHOICES = [
        ("ESSALUD", "EsSalud"),
        ("EPS", "EPS"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    employee = models.ForeignKey(
        "employees.Employee", on_delete=models.PROTECT, related_name="compensations"
    )

    # versioning
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)

    # salary
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    has_family_allowance = models.BooleanField(default=False)

    # snapshots (string, no FK by lifecycle)
    regimen_laboral = models.CharField(max_length=20)
    pension_regime = models.CharField(max_length=20, choices=PENSION_REGIME_CHOICES)
    afp_commission_type = models.CharField(
        max_length=8, choices=AFP_COMMISSION_CHOICES, blank=True, default=""
    )
    cuspp = models.CharField(max_length=12, blank=True, default="")
    health_regime = models.CharField(max_length=16, choices=HEALTH_REGIME_CHOICES)
    eps_provider = models.CharField(max_length=64, blank=True, default="")

    # banking
    cci = models.CharField(max_length=20, blank=True, default="")
    bank_code = models.CharField(max_length=8, blank=True, default="")
    bank_account = models.CharField(max_length=20, blank=True, default="")
    permission_level = models.IntegerField(default=6)

    # provenance
    source = models.CharField(max_length=24, choices=SOURCE_CHOICES)
    contract_snapshot = models.ForeignKey(
        "contracts.Contract", null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    # audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="+",
    )

    class Meta(TenantScopedModel.Meta):
        db_table = "payroll_compensation"
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "valid_from"], name="uniq_compensation_employee_validfrom"
            ),
        ]
        ordering = ["-valid_from"]
        indexes = [
            models.Index(fields=["tenant", "employee", "-valid_from"]),
        ]

    def __str__(self):
        return f"{self.employee_id} {self.base_salary} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def current_for(cls, employee, as_of_date: date):
        """Return the Compensation row valid for `employee` on `as_of_date`, or None."""
        return (
            cls.objects.filter(employee=employee, valid_from__lte=as_of_date)
            .filter(models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=as_of_date))
            .order_by("-valid_from")
            .first()
        )
