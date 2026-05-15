"""Serializers for B.13 Displacement + LocationHistory."""
from rest_framework import serializers

from apps.organization.models import (
    Displacement,
    DisplacementExtension,
    LocationHistory,
)


class DisplacementExtensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplacementExtension
        fields = [
            'id', 'displacement', 'previous_end_date', 'new_end_date',
            'reason', 'resolution_number', 'granted_by', 'granted_at',
        ]
        read_only_fields = ['id', 'granted_at']


class DisplacementSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    extensions = DisplacementExtensionSerializer(many=True, read_only=True)

    class Meta:
        model = Displacement
        fields = [
            'id', 'tenant', 'employee',
            'kind', 'kind_display', 'status', 'status_display',
            'origen_department', 'destino_department',
            'origen_position', 'destino_position',
            'destino_entidad_externa',
            'start_date', 'end_date',
            'justification', 'resolution_number',
            'requested_by',
            'approved_by_supervisor', 'approved_by_supervisor_at',
            'approved_by_hr', 'approved_by_hr_at',
            'approved_by_titular', 'approved_by_titular_at',
            'cancelled_reason', 'cancelled_at',
            'activated_at', 'completed_at',
            'resolution_pdf',
            'created_at', 'updated_at',
            'extensions',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'kind_display',
            'approved_by_supervisor', 'approved_by_supervisor_at',
            'approved_by_hr', 'approved_by_hr_at',
            'approved_by_titular', 'approved_by_titular_at',
            'cancelled_reason', 'cancelled_at',
            'activated_at', 'completed_at',
            'created_at', 'updated_at',
            'extensions',
        ]


class CancelDisplacementInputSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False)


class ExtendDisplacementInputSerializer(serializers.Serializer):
    new_end_date = serializers.DateField(required=True)
    reason = serializers.CharField(required=True, allow_blank=False)
    resolution_number = serializers.CharField(required=False, allow_blank=True, default='')


class LocationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationHistory
        fields = '__all__'
