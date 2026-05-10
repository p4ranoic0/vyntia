# B.7 CCF + SalaryBand Implementation Plan (Ley 30709)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Ley 30709 / D.S. 002-2018-TR compliance — Cuadro de Categorías y Funciones (CCF), 4-factor scoring methodology per R.M. 243-2018-TR, salary bands per category, employee assignment to category via Position, salary-gap audit by category × sex, and Excel bulk import of CCF data.

**Architecture:** New `apps/compensation/` Django app for CCF + Category + SalaryBand + factor scoring. Position (B.6) gets a nullable `category` FK so each Position rolls up into its CCF category. Audit endpoint computes group means per category × sex via EmploymentData/Contract salaries. Excel import accepts a predefined .xlsx template; download endpoint emits the template. UI-only sector gate (per user choice) hides menu/routes for public-sector tenants via `useTenant()`.

**Branch:** `vyntia/B7-ccf-salaryband`
**Backlog items in scope:** #105 (CCF — Ley 30709) + #106 (SalaryBand + Excel + audit).
**User-confirmed scope decisions (2026-05-10):**
- PoliticaSalarial deferred to B.15 (Policies module). B.7 ships data layer + audit + import only.
- Full 4-factor methodology with subfactor scores per R.M. 243-2018-TR (Competencias / Responsabilidad / Esfuerzo / Condiciones).
- Excel import + audit endpoint both ship in B.7.
- UI-only sector gate (backend permissive, frontend hides for public tenants).

**Out of scope (deferred):**
- PoliticaSalarial document model → B.15.
- Dashboard de equidad salarial (visual analytics) → B.12 (analytics module).
- Workflow de reclamos por discriminación → independent channel.
- Plan de nivelación automático (algorithmic raise suggestions) → B.7.1 if requested.
- Capacitación integrada (curso anual igualdad) → M05.
- Aviso automático al trabajador (PDF on category change) → B.7.1.

**Test baselines (post-B.6 SHA `79ccb27e`):**
- pytest 393/1/17, vitest 9/43, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.7:
- pytest **415+/1/17** (~22 new tests across models + factor scoring + audit + import).
- vitest **10+ files / 48+ tests** (CCF service + admin form tests).
- ESLint: held flat.
- Bundle: CCF admin pages share main bundle; no lazy chunk needed (forms only, no heavy graph lib).

---

## Task 1: Branch + plan + scaffold compensation app

```bash
cd D:/VYNTIA
git checkout -b vyntia/B7-ccf-salaryband    # already done
mkdir -p apps/api/apps/compensation/{models,migrations,tests,services,management/commands}
touch apps/api/apps/compensation/__init__.py
touch apps/api/apps/compensation/{models,migrations,tests,services,management,management/commands}/__init__.py
```

Add `apps.compensation.apps.CompensationConfig` to `LOCAL_APPS` in `vyntia/settings/base.py`.

Capture baselines: pytest 393/1/17, ESLint 278.

Commit:
```
docs(B7): plan for CCF + SalaryBand (Ley 30709, 2 backlog items in scope)
```

---

## Task 2: Create JobFactor + JobSubfactor reference data models (R.M. 243-2018-TR)

**Files:**
- `apps/api/apps/compensation/models/job_factor.py`
- `apps/api/apps/compensation/models/job_subfactor.py`
- `apps/api/apps/compensation/management/commands/seed_job_factors.py`

**JobFactor (system-wide reference):**
```python
class JobFactor(models.Model):
    """One of the 4 factors per R.M. 243-2018-TR.

    System-wide reference data. Seeded with: COMPETENCIAS, RESPONSABILIDAD,
    ESFUERZO, CONDICIONES.
    """
    KIND_CHOICES = [
        ('competencias', 'Competencias'),
        ('responsabilidad', 'Responsabilidad'),
        ('esfuerzo', 'Esfuerzo'),
        ('condiciones', 'Condiciones de Trabajo'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('25.00'),
                                  help_text='% weight of this factor (sums to 100 across all 4)')
    is_active = models.BooleanField(default=True)
```

**JobSubfactor (system-wide reference):**
```python
class JobSubfactor(models.Model):
    """A subfactor under one of the 4 factors per R.M. 243-2018-TR.

    E.g. COMPETENCIAS has subfactors: conocimientos, habilidades, experiencia.
    RESPONSABILIDAD has: por personas, por bienes, por decisiones, por resultados.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    factor = models.ForeignKey('compensation.JobFactor', on_delete=models.CASCADE,
                                related_name='subfactors')
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)
```

**Seed command:** `seed_job_factors` — idempotent. Seeds 4 factors + ~10 subfactors covering R.M. 243-2018-TR canonical list.

Tests: smoke seed + idempotency.

