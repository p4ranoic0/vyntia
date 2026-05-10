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

(Filled by Task 14.)

## ADR-B.5: Testing strategy for employment lifecycle

(Filled by Task 14.)

## ADR-B.6: SERVIR vs LCT in UI

(Filled by Task 14.)

## ADR-B.7: Versioning of critical models (Position, Contract)

(Filled by Task 14.)

## ADR-B.8: Org chart frontend library

(Filled by Task 14.)

## ADR-B.9: Severance calculation scope (B vs D)

(Filled by Task 14.)
