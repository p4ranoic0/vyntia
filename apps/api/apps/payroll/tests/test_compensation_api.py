"""D.3 — Compensation CRUD API + history per employee."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.payroll.models import Compensation
from apps.tenancy.models import Tenant


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username="api_staff",
        email="api_staff@test.local",
        password="pw",
        nombres_usuario="API",
        apellidos_usuario="Staff",
    )


@pytest.fixture
def tenant(db, staff_user):
    return Tenant.objects.create(
        slug="api-t1", name="APIT1", ruc="20111111114", plan="starter", status="active",
        created_by=staff_user,
    )


@pytest.fixture
def hr_user(db):
    """HR user with Administrador RRHH role — satisfies RRHHPermission."""
    user = User.objects.create_user(
        username="hr_comp_api",
        email="hr_comp_api@test.local",
        password="Test1234!",
        nombres_usuario="HR",
        apellidos_usuario="CompAPI",
        tipo_usuario="rrhh",
        nivel_acceso="total",
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol="Administrador RRHH",
        defaults={"estado_rol": "activo", "nivel_jerarquico": 2, "es_rol_sistema": True},
    )
    UserRole.objects.get_or_create(
        usuario=user, rol=role,
        defaults={"estado_asignacion": "activo"},
    )
    return user


@pytest.fixture
def hr_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")
    return client


@pytest.fixture
def anon_client():
    return APIClient()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCompensationApi:
    def test_list_create_history(self, tenant, hr_client):
        emp = Employee.objects.create(
            tenant=tenant, numero_documento="11111111", tipo_documento="DNI",
            nombres_empleado="A", apellido_paterno="B", apellido_materno="C",
            correo_personal="a.b@test.local",
        )
        Compensation.objects.create(
            tenant=tenant, employee=emp, valid_from=date(2025, 1, 1),
            base_salary=Decimal("3000.00"), regimen_laboral="728",
            pension_regime="ONP", health_regime="ESSALUD", source="MIGRATION",
        )

        # LIST
        resp = hr_client.get("/api/v1/payroll/compensations/")
        assert resp.status_code == 200
        data = resp.data.get("data", resp.data) if hasattr(resp.data, "get") else resp.data
        # DRF DefaultRouter returns a list or paginated object
        items = data if isinstance(data, list) else data.get("results", data)
        assert len(items) >= 1

        # HISTORY endpoint
        hist = hr_client.get(f"/api/v1/payroll/compensations/history/{emp.id}/")
        assert hist.status_code == 200

        # CREATE new version
        new = hr_client.post("/api/v1/payroll/compensations/", {
            "employee": str(emp.id), "valid_from": "2026-01-01",
            "base_salary": "3500.00", "regimen_laboral": "728",
            "pension_regime": "ONP", "health_regime": "ESSALUD",
            "source": "MANUAL",
        }, format="json")
        assert new.status_code == 201, new.data
        assert Compensation.objects.filter(employee=emp).count() == 2

    def test_unauthenticated_rejected(self, anon_client):
        assert anon_client.get("/api/v1/payroll/compensations/").status_code in (401, 403)
