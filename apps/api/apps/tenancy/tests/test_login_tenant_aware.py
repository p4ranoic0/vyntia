"""Tests for tenant-aware login enforcement."""

import pytest
from django.test import override_settings
from rest_framework.test import APIClient

from apps.tenancy.models import Tenant, TenantMembership

# Allow tenant-subdomain hostnames during these HTTP-level tests.
ALLOWED_HOSTS_FOR_TESTS = [
    "testserver",
    "acme.vyntia.pe",
    "vyntia.pe",
    "localhost",
    "127.0.0.1",
]


@pytest.fixture(autouse=True)
def _allow_tenant_hosts(settings):
    """Permit `acme.vyntia.pe` (and friends) during these tests, and inject
    TenantMiddleware so that subdomain → request.tenant resolution actually
    happens (the testing settings strip extra middleware by default).
    """
    settings.ALLOWED_HOSTS = ALLOWED_HOSTS_FOR_TESTS
    # Inject TenantMiddleware just before AuthenticationMiddleware so that
    # request.tenant is populated when the login view runs.
    middleware = list(settings.MIDDLEWARE)
    if "apps.tenancy.middleware.TenantMiddleware" not in middleware:
        # Place it after CommonMiddleware so the host header has been processed.
        try:
            insert_after = middleware.index(
                "django.middleware.common.CommonMiddleware"
            )
            middleware.insert(insert_after + 1, "apps.tenancy.middleware.TenantMiddleware")
        except ValueError:
            middleware.insert(0, "apps.tenancy.middleware.TenantMiddleware")
    settings.MIDDLEWARE = middleware


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="testpass123"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="testpass123"
    )
    return user


@pytest.fixture
def member_in_acme(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestLoginWithoutTenantSubdomain:
    """Legacy: login from a non-tenant host (testserver, admin) works as before."""

    def test_login_succeeds_without_tenant_context(self, client, member_user):
        """Backward-compat: existing tests using testserver hostname still pass."""
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        assert "access" in data


@pytest.mark.django_db
class TestLoginOnTenantSubdomain:
    """When request.tenant is set, login enforces an active TenantMembership."""

    def test_login_succeeds_for_active_member(self, client, tenant_acme, member_user, member_in_acme):
        # Simulate the request hitting acme.vyntia.pe
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        assert "access" in data

    def test_login_blocked_for_user_without_membership(self, client, tenant_acme, member_user):
        # member_user exists globally but has NO membership in acme
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 403

    def test_login_blocked_for_invited_but_not_active_membership(
        self, client, tenant_acme, member_user
    ):
        # User has invited (not active) membership
        TenantMembership.objects.create(
            tenant=tenant_acme, user=member_user, role="member", status="invited"
        )
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 403

    def test_login_token_contains_tenant_claims(
        self, client, tenant_acme, member_user, member_in_acme
    ):
        """The access token returned by login on a tenant subdomain has tenant_id claim."""
        response = client.post(
            "/api/v1/auth/login/",
            {"username": "maria", "password": "testpass123"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json().get("data") or response.json()
        access = data["access"]

        # Decode the token to check claims (without verification, just for inspection)
        import jwt as pyjwt
        payload = pyjwt.decode(access, options={"verify_signature": False})
        assert payload["tenant_id"] == str(tenant_acme.id)
        assert payload["tenant_slug"] == "acme"
        assert payload["membership_role"] == "admin"
