"""Vendor-managed regulatory catalog (D.2).

Global (no tenant FK) per decision D-E — except PayrollConcept, which is
vendor-seeded (tenant=NULL) with optional per-tenant custom concepts that
inherit their parent's affectation flags. All rows are date-versioned with
(valid_from, valid_to); lookups resolve the row valid at a given date
(ADR-D.6 tax-year cutoff). Decimals follow ADR-D.2.
"""

import uuid

from django.db import models


class _VersionedQuerySet(models.QuerySet):
    def valid_at(self, as_of_date):
        return self.filter(valid_from__lte=as_of_date).filter(
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=as_of_date)
        )


class TaxParameter(models.Model):
    """Date-versioned regulatory scalar (UIT, RMV, rates, renta-5ta brackets)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64, db_index=True)
    value = models.DecimalField(max_digits=14, decimal_places=4)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    unit = models.CharField(
        max_length=8,
        choices=[("PEN", "Soles"), ("RATE", "Tasa"), ("UIT", "Múltiplo UIT")],
    )
    source_law = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)

    objects = _VersionedQuerySet.as_manager()

    class Meta:
        db_table = "payroll_tax_parameter"
        constraints = [
            models.UniqueConstraint(fields=["code", "valid_from"], name="uniq_taxparam_code_validfrom"),
        ]
        ordering = ["code", "-valid_from"]

    def __str__(self):
        return f"{self.code}={self.value} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def get(cls, code, as_of_date):
        """Return the TaxParameter for `code` valid on `as_of_date`, or None."""
        return cls.objects.filter(code=code).valid_at(as_of_date).order_by("-valid_from").first()


class PayrollConcept(models.Model):
    """SUNAT Tabla 22 concept (vendor) or tenant custom concept (parent-inherited)."""

    CATEGORY_CHOICES = [
        ("INCOME", "Ingreso"),
        ("DEDUCTION", "Descuento"),
        ("CONTRIBUTION_EMPLOYER", "Aporte empleador"),
        ("TAX", "Tributo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=64)
    sunat_code = models.CharField(max_length=4, blank=True, default="")
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=24, blank=True, default="")
    affects_income_tax = models.BooleanField(default=False)
    affects_afp_onp = models.BooleanField(default=False)
    affects_essalud = models.BooleanField(default=False)
    affects_cts = models.BooleanField(default=False)
    affects_gratification = models.BooleanField(default=False)
    is_remunerative = models.BooleanField(default=True)
    is_variable = models.BooleanField(default=False)
    cts_min_frequency = models.IntegerField(default=3)
    formula_code = models.CharField(max_length=64, blank=True, default="")
    parent_concept = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="custom_children"
    )
    tenant = models.ForeignKey(
        "tenancy.Tenant", null=True, blank=True, on_delete=models.PROTECT, related_name="+"
    )
    is_active = models.BooleanField(default=True)

    _INHERITED_FLAGS = (
        "affects_income_tax", "affects_afp_onp", "affects_essalud",
        "affects_cts", "affects_gratification", "is_remunerative",
    )

    class Meta:
        db_table = "payroll_concept"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "code"], name="uniq_concept_tenant_code"),
        ]
        ordering = ["sunat_code", "code"]

    def __str__(self):
        return f"{self.sunat_code or '----'} {self.code}"

    def clean(self):
        """Custom concepts inherit affectation flags from their parent (no override)."""
        if self.parent_concept_id:
            for flag in self._INHERITED_FLAGS:
                setattr(self, flag, getattr(self.parent_concept, flag))
            if not self.sunat_code:
                self.sunat_code = self.parent_concept.sunat_code


class RegimenConfig(models.Model):
    """Date-versioned per-régimen-laboral configuration (728 in MVP)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    regimen_code = models.CharField(max_length=24, db_index=True)
    valid_from = models.DateField()
    valid_to = models.DateField(null=True, blank=True)
    vacation_days_annual = models.IntegerField()
    applies_asignacion_familiar = models.BooleanField(default=True)
    applies_cts = models.BooleanField(default=True)
    applies_gratification = models.BooleanField(default=True)
    cts_deposit_months = models.JSONField(default=list)
    gratification_months = models.JSONField(default=list)
    severance_indemnization_formula = models.CharField(max_length=64)
    essalud_rate_override = models.DecimalField(max_digits=6, decimal_places=4, null=True, blank=True)
    policy_notes = models.TextField(blank=True, default="")

    objects = _VersionedQuerySet.as_manager()

    class Meta:
        db_table = "payroll_regimen_config"
        constraints = [
            models.UniqueConstraint(fields=["regimen_code", "valid_from"], name="uniq_regimen_code_validfrom"),
        ]
        ordering = ["regimen_code", "-valid_from"]

    def __str__(self):
        return f"{self.regimen_code} ({self.valid_from}..{self.valid_to or '∞'})"

    @classmethod
    def get(cls, regimen_code, as_of_date):
        return cls.objects.filter(regimen_code=regimen_code).valid_at(as_of_date).order_by("-valid_from").first()
