"""Smoke tests for B.8 API endpoints (CPE/CAP/MPP routes + actions)."""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.models import Role, User, UserRole
from apps.organization.models import (
    Department,
    Position,
    PositionRegister,
    PositionRegisterEntry,
)


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test", nombre_unidad_organica="Test", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(
        code="DIR-001", name="Director", department=department,
        servir_group="dp", servir_level="dp_3",
    )


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username="hr_b8",
        email="hr_b8@test.local",
        password="Test1234!",
        nombres_usuario="HR",
        apellidos_usuario="B8",
        tipo_usuario="rrhh",
        nivel_acceso="total",
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol="Administrador RRHH",
        defaults={"estado_rol": "activo", "nivel_jerarquico": 2, "es_rol_sistema": True},
    )
    UserRole.objects.get_or_create(
        usuario=user,
        rol=role,
        defaults={"estado_asignacion": "activo"},
    )
    return user


@pytest.fixture
def auth_client(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")
    return client


@pytest.fixture
def cpe_register(db):
    return PositionRegister.objects.create(
        register_type="cpe", title="CPE 2026 - MEF",
    )


@pytest.fixture
def cap_register(db):
    return PositionRegister.objects.create(
        register_type="cap", title="CAP 2026 - MEF",
    )


@pytest.mark.django_db
class TestB8Routing:
    def test_position_registers_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/organization/position-registers/")
        assert response.status_code in (401, 403)

    def test_position_register_entries_requires_auth(self):
        client = APIClient()
        response = client.get("/api/v1/organization/position-register-entries/")
        assert response.status_code in (401, 403)

    def test_authenticated_user_lists_registers(self, auth_client, cpe_register):
        response = auth_client.get("/api/v1/organization/position-registers/")
        assert response.status_code == 200

    def test_filter_registers_by_type(self, auth_client, cpe_register, cap_register):
        response = auth_client.get(
            "/api/v1/organization/position-registers/?register_type=cpe"
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestB8RegisterActions:
    def test_approve_action(self, auth_client, cpe_register):
        url = f"/api/v1/organization/position-registers/{cpe_register.id}/approve/"
        response = auth_client.post(url, {}, format="json")
        assert response.status_code == 200
        cpe_register.refresh_from_db()
        assert cpe_register.status == "approved"

    def test_register_in_servir_action_requires_approval(self, auth_client, cpe_register):
        url = f"/api/v1/organization/position-registers/{cpe_register.id}/register-in-servir/"
        response = auth_client.post(url, {"reference": "REF-001"}, format="json")
        # Draft → blocked
        assert response.status_code == 400

    def test_register_in_servir_action_succeeds_after_approval(
        self, auth_client, cpe_register, admin_user,
    ):
        cpe_register.approve(user=admin_user)
        url = f"/api/v1/organization/position-registers/{cpe_register.id}/register-in-servir/"
        response = auth_client.post(url, {"reference": "SERVIR-001"}, format="json")
        assert response.status_code == 200
        cpe_register.refresh_from_db()
        assert cpe_register.status == "registered_servir"
        assert cpe_register.servir_registration_ref == "SERVIR-001"

    def test_register_in_servir_rejects_cap(self, auth_client, cap_register, admin_user):
        cap_register.approve(user=admin_user)
        url = f"/api/v1/organization/position-registers/{cap_register.id}/register-in-servir/"
        response = auth_client.post(url, {"reference": "REF-001"}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestB8MPPDownload:
    def test_mpp_html_returns_html(self, auth_client, cpe_register, position):
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=1,
            plaza_code="P-001", plaza_count=1,
        )
        url = f"/api/v1/organization/position-registers/{cpe_register.id}/mpp-html/"
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'].startswith('text/html')
        assert b"Manual de Perfiles de Puestos" in response.content
        assert b"DIR-001" in response.content

    def test_mpp_pdf_returns_pdf(self, auth_client, cpe_register, position):
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=1,
        )
        url = f"/api/v1/organization/position-registers/{cpe_register.id}/mpp-pdf/"
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert response['Content-Disposition'].startswith('attachment')
        assert response.content[:4] == b"%PDF"

    def test_mpp_html_rejects_cap(self, auth_client, cap_register):
        url = f"/api/v1/organization/position-registers/{cap_register.id}/mpp-html/"
        response = auth_client.get(url)
        assert response.status_code == 400


@pytest.mark.django_db
class TestB8EntryCRUD:
    def test_create_entry_via_api(self, auth_client, cpe_register, position):
        payload = {
            "register": str(cpe_register.id),
            "position": str(position.id),
            "sequence": 1,
            "plaza_code": "P-001",
            "plaza_count": 2,
            "situacion": "vacante",
            "nivel_organizacional": "Alta Dirección",
            "nivel_remunerativo": "DP-3",
        }
        response = auth_client.post(
            "/api/v1/organization/position-register-entries/",
            payload, format="json",
        )
        assert response.status_code == 201
        assert PositionRegisterEntry.objects.filter(register=cpe_register).count() == 1

    def test_filter_entries_by_register(self, auth_client, cpe_register, position):
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=1,
        )
        response = auth_client.get(
            f"/api/v1/organization/position-register-entries/?register={cpe_register.id}"
        )
        assert response.status_code == 200
