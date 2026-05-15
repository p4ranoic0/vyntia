"""induction_service — InductionPlan orchestration + RPE 265 certificate (B.11).

Builds plans with templated default checklists, marks tasks done idempotently,
assigns mentors, records evaluations, and generates the RPE 265-2017 obligatory
finalization certificate using the existing pdf_generator fallback chain
(xhtml2pdf → WeasyPrint → ReportLab).

See Module 03.3 and ROADMAP-B.md backlog #114, #115.
"""

from __future__ import annotations

from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.documents.services.pdf_generator import PDFGenerator
from apps.onboarding.models import (
    InductionEvaluation,
    InductionMentor,
    InductionPlan,
    InductionTask,
)


DEFAULT_GENERAL_TASKS: list[tuple[str, str, int]] = [
    ('day_1', 'Bienvenida y recorrido por las instalaciones', 0),
    ('day_1', 'Entrega de credenciales y accesos', 0),
    ('first_week', 'Inducción a misión, visión, valores y código de ética', 3),
    ('first_week', 'Inducción a políticas de seguridad y SST', 4),
    ('first_month', 'Reunión 1:1 con el supervisor directo', 10),
    ('first_month', 'Encuesta inicial de clima y ajuste', 25),
]


@transaction.atomic
def build_plan_for_employee(
    *,
    employee,
    contract=None,
    kind: str = 'general',
    title: str = '',
    tenant=None,
    created_by=None,
    lengua_originaria: str = '',
) -> InductionPlan:
    """Create a new InductionPlan; for kind='general', scaffold default tasks."""
    if tenant is None:
        tenant = getattr(employee, 'tenant', None)
    plan = InductionPlan.objects.create(
        tenant=tenant,
        employee=employee,
        contract=contract,
        title=title or f'Inducción {kind} — {employee.numero_documento}',
        kind=kind,
        created_by=created_by,
        lengua_originaria=lengua_originaria,
    )
    if kind == 'general':
        for order, (task_kind, task_title, offset) in enumerate(DEFAULT_GENERAL_TASKS):
            InductionTask.objects.create(
                plan=plan,
                kind=task_kind,
                title=task_title,
                due_offset_days=offset,
                order=order,
            )
    return plan


def mark_task_done(*, task_id, user) -> InductionTask:
    """Mark a task as done idempotently — keeps the first completed_at."""
    task = InductionTask.objects.get(pk=task_id)
    if task.completed_at is None:
        task.completed_at = timezone.now()
        task.completed_by = user
        task.save(update_fields=['completed_at', 'completed_by'])
    return task


def assign_mentor(*, plan_id, mentor_user, notes: str = '') -> InductionMentor:
    """Assign or replace the mentor for a plan (OneToOne)."""
    plan = InductionPlan.objects.get(pk=plan_id)
    mentor, _created = InductionMentor.objects.update_or_create(
        plan=plan,
        defaults={'mentor': mentor_user, 'notes': notes},
    )
    return mentor


def record_evaluation(
    *,
    plan_id,
    score: int,
    evaluator,
    competencies: dict | None = None,
    comments: str = '',
) -> InductionEvaluation:
    """Create or replace the evaluation for a plan."""
    plan = InductionPlan.objects.get(pk=plan_id)
    # Delete existing eval if any (since OneToOne)
    InductionEvaluation.objects.filter(plan=plan).delete()
    return InductionEvaluation.objects.create(
        plan=plan,
        score=score,
        evaluator=evaluator,
        competencies=competencies or {},
        comments=comments,
    )


# --------------------------------------------------------------------------- #
# Certificate generation                                                      #
# --------------------------------------------------------------------------- #

def render_certificate_html(plan_id) -> str:
    """Return the HTML of the RPE 265 finalization certificate."""
    plan = InductionPlan.objects.select_related('employee').get(pk=plan_id)
    evaluation_score = None
    try:
        evaluation_score = plan.evaluation.score
    except InductionEvaluation.DoesNotExist:
        pass

    employee = plan.employee
    full_name = ' '.join(
        part for part in [
            getattr(employee, 'nombres_empleado', ''),
            getattr(employee, 'apellido_paterno', ''),
            getattr(employee, 'apellido_materno', ''),
        ] if part
    )

    return render_to_string('induccion/certificado.html', {
        'plan': plan,
        'employee_full_name': full_name,
        'evaluation_score': evaluation_score,
        'issued_at': timezone.now(),
    })


def render_certificate_pdf(plan_id) -> bytes:
    """Return the PDF bytes via the project pdf_generator chain.

    Reuses PDFGenerator's xhtml2pdf → WeasyPrint → ReportLab fallback chain
    via the internal _html_to_pdf helper. We don't go through the
    `generar_pdf_certificado` flow because we render our own HTML here.
    """
    html = render_certificate_html(plan_id)
    generator = PDFGenerator()
    return generator._html_to_pdf(html)
