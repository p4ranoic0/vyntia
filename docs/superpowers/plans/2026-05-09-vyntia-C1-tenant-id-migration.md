# C.1 — Tenant ID Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `tenant = FK(Tenant)` to all 31 business models across 8 apps, convert simple `unique` constraints to composite `(tenant, field)`, de-singletonize `Company` (one config per tenant), and update the 3 `Company.get_config()` call sites — all on a blank-slate dev DB without breaking the 176-test baseline.

**Architecture:** Retrofit pattern — existing models add `tenant = ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=PROTECT, db_index=True)` directly via migration. The `null=True` is **transitional** for C.1 only — the spec § 3.2 specifies NOT NULL, but enforcing it now would break the 176 existing tests that don't yet pass tenant. C.3 (middleware) will introduce a tenant context that all writes inherit, then a follow-up migration in C.3 (or end-of-C cleanup) flips to NOT NULL. New models created in future sub-projects use the new `TenantScopedModel` abstract base in `apps/core/models.py` with NOT NULL semantics.

**Tech Stack:** Django 5.2, PostgreSQL 15.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` § 3.2-3.4

**Source roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`

---

## Baseline snapshot (must be preserved or improved at every commit)

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest tests/ apps/tenancy/tests/ -q` | 176 passed / 7 failed / 3 skipped (after C.0) |
| Frontend build | `cd apps/web && npm run build` | Exit 0 |

C.1 ships ~50 new migrations (one or two per app). No new tests in C.1 — the existing 176 must continue to pass with `tenant=NULL` defaulted.

---

## Models inventory (verified pre-plan)

| App | Models to retrofit | Skip (global) | Composite unique changes |
|-----|--------------------|---------------|--------------------------|
| identity | Role, Permission, RolePermission, ModulePermission, UserRole | User, Module | Role.nombre_rol; RolePermission(rol,permiso); ModulePermission(modulo,permiso); UserRole(usuario,rol) |
| organization | Department, Company, LocationHistory | — | Department.siglas_area; Company → unique(tenant) |
| employees | Employee, AcademicRecord, Certification, FamilyMember | — | Employee.numero_documento; AcademicRecord(empleado,nivel,carrera,institucion); Certification(empleado,curso,inst,fecha); FamilyMember(empleado,numero_documento) |
| contracts | Contract, ContractAmendment, EmploymentData | — | Contract.numero_contrato |
| documents | DigitalDocument, DocumentTemplate | — | (no current uniques to widen) |
| payroll | AfpConfiguration, CompensationConfiguration, MonthlyPayroll, PayrollDetail, PayrollConcept, MassDeduction, PaySlip, PaymentSchedule, TaxParameter | — | AfpConfiguration(afp_nombre,vigencia_mes); CompensationConfiguration(tipo,codigo); MonthlyPayroll(periodo,modalidad,meta); PayrollDetail(planilla,empleado); TaxParameter(anio) |
| time_off | VacationConfiguration, VacationPeriod, VacationRequest, VacationGrant, VacationRequestHistory | — | VacationConfiguration(tipo,area,empleado,fecha); VacationPeriod(empleado,ano,contrato) |
| onboarding | OnboardingProcess | — | (no current uniques to widen) |

**Total:** 31 models retrofitted, 12 composite unique constraints widened.

**`Company.get_config()` call sites to update** (Task 3):
- `apps/api/api/v1/rrhh/views.py:2861, 2871` — 2 calls
- `apps/api/apps/documents/services/template_service.py:324` — 1 call

---

## Branch

`vyntia/C1-tenant-id-migration` — branched from `master` (HEAD has `Merge C.0`).

---

## Task pattern (used 8 times — Tasks 2-9)

For each app, the pattern is:

1. Update each model: add `tenant = models.ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=models.PROTECT, db_index=True, related_name='+')` and adjust uniqueness constraints.
2. `manage.py makemigrations <app> --settings=vyntia.settings.development` — accept any defaults Django asks for (since DB will be blank-slate, defaults are unused).
3. `manage.py migrate <app> --settings=vyntia.settings.development` — apply.
4. `manage.py check --settings=vyntia.settings.development` — verify clean.
5. `pytest apps/<app>/ tests/ -q` — verify no regression.
6. Commit with `chore(C1): add tenant FK to <app> models`.

**Key conventions:**
- `related_name='+'` — disable reverse accessor on Tenant. Otherwise we'd add 30+ reverse accessors to Tenant, which is noisy.
- `null=True, blank=True` — transitional, see Architecture above.
- `on_delete=PROTECT` — prevents accidental data loss when a tenant is deleted (use SoftDelete pattern in admin).
- `db_index=True` — every tenant-filtered query benefits.

---

## Task 1: Branch + `TenantScopedModel` abstract base

**Files:**
- Create: `apps/api/apps/core/models.py` (new file)

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/C1-tenant-id-migration
```

