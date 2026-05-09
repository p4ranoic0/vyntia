# Restore Tenant Runbook

> How to restore a tenant from backup — single-tenant restore inside a
> shared Postgres DB.

## Overview

VYNTIA's database strategy for the C series is **shared schema, RLS-isolated**
— one Postgres database with all tenants' rows commingled, RLS policies enforcing
isolation. This makes per-tenant restores non-trivial: the standard
`pg_restore` operates at database/schema level, not row-level.

The pragmatic restore strategy:

1. **Backup capture (continuous):** nightly `pg_dump` of the entire database
   stored in encrypted offsite storage. Retention: 30 days.
2. **Per-tenant export (on-demand):** `manage.py export_tenant <slug>` (NOT
   YET IMPLEMENTED — placeholder; see Future work) dumps a single tenant's
   rows from every tenant-scoped table to a JSON archive.
3. **Per-tenant restore:** restore the JSON archive into a fresh tenant or
   merge into an existing one.

For now, restore = full DB restore to a staging instance + manual extraction.

## Use cases

- **Customer-driven undo:** "We accidentally deleted everyone's vacation
  balance, please restore from yesterday." → Full DB restore to staging,
  extract that tenant's `vacation_*` tables, copy back to prod.
- **Disaster recovery:** prod DB corruption → restore latest backup to a
  new instance, point app at it. (This is a global operation, not
  per-tenant.)
- **Mistaken cancellation:** customer was cancelled prematurely → see the
  **Suspend Tenant** runbook's "Reverse a cancellation" section first.
  Restore from backup is only needed if data was purged after the 30-day
  window (currently manual purge — has not been triggered as of this
  runbook's authorship).

## Prerequisites

- Access to the encrypted backup bucket.
- A staging Postgres 15 instance with capacity ≥ prod DB.
- The target tenant's slug + the desired backup timestamp.
- Approval from the customer (the data is theirs; they must request the
  restore in writing via support ticket).

## Procedure: full restore to staging

1. **Provision staging Postgres:**
   ```bash
   pg_restore --create -d postgres -j 4 vyntia-2026-05-08.dump
   ```
2. **Apply RLS policies on staging:**
   ```bash
   cd apps/api && python manage.py setup_rls --settings=vyntia.settings.staging
   ```
3. **Verify the target tenant exists in the restored DB:**
   ```sql
   SELECT id, slug, status FROM tenancy_tenant WHERE slug = '<target>';
   ```

## Procedure: extract a single tenant's data

For each affected table, write a CSV with `tenant_id = '<target-uuid>'`:

```sql
\copy (SELECT * FROM time_off_vacationrequest WHERE tenant_id = '<uuid>')
  TO '/tmp/vacation_requests_acme.csv' CSV HEADER;
```

Repeat for every table in the affected scope. Use the table list from
`manage.py shell --settings=vyntia.settings.staging`:

```python
from apps.tenancy.rls.introspection import get_tenant_scoped_models
for m in get_tenant_scoped_models():
    print(m._meta.db_table)
```

## Procedure: merge back into prod

This is the dangerous part. Test in staging first.

1. **Pause writes** for the target tenant: suspend it via admin panel (see
   **Suspend Tenant** runbook). This blocks members from creating new data
   that would conflict with the restore.
2. **Backup the current state** (full prod dump) — defense in depth.
3. **Truncate the affected tables FOR THIS TENANT ONLY** in prod:
   ```sql
   DELETE FROM time_off_vacationrequest WHERE tenant_id = '<uuid>';
   ```
   ⚠️ Without `tenant_id` filter, you will wipe all tenants' data.
4. **Load the CSV back in:**
   ```sql
   \copy time_off_vacationrequest FROM '/tmp/vacation_requests_acme.csv' CSV HEADER;
   ```
5. **Verify counts** match the staging extract.
6. **Un-suspend the tenant** (see **Suspend Tenant** → Reverse a suspension).

## Verification

- Member can log in and see the restored data.
- No leak: a member of a different tenant cannot see the restored rows
  (run `test_tenant_isolation.py` against staging post-restore).
- Audit log: insert a row into `tenancy_supportsession` documenting the
  restore action with `reason="Restore from backup yyyy-mm-dd"`.

## Future work

- `manage.py export_tenant <slug>` — single-command JSON export.
- `manage.py import_tenant <archive>` — single-command import with conflict
  resolution.
- Automated nightly per-tenant snapshots stored separately from the global
  dump (priced per tenant).
- Postgres row-level archiving via `pg_partman` partitioning by `tenant_id`
  (deferred — not on roadmap).

## References

- Spec: § 13 (Open questions: backups, retention)
- RLS introspection: `apps/api/apps/tenancy/rls/introspection.py`
- Roles: see `docs/operations/rls-setup.md`
