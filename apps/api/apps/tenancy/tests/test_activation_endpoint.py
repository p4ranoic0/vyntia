"""Tests for the POST /api/v1/auth/activate/ endpoint."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.tenancy.models import Tenant, TenantInvitation, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.fixture
def fresh_invitation(tenant_acme, staff_user):
    return TenantInvitation.objects.create(
        tenant=tenant_acme,
        email="ceo@acme.com",
        token="signed.invite.token.abc",
        role="owner",
        expires_at=timezone.now() + timedelta(days=7),
        created_by=staff_user,
    )


@pytest.fixture
def expired_invitation(tenant_acme, staff_user):
    return TenantInvitation.objects.create(
        tenant=tenant_acme,
        email="late@acme.com",
        token="expired.invite.token",
        role="member",
        expires_at=timezone.now() - timedelta(hours=1),
        created_by=staff_user,
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestActivateEndpoint:
    def test_activates_new_user_and_creates_membership(
        self, client, fresh_invitation, tenant_acme, django_user_model
    ):
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "CEO of Acme",
                "password": "verysecurepass123",
            },
            format="json",
        )
        assert response.status_code == 200
        body = response.json()["data"]
        assert "access" in body
        assert body["tenant"]["slug"] == "acme"
        assert body["role"] == "owner"

        # User created
        user = django_user_model.objects.get(email__iexact="ceo@acme.com")
        assert user.is_active

        # Membership created and active
        m = TenantMembership.objects.get(tenant=tenant_acme, user=user)
        assert m.status == "active"
        assert m.joined_at is not None

        # Invitation marked accepted
        fresh_invitation.refresh_from_db()
        assert fresh_invitation.accepted_at is not None

    def test_invalid_token_returns_400(self, client):
        response = client.post(
            "/api/v1/auth/activate/",
            {"token": "nope", "name": "X", "password": "pass12345"},
            format="json",
        )
        assert response.status_code == 400

    def test_expired_token_returns_400(self, client, expired_invitation):
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": expired_invitation.token,
                "name": "X",
                "password": "pass12345",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_already_accepted_invitation_returns_400(
        self, client, fresh_invitation
    ):
        # Accept it once
        client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "First",
                "password": "pass12345",
            },
            format="json",
        )
        # Try to accept again
        response = client.post(
            "/api/v1/auth/activate/",
            {
                "token": fresh_invitation.token,
                "name": "Second",
                "password": "pass12345",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_short_password_rejected(self, client, fresh_invitation):
        response = client.post(
            "/api/v1/auth/activate/",
            {"token": fresh_invitation.token, "name": "X", "password": "short"},
            format="json",
        )
        assert response.status_code == 400  # serializer min_length=8
