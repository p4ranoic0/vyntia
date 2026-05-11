"""Tests for B.9 Candidate model (external candidate)."""
import pytest
from django.db import IntegrityError

from apps.employees.models import Candidate


@pytest.fixture
def candidate(db):
    return Candidate.objects.create(
        document_type='dni',
        document_number='12345678',
        first_names='Juan',
        last_names='Pérez',
        email='juan.perez@example.com',
        years_experience=5,
        highest_education='Ingeniero de Sistemas',
        source='website',
    )


@pytest.mark.django_db
class TestCandidate:
    def test_create_minimal(self, candidate):
        assert candidate.id is not None
        assert candidate.is_active is True
        assert candidate.full_name == 'Juan Pérez'

    def test_full_name_strips(self, db):
        c = Candidate.objects.create(
            document_number='X', first_names='  Ana ', last_names='  Torres ',
            email='a@b.com',
        )
        assert c.full_name.startswith('Ana')

    def test_doc_type_choices(self):
        kinds = {k for k, _ in Candidate.DOC_TYPE_CHOICES}
        assert kinds == {'dni', 'ce', 'passport', 'ptp'}

    def test_unique_constraint_per_tenant(self):
        # With both tenants NULL, PostgreSQL allows duplicates per SQL spec.
        # Verify constraint is declared (will block once tenant context exists).
        constraint_names = {c.name for c in Candidate._meta.constraints}
        assert 'unique_candidate_doc_per_tenant' in constraint_names

    def test_default_values(self, candidate):
        assert candidate.years_experience == 5
        assert candidate.gender == ''
        assert candidate.is_active is True

    def test_string_repr(self, candidate):
        s = str(candidate)
        assert 'Juan Pérez' in s
        assert 'DNI' in s
        assert '12345678' in s

    def test_email_indexed(self):
        # Index existence
        index_field_sets = [tuple(i.fields) for i in Candidate._meta.indexes]
        assert ('tenant', 'email') in index_field_sets
        assert ('tenant', 'document_number') in index_field_sets
