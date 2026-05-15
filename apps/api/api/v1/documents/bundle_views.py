"""ViewSets for B.10 documents — HiringDocumentBundle + HiringBundleItem."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.documents.models import (
    DigitalDocument,
    DocumentSignature,
    HiringBundleItem,
    HiringDocumentBundle,
)
from apps.documents.services import bundle_service

from .serializers_b10 import (
    AttachAcuseInputSerializer,
    AttachDocumentInputSerializer,
    HiringBundleItemSerializer,
    HiringDocumentBundleSerializer,
)


class HiringDocumentBundleViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Hiring document bundles — tenant-scoped, HR-only."""
    queryset = HiringDocumentBundle.objects.select_related(
        'employee', 'contract', 'created_by',
    ).prefetch_related('items')
    serializer_class = HiringDocumentBundleSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['title']
    filterset_fields = ['status', 'employee', 'contract']
    ordering_fields = ['created_at', 'sent_at', 'acknowledged_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        """Custom create — uses build_bundle service so items scaffold."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.validated_data['employee']
        contract = serializer.validated_data.get('contract')
        title = serializer.validated_data.get('title') or ''
        item_kinds = serializer.validated_data.get('item_kinds') or None
        bundle = bundle_service.build_bundle(
            employee=employee,
            contract=contract,
            tenant=getattr(request, 'tenant', None),
            item_kinds=item_kinds,
            created_by=request.user if request.user.is_authenticated else None,
            title=title,
        )
        return APIResponse.success(
            data=HiringDocumentBundleSerializer(bundle).data,
            message='Bundle creado',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='send')
    def send(self, request, pk=None):
        bundle = self.get_object()
        try:
            out = bundle_service.mark_sent(bundle_id=bundle.id)
        except Exception as exc:
            return APIResponse.error(
                message=str(exc), status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=HiringDocumentBundleSerializer(out).data,
            message='Bundle enviado',
        )

    @action(detail=True, methods=['post'], url_path='acknowledge')
    def acknowledge(self, request, pk=None):
        bundle = self.get_object()
        out = bundle_service.mark_acknowledged_if_complete(bundle_id=bundle.id)
        if out.status != 'acknowledged':
            return APIResponse.error(
                message='Aún faltan firmas requeridas',
                errors=[f'Bundle aún en status={out.status}'],
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=HiringDocumentBundleSerializer(out).data,
            message='Bundle acusado',
        )


class HiringBundleItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Hiring bundle items — read + attach actions only (no plain CRUD)."""
    queryset = HiringBundleItem.objects.select_related(
        'bundle', 'document', 'signature',
    )
    serializer_class = HiringBundleItemSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['bundle', 'kind', 'required']
    ordering_fields = ['order']
    ordering = ['order', 'kind']

    @action(detail=True, methods=['post'], url_path='attach-document')
    def attach_document(self, request, pk=None):
        item = self.get_object()
        input_serializer = AttachDocumentInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            document = DigitalDocument.objects.get(
                pk=input_serializer.validated_data['document_id'],
            )
        except DigitalDocument.DoesNotExist:
            return APIResponse.error(
                message='Documento no encontrado',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        out = bundle_service.attach_document(
            bundle_item_id=item.id, document=document,
        )
        return APIResponse.success(
            data=HiringBundleItemSerializer(out).data,
            message='Documento adjunto',
        )

    @action(detail=True, methods=['post'], url_path='attach-acuse')
    def attach_acuse(self, request, pk=None):
        item = self.get_object()
        input_serializer = AttachAcuseInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            signature = DocumentSignature.objects.get(
                pk=input_serializer.validated_data['signature_id'],
            )
        except DocumentSignature.DoesNotExist:
            return APIResponse.error(
                message='Firma no encontrada',
                status_code=status.HTTP_404_NOT_FOUND,
            )
        out = bundle_service.attach_acuse(
            bundle_item_id=item.id, signature=signature,
        )
        return APIResponse.success(
            data=HiringBundleItemSerializer(out).data,
            message='Acuse adjunto',
        )
