"""Tests for B.9 PersonnelRequisition (alta autorizada con doble firma)."""
import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import PersonnelRequisition
from apps.identity.models import User
from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test", nombre_unidad_organica="Test", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(
        code="ANA-001", name="Analista", department=department,
    )


@pytest.fixture
def requester(db):
    return User.objects.create(
        username="req", email="req@test.local",
        tipo_usuario="rrhh", estado_usuario="activo",
    )


@pytest.fixture
def hr_approver(db):
    return User.objects.create(
        username="hr", email="hr@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def finance_approver(db):
    return User.objects.create(
        username="fin", email="fin@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def requisition(department, position, requester):
    return PersonnelRequisition.objects.create(
        position=position,
        department=department,
        justification='replacement',
        requested_by=requester,
        code='REQ-2026-0001',
    )


@pytest.mark.django_db
class TestRequisitionLifecycle:
    def test_defaults(self, requisition):
        assert requisition.status == 'draft'
        assert requisition.requested_count == 1
        assert requisition.is_fully_approved is False

    def test_submit_for_approval(self, requisition):
        requisition.submit_for_approval()
        requisition.refresh_from_db()
        assert requisition.status == 'pending_approval'

    def test_submit_from_non_draft_raises(self, requisition):
        requisition.status = 'approved'
        requisition.save()
        with pytest.raises(ValidationError):
            requisition.submit_for_approval()

    def test_hr_approval_alone_keeps_pending(self, requisition, hr_approver):
        requisition.approve_hr(user=hr_approver)
        requisition.refresh_from_db()
        assert requisition.status == 'pending_approval'
        assert requisition.approved_by_hr == hr_approver
        assert requisition.is_fully_approved is False
        assert requisition.approved_at is None

    def test_finance_approval_alone_keeps_pending(self, requisition, finance_approver):
        requisition.approve_finance(user=finance_approver)
        requisition.refresh_from_db()
        assert requisition.status == 'pending_approval'
        assert requisition.approved_by_finance == finance_approver
        assert requisition.is_fully_approved is False

    def test_double_approval_flips_to_approved(
        self, requisition, hr_approver, finance_approver,
    ):
        requisition.approve_hr(user=hr_approver)
        requisition.approve_finance(user=finance_approver)
        requisition.refresh_from_db()
        assert requisition.status == 'approved'
        assert requisition.is_fully_approved is True
        assert requisition.approved_at is not None

    def test_reject_requires_reason(self, requisition, hr_approver):
        with pytest.raises(ValidationError):
            requisition.reject(user=hr_approver, reason='')

    def test_reject_sets_status_and_metadata(self, requisition, hr_approver):
        requisition.submit_for_approval()
        requisition.reject(user=hr_approver, reason='Sin presupuesto')
        requisition.refresh_from_db()
        assert requisition.status == 'rejected'
        assert requisition.rejected_by == hr_approver
        assert requisition.rejected_reason == 'Sin presupuesto'
        assert requisition.rejected_at is not None

    def test_cannot_reject_approved(self, requisition, hr_approver, finance_approver):
        requisition.approve_hr(user=hr_approver)
        requisition.approve_finance(user=finance_approver)
        with pytest.raises(ValidationError):
            requisition.reject(user=hr_approver, reason='reason')

    def test_cancel_pending(self, requisition, requester):
        requisition.submit_for_approval()
        requisition.cancel(user=requester)
        requisition.refresh_from_db()
        assert requisition.status == 'cancelled'

    def test_cannot_cancel_approved(self, requisition, hr_approver, finance_approver):
        requisition.approve_hr(user=hr_approver)
        requisition.approve_finance(user=finance_approver)
        with pytest.raises(ValidationError):
            requisition.cancel(user=hr_approver)

    def test_mark_fulfilled_requires_approved(
        self, requisition, hr_approver, finance_approver,
    ):
        with pytest.raises(ValidationError):
            requisition.mark_fulfilled()
        requisition.approve_hr(user=hr_approver)
        requisition.approve_finance(user=finance_approver)
        requisition.mark_fulfilled()
        requisition.refresh_from_db()
        assert requisition.status == 'fulfilled'

    def test_justification_choices_cover_4_kinds(self):
        kinds = {k for k, _ in PersonnelRequisition.JUSTIFICATION_CHOICES}
        assert kinds == {'new_position', 'replacement', 'expansion', 'temporary'}
