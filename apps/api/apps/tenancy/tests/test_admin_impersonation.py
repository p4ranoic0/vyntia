"""Tests for /api/admin/users/<id>/impersonate/ + /api/admin/support-sessions/."""

import pytest
import jwt as pyjwt
from django.conf import settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import (
    SupportSession, Tenant, TenantMembership,
)


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def target_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def membership(tenant, target_user):
    return TenantMembership.objects.create(
        tenant=tenant, user=target_user, role="admin", status="active"
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestImpersonate:
    def test_creates_support_session_and_returns_tokens(
        self, client, staff_user, target_user, tenant, membership
    ):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "Ticket #1234 — bug en boletas", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access" in data
        assert "refresh" in data
        assert "support_session_id" in data

        # SupportSession created with right metadata
        session = SupportSession.objects.get(pk=data["support_session_id"])
        assert session.staff_user == staff_user
        assert session.target_user == target_user
        assert session.tenant == tenant
        assert session.reason.startswith("Ticket #1234")

    def test_token_contains_impersonation_claims(
        self, client, staff_user, target_user, tenant, membership
    ):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "support reason", "tenant_id": str(tenant.id)},
            format="json",
        )
        access = response.json()["data"]["access"]
        payload = pyjwt.decode(access, options={"verify_signature": False})
        assert payload["impersonated_by"] == str(staff_user.id)
        assert payload["tenant_id"] == str(tenant.id)
        assert payload["support_session_id"]

    def test_404_for_unknown_user(self, client, tenant):
        response = client.post(
            f"/api/admin/users/00000000-0000-0000-0000-000000000000/impersonate/",
            {"reason": "x" * 10, "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 404

    def test_400_when_reason_too_short(self, client, target_user, tenant, membership):
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "a", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 400

    def test_400_when_user_not_member(self, client, target_user, tenant):
        # No membership — should reject
        response = client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "support reason", "tenant_id": str(tenant.id)},
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestSupportSessionsList:
    def test_lists_sessions(self, client, staff_user, target_user, tenant, membership):
        # Create one session via the impersonate endpoint
        client.post(
            f"/api/admin/users/{target_user.id}/impersonate/",
            {"reason": "audit", "tenant_id": str(tenant.id)},
            format="json",
        )
        response = client.get("/api/admin/support-sessions/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["staff_user"] == "zviera"
        assert data["results"][0]["target_user"] == "maria"
