"""Serializers for B.14 Termination + SeveranceSettlement."""
from rest_framework import serializers

from apps.contracts.models import (
    SeveranceLine,
    SeveranceSettlement,
    Termination,
)


class TerminationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    causal_display = serializers.CharField(source='get_causal_display', read_only=True)
    regimen_display = serializers.CharField(source='get_regimen_display', read_only=True)
    baja_tregistro_overdue_48h = serializers.BooleanField(read_only=True)
    hours_since_completion = serializers.FloatField(read_only=True)

    class Meta:
        model = Termination
        fields = [
            'id', 'tenant', 'contract', 'employee',
            'regimen', 'regimen_display',
            'causal', 'causal_display',
            'status', 'status_display',
            'fecha_cese', 'last_day_worked', 'motivo',
            'carta_renuncia_file', 'acta_cese_file',
            'baja_t_registro',
            'initiated_by', 'initiated_at',
            'completed_by', 'completed_at',
            'liquidated_by', 'liquidated_at',
            'cancelled_reason', 'cancelled_at', 'cancelled_by',
            'baja_tregistro_overdue_48h', 'hours_since_completion',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'causal_display', 'regimen_display',
            'baja_t_registro',
            'initiated_by', 'initiated_at',
            'completed_by', 'completed_at',
            'liquidated_by', 'liquidated_at',
            'cancelled_reason', 'cancelled_at', 'cancelled_by',
            'baja_tregistro_overdue_48h', 'hours_since_completion',
            'created_at', 'updated_at',
        ]


class InitiateTerminationInputSerializer(serializers.Serializer):
    contract = serializers.UUIDField()
    causal = serializers.ChoiceField(choices=[c[0] for c in Termination.CAUSALES])
    regimen = serializers.ChoiceField(
        choices=[r[0] for r in Termination.REGIMENES], default='728',
    )
    fecha_cese = serializers.DateField()
    last_day_worked = serializers.DateField(required=False, allow_null=True)
    motivo = serializers.CharField(required=False, allow_blank=True, default='')


class CancelTerminationInputSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


class MarkBajaTRegistroInputSerializer(serializers.Serializer):
    declaration = serializers.UUIDField()


# ---------------------------- Settlement ----------------------------

class SeveranceLineSerializer(serializers.ModelSerializer):
    component_display = serializers.CharField(source='get_component_display', read_only=True)

    class Meta:
        model = SeveranceLine
        fields = [
            'id', 'settlement', 'component', 'component_display',
            'amount', 'base_calculation', 'formula_note',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'component_display', 'created_at', 'updated_at']


class SeveranceSettlementSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lines = SeveranceLineSerializer(many=True, read_only=True)

    class Meta:
        model = SeveranceSettlement
        fields = [
            'id', 'tenant', 'termination', 'status', 'status_display',
            'sueldo_base', 'fecha_inicio_contrato', 'fecha_cese',
            'total_amount', 'paid_amount',
            'computed_at', 'computed_by',
            'paid_at', 'paid_by',
            'manual_override', 'notes',
            'lines',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display',
            'sueldo_base', 'fecha_inicio_contrato', 'fecha_cese',
            'total_amount', 'paid_amount',
            'computed_at', 'computed_by',
            'paid_at', 'paid_by',
            'lines',
            'created_at', 'updated_at',
        ]


class ComputeSettlementInputSerializer(serializers.Serializer):
    dias_acumulados_no_gozados = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, allow_null=True, default=None,
    )


class MarkSettlementPaidInputSerializer(serializers.Serializer):
    paid_total = serializers.DecimalField(max_digits=14, decimal_places=2)
    paid_at = serializers.DateTimeField(required=False, allow_null=True)
