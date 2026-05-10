# B.0 — Audit & Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a documented, prioritized inventory of what exists in the 6 Vyntia Core apps today (post-A+C), what's missing vs. INTRANET legacy, what's missing vs. maestro modules 01/02/03, and what cross-cutting decisions block B.1+. Output: 4 markdown documents under `.planning/audit-B/`. **NO production code is written in this phase.**

**Architecture:** Read-only audit. Subagents read VYNTIA source, INTRANET legacy source (`D:/INTRANET/back/app_rrhh/`), the maestro catalog (`docs/00_VYNTIA_MAESTRO.md`), and pytest/tsc/lint output. They synthesize findings into 4 documents (`INVENTORY.md`, `BACKLOG.md`, `ROADMAP-B.md`, `ADRS.md`) committed incrementally on branch `vyntia/B0-audit`. Final merge to master is the close-out.

**Tech Stack:** Markdown + git (no Python/JS code touched). Source reading via Read/Grep/Glob.

**Source spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`

---

## Baseline snapshot

| Check | Expected before B.0 | Expected after B.0 |
|---|---|---|
| Backend pytest | 271 passed, 7 failed (pre-existing), 17 skipped | unchanged (no code touched) |
| Frontend build | exit 0 | unchanged |
| Frontend tsc | 1 error (BlankEnum) | unchanged |
| Frontend vitest | 32 passed | unchanged |
| Frontend lint | 641 warnings | unchanged |
| `.planning/audit-B/` | doesn't exist | 4 markdown files committed |

B.0 adds: 4 markdown documents (~600-1500 lines combined). 0 lines of code change.

---

## File structure

**Files to create:**

```
.planning/audit-B/
├── INVENTORY.md          # 6 chapters (one per Core app) — state, legacy gaps, maestro gaps, bugs, tenant audit
├── BACKLOG.md            # priority table — every actionable item from inventory + gap analyses
├── ROADMAP-B.md          # confirmed phase structure B.1...B.N (master roadmap for sub-project B)
└── ADRS.md               # 9 architectural decisions to lock before B.1
```

**Files to read (no modification):**

- `apps/api/apps/{identity,organization,employees,contracts,documents,onboarding}/` — current VYNTIA Core
- `D:/INTRANET/back/app_rrhh/models/` — 18 legacy model files
- `D:/INTRANET/back/app_rrhh/{filters,managers,services}` and `D:/INTRANET/back/api/` — legacy logic + endpoints
- `apps/web/src/features/{auth,identity,organization,employees,contracts,documents,onboarding}/` — current VYNTIA UI
- `D:/INTRANET/front/src/` — legacy UI
- `docs/00_VYNTIA_MAESTRO.md` § 3 — module catalog
- `docs/modulos/{01_planificacion_politicas,02_organizacion_trabajo,03_gestion_empleo}.md` — module deep specs (if they exist)

**Files NOT to touch in B.0:**

- Any source code (`.py`, `.ts`, `.tsx`, `.js`, `.tsx`, `.css`)
- Any settings file
- Any test file
- Database

---

## Branch

`vyntia/B0-audit` — branched from `master` (HEAD has `Merge C.8`, currently `e28c0b2c` + spec commit `3fc48a01`).

---

## Task 1: Setup branch + audit workspace skeleton

**Files:**
- Create: `.planning/audit-B/INVENTORY.md` (skeleton with 6 empty chapter headings)
- Create: `.planning/audit-B/BACKLOG.md` (skeleton with empty table header)
- Create: `.planning/audit-B/ROADMAP-B.md` (skeleton with the 16-phase outline from spec, marked as "tentative")
- Create: `.planning/audit-B/ADRS.md` (skeleton with the 9 ADR titles from spec § 7)

- [ ] **Step 1.1: Create branch**

```bash
cd D:/VYNTIA
git checkout master
git checkout -b vyntia/B0-audit
```

- [ ] **Step 1.2: Create audit-B directory skeleton**

Use the Write tool to create each of the 4 files with the skeleton content below. Do not create them via bash heredoc — the Write tool is the standard.

`.planning/audit-B/INVENTORY.md`:

```markdown
# Vyntia Core — Inventory (B.0 audit)

> Per-app inventory of state-of-the-codebase for Vyntia Core (post-Foundation A + Multi-tenancy C).
> Audit date: 2026-05-09.
> Sources: VYNTIA `apps/api/apps/*` and `apps/web/src/features/*`, INTRANET legacy `D:/INTRANET/`, maestro `docs/00_VYNTIA_MAESTRO.md` § 3.

## Status legend

- ✅ Implemented and working
- ⚠️ Partial / needs polish
- ❌ Missing / not started
- 🐛 Bug or deuda técnica

## App: identity

(Filled by Task 2.)

## App: organization

(Filled by Task 3.)

## App: employees

(Filled by Task 4.)

## App: contracts

(Filled by Task 5.)

## App: documents

(Filled by Task 6.)

## App: onboarding

(Filled by Task 7.)

## Cross-cutting deuda técnica

(Filled by Task 8 — pytest failures, tsc errors, lint warnings attributed by app.)

## Maestro gaps — Module 01 (Policies)

(Filled by Task 9.)

## Maestro gaps — Module 02 (Organization extended)

(Filled by Task 10.)

## Maestro gaps — Module 03 (Employment lifecycle)

(Filled by Task 11.)
```

`.planning/audit-B/BACKLOG.md`:

```markdown
# Vyntia Core — Backlog (B.0 audit)

> Prioritized list of actionable items derived from `INVENTORY.md`. Each item maps to a phase B.X.
> Audit date: 2026-05-09.

## Priority legend

- **P0** — blocks commercial launch of Vyntia Core
- **P1** — important but not launch-blocking; can ship in later phase
- **P2** — nice-to-have; may be deferred to post-B sub-project

## Type legend

- **bug** — defect in existing code
- **parity** — feature in INTRANET legacy not yet ported to VYNTIA
- **new** — feature from maestro that doesn't exist in VYNTIA or legacy
- **tenant** — multi-tenant readiness fix

## Backlog

| # | Item | App | Type | Prio | Phase | Deps | Estimation |
|---|------|-----|------|:----:|:-----:|------|:----------:|

(Filled by Task 12 — synthesizes from INVENTORY.md.)
```

`.planning/audit-B/ROADMAP-B.md`:

```markdown
# Sub-project B — Master Roadmap (confirmed by B.0 audit)

> Confirmed phase structure for sub-project B. Each phase is a separate branch and PR, mergeable independently.
> Source spec: `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`.
> Roadmap version: TENTATIVE (will be confirmed by Task 13 post-audit).

## Phase table

