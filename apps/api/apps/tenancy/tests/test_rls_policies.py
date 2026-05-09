"""Unit tests for RLS policy SQL generators (pure functions, no DB)."""

from apps.tenancy.rls.policies import (
    generate_create_role_sql,
    generate_enable_rls_sql,
    generate_grant_sql,
    generate_standard_policy_sql,
    generate_dual_clause_policy_sql,
)


class TestRoleCreation:
    def test_create_role_idempotent_block(self):
        sql = generate_create_role_sql("vyntia_app", bypass_rls=False)
        assert "DO $$" in sql
        assert "CREATE ROLE vyntia_app" in sql
        assert "NOLOGIN" in sql
        assert "BYPASSRLS" not in sql.upper().replace("NOBYPASSRLS", "")

    def test_create_role_with_bypassrls(self):
        sql = generate_create_role_sql("vyntia_admin", bypass_rls=True)
        assert "CREATE ROLE vyntia_admin" in sql
        assert "BYPASSRLS" in sql


class TestEnableRLS:
    def test_enable_and_force(self):
        sql = generate_enable_rls_sql("employees_employee")
        assert "ALTER TABLE employees_employee ENABLE ROW LEVEL SECURITY" in sql
        assert "ALTER TABLE employees_employee FORCE ROW LEVEL SECURITY" in sql


class TestStandardPolicy:
    def test_policy_uses_app_tenant_id_setting(self):
        sql = generate_standard_policy_sql("employees_employee")
        assert "DROP POLICY IF EXISTS tenant_isolation ON employees_employee" in sql
        assert "CREATE POLICY tenant_isolation ON employees_employee" in sql
        assert "current_setting('app.tenant_id', TRUE)" in sql
        assert "::uuid" in sql
        assert "TO vyntia_app" in sql

    def test_policy_has_using_and_with_check(self):
        sql = generate_standard_policy_sql("employees_employee")
        assert "USING (" in sql
        assert "WITH CHECK (" in sql


class TestDualClausePolicy:
    def test_membership_policy_allows_user_scoped_reads(self):
        sql = generate_dual_clause_policy_sql("tenancy_tenantmembership")
        assert "tenant_id = current_setting('app.tenant_id', TRUE)::uuid" in sql
        assert "user_id = current_setting('app.user_id', TRUE)::uuid" in sql
        assert "\n        OR\n" in sql

    def test_dual_clause_with_check_remains_strict(self):
        sql = generate_dual_clause_policy_sql("tenancy_tenantmembership")
        assert sql.count("user_id = current_setting") == 1


class TestGrant:
    def test_grant_app_user_full_dml(self):
        sql = generate_grant_sql("employees_employee")
        assert "GRANT SELECT, INSERT, UPDATE, DELETE ON employees_employee TO vyntia_app" in sql

    def test_grant_readonly_select_only(self):
        sql = generate_grant_sql("employees_employee")
        assert "GRANT SELECT ON employees_employee TO vyntia_readonly" in sql
