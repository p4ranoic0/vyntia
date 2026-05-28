"""Shared fixtures + builders for D.4a engine tests."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.employees.models import Employee
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


@pytest.fixture
def seeded_catalog(db):
    """Run `seed_payroll_catalog` once per test that needs it."""
    call_command("seed_payroll_catalog")


@pytest.fixture
def tenant(db):
    User = get_user_model()
    staff = User.objects.create_user(
        username="engine_test_staff", email="engine_staff@vyntia.pe", password="testpass123"
    )
    return Tenant.objects.create(
        slug="t1", name="T1", ruc="20111111111", plan="starter", status="active",
        created_by=staff,
    )


def make_employee(
    tenant,
    *,
    sistema_pensiones="ONP",
    tipo_comision="",
    codigo_cuspp="",
    tipo_seguro_salud="ESSALUD",
    es_padre_familia=False,
    doc="11111111",
):
    return Employee.objects.create(
        tenant=tenant,
        numero_documento=doc, tipo_documento="DNI",
        nombres_empleado="A", apellido_paterno="B", apellido_materno="C",
        sistema_pensiones=sistema_pensiones,
        tipo_comision=tipo_comision or None,
        codigo_cuspp=codigo_cuspp or None,
        tipo_seguro_salud=tipo_seguro_salud,
        es_padre_familia=es_padre_familia,
        correo_personal="test@test.com",
    )


def make_compensation(
    tenant, employee,
    *,
    base_salary,
    has_family_allowance=False,
    pension_regime=None,  # inferred from employee.sistema_pensiones if None
    afp_commission_type=None,
    health_regime=None,
):
    if pension_regime is None:
        # employee.sistema_pensiones uses spaces ("AFP INTEGRA") — strategy snapshot uses underscores
        v = (employee.sistema_pensiones or "ONP").upper().replace(" ", "_")
        pension_regime = v if v.startswith("AFP_") or v == "ONP" else "ONP"
    if afp_commission_type is None:
        afp_commission_type = (employee.tipo_comision or "") if employee.tipo_comision else ""
    if health_regime is None:
        health_regime = "EPS" if (employee.tipo_seguro_salud or "").upper() == "EPS" else "ESSALUD"

    return Compensation.objects.create(
        tenant=tenant, employee=employee, valid_from=date(2024, 1, 1), valid_to=None,
        base_salary=Decimal(base_salary), has_family_allowance=has_family_allowance,
        regimen_laboral="728", pension_regime=pension_regime,
        afp_commission_type=afp_commission_type, cuspp=employee.codigo_cuspp or "",
        health_regime=health_regime, source="MIGRATION",
    )