Commit:
```
feat(B7): JobFactor + JobSubfactor reference models (R.M. 243-2018-TR)
```

---

## Task 3: Create CategoryFunctionTable (CCF) + Category models

**Files:**
- `apps/api/apps/compensation/models/category_function_table.py`
- `apps/api/apps/compensation/models/category.py`

**CategoryFunctionTable (CCF — tenant-scoped, versioned):**
```python
class CategoryFunctionTable(models.Model):
    """CCF — Cuadro de Categorías y Funciones (Ley 30709).

    A versioned document that aggregates Category rows for the tenant.
    Required by Ley 30709 for all private-sector employers. Versioning
    is inline (per ADR-B.7 pattern) so historical CCFs remain queryable
    for SUNAFIL audits.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('approved', 'Aprobado'),
        ('superseded', 'Reemplazado'),
        ('archived', 'Archivado'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='successors')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft',
                               db_index=True)
    effective_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='approved_ccfs')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('identity.User', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='created_ccfs')
```

**Category (CCF row):**
```python
class Category(models.Model):
    """A categoría inside a CCF. Holds denomination, requirements, factor scores."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')
    ccf = models.ForeignKey('compensation.CategoryFunctionTable',
                             on_delete=models.CASCADE, related_name='categories')

    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    functions_summary = models.TextField(blank=True,
                                          help_text='Funciones generales de la categoría (Ley 30709 § 4.1).')

    # Minimum requirements (objetivos per Ley 30709)
    min_education = models.CharField(max_length=200, blank=True)
    min_experience_years = models.PositiveIntegerField(default=0)
    technical_competencies = models.JSONField(default=list, blank=True)
    soft_competencies = models.JSONField(default=list, blank=True)
    physical_conditions = models.TextField(blank=True)

    # Computed score (sum of factor scores × weight); written by service layer
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'),
                                       help_text='Total puntaje (computed from factor scores).')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'ccf', 'code'],
                name='unique_category_code_per_ccf_per_tenant',
            ),
        ]
```

Tests: smoke create CCF + Category, unique constraint, cascade delete CCF→Categories.

Commit:
```
feat(B7): CategoryFunctionTable (CCF) + Category models (Ley 30709)
```

---

## Task 4: Create CategoryFactorScore + SalaryBand models

**Files:**
- `apps/api/apps/compensation/models/category_factor_score.py`
- `apps/api/apps/compensation/models/salary_band.py`

**CategoryFactorScore (Category × Subfactor → score):**
```python
class CategoryFactorScore(models.Model):
    """Score for one (Category, JobSubfactor) pair. Drives Ley 30709 audit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey('compensation.Category',
                                  on_delete=models.CASCADE, related_name='factor_scores')
    subfactor = models.ForeignKey('compensation.JobSubfactor',
                                   on_delete=models.PROTECT, related_name='+')
    score = models.PositiveIntegerField(default=0,
                                         help_text='Score 0..subfactor.max_score')
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'subfactor'],
                name='unique_factor_score_per_category_subfactor',
            ),
        ]

    def clean(self):
        if self.score > self.subfactor.max_score:
            raise ValidationError(
                f"Score {self.score} excede max {self.subfactor.max_score} "
                f"para subfactor {self.subfactor.code}."
            )
```

**SalaryBand (1-to-1 with Category):**
```python
class SalaryBand(models.Model):
    """Banda salarial mín/medio/máx per Category. Ley 30709 § 4.1."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.OneToOneField('compensation.Category',
                                     on_delete=models.CASCADE, related_name='salary_band')
    min_salary = models.DecimalField(max_digits=12, decimal_places=2)
    mid_salary = models.DecimalField(max_digits=12, decimal_places=2)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='PEN')

    placement_criteria = models.TextField(blank=True,
                                           help_text='Criterios para ubicar al trabajador en la banda (experiencia, desempeño, etc.).')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.min_salary >= self.mid_salary:
            raise ValidationError("min_salary debe ser < mid_salary")
        if self.mid_salary >= self.max_salary:
            raise ValidationError("mid_salary debe ser < max_salary")
```

Tests: smoke create, salary band validation, score within max bound, cascade behavior.

Commit:
```
feat(B7): CategoryFactorScore + SalaryBand (Ley 30709 banding)
```

---

## Task 5: Add `Position.category` FK + `Category.total_score` service

**Files:**
- `apps/api/apps/organization/models/position.py` — add `category` FK
- `apps/api/apps/compensation/services/scoring_service.py` — total_score recomputation

```python
# Position addition
category = models.ForeignKey(
    'compensation.Category',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='positions',
    help_text='Ley 30709 category from CCF (post-B.7). Nullable while CCF rolls out.',
)
```

