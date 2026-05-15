"""Tests for B.11 probation_service."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.contracts.models import Contract, ProbationPeriod
from apps.contracts.services import probation_service
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
        numero_documento='60606060', tipo_documento='DNI',
        nombres_empleado='Tania', apellido_paterno='Mora',
        apellido_materno='Cruz', fecha_nacimiento=date(1990, 6, 6),
        estado_empleado='activo',
    )


def _make_contract(employee, department, num):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato=f'CON-B11s-{num}', tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'), cargo='X', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b11ps', email='hr_b11ps@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestCreateForContract:
    def test_defaults_to_728_comun_90d(self, employee, department):
        c = _make_contract(employee, department, '001')
        p = probation_service.create_for_contract(contract=c)
        assert p.regimen == '728_comun'
        assert p.plazo_dias == 90

    def test_uses_contract_fecha_inicio(self, employee, department):
        c = _make_contract(employee, department, '002')
        c.fecha_inicio = date(2026, 1, 1)
        c.save()
        p = probation_service.create_for_contract(contract=c, regimen='728_calificado')
        assert p.start_date == date(2026, 1, 1)
        assert p.plazo_dias == 180


@pytest.mark.django_db
class TestListOverdue:
    def test_excludes_decided(self, employee, department, hr_user):
        c1 = _make_contract(employee, department, '101')
        c2 = _make_contract(employee, department, '102')
        # Both overdue
        for c in (c1, c2):
            p = ProbationPeriod.objects.create(
                contract=c, regimen='728_comun',
                start_date=date.today() - timedelta(days=120),
            )
        p2 = ProbationPeriod.objects.get(contract=c2)
        p2.mark_evaluated(score=80, evaluator=hr_user)
        p2.mark_ratified(user=hr_user)
        overdue = probation_service.list_overdue()
        ids = {p.id for p in overdue}
        assert ProbationPeriod.objects.get(contract=c1).id in ids
        assert p2.id not in ids


@pytest.mark.django_db
class TestAlertas:
    def test_alertas_30d(self, employee, department):
        c1 = _make_contract(employee, department, '201')
        # 25 days remaining
        ProbationPeriod.objects.create(
            contract=c1, regimen='728_comun',
            start_date=date.today() - timedelta(days=65),
        )
        rows = list(probation_service.list_alertas_30d())
        assert len(rows) == 1

    def test_alertas_15d_subset_of_30d(self, employee, department):
        c1 = _make_contract(employee, department, '301')
        c2 = _make_contract(employee, department, '302')
        # c1: 25 days left → in 30d but not 15d
        ProbationPeriod.objects.create(
            contract=c1, regimen='728_comun',
            start_date=date.today() - timedelta(days=65),
        )
        # c2: 10 days left → in both
        ProbationPeriod.objects.create(
            contract=c2, regimen='728_comun',
            start_date=date.today() - timedelta(days=80),
        )
        rows_30 = list(probation_service.list_alertas_30d())
        rows_15 = list(probation_service.list_alertas_15d())
        ids_30 = {p.id for p in rows_30}
        ids_15 = {p.id for p in rows_15}
        assert ids_15.issubset(ids_30)
        assert len(rows_30) >= len(rows_15)
