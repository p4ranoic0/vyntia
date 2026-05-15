"""Serializers for B.10 contracts — TRegistroDeclaration + B.11 ProbationPeriod."""
from rest_framework import serializers

from apps.contracts.models import ProbationPeriod, TRegistroDeclaration


class TRegistroDeclarationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    declaration_type_display = serializers.CharField(
        source='get_declaration_type_display', read_only=True,
    )

    class Meta:
        model = TRegistroDeclaration
        fields = [
            'id', 'tenant',
            'declaration_type', 'declaration_type_display',
            'status', 'status_display',
            'contract', 'employee',
            'employer_ruc', 'employer_razon_social',
            'worker_doc_type', 'worker_doc_number',
            'worker_apellido_paterno', 'worker_apellido_materno',
            'worker_nombres', 'worker_birth_date', 'worker_gender',
            'worker_nationality_code', 'worker_address',
            'contract_start_date', 'contract_end_date',
            'work_modality_code', 'occupation_code',
            'regimen_laboral_code', 'regimen_pensionario',
            'pension_provider_code', 'cuspp',
            'regimen_salud', 'eps_code',
            'remuneracion_basica', 'jornada_horas_semanales',
            'anexo3_txt', 'pvs_errors',
            'sunat_reference', 'sunat_response_at', 'rejection_reason',
            'submitted_at', 'submitted_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display',
            'declaration_type_display',
            'anexo3_txt', 'pvs_errors',
            'sunat_reference', 'sunat_response_at', 'rejection_reason',
            'submitted_at', 'submitted_by',
            'created_at', 'updated_at',
        ]


class SubmitDeclarationInputSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False, allow_blank=True, default='')


class MarkAcceptedInputSerializer(serializers.Serializer):
    reference = serializers.CharField(required=False, allow_blank=True, default='')


class MarkRejectedInputSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


# ---------------------------- B.11 ProbationPeriod -----------------------------

class ProbationPeriodSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    regimen_display = serializers.CharField(
        source='get_regimen_display', read_only=True,
    )
    days_remaining = serializers.IntegerField(read_only=True)
    is_within_30_days = serializers.BooleanField(read_only=True)
    is_within_15_days = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProbationPeriod
        fields = [
            'id', 'tenant', 'contract',
            'regimen', 'regimen_display',
            'plazo_dias', 'start_date', 'end_date',
            'status', 'status_display',
            'evaluation_score', 'evaluation_competencies',
            'evaluator', 'evaluated_at',
            'decision_reason', 'decided_by', 'decided_at',
            'days_remaining', 'is_within_30_days', 'is_within_15_days',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'plazo_dias', 'end_date',
            'status', 'status_display', 'regimen_display',
            'evaluation_score', 'evaluation_competencies',
            'evaluator', 'evaluated_at',
            'decision_reason', 'decided_by', 'decided_at',
            'days_remaining', 'is_within_30_days', 'is_within_15_days',
            'created_at', 'updated_at',
        ]


class EvaluateProbationInputSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0, max_value=100, required=True)
    competencies = serializers.JSONField(required=False, default=dict)
    comments = serializers.CharField(required=False, allow_blank=True, default='')


class NotRenewInputSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)