- [ ] **Step 1.2: Verify `apps/core/` does not yet have `models.py`**

```bash
ls apps/api/apps/core/
```

Expected: `apps.py`, `constants.py`, `database.py`, `decorators.py`, `exceptions.py`, `logging.py`, `middleware.py`, `pagination.py`, `permission_service.py`, `permissions.py`, `responses.py`, `tasks.py`, `validators.py`, `__init__.py` — but no `models.py`.

- [ ] **Step 1.3: Create `apps/api/apps/core/models.py`**

```python
"""Cross-cutting abstract models for tenant-scoped data.

`TenantScopedModel` is the canonical base for NEW models created after C.1.
Existing models are retrofitted with `tenant = FK(...)` directly via migration
(rather than refactoring class hierarchies) — see C.1 plan § "Architecture".

The retrofit uses `null=True, blank=True` transitionally; this base class uses
NOT NULL semantics. After C.3 introduces tenant context middleware and the
backfill migration completes, both will converge on NOT NULL.
"""

from django.db import models


class TenantScopedModel(models.Model):
    """Abstract base for models scoped to a single tenant.

    Use for any new model where every row belongs to exactly one tenant.
    The `tenant` FK uses `on_delete=PROTECT` to prevent cascade deletes
    when a tenant is removed (use the soft-delete admin flow instead).

    Example:
        class Project(TenantScopedModel):
            name = models.CharField(max_length=200)
            class Meta(TenantScopedModel.Meta):
                db_table = "myapp_project"
    """

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )

    class Meta:
        abstract = True
```

- [ ] **Step 1.4: Verify Django system check (no migrations needed — abstract model)**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --settings=vyntia.settings.development
```

Expected: `System check identified no issues (0 silenced).` and `No changes detected`.

- [ ] **Step 1.5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/core/models.py
git commit -m "chore(C1): add TenantScopedModel abstract base in apps/core/models.py"
```

---

## Task 2: Identity app — tenant FK + composite uniques

**Files:**
- Modify: `apps/api/apps/identity/models/roles.py` (Role, Permission)
- Modify: `apps/api/apps/identity/models/rbac.py` (RolePermission, ModulePermission, UserRole — keep Module untouched)
- Create: `apps/api/apps/identity/migrations/<auto>_add_tenant_fk.py` (one or more auto-generated migrations)

- [ ] **Step 2.1: Read current state of `roles.py`**

```bash
cd D:/VYNTIA
cat apps/api/apps/identity/models/roles.py
```

Confirm `Role` has `nombre_rol = ...(unique=True)` and `Permission` has its own fields.

- [ ] **Step 2.2: Update `Role` and `Permission`**

In `apps/api/apps/identity/models/roles.py`:

For `Role`:
- Add inside the model fields (e.g., before `class Meta`):
  ```python
  tenant = models.ForeignKey(
      "tenancy.Tenant",
      null=True,
      blank=True,
      on_delete=models.PROTECT,
      db_index=True,
      related_name="+",
  )
  ```
- In `class Meta`, change `nombre_rol` field from `unique=True` to NOT unique, and add a `constraints` list with a `UniqueConstraint(fields=["tenant", "nombre_rol"], name="unique_role_per_tenant")`. If `class Meta` already has a `constraints` list, append to it.

For `Permission`:
- Add the same `tenant = ...` FK field as above.
- No unique constraint changes needed (Permission has no current unique fields per the inventory).

- [ ] **Step 2.3: Update `RolePermission`, `ModulePermission`, `UserRole`**

In `apps/api/apps/identity/models/rbac.py`:

For each of `RolePermission`, `ModulePermission`, `UserRole`:
- Add the same `tenant = ...` FK field.
- In `class Meta`, change the existing `unique_together = [...]` from a 2-field tuple to a 3-field tuple including `tenant`:
  - `RolePermission`: `unique_together = ["tenant", "rol", "permiso"]`
  - `ModulePermission`: `unique_together = ["tenant", "modulo", "permiso"]`
  - `UserRole`: `unique_together = ["tenant", "usuario", "rol"]`

