# B.9 Selección Implementation Plan (Module 03.1 — SERVIR Proceso 5 / sector privado + público)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 03.1 — Selección — covering the full personnel-selection lifecycle from authorized requisition through merit-ranked hiring decision. Both private sector (Ley 728 / DL 1057-CAS) and public sector (Ley 30057 SERVIR concurso público) are first-class scenarios sharing the same model layer and discriminating by `JobPosting.sector_mode`.

**Architecture:** 7-model module per backlog item #110. Single tenant-scoped chain `PersonnelRequisition → JobPosting → JobApplication → CandidateEvaluation → MeritRanking`, plus `Candidate` (decoupled from User — most candidates are external) and `SelectionStage` (configurable evaluation stages per posting). Sector is a JobPosting flag (`private` | `public_servir`) that gates plazos legales (≥7 días hábiles publicación pública SERVIR), nota mínima eliminatoria 14/20 en conocimientos, transparencia obligatoria, and integration hook with CPE entries (B.8) for público — no separate models. Frontend ships HR admin pages only; public candidate-portal is out of scope (see deferrals).

**Branch:** `vyntia/B9-seleccion`
**Backlog items in scope:** #110 (Selección — 7 models, sector privado + público).
**User-confirmed scope decisions (2026-05-10):**
- Full 7 models from backlog (not the MVP-4 split).
- Sector público SERVIR concurso completo en B.9 (no diferir).
- Backend + API + admin HR pages (no candidate public portal).
- Module 11 (ATS avanzado) diferido completamente — no hooks `external_source`.

**Out of scope (deferred):**
- Candidate-facing public portal (sin auth, postulación externa) → B.9.1 if requested.
- Module 11 ATS features (job-board scraping, social, video interviewing, AI matching) → M11 phase.
- Selección psicolaboral via tercero (integración con proveedor) → M11.
- Document templates auto-generated for "bases del concurso" PDF → B.15 Policies (template engine).
- Comité de Selección con RBAC dedicado por miembro → simplified to `evaluator` FK on CandidateEvaluation; full committee model in M11.
- Integración con SERVIR portal externo (publicación remota) → manual today; post-B.

**Test baselines (post-B.8 SHA `bb4130a0`):**
- pytest 482/1/17, vitest 11/63, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.9:
- pytest **535+/1/17** (~50+ new tests across 7 models + ranking service + API smoke).
- vitest **12+ files / 75+ tests** (selectionService + page snapshots).
- ESLint: held flat.

---

## Task 1: Branch + plan + scaffold

Branch already created. Place plan, commit, capture baselines.

---

## Task 2: Candidate model (external person, not User)

**Files:**
- `apps/api/apps/employees/models/candidate.py`

```python
class Candidate(models.Model):
    """External candidate participating in selection processes.

    Decoupled from `identity.User` — most candidates are external and never
    receive a system account. If a candidate becomes hired, link from
    `Employee.candidate` FK (post-Vinculación, B.10) for traceability.
    """

    GENDER_CHOICES = [('M', 'Masculino'), ('F', 'Femenino'), ('X', 'No binario / sin declarar')]
    DOC_TYPE_CHOICES = [
        ('dni', 'DNI'), ('ce', 'Carné de Extranjería'),
        ('passport', 'Pasaporte'), ('ptp', 'PTP'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                               null=True, blank=True, db_index=True, related_name='+')

    # Identity
    document_type = models.CharField(max_length=10, choices=DOC_TYPE_CHOICES, default='dni')
    document_number = models.CharField(max_length=20, db_index=True)
    first_names = models.CharField(max_length=100)
    last_names = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    # Contact
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=300, blank=True)

    # Career snapshot (denormalized for ranking; full CV in attached files)
    years_experience = models.PositiveIntegerField(default=0)
    highest_education = models.CharField(max_length=100, blank=True)

    # Files
    cv_file = models.FileField(upload_to='candidates/%Y/%m/', null=True, blank=True)

    # Source attribution
    source = models.CharField(max_length=50, blank=True,
                               help_text='internal_referral | website | linkedin | servir | walk_in | other')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'document_number']),
            models.Index(fields=['tenant', 'email']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'document_type', 'document_number'],
                name='unique_candidate_doc_per_tenant',
            ),
        ]

    @property
    def full_name(self):
        return f"{self.first_names} {self.last_names}".strip()
```

