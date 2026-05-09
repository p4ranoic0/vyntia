"""Tests for the cross-subdomain exchange flow."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenancy.auth.exchange_token import issue_exchange_token
from apps.tenancy.models import Tenant, TenantMembership

# Allow tenant-subdomain hostnames during these HTTP-level tests.
ALLOWED_HOSTS_FOR_TESTS = [
    "testserver",
    "acme.vyntia.pe",
    "beta.vyntia.pe",
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
    # request.tenant is populated when the exchange view runs.
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
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_acme(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_beta(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="testpass123"
    )


@pytest.fixture
def member_in_acme(tenant_acme, member_user):
    return TenantMembership.objects.create(
        tenant=tenant_acme, user=member_user, role="admin", status="active"
    )


@pytest.fixture
def client():
    return APIClient()


def auth(user):
    return f"Bearer {RefreshToken.for_user(user).access_token}"


@pytest.mark.django_db
class TestWorkspaceExchangeIssue:
    def test_issues_token_for_member(self, client, member_user, member_in_acme):
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert "exchange_token" in data
        assert "acme.vyntia.pe" in data["redirect_url"]

    def test_403_for_non_member(self, client, member_user, tenant_acme):
        # member_user has no membership in acme
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 403

    def test_404_for_unknown_workspace(self, client, member_user):
        client.credentials(HTTP_AUTHORIZATION=auth(member_user))
        response = client.post("/api/v1/workspaces/ghost/exchange/")
        assert response.status_code == 404

    def test_401_when_unauthenticated(self, client):
        response = client.post("/api/v1/workspaces/acme/exchange/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestAuthExchangeConsume:
    def test_consumes_valid_token(
        self, client, tenant_acme, member_user, member_in_acme
    ):
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "access" in data
        assert data["tenant"]["slug"] == "acme"

    def test_rejects_token_for_wrong_tenant(
        self, client, tenant_acme, tenant_beta, member_user
    ):
        # Token issued for acme, but consumed at beta
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            HTTP_HOST="beta.vyntia.pe",
        )
        assert response.status_code == 400

    def test_rejects_when_not_on_tenant_subdomain(
        self, client, tenant_acme, member_user
    ):
        token = issue_exchange_token(user_id=member_user.id, tenant_id=tenant_acme.id)
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": token},
            format="json",
            # No HTTP_HOST → defaults to testserver → no tenant
        )
        assert response.status_code == 400

    def test_rejects_garbage_token(self, client, tenant_acme):
        response = client.post(
            "/api/v1/auth/exchange/",
            {"exchange_token": "not.a.valid.jwt"},
            format="json",
            HTTP_HOST="acme.vyntia.pe",
        )
        assert response.status_code == 400