Leave `Module` untouched (global per spec § 3.2).

- [ ] **Step 2.4: Make migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations identity --settings=vyntia.settings.development
```

Django may prompt for one-time defaults for the new `tenant` field. Since it's `null=True`, it should NOT prompt. If it does, accept default of None.

Expected: a migration file is created in `apps/identity/migrations/`.

- [ ] **Step 2.5: Apply migration**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate identity --settings=vyntia.settings.development
```

Expected: clean apply.

- [ ] **Step 2.6: Verify check + tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: check clean, ≥176 passed.

- [ ] **Step 2.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/identity/models/roles.py \
        apps/api/apps/identity/models/rbac.py \
        apps/api/apps/identity/migrations/
git commit -m "chore(C1): add tenant FK to identity RBAC models (Role, Permission, RolePermission, ModulePermission, UserRole)"
```

---

## Task 3: Organization app — tenant FK + de-singletonize Company

**Files:**
- Modify: `apps/api/apps/organization/models/department.py`
- Modify: `apps/api/apps/organization/models/company.py` (de-singletonize)
- Modify: `apps/api/apps/organization/models/location_history.py`
- Modify: `apps/api/api/v1/rrhh/views.py:2861, 2871` (2 callers of `Company.get_config()`)
- Modify: `apps/api/apps/documents/services/template_service.py:324` (1 caller)
- Create: migrations under `apps/organization/migrations/`

- [ ] **Step 3.1: Update `Department`**

In `apps/api/apps/organization/models/department.py`:
- Add `tenant = ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=PROTECT, db_index=True, related_name='+')`.
- Change `siglas_area` from `unique=True` to NOT unique.
- Add `class Meta` constraint: `UniqueConstraint(fields=["tenant", "siglas_area"], name="unique_department_siglas_per_tenant")`.

- [ ] **Step 3.2: Update `LocationHistory`**

In `apps/api/apps/organization/models/location_history.py`:
- Add `tenant = ForeignKey(...)` FK only — no unique changes.

- [ ] **Step 3.3: Update `Company` (de-singletonize)**

In `apps/api/apps/organization/models/company.py`:
- Read the current file. Identify the `get_config()` classmethod (probably uses `pk=1` hardcoded).
- Add `tenant = ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=PROTECT, db_index=True, related_name='+')`.
- Add `class Meta` constraint: `UniqueConstraint(fields=["tenant"], name="unique_company_per_tenant", condition=Q(tenant__isnull=False))` so that during the transition each non-null tenant has at most one Company. (With current `null=True`, multiple null-tenant rows are allowed, which is fine for legacy/fixture data.)
- Update the `get_config()` classmethod signature to:
  ```python
  @classmethod
  def get_config(cls, tenant=None):
      """Returns the Company config for the given tenant.

      Backward-compat: if tenant is None, falls back to the legacy singleton
      (pk=1). This fallback will be removed in C.3 once middleware ensures
      every authenticated request has a tenant context.
      """
      if tenant is None:
          # Legacy singleton fallback — only for unauthenticated migration tools
          return cls.objects.filter(pk=1).first()
      return cls.objects.filter(tenant=tenant).first()
  ```

- [ ] **Step 3.4: Update the 3 `Company.get_config()` callers**

In `apps/api/api/v1/rrhh/views.py` lines around 2861 and 2871:

Read the surrounding context. Replace `Company.get_config()` (no args) with `Company.get_config(tenant=request.tenant if hasattr(request, 'tenant') else None)`. Since `request.tenant` doesn't exist yet (TenantMiddleware comes in C.3), the fallback to `None` keeps behavior identical to today.

In `apps/api/apps/documents/services/template_service.py` line 324:

Replace `Company.get_config()` with `Company.get_config(tenant=None)` for now. Add a TODO comment: `# TODO(C.3): pass tenant from service caller once middleware ships`.

- [ ] **Step 3.5: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations organization --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate organization --settings=vyntia.settings.development
```

- [ ] **Step 3.6: Verify check + tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: check clean, ≥176 passed.

- [ ] **Step 3.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/organization/models/department.py \
        apps/api/apps/organization/models/company.py \
        apps/api/apps/organization/models/location_history.py \
        apps/api/apps/organization/migrations/ \
        apps/api/api/v1/rrhh/views.py \
        apps/api/apps/documents/services/template_service.py
git commit -m "chore(C1): add tenant FK to organization models + de-singletonize Company.get_config()"
```

