# Provision Tenant Runbook

> How to create a new VYNTIA tenant (workspace) and send the activation invitation.

## Overview

A "tenant" in VYNTIA is a customer workspace at `<slug>.vyntia.pe`. Provisioning
creates the `Tenant` row + the seed config (default Roles, Permissions, Module
bindings) + a first-admin invitation email containing an activation link.

The flow has two implementations:

1. **Admin panel UI (preferred):** `admin.vyntia.pe` → Tenants → Nuevo tenant.
   Form-based, validated, surfaces errors. Use this in 99% of cases.
2. **Direct API call:** `POST /api/admin/tenants/` with the same payload as
   the UI. Use this for scripted / batch provisioning only.

## Prerequisites

- A Vyntia staff user (`is_vyntia_staff=True`) with valid login on
  `admin.vyntia.pe`.
- The customer's legal data: RUC (11 digits), legal name, desired
  subdomain slug (must be a–z/0–9/hyphens, not in `RESERVED_SUBDOMAINS`),
  plan tier (`starter`/`pro`/`enterprise`/`govtech`), trial period in days.
- The customer's first admin: name + email. They will receive the
  activation link.
- (For self-hosted DNS) a CNAME for `<slug>.vyntia.pe` pointing to the
  app load balancer. Cloudflare provisioning is currently manual.

## Procedure (admin panel)

1. Log in to `https://admin.vyntia.pe`.
2. Click **Tenants** → **Nuevo tenant**.
3. Fill the form:
   - **Slug (subdomain):** `acme` → resolves to `acme.vyntia.pe`.
   - **Nombre legal:** Customer's legal name as on RUC.
   - **RUC:** 11 digits. Validated client-side.
   - **Plan:** Choose tier.
   - **Trial (días):** Days until trial expires (`trial_ends_at`). Typical: 30.
   - **Nombre del admin / Email del admin:** First user. They receive the link.
4. Click **Crear tenant**. On success, a toast shows the activation URL —
   copy it to the customer through the agreed channel (the email is also
   sent automatically by C.4 backend).
5. The tenant lands on the list with status `trial` and member count `0`.

## Procedure (API)

```bash
curl -X POST https://admin.vyntia.pe/api/admin/tenants/ \
  -H "Authorization: Bearer <staff-jwt>" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "acme",
    "name": "Acme Corp S.A.C.",
    "ruc": "20123456789",
    "plan": "starter",
    "trial_days": 30,
    "admin_email": "ceo@acme.com",
    "admin_name": "María Pérez"
  }'
```

Response:

```json
{
  "success": true,
  "data": {
    "tenant": { "id": "...", "slug": "acme", "status": "trial", ... },
    "invitation": {
      "id": "...",
      "email": "ceo@acme.com",
      "expires_at": "...",
      "activation_url": "https://acme.vyntia.pe/activate?token=..."
    }
  }
}
```

## Verification

After provisioning:

1. **Tenant row exists:**
   ```sql
   SELECT id, slug, status, plan FROM tenancy_tenant WHERE slug = 'acme';
   ```
2. **Seed CompanyConfig + default Roles/Permissions:**
   ```sql
   SELECT COUNT(*) FROM identity_role WHERE tenant_id = (SELECT id FROM tenancy_tenant WHERE slug='acme');
   ```
   Expect ≥ 3 (admin, hr, employee).
3. **Invitation row exists, not yet consumed:**
   ```sql
   SELECT email, expires_at, consumed_at FROM tenancy_tenantinvitation
     WHERE tenant_id = (SELECT id FROM tenancy_tenant WHERE slug='acme');
   ```
   `consumed_at` should be NULL.
4. **DNS resolves** (manual): `dig acme.vyntia.pe` returns the LB IP.
5. **Customer can reach the activation page** — open the URL in an
   incognito window; the form should render and accept name + password.

## Rollback

If the tenant was created in error AND has not been activated:

```sql
DELETE FROM tenancy_tenantinvitation WHERE tenant_id = '...';
DELETE FROM tenancy_tenant WHERE id = '...';
```

If the tenant has been activated (members exist), follow the **Suspend
Tenant** runbook instead — never hard-delete an active tenant.

## References

- Spec: `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 6 (Auth flow), § 7 (Provisioning)
- Backend code: `apps/api/api/admin/tenants/views.py`, `apps/api/apps/tenancy/seeding.py`
- Admin UI: `apps/web/src/features/admin/pages/CreateTenantPage.tsx`
