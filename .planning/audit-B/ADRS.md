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

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** Several VYNTIA models carry historical legal weight: changing them in place destroys context that auditors, employees, and courts may need years later. The two clearest cases:
- **Position** (B.6): a position carries salary band, role definition, requirements, and reporting line. Changing the salary band of "Analyst II" in 2027 must not retroactively rewrite what people occupying that position earned in 2026 — the contract referenced the 2026 definition.
- **Contract**: an existing contract may be amended (sueldo update, plazo extension, addendum). Today this is implemented in `apps/contracts/` via Contract + ContractAmendment (introduced L3.10.3) — the contract is immutable once issued; changes are amendments referencing the original.

A general approach (e.g., `django-simple-history` recording every row change automatically) is tempting but mismatches the legal model: not every column change is a legally significant amendment. Some are corrections (typo fix); some are amendments (sueldo change). The model needs to encode that distinction explicitly.

**Decision:** Per-model versioning strategy, not a global library.
- **Position**: inline versioning on the Position model itself. Fields: `version: int` (starts at 1), `parent: ForeignKey('self', null=True, related_name='successors')` pointing to the previous version. A change to a "versioned" field (salary band, role definition) creates a new Position row with `version = parent.version + 1` and links back. Non-versioned fields (typo in description, internal notes) update in place. Active assignments reference the specific Position version they were issued against.
- **Contract**: continue with the existing explicit Contract + ContractAmendment split (already implemented in L3.10.3). The Contract row is immutable post-issuance; amendments are separate records linked via FK. No `django-simple-history`.
- **Other models** (Employee, Department, etc.): no versioning. Audit fields (ADR-B.2) plus AuditEvent for high-stakes mutations are sufficient.

Rationale: explicit, model-specific versioning is auditable in plain SQL — a lawyer's tech advisor can read the schema and understand the history model. Library-driven shadow tables are opaque.

**Consequences:**
- Positive: Legal review can read history straight from the schema. No need to query a hidden `pgh_history` table.
- Positive: Distinction between "amendment" and "correction" is encoded — you cannot accidentally rewrite history with a typo fix.
- Positive: References from other models (assignments → Position version, payroll → Contract version) are explicit and queryable.
- Negative: Each versioned model carries its own boilerplate (parent FK, version column, duplication-on-change service). Mitigation: extract `VersionedModelMixin` in `apps/core/` once both Position and Contract patterns settle.
- Negative: Querying "current" rows requires `WHERE successor_id IS NULL` (or a `current_version` flag). Performance acceptable with index on `parent_id`.
- Negative: Some historical queries (e.g., "show me all Positions with salary > X at any point in time") become more complex — must traverse versions.
- Neutral: Migration cost low because Contract already follows the pattern; only Position is new.

**Alternatives considered:**
- `django-simple-history` for automatic record-level history: rejected because it's opaque (auto-generated shadow tables), it can't distinguish amendments from corrections, and it doesn't model the explicit "this assignment references THIS version of the position" relationship cleanly.
- Event sourcing on these models: rejected as overkill — the volume of changes is low (positions rarely change, contracts amended occasionally) and event sourcing complicates simple reads massively.
- Snapshot-on-payroll (only the moments payroll runs are versioned): rejected because non-payroll consumers (legal, HR reports, court requests) need full history.
- Full audit log (ADR-B.2) instead of versioning: rejected because audit log records changes but doesn't make versioned references queryable — "what was this Position's salary band when this contract was signed?" is awkward without versioned rows.

**Reference:** L3.10.3 contract amendment pattern in `apps/contracts/models/contract_amendment.py`. B.6 plan (Position) to apply same pattern. Maestro Module 02 (Position).



## ADR-B.8: Org chart frontend library

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** B.6 (organization extended) requires an interactive org chart: navigable, drill-down, drag-drop reordering of reporting relationships, and visual presentation of departments + positions + occupants. Several JavaScript libraries are candidates:
- `react-d3-tree`: thin React wrapper around D3 hierarchical tree; declarative; read-only by default.
- `dagre-d3`: graph layout library on D3; generic but imperative.
- `@xyflow/react` (formerly React Flow): node-based editor framework with drag-drop, custom nodes, panning, zooming, minimap; mature, ~150 KB gzipped, MIT licensed; v11+ has stable TypeScript types and active maintenance.
- Custom CSS grid + handwritten layout: full control but reimplements panning, zooming, edge routing.

The org chart in VYNTIA needs to be both viewable (employee facing — "who reports to whom") and editable (RRHH facing — drag-drop to reassign). Read-only solutions don't cover the editing UX.

**Decision:** Adopt `@xyflow/react` for the org chart in B.6 and any future graph-shaped UIs (workflow visualizer, process diagrams). Lazy-load it on the org-chart route so users not on that page don't pay the ~150 KB cost. Define custom node components for Department, Position, and Employee node types.

**Consequences:**
- Positive: Drag-drop reordering, panning, zooming, minimap come for free — no UX framework to build.
- Positive: TypeScript-first, good docs, active community (sustained releases through 2025–26).
- Positive: Reusable for future phases (workflow visualizer, ascenso tree, organization migration tool).
- Positive: Lazy-loading mitigates bundle impact for users not on the org chart screen.
- Negative: ~150 KB gzipped is a sizable dependency; users who do hit the page see slower first paint compared to a hand-rolled solution. Mitigation: lazy-loaded chunk + skeleton loader.
- Negative: Library version churn (v11→v12 happened recently with rename). Need to pin and review on update.
- Negative: Custom layout for hierarchical org chart still requires writing a layout algorithm or wrapping `dagre` — `@xyflow/react` doesn't auto-layout trees out of the box. Acceptable; layout is a one-time integration cost.
- Neutral: License (MIT) is compatible.

