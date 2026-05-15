"""ViewSets for B.12 legajo content — WorkExperience + SwornDeclaration + JobHistory."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.employees.models import JobHistory, SwornDeclaration, WorkExperience

from .serializers_b12 import (
    JobHistorySerializer,
    SwornDeclarationSerializer,
    WorkExperienceSerializer,
)


class WorkExperienceViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = WorkExperience.objects.select_related('employee')
    serializer_class = WorkExperienceSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'sector', 'is_current']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']


class SwornDeclarationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = SwornDeclaration.objects.select_related('employee', 'document')
    serializer_class = SwornDeclarationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'kind', 'is_active']
    ordering_fields = ['declared_at']
    ordering = ['-declared_at']


class JobHistoryViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = JobHistory.objects.select_related('employee', 'position')
    serializer_class = JobHistorySerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee', 'motive', 'position']
    ordering_fields = ['start_date']
    ordering = ['-start_date']
