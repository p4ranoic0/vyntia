"""ViewSets for B.11 Induction (Module 03.3)."""
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action

from api.v1.rrhh.permissions import RRHHPermission
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.identity.models import User
from apps.onboarding.models import (
    InductionMaterial,
    InductionPlan,
    InductionTask,
)
from apps.onboarding.services import induction_service

from .induction_serializers import (
    AssignMentorInputSerializer,
    InductionMaterialSerializer,
    InductionPlanSerializer,
    InductionTaskSerializer,
    RecordEvaluationInputSerializer,
)


class InductionPlanViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """Induction plans per Module 03.3 — tenant-scoped, HR-only."""
    queryset = InductionPlan.objects.select_related(
        'employee', 'contract', 'created_by',
    ).prefetch_related('tasks', 'materials')
    serializer_class = InductionPlanSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    search_fields = ['title']
    filterset_fields = ['status', 'kind', 'employee', 'contract']
    ordering_fields = ['created_at', 'starts_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        """Use induction_service.build_plan_for_employee so tasks scaffold."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.validated_data['employee']
        contract = serializer.validated_data.get('contract')
        kind = serializer.validated_data.get('kind', 'general')
        title = serializer.validated_data.get('title', '')
        lengua = serializer.validated_data.get('lengua_originaria', '')
        plan = induction_service.build_plan_for_employee(
            employee=employee, contract=contract, kind=kind, title=title,
            tenant=getattr(request, 'tenant', None),
            created_by=request.user if request.user.is_authenticated else None,
            lengua_originaria=lengua,
        )
        return APIResponse.success(
            data=InductionPlanSerializer(plan).data,
            message='Plan creado',
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='start')
    def start(self, request, pk=None):
        plan = self.get_object()
        try:
            plan.mark_in_progress()
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=InductionPlanSerializer(plan).data,
            message='Plan iniciado',
        )

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        plan = self.get_object()
        try:
            plan.mark_completed()
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=InductionPlanSerializer(plan).data,
            message='Plan completado',
        )

    @action(detail=True, methods=['post'], url_path='certify')
    def certify(self, request, pk=None):
        plan = self.get_object()
        try:
            plan.mark_certified()
        except Exception as exc:
            return APIResponse.error(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)
        return APIResponse.success(
            data=InductionPlanSerializer(plan).data,
            message='Plan certificado',
        )

    @action(detail=True, methods=['post'], url_path='assign-mentor')
    def assign_mentor(self, request, pk=None):
        plan = self.get_object()
        input_serializer = AssignMentorInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        try:
            mentor_user = User.objects.get(pk=input_serializer.validated_data['mentor'])
        except User.DoesNotExist:
            return APIResponse.error(message='Mentor no encontrado',
                                     status_code=status.HTTP_404_NOT_FOUND)
        induction_service.assign_mentor(
            plan_id=plan.id, mentor_user=mentor_user,
            notes=input_serializer.validated_data.get('notes', ''),
        )
        return APIResponse.success(
            data=InductionPlanSerializer(plan).data,
            message='Mentor asignado',
        )

    @action(detail=True, methods=['post'], url_path='record-evaluation')
    def record_evaluation(self, request, pk=None):
        plan = self.get_object()
        input_serializer = RecordEvaluationInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        evaluation = induction_service.record_evaluation(
            plan_id=plan.id,
            score=input_serializer.validated_data['score'],
            evaluator=request.user,
            competencies=input_serializer.validated_data.get('competencies') or {},
            comments=input_serializer.validated_data.get('comments', ''),
        )
        return APIResponse.success(
            data={
                'plan': InductionPlanSerializer(plan).data,
                'evaluation': {
                    'id': str(evaluation.id),
                    'score': evaluation.score,
                    'passed': evaluation.passed,
                },
            },
            message='Evaluación registrada',
        )

    @action(detail=True, methods=['get'], url_path='certificate-pdf')
    def certificate_pdf(self, request, pk=None):
        plan = self.get_object()
        pdf_bytes = induction_service.render_certificate_pdf(plan.id)
        response = HttpResponse(
            pdf_bytes, content_type='application/pdf',
        )
        response['Content-Disposition'] = (
            f'attachment; filename="induccion_{plan.employee_id}_{plan.id}.pdf"'
        )
        return response


class InductionTaskViewSet(viewsets.ModelViewSet):
    """Tasks per induction plan."""
    queryset = InductionTask.objects.select_related('plan', 'completed_by')
    serializer_class = InductionTaskSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan', 'kind']
    ordering_fields = ['order', 'due_offset_days']
    ordering = ['order', 'due_offset_days']

    @action(detail=True, methods=['post'], url_path='mark-done')
    def mark_done(self, request, pk=None):
        task = self.get_object()
        out = induction_service.mark_task_done(task_id=task.id, user=request.user)
        return APIResponse.success(
            data=InductionTaskSerializer(out).data,
            message='Tarea completada',
        )


class InductionMaterialViewSet(viewsets.ModelViewSet):
    """Materials (videos / PDFs / interactive) for an induction plan."""
    queryset = InductionMaterial.objects.select_related('plan', 'task')
    serializer_class = InductionMaterialSerializer
    permission_classes = [RRHHPermission]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['plan', 'task', 'format']
