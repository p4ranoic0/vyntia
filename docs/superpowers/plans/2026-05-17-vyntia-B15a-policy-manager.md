# Phase B.15a — Policy Manager (Module 01)

**Branch:** `vyntia/B15a-policy-manager`
**Spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md` (Módulo 01 — Políticas)
**Master roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`
**Backlog items:** #128 (Policy + PolicyVersion + PolicyApprovalFlow + PolicyPublication + PolicyAcknowledgment)
**ADR baseline:** ADR-B.4 (filesystem storage via `apps.core.storage.TenantStorage`) — followed strictly.

## Goal

Ship a complete versioned policy manager: Policy (header), PolicyVersion (immutable versioned content with PDF attachment), PolicyApprovalFlow (multi-step approval), PolicyPublication (org-wide release), PolicyAcknowledgment (per-employee acuse de recibido with audit trail).

Module 01 policies cover *RIT, Código de Ética, Reglamento SST, políticas de datos personales, manual de funciones, procedimientos*. The manager has to enforce: only approved versions can be published, only published versions can be acknowledged, and each employee acknowledgment captures a full audit trail (timestamp, IP, UA, signature kind) per Ley 29733 + Art. 27 LPCL.

Out-of-scope (deferred to B.15b or later):
- HRStrategicPlan + StrategicObjective + KPI (B.15b)
- WorkforcePlan + HeadcountProjection + SuccessionPlan + KeyPosition + SuccessorCandidate (B.15b)
- ComplianceMatrix + ComplianceObligation + Evidence with vencimiento alerts (B.15b)
- E-signature integration with B.10 DocumentSignature (caller-integrates; not blocking)
- Cron real para alertas de acknowledgments pendientes → post-B (mismo lugar que probation alertas)

## Tasks

### Task 1 — Plan + branch (DONE)

### Task 2 — New app `apps/policies/`

Files to create:
- `apps/api/apps/policies/__init__.py`
- `apps/api/apps/policies/apps.py` — `PoliciesConfig(name='apps.policies', label='policies', verbose_name='VYNTIA Policies')`.
- `apps/api/apps/policies/models/__init__.py` — re-exports.
- `apps/api/apps/policies/models/policy.py` — `Policy` (header).
  - Fields: id UUID, tenant FK, kind (rit/codigo_etica/reglamento_sst/politica_datos/manual_funciones/procedimiento/otro), title, description, owner_user FK identity.User, owner_area FK organization.Department, status (draft/in_review/approved/published/retired), current_version FK PolicyVersion (nullable, set after publish), created_at, updated_at, created_by, updated_by.
  - Unique constraint per (tenant, kind, title).
  - Helpers: `latest_version()`, `is_published`, `is_active`.
- `apps/api/apps/policies/models/policy_version.py` — `PolicyVersion` (immutable content).
  - Fields: id UUID, tenant FK, policy FK, version_number int, content_html TextField, pdf_file FileField (TenantStorage upload_to='politicas/'), change_summary, effective_date, status (draft/under_review/approved/published/retired), submitted_at, submitted_by, approved_at, published_at, retired_at, created_at, updated_at.
  - Unique constraint per (policy, version_number).
  - Helpers: `mark_under_review()`, `mark_approved()`, `mark_published()`, `mark_retired()`.
- `apps/api/apps/policies/models/policy_approval_flow.py` — `PolicyApprovalFlow` + `PolicyApprovalStep`.
  - `PolicyApprovalFlow`: id UUID, tenant FK, policy_version OneToOne, status (pending/approved/rejected), created_at, completed_at.
  - `PolicyApprovalStep`: id UUID, flow FK, order int, approver_user FK identity.User, role_hint (optional), decision (pending/approved/rejected), decided_at, decided_by, comment, created_at.
  - Unique constraint per (flow, order). Helper: `next_pending_step()`.
