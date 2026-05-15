"""ViewSets for B.10 contracts — TRegistroDeclaration."""
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.contracts.models import TRegistroDeclaration
from apps.contracts.services import tregistro_service
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin

from .serializers import (
    MarkAcceptedInputSerializer,
    MarkRejectedInputSerializer,
    SubmitDeclarationInputSerializer,
    TRegistroDeclarationSerializer,
)


class TRegistroDeclarationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """SUNAT T-Registro declarations — tenant-scoped, HR-only."""
    queryset = TRegistroDeclaration.objects.select_related(
        'contract', 'employee', 'submitted_by',
    )
    serializer_class = TRegistroDeclarationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = [
        'worker_doc_number', 'worker_apellido_paterno', 'worker_nombres',
        'sunat_reference', 'employer_ruc',
    ]
    filterset_fields = ['status', 'declaration_type', 'contract', 'employee']
    ordering_fields = ['created_at', 'submitted_at']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'], url_path='generate-anexo3')
    def generate_anexo3(self, request, pk=None):
        declaration = self.get_object()
        declaration.anexo3_txt = tregistro_service.build_anexo3_txt(declaration)
        declaration.save(update_fields=['anexo3_txt', 'updated_at'])
        return APIResponse.success(
            data=TRegistroDeclarationSerializer(declaration).data,
            message='Anexo 3 generado',
        )

    @action(detail=True, methods=['post'], url_path='validate-pvs')
    def validate_pvs(self, request, pk=None):
        declaration = self.get_object()
        out = tregistro_service.validate_and_persist(declaration.id)
        return APIResponse.success(
            data=TRegistroDeclarationSerializer(out).data,
            message=(
                'Validación PVS limpia' if not out.pvs_errors
                else f'{len(out.pvs_errors)} errores PVS'
            ),
        )

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        declaration = self.get_object()
        input_serializer = SubmitDeclarationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            out = tregistro_service.submit_declaration(
                declaration.id,
                user=request.user,
                reference=input_serializer.validated_data.get('reference', ''),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        if out.pvs_errors:
            return APIResponse.error(
                message='No se pudo enviar; existen errores PVS',
                errors=out.pvs_errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TRegistroDeclarationSerializer(out).data,
            message='Declaración enviada',
        )

    @action(detail=True, methods=['post'], url_path='mark-accepted')
    def mark_accepted(self, request, pk=None):
        declaration = self.get_object()
        input_serializer = MarkAcceptedInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            declaration.mark_accepted(
                reference=input_serializer.validated_data.get('reference', ''),
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TRegistroDeclarationSerializer(declaration).data,
            message='Declaración aceptada por SUNAT',
        )

    @action(detail=True, methods=['post'], url_path='mark-rejected')
    def mark_rejected(self, request, pk=None):
        declaration = self.get_object()
        input_serializer = MarkRejectedInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            declaration.mark_rejected(
                reason=input_serializer.validated_data['reason'],
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=TRegistroDeclarationSerializer(declaration).data,
            message='Declaración rechazada',
        )

    @action(detail=True, methods=['get'], url_path='anexo3-txt')
    def anexo3_txt(self, request, pk=None):
        declaration = self.get_object()
        if not declaration.anexo3_txt:
            declaration.anexo3_txt = tregistro_service.build_anexo3_txt(declaration)
            declaration.save(update_fields=['anexo3_txt', 'updated_at'])
        filename = (
            f'tregistro_{declaration.employer_ruc}_'
            f'{declaration.declaration_type}_'
            f'{declaration.created_at.strftime("%Y%m%d")}.txt'
        )
        response = HttpResponse(
            declaration.anexo3_txt, content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
