"""Tests for B.7 salary-gap audit service (Ley 30709 § 8)."""
from datetime import date
from decimal import Decimal

import pytest

from apps.compensation.models import Category, CategoryFunctionTable
from apps.compensation.services import (
    compute_salary_gap_by_category,
    summarize_gap,
)
from apps.contracts.models import EmploymentData
from apps.employees.models import Employee
from apps.organization.models import Department, Position


@pytest.fixture
def ccf(db):
    return CategoryFunctionTable.objects.create(title="CCF Test")


@pytest.fixture
def category(ccf):
    return Category.objects.create(ccf=ccf, code="ANA", name="Analista")


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test",
        nombre_unidad_organica="Test",
        siglas_area="T",
    )


@pytest.fixture
def position(department, category):
    return Position.objects.create(
        code="ANA-001",
        name="Analista",
        department=department,
        category=category,
    )


def _make_employee(numero, genero, salario, position, department):
    emp = Employee.objects.create(
        nombres_empleado=f"Emp{numero}",
        apellido_paterno="Test",
        apellido_materno="X",
        numero_documento=numero,
        correo_personal=f"{numero}@test.local",
        estado_empleado="activo",
        genero_empleado=genero,
    )
    EmploymentData.objects.create(
        empleado=emp,
        area=department,
        cargo_empleado="Analista",
        categoria="profesional",
        tipo_contrato="CAS",
        regimen_laboral="cas",
        fecha_ingreso=date(2024, 1, 1),
        fecha_inicio_contrato=date(2024, 1, 1),
        sueldo_basico=Decimal(salario),
        estado_datos="activo",
        position=position,
    )
    return emp


@pytest.mark.django_db
class TestSalaryGapAudit:
    def test_no_employees_returns_zero_brecha(self, category):
        rows = compute_salary_gap_by_category()
        assert len(rows) == 1
        assert rows[0]["brecha_pct"] == Decimal("0.00")
        assert rows[0]["alert"] is False

    def test_equal_salaries_no_alert(self, category, position, department):
        _make_employee("11111111", "masculino", 5000, position, department)
        _make_employee("22222222", "femenino", 5000, position, department)
        rows = compute_salary_gap_by_category()
        assert rows[0]["brecha_pct"] == Decimal("0.00")
        assert rows[0]["alert"] is False

    def test_11pct_brecha_triggers_alert(self, category, position, department):
        _make_employee("10000001", "masculino", 5200, position, department)
        _make_employee("10000002", "masculino", 5200, position, department)
        _make_employee("20000001", "femenino", 4600, position, department)
        _make_employee("20000002", "femenino", 4600, position, department)
        rows = compute_salary_gap_by_category()
        # brecha = (5200 - 4600) / 5200 * 100 = 11.54%
        assert rows[0]["brecha_pct"] == Decimal("11.54")
        assert rows[0]["alert"] is True

    def test_negative_brecha_alerts_too(self, category, position, department):
        # Women earn more — also a brecha to flag (|brecha| > 5%)
        _make_employee("30000001", "masculino", 4000, position, department)
        _make_employee("30000002", "femenino", 5000, position, department)
        rows = compute_salary_gap_by_category()
        # (4000 - 5000) / 4000 * 100 = -25.00
        assert rows[0]["brecha_pct"] == Decimal("-25.00")
        assert rows[0]["alert"] is True

    def test_brecha_under_5pct_no_alert(self, category, position, department):
        _make_employee("40000001", "masculino", 5000, position, department)
        _make_employee("40000002", "femenino", 4900, position, department)
        rows = compute_salary_gap_by_category()
        # (5000 - 4900) / 5000 = 2.00
        assert rows[0]["brecha_pct"] == Decimal("2.00")
        assert rows[0]["alert"] is False

    def test_returns_counts_per_group(self, category, position, department):
        _make_employee("50000001", "masculino", 5000, position, department)
        _make_employee("50000002", "masculino", 5000, position, department)
        _make_employee("50000003", "masculino", 5000, position, department)
        _make_employee("50000004", "femenino", 4500, position, department)
        rows = compute_salary_gap_by_category()
        assert rows[0]["group_male"]["count"] == 3
        assert rows[0]["group_female"]["count"] == 1

    def test_filter_by_ccf_id(self, ccf, position, department):
        # Create another CCF with its own category
        other_ccf = CategoryFunctionTable.objects.create(title="Other CCF")
        Category.objects.create(ccf=other_ccf, code="OTHER", name="Other")

        rows_all = compute_salary_gap_by_category()
        rows_filtered = compute_salary_gap_by_category(ccf_id=ccf.id)
        assert len(rows_all) == 2
        assert len(rows_filtered) == 1
        assert rows_filtered[0]["category_code"] == "ANA"


@pytest.mark.django_db
class TestSummarizeGap:
    def test_empty_rows(self):
        out = summarize_gap([])
        assert out["total_categories"] == 0
        assert out["alerted_categories"] == 0
        assert out["overall_brecha_pct"] == Decimal("0.00")

    def test_aggregates_counts_and_alerts(self, category, position, department):
        _make_employee("60000001", "masculino", 5000, position, department)
        _make_employee("60000002", "femenino", 4000, position, department)
        rows = compute_salary_gap_by_category()
        out = summarize_gap(rows)
        assert out["total_categories"] == 1
        assert out["alerted_categories"] == 1  # 20% brecha
        assert out["total_male_employees"] == 1
        assert out["total_female_employees"] == 1
