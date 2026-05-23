# D.0 — Audit & Inventory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a documented, prioritized inventory of: (1) what exists in `apps.payroll/` legacy (to confirm cero-consumo per D-I decision), (2) cross-app touch-points D will consume (Employee, Contract, EmploymentData, SeveranceSettlement, TRegistroDeclaration, audit_lite), (3) regulatory rules backlog derived from `docs/normativa/N06-N09` (~80-120 actionable items), (4) cross-cutting deuda técnica that affects D, (5) 8 architectural decisions (ADRs) that block D.1+. **NO production code is written in this phase.**

**Architecture:** Read-only audit. Source reads: VYNTIA `apps/api/apps/*`, `apps/web/src/features/*`, `docs/normativa/N06-N09`, `docs/modulos/04_*`, and pytest/tsc/lint output. Synthesizes findings into 4 markdown documents (`INVENTORY.md`, `BACKLOG.md`, `ROADMAP-D.md`, `ADRS.md`) committed incrementally on branch `vyntia/D0-audit`. Final merge to `master` is the close-out.

**Tech Stack:** Markdown + git (no Python/JS code touched). Source reading via Read/Grep/Glob.

**Source spec:** `docs/superpowers/specs/2026-05-23-vyntia-D-vyntia-pay-design.md` (commit `bdbe7c02`)
**Source master roadmap:** `docs/superpowers/plans/2026-05-23-vyntia-D-vyntia-pay-master-roadmap.md`

---

## Baseline snapshot

| Check | Expected before D.0 | Expected after D.0 |
|---|---|---|
| Backend pytest | 985 passed, 1 failed (`test_permisos_debug`), 17 skipped | unchanged (no code touched) |
| Frontend build | clean ~10s | unchanged |
| Frontend tsc | 1 error (`BlankEnum.ts` pre-existing) | unchanged |
| Frontend vitest | 178 passed / 28 files | unchanged |
| Frontend ESLint | ≤ 278 warnings | unchanged |
| `manage.py check` | 0 silenced | unchanged |
| `.planning/audit-D/` | doesn't exist | 4 markdown files committed |

D.0 adds: 4 markdown documents (~800-1500 lines combined). 0 lines of code change.

---

## File structure

**Files to create:**

```
.planning/audit-D/
├── INVENTORY.md          # Per-area inventory: payroll-legacy, cross-app touch-points, frontend, tests
├── BACKLOG.md            # Priority table — every actionable item from inventory + regulatory N06-N09
├── ROADMAP-D.md          # CONFIRMED phase structure D.1...D.14 (overrides tentative master roadmap)
└── ADRS.md               # 8 architectural decisions to lock before D.1
```

**Files to read (no modification):**

- `apps/api/apps/payroll/` — 9 legacy models + 2 services + 2 migrations + 1 management command (audit content + confirm cero-consumo)
- `apps/api/apps/contracts/` — read `SeveranceSettlement`, `SeveranceLine`, `Contract`, `EmploymentData`, `TRegistroDeclaration` for touch-points D will consume
- `apps/api/apps/employees/models/employee.py` — Employee fields D will read
- `apps/api/apps/audit_lite/` — payload shape D will extend
- `apps/api/apps/documents/services/access_service.py` — B.12 permission_level D will reuse
- `apps/api/apps/core/` — `business_days_between` if terminal-2 prep work merged
- `apps/web/src/features/payroll/` — frontend payroll legacy
- `apps/web/src/shared/layout/EmployeeLayout.tsx` — portal shell D will reuse
- `docs/00_VYNTIA_MAESTRO.md` § 3 module 04
- `docs/modulos/04_gestion_compensacion.md` — module deep spec
- `docs/normativa/N06_planilla_electronica_sunat.md` — Tabla 22 + PLAME + T-Registro
- `docs/normativa/N07_aportes_pensiones_salud.md` — AFP/ONP/EsSalud/EPS
- `docs/normativa/N08_beneficios_sociales.md` — CTS, Grati, Vacaciones, Util, Asig Fam
- `docs/normativa/N09_renta_5ta_categoria.md` — Renta 5ta
- `docs/normativa/N01_regimen_privado_728.md` — Régimen 728 base
- `docs/comercial/C01_tiers_planes_comerciales.md` — Starter tier definition
- `docs/agent-reports/pm/2026-05-23-empleados-v5.md` — empleados sealed-for-D + deuda diferida

**Files NOT to touch in D.0:**

- Any source code (`.py`, `.ts`, `.tsx`, `.js`, `.css`)
- Any settings file
- Any test file
- Database

---

## Branch

`vyntia/D0-audit` — branched from `master` (HEAD has tag `b-vyntia-core-complete` 2026-05-19 + posterior commits sealed-for-D + nuevo spec commit `bdbe7c02`).

**Pre-flight check:** if currently on `vyntia/D-prep-foundation` (terminal-2 branch), the spec commit `bdbe7c02` is on THAT branch, not master. D.0 audit references the spec by content (file already on disk), so branch can start from master cleanly; merge order will eventually bring D-prep-foundation + D-audit into master independently.

---

## Task 1: Setup branch + audit workspace skeleton

**Files:**
- Create: `.planning/audit-D/INVENTORY.md` (skeleton with empty chapter headings)
- Create: `.planning/audit-D/BACKLOG.md` (skeleton with empty table header)
- Create: `.planning/audit-D/ROADMAP-D.md` (skeleton with the 15-phase outline from master, marked "tentative")
- Create: `.planning/audit-D/ADRS.md` (skeleton with the 8 ADR titles from spec § 5.2)

- [ ] **Step 1.1: Create branch from master**

```bash
cd D:/VYNTIA
git checkout master
git pull origin master  # if remote
git checkout -b vyntia/D0-audit
```

Expected: branch created, HEAD shows `b-vyntia-core-complete` tag ancestor.

- [ ] **Step 1.2: Create audit-D directory + 4 skeleton files**

Use the Write tool to create each of the 4 files with the skeleton content below. Do NOT create them via bash heredoc — the Write tool is the standard.

`.planning/audit-D/INVENTORY.md`:

```markdown
# Vyntia Pay (D) — Inventory (D.0 audit)

> Inventory of: (1) `apps.payroll/` legacy state, (2) cross-app touch-points D will consume, (3) frontend payroll legacy + portal empleado, (4) cross-cutting deuda técnica affecting D.
> Audit date: 2026-05-23.
> Sources: VYNTIA `apps/api/apps/*` and `apps/web/src/features/*`, `docs/normativa/N06-N09`, `docs/modulos/04_*`, maestro `docs/00_VYNTIA_MAESTRO.md`.

## Status legend

- ✅ Implemented and working
- ⚠️ Partial / needs polish
- ❌ Missing / not started
- 🐛 Bug or deuda técnica
- 🗑️ Dead code (to be removed in D.1)

## Section 1 — `apps.payroll/` legacy inventory

(Filled by Task 2.)

## Section 2 — Cross-app touch-points D will consume

(Filled by Task 3.)

## Section 3 — Frontend payroll legacy + portal empleado

(Filled by Task 4.)

## Section 4 — Cross-cutting deuda técnica affecting D

(Filled by Task 5.)

## Section 5 — Regulatory rules inventory (N06-N09)

(Filled by Task 6.)
```

`.planning/audit-D/BACKLOG.md`:

```markdown
# Vyntia Pay (D) — Backlog (D.0 audit)

> Prioritized list of actionable items derived from `INVENTORY.md`. Each item maps to a phase D.X.
> Audit date: 2026-05-23.

## Priority legend

- **P0** — blocks Starter tier launch
- **P1** — important but not launch-blocking; can ship in later phase
- **P2** — nice-to-have; may be deferred to post-D sub-project

## Type legend

- **regulatory** — rule derived from cartilla SUNAT / ley / D.S.
- **bug** — defect in existing code
- **parity** — feature in INTRANET legacy not yet ported (only if D-I greenfield finds anything worth porting)
- **new** — model/service from spec § 4 to build
- **tenant** — multi-tenant readiness fix
- **deuda** — debt cleanup

## Backlog

| # | Item | Area | Type | Prio | Phase | Deps | Estimation | Source/Cita |
|---|------|------|:----:|:----:|:-----:|------|:----------:|-------------|

(Filled by Task 7 — synthesizes from INVENTORY.md.)
```

`.planning/audit-D/ROADMAP-D.md`:

```markdown
# Sub-project D — Master Roadmap (confirmed by D.0 audit)

> Confirmed phase structure for sub-project D. Each phase is a separate branch and PR, mergeable independently.
> Source spec: `docs/superpowers/specs/2026-05-23-vyntia-D-vyntia-pay-design.md`.
> Roadmap version: TENTATIVE (will be confirmed by Task 8 post-audit).

## Phase table

| Fase | Branch | Scope | Necesita | Plan detallado | Sign-off |
|------|--------|-------|----------|----------------|----------|
| D.0  | `vyntia/D0-audit` | Audit & inventory (this phase) | A, C, B | `2026-05-23-vyntia-D0-audit.md` | — |
| D.1  | `vyntia/D1-polish-baseline` | Drop legacy + greenfield skeleton + audit_lite payroll payloads | D.0 | TBD post-D.0 | — |
| D.2  | `vyntia/D2-catalogo-regulatorio` | TaxParameter + PayrollConcept + RegimenConfig + seed | D.1 | TBD | — |
| D.3  | `vyntia/D3-compensation-contract` | Compensation modelo + admin CRUD + migrate command | D.2 | TBD | — |
| D.4  | `vyntia/D4-engine-728` | Regime728Strategy.compute_payslip + golden cartilla | D.2, D.3 | TBD | ⚠️ |
| D.5  | `vyntia/D5-payroll-run-lifecycle` | PayrollRun state machine + PayrollAdjustment | D.4 | TBD | — |
| D.6  | `vyntia/D6-payslip-portal` | PaySlip + PDF + /mis-boletas | D.5 | TBD | — |
| D.7  | `vyntia/D7-cts` | CtsDeposit + compute_cts + alertas | D.4 | TBD | ⚠️ |
| D.8  | `vyntia/D8-gratificaciones` | Gratification + compute_gratification + Bonif Extra | D.4 | TBD | ⚠️ |
| D.9  | `vyntia/D9-plame-exporter` | PlameExporter (10 .txt + ZIP) + validator interno | D.5 | TBD | — |
| D.10 | `vyntia/D10-tregistro-deltas` | PayrollRun.close() auto-genera TRegistroDeclaration | D.5 + B.10 | TBD | — |
| D.11 | `vyntia/D11-afpnet-exporter` | AfpnetExporter .xlsx 25 cols | D.5 | TBD | — |
| D.12 | `vyntia/D12-liquidacion-bbss` | Extiende severance_service con engine real | D.4, D.7, D.8 + B.14 | TBD | ⚠️ |
| D.13 | `vyntia/D13-csv-reopen-adjust` | CSV provisiones + UI REOPENED + Adjustment modal | D.5 | TBD | — |
| D.14 | `vyntia/D14-e2e-close-out` | Playwright lifecycle + docs + tag `d-vyntia-pay-complete` | D.6-D.13 | TBD | — |

## Order and dependencies

(Diagram from master roadmap — reproduce here.)

## Adjustments by audit (filled by Task 8)

(Document any phase additions/removals/reorderings discovered during the audit.)
```

`.planning/audit-D/ADRS.md`:

```markdown
# Sub-project D — Architectural Decision Records

> 8 cross-cutting decisions to lock before D.1 starts coding. Each ADR follows the format:
> Title / Context / Decision / Consequences / Status (proposed | accepted | superseded).

## ADR-D.1: Strategy Pattern interface

(Filled by Task 8.)

## ADR-D.2: Decimal precision policy

(Filled by Task 8.)

## ADR-D.3: audit_lite payload shape `payroll.*`

(Filled by Task 8.)

## ADR-D.4: PayrollRun concurrency

(Filled by Task 8.)

## ADR-D.5: Renta 5ta correction al cese

(Filled by Task 8.)

## ADR-D.6: Tax year cutoff

(Filled by Task 8.)

## ADR-D.7: PVS validator scope

(Filled by Task 8.)

## ADR-D.8: Regulatory sign-off workflow

(Filled by Task 8.)
```

- [ ] **Step 1.3: Verify the 4 files exist**

```bash
cd D:/VYNTIA && ls -la .planning/audit-D/
```

Expected: 4 files (INVENTORY.md, BACKLOG.md, ROADMAP-D.md, ADRS.md).

- [ ] **Step 1.4: Commit skeleton**

```bash
cd D:/VYNTIA
git add .planning/audit-D/
git commit -m "docs(D0): audit workspace skeleton (INVENTORY + BACKLOG + ROADMAP + ADRS)"
```

Expected: 1 commit, 4 new files, ~150 lines.

---

## Task 2: Inventory `apps.payroll/` legacy

**Files:**
- Modify: `.planning/audit-D/INVENTORY.md` — fill Section 1

**Goal:** confirm D-I decision (greenfield is safe = cero consumer activo). If grep finds active consumers of any of the 9 legacy models or 2 services, escalate.

- [ ] **Step 2.1: List all legacy payroll source files**

```bash
cd D:/VYNTIA
find apps/api/apps/payroll/ -type f -name "*.py" | sort
```

Expected: ~13 files (apps.py, models/__init__.py, models/compensation.py, models/tax_parameter.py, services/__init__.py, services/descuento_masivo_service.py, services/planilla_calculo_service.py, migrations/0001_initial.py, migrations/0002_*, management/commands/seed_remuneraciones_config.py, etc.).

- [ ] **Step 2.2: List the 9 legacy model classes**

Use Grep to enumerate classes:

```bash
# Use Grep tool
pattern: "^class "
path: apps/api/apps/payroll/models/
output_mode: content
-n: true
```

Expected: 9 classes (AfpConfiguration, CompensationConfiguration, MonthlyPayroll, PayrollDetail, PayrollConcept, MassDeduction, PaySlip, PaymentSchedule, TaxParameter).

For each class, note: file, line, brief purpose (read 5-10 lines around the class def).

- [ ] **Step 2.3: Check cero-consumo of legacy models (grep external imports)**

For each of the 9 model classes, grep the rest of the codebase:

```bash
# Use Grep tool, per class
pattern: "from apps.payroll.* import.*<ClassName>"
output_mode: files_with_matches
```

AND:

```bash
# Use Grep tool, per class
pattern: "apps.payroll.models.*<ClassName>"
output_mode: files_with_matches
```

AND:

```bash
# Use Grep tool, per class — check string lazy FK
pattern: "['\"]payroll\\.<ClassName>['\"]"
output_mode: files_with_matches
```

Expected for D-I to hold: **zero matches outside `apps/api/apps/payroll/` itself + zero matches in `apps/api/api/v1/*` + zero matches in `apps/web/src/`**. If ANY external match exists, that consumer must be migrated or the model preserved.

- [ ] **Step 2.4: Check cero-consumo of legacy services**

```bash
# Use Grep tool
pattern: "PlanillaCalculoService|DescuentoMasivoService"
glob: "**/*.py"
output_mode: files_with_matches
```

Expected: only matches inside `apps/api/apps/payroll/services/` itself. If a viewset/serializer imports either service, that's a consumer.

- [ ] **Step 2.5: Check cero-consumo of legacy API endpoints**

```bash
# Use Grep tool
pattern: "/api/v1/payroll/|/api/v1/remuneraciones/"
glob: "apps/web/src/**/*.{ts,tsx}"
output_mode: content
-n: true
```

Expected: ZERO matches (any matches mean frontend is wired to legacy backend endpoints — those endpoints must be preserved through D.1 transition or frontend redirected).

- [ ] **Step 2.6: Check legacy frontend consumers**

```bash
# Use Grep tool
pattern: "from .*features/payroll"
glob: "apps/web/src/**/*.{ts,tsx}"
output_mode: content
-n: true
```

Expected: matches confined to `apps/web/src/features/payroll/` itself. Outside matches = consumers to deal with in D.1.

- [ ] **Step 2.7: Fill INVENTORY.md Section 1**

Use Edit tool to replace the `(Filled by Task 2.)` placeholder with:

```markdown
## Section 1 — `apps.payroll/` legacy inventory

