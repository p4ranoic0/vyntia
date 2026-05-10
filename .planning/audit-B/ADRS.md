# Sub-project B — Architectural Decision Records

> Cross-cutting decisions to lock before B.1. Each ADR follows the format:
> Title / Context / Decision / Consequences / Status (proposed | accepted | superseded).

## ADR-B.1: i18n strategy

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** The current VYNTIA UI ships only Spanish strings (es-PE), with copy hard-coded in JSX and Django templates. The Maestro positions VYNTIA in the Peru GovTech tier first, with potential LATAM expansion (Colombia, Chile, México) in the long term. No current customer or design partner has requested an English UI, and SERVIR/LCT terminology is intrinsically Spanish. Adding a full i18n stack now (react-i18next + Django gettext + extraction tooling + translator workflow) would tax every B phase by ~10–15% on string-heavy work and gate every PR on translation review.

Sub-project B is the path to a sellable Vyntia Core. Multi-language is not a sales blocker today, and adopting i18n later is technically harder than starting with it but well within scope of a future dedicated sub-project (e.g., LATAM expansion).

**Decision:** Spanish-only (es-PE) for the entirety of sub-project B. No i18n infrastructure is introduced. Strings remain in code/templates. Multi-language support is deferred to a post-B sub-project triggered by either (a) signed export demand from a non-Spanish customer, or (b) LATAM expansion phase.

**Consequences:**
- Positive: Each B phase ships ~10–15% faster on UI work. No translator workflow to staff. No build-time extraction step. Reduced PR review surface.
- Positive: Avoids premature abstraction — i18n keys often turn out wrong on first pass without real translation pressure.
- Negative: Retrofitting i18n later is expensive (every string must be extracted, every component touched). Estimated 2–3 weeks of dedicated work plus ongoing translation cost.
- Negative: Limits short-term TAM to Spanish-speaking markets (which is already the strategic focus, so impact is small).
- Neutral: Code stays readable for Spanish-speaking devs (no `t('employees.list.title')` indirection).

**Alternatives considered:**
- Full i18n via react-i18next + Django gettext from B.1: rejected because it imposes a 2-week tax on B.1 plus per-phase overhead with no current customer demand and no firm LATAM commitment.
- Hybrid (i18n keys in code, only es-PE locale shipped): rejected because the developer ergonomic cost is paid (indirection, key management) without delivering any user-facing benefit, and key naming converges poorly without a second language to validate against.

**Reference:** Maestro `docs/00_VYNTIA_MAESTRO.md` (positioning: Peru-first GovTech). Backlog item for "LATAM i18n" to be filed in BACKLOG.md if/when expansion is committed.



## ADR-B.2: Audit log scope

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** Both SERVIR (public sector) and large private clients increasingly require traceability — "who did what, when" — for HR mutations, especially around hiring, severance, salary changes, and disciplinary actions. A dedicated full audit log with immutable event store, queryable UI, retention policies, and signed records is scoped as a separate post-B sub-project (sub-proyecto X — full audit log). Without any audit infrastructure in B, several B phases that mutate critical state (B.13 desplazamiento, B.14 desvinculación, B.7 contract amendments) ship without trazabilidad and create both legal exposure and a hard-to-add-later debt: backfilling audit history is impossible.

The C.0 multi-tenant base model already standardizes `created_at`, `updated_at`, `created_by`, `updated_by` on tenant-scoped models. That gives us 80% of "who/when" for routine mutations cheaply, but does not capture before/after diffs or domain-significant events (e.g., "Empleado X cesado por causa Y on date Z").

**Decision:** Adopt minimal inline audit for sub-project B. Two layers:
1. **Audit fields** (already standard from C.0): every tenant-scoped business model carries `created_at`, `updated_at`, `created_by`, `updated_by`. Enforced via the C.0 base model. No change required.
2. **Domain audit events**: a small new app `apps/audit_lite/` introduced in B.1 exposes a single `AuditEvent` model (`tenant`, `actor_user`, `action`, `target_model`, `target_id`, `payload_json`, `created_at`) and a `record_event()` helper. Specific high-stakes flows (cese, desvinculación, suspensión empleado, contract amendments, position changes) call `record_event()` synchronously inside the same transaction as the mutation. No retention policy, no UI viewer in B; events are queryable via Django admin.

