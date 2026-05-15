"""Serializers for B.11 Induction (Module 03.3)."""
from rest_framework import serializers

from apps.onboarding.models import (
    InductionEvaluation,
    InductionMaterial,
    InductionMentor,
    InductionPlan,
    InductionTask,
)


class InductionTaskSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(
        source='get_kind_display', read_only=True,
    )
    is_done = serializers.BooleanField(read_only=True)

    class Meta:
        model = InductionTask
        fields = [
            'id', 'plan', 'kind', 'kind_display',
            'title', 'description',
            'due_offset_days', 'order',
            'completed_at', 'completed_by',
            'is_done',
        ]
        read_only_fields = ['id', 'kind_display', 'is_done',
                            'completed_at', 'completed_by']


class InductionMaterialSerializer(serializers.ModelSerializer):
    format_display = serializers.CharField(
        source='get_format_display', read_only=True,
    )

    class Meta:
        model = InductionMaterial
        fields = [
            'id', 'plan', 'task',
            'title', 'format', 'format_display',
            'url', 'file', 'duration_minutes',
        ]
        read_only_fields = ['id', 'format_display']


class InductionMentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = InductionMentor
        fields = ['id', 'plan', 'mentor', 'assigned_at', 'notes']
        read_only_fields = ['id', 'assigned_at']


class InductionEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InductionEvaluation
        fields = [
            'id', 'plan', 'score', 'passed', 'competencies',
            'evaluator', 'evaluated_at', 'comments',
        ]
        read_only_fields = ['id', 'passed', 'evaluated_at']


class InductionPlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_status_display', read_only=True,
    )
    kind_display = serializers.CharField(
        source='get_kind_display', read_only=True,
    )
    tasks = InductionTaskSerializer(many=True, read_only=True)
    materials = InductionMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = InductionPlan
        fields = [
            'id', 'tenant', 'employee', 'contract',
            'title', 'kind', 'kind_display',
            'status', 'status_display',
            'starts_at', 'ends_at', 'completed_at', 'certified_at',
            'certificate_pdf', 'lengua_originaria',
            'created_by', 'created_at', 'updated_at',
            'tasks', 'materials',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'kind_display',
            'completed_at', 'certified_at', 'certificate_pdf',
            'created_by', 'created_at', 'updated_at',
            'tasks', 'materials',
        ]


class AssignMentorInputSerializer(serializers.Serializer):
    mentor = serializers.UUIDField(required=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class RecordEvaluationInputSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0, max_value=100, required=True)
    competencies = serializers.JSONField(required=False, default=dict)
    comments = serializers.CharField(required=False, allow_blank=True, default='')
