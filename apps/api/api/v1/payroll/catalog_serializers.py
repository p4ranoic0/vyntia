"""Read-only serializers for the vendor regulatory catalog (D.2)."""

from rest_framework import serializers

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter


class TaxParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxParameter
        fields = ["id", "code", "value", "unit", "valid_from", "valid_to", "source_law", "metadata"]


class PayrollConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollConcept
        fields = [
            "id", "code", "sunat_code", "name", "category", "subcategory",
            "affects_income_tax", "affects_afp_onp", "affects_essalud",
            "affects_cts", "affects_gratification", "is_remunerative",
            "is_variable", "cts_min_frequency", "formula_code",
            "parent_concept", "tenant", "is_active",
        ]


class RegimenConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegimenConfig
        fields = [
            "id", "regimen_code", "valid_from", "valid_to", "vacation_days_annual",
            "applies_asignacion_familiar", "applies_cts", "applies_gratification",
            "cts_deposit_months", "gratification_months",
            "severance_indemnization_formula", "essalud_rate_override", "policy_notes",
        ]
