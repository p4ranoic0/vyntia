# C.2 — PostgreSQL RLS Policies Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `setup_rls` Django management command that creates 3 PostgreSQL roles (`vyntia_app`, `vyntia_admin`, `vyntia_readonly`) and applies `ENABLE ROW LEVEL SECURITY` + `FORCE` + tenant policies on all 32 tenant-scoped tables. Add `--check` mode for CI verification. Production settings switch to `vyntia_app`. Dev/test continues using `postgres` (BYPASSRLS implicit) — no test breakage.

**Architecture:** The command is **opt-in** — it does NOT run automatically with `migrate`. Operators run it explicitly during deploys (or once in dev for local testing). The dev DB user is `postgres` (superuser with implicit BYPASSRLS), so even if `setup_rls` is run locally, the existing 176 tests continue to pass because the connection bypasses RLS. RLS is only enforced in production where the app connects as `vyntia_app` (no BYPASSRLS). The command is idempotent — safe to re-run after deploys, schema changes, or migrations. Two policy variants: standard tenant-only for business tables, dual-clause `tenant OR user` for `tenancy_tenant` / `tenancy_tenantmembership` (workspace switcher needs cross-tenant user-scoped reads, see spec § 4.2).

**Tech Stack:** Django 5.2 management commands, PostgreSQL 15 RLS, pytest-django for integration tests against the live test DB.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 4

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot (must be preserved or improved)

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | ≥176 passed / ≤8 failed / 3 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |

C.2 adds: ~10-15 new tests (unit tests for SQL generators + integration tests for setup_rls). Target ≥185 passed.

---

## File structure

**Files to create:**

```
apps/api/apps/tenancy/
├── management/
│   ├── __init__.py                            # already exists
│   └── commands/
│       ├── __init__.py                        # already exists
│       └── setup_rls.py                       # NEW — main command
├── rls/
│   ├── __init__.py                            # NEW
│   ├── policies.py                            # NEW — SQL generators (pure functions)
│   └── introspection.py                       # NEW — discover tenant-scoped tables
└── tests/
    ├── test_rls_policies.py                   # NEW — unit tests for SQL generators
    └── test_setup_rls_command.py              # NEW — integration test for the command

docs/operations/
└── rls-setup.md                               # NEW — runbook
```

**Files to modify:**

- `apps/api/vyntia/settings/production.py` — switch `DATABASES['default']['USER']` to `vyntia_app`

---

## Branch

`vyntia/C2-rls-policies` — branched from `master` (HEAD has `Merge C.1`).

---

## Task 1: Branch + command skeleton + introspection helper

**Files:**
- Create: `apps/api/apps/tenancy/management/__init__.py` (only if missing)
- Create: `apps/api/apps/tenancy/management/commands/__init__.py` (only if missing)
- Create: `apps/api/apps/tenancy/management/commands/setup_rls.py`
- Create: `apps/api/apps/tenancy/rls/__init__.py`
- Create: `apps/api/apps/tenancy/rls/introspection.py`

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C2-rls-policies
```

- [ ] **Step 1.2: Verify management dirs exist (created during C.0 if Django admin was registered)**

```bash
ls apps/api/apps/tenancy/management/ 2>/dev/null || mkdir -p apps/api/apps/tenancy/management/commands
```

If they don't exist, create the dirs and empty `__init__.py` files:

```python
# apps/api/apps/tenancy/management/__init__.py
```

```python
# apps/api/apps/tenancy/management/commands/__init__.py
```

- [ ] **Step 1.3: Create `apps/tenancy/rls/__init__.py`**

```python
# apps/api/apps/tenancy/rls/__init__.py
"""RLS (Row-Level Security) helpers for the tenancy layer.

This package contains:
- policies.py: pure functions that generate SQL strings for RLS policies
- introspection.py: discovery of which Django models are tenant-scoped
"""
```

- [ ] **Step 1.4: Create `apps/tenancy/rls/introspection.py`**

```python
"""Discover tenant-scoped Django models for RLS policy application.

A model is considered tenant-scoped if it has a `tenant` field that is
a ForeignKey to `tenancy.Tenant`. The C.1 migration added this to 32
business models across 8 apps.
"""

