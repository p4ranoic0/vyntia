# B.11 Inducción + Período de Prueba Implementation Plan (Modules 03.3 + 03.4)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Modules 03.3 (Inducción RPE 265-2017-SERVIR-PE) and 03.4 (Período
de Prueba). Single phase per the master roadmap. Backend models + services +
API + admin pages for both modules.

**Architecture:**
- **Inducción (onboarding app):** 5 models — `InductionPlan` (header tied to
  Employee), `InductionTask` (checklist children with due date + kind), `InductionMaterial`
  (videos/PDFs/links attached to a task), `InductionMentor` (buddy User assignment),
  `InductionEvaluation` (post-inducción score + competencies). Plan lifecycle
  draft → in_progress → completed → certified. Sector-agnostic: SERVIR
  RPE 265-2017 fields (lengua_originaria flag) coexist with private use.
- **Período de Prueba (contracts app):** 1 model `ProbationPeriod` linked to
  Contract. régimen-specific plazos: 728 personal común 3 months, calificados
  6 months (pacto), dirección/confianza 12 months (pacto); MYPE pequeña 3
  months; 276 carrera administrativa 3 years; CAS does not apply.
  Lifecycle pending → in_progress → evaluated → ratified | not_renewed.
  Alertas a 30 / 15 days before end_date.

**Branch:** `vyntia/B11-induccion-prueba`
**Backlog items in scope:**
- #114 — Module 03.3: 5-model InductionPlan family (P1, 1w)
- #115 — Module 03.3: Certificate generation (RPE 265 obligatorio) (P1, 0.5w)
- #116 — Module 03.4: ProbationPeriod model with régimen-specific plazos +
  alertas + evaluación + ratificación (P1, 1w)

**User-confirmed scope (work-without-pause mode 2026-05-14):**
- Single B.11 PR covering all 3 backlog items.
- Certificate generation reuses existing pdf_generator (xhtml2pdf → WeasyPrint
  → ReportLab fallback). No new PDF rendering pipeline.
- Mentor is an `identity.User` reference (no separate Mentor model with bio /
  expertise — that comes in M05 Learning).
- ProbationPeriod is auto-created on Contract creation for applicable regímenes
  via a service helper, **not** a Django signal (to keep the seam explicit).
- Alertas use computed properties + service queries; no scheduled-cron infra
  is added in B.11 (the alerta list is exposed via API endpoint that the cron
  / dashboard will hit later).

**Out of scope (deferred):**
- Real cron scheduling of probation alerts → post-B (a single `cron_celery`
  cleanup phase).
- Multi-idioma material (lengua originaria — Quechua, Aymara) localization →
  M11 / i18n phase.
- LMS integration / completion tracking of multimedia materials → M05.
- Evaluación 360° del mentor / del trabajador → M06 Performance.
- E-signature of the induction certificate by RRHH director (reuses B.10
  DocumentSignature when caller chooses to).

**Test baselines (post-B.10 SHA `4dde71d9`):**
- pytest 646/1/17, vitest 96/15, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.11:
- pytest **710+/1/17** (~60+ new tests across 6 models + 2 services + 2 API smoke).
- vitest **17+ files / 110+ tests** (+2 service test files, ~14 cases).
- ESLint: held flat (278).

---

## Task 1: Branch + plan + scaffold

Branch created from master at `4dde71d9`. Place plan, commit.

---

## Task 2: Induction models — Plan + Task + Material + Mentor + Evaluation

**Files:**
- `apps/api/apps/onboarding/models/induction.py`
- `apps/api/apps/onboarding/models/__init__.py` (add exports)
- `apps/api/apps/onboarding/migrations/0003_b11_induction.py`
- `apps/api/apps/onboarding/tests/__init__.py`
- `apps/api/apps/onboarding/tests/test_b11_induction_models.py`

**Shape:**
```python
class InductionPlan(models.Model):
    STATUSES = [
        ('draft', 'Borrador'),
        ('in_progress', 'En progreso'),
        ('completed', 'Completada'),
        ('certified', 'Certificada'),
    ]
    KINDS = [
        ('general', 'General (misión/visión/políticas)'),
        ('especifica', 'Específica (funciones del puesto)'),
        ('tecnica', 'Técnica (capacitación específica)'),
        ('mixed', 'Mixta (general + específica)'),
    ]
    id, tenant, employee (FK), contract (FK nullable),
    title, kind, status,
    starts_at, ends_at, completed_at, certified_at,
    lengua_originaria (CharField, blank — code per ISO 639-3),
    created_by, created_at, updated_at

    def mark_in_progress() ...
    def mark_completed() ...
    def mark_certified(certificate_url) ...

class InductionTask(models.Model):
    KINDS = [('day_1', 'Día 1'), ('first_week', 'Primera semana'),
             ('first_month', 'Primer mes'), ('ongoing', 'Continua')]
    bundle (Plan FK), kind, title, description,
    due_offset_days (positive int from plan.starts_at),
    completed_at (DateTime nullable), completed_by,
    order

    @property
    def is_done -> bool

class InductionMaterial(models.Model):
    FORMATS = [('video', 'Video'), ('pdf', 'PDF'),
               ('interactive', 'Interactivo'), ('link', 'Enlace externo')]
    plan (FK), task (FK nullable), title, format, url, file (FileField),
    duration_minutes

class InductionMentor(models.Model):
    plan (OneToOne), mentor (User FK), assigned_at, notes

class InductionEvaluation(models.Model):
    plan (OneToOne), score (0-100), passed, competencies_json,
    evaluator (User FK), evaluated_at, comments
```