- `apps/api/apps/policies/models/policy_publication.py` — `PolicyPublication`.
  - Fields: id UUID, tenant FK, policy_version OneToOne, published_at, published_by, target_audience (all/role/area/employee), target_role FK identity.Role nullable, target_area FK organization.Department nullable, target_employees M2M employees.Employee blank, requires_acknowledgment bool default True, acknowledgment_deadline date nullable, notification_sent bool default False.
  - Helper: `expand_target_employees()` → returns full set of employees affected.
- `apps/api/apps/policies/models/policy_acknowledgment.py` — `PolicyAcknowledgment`.
  - Fields: id UUID, tenant FK, publication FK, employee FK employees.Employee, status (pending/acknowledged/expired/declined), acknowledged_at, signature_kind (canvas/typed/checkbox/none), signature_payload TextField (base64 or text), ip GenericIPAddressField, user_agent, declined_reason, created_at, updated_at.
  - Unique constraint per (publication, employee).
  - Helper: `is_overdue()`.

Migrations:
- `policies/migrations/0001_b15a_policy_models.py`

Register app: append `"apps.policies.apps.PoliciesConfig"` to `LOCAL_APPS` in `vyntia/settings/base.py`.

### Task 3 — Services

- `apps/api/apps/policies/services/policy_service.py`
  - `create_policy(*, tenant, kind, title, description, owner_user, owner_area=None, user=None) -> Policy`
  - `create_version(*, policy, content_html, pdf_file=None, change_summary='', effective_date=None, user) -> PolicyVersion` — derives next version_number; status='draft'.
  - `submit_for_review(version, user) -> PolicyApprovalFlow` — transitions version to 'under_review' + creates flow with required approval steps (caller passes list of approver_users). Idempotent at the boundary: re-submit replaces previous flow if any.
  - `register_approval_decision(*, flow, step_order, approver, decision, comment='') -> PolicyApprovalStep` — validates approver matches step's approver_user; records decision; auto-completes flow if all steps approved → marks version 'approved'; if any rejected → flow rejected + version reverts to 'draft'.
  - `publish(*, version, target_audience, target_role=None, target_area=None, target_employees=None, requires_acknowledgment=True, deadline=None, user) -> PolicyPublication` — requires version.status='approved'; creates PolicyPublication; transitions version → 'published'; sets policy.current_version + policy.status='published'.
  - `retire(policy, user)` — transitions policy and current_version to 'retired'.
  - `list_pending_approvals_for_user(user)` — returns PolicyApprovalStep rows where approver_user=user and decision='pending'.
- `apps/api/apps/policies/services/policy_acknowledgment_service.py`
  - `seed_acknowledgments_for_publication(publication) -> int` — idempotent; expands `publication.expand_target_employees()` and creates PolicyAcknowledgment rows with status='pending' (skips duplicates).
  - `capture(*, acknowledgment, signature_kind, signature_payload, ip, user_agent) -> PolicyAcknowledgment` — validates signature_kind + payload combo; transitions to 'acknowledged'.
  - `decline(*, acknowledgment, reason, ip, user_agent) -> PolicyAcknowledgment` — transitions to 'declined'.
  - `expire_overdue(tenant=None) -> int` — flips pending rows past deadline to 'expired'.
  - `list_pending_for_employee(employee) -> QuerySet[PolicyAcknowledgment]`.

### Task 4 — API surface + smoke tests

Routes under `/api/v1/policies/`:
- `policies/` — CRUD + actions: `submit-for-review` (POST detail; requires latest draft version), `retire` (POST detail).
- `policy-versions/` — CRUD + actions: `submit-for-review` (POST detail; requires draft status; payload `approvers` list of user_ids), `publish` (POST detail; requires approved + target audience payload).
- `policy-approval-flows/` — CRUD read-only + nested `decide` (POST detail step_order + decision + comment).
- `policy-publications/` — CRUD + read.
- `policy-acknowledgments/` — list + retrieve + actions: `acknowledge` (POST detail), `decline` (POST detail), `expire-overdue` (collection POST).

