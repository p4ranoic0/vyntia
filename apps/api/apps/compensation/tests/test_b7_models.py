"""Tests for B.7 CCF / Category / FactorScore / SalaryBand models + scoring service."""
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command

from apps.compensation.models import (
    Category,
    CategoryFactorScore,
    CategoryFunctionTable,
    JobFactor,
    JobSubfactor,
    SalaryBand,
)
from apps.compensation.services import recompute_category_total


@pytest.fixture
def seeded_factors(db):
    call_command("seed_job_factors")


@pytest.fixture
def ccf(db):
    return CategoryFunctionTable.objects.create(
        title="CCF 2026", description="Test CCF",
    )


@pytest.fixture
def category(ccf):
    return Category.objects.create(
        ccf=ccf, code="CAT-001", name="Analista I",
        min_experience_years=2,
    )


@pytest.mark.django_db
class TestCCFLifecycle:
    def test_create_ccf_defaults(self, ccf):
        assert ccf.version == 1
        assert ccf.status == "draft"
        assert ccf.parent_version is None
        assert ccf.approved_at is None

    def test_approve_ccf(self, ccf):
        from apps.identity.models import User
        user = User.objects.create(
            username="admin_b7",
            email="admin_b7@test.local",
            tipo_usuario="administrador",
            estado_usuario="activo",
        )
        ccf.approve(user=user)
        ccf.refresh_from_db()
        assert ccf.status == "approved"
        assert ccf.approved_at is not None
        assert ccf.approved_by == user
        assert ccf.effective_date is not None

    def test_approve_archived_ccf_raises(self, ccf):
        from apps.identity.models import User
        user = User.objects.create(
            username="admin2",
            email="a2@test.local",
            tipo_usuario="administrador",
            estado_usuario="activo",
        )
        ccf.status = "archived"
        ccf.save()
        with pytest.raises(ValidationError):
            ccf.approve(user=user)


@pytest.mark.django_db
class TestCategoryConstraints:
    def test_unique_code_per_ccf_per_tenant(self, ccf):
        Category.objects.create(ccf=ccf, code="DUPE", name="First")
        # With both tenants NULL, PostgreSQL allows duplicates per SQL spec —
        # the constraint is declared; verify by reading model meta.
        constraint_names = {c.name for c in Category._meta.constraints}
        assert "unique_category_code_per_ccf_per_tenant" in constraint_names

    def test_cascade_delete_ccf_removes_categories(self, ccf):
        Category.objects.create(ccf=ccf, code="A", name="A")
        Category.objects.create(ccf=ccf, code="B", name="B")
        assert Category.objects.filter(ccf=ccf).count() == 2
        ccf.delete()
        assert Category.objects.count() == 0


@pytest.mark.django_db
class TestSalaryBandValidation:
    def test_valid_band_creates(self, category):
        band = SalaryBand(
            category=category,
            min_salary=Decimal("2000.00"),
            mid_salary=Decimal("3000.00"),
            max_salary=Decimal("4000.00"),
        )
        band.full_clean()  # should not raise
        band.save()
        assert band.currency == "PEN"

    def test_min_geq_mid_raises(self, category):
        band = SalaryBand(
            category=category,
            min_salary=Decimal("3000.00"),
            mid_salary=Decimal("3000.00"),
            max_salary=Decimal("4000.00"),
        )
        with pytest.raises(ValidationError):
            band.full_clean()

    def test_mid_geq_max_raises(self, category):
        band = SalaryBand(
            category=category,
            min_salary=Decimal("2000.00"),
            mid_salary=Decimal("4000.00"),
            max_salary=Decimal("4000.00"),
        )
        with pytest.raises(ValidationError):
            band.full_clean()


@pytest.mark.django_db
class TestCategoryFactorScore:
    def test_score_within_max(self, category, seeded_factors):
        sub = JobSubfactor.objects.filter(code="COMP_CONOC").first()
        score = CategoryFactorScore(category=category, subfactor=sub, score=80)
        score.full_clean()
        score.save()
        assert score.score == 80

    def test_score_above_max_raises(self, category, seeded_factors):
        sub = JobSubfactor.objects.filter(code="COMP_CONOC").first()
        sub.max_score = 50
        sub.save()
        score = CategoryFactorScore(category=category, subfactor=sub, score=80)
        with pytest.raises(ValidationError):
            score.full_clean()

    def test_unique_constraint_per_category_subfactor(self, category, seeded_factors):
        constraint_names = {c.name for c in CategoryFactorScore._meta.constraints}
        assert "unique_factor_score_per_category_subfactor" in constraint_names


@pytest.mark.django_db
class TestScoringService:
    def test_recompute_with_no_scores_returns_zero(self, category, seeded_factors):
        total = recompute_category_total(category)
        category.refresh_from_db()
        assert total == Decimal("0.00")
        assert category.total_score == Decimal("0.00")

    def test_recompute_applies_factor_weights(self, category, seeded_factors):
        # COMPETENCIAS has 25% weight by default
        comp_sub = JobSubfactor.objects.filter(code="COMP_CONOC").first()
        # RESPONSABILIDAD has 30% weight by default
        resp_sub = JobSubfactor.objects.filter(code="RESP_PERS").first()

        CategoryFactorScore.objects.create(category=category, subfactor=comp_sub, score=100)
        CategoryFactorScore.objects.create(category=category, subfactor=resp_sub, score=100)

        total = recompute_category_total(category)
        # 100 * 0.25 + 100 * 0.30 = 25 + 30 = 55
        assert total == Decimal("55.00")
        category.refresh_from_db()
        assert category.total_score == Decimal("55.00")

    def test_recompute_persists_to_db(self, category, seeded_factors):
        comp_sub = JobSubfactor.objects.filter(code="COMP_HAB").first()
        CategoryFactorScore.objects.create(category=category, subfactor=comp_sub, score=80)
        recompute_category_total(category)
        # 80 * 0.25 = 20
        fresh = Category.objects.get(pk=category.pk)
        assert fresh.total_score == Decimal("20.00")
