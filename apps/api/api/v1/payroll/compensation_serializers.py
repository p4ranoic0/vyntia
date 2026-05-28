"""Compensation serializer (D.3)."""

from rest_framework import serializers

from apps.payroll.models import Compensation


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = [
            "id", "employee", "valid_from", "valid_to", "base_salary",
            "has_family_allowance", "regimen_laboral", "pension_regime",
            "afp_commission_type", "cuspp", "health_regime", "eps_provider",
            "cci", "bank_code", "bank_account", "permission_level",
            "source", "contract_snapshot", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