**scoring_service.py:**
```python
def recompute_category_total(category):
    """Sum all factor scores × factor weight → total_score on Category."""
    from apps.compensation.models import CategoryFactorScore
    scores = CategoryFactorScore.objects.select_related(
        'subfactor', 'subfactor__factor'
    ).filter(category=category)
    total = Decimal('0.00')
    for s in scores:
        weight = s.subfactor.factor.weight / Decimal('100.00')
        total += Decimal(s.score) * weight
    category.total_score = total
    category.save(update_fields=['total_score'])
    return total
```

Migration: `organization.0008_position_category_fk` + `compensation.0001_initial`.

Tests: service recomputes total correctly across factor weights.

Commit:
```
feat(B7): Position.category FK + Category total_score recompute service
```

---

## Task 6: Salary-gap audit service (Ley 30709 § 8)

**Files:**
- `apps/api/apps/compensation/services/audit_service.py`

```python
def compute_salary_gap_by_category(*, tenant=None, ccf_id=None):
    """Return list of dicts per Category × sex with avg salary and brecha %.

    Each row:
        {
          'category_id': ..., 'category_code': ..., 'category_name': ...,
          'group_male': {'count': N, 'avg_salary': Decimal},
          'group_female': {'count': N, 'avg_salary': Decimal},
          'brecha_pct': Decimal,  # (male_avg - female_avg) / male_avg * 100
          'alert': bool,           # True when |brecha_pct| > 5
        }
    """
    from apps.compensation.models import Category
    from apps.contracts.models import EmploymentData
    from apps.organization.models import Position

    qs = Category.objects.filter(is_active=True)
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    if ccf_id is not None:
        qs = qs.filter(ccf_id=ccf_id)

    rows = []
    for cat in qs:
        positions = Position.objects.filter(category=cat, is_current=True)
        emp_data = EmploymentData.objects.filter(
            position__in=positions,
            estado_datos='activo',
        ).select_related('empleado')

        male = [e for e in emp_data if getattr(e.empleado, 'genero_empleado', '') == 'masculino']
        female = [e for e in emp_data if getattr(e.empleado, 'genero_empleado', '') == 'femenino']

        def avg_salary(group):
            if not group:
                return Decimal('0.00')
            total = sum((Decimal(g.salario_basico or 0) for g in group), Decimal('0.00'))
            return total / len(group)

        m_avg = avg_salary(male)
        f_avg = avg_salary(female)
        brecha = Decimal('0.00')
        if m_avg > 0:
            brecha = (m_avg - f_avg) / m_avg * 100

        rows.append({
            'category_id': str(cat.id),
            'category_code': cat.code,
            'category_name': cat.name,
            'group_male': {'count': len(male), 'avg_salary': m_avg},
            'group_female': {'count': len(female), 'avg_salary': f_avg},
            'brecha_pct': brecha,
            'alert': abs(brecha) > Decimal('5.00'),
        })
    return rows
```

Tests (in apps/compensation/tests/test_audit_service.py):
- No employees → 0 brecha, no alert.
- Equal salaries → 0 brecha.
- 11% brecha → alert True.
- Negative brecha (women earn more) → alert True too (absolute > 5).
- Cross-tenant isolation.

Commit:
```
feat(B7): salary-gap audit service per Ley 30709 § 8
```

---

## Task 7: Excel import + template export service

**Files:**
- `apps/api/apps/compensation/services/ccf_excel_service.py`

Two functions:
1. `export_template()` — returns BytesIO with .xlsx header row matching expected format.
2. `import_ccf(*, file, tenant, ccf_title, user)` — parses uploaded xlsx, validates rows, creates CCF + Category + SalaryBand + CategoryFactorScore atomically.

Column schema:
- `code` (str, required)
- `name` (str, required)
- `description` (str)
- `min_education` (str)
- `min_experience_years` (int)
- `salary_min` (decimal)
- `salary_mid` (decimal)
- `salary_max` (decimal)
- `factor_<subfactor_code>` (int) — one column per subfactor; matches seeded JobSubfactor rows.

Errors per row collected and returned (does not partial-commit). Either full success or rollback.

Tests (in apps/compensation/tests/test_excel_service.py):
- Template export contains expected headers.
- Valid import creates CCF + N Categories + SalaryBand + scores.
- Invalid row (negative score) → no commit, error list returned.
- Tenant isolation enforced.

Commit:
```
feat(B7): Excel template export + bulk CCF import service
```

---

## Task 8: API ViewSets + serializers + URL routing

**Files:**
- `apps/api/api/v1/compensation/__init__.py`
- `apps/api/api/v1/compensation/serializers.py`
- `apps/api/api/v1/compensation/views.py`
- `apps/api/api/v1/compensation/urls.py`
- `apps/api/api/v1/urls.py` (register `compensation/`)