URLs file: `apps/api/api/v1/policies/urls.py` + `views.py`. Wire `path('policies/', include('api.v1.policies.urls'))` into `api/v1/urls.py`.

All ViewSets: `TenantAwareViewSetMixin` + `RRHHPermission` (existing in `api/v1/rrhh/permissions.py`).

Smoke tests (≥ 6 per file, total ≥ 18):
- `apps/api/apps/policies/tests/test_b15a_policy_models.py` — model rules + uniques + lifecycle helpers.
- `apps/api/apps/policies/tests/test_b15a_policy_service.py` — service flows (create_policy → version → submit → approve → publish).
- `apps/api/apps/policies/tests/test_b15a_acknowledgment_service.py` — seed + capture + decline + expire.
- `apps/api/apps/policies/tests/test_b15a_api_smoke.py` — 5 ViewSets routing + auth gating.

### Task 5 — Frontend services + admin pages + acuse page

Services (under `apps/web/src/features/policies/`):
- `services/policiesService.ts` — list/get/create policies; nested versions: createVersion/submitForReview/publish/retire.
- `services/policyApprovalsService.ts` — listPending; decide.
- `services/policyAcknowledgmentsService.ts` — listForMe; acknowledge; decline; admin: listForPublication; expireOverdue.

Pages (lazy under `/politicas/...` + AdminRoute where applicable):
- `pages/PoliciesListPage.tsx` — admin grid of Policies; create + open detail.
- `pages/PolicyDetailPage.tsx` — versions list + submit/publish actions + approvals tab + acknowledgments tab.
- `pages/PolicyAcknowledgmentInboxPage.tsx` — employee-facing page listing their pending acuses; canvas-based or checkbox signature; opens version PDF before acknowledging.
- `pages/PolicyApprovalsInboxPage.tsx` — for approvers (managers/RRHH): list pending steps; approve/reject inline.

Routes: `/politicas/admin`, `/politicas/admin/:id`, `/politicas/mis-acuses`, `/politicas/aprobaciones`.

Tests (vitest):
- `apps/web/src/features/policies/services/__tests__/policiesService.test.ts`
- `apps/web/src/features/policies/services/__tests__/policyAcknowledgmentsService.test.ts`

### Task 6 — Close-out + merge to master

- Baselines compared against B.14 SHA `f16f05f1`:
  - pytest must not drop from 856/1/17 baseline; should ADD net positive tests.
  - vitest must not drop from 24 files / 150 tests baseline.
  - ESLint preserved at 278.
  - Build clean.
  - `manage.py check`: 0 silenced.
- Final commit on branch then merge `--no-ff` to master.
- Update memory: `subproject_b_progress.md` with B.15a close-out + remaining B.15b scope.

## Lessons to apply from B.14

- Always use `select_related('termination', 'completed_by')` in queryset to avoid N+1 (B.14 carry-over).
- Action input serializers must be top-level classes in views.py, not inline (B.14 pattern).
- `TenantAwareViewSetMixin` already handles `perform_create`/`get_queryset` — don't reimplement.
- File field upload_to should be category-prefixed (`politicas/` not bare).
- Each test_*_api_smoke.py must include auth gating tests (unauthenticated → 401 or 403).
- Frontend lazy pages: register routes via existing `LazyAdminRoutes` style in App.tsx.

## Risk register

- New app registration mid-suite: a missing `LOCAL_APPS` entry breaks pytest immediately — verify with `manage.py check` after each commit.
- `OneToOne` from PolicyApprovalFlow ↔ PolicyVersion is the strongest invariant; tests must cover re-submit overwrite path.
- PolicyAcknowledgment IP/UA capture must use `request.META.get('REMOTE_ADDR')` + `HTTP_USER_AGENT` (be permissive with empty values).
- Signature_payload may be large (canvas base64); use TextField, not CharField; document size cap to 200 KB in docstring (no DB-level limit for now).