| Fase | Branch | Scope | Necesita | Plan detallado |
|------|--------|-------|----------|----------------|
| B.0  | `vyntia/B0-audit` | Audit & inventory (this phase) | A, C | `2026-05-09-vyntia-B0-audit.md` |
| B.1  | `vyntia/B1-polish-baseline` | Polish wave: bug-fix baseline (pytest, tsc, lint, tenant audit fixes) | B.0 | TBD post-B.0 |
| B.2  | `vyntia/B2-polish-identity` | Polish wave: identity (users, roles, RBAC UI) | B.1 | TBD |
| B.3  | `vyntia/B3-polish-organization` | Polish wave: organization (departments, locations, company config) | B.1 | TBD |
| B.4  | `vyntia/B4-polish-employees` | Polish wave: employees (Empleado + datos personales/familiares/académicos) | B.1 | TBD |
| B.5  | `vyntia/B5-polish-contracts-documents-onboarding` | Polish wave: contracts + documents + onboarding | B.1 | TBD |
| B.6  | `vyntia/B6-positions-orgchart` | Módulo 02: Position + OrgChart | B.3 | TBD |
| B.7  | `vyntia/B7-ccf-salaryband` | Módulo 02: CCF (Ley 30709) + SalaryBand | B.6 | TBD |
| B.8  | `vyntia/B8-mpp-cpe` | Módulo 02: MPP + CPE (SERVIR) | B.6 | TBD |
| B.9  | `vyntia/B9-seleccion` | Módulo 03.1: Selección | B.6 | TBD |
| B.10 | `vyntia/B10-vinculacion-tregistro` | Módulo 03.2: Vinculación + T-Registro | B.6 | TBD |
| B.11 | `vyntia/B11-induccion-prueba` | Módulo 03.3+4: Inducción + Período de prueba | B.10 | TBD |
| B.12 | `vyntia/B12-legajos-completos` | Módulo 03.5: Legajos digitales completos | B.5 | TBD |
| B.13 | `vyntia/B13-desplazamiento` | Módulo 03.6: Desplazamiento (rotación, encargatura, destaque) | B.10 | TBD |
| B.14 | `vyntia/B14-desvinculacion-liquidacion` | Módulo 03.7: Desvinculación + liquidación | B.10 | TBD |
| B.15 | `vyntia/B15-policies` | Módulo 01: Policies | B.1 | TBD |
| B.16 | `vyntia/B16-e2e-close-out` | E2E + docs + tag b-vyntia-core-complete | B.1-B.15 | TBD |

## Order and dependencies

Diagram:

```
B.0 → B.1 → B.2-B.5 (polish wave, parallel)
                │
                ▼
       B.6 → B.7 (CCF)
        │  → B.8 (MPP/CPE)
        │  → B.9 (Selección)
        │  → B.10 (Vinculación)
        │       │
        │       ▼
        │     B.11 → B.13 → B.14
        │     B.12 (parallel)
        ▼
      B.15 (Policies, parallel to B.6+)
        ▼
      B.16 (close-out)
```

## Adjustments by audit (filled by Task 13)

(Document any phase additions/removals/reorderings discovered during the audit.)
```

`.planning/audit-B/ADRS.md`:

```markdown
# Sub-project B — Architectural Decision Records

> Cross-cutting decisions to lock before B.1. Each ADR follows the format:
> Title / Context / Decision / Consequences / Status (proposed | accepted | superseded).

## ADR-B.1: i18n strategy

(Filled by Task 14.)

## ADR-B.2: Audit log scope

(Filled by Task 14.)

## ADR-B.3: Approval workflow strategy

(Filled by Task 14.)

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
```

- [ ] **Step 1.3: Verify the 4 files exist**

```bash
cd D:/VYNTIA && ls -la .planning/audit-B/
```

Expected: 4 files (INVENTORY.md, BACKLOG.md, ROADMAP-B.md, ADRS.md).

- [ ] **Step 1.4: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/
git commit -m "docs(B0): audit workspace skeleton (INVENTORY + BACKLOG + ROADMAP + ADRS)"
```

---

## Tasks 2-7: Per-app inventory chapters

Six tasks, one per Core app. Each fills a chapter in `INVENTORY.md` with this exact structure:

```markdown
## App: <name>

### Estado actual en VYNTIA (post-A+C)

#### Modelos
- `<Model>` (file: `apps/api/apps/<app>/models/<file>.py`) — <brief purpose>
  - Campos clave: <list>
  - Tenant FK: ✅/❌
  - Manager: default `objects` / TenantManager (none wired in C.0–C.5)

#### Endpoints REST
- `GET /api/v1/<path>/` — list (file: `api/v1/<path>/views.py`)
- `POST /api/v1/<path>/` — create
- (etc.)

#### UI (frontend)
- `<Page>` at `apps/web/src/features/<feature>/pages/<file>.tsx` — <purpose>
- (etc.)

#### Tests
- `apps/api/apps/<app>/tests/test_<x>.py` — <count> tests
- (etc.)

### Gaps vs INTRANET legacy

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|

(Each row: feature in `D:/INTRANET/back/app_rrhh/...` that VYNTIA hasn't ported, with type bug/parity/new and prio P0/P1/P2.)

### Gaps vs maestro

(Features the maestro requires that don't exist in VYNTIA or INTRANET. Reference module + section.)

### Bugs y deuda técnica conocidos

(Pytest failures, TS errors, lint warnings attributable to this app.)

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|

(Check if endpoints respect tenant scoping, if models have tenant FK, if RLS policies cover this app's tables.)

### Notas

(Decisions from A or C affecting this app, risks of touching it.)
```

The 6 tasks (2-7) are templated. Each follows the same procedure but for a different app.

---

## Task 2: Inventory — `identity`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: identity` chapter from skeleton)

- [ ] **Step 2.1: Read VYNTIA identity app**

Use Read on each of these:

```
apps/api/apps/identity/models/__init__.py
apps/api/apps/identity/models/user.py
apps/api/apps/identity/models/role.py
apps/api/apps/identity/models/permission.py
apps/api/apps/identity/models/module.py        # if exists
apps/api/apps/identity/services/menu_service.py
apps/api/api/v1/identity/views.py              # if exists
apps/api/api/v1/auth/views.py                  # auth endpoints
apps/api/api/v1/auth/serializers.py
apps/web/src/features/identity/                # via Glob: features/identity/**
apps/web/src/features/auth/                    # auth UI
```

Use Glob with `apps/api/apps/identity/**/*.py` and `apps/web/src/features/identity/**/*.tsx` to enumerate all files. Use Grep `class \w+` to find model class names.

- [ ] **Step 2.2: Read INTRANET legacy auth/identity equivalents**

