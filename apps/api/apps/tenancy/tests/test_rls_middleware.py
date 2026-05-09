"""Tests for RLSMiddleware (SET LOCAL of app.tenant_id / app.user_id).

These tests require PostgreSQL because they verify session variables. They
skip on SQLite.
"""

import uuid

import pytest
from django.db import connection
from django.test import RequestFactory

from apps.tenancy.middleware import RLSMiddleware
from apps.tenancy.models import Tenant

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="RLSMiddleware tests require PostgreSQL.",
)


def _stub_response(request):
    from django.db import connection
    from django.http import HttpResponse
    # Capture the session variables for assertions
    with connection.cursor() as cur:
        cur.execute("SELECT current_setting('app.tenant_id', TRUE)")
        request._captured_tenant_id = cur.fetchone()[0]
        cur.execute("SELECT current_setting('app.user_id', TRUE)")
        request._captured_user_id = cur.fetchone()[0]
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
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme", ruc="20123456789",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.mark.django_db(transaction=True)
class TestRLSMiddleware:
    def test_sets_tenant_id_when_request_has_tenant(self, factory, tenant):
        middleware = RLSMiddleware(_stub_response)
        request = factory.get("/")
        request.tenant = tenant
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        middleware(request)
        assert request._captured_tenant_id == str(tenant.id)

    def test_no_tenant_no_set(self, factory):
        middleware = RLSMiddleware(_stub_response)
        request = factory.get("/")
        request.tenant = None
        request.user = type("AnonUser", (), {"is_authenticated": False})()
        middleware(request)
        # Nothing was set; current_setting returns empty string
        assert request._captured_tenant_id in ("", None)
