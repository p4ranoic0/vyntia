"""Compensation CRUD viewset (D.3)."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.payroll.models import Compensation

from .compensation_serializers import CompensationSerializer


class CompensationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """HR-only CRUD over per-employee compensation snapshots."""

    queryset = Compensation.objects.select_related("employee").all()
    serializer_class = CompensationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["employee", "source", "valid_from"]
    ordering_fields = ["valid_from", "created_at"]
    ordering = ["-valid_from"]

    def perform_create(self, serializer):
        tenant = getattr(self.request, "tenant", None)
        kwargs = {"created_by": self.request.user}
        if tenant is not None:
            kwargs["tenant"] = tenant
        else:
            # Outside tenant middleware (e.g. tests, admin panel): derive tenant
            # from the employee's tenant so the NOT NULL constraint is satisfied.
            employee = serializer.validated_data.get("employee")
            if employee is not None and getattr(employee, "tenant", None) is not None:
                kwargs["tenant"] = employee.tenant
        serializer.save(**kwargs)

    @action(detail=False, methods=["get"], url_path="history/(?P<employee_id>[^/.]+)")
    def history(self, request, employee_id=None):
        """All compensation versions for one employee, newest first (BACKLOG #42)."""
        qs = self._filter_by_tenant(
            Compensation.objects.filter(employee_id=employee_id).order_by("-valid_from")
        )
        return Response(self.get_serializer(qs, many=True).data)
