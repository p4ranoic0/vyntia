# Sub-Project C — Multi-Tenancy + RLS — Master Roadmap

> **For agentic workers:** This is a roadmap, not an executable plan. Per-sub-layer detailed plans live alongside this file (e.g., `2026-05-09-vyntia-C0-tenancy-foundations.md`) and are generated AFTER the previous sub-layer merges to incorporate lessons learned. To execute, work on one sub-layer at a time using `superpowers:subagent-driven-development` against the detailed plan.

**Goal:** Transform the single-tenant Foundation codebase into a multi-tenant SaaS with PostgreSQL RLS-enforced data isolation, admin-provisioned tenants, subdomain routing, and global-identity multi-workspace user model — ready to onboard the first paying customer.

**Architecture:** Defense in depth — Django middleware layer (`TenantManager` + `ContextVar`) as primary tenant scoping, PostgreSQL RLS policies as cryptographic safety net. Wildcard DNS `*.vyntia.pe` routes each tenant to its subdomain. Global `User` model with M2M `TenantMembership` allows one identity to belong to multiple tenants (Slack pattern). Vyntia staff manages tenant lifecycle via dedicated `admin.vyntia.pe` panel.

**Tech Stack:** Django 5.2 + DRF, PostgreSQL 15+ RLS, JWT (existing rest_framework_simplejwt), React 18 + Vite + TypeScript, wildcard TLS cert (Let's Encrypt or vendor).

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` (locked 2026-05-09)

---

## Why split into 9 sub-PRs

Sub-project C touches every business model in the codebase (~30+ tables get `tenant_id`). Doing it as a single mega-PR creates several risks:

1. **Review impossibility** — a 5000+ line PR is unreviewable.
2. **Rollback fragility** — any single bug forces a full revert.
3. **Merge conflicts** — long-running branch diverges painfully from `master`.
4. **Lessons lost** — the team learns less from one big swing than from 9 incremental ones.
5. **Test feedback delay** — broken isolation only surfaces at the very end.

The 9-sub-layer approach mirrors Foundation's L3 (Django app split into 11 sub-PRs) and L4 (frontend reorg into 11 sub-PRs) — both shipped on time with clean baselines preserved per merge.

**Each sub-layer is independently mergeable:** lands on `master`, baselines (pytest 161/8/3, vitest 7, build clean) preserved or improved, before the next branches off.

---

## Sub-layer table

| Sub | Branch | Layer | Scope | Detailed plan |
|-----|--------|-------|-------|---------------|
| **C.0** | `vyntia/C0-tenancy-foundations` | Backend | Create `apps/tenancy/` Django app with 4 models (`Tenant`, `TenantMembership`, `TenantInvitation`, `SupportSession`) + Django admin. NO `tenant_id` added to other apps yet. | `2026-05-09-vyntia-C0-tenancy-foundations.md` ✅ merged 2026-05-09 |
| **C.1** | `vyntia/C1-tenant-id-migration` | Backend (DB) | Add `tenant = FK(Tenant)` to all business models across 7 apps. Composite uniques on key fields. `CompanyConfig` deserialized from singleton to per-tenant. Blank-slate DB strategy (drop + regenerate, no data retrofit). `TenantScopedModel` abstract base in `apps/core/`. | `2026-05-09-vyntia-C1-tenant-id-migration.md` ✅ merged 2026-05-09 |
| **C.2** | `vyntia/C2-rls-policies` | Backend (DB) | PostgreSQL roles (`vyntia_app`, `vyntia_admin`, `vyntia_readonly`). `setup_rls` management command (idempotent). All tenant-scoped tables get `ENABLE ROW LEVEL SECURITY` + `FORCE` + tenant policy. Production settings switch to `vyntia_app`. Dual-clause policy on `tenancy_tenantmembership` and `tenancy_tenant`. | `2026-05-09-vyntia-C2-rls-policies.md` ✅ merged 2026-05-09 |
| **C.3** | `vyntia/C3-tenant-middleware` | Backend (Django) | `TenantMiddleware` (subdomain → Tenant resolution, reserved-subdomain handling). `RLSMiddleware` (`SET LOCAL app.tenant_id` + `app.user_id`). `TenantManager` + `UnsafeManager`. `tenant_context()` ContextVar utilities. `TenantAuthMiddleware` validates JWT.tenant_id matches request.tenant.id. | `2026-05-09-vyntia-C3-tenant-middleware.md` ✅ merged 2026-05-09 |
| **C.4** | `vyntia/C4-auth-tenant-aware` | Backend (Auth) | Tenant-aware login (membership lookup via RLS). Activation endpoint (`POST /auth/activate/`). Workspace listing (`GET app.vyntia.pe/api/v1/workspaces/`) and exchange flow. JWT claims include `tenant_id`, `tenant_slug`, `membership_role`. | TBD after C.3 merges |
| **C.5** | `vyntia/C5-admin-api` | Backend (Admin) | `/api/admin/tenants/*` endpoints behind `is_vyntia_staff` permission. `setup_tenant_seed` helper (default Roles + Permissions + Module bindings per plan). Impersonation flow + `SupportSession` audit log. | TBD after C.4 merges |
| **C.6** | `vyntia/C6-frontend-tenant` | Frontend | `TenantProvider` (boot-time slug resolution), `WorkspaceSwitcher` (app.vyntia.pe), `ActivationPage` (/activate?token=...), `TenantSettingsPage`, `MembershipsPage`, `ImpersonationBanner`, `TenantBadge`. Updated `apiClient` with token-tenant validation. | TBD after C.4 merges (parallel with C.5/C.7) |
| **C.7** | `vyntia/C7-admin-panel-frontend` | Frontend | `admin.vyntia.pe` UI: `TenantsListPage`, `TenantDetailPage`, `CreateTenantPage`, `ImpersonationLogPage`. Branched routing in `App.tsx` based on subdomain. | TBD after C.5 merges (parallel with C.6) |
| **C.8** | `vyntia/C8-isolation-tests-docs` | Tests + Docs | `tests/test_tenant_isolation.py` (ORM, RLS raw-SQL, JWT cross-tenant). Playwright e2e `tests/e2e/tenant-isolation.test.js`. Runbooks (`docs/operations/{provision,suspend,impersonate,restore}.md`). CI `rls-policy-audit` job. | TBD after C.7 merges |

---

## Order and dependencies

```
C.0 → C.1 → C.2 → C.3 → C.4 ┬→ C.5 → C.7 ┐
                            └→ C.6 ──────┴→ C.8
```

- **C.0 → C.4 are strictly sequential** (each builds on the previous).
- **C.5 (admin API) and C.6 (tenant frontend) can run in parallel** after C.4 merges — they touch disjoint codebases.
- **C.7 (admin frontend) needs C.5** (consumes admin API) but is independent of C.6.
- **C.8 needs everything** (tests + ops runbooks for the complete system).

This means after C.4 merges, two parallel work streams open up. With the L4 pattern of subagent-driven development, both can land within days of each other.

---

## Per-sub-layer baselines (must be preserved or improved)

| Check | Command | Expected after every merge |
|---|---|---|
| Django system check | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ -q` | ≥161 passed / ≤8 failed / 3 skipped (target: grow toward 200+ as tenancy tests are added) |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |
| Frontend types | `cd apps/web && npx tsc --noEmit -p tsconfig.app.json` | 1 error (BlankEnum.ts pre-existing — unchanged) |
| Frontend tests | `cd apps/web && npm test -- --run` | ≥7 passed |
| Frontend lint | `cd apps/web && npm run lint` | ≤634 warnings (pre-existing baseline) |

Tenancy-specific checks added incrementally:

| Check | First active in | Expected |
|---|---|---|
| `pytest apps/api/apps/tenancy/tests/` | C.0 | tenancy app tests pass (~15-20 cases) |
| `pytest apps/api/tests/test_tenant_isolation.py` | C.3 | ORM isolation tests pass |
| RLS raw-SQL leak tests | C.3 | RLS blocks cross-tenant raw queries |
| `manage.py setup_rls --check` | C.2 | every tenant-scoped table has its policy |
| Playwright tenant isolation E2E | C.8 | ≥3 e2e tests pass |
| CI `rls-policy-audit` job | C.8 | green |

---

## Definition of Done (sub-project C)

- [ ] All 9 sub-layers (C.0–C.8) merged to `master` with `--no-ff`
- [ ] `git tag c-multitenancy-complete` applied
- [ ] `pytest tests/` ≥ 200 passed, no regressions from baseline
- [ ] `pytest tests/test_tenant_isolation.py` 100% pass
- [ ] `manage.py setup_rls --check` clean
- [ ] `npm run build` exit 0, `npm test -- --run` ≥ 20 passed
- [ ] CI `rls-policy-audit` job green
- [ ] Manual smoke: provision a tenant via `admin.vyntia.pe`, accept invitation, log in, verify isolation against a second tenant
- [ ] Runbooks committed: `docs/operations/{provision-tenant,suspend-tenant,impersonate-user,restore-tenant}.md`
- [ ] `docs/ROADMAP_SUBPROJECTS.md` updated: C ✅, B unblocked
- [ ] `CLAUDE.md` updated: active sub-project = B (Vyntia Core functional migration)
- [ ] Memory file `active_subproject.md` updated

---

## Conventions (reused from Foundation)

| Convention | Pattern |
|---|---|
| Branch name | `vyntia/C<N>.<sub>-<short-description>` |
| Commit prefix | `chore(C<N>):`, `feat(C<N>):`, `fix(C<N>):`, `docs(C<N>):`, `test(C<N>):` |
| Merge style | `git merge --no-ff` to preserve sub-layer history |
| Atomic commits | One commit per task in the sub-layer's plan |
| Rename-detection-friendly moves | `git mv` on file moves, body-only changes in separate commits |

---

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| RLS policy bug allows cross-tenant leak | CRITICAL — data breach | C.8 isolation tests run on every PR; `rls-policy-audit` CI job blocks merge if policy missing; pen-testing before first paying customer |
| `tenant_id` migration breaks existing dev data | LOW — spec says blank-slate | Document the DB drop+regenerate procedure in C.1 plan; use `vyntia_admin` for the migration |
| Performance regression from RLS overhead | MEDIUM — degraded UX | C.8 includes a benchmark suite; if median query time grows >15%, revisit indexes |
| Wildcard TLS cert expiry / renewal | HIGH — outage | C.8 runbook covers cert provisioning + auto-renewal via Let's Encrypt + cron alert |
| Reserved-subdomain collision with future feature | LOW | C.0 ships a `RESERVED_SUBDOMAINS` constant; spec § 2 lists the canonical set |
| Workspace switcher exposes tenant existence to bad actors | MEDIUM | The widened `TenantMembership` policy keys on `app.user_id` — only the user's own memberships are visible |
| Impersonation abuse by Vyntia staff | HIGH (legal) | `SupportSession` audits every action; customer can view all impersonations on their tenant; reason field mandatory; max session 2h |

---

## Out of scope (will not ship in C)

- Public self-service signup
- Stripe / Culqi billing automation
- Per-tenant feature flags / plan-based module gating
- DB-per-tenant tier (premium upsell)
- Custom domains (`hr.acme.com` instead of `acme.vyntia.pe`)
- SCIM / SAML / SSO
- Multi-region / data residency
- Audit log retention beyond 90 days

These are tracked in `docs/ROADMAP_SUBPROJECTS.md` and the spec § 1, and become future sub-projects after C ships.

---

**Next step:** Execute C.0 using the detailed plan at `docs/superpowers/plans/2026-05-09-vyntia-C0-tenancy-foundations.md`. Once C.0 merges to `master`, the C.1 detailed plan is generated incorporating lessons from C.0 execution.