```
D:/INTRANET/back/app_rrhh/models/usuario.py
D:/INTRANET/back/app_rrhh/models/roles.py
D:/INTRANET/back/app_rrhh/models/sistema.py    # legacy "modules" + permissions
D:/INTRANET/back/app_rrhh/auth.py               # if exists
D:/INTRANET/back/api/v1/auth/                   # legacy endpoints (if structure mirrors)
```

For each legacy model field/method, ask: "Does VYNTIA have an equivalent? If not, is it a parity gap or just abandoned?"

- [ ] **Step 2.3: Read maestro § 3 for identity coverage**

The maestro doesn't have a dedicated module for identity (it's transversal). But check:

- `docs/00_VYNTIA_MAESTRO.md` § 5.3 (apps transversales) — what `identity` should ultimately deliver
- `docs/00_VYNTIA_MAESTRO.md` § 4 (estrategia comercial) — RBAC implications for tier separation

- [ ] **Step 2.4: Run pytest scoped to identity to find failures**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/identity/tests/ -v 2>&1 | tail -20
```

Note any FAIL or ERROR cases, attribute them to the identity chapter.

- [ ] **Step 2.5: Find tsc / lint warnings for identity feature**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/identity" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/identity" | head -20
```

- [ ] **Step 2.6: Tenant-readiness audit for identity**

Check:
- Does User model have a `tenant` FK? (User is a special case — it can be cross-tenant via TenantMembership.)
- Does identity expose endpoints that should be tenant-scoped but aren't?
- Are roles per-tenant or global? (Per-tenant per spec.)

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/identity/models/ apps/api/apps/identity/services/ 2>/dev/null | head -10
```

- [ ] **Step 2.7: Write the identity chapter**

Use Edit to replace the placeholder text under `## App: identity` in `INVENTORY.md` with the full chapter following the template above. Be specific:
- Cite line numbers for non-obvious findings (e.g., `User model lacks last_password_change field — see legacy usuario.py:67`)
- For each gap, propose a phase (B.2 polish identity, or B.X if it crosses concerns)
- For each bug, link to the file + test name

- [ ] **Step 2.8: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — identity app"
```

---

## Task 3: Inventory — `organization`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: organization` chapter)

Follow Task 2's procedure with these source files:

VYNTIA:
- `apps/api/apps/organization/models/department.py` (or `area.py` — verify)
- `apps/api/apps/organization/models/company_config.py`
- `apps/api/apps/organization/models/location.py` (if exists)
- `apps/api/api/v1/organization/views.py`
- `apps/web/src/features/organization/`

INTRANET legacy:
- `D:/INTRANET/back/app_rrhh/models/area.py`
- `D:/INTRANET/back/app_rrhh/models/configuracion_empresa.py`
- `D:/INTRANET/back/app_rrhh/models/ubicacion.py`

Maestro: `docs/00_VYNTIA_MAESTRO.md` § 3 module 02 — note that Position/OrgChart/CCF/MPP/CPE belong here but are not yet implemented; they'll be covered in Tasks 9-11 (gap analysis), not this task. This task only audits what currently exists in `organization`.

- [ ] **Step 3.1: Read VYNTIA organization sources**
- [ ] **Step 3.2: Read INTRANET legacy `area.py`, `configuracion_empresa.py`, `ubicacion.py`**
- [ ] **Step 3.3: Run pytest scoped to organization**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/organization/tests/ -v 2>&1 | tail -20
```

- [ ] **Step 3.4: Find tsc / lint warnings for organization feature**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/organization" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/organization" | head -20
```

- [ ] **Step 3.5: Tenant-readiness audit for organization**

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/organization/ 2>/dev/null | head -10
```

Check: does each model FK to `tenancy.Tenant`? Does `ConfiguracionEmpresa` have unique-per-tenant constraint (since each tenant has one company config)?

- [ ] **Step 3.6: Write the organization chapter**
- [ ] **Step 3.7: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — organization app"
```

---

## Task 4: Inventory — `employees`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: employees` chapter)

VYNTIA sources:
- `apps/api/apps/employees/models/employee.py`
- `apps/api/apps/employees/models/family_member.py`
- `apps/api/apps/employees/models/academic_record.py`
- `apps/api/apps/employees/models/courses_certifications.py`
- `apps/api/apps/employees/services/employee_report_service.py`
- `apps/api/api/v1/employees/views.py`
- `apps/web/src/features/employees/`

INTRANET legacy:
- `D:/INTRANET/back/app_rrhh/models/empleado.py`
- `D:/INTRANET/back/app_rrhh/models/datos_familiares.py`
- `D:/INTRANET/back/app_rrhh/models/datos_academicos.py`
- `D:/INTRANET/back/app_rrhh/models/cursos_certificaciones.py`

Maestro: § 3 module 03 — Employee section. (Sub-procesos like Selección/Vinculación/Desvinculación are gap analysis Task 11.)

- [ ] **Step 4.1: Read VYNTIA employees sources**
- [ ] **Step 4.2: Read INTRANET legacy `empleado.py` and family/academic/courses files**
- [ ] **Step 4.3: Run pytest scoped to employees**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/employees/tests/ -v 2>&1 | tail -20
```

- [ ] **Step 4.4: Find tsc / lint warnings**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/employees" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/employees" | head -20
```

- [ ] **Step 4.5: Tenant-readiness audit**

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/employees/ 2>/dev/null | head -10
```

Verify: Employee.tenant FK (it should exist post-C.1). Are unique constraints on `numero_documento` per-tenant (composite) or global?

- [ ] **Step 4.6: Write the employees chapter**

⚠️ Special attention: the employees app is the largest of the 6 (4 models, plus the legacy had `empleado.py` with many fields some of which might not have been ported). Be thorough on field-by-field comparison.

- [ ] **Step 4.7: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — employees app"
```

---

## Task 5: Inventory — `contracts`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: contracts` chapter)

VYNTIA sources:
- `apps/api/apps/contracts/models/contract.py`
- `apps/api/apps/contracts/models/contract_amendment.py` (split in L3.10.3)
- `apps/api/apps/contracts/models/employment_data.py` (DatosLaborales)
- `apps/api/api/v1/contracts/views.py`
- `apps/web/src/features/contracts/`

INTRANET legacy:
- `D:/INTRANET/back/app_rrhh/models/contratos_adendas.py`
- `D:/INTRANET/back/app_rrhh/models/datos_laborales.py`

Maestro: § 3 module 03.2 (Vinculación). Note: T-Registro, signature workflows, contract templates with variables — those are gap analysis Task 11.