from django.apps import apps
from django.db import models


def get_tenant_scoped_models():
    """Return list of all Django models that have a `tenant` FK to tenancy.Tenant.

    Order is deterministic (sorted by app_label, then model_name) for
    idempotent policy generation.
    """
    result = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            tenant_field = _get_tenant_field(model)
            if tenant_field is not None:
                result.append(model)
    result.sort(key=lambda m: (m._meta.app_label, m._meta.model_name))
    return result


def _get_tenant_field(model):
    """Return the `tenant` field if it's a FK to tenancy.Tenant, else None."""
    for field in model._meta.local_fields:
        if field.name != "tenant":
            continue
        if not isinstance(field, models.ForeignKey):
            continue
        related = field.related_model
        if related is None:
            continue
        if (related._meta.app_label, related._meta.model_name) == ("tenancy", "tenant"):
            return field
    return None


def get_table_names_for_rls():
    """Return the list of `db_table` names to apply RLS to, sorted."""
    return [m._meta.db_table for m in get_tenant_scoped_models()]
```

- [ ] **Step 1.5: Create command skeleton `apps/tenancy/management/commands/setup_rls.py`**

```python
"""setup_rls — apply PostgreSQL RLS policies to tenant-scoped tables.

Usage:
    manage.py setup_rls           # apply roles + policies (idempotent)
    manage.py setup_rls --check   # verify policies exist, exit 1 if missing
    manage.py setup_rls --verbose # log every SQL statement

This command requires CREATEROLE + table-owner privileges. Typically run
as the postgres superuser during deploys.

Architecture: see docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md § 4
Runbook: see docs/operations/rls-setup.md
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Apply PostgreSQL RLS roles and policies to tenant-scoped tables (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Verify policies exist on every tenant-scoped table; do not apply changes.",
        )
        parser.add_argument(
            "--verbose-sql",
            action="store_true",
            help="Print every SQL statement before executing.",
        )

    def handle(self, *args, **options):
        if options["check"]:
            self._handle_check()
        else:
            self._handle_apply(verbose=options["verbose_sql"])

    def _handle_apply(self, verbose):
        self.stdout.write(self.style.NOTICE("setup_rls: scaffold — Tasks 2-5 fill this in"))

    def _handle_check(self):
        self.stdout.write(self.style.NOTICE("setup_rls --check: scaffold — Task 6 fills this in"))
```

- [ ] **Step 1.6: Verify Django system check + command discoverable**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py help setup_rls --settings=vyntia.settings.development 2>&1 | head -10
```

Expected: check clean. `help setup_rls` shows the help text from the docstring.

- [ ] **Step 1.7: Smoke test introspection**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py shell --settings=vyntia.settings.development -c "
from apps.tenancy.rls.introspection import get_table_names_for_rls
for t in get_table_names_for_rls():
    print(t)
"
```

Expected: a list of ~32 table names, one per line, sorted by `app_label`/`model_name`.

- [ ] **Step 1.8: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/management/ \
        apps/api/apps/tenancy/rls/
git commit -m "chore(C2): scaffold setup_rls command + introspection helper"
```

---

## Task 2: Policy SQL generators (pure functions, unit-tested)

**Files:**
- Create: `apps/api/apps/tenancy/rls/policies.py`
- Create: `apps/api/apps/tenancy/tests/test_rls_policies.py`

- [ ] **Step 2.1: Write the failing tests**

Create `apps/api/apps/tenancy/tests/test_rls_policies.py`:

```python
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
        assert "BYPASSRLS" not in sql.upper().replace("NOBYPASSRLS", "")  # only NOBYPASSRLS

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
        assert " OR " in sql

    def test_dual_clause_with_check_remains_strict(self):
        """WITH CHECK should not include the OR — INSERTs require active tenant context."""
        sql = generate_dual_clause_policy_sql("tenancy_tenantmembership")
        # The WITH CHECK clause should reference only tenant_id, not user_id
        assert sql.count("user_id = current_setting") == 1  # only in USING


class TestGrant:
    def test_grant_app_user_full_dml(self):
        sql = generate_grant_sql("employees_employee")
        assert "GRANT SELECT, INSERT, UPDATE, DELETE ON employees_employee TO vyntia_app" in sql

    def test_grant_readonly_select_only(self):
        sql = generate_grant_sql("employees_employee")
        assert "GRANT SELECT ON employees_employee TO vyntia_readonly" in sql
```

- [ ] **Step 2.2: Run — tests should fail (no policies module yet)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_rls_policies.py -v 2>&1 | tail -10
```

Expected: ImportError on `policies` module.

- [ ] **Step 2.3: Implement `apps/tenancy/rls/policies.py`**

```python
"""SQL generators for PostgreSQL RLS policies.

