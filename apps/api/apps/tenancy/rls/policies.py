"""SQL generators for PostgreSQL RLS policies.

These are pure functions — no DB connection, no Django imports.
They produce idempotent SQL strings ready to be executed by setup_rls.

Two policy types:
- Standard: tenant_id = current_setting('app.tenant_id'). Used by all
  business tables (employees, contracts, payroll, etc.).
- Dual-clause: tenant_id = setting() OR user_id = setting(). Used only by
  tenancy_tenantmembership to enable the workspace switcher endpoint.
"""

APP_ROLE = "vyntia_app"
ADMIN_ROLE = "vyntia_admin"
READONLY_ROLE = "vyntia_readonly"


def generate_create_role_sql(role_name: str, bypass_rls: bool = False) -> str:
    """Idempotent role creation. Wraps in DO $$ ... $$ block to gate on existence."""
    bypass_clause = "BYPASSRLS" if bypass_rls else "NOBYPASSRLS"
    return f"""
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '{role_name}') THEN
        CREATE ROLE {role_name} NOLOGIN {bypass_clause};
    END IF;
END
$$;
""".strip()


def generate_enable_rls_sql(table_name: str) -> str:
    """Enable + force RLS on a table."""
    return (
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;\n"
        f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;"
    )


def generate_standard_policy_sql(table_name: str) -> str:
    """Tenant-only policy for business tables."""
    return f"""
DROP POLICY IF EXISTS tenant_isolation ON {table_name};
CREATE POLICY tenant_isolation ON {table_name}
    FOR ALL
    TO {APP_ROLE}
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
""".strip()


def generate_dual_clause_policy_sql(table_name: str) -> str:
    """Dual-clause policy for tenancy_tenantmembership."""
    return f"""
DROP POLICY IF EXISTS membership_isolation ON {table_name};
CREATE POLICY membership_isolation ON {table_name}
    FOR ALL
    TO {APP_ROLE}
    USING (
        tenant_id = current_setting('app.tenant_id', TRUE)::uuid
        OR
        user_id = current_setting('app.user_id', TRUE)::uuid
    )
    WITH CHECK (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
""".strip()


def generate_grant_sql(table_name: str) -> str:
    """Grant DML to vyntia_app, SELECT to vyntia_readonly."""
    return (
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table_name} TO {APP_ROLE};\n"
        f"GRANT SELECT ON {table_name} TO {READONLY_ROLE};"
    )
