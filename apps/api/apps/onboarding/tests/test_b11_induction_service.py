"""Tests for B.11 induction_service."""
from datetime import date

import pytest

from apps.employees.models import Employee
from apps.identity.models import User
from apps.onboarding.models import (
    InductionEvaluation,
    InductionMentor,
    InductionPlan,
    InductionTask,
)
from apps.onboarding.services import induction_service


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='80808080', tipo_documento='DNI',
        nombres_empleado='Lucía', apellido_paterno='Castro',
        apellido_materno='Díaz', fecha_nacimiento=date(1992, 3, 3),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b11_svc', email='hr_b11_svc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def mentor_user(db):
    return User.objects.create(
        username='mentor_b11', email='mentor_b11@test.local',
        tipo_usuario='colaborador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestBuildPlanForEmployee:
    def test_general_kind_scaffolds_default_tasks(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        assert plan.status == 'draft'
        assert plan.kind == 'general'
        assert plan.tasks.count() == len(induction_service.DEFAULT_GENERAL_TASKS)

    def test_especifica_kind_no_default_tasks(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='especifica', created_by=hr_user,
        )
        assert plan.tasks.count() == 0

    def test_passes_through_title_and_lengua(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general',
            title='Plan custom', lengua_originaria='quz',
            created_by=hr_user,
        )
        assert plan.title == 'Plan custom'
        assert plan.lengua_originaria == 'quz'


@pytest.mark.django_db
class TestMarkTaskDone:
    def test_persists_user_timestamp(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        task = plan.tasks.first()
        induction_service.mark_task_done(task_id=task.id, user=hr_user)
        task.refresh_from_db()
        assert task.completed_at is not None
        assert task.completed_by == hr_user

    def test_idempotent(self, employee, hr_user, mentor_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        task = plan.tasks.first()
        induction_service.mark_task_done(task_id=task.id, user=hr_user)
        first = InductionTask.objects.get(pk=task.id).completed_at
        # Second call with a different user should not overwrite
        induction_service.mark_task_done(task_id=task.id, user=mentor_user)
        again = InductionTask.objects.get(pk=task.id).completed_at
        assert again == first
        assert InductionTask.objects.get(pk=task.id).completed_by == hr_user


@pytest.mark.django_db
class TestAssignMentor:
    def test_creates_mentor(self, employee, hr_user, mentor_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        mentor = induction_service.assign_mentor(
            plan_id=plan.id, mentor_user=mentor_user, notes='Buddy A',
        )
        assert mentor.mentor == mentor_user
        assert mentor.notes == 'Buddy A'

    def test_replaces_previous(self, employee, hr_user, mentor_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        induction_service.assign_mentor(plan_id=plan.id, mentor_user=hr_user)
        induction_service.assign_mentor(plan_id=plan.id, mentor_user=mentor_user)
        plan.refresh_from_db()
        assert InductionMentor.objects.filter(plan=plan).count() == 1
        assert plan.mentor.mentor == mentor_user


@pytest.mark.django_db
class TestRecordEvaluation:
    def test_passed_score(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        ev = induction_service.record_evaluation(
            plan_id=plan.id, score=85, evaluator=hr_user,
            competencies={'comunicacion': 8, 'tecnico': 9},
            comments='Excelente',
        )
        assert ev.passed is True
        assert ev.competencies['comunicacion'] == 8

    def test_failed_score(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        ev = induction_service.record_evaluation(
            plan_id=plan.id, score=40, evaluator=hr_user,
        )
        assert ev.passed is False

    def test_replaces_previous(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        induction_service.record_evaluation(plan_id=plan.id, score=50, evaluator=hr_user)
        induction_service.record_evaluation(plan_id=plan.id, score=90, evaluator=hr_user)
        evs = InductionEvaluation.objects.filter(plan=plan)
        assert evs.count() == 1
        assert evs.first().score == 90


@pytest.mark.django_db
class TestRenderCertificateHtml:
    def test_includes_employee_name(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        plan.mark_in_progress()
        plan.mark_completed()
        html = induction_service.render_certificate_html(plan.id)
        assert employee.nombres_empleado in html
        assert employee.apellido_paterno in html

    def test_includes_completion_date(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        plan.mark_in_progress()
        plan.mark_completed()
        html = induction_service.render_certificate_html(plan.id)
        assert 'Finalización' in html

    def test_includes_evaluation_score_when_present(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        induction_service.record_evaluation(plan_id=plan.id, score=88, evaluator=hr_user)
        plan.mark_in_progress()
        plan.mark_completed()
        html = induction_service.render_certificate_html(plan.id)
        assert '88' in html

    def test_references_rpe_265(self, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=hr_user,
        )
        plan.mark_in_progress()
        plan.mark_completed()
        html = induction_service.render_certificate_html(plan.id)
        assert 'SERVIR' in html
        assert '265-2017' in html
