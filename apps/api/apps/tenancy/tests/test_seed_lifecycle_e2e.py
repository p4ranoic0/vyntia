"""Smoke tests for the seed_lifecycle_e2e management command (B.16 backlog #132).

These tests verify that the seed:
  - Provisions every resource the Playwright lifecycle E2E expects.
  - Is idempotent on re-run (no duplicates, IDs stable).
  - Emits a parseable `SEED_OUTPUT:` json line on stdout.
  - Leaves the admin user authenticatable with the seeded password.
"""
import json
from io import StringIO

import pytest
from django.core.management import call_command

from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department, Position
from apps.tenancy.models import Tenant, TenantMembership


def _run_seed():
    out = StringIO()
    call_command("seed_lifecycle_e2e", stdout=out)
    return out.getvalue()


def _parse_payload(output: str) -> dict:
    line = next(ln for ln in output.splitlines() if ln.startswith("SEED_OUTPUT:"))
    return json.loads(line.removeprefix("SEED_OUTPUT:").strip())


@pytest.mark.django_db
class TestSeedLifecycleE2e:
    def test_first_run_creates_full_graph(self):
        output = _run_seed()
        payload = _parse_payload(output)

        tenant = Tenant.objects.get(slug="lifecycle")
        assert str(tenant.id) == payload["tenant_id"]
        assert tenant.status == "active"
        assert tenant.plan == "starter"

        admin = User.objects.get(username="admin_lifecycle")
        assert admin.email == "admin@lifecycle.test"
        assert admin.tipo_usuario == "administrador"
        assert admin.is_active is True

        membership = TenantMembership.objects.get(tenant=tenant, user=admin)
        assert membership.role == "admin"
        assert membership.status == "active"

        role = Role.objects.get(tenant=tenant, nombre_rol="Admin RRHH")
        assert UserRole.objects.filter(
            tenant=tenant, usuario=admin, rol=role, estado_asignacion="activo"
        ).exists()

        department = Department.objects.get(tenant=tenant, siglas_area="TI")
        assert department.unit_type == "gerencia"

        position = Position.objects.get(tenant=tenant, code="DEV-SR-01", version=1)
        assert position.name == "Desarrollador Senior"
        assert position.department_id == department.id

    def test_second_run_is_idempotent(self):
        first = _parse_payload(_run_seed())
        second = _parse_payload(_run_seed())

        assert first == second
        # And the underlying rows haven't multiplied.
        assert Tenant.objects.filter(slug="lifecycle").count() == 1
        assert User.objects.filter(username="admin_lifecycle").count() == 1
        assert Department.objects.filter(tenant_id=first["tenant_id"]).count() == 1
        assert Position.objects.filter(tenant_id=first["tenant_id"]).count() == 1
        assert TenantMembership.objects.filter(
            tenant_id=first["tenant_id"], user__username="admin_lifecycle"
        ).count() == 1

    def test_admin_password_is_authenticatable(self):
        _run_seed()
        admin = User.objects.get(username="admin_lifecycle")
        assert admin.check_password("LifecyclePass123!") is True

    def test_stdout_payload_keys_are_complete(self):
        payload = _parse_payload(_run_seed())
        required = {
            "tenant_id",
            "tenant_slug",
            "tenant_host",
            "admin_email",
            "admin_username",
            "admin_password",
            "department_id",
            "position_id",
            "role_id",
        }
        assert required.issubset(payload.keys())
        assert payload["tenant_host"] == "lifecycle.vyntia.pe"
        assert payload["admin_password"] == "LifecyclePass123!"
