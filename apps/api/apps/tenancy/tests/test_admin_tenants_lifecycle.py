"""Tests for tenant lifecycle actions: suspend, cancel, re-invite."""

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
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20111111111",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestSuspend:
    def test_suspends_active_tenant(self, client, tenant):
        response = client.post(f"/api/admin/tenants/{tenant.id}/suspend/")
        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.status == "suspended"

    def test_cannot_suspend_cancelled_tenant(self, client, tenant):
        tenant.status = "cancelled"
        tenant.save()
        response = client.post(f"/api/admin/tenants/{tenant.id}/suspend/")
        assert response.status_code == 400


@pytest.mark.django_db
class TestCancel:
    def test_cancels_tenant(self, client, tenant):
        response = client.post(f"/api/admin/tenants/{tenant.id}/cancel/")
        assert response.status_code == 200
        tenant.refresh_from_db()
        assert tenant.status == "cancelled"
        assert tenant.cancelled_at is not None


@pytest.mark.django_db
class TestReinvite:
    def test_creates_new_invitation(self, client, tenant):
        response = client.post(
            f"/api/admin/tenants/{tenant.id}/invitations/",
            {"email": "newadmin@acme.com", "role": "owner"},
            format="json",
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["email"] == "newadmin@acme.com"
        assert "activation_url" in data
        assert TenantInvitation.objects.filter(
            tenant=tenant, email="newadmin@acme.com"
        ).count() == 1

    def test_email_required(self, client, tenant):
        response = client.post(
            f"/api/admin/tenants/{tenant.id}/invitations/",
            {},
            format="json",
        )
        assert response.status_code == 400
