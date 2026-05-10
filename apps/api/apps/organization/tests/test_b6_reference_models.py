"""Tests for B.6 OccupationalCategory + CIUOCode reference data."""
import pytest
from django.core.management import call_command

from apps.organization.models import CIUOCode, OccupationalCategory


@pytest.mark.django_db
class TestOccupationalCategorySeeder:
    def test_seed_command_creates_three_categories(self):
        call_command("seed_occupational_data")
        assert OccupationalCategory.objects.count() >= 3
        assert OccupationalCategory.objects.filter(code="01").exists()
        assert OccupationalCategory.objects.filter(code="02").exists()
        assert OccupationalCategory.objects.filter(code="03").exists()

    def test_seed_command_is_idempotent(self):
        call_command("seed_occupational_data")
        first_count = OccupationalCategory.objects.count()
        call_command("seed_occupational_data")
        assert OccupationalCategory.objects.count() == first_count


@pytest.mark.django_db
class TestCIUOCodeSeeder:
    def test_seed_command_creates_ciuo_codes(self):
        call_command("seed_occupational_data")
        # We seeded ~80 codes
        assert CIUOCode.objects.count() >= 50

    def test_ciuo_code_has_big_group(self):
        call_command("seed_occupational_data")
        sample = CIUOCode.objects.first()
        assert sample is not None
        assert sample.big_group  # non-empty

    def test_ciuo_code_str_representation(self):
        cat = CIUOCode.objects.create(code="9999", name="Test code")
        assert "9999" in str(cat)
        assert "Test code" in str(cat)