Sub-proyecto X later replaces `audit_lite` with a full event store (likely append-only, signed, with retention) and migrates these rows.

**Consequences:**
- Positive: Legal/compliance gap closed for the highest-risk flows without scope creep.
- Positive: `record_event()` call sites are easy to find and migrate when X arrives — they are explicit, not magic.
- Positive: AuditEvent table is small (only high-stakes events), so no immediate performance concern.
- Negative: Two audit mechanisms coexist (audit fields + AuditEvent). Some confusion possible until X consolidates.
- Negative: No tamper resistance in B (DBA could edit AuditEvent rows). Acceptable for B; X addresses.
- Negative: No UI viewer — admin-only access in B. RRHH users cannot self-serve audit queries.
- Neutral: Audit events are tenant-scoped (FK to Tenant), so they participate in the same isolation guarantees as business data.

**Alternatives considered:**
- Do nothing in B (rely solely on C.0 audit fields): rejected because audit fields don't capture domain events ("cese" is a state transition, not a row update) and don't capture before/after for amendments. Liability risk too high.
- Build a full audit log in B (event store, signing, UI, retention): rejected because that is the entire scope of sub-proyecto X and would block B.1 by 4–6 weeks.
- Use `django-simple-history` for automatic record-level history: rejected because it generates per-table shadow tables, doesn't capture domain events naturally (only row changes), and integrates poorly with planned event-sourcing in X.

**Reference:** Sub-proyecto X (Audit log) — to be planned post-B. C.0 base model in `apps/core/models.py`.



## ADR-B.3: Approval workflow strategy

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** Several B phases involve approvals: B.13 (desplazamiento — needs manager + RRHH sign-off), B.14 (desvinculación — needs RRHH + legal sign-off, sometimes director), and additional flows in scope (ascenso, aumento, suspensión). Each currently has no formal approval state machine. A general-purpose declarative workflow engine (sub-proyecto T — Workflow engine) is scoped as a separate post-B initiative; building it inside B would block multiple phases on a non-trivial framework design.

Without any approval mechanism, B.13 and B.14 cannot ship a credible workflow — desplazamiento approved via informal email is not a sellable feature for SERVIR clients.

**Decision:** Adopt minimal inline approvals per flow during sub-project B. Each phase that needs approvals implements its own simple state machine on the relevant model:
- States: `pendiente → aprobado | rechazado` (some flows may add `revisado` as an intermediate step).
- Fields on the model: `approval_status`, `approval_requested_by` (FK User), `approval_requested_at`, `approval_decided_by` (FK User), `approval_decided_at`, `approval_comment` (text).
- Approval actions log to `audit_lite.AuditEvent` (per ADR-B.2) so trazabilidad is captured.
- No multi-step approvers, no parallel approvals, no escalation rules in B. Single approver per flow; role-gated via existing RBAC (e.g., `@require_admin`, `@require_hr`).

Sub-proyecto T later refactors all of these per-flow state machines into a declarative engine (workflow definitions, parallel approvers, SLAs, escalation, etc.) and migrates existing data.

**Consequences:**
- Positive: B.13 and B.14 unblocked — each owns a small, testable state machine.
- Positive: Per-flow audit trail piggybacks on ADR-B.2 (`audit_lite`) for free.
- Positive: Simple to reason about for legal/compliance — no abstract workflow definitions to interpret.
- Negative: Code duplication across flows (3–5 nearly-identical state machines by end of B). Acceptable as transitional debt.
- Negative: No SLA tracking, no email reminders, no escalation in B. Approvers must self-serve via UI.
- Negative: Migration to T will require a data migration per flow when the engine arrives.
- Neutral: All inline approvals share a small mixin (`ApprovableMixin` in `apps/core/`) introduced in B.1 to keep field naming consistent.