ViewSets:
- `JobFactorViewSet` — read-only, system-wide.
- `JobSubfactorViewSet` — read-only, system-wide, filterable by factor.
- `CategoryFunctionTableViewSet` — TenantAwareViewSetMixin + RRHHPermission. Custom action `approve` (changes status → approved, sets approved_at + approved_by).
- `CategoryViewSet` — TenantAwareViewSetMixin + RRHHPermission. Custom action `recompute_total` (calls scoring_service).
- `SalaryBandViewSet` — TenantAwareViewSetMixin + RRHHPermission. Nested under Category.
- `CategoryFactorScoreViewSet` — TenantAwareViewSetMixin + RRHHPermission.

Custom endpoints:
- `GET /api/v1/compensation/audit/salary-gap/?ccf_id=<uuid>` — calls audit service, returns gap report.
- `GET /api/v1/compensation/ccf/template-excel/` — emits the import template xlsx.
- `POST /api/v1/compensation/ccf/import-excel/` — multipart upload; calls import service.

Tests: routing smoke + auth gating + smoke on each custom endpoint.

Commit:
```
feat(B7): API surface for CCF + audit + Excel import
```

---

## Task 9: Frontend service + types

**Files:**
- `apps/web/src/features/compensation/services/ccfService.ts` (new feature folder)
- `apps/web/src/features/compensation/services/index.ts`
- `apps/web/src/features/compensation/index.ts`

`ccfService.ts` exposes:
- `listCCFs()`, `getCCF(id)`, `createCCF(...)`, `approveCCF(id)`.
- `listCategories(ccfId)`, `createCategory(...)`, `updateCategory(...)`, `recomputeTotal(id)`.
- `listSalaryBands()`, `upsertSalaryBand(categoryId, band)`.
- `listFactors()`, `listSubfactors(factorId)`.
- `getSalaryGapAudit(ccfId)`.
- `downloadTemplate()` (blob).
- `uploadCCFExcel(file, ccfTitle)`.

Tests (apps/web/src/features/compensation/services/__tests__/ccfService.test.ts): 6+ vitest unit tests for service shape.

Commit:
```
feat(B7): frontend CCF service + types
```

---

## Task 10: Frontend CCF admin pages

**Files:**
- `apps/web/src/features/compensation/pages/CCFListPage.tsx` — list of CCFs (status, version, effective_date), create button.
- `apps/web/src/features/compensation/pages/CCFEditorPage.tsx` — edit CCF metadata + categories + scores; tabs for Categories / Salary Bands / Audit / Excel Import.
- `apps/web/src/features/compensation/components/CategoryFormModal.tsx` — modal form for Category + factor scores + salary band.
- `apps/web/src/features/compensation/components/SalaryGapAuditPanel.tsx` — table of categories with brecha %, alert badge when > 5%.
- `apps/web/src/features/compensation/components/CCFExcelImporter.tsx` — drop zone + template download + import button + error report.

UI sector gate: top-level component returns `null` when `useTenant().sector === 'public'`. Menu entry hidden via the same hook.

Route in App.tsx: `/compensacion/ccf` → CCFListPage (for HR users only via AdminRoute).

Vitest snapshot tests for SalaryGapAuditPanel + CCFExcelImporter (rendering with sample data).

Commit:
```
feat(B7): frontend CCF admin pages (sector-gated)
```

---

## Task 11: Final verification + close-out

- Capture final baselines:
  - pytest (target: ≥415 passing).
  - vitest (target: 10+ files passing).
  - ESLint (target: 278 ± 3).
  - tsc 1 preserved.
  - Build clean.
  - manage.py check 0 silenced.
- Curl smoke:
  - `GET /api/v1/compensation/job-factors/` (200 with HR auth).
  - `GET /api/v1/compensation/audit/salary-gap/` (200 empty when no data).
- Update memory pointer + test_baselines.
- Merge to master.

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 105 | CCF — Ley 30709 compliance | Tasks 2-4, 6 |
| 106 | SalaryBand + análisis brechas + import Excel | Tasks 4, 6, 7 |
| ADR-B.6 sector gating | UI-only gate via useTenant() (per user) | Task 10 |
| ADR-B.7 versioning | CCF uses same pattern (version + parent_version + status) | Task 3 |
| Maestro § 5.3 brecha audit | Audit service + endpoint + UI panel | Tasks 6, 8, 10 |
| Maestro § 5.4 importación masiva | Excel template + bulk import service + endpoint + UI | Tasks 7, 8, 10 |

Coverage: 2 of 2 in-scope items + 4 architectural decisions applied.

**Deferred to other phases (per user/plan):**
- PoliticaSalarial → B.15.
- Dashboard equidad salarial → B.12.
- Reclamos por discriminación → independent channel.
- Plan de nivelación automático → B.7.1.
- Capacitación obligatoria → M05.
- Aviso al trabajador (PDF) → B.7.1.