- [ ] **Step 5.1: Read VYNTIA contracts sources**
- [ ] **Step 5.2: Read INTRANET legacy contracts files**
- [ ] **Step 5.3: Run pytest scoped to contracts**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/contracts/tests/ -v 2>&1 | tail -20
```

- [ ] **Step 5.4: Find tsc / lint warnings**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/contracts" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/contracts" | head -20
```

- [ ] **Step 5.5: Tenant-readiness audit**

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/contracts/ 2>/dev/null | head -10
```

Note from L3.10.3: Contract was split into Contract + ContractAmendment. Verify both have tenant FK.

- [ ] **Step 5.6: Write the contracts chapter**

Mention the L3.10.3 split as context (LR21 lesson: model splits require consumer updates). Note if any consumers still expect the unified Contract.

- [ ] **Step 5.7: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — contracts app"
```

---

## Task 6: Inventory — `documents`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: documents` chapter)

VYNTIA sources:
- `apps/api/apps/documents/models/document_file.py`
- `apps/api/apps/documents/models/document_template.py`
- `apps/api/apps/documents/services/pdf_generator.py`
- `apps/api/apps/documents/services/template_service.py`
- `apps/api/templates/{reportes,certificados,contratos}/`
- `apps/web/src/features/documents/`

INTRANET legacy:
- `D:/INTRANET/back/app_rrhh/models/documentos_digitales.py`
- `D:/INTRANET/back/app_rrhh/models/plantilla_documento.py`
- `D:/INTRANET/back/app_rrhh/services/` (PDF generation)

Maestro: § 3 module 03.5 (Legajos digitales). Full legajo with index/search/retention is Task 11 gap analysis; this task audits the current document storage + template system.

- [ ] **Step 6.1: Read VYNTIA documents sources**
- [ ] **Step 6.2: Read INTRANET legacy documents files + check D:/INTRANET/back/templates/ for HTML templates**
- [ ] **Step 6.3: Run pytest scoped to documents**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/documents/tests/ -v 2>&1 | tail -20
```

- [ ] **Step 6.4: Find tsc / lint warnings**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/documents" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/documents" | head -20
```

- [ ] **Step 6.5: Tenant-readiness audit**

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/documents/ 2>/dev/null | head -10
```

Note: PDF generation is currently filesystem-based; ADR-B.4 will decide if this stays or migrates to S3/Azure. The audit only documents the current state.

- [ ] **Step 6.6: Write the documents chapter**

Special focus: list all available HTML templates (in `apps/api/templates/`) and what each generates. Identify legacy templates not yet ported.

- [ ] **Step 6.7: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — documents app"
```

---

## Task 7: Inventory — `onboarding`

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## App: onboarding` chapter)

VYNTIA sources:
- `apps/api/apps/onboarding/models/onboarding_process.py`
- `apps/api/apps/onboarding/services/onboarding_service.py`
- `apps/api/apps/onboarding/services/onboarding_notification_service.py`
- `apps/api/api/v1/onboarding/views.py`
- `apps/web/src/features/onboarding/`

INTRANET legacy:
- `D:/INTRANET/back/app_rrhh/models/onboarding.py`

Maestro: § 3 module 03.3 (Inducción). Note RPE 265-2017-SERVIR-PE compliance is required for public sector — this is gap analysis Task 11.

- [ ] **Step 7.1: Read VYNTIA onboarding sources**
- [ ] **Step 7.2: Read INTRANET legacy onboarding.py**
- [ ] **Step 7.3: Run pytest scoped to onboarding**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest apps/onboarding/tests/ -v 2>&1 | tail -20
```

- [ ] **Step 7.4: Find tsc / lint warnings**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep "features/onboarding" | head -10
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | grep "features/onboarding" | head -20
```

- [ ] **Step 7.5: Tenant-readiness audit**

```bash
cd D:/VYNTIA && grep -rn "tenant" apps/api/apps/onboarding/ 2>/dev/null | head -10
```

- [ ] **Step 7.6: Write the onboarding chapter**

Special focus: notification flow (email templates, Celery task delivery). Verify the email subjects mention "VYNTIA" not "INTRANET" (foundation L1 should have rebranded; verify).

- [ ] **Step 7.7: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): inventory chapter — onboarding app"
```

---

## Task 8: Cross-cutting deuda técnica

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## Cross-cutting deuda técnica` chapter)

This task aggregates technical debt that cuts across apps:

- [ ] **Step 8.1: Run full pytest, capture all failures**

```bash
cd D:/VYNTIA/apps/api && D:/VYNTIA/.venv/Scripts/python.exe -m pytest tests/ apps/tenancy/tests/ -v 2>&1 | grep -E "FAILED|ERROR" > /tmp/pytest-failures.txt
cat /tmp/pytest-failures.txt
```

Expected: 7 pre-existing failures. Capture each test name + module.

- [ ] **Step 8.2: Run full tsc, capture all errors**

```bash
cd D:/VYNTIA/apps/web && npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -E "error TS" > /tmp/tsc-errors.txt
cat /tmp/tsc-errors.txt
```

Expected: 1 error in `BlankEnum.ts`. Capture file:line:error.

- [ ] **Step 8.3: Run full lint, capture warning count by area**

```bash
cd D:/VYNTIA/apps/web && npm run lint 2>&1 | tail -50 > /tmp/lint-output.txt
cat /tmp/lint-output.txt
```

Expected ~641 warnings. Categorize: which directories have the most? (Likely `generated/api/` is the bulk — those are code-gen.)

- [ ] **Step 8.4: Write the deuda chapter**

Enumerate each item with attribution to an app and a proposed phase:

```markdown
## Cross-cutting deuda técnica

### Pytest pre-existing failures (7)

| Test | App | Cause | Proposed phase to fix |
|------|-----|-------|-----------------------|
| `test_employees_list_returns_paginated` | employees | (root cause) | B.4 |
| ... | ... | ... | ... |

### TS errors (1)

| File | Error | Proposed fix |
|------|-------|--------------|
| `apps/web/src/generated/api/models/BlankEnum.ts:6:5` | `(error message)` | (suggest fix or wontfix justification) — proposed phase B.1 |

### Lint warnings (641 total)

| Directory | Count | Category | Proposed phase |
|-----------|------:|---------|----------------|
| `generated/api/` | (count) | auto-generated | wontfix or B.1 ignore-rule |
| `features/employees/` | (count) | unused vars, any-types | B.4 |
| ... | ... | ... | ... |
```

- [ ] **Step 8.5: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): cross-cutting deuda chapter (pytest failures + tsc + lint by app)"
```

---

## Task 9: Maestro gap analysis — Module 01 (Policies)

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## Maestro gaps — Module 01 (Policies)` chapter)

Module 01 is entirely missing — there is no `policies` Django app today. This task documents what the maestro requires and how big the gap is.

