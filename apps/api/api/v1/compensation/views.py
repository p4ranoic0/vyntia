"""ViewSets for B.7 CCF + audit + Excel API."""
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.v1.rrhh.permissions import RRHHPermission
from apps.compensation.models import (
    Category,
    CategoryFactorScore,
    CategoryFunctionTable,
    JobFactor,
    JobSubfactor,
    SalaryBand,
)
from apps.compensation.services import (
    compute_salary_gap_by_category,
    export_template,
    import_ccf,
    recompute_category_total,
    summarize_gap,
)
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin

from .serializers import (
    CategoryFactorScoreSerializer,
    CategoryFunctionTableSerializer,
    CategorySerializer,
    CCFApprovalSerializer,
    CCFExcelImportSerializer,
    JobFactorSerializer,
    JobSubfactorSerializer,
    SalaryBandSerializer,
)


class JobFactorViewSet(viewsets.ReadOnlyModelViewSet):
    """JobFactor reference data — system-wide (no tenant filter)."""
    queryset = JobFactor.objects.filter(is_active=True).order_by('kind')
    serializer_class = JobFactorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


class JobSubfactorViewSet(viewsets.ReadOnlyModelViewSet):
    """JobSubfactor reference data — system-wide."""
    queryset = JobSubfactor.objects.filter(is_active=True).select_related('factor').order_by('factor', 'code')
    serializer_class = JobSubfactorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['factor']


class CategoryFunctionTableViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """CCF — tenant-scoped versioned document."""
    queryset = CategoryFunctionTable.objects.select_related('approved_by', 'created_by').prefetch_related('categories')
    serializer_class = CategoryFunctionTableSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['title', 'description']
    filterset_fields = ['status']
    ordering_fields = ['effective_date', 'version', 'created_at']
    ordering = ['-effective_date', '-version']

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        ccf = self.get_object()
        in_serializer = CCFApprovalSerializer(data=request.data)
        in_serializer.is_valid(raise_exception=True)
        try:
            ccf.approve(
                user=request.user,
                effective_date=in_serializer.validated_data.get('effective_date'),
            )
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=CategoryFunctionTableSerializer(ccf).data,
            message="CCF aprobado",
        )


class CategoryViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Category — tenant-scoped, belongs to a CCF."""
    queryset = Category.objects.select_related('ccf').order_by('ccf', 'code')
    serializer_class = CategorySerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['code', 'name', 'description']
    filterset_fields = ['ccf', 'is_active']
    ordering_fields = ['code', 'total_score', 'created_at']

    @action(detail=True, methods=['post'], url_path='recompute-total')
    def recompute_total(self, request, pk=None):
        category = self.get_object()
        total = recompute_category_total(category)
        return APIResponse.success(
            data={'category_id': str(category.id), 'total_score': str(total)},
            message="Total recomputado",
        )


class CategoryFactorScoreViewSet(viewsets.ModelViewSet):
    """CategoryFactorScore — Category × Subfactor scores."""
    queryset = CategoryFactorScore.objects.select_related(
        'category', 'subfactor', 'subfactor__factor',
    )
    serializer_class = CategoryFactorScoreSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'subfactor']

    def perform_create(self, serializer):
        score = serializer.save()
        recompute_category_total(score.category)

    def perform_update(self, serializer):
        score = serializer.save()
        recompute_category_total(score.category)

    def perform_destroy(self, instance):
        category = instance.category
        instance.delete()
        recompute_category_total(category)


class SalaryBandViewSet(viewsets.ModelViewSet):
    """SalaryBand — 1-to-1 with Category."""
    queryset = SalaryBand.objects.select_related('category')
    serializer_class = SalaryBandSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']


class SalaryGapAuditView(APIView):
    """GET /api/v1/compensation/audit/salary-gap/?ccf_id=<uuid>

    Returns Ley 30709 § 8 audit: brecha % per category × sex with alert
    flag for |brecha| > 5%. Includes summary metrics.
    """
    permission_classes = [RRHHPermission]

    def get(self, request, *args, **kwargs):
        tenant = getattr(request, 'tenant', None)
        ccf_id = request.query_params.get('ccf_id')
        rows = compute_salary_gap_by_category(tenant=tenant, ccf_id=ccf_id)
        summary = summarize_gap(rows)
        return APIResponse.success(
            data={'rows': rows, 'summary': summary},
            message="Audit report",
        )


class CCFExcelTemplateView(APIView):
    """GET /api/v1/compensation/ccf/template-excel/

    Returns the .xlsx template for CCF bulk import.
    """
    permission_classes = [RRHHPermission]

    def get(self, request, *args, **kwargs):
        buf = export_template()
        response = HttpResponse(
            buf.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="ccf_template.xlsx"'
        return response


class CCFExcelImportView(APIView):
    """POST /api/v1/compensation/ccf/import-excel/

    Multipart upload: file=<.xlsx>, ccf_title=<str>. Returns CCFImportResult
    in JSON form (success, ccf_id, counts, row_errors).
    """
    permission_classes = [RRHHPermission]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        serializer = CCFExcelImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = import_ccf(
            file=serializer.validated_data['file'],
            tenant=getattr(request, 'tenant', None),
            ccf_title=serializer.validated_data['ccf_title'],
            user=request.user,
        )
        payload = {
            'success': result.success,
            'ccf_id': result.ccf_id,
            'categories_created': result.categories_created,
            'bands_created': result.bands_created,
            'scores_created': result.scores_created,
            'row_errors': result.row_errors,
            'fatal_error': result.fatal_error,
        }
        if not result.success:
            return APIResponse.error(
                message=result.fatal_error or "Import failed with row errors",
                data=payload,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return APIResponse.success(
            data=payload,
            message=f"Imported {result.categories_created} categorías",
            status_code=status.HTTP_201_CREATED,
        )
