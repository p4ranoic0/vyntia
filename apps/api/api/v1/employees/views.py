"""ViewSets for B.9 Selección — Module 03.1.

7 ViewSets at /api/v1/employees/ covering the full PersonnelRequisition →
JobPosting → JobApplication → CandidateEvaluation → MeritRanking flow,
plus Candidate (external persons) and SelectionStage (per-posting etapas).
"""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.employees.models import (
    Candidate,
    CandidateEvaluation,
    JobApplication,
    JobPosting,
    MeritRanking,
    PersonnelRequisition,
    SelectionStage,
)
from apps.employees.services import compute_merit_ranking

from .serializers import (
    CandidateEvaluationSerializer,
    CandidateSerializer,
    JobApplicationAdvanceSerializer,
    JobApplicationEliminateSerializer,
    JobApplicationSerializer,
    JobPostingCloseSerializer,
    JobPostingDeclareVoidSerializer,
    JobPostingPublishSerializer,
    JobPostingSerializer,
    MeritRankingSerializer,
    PersonnelRequisitionSerializer,
    RequisitionApprovalSerializer,
    RequisitionRejectSerializer,
    SelectionStageSerializer,
)


class CandidateViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """External candidates — tenant-scoped."""
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['document_number', 'first_names', 'last_names', 'email']
    filterset_fields = ['document_type', 'is_active', 'source']
    ordering_fields = ['created_at', 'last_names']
    ordering = ['-created_at']


class PersonnelRequisitionViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """PersonnelRequisition — alta autorizada con doble firma."""
    queryset = PersonnelRequisition.objects.select_related(
        'position', 'department', 'requested_by',
        'approved_by_hr', 'approved_by_finance',
    )
    serializer_class = PersonnelRequisitionSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code']
    filterset_fields = ['status', 'position', 'department', 'justification']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        req = self.get_object()
        try:
            req.submit_for_approval()
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PersonnelRequisitionSerializer(req).data,
            message='Requisición enviada a aprobación',
        )

    @action(detail=True, methods=['post'], url_path='approve-hr')
    def approve_hr(self, request, pk=None):
        req = self.get_object()
        RequisitionApprovalSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            req.approve_hr(user=request.user)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PersonnelRequisitionSerializer(req).data,
            message='Aprobación HR registrada',
        )

    @action(detail=True, methods=['post'], url_path='approve-finance')
    def approve_finance(self, request, pk=None):
        req = self.get_object()
        RequisitionApprovalSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            req.approve_finance(user=request.user)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PersonnelRequisitionSerializer(req).data,
            message='Aprobación Finanzas registrada',
        )

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        req = self.get_object()
        in_ser = RequisitionRejectSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        try:
            req.reject(user=request.user, reason=in_ser.validated_data['reason'])
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PersonnelRequisitionSerializer(req).data,
            message='Requisición rechazada',
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        req = self.get_object()
        try:
            req.cancel(user=request.user)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=PersonnelRequisitionSerializer(req).data,
            message='Requisición cancelada',
        )


class JobPostingViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """JobPosting — convocatoria privada o SERVIR."""
    queryset = JobPosting.objects.select_related(
        'requisition', 'cpe_entry', 'created_by',
    )
    serializer_class = JobPostingSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'code', 'summary']
    filterset_fields = ['sector_mode', 'status', 'requisition', 'posting_kind']
    ordering_fields = ['created_at', 'published_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        posting = self.get_object()
        JobPostingPublishSerializer(data=request.data).is_valid(raise_exception=True)
        try:
            posting.publish(user=request.user)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobPostingSerializer(posting).data,
            message='Convocatoria publicada',
        )

    @action(detail=True, methods=['post'], url_path='start-evaluation')
    def start_evaluation(self, request, pk=None):
        posting = self.get_object()
        try:
            posting.start_evaluation()
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobPostingSerializer(posting).data,
            message='Evaluación iniciada',
        )

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, pk=None):
        posting = self.get_object()
        in_ser = JobPostingCloseSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        try:
            posting.close(reason=in_ser.validated_data.get('reason', ''))
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobPostingSerializer(posting).data,
            message='Convocatoria cerrada',
        )

    @action(detail=True, methods=['post'], url_path='declare-void')
    def declare_void(self, request, pk=None):
        posting = self.get_object()
        in_ser = JobPostingDeclareVoidSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        try:
            posting.declare_void(reason=in_ser.validated_data['reason'])
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobPostingSerializer(posting).data,
            message='Convocatoria declarada desierta',
        )

    @action(detail=True, methods=['post'], url_path='compute-ranking')
    def compute_ranking(self, request, pk=None):
        posting = self.get_object()
        try:
            rows = compute_merit_ranking(posting=posting)
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=MeritRankingSerializer(rows, many=True).data,
            message=f'Cuadro de méritos calculado ({len(rows)} candidatos)',
        )


class SelectionStageViewSet(viewsets.ModelViewSet):
    queryset = SelectionStage.objects.select_related('posting')
    serializer_class = SelectionStageSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['posting', 'kind', 'is_eliminatoria']
    ordering_fields = ['order']
    ordering = ['posting', 'order']


class JobApplicationViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    queryset = JobApplication.objects.select_related(
        'posting', 'candidate', 'eliminated_at_stage',
    )
    serializer_class = JobApplicationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['posting', 'candidate', 'status']
    ordering_fields = ['applied_at']
    ordering = ['-applied_at']

    @action(detail=True, methods=['post'], url_path='advance-to')
    def advance_to(self, request, pk=None):
        app = self.get_object()
        in_ser = JobApplicationAdvanceSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        try:
            app.advance_to(in_ser.validated_data['new_status'])
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobApplicationSerializer(app).data,
            message=f'Postulación avanzada a {app.status}',
        )

    @action(detail=True, methods=['post'], url_path='eliminate')
    def eliminate(self, request, pk=None):
        app = self.get_object()
        in_ser = JobApplicationEliminateSerializer(data=request.data)
        in_ser.is_valid(raise_exception=True)
        stage = None
        if in_ser.validated_data.get('stage'):
            try:
                stage = SelectionStage.objects.get(pk=in_ser.validated_data['stage'])
            except SelectionStage.DoesNotExist:
                return APIResponse.error(
                    message='Etapa no encontrada',
                    status_code=status.HTTP_404_NOT_FOUND,
                )
        try:
            app.eliminate(stage=stage, reason=in_ser.validated_data.get('reason', ''))
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobApplicationSerializer(app).data,
            message='Postulación eliminada',
        )

    @action(detail=True, methods=['post'], url_path='withdraw')
    def withdraw(self, request, pk=None):
        app = self.get_object()
        try:
            app.withdraw()
        except Exception as e:
            return APIResponse.error(message=str(e), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=JobApplicationSerializer(app).data,
            message='Postulación retirada',
        )


class CandidateEvaluationViewSet(viewsets.ModelViewSet):
    queryset = CandidateEvaluation.objects.select_related(
        'application', 'stage', 'evaluator',
    )
    serializer_class = CandidateEvaluationSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['application', 'stage', 'evaluator', 'passed']
    ordering = ['stage__order']

    def perform_create(self, serializer):
        serializer.save(evaluator=self.request.user)


class MeritRankingViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only — rankings are computed via JobPostingViewSet.compute_ranking."""
    queryset = MeritRanking.objects.select_related('posting', 'application')
    serializer_class = MeritRankingSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['posting', 'outcome']
    ordering = ['posting', 'rank']