### Legacy source files (count: <N>)

| File | LOC | Purpose | D-I disposition |
|---|---|---|---|
| `apps.py` | <N> | App config (default_auto_field, name='apps.payroll') | KEEP (regenerate in D.1) |
| `models/__init__.py` | <N> | Re-exports | 🗑️ DROP (D.1) — replaced by new modular models/ |
| `models/compensation.py` | <N> | 8 model classes (AfpConfiguration, CompensationConfiguration, MonthlyPayroll, PayrollDetail, PayrollConcept, MassDeduction, PaySlip, PaymentSchedule) | 🗑️ DROP (D.1) |
| `models/tax_parameter.py` | <N> | TaxParameter (legacy shape, not compatible with D-E vendor-managed) | 🗑️ DROP (D.1) — D.2 recreates with versioning |
| `services/descuento_masivo_service.py` | <N> | <purpose> | 🗑️ DROP (D.1) |
| `services/planilla_calculo_service.py` | <N> | <purpose> | 🗑️ DROP (D.1) — D.4 reescribe con Strategy |
| `migrations/0001_initial.py` | <N> | Initial schema for legacy 9 models | 🗑️ DROP via squash in D.1 |
| `migrations/0002_*.py` | <N> | <purpose> | 🗑️ DROP via squash in D.1 |
| `management/commands/seed_remuneraciones_config.py` | <N> | <purpose> | 🗑️ DROP (D.1) — D.2 reemplaza con `seed_payroll_catalog` |

### Consumer audit

| Asset | External consumers (count) | Files | D-I disposition |
|---|---|---|---|
| `AfpConfiguration` | <N> | <list or "none">  | <DROP / migrate consumer first> |
| `CompensationConfiguration` | <N> | | |
| `MonthlyPayroll` | <N> | | |
| `PayrollDetail` | <N> | | |
| `PayrollConcept` (legacy) | <N> | | |
| `MassDeduction` | <N> | | |
| `PaySlip` (legacy) | <N> | | |
| `PaymentSchedule` | <N> | | |
| `TaxParameter` (legacy) | <N> | | |
| `PlanillaCalculoService` | <N> | | |
| `DescuentoMasivoService` | <N> | | |
| API endpoints `/api/v1/payroll/*` | <N> | <list> | |
| Frontend `features/payroll/*` | <N> | <list of external importers> | |

### Cero-consumo verdict

- [ ] **PASS** — todos los assets legacy tienen 0 consumers externos. D-I greenfield es seguro sin migration de consumers.
- [ ] **FAIL** — los siguientes consumers requieren tratamiento antes de D.1 drop:
  - <list>

### Pre-D-I migration tasks (if FAIL)

(Only if FAIL. Otherwise omit.)

| # | Consumer | Disposition | Effort |
|---|---|---|---|
```

- [ ] **Step 2.8: Commit Section 1**

```bash
cd D:/VYNTIA
git add .planning/audit-D/INVENTORY.md
git commit -m "docs(D0): INVENTORY Section 1 — apps.payroll/ legacy + cero-consumo audit"
```

---

## Task 3: Inventory cross-app touch-points

**Files:**
- Modify: `.planning/audit-D/INVENTORY.md` — fill Section 2

**Goal:** inventory every model + service D will consume from sister apps (so we know exactly what surface area D depends on, plus where breaking changes in sister apps could hurt D later).

- [ ] **Step 3.1: Inventory `apps.employees.Employee` fields D reads**

Read `apps/api/apps/employees/models/employee.py` and list fields D-Pay engine will read:

- `id` (UUID PK)
- `tenant_id` (FK)
- `numero_documento`, `tipo_documento`
- `nombres_empleado`, `apellido_paterno`, `apellido_materno`
- `fecha_nacimiento`
- (others as discovered)

Note any fields with non-obvious semantics relevant to payroll calculation.

- [ ] **Step 3.2: Inventory `apps.contracts.EmploymentData` fields D reads**

Read `apps/api/apps/contracts/models/employment_data.py`. List fields:

- `empleado` (FK Employee)
- `regimen_laboral` (CharField — for filtering payroll-eligible per `REGIMENES_PLANILLA`)
- `fecha_ingreso`, `fecha_cese`
- `sueldo_basico` (Decimal — to be migrated to Compensation in D.3)
- `estado_datos` (active/inactive filter)
- (others)

Note the `REGIMENES_PLANILLA` constant (currently `('728', '276', '1057', 'practicas')` per spec). D-A says we ship 728 only in MVP; verify what filtering happens elsewhere.

- [ ] **Step 3.3: Inventory `apps.contracts.Contract` and `ContractAmendment`**

Read relevant model files. Note fields D will read (contract dates, status, type).

- [ ] **Step 3.4: Inventory `apps.contracts.Termination`**

Note status flow `draft → in_progress → completed → liquidated → baja_t_registro_done`. D.12 hooks the engine into `compute_settlement()` service. Document the current service signature.

- [ ] **Step 3.5: Inventory `apps.contracts.SeveranceSettlement` + `SeveranceLine`**

Note B.14 minimum legal scope. List the 4 lines currently produced (`cts`, `vac_truncas`, `grat_trunca`, `indemnizacion`). D.12 will replace the formulas with `Regime728Strategy.compute_severance()`.

- [ ] **Step 3.6: Inventory `apps.contracts.TRegistroDeclaration`**

Note B.10 shape: `declaration_type` ('alta'/'baja'/'modificacion'), `status` ('draft'/'validated'/'submitted'/'accepted'/'rejected'). D.10 triggers auto-creation from `PayrollRun.close()`.

- [ ] **Step 3.7: Inventory `apps.audit_lite.AuditEvent`**

Read `apps/api/apps/audit_lite/models.py`. Document current payload shape (event_type, actor_id, target_type, target_id, payload_json?, timestamp). D.1 will register `payroll.*` event_types. Check if schema_version field exists — if not, ADR-D.3 must propose adding it.

- [ ] **Step 3.8: Inventory `apps.documents.services.access_service`**

Read `apps/api/apps/documents/services/access_service.py`. Document `can_access(user, doc)` + `user_permission_level(user)` signatures. D.6 PaySlip permission gate reuses these.

- [ ] **Step 3.9: Inventory `apps.core.business_days`** (if exists)

Check if `apps/api/apps/core/business_days.py` exists (terminal-2 prep work). If yes, document `business_days_between(start, end, region=None)` signature. If NOT yet merged, flag as **prerequisite blocker** for D.4 (needed for CTS deposit due date calculation).

- [ ] **Step 3.10: Fill INVENTORY.md Section 2**

Use Edit tool to replace `(Filled by Task 3.)` with the per-app touch-point report. Format:

```markdown
## Section 2 — Cross-app touch-points D will consume

### apps.employees.Employee

(fields D reads, with current types and any semantic notes)

### apps.contracts.EmploymentData

(fields, `REGIMENES_PLANILLA` constant location, current filter usage)

### apps.contracts.Contract + ContractAmendment

(...)

### apps.contracts.Termination

(...)

### apps.contracts.SeveranceSettlement + SeveranceLine

(... B.14 minimum legal scope + D.12 extension point)

### apps.contracts.TRegistroDeclaration

(... B.10 shape + D.10 trigger point)

### apps.audit_lite.AuditEvent

(... current payload shape + D extension)

### apps.documents.services.access_service

(... PL gate functions D.6 reuses)

### apps.core.business_days

