"""Tests for the GET /api/v1/workspaces/ endpoint."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def tenant_alpha(staff_user):
    return Tenant.objects.create(
        slug="alpha", name="Alpha Inc", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_beta(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta LLC", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_in_alpha(tenant_alpha, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_alpha, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def member_in_beta(tenant_beta, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_beta, user=member_user, role="member", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


def auth_token(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db
class TestWorkspacesList:
    def test_authenticated_user_sees_their_workspaces(
        self, client, member_user, member_in_alpha, member_in_beta
    ):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 200
        data = response.json()["data"]
        slugs = sorted(w["slug"] for w in data)
        assert slugs == ["alpha", "beta"]

    def test_returns_role_per_workspace(
        self, client, member_user, member_in_alpha, member_in_beta
    ):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        data = response.json()["data"]
        roles_by_slug = {w["slug"]: w["role"] for w in data}
        assert roles_by_slug["alpha"] == "admin"
        assert roles_by_slug["beta"] == "member"

    def test_empty_for_user_with_no_memberships(self, client, member_user):
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 200
        assert response.json()["data"] == []

    def test_unauthenticated_returns_401(self, client):
        response = client.get("/api/v1/workspaces/")
        assert response.status_code == 401

    def test_excludes_invited_only_memberships(
        self, client, member_user, tenant_alpha
    ):
        TenantMembership.objects.create(
            tenant=tenant_alpha, user=member_user, role="member", status="invited"
        )
        token = auth_token(member_user)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = client.get("/api/v1/workspaces/")
        assert response.json()["data"] == []
