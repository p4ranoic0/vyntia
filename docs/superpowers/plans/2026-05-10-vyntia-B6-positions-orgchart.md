# B.6 Positions + OrgChart Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 02 (Organización del Trabajo y Distribución) — introduce Position catalog, position profiles, occupational classifications (Tabla 9/10 SUNAT), Plaza assignment workflow, and the OrgChart UI. Preserve legacy `cargo` string fields alongside new FK references (nullable, deferred backfill).

**Architecture:** New `apps/organization/` models for the position domain. `Department` model extended with `unit_type` + `cost_center` (treated as the canonical OrgUnit). `EmploymentData.position` and `ContractAmendment.new_position` FK columns added nullable beside legacy `cargo` strings. New ViewSets at `/api/v1/organization/{positions,position-profiles,occupational-categories,ciuo-codes,plazas,position-risk-profiles}/`. Frontend OrgChart at `/organizacion/orgchart` powered by `@xyflow/react` with dagre auto-layout, lazy-loaded route. Per-tenant data via TenantAwareViewSetMixin (B.1). Position versioning per ADR-B.7 (inline `version: int` + `parent: FK self`).

**Branch:** `vyntia/B6-positions-orgchart`
**Backlog items in scope:** #102 (7 models — implemented as 6 new + extended Department), #103 (OrgChart UI viewer + editor), #104 (cargo FK migration, nullable + defer backfill per user decision).
**Scope decisions (user-confirmed 2026-05-10):**
- Single B.6 PR per roadmap (~2 weeks).
- Cargo migration: add FK alongside as nullable, defer backfill (no auto-create or mapping CSV).
- OrgChart UI: full viewer + drag-drop editor per ADR-B.8.

**Out of scope (deferred to B.7/B.8/post-B):**
- CCF (CategoryFunctionTable) + SalaryBand + Ley 30709 compliance → B.7
- MPP + CPE + CAP → B.8
- Cargo data backfill scripts per tenant → operational task post-merge
- PDF export of orgchart → browser print sufficient; polished PDF in B.6.1 if requested
- Bulk import from Excel → B.6.1 follow-up

**Test baselines (post-B.5b SHA `0059cd7f`):**
- pytest 365/1/17, vitest 7/32, ESLint 277, tsc 1 (BlankEnum), build clean, manage.py check 0 silenced.

After B.6:
- pytest **380+/1/17** (~15+ new tests for 6 models + Position versioning + Plaza lifecycle + viewset smoke).
- vitest **8+ files / 35+ tests** (new OrgChart component tests).
- ESLint: held flat (new code must lint clean).
- Bundle: ~150 KB additional gzipped on `/organizacion/orgchart` route (lazy-loaded, no impact elsewhere).

---

## Task 1: Branch + plan + scaffold

```bash
cd D:/VYNTIA
git checkout -b vyntia/B6-positions-orgchart    # already done
git add docs/superpowers/plans/2026-05-10-vyntia-B6-positions-orgchart.md
git commit -m "docs(B6): plan for Position + OrgChart (Module 02, 3 backlog items in scope)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

Capture baselines: pytest 365/1/17, ESLint 277, tsc 1, bundle size.

---

## Task 2: Extend `Department` with `unit_type` + `cost_center` (OrgUnit fold-in)

**File:** `apps/api/apps/organization/models/department.py`

Add two fields:
- `unit_type` — CharField choices: DIRECCION, GERENCIA, SUBGERENCIA, OFICINA, AREA, EQUIPO. Default 'AREA' (matches legacy assumption).
- `cost_center` — CharField nullable, max_length=50, indexed.

Plus DB index on `unit_type`.

Rationale: Department already has `area_padre` (parent FK) and `nivel_jerarquico` (depth). Adding `unit_type` + `cost_center` makes it the canonical OrgUnit per Maestro § 2.1 without a duplicate model. Saves a JOIN and avoids data migration complexity.

**Migration:** `apps/api/apps/organization/migrations/0003_orgunit_fields.py` — both fields nullable. No backfill (legacy areas inherit `unit_type='AREA'` via default).

Commit:
```
feat(B6): extend Department with unit_type + cost_center (folds OrgUnit concept)
```

---

## Task 3: Create OccupationalCategory + CIUOCode reference models (SUNAT Tabla 9/10)

**Files:**
- `apps/api/apps/organization/models/occupational_category.py` — Tabla 10 SUNAT
- `apps/api/apps/organization/models/ciuo_code.py` — Tabla 9 SUNAT (CIUO-08 OIT)
- `apps/api/apps/organization/management/commands/seed_occupational_data.py` — idempotent seeder

**OccupationalCategory (Tabla 10 SUNAT):**
```python
class OccupationalCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=4, unique=True)  # SUNAT code
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'occupational_category'
        ordering = ['code']