(... or "BLOCKER: not yet merged from terminal-2")
```

- [ ] **Step 3.11: Commit Section 2**

```bash
cd D:/VYNTIA
git add .planning/audit-D/INVENTORY.md
git commit -m "docs(D0): INVENTORY Section 2 — cross-app touch-points D consumes"
```

---

## Task 4: Inventory frontend payroll legacy + portal empleado

**Files:**
- Modify: `.planning/audit-D/INVENTORY.md` — fill Section 3

**Goal:** map current `apps/web/src/features/payroll/` state + confirm `EmployeeLayout` and route discrimination exist for `/mis-boletas` in D.6.

- [ ] **Step 4.1: Inventory `apps/web/src/features/payroll/`**

```bash
find apps/web/src/features/payroll -type f | sort
```

List all .tsx and .ts files. For each, note: (a) is it consumed externally? (b) does it call legacy /api/v1/payroll/ endpoints? (c) D-I disposition.

- [ ] **Step 4.2: Inventory `apps/web/src/shared/layout/EmployeeLayout.tsx`**

Read the file. Document:
- How `EmployeeLayout` wraps content (sidebar + header)
- What menu items exist for `tipo_usuario === 'empleado'`
- How to add `/mis-boletas` cleanly in D.6

- [ ] **Step 4.3: Inventory employee-facing routes**

```bash
# Use Grep tool
pattern: "tipo_usuario === 'empleado'|EmployeeLayout"
glob: "apps/web/src/App.tsx"
output_mode: content
-n: true
```

Document the current route discrimination pattern. D.6 will add `/mis-boletas` as a sibling.

- [ ] **Step 4.4: Inventory boleta-generation code path**

Look for any existing boleta rendering or templates:

```bash
# Use Grep tool
pattern: "boleta|payslip|paySlip|PaySlip"
glob: "apps/api/templates/**/*.html"
output_mode: files_with_matches
```

If any boleta_*.html exists, note it (D.6 may reuse template structure).

- [ ] **Step 4.5: Fill INVENTORY.md Section 3**

Use Edit tool to populate Section 3 with the findings.

- [ ] **Step 4.6: Commit Section 3**

```bash
cd D:/VYNTIA
git add .planning/audit-D/INVENTORY.md
git commit -m "docs(D0): INVENTORY Section 3 — frontend payroll legacy + portal empleado"
```

---

## Task 5: Cross-cutting deuda técnica affecting D

**Files:**
- Modify: `.planning/audit-D/INVENTORY.md` — fill Section 4

**Goal:** capture any pre-existing technical debt (bugs, perf, missing helpers) that D will trip over if not addressed. Cross-reference `docs/agent-reports/pm/2026-05-23-empleados-v5.md` for known sealed-for-D items.

- [ ] **Step 5.1: Run pytest, capture failures**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api
pytest --tb=no -q 2>&1 | tail -30
```

Note any non-baseline failures. Expected baseline: 985 passed, 1 failed (`test_permisos_debug`), 17 skipped.

- [ ] **Step 5.2: Run frontend lint + tsc + vitest**

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -10
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -20
npm test -- --run 2>&1 | tail -20
```

Note baselines: ESLint ≤ 278, tsc 1 (BlankEnum.ts), vitest 178/28.

- [ ] **Step 5.3: Catalog terminal-2 prep items still pending**

Read `docs/agent-reports/pm/2026-05-23-empleados-v5.md` § "Pendientes que el Bloque G NO atendió" and § "3 acciones priorizadas (post v5)". Cross-reference with `git log --oneline -20` to see which were merged.

Document remaining items in Section 4 with `[BLOCKER]` flag if D would hit them.

- [ ] **Step 5.4: Check `Employee.boletas_recientes()` stub status**

```bash
# Use Grep tool
pattern: "boletas_recientes"
output_mode: content
-n: true
```

If still present, flag as `[BLOCKER for D.1]` — colliding with new PaySlip model.

- [ ] **Step 5.5: Check `N+1 EmpleadoListSerializer` fix status**

Verify if terminal-2's perf fix landed:

```bash
git log --oneline --all | grep -i "N+1\|EmpleadoListSerializer"
```

If not merged, flag as `[NICE-TO-HAVE for D.6]` — D dashboards will list empleados.

- [ ] **Step 5.6: Check `business_days_between` + feriados peruanos**

```bash
# Use Glob tool
pattern: "apps/api/apps/core/business_days.py"
```

If missing, flag as `[BLOCKER for D.4]` (CTS deposit due date needs día hábil calc) and `[BLOCKER for D.7]`. D.0 BACKLOG must include "ensure terminal-2 lands before D.4 OR fold into D.4 internal task".

- [ ] **Step 5.7: Fill INVENTORY.md Section 4**

Format:

```markdown
## Section 4 — Cross-cutting deuda técnica affecting D

### Pre-existing baselines (no regresar)

(table from steps 5.1-5.2)

### Sealed-for-D items from v5 PM report still pending

| Item | Source | Affects D phase | Severity for D | Resolution |
|---|---|---|---|---|
| `Employee.boletas_recientes()` stub | empleados-v5 § Pendientes | D.1 | [BLOCKER] | Drop in D.1 (collides with new PaySlip) |
| `business_days_between` + feriados | terminal-2 prep | D.4, D.7 | [BLOCKER] if not merged | Fold into D.4 internal if terminal-2 not done |
| Batch CSV import | terminal-2 prep | D.0 client UX | [NICE-TO-HAVE] | Cliente puede usar UI manual si CSV no listo |
| N+1 EmpleadoListSerializer | terminal-2 prep | D.6 dashboards | [PERF] | Mejora D.6 pero no bloquea |
| V4-N2/N5/N6/N7 from PM v5 | terminal-3 polish | None for D | — | Independent of D |
| ... | | | | |
```

- [ ] **Step 5.8: Commit Section 4**

```bash
cd D:/VYNTIA
git add .planning/audit-D/INVENTORY.md
git commit -m "docs(D0): INVENTORY Section 4 — cross-cutting deuda técnica affecting D"
```

---

## Task 6: Regulatory rules inventory (N06-N09)

**Files:**
- Modify: `.planning/audit-D/INVENTORY.md` — fill Section 5

**Goal:** extract every business rule from `docs/normativa/N06-N09` (the regulatory ground truth) into a structured inventory that becomes the backbone of the BACKLOG. Each rule cites its source for traceability.

This is the densest task — count ~80-120 rules. Take time per source doc.

- [ ] **Step 6.1: Read N06 — Planilla Electrónica SUNAT**

Read `docs/normativa/N06_planilla_electronica_sunat.md`. Extract rules into a structured list:

```markdown
### N06 — Planilla Electrónica SUNAT (PLAME + T-Registro + Tabla 22)

| # | Rule | Citation | Phase affected |
|---|------|----------|---|
| 1 | PLAME = 10 archivos .txt + 1 ZIP | N06 § X | D.9 |
| 2 | T-Registro alta antes de la 24h del primer día | N06 § X | D.10 |
| 3 | Tabla 22 código 0101 = "Alimentación principal dinero" — afecta IT/AFP/EsSalud/CTS | N06 § X | D.2 |
| 4 | Tabla 22 código 0109 = "Gratificación FP" — afecta IT/AFP/NOT EsSalud (Ley 30334)/NOT CTS | N06 § X | D.2 + D.8 |
| ... | (continue for ~25-40 rules) | | |
```

Don't skip — every concept de Tabla 22 que el spec menciona necesita su row.

- [ ] **Step 6.2: Read N07 — Aportes Pensiones Salud**

Same structure for AFP/ONP/EsSalud/EPS/SCTR/SENATI/SENCICO:

```markdown
### N07 — Aportes Pensiones y Salud

| # | Rule | Citation | Phase affected |
|---|------|----------|---|
| 1 | AFP obligatorio 10% remuneración | N07 § X | D.2, D.4 |
| 2 | AFP comisión flujo: tasa variable por AFP | N07 § X | D.2 |
| 3 | AFP comisión mixta: flujo + saldo + prima SISCO | N07 § X | D.2 |
| 4 | Prima SISCO con tope RMA actualizado trimestralmente | N07 § X | D.2 |
| 5 | ONP 13% remuneración | N07 § X | D.2, D.4 |
| 6 | EsSalud 9% empleador | N07 § X | D.4 |
| 7 | EPS crédito 2.25% sobre aporte trabajador | N07 § X | D.4 |
| 8 | SCTR (régimen especial — verificar si aplica 728 base) | N07 § X | D.4 (out-of-scope MVP?) |
| ... | (~15-25 rules) | | |
```

- [ ] **Step 6.3: Read N08 — Beneficios Sociales**

```markdown
### N08 — Beneficios Sociales (CTS, Gratis, Vac, Util, Asig Fam)

