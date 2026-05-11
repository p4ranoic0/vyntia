"""Tests for B.8 Position SERVIR fields (Ley 30057)."""
import pytest

from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test",
        nombre_unidad_organica="Test",
        siglas_area="T",
    )


@pytest.mark.django_db
class TestPositionServirFields:
    def test_position_servir_fields_default_null(self, department):
        """Private-sector tenants leave SERVIR fields blank/null."""
        pos = Position.objects.create(
            code="ANA-001", name="Analista", department=department,
        )
        assert pos.servir_group is None
        assert pos.servir_level is None
        assert pos.salary_tier is None
        assert pos.familia_puesto == ""

    def test_position_with_servir_classification(self, department):
        """Public-sector tenants populate SERVIR fields."""
        pos = Position.objects.create(
            code="DIR-001",
            name="Director General",
            department=department,
            servir_group="dp",
            servir_level="dp_3",
            salary_tier="principal",
            familia_puesto="Dirección institucional",
        )
        assert pos.servir_group == "dp"
        assert pos.get_servir_group_display() == "Directivo Público"
        assert pos.servir_level == "dp_3"
        assert pos.get_servir_level_display() == "DP-3"
        assert pos.salary_tier == "principal"
        assert pos.familia_puesto == "Dirección institucional"

    def test_servir_group_choices_cover_ley_30057_groups(self):
        """All 5 SERVIR servidor classifications per Ley 30057 Art. 2."""
        kinds = {k for k, _ in Position.SERVIR_GROUP_CHOICES}
        assert kinds == {"fp", "dp", "cc", "cs", "cf"}

    def test_servir_level_choices_cover_carrera_and_directivo(self):
        """CF-1..CF-4 for servidor de carrera + DP-1..DP-4 for directivo público."""
        levels = {k for k, _ in Position.SERVIR_LEVEL_CHOICES}
        assert levels == {
            "cf_1", "cf_2", "cf_3", "cf_4",
            "dp_1", "dp_2", "dp_3", "dp_4",
        }

    def test_salary_tier_choices_per_ds_138_2014(self):
        """D.S. 138-2014-EF defines 3 compensation tiers."""
        tiers = {k for k, _ in Position.SALARY_TIER_CHOICES}
        assert tiers == {"principal", "ajustada", "priorizada"}