```

Seed: 3 rows (ejecutivo, empleado, obrero).

**CIUOCode (Tabla 9 SUNAT — CIUO-08 OIT):**
```python
class CIUOCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=4, unique=True)  # 4-digit CIUO-08
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    big_group = models.CharField(max_length=100, blank=True)  # CIUO-08 main group
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'ciuo_code'
        ordering = ['code']
        indexes = [models.Index(fields=['big_group'])]
```

Seed: top ~80 CIUO-08 codes commonly used in Peru. Source: SUNAT Tabla 9 published list, embedded as a Python tuple of `(code, name, big_group)` in the seeder. Not a full ~430 codes — pragmatic subset; expand-as-needed in B.6.1.

Both are **system-wide** (no tenant FK) — these are SUNAT reference data shared across all tenants. Read-only via admin and API.

Tests:
- Smoke: create both models, seed runs without error.
- Idempotency: seed twice → same row count.

Commit:
```
feat(B6): OccupationalCategory + CIUOCode reference models (SUNAT Tabla 9/10)
```

---

## Task 4: Create Position model with ADR-B.7 versioning

**File:** `apps/api/apps/organization/models/position.py`

```python
class Position(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    # Identity
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=200)

    # Versioning (ADR-B.7)
    version = models.PositiveIntegerField(default=1)
    parent_version = models.ForeignKey('self', on_delete=models.PROTECT,
                                        null=True, blank=True, related_name='successors')
    effective_date = models.DateField()
    is_current = models.BooleanField(default=True, db_index=True)

    # Classification
    department = models.ForeignKey('organization.Department',
                                    on_delete=models.PROTECT,
                                    related_name='positions')
    occupational_category = models.ForeignKey(
        'organization.OccupationalCategory', on_delete=models.PROTECT,
        null=True, blank=True
    )
    ciuo_code = models.ForeignKey('organization.CIUOCode',
                                   on_delete=models.PROTECT,
                                   null=True, blank=True)

    # Reporting line
    reports_to = models.ForeignKey('self', on_delete=models.PROTECT,
                                    null=True, blank=True, related_name='direct_reports')

    # Lifecycle
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'position'
        indexes = [
            models.Index(fields=['tenant', 'code']),
            models.Index(fields=['tenant', 'is_current']),
            models.Index(fields=['department']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code', 'version'],
                name='unique_position_code_version_per_tenant',
            ),
        ]

    def create_new_version(self, **changes) -> 'Position':
        """Create a new version of this Position with the given field changes.
        Marks the current version as NOT current; new version becomes current.
        Atomic via transaction.atomic() in the caller (service layer).
        """
        new = Position(
            tenant=self.tenant,
            code=self.code,
            name=self.name,
            version=self.version + 1,
            parent_version=self,
            effective_date=changes.pop('effective_date', timezone.now().date()),
            is_current=True,
            department=self.department,
            occupational_category=self.occupational_category,
            ciuo_code=self.ciuo_code,
            reports_to=self.reports_to,
            is_active=True,
        )
        for k, v in changes.items():
            setattr(new, k, v)
        self.is_current = False
        self.save(update_fields=['is_current'])
        new.save()
        return new