- [ ] **Step 9.1: Read maestro § 3 module 01**

```
docs/00_VYNTIA_MAESTRO.md (lines 139-152 approximately)
```

If `docs/modulos/01_planificacion_politicas.md` exists, read it for deep detail.

```bash
cd D:/VYNTIA && ls docs/modulos/ 2>/dev/null
```

- [ ] **Step 9.2: Check INTRANET legacy for any policy-related code**

```bash
cd D:/INTRANET && grep -rn "polic\|política\|directiva" back/app_rrhh/ 2>/dev/null | head -10
```

Likely: nothing significant. Confirm legacy has no policy module.

- [ ] **Step 9.3: Write Module 01 gap chapter**

```markdown
## Maestro gaps — Module 01 (Policies)

### Maestro requirements
- Gestor documental de políticas (versionado, aprobación, difusión)
- Plan de RRHH anual con objetivos y KPIs
- Matriz de cumplimiento normativo
- Alertas de vencimiento de directivas

### Entities required (per maestro)
- `Policy` — política con metadatos
- `PolicyVersion` — versionado
- `HRPlan` — plan anual de RRHH
- `HRPlanObjective` — objetivos del plan
- `ComplianceMatrix` — matriz de cumplimiento

### Current state in VYNTIA
❌ Module 01 has zero implementation. No `policies` Django app, no UI, no models.

### Current state in INTRANET legacy
❌ Module 01 has zero implementation in legacy either.

### Estimated work
- Create new `apps/policies/` Django app
- 5 models with tenant FK
- CRUD endpoints + serializers
- Versioning logic (use ADR-B.7 versioning decision)
- Document upload + storage (use ADR-B.4 storage decision)
- Approval workflow (use ADR-B.3 workflow decision)
- Frontend: `features/policies/` with list/detail/edit/version-history pages
- Tier comercial: Pro

### Phase mapping
- Single phase: B.15

### Dependencies
- ADR-B.4 (storage) decided
- ADR-B.3 (workflow) decided
- ADR-B.7 (versioning) decided
- B.1-B.5 polish wave done (so policies app starts on a clean baseline)
```

- [ ] **Step 9.4: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): maestro gap analysis — Module 01 Policies"
```

---

## Task 10: Maestro gap analysis — Module 02 (Organization extended)

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## Maestro gaps — Module 02 (Organization extended)` chapter)

Module 02 partially exists (Department, ConfiguracionEmpresa, Location). Missing: Position, OrgChart, CCF, SalaryBand, MPP, CPE.

- [ ] **Step 10.1: Read maestro § 3 module 02 + linked deep doc**

```
docs/00_VYNTIA_MAESTRO.md (lines 156-171)
docs/modulos/02_organizacion_trabajo.md (if exists)
```

- [ ] **Step 10.2: Check INTRANET legacy for any position/orgchart/CCF code**

```bash
cd D:/INTRANET && grep -rn "position\|cargo\|orgchart\|organigrama\|salaryband\|banda\|MPP\|CPE\|CCF" back/app_rrhh/ 2>/dev/null | head -20
```

If legacy had any of these, capture them as parity (not new) gaps.

- [ ] **Step 10.3: Look up Ley 30709 requirements (CCF specifics)**

The CCF — Cuadro de Categorías y Funciones — is a legal artifact required by Peruvian Ley 30709 (igualdad salarial). Document the required structure based on existing knowledge in the spec or maestro.

If unsure, note: "ADR-B.X may need to be added: research CCF legal structure before B.7."

- [ ] **Step 10.4: Look up SERVIR MPP/CPE requirements**

MPP = Manual de Perfiles de Puestos, CPE = Cuadro de Puestos de la Entidad. Public-sector only.

If maestro doesn't have details, flag for research in ADRS phase.

- [ ] **Step 10.5: Write Module 02 gap chapter**

```markdown
## Maestro gaps — Module 02 (Organization extended)

### Already implemented (from B.0 inventory)
- Department (Area)
- Location (Ubicacion)
- ConfiguracionEmpresa

### Maestro requirements not yet implemented
- **Position** — catálogo de puestos / perfiles de puesto. Maps to → B.6.
- **PositionProfile** — descripción detallada del puesto. → B.6.
- **OrgUnit** — estructura jerárquica navegable (organigrama). → B.6.
- **CategoryFunctionTable (CCF)** — Ley 30709 igualdad salarial. → B.7.
- **SalaryBand** — banda salarial por categoría. → B.7.
- **MPP (Manual Perfiles)** — sector público SERVIR. → B.8.
- **CPE (Cuadro Puestos Entidad)** — sector público SERVIR. → B.8.

### Legacy parity gaps (from INTRANET review)
(Capture from Step 10.2.)

### Estimated work per phase
- B.6 — Position + OrgChart: ~2 weeks (3 models, OrgChart UI lib decision in ADR-B.8, drag-drop reordering, parent-child traversal)
- B.7 — CCF + SalaryBand: ~1.5 weeks (legal compliance, may require legal review pass)
- B.8 — MPP + CPE: ~1.5 weeks (public sector schema, distinct UI flow gated by tenant.sector)

### Dependencies
- B.3 polish-organization done first
- ADR-B.6 (SERVIR vs LCT in UI) decided before B.8
- ADR-B.7 (versioning of Position) decided before B.6
- ADR-B.8 (org chart frontend lib) decided before B.6
```

- [ ] **Step 10.6: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): maestro gap analysis — Module 02 Organization extended"
```

---

## Task 11: Maestro gap analysis — Module 03 (Employment lifecycle)

**Files:**
- Modify: `.planning/audit-B/INVENTORY.md` (replace `## Maestro gaps — Module 03 (Employment lifecycle)` chapter)

Module 03 partially exists. Sub-procesos:

- 03.1 Selección — ❌ missing
- 03.2 Vinculación — ⚠️ partial (Contract exists; T-Registro integration missing)
- 03.3 Inducción — ⚠️ partial (Onboarding exists; RPE 265-2017 compliance unverified)
- 03.4 Período de prueba — ❌ missing (no probation tracking model)
- 03.5 Administración de Legajos — ⚠️ partial (DocumentFile exists; full digital dossier missing)
- 03.6 Desplazamiento — ❌ missing (no displacement model)
- 03.7 Desvinculación — ❌ missing (no termination model, no severance calculation)

- [ ] **Step 11.1: Read maestro § 3 module 03 + linked deep doc**

```
docs/00_VYNTIA_MAESTRO.md (lines 175-191)
docs/modulos/03_gestion_empleo.md (if exists)
```

- [ ] **Step 11.2: For each sub-proceso, check INTRANET legacy**

