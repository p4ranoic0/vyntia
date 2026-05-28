"""D.3 — Compensation versioned tenant-scoped snapshot."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


User = get_user_model()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="t1_staff",
        email="t1_staff@test.local",
        password="pw",
        nombres_usuario="Staff",
        apellidos_usuario="User",
    )


@pytest.fixture
def tenant(db, staff_user):
    return Tenant.objects.create(
        slug="comp-t1", name="T1", ruc="20111111112", plan="starter", status="active",
        created_by=staff_user,
    )


@pytest.fixture
def employee(db, tenant):
    return Employee.objects.create(
        tenant=tenant,
        numero_documento="11111111", tipo_documento="DNI",
        nombres_empleado="Ana", apellido_paterno="Pérez", apellido_materno="Lopez",
        correo_personal="ana.perez@test.local",
    )


@pytest.mark.django_db
class TestCompensationLookup:
    def test_current_for_returns_active_version(self, tenant, employee):
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2024, 1, 1),
            valid_to=date(2024, 12, 31), base_salary=Decimal("2500.00"),
            regimen_laboral="728", pension_regime="ONP", health_regime="ESSALUD",
            source="MIGRATION",
        )
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
            valid_to=None, base_salary=Decimal("3000.00"),
            regimen_laboral="728", pension_regime="ONP", health_regime="ESSALUD",
            source="MANUAL",
        )
        assert Compensation.current_for(employee, date(2024, 6, 1)).base_salary == Decimal("2500.00")
        assert Compensation.current_for(employee, date(2026, 6, 1)).base_salary == Decimal("3000.00")

    def test_current_for_returns_none_when_no_row(self, employee):
        assert Compensation.current_for(employee, date(2024, 6, 1)) is None


@pytest.mark.django_db
class TestCompensationConstraints:
    def test_unique_employee_valid_from(self, tenant, employee):
        Compensation.objects.create(
            tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
            base_salary=Decimal("3000.00"), regimen_laboral="728",
            pension_regime="ONP", health_regime="ESSALUD", source="MANUAL",
        )
        with pytest.raises(IntegrityError):
            Compensation.objects.create(
                tenant=tenant, employee=employee, valid_from=date(2025, 1, 1),
                base_salary=Decimal("3500.00"), regimen_laboral="728",
                pension_regime="ONP", health_regime="ESSALUD", source="MANUAL",
            )