```

Versioned fields (changing them triggers `create_new_version`): name, department, occupational_category, ciuo_code, reports_to. Non-versioned fields (typo fixes, code rename) update in place. The ViewSet enforces this distinction.

**Migration:** `0004_position.py`.

Tests (apps/organization/tests/test_position.py):
- Smoke create + retrieve.
- `create_new_version` increments version, links parent, flips `is_current`.
- Tenant scoping: cross-tenant Position lookup blocked.

Commit:
```
feat(B6): Position model with versioning per ADR-B.7
```

---

## Task 5: Create PositionProfile model + sub-models

**Files:**
- `apps/api/apps/organization/models/position_profile.py`
- `apps/api/apps/organization/models/position_function.py`
- `apps/api/apps/organization/models/position_requirement.py`

**PositionProfile** is 1-to-1 with Position. Contains free-text mission and lists of competencies (JSON since they're tag-like). Education/experience requirements are structured (sub-model rows).

```python
class PositionProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.OneToOneField('organization.Position',
                                     on_delete=models.CASCADE,
                                     related_name='profile')
    mission = models.TextField(blank=True)
    technical_competencies = models.JSONField(default=list, blank=True)  # list of strings
    soft_competencies = models.JSONField(default=list, blank=True)
    work_conditions = models.TextField(blank=True)  # jornada, viajes, lugar
    kpis = models.JSONField(default=list, blank=True)  # list of strings

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PositionFunction(models.Model):
    """List-shape model so functions are queryable and orderable."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey('organization.Position',
                                  on_delete=models.CASCADE,
                                  related_name='functions')
    description = models.TextField()
    is_primary = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class PositionRequirement(models.Model):
    KIND_CHOICES = [
        ('education', 'Educación'),
        ('experience', 'Experiencia'),
        ('language', 'Idioma'),
        ('certification', 'Certificación'),
        ('other', 'Otro'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.ForeignKey('organization.Position',
                                  on_delete=models.CASCADE,
                                  related_name='requirements')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    description = models.CharField(max_length=300)
    is_required = models.BooleanField(default=True)
```

Migrations: `0005_position_profile.py`.

Tests: smoke create + cascade delete (deleting Position deletes profile + functions + requirements).

Commit:
```
feat(B6): PositionProfile + PositionFunction + PositionRequirement
```

---

## Task 6: Create Plaza model (assignment workflow)

**File:** `apps/api/apps/organization/models/plaza.py`

```python
class Plaza(models.Model):
    STATUS_CHOICES = [
        ('vacante', 'Vacante'),
        ('ocupada', 'Ocupada'),
        ('congelada', 'Congelada'),
        ('eliminada', 'Eliminada'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.PROTECT,
                                null=True, blank=True, db_index=True, related_name='+')

    code = models.CharField(max_length=30)  # plaza-specific identifier
    position = models.ForeignKey('organization.Position',
                                  on_delete=models.PROTECT,
                                  related_name='plazas')
    current_employee = models.ForeignKey('employees.Employee',
                                          on_delete=models.SET_NULL,
                                          null=True, blank=True,
                                          related_name='plazas')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacante',
                              db_index=True)

    # Lifecycle metadata
    opened_at = models.DateField(null=True, blank=True)
    closed_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plaza'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['position', 'status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_plaza_code_per_tenant',
            ),
        ]

    def occupy(self, employee):
        """Assign an employee — moves to OCUPADA."""
        if self.status not in ('vacante', 'congelada'):
            raise ValidationError(f"No se puede ocupar una plaza con estado {self.status}")
        self.current_employee = employee
        self.status = 'ocupada'
        self.save(update_fields=['current_employee', 'status', 'updated_at'])

    def vacate(self):
        """Unassign — moves to VACANTE."""
        self.current_employee = None
        self.status = 'vacante'
        self.save(update_fields=['current_employee', 'status', 'updated_at'])
```

Migration: `0006_plaza.py`.

Tests:
- Occupy/vacate transitions.
- Cannot occupy when ELIMINADA or already OCUPADA without vacate first.
- Tenant scoping.

Commit:
```
feat(B6): Plaza model + assignment workflow
```

---

## Task 7: Create PositionRiskProfile (SST stub)

**File:** `apps/api/apps/organization/models/position_risk_profile.py`

```python
class PositionRiskProfile(models.Model):
    """SST-bound risk profile for a Position. Stub model in B.6 — full risk
    catalog comes with the SST module (M07, scope post-B Core)."""

    LEVEL_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('very_high', 'Muy alto'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    position = models.OneToOneField('organization.Position',
                                     on_delete=models.CASCADE,
                                     related_name='risk_profile')
    overall_level = models.CharField(max_length=20, choices=LEVEL_CHOICES,
                                      default='low')
    risk_factors = models.JSONField(default=list, blank=True)  # placeholder for SST detail
    notes = models.TextField(blank=True)
    requires_medical_exam = models.BooleanField(default=False)
    requires_iperc = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Migration: `0007_position_risk_profile.py`.

Commit:
```
feat(B6): PositionRiskProfile (SST stub model)
```

---

## Task 8: EmploymentData.position + ContractAmendment.new_position FK (nullable, defer backfill)

**Files:**
- `apps/api/apps/contracts/models/employment_data.py`
- `apps/api/apps/contracts/models/contract_amendment.py`

Add `position` FK to Position (nullable, on_delete=SET_NULL). Preserve legacy `cargo_empleado` and `nuevo_cargo` strings unchanged. No data backfill in this migration — operational task per user decision.

```python
# employment_data.py
position = models.ForeignKey(
    'organization.Position',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='employment_records',
    help_text='Catalog position FK (post-B.6). Legacy cargo_empleado preserved.',
)
```

```python
# contract_amendment.py — for ADENDA_CARGO
new_position = models.ForeignKey(
    'organization.Position',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='cargo_amendments',
    help_text='New position FK (post-B.6). Legacy nuevo_cargo preserved.',
)
```

Add `position` to admin / serializer Meta.fields (optional read).

Migrations: `apps/contracts/migrations/0003_employment_data_position.py` + `0004_contract_amendment_new_position.py`.

**No tests added here** — these are pure schema additions covered by the model tests in Task 4.

Commit:
```
feat(B6): EmploymentData.position + ContractAmendment.new_position FK (nullable, backfill deferred)
```

---

## Task 9: ViewSets, serializers, URL routing for the 6 new models

**Files:**
- `apps/api/api/v1/organization/views.py` — extend existing module with 6 new ViewSets
- `apps/api/api/v1/organization/serializers.py` — new file (organization currently lives in rrhh/)
- `apps/api/api/v1/organization/urls.py` — extend with new routes

Pattern: each ViewSet inherits `TenantAwareViewSetMixin` (B.1), declares `queryset`, `serializer_class`, `filter_backends`, `search_fields`, `ordering_fields`. Read-write for HR; read-only for employees (per RRHHPermission).

ViewSets:
- `PositionViewSet` — full CRUD + custom `@action` `new_version` (creates new version per ADR-B.7).
- `PositionProfileViewSet` — full CRUD; nested under Position.
- `OccupationalCategoryViewSet` — list/retrieve only (SUNAT reference data, system-wide, no tenant filter).
- `CIUOCodeViewSet` — list/retrieve only (system-wide).
- `PlazaViewSet` — full CRUD + custom actions `occupy` (POST `/plazas/<id>/occupy/`), `vacate` (POST `/plazas/<id>/vacate/`).
- `PositionRiskProfileViewSet` — full CRUD; nested under Position.

URL prefixes (under `/api/v1/organization/`):
- `positions/` → PositionViewSet
- `positions/<id>/profile/` → PositionProfileViewSet (nested)
- `occupational-categories/` → OccupationalCategoryViewSet (system-wide)
- `ciuo-codes/` → CIUOCodeViewSet (system-wide)
- `plazas/` → PlazaViewSet
- `positions/<id>/risk-profile/` → PositionRiskProfileViewSet (nested)

Tests:
- 4 routing smoke tests (each new endpoint returns 401 unauthenticated, 200 with HR token, etc.).
- 1 versioning test on PositionViewSet.new_version action.
- 1 Plaza lifecycle test (occupy → vacate via API).

Commit:
```
feat(B6): API surface for Position/Plaza/profiles/risk + SUNAT reference catalogs
```

---

## Task 10: Frontend dependencies + lazy-loaded OrgChart route skeleton

**Files:**
- `apps/web/package.json` — add `@xyflow/react@^12` + `dagre@^0.8`
- `apps/web/src/features/organization/pages/OrgChartPage.tsx` (new)
- `apps/web/src/features/organization/components/OrgChartCanvas.tsx` (new, contains the actual `@xyflow/react` usage)
- `apps/web/src/features/organization/components/OrgChartNodes.tsx` (custom DepartmentNode, PositionNode, EmployeeNode)
- `apps/web/src/features/organization/services/orgchartService.ts` (new, calls `/api/v1/organization/positions/`, `/plazas/`, etc.)
- `apps/web/src/App.tsx` — register lazy route `/organizacion/orgchart`

```bash
cd D:/VYNTIA/apps/web
npm install @xyflow/react@^12 dagre@^0.8
npm install --save-dev @types/dagre
```

Lazy load:
```tsx
const OrgChartPage = lazy(() => import('@/features/organization/pages/OrgChartPage'))
```

Initial commit ships skeleton + lazy boundary + 401-tolerant data fetch. Real canvas in Task 11.

Commit:
```
feat(B6): install @xyflow/react + dagre, scaffold lazy OrgChart route
```

---

## Task 11: OrgChart canvas — viewer + drag-drop editor

**File:** `apps/web/src/features/organization/components/OrgChartCanvas.tsx`

Pattern:
- Fetch Departments + Positions + Plazas via `orgchartService` (React Query, paginated, server-side).
- Build nodes/edges from the data: Department nodes (top-level), Position child nodes (below Department), Employee child nodes (below occupied Plaza).
- Use `dagre` for auto-layout (hierarchical, top-down).
- Custom node components (DepartmentNode, PositionNode, EmployeeNode) — Tailwind-styled cards.
- Read-only mode by default (employees see view-only).
- HR users (per `useAuth`) get drag-drop:
  - Dragging a Department node onto another Department reparents (calls `PATCH /api/v1/organization/departments/<id>/` with new `area_padre`).
  - Dragging a Position node onto a Department changes the position's department.
  - Dragging an Employee node onto another Plaza vacates source + occupies target (atomic via 2 API calls or new bulk endpoint).
- Search bar: filters visible nodes by name match.
- Minimap, zoom controls (built-in from `@xyflow/react`).
- Lazy-loaded — initial bundle impact bounded to /organizacion/orgchart route.

Tests (apps/web/src/features/organization/components/__tests__/OrgChartCanvas.test.tsx):
- Renders Department + Position + Employee nodes with sample data.
- Drag handler called with correct (sourceId, targetId) — mocked drop.
- Read-only mode hides drag affordances.

Commit:
```
feat(B6): OrgChart canvas with @xyflow/react viewer + drag-drop editor
```

---

## Task 12: Final verification + close-out

- Run all baselines:
  - pytest (target: ≥380 passing).
  - vitest (target: 8+ files passing).
  - ESLint (target: 277 or less).
  - tsc (1 BlankEnum preserved).
  - Vite build clean (with bundle size split visible).
  - manage.py check (0 silenced).
- Curl smoke check:
  - `GET /api/v1/organization/positions/` (401 unauth, 200 auth).
  - `GET /api/v1/organization/occupational-categories/` (seeded data visible).
  - `GET /api/v1/organization/ciuo-codes/` (seeded data visible).
- Update memory pointer to mark B.6 complete.
- Optional: capture before/after lighthouse score on /organizacion/orgchart (for follow-up perf work).

---

## Self-Review

| # | Item | Task |
|---|---|---|
| 102 | Position + PositionProfile + OrgUnit + Plaza + RiskProfile + CIUOCode + OccupationalCategory | Tasks 2-7 (OrgUnit folded into Department per pragmatic design) |
| 103 | OrgChart UI (drag-drop, parent-child, search, PDF export) | Tasks 10-11 (PDF deferred to browser print; can add jspdf in B.6.1) |
| 104 | Migration EmploymentData.cargo (string) → EmploymentData.position (FK) | Task 8 (FK added nullable; backfill deferred per user) |
| ADR-B.6 | Sector gating (private vs public) | Visible in Position model: `tenant` FK exposes `sector` via Tenant.sector. UI branches via useTenant() — no in-Position field |
| ADR-B.7 | Position versioning (inline `version` + `parent_version`) | Task 4 |
| ADR-B.8 | `@xyflow/react` org chart library | Tasks 10-11 |

Coverage: 3 of 3 in-scope items + 3 ADRs applied.

**Out of scope (deferred):**
- Cargo data backfill scripts → operational task per user decision (FK nullable; populate when ready)
- PDF export polish → browser print sufficient; jspdf integration in B.6.1 if requested
- Bulk Excel import → B.6.1
- CCF/SalaryBand → B.7
- MPP/CPE/CAP → B.8
- SST full risk catalog → M07 post-B Core
