"""ViewSets for B.13 Displacement + LocationHistory."""
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.organization.models import (
    Displacement,
    DisplacementExtension,
    LocationHistory,
)
from apps.organization.services import displacement_service

from .displacement_serializers import (
    CancelDisplacementInputSerializer,
    DisplacementExtensionSerializer,
    DisplacementSerializer,
    ExtendDisplacementInputSerializer,
    LocationHistorySerializer,
)


class DisplacementViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Displacement per Module 03.6 — tenant-scoped, HR-only."""
    queryset = Displacement.objects.select_related(
        'employee', 'origen_department', 'destino_department',
        'origen_position', 'destino_position',
        'requested_by', 'approved_by_supervisor',
        'approved_by_hr', 'approved_by_titular',
    ).prefetch_related('extensions')
    serializer_class = DisplacementSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'kind', 'employee']
    ordering_fields = ['created_at', 'start_date']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        user = self.request.user if self.request.user.is_authenticated else None
        if tenant is not None:
            serializer.save(tenant=tenant, requested_by=user)
        else:
            serializer.save(requested_by=user)

    def _act(self, request, fn_name, **kwargs):
        period = self.get_object()
        try:
            getattr(period, fn_name)(**kwargs)
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=DisplacementSerializer(period).data,
            message=f'{fn_name} ejecutado',
        )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        return self._act(request, 'submit')

    @action(detail=True, methods=['post'], url_path='approve-supervisor')
    def approve_supervisor(self, request, pk=None):
        return self._act(request, 'approve_supervisor', user=request.user)

    @action(detail=True, methods=['post'], url_path='approve-hr')
    def approve_hr(self, request, pk=None):
        return self._act(request, 'approve_hr', user=request.user)

    @action(detail=True, methods=['post'], url_path='approve-titular')
    def approve_titular(self, request, pk=None):
        return self._act(request, 'approve_titular', user=request.user)

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        return self._act(request, 'activate')

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        return self._act(request, 'complete')

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        input_serializer = CancelDisplacementInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        return self._act(request, 'cancel', reason=input_serializer.validated_data['reason'])

    @action(detail=True, methods=['post'], url_path='extend')
    def extend(self, request, pk=None):
        input_serializer = ExtendDisplacementInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        d = self.get_object()
        try:
            ext = displacement_service.extend_displacement(
                displacement_id=d.id,
                new_end_date=input_serializer.validated_data['new_end_date'],
                reason=input_serializer.validated_data['reason'],
                granted_by=request.user,
                resolution_number=input_serializer.validated_data.get('resolution_number', ''),
            )
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=DisplacementExtensionSerializer(ext).data,
            message='Prórroga registrada',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='resolution-pdf')
    def resolution_pdf(self, request, pk=None):
        d = self.get_object()
        pdf_bytes = displacement_service.render_resolution_pdf(d.id)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="desplazamiento_{d.employee_id}_{d.id}.pdf"'
        )
        return response


class DisplacementExtensionViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of prórrogas registered via /displacements/<id>/extend/."""
    queryset = DisplacementExtension.objects.select_related('displacement', 'granted_by')
    serializer_class = DisplacementExtensionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['displacement']
    ordering = ['-granted_at']


class LocationHistoryViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Historial de ubicaciones — backlog #101."""
    queryset = LocationHistory.objects.select_related(
        'empleado', 'area_origen', 'area_destino',
    )
    serializer_class = LocationHistorySerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['empleado', 'tipo_movimiento']
    ordering_fields = ['fecha_inicio']
    ordering = ['-fecha_inicio']