**Alternatives considered:**
- Build a mini workflow framework in B.1 (lighter than T but generic): rejected because past experience says "small workflow engines" tend to grow into full ones — scope creep risk too high; T is already scoped to do this properly.
- Defer all approval-bearing flows to T (postpone B.13 and B.14): rejected because B.13 and B.14 are core HR and a Vyntia Core demo without desvinculación is not sellable.
- Use third-party libs like `django-fsm` or `viewflow`: rejected because both add framework lock-in and `django-fsm` is unmaintained; the inline state machine is ~30 lines per flow.

**Reference:** Sub-proyecto T (Workflow engine) — to be planned post-B. ADR-B.2 (`audit_lite`) for audit integration.



## ADR-B.4: Document storage backend

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** VYNTIA generates and stores significant document volume: PDF certificates (laboral, vacaciones), Word/PDF contracts and amendments, and the legajo digital (employee personnel file: identity docs, academic certificates, contract scans). Today, documents land on the local filesystem under `MEDIA_ROOT` (`apps/api/media/`). The Module 06 audit (Task 6) flagged that without tenant segregation in the filesystem path, a path-traversal bug or misconfigured permission check could leak documents across tenants — a hard-fail for a multi-tenant SaaS.

Production multi-tenant SaaS typically uses S3 or Azure Blob with per-tenant prefixes and pre-signed URLs for download. That architecture is correct long-term but requires (a) provisioning a bucket/account and IAM, (b) replacing direct filesystem reads in PDF generation pipeline, (c) signed URL generation in download views, (d) ops monitoring. None of this is on B's critical path; deployment hardening is post-B.

**Decision:** Stay on filesystem storage for the duration of sub-project B. Two protective measures:
1. **Storage abstraction layer**: introduce `apps/core/storage.py` exposing a `TenantStorage` class that wraps Django's `default_storage` and prefixes all paths with `<tenant_id>/`. All document-writing code (PDF generator, contract upload, legajo upload) uses `TenantStorage` instead of touching paths directly. Switching to S3/Azure later becomes a settings change (`DEFAULT_FILE_STORAGE = ...`) plus a one-time data migration, not a code rewrite.
2. **Tenant-segregated MEDIA_ROOT layout**: documents land under `MEDIA_ROOT/<tenant_id>/<category>/<filename>` (e.g., `media/42/documentos_empleados/legajo-EMP-1234.pdf`). Per-tenant directories make filesystem-traversal-style cross-tenant leaks structurally harder; the application also enforces tenant scoping on read.

This is the **critical mitigation noted in B.5b** (the post-C.0 work splitting tenant E2E from the rest). Signed URLs and S3-style access control come from the post-B deployment hardening sub-project.

**Consequences:**
- Positive: Cross-tenant document leak risk reduced — both code path (TenantStorage enforces prefix) and filesystem layout (per-tenant directories) are tenant-aware.
- Positive: Migration to S3/Azure later is a config switch + one-time data move, not a refactor across N call sites.
- Positive: No new external service dependency in B (no S3 credentials, no IAM, no ops cost).
- Negative: Filesystem doesn't scale horizontally — single-server deployment is implied throughout B. Acceptable; B is for first sellable product, not multi-region.
- Negative: No signed URLs in B, so download views must check tenant + permission server-side before streaming. Bug in that check = leak. Mitigation: dedicated test coverage on the download endpoints in B.5b/B.16.
- Negative: Backups must include `MEDIA_ROOT`. Operations runbook to be added in deployment sub-project.
- Neutral: Local dev still trivial (filesystem); test fixtures can use `tmp_path`.

