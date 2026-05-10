"""Tests for B.6 Plaza assignment workflow."""
import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.organization.models import Department, Plaza, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test",
        nombre_unidad_organica="Test",
        siglas_area="T",
        unit_type="area",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(
        code="ANA-001",
        name="Analista I",
        department=department,
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        nombres_empleado="Juan",
        apellido_paterno="Perez",
        apellido_materno="Lopez",
        numero_documento="12345678",
        correo_personal="juan.perez@test.local",
        estado_empleado="activo",
    )


@pytest.fixture
def another_employee(db):
    return Employee.objects.create(
        nombres_empleado="Maria",
        apellido_paterno="Garcia",
        apellido_materno="Torres",
        numero_documento="87654321",
        correo_personal="maria.garcia@test.local",
        estado_empleado="activo",
    )


@pytest.mark.django_db
class TestPlazaCreate:
    def test_create_plaza_defaults_to_vacante(self, position):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        assert plaza.status == "vacante"
        assert plaza.current_employee is None


@pytest.mark.django_db
class TestPlazaWorkflow:
    def test_occupy_assigns_employee_and_flips_status(self, position, employee):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.occupy(employee)
        plaza.refresh_from_db()
        assert plaza.status == "ocupada"
        assert plaza.current_employee == employee

    def test_vacate_unassigns_and_flips_status(self, position, employee):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.occupy(employee)
        plaza.vacate()
        plaza.refresh_from_db()
        assert plaza.status == "vacante"
        assert plaza.current_employee is None

    def test_occupy_idempotent_on_same_employee(self, position, employee):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.occupy(employee)
        plaza.occupy(employee)  # idempotent
        plaza.refresh_from_db()
        assert plaza.status == "ocupada"
        assert plaza.current_employee == employee

    def test_cannot_occupy_already_occupied_plaza(
        self, position, employee, another_employee
    ):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.occupy(employee)
        with pytest.raises(ValidationError):
            plaza.occupy(another_employee)

    def test_cannot_occupy_eliminada_plaza(self, position, employee):
        plaza = Plaza.objects.create(
            code="PLAZA-001", position=position, status="eliminada"
        )
        with pytest.raises(ValidationError):
            plaza.occupy(employee)

    def test_freeze_moves_to_congelada(self, position):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.freeze()
        plaza.refresh_from_db()
        assert plaza.status == "congelada"

    def test_soft_delete_unassigns_and_marks_eliminada(self, position, employee):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.occupy(employee)
        plaza.soft_delete()
        plaza.refresh_from_db()
        assert plaza.status == "eliminada"
        assert plaza.current_employee is None

    def test_occupy_after_freeze_works(self, position, employee):
        plaza = Plaza.objects.create(code="PLAZA-001", position=position)
        plaza.freeze()
        plaza.occupy(employee)
        plaza.refresh_from_db()
        assert plaza.status == "ocupada"
        assert plaza.current_employee == employee
