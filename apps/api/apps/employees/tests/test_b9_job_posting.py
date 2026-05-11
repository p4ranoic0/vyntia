"""Tests for B.9 JobPosting (convocatoria con sector + plazos SERVIR)."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import JobPosting, PersonnelRequisition
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
def admin(db):
    return User.objects.create(
        username="admin", email="admin@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def hr(db):
    return User.objects.create(
        username="hr2", email="hr2@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def finance(db):
    return User.objects.create(
        username="fin2", email="fin2@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def approved_requisition(department, position, admin, hr, finance):
    req = PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=admin,
    )
    req.approve_hr(user=hr)
    req.approve_finance(user=finance)
    return req


@pytest.fixture
def draft_requisition(department, position, admin):
    return PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=admin,
    )


@pytest.fixture
def private_posting(approved_requisition):
    return JobPosting.objects.create(
        requisition=approved_requisition,
        title='Analista I — Sector privado',
        sector_mode='private',
    )


@pytest.fixture
def public_posting(approved_requisition):
    return JobPosting.objects.create(
        requisition=approved_requisition,
        title='Analista I — SERVIR',
        sector_mode='public_servir',
        bases_url='https://servir.gob.pe/bases/001',
        applications_open_at=date(2026, 6, 1),
        applications_close_at=date(2026, 6, 15),
        transparency_published=True,
    )


@pytest.mark.django_db
class TestJobPostingLifecycle:
    def test_defaults(self, private_posting):
        assert private_posting.status == 'draft'
        assert private_posting.sector_mode == 'private'
        assert private_posting.posting_kind == 'external'
        assert private_posting.transparency_published is False

    def test_publish_private_succeeds(self, private_posting, admin):
        private_posting.publish(user=admin)
        private_posting.refresh_from_db()
        assert private_posting.status == 'published'
        assert private_posting.published_at is not None

    def test_publish_requires_approved_requisition(self, draft_requisition, admin):
        posting = JobPosting.objects.create(
            requisition=draft_requisition, title='X', sector_mode='private',
        )
        with pytest.raises(ValidationError, match="aprobada"):
            posting.publish(user=admin)

    def test_publish_servir_succeeds_with_all_requirements(self, public_posting, admin):
        public_posting.publish(user=admin)
        public_posting.refresh_from_db()
        assert public_posting.status == 'published'

    def test_servir_requires_bases(self, approved_requisition, admin):
        p = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='public_servir',
            applications_open_at=date(2026, 6, 1),
            applications_close_at=date(2026, 6, 15),
            transparency_published=True,
        )
        with pytest.raises(ValidationError, match="bases"):
            p.publish(user=admin)

    def test_servir_requires_min_7_days_open(self, approved_requisition, admin):
        p = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='public_servir',
            bases_url='https://x.gob.pe/b',
            applications_open_at=date(2026, 6, 1),
            applications_close_at=date(2026, 6, 5),  # only 4 days
            transparency_published=True,
        )
        with pytest.raises(ValidationError, match="al menos 7"):
            p.publish(user=admin)

    def test_servir_requires_transparency_flag(self, approved_requisition, admin):
        p = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='public_servir',
            bases_url='https://x.gob.pe/b',
            applications_open_at=date(2026, 6, 1),
            applications_close_at=date(2026, 6, 15),
            transparency_published=False,
        )
        with pytest.raises(ValidationError, match="transparency"):
            p.publish(user=admin)

    def test_clean_rejects_inverted_dates(self, approved_requisition):
        p = JobPosting(
            requisition=approved_requisition, title='X', sector_mode='private',
            applications_open_at=date(2026, 6, 15),
            applications_close_at=date(2026, 6, 1),
        )
        with pytest.raises(ValidationError):
            p.clean()

    def test_start_evaluation_requires_published(self, private_posting):
        with pytest.raises(ValidationError):
            private_posting.start_evaluation()

    def test_close_flow(self, private_posting, admin):
        private_posting.publish(user=admin)
        private_posting.close(reason='Candidato contratado')
        private_posting.refresh_from_db()
        assert private_posting.status == 'closed'
        assert 'contratado' in private_posting.closed_reason

    def test_declare_void_requires_reason(self, private_posting, admin):
        private_posting.publish(user=admin)
        with pytest.raises(ValidationError):
            private_posting.declare_void(reason='')

    def test_declare_void_marks_status(self, private_posting, admin):
        private_posting.publish(user=admin)
        private_posting.declare_void(reason='Sin candidatos aptos')
        private_posting.refresh_from_db()
        assert private_posting.status == 'declared_void'

    def test_cancel_only_in_draft(self, private_posting, admin):
        private_posting.cancel()
        assert private_posting.status == 'cancelled'
        # Cannot cancel again from cancelled
        with pytest.raises(ValidationError):
            private_posting.cancel()

    def test_sector_mode_choices(self):
        kinds = {k for k, _ in JobPosting.SECTOR_MODE_CHOICES}
        assert kinds == {'private', 'public_servir'}

    def test_status_choices_cover_full_lifecycle(self):
        statuses = {k for k, _ in JobPosting.STATUS_CHOICES}
        assert statuses == {
            'draft', 'published', 'in_evaluation',
            'closed', 'cancelled', 'declared_void',
        }