**Alternatives considered:**
- S3 from B.1: rejected because of provisioning + ops cost (IAM, billing, monitoring), and signed URL implementation work that doesn't compound with any other B deliverable.
- Azure Blob from B.1: rejected for the same reasons; no preference between S3 and Azure forced today, decision deferred to deployment sub-project.
- Continue without storage abstraction: rejected because every document write site would need rewriting when migration eventually happens — debt grows linearly with B's scope.

**Reference:** Module 06 audit (Task 6) leak risk; B.5b plan (post-C.0 tenant isolation work). `apps/core/storage.py` to be added in B.1.



## ADR-B.5: Testing strategy for employment lifecycle

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** Module 03 in the Maestro decomposes employment into 7 sub-procesos that compose into a single lifecycle: selección → contratación → onboarding → vida laboral (asistencia, ausencias, vacaciones, desplazamiento, ascensos) → desvinculación → cese → post-cese. Each B phase implements one or two slices of that pipeline. Testing each slice in isolation is necessary but not sufficient: the sellable claim is "VYNTIA manages the full employment lifecycle," which is only true if the integration works end-to-end. Costly Playwright e2e on every phase would slow B significantly; no e2e at all would let composition bugs ship.

The C.0 work already added an opt-in tenant isolation Playwright suite (`tests/e2e/tenant-isolation.test.js`, gated by `RUN_TENANT_E2E=1`). The pattern of opt-in heavy e2e plus default-on pytest is established and works.

**Decision:** Three-tier strategy:
1. **Per-phase pytest unit tests**: every B phase ships unit tests for new models, services, validators, and serializers. Default-on, run on every CI invocation. Existing baseline (161 passing) must not regress.
2. **Per-phase pytest integration tests**: every B phase that touches multiple bounded contexts (e.g., contracts → employees → audit_lite) ships integration tests using Django test client + DRF APIClient. Default-on.
3. **B.16 close-out Playwright e2e for full lifecycle**: a new `tests/e2e/employment-lifecycle.test.js` is added in the final B phase (B.16), exercising the full happy path: provision tenant → seed admin → create empleado → assign position → issue contract → run onboarding step → record asistencia → request vacaciones → process desplazamiento → run desvinculación → confirm cese settlement. Opt-in, gated by `RUN_LIFECYCLE_E2E=1`, documented as a release-gate test.

The two e2e suites (tenant isolation + lifecycle) are both opt-in but become required for any release branch promotion.

**Consequences:**
- Positive: Each phase's CI runs fast (no Playwright per phase). Baseline preserved.
- Positive: Integration bugs caught at B.16 instead of post-launch — single dedicated phase to fix lifecycle composition issues.
- Positive: Lifecycle e2e doubles as live demo script (the test reads as a sales-friendly walkthrough).
- Negative: B.16 is a heavy phase (e2e write + bug fixing the issues it surfaces). Risk of underestimation — flagged for spec discussion when B.16 is planned.
- Negative: Bugs that span phases may sit undetected until B.16. Mitigation: integration tests at each phase boundary catch most cases.
- Negative: Two opt-in e2e suites mean two CI configurations to maintain; if devs forget to run them, regression slips.
- Neutral: Vitest frontend unit tests continue per-component; no change.

**Alternatives considered:**
- Playwright e2e per phase: rejected because each phase would carry 30–60 minutes of e2e dev work plus brittle test maintenance, with most coverage redundant to the lifecycle test.
- pytest only (no e2e in B): rejected because UI regressions in critical flows (contract issue, desvinculación) would only surface in production; lifecycle e2e is a release blocker.
- One giant e2e suite that runs on every push: rejected because suite runtime would exceed 15–20 minutes and slow down per-phase iteration.
- Keep tenant isolation e2e gated but make lifecycle e2e default-on: rejected because lifecycle e2e provisions tenants and seeds extensive data — dev environments may not be ready.

**Reference:** `tests/e2e/tenant-isolation.test.js` (C.0 pattern). B.16 plan to define lifecycle e2e in detail. ROADMAP-B.md test baselines.



