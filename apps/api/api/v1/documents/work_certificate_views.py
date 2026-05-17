"""ViewSet for B.14 WorkCertificate (Module 03.7 Art. 45 LPCL)."""
from django.http import FileResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework import serializers

from api.v1.rrhh.permissions import RRHHPermission
from apps.contracts.models import Termination
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.documents.models import WorkCertificate
from apps.documents.services import work_certificate_service


class WorkCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCertificate
        fields = [
            'id', 'tenant', 'termination', 'employee', 'contract',
            'numero_constancia', 'fecha_emision',
            'cargo_snapshot', 'area_snapshot',
            'fecha_inicio_snapshot', 'fecha_fin_snapshot',
            'sueldo_snapshot', 'motivo_cese_textual',
            'signed_by', 'pdf_file', 'digital_document',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'cargo_snapshot', 'area_snapshot',
            'fecha_inicio_snapshot', 'fecha_fin_snapshot',
            'sueldo_snapshot', 'motivo_cese_textual',
            'pdf_file', 'digital_document',
            'created_at', 'updated_at',
        ]


class GenerateCertificateInputSerializer(serializers.Serializer):
    termination = serializers.UUIDField()


class WorkCertificateViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = WorkCertificate.objects.select_related(
        'termination', 'employee', 'contract', 'signed_by',
    )
    serializer_class = WorkCertificateSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['employee', 'termination']
    search_fields = ['numero_constancia', 'cargo_snapshot']
    ordering_fields = ['fecha_emision', 'created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        input_serializer = GenerateCertificateInputSerializer(data=request.data)
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
        try:
            cert = work_certificate_service.generate_certificate(
                termination,
                user=request.user if request.user.is_authenticated else None,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=WorkCertificateSerializer(cert).data,
            message='Constancia generada',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        cert = self.get_object()
        if not cert.pdf_file:
            return APIResponse.error(
                message='Certificate has no PDF attached',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            response = FileResponse(
                cert.pdf_file.open('rb'),
                content_type='application/pdf',
            )
            response['Content-Disposition'] = (
                f'attachment; filename="{cert.numero_constancia}.pdf"'
            )
            return response
        except Exception as exc:  # pragma: no cover — IO edge
            return APIResponse.error(
                message=f'Failed to open PDF: {exc}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
