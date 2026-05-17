"""Tests for B.15b ComplianceMatrix + ComplianceObligation + Evidence models."""
from datetime import date, timedelta

import pytest

from apps.identity.models import User
from apps.policies.models import (
    ComplianceMatrix,
    ComplianceObligation,
    Evidence,
)


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='comp_owner', email='comp@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def matrix(owner):
    return ComplianceMatrix.objects.create(
        name='Matriz 2026', fiscal_year=2026, owner_user=owner,
    )


@pytest.mark.django_db
class TestComplianceMatrix:
    def test_default_active(self, matrix):
        assert matrix.status == 'active'

    def test_str(self, matrix):
        assert 'Matriz 2026' in str(matrix)

    def test_unique_name_per_year_per_tenant(self, owner):
        from apps.tenancy.models import Tenant
        t = Tenant.objects.create(
            slug='acme-comp', name='ACME', ruc='20100000004',
            plan='starter', status='active', created_by=owner,
        )
        ComplianceMatrix.objects.create(
            tenant=t, name='M', fiscal_year=2026, owner_user=owner,
        )
        with pytest.raises(Exception):
            ComplianceMatrix.objects.create(
                tenant=t, name='M', fiscal_year=2026, owner_user=owner,
            )


@pytest.mark.django_db
class TestComplianceObligation:
    def test_days_to_due(self, matrix):
        o = ComplianceObligation.objects.create(
            matrix=matrix, code='SUNAT-001', title='PDT 601',
            source='sunat', frequency='mensual',
            next_due_date=date.today() + timedelta(days=10),
        )
        assert o.days_to_due() == 10

    def test_is_overdue_past_due(self, matrix):
        o = ComplianceObligation.objects.create(
            matrix=matrix, code='SUNAT-002', title='PDT 601-2',
            source='sunat', frequency='mensual',
            next_due_date=date.today() - timedelta(days=2),
        )
        assert o.is_overdue() is True

    def test_is_overdue_when_completed(self, matrix):
        o = ComplianceObligation.objects.create(
            matrix=matrix, code='SUNAT-003', title='PDT 601-3',
            source='sunat', frequency='mensual',
            next_due_date=date.today() - timedelta(days=2),
            status='cumplido',
        )
        assert o.is_overdue() is False

    def test_unique_code_per_matrix(self, matrix):
        ComplianceObligation.objects.create(
            matrix=matrix, code='X-001', title='X',
            source='otro', frequency='unica',
            next_due_date=date.today(),
        )
        with pytest.raises(Exception):
            ComplianceObligation.objects.create(
                matrix=matrix, code='X-001', title='Otro',
                source='otro', frequency='unica',
                next_due_date=date.today(),
            )


@pytest.mark.django_db
class TestEvidence:
    def test_create_evidence_note(self, matrix):
        o = ComplianceObligation.objects.create(
            matrix=matrix, code='E-001', title='X',
            source='sunafil', frequency='anual',
            next_due_date=date.today(),
        )
        e = Evidence.objects.create(
            obligation=o, kind='nota', note='Subido al portal SUNAFIL',
        )
        assert e.kind == 'nota'
        assert 'nota' in str(e)

    def test_create_evidence_link(self, matrix):
        o = ComplianceObligation.objects.create(
            matrix=matrix, code='E-002', title='X',
            source='sunafil', frequency='anual',
            next_due_date=date.today(),
        )
        e = Evidence.objects.create(
            obligation=o, kind='link', url='https://sunafil.gob.pe/x',
        )
        assert e.url == 'https://sunafil.gob.pe/x'
