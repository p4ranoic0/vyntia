"""ViewSets for B.6 Position + Plaza + reference data API."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.organization.models import (
    CIUOCode,
    OccupationalCategory,
    Plaza,
    Position,
    PositionFunction,
    PositionProfile,
    PositionRequirement,
    PositionRiskProfile,
)

from .serializers import (
    CIUOCodeSerializer,
    OccupationalCategorySerializer,
    PlazaOccupySerializer,
    PlazaSerializer,
    PositionFunctionSerializer,
    PositionNewVersionSerializer,
    PositionProfileSerializer,
    PositionRequirementSerializer,
    PositionRiskProfileSerializer,
    PositionSerializer,
)


class OccupationalCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """SUNAT Tabla 10 — system-wide reference data (read-only)."""
    queryset = OccupationalCategory.objects.filter(is_active=True).order_by('code')
    serializer_class = OccupationalCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # ~3 rows, no pagination needed


class CIUOCodeViewSet(viewsets.ReadOnlyModelViewSet):
    """CIUO-08 (SUNAT Tabla 9) — system-wide reference data (read-only)."""
    queryset = CIUOCode.objects.filter(is_active=True).order_by('code')
    serializer_class = CIUOCodeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['code', 'name', 'big_group']
    filterset_fields = ['big_group']


class PositionViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Position catalog — tenant-scoped, versioned per ADR-B.7."""
    queryset = Position.objects.select_related(
        'department', 'occupational_category', 'ciuo_code', 'reports_to'
    )
    serializer_class = PositionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['code', 'name', 'description']
    filterset_fields = ['department', 'is_current', 'is_active', 'occupational_category']
    ordering_fields = ['code', 'version', 'effective_date', 'created_at']
    ordering = ['code', '-version']

    def get_queryset(self):
        qs = super().get_queryset()
        # Default to current versions only — opt-in to history via ?is_current=false
        if self.action == 'list' and 'is_current' not in self.request.query_params:
            qs = qs.filter(is_current=True)
        return qs

    @action(detail=True, methods=['post'], url_path='new-version')
    def new_version(self, request, pk=None):
        """Create a new version of this Position per ADR-B.7."""
        from apps.organization.models import (
            CIUOCode as _CIUOCode,
            Department as _Department,
            OccupationalCategory as _OccupationalCategory,
        )

        position = self.get_object()
        in_serializer = PositionNewVersionSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        data = in_serializer.validated_data

        # Resolve UUID inputs to model instances
        changes = {}
        if 'name' in data and data['name'] is not None:
            changes['name'] = data['name']
        if 'effective_date' in data and data['effective_date'] is not None:
            changes['effective_date'] = data['effective_date']
        if 'department' in data and data['department'] is not None:
            changes['department'] = _Department.objects.get(pk=data['department'])
        if 'occupational_category' in data and data['occupational_category'] is not None:
            changes['occupational_category'] = _OccupationalCategory.objects.get(
                pk=data['occupational_category']
            )
        if 'ciuo_code' in data and data['ciuo_code'] is not None:
            changes['ciuo_code'] = _CIUOCode.objects.get(pk=data['ciuo_code'])
        if 'reports_to' in data and data['reports_to'] is not None:
            changes['reports_to'] = Position.objects.get(pk=data['reports_to'])

        try:
            new_position = position.create_new_version(
                created_by=request.user,
                **changes,
            )
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)

        out = PositionSerializer(new_position)
        return APIResponse.success(
            data=out.data,
            message=f"Nueva versión {new_position.version} creada",
            status_code=status.HTTP_201_CREATED,
        )


class PositionProfileViewSet(viewsets.ModelViewSet):
    """Position profile (1-to-1 with Position)."""
    queryset = PositionProfile.objects.select_related('position')
    serializer_class = PositionProfileSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position']


class PositionFunctionViewSet(viewsets.ModelViewSet):
    """Position function list (ordered)."""
    queryset = PositionFunction.objects.select_related('position')
    serializer_class = PositionFunctionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['position', 'is_primary']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']


class PositionRequirementViewSet(viewsets.ModelViewSet):
    """Position requirements (education, experience, language, certification)."""
    queryset = PositionRequirement.objects.select_related('position')
    serializer_class = PositionRequirementSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'kind', 'is_required']


class PositionRiskProfileViewSet(viewsets.ModelViewSet):
    """SST risk profile (1-to-1 with Position). Stub model per Task 7."""
    queryset = PositionRiskProfile.objects.select_related('position')
    serializer_class = PositionRiskProfileSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'overall_level', 'requires_medical_exam', 'requires_iperc']


class PlazaViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Plaza catalog — assignment workflow (vacante/ocupada/congelada/eliminada)."""
    queryset = Plaza.objects.select_related('position', 'current_employee')
    serializer_class = PlazaSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['code', 'notes']
    filterset_fields = ['status', 'position']
    ordering_fields = ['code', 'status', 'created_at']
    ordering = ['code']

    @action(detail=True, methods=['post'], url_path='occupy')
    def occupy(self, request, pk=None):
        from apps.employees.models import Employee
        plaza = self.get_object()
        in_serializer = PlazaOccupySerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        try:
            employee = Employee.objects.get(pk=in_serializer.validated_data['employee'])
        except Employee.DoesNotExist:
            return APIResponse.error(
                message="Empleado no encontrado",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        try:
            plaza.occupy(employee)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PlazaSerializer(plaza).data,
            message="Plaza ocupada",
        )

    @action(detail=True, methods=['post'], url_path='vacate')
    def vacate(self, request, pk=None):
        plaza = self.get_object()
        try:
            plaza.vacate()
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PlazaSerializer(plaza).data,
            message="Plaza vacada",
        )

    @action(detail=True, methods=['post'], url_path='freeze')
    def freeze(self, request, pk=None):
        plaza = self.get_object()
        try:
            plaza.freeze()
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PlazaSerializer(plaza).data,
            message="Plaza congelada",
        )
