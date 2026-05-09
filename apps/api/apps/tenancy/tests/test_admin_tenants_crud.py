"""Tests for /api/admin/tenants/ CRUD."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.models import Tenant, TenantInvitation


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.fixture
def existing_tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def client():
    return APIClient()


def auth(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


@pytest.mark.django_db
class TestTenantsListPermission:
    def test_anonymous_denied(self, client):
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 401

    def test_regular_user_denied(self, client, regular_user):
        client.credentials(HTTP_AUTHORIZATION=auth(regular_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 403

    def test_vyntia_staff_allowed(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestTenantsList:
    def test_returns_paginated_results(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "results" in data
        assert "pagination" in data
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["slug"] == "acme"


@pytest.mark.django_db
class TestTenantsCreate:
    def test_creates_tenant_with_invitation(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "newco",
                "name": "New Co S.A.C.",
                "ruc": "20999999999",
                "plan": "starter",
                "trial_days": 30,
                "admin_email": "ceo@newco.com",
                "admin_name": "CEO",
            },
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["tenant"]["slug"] == "newco"
        assert data["invitation"]["email"] == "ceo@newco.com"
        assert "activation_url" in data["invitation"]
        # Tenant + invitation persisted
        tenant = Tenant.objects.get(slug="newco")
        assert tenant.status == "trial"
        assert TenantInvitation.objects.filter(tenant=tenant, accepted_at__isnull=True).count() == 1

    def test_rejects_reserved_slug(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "admin",  # reserved
                "name": "X",
                "ruc": "20999999999",
                "plan": "starter",
                "admin_email": "ceo@x.com",
                "admin_name": "CEO",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_rejects_duplicate_slug(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "acme",
                "name": "Other",
                "ruc": "20888888888",
                "plan": "starter",
                "admin_email": "x@y.com",
                "admin_name": "X",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_rejects_bad_ruc_format(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.post(
            "/api/admin/tenants/",
            {
                "slug": "valid",
                "name": "X",
                "ruc": "12345",  # too short
                "plan": "starter",
                "admin_email": "x@y.com",
                "admin_name": "X",
            },
            format="json",
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestTenantDetail:
    def test_get_returns_tenant(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get(f"/api/admin/tenants/{existing_tenant.id}/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["slug"] == "acme"
        assert data["member_count"] == 0  # no memberships yet

    def test_patch_updates_plan(self, client, staff_user, existing_tenant):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.patch(
            f"/api/admin/tenants/{existing_tenant.id}/",
            {"plan": "pro"},
            format="json",
        )
        assert response.status_code == 200
        existing_tenant.refresh_from_db()
        assert existing_tenant.plan == "pro"

    def test_get_404_for_unknown(self, client, staff_user):
        client.credentials(HTTP_AUTHORIZATION=auth(staff_user))
        response = client.get("/api/admin/tenants/00000000-0000-0000-0000-000000000000/")
        assert response.status_code == 404
