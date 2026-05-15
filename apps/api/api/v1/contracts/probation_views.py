"""ViewSet for B.11 ProbationPeriod (Module 03.4)."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.contracts.models import ProbationPeriod
from apps.contracts.services import probation_service
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin

from .serializers import (
    EvaluateProbationInputSerializer,
    NotRenewInputSerializer,
    ProbationPeriodSerializer,
)


class ProbationPeriodViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Período de prueba per Module 03.4 — tenant-scoped, HR-only."""
    queryset = ProbationPeriod.objects.select_related(
        'contract', 'evaluator', 'decided_by',
    )
    serializer_class = ProbationPeriodSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'regimen', 'contract']
    ordering_fields = ['end_date', 'start_date', 'created_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        period = self.get_object()
        try:
            period.mark_in_progress()
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=ProbationPeriodSerializer(period).data,
            message='Período en progreso',
        )

    @action(detail=True, methods=['post'], url_path='evaluate')
    def evaluate(self, request, pk=None):
        period = self.get_object()
        input_serializer = EvaluateProbationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            period.mark_evaluated(
                score=input_serializer.validated_data['score'],
                evaluator=request.user,
                competencies=input_serializer.validated_data.get('competencies') or {},
                comments=input_serializer.validated_data.get('comments', ''),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=ProbationPeriodSerializer(period).data,
            message='Período evaluado',
        )

    @action(detail=True, methods=['post'], url_path='ratify')
    def ratify(self, request, pk=None):
        period = self.get_object()
        try:
            period.mark_ratified(user=request.user)
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=ProbationPeriodSerializer(period).data,
            message='Trabajador ratificado',
        )

    @action(detail=True, methods=['post'], url_path='not-renew')
    def not_renew(self, request, pk=None):
        period = self.get_object()
        input_serializer = NotRenewInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            period.mark_not_renewed(
                user=request.user,
                reason=input_serializer.validated_data['reason'],
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=ProbationPeriodSerializer(period).data,
            message='Trabajador no renovado',
        )

    @action(detail=False, methods=['get'], url_path='alertas')
    def alertas(self, request):
        tenant = getattr(request, 'tenant', None)
        rows_30d = probation_service.list_alertas_30d(tenant=tenant)
        rows_15d = probation_service.list_alertas_15d(tenant=tenant)
        return APIResponse.success(
            data={
                'within_30_days': ProbationPeriodSerializer(rows_30d, many=True).data,
                'within_15_days': ProbationPeriodSerializer(rows_15d, many=True).data,
            },
            message=f'{len(rows_30d)} en 30d / {len(rows_15d)} en 15d',
        )
