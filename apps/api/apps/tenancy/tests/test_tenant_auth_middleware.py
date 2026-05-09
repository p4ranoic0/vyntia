"""Tests for TenantAuthMiddleware (JWT tenant_id validation)."""

import uuid

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework.exceptions import AuthenticationFailed

from apps.tenancy.middleware import TenantAuthMiddleware
from apps.tenancy.models import Tenant


def _ok(request):
    return HttpResponse("ok")


@pytest.fixture
def factory():
    return RequestFactory()


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


def _set_user(request, user, *, jwt_tenant_id=None):
    """Helper: simulate auth middleware having run."""
    request.user = user
    if jwt_tenant_id is not None:
        request.auth = {"tenant_id": str(jwt_tenant_id)}
    else:
        request.auth = None


@pytest.mark.django_db
class TestTenantAuthMiddleware:
    def test_no_tenant_skipped(self, factory, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = None
        _set_user(request, staff_user, jwt_tenant_id=uuid.uuid4())
        # Should not raise even with a mismatching tenant_id, because request.tenant is None
        response = middleware(request)
        assert response.status_code == 200

    def test_anonymous_user_skipped(self, factory, tenant_acme):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        request.auth = None
        response = middleware(request)
        assert response.status_code == 200

    def test_jwt_without_tenant_id_passes(self, factory, tenant_acme, staff_user):
        """Legacy tokens (pre-C.4) without tenant_id claim should still work."""
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=None)
        response = middleware(request)
        assert response.status_code == 200

    def test_matching_tenant_id_passes(self, factory, tenant_acme, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=tenant_acme.id)
        response = middleware(request)
        assert response.status_code == 200

    def test_mismatching_tenant_id_raises(self, factory, tenant_acme, staff_user):
        middleware = TenantAuthMiddleware(_ok)
        request = factory.get("/")
        request.tenant = tenant_acme
        _set_user(request, staff_user, jwt_tenant_id=uuid.uuid4())  # different
        with pytest.raises(AuthenticationFailed) as exc_info:
            middleware(request)
        assert "tenant_id mismatch" in str(exc_info.value)
