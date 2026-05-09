# Impersonate User Runbook

> How a Vyntia support engineer assumes a customer user's session for
> debugging purposes — and how the audit trail is recorded.

## Overview

Impersonation lets staff (`is_vyntia_staff=True`) reproduce a customer's
exact view of the application: same permissions, same data scope, same
tenant context. Every impersonation:

- Creates a `SupportSession` row with `staff_user`, `target_user`, `tenant`,
  `reason`, `started_at`, `expires_at`.
- Issues a special JWT carrying both `tenant_id` (the target's tenant) and
  `impersonated_by` (the staff user) claims.
- Triggers a sticky amber banner on every page in the target's app:
  "Sesión de soporte Vyntia activa — todas las acciones quedan registradas."
- Increments `actions_count` on the SupportSession every time the impersonation
  token is used to mutate state (writes only — reads are not counted to keep
  the audit log meaningful).

## Prerequisites

- Vyntia staff JWT (login on `admin.vyntia.pe`).
- The target user's email or username.
- A documented reason (free-text, mandatory) — appears in the audit log.

## Procedure

The admin UI for this is deferred (per C.7 spec deviation). Use the API
directly:

```bash
# Step 1: search for the target user
curl "https://admin.vyntia.pe/api/admin/users/?q=customer.email@acme.com" \
  -H "Authorization: Bearer <staff-jwt>"

# Step 2: open an impersonation session
curl -X POST https://admin.vyntia.pe/api/admin/users/<user-id>/impersonate/ \
  -H "Authorization: Bearer <staff-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Investigating ticket #12345 — vacation balance discrepancy"}'
```

Response:

```json
{
  "success": true,
  "data": {
    "support_session_id": "...",
    "access_token": "<impersonation JWT>",
    "expires_at": "<ISO timestamp, ~1h from now>",
    "redirect_url": "https://acme.vyntia.pe/auth/exchange?token=..."
  }
}
```

Open the `redirect_url` in an incognito browser window. The customer's
app loads with the staff user assuming the target's session. The amber
banner is visible at the top of every authenticated page.

## Ending a session

Sessions auto-expire at `expires_at` (typically 1 hour). To end early:

```bash
curl -X POST https://admin.vyntia.pe/api/admin/support-sessions/<id>/end/ \
  -H "Authorization: Bearer <staff-jwt>"
```

(If the `/end/` endpoint is not exposed, simply close the browser; the next
mutating request after `expires_at` will be rejected.)

## Verification

1. **SupportSession exists:**
   ```sql
   SELECT staff_user_id, target_user_id, reason, started_at, expires_at, ended_at, actions_count
     FROM tenancy_supportsession ORDER BY started_at DESC LIMIT 5;
   ```
2. **Banner visible:** load any page on the customer's subdomain in the
   impersonation browser — amber banner at top with `role="alert"`.
3. **Audit page lists the session:** `admin.vyntia.pe` → **Support Sessions**
   shows the session as "Activa" until `ended_at` is set or the session
   expires.

## Constraints

- **Never share the impersonation token** outside the support engineer who
  created it. The token effectively *is* the customer's identity.
- **Document the reason** — free text, but legible. The audit log is
  reviewed quarterly.
- **Don't perform destructive actions** (delete records, cancel contracts)
  while impersonating unless the customer has authorized it in writing
  via the support ticket.
- Read-only investigations are zero-friction; write actions surface the
  banner unmissably.

## References

- Spec: § 7.3 (Impersonation)
- Backend: `apps/api/api/admin/users/views.py` (UserImpersonateView), `apps/api/apps/tenancy/auth/impersonation.py`
- Admin UI: `apps/web/src/features/admin/pages/SupportSessionsListPage.tsx`
- Banner: `apps/web/src/features/tenancy/components/ImpersonationBanner.tsx`
