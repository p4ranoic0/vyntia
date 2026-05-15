"""Serializers for B.12 legajo content — WorkExperience + SwornDeclaration + JobHistory."""
from rest_framework import serializers

from apps.employees.models import JobHistory, SwornDeclaration, WorkExperience


class WorkExperienceSerializer(serializers.ModelSerializer):
    sector_display = serializers.CharField(source='get_sector_display', read_only=True)

    class Meta:
        model = WorkExperience
        fields = [
            'id', 'tenant', 'employee',
            'employer', 'position_title',
            'sector', 'sector_display',
            'start_date', 'end_date', 'is_current',
            'responsibilities', 'reference_name', 'reference_phone',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'sector_display', 'created_at', 'updated_at']


class SwornDeclarationSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = SwornDeclaration
        fields = [
            'id', 'tenant', 'employee',
            'kind', 'kind_display',
            'declared_at', 'valid_until', 'document', 'notes',
            'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'kind_display', 'created_at', 'updated_at']


class JobHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobHistory
        fields = [
            'id', 'tenant', 'employee',
            'position', 'position_label',
            'department_label',
            'start_date', 'end_date', 'motive',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
