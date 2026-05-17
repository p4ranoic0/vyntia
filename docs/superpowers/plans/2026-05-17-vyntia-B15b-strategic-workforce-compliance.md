# Phase B.15b — Strategic + Workforce + Compliance (Module 01)

**Branch:** `vyntia/B15b-strategic-workforce-compliance`
**Spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md` (Módulo 01 — Planificación + Cumplimiento)
**Master roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`
**Backlog items:** #129 (HRStrategicPlan), #130 (WorkforcePlan + Succession), #131 (ComplianceMatrix)
**Predecessor:** B.15a (Policy Manager) merged `98f1bbf5` 2026-05-17.

## Goal

Cerrar Module 01 con las 3 entidades de planificación / cumplimiento que faltan:
- **#129 — Plan estratégico de RRHH**: HRStrategicPlan (período anual/multianual) → StrategicObjective (objetivos con peso) → KPI (métricas con `target` + `actual` y cálculo de progreso).
- **#130 — Plan de dotación + sucesión**: WorkforcePlan → HeadcountProjection (proyección por área/cargo) + SuccessionPlan → KeyPosition (cargos clave) → SuccessorCandidate (candidatos rankeados readiness 1-4).
- **#131 — Matriz de cumplimiento**: ComplianceMatrix → ComplianceObligation (obligaciones legales/normativas con vencimiento) → Evidence (archivos/links que demuestran cumplimiento) + service de alertas (próximos a vencer + vencidos).

Todo va al app existente `apps/policies/` (creado en B.15a) — Module 01 = un app.

Out-of-scope (post-B):
- Approval workflow para Strategic / Workforce plans (se gestionan con published_by/approved_by simple, sin flujo multi-step). Si se necesita, reusar PolicyApprovalFlow de B.15a.
- Real cron para alertas de vencimiento — endpoint manual + collection action `alertas-vencimiento`. Cron real va al `cron_celery` post-B.
- Integración con Payroll para HeadcountProjection cost estimates → D.
- Versionado de StrategicPlan al estilo PolicyVersion — single-row + edit hasta MVP.

## Tasks

### Task 1 — Plan + branch (DONE)

### Task 2 — #129 HRStrategicPlan + StrategicObjective + KPI

Files to create:
- `apps/api/apps/policies/models/strategic_plan.py`
  - `HRStrategicPlan` — tenant, name, fiscal_year (int), period_start, period_end, status (draft/active/completed/archived), description, owner_user, approved_by, approved_at.
  - `StrategicObjective` — FK HRStrategicPlan, code (PE-01 etc), title, description, weight (Decimal 0..100), order, owner_user.
  - `KPI` — FK StrategicObjective, name, formula_note, unit (% / N / S/.), target Decimal, actual Decimal default 0, target_date, status (on_track/at_risk/off_track/done). Helper `progress_pct()`.
- Re-export desde `apps/api/apps/policies/models/__init__.py`.

Migration: `0002_b15b_strategic_plan.py`.

### Task 3 — #130 WorkforcePlan + HeadcountProjection + SuccessionPlan + KeyPosition + SuccessorCandidate

Files to create:
- `apps/api/apps/policies/models/workforce_plan.py`
  - `WorkforcePlan` — tenant, name, fiscal_year, period_start, period_end, status (draft/active/completed/archived), description, owner_user.
  - `HeadcountProjection` — FK WorkforcePlan, area FK Department (optional, null=true para totales globales), position FK organization.Position (optional), current_headcount int, projected_headcount int, delta_required int (computed), justification text, target_quarter (Q1..Q4 enum).
- `apps/api/apps/policies/models/succession_plan.py`
  - `SuccessionPlan` — tenant, name, fiscal_year, owner_user, status (draft/active/archived), notes.
  - `KeyPosition` — FK SuccessionPlan, position FK organization.Position, criticality (alta/media/baja), risk_notes, current_holder FK employees.Employee (optional).
  - `SuccessorCandidate` — FK KeyPosition, employee FK employees.Employee, readiness_level (1=ready_now / 2=ready_1y / 3=ready_2y / 4=development_needed), order (int para ranking), notes. Unique (key_position, employee).

Migration: `0003_b15b_workforce_succession.py`.

### Task 4 — #131 ComplianceMatrix + ComplianceObligation + Evidence

Files to create:
- `apps/api/apps/policies/models/compliance.py`
  - `ComplianceMatrix` — tenant, name, fiscal_year, owner_user, status (active/archived), description.
  - `ComplianceObligation` — FK ComplianceMatrix, code (e.g., "SUNAT-PVS-AAA"), title, description, source (sunat/sunafil/mintra/mtpe/servir/essalud/onp/afp/interno/otro), frequency (mensual/trimestral/semestral/anual/unica/ad_hoc), next_due_date, last_completed_at, status (pendiente/en_curso/cumplido/vencido), severity (alta/media/baja), responsible_user FK identity.User (optional).
  - `Evidence` — FK ComplianceObligation, kind (archivo/link/nota), file FileField (upload_to='compliance/AAAA/MM/' via TenantStorage), url, note, captured_at, captured_by FK identity.User.

Migration: `0004_b15b_compliance.py`.

Re-export todos desde `apps/api/apps/policies/models/__init__.py`.

### Task 5 — Services

- `apps/api/apps/policies/services/strategic_plan_service.py`
  - `create_plan(*, tenant, name, fiscal_year, period_start, period_end, owner_user, description='') -> HRStrategicPlan`.
  - `add_objective(*, plan, code, title, description='', weight, owner_user=None) -> StrategicObjective`.
  - `add_kpi(*, objective, name, target, target_date, unit='', formula_note='') -> KPI`.
  - `update_kpi_actual(*, kpi, actual, status=None) -> KPI` (auto-set status si no se pasa).
  - `mark_active(plan)`, `mark_completed(plan)`, `archive(plan)`.
  - `compute_progress(plan) -> dict` (weighted progress por objective).
