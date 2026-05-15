"""Tests for B.11 ProbationPeriod model (Module 03.4)."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.contracts.models import Contract, ProbationPeriod
from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='RRHH', siglas_area='RH', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='70707070', tipo_documento='DNI',
        nombres_empleado='Iván', apellido_paterno='Soto',
        apellido_materno='León', fecha_nacimiento=date(1988, 2, 2),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B11-001', tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'), cargo='Analista', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b11p', email='hr_b11p@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestProbationPeriod:
    def test_create_persists_plazo_dias_from_regimen(self, contract):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=date.today(),
        )
        assert p.plazo_dias == 90

    def test_end_date_auto_computed_on_save(self, contract):
        start = date(2026, 5, 1)
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_calificado', start_date=start,
        )
        assert p.plazo_dias == 180
        assert p.end_date == start + timedelta(days=180)

    def test_276_carrera_3_year_plazo(self, contract):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='276_carrera', start_date=date.today(),
        )
        assert p.plazo_dias == 1095

    def test_no_aplica_regimen_zero_plazo(self, contract):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='no_aplica', start_date=date.today(),
        )
        assert p.plazo_dias == 0

    def test_mark_evaluated_promotes_status(self, contract, hr_user):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=date.today(),
        )
        p.mark_evaluated(score=85, evaluator=hr_user, competencies={'tecnico': 9})
        p.refresh_from_db()
        assert p.status == 'evaluated'
        assert p.evaluation_score == 85
        assert p.evaluator == hr_user

    def test_mark_ratified_only_from_evaluated(self, contract, hr_user):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=date.today(),
        )
        with pytest.raises(ValidationError):
            p.mark_ratified(user=hr_user)
        p.mark_evaluated(score=85, evaluator=hr_user)
        p.mark_ratified(user=hr_user)
        p.refresh_from_db()
        assert p.status == 'ratified'
        assert p.decided_by == hr_user

    def test_mark_not_renewed_requires_reason(self, contract, hr_user):
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=date.today(),
        )
        p.mark_evaluated(score=40, evaluator=hr_user)
        with pytest.raises(ValidationError):
            p.mark_not_renewed(user=hr_user, reason='')
        p.mark_not_renewed(user=hr_user, reason='Bajo desempeño')
        p.refresh_from_db()
        assert p.status == 'not_renewed'
        assert p.decision_reason == 'Bajo desempeño'

    def test_days_remaining(self, contract):
        start = date.today() - timedelta(days=60)
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=start,
        )
        # Plazo 90, started 60 days ago → 30 days remaining
        assert p.days_remaining == 30

    def test_is_within_30_days_boundary(self, contract):
        start = date.today() - timedelta(days=61)
        p = ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun', start_date=start,
        )
        assert p.days_remaining == 29
        assert p.is_within_30_days is True
        assert p.is_within_15_days is False
