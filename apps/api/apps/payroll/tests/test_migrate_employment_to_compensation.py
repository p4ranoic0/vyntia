"""D.3 — migrate_employment_to_compensation: one snapshot per active employee."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.audit_lite.models import AuditEvent
from apps.contracts.models import Contract, EmploymentData
from apps.employees.models import Employee
from apps.organization.models import Department
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


User = get_user_model()


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="mig_staff",
        email="mig_staff@test.local",
        password="pw",
        nombres_usuario="Mig",
        apellidos_usuario="Staff",
    )


@pytest.fixture
def tenant(db, staff_user):
    return Tenant.objects.create(
        slug="mig-t1", name="MigT1", ruc="20111111113", plan="starter", status="active",
        created_by=staff_user,
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica="RRHH Mig", siglas_area="RHM", estado_area="activa",
    )


@pytest.mark.django_db
class TestMigrateEmploymentToCompensation:
    def test_creates_one_compensation_per_active_employee_from_max_value(self, tenant, department):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="11111111", tipo_documento="DNI",
            nombres_empleado="Ana", apellido_paterno="Pérez", apellido_materno="Lopez",
            correo_personal="ana.m@test.local",
            sistema_pensiones="ONP", tipo_seguro_salud="ESSALUD",
        )
        EmploymentData.objects.create(
            tenant=tenant, empleado=emp, area=department,
            regimen_laboral="728",
            cargo_empleado="Analista", categoria="profesional",
            tipo_contrato="indefinido",
            sueldo_basico=Decimal("2800.00"), estado_datos="activo",
            fecha_ingreso=date(2024, 1, 15),
            fecha_inicio_contrato=date(2024, 1, 15),
        )
        Contract.objects.create(
            tenant=tenant, empleado=emp, area=department,
            numero_contrato="C-001",
            tipo_documento="LEY_728_INDETERMINADO",
            fecha_inicio=date(2024, 1, 15), salario_bruto=Decimal("3000.00"),
            cargo="Analista", status="ACTIVO",
        )

        call_command("migrate_employment_to_compensation")

        comp = Compensation.objects.get(employee=emp)
        assert comp.base_salary == Decimal("3000.00")  # max of 2800 vs 3000
        assert comp.regimen_laboral == "728"
        assert comp.pension_regime == "ONP"
        assert comp.health_regime == "ESSALUD"
        assert comp.source == "MIGRATION"
        assert comp.valid_from == date(2024, 1, 15)

        # Divergence (2800 vs 3000) → audit event
        event = AuditEvent.objects.get(action="payroll.compensation.migrated_with_divergence")
        assert event.target_id == str(emp.id)
        assert Decimal(event.payload_json["sueldo_basico"]) == Decimal("2800.00")
        assert Decimal(event.payload_json["salario_bruto"]) == Decimal("3000.00")

    def test_idempotent_skips_employees_with_existing_compensation(self, tenant, department):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="22222222", tipo_documento="DNI",
            nombres_empleado="Luis", apellido_paterno="Soto", apellido_materno="Diaz",
            correo_personal="luis.s@test.local",
            sistema_pensiones="AFP INTEGRA", tipo_seguro_salud="ESSALUD",
            tipo_comision="FLUJO",
        )
        EmploymentData.objects.create(
            tenant=tenant, empleado=emp, area=department,
            regimen_laboral="728",
            cargo_empleado="Desarrollador", categoria="profesional",
            tipo_contrato="indefinido",
            sueldo_basico=Decimal("3500.00"), estado_datos="activo",
            fecha_ingreso=date(2025, 1, 1),
            fecha_inicio_contrato=date(2025, 1, 1),
        )

        call_command("migrate_employment_to_compensation")
        before = Compensation.objects.filter(employee=emp).count()

        call_command("migrate_employment_to_compensation")
        after = Compensation.objects.filter(employee=emp).count()
        assert before == after == 1

    def test_skips_employees_without_active_employment_data(self, tenant):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="33333333", tipo_documento="DNI",
            nombres_empleado="Sin", apellido_paterno="Datos", apellido_materno="X",
            correo_personal="sin.datos@test.local",
        )
        call_command("migrate_employment_to_compensation")
        assert not Compensation.objects.filter(employee=emp).exists()