```bash
cd D:/INTRANET && grep -rn "selección\|vinculación\|inducción\|período de prueba\|legajo\|desplazamiento\|cese\|desvinculación\|terminación\|liquidación" back/app_rrhh/ 2>/dev/null | head -30
```

Capture any partial implementation (e.g., legacy may have had a basic termination flow).

- [ ] **Step 11.3: Research T-Registro integration requirements**

T-Registro is SUNAT's mandatory employment registration system. Vinculación (03.2) requires registering the contract with T-Registro within 24h.

```bash
cd D:/VYNTIA && grep -rn "T-Registro\|tregistro\|t_registro" docs/ apps/ 2>/dev/null | head -10
```

If no existing implementation, flag B.10 as needing API integration design (likely an ADR addition).

- [ ] **Step 11.4: Research severance calculation scope (B vs D demarcation)**

Per spec § 4 RB7: "B.14 implements only minimum legal calculation; Pay (D) extends with full regimes." Define minimum legal calculation:
- CTS proporcional (1 mes por cada año + 1/12 del último periodo)
- Vacaciones truncas
- Gratificación trunca
- Indemnización por despido arbitrario (1.5 sueldos por año, capped at 12)

- [ ] **Step 11.5: Write Module 03 gap chapter**

For each of the 7 sub-procesos: maestro requirements, current state in VYNTIA + legacy, estimated work, phase mapping (B.9 selección, B.10 vinculación + T-Registro, B.11 inducción + prueba, B.12 legajos, B.13 desplazamiento, B.14 desvinculación + liquidación), dependencies.

- [ ] **Step 11.6: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/INVENTORY.md
git commit -m "docs(B0): maestro gap analysis — Module 03 Employment lifecycle (7 sub-procesos)"
```

---

## Task 12: Synthesize BACKLOG.md

**Files:**
- Modify: `.planning/audit-B/BACKLOG.md`

Aggregate every actionable item from `INVENTORY.md` (chapters 2-11) into the priority backlog.

- [ ] **Step 12.1: Re-read INVENTORY.md fully**

```bash
cd D:/VYNTIA && cat .planning/audit-B/INVENTORY.md | head -500
cd D:/VYNTIA && cat .planning/audit-B/INVENTORY.md | tail -500
```

(Or use Read with offset/limit if the file is huge.)

- [ ] **Step 12.2: Extract every item into the backlog**

For each item: assign `app | type | priority | phase | deps | estimation`.

Priority rubric (apply consistently):
- **P0**: blocks Vyntia Core MVP — without it the product can't be sold (e.g., "tenant FK missing on Document → cross-tenant leak"; "Selección is required for Starter").
- **P1**: important for completeness, not strictly launch-blocking (e.g., "MPP/CPE only matters for SERVIR clients"; "PDF generation works but lacks signed URLs").
- **P2**: nice-to-have, can defer to post-B (e.g., "audit log of every change to Employee record" — ADR-B.2 may move to sub-project X).

Estimation rubric:
- 0.5d = a few-line edit + test
- 1d = single-file feature
- 2d = multi-file feature with tests
- 1w = new model + endpoint + UI
- 2w = new sub-feature with workflow

- [ ] **Step 12.3: Write the BACKLOG.md table**

Replace the placeholder table with the full list. Sort by phase, then priority.

Target: ~50-150 items total (based on the size of the audit). If <30, the audit was too shallow; re-do.

- [ ] **Step 12.4: Validate phase consistency**

Ensure every backlog item's phase matches the proposed phase in INVENTORY.md. Where they conflict, prefer the BACKLOG view (it has cross-cutting visibility).

If items can't fit cleanly into B.1-B.16, propose roadmap adjustment to be confirmed in Task 13.

- [ ] **Step 12.5: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/BACKLOG.md
git commit -m "docs(B0): backlog synthesis from inventory + maestro gap analyses"
```

---

## Task 13: Confirm/adjust ROADMAP-B.md

**Files:**
- Modify: `.planning/audit-B/ROADMAP-B.md`

The skeleton roadmap from Task 1 is tentative. Now we have data — confirm or adjust.

- [ ] **Step 13.1: Compare backlog distribution against the proposed phases**

For each phase B.1...B.16, count:
- # of P0 items
- # of P1 items
- # of P2 items
- estimated total work (sum of estimations)

If a phase has too much (>2 weeks) or too little (<2 days), propose split or merge.

- [ ] **Step 13.2: Apply adjustments**

Document each adjustment in the "Adjustments by audit" section of ROADMAP-B.md. Examples:

```markdown
## Adjustments by audit

- **B.5 split into B.5a + B.5b:** the polish wave for contracts + documents + onboarding has 22 P0 items totaling ~3 weeks. Split: B.5a = contracts polish (1 week), B.5b = documents + onboarding polish (1.5 weeks).
- **B.7 and B.8 merged:** CCF and MPP/CPE share 60% of the implementation (similar entities, different sector exposure). Single phase B.7 covers both with sector toggles.
- **B.X.1 added:** Tenant readiness audit revealed that `documents` lacks proper signed URLs for cross-tenant document access. New phase B.X.1 inserted between B.6 and B.9.
```

- [ ] **Step 13.3: Update the phase table in ROADMAP-B.md**

Reflect adjustments. Mark each phase row's `Plan detallado` cell with the expected plan filename (still TBD until that phase's plan is written).

- [ ] **Step 13.4: Update the dependency diagram**

If phases were split, merged, or reordered, redraw the diagram in ROADMAP-B.md.

- [ ] **Step 13.5: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/ROADMAP-B.md
git commit -m "docs(B0): roadmap-B confirmed by audit (with adjustments documented)"
```

---

## Task 14: Draft 9 ADRs in ADRS.md

**Files:**
- Modify: `.planning/audit-B/ADRS.md`

Each ADR follows this format:

```markdown
## ADR-B.N: <Title>

**Status:** Proposed (will be Accepted upon merging B.0)

**Context:** (1-3 paragraphs explaining the problem and constraints.)

**Decision:** (1-2 sentences stating what we decided.)

**Consequences:**
- Positive: (list)
- Negative: (list)
- Neutral: (list)

**Alternatives considered:**
- Option A: (description) — rejected because...
- Option B: (description) — rejected because...

