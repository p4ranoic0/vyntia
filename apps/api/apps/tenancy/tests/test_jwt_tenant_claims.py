"""Tests for tenant claims emission in JWT tokens."""

import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.tenancy.context import tenant_context
from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.fixture
def membership(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.mark.django_db
class TestTokenClaimsWithTenantContext:
    def test_token_includes_tenant_id_when_context_set(self, tenant_acme, member_user, membership):
        """When issued during a tenant context, the access token has tenant_id claim."""
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        with tenant_context(tenant_acme):
            token = CustomTokenObtainPairSerializer.get_token(member_user)
        assert token["tenant_id"] == str(tenant_acme.id)
        assert token["tenant_slug"] == "acme"
        assert token["membership_role"] == "admin"

    def test_token_omits_tenant_claims_when_no_context(self, member_user):
        """Without tenant context (legacy/admin paths), token has no tenant claims."""
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        token = CustomTokenObtainPairSerializer.get_token(member_user)
        # Backward-compat: tokens minted without tenant context still work
        assert "tenant_id" not in token or token["tenant_id"] is None
        assert "tenant_slug" not in token or token["tenant_slug"] is None

    def test_token_omits_tenant_claims_when_no_membership(self, tenant_acme, member_user):
        """If user has no membership in the active tenant, claims are absent.

        This shouldn't happen in normal flow (login enforces membership in Task 2),
        but the serializer is defensive.
        """
        from api.v1.auth.serializers import CustomTokenObtainPairSerializer

        with tenant_context(tenant_acme):
            token = CustomTokenObtainPairSerializer.get_token(member_user)
        # No membership exists → no role claim
        assert "membership_role" not in token or token["membership_role"] is None