These are pure functions — no DB connection, no Django imports beyond None.
They produce idempotent SQL strings ready to be executed by setup_rls.

Two policy types:
- Standard: tenant_id = current_setting('app.tenant_id'). Used by all
  business tables (employees, contracts, payroll, etc.).
- Dual-clause: tenant_id = setting() OR user_id = setting(). Used only by
  tenancy_tenant and tenancy_tenantmembership to enable the workspace
  switcher endpoint at app.vyntia.pe.
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
    """Enable + force RLS on a table. Force means even the table owner respects policies."""
    return (
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;\n"
        f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;"
    )


def generate_standard_policy_sql(table_name: str) -> str:
    """Tenant-only policy for business tables.

    Uses `current_setting('app.tenant_id', TRUE)` — the TRUE means missing
    setting returns NULL, which makes `tenant_id = NULL` always false (safe default).
    """
    return f"""
DROP POLICY IF EXISTS tenant_isolation ON {table_name};
CREATE POLICY tenant_isolation ON {table_name}
    FOR ALL
    TO {APP_ROLE}
    USING (tenant_id = current_setting('app.tenant_id', TRUE)::uuid)
    WITH CHECK (tenant_id = current_setting('app.tenant_id', TRUE)::uuid);
""".strip()


def generate_dual_clause_policy_sql(table_name: str) -> str:
    """Dual-clause policy for tenancy_tenant and tenancy_tenantmembership.

    USING clause widens to allow user-scoped reads (workspace switcher).
    WITH CHECK stays strict — INSERTs/UPDATEs still require active tenant context.
    """
    # tenancy_tenant lookups by user happen via TenantMembership.user → tenant.
    # The policy on tenancy_tenant references user_id by joining through memberships,
    # but for simplicity we expose direct user_id-based reads on memberships only.
    # For tenancy_tenant, the user-scoped read requires a JOIN, so the dual clause
    # is structurally different. For C.2, we apply dual-clause to memberships;
    # tenancy_tenant uses standard policy (workspace switcher reads memberships, then
    # follows the FK to tenant — fine because membership row already authorized).
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
```

- [ ] **Step 2.4: Run tests — should pass**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_rls_policies.py -v 2>&1 | tail -15
```

Expected: ~10 tests passed.

- [ ] **Step 2.5: Run full suite — no regression**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥186 passed (176 + ~10 new).

- [ ] **Step 2.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/rls/policies.py \
        apps/api/apps/tenancy/tests/test_rls_policies.py
