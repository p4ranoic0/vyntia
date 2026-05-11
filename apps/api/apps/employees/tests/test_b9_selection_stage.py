"""Tests for B.9 SelectionStage."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.employees.models import JobPosting, PersonnelRequisition, SelectionStage
from apps.identity.models import User
from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test", nombre_unidad_organica="Test", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(code="X", name="X", department=department)


@pytest.fixture
def admin(db):
    return User.objects.create(
        username="adm_st", email="adm_st@test.local",
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


@pytest.mark.django_db
class TestSelectionStage:
    def test_create_minimal(self, posting):
        s = SelectionStage.objects.create(
            posting=posting, kind='curricular', name='CV review', order=1,
        )
        assert s.is_eliminatoria is True
        assert s.min_score == Decimal('0')
        assert s.max_score == Decimal('20')

    def test_unique_order_per_posting(self, posting):
        SelectionStage.objects.create(posting=posting, kind='curricular', name='A', order=1)
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                SelectionStage.objects.create(
                    posting=posting, kind='knowledge', name='B', order=1,
                )

    def test_clean_min_gt_max_raises(self, posting):
        s = SelectionStage(
            posting=posting, kind='curricular', name='X', order=1,
            min_score=Decimal('15'), max_score=Decimal('14'),
        )
        with pytest.raises(ValidationError):
            s.clean()

    def test_clean_weight_out_of_range_raises(self, posting):
        s = SelectionStage(
            posting=posting, kind='curricular', name='X', order=1,
            weight=Decimal('150'),
        )
        with pytest.raises(ValidationError):
            s.clean()

    def test_kind_choices_cover_servir_flow(self):
        kinds = {k for k, _ in SelectionStage.KIND_CHOICES}
        # SERVIR flow needs: curricular, knowledge, psycho, interview
        assert {'curricular', 'knowledge', 'psycho', 'interview'} <= kinds

    def test_servir_knowledge_min_14_supported(self, posting):
        s = SelectionStage.objects.create(
            posting=posting, kind='knowledge', name='Conocimientos',
            order=1, min_score=Decimal('14.00'), max_score=Decimal('20.00'),
        )
        s.clean()  # no error
        assert s.min_score == Decimal('14.00')

    def test_ordering(self, posting):
        SelectionStage.objects.create(posting=posting, kind='knowledge', name='B', order=2)
        SelectionStage.objects.create(posting=posting, kind='curricular', name='A', order=1)
        ordered = list(SelectionStage.objects.filter(posting=posting))
        assert [s.order for s in ordered] == [1, 2]

    def test_cascade_delete_with_posting(self, posting):
        SelectionStage.objects.create(posting=posting, kind='curricular', name='A', order=1)
        SelectionStage.objects.create(posting=posting, kind='knowledge', name='B', order=2)
        assert SelectionStage.objects.filter(posting=posting).count() == 2
        posting.delete()
        assert SelectionStage.objects.count() == 0