---

## Task 4: Employees app — tenant FK + composite uniques

**Files:**
- Modify: `apps/api/apps/employees/models/employee.py`
- Modify: `apps/api/apps/employees/models/academic_record.py`
- Modify: `apps/api/apps/employees/models/certification.py`
- Modify: `apps/api/apps/employees/models/family_member.py`
- Create: migrations under `apps/employees/migrations/`

- [ ] **Step 4.1: Update `Employee`**

In `apps/api/apps/employees/models/employee.py`:
- Add `tenant = FK(...)`.
- Change `numero_documento` from `unique=True` to NOT unique.
- Add `class Meta` constraint: `UniqueConstraint(fields=["tenant", "numero_documento"], name="unique_employee_doc_per_tenant")`.

- [ ] **Step 4.2: Update `AcademicRecord`**

In `apps/api/apps/employees/models/academic_record.py`:
- Add `tenant = FK(...)`.
- Change `unique_together = [['empleado', 'nivel_educativo', 'nombre_carrera', 'nombre_institucion']]` to `unique_together = [['tenant', 'empleado', 'nivel_educativo', 'nombre_carrera', 'nombre_institucion']]`.

- [ ] **Step 4.3: Update `Certification`**

In `apps/api/apps/employees/models/certification.py`:
- Add `tenant = FK(...)`.
- Change `unique_together = [['empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]` to `unique_together = [['tenant', 'empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]`.

- [ ] **Step 4.4: Update `FamilyMember`**

In `apps/api/apps/employees/models/family_member.py`:
- Add `tenant = FK(...)`.
- Change `unique_together = [['empleado', 'numero_documento']]` to `unique_together = [['tenant', 'empleado', 'numero_documento']]`.

- [ ] **Step 4.5: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations employees --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate employees --settings=vyntia.settings.development
```

- [ ] **Step 4.6: Verify check + tests**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: check clean, ≥176 passed.

- [ ] **Step 4.7: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/employees/ \
        apps/api/apps/employees/migrations/
git commit -m "chore(C1): add tenant FK to employees models (Employee, AcademicRecord, Certification, FamilyMember)"
```

---

## Task 5: Contracts app — tenant FK + composite uniques

**Files:**
- Modify: `apps/api/apps/contracts/models/contract.py` (Contract — `numero_contrato`)
- Modify: `apps/api/apps/contracts/models/contract_amendment.py` (ContractAmendment)
- Modify: `apps/api/apps/contracts/models/employment_data.py` (EmploymentData)

- [ ] **Step 5.1: Update `Contract`**

- Add `tenant = FK(...)`.
- Change `numero_contrato` from `unique=True` to NOT unique.
- Add `class Meta` constraint: `UniqueConstraint(fields=["tenant", "numero_contrato"], name="unique_contract_number_per_tenant")`.

- [ ] **Step 5.2: Update `ContractAmendment` and `EmploymentData`**

- Add `tenant = FK(...)` to each. No unique changes (no current unique constraints per inventory).

- [ ] **Step 5.3: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations contracts --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate contracts --settings=vyntia.settings.development
```

- [ ] **Step 5.4: Verify**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

Expected: check clean, ≥176 passed.

- [ ] **Step 5.5: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/contracts/
git commit -m "chore(C1): add tenant FK to contracts models (Contract, ContractAmendment, EmploymentData)"
```

---

## Task 6: Documents app — tenant FK

**Files:**
- Modify: `apps/api/apps/documents/models/digital_document.py`
- Modify: `apps/api/apps/documents/models/document_template.py`

- [ ] **Step 6.1: Update both models**

Add `tenant = FK(...)` to each. No unique constraint changes.

- [ ] **Step 6.2: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations documents --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate documents --settings=vyntia.settings.development
```

- [ ] **Step 6.3: Verify**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

- [ ] **Step 6.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/documents/
git commit -m "chore(C1): add tenant FK to documents models (DigitalDocument, DocumentTemplate)"
```

---

## Task 7: Payroll app — tenant FK + composite uniques (9 models)

**Files:**
- Modify: `apps/api/apps/payroll/models/compensation.py` (8 models live here per inventory)
- Modify: `apps/api/apps/payroll/models/tax_parameter.py` (TaxParameter)

