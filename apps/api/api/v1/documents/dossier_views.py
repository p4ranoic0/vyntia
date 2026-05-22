"""ViewSets for B.12 documents — DigitalDossier + DossierSection + DocumentAccessLog."""
from django.db.models import Max
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
from apps.documents.services import access_service, dossier_service
from apps.employees.models import Employee


def _client_ip(request):
    """Best-effort client IP extraction for audit logs."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '') or ''


def _user_agent(request):
    return (request.META.get('HTTP_USER_AGENT') or '')[:400]

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
        """Generate and download the dossier consolidated PDF.

        PL gate (#118): the dossier may contain sections with permission_level
        up to 9 (médicos, accidentes). The user MUST have an effective level
        >= MAX(section.permission_level). Otherwise → 403 + 'denied' audit log.
        Audit log (#121): every attempt (granted or denied) is recorded with
        client IP, user-agent, and timestamp.
        """
        dossier = self.get_object()
        user = request.user
        ip = _client_ip(request)
        ua = _user_agent(request)

        # Effective PL required = highest PL across the dossier's sections.
        max_pl = (
            dossier.sections.aggregate(m=Max('permission_level')).get('m') or 0
        )
        user_level = access_service.user_permission_level(user)

        if user_level < int(max_pl):
            # Audit denied attempt against the FIRST section that gates it
            # (DossierSection is the closest "document-like" entity we have here).
            denied_section = (
                dossier.sections.order_by('-permission_level').first()
            )
            if denied_section is not None:
                DocumentAccessLog.objects.create(
                    tenant=getattr(dossier, 'tenant', None),
                    document=None,  # consolidated PDF, no single DigitalDocument
                    user=user if getattr(user, 'is_authenticated', False) else None,
                    action='denied',
                    ip=ip or None,
                    user_agent=ua,
                    required_permission_level=int(max_pl),
                    user_permission_level=user_level,
                    notes=f'consolidated_pdf:dossier={dossier.pk}:section={denied_section.kind}',
                )
            return APIResponse.error(
                message=(
                    'No tiene permisos suficientes para descargar este legajo. '
                    f'Nivel requerido: {max_pl}. Su nivel: {user_level}.'
                ),
                status_code=status.HTTP_403_FORBIDDEN,
            )

        pdf_bytes = dossier_service.render_consolidated_pdf(dossier.id)

        # Log granted download against the dossier (no document FK — null).
        DocumentAccessLog.objects.create(
            tenant=getattr(dossier, 'tenant', None),
            document=None,
            user=user if getattr(user, 'is_authenticated', False) else None,
            action='download',
            ip=ip or None,
            user_agent=ua,
            required_permission_level=int(max_pl),
            user_permission_level=user_level,
            notes=f'consolidated_pdf:dossier={dossier.pk}',
        )

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="legajo_{dossier.employee_id}.pdf"'
        )
        return response


class DossierSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Sections of a digital dossier — PL-gated per § 6.3 (#118).

    A section's `permission_level` (1-9) is the minimum effective level the
    requester must have. The queryset is filtered so a user with
    `nivel_acceso=personal` (level 3) never sees PL 5+ sections (médicos,
    accidentes). Tenant isolation via dossier.tenant.
    """
    queryset = DossierSection.objects.select_related('dossier')
    serializer_class = DossierSectionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dossier', 'kind']
    ordering_fields = ['order']
    ordering = ['order', 'kind']

    def get_queryset(self):
        """Filter by tenant (via dossier) and by user's permission_level."""
        queryset = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            queryset = queryset.filter(dossier__tenant=tenant)
        user_level = access_service.user_permission_level(self.request.user)
        return queryset.filter(permission_level__lte=user_level)


class DocumentAccessLogViewSet(TenantAwareViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Read-only audit trail — backlog #121."""
    queryset = DocumentAccessLog.objects.select_related('document', 'user')
    serializer_class = DocumentAccessLogSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document', 'user', 'action']
    ordering_fields = ['occurred_at']
    ordering = ['-occurred_at']
