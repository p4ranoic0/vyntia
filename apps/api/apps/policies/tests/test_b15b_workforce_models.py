"""Tests for B.15b WorkforcePlan + HeadcountProjection + SuccessionPlan + KeyPosition + SuccessorCandidate models."""
from datetime import date
from decimal import Decimal

import pytest

from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department, Position
from apps.policies.models import (
    HeadcountProjection,
    KeyPosition,
    SuccessionPlan,
    SuccessorCandidate,
    WorkforcePlan,
)


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='wf_owner', email='wf@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='TI', siglas_area='TI', estado_area='activa',
    )


@pytest.fixture
def position(db, department):
    return Position.objects.create(
        code='POS-DEV-SR', name='Desarrollador Senior',
        department=department,
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='61616161', tipo_documento='DNI',
        nombres_empleado='Ana', apellido_paterno='García',
        apellido_materno='Soto', fecha_nacimiento=date(1985, 6, 15),
        estado_empleado='activo',
    )


@pytest.fixture
def workforce_plan(owner):
    return WorkforcePlan.objects.create(
        name='Dotación 2026', fiscal_year=2026,
        period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
        owner_user=owner,
    )


@pytest.mark.django_db
class TestWorkforcePlan:
    def test_create_default_draft(self, workforce_plan):
        assert workforce_plan.status == 'draft'
        assert 'Dotación 2026' in str(workforce_plan)


@pytest.mark.django_db
class TestHeadcountProjection:
    def test_delta_required_computed(self, workforce_plan, department, position):
        p = HeadcountProjection.objects.create(
            plan=workforce_plan, area=department, position=position,
            current_headcount=5, projected_headcount=8, target_quarter='Q2',
        )
        assert p.delta_required == 3

    def test_negative_delta(self, workforce_plan):
        p = HeadcountProjection.objects.create(
            plan=workforce_plan, current_headcount=10, projected_headcount=7,
        )
        assert p.delta_required == -3

    def test_global_projection_without_area(self, workforce_plan):
        p = HeadcountProjection.objects.create(
            plan=workforce_plan, current_headcount=100, projected_headcount=120,
            target_quarter='Q4',
        )
        assert p.area is None
        assert p.position is None


@pytest.fixture
def succession_plan(owner):
    return SuccessionPlan.objects.create(
        name='Sucesión 2026', fiscal_year=2026, owner_user=owner,
    )


@pytest.mark.django_db
class TestSuccessionPlan:
    def test_unique_name_per_year(self, owner):
        from apps.tenancy.models import Tenant
        t = Tenant.objects.create(
            slug='acme-succ', name='ACME', ruc='20100000003',
            plan='starter', status='active', created_by=owner,
        )
        SuccessionPlan.objects.create(
            tenant=t, name='X', fiscal_year=2026, owner_user=owner,
        )
        with pytest.raises(Exception):
            SuccessionPlan.objects.create(
                tenant=t, name='X', fiscal_year=2026, owner_user=owner,
            )


@pytest.mark.django_db
class TestKeyPosition:
    def test_unique_position_per_plan(self, succession_plan, position):
        KeyPosition.objects.create(
            plan=succession_plan, position=position, criticality='alta',
        )
        with pytest.raises(Exception):
            KeyPosition.objects.create(
                plan=succession_plan, position=position, criticality='media',
            )


@pytest.mark.django_db
class TestSuccessorCandidate:
    def test_create_candidate(self, succession_plan, position, employee):
        kp = KeyPosition.objects.create(
            plan=succession_plan, position=position, criticality='alta',
        )
        c = SuccessorCandidate.objects.create(
            key_position=kp, employee=employee, readiness_level=1, order=1,
        )
        assert c.readiness_level == 1
        assert 'readiness=1' in str(c)

    def test_unique_employee_per_key_position(self, succession_plan, position, employee):
        kp = KeyPosition.objects.create(
            plan=succession_plan, position=position, criticality='alta',
        )
        SuccessorCandidate.objects.create(
            key_position=kp, employee=employee, readiness_level=2,
        )
        with pytest.raises(Exception):
            SuccessorCandidate.objects.create(
                key_position=kp, employee=employee, readiness_level=3,
            )
