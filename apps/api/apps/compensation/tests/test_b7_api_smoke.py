"""Smoke tests for B.7 API endpoints (routing + auth gating + custom actions).

Defines a local hr_client fixture (JWT-authenticated client with Administrador
RRHH role) since pytest does not auto-discover the conftest at apps/api/tests/
from apps/api/apps/compensation/tests/.
"""
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.compensation.models import (
    Category,
    CategoryFunctionTable,
    JobSubfactor,
)
from apps.identity.models import Role, User, UserRole


@pytest.fixture
def api_client(db):
    return APIClient()


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username="hr_b7",
        email="hr_b7@test.local",
        password="Test1234!",
        nombres_usuario="HR",
        apellidos_usuario="B7",
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
def hr_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")
    return client


@pytest.fixture
def seeded(db):
    call_command("seed_job_factors")


@pytest.mark.django_db
class TestB7Routing:
    def test_ccf_endpoint_requires_auth(self, api_client):
        response = api_client.get("/api/v1/compensation/ccfs/")
        assert response.status_code in (401, 403)

    def test_categories_endpoint_requires_auth(self, api_client):
        response = api_client.get("/api/v1/compensation/categories/")
        assert response.status_code in (401, 403)

    def test_job_factors_endpoint_authenticated(self, hr_client, seeded):
        response = hr_client.get("/api/v1/compensation/job-factors/")
        assert response.status_code == 200

    def test_job_subfactors_endpoint_authenticated(self, hr_client, seeded):
        response = hr_client.get("/api/v1/compensation/job-subfactors/")
        assert response.status_code == 200

    def test_audit_endpoint_smoke(self, hr_client, seeded):
        # No data — empty rows but 200 OK
        response = hr_client.get("/api/v1/compensation/audit/salary-gap/")
        assert response.status_code == 200

    def test_template_excel_endpoint_smoke(self, hr_client, seeded):
        response = hr_client.get("/api/v1/compensation/ccf/template-excel/")
        assert response.status_code == 200
        assert response['Content-Type'].startswith('application/vnd.openxmlformats')

    def test_import_excel_requires_file(self, hr_client, seeded):
        response = hr_client.post(
            "/api/v1/compensation/ccf/import-excel/",
            data={"ccf_title": "Test CCF"},
        )
        # File is required → 400 from serializer
        assert response.status_code == 400


@pytest.mark.django_db
class TestB7CCFLifecycleAPI:
    def test_create_then_approve_ccf(self, hr_client, seeded):
        # Create
        response = hr_client.post(
            "/api/v1/compensation/ccfs/",
            data={"title": "Mi CCF 2026"},
            format="json",
        )
        assert response.status_code in (200, 201)
        ccf_id = (
            response.data.get("data", {}).get("id")
            if isinstance(response.data.get("data"), dict)
            else response.data.get("id")
        )
        assert ccf_id is not None

        # Approve
        response = hr_client.post(
            f"/api/v1/compensation/ccfs/{ccf_id}/approve/",
            data={},
            format="json",
        )
        assert response.status_code == 200
        ccf = CategoryFunctionTable.objects.get(pk=ccf_id)
        assert ccf.status == "approved"


@pytest.mark.django_db
class TestB7FactorScoreAutoRecompute:
    def test_creating_factor_score_via_api_recomputes_total(self, hr_client, seeded):
        ccf = CategoryFunctionTable.objects.create(title="Test")
        cat = Category.objects.create(ccf=ccf, code="X", name="X")
        sub = JobSubfactor.objects.filter(code="COMP_CONOC").first()

        response = hr_client.post(
            "/api/v1/compensation/factor-scores/",
            data={
                "category": str(cat.id),
                "subfactor": str(sub.id),
                "score": 80,
            },
            format="json",
        )
        assert response.status_code in (200, 201)
        cat.refresh_from_db()
        # 80 * 0.25 = 20.00
        assert str(cat.total_score) == "20.00"