Migration: `employees.000X_b9_candidate`.

Tests: smoke create; uniqueness per tenant on (doc_type, doc_number); email lookup index.

Commit:
```
feat(B9): Candidate model (external candidate, decoupled from User)
```

---

## Task 3: PersonnelRequisition model (alta autorizada)

**Files:**
- `apps/api/apps/employees/models/personnel_requisition.py`

Workflow: `draft → pending_approval → approved | rejected | cancelled`. Approval requires both HR (`approved_by_hr`) and finance (`approved_by_finance`) — both nullable until set.

```python
class PersonnelRequisition(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending_approval', 'Pendiente de aprobación'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('cancelled', 'Cancelada'),
        ('fulfilled', 'Cubierta'),
    ]
    JUSTIFICATION_CHOICES = [
        ('new_position', 'Plaza nueva'),
        ('replacement', 'Reemplazo por baja'),
        ('expansion', 'Crecimiento del área'),
        ('temporary', 'Cobertura temporal'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    code = models.CharField(max_length=30, blank=True,
                             help_text='Auto-generated from sequence, e.g. REQ-2026-0001.')
    position = models.ForeignKey('organization.Position', on_delete=models.PROTECT,
                                  related_name='requisitions')
    plaza = models.ForeignKey('organization.Plaza', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='requisitions',
                               help_text='Optional — concrete plaza being filled. May be null for new plazas.')
    department = models.ForeignKey('organization.Department', on_delete=models.PROTECT,
                                    related_name='requisitions')
    justification = models.CharField(max_length=20, choices=JUSTIFICATION_CHOICES)
    justification_notes = models.TextField(blank=True)

    requested_count = models.PositiveIntegerField(default=1)
    requested_start_date = models.DateField(null=True, blank=True)
    estimated_monthly_cost = models.DecimalField(max_digits=12, decimal_places=2,
                                                   null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='draft', db_index=True)

    requested_by = models.ForeignKey('identity.User', on_delete=models.PROTECT,
                                      related_name='requisitions_requested')
    approved_by_hr = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name='+')
    approved_by_finance = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                              null=True, blank=True, related_name='+')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @transaction.atomic
    def submit_for_approval(self):
        """draft → pending_approval"""

    @transaction.atomic
    def approve_hr(self, *, user): ...
    @transaction.atomic
    def approve_finance(self, *, user): ...
    @transaction.atomic
    def reject(self, *, user, reason): ...
    @transaction.atomic
    def cancel(self, *, user): ...
    def mark_fulfilled(self): ...

    @property
    def is_fully_approved(self):
        return self.approved_by_hr_id and self.approved_by_finance_id
```

`status` flips to `approved` only when **both** HR and finance approve. Single approval moves to `pending_approval` and stays there.

Migration: `employees.000Y_b9_personnel_requisition`.

Tests: lifecycle transitions; fully-approved property; FK PROTECT on Position; tenant constraint on code.

Commit:
```
feat(B9): PersonnelRequisition model (alta autorizada con doble firma HR + Finanzas)
```

---

## Task 4: JobPosting model (convocatoria con sector)

**Files:**
- `apps/api/apps/employees/models/job_posting.py`

