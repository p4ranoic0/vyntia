"""ViewSets for B.10 documents — DocumentSignature."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.documents.models import DocumentSignature
from apps.documents.services import signature_service

from .serializers_b10 import (
    CaptureSignatureInputSerializer,
    DocumentSignatureSerializer,
    RejectSignatureInputSerializer,
)


class DocumentSignatureViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """E-signature records — tenant-scoped, HR-only."""
    queryset = DocumentSignature.objects.select_related('document', 'signer_user')
    serializer_class = DocumentSignatureSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['signer_name', 'signer_doc_number', 'signer_email']
    filterset_fields = ['status', 'kind', 'document']
    ordering_fields = ['requested_at', 'signed_at']
    ordering = ['-requested_at']

    @action(detail=True, methods=['post'], url_path='capture')
    def capture(self, request, pk=None):
        signature = self.get_object()
        input_serializer = CaptureSignatureInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            out = signature_service.capture_signature(
                signature_id=signature.id,
                signer_ip=request.META.get('REMOTE_ADDR', '') or '',
                signer_user_agent=request.META.get('HTTP_USER_AGENT', '')[:400],
                **input_serializer.validated_data,
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=DocumentSignatureSerializer(out).data,
            message='Firma capturada',
        )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        signature = self.get_object()
        input_serializer = RejectSignatureInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            out = signature_service.reject_signature(
                signature_id=signature.id,
                reason=input_serializer.validated_data['reason'],
            )
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=DocumentSignatureSerializer(out).data,
            message='Firma rechazada',
        )

    @action(detail=False, methods=['post'], url_path='expire-overdue')
    def expire_overdue(self, request):
        count = signature_service.expire_overdue_signatures()
        return APIResponse.success(
            data={'expired_count': count},
            message=f'{count} firmas expiradas',
        )
