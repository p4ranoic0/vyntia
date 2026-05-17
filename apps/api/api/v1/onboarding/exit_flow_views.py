"""ViewSets for B.14 ExitInterview + HandoverChecklist + SystemsOffboarding."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, serializers, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.contracts.models import Termination
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.identity.models import User
from apps.onboarding.models import (
    ExitInterview,
    HandoverChecklist,
    HandoverItem,
    SystemsOffboarding,
)
from apps.onboarding.services import exit_flow_service


# ---------------------------- Serializers ----------------------------

class ExitInterviewSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sentiment_display = serializers.CharField(source='get_sentiment_display', read_only=True)

    class Meta:
        model = ExitInterview
        fields = [
            'id', 'tenant', 'termination',
            'status', 'status_display',
            'answers', 'sentiment', 'sentiment_display', 'comments',
            'interviewer', 'interview_date',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'sentiment_display',
            'answers', 'sentiment', 'comments',
            'interviewer', 'interview_date',
            'created_at', 'updated_at',
        ]


class SubmitExitInterviewInputSerializer(serializers.Serializer):
    answers = serializers.JSONField()
    sentiment = serializers.ChoiceField(choices=[s[0] for s in ExitInterview.SENTIMENTS])
    comments = serializers.CharField(required=False, allow_blank=True, default='')
    interview_date = serializers.DateField(required=False, allow_null=True)


class HandoverItemSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = HandoverItem
        fields = [
            'id', 'checklist', 'kind', 'kind_display',
            'name', 'description', 'is_required',
            'status', 'status_display',
            'delivered_at', 'delivered_by', 'notes', 'order',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'kind_display', 'status_display',
            'delivered_at', 'delivered_by',
            'created_at', 'updated_at',
        ]


class HandoverChecklistSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = HandoverItemSerializer(many=True, read_only=True)

    class Meta:
        model = HandoverChecklist
        fields = [
            'id', 'tenant', 'termination',
            'status', 'status_display',
            'receiving_user',
            'signed_by_outgoing', 'signed_by_outgoing_at',
            'signed_by_incoming', 'signed_by_incoming_at',
            'completed_at', 'notes', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display',
            'signed_by_outgoing', 'signed_by_outgoing_at',
            'signed_by_incoming', 'signed_by_incoming_at',
            'completed_at', 'items',
            'created_at', 'updated_at',
        ]


class CompleteHandoverInputSerializer(serializers.Serializer):
    signed_by_outgoing = serializers.IntegerField()
    signed_by_incoming = serializers.IntegerField()


class DeliverItemInputSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class SystemsOffboardingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SystemsOffboarding
        fields = [
            'id', 'tenant', 'termination',
            'status', 'status_display',
            'checks', 'notes',
            'completed_at', 'completed_by',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display',
            'completed_at', 'completed_by',
            'created_at', 'updated_at',
        ]


class CompleteSystemsOffboardingInputSerializer(serializers.Serializer):
    checks = serializers.DictField(child=serializers.BooleanField())
    notes = serializers.CharField(required=False, allow_blank=True, default='')


# ---------------------------- ViewSets ----------------------------

class ExitInterviewViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = ExitInterview.objects.select_related('termination', 'interviewer')
    serializer_class = ExitInterviewSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'sentiment', 'termination']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        interview = self.get_object()
        input_serializer = SubmitExitInterviewInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            exit_flow_service.mark_interview_done(
                interview,
                answers=input_serializer.validated_data['answers'],
                sentiment=input_serializer.validated_data['sentiment'],
                comments=input_serializer.validated_data.get('comments', ''),
                interviewer=request.user,
                interview_date=input_serializer.validated_data.get('interview_date'),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=ExitInterviewSerializer(interview).data,
            message='Entrevista registrada',
        )


class HandoverChecklistViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = HandoverChecklist.objects.select_related(
        'termination', 'receiving_user',
        'signed_by_outgoing', 'signed_by_incoming',
    ).prefetch_related('items')
    serializer_class = HandoverChecklistSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'termination']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        checklist = self.get_object()
        input_serializer = CompleteHandoverInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            signed_out = User.objects.get(pk=input_serializer.validated_data['signed_by_outgoing'])
            signed_in = User.objects.get(pk=input_serializer.validated_data['signed_by_incoming'])
        except User.DoesNotExist:
            return APIResponse.error(
                message='User not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            exit_flow_service.complete_handover(
                checklist,
                signed_by_outgoing=signed_out,
                signed_by_incoming=signed_in,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=HandoverChecklistSerializer(checklist).data,
            message='Entrega completada',
        )


class HandoverItemViewSet(viewsets.ModelViewSet):
    queryset = HandoverItem.objects.select_related('checklist', 'delivered_by')
    serializer_class = HandoverItemSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['checklist', 'status', 'kind']
    ordering = ['order', 'created_at']

    @action(detail=True, methods=['post'], url_path='deliver')
    def deliver(self, request, pk=None):
        item = self.get_object()
        input_serializer = DeliverItemInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            exit_flow_service.mark_item_delivered(
                item,
                user=request.user,
                notes=input_serializer.validated_data.get('notes', ''),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=HandoverItemSerializer(item).data,
            message='Item entregado',
        )

    @action(detail=True, methods=['post'], url_path='no-aplica')
    def no_aplica(self, request, pk=None):
        item = self.get_object()
        input_serializer = DeliverItemInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            exit_flow_service.mark_item_no_aplica(
                item, notes=input_serializer.validated_data.get('notes', ''),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=HandoverItemSerializer(item).data,
            message='Item marcado N/A',
        )


class SystemsOffboardingViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = SystemsOffboarding.objects.select_related('termination', 'completed_by')
    serializer_class = SystemsOffboardingSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'termination']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        offboarding = self.get_object()
        input_serializer = CompleteSystemsOffboardingInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            exit_flow_service.complete_systems_offboarding(
                offboarding,
                checks=input_serializer.validated_data['checks'],
                user=request.user,
                notes=input_serializer.validated_data.get('notes', ''),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=SystemsOffboardingSerializer(offboarding).data,
            message='Offboarding de sistemas completado',
        )


class ScaffoldExitFlowInputSerializer(serializers.Serializer):
    termination = serializers.UUIDField()


class ExitFlowScaffoldView(viewsets.ViewSet):
    """One-off endpoint to scaffold ExitInterview + HandoverChecklist + SystemsOffboarding."""
    permission_classes = [RRHHPermission]

    def create(self, request):
        input_serializer = ScaffoldExitFlowInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            termination = Termination.objects.get(
                pk=input_serializer.validated_data['termination'],
            )
        except Termination.DoesNotExist:
            return APIResponse.error(
                message='Termination not found',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        out = exit_flow_service.scaffold_exit_flow(
            termination, user=request.user if request.user.is_authenticated else None,
        )
        return APIResponse.success(
            data={
                'interview': ExitInterviewSerializer(out['interview']).data,
                'checklist': HandoverChecklistSerializer(out['checklist']).data,
                'systems_offboarding': SystemsOffboardingSerializer(out['systems_offboarding']).data,
            },
            message='Flujo de salida creado',
            status_code=status.HTTP_201_CREATED,
        )
