"""Tests for B.14 SeveranceSettlement + SeveranceLine models."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.contracts.models import (
    Contract,
    SeveranceLine,
    SeveranceSettlement,
    Termination,
)
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
        numero_documento='72727272', tipo_documento='DNI',
        nombres_empleado='Marco', apellido_paterno='Quispe',
        apellido_materno='Cruz', fecha_nacimiento=date(1990, 5, 5),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14-002', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=400),
        salario_bruto=Decimal('4000.00'), cargo='Especialista', status='ACTIVO',
    )


@pytest.fixture
def termination(contract, employee):
    return Termination.objects.create(
        contract=contract, employee=employee,
        regimen='728', causal='renuncia',
        fecha_cese=date.today(),
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b14s', email='hr_b14s@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestSeveranceSettlement:
    def test_create_defaults(self, termination):
        s = SeveranceSettlement.objects.create(
            termination=termination,
            sueldo_base=Decimal('4000.00'),
        )
        assert s.status == 'draft'
        assert s.total_amount == Decimal('0')

    def test_mark_computed_persists_user_and_timestamp(self, termination, hr_user):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
        )
        s.mark_computed(user=hr_user)
        s.refresh_from_db()
        assert s.status == 'computed'
        assert s.computed_by == hr_user
        assert s.computed_at is not None

    def test_mark_paid_requires_within_5pct(self, termination, hr_user):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
            total_amount=Decimal('1000.00'),
        )
        s.mark_computed(user=hr_user)
        with pytest.raises(ValidationError):
            s.mark_paid(paid_total=Decimal('2000.00'), user=hr_user)
        s.mark_paid(paid_total=Decimal('1040.00'), user=hr_user)
        s.refresh_from_db()
        assert s.status == 'paid'
        assert s.paid_amount == Decimal('1040.00')

    def test_mark_paid_blocked_when_not_computed(self, termination, hr_user):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
        )
        with pytest.raises(ValidationError):
            s.mark_paid(paid_total=Decimal('500.00'), user=hr_user)

    def test_recompute_total_sums_lines(self, termination):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
        )
        SeveranceLine.objects.create(
            settlement=s, component='cts', amount=Decimal('666.66'),
        )
        SeveranceLine.objects.create(
            settlement=s, component='vac_truncas', amount=Decimal('333.33'),
        )
        s.recompute_total()
        s.refresh_from_db()
        assert s.total_amount == Decimal('999.99')


@pytest.mark.django_db
class TestSeveranceLine:
    def test_unique_component_per_settlement(self, termination):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
        )
        SeveranceLine.objects.create(
            settlement=s, component='cts', amount=Decimal('100.00'),
        )
        with pytest.raises(Exception):
            SeveranceLine.objects.create(
                settlement=s, component='cts', amount=Decimal('200.00'),
            )

    def test_negative_amount_rejected(self, termination):
        s = SeveranceSettlement.objects.create(
            termination=termination, sueldo_base=Decimal('4000.00'),
        )
        line = SeveranceLine(
            settlement=s, component='cts', amount=Decimal('-1'),
        )
        with pytest.raises(ValidationError):
            line.full_clean()