**Tests (~14):**
- create_plan_defaults
- mark_in_progress requires status='draft'
- mark_completed requires status='in_progress'
- mark_certified requires status='completed'
- task_default_not_done
- task_is_done_after_completed_at
- material_optional_task
- mentor_one_per_plan (OneToOneField)
- evaluation_one_per_plan (OneToOneField)
- evaluation_passed_when_score_>=60
- tenant_isolation_via_indexes_present
- string_repr_includes_employee_kind
- multiple_plans_per_employee_allowed
- plan_indexed_by_tenant_status

---

## Task 3: induction_service + certificate generation

**Files:**
- `apps/api/apps/onboarding/services/induction_service.py`
- `apps/api/apps/onboarding/services/__init__.py` (add export)
- `apps/api/apps/onboarding/tests/test_b11_induction_service.py`
- `apps/api/templates/induccion/certificado.html` (Django template for cert)

**Service shape:**
```python
DEFAULT_GENERAL_TASKS = [
    ('day_1', 'Bienvenida y recorrido por las instalaciones'),
    ('day_1', 'Entrega de credenciales y accesos'),
    ('first_week', 'Inducción a misión, visión, valores y código de ética'),
    ('first_week', 'Inducción a políticas de seguridad y SST'),
    ('first_month', 'Reunión 1:1 con el supervisor directo'),
    ('first_month', 'Encuesta inicial de clima y ajuste'),
]

@transaction.atomic
def build_plan_for_employee(*, employee, contract=None, kind='general',
                             title='', tenant=None, created_by=None) -> InductionPlan: ...

def mark_task_done(*, task_id, user) -> InductionTask: ...
def assign_mentor(*, plan_id, mentor_user) -> InductionMentor: ...
def record_evaluation(*, plan_id, score, evaluator, competencies=None, comments='') -> InductionEvaluation: ...

def render_certificate_html(plan_id) -> str: ...
def render_certificate_pdf(plan_id) -> bytes:
    """Delegates to pdf_generator's chain (xhtml2pdf → WeasyPrint → ReportLab)."""
```

**Tests (~10):**
- build_plan_creates_default_general_tasks
- build_plan_specific_kind_creates_no_default_tasks
- mark_task_done_persists_user_timestamp
- mark_task_done_idempotent (subsequent calls keep first completed_at)
- assign_mentor_replaces_previous (OneToOne)
- record_evaluation_passed_score
- record_evaluation_failed_score
- render_certificate_html_contains_employee_name
- render_certificate_html_contains_completion_date
- certificate_includes_plan_kind_label

---

## Task 4: ProbationPeriod model + probation_service

**Files:**
- `apps/api/apps/contracts/models/probation_period.py`
- `apps/api/apps/contracts/models/__init__.py` (add export)
- `apps/api/apps/contracts/services/probation_service.py`
- `apps/api/apps/contracts/services/__init__.py` (add export)
- `apps/api/apps/contracts/migrations/0006_b11_probation_period.py`
- `apps/api/apps/contracts/tests/test_b11_probation_period.py`
- `apps/api/apps/contracts/tests/test_b11_probation_service.py`

**Shape:**
```python
class ProbationPeriod(models.Model):
    REGIMENES = [
        ('728_comun', '728 — Personal común'),
        ('728_calificado', '728 — Trabajador calificado (con pacto)'),
        ('728_direccion', '728 — Dirección / Confianza (con pacto)'),
        ('mype_pequena', 'MYPE Pequeña'),
        ('276_carrera', '276 — Carrera Administrativa'),
        ('no_aplica', 'No aplica (CAS u otros)'),
    ]
    STATUSES = [
        ('pending', 'Pendiente de inicio'),
        ('in_progress', 'En período de prueba'),
        ('evaluated', 'Evaluado, pendiente decisión'),
        ('ratified', 'Ratificado'),
        ('not_renewed', 'No renovado'),
    ]
    id, tenant, contract (OneToOne),
    regimen, plazo_dias (int, computed from regimen),
    start_date, end_date (computed),
    status,
    evaluation_score, evaluation_competencies (JSONField),
    evaluator (User FK), evaluated_at,
    decision_reason, decided_by, decided_at,
    created_at, updated_at

    def days_remaining -> int
    def is_within_30_days -> bool
    def is_within_15_days -> bool

    def mark_evaluated(score, evaluator, competencies, comments) ...
    def mark_ratified(user) ...
    def mark_not_renewed(user, reason) ...

# Plazos default (in days) per régimen:
PLAZO_DIAS = {
    '728_comun': 90,
    '728_calificado': 180,
    '728_direccion': 365,
    'mype_pequena': 90,
    '276_carrera': 1095,  # 3 years
    'no_aplica': 0,
}
```

