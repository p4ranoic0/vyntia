"""Tests for B.9 JobApplication state machine."""
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.employees.models import (
    Candidate,
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
        username="adm_app", email="adm_app@test.local",
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
def candidate(db):
    return Candidate.objects.create(
        document_number='99999999',
        first_names='Cand',
        last_names='Idata',
        email='cand@test.local',
    )


@pytest.fixture
def application(posting, candidate):
    return JobApplication.objects.create(posting=posting, candidate=candidate)


@pytest.mark.django_db
class TestJobApplication:
    def test_defaults(self, application):
        assert application.status == 'received'
        assert application.applied_at is not None

    def test_unique_per_posting_candidate(self, posting, candidate):
        JobApplication.objects.create(posting=posting, candidate=candidate)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                JobApplication.objects.create(posting=posting, candidate=candidate)

    def test_advance_legal_transition(self, application):
        application.advance_to('reviewing')
        application.refresh_from_db()
        assert application.status == 'reviewing'
        application.advance_to('in_evaluation')
        assert application.status == 'in_evaluation'
        application.advance_to('finalist')
        application.advance_to('offered')
        application.advance_to('accepted')
        application.advance_to('hired')
        assert application.status == 'hired'

    def test_advance_illegal_transition_raises(self, application):
        # received → finalist is not legal
        with pytest.raises(ValidationError, match="Transición inválida"):
            application.advance_to('finalist')

    def test_advance_from_terminal_raises(self, application):
        application.advance_to('reviewing')
        application.advance_to('in_evaluation')
        application.eliminate(reason='no fit')
        with pytest.raises(ValidationError):
            application.advance_to('reviewing')

    def test_eliminate_with_stage(self, application, posting):
        stage = SelectionStage.objects.create(
            posting=posting, kind='knowledge', name='K', order=1,
        )
        application.advance_to('reviewing')
        application.advance_to('in_evaluation')
        application.eliminate(stage=stage, reason='Score 11/14')
        application.refresh_from_db()
        assert application.status == 'eliminated'
        assert application.eliminated_at_stage == stage
        assert application.elimination_reason == 'Score 11/14'

    def test_eliminate_terminal_raises(self, application):
        application.withdraw()
        with pytest.raises(ValidationError):
            application.eliminate(reason='X')

    def test_withdraw_from_received(self, application):
        application.withdraw()
        application.refresh_from_db()
        assert application.status == 'withdrawn'
        assert application.withdrawn_at is not None

    def test_withdraw_terminal_raises(self, application):
        application.withdraw()
        with pytest.raises(ValidationError):
            application.withdraw()

    def test_advance_transitions_keys_match_status_choices(self):
        choices = {k for k, _ in JobApplication.STATUS_CHOICES}
        assert set(JobApplication.ADVANCE_TRANSITIONS.keys()) == choices
