# Suspend Tenant Runbook

> How to suspend (or cancel) a tenant — block all members from logging in,
> while preserving data for possible restoration.

## Overview

Suspending a tenant flips its `status` field from `active`/`trial` to
`suspended`. The login flow rejects any session attempt against a suspended
tenant with a clear message. Data is **NOT deleted** — suspension is reversible
by flipping the status back. **Cancellation** is a separate, harder-to-undo
state (still reversible at DB level but the UI doesn't expose un-cancel).

Use cases:
- **Suspend:** delinquent payment, contract dispute, security investigation.
- **Cancel:** customer churn, end of trial without conversion.

## Prerequisites

- Vyntia staff user (`is_vyntia_staff=True`).
- The target tenant's slug or UUID.
- Approval from finance/legal for cancel actions.

## Procedure (admin panel)

1. Log in to `admin.vyntia.pe`.
2. Tenants → click on the target tenant slug → **Detalle**.
3. Click **Suspender** (orange) for reversible suspension, OR
   **Cancelar tenant** (red) for cancellation. Confirmation prompt appears
   for cancel.

## Procedure (API)

```bash
# Suspend
curl -X POST https://admin.vyntia.pe/api/admin/tenants/<id>/suspend/ \
  -H "Authorization: Bearer <staff-jwt>"

# Cancel
curl -X POST https://admin.vyntia.pe/api/admin/tenants/<id>/cancel/ \
  -H "Authorization: Bearer <staff-jwt>"
```

## Verification

1. **Status flipped:**
   ```sql
   SELECT slug, status, cancelled_at FROM tenancy_tenant WHERE id = '...';
   ```
   - Suspend: `status = 'suspended'`, `cancelled_at` NULL.
   - Cancel: `status = 'cancelled'`, `cancelled_at` set.

2. **Login attempt blocked:** open `<slug>.vyntia.pe`, attempt to log in
   as any member — the response should be 403 with a "tenant suspended"
   message (not 401 — the credentials are valid, the tenant just doesn't
   accept sessions).

3. **JWT-already-issued check:** any access token issued before suspension
   may still work for up to 5 minutes (until expiry). After refresh, the
   refresh request will be rejected. This is by design — short-lived access
   tokens are the security boundary.

## Reverse a suspension

Set status back to `active` (or `trial` if the trial isn't over):

```sql
UPDATE tenancy_tenant SET status = 'active', cancelled_at = NULL WHERE id = '...';
```

Or via the admin API (if exposed; otherwise DB only). Members can log in
on next attempt; no data was lost.

## Reverse a cancellation

Cancellation is reversible but no UI button — DB only:

```sql
UPDATE tenancy_tenant SET status = 'active', cancelled_at = NULL WHERE id = '...';
```

After 30 days from `cancelled_at`, automated cleanup may purge the data
(currently manual). Confirm data still exists before un-cancelling.

## References

- Spec: § 7 (Provisioning), § 7.3 (Lifecycle)
- Backend: `apps/api/api/admin/tenants/views.py` (TenantSuspendView, TenantCancelView)
- Admin UI: `apps/web/src/features/admin/pages/TenantDetailPage.tsx`