**Reference:** (link to maestro section, spec section, or external doc if relevant.)
```

This task is split into 3 sub-tasks because 9 ADRs is a lot to draft in one shot.

### Task 14a: ADRs B.1-B.3 (cross-cutting infra)

- [ ] **Step 14a.1: Draft ADR-B.1 — i18n strategy**

Context: VYNTIA UI is currently Spanish-only. Maestro § 4 mentions GovTech tier (sector público SERVIR) which is Peru-only. But VYNTIA could expand to other LATAM countries.

Decision: Spanish-only (es-PE) for B. Multi-language deferred to post-B if export demand appears.

Consequences positive: faster B delivery; no i18n infra required. Negative: hard to add EN later (every string needs extraction). Neutral: codebase strings stay in code.

Alternatives: full i18n via `react-i18next` + Django `gettext` from B.1 (rejected: 2-week tax with no current customer demand).

- [ ] **Step 14a.2: Draft ADR-B.2 — audit log scope**

Context: SERVIR + private sector clients may demand "who changed what when" trazabilidad. Sub-proyecto X is dedicated to a transversal audit log but is post-B. Without it, B.X phases that mutate critical state (contracts, terminations) lack audit trail.

Decision: minimal inline audit. Each tenant-scoped business model gets `created_at`, `updated_at`, `created_by`, `updated_by` audit fields (already standard in C.0 → present in most models). Specific high-stakes actions (cese, desvinculación, suspensión de empleado) emit `AuditEvent` rows in a small new app `apps/audit_lite/` introduced in B.1. Sub-proyecto X later replaces with full audit log.

Alternatives: do nothing in B (rejected: liability for SERVIR clients); full audit log in B (rejected: scope too big, X covers it).

- [ ] **Step 14a.3: Draft ADR-B.3 — approval workflow strategy**

Context: Several flows need approvals: cese de empleado (termination), ascenso (promotion), aumento salarial (salary change), desplazamiento (movement). Sub-proyecto T is the workflow engine but is post-B.

Decision: minimal inline approvals per flow. Each phase that introduces a workflow (B.13 desplazamiento, B.14 desvinculación) implements its own simple state machine: `pendiente → aprobado | rechazado`, with FK to the approver User. Sub-proyecto T later refactors all of these into a declarative engine.

Alternatives: build mini workflow framework in B.1 (rejected: scope creep); defer all approval flows to T (rejected: blocks B.13 and B.14).

- [ ] **Step 14a.4: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/ADRS.md
git commit -m "docs(B0): ADRs B.1-B.3 (i18n, audit log, approval workflows)"
```

### Task 14b: ADRs B.4-B.6 (technical infra)

- [ ] **Step 14b.1: Draft ADR-B.4 — document storage backend**

Context: PDF generation + legajos digitales need persistent storage. Currently `MEDIA_ROOT` is filesystem. Production deployments to multi-tenant SaaS typically use S3 or Azure Blob with signed URLs to avoid serving files through Django.

Decision: stay on filesystem for B. Add an abstraction (`apps/core/storage.py`) so future migration to S3/Azure is a config change, not a code rewrite. Signed URLs come from sub-proyecto post-B (deployment hardening).

Alternatives: S3 in B (rejected: cost + ops complexity for a not-yet-revenue product); Azure Blob (rejected: same).

- [ ] **Step 14b.2: Draft ADR-B.5 — testing strategy for employment lifecycle**

Context: Module 03 has 7 sub-procesos that compose into a lifecycle (selección → contratación → onboarding → vida laboral → cese). Each phase tests its own piece, but the integration is critical for a sellable product.

Decision: each B.X phase ships pytest unit + integration tests for its sub-proceso. B.16 close-out phase adds Playwright e2e tests for the full lifecycle (provision tenant → empleado → contrato → cese) that exercise all phases together.