| # | Rule | Citation | Phase affected |
|---|------|----------|---|
| 1 | CTS fórmula: (Rem Comp / 12) × meses + (Rem Comp / 360) × días | N08 § 1.3 | D.7 |
| 2 | CTS Rem Computable = básico + asig fam + 1/6 grati + promedio variables si ≥3 meses | N08 § 1.4 | D.7 |
| 3 | CTS períodos: nov-abr → depósito 15-may; may-oct → depósito 15-nov | N08 § 1.5 | D.7 |
| 4 | CTS exclusiones: utilidades, movilidad supeditada, refrigerio no principal, asig por eventos personales, condiciones trabajo (ropa, viáticos), canasta Navidad | N08 § 1.4 | D.7 |
| 5 | CTS trunca al cese: misma fórmula, días desde último depósito, pago directo 48h | N08 § 1.6 | D.7, D.12 |
| 6 | CTS disponibilidad 100% Ley 32322 hasta 31/12/2026 | N08 § 1.7 | D.7 (nota informativa) |
| 7 | Gratificación FP = Rem Comp × (meses trabajados ene-jun / 6) | N08 § 2.3 | D.8 |
| 8 | Gratificación Navidad = Rem Comp × (meses trabajados jul-dic / 6) | N08 § 2.3 | D.8 |
| 9 | Bonificación Extraordinaria Ley 30334 = grati × 9% (EsSalud) o × 6.75% (EPS) | N08 § 2.4 | D.8 |
| 10 | Grati plazo: 1ra quincena jul / 1ra quincena dic | N08 § 2.2 | D.8 |
| 11 | Grati trunca al cese: misma fórmula con meses trabajados parciales | N08 § 2.5 | D.8, D.12 |
| 12 | Vacaciones: 30d/año régimen 728 con récord ≥260 días subordinados | N08 § 3 | D.4 + time_off existing |
| 13 | Vacaciones truncas: (Rem Comp / 360) × días computables | N08 § 3 | D.12 |
| 14 | Asignación Familiar = 10% RMV mensual si tiene hijos < 18 (o > 18 estudiando hasta 24) | N08 § 5 | D.4 |
| 15 | Asignación Familiar NO afecta a CTS gratificación (verificar) | N08 § 5 | D.2 PayrollConcept flags |
| ... | (~20-30 rules) | | |
```

- [ ] **Step 6.4: Read N09 — Renta 5ta Categoría**

```markdown
### N09 — Impuesto a la Renta de 5ta Categoría

| # | Rule | Citation | Phase affected |
|---|------|----------|---|
| 1 | Algoritmo mensual proyectivo: RBA = rem mes × meses_restantes + rem ya pagadas + gratis previstas | N09 § X | D.4 |
| 2 | Renta neta = max(0, RBA - 7 × UIT) | N09 § X | D.4 |
| 3 | Escala progresiva 2026: tramo 1 ≤5UIT × 8%; tramo 2 ≤20UIT × 14%; tramo 3 ≤35UIT × 17%; tramo 4 ≤45UIT × 20%; tramo 5 >45UIT × 30% | N09 § X | D.2, D.4 |
| 4 | Denominador mensual: ene-mar=12; abr=9; may-jul=8; ago=5; sep-nov=4; dic=ajuste final | N09 § X | D.4 |
| 5 | Diciembre ajuste final: impuesto anual - retenido anteriormente | N09 § X | D.4 |
| 6 | Regularización al cese (cese anterior a dic): Renta proyectada vs Renta real → ajuste en boleta final | N09 § X | D.12 (ADR-D.5) |
| 7 | Conceptos NO afectan renta 5ta: indemnización despido, asig matrimonio/fallecimiento, CTS, movilidad supeditada | N09 § X | D.2 PayrollConcept flags |
| ... | (~10-15 rules) | | |
```

- [ ] **Step 6.5: Fill INVENTORY.md Section 5**

Combine all 4 sub-sections (N06, N07, N08, N09) into Section 5. Total expected: ~80-120 rules.

- [ ] **Step 6.6: Commit Section 5**

```bash
cd D:/VYNTIA
git add .planning/audit-D/INVENTORY.md
git commit -m "docs(D0): INVENTORY Section 5 — regulatory rules N06-N09 (~80-120 rules)"
```

---

## Task 7: Synthesize BACKLOG

**Files:**
- Modify: `.planning/audit-D/BACKLOG.md` — fill the priority table

**Goal:** convert INVENTORY findings into actionable, prioritized backlog. Each item maps to a phase D.X. Items derived from:
- Section 1 deuda (legacy drop disposition)
- Section 2 touch-point validations
- Section 3 frontend gaps
- Section 4 deuda técnica blockers
- Section 5 regulatory rules

- [ ] **Step 7.1: Convert legacy drop to BACKLOG items**

For each legacy asset flagged for DROP, create a BACKLOG row:

| # | Item | Area | Type | Prio | Phase | Deps | Est | Source/Cita |
|---|---|---|---|---|---|---|---|---|
| 1 | Drop `apps.payroll.models.AfpConfiguration` + 8 sibling models | payroll | deuda | P0 | D.1 | D.0 | 1h | INV § 1 |
| 2 | Drop `services.planilla_calculo_service.PlanillaCalculoService` | payroll | deuda | P0 | D.1 | D.0 | 30min | INV § 1 |
| 3 | Squash 2 legacy migrations | payroll | deuda | P0 | D.1 | D.0 | 1h | INV § 1 |
| ... | | | | | | | | |

- [ ] **Step 7.2: Convert touch-point findings to BACKLOG items**

Items like:
- "Verify `EmploymentData.REGIMENES_PLANILLA` constant is read-only for D-A (728-only filter)" — P1 — D.0 verification (no code)
- "Document audit_lite.AuditEvent.payload_json shape for ES-compat (ADR-D.3 input)" — P0 — D.0 — produces ADR
- "Reuse `apps.documents.services.access_service.user_permission_level` in PaySlip viewset" — P0 — D.6

- [ ] **Step 7.3: Convert deuda técnica blockers to BACKLOG items**

From Section 4:
- "Coordinate with terminal-2: ensure `business_days_between` merges before D.4 starts" — P0 BLOCKER — pre-D.4
- "Drop `Employee.boletas_recientes()` stub" — P0 — D.1 (already on D-prep-foundation if terminal-2 merged)
- etc.

- [ ] **Step 7.4: Convert regulatory rules to BACKLOG items**

For each rule in Section 5 that translates to code:
- "Implement Tabla 22 PayrollConcept code 0101 con flags IT/AFP/EsSalud/CTS=True, gratis=False" — P0 — D.2 — N06 § X
- "Implement CTS formula CtsService.compute() per N08 § 1.3" — P0 — D.7 — N08 § 1.3
- "Implement Gratificación Bonificación Extraordinaria 9%/6.75% per Ley 30334" — P0 — D.8 — N08 § 2.4
- "Implement Renta 5ta tramo 5 (>45UIT × 30%) per N09 § X" — P0 — D.4 — N09 § X
- etc.

Note rules that are PURELY informational (no code, e.g. "Ley 32322 disponibilidad 100% hasta dic/2026"). Tag as P2/doc/none.

- [ ] **Step 7.5: Final BACKLOG sort + counts**

After all items added, sort by Phase then Prio. Add summary at top:

```markdown
## Summary

- **Total items:** <N>
- **P0:** <N>
- **P1:** <N>
- **P2:** <N>

### By phase

