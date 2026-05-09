"""Tests for the TenantInvitation model."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.tenancy.models import Tenant, TenantInvitation


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme",
        name="Acme",
        ruc="20123456789",
        plan="starter",
        status="trial",
        created_by=staff_user,
    )


@pytest.mark.django_db
class TestTenantInvitationModel:
    def test_create_invitation(self, tenant, staff_user):
        expires = timezone.now() + timedelta(days=7)
        inv = TenantInvitation.objects.create(
            tenant=tenant,
            email="ceo@acme.com",
            token="signed.jwt.token.abc123",
            role="owner",
            expires_at=expires,
            created_by=staff_user,
        )
        assert inv.id is not None
        assert inv.tenant == tenant
        assert inv.email == "ceo@acme.com"
        assert inv.token == "signed.jwt.token.abc123"
        assert inv.role == "owner"
        assert inv.expires_at == expires
        assert inv.accepted_at is None
        assert inv.created_at is not None

    def test_token_must_be_unique(self, tenant, staff_user):
        TenantInvitation.objects.create(
            tenant=tenant,
            email="a@acme.com",
            token="same-token",
            role="admin",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=staff_user,
        )
        with pytest.raises(IntegrityError):
            TenantInvitation.objects.create(
                tenant=tenant,
                email="b@acme.com",
                token="same-token",
                role="member",
                expires_at=timezone.now() + timedelta(days=7),
                created_by=staff_user,
            )

    def test_str_representation(self, tenant, staff_user):
        inv = TenantInvitation.objects.create(
            tenant=tenant,
            email="ceo@acme.com",
            token="t1",
            role="owner",
            expires_at=timezone.now() + timedelta(days=7),
            created_by=staff_user,
        )
        assert str(inv) == "ceo@acme.com → acme (owner)"
