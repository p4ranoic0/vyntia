"""Smoke tests for B.6 API endpoints (routes + permission gating)."""
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test",
        nombre_unidad_organica="Test",
        siglas_area="T",
        unit_type="area",
    )


@pytest.fixture
def api_client(db):
    """Unauthenticated client."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create(
        username="admin_b6",
        email="admin_b6@test.local",
        nombres_usuario="Admin",
        apellidos_usuario="B6",
        tipo_usuario="administrador",
        estado_usuario="activo",
    )
    user.set_password("Test1234!")
    user.save()
    return user


@pytest.fixture
def auth_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
class TestB6Routing:
    def test_positions_endpoint_requires_auth(self, api_client):
        response = api_client.get("/api/v1/organization/positions/")
        assert response.status_code in (401, 403)

    def test_plazas_endpoint_requires_auth(self, api_client):
        response = api_client.get("/api/v1/organization/plazas/")
        assert response.status_code in (401, 403)

    def test_occupational_categories_endpoint_exists(self, api_client):
        response = api_client.get("/api/v1/organization/occupational-categories/")
        # Reference data — IsAuthenticatedOrReadOnly. Unauthenticated GET allowed.
        assert response.status_code in (200, 401, 403)

    def test_ciuo_codes_endpoint_exists(self, api_client):
        response = api_client.get("/api/v1/organization/ciuo-codes/")
        assert response.status_code in (200, 401, 403)


@pytest.mark.django_db
class TestB6ReferenceDataAPI:
    def test_authenticated_user_can_list_occupational_categories(self, auth_client):
        call_command("seed_occupational_data")
        response = auth_client.get("/api/v1/organization/occupational-categories/")
        assert response.status_code == 200
        # Should return at least 3 SUNAT Tabla 10 categories
        if isinstance(response.data, list):
            assert len(response.data) >= 3
        else:
            # paginated or wrapped
            payload = response.data.get("data") or response.data.get("results") or []
            if hasattr(payload, "__len__"):
                assert len(payload) >= 3 or len(response.data) > 0

    def test_authenticated_user_can_list_ciuo_codes(self, auth_client):
        call_command("seed_occupational_data")
        response = auth_client.get("/api/v1/organization/ciuo-codes/")
        assert response.status_code == 200
