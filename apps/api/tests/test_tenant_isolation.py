"""Cross-cutting tenant isolation tests — proves the multi-tenancy contract.

If any of these tests fails, multi-tenancy is broken at a structural level.

**Test infra reality (see C.8 plan):**

- The default test DB is SQLite (`vyntia.settings.testing`). RLS, raw-SQL
  bypass, and Postgres-only constructs (`SET LOCAL app.tenant_id`) cannot
  run there. Tests that depend on RLS are gated with `@pytest.mark.skipif`
  on `connection.vendor != 'postgresql'`.
- `Employee.objects` is the default Django Manager (TenantManager is not
  attached to models in C.0-C.5). The spec § 9.2 ORM-isolation test is
  written verbatim and gated; it documents the future contract once
  TenantManager wiring lands.
- The `unsafe` manager test from spec § 9.2 is dropped — the attribute
  doesn't exist on any model in C.0-C.5.
- Tenancy middleware is excluded from `vyntia.settings.testing.MIDDLEWARE`;
  the JWT-replay test injects it via the `_inject_tenant_middleware` fixture
  (pattern from `apps/tenancy/tests/test_login_tenant_aware.py:18-39`).
"""

import pytest
from django.db import connection
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import User
from apps.tenancy.context import tenant_context
from apps.tenancy.models import TenantMembership

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Test setup: inject tenancy middleware (mirrors test_login_tenant_aware.py)
# ---------------------------------------------------------------------------


ALLOWED_HOSTS_FOR_TESTS = [
    "testserver",
    "test-a.vyntia.pe",
    "test-b.vyntia.pe",
    "vyntia.pe",
    "localhost",
    "127.0.0.1",
]


@pytest.fixture
def _inject_tenant_middleware(settings):
    """Permit tenant subdomains as hosts AND inject TenantMiddleware +
    TenantAuthMiddleware so request.tenant + JWT-vs-tenant validation fire.
    """
    settings.ALLOWED_HOSTS = ALLOWED_HOSTS_FOR_TESTS
    middleware = list(settings.MIDDLEWARE)
    if "apps.tenancy.middleware.TenantMiddleware" not in middleware:
        try:
            insert_after = middleware.index(
                "django.middleware.common.CommonMiddleware"
            )
            middleware.insert(
                insert_after + 1, "apps.tenancy.middleware.TenantMiddleware"
            )
        except ValueError:
            middleware.insert(0, "apps.tenancy.middleware.TenantMiddleware")
    if "apps.tenancy.middleware.TenantAuthMiddleware" not in middleware:
        # TenantAuthMiddleware must run after AuthenticationMiddleware so
        # request.user is populated before we cross-check JWT claims.
        try:
            insert_after = middleware.index(
                "django.contrib.auth.middleware.AuthenticationMiddleware"
            )
            middleware.insert(
                insert_after + 1,
                "apps.tenancy.middleware.TenantAuthMiddleware",
            )
        except ValueError:
            middleware.append("apps.tenancy.middleware.TenantAuthMiddleware")
    settings.MIDDLEWARE = middleware


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_employee(numero_documento, tenant=None, **overrides):
    """Create an Employee. The `tenant` FK is required by the schema; pass it
    explicitly (the codebase doesn't currently auto-set it from context)."""
    defaults = dict(
        nombres_empleado="Test",
        apellido_paterno="Iso",
        apellido_materno="Lation",
        numero_documento=numero_documento,
        tipo_documento="DNI",
        correo_personal=f"{numero_documento}@test.com",
        fecha_nacimiento="1990-01-01",
        estado_civil="soltero",
        genero_empleado="masculino",
        direccion_domicilio="Av. Test 123",
        distrito_domicilio="Lima",
        provincia_domicilio="Lima",
        departamento_domicilio="Lima",
        estado_empleado="activo",
    )
    defaults.update(overrides)
    if tenant is not None:
        defaults["tenant"] = tenant
    return Employee.objects.create(**defaults)


def _create_user_with_membership(tenant, username, role="member"):
    """Create a User and an active TenantMembership in `tenant`."""
    user = User.objects.create_user(
        username=username,
        email=f"{username}@test.com",
        password="testpass123",
    )
    TenantMembership.objects.create(
        tenant=tenant,
        user=user,
        role=role,
        status="active",
    )
    return user


def _login_token(user, tenant):
    """Issue a tenant-aware JWT for `user` in `tenant`. Mirrors C.4 login."""
    refresh = RefreshToken.for_user(user)
    refresh["tenant_id"] = str(tenant.id)
    refresh["tenant_slug"] = tenant.slug
    refresh["membership_role"] = "member"
    return str(refresh.access_token)


