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
        """Split a multi-statement SQL string on ';' boundaries.

        Naive split — fine because our generators don't use ';' inside string
        literals or DO blocks (DO blocks are atomic from psycopg's perspective).
        """
        return [s.strip() for s in sql.split(";") if s.strip()]

    # --- check mode ---

    def _handle_check(self):
        """Verify every tenant-scoped table has its RLS policy. Exit 1 on failure."""
        import sys

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
                    missing.append(f"{table} -> missing policy '{expected_policy}'")

        if missing:
            self.stdout.write(self.style.ERROR(
                f"setup_rls --check: {len(missing)} tables missing RLS policy:"
            ))
            for line in missing:
                self.stdout.write(self.style.ERROR(f"  - {line}"))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS(
            f"setup_rls --check: all {len(models)} tenant-scoped tables have policies."
        ))