- `apps/api/apps/policies/services/workforce_plan_service.py`
  - `create_plan(*, tenant, name, fiscal_year, period_start, period_end, owner_user) -> WorkforcePlan`.
  - `add_projection(*, plan, area=None, position=None, current_headcount, projected_headcount, justification='', target_quarter='Q1') -> HeadcountProjection` (auto-compute delta).
  - `create_succession_plan(*, tenant, name, fiscal_year, owner_user) -> SuccessionPlan`.
  - `add_key_position(*, succession_plan, position, criticality, current_holder=None, risk_notes='') -> KeyPosition`.
  - `add_successor(*, key_position, employee, readiness_level, order=0, notes='') -> SuccessorCandidate` (idempotent vía unique).
- `apps/api/apps/policies/services/compliance_service.py`
  - `create_matrix(*, tenant, name, fiscal_year, owner_user, description='') -> ComplianceMatrix`.
  - `add_obligation(*, matrix, code, title, source, frequency, next_due_date, severity='media', responsible_user=None) -> ComplianceObligation`.
  - `attach_evidence(*, obligation, kind, file=None, url='', note='', captured_by=None) -> Evidence`.
  - `mark_obligation_completed(*, obligation, completed_at=None, evidence_kwargs=None) -> ComplianceObligation` (avanza last_completed_at, recompute next_due_date según frequency).
  - `recompute_due_dates(tenant=None) -> int` (sigue las frequency reglas; calcula next_due_date desde last_completed_at).
  - `list_alerts(tenant=None, days_ahead=30) -> dict` (`{overdue: [...], due_soon: [...]}`).
  - `mark_overdue_obligations(tenant=None) -> int` (bulk update status='vencido' donde next_due_date < today y status='pendiente').

### Task 6 — API surface + smoke tests

Extender `apps/api/api/v1/policies/urls.py` + `views.py`:
- /strategic-plans/ CRUD + actions: activate, complete, archive, progress (GET detail).
- /strategic-objectives/ CRUD.
- /kpis/ CRUD + actions: update-actual (POST detail).
- /workforce-plans/ CRUD.
- /headcount-projections/ CRUD.
- /succession-plans/ CRUD.
- /key-positions/ CRUD.
- /successor-candidates/ CRUD.
- /compliance-matrices/ CRUD.
- /compliance-obligations/ CRUD + actions: mark-completed (POST detail), alertas (GET collection).
- /evidences/ CRUD + attach via service.

Todos TenantAwareViewSetMixin + RRHHPermission.

Smoke tests:
- `apps/api/apps/policies/tests/test_b15b_strategic_models.py` (≥ 10).
- `apps/api/apps/policies/tests/test_b15b_workforce_models.py` (≥ 10).
- `apps/api/apps/policies/tests/test_b15b_compliance_models.py` (≥ 10).
- `apps/api/apps/policies/tests/test_b15b_services.py` (≥ 10: strategic + workforce + compliance flows).
- `apps/api/apps/policies/tests/test_b15b_api_smoke.py` (≥ 14: routing + auth gating + 3-4 happy paths per área).

### Task 7 — Frontend services + admin pages

Servicios (apps/web/src/features/policies/services/):
- strategicPlanService.ts — plans + objectives + kpis (CRUD + update-actual + progress).
- workforcePlanService.ts — plans + projections + succession + key positions + candidates.
- complianceService.ts — matrices + obligations + evidences + alertas + mark-completed.

Páginas (apps/web/src/features/policies/pages/):
- StrategicPlanListPage.tsx — admin grid plans + drill objectives/KPIs.
- WorkforcePlanListPage.tsx — plans grid + per-plan projections list + succession sub-grid.
- ComplianceMatrixListPage.tsx — matrices grid + obligations badge (vencido/próximo/al día) + alertas-vencimiento collection action.
- index.ts extender exports.

Rutas en App.tsx:
- /politicas/estrategico
- /politicas/dotacion
- /politicas/cumplimiento

Vitest:
- strategicPlanService.test.ts, workforcePlanService.test.ts, complianceService.test.ts (≥ 6 cada uno).

### Task 8 — Close-out + merge to master

- Baselines vs B.15a SHA `98f1bbf5`:
  - pytest must not regress from 910/1/17; expected ~50+ new passes.
  - vitest must not regress from 25/160; expected ~20+ new tests.
  - ESLint 278 preserved.
  - Build clean.
  - manage.py check 0 silenced.
- Tag final del Module 01: documentar que B.15a + B.15b cierran #128, #129, #130, #131.
- Actualizar memoria: `subproject_b_progress.md` con B.15b close-out + indicar B.16 como única fase pendiente.

## Risk register

- **Decimal precision en KPI**: usar Decimal(12, 4) para target/actual (% son fraccionales). Cuidado con divisiones / cero en `progress_pct()` (target=0 → return 0).
- **HeadcountProjection delta auto-compute**: hay que decidir si recalculamos en save() o lo expongo como property (preferencia: property, evita update_fields tracking).
- **ComplianceObligation.next_due_date sin last_completed**: si nunca se ha completado, next_due_date es el seed inicial. `recompute_due_dates` solo aplica si hay last_completed_at.
- **TenantStorage para Evidence.file**: igual que PolicyVersion.pdf_file — upload_to con prefijo categórico; TenantStorage agrega prefijo tenant.
- **Position FK en KeyPosition**: el modelo Position (apps.organization) viene de B.6 — verificar lookup path `organization.Position`.