## ADR-B.6: SERVIR vs LCT in UI

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** VYNTIA is positioned for both private sector clients (regulated by LCT — Ley General del Trabajo and Ley 30709 on equal-pay/CCF) and public sector clients (regulated by SERVIR via D.Leg. 1057/CAS, D.Leg. 728, D.Leg. 276, plus MPP — Manual de Perfiles de Puestos and CPE — Cuadro de Puestos de la Entidad). The two regimes overlap on ~80% of HR concepts (employee, contract, vacaciones, asistencia) but diverge on:
- Position management: private uses CCF; public uses MPP/CPE with formal Designación and Encargatura concepts.
- Disciplinary process: public has a regulated PAD (Procedimiento Administrativo Disciplinario); private follows internal RIT.
- Movement: public has Desplazamiento with 6 sub-types (designación, rotación, encargatura, comisión, destaque, transferencia); private uses simpler reassignment.
- Severance: public has formal cese causes; private has LCT-defined causes plus indemnización por despido arbitrario.
- Retributions: public has fixed scales; private uses CCF bands per Ley 30709.

Treating these as separate products would double infrastructure cost and fork the codebase. Treating them identically would force one regime's UI on the other, breaking domain fit.

**Decision:** Single codebase with a per-tenant `sector` discriminator.
- Add `Tenant.sector` field (`'private' | 'public'`) seeded at provisioning.
- Frontend exposes a `useTenant()` hook returning `{ sector, ... }`. Sector-specific UI branches use this hook; default route guards prevent showing public-only screens to private tenants and vice versa.
- Backend models share a common base (Employee, Contract, Position) plus sector-specific subclasses or sector-conditional fields where schemas diverge significantly. Examples: `Position` keeps a base table plus `private_attrs` / `public_attrs` JSON or sector-specific child tables; movement records have a `kind` enum that admits both `reassignment` (private) and the 6 desplazamiento types (public).
- Sector-conditional validation lives in services (`apps/<context>/services/`), not in serializers, so the same DRF endpoint can serve both sectors.
- Only ~20% of Core diverges; the bulk of UI and models is shared.

**Consequences:**
- Positive: Single codebase, single CI pipeline, single deployment. Lowest TCO.
- Positive: Common code (employees, vacaciones, asistencia, identity) gets twice the testing/usage.
- Positive: A tenant that switches sector classification (rare but real, e.g., a state-owned enterprise spin-off) doesn't require migration to a different product.
- Negative: Some screens become busier with conditional branches (`if sector === 'public' ...`). Mitigation: factor into separate sector-aware components when branches exceed ~3 cases.
- Negative: Reviewers must remember sector when validating PRs — easy to forget the other sector path. Mitigation: PR template question "tested both sectors?" plus CI coverage on both paths.
- Negative: A regression in sector logic potentially affects all tenants of that sector simultaneously.
- Neutral: Demos and sales materials need two flavors; that work would exist regardless of architecture.

**Alternatives considered:**
- Separate tenants per sector with separate apps deployed: rejected because it doubles infra cost (DBs, deploys, monitoring), splits engineering attention, and forces customers in mixed contexts (e.g., consulting firms with public + private clients) to maintain two accounts.
- Separate apps (vyntia-private, vyntia-public) sharing a library: rejected because divergence is small and library coordination overhead is high. Forks tend to drift.
- Plugin architecture (sector pluggable at runtime per workspace): rejected as overengineering — only two plugins ever, and they touch the same domain entities.
- Tag features in code with feature flags rather than per-tenant sector: rejected because sector is identity, not a flag — a tenant doesn't toggle between private and public week to week.

**Reference:** Maestro Module 02 (organization, position) and Module 03 (lifecycle) for sector divergences. Phase B.6 (Position) and B.13 (Desplazamiento) plans must explicitly call out sector branches.



## ADR-B.7: Versioning of critical models (Position, Contract)

(Filled by Task 14.)

## ADR-B.8: Org chart frontend library

(Filled by Task 14.)

## ADR-B.9: Severance calculation scope (B vs D)

(Filled by Task 14.)
