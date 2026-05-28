import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.testing")
django.setup()


@pytest.fixture
def api_client():
    """Cliente API para tests."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user_data():
    """Datos de usuario para tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "nombres_usuario": "Test",
        "apellidos_usuario": "User",
    }


@pytest.fixture
def create_user(db, user_data):
    """Crear usuario para tests."""
    from django.contrib.auth import get_user_model

    user_model = get_user_model()

    def _create_user(**kwargs):
        data = user_data.copy()
        data.update(kwargs)
        return user_model.objects.create_user(**data)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Cliente autenticado para tests de API."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user
    return api_client, user


# ---------------------------------------------------------------------------
# Cross-tenant isolation fixtures (used by tests/test_tenant_isolation.py)
# ---------------------------------------------------------------------------

from django.contrib.auth import get_user_model
from django.db import connection

from apps.tenancy.context import tenant_context
from apps.tenancy.models import Tenant


@pytest.fixture
def isolation_staff_user(db):
    """A Vyntia staff user used as `created_by` for the isolation-test tenants."""
    User = get_user_model()
    return User.objects.create_user(
        username="iso_staff",
        email="iso_staff@vyntia.pe",
        password="testpass123",
    )


@pytest.fixture
def tenant_a(db, isolation_staff_user):
    """Tenant A — used as the "current tenant" in cross-cutting isolation tests."""
    return Tenant.objects.create(
        slug="test-a",
        name="Tenant A (test)",
        ruc="20111111111",
        plan="starter",
        status="active",
        created_by=isolation_staff_user,
    )


@pytest.fixture
def tenant_b(db, isolation_staff_user):
    """Tenant B — used as the "other tenant" we should never leak into."""
    return Tenant.objects.create(
        slug="test-b",
        name="Tenant B (test)",
        ruc="20222222222",
        plan="starter",
        status="active",
        created_by=isolation_staff_user,
    )


@pytest.fixture
def in_tenant_a(tenant_a):
    """Activate tenant_a's Python context AND (on Postgres only) the SQL-level
    `app.tenant_id` setting that RLS policies read.

    On SQLite (`connection.vendor == 'sqlite'`), the SQL-level setting is
    skipped — RLS doesn't exist there. Tests that depend on RLS enforcement
    must guard themselves with `@pytest.mark.skipif(...)`.

    Yields the tenant for caller convenience.
    """
    with tenant_context(tenant_a):
        if connection.vendor == "postgresql":
            with connection.cursor() as cur:
                cur.execute("SET LOCAL app.tenant_id = %s", [str(tenant_a.id)])
        yield tenant_a


@pytest.fixture
def in_tenant_b(tenant_b):
    """Mirror of in_tenant_a for tenant_b."""
    with tenant_context(tenant_b):
        if connection.vendor == "postgresql":
            with connection.cursor() as cur:
                cur.execute("SET LOCAL app.tenant_id = %s", [str(tenant_b.id)])
        yield tenant_b
