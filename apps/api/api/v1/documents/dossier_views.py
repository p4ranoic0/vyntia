"""ViewSets for B.12 documents — DigitalDossier + DossierSection + DocumentAccessLog."""
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.documents.models import (
    DigitalDossier,
    DocumentAccessLog,
    DossierSection,
)
from apps.documents.services import dossier_service
from apps.employees.models import Employee

from .serializers_b12 import (
    DigitalDossierSerializer,
    DocumentAccessLogSerializer,
    DossierSectionSerializer,
)


class DigitalDossierViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Legajo digital per Module 03.5 — tenant-scoped, HR-only."""
    queryset = DigitalDossier.objects.select_related('employee').prefetch_related('sections')
    serializer_class = DigitalDossierSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'is_closed']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get('employee')
        if not employee_id:
            return APIResponse.error(
                message='employee es requerido',
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return APIResponse.error(
                message='Empleado no encontrado',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        dossier = dossier_service.build_dossier_for_employee(
            employee=employee,
            tenant=getattr(request, 'tenant', None),
        )
        return APIResponse.success(
            data=DigitalDossierSerializer(dossier).data,
            message='Legajo creado',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='build')
    def build(self, request, pk=None):
        """Idempotent build — seeds any missing sections."""
        dossier = self.get_object()
        dossier_service.build_dossier_for_employee(employee=dossier.employee)
        dossier.refresh_from_db()
        return APIResponse.success(
            data=DigitalDossierSerializer(dossier).data,
            message='Legajo provisionado',
        )

    @action(detail=True, methods=['get'], url_path='consolidated-pdf')
    def consolidated_pdf(self, request, pk=None):
        dossier = self.get_object()
        pdf_bytes = dossier_service.render_consolidated_pdf(dossier.id)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="legajo_{dossier.employee_id}.pdf"'
        )
        return response


class DossierSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DossierSection.objects.select_related('dossier')
    serializer_class = DossierSectionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dossier', 'kind']
    ordering_fields = ['order']
    ordering = ['order', 'kind']


class DocumentAccessLogViewSet(TenantAwareViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only audit trail — backlog #121."""
    queryset = DocumentAccessLog.objects.select_related('document', 'user')
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'user', 'action']
    ordering_fields = ['occurred_at']
    ordering = ['-occurred_at']