```python
class JobPosting(models.Model):
    SECTOR_MODE_CHOICES = [
        ('private', 'Sector privado'),
        ('public_servir', 'Sector público — concurso SERVIR (Ley 30057)'),
    ]
    POSTING_KIND_CHOICES = [
        ('internal', 'Interna'),
        ('external', 'Externa'),
        ('mixed', 'Mixta'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicada'),
        ('in_evaluation', 'En evaluación'),
        ('closed', 'Cerrada'),
        ('cancelled', 'Cancelada'),
        ('declared_void', 'Declarada desierta'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    requisition = models.ForeignKey('employees.PersonnelRequisition',
                                     on_delete=models.PROTECT, related_name='postings')
    code = models.CharField(max_length=30, blank=True)
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)

    sector_mode = models.CharField(max_length=20, choices=SECTOR_MODE_CHOICES,
                                    default='private', db_index=True)
    posting_kind = models.CharField(max_length=20, choices=POSTING_KIND_CHOICES,
                                     default='external')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='draft', db_index=True)

    # Plazos (mandatory for public_servir; optional for private)
    published_at = models.DateTimeField(null=True, blank=True)
    applications_open_at = models.DateField(null=True, blank=True)
    applications_close_at = models.DateField(null=True, blank=True)
    results_announce_at = models.DateField(null=True, blank=True)

    # SERVIR-specific
    bases_url = models.URLField(blank=True, help_text='Public URL to bases PDF.')
    bases_file = models.FileField(upload_to='postings/bases/%Y/%m/', null=True, blank=True)
    cpe_entry = models.ForeignKey('organization.PositionRegisterEntry',
                                    on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='postings',
                                    help_text='Plaza del CPE (Ley 30057, B.8) que esta convocatoria cubre.')
    transparency_published = models.BooleanField(default=False,
                                                   help_text='SERVIR Art. 5: publicación obligatoria en portal institucional + SERVIR.')

    closed_reason = models.TextField(blank=True,
                                      help_text='Motivo de cierre o de declaración desierta.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='+')

    @transaction.atomic
    def publish(self, *, user):
        """draft → published. Validates plazos for public_servir."""

    @transaction.atomic
    def close(self, *, reason=''): ...
    @transaction.atomic
    def declare_void(self, *, reason): ...

    def clean(self):
        # Public SERVIR requires plazos + bases + ≥7 días hábiles between open/close.
        if self.sector_mode == 'public_servir':
            ...
```

Migration: `employees.000Z_b9_job_posting`.

Tests: lifecycle; SERVIR validation on publish (plazos + bases + transparency flag); CPE FK gating; private posting passes without plazos.

Commit:
```
feat(B9): JobPosting model (convocatoria con sector private | public_servir + plazos legales SERVIR)
```

---

## Task 5: SelectionStage model (etapas configurables)

**Files:**
- `apps/api/apps/employees/models/selection_stage.py`

```python
class SelectionStage(models.Model):
    KIND_CHOICES = [
        ('curricular', 'Evaluación curricular'),
        ('knowledge', 'Prueba de conocimientos'),
        ('psycho', 'Evaluación psicolaboral'),
        ('interview', 'Entrevista personal'),
        ('technical', 'Prueba técnica'),
        ('reference', 'Verificación de referencias'),
        ('other', 'Otra'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    posting = models.ForeignKey('employees.JobPosting', on_delete=models.CASCADE,
                                 related_name='stages')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    name = models.CharField(max_length=100,
                              help_text='Custom display name; defaults to kind label.')
    order = models.PositiveIntegerField(default=0)
    is_eliminatoria = models.BooleanField(default=True,
                                            help_text='Failing this stage removes candidate from process.')
    min_score = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                      help_text='Minimum passing score (e.g. 14.00 for SERVIR conocimientos).')
    max_score = models.DecimalField(max_digits=5, decimal_places=2, default=20)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text='Weight in final merit ranking (must sum to 100 across non-eliminatoria stages or for total).')
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'selection_stage'
        ordering = ['posting', 'order']
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'order'],
                name='unique_stage_order_per_posting',
            ),
        ]

    def clean(self):
        if self.min_score > self.max_score:
            raise ValidationError("min_score no puede exceder max_score.")
```

Migration: `employees.000W_b9_selection_stage`.

Tests: ordering uniqueness per posting; clean() validation; default kinds for SERVIR (curricular/knowledge/interview seeded helper).

Commit:
```
feat(B9): SelectionStage model (etapas configurables por convocatoria)
```

---

## Task 6: JobApplication model (postulación + estado machine)

**Files:**
- `apps/api/apps/employees/models/job_application.py`

```python
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('received', 'Recibida'),
        ('reviewing', 'En revisión'),
        ('in_evaluation', 'En evaluación'),
        ('eliminated', 'Eliminada'),
        ('finalist', 'Finalista'),
        ('offered', 'Oferta enviada'),
        ('accepted', 'Aceptada'),
        ('hired', 'Contratada'),
        ('rejected', 'Rechazada'),
        ('withdrawn', 'Retirada por candidato'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    posting = models.ForeignKey('employees.JobPosting', on_delete=models.PROTECT,
                                 related_name='applications')
    candidate = models.ForeignKey('employees.Candidate', on_delete=models.PROTECT,
                                    related_name='applications')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                               default='received', db_index=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    eliminated_at_stage = models.ForeignKey('employees.SelectionStage',
                                              on_delete=models.SET_NULL,
                                              null=True, blank=True, related_name='+',
                                              help_text='Stage that eliminated this application (if any).')
    elimination_reason = models.TextField(blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)

    cover_letter = models.TextField(blank=True)
    custom_cv_file = models.FileField(upload_to='applications/cv/%Y/%m/',
                                        null=True, blank=True,
                                        help_text='Posting-specific CV; falls back to candidate.cv_file.')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_application'
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'candidate'],
                name='unique_application_per_posting_candidate',
            ),
        ]

    def advance_to(self, status): ...
    def eliminate(self, *, stage, reason): ...
    def withdraw(self): ...
```