| Phase | P0 | P1 | P2 | Total |
|-------|---:|---:|---:|------:|
| D.1   | <N> | <N> | <N> | <N> |
| D.2   | <N> | <N> | <N> | <N> |
| D.3   | <N> | <N> | <N> | <N> |
| D.4   | <N> | <N> | <N> | <N> |
| D.5   | <N> | <N> | <N> | <N> |
| D.6   | <N> | <N> | <N> | <N> |
| D.7   | <N> | <N> | <N> | <N> |
| D.8   | <N> | <N> | <N> | <N> |
| D.9   | <N> | <N> | <N> | <N> |
| D.10  | <N> | <N> | <N> | <N> |
| D.11  | <N> | <N> | <N> | <N> |
| D.12  | <N> | <N> | <N> | <N> |
| D.13  | <N> | <N> | <N> | <N> |
| D.14  | <N> | <N> | <N> | <N> |
```

Sanity check: expected ~80-150 total items. If <60 or >200, re-examine Section 5 (under-extraction or duplication).

- [ ] **Step 7.6: Commit BACKLOG**

```bash
cd D:/VYNTIA
git add .planning/audit-D/BACKLOG.md
git commit -m "docs(D0): BACKLOG synthesized from INVENTORY (~80-150 items)"
```

---

## Task 8: Draft the 8 ADRs

**Files:**
- Modify: `.planning/audit-D/ADRS.md` — fill all 8 ADRs

**Goal:** lock the 8 architectural decisions before D.1 starts coding. Each ADR follows the standard format and references INVENTORY / BACKLOG / spec.

- [ ] **Step 8.1: ADR-D.1 Strategy Pattern interface**

Replace `(Filled by Task 8.)` for ADR-D.1 with:

```markdown
## ADR-D.1: Strategy Pattern interface

**Status:** accepted

**Context:**
Per D-A, D-Pay ships 728-only but the architecture must support inyectar otros regímenes (CAS, 276, SERVIR, MYPE, Agrario, etc.) sin refactor del engine. Strategy Pattern via ABC con factory.

**Decision:**
Define `RegimenStrategy` (ABC) in `apps/api/apps/payroll/strategies/base.py` con métodos:

```python
class RegimenStrategy(ABC):
    @abstractmethod
    def compute_payslip(self, employee, period: PayrollPeriod) -> PaySlipSnapshot: ...

    @abstractmethod
    def compute_cts(self, employee, semester: CtsSemester) -> CtsResult: ...

    @abstractmethod
    def compute_gratification(self, employee, semester: GratiPeriod) -> GratiResult: ...

    @abstractmethod
    def compute_severance(self, employee, termination_date: date, cause: str) -> SettleResult: ...

    @abstractmethod
    def compute_renta_5ta(self, employee, period: PayrollPeriod, accumulated: Decimal) -> Decimal: ...
```

Dataclass returns son IMMUTABLE (`@dataclass(frozen=True)`).

Factory en `apps/api/apps/payroll/strategies/__init__.py`:

```python
class RegimenStrategyFactory:
    _registry: dict[str, type[RegimenStrategy]] = {}

    @classmethod
    def register(cls, regimen_code: str, strategy_cls: type[RegimenStrategy]) -> None: ...

    @classmethod
    def get(cls, regimen_code: str, as_of_date: date) -> RegimenStrategy:
        cls = cls._registry[regimen_code]
        regimen_config = RegimenConfig.get(regimen_code, as_of_date)
        return cls(regimen_config)
```

`Regime728Strategy` se registra en `apps/api/apps/payroll/strategies/regime_728.py` con `RegimenStrategyFactory.register("728", Regime728Strategy)`.

**Consequences:**
- D.1 crea el skeleton (ABC + factory + stub Regime728Strategy).
- D.4 implementa Regime728Strategy completo.
- Cualquier régimen futuro (post-D) registra su Strategy + RegimenConfig sin tocar el engine.
- Tests del engine son fixture-driven sobre `strategy.compute_*` (puros, sin DB).
- Pros: clean DI, extensible, testable.
- Contras: indirection extra cuando solo hay 1 régimen (acceptable cost for forward-compat).
```

- [ ] **Step 8.2: ADR-D.2 Decimal precision policy**

```markdown
## ADR-D.2: Decimal precision policy

**Status:** accepted

**Context:**
Cálculos de planilla son finanzas peruanas en soles. SUNAT y AFPnet exigen valores en céntimos (2 decimales) pero los cálculos intermedios (tasas, promedios, divisiones por 360) necesitan más precisión para evitar drift.

**Decision:**
- **Intermedios:** `Decimal(14, 4)` — 14 dígitos total, 4 decimales. Suficiente para `999_999_999.9999` (largest realistic intermediate).
- **Finales (montos persisted en `PayrollLine.amount`, `PaySlip.*`, `CtsDeposit.amount`, etc.):** `Decimal(12, 2)` — 12 dígitos total, 2 decimales. Permite `9_999_999_999.99` (suficiente para corporativo grande).
- **Tasas (`TaxParameter.value` cuando `unit='RATE'`):** `Decimal(14, 4)` — ej. `0.0137` para prima SISCO.
- **Redondeo:** `ROUND_HALF_UP` en cada conversion intermedio→final. Estándar SUNAT (verificado en cartilla PVS).
- **Quantize policy:** después de cada `compute_*` retornar montos con `.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

**Consequences:**
- Modelos: `DecimalField(max_digits=12, decimal_places=2)` para campos `amount` finales; `DecimalField(max_digits=14, decimal_places=4)` para `TaxParameter.value` y cómputos intermedios persistidos.
- Test helpers: `assert_money_equal(a, b)` con tolerancia `Decimal("0.00")` (zero tolerance una vez se aplicó quantize).
- Riesgo: divisor 360 en CTS+vac truncas — usar `Decimal` desde input, NO float.
```

- [ ] **Step 8.3: ADR-D.3 audit_lite payload shape `payroll.*`**

```markdown
## ADR-D.3: audit_lite payload shape `payroll.*`

**Status:** accepted (pending audit_lite schema confirmation in INV § 2)

**Context:**
Per D-C, persistencia es CRUD pero audit_lite registra eventos high-stakes con payload shape ES-compatible para forward-compat. Cada fase regulatoria debe emitir eventos persistidos.

**Decision:**
Cada evento payroll persisted en `apps.audit_lite.AuditEvent` con shape:

```json
{
  "event_type": "payroll.run.calculated",
  "schema_version": 1,
  "actor_id": "<UUID identity.User>",
  "tenant_id": "<UUID tenant>",
  "target_type": "PayrollRun",
  "target_id": "<UUID>",
  "payload": {
    "period_year": 2026,
    "period_month": 5,
    "period_type": "REGULAR",
    "total_gross": "150000.00",
    "total_net": "120000.00",
    "total_employer_contributions": "13500.00",
    "slip_count": 50,
    "calculation_duration_ms": 1234
  },
  "occurred_at": "2026-06-01T10:23:45Z"
}
```

Event types canonical:
- `payroll.run.created` (DRAFT)
- `payroll.run.calculated` (DRAFT→CALCULATED)
- `payroll.run.approved` (CALCULATED→APPROVED)
- `payroll.run.closed` (APPROVED→CLOSED)
- `payroll.run.reopened` (CLOSED→REOPENED)
- `payroll.slip.calculated` (per-employee snapshot)
- `payroll.adjustment.applied`
- `cts.deposit.computed`
- `cts.deposit.paid`
- `gratification.computed`
- `gratification.paid`
- `severance.settlement.computed`
- `severance.settlement.paid`

Si `apps.audit_lite.AuditEvent` no tiene `schema_version` field, D.1 lo agrega via migration (preserva backward-compat: `default=1`).

**Consequences:**
- D.1 migration adds `schema_version` to AuditEvent if missing.
- D.5 service emits events on every state transition.
- D.7/D.8/D.12 services emit their respective events.
- Future ES migration can replay these payloads to reconstruct state.
```

- [ ] **Step 8.4: ADR-D.4 PayrollRun concurrency**

```markdown
## ADR-D.4: PayrollRun concurrency

**Status:** accepted

**Context:**
PayrollRun pasa por estados (DRAFT→CALCULATED→APPROVED→CLOSED→REOPENED). Dos operadores podrían intentar cerrar el mismo run simultáneamente. ¿Lock pessimistic o optimistic?

**Decision:**
**Pessimistic locking** via `select_for_update()` en todas las transiciones de status del PayrollRun. Razones:
- Operaciones de cierre son raras (1 por mes) — overhead de lock es trivial.
- Cálculo (CALCULATED transition) puede tomar 30s+ para 50 empleados — ventana para race condition.
- Optimistic locking requiere version field + retry loop — más complejidad para mismo resultado.

Implementación en `PayrollRunService`:

```python
@transaction.atomic
def calculate(self, payroll_run_id: UUID, actor: User) -> None:
    run = PayrollRun.objects.select_for_update().get(pk=payroll_run_id)
    if run.status != "DRAFT":
        raise InvalidTransition(f"Cannot calculate from status={run.status}")
    # ... compute slips ...
    run.status = "CALCULATED"
    run.save()
    AuditEvent.objects.create(event_type="payroll.run.calculated", ...)