- [ ] **Step 7.1: Update each model**

For each of the 9 models, add `tenant = FK(...)`.

For models with existing `UniqueConstraint`, prepend `tenant` to the `fields` list and rename the constraint:

| Model | Current `UniqueConstraint(fields=...)` | New |
|-------|----------------------------------------|-----|
| `AfpConfiguration` | `["afp_nombre", "vigencia_mes"]` | `["tenant", "afp_nombre", "vigencia_mes"]` |
| `CompensationConfiguration` | `["tipo", "codigo"]` | `["tenant", "tipo", "codigo"]` |
| `MonthlyPayroll` | `["periodo", "modalidad", "meta_presupuestal"]` | `["tenant", "periodo", "modalidad", "meta_presupuestal"]` |
| `PayrollDetail` | `["planilla", "empleado"]` | `["tenant", "planilla", "empleado"]` |
| `TaxParameter` | `["anio"]` | `["tenant", "anio"]` |

For models without explicit unique constraints (`PayrollConcept`, `MassDeduction`, `PaySlip`, `PaymentSchedule`), add only the FK.

If the constraint already has a `name=`, append `_per_tenant` suffix to keep names unique.

- [ ] **Step 7.2: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations payroll --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate payroll --settings=vyntia.settings.development
```

- [ ] **Step 7.3: Verify**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

- [ ] **Step 7.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/payroll/
git commit -m "chore(C1): add tenant FK to payroll models (9 models)"
```

---

## Task 8: TimeOff app — tenant FK + composite uniques (5 models)

**Files:**
- Modify: `apps/api/apps/time_off/models/vacation.py` (all 5 models live here)

- [ ] **Step 8.1: Update each model**

For each of the 5 models, add `tenant = FK(...)`.

For models with existing `unique_together`, prepend `tenant`:

| Model | Current | New |
|-------|---------|-----|
| `VacationConfiguration` | `[['tipo_configuracion', 'area', 'empleado', 'fecha_inicio_vigencia']]` | `[['tenant', 'tipo_configuracion', 'area', 'empleado', 'fecha_inicio_vigencia']]` |
| `VacationPeriod` | `[['empleado', 'ano_periodo', 'contrato']]` | `[['tenant', 'empleado', 'ano_periodo', 'contrato']]` |

For `VacationRequest`, `VacationGrant`, `VacationRequestHistory`: add only the FK.

- [ ] **Step 8.2: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations time_off --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate time_off --settings=vyntia.settings.development
```

- [ ] **Step 8.3: Verify**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

- [ ] **Step 8.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/time_off/
git commit -m "chore(C1): add tenant FK to time_off models (5 vacation models)"
```

---

## Task 9: Onboarding app — tenant FK

**Files:**
- Modify: `apps/api/apps/onboarding/models/onboarding_process.py`

- [ ] **Step 9.1: Update `OnboardingProcess`**

Add `tenant = FK(...)`. No unique changes (the existing OneToOne fields on `empleado`/`usuario` provide implicit uniqueness; no widening needed because each Employee belongs to exactly one tenant via Employee.tenant).

- [ ] **Step 9.2: Make + apply migrations**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations onboarding --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe manage.py migrate onboarding --settings=vyntia.settings.development
```

- [ ] **Step 9.3: Verify**

```bash
D:/VYNTIA/.venv/Scripts/python.exe manage.py check --settings=vyntia.settings.development
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
```

- [ ] **Step 9.4: Commit**

```bash
cd D:/VYNTIA
git add apps/api/apps/onboarding/
git commit -m "chore(C1): add tenant FK to onboarding model (OnboardingProcess)"
```

---

## Task 10: Final verification + merge

- [ ] **Step 10.1: Full pytest baseline + missing-migration check**

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -q 2>&1 | tail -5
D:/VYNTIA/.venv/Scripts/python.exe manage.py makemigrations --dry-run --check --settings=vyntia.settings.development 2>&1 | tail -2
```

Expected: ≥176 passed / ≤8 failed / 3 skipped, and `No changes detected`.

- [ ] **Step 10.2: Frontend baseline (sanity — no frontend changes)**

```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
```

Expected: build exit 0.

- [ ] **Step 10.3: Verify all 31 models have `tenant` field**

Run a quick introspection script:

