"""Tests for B.11 Induction models (Module 03.3 RPE 265-2017)."""
from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.identity.models import User
from apps.onboarding.models import (
    InductionEvaluation,
    InductionMaterial,
    InductionMentor,
    InductionPlan,
    InductionTask,
)


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='90909090', tipo_documento='DNI',
        nombres_empleado='Sofía', apellido_paterno='Rojas',
        apellido_materno='Vera', fecha_nacimiento=date(1995, 5, 5),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b11', email='hr_b11@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def plan(employee, hr_user):
    return InductionPlan.objects.create(
        employee=employee, title='Plan general onboarding',
        kind='general', created_by=hr_user,
    )


@pytest.mark.django_db
class TestInductionPlan:
    def test_defaults(self, plan):
        assert plan.id is not None
        assert plan.status == 'draft'
        assert plan.kind == 'general'

    def test_string_repr(self, plan):
        s = str(plan)
        assert 'General' in s
        assert plan.title in s

    def test_mark_in_progress_only_from_draft(self, plan):
        plan.mark_in_progress()
        plan.refresh_from_db()
        assert plan.status == 'in_progress'
        assert plan.starts_at is not None
        with pytest.raises(ValidationError):
            plan.mark_in_progress()

    def test_mark_completed_requires_in_progress(self, plan):
        with pytest.raises(ValidationError):
            plan.mark_completed()
        plan.mark_in_progress()
        plan.mark_completed()
        plan.refresh_from_db()
        assert plan.status == 'completed'
        assert plan.completed_at is not None

    def test_mark_certified_requires_completed(self, plan):
        plan.mark_in_progress()
        with pytest.raises(ValidationError):
            plan.mark_certified()
        plan.mark_completed()
        plan.mark_certified()
        plan.refresh_from_db()
        assert plan.status == 'certified'
        assert plan.certified_at is not None

    def test_multiple_plans_per_employee_allowed(self, employee, hr_user):
        InductionPlan.objects.create(
            employee=employee, title='P1', kind='general', created_by=hr_user,
        )
        InductionPlan.objects.create(
            employee=employee, title='P2', kind='especifica', created_by=hr_user,
        )
        assert InductionPlan.objects.filter(employee=employee).count() == 2

    def test_indexes_declared(self):
        index_fields = {tuple(i.fields) for i in InductionPlan._meta.indexes}
        assert ('tenant', 'status') in index_fields
        assert ('tenant', 'employee') in index_fields


@pytest.mark.django_db
class TestInductionTask:
    def test_default_not_done(self, plan):
        task = InductionTask.objects.create(
            plan=plan, kind='day_1', title='Bienvenida',
        )
        assert task.is_done is False

    def test_is_done_after_completed_at(self, plan, hr_user):
        from django.utils import timezone
        task = InductionTask.objects.create(
            plan=plan, kind='day_1', title='Bienvenida',
        )
        task.completed_at = timezone.now()
        task.completed_by = hr_user
        task.save()
        assert task.is_done is True


@pytest.mark.django_db
class TestInductionMaterial:
    def test_optional_task_reference(self, plan):
        m = InductionMaterial.objects.create(
            plan=plan, title='Bienvenida video',
            format='video', url='https://example.com/v.mp4',
        )
        assert m.task is None
        assert m.plan == plan


@pytest.mark.django_db
class TestInductionMentor:
    def test_one_per_plan(self, plan, hr_user):
        InductionMentor.objects.create(plan=plan, mentor=hr_user)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            InductionMentor.objects.create(plan=plan, mentor=hr_user)


@pytest.mark.django_db
class TestInductionEvaluation:
    def test_passed_when_score_above_threshold(self, plan, hr_user):
        e = InductionEvaluation.objects.create(
            plan=plan, score=70, evaluator=hr_user,
        )
        assert e.passed is True

    def test_failed_when_score_below_threshold(self, plan, hr_user):
        e = InductionEvaluation.objects.create(
            plan=plan, score=50, evaluator=hr_user,
        )
        assert e.passed is False

    def test_passed_boundary_exact_60(self, plan, hr_user):
        e = InductionEvaluation.objects.create(
            plan=plan, score=60, evaluator=hr_user,
        )
        assert e.passed is True

    def test_one_per_plan(self, plan, hr_user):
        InductionEvaluation.objects.create(plan=plan, score=80, evaluator=hr_user)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            InductionEvaluation.objects.create(plan=plan, score=90, evaluator=hr_user)