```

`PayrollAdjustment` también usa `select_for_update()` sobre el `PayrollRun` para evitar adjustes simultáneos en runs CALCULATED.

**Consequences:**
- Tests deben usar `transaction.atomic` + `pytest.mark.django_db(transaction=True)` para verificar lock real.
- Postgres-only (SQLite local respeta la sintaxis pero no aplica lock real — tests integration corren contra Postgres).
- Sin retry loop necesario.
```

- [ ] **Step 8.5: ADR-D.5 Renta 5ta correction al cese**

```markdown
## ADR-D.5: Renta 5ta correction al cese

**Status:** accepted (pending N09 verification in INV § 5)

**Context:**
N09 § X define un algoritmo PROYECTIVO mensual (RBA = rem mes × meses_restantes + ...) que asume el trabajador permanece hasta diciembre. Cuando un trabajador cesa antes de diciembre, la proyección fue incorrecta — necesita regularización.

**Decision:**
En `Regime728Strategy.compute_renta_5ta` cuando `compute_severance` lo llama (i.e., en contexto cese), aplicar la regularización:

```
1. Calcular Renta real anual:
   real_anual = remuneraciones_pagadas_ene_a_cese + grati_pagadas_ene_a_cese
   renta_neta_real = max(0, real_anual - 7 × UIT_vigente_cese)
   impuesto_anual_real = aplicar_escala_progresiva(renta_neta_real)

2. Sumar retenciones aplicadas previamente:
   total_retenido = sum(payslip.renta_5ta_amount for payslip in periodos_anteriores)

3. Ajuste cese:
   ajuste = impuesto_anual_real - total_retenido
   # Si ajuste > 0: trabajador debe pagar más → descuento adicional en liquidación
   # Si ajuste < 0: trabajador tiene retención excesiva → devolución en liquidación
```

El ajuste se persiste como `SeveranceLine` con `concept='renta_5ta_regularizacion_cese'` y monto positivo o negativo (signed).

**Consequences:**
- D.4 expone `compute_renta_5ta(employee, period, accumulated, mode='monthly'|'cese')`.
- D.12 invoca el modo cese.
- Test fixture: trabajador con sueldo 5000 cesa en agosto → comparar vs cálculo manual.
- Riesgo: trabajadores recontratados en mismo año (cese + reingreso) → fuera de scope MVP, se acumula como dos periods independientes (D.0 NOTA: si surge en cliente piloto, abrir D.x).
```

- [ ] **Step 8.6: ADR-D.6 Tax year cutoff**

```markdown
## ADR-D.6: Tax year cutoff

**Status:** accepted

**Context:**
UIT, RMV, asig familiar cambian cada año (TaxParameter con `valid_from`/`valid_to`). PayrollRun de diciembre 2026 usa UIT 2026 = S/5500. PayrollRun de enero 2027 usa UIT 2027 = S/X. ¿Qué pasa si el PLAME de diciembre se genera en enero (operador cerró tarde)?

**Decision:**
- **Cómputo usa los parámetros vigentes en el ÚLTIMO día del período**, no la fecha de cálculo. Ejemplo:
  - PayrollRun de período Y=2026, M=12, M.last_day=2026-12-31 → usa UIT 2026.
  - PayrollRun de período Y=2027, M=1, M.last_day=2027-01-31 → usa UIT 2027.
- **Lookup:** `TaxParameter.get(code="UIT", as_of_date=period_end_date)`.
- **PayrollRun.create_run** valida que `RegimenConfig.get(regimen, period_end_date)` exista para el régimen del empleado. Si no, error explícito al admin.
- **Grati Navidad pagada en enero por retraso operativo**: el PayrollRun debe ser período 2026-12 con TypePeriod=GRATIFICATION_NAV — los parámetros se calculan con cutoff 2026-12-31 aunque el pago real se ejecute en enero.

**Consequences:**
- D.2 `seed_payroll_catalog` siembra UIT/RMV/asig 2024, 2025, 2026, 2027 (los 4 años cubren retroactivos + forward).
- D.4 nunca usa `today` para parámetros — siempre `period_end_date` derivado del PayrollRun.
- Tests: verificar que cambiar `period_year` cambia UIT usada.
```

- [ ] **Step 8.7: ADR-D.7 PVS validator scope**

```markdown
## ADR-D.7: PVS validator scope

**Status:** accepted

**Context:**
B.10 introdujo 11 reglas en `apps.contracts.services.tregistro_service.validate_pvs()` (RUC checksum, longitudes, fechas, choices, etc.). D.9 PlameExporter necesita validator más completo para los 10 archivos.

**Decision:**
Replicar las reglas de PVS oficial razonablemente conocidas (sin ingeniería inversa del binario PVS real). Set inicial:

**Heredadas de B.10 (11):**
1. RUC empleador: 11 dígitos numéricos + checksum mod 11
2. Documento trabajador: longitud según tipo (DNI=8, CE=9-12)
3. Fecha nacimiento ≤ today
4. Fecha ingreso ≥ fecha nacimiento + 18 años
5. Régimen pensionario ∈ choices oficiales
6. Régimen salud ∈ choices oficiales
7. Modalidad contractual ∈ choices oficiales
8. Tipo trabajo ∈ choices oficiales (N/C/M/P)
9. Sexo ∈ {M, F}
10. Días laborados ∈ [0, 31]
11. Sumatoria (días lab + días subs + días no lab) ≤ días del mes

**Nuevas D.9 (estimación 8-12 más):**
12. Cada PayrollLine.concept.sunat_code está en Tabla 22 vigente
13. Total ingresos PLANI.txt = sum(PayrollLine donde concept.category=INCOME)
14. Total descuentos PLANI.txt = sum(PayrollLine donde concept.category=DEDUCTION)
15. AFP CUSPP presente si pension_regime ∈ AFP_*
16. Aporte AFP empleador en PLANI = remuneración asegurable × 10% (tolerancia ±0.01)
17. Aporte EsSalud = sum_ingresos_afectos × 9% (tolerancia ±0.01)
18. Renta 5ta retenida ≤ tope progresivo (sanity)
19. Asig familiar = 10% RMV vigente período (si applicable)
20. (otros TBD durante implementación D.9)

**Consequences:**
- D.9 implementa `apps/api/apps/payroll/services/pvs_validator.py` con ~20 reglas + tests fixture-driven.
- Si el cliente piloto reporta PLAME rechazado por SUNAT con regla no replicada, D.x agrega la regla retrospectivamente.
- NO replica reglas de business semánticas (ej. "el sueldo no puede ser <RMV") — eso es validación del modelo en D.3.
```

- [ ] **Step 8.8: ADR-D.8 Regulatory sign-off workflow**

```markdown
## ADR-D.8: Regulatory sign-off workflow

**Status:** accepted

**Context:**
D-H decision: validation tier 4 requires user sign-off antes de merge de fases regulatorias D.4, D.7, D.8, D.12.

**Decision:**
Template `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md` con shape:

```markdown
# D.<N> <PhaseName> — Regulatory Sign-off

**Phase:** D.<N> · **Branch:** vyntia/D<N>-<name> · **Date generated:** YYYY-MM-DD

## Test results summary

- Tier 1 pytest unit: <N>/<N> passed
- Tier 2 pytest integration: <N>/<N> passed
- Cartilla SUNAT golden cases: <N>/<N> matched
- Benchmark Sentinel/Buk (opcional): <N>/<N> matched within ±0.01 PEN

## Scenarios computed

| # | Caso | Input (resumen) | Expected (cita normativa) | Computed | Match | Sentinel/Buk |
|---|------|----------------|---------------------------|----------|-------|--------------|
| 1 | Sueldo plano 3000, 30 días | basico=3000, dias=30, sin asig fam | gross=3000, AFP=300, neto=2700 (N07 § 1.2) | gross=3000, AFP=300, neto=2700 | ✓ | S/2700 ✓ |
| 2 | ... | ... | ... | ... | ✓/✗ | ... |
| ... (30 casos) | | | | | | |