# ---------------------------------------------------------------------------
# ORM-level isolation (gated — requires TenantManager wiring on models)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="Spec § 9.2 ORM isolation requires (1) Postgres + RLS active in test DB "
    "AND (2) TenantManager attached to Employee.objects. Currently neither is the "
    "case (test DB is SQLite; Employee uses default Django Manager). This test is "
    "documentation of the future contract — see C.8 plan controller-discovery notes.",
)
def test_orm_isolation_per_tenant(in_tenant_a, in_tenant_b):
    """Employee created in tenant_a is invisible from tenant_b's ORM queries.

    Contract: when wired up, calling Employee.objects inside `tenant_context(B)`
    must not return rows belonging to tenant_a. Today the enforcement is RLS
    at the SQL layer; tomorrow it'll also be Python-side via TenantManager.
    """
    with tenant_context(in_tenant_a):
        _create_employee("00000001", tenant=in_tenant_a)

    with tenant_context(in_tenant_b):
        # When TenantManager is attached this should be 0; pre-wiring it leaks.
        # On Postgres with RLS active and the connection user being vyntia_app,
        # RLS would filter at the SQL layer.
        assert Employee.objects.filter(numero_documento="00000001").count() == 0


# ---------------------------------------------------------------------------
# RLS (raw SQL) isolation — Postgres-only, requires vyntia_app connection role
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="RLS is a Postgres feature. Test DB is SQLite by default. Future "
    "C.8.1 sub-layer can wire up a Postgres test settings file with the "
    "vyntia_app role to make this test executable.",
)
def test_rls_blocks_raw_sql(in_tenant_a, in_tenant_b):
    """Raw SQL inside tenant_b's session cannot SELECT employees created in tenant_a.

    Strongest isolation guarantee — even raw `connection.cursor().execute(...)`
    is filtered by Postgres RLS. Requires the connection user to be
    `vyntia_app` (NO BYPASSRLS) AND `app.tenant_id` set via SET LOCAL.
    The `in_tenant_a/b` fixtures handle the SET LOCAL part on Postgres.
    """
    with tenant_context(in_tenant_a):
        _create_employee("11111110", tenant=in_tenant_a)

    with tenant_context(in_tenant_b), connection.cursor() as cur:
        cur.execute(
            "SELECT id FROM empleados WHERE numero_documento = %s",
            ["11111110"],
        )
        rows = cur.fetchall()
        assert rows == [], (
            f"RLS leak: tenant_b saw tenant_a's Employee via raw SQL: {rows}"
        )


# ---------------------------------------------------------------------------
# JWT cross-tenant replay defense (runs on SQLite — middleware is Python-side)
# ---------------------------------------------------------------------------


def test_jwt_token_cannot_be_used_across_tenants(
    tenant_a, tenant_b, _inject_tenant_middleware
):
    """A JWT issued for tenant_a's session must be rejected when sent on tenant_b's host.

    The TenantAuthMiddleware (C.3) decodes the JWT, compares its `tenant_id`
    claim against `request.tenant.id`, and returns 401/403 on mismatch.
    """
    user = _create_user_with_membership(tenant_a, username="iso_jwt_user")
    token = _login_token(user, tenant_a)

    client = APIClient(HTTP_HOST="test-b.vyntia.pe")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = client.get("/api/v1/employees/")
    assert response.status_code in (401, 403), (
        f"Cross-tenant JWT replay should be blocked but got "
        f"{response.status_code}: {response.content!r}"
    )


def test_jwt_token_accepted_on_correct_tenant(
    tenant_a, _inject_tenant_middleware
):
    """Sanity check: same JWT on the matching subdomain should NOT be rejected
    for tenant reasons. (It may still 200/404/403 for other reasons — RLS,
    permissions, RBAC — but it must not 401 with a 'tenant' message.)
    """
    user = _create_user_with_membership(
        tenant_a, username="iso_jwt_user_ok"
    )
    token = _login_token(user, tenant_a)

    client = APIClient(HTTP_HOST="test-a.vyntia.pe")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    response = client.get("/api/v1/employees/")
    if response.status_code == 401:
        body = response.content.decode("utf-8", errors="replace").lower()
        assert "tenant" not in body, (
            f"Token rejected on its own tenant — middleware regression: "
            f"{body}"
        )


def test_unauthenticated_request_on_tenant_subdomain_rejected(
    tenant_a, _inject_tenant_middleware
):
    """Sanity: requests to /api/v1/employees/ without a token are 401."""
    client = APIClient(HTTP_HOST="test-a.vyntia.pe")
    response = client.get("/api/v1/employees/")
    assert response.status_code == 401