Alternatives: Playwright per phase (rejected: e2e tests are expensive to maintain; better to consolidate); pytest only (rejected: doesn't catch UI regressions).

- [ ] **Step 14b.3: Draft ADR-B.6 — SERVIR vs LCT in UI**

Context: Vyntia targets both private (LCT — Ley General del Trabajo) and public (SERVIR) sectors. Some features differ: private uses CCF (Ley 30709); public uses MPP + CPE. Some flows differ: public has Designación + Encargatura (legacy displacement types).

Decision: each Tenant has a `sector` field (`'private' | 'public'`). UI conditionally shows sector-specific features via `useTenant().sector`. Backend models have shared base + sector-specific subclasses where the schemas diverge significantly. Both sectors share most of Core; only ~20% diverges.

Alternatives: separate tenants (rejected: doubles infra cost); separate apps (rejected: forks codebase).

- [ ] **Step 14b.4: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/ADRS.md
git commit -m "docs(B0): ADRs B.4-B.6 (storage, testing, SERVIR/LCT UI)"
```

### Task 14c: ADRs B.7-B.9 (model + frontend specifics)

- [ ] **Step 14c.1: Draft ADR-B.7 — versioning of critical models**

Context: Position (B.6) and Contract (already exists) need historical versioning. A user might change a Position's salary band, but old assignments must reflect the salary at the time. Same for Contract amendments (already implemented via `ContractAmendment` from L3.10.3).

Decision: per-model versioning strategy. Position uses inline versioning (Position has `version` int + `parent` self-FK to previous version). Contract continues with the explicit `Contract + ContractAmendment` split (already in place). No `django-simple-history` package — too magical; explicit versioning is clearer for legal review.

Alternatives: `django-simple-history` (rejected: opaque, hard to audit); event sourcing (rejected: overkill for non-payroll data).

- [ ] **Step 14c.2: Draft ADR-B.8 — org chart frontend library**

Context: B.6 needs a navigable, interactive org chart. Multiple JS libs available: `react-d3-tree`, `dagre-d3`, `react-flow`, `@xyflow/react`.

Decision: `@xyflow/react` (formerly React Flow). It supports drag-drop reordering out of the box, has TypeScript types, active maintenance, and the bundle size impact is acceptable (~150kb minified). Lazy-loaded so users not on org chart pages don't pay the cost.

Alternatives: `react-d3-tree` (rejected: read-only, no drag-drop); `dagre-d3` (rejected: D3-imperative, harder to maintain); custom CSS grid (rejected: reinventing the wheel).

- [ ] **Step 14c.3: Draft ADR-B.9 — severance calculation scope (B vs D)**

Context: B.14 (desvinculación) needs to calculate liquidation. Pay (D) is the full payroll engine. The line between them must be explicit so we don't double-implement or under-deliver.

Decision: B.14 implements **minimum legal calculation only** for liquidación at termination time:
- CTS proporcional (1 sueldo / año, prorrateo del último periodo)
- Vacaciones truncas (días no gozados × jornal)
- Gratificación trunca (proporcional al semestre actual)
- Indemnización por despido arbitrario (1.5 sueldos / año, capped at 12 sueldos)

Sub-proyecto D extends with: AFP/ONP detraction, Renta 5ta, multi-régimen (RLE, MYPE, agraria, etc.), CTS depósito semestral, gratificaciones programadas, retroactivos. The minimum calc in B.14 produces a `SeveranceSettlement` record; D enhances it with the full payroll context.

Alternatives: full liquidation in B.14 (rejected: blurs the B/D boundary); defer all to D (rejected: blocks B.14 desvinculación, which is core HR functionality).

- [ ] **Step 14c.4: Commit**

```bash
cd D:/VYNTIA
git add .planning/audit-B/ADRS.md
git commit -m "docs(B0): ADRs B.7-B.9 (versioning, orgchart lib, severance scope)"
```

---

## Task 15: Self-review + close-out + merge to master

**Files:**
- Read all of `.planning/audit-B/`
- Optionally fix anything inconsistent inline
- Merge to master

- [ ] **Step 15.1: Read all 4 audit docs cover-to-cover**

```bash
cd D:/VYNTIA
wc -l .planning/audit-B/*.md
cat .planning/audit-B/INVENTORY.md | head -100
```

(Use Read tool for each file at full length.)

- [ ] **Step 15.2: Check for consistency**

Verify:
- Every BACKLOG item has a phase that exists in ROADMAP-B.md
- Every phase in ROADMAP-B.md has at least one BACKLOG item (otherwise the phase has no work)
- Every ADR is referenced from at least one INVENTORY chapter or BACKLOG item
- The "Próximo paso inmediato" in the spec maps to "B.1 next" in ROADMAP-B

If anything's inconsistent, fix inline. Don't write a separate fix-up commit; just edit the file in place and amend the previous commit IF it's a typo (or commit a `docs(B0): consistency fix` if substantial).

- [ ] **Step 15.3: Update master roadmap**

In `docs/superpowers/plans/2026-05-09-vyntia-C-multitenancy-master-roadmap.md`, B.0 was never tracked there (that roadmap was C-specific). Skip this step — B has its own roadmap at `.planning/audit-B/ROADMAP-B.md`.

But create a new top-level B roadmap file:

`docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`:

```markdown
# Sub-project B — Vyntia Core Functional — Master Roadmap

> Generated by B.0 audit. Source: `.planning/audit-B/ROADMAP-B.md`.
> Source spec: `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`.

| Phase | Branch | Scope | Plan |
|-------|--------|-------|------|
| B.0   | `vyntia/B0-audit` | Audit & inventory | `2026-05-09-vyntia-B0-audit.md` ✅ merged 2026-05-09 |
| B.1   | `vyntia/B1-polish-baseline` | Polish baseline | TBD |
... (copy from ROADMAP-B.md) ...
```

Use Write to create this file, then add to staging.

- [ ] **Step 15.4: Update CLAUDE.md and ROADMAP_SUBPROJECTS.md**

CLAUDE.md: confirm "Active sub-project: B" (already set during C.8 close-out). No change needed unless something contradicts.

`docs/ROADMAP_SUBPROJECTS.md`: confirm B is the active row. If E and F still show as separate rows, mark them as "absorbed in B" inline:

```markdown
| 11 | **E** | Extensión Organización (positions, org chart) | B | Core extension | (absorbed into B per spec 2026-05-09) |
| 12 | **F** | Policies (gestión políticas SERVIR) | B | GovTech tier | (absorbed into B per spec 2026-05-09) |
```

- [ ] **Step 15.5: Commit + merge to master**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md \
        docs/ROADMAP_SUBPROJECTS.md
# (CLAUDE.md only if changed)
git commit -m "docs(B0): close-out — master roadmap published, E+F absorption noted"
git checkout master
git merge --no-ff vyntia/B0-audit \
  -m "Merge B.0: audit & inventory (4 docs in .planning/audit-B/, master roadmap published)"
git log --graph --oneline -5
```

Verify the merge landed (diamond visible).

⚠️ Do NOT apply a milestone tag for B.0. B.0 is the kickoff phase of B, not a milestone. The tag `b-vyntia-core-complete` comes at the close of B.16.

⚠️ No remote push.

---

## Self-Review

### Spec coverage check

| Spec § requirement | Covered by task |
|---|---|
| § 3.3 INVENTORY.md per-app | Tasks 2-7 |
| § 3.3 INVENTORY.md cross-cutting deuda | Task 8 |
| § 3.3 INVENTORY.md maestro gaps modules 01/02/03 | Tasks 9, 10, 11 |
| § 3.3 BACKLOG.md priority table | Task 12 |
| § 3.3 ROADMAP-B.md confirmed | Task 13 |
| § 3.3 ADRS.md (9 ADRs) | Task 14 (split into 14a, 14b, 14c) |
| § 5.1 baselines preserved | Pytest/tsc/vitest unchanged (B.0 writes no code) |
| Audit timeboxed 3-5 days | 15 tasks × ~30 min each = ~7-8 hours of subagent work + ~7 hours of human review = ~3 days |
| Master roadmap published | Step 15.3 |
| E and F absorption noted | Step 15.4 |

### Spec deviations

1. **Task 14 split into 14a/14b/14c** — 9 ADRs is too much for a single subagent task. Split into 3 thematic groups (cross-cutting infra, technical infra, model+frontend specifics). Each subtask drafts 3 ADRs.

2. **No milestone tag for B.0** — the spec says tag `b-vyntia-core-complete` at the close of B. B.0 is just the kickoff; tag waits for B.16.

3. **Master roadmap created in B.0 (not later)** — having `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md` after B.0 lets subsequent phases (B.1+) reference it consistently. No tracker spec change required.

### Out of scope (deferred)

- Actual implementation of any feature (all phases B.1+).
- ADR research that requires external sources (ed legal CCF/MPP details if maestro is silent — flagged in Task 10/11 for follow-up before that phase starts, not blocking B.0 close-out).
- Performance benchmarking (deferred to B.16 close-out).

### Type consistency

- File paths use `.planning/audit-B/` consistently.
- Phase identifiers `B.0`, `B.1`, ..., `B.16` consistent.
- Branch naming `vyntia/B<N>-<short-name>` consistent.
- Commit prefixes `docs(B0): ...` consistent.
- Document filenames lowercase with hyphens (`provision-tenant.md` style).

### Placeholder scan

- All ADR content drafted is concrete (not "TBD") — only the formal "Status: Proposed" remains until B.0 merges, then they become "Accepted".
- The ROADMAP-B.md skeleton lists all 16 phases by name and branch; only the per-phase plan filename column has TBD because those plans are written in subsequent phases.
- BACKLOG.md skeleton has no real items (Task 12 fills); that's the design.

---

**Plan complete.** When executed, B.0 ships ~16 commits, ~4 documents (~1500 lines), 1 new master roadmap doc. Master gets the merge commit `Merge B.0: audit & inventory`. After B.0 merges, the next step is to write the B.1 plan based on `.planning/audit-B/BACKLOG.md` priorities.