Migration: `employees.000V_b9_job_application`.

Tests: unique constraint per posting/candidate; eliminate flow sets stage + status; withdraw irreversible.

Commit:
```
feat(B9): JobApplication model (postulación con state machine)
```

---

## Task 7: CandidateEvaluation model (calificación por etapa)

**Files:**
- `apps/api/apps/employees/models/candidate_evaluation.py`

```python
class CandidateEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey('employees.JobApplication', on_delete=models.CASCADE,
                                      related_name='evaluations')
    stage = models.ForeignKey('employees.SelectionStage', on_delete=models.PROTECT,
                                related_name='evaluations')
    evaluator = models.ForeignKey('identity.User', on_delete=models.PROTECT,
                                    related_name='evaluations_authored')

    score = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()
    notes = models.TextField(blank=True)

    evaluated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidate_evaluation'
        ordering = ['stage__order', 'application']
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'stage'],
                name='unique_evaluation_per_application_stage',
            ),
        ]

    def clean(self):
        if not (self.stage.min_score <= self.score <= self.stage.max_score):
            raise ValidationError(
                f"Puntaje {self.score} fuera de rango [{self.stage.min_score}, {self.stage.max_score}]"
            )

    def save(self, *args, **kwargs):
        # Auto-derive passed from score vs stage.min_score
        self.passed = self.score >= self.stage.min_score
        super().save(*args, **kwargs)
```

Migration: `employees.000U_b9_candidate_evaluation`.

Tests: unique per (application, stage); auto-derived passed; clean() range validation; eliminatoria stage failing → application.eliminate() helper hook (in service layer Task 8).

Commit:
```
feat(B9): CandidateEvaluation model (calificación por etapa con score range + auto-passed)
```

---

## Task 8: MeritRanking model + ranking_service

**Files:**
- `apps/api/apps/employees/models/merit_ranking.py`
- `apps/api/apps/employees/services/__init__.py` (extend)
- `apps/api/apps/employees/services/ranking_service.py`

```python
class MeritRanking(models.Model):
    OUTCOME_CHOICES = [
        ('winner', 'Ganador'),
        ('waiting_list', 'Lista de espera'),
        ('eliminated', 'Eliminado'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    posting = models.ForeignKey('employees.JobPosting', on_delete=models.CASCADE,
                                 related_name='rankings')
    application = models.ForeignKey('employees.JobApplication',
                                      on_delete=models.CASCADE, related_name='rankings')

    rank = models.PositiveIntegerField(help_text='1 = winner; 2+ = waiting list / eliminated.')
    total_score = models.DecimalField(max_digits=6, decimal_places=2)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    snapshot_at = models.DateTimeField(auto_now_add=True)

    # Detailed breakdown (denormalized for transparency / SERVIR audit)
    score_breakdown = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'merit_ranking'
        ordering = ['posting', 'rank']
        constraints = [
            models.UniqueConstraint(
                fields=['posting', 'application'],
                name='unique_ranking_per_posting_application',
            ),
        ]
```

**ranking_service.py:**
```python
def compute_merit_ranking(*, posting, declare_winner=True):
    """Aggregate evaluations across stages × applications and write MeritRanking rows.

    Algorithm:
    1. For each non-eliminated JobApplication of `posting`:
       - Sum (eval.score × stage.weight / 100) across all CandidateEvaluations.
       - Skip applications that failed any eliminatoria stage.
    2. Sort descending by total_score, break ties by earlier applied_at.
    3. Assign rank 1..N. Outcome = 'winner' for rank=1 (if declare_winner)
       else 'waiting_list' until candidate count drops below requested.
    4. Failed-eliminatoria applications get outcome='eliminated' rank=None? No — give them ranks at end with 0 score for transparency.
    5. Atomic transaction: delete existing rankings for posting, write new ones.
    """
```

