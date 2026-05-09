"""Integration tests for the setup_rls management command.

These tests exercise the command against the live test DB. They verify:
- Roles are created (vyntia_app, vyntia_admin, vyntia_readonly)
- RLS is enabled on every tenant-scoped table
- The right policy variant is applied per table
- The command is idempotent (re-running succeeds)

Note: RLS is a PostgreSQL-only feature. When the test DB is SQLite (the default
for the local pytest config), these tests are skipped. Run against PostgreSQL
to exercise them, e.g. via the `bd_vyntia_test` database in CI.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection

pytestmark = pytest.mark.skipif(
    connection.vendor != "postgresql",
    reason="setup_rls integration tests require PostgreSQL (RLS is a Postgres feature).",
)


@pytest.fixture
def run_setup_rls():
    """Run setup_rls and return captured stdout."""
    out = StringIO()
    call_command("setup_rls", stdout=out)
    return out.getvalue()


@pytest.mark.django_db(transaction=True)
class TestSetupRLSApply:
    def test_command_runs_without_error(self, run_setup_rls):
        assert "applied roles + policies" in run_setup_rls

    def test_creates_three_roles(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT rolname FROM pg_catalog.pg_roles
                WHERE rolname IN ('vyntia_app', 'vyntia_admin', 'vyntia_readonly')
                ORDER BY rolname
            """)
            roles = [row[0] for row in cur.fetchall()]
        assert roles == ["vyntia_admin", "vyntia_app", "vyntia_readonly"]

    def test_vyntia_admin_has_bypassrls(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("SELECT rolbypassrls FROM pg_catalog.pg_roles WHERE rolname = 'vyntia_admin'")
            assert cur.fetchone()[0] is True

    def test_vyntia_app_does_not_have_bypassrls(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("SELECT rolbypassrls FROM pg_catalog.pg_roles WHERE rolname = 'vyntia_app'")
            assert cur.fetchone()[0] is False

    def test_business_tables_have_rls_enabled(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT relrowsecurity, relforcerowsecurity
                FROM pg_catalog.pg_class
                WHERE relname = 'empleado'
            """)
            row = cur.fetchone()
        assert row is not None, "empleado table not found"
        enabled, forced = row
        assert enabled is True
        assert forced is True

    def test_business_table_has_standard_policy(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT policyname FROM pg_catalog.pg_policies
                WHERE tablename = 'empleado'
            """)
            policies = [row[0] for row in cur.fetchall()]
        assert "tenant_isolation" in policies

    def test_tenant_membership_has_dual_clause_policy(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT policyname FROM pg_catalog.pg_policies
                WHERE tablename = 'tenancy_tenantmembership'
            """)
            policies = [row[0] for row in cur.fetchall()]
        assert "membership_isolation" in policies

    def test_idempotent(self):
        """Running setup_rls twice should succeed without errors."""
        out1 = StringIO()
        call_command("setup_rls", stdout=out1)
        out2 = StringIO()
        call_command("setup_rls", stdout=out2)
        assert "applied roles + policies" in out2.getvalue()


@pytest.mark.django_db(transaction=True)
class TestSetupRLSCheck:
    def test_check_passes_after_apply(self):
        """After setup_rls runs, --check should report all tables have policies."""
        call_command("setup_rls")
        out = StringIO()
        call_command("setup_rls", "--check", stdout=out)
        result = out.getvalue()
        assert "all" in result and "policies" in result

    def test_check_fails_when_policy_dropped(self):
        """If any tenant-scoped table loses its policy, --check exits 1."""
        call_command("setup_rls")
        with connection.cursor() as cur:
            cur.execute("DROP POLICY IF EXISTS tenant_isolation ON empleado;")
        with pytest.raises(SystemExit) as exc_info:
            call_command("setup_rls", "--check")
        assert exc_info.value.code == 1