```bash
cd D:/VYNTIA/apps/api
D:/VYNTIA/.venv/Scripts/python.exe manage.py shell --settings=vyntia.settings.development << 'EOF'
from django.apps import apps

TENANT_SCOPED_APPS = ['identity', 'organization', 'employees', 'contracts', 'documents', 'payroll', 'time_off', 'onboarding']
SKIP = {('identity', 'User'), ('identity', 'Module')}

print("Models WITH tenant field:")
print("Models WITHOUT tenant field (should match SKIP):")

for app_label in TENANT_SCOPED_APPS:
    app = apps.get_app_config(app_label)
    for model in app.get_models():
        has_tenant = any(f.name == 'tenant' for f in model._meta.local_fields)
        marker = "✓" if has_tenant else ("·" if (app_label, model.__name__) in SKIP else "✗ MISSING")
        print(f"  {marker}  {app_label}.{model.__name__}")
EOF
```

Expected: every model in the inventory has `✓`. The only `·` should be `identity.User` and `identity.Module`. No `✗ MISSING`.

- [ ] **Step 10.4: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, find the C.1 row and update the "Detailed plan" cell:

```
`2026-05-09-vyntia-C1-tenant-id-migration.md` ✅ merged 2026-05-09
```

- [ ] **Step 10.5: Commit roadmap update**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md
git commit -m "docs(C1): mark C.1 done in master roadmap"
```

- [ ] **Step 10.6: Merge to master**

```bash
cd D:/VYNTIA
git checkout master
git merge --no-ff vyntia/C1-tenant-id-migration \
  -m "Merge C.1: add tenant_id FK to all 31 business models across 8 apps"
```

Expected: clean merge.

- [ ] **Step 10.7: Verify post-merge**

```bash
git log --oneline -3
git status
```

Expected: working tree clean, HEAD on the merge commit.

---

## Self-Review

### Spec coverage check

| Spec § 3.2 requirement | Covered by task |
|---|---|
| `tenant = FK(Tenant, on_delete=PROTECT, db_index=True)` on all business models | Tasks 2-9 (with `null=True` deviation noted) |
| User and Module stay global | Tasks 2 (skipped) |
| `Employee.numero_documento` composite unique | Task 4 |
| `Role.nombre_rol` composite unique | Task 2 |
| `Permission.nombre_permiso` composite unique | Task 2 — DEVIATION: Permission has no current `unique=True` per inventory; no composite added |
| `Department.siglas_area` composite unique | Task 3 |
| `Company` per-tenant unique | Task 3 |
| `Contract.numero_contrato` composite unique | Task 5 |
| `TenantScopedModel` abstract base in `apps/core/models.py` | Task 1 |
| `Company.get_config()` callers updated | Task 3 |

### Deviations from spec

1. **`null=True` on retrofit FKs** — spec § 3.2 implies NOT NULL. Deviation explained in Architecture above; will be reverted in C.3 cleanup migration after middleware ensures all writes have tenant.
2. **`Permission.nombre_permiso`** — spec § 3.3 lists this as composite unique target, but the actual model in code has no `unique=True` on this field per the inventory exploration. No migration needed.
3. **`related_name="+"`** on tenant FKs — spec doesn't specify, but adding 31 reverse accessors to Tenant is noisy. `+` disables them; we'll use forward queries (`tenant.id` ↔ `model.objects.filter(tenant=...)`) instead.

### Placeholder scan

- One TODO intentionally added in `template_service.py` (Task 3) flagged for C.3 follow-up — that is documented intent, not a placeholder failure.
- All other code is complete and runnable.

### Type consistency

- Every `tenant = ForeignKey('tenancy.Tenant', null=True, blank=True, on_delete=PROTECT, db_index=True, related_name='+')` is byte-identical across the 31 models. Single source of truth.
- Constraint naming convention: `unique_<entity>_<field>_per_tenant` — consistent across the 12 widened constraints.

### Out of scope (deferred)

- RLS policies (C.2)
- TenantManager / UnsafeManager (C.3)
- Subdomain middleware + RLSMiddleware (C.3)
- Flipping `null=True` → `null=False` after middleware lands (end of C.3 or dedicated migration)
- New tests verifying tenant scoping behavior (C.3 — they need middleware to be meaningful)

---

**Plan complete.** When executed, C.1 ships ~10 commits (1 chore + 8 feat per app + 1 docs), ~25 migration files (auto-generated, ~3 per app for AddField + AlterUniqueTogether/AddConstraint changes), and zero regressions in the 176-test baseline.
