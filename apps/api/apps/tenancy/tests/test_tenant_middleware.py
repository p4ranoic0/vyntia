"""Tests for TenantMiddleware (subdomain → Tenant resolution)."""

import pytest
from django.test import RequestFactory

from apps.tenancy.middleware import TenantMiddleware
from apps.tenancy.models import Tenant


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
def factory():
    return RequestFactory()


def get_response_stub(request):
    """A trivial inner middleware that just returns request.tenant for inspection."""
    from django.http import HttpResponse
    return HttpResponse(str(getattr(request, "tenant", "no-tenant-attr")))


@pytest.mark.django_db
class TestTenantMiddleware:
    def test_resolves_active_tenant_from_subdomain(self, factory, tenant_acme):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="acme.vyntia.pe")
        response = middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "acme"

    def test_strips_port_from_host(self, factory, tenant_acme):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="acme.vyntia.pe:8000")
        middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "acme"

    def test_reserved_subdomain_admin_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="admin.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_reserved_subdomain_app_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="app.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_localhost_yields_no_tenant(self, factory):
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="localhost:8000")
        middleware(request)
        assert request.tenant is None

    def test_unknown_subdomain_yields_no_tenant(self, factory):
        """An unknown slug doesn't 404 the request — it just doesn't set tenant."""
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="ghost-tenant.vyntia.pe")
        middleware(request)
        assert request.tenant is None

    def test_suspended_tenant_not_resolved(self, factory, staff_user):
        Tenant.objects.create(
            slug="suspended", name="Suspended", ruc="20999999999",
            plan="starter", status="suspended", created_by=staff_user,
        )
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="suspended.vyntia.pe")
        middleware(request)
        # Suspended tenants don't resolve — login attempts go through but UX is blocked
        assert request.tenant is None

    def test_trial_tenant_resolves(self, factory, staff_user):
        Tenant.objects.create(
            slug="newtrial", name="New", ruc="20111000111",
            plan="starter", status="trial", created_by=staff_user,
        )
        middleware = TenantMiddleware(get_response_stub)
        request = factory.get("/", HTTP_HOST="newtrial.vyntia.pe")
        middleware(request)
        assert request.tenant is not None
        assert request.tenant.slug == "newtrial"