git commit -m "feat(C2): RLS policy SQL generators (pure functions, TDD)"
```

---

## Task 3: Implement `setup_rls` apply mode

**Files:**
- Modify: `apps/api/apps/tenancy/management/commands/setup_rls.py`

- [ ] **Step 3.1: Replace the `_handle_apply` method**

Replace the entire body of `apps/api/apps/tenancy/management/commands/setup_rls.py` with the full implementation:

```python
"""setup_rls — apply PostgreSQL RLS policies to tenant-scoped tables.

Usage:
    manage.py setup_rls               # apply roles + policies (idempotent)
    manage.py setup_rls --check       # verify policies exist
    manage.py setup_rls --verbose-sql # log every SQL statement

This command requires CREATEROLE + table-owner privileges. Typically run
as the postgres superuser during deploys.

Architecture: see docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md § 4
Runbook: see docs/operations/rls-setup.md
"""

from django.core.management.base import BaseCommand
from django.db import connection

from apps.tenancy.rls.introspection import get_tenant_scoped_models
from apps.tenancy.rls.policies import (
    APP_ROLE,
    ADMIN_ROLE,
    READONLY_ROLE,
    generate_create_role_sql,
    generate_dual_clause_policy_sql,
    generate_enable_rls_sql,
    generate_grant_sql,
    generate_standard_policy_sql,
)

# Tables that get the dual-clause (tenant_id OR user_id) policy.
# Workspace switcher needs user-scoped reads of memberships.
DUAL_CLAUSE_TABLES = {"tenancy_tenantmembership"}


class Command(BaseCommand):
    help = "Apply PostgreSQL RLS roles and policies to tenant-scoped tables (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Verify policies exist on every tenant-scoped table; exit 1 if missing.",
        )
        parser.add_argument(
            "--verbose-sql",
            action="store_true",
            help="Print every SQL statement before executing.",
        )

    def handle(self, *args, **options):
        if options["check"]:
            self._handle_check()
        else:
            self._handle_apply(verbose=options["verbose_sql"])

    # --- apply mode ---

    def _handle_apply(self, verbose):
        self.stdout.write(self.style.NOTICE("setup_rls: applying roles and policies..."))

        # Step 1: ensure roles exist
        self._apply_roles(verbose)

        # Step 2: apply RLS policies to every tenant-scoped table
        models = get_tenant_scoped_models()
        for model in models:
            table = model._meta.db_table
            self._apply_policies_for_table(table, verbose)

        self.stdout.write(self.style.SUCCESS(
            f"setup_rls: applied roles + policies to {len(models)} tables."
        ))

    def _apply_roles(self, verbose):
        sqls = [
            generate_create_role_sql(APP_ROLE, bypass_rls=False),
            generate_create_role_sql(ADMIN_ROLE, bypass_rls=True),
            generate_create_role_sql(READONLY_ROLE, bypass_rls=False),
        ]
        with connection.cursor() as cur:
            for sql in sqls:
                if verbose:
                    self.stdout.write(f"-- {sql.splitlines()[0]}")
                cur.execute(sql)

    def _apply_policies_for_table(self, table, verbose):
        if table in DUAL_CLAUSE_TABLES:
            policy_sql = generate_dual_clause_policy_sql(table)
        else:
            policy_sql = generate_standard_policy_sql(table)

        sqls = [
            generate_enable_rls_sql(table),
            policy_sql,
            generate_grant_sql(table),
        ]
        with connection.cursor() as cur:
            for sql in sqls:
                if verbose:
                    self.stdout.write(f"-- applying to {table}")
                # SQL strings may contain multiple statements separated by ';'
                for statement in self._split_statements(sql):
                    cur.execute(statement)

    @staticmethod
    def _split_statements(sql):
        """Split a multi-statement SQL string on `;` boundaries.

        Naive split — fine because our generators don't use `;` inside string
        literals or DO blocks (DO blocks are atomic from psycopg's perspective).
        """
        return [s.strip() for s in sql.split(";") if s.strip()]

    # --- check mode (Task 5 fills in) ---

    def _handle_check(self):
        self.stdout.write(self.style.NOTICE("setup_rls --check: not yet implemented (Task 5)"))