**Alternatives considered:**
- `react-d3-tree`: rejected because read-only by default, no native drag-drop, and adapting it to editing needs as much work as switching libraries.
- `dagre-d3`: rejected because D3's imperative model is awkward to maintain in a React codebase — every node update requires manual DOM management.
- Custom CSS grid: rejected because reinventing panning/zooming/minimap/drag-drop is a multi-week project.
- `react-flow` v10 (older API): rejected because superseded by `@xyflow/react`.
- `vis.js`/`cytoscape.js`: rejected because graph-database-style libraries; their visual idiom doesn't fit hierarchical org charts as cleanly.

**Reference:** `@xyflow/react` docs at https://reactflow.dev. B.6 plan to detail node component design. Bundle audit to be added as part of B.6 verification.



## ADR-B.9: Severance calculation scope (B vs D)

**Status:** Proposed (becomes Accepted on B.0 merge)

**Context:** B.14 (desvinculación) needs to compute and present a liquidación (severance settlement) when an employee is terminated. Sub-proyecto D (Vyntia Pay) is the full payroll engine, and severance is a payroll-adjacent calculation. Without an explicit boundary, two failure modes are likely:
- B.14 ships a barebones placeholder calculation that customers can't trust → desvinculación is unsellable.
- B.14 implements the full payroll-grade severance with all régimen variants, AFP/ONP detraction, Renta 5ta, etc. → blurs the B/D boundary, duplicates work D will redo, and inflates B.14's scope.

The legal minimum that any LCT termination requires:
- CTS proporcional (1 sueldo per year worked, prorated for the partial period since last semestre deposit).
- Vacaciones truncas (días no gozados × jornal).
- Gratificación trunca (proportional to current semester at termination date).
- Indemnización por despido arbitrario (1.5 sueldos per year, capped at 12 sueldos), where applicable.

These four components are stable in law (D.S. 003-97-TR, D.S. 001-97-TR, Ley 27735) and can be computed without a full payroll engine — they only need contract data, vacation balance, and current sueldo.

**Decision:** B.14 implements the **minimum legal severance calculation only**:
- CTS proporcional (last semester only; depósito CTS history not required for B.14 — that lives in D).
- Vacaciones truncas based on accumulated balance from B's vacation system.
- Gratificación trunca for the current semester (Julio or Diciembre).
- Indemnización por despido arbitrario where the cese cause is "despido arbitrario."

The output is persisted as a `SeveranceSettlement` record in B.14, with line items, totals, and a generated PDF settlement letter.

**Sub-proyecto D extends `SeveranceSettlement` later with**:
- AFP/ONP detraction (requires the AFP/ONP régimen tables and current employee's afiliación).
- Retención de quinta categoría (Renta 5ta) calculation.
- Multi-régimen variants: RLE, MYPE, agraria, construcción civil, etc.
- CTS depósito semestral handling (full history, not just proporcional last semester).
- Gratificaciones programadas and bonificación extraordinaria 9%.
- Retroactivos and reintegros if any payroll periods were unpaid at termination.
- Integration with ONP/AFP T-Registro for cessation notifications.

When D arrives, the existing `SeveranceSettlement` records remain valid; D enhances new settlements with the additional components and may offer a "recompute under D engine" action for already-issued settlements (out of scope for B).

**Consequences:**
- Positive: B.14 ships a credible, legally-grounded severance flow without waiting for D.
- Positive: B/D boundary is explicit and enforceable in code review — anyone trying to add AFP/ONP logic to B.14 gets pushback citing this ADR.
- Positive: `SeveranceSettlement` table is stable across the B → D transition (D extends, doesn't replace).
- Positive: Test coverage scope for B.14 stays bounded — only 4 calculation rules.
- Negative: A B-only customer running a complex régimen (e.g., agraria) gets an incomplete severance number and must manually adjust. Documented limitation in B.14.
- Negative: Customers in régimen MYPE may feel the indemnización cap (since their cap is different); B.14 only covers default LCT cap.
- Negative: B.14's calculation may be subtly wrong if D's eventual implementation reveals edge cases (e.g., last partial month with overtime). Mitigation: B.14 includes manual override fields on `SeveranceSettlement` lines.
- Neutral: SERVIR severance differs (different cause framework). B.14 covers SERVIR's analogous minimums per ADR-B.6 sector branching.

**Alternatives considered:**
- Full liquidación in B.14 (all regímenes, all detractions): rejected because that is sub-proyecto D's whole point. Replicating D inside B blurs the architecture and likely costs 4–6 weeks B.14 could not absorb.
- Defer all severance to D (B.14 ships without calculation): rejected because B.14 is core HR — a desvinculación module that can't tell you what to pay is not sellable to RRHH directors.
- Hybrid: B.14 computes nothing but exposes a hook so D plugs in later: rejected because the hook would be empty in B and the demoable feature would be missing.

**Reference:** D.S. 003-97-TR (LCT consolidated); D.S. 001-97-TR (CTS); Ley 27735 (Gratificaciones); Ley 28051 (PLAME). Sub-proyecto D scope in `docs/ROADMAP_SUBPROJECTS.md`. Maestro Module 03.6 (desvinculación).

