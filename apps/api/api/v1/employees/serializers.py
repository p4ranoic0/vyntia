"""Serializers for B.9 Selección — Module 03.1.

Built fresh under api/v1/employees/ since prior employee endpoints live in
api/v1/rrhh/. Future B.x phases should consolidate here.
"""
from rest_framework import serializers

from apps.employees.models import (
    Candidate,
    CandidateEvaluation,
    JobApplication,
    JobPosting,
    MeritRanking,
    PersonnelRequisition,
    SelectionStage,
)


class CandidateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Candidate
        fields = [
            'id', 'tenant',
            'document_type', 'document_number',
            'first_names', 'last_names', 'full_name',
            'birth_date', 'gender',
            'email', 'phone', 'address',
            'years_experience', 'highest_education',
            'cv_file',
            'source',
            'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']


class PersonnelRequisitionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    justification_display = serializers.CharField(
        source='get_justification_display', read_only=True,
    )
    is_fully_approved = serializers.BooleanField(read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    department_name = serializers.CharField(
        source='department.nombre_completo', read_only=True,
    )

    class Meta:
        model = PersonnelRequisition
        fields = [
            'id', 'tenant',
            'code',
            'position', 'position_name',
            'plaza',
            'department', 'department_name',
            'justification', 'justification_display',
            'justification_notes',
            'requested_count', 'requested_start_date', 'estimated_monthly_cost',
            'status', 'status_display',
            'requested_by',
            'approved_by_hr', 'approved_by_finance', 'approved_at',
            'rejected_by', 'rejected_at', 'rejected_reason',
            'is_fully_approved',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'approved_by_hr', 'approved_by_finance',
            'approved_at', 'rejected_by', 'rejected_at', 'rejected_reason',
            'is_fully_approved',
            'created_at', 'updated_at',
        ]


class RequisitionApprovalSerializer(serializers.Serializer):
    """Empty body for approve-hr/approve-finance/cancel/mark-fulfilled."""


class RequisitionRejectSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000)


class JobPostingSerializer(serializers.ModelSerializer):
    sector_mode_display = serializers.CharField(
        source='get_sector_mode_display', read_only=True,
    )
    posting_kind_display = serializers.CharField(
        source='get_posting_kind_display', read_only=True,
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            'id', 'tenant',
            'requisition', 'code', 'title', 'summary',
            'sector_mode', 'sector_mode_display',
            'posting_kind', 'posting_kind_display',
            'status', 'status_display',
            'published_at', 'applications_open_at', 'applications_close_at',
            'results_announce_at',
            'bases_url', 'bases_file', 'cpe_entry', 'transparency_published',
            'closed_reason',
            'application_count',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = [
            'id', 'status', 'published_at', 'application_count',
            'created_at', 'updated_at',
        ]

    def get_application_count(self, obj):
        return obj.applications.count()


class JobPostingPublishSerializer(serializers.Serializer):
    """Empty body — publish action validates internally."""


class JobPostingCloseSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class JobPostingDeclareVoidSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=2000)


class SelectionStageSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = SelectionStage
        fields = [
            'id',
            'posting',
            'kind', 'kind_display', 'name',
            'order', 'is_eliminatoria',
            'min_score', 'max_score', 'weight',
            'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JobApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    posting_title = serializers.CharField(source='posting.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = [
            'id', 'tenant',
            'posting', 'posting_title',
            'candidate', 'candidate_name',
            'status', 'status_display',
            'applied_at',
            'eliminated_at_stage', 'elimination_reason',
            'withdrawn_at',
            'cover_letter', 'custom_cv_file',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'applied_at', 'eliminated_at_stage',
            'elimination_reason', 'withdrawn_at',
            'created_at', 'updated_at',
        ]


class JobApplicationAdvanceSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(
        choices=JobApplication.STATUS_CHOICES,
    )


class JobApplicationEliminateSerializer(serializers.Serializer):
    stage = serializers.UUIDField(required=False, allow_null=True)
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True)


class CandidateEvaluationSerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source='stage.name', read_only=True)
    candidate_name = serializers.CharField(
        source='application.candidate.full_name', read_only=True,
    )

    class Meta:
        model = CandidateEvaluation
        fields = [
            'id',
            'application', 'candidate_name',
            'stage', 'stage_name',
            'evaluator',
            'score', 'passed', 'notes',
            'evaluated_at', 'updated_at',
        ]
        # evaluator is set automatically by ViewSet.perform_create from
        # request.user — clients should not send it.
        read_only_fields = ['id', 'evaluator', 'passed', 'evaluated_at', 'updated_at']


class MeritRankingSerializer(serializers.ModelSerializer):
    outcome_display = serializers.CharField(source='get_outcome_display', read_only=True)
    candidate_name = serializers.CharField(
        source='application.candidate.full_name', read_only=True,
    )

    class Meta:
        model = MeritRanking
        fields = [
            'id',
            'posting', 'application', 'candidate_name',
            'rank', 'total_score', 'outcome', 'outcome_display',
            'score_breakdown', 'snapshot_at',
        ]
        read_only_fields = fields
