"""ViewSets for B.15a policies bounded context.

Endpoints under `/api/v1/policies/`:
- policies/                  CRUD + submit-for-review, retire
- policy-versions/           CRUD + submit-for-review, publish
- policy-approval-flows/     read + decide (POST detail)
- policy-publications/       CRUD + seed-acknowledgments
- policy-acknowledgments/    list/retrieve + acknowledge, decline, expire-overdue (collection)

All ViewSets are TenantAwareViewSetMixin + RRHHPermission.
"""
from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.employees.models import Employee
from apps.identity.models import Role, User
from apps.organization.models import Department
from apps.policies.models import (
    Policy,
    PolicyAcknowledgment,
    PolicyApprovalFlow,
    PolicyApprovalStep,
    PolicyPublication,
    PolicyVersion,
)
from apps.policies.services import policy_acknowledgment_service, policy_service


# ---------------------------- Serializers ----------------------------


class PolicySerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Policy
        fields = [
            'id', 'tenant',
            'kind', 'kind_display',
            'title', 'description',
            'owner_user', 'owner_area',
            'status', 'status_display',
            'current_version',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]
        read_only_fields = [
            'id', 'kind_display', 'status_display', 'status', 'current_version',
            'created_at', 'updated_at', 'created_by', 'updated_by',
        ]


class PolicyVersionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PolicyVersion
        fields = [
            'id', 'tenant', 'policy',
            'version_number', 'content_html', 'pdf_file',
            'change_summary', 'effective_date',
            'status', 'status_display',
            'submitted_at', 'submitted_by', 'approved_at',
            'published_at', 'retired_at',
            'created_at', 'updated_at', 'created_by',
        ]
        read_only_fields = [
            'id', 'version_number', 'status', 'status_display',
            'submitted_at', 'submitted_by', 'approved_at',
            'published_at', 'retired_at',
            'created_at', 'updated_at', 'created_by',
        ]


class SubmitForReviewInputSerializer(serializers.Serializer):
    approvers = serializers.ListField(
        child=serializers.UUIDField(), allow_empty=False,
    )


class PublishInputSerializer(serializers.Serializer):
    target_audience = serializers.ChoiceField(
        choices=[c[0] for c in PolicyPublication.TARGET_AUDIENCES],
        default='all',
    )
    target_role = serializers.UUIDField(required=False, allow_null=True)
    target_area = serializers.UUIDField(required=False, allow_null=True)
    target_employees = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list,
    )
    requires_acknowledgment = serializers.BooleanField(default=True)
    deadline = serializers.DateField(required=False, allow_null=True)


class PolicyApprovalStepSerializer(serializers.ModelSerializer):
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)

    class Meta:
        model = PolicyApprovalStep
        fields = [
            'id', 'flow', 'order',
            'approver_user', 'role_hint',
            'decision', 'decision_display',
            'decided_at', 'decided_by', 'comment',
            'created_at',
        ]
        read_only_fields = fields


class PolicyApprovalFlowSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    steps = PolicyApprovalStepSerializer(many=True, read_only=True)

    class Meta:
        model = PolicyApprovalFlow
        fields = [
            'id', 'tenant', 'policy_version',
            'status', 'status_display',
            'created_at', 'completed_at', 'steps',
        ]
        read_only_fields = fields


class DecideStepInputSerializer(serializers.Serializer):
    step_order = serializers.IntegerField()
    decision = serializers.ChoiceField(choices=['approved', 'rejected'])
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class PolicyPublicationSerializer(serializers.ModelSerializer):
    target_audience_display = serializers.CharField(
        source='get_target_audience_display', read_only=True,
    )

    class Meta:
        model = PolicyPublication
        fields = [
            'id', 'tenant', 'policy_version',
            'published_at', 'published_by',
            'target_audience', 'target_audience_display',
            'target_role', 'target_area', 'target_employees',
            'requires_acknowledgment', 'acknowledgment_deadline',
            'notification_sent',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'target_audience_display',
            'created_at', 'updated_at',
        ]


class PolicyAcknowledgmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    signature_kind_display = serializers.CharField(
        source='get_signature_kind_display', read_only=True,
    )

    class Meta:
        model = PolicyAcknowledgment
        fields = [
            'id', 'tenant',
            'publication', 'employee',
            'status', 'status_display',
            'acknowledged_at',
            'signature_kind', 'signature_kind_display', 'signature_payload',
            'ip', 'user_agent',
            'declined_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'acknowledged_at',
            'signature_kind_display',
            'created_at', 'updated_at',
        ]


class AcknowledgeInputSerializer(serializers.Serializer):
    signature_kind = serializers.ChoiceField(
        choices=[c[0] for c in PolicyAcknowledgment.SIGNATURE_KINDS],
    )
    signature_payload = serializers.CharField(
        required=False, allow_blank=True, default='',
    )


class DeclineInputSerializer(serializers.Serializer):
    reason = serializers.CharField()


# ---------------------------- ViewSets ----------------------------


def _client_ip(request) -> str | None:
    fwd = request.META.get('HTTP_X_FORWARDED_FOR')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _user_agent(request) -> str:
    return request.META.get('HTTP_USER_AGENT', '') or ''


class PolicyViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = Policy.objects.select_related('owner_user', 'owner_area', 'current_version')
    serializer_class = PolicySerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['kind', 'status', 'owner_user', 'owner_area']
    ordering = ['-updated_at']

    @action(detail=True, methods=['post'], url_path='retire')
    def retire(self, request, pk=None):
        policy = self.get_object()
        try:
            policy_service.retire(policy, user=request.user if request.user.is_authenticated else None)
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PolicySerializer(policy).data, message='Política retirada',
        )


class PolicyVersionViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = PolicyVersion.objects.select_related('policy', 'submitted_by')
    serializer_class = PolicyVersionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['policy', 'status']
    ordering = ['policy', '-version_number']

    @action(detail=True, methods=['post'], url_path='submit-for-review')
    def submit_for_review(self, request, pk=None):
        version = self.get_object()
        input_ser = SubmitForReviewInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        approver_ids = input_ser.validated_data['approvers']
        approvers = list(User.objects.filter(pk__in=approver_ids))
        if len(approvers) != len(approver_ids):
            return APIResponse.error(
                message='Uno o más aprobadores no existen',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            flow = policy_service.submit_for_review(
                version=version, approvers=approvers,
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PolicyApprovalFlowSerializer(flow).data,
            message='Versión enviada a revisión',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        version = self.get_object()
        input_ser = PublishInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        data = input_ser.validated_data
        target_role = None
        target_area = None
        target_employees_qs = None
        if data.get('target_role'):
            target_role = Role.objects.filter(pk=data['target_role']).first()
            if target_role is None:
                return APIResponse.error(
                    message='target_role no existe',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        if data.get('target_area'):
            target_area = Department.objects.filter(pk=data['target_area']).first()
            if target_area is None:
                return APIResponse.error(
                    message='target_area no existe',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        if data.get('target_employees'):
            target_employees_qs = Employee.objects.filter(pk__in=data['target_employees'])
        try:
            publication = policy_service.publish(
                version=version,
                target_audience=data['target_audience'],
                target_role=target_role,
                target_area=target_area,
                target_employees=target_employees_qs,
                requires_acknowledgment=data['requires_acknowledgment'],
                deadline=data.get('deadline'),
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        # Seed acks if required
        if publication.requires_acknowledgment:
            policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        return APIResponse.success(
            data=PolicyPublicationSerializer(publication).data,
            message='Política publicada',
            status_code=status.HTTP_201_CREATED,
        )


class PolicyApprovalFlowViewSet(TenantAwareViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = PolicyApprovalFlow.objects.select_related('policy_version').prefetch_related('steps')
    serializer_class = PolicyApprovalFlowSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'policy_version']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='decide')
    def decide(self, request, pk=None):
        flow = self.get_object()
        input_ser = DecideStepInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        try:
            step = policy_service.register_approval_decision(
                flow=flow,
                step_order=input_ser.validated_data['step_order'],
                approver=request.user,
                decision=input_ser.validated_data['decision'],
                comment=input_ser.validated_data.get('comment', ''),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        flow.refresh_from_db()
        return APIResponse.success(
            data={
                'step': PolicyApprovalStepSerializer(step).data,
                'flow': PolicyApprovalFlowSerializer(flow).data,
            },
            message='Decisión registrada',
        )


class PolicyPublicationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = PolicyPublication.objects.select_related('policy_version', 'published_by')
    serializer_class = PolicyPublicationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['policy_version', 'target_audience']
    ordering = ['-published_at']

    @action(detail=True, methods=['post'], url_path='seed-acknowledgments')
    def seed_acknowledgments(self, request, pk=None):
        publication = self.get_object()
        created = policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        return APIResponse.success(
            data={'created': created},
            message=f'{created} acuses creados',
        )


class PolicyAcknowledgmentViewSet(TenantAwareViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = PolicyAcknowledgment.objects.select_related(
        'publication', 'publication__policy_version', 'employee',
    )
    serializer_class = PolicyAcknowledgmentSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['publication', 'employee', 'status']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge(self, request, pk=None):
        ack = self.get_object()
        input_ser = AcknowledgeInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        try:
            policy_acknowledgment_service.capture(
                acknowledgment=ack,
                signature_kind=input_ser.validated_data['signature_kind'],
                signature_payload=input_ser.validated_data.get('signature_payload', ''),
                ip=_client_ip(request),
                user_agent=_user_agent(request),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PolicyAcknowledgmentSerializer(ack).data, message='Acuse registrado',
        )

    @action(detail=True, methods=['post'], url_path='decline')
    def decline(self, request, pk=None):
        ack = self.get_object()
        input_ser = DeclineInputSerializer(data=request.data)
        input_ser.is_valid(raise_exception=True)
        try:
            policy_acknowledgment_service.decline(
                acknowledgment=ack,
                reason=input_ser.validated_data['reason'],
                ip=_client_ip(request),
                user_agent=_user_agent(request),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PolicyAcknowledgmentSerializer(ack).data, message='Acuse rechazado',
        )

    @action(detail=False, methods=['post'], url_path='expire-overdue')
    def expire_overdue(self, request):
        tenant = getattr(request, 'tenant', None)
        count = policy_acknowledgment_service.expire_overdue(tenant=tenant)
        return APIResponse.success(
            data={'expired': count}, message=f'{count} acuses vencidos',
        )