## Notes / observaciones del autor

(El autor de la fase explica decisiones edge-case, qué reglas se omiten/postergan, etc.)

## Sign-off

- [ ] **APPROVED** — <user>, <ISO date>, comentario opcional
- [ ] **CHANGES_REQUESTED** — <user>, <ISO date>, razón obligatoria

## Estado actual

`regulatory_audit: pending | approved | changes_requested`
```

**Workflow:**
1. Al cerrar la fase D.<N>, el autor (Claude o user) genera el file llenando la tabla con los resultados de los tests + cita normativa per row.
2. Authors solicitan sign-off al user pegando link al file en mensaje de la terminal.
3. User abre el file, revisa, escribe APPROVED o CHANGES_REQUESTED y commitea el cambio en mismo branch.
4. Merge del PR queda gated en script `scripts/check_regulatory_signoff.sh` (D.0 BACKLOG agrega ese script como item de D.1) que verifica:
   - Si fase es D.4/D.7/D.8/D.12: existe `REGULATORY-SIGNOFF.md` con `APPROVED` checked
   - Si checked CHANGES_REQUESTED o ambos vacíos: exit 1
5. Tag final `d-vyntia-pay-complete` (D.14) verifica las 4 phases tienen sign-off APPROVED commiteado en master.

**Consequences:**
- 4 phases con artefactos extra de ~50-200 líneas c/u.
- ~1-2 días de latency por sign-off (acceptable, fase queda en branch).
- Trazabilidad regulatoria: ante reclamo SUNAFIL, los `REGULATORY-SIGNOFF.md` commiteados son evidencia de que el cálculo fue revisado por persona con expertise.
```

- [ ] **Step 8.9: Commit ADRs**

```bash
cd D:/VYNTIA
git add .planning/audit-D/ADRS.md
git commit -m "docs(D0): ADRS — 8 architectural decisions for D-Pay (ADR-D.1..D.8)"
```

---

## Task 9: Confirm + adjust ROADMAP-D

**Files:**
- Modify: `.planning/audit-D/ROADMAP-D.md` — fill "Adjustments by audit" section

**Goal:** transform TENTATIVE roadmap into CONFIRMED. Apply any adjustments discovered during the audit (splits, additions, removals, dependency changes).

- [ ] **Step 9.1: Review BACKLOG counts per phase**

Open `.planning/audit-D/BACKLOG.md` summary table. Note:
- Any phase with >40 P0 items → consider split
- Any phase with <3 items → consider merge with neighbor
- Any new dependency between phases (e.g., terminal-2 prep BLOCKER for D.4)

- [ ] **Step 9.2: Apply adjustments**

Update `ROADMAP-D.md` phase table if:
- D.4 needs split into D.4 (engine ingresos+descuentos) + D.4b (Renta 5ta + EsSalud)
- D.9 needs split into D.9 (3 archivos críticos) + D.9b (7 archivos complementarios)
- Any phase added/removed
- Dependencies revised based on actual touch-point findings

Replace `(Document any phase additions/removals/reorderings discovered during the audit.)` placeholder with the structured adjustments + rationale.

If NO adjustments needed (BACKLOG counts are balanced, dependencies hold), explicitly state:

```markdown
## Adjustments by audit (filled by Task 9)

No adjustments required. The 15-phase tentative outline holds after audit:
- All phases have ≥5 P0 items and ≤40 P0 items.
- All inter-phase dependencies verified (see Section X).
- No splits needed.
- No phases removable.

ROADMAP version: **CONFIRMED** 2026-05-23.
```

- [ ] **Step 9.3: Final pre-flight check + commit**

```bash
cd D:/VYNTIA
git add .planning/audit-D/ROADMAP-D.md
git commit -m "docs(D0): ROADMAP-D CONFIRMED (adjustments applied per audit)"
```

---

## Task 10: Pre-merge audit verification + close-out

**Files:**
- Read-only verification + final commit message updating master roadmap

- [ ] **Step 10.1: Verify all 4 audit files complete**

```bash
cd D:/VYNTIA
ls -la .planning/audit-D/
wc -l .planning/audit-D/*.md
```

Expected file sizes:
- `INVENTORY.md` ≥ 400 lines
- `BACKLOG.md` ≥ 200 lines (table rows)
- `ROADMAP-D.md` ≥ 100 lines
- `ADRS.md` ≥ 250 lines (8 ADRs × ~30 lines each)

- [ ] **Step 10.2: Verify no placeholders left**

```bash
# Use Grep tool
pattern: "TBD|TODO|\\(Filled by Task|FIXME"
glob: ".planning/audit-D/*.md"
output_mode: content
-n: true
```

Expected: 0 matches. Only acceptable TBD is in BACKLOG `Source/Cita` column for rules where citation needs spot-fix (max 5 total).

If any `(Filled by Task N.)` placeholder remains, that task was skipped — go fill it.

- [ ] **Step 10.3: Verify baselines unchanged (pytest/vitest/build)**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api && pytest --tb=no -q 2>&1 | tail -3
```

Expected: 985 passed, 1 failed (`test_permisos_debug` pre-existing), 17 skipped — IDENTICAL to baseline.

```bash
cd D:/VYNTIA/apps/web
npm run lint 2>&1 | tail -3
npx tsc --noEmit -p tsconfig.app.json 2>&1 | tail -5
npm test -- --run 2>&1 | tail -5
```

Expected: lint ≤ 278, tsc 1 (BlankEnum.ts), vitest 178/28.

If any baseline regressed: D.0 introduced code change (forbidden). Investigate — likely accidental modification. Revert + re-run.

- [ ] **Step 10.4: Verify master roadmap reflects CONFIRMED state**

Update `docs/superpowers/plans/2026-05-23-vyntia-D-vyntia-pay-master-roadmap.md` if D.0 audit produced adjustments:
- Change "TENTATIVE" → "CONFIRMED 2026-05-23"
- Cross-reference `.planning/audit-D/ROADMAP-D.md` as source-of-truth

(If no adjustments per Task 9.2 "NO adjustments required" branch, only change TENTATIVE→CONFIRMED.)

- [ ] **Step 10.5: Final commit + merge prep**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-05-23-vyntia-D-vyntia-pay-master-roadmap.md
git commit -m "docs(D0): master roadmap CONFIRMED post-audit"
git log --oneline master..HEAD
```

Expected: ~10 commits on branch `vyntia/D0-audit` (one per Task 1.4 + 2.8 + 3.11 + 4.6 + 5.8 + 6.6 + 7.6 + 8.9 + 9.3 + 10.5).

- [ ] **Step 10.6: Open PR for merge**

```bash
cd D:/VYNTIA
git push origin vyntia/D0-audit  # if remote configured
# Otherwise: merge directly
git checkout master
git merge --no-ff vyntia/D0-audit -m "Merge D.0 audit — INVENTORY + BACKLOG + ROADMAP + ADRS"
git tag d0-audit-done  # optional, marker
```

Expected: 1 merge commit on master, branch preserved.

- [ ] **Step 10.7: Verify post-merge baselines**

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api && pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA/apps/web && npm run build 2>&1 | tail -3
```

Expected: same baselines (D.0 was docs-only).

---

## D.0 Done — Handoff to D.1

Outputs ready for D.1 planning:
- `.planning/audit-D/INVENTORY.md` — every consumer + touch-point catalogued
- `.planning/audit-D/BACKLOG.md` — every item D.1-D.13 will close, scoped per phase
- `.planning/audit-D/ROADMAP-D.md` — CONFIRMED phase structure
- `.planning/audit-D/ADRS.md` — 8 locked decisions
- `docs/superpowers/plans/2026-05-23-vyntia-D-vyntia-pay-master-roadmap.md` — updated status

Next step: generate `2026-05-XX-vyntia-D1-polish-baseline.md` cuando arranque D.1 (incorporando cualquier lección de D.0). Use writing-plans skill con BACKLOG D.1 rows como source.
