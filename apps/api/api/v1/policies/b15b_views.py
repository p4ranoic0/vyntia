"""ViewSets for B.15b strategic + workforce + compliance entities.

Mounted under /api/v1/ (flat, registered via api.v1.policies.urls).
All ViewSets are TenantAwareViewSetMixin + RRHHPermission.
"""
from __future__ import annotations

from decimal import Decimal

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.policies.models import (
    ComplianceMatrix,
    ComplianceObligation,
    Evidence,
    HeadcountProjection,
    HRStrategicPlan,
    KPI,
    KeyPosition,
    StrategicObjective,
    SuccessionPlan,
    SuccessorCandidate,
    WorkforcePlan,
)
from apps.policies.services import (
    compliance_service,
    strategic_plan_service,
    workforce_plan_service,
)


# ============== Strategic Plan ==============


class HRStrategicPlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = HRStrategicPlan
        fields = [
            'id', 'tenant', 'name', 'fiscal_year',
            'period_start', 'period_end', 'description',
            'status', 'status_display',
            'owner_user', 'approved_by', 'approved_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'approved_by', 'approved_at',
            'created_at', 'updated_at',
        ]


class StrategicObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategicObjective
        fields = [
            'id', 'plan', 'code', 'title', 'description',
            'weight', 'order', 'owner_user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class KPISerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_pct = serializers.SerializerMethodField()

    class Meta:
        model = KPI
        fields = [
            'id', 'objective', 'name', 'formula_note', 'unit',
            'target', 'actual', 'target_date',
            'status', 'status_display', 'progress_pct',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status_display', 'progress_pct', 'created_at', 'updated_at',
        ]

    def get_progress_pct(self, obj):
        return str(obj.progress_pct())


class UpdateKpiActualInput(serializers.Serializer):
    actual = serializers.DecimalField(max_digits=14, decimal_places=4)
    status = serializers.ChoiceField(
        choices=[c[0] for c in KPI.STATUSES], required=False, allow_null=True,
    )


class HRStrategicPlanViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = HRStrategicPlan.objects.select_related('owner_user', 'approved_by')
    serializer_class = HRStrategicPlanSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'status', 'owner_user']
    ordering = ['-fiscal_year']

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        plan = self.get_object()
        try:
            strategic_plan_service.mark_active(plan, user=request.user if request.user.is_authenticated else None)
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(data=HRStrategicPlanSerializer(plan).data, message='Plan activado')

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        plan = self.get_object()
        try:
            strategic_plan_service.mark_completed(plan)
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(data=HRStrategicPlanSerializer(plan).data, message='Plan completado')

    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, pk=None):
        plan = self.get_object()
        strategic_plan_service.archive(plan)
        return APIResponse.success(data=HRStrategicPlanSerializer(plan).data, message='Plan archivado')

    @action(detail=True, methods=['get'], url_path='progress')
    def progress(self, request, pk=None):
        plan = self.get_object()
        return APIResponse.success(
            data=strategic_plan_service.compute_progress(plan),
            message='Progreso calculado',
        )


class StrategicObjectiveViewSet(viewsets.ModelViewSet):
    queryset = StrategicObjective.objects.all()
    serializer_class = StrategicObjectiveSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan', 'code']
    ordering = ['plan', 'order']


class KPIViewSet(viewsets.ModelViewSet):
    queryset = KPI.objects.select_related('objective')
    serializer_class = KPISerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['objective', 'status']
    ordering = ['objective', 'name']

    @action(detail=True, methods=['post'], url_path='update-actual')
    def update_actual(self, request, pk=None):
        kpi = self.get_object()
        ser = UpdateKpiActualInput(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            strategic_plan_service.update_kpi_actual(
                kpi=kpi,
                actual=ser.validated_data['actual'],
                status=ser.validated_data.get('status'),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(data=KPISerializer(kpi).data, message='KPI actualizado')


# ============== Workforce Plan ==============


class WorkforcePlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WorkforcePlan
        fields = [
            'id', 'tenant', 'name', 'fiscal_year',
            'period_start', 'period_end', 'description',
            'status', 'status_display', 'owner_user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status_display', 'created_at', 'updated_at']


class HeadcountProjectionSerializer(serializers.ModelSerializer):
    delta_required = serializers.IntegerField(read_only=True)

    class Meta:
        model = HeadcountProjection
        fields = [
            'id', 'plan', 'area', 'position',
            'current_headcount', 'projected_headcount', 'delta_required',
            'target_quarter', 'justification',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'delta_required', 'created_at', 'updated_at']


class WorkforcePlanViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = WorkforcePlan.objects.select_related('owner_user')
    serializer_class = WorkforcePlanSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'status']
    ordering = ['-fiscal_year']


class HeadcountProjectionViewSet(viewsets.ModelViewSet):
    queryset = HeadcountProjection.objects.select_related('plan', 'area', 'position')
    serializer_class = HeadcountProjectionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan', 'target_quarter', 'area', 'position']
    ordering = ['plan', 'target_quarter']


# ============== Succession Plan ==============


class SuccessionPlanSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SuccessionPlan
        fields = [
            'id', 'tenant', 'name', 'fiscal_year', 'notes',
            'status', 'status_display', 'owner_user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status_display', 'created_at', 'updated_at']


class KeyPositionSerializer(serializers.ModelSerializer):
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)

    class Meta:
        model = KeyPosition
        fields = [
            'id', 'plan', 'position', 'criticality', 'criticality_display',
            'risk_notes', 'current_holder',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'criticality_display', 'created_at', 'updated_at']