Migration: `employees.000T_b9_merit_ranking`.

Tests: ranking algorithm end-to-end (3 candidates × 3 stages → expected order); eliminatoria fail filters out; ties broken by applied_at; idempotent recompute.

Commit:
```
feat(B9): MeritRanking + ranking_service (aggregation algorithm with eliminatoria filtering)
```

---

## Task 9: API ViewSets + serializers + URLs

**Files:**
- `apps/api/api/v1/employees/views.py` — extend with 7 new ViewSets
- `apps/api/api/v1/employees/serializers.py` — extend with serializers
- `apps/api/api/v1/employees/urls.py` — register routes

Routes flat under `/api/v1/` (matches existing employees-app convention
per api/v1/urls.py § 7):
- `/candidates/` — CandidateViewSet (CRUD)
- `/personnel-requisitions/` — RequisitionViewSet + `submit/`, `approve-hr/`, `approve-finance/`, `reject/`, `cancel/`
- `/job-postings/` — JobPostingViewSet + `publish/`, `start-evaluation/`, `close/`, `declare-void/`, `compute-ranking/`
- `/selection-stages/` — SelectionStageViewSet (CRUD, filtered by posting)
- `/job-applications/` — JobApplicationViewSet + `advance-to/`, `eliminate/`, `withdraw/`
- `/candidate-evaluations/` — CandidateEvaluationViewSet (CRUD; evaluator auto-set from request.user)
- `/merit-rankings/` — MeritRankingViewSet (read-only; computed via job-postings/<id>/compute-ranking/)

Permission gating: RRHHPermission + TenantAwareViewSetMixin on tenant-scoped models. Public-sector posting actions check sector_mode validation.

Tests: smoke routing + auth + custom actions.

Commit:
```
feat(B9): API surface for Selección — 7 ViewSets + 8 custom actions
```

---

## Task 10: Frontend service + admin pages

**Files:**
- `apps/web/src/features/recruitment/services/selectionService.ts` (new feature dir)
- `apps/web/src/features/recruitment/pages/RequisitionListPage.tsx`
- `apps/web/src/features/recruitment/pages/JobPostingEditorPage.tsx`
- `apps/web/src/features/recruitment/pages/CandidateDashboardPage.tsx` (per-posting candidate view + ranking)
- Route registration in App.tsx: `/seleccion/requisiciones`, `/seleccion/convocatorias/:id`, `/seleccion/convocatorias/:id/candidatos`

Service methods (~15):
- `listRequisitions/getRequisition/createRequisition/submitRequisition/approveHR/approveFinance/rejectRequisition`
- `listPostings/getPosting/createPosting/publishPosting/closePosting/declareVoid`
- `listStages/upsertStage`
- `listCandidates/createCandidate`
- `listApplications/createApplication/eliminateApplication`
- `listEvaluations/upsertEvaluation`
- `computeRanking(postingId)` + `listRanking(postingId)`

Vitest tests (≥10).

Commit:
```
feat(B9): frontend service + admin pages for Selección (HR-only)
```

---

## Task 11: Final verification + merge

Verify baselines (pytest 535+, vitest 12+ files, ESLint 278, tsc 1, build clean, manage.py check 0).
Update memory + test_baselines.
Merge to master with comprehensive message.

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 110 | Selección 7-model module | Tasks 2-8 |
| Sector privado + público | sector_mode discriminator on JobPosting | Task 4 |
| Concurso público SERVIR completo | plazos + bases + CPE FK + transparency flag | Tasks 4, 5 |
| Backend + API + admin HR pages | 7 ViewSets + 3 admin pages | Tasks 9, 10 |
| ADR-B.7 versioning | NOT applied — Selección is not a versioned doc | — |
| Position + Plaza FK (B.6) | PersonnelRequisition.position + .plaza | Task 3 |
| CPE entry FK (B.8) | JobPosting.cpe_entry SET_NULL | Task 4 |

**Deferred (with rationale):**
- Public candidate portal — scope explosion; HR admin sufficient for MVP.
- M11 ATS hooks — explicit user decision; no hooks today.
- Comité de Selección con RBAC — single evaluator FK simplification.
- SERVIR portal external integration — manual today.
- Document templates for "bases del concurso" → B.15 Policies.
