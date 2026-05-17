"""ViewSets for B.14 Termination + SeveranceSettlement (Module 03.7)."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.contracts.models import (
    Contract,
    SeveranceSettlement,
    Termination,
    TRegistroDeclaration,
)
from apps.contracts.services import severance_service, termination_service
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin

from .termination_serializers import (
    CancelTerminationInputSerializer,
    ComputeSettlementInputSerializer,
    InitiateTerminationInputSerializer,
    MarkBajaTRegistroInputSerializer,
    MarkSettlementPaidInputSerializer,
    SeveranceSettlementSerializer,
    TerminationSerializer,
)


class TerminationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = Termination.objects.select_related(
        'contract', 'employee', 'baja_t_registro',
        'initiated_by', 'completed_by', 'liquidated_by',
    )
    serializer_class = TerminationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'regimen', 'causal', 'contract', 'employee']
    search_fields = ['contract__numero_contrato', 'motivo']
    ordering_fields = ['created_at', 'fecha_cese', 'completed_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        """Use termination_service.initiate_termination to enforce invariants."""
        input_serializer = InitiateTerminationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            contract = Contract.objects.get(pk=input_serializer.validated_data['contract'])
        except Contract.DoesNotExist:
            return APIResponse.error(
                message='Contract not found', status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            termination = termination_service.initiate_termination(
                contract=contract,
                causal=input_serializer.validated_data['causal'],
                regimen=input_serializer.validated_data.get('regimen', '728'),
                fecha_cese=input_serializer.validated_data['fecha_cese'],
                last_day_worked=input_serializer.validated_data.get('last_day_worked'),
                motivo=input_serializer.validated_data.get('motivo', ''),
                user=request.user if request.user.is_authenticated else None,
                tenant=getattr(request, 'tenant', None),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TerminationSerializer(termination).data,
            message='Cese iniciado',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        termination = self.get_object()
        try:
            termination_service.complete_termination(termination, user=request.user)
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TerminationSerializer(termination).data,
            message='Cese completado',
        )

    @action(detail=True, methods=['post'], url_path='liquidate')
    def liquidate(self, request, pk=None):
        termination = self.get_object()
        try:
            termination_service.liquidate(termination, user=request.user)
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TerminationSerializer(termination).data,
            message='Liquidación cerrada',
        )

    @action(detail=True, methods=['post'], url_path='mark-baja-tregistro-done')
    def mark_baja_tregistro_done(self, request, pk=None):
        termination = self.get_object()
        input_serializer = MarkBajaTRegistroInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            declaration = TRegistroDeclaration.objects.get(
                pk=input_serializer.validated_data['declaration'],
            )
        except TRegistroDeclaration.DoesNotExist:
            return APIResponse.error(
                message='Declaration not found', status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            termination_service.mark_baja_tregistro_done(
                termination, declaration=declaration,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TerminationSerializer(termination).data,
            message='Baja T-Registro registrada',
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        termination = self.get_object()
        input_serializer = CancelTerminationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            termination_service.cancel_termination(
                termination,
                reason=input_serializer.validated_data['reason'],
                user=request.user,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TerminationSerializer(termination).data,
            message='Cese cancelado',
        )

    @action(detail=False, methods=['get'], url_path='alertas-48h-sla')
    def alertas_48h_sla(self, request):
        tenant = getattr(request, 'tenant', None)
        rows = termination_service.list_pending_baja_tregistro_48h(tenant=tenant)
        return APIResponse.success(
            data=TerminationSerializer(rows, many=True).data,
            message=f'{len(rows)} cese(s) con SLA vencido',
        )


class SeveranceSettlementViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = SeveranceSettlement.objects.select_related(
        'termination', 'termination__employee', 'computed_by', 'paid_by',
    ).prefetch_related('lines')
    serializer_class = SeveranceSettlementSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'termination']
    ordering_fields = ['created_at', 'paid_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='compute')
    def compute(self, request, pk=None):
        settlement = self.get_object()
        input_serializer = ComputeSettlementInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            settlement = severance_service.compute_settlement(
                settlement.termination,
                user=request.user,
                dias_acumulados_no_gozados=input_serializer.validated_data.get(
                    'dias_acumulados_no_gozados',
                ),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=SeveranceSettlementSerializer(settlement).data,
            message='Liquidación recomputada',
        )

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        settlement = self.get_object()
        input_serializer = MarkSettlementPaidInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            severance_service.mark_paid(
                settlement,
                paid_total=input_serializer.validated_data['paid_total'],
                paid_at=input_serializer.validated_data.get('paid_at'),
                user=request.user,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=SeveranceSettlementSerializer(settlement).data,
            message='Pago registrado',
        )