**probation_service shape:**
```python
def create_for_contract(*, contract, regimen='728_comun', start_date=None) -> ProbationPeriod: ...
def list_overdue(tenant=None) -> QuerySet: ...
def list_alertas_30d(tenant=None) -> QuerySet: ...
def list_alertas_15d(tenant=None) -> QuerySet: ...
```

**Tests (~12):**
Model tests (8):
- create_persists_plazo_dias_from_regimen
- end_date_auto_computed_on_save
- mark_evaluated_promotes_status
- mark_ratified_only_from_evaluated
- mark_not_renewed_requires_reason
- days_remaining_calculation
- is_within_30_days_boundary
- no_aplica_regimen_has_zero_plazo

Service tests (4):
- create_for_contract_defaults_to_728_comun_90d
- list_overdue_excludes_decided
- list_alertas_30d_filters_correctly
- list_alertas_15d_subset_of_30d

---

## Task 5: API surface (4 ViewSets + custom actions)

**Files:**
- `apps/api/api/v1/onboarding/induction_views.py` (new)
- `apps/api/api/v1/onboarding/serializers.py` (extend or new)
- `apps/api/api/v1/onboarding/urls.py` (extend)
- `apps/api/api/v1/contracts/probation_views.py` (new)
- `apps/api/api/v1/contracts/serializers.py` (extend)
- `apps/api/api/v1/contracts/urls.py` (extend)
- `apps/api/apps/onboarding/tests/test_b11_api_smoke.py`
- `apps/api/apps/contracts/tests/test_b11_api_smoke.py`

**Endpoints:**

```
GET    /api/v1/onboarding/induction-plans/
POST   /api/v1/onboarding/induction-plans/
GET    /api/v1/onboarding/induction-plans/<uuid>/
PATCH  /api/v1/onboarding/induction-plans/<uuid>/
POST   /api/v1/onboarding/induction-plans/<uuid>/start/
POST   /api/v1/onboarding/induction-plans/<uuid>/complete/
POST   /api/v1/onboarding/induction-plans/<uuid>/certify/
POST   /api/v1/onboarding/induction-plans/<uuid>/assign-mentor/
POST   /api/v1/onboarding/induction-plans/<uuid>/record-evaluation/
GET    /api/v1/onboarding/induction-plans/<uuid>/certificate-pdf/  (PDF download)
GET    /api/v1/onboarding/induction-tasks/
POST   /api/v1/onboarding/induction-tasks/<uuid>/mark-done/
GET    /api/v1/onboarding/induction-materials/
POST   /api/v1/onboarding/induction-materials/

GET    /api/v1/probation-periods/                  (flat under /api/v1/)
POST   /api/v1/probation-periods/
GET    /api/v1/probation-periods/<uuid>/
PATCH  /api/v1/probation-periods/<uuid>/
POST   /api/v1/probation-periods/<uuid>/evaluate/
POST   /api/v1/probation-periods/<uuid>/ratify/
POST   /api/v1/probation-periods/<uuid>/not-renew/
GET    /api/v1/probation-periods/alertas/          (collection action — 30d + 15d windows)
```

All TenantAwareViewSetMixin + RRHHPermission.

**Tests:** ~18 across 2 smoke files (auth gating, happy paths, state-machine misuse).

---

## Task 6: Frontend services + admin pages

**Files:**
- `apps/web/src/features/onboarding/services/inductionService.ts`
- `apps/web/src/features/onboarding/services/__tests__/inductionService.test.ts`
- `apps/web/src/features/contracts/services/probationPeriodService.ts`
- `apps/web/src/features/contracts/services/__tests__/probationPeriodService.test.ts`
- `apps/web/src/features/onboarding/pages/InductionPlanListPage.tsx`
- `apps/web/src/features/contracts/pages/ProbationPeriodListPage.tsx`
- Route registration in `App.tsx`: `/induccion`, `/periodo-prueba`

Typed clients + vitest unit tests (~14 cases). Two simple list pages with row
actions (start, complete, certify, evaluate, ratify, not-renew). Lazy-loaded +
AdminRoute-gated.

---

## Task 7: Final verification + merge

1. `pytest -q` from `apps/api/` — assert ≥ 710 passing.
2. `npm test -- --run`, `npm run lint`, `npx tsc --noEmit -p tsconfig.app.json`, `npm run build`.
3. `manage.py check` clean.
4. Update `subproject_b_progress.md` with close-out + merge SHA.
5. `git merge --no-ff` to master.

Done criteria:
- Backlog #114, #115, #116 closed.
- Baselines preserved.
- Memory file updated.
