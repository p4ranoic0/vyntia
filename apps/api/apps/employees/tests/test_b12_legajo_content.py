"""Tests for B.12 legajo content — WorkExperience + SwornDeclaration + JobHistory."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import (
    Employee,
    JobHistory,
    SwornDeclaration,
    WorkExperience,
)


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='20202020', tipo_documento='DNI',
        nombres_empleado='Diego', apellido_paterno='Vargas',
        apellido_materno='Mora', fecha_nacimiento=date(1989, 8, 8),
        estado_empleado='activo',
    )


@pytest.mark.django_db
class TestWorkExperience:
    def test_create_minimal(self, employee):
        w = WorkExperience.objects.create(
            employee=employee, employer='ACME', position_title='Analista',
            start_date=date(2020, 1, 1), end_date=date(2022, 12, 31),
        )
        assert w.id is not None
        assert w.sector == 'privado'

    def test_clean_rejects_end_before_start(self, employee):
        w = WorkExperience(
            employee=employee, employer='X', position_title='Y',
            start_date=date(2020, 12, 31), end_date=date(2020, 1, 1),
        )
        with pytest.raises(ValidationError):
            w.clean()

    def test_clean_rejects_is_current_with_end_date(self, employee):
        w = WorkExperience(
            employee=employee, employer='X', position_title='Y',
            start_date=date(2020, 1, 1), end_date=date(2022, 1, 1),
            is_current=True,
        )
        with pytest.raises(ValidationError):
            w.clean()

    def test_sector_choices(self):
        kinds = {k for k, _ in WorkExperience.SECTOR_CHOICES}
        assert kinds == {'privado', 'publico', 'ong', 'autonomo'}


@pytest.mark.django_db
class TestSwornDeclaration:
    def test_create_4_kinds(self, employee):
        for kind in ('no_parentesco', 'no_incompatibilidad', 'intereses', 'impedimentos'):
            SwornDeclaration.objects.create(
                employee=employee, kind=kind, declared_at=date.today(),
            )
        assert SwornDeclaration.objects.filter(employee=employee).count() == 4

    def test_default_is_active_true(self, employee):
        s = SwornDeclaration.objects.create(
            employee=employee, kind='intereses', declared_at=date.today(),
        )
        assert s.is_active is True

    def test_valid_until_optional(self, employee):
        s = SwornDeclaration.objects.create(
            employee=employee, kind='no_parentesco', declared_at=date.today(),
            valid_until=date.today() + timedelta(days=365),
        )
        assert s.valid_until is not None


@pytest.mark.django_db
class TestJobHistory:
    def test_create(self, employee):
        h = JobHistory.objects.create(
            employee=employee, position_label='Analista',
            department_label='RRHH', start_date=date(2024, 1, 1),
            motive='hiring',
        )
        assert h.id is not None

    def test_multiple_in_timeline(self, employee):
        JobHistory.objects.create(
            employee=employee, position_label='Asistente',
            start_date=date(2023, 1, 1), end_date=date(2024, 1, 1),
            motive='hiring',
        )
        JobHistory.objects.create(
            employee=employee, position_label='Analista',
            start_date=date(2024, 1, 1),
            motive='promotion',
        )
        assert JobHistory.objects.filter(employee=employee).count() == 2

    def test_ordering_by_start_date_desc(self, employee):
        h1 = JobHistory.objects.create(
            employee=employee, position_label='Old',
            start_date=date(2020, 1, 1), end_date=date(2022, 1, 1),
        )
        h2 = JobHistory.objects.create(
            employee=employee, position_label='New',
            start_date=date(2024, 1, 1),
        )
        rows = list(JobHistory.objects.filter(employee=employee))
        assert rows[0].id == h2.id
        assert rows[1].id == h1.id