```

- [ ] **Step 3.2: Smoke test — run setup_rls in dev**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py setup_rls --verbose-sql --settings=vyntia.settings.development 2>&1 | tail -20
```

Expected: output ending with `setup_rls: applied roles + policies to 32 tables.`

- [ ] **Step 3.3: Verify idempotency — run again, no errors**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py setup_rls --settings=vyntia.settings.development 2>&1 | tail -5
```

Expected: clean second run, same success message.

- [ ] **Step 3.4: Verify tests still pass (dev user is `postgres` superuser → BYPASSRLS implicit)**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥186 passed. Tests are unaffected because `postgres` bypasses RLS.

- [ ] **Step 3.5: Verify policies exist via pg_catalog**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py dbshell --settings=vyntia.settings.development -- -c "SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public' AND tablename LIKE 'employees_%' OR tablename LIKE 'tenancy_%' ORDER BY tablename;" 2>&1 | head -20
```

Expected: rows showing `tenant_isolation` policies on business tables and `membership_isolation` on `tenancy_tenantmembership`.

- [ ] **Step 3.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/management/commands/setup_rls.py
git commit -m "feat(C2): implement setup_rls apply mode (roles + policies on 32 tables)"
```

---

## Task 4: Integration test for `setup_rls`

**Files:**
- Create: `apps/api/apps/tenancy/tests/test_setup_rls_command.py`

- [ ] **Step 4.1: Write integration tests**

```python
"""Integration tests for the setup_rls management command.

These tests exercise the command against the live test DB. They verify:
- Roles are created (vyntia_app, vyntia_admin, vyntia_readonly)
- RLS is enabled on every tenant-scoped table
- The right policy variant is applied per table
- The command is idempotent (re-running succeeds)
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection


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
                WHERE relname = 'employees_employee'
            """)
            enabled, forced = cur.fetchone()
        assert enabled is True
        assert forced is True

    def test_business_table_has_standard_policy(self, run_setup_rls):
        with connection.cursor() as cur:
            cur.execute("""
                SELECT policyname FROM pg_catalog.pg_policies
                WHERE tablename = 'employees_employee'
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
```

- [ ] **Step 4.2: Run integration tests**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_setup_rls_command.py -v 2>&1 | tail -20
```

Expected: 8 tests passed.

- [ ] **Step 4.3: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥194 passed.

- [ ] **Step 4.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/tests/test_setup_rls_command.py
git commit -m "test(C2): integration tests for setup_rls (roles, RLS, policies, idempotency)"
```

---

## Task 5: Implement `--check` mode

**Files:**
- Modify: `apps/api/apps/tenancy/management/commands/setup_rls.py`

- [ ] **Step 5.1: Replace `_handle_check` method**

In `apps/api/apps/tenancy/management/commands/setup_rls.py`, replace the `_handle_check` method body:

```python
    def _handle_check(self):
        """Verify every tenant-scoped table has its RLS policy. Exit 1 on failure."""
        from apps.tenancy.rls.introspection import get_tenant_scoped_models

        models = get_tenant_scoped_models()
        missing = []
        with connection.cursor() as cur:
            for model in models:
                table = model._meta.db_table
                expected_policy = (
                    "membership_isolation" if table in DUAL_CLAUSE_TABLES else "tenant_isolation"
                )
                cur.execute(
                    "SELECT 1 FROM pg_catalog.pg_policies "
                    "WHERE tablename = %s AND policyname = %s",
                    [table, expected_policy],
                )
                if cur.fetchone() is None:
                    missing.append(f"{table} → missing policy '{expected_policy}'")

        if missing:
            self.stdout.write(self.style.ERROR(
                f"setup_rls --check: {len(missing)} tables missing RLS policy:"
            ))
            for line in missing:
                self.stdout.write(self.style.ERROR(f"  - {line}"))
            import sys
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS(
            f"setup_rls --check: all {len(models)} tenant-scoped tables have policies."
        ))
```

- [ ] **Step 5.2: Add tests for `--check` mode**

Append to `apps/api/apps/tenancy/tests/test_setup_rls_command.py`:

```python
@pytest.mark.django_db(transaction=True)
class TestSetupRLSCheck:
    def test_check_passes_after_apply(self):
        call_command("setup_rls")  # apply first
        out = StringIO()
        call_command("setup_rls", "--check", stdout=out)
        assert "all" in out.getvalue() and "policies" in out.getvalue()

    def test_check_fails_when_policy_dropped(self):
        call_command("setup_rls")
        with connection.cursor() as cur:
            cur.execute("DROP POLICY IF EXISTS tenant_isolation ON employees_employee;")
        with pytest.raises(SystemExit) as exc_info:
            call_command("setup_rls", "--check")
        assert exc_info.value.code == 1
```

- [ ] **Step 5.3: Smoke test**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py setup_rls --check --settings=vyntia.settings.development 2>&1 | tail -3
```

Expected: `setup_rls --check: all 32 tenant-scoped tables have policies.`

- [ ] **Step 5.4: Run tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/tenancy/tests/test_setup_rls_command.py -v 2>&1 | tail -15
```

Expected: 10 tests passed (8 from Task 4 + 2 new).

- [ ] **Step 5.5: Run full suite**

```bash
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: ≥196 passed.

- [ ] **Step 5.6: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/tenancy/management/commands/setup_rls.py \
        apps/api/apps/tenancy/tests/test_setup_rls_command.py
git commit -m "feat(C2): setup_rls --check mode for CI verification"
```

---

## Task 6: Production settings + runbook

**Files:**
- Modify: `apps/api/vyntia/settings/production.py`
- Create: `docs/operations/rls-setup.md`

- [ ] **Step 6.1: Update production settings**

In `apps/api/vyntia/settings/production.py`, find the `DATABASES` block. The current default user is likely something like `os.environ.get('DB_USER', 'postgres')`. Change the default to `vyntia_app`:

Find:
```python
"USER": os.environ.get("DB_USER", "postgres"),
```

Replace with:
```python
"USER": os.environ.get("DB_USER", "vyntia_app"),
```

If there are read-replica or other connection blocks in production.py, update them similarly. The migration user (when running `migrate` and `setup_rls` in deploys) should be a separate env var like `DB_MIGRATOR_USER` (defaults to `postgres` or `vyntia_admin` — document in runbook).

- [ ] **Step 6.2: Create runbook `docs/operations/rls-setup.md`**

```markdown
# RLS Setup Runbook

> How to provision PostgreSQL roles and apply RLS policies for VYNTIA in any environment.

## Overview

VYNTIA uses PostgreSQL Row-Level Security (RLS) for tenant data isolation. The
`setup_rls` Django management command provisions 3 roles and applies policies
to every tenant-scoped table.

- **Roles:** `vyntia_app` (NO BYPASSRLS — used by Django app), `vyntia_admin`
  (BYPASSRLS — used by migrations + ETL), `vyntia_readonly` (NO BYPASSRLS,
  SELECT-only — used by reporting tools).
- **Policies:** standard tenant-only on business tables, dual-clause
  (tenant OR user) on `tenancy_tenantmembership` for the workspace switcher.
- **`FORCE ROW LEVEL SECURITY`** is enabled — even the table owner respects
  policies. Only `vyntia_admin` (BYPASSRLS) sees cross-tenant.

## Prerequisites

- PostgreSQL 15+
- Database created with migrations applied (`manage.py migrate`)
- A connection user with `CREATEROLE` privilege (typically `postgres`
  superuser) for the duration of `setup_rls` execution

## Initial deployment

In production, the deploy pipeline should:

1. Apply Django migrations as `vyntia_admin` (BYPASSRLS):
   ```bash
   DB_USER=vyntia_admin python manage.py migrate --settings=vyntia.settings.production
   ```

2. Run `setup_rls` as `postgres` superuser (needed for CREATEROLE):
   ```bash
   DB_USER=postgres python manage.py setup_rls --settings=vyntia.settings.production
   ```

3. Application runtime connects as `vyntia_app` (no BYPASSRLS — this is the
   default in `vyntia.settings.production`):
   ```bash
   # Default DB_USER=vyntia_app
   gunicorn vyntia.wsgi:application
   ```

## Local development

Dev environments default to `postgres` user (BYPASSRLS implicit). RLS is
**not enforced** in dev unless you explicitly run `setup_rls`. Tests pass
either way because the test DB user is also `postgres`.

To experiment with RLS locally:

```bash
cd apps/api
python manage.py setup_rls --settings=vyntia.settings.development
# Now policies are in place. To see them work, switch DB_USER to vyntia_app:
DB_USER=vyntia_app python manage.py shell
# >>> from apps.employees.models import Employee
# >>> Employee.objects.all()  # Returns 0 rows — app.tenant_id not set
```

To set the tenant context manually for testing:

```sql
SET LOCAL app.tenant_id = '00000000-0000-0000-0000-000000000001';
```

## Verification (CI)

Add to your CI pipeline after deploy:

```bash
python manage.py setup_rls --check --settings=vyntia.settings.production
```

Exits with status 1 and lists missing policies if any tenant-scoped table
lacks an RLS policy. Should be green on every successful deploy.

## Idempotency

`setup_rls` is idempotent — safe to re-run after migrations, schema changes,
or new tenant-scoped models. It uses `DROP POLICY IF EXISTS` then `CREATE
POLICY`, so re-runs always converge on the canonical state.

When adding a new tenant-scoped model in code:
1. Run `manage.py migrate` to add the column
2. Run `manage.py setup_rls` to apply the policy to the new table

## Troubleshooting

### "permission denied for relation X"

The application connects as `vyntia_app` but the `GRANT` was missed for that
table. Re-run `setup_rls` as `postgres`.

### "RLS policy returns 0 rows for everything"

`app.tenant_id` is not being set on the connection. This is C.3's job
(`RLSMiddleware`). Until C.3 ships, `vyntia_app` connections will return
empty results — which is why dev defaults to `postgres` (BYPASSRLS).

### "CREATE ROLE permission denied"

Run `setup_rls` as the `postgres` superuser (or any role with `CREATEROLE`).
Check via:
```sql
SELECT rolname, rolcreaterole, rolsuper FROM pg_catalog.pg_roles WHERE rolname = current_user;
```

## Manual verification queries

```sql
-- List all RLS policies in the public schema
SELECT tablename, policyname, cmd, qual
FROM pg_catalog.pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- Check if RLS is enabled and forced on a specific table
SELECT relname, relrowsecurity, relforcerowsecurity
FROM pg_catalog.pg_class
WHERE relname = 'employees_employee';

-- List the 3 vyntia roles and their bypass status
SELECT rolname, rolbypassrls, rolcreaterole, rolsuper
FROM pg_catalog.pg_roles
WHERE rolname LIKE 'vyntia_%'
ORDER BY rolname;
```
```

- [ ] **Step 6.3: Verify settings change doesn't break dev**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.production 2>&1 | tail -3
```

Note: production settings may require additional env vars to fully boot. The check is acceptable if it errors on missing env vars unrelated to DATABASES.USER. The point is: confirm the change is syntactically valid Python.

- [ ] **Step 6.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/vyntia/settings/production.py \
        docs/operations/rls-setup.md
git commit -m "docs(C2): RLS setup runbook + production settings switch to vyntia_app"
```

---

## Task 7: Final verification + merge

- [ ] **Step 7.1: Full backend pytest baseline**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development 2>&1 | tail -2
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: ≥196 passed (176 baseline + ~20 new for C.2). Check clean. No pending migrations.

- [ ] **Step 7.2: Verify --check passes in dev**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py setup_rls --check --settings=vyntia.settings.development 2>&1 | tail -3
```

Expected: `all 32 tenant-scoped tables have policies.`

- [ ] **Step 7.3: Frontend baseline (sanity — no FE changes)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
```

Expected: build exit 0.

- [ ] **Step 7.4: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.2 row and update the "Detailed plan" cell to:

```
`2026-05-09-vyntia-C2-rls-policies.md` ✅ merged 2026-05-09
```

- [ ] **Step 7.5: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C2): mark C.2 done in master roadmap"
```

- [ ] **Step 7.6: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C2-rls-policies \
  -m "Merge C.2: PostgreSQL RLS roles + policies + setup_rls command"
```

Expected: clean merge.

- [ ] **Step 7.7: Verify post-merge**

```bash
git log --oneline -3
git status
```

Expected: working tree clean, HEAD on the merge commit.

---

## Self-Review

### Spec coverage check

| Spec § 4 requirement | Covered by task |
|---|---|
| 3 PostgreSQL roles with correct BYPASSRLS settings | Task 3 (apply mode) |
| `ENABLE ROW LEVEL SECURITY` + `FORCE` on every business table | Task 3 |
| `tenant_isolation` policy with `current_setting('app.tenant_id', TRUE)::uuid` | Task 2 (SQL gen) + Task 3 (apply) |
| Dual-clause policy on `tenancy_tenantmembership` | Task 2 + Task 3 |
| GRANT DML to `vyntia_app`, SELECT to `vyntia_readonly` | Task 2 + Task 3 |
| `setup_rls` management command | Task 1 (skeleton) + Task 3 (apply) + Task 5 (--check) |
| Idempotency | Task 3 (DROP POLICY IF EXISTS) + Task 4 (idempotent test) |
| Production settings switch to `vyntia_app` | Task 6 |
| Runbook documentation | Task 6 |

### Spec deviations

1. **`tenancy_tenant` table** — spec § 4.2 mentions a "policy variant" applied to both `tenancy_tenant` and `tenancy_tenantmembership`. This plan applies dual-clause only to `tenancy_tenantmembership`; `tenancy_tenant` keeps the standard policy. **Rationale:** the workspace switcher reads `TenantMembership` rows first (filtered by user_id), then follows the FK to `Tenant` — at that point the membership row already authorized the user, and the standard policy on `Tenant` works because we're in the user's tenant context after the JOIN. Adding a dual-clause policy on `Tenant` would expose tenant existence info via timing/error messages. The simpler path is preferred.

2. **Migration user** — spec § 4.1 has both `vyntia_admin` and `vyntia_migrator`. This plan uses `vyntia_admin` for both deploys and migrations (single role). The `vyntia_reporter` user mentioned in the spec is renamed to `vyntia_readonly` for clarity (consistent with the role name).

### Placeholder scan

- All code blocks contain runnable code.
- All file paths are absolute or workspace-relative.
- No "TBD" or "TODO" except a deliberate one in Task 5 marker for `--check` test of the missing-policy case.

### Type consistency

- Constants `APP_ROLE`, `ADMIN_ROLE`, `READONLY_ROLE` defined once in `policies.py`, imported in `setup_rls.py`. Single source of truth.
- Policy names `tenant_isolation` and `membership_isolation` consistent across SQL generators, command, and `--check` mode.
- Table list comes from `get_tenant_scoped_models()` consistently in `apply` and `check` paths.

### Out of scope (deferred)

- `RLSMiddleware` to set `app.tenant_id` on each request (C.3)
- `TenantManager`/`UnsafeManager` Django ORM layer (C.3)
- Subdomain resolution (C.3)
- Tests proving RLS actually blocks cross-tenant queries when `vyntia_app` user is used (C.3 — depends on middleware)

---

**Plan complete.** When executed, C.2 ships ~7 commits, ~6 new files (~600 LOC), 1 modified settings file, ~20 new tests. Tests baseline grows from 176 → ~196. Frontend untouched.