class SuccessorCandidateSerializer(serializers.ModelSerializer):
    readiness_display = serializers.CharField(source='get_readiness_level_display', read_only=True)

    class Meta:
        model = SuccessorCandidate
        fields = [
            'id', 'key_position', 'employee',
            'readiness_level', 'readiness_display',
            'order', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'readiness_display', 'created_at', 'updated_at']


class SuccessionPlanViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = SuccessionPlan.objects.select_related('owner_user')
    serializer_class = SuccessionPlanSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'status']
    ordering = ['-fiscal_year']


class KeyPositionViewSet(viewsets.ModelViewSet):
    queryset = KeyPosition.objects.select_related('plan', 'position', 'current_holder')
    serializer_class = KeyPositionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan', 'criticality']
    ordering = ['plan', 'criticality']


class SuccessorCandidateViewSet(viewsets.ModelViewSet):
    queryset = SuccessorCandidate.objects.select_related('key_position', 'employee')
    serializer_class = SuccessorCandidateSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['key_position', 'readiness_level']
    ordering = ['key_position', 'order']


# ============== Compliance Matrix ==============


class ComplianceMatrixSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ComplianceMatrix
        fields = [
            'id', 'tenant', 'name', 'fiscal_year', 'description',
            'status', 'status_display', 'owner_user',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'status_display', 'created_at', 'updated_at']


class ComplianceObligationSerializer(serializers.ModelSerializer):
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    days_to_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceObligation
        fields = [
            'id', 'matrix', 'code', 'title', 'description',
            'source', 'source_display',
            'frequency', 'frequency_display',
            'severity', 'severity_display',
            'next_due_date', 'last_completed_at',
            'status', 'status_display',
            'responsible_user',
            'days_to_due', 'is_overdue',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'source_display', 'frequency_display', 'status_display',
            'severity_display', 'last_completed_at',
            'days_to_due', 'is_overdue',
            'created_at', 'updated_at',
        ]

    def get_days_to_due(self, obj):
        return obj.days_to_due()

    def get_is_overdue(self, obj):
        return obj.is_overdue()


class EvidenceSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = Evidence
        fields = [
            'id', 'tenant', 'obligation', 'kind', 'kind_display',
            'file', 'url', 'note',
            'captured_at', 'captured_by',
        ]
        read_only_fields = ['id', 'kind_display', 'captured_at']


class MarkObligationCompletedInput(serializers.Serializer):
    completed_at = serializers.DateTimeField(required=False, allow_null=True)


class ComplianceMatrixViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = ComplianceMatrix.objects.select_related('owner_user')
    serializer_class = ComplianceMatrixSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['fiscal_year', 'status']
    ordering = ['-fiscal_year']


class ComplianceObligationViewSet(viewsets.ModelViewSet):
    queryset = ComplianceObligation.objects.select_related('matrix', 'responsible_user')
    serializer_class = ComplianceObligationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['matrix', 'source', 'frequency', 'severity', 'status']
    ordering = ['next_due_date']

    @action(detail=True, methods=['post'], url_path='mark-completed')
    def mark_completed(self, request, pk=None):
        obligation = self.get_object()
        ser = MarkObligationCompletedInput(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            compliance_service.mark_obligation_completed(
                obligation=obligation,
                completed_at=ser.validated_data.get('completed_at'),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=ComplianceObligationSerializer(obligation).data,
            message='Obligación marcada como cumplida',
        )

    @action(detail=False, methods=['get'], url_path='alertas')
    def alertas(self, request):
        tenant = getattr(request, 'tenant', None)
        days_ahead = int(request.query_params.get('days_ahead', '30'))
        alerts = compliance_service.list_alerts(tenant=tenant, days_ahead=days_ahead)
        return APIResponse.success(
            data={
                'overdue': ComplianceObligationSerializer(alerts['overdue'], many=True).data,
                'due_soon': ComplianceObligationSerializer(alerts['due_soon'], many=True).data,
                'cutoff_date': str(alerts['cutoff_date']),
            },
            message='Alertas calculadas',
        )

    @action(detail=False, methods=['post'], url_path='mark-overdue')
    def mark_overdue(self, request):
        tenant = getattr(request, 'tenant', None)
        count = compliance_service.mark_overdue_obligations(tenant=tenant)
        return APIResponse.success(
            data={'flagged_overdue': count}, message=f'{count} obligaciones marcadas vencidas',
        )


class EvidenceViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = Evidence.objects.select_related('obligation', 'captured_by')
    serializer_class = EvidenceSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['obligation', 'kind']
    ordering = ['-captured_at']
