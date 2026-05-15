"""Serializers for B.10 contracts — TRegistroDeclaration."""
from rest_framework import serializers

from apps.contracts.models import TRegistroDeclaration


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
