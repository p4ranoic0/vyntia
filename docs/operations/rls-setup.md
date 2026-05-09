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

1. Apply Django migrations as `vyntia_admin` (BYPASSRLS) or `postgres`:
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
either way because the test DB user is also `postgres` (and pytest uses
SQLite for many tests, which doesn't support RLS at all — those are skipped).

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
WHERE relname = 'empleado';

-- List the 3 vyntia roles and their bypass status
SELECT rolname, rolbypassrls, rolcreaterole, rolsuper
FROM pg_catalog.pg_roles
WHERE rolname LIKE 'vyntia_%'
ORDER BY rolname;
```
