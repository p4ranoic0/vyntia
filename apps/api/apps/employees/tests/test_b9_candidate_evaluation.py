"""Tests for B.9 CandidateEvaluation."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.employees.models import (
    Candidate,
    CandidateEvaluation,
    JobApplication,
    JobPosting,
    PersonnelRequisition,
    SelectionStage,
)
from apps.identity.models import User
from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="T", nombre_unidad_organica="T", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(code="P", name="P", department=department)


@pytest.fixture
def admin(db):
    return User.objects.create(
        username="adm_ev", email="adm_ev@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def evaluator(db):
    return User.objects.create(
        username="ev1", email="ev1@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def posting(department, position, admin):
    req = PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=admin,
    )
    return JobPosting.objects.create(
        requisition=req, title='X', sector_mode='private',
    )


@pytest.fixture
def stage(posting):
    return SelectionStage.objects.create(
        posting=posting, kind='knowledge', name='Conocimientos',
        order=1, min_score=Decimal('14.00'), max_score=Decimal('20.00'),
    )


@pytest.fixture
def candidate(db):
    return Candidate.objects.create(
        document_number='99999998',
        first_names='X', last_names='Y',
        email='xy@test.local',
    )


@pytest.fixture
def application(posting, candidate):
    return JobApplication.objects.create(posting=posting, candidate=candidate)


@pytest.mark.django_db
class TestCandidateEvaluation:
    def test_create_passing_score(self, application, stage, evaluator):
        ev = CandidateEvaluation(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('17.50'),
        )
        ev.full_clean()
        ev.save()
        assert ev.passed is True

    def test_create_failing_score(self, application, stage, evaluator):
        ev = CandidateEvaluation(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('14.00'),  # exactly min — passes
        )
        ev.save()
        assert ev.passed is True
        # Just below min:
        application2 = JobApplication.objects.create(
            posting=application.posting,
            candidate=Candidate.objects.create(
                document_number='99999997', first_names='A', last_names='B',
                email='ab@test.local',
            ),
        )
        ev2 = CandidateEvaluation(
            application=application2, stage=stage, evaluator=evaluator,
            score=Decimal('13.99'),
        )
        ev2.save()
        assert ev2.passed is False

    def test_clean_score_out_of_range_raises(self, application, stage, evaluator):
        ev = CandidateEvaluation(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('25.00'),
        )
        with pytest.raises(ValidationError):
            ev.clean()
        ev2 = CandidateEvaluation(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('5.00'),  # below min_score=14
        )
        with pytest.raises(ValidationError):
            ev2.clean()

    def test_unique_per_application_stage(self, application, stage, evaluator):
        CandidateEvaluation.objects.create(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('15.00'),
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                CandidateEvaluation.objects.create(
                    application=application, stage=stage, evaluator=evaluator,
                    score=Decimal('16.00'),
                )

    def test_passed_auto_recomputed_on_save(self, application, stage, evaluator):
        ev = CandidateEvaluation.objects.create(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('15.00'),
        )
        assert ev.passed is True
        ev.score = Decimal('13.50')
        ev.save()
        ev.refresh_from_db()
        assert ev.passed is False

    def test_cascade_delete_with_application(self, application, stage, evaluator):
        CandidateEvaluation.objects.create(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('15.00'),
        )
        application.delete()
        assert CandidateEvaluation.objects.count() == 0

    def test_protect_evaluator_delete(self, application, stage, evaluator):
        from django.db.models import ProtectedError
        CandidateEvaluation.objects.create(
            application=application, stage=stage, evaluator=evaluator,
            score=Decimal('15.00'),
        )
        with pytest.raises(ProtectedError):
            evaluator.delete()
