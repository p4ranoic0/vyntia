"""Tests for B.7 JobFactor + JobSubfactor seeder and model invariants."""
import pytest
from django.core.management import call_command

from apps.compensation.models import JobFactor, JobSubfactor


@pytest.mark.django_db
class TestJobFactorSeeder:
    def test_seed_creates_four_canonical_factors(self):
        call_command("seed_job_factors")
        assert JobFactor.objects.count() == 4
        kinds = set(JobFactor.objects.values_list("kind", flat=True))
        assert kinds == {"competencias", "responsabilidad", "esfuerzo", "condiciones"}

    def test_seed_creates_canonical_subfactors(self):
        call_command("seed_job_factors")
        # We seed 14 subfactors (3+4+4+3)
        assert JobSubfactor.objects.count() == 14
        # Each factor has its expected count
        assert JobSubfactor.objects.filter(factor__kind="competencias").count() == 3
        assert JobSubfactor.objects.filter(factor__kind="responsabilidad").count() == 4
        assert JobSubfactor.objects.filter(factor__kind="esfuerzo").count() == 4
        assert JobSubfactor.objects.filter(factor__kind="condiciones").count() == 3

    def test_seed_is_idempotent(self):
        call_command("seed_job_factors")
        first_factors = JobFactor.objects.count()
        first_subs = JobSubfactor.objects.count()
        call_command("seed_job_factors")
        assert JobFactor.objects.count() == first_factors
        assert JobSubfactor.objects.count() == first_subs

    def test_factor_weights_default_to_100_total(self):
        call_command("seed_job_factors")
        total_weight = sum(f.weight for f in JobFactor.objects.all())
        assert total_weight == 100

    def test_subfactor_str_representation(self):
        f = JobFactor.objects.create(kind="competencias", name="Test", weight=25)
        s = JobSubfactor.objects.create(
            factor=f, code="TEST-001", name="Test sub", max_score=50,
        )
        assert "TEST-001" in str(s)
        assert "Test sub" in str(s)
