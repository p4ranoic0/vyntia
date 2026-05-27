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

### Legacy source files (count: 14)

| File | LOC | Purpose | D-I disposition |
|---|---|---|---|
| `apps.py` | 37 | App config (`default_auto_field`, `name='apps.payroll'`) | KEEP (regenerate in D.1 with same name) |
| `models/__init__.py` | 25 | Re-exports all 9 model classes | 🗑️ DROP (D.1) — replaced by new modular `models/` |
| `models/compensation.py` | 614 | 8 model classes: `AfpConfiguration`, `CompensationConfiguration`, `MonthlyPayroll`, `PayrollDetail`, `PayrollConcept`, `MassDeduction`, `PaySlip`, `PaymentSchedule` | 🗑️ DROP (D.1) — D.2–D.6 recreate with compliant shape |
| `models/tax_parameter.py` | 85 | `TaxParameter` — stores UIT by fiscal year; limited to 4ta-cat fields only (not 5ta escala) | 🗑️ DROP (D.1) — D.2 recreates with `unit` field + versioning |
| `services/__init__.py` | 12 | Re-exports `PlanillaCalculoService`, `DescuentoMasivoService` | 🗑️ DROP (D.1) |
| `services/planilla_calculo_service.py` | 342 | `PlanillaCalculoService` — computes `MonthlyPayroll` details (haberes, AFP/ONP, EsSalud, renta 4ta); **no renta 5ta, no Strategy pattern** | 🗑️ DROP (D.1) — D.4 reescribe con `Regime728Strategy` |
| `services/descuento_masivo_service.py` | 352 | `DescuentoMasivoService` — parses Excel (openpyxl) and applies `MassDeduction` records to `PayrollDetail` | 🗑️ DROP (D.1) — D.13 reemplaza con CSV provisiones |
| `migrations/0001_initial.py` | 337 | Initial schema for all 9 legacy models | 🗑️ DROP via squash in D.1 |
| `migrations/0002_remove_afpconfiguration_uniq_config_afp_nombre_vigencia_and_more.py` | 104 | Constraint rename migration (adds `_per_tenant` suffix to 5 UniqueConstraints) | 🗑️ DROP via squash in D.1 |
| `management/commands/seed_remuneraciones_config.py` | 113 | Seeds UIT + AFP rates from SBS; imports `AfpConfiguration`, `TaxParameter` | 🗑️ DROP (D.1) — D.2 reemplaza con `seed_payroll_catalog` |
| `management/__init__.py` | 0 | Package marker | 🗑️ DROP (D.1) |
| `management/commands/__init__.py` | 0 | Package marker | 🗑️ DROP (D.1) |
| `migrations/__init__.py` | 0 | Package marker | KEEP (required by Django) |
| `__init__.py` | 0 | Package marker | KEEP |

**Total non-empty LOC:** 2,021 (across 14 files; 4 are empty `__init__.py` / package markers).

### Model class quick reference

| Class | File | Line | Brief purpose |
|---|---|---|---|
| `AfpConfiguration` | `compensation.py` | 10 | AFP rates per `vigencia_mes` (YYYY-MM): `aporte_obligatorio_pct` 10%, `comision_flujo_pct`, `comision_mixta_pct`, `prima_seguro_pct`, `remuneracion_max_asegurable` |
| `CompensationConfiguration` | `compensation.py` | 69 | Concept catalog (income/deduction): `tipo`, `codigo`, `nombre`, `porcentaje`, `monto_fijo`, `aplica_base_imponible` |
| `MonthlyPayroll` | `compensation.py` | 131 | Payroll header per period+modalidad; states: `borrador→procesando→generada→aprobada→pagada→anulada`; totals denormalized |
| `PayrollDetail` | `compensation.py` | 241 | Per-employee line within `MonthlyPayroll`; snapshot of all haberes/descuentos/neto fields |
| `PayrollConcept` | `compensation.py` | 397 | Variable concepts applied to `PayrollDetail` (linked to `CompensationConfiguration`) |
| `MassDeduction` | `compensation.py` | 444 | Excel-uploaded bulk deductions for a period; states: `pendiente→procesado→aplicado→anulado` |
| `PaySlip` | `compensation.py` | 508 | PDF boleta linked 1-to-1 to `PayrollDetail`; stores `archivo_pdf`, `hash_documento` |
| `PaymentSchedule` | `compensation.py` | 558 | Payment calendar entry linked to `MonthlyPayroll`; scheduled vs executed dates |
| `TaxParameter` | `tax_parameter.py` | 12 | UIT by fiscal year (`anio`); only stores `tope_renta_cuarta_uit` and `porcentaje_renta_cuarta` — **missing renta 5ta brackets** |

### Consumer audit

| Asset | External consumers (count) | Files | D-I disposition |
|---|---|---|---|
| `AfpConfiguration` | **2** | `apps/api/api/v1/rrhh/views.py` (line 8), `apps/api/api/v1/rrhh/serializers.py` (line 7) | ⚠️ CONSUMER EXISTS — migrate consumers before D.1 drop |
| `CompensationConfiguration` | **2** | `apps/api/api/v1/rrhh/views.py` (line 8), `apps/api/api/v1/rrhh/serializers.py` (line 7) | ⚠️ CONSUMER EXISTS — migrate consumers before D.1 drop |
| `MonthlyPayroll` | 0 | none | ✅ DROP (D.1) safe |
| `PayrollDetail` | 0 | none | ✅ DROP (D.1) safe |
| `PayrollConcept` (legacy) | 0 | none | ✅ DROP (D.1) safe |
| `MassDeduction` | 0 | none | ✅ DROP (D.1) safe |
| `PaySlip` (legacy) | 0 | none | ✅ DROP (D.1) safe |
| `PaymentSchedule` | 0 | none | ✅ DROP (D.1) safe |
| `TaxParameter` (legacy) | 0 (only `seed_remuneraciones_config.py` — internal to payroll mgmt cmd) | `apps/api/apps/payroll/management/commands/seed_remuneraciones_config.py` | ✅ DROP (D.1) safe (mgmt cmd self-contained, drops with payroll) |
| `PlanillaCalculoService` | **1** | `apps/api/api/v1/rrhh/remuneraciones_views.py` (line 23, used at lines 463, 928, 972) | ⚠️ CONSUMER EXISTS — `remuneraciones_views.py` instantiates it; must be replaced in D.1 |
| `DescuentoMasivoService` | **1** | `apps/api/api/v1/rrhh/remuneraciones_views.py` (line 23, used at lines 928, 972) | ⚠️ CONSUMER EXISTS — same view; must be replaced in D.1 |
| API endpoints `/api/v1/payroll/*` | **2 locations** | `apps/web/src/features/payroll/services/payrollService.ts` (all CRUD calls), `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` (line 144: `/api/v1/payroll/monthly-runs/`) | ⚠️ CONSUMERS EXIST — frontend fully wired to legacy endpoints; D.1 must preserve or redirect |
| Frontend `features/payroll/*` external importers | **1 file** | `apps/web/src/App.tsx` (lines 33–39: imports 7 page components from `@/features/payroll/pages/`) | ⚠️ CONSUMER EXISTS — `App.tsx` imports 7 payroll pages; these are routing imports (expected), not business-logic coupling |

### Cero-consumo verdict

- [ ] **PASS**
- [x] **FAIL** — los siguientes consumers requieren tratamiento antes de D.1 drop:
  - `apps/api/api/v1/rrhh/views.py` — imports `AfpConfiguration`, `CompensationConfiguration` from `apps.payroll.models`
  - `apps/api/api/v1/rrhh/serializers.py` — imports `AfpConfiguration`, `CompensationConfiguration` from `apps.payroll.models`
  - `apps/api/api/v1/rrhh/remuneraciones_views.py` — imports and instantiates `PlanillaCalculoService` and `DescuentoMasivoService`
  - `apps/web/src/features/payroll/services/payrollService.ts` — calls 30+ `/api/v1/payroll/*` endpoints
  - `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` — calls `/api/v1/payroll/monthly-runs/` (line 144)
  - `apps/web/src/App.tsx` — imports 7 page components from `@/features/payroll/pages/` (routing; expected, low-risk)

### Pre-D-I migration tasks (if FAIL)

| # | Consumer | Disposition | Effort |
|---|---|---|---|
| 1 | `api/v1/rrhh/views.py` + `serializers.py` import `AfpConfiguration`, `CompensationConfiguration` | Replace with new D.2 models or remove if views replaced wholesale in D.1 | 2h |
| 2 | `api/v1/rrhh/remuneraciones_views.py` uses `PlanillaCalculoService` + `DescuentoMasivoService` | Replace with stub 501-or-redirect view in D.1; full replacement in D.4+D.13 | 3h |
| 3 | `apps/web/src/features/payroll/services/payrollService.ts` calls 30+ `/api/v1/payroll/*` endpoints | Keep legacy endpoints wired during D.1–D.5 transition; replace endpoints per phase D.2→D.6 | 0h now (D.1 task) |
| 4 | `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` calls `/api/v1/payroll/monthly-runs/` | Guard with try/catch or feature flag until D.5 provides real endpoint | 1h |
| 5 | `apps/web/src/App.tsx` imports 7 payroll page components | Low-risk routing import; keep pages functional through D.1–D.6; no action required at D.1 | 0h |

## Section 2 — Cross-app touch-points D will consume

### apps.employees.Employee

**File:** `apps/api/apps/employees/models/employee.py` | **Table:** `empleado`

Fields D-Pay engine will read:

| Field | Type | Semantic notes for D |
|---|---|---|
| `id` | `UUIDField` (PK) | Primary join key across all D models |
| `tenant` | FK → `tenancy.Tenant` | Row-level isolation — every D query must filter by tenant |
| `numero_documento` | `CharField(20)` | Identifier on boleta header; must match T-Registro worker_doc_number |
| `tipo_documento` | `CharField(10)` | Choices: `DNI`, `CE`, `PASAPORTE`, `OTROS`; maps to SUNAT Tabla 2 codes in TRegistroDeclaration |
| `nombres_empleado` | `CharField(100)` | Boleta header first line |
| `apellido_paterno` | `CharField(100)` | Boleta header |
| `apellido_materno` | `CharField(100)` | Boleta header |
| `fecha_nacimiento` | `DateField` (nullable) | Age at period close → drives AFP prima SISCO eligibility ceiling |
| `estado_empleado` | `CharField(15)` | Choices: `activo`, `inactivo`, `suspendido`, `cesado`. D only processes `activo` employees in a PayrollRun |
| `genero_empleado` | `CharField(15)` | Choices: `masculino`, `femenino`, `otro`, `no_especifica`; needed for T-Registro `worker_gender` field |
| `estado_civil` | `CharField(15)` | Informational for boleta header |
| `direccion_domicilio` | `CharField(200)` | Boleta header address block |
| `distrito_domicilio` | `CharField(100)` | Boleta header address block |
| `sistema_pensiones` | `CharField(20)` | **Critical for D.4.** Choices: `ONP`, `AFP PRIMA`, `AFP INTEGRA`, `AFP PROFUTURO`, `AFP HABITAT`, plus `PENSIONISTA-*`, `SIN PENSION`. Drives ONP (13%) vs AFP (10% + comisión + prima) branch in compute_payslip |
| `tipo_comision` | `CharField(10)` (nullable) | `FLUJO` or `MIXTA` — AFP commission method. D.4 reads this to select correct AFP rate row from TaxParameter |
| `codigo_cuspp` | `CharField(20)` (nullable) | AFP CUSPP code; needed in TRegistroDeclaration + AFPnet export |
| `tipo_seguro_salud` | `CharField(10)` | Choices: `ESSALUD`, `EPS`, `PRIVADO`, `NINGUNO`; D.4 switches employer EsSalud 9% vs EPS credit 2.25% path |
| `es_padre_familia` | `BooleanField` | Used with `asignacion_familiar` — note: actual family-member eligibility check is in `apps.employees.FamilyMember`, not this flag alone |
| `tiene_suspension_renta_cuarta_vigente` | `BooleanField` | If True + `fecha_inicio/fin_suspension_renta` covers the period, renta 5ta retention is suppressed for that period |
| `entidad_bancaria` | `CharField(100)` | For payment disbursement metadata on boleta |
| `numero_cuenta_bancaria` | `CharField(30)` | Payment disbursement |
| `numero_cci` | `CharField(30)` | CCI for interbank transfer |

**Non-obvious semantics:**
- `tenant` is nullable (`null=True, blank=True`) at the model level but constrained via `UniqueConstraint(["tenant", "numero_documento"])` — in practice every production row has a non-null tenant.
- There is NO `nombre_completo` database column; it is a `@property` → `f"{nombres_empleado} {apellido_paterno} {apellido_materno}"`. Do not reference in ORM `.values()` calls.
- `estado_empleado` is independent of `EmploymentData.estado_datos`; an employee can be `activo` with an `inactivo` EmploymentData record. D must join both and filter `estado_datos='activo'` as well.
- Pension system split: the employee carries their own `sistema_pensiones` and `tipo_comision`, not the EmploymentData — D.4 reads directly from Employee, not from EmploymentData.

---

### apps.contracts.EmploymentData

**File:** `apps/api/apps/contracts/models/employment_data.py` | **Table:** `datos_laborales`

Fields D reads:

| Field | Type | Semantic notes for D |
|---|---|---|
| `id` | `UUIDField` (PK) | |
| `empleado` | FK → `employees.Employee` | Reverse accessor: `employee.datos_laborales` |
| `tenant` | FK → `tenancy.Tenant` | Tenant isolation |
| `area` | FK → `organization.Department` | Department for PayrollRun grouping/reporting. Department has NO `nombre` field — use `siglas_area` or `nombre_unidad_organica` |
| `regimen_laboral` | `CharField(20)` | **Primary eligibility gate for D.** See `REGIMENES_PLANILLA` constant below |
| `fecha_ingreso` | `DateField` | Seniority start — used by CTS, gratification, indemnization calculations |
| `fecha_inicio_contrato` | `DateField` | Contract validity window start |
| `fecha_fin_contrato` | `DateField` (nullable) | Contract end; NULL = indefinite |
| `fecha_cese` | `DateField` (nullable) | Cessation date; if set, employee is no longer in active payroll |
| `sueldo_basico` | `DecimalField(10,2)` | **Current source of basic salary for D.3 migration.** D.3 introduces `Compensation` model; until then D reads this field. |
| `asignacion_familiar` | `DecimalField(8,2)` | Already denormalized here as amount. D.4 must verify this reflects 10% of RMV per N08 § 5 — the field is a stored amount, not computed dynamically |
| `bonificacion_especial` | `DecimalField(8,2)` | Ad-hoc special bonus — not an AFP/CTS-affecting concept by default |
| `otras_bonificaciones` | `DecimalField(8,2)` | Catch-all; D must determine Tabla-22 classification for each bonus before including in remuneración computable |
| `estado_datos` | `CharField(15)` | `activo`, `inactivo`, `suspendido`. D filters `estado_datos='activo'` |
| `cargo_empleado` | `CharField(100)` | Job title string on boleta |
| `jornada_laboral` | `CharField(15)` | `completa`, `parcial`, `por_horas` — affects proportional calcs for part-time |
| `horas_semanales` | `DecimalField(4,2)` | Default 40.00 — used in pro-rata for part-time payroll |
| `position` | FK → `organization.Position` (nullable) | B.6 catalog FK; `cargo_empleado` string preserved as legacy |

**`REGIMENES_PLANILLA` constant** — defined at line 292 of employment_data.py:

```python
REGIMENES_PLANILLA = ('728', '276', '1057', 'practicas')
```

Locación (`locacion`) and consultoría (`consultoria`) are civil contracts (4ta categoría) and are **excluded** from T-Registro/PLAME. D-A ships 728-only in MVP; the filter used in D.4 should be:

```python
EmploymentData.objects.filter(
    regimen_laboral='728',
    estado_datos='activo',
    fecha_cese__isnull=True,
    tenant=tenant,
)
```

**Important:** The `REGIMEN_LABORAL_CHOICES` list on the model does NOT include `'mype'` — the spec notes D-A ships 728 only, but also notes MyPE employees may have 728+15 vacation days. The hardcoded vacation map `_DIAS_VACACIONES_ANUALES_POR_REGIMEN` at line 308 includes a TODO for sub-project D to replace with configurable `RegimenLaboralConfig`.

**UniqueConstraint:** `['empleado', 'fecha_inicio_contrato']` — one EmploymentData row per employee per contract start date.

---

### apps.contracts.Contract + ContractAmendment

**Files:** `contract.py` (table: `contratos_adendas`) + `contract_amendment.py` (table: `contract_amendments`)

**Contract fields D reads:**

| Field | Type | Semantic notes for D |
|---|---|---|
| `id` | `UUIDField` (PK) | |
| `empleado` | FK → `employees.Employee` | Via `employee.contratos_adendas` reverse accessor |
| `tenant` | FK → `tenancy.Tenant` | |
| `numero_contrato` | `CharField(50)` | Unique per tenant via constraint |
| `tipo_documento` | `CharField(25)` | Choices include `LEY_728_FIJO`, `LEY_728_INDETERMINADO`, `LEY_728_FIJO_SUPLENCIA` — D.10 auto-creates TRegistroDeclaration based on this |
| `fecha_inicio` | `DateField` | Contract start — used by `severance_service.compute_settlement` |
| `fecha_fin` | `DateField` (nullable) | NULL for indefinite contracts |
| `salario_bruto` | `DecimalField(10,2)` | Gross salary snapshot on contract. Note: `severance_service` reads `contract.salario_bruto` directly, NOT `EmploymentData.sueldo_basico` |
| `status` | `CharField(15)` | DB column `estado`. Choices: `BORRADOR`, `PENDIENTE`, `ACTIVO`, `VENCIDO`, `TERMINADO`, `ANULADO`. D only processes `ACTIVO` contracts |
| `area` | FK → `organization.Department` | Has direct area FK (unlike EmploymentData path) |

**⚠️ Salary data divergence risk:** `Contract.salario_bruto` and `EmploymentData.sueldo_basico` are stored independently. After a salary amendment, only `EmploymentData.sueldo_basico` may be updated (or only `Contract` via `ContractAmendment.nuevo_salario`). D.3 must establish `Compensation` as the single source of truth and reconcile these two fields.

**ContractAmendment fields D reads (for D.3 salary history):**

| Field | Type | Semantic notes for D |
|---|---|---|
| `id` | `UUIDField` (PK) | |
| `parent_contract` | FK → `contracts.Contract` | Reverse accessor: `contract.amendments` |
| `tipo_documento` | `CharField(25)` | `ADENDA_SALARIAL`, `ADENDA_CARGO`, `ADENDA_HORARIO`, `ADENDA_EXTENSION` |
| `fecha_inicio` | `DateField` | Effective date of amendment |
| `nuevo_salario` | `DecimalField(10,2)` (nullable) | New gross salary (only for `ADENDA_SALARIAL`) |
| `status` | `CharField(15)` | Same choices as Contract.status |

---

### apps.contracts.Termination

**File:** `apps/api/apps/contracts/models/termination.py` | **Table:** `termination`

**Status flow:**

```
draft → in_progress → completed → liquidated → baja_t_registro_done
                                              ↘ (cancelled from any state except baja_t_registro_done)
```

**Key fields D reads:**

| Field | Type | Semantic notes for D |
|---|---|---|
| `id` | `UUIDField` (PK) | |
| `tenant` | FK → `tenancy.Tenant` | |
| `contract` | OneToOneField → `contracts.Contract` | Reverse: `contract.termination` |
| `employee` | FK → `employees.Employee` | Reverse: `employee.terminations` |
| `regimen` | `CharField(10)` | `728`, `276`, `cas`, `mype`, `otros` — drives which CAUSALES apply |
| `causal` | `CharField(30)` | See CAUSALES list; `despido_arbitrario` and `despido_indirecto` trigger `indemnizacion` line in settlement |
| `status` | `CharField(30)` | Flow above; D.12 hooks in at `completed` status |
| `fecha_cese` | `DateField` | Last day of formal employment — critical for all trunca calculations |
| `last_day_worked` | `DateField` (nullable) | May differ from `fecha_cese` if employee had pending vacation |
| `baja_t_registro` | OneToOneField → `contracts.TRegistroDeclaration` (nullable) | D.10 auto-creates a `baja` declaration from `PayrollRun.close()` and links it here |

**D.12 hook point:** D.12 extends `compute_settlement` — it calls `severance_service.compute_settlement(termination, ...)` which is currently imported via `apps.contracts.services.severance_service`. D.12 replaces the 4 formula functions with `Regime728Strategy.compute_severance()`.

---

### apps.contracts.SeveranceSettlement + SeveranceLine

**File:** `apps/api/apps/contracts/models/severance_settlement.py` | **Tables:** `severance_settlement`, `severance_line`

**B.14 minimum legal scope — 4 (+ 1 generic) SeveranceLine components:**

| `component` code | Legal basis | Formula (current B.14 minimum) | D.12 replacement |
|---|---|---|---|
| `cts` | D.S. 001-97-TR | `(sueldo × meses_semestre) / 6`, capped at `sueldo` | `Regime728Strategy.compute_cts()` — adds 1/6 grati to remuneración computable |
| `vac_truncas` | D.S. 012-92-TR | `jornal × (meses_año × 2.5 días)` | `Regime728Strategy` uses time_off actual accrual vs proportional, whichever higher |
| `grat_trunca` | Ley 27735 | `(sueldo × meses_semestre) / 6` | `Regime728Strategy.compute_gratification()` called in severance context |
| `indemnizacion` | LPCL Art. 38 | `sueldo × 1.5 × (días/365)`, capped 12 sueldos; only for `despido_arbitrario` / `despido_indirecto` | `Regime728Strategy.compute_severance()` — same formula, different inputs |
| `otros` | Manual | Generic adjustment line | Preserved as-is |

**`compute_settlement` signature (current):**

```python
@transaction.atomic
def compute_settlement(
    termination: Termination,
    *,
    user=None,
    dias_acumulados_no_gozados: Decimal | None = None,
) -> SeveranceSettlement:
```

**Idempotent:** deletes and recreates all lines on re-call. D.12 will extend this function or replace it entirely with Strategy-aware version.

**SeveranceSettlement key fields for D.12:**

| Field | Type | Notes |
|---|---|---|
| `status` | `CharField(10)` | `draft → computed → paid → void` |
| `sueldo_base` | `DecimalField(12,2)` | Snapshot of gross salary at cese |
| `fecha_inicio_contrato` | `DateField` | From `contract.fecha_inicio` |
| `fecha_cese` | `DateField` | From `termination.fecha_cese` |
| `total_amount` | `DecimalField(14,2)` | Recomputed via `recompute_total()` (sums all SeveranceLine.amount) |
| `manual_override` | `JSONField` | Keyed by `component_code` — allows manual amount overrides without re-running engine |

**⚠️ Current formula gaps vs full N08 spec (D.12 must address):**
- CTS formula uses `sueldo/6 × meses` — missing 1/6 gratificación in remuneración computable per D.S. 001-97-TR Art. 9
- Vacaciones truncas: uses `meses × 2.5` (30 days/12 months) but does not consult actual `time_off` accrual records
- No Renta 5ta regularization al cese (see ADR-D.5)
- No `renta_5ta_regularizacion_cese` line type in COMPONENTS yet (D.12 must add)

---

### apps.contracts.TRegistroDeclaration

**File:** `apps/api/apps/contracts/models/t_registro_declaration.py` | **Table:** `t_registro_declaration`

**`declaration_type` choices:** `alta`, `baja`, `modificacion`

**Status flow:**

```
draft → validated (PVS) → submitted (SUNAT) → accepted
                                             ↘ rejected
```

**Key fields for D.10:**

| Field | Type | Notes |
|---|---|---|
| `declaration_type` | `CharField(20)` | D.10 creates `baja` declarations from `PayrollRun.close()` when a termination is linked |
| `status` | `CharField(20)` | `draft`, `validated`, `submitted`, `accepted`, `rejected` |
| `contract` | FK → `contracts.Contract` | |
| `employee` | FK → `employees.Employee` | |
| `regimen_laboral_code` | `CharField(3)` | Default `'728'` — for D-A 728-only MVP |
| `regimen_pensionario` | `CharField(20)` | `snp` (ONP), `spp` (AFP), `decreto_19990`, `decreto_20530`, `sin_regimen` |
| `pension_provider_code` | `CharField(10)` | AFP code if SPP |
| `cuspp` | `CharField(20)` | From `Employee.codigo_cuspp` |
| `remuneracion_basica` | `DecimalField(12,2)` | Salary snapshot for T-Registro |
| `anexo3_txt` | `TextField` | Generated Anexo 3 plain-text payload |
| `pvs_errors` | `JSONField(list)` | PVS validation errors; must be `[]` before `mark_validated()` |
| `sunat_reference` | `CharField(64)` | SUNAT constancia number |

**D.10 trigger point:** `PayrollRun.close()` will iterate over employees whose `Termination.status = 'completed'` in the closed period and auto-create `TRegistroDeclaration(declaration_type='baja')`. The declaration is linked back to `Termination.baja_t_registro`.

**UniqueConstraint:** `(tenant, contract, declaration_type)` where `status IN ('submitted', 'accepted')` — prevents duplicate active T-Registro submissions.

---

### apps.audit_lite.AuditEvent

**File:** `apps/api/apps/audit_lite/models.py` | **Table:** `audit_lite_event`

**Current field shape:**

| Field | Type | Notes |
|---|---|---|
| `id` | `UUIDField` (PK) | |
| `tenant` | FK → `tenancy.Tenant` | Non-nullable — every event is tenant-scoped |
| `actor_user` | FK → `AUTH_USER_MODEL` (nullable) | Null for system-initiated events |
| `action` | `CharField(128)` | Dotted action name e.g. `"employee.terminated"`. D will register `payroll.*` namespaced actions |
| `target_model` | `CharField(128)` | Dotted model label e.g. `"employees.Employee"` |
| `target_id` | `CharField(64)` | String PK of target (UUID or int as str) |
| `payload_json` | `JSONField` (default `dict`) | Mutation snapshot: before/after, reason, etc. Free-form |
| `created_at` | `DateTimeField` (auto, indexed) | Event timestamp |

**🚨 CRITICAL FINDING — `schema_version` field DOES NOT EXIST.**

The current `AuditEvent` model has **no `schema_version` field**. ADR-D.3 proposes adding it with `default=1`. This requires a migration in D.1. Without it, payroll event payloads cannot be versioned for forward-compat / future ES migration.

**ADR-D.3 migration required in D.1:**
```python
models.IntegerField(default=1, help_text="Payload schema version for forward-compat")
```

**Existing B-era event types (for naming convention reference):** `employee.terminated`, `contract.amendment_applied`, `tregistro.submitted`, etc.

**Composite indexes available:** `(tenant, action, -created_at)` and `(target_model, target_id)` — D queries should filter by `tenant + action` for per-payroll-run event lookups.

---

### apps.documents.services.access_service

**File:** `apps/api/apps/documents/services/access_service.py`

D.6 PaySlip permission gate reuses these functions:

**`user_permission_level(user) -> int`**

```python
def user_permission_level(user) -> int:
```

- Input: any User object (or None / unauthenticated)
- Output: integer 0-9 derived from `user.nivel_acceso` string
- Level map: `total=9`, `departamental=5`, `personal=3`, `limitado=2`, `lectura=1`
- Returns `0` for unauthenticated/None, `1` as fallback for unrecognized `nivel_acceso`

**`can_access(user, document) -> bool`**

```python
def can_access(user, document) -> bool:
```

- Returns `True` iff `user_permission_level(user) >= int(document.permission_level or 0)`
- D.6 PaySlip viewset will set `permission_level` appropriately (e.g., `3` = personal, readable only by the employee themselves or RRHH)

**`log_access(*, document, user, action, ip, user_agent, notes) -> DocumentAccessLog`**

- Persists a `DocumentAccessLog` entry for every access check
- D.6 should call this (or `check_and_log`) on every boleta view/download

**`check_and_log(*, document, user, action, ip, user_agent) -> bool`**

- Combined check + log — preferred for D.6 endpoint gating
- Logs `action` on grant, `'denied'` on reject

**⚠️ Coupling note:** These functions reference `apps.documents.models.DocumentAccessLog` and `apps.documents.models.DigitalDocument`. D.6 `PaySlip` is a different model. D.6 will need to either: (a) inherit from `DigitalDocument`, (b) create a parallel `PaySlipAccessLog` model with a similar permission gate, or (c) adapt `can_access` to accept any object with a `permission_level` attribute. Decision belongs to ADR-D.7.

---

### apps.core.business_days

**File:** `apps/api/apps/core/business_days.py`

**🚨 BLOCKER: File does NOT exist.**

`business_days.py` was planned as part of terminal-2 prep work but has **not been merged** as of audit date 2026-05-23.

**Impact:**
- **[BLOCKER for D.4]** — `Regime728Strategy.compute_payslip` does not need business days directly, but CTS deposit due date validation (15-May / 15-Nov; if that date is a holiday, next business day) requires a `business_days_between` helper.
- **[BLOCKER for D.7]** — `CtsDeposit` due date alert service needs to compute "next business day in Peru" relative to the statutory 15-May/15-Nov dates.

**Resolution options (to be decided in BACKLOG):**
1. Merge terminal-2 branch before D.4 starts (preferred)
2. Fold implementation into D.4 as an internal task: implement `apps/core/business_days.py` with at minimum `is_business_day(d, region='PE')` and `next_business_day(d, region='PE')` using a hardcoded feriados peruanos list for 2026-2027

## Section 3 — Frontend payroll legacy + portal empleado

### 4.1 Inventory of `apps/web/src/features/payroll/` files

**File count:** 13 files (8 pages, 1 service, 2 hooks, 2 index files)

| File | Type | External consumers? | API calls | D-I disposition |
|---|---|---|---|---|
| `index.ts` | Index re-export | None (module index) | None | ✅ KEEP (module structure) |
| `pages/index.ts` | Index re-export | None (module index) | None | ✅ KEEP |
| `pages/BoletasPagoPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/payslips/`, `/api/v1/payroll/monthly-runs/` | ⚠️ ACTIVE (legacy boleta viewer) — D.6 replaces |
| `pages/ConfiguracionRemuneracionesPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/compensation-configurations/` | ⚠️ ACTIVE (legacy concept catalog) — D.2 replaces |
| `pages/ConfiguracionUitPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/tax-parameters/` | ⚠️ ACTIVE (legacy UIT config) — D.2 replaces |
| `pages/DescuentosMasivosPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/mass-deductions/` | ⚠️ ACTIVE (legacy bulk deductions) — D.13 replaces |
| `pages/PlanillasMensualesPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/monthly-runs/`, `/api/v1/payroll/details/` | ⚠️ ACTIVE (legacy payroll runs) — D.5 replaces |
| `pages/ProcesoPlanillasPage.tsx` | Admin page | Imported by `App.tsx` (routing) | Multiple `/api/v1/payroll/*` endpoints | ⚠️ ACTIVE (legacy payroll workflow) — D.5 replaces |
| `pages/RemuneracionesHomePage.tsx` | Admin page (home/dashboard) | Imported by `App.tsx` (routing) | `/api/v1/payroll/compensation-configurations/` | ⚠️ ACTIVE (legacy payroll menu) — D.1 redirects or hides |
| `pages/ReportesRemuneracionesPage.tsx` | Admin page | Imported by `App.tsx` (routing) | `/api/v1/payroll/monthly-runs/` | ⚠️ ACTIVE (legacy payroll reports) — D.9/D.11 replace with PLAME/AFPnet |
| `services/index.ts` | Index re-export | None (module index) | None | ✅ KEEP |
| `services/payrollService.ts` | Service layer | Consumed by all 8 pages above | **30+ calls** to `/api/v1/payroll/*` endpoints (see list below) | ⚠️ CRITICAL CONSUMER — must preserve endpoints through D.1–D.5 transition |
| `hooks/index.ts` | Index re-export | None (module index) | None | ✅ KEEP |
| `hooks/useRemuneraciones.ts` | Custom hook | Consumed by payroll pages (indirectly via service) | Uses `payrollService` functions | ⚠️ ACTIVE (wrapper hook) — maintained through transition |

**API endpoint coverage in `payrollService.ts`:**

| Endpoint family | Method count | Endpoints | Status |
|---|---|---|---|
| `/api/v1/payroll/compensation-configurations/` | 4 | list, create, update, remove | ⚠️ Active (D.2 replaces) |
| `/api/v1/payroll/afp-configurations/` | 4 | listAfp, createAfp, updateAfp, removeAfp | ⚠️ Active (D.2 replaces) |
| `/api/v1/payroll/tax-parameters/` | 6 | listUit, getUit, createUit, updateUit, removeUit, activarUit | ⚠️ Active (D.2 replaces) |
| `/api/v1/payroll/monthly-runs/` | 10 | list, get, create, update, remove, generar, regenerar, calcular, preview, aprobar, estadisticas | ⚠️ Active (D.5 replaces) |
| `/api/v1/payroll/details/` | 6 | list, get, create, update, remove + direct import | ⚠️ Active (D.5 replaces) |
| `/api/v1/payroll/mass-deductions/` | 7 | list, get, create, update, remove, procesar, anular | ⚠️ Active (D.13 replaces) |
| `/api/v1/payroll/payslips/` | 4 | list, get, downloadBoletaPdf, descargaMasivaBoletas | ⚠️ Active (D.6 replaces) |
| `/api/v1/payroll/payment-schedules/` | 6 | list, get, create, update, remove, getCalendario | ⚠️ Active (D.5 replaces) |
| **Total** | **47 method calls** | **8 endpoint families** | All legacy; D.1–D.6 preserve URIs but replace backend handlers |

**Task 2 finding confirmed:** Frontend is an **ACTIVE CONSUMER** of legacy payroll endpoints. D-I FAIL confirmed — these endpoints must be preserved through the transition or frontend must be redirected per phase. See Section 1 Pre-D-I migration tasks.

---

### 4.2 Inventory of `EmployeeLayout.tsx` structure

**File:** `apps/web/src/shared/layout/EmployeeLayout.tsx` | **Status:** ✅ READY for D.6 extension

**Current layout structure:**

- **Type:** Functional React component accepting `{ children, title?, description? }`
- **Visual structure:**
  - Header section with title + optional description (lines 55–67)
  - Horizontal navigation tabs section (lines 69–99) — using React Router Links
  - Content area (lines 101–104) — renders `children`
- **Navigation pattern:** Tab-based with active state detection via `location.pathname` matching

**Current menu items for `tipo_usuario === 'empleado'` context:**

The component does **NOT explicitly check `tipo_usuario`**. Instead, it is used by the employee-facing data pages in `App.tsx` (lines 292–296):
- `/empleados/datos-personales` → `DatosPersonalesPage`
- `/empleados/datos-laborales` → `DatosLaboralesPage`
- `/empleados/datos-academicos` → `DatosAcademicosPage`
- `/empleados/datos-familiares` → `DatosFamiliaresPage`

The `EmployeeLayout` provides **4 hardcoded sub-menu tabs** (not role-gated):

| Tab | Icon | Route | Description |
|---|---|---|---|
| Datos Personales | Users | `/empleados/datos-personales` | Información personal del empleado |
| Datos Laborales | Briefcase | `/empleados/datos-laborales` | Información laboral y contractual |
| Datos Académicos | GraduationCap | `/empleados/datos-academicos` | Formación académica y certificaciones |
| Datos Familiares | Heart | `/empleados/datos-familiares` | Información familiar y contactos de emergencia |

**D.6 `/mis-boletas` integration pattern:**

✅ **Clean extension point identified.** To add `/mis-boletas` in D.6:

1. **Add to `subMenuItems` array** (line 19):
   ```typescript
   {
     title: 'Mis Boletas',
     icon: FileText, // or ReceiptText from lucide-react
     href: '/mis-boletas',
     description: 'Descarga de boletas de pago'
   }
   ```

2. **Create route in `App.tsx`** (sibling to lines 292–296):
   ```typescript
   <Route path="/mis-boletas" element={
     <OnboardingRoute>
       <EmployeeLayout title="Mis Boletas" description="...">
         <MisBoletasPage />
       </EmployeeLayout>
     </OnboardingRoute>
   } />
   ```

3. **No layout restructure needed** — `EmployeeLayout` already handles navigation routing correctly; just add the menu item and the corresponding `App.tsx` route.

---

### 4.3 Inventory of employee-facing routes

**Search:** `App.tsx` lines 173–215 and 278–303 show employee route discrimination pattern.

**Route pattern found (lines 178, 183, 197, 202):**
```typescript
enabled: user?.tipo_usuario === 'empleado'
if (user?.tipo_usuario !== 'empleado') return <Navigate to="/" replace />
```

**Current employee-facing routes (no role guard, open to all authenticated users):**

| Path | Component | Guard | Notes |
|---|---|---|---|
| `/` | `<Dashboard />` | `OnboardingRoute` (checks onboarding state) | Home; shared by all users |
| `/dashboard` | `<Dashboard />` | `OnboardingRoute` | Alias for `/` |
| `/vacaciones` | `<VacacionesManagementPage />` | None (open to all authenticated) | Vacation request submission |
| `/vacaciones/nueva-solicitud` | `<NuevaSolicitudPage />` | None | New vacation request |
| `/vacaciones/solicitudes` | `<SolicitudesPage />` | None | My vacation requests |
| `/legajo` | `<LegajoPage />` | None | View own legajo (document file) |
| `/legajo/:empleadoId` | `<LegajoPage />` | None | View employee legajo (admin access gated in component) |
| `/empleados/datos-personales` | `<DatosPersonalesPage />` | None | View/edit own personal data |
| `/empleados/datos-laborales` | `<DatosLaboralesPage />` | None | View/edit own employment data |
| `/empleados/datos-academicos` | `<DatosAcademicosPage />` | None | View/edit own academic data |
| `/empleados/datos-familiares` | `<DatosFamiliaresPage />` | None | View/edit own family data |
| `/onboarding` | `<OnboardingPage />` | `OnboardingGuard` (role check + onboarding state) | Employee onboarding flow (new hires only) |

**Key observations:**

1. **No `/mis-boletas` route currently exists.** D.6 must add it here.
2. **No explicit `tipo_usuario === 'empleado'` guard on employee routes.** Access control is implemented **in component logic** (e.g., `DatosPersonalesPage` checks if user is viewing own record).
3. **`OnboardingRoute` wrapper** (lines 173–189) redirects employees with incomplete onboarding to `/onboarding`; other users pass through.
4. **`OnboardingGuard` wrapper** (lines 192–214) enforces that only employees with incomplete onboarding can access `/onboarding`.
5. **Employee routes live alongside admin routes.** Discrimination happens via `AdminRoute` wrapper on admin pages (lines 162–170: requires `isAdminOrRRHH()`).

**D.6 integration:** Add route after line 296:
```typescript
<Route path="/mis-boletas" element={
  <OnboardingRoute>
    <EmployeeLayout title="Mis Boletas" description="Tus boletas de pago">
      <MisBoletasPage />
    </EmployeeLayout>
  </OnboardingRoute>
} />
```

---

### 4.4 Inventory of boleta-generation templates

**Backend template search:**

Template files found in `apps/api/templates/`:
- `adendas/`, `certificados/`, `cese/`, `contratos/`, `desplazamiento/`, `induccion/`, `legajo/`, `mpp/`, `reportes/`, etc.

**Boleta search result:** ❌ **NO boleta_*.html template found.**

The legacy `PaySlip` model has an `archivo_pdf` field (line 48, Section 1) but there is **no corresponding HTML template** for boleta rendering.

**Implication for D.6:**

- D.6 must **create a new boleta HTML template** from scratch (or port from INTRANET legacy if available).
- D.6 will generate boleta PDFs via the new `PaySlip.generate_pdf()` service method.
- **Recommended template location:** `apps/api/templates/boletas/boleta_pago.html` (parallel to existing structure).

**Templates that may offer reusable structural patterns:**

| Template | Purpose | Reusable for D.6? |
|---|---|---|
| `contratos/contrato_728.html` | Contract document | Partial (header/footer, signature block) |
| `certificados/certificado_laboral.html` | Labor certificate | Partial (employee header block) |
| `cese/constancia_trabajo.html` | Termination certificate | Partial (employee identifiers) |
| `legajo/consolidated_index.html` | Legajo index | Likely not (document listing, not pay stub) |

**D.6 design notes:**
- Boleta must show: period, employee ID, salary components, deductions, net-to-pay
- Should reuse employee header pattern from contratos/certificados
- PDF generation via ReportLab (per CLAUDE.md — xhtml2pdf and WeasyPrint unavailable on Windows)
- Template must be single-line Django tags (no multi-line `{% %}` per CLAUDE.md gotcha)

---

### 4.5 Summary: D-I disposition for frontend payroll

**Frontend payroll legacy status:** ⚠️ **ACTIVE CONSUMER of legacy backend endpoints**

| Component | Consumers | Status | D-I action required? |
|---|---|---|---|
| **8 admin pages** (Config, Planillas, Boletas, etc.) | `App.tsx` routing | Active, functional | ✅ Routes preserved; handlers replaced per phase D.1–D.6 |
| **`payrollService.ts`** | All 8 pages + HROverviewDashboard | Active, 47 method calls | ✅ Endpoints preserved through transition; replaced per phase |
| **`useRemuneraciones.ts`** | Payroll pages (indirect) | Active wrapper | ✅ Maintained as-is |
| **`EmployeeLayout.tsx`** | Will be used by `/mis-boletas` (D.6) | Ready to extend | ✅ No changes in D.1; add menu item in D.6 |
| **Employee routes** (vacaciones, legajo, datos, onboarding) | All authenticated users | Active, working | ✅ `/mis-boletas` added in D.6 |
| **Boleta templates** | Legacy `PaySlip` generation | ❌ None found | ❌ **D.6 creates new template** |

**Conclusion:** Frontend payroll is **NOT a D-I greenfield candidate**. Legacy endpoints must be preserved and progressively replaced per phase. No frontend code changes required in D.0 or D.1; full redesign happens D.2–D.6.

## Section 4 — Cross-cutting deuda técnica affecting D

### Pre-existing baselines (no regresar)

| Metric | Expected baseline | Actual (D.0 audit run) | Status |
|---|---|---|---|
| Backend pytest | 985 passed, 1 failed (`test_permisos_debug`), 17 skipped | **1,058 passed, 1 failed, 17 skipped** | ✅ PASS (delta +73 from terminal-2 + Bloque H test additions; 1 pre-existing failure unchanged) |
| Frontend ESLint | ≤ 278 warnings | **278** (proxy — v5 PM report; `node_modules` not installed in worktree) | ✅ PASS (proxy) |
| Frontend tsc | 1 error (`BlankEnum.ts`) | **0 errors** (proxy — v5 PM report confirms `exit 0` after Bloque F tsconfig fix) | ✅ PASS (proxy) |
| Frontend vitest | 178 passed / 28 files | **178/28** (proxy — v5 PM report; `node_modules` not installed in worktree) | ✅ PASS (proxy) |

**Note on pytest delta (+73):** The worktree includes all commits from `vyntia/D-prep-foundation` merged via `Merge PR #1` (`7066414b`) plus `vyntia/H-empleados-polish` (`634e3436`). These branches added tests for: catálogo feriados peruanos (business_days), batch CSV import (#130), N+1 serializer fix, Bloque H contracts/employees. All additions are expected and positive. The 1 pre-existing failure (`test_permisos_debug`) is unchanged.

**Note on frontend proxy:** The worktree at `D:/VYNTIA-D0-audit/apps/web/node_modules` is absent (expected — worktrees share the npm install from the main tree at `D:/VYNTIA/apps/web/node_modules`). Frontend tool runs were attempted but failed with `command not found`. The v5 PM report (`2026-05-23-empleados-v5.md`) confirmed 278/0/178 baselines post-Bloque G, and the Bloque H frontend commits (console.log cleanup, EmpleadosListPage deletion, unwrapBlobError, peruvianValidation.ts) are additive non-test-breaking changes.

---

### Sealed-for-D items from v5 PM report — status per item

| Item | v5 Source | Merged? | Commit | Severity for D | Resolution |
|---|---|---|---|---|---|
| `Employee.boletas_recientes()` stub | empleados-v5 § Pendientes + Bloque H action 1 | **YES** (Bloque H) | `634e3436` (merge) | ~~[BLOCKER for D.1]~~ → CLOSED | Deleted before D — grep confirms 0 matches in production source |
| N+1 `EmpleadoListSerializer` (66→3 queries) | empleados-v5 § Pendientes | **YES** | `26e3a16f`, `7066414b` | ~~[PERF for D.6]~~ → CLOSED | D.6 dashboards list empleados at ~3 queries, not 66 |
| Batch import CSV #130 | terminal-2 prep | **YES** | `4843f799`, `7066414b` | ~~[NICE-TO-HAVE]~~ → CLOSED | Available before D start |
| `business_days_between` + feriados peruanos Ley 29408 | terminal-2 prep / N8 v3 | **YES** | `75fb675f`, `7066414b` | ~~[BLOCKER for D.4, D.7]~~ → CLOSED | `apps/api/apps/core/business_days.py` + `holidays.py` exist and tested |
| V4-N2: `EmpleadoSerializer` legacy scope tenant | empleados-v5 § Pendientes | **YES** (Bloque H) | `e7af9815` | ~~[LOW]~~ → CLOSED | Merged in Bloque H |
| V4-N5: `family_member.py:404` leap-drifty age calc | empleados-v5 § Pendientes | **YES** (Bloque H) | `46b873d3` | ~~[LOW]~~ → CLOSED | Merged in Bloque H |
| V4-N7: `setup_roles_permisos` hardcoded admin user | empleados-v5 § Pendientes | **YES** (Bloque H) | `a4af9bc0` | ~~[MEDIUM]~~ → CLOSED | Gated with `--seed-admin` flag |
| V4-N6: extract `peruvianValidation.ts` | empleados-v5 § Pendientes | **YES** (Bloque H) | `5ea87e87` | ~~[LOW]~~ → CLOSED | Extracted to `apps/web/src/shared/utils/peruvianValidation.ts` |
| V4-3: `unwrapBlobError` for 7 blob services | empleados-v5 § Pendientes | **YES** (Bloque H) | `ffc1768a` | ~~[LOW]~~ → CLOSED | Shared helper applied to blob services |
| `EmpleadosListPage.tsx` huérfana | empleados-v5 § Pendientes | **YES** (Bloque H) | `47eac91d` | ~~[LOW]~~ → CLOSED | Deleted along with 4 orphan modals |
| 29 `console.log` debug | empleados-v5 § Pendientes | **YES** (Bloque H) | `66544bb9` | ~~[LOW]~~ → CLOSED | Cleaned |
| `/legajos-digitales` sidebar not in seed_menu | empleados-v5 § Pendientes | **YES** (Bloque H) | `b4810ff3` | ~~[LOW]~~ → CLOSED | Registered in `seed_menu.py` |
| V4-3 contracts: Bloque H contracts fixes | Bloque H action | **YES** | `76460893` | ~~[LOW]~~ → CLOSED | 4 audit-v1 bugs fixed |

---

### Open deuda técnica (still pending, carried into D)

| Item | Source | Affects D phase | Severity for D | Resolution |
|---|---|---|---|---|
| N6 v3 — 3 viewsets B.9 (`SelectionStage`, `CandidateEvaluation`, `MeritRanking`) use custom `posting__tenant` filter instead of `TenantAwareViewSetMixin` | empleados-v5 § Pendientes | D.0 architectural note (not code D touches) | [LOW] — B.9 module is onboarding/hiring; D doesn't touch these viewsets | Document in BACKLOG as architectural consistency item; resolve post-D or in a standalone cleanup sprint |
| `getattr(request, "tenant", None)` repeated in 30+ view sites; no shared `get_request_tenant()` helper | N8 v3 / empleados-v5 | D views will follow same pattern | [LOW/PERF] — pattern works correctly, just inconsistent | D.1 or dedicated cleanup sprint; document in BACKLOG; D views can use `TenantAwareViewSetMixin` (already available) |
| `AuditEvent.schema_version` field does not exist | INV § 2 (ADR-D.3) | D.1 migration required | [BLOCKER for D.1] | D.1 adds migration: `models.IntegerField(default=1)` — blocks versioned payroll audit events |
| Sub-proyecto E (Modularidad/Plans) — `Tenant.plan` + `MenuService` filtrado + `<FeatureRoute>` guard | empleados-v5 § Acciones | Independent of D | [P2 — product decision] | Separate brainstorm required; does not block D |

---

### Blocker / non-blocker summary for D start

| Check | Result | Blocker? |
|---|---|---|
| `Employee.boletas_recientes()` stub | ✅ DELETED — 0 matches in source | NO BLOCKER |
| `business_days_between` + feriados | ✅ EXISTS — `apps/core/business_days.py` + `holidays.py` | NO BLOCKER |
| N+1 `EmpleadoListSerializer` | ✅ FIXED — 66→3 queries | NO BLOCKER |
| `AuditEvent.schema_version` | ❌ MISSING — migration required in D.1 | [BLOCKER for D.1] |
| pytest baseline | ✅ 1,058 passed (+73 expected from merged prep), 1 pre-existing failure | NO BLOCKER |
| Frontend baselines | ✅ proxy 278/0 errors/178 (v5 confirmed; `node_modules` absent in worktree) | NO BLOCKER |

## Section 5 — Regulatory rules inventory (N06-N09)

> Extracted 2026-05-23. Each row becomes one BACKLOG item in Task 7. Citations use real section numbers from source docs. Phases: D.2 = catálogo, D.4 = engine, D.6 = PaySlip/boleta, D.7 = CTS, D.8 = Gratificaciones, D.9 = PLAME exporter, D.10 = T-Registro, D.11 = AFPnet, D.12 = Liquidación.

---

### 5.1 N06 — Planilla Electrónica SUNAT (T-Registro + PLAME)

| # | Rule | Citation | Phase affected |
|---|------|----------|----------------|
| N06-01 | PLAME (Formulario Virtual 0601) genera exactamente 10 archivos .txt + 1 ZIP: PLANI, JORNA, PDT, IMP, DERECH, PRACT, CUART, TERCE, EMPAL, ESTAB | N06 § 4.1 | D.9 |
| N06-02 | Archivos PLAME: formato plano ASCII, separador pipe `&#124;`, salto de línea `\n`, fechas DD/MM/AAAA, decimales con punto, sin comillas | N06 § 4.2 | D.9 |
| N06-03 | El ZIP de los 10 archivos es lo que se carga al PDT PLAME; no se pueden cargar archivos individuales | N06 § 4.4 | D.9 |
| N06-04 | Plazo de presentación PLAME: según cronograma SUNAT por último dígito de RUC (entre el 11 y 24 del mes siguiente) | N06 § 1.2 | D.9 |
| N06-05 | T-Registro alta: plazo hasta el primer día de prestación del trabajador (no hay gracia) | N06 § 1.1 | D.10 |
| N06-06 | T-Registro baja: plazo hasta el día en que se produce el cese | N06 § 1.1 | D.10 |
| N06-07 | T-Registro modificación: hasta 5 días después del hecho que origina la modificación | N06 § 6 | D.10 |
| N06-08 | T-Registro declaraciones: tipos `alta`, `baja`, `modificacion`; cada una genera su propio archivo | N06 § 5.3 | D.10 |
| N06-09 | PVS (Programa Validador SUNAT) valida: (1) número exacto de campos, (2) tipo y longitud, (3) existencia en tabla paramétrica, (4) habilitación por sector, (5) obligatoriedad según estructura, (6) no duplicidad en estructuras 4/5/6/9/10 | N06 § 1.3 | D.9 |
| N06-10 | PVS debe ejecutarse antes del envío; el sistema debe replicar sus 6 validaciones internamente | N06 § 1.3 | D.9 |
| N06-11 | Tabla 1 — Tipo de Documento: 00 Otros, 01 DNI, 04 Carnet Extranjería, 06 RUC, 07 Pasaporte, 08 PTP, 10 Doc.Trib, 11 Partida Nacimiento | N06 § 3.1 | D.2 |
| N06-12 | Tabla 8 — Tipo de Trabajador: MVP D-A usa código 10 (Indeterminado 728) y 11 (Plazo fijo 728); otros regímenes (276, CAS, MYPE, agrario) son post-MVP | N06 § 3.6 | D.2 |
| N06-13 | Tabla 9 — Ocupación: clasificación CIUO-08 de 4 dígitos; obligatorio en T-Registro por trabajador | N06 § 3.7 | D.2 |
| N06-14 | Tabla 11 — Régimen Pensionario: 04 = ONP, 21 = AFP INTEGRA, 22 = AFP PRIMA, 23 = AFP PROFUTURO, 25 = AFP HABITAT, 32 = no pensionable | N06 § 3.9 | D.2 |
| N06-15 | Tabla 12 — Tipo de Contrato: 01 = Indeterminado 728, 02 = Plazo fijo naturaleza temporal, 03 = Plazo fijo accidental, 04 = Plazo fijo obra/servicio; MVP cubre 01-04 | N06 § 3.10 | D.2 |
| N06-16 | Tabla 13 — Régimen de Salud: 01 = EsSalud, 04 = EsSalud + EPS; campo obligatorio en T-Registro y PLAME | N06 § 3.11 | D.2 |
| N06-17 | Tabla 17 — Motivo de cese: 01 Renuncia, 02 Despido, 03 Término contrato, 04 Fallecimiento, 08 Mutuo disenso, 11 Despido arbitrario (+ indemnización), 12 Despido falta grave (sin indem); todos generan liquidación | N06 § 3.12 | D.12 |
| N06-18 | Tabla 18 — Tipo de Jornada: 1 Regular diurna, 2 Regular nocturna, 3 Atípica, 4 Reducida (<4h) | N06 § 3.13 | D.2 |
| N06-19 | Tabla 21 — Suspensiones: 11 Maternidad (subsidio EsSalud), 12 Incapacidad temporal (empleador días 1-20; EsSalud día 21+), 14 Vacaciones (empleador), 21 Licencia sin goce (NO pago), 22 Huelga (NO pago) | N06 § 3.15 | D.4 |
| N06-20 | Concepto 0101 Remuneración básica: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=SÍ | N06 § 3.16 | D.2 |
| N06-21 | Concepto 0102 Alimentación principal especie: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=SÍ | N06 § 3.16 | D.2 |
| N06-22 | Concepto 0103 Comisiones regulares: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=SÍ* (*solo promedio si ≥3 veces/semestre) | N06 § 3.16 | D.2 |
| N06-23 | Concepto 0104 Asignación familiar: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=SÍ | N06 § 3.16 | D.2 |
| N06-24 | Concepto 0106 Horas extras: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=SÍ* (*promedio si ≥3 veces/semestre) | N06 § 3.16 | D.2 |
| N06-25 | Concepto 0107 Vacaciones: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS=NO | N06 § 3.16 | D.2 |
| N06-26 | Concepto 0108 Reintegros: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=SÍ, CTS según concepto original | N06 § 3.16 | D.2 |
| N06-27 | Concepto 0109 Gratificación Fiestas Patrias: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=NO** (**Ley 30334), CTS=NO | N06 § 3.16 | D.2 |
| N06-28 | Concepto 0110 Gratificación Navidad: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=NO** (**Ley 30334), CTS=NO | N06 § 3.16 | D.2 |
| N06-29 | Concepto 0111 Gratificación trunca: afecta Renta 5ta=SÍ, AFP=SÍ, EsSalud=NO** (**Ley 30334), CTS=NO | N06 § 3.16 | D.2 |
| N06-30 | Concepto 0115 Movilidad supeditada a asistencia: NO afecta a ningún tributo/aporte/CTS | N06 § 3.16 | D.2 |
| N06-31 | Concepto 0116 Refrigerio no principal: NO afecta a ningún tributo/aporte/CTS | N06 § 3.16 | D.2 |
| N06-32 | Concepto 0120 CTS: NO afecta Renta 5ta (beneficio social), NO afecta AFP, NO afecta EsSalud, NO afecta CTS | N06 § 3.16 | D.2 |
| N06-33 | Concepto 0501 Indemnización por vacaciones no gozadas: afecta parcialmente Renta 5ta; NO afecta AFP, EsSalud, CTS | N06 § 3.16 | D.2 |
| N06-34 | Concepto 0503 Indemnización por despido arbitrario: NO afecta Renta 5ta, NO afecta AFP, EsSalud, CTS | N06 § 3.16 | D.2 |
| N06-35 | Concepto 0601 Aporte obligatorio AFP fondo (10%): rubro descuentos del trabajador | N06 § 3.16 | D.2 |
| N06-36 | Concepto 0605 Retención Renta 5ta Categoría: rubro tributos del trabajador; mapeado a retención mensual proyectiva | N06 § 3.16 | D.2 |
| N06-37 | Concepto 0606 Comisión/Prima AFP (comisión AFP + prima SISCO): rubro descuentos del trabajador | N06 § 3.16 | D.2 |
| N06-38 | Concepto 0607 Aporte voluntario con fin previsional AFP: rubro descuentos del trabajador | N06 § 3.16 | D.2 |
| N06-39 | Concepto 0801 Aporte EsSalud 9%: rubro aportes del empleador | N06 § 3.16 | D.2 |
| N06-40 | Todas las tablas paramétricas (Tabla 1, 8, 9, 10, 11, 12, 13, 17, 18, 21, 22, etc.) deben existir como catálogos versionados en BD con campos `valid_from`, `valid_to` | N06 § 5.1 | D.2 |
| N06-41 | Catálogos Tabla 22: cada concepto necesita metadata JSONB con matriz de afectación: `afecta_renta_5ta`, `afecta_afp`, `afecta_onp`, `afecta_essalud`, `afecta_cts`, `afecta_gratificacion` | N06 § 5.1 | D.2 |
| N06-42 | Error crítico a prevenir: concepto creado sin mapeo a código SUNAT → campo código_sunat debe ser obligatorio en el formulario de creación de concepto | N06 § 7 | D.2 |
| N06-43 | Error crítico a prevenir: trabajador AFP sin CUSPP registrado → validación cruzada con AFPnet obligatoria antes de generar PLAME | N06 § 7 | D.11 |
| N06-44 | Error crítico a prevenir: diferencia entre T-Registro y PLAME (alta/baja no sincronizada) → eventos del sistema deben disparar ambas declaraciones automáticamente | N06 § 7 | D.10 |

---

### 5.2 N07 — Aportes a Pensiones y Salud (AFP, ONP, EsSalud, EPS, SCTR)

| # | Rule | Citation | Phase affected |
|---|------|----------|----------------|
| N07-01 | Aporte obligatorio AFP al fondo: 10% de la remuneración asegurable del trabajador | N07 § 1.3 | D.4 |
| N07-02 | Prima SISCO AFP (seguro invalidez, sobrevivencia, sepelio): 1.37% de la remuneración asegurable, con tope RMA | N07 § 1.3 | D.4 |
| N07-03 | Tope RMA para prima SISCO (Abr-Jun 2026): S/ 12,598.91 actualizada trimestralmente por SBS; el exceso sobre RMA no paga prima pero sí fondo y comisión | N07 § 1.4 | D.4 |
| N07-04 | Comisión AFP por flujo: % sobre remuneración mensual; Integra 1.55%, Prima 1.60%, Profuturo 1.69%, Habitat 1.47% | N07 § 1.2 | D.4 |
| N07-05 | Comisión AFP sobre saldo (mixta — anual): % sobre fondo acumulado; Integra 1.00%, Prima 1.25%, Profuturo 0.68%, Habitat 1.25% | N07 § 1.2 | D.4 |
| N07-06 | Comisión por flujo: solo pueden mantenerla afiliados antes del 01/02/2013; nuevos afiliados usan mixta por defecto | N07 § 1.5 | D.4 |
| N07-07 | Licitación AFP 2025-2027: todos los nuevos afiliados al SPP entre 01/06/2025 y 31/05/2027 se incorporan obligatoriamente a Profuturo | N07 § 1.2 | D.4 |
| N07-08 | Archivo AFPnet: Excel de 25 columnas (CUSPP, tipo doc, nro doc, apellidos, nombres, fecha nacimiento, sexo, relación laboral, fechas, días laborados/subsidiados/no laborados, motivo excepción, remuneración asegurable, aportes voluntarios, aporte empleador, tipo trabajo) | N07 § 1.6 | D.11 |
| N07-09 | AFPnet soporta DNP (declaración sin pago) y DYP (declaración y pago); el sistema debe generar ambos tipos | N07 § 1.7 | D.11 |
| N07-10 | Aporte ONP: 13% de la remuneración asegurable, sin tope; base mínima = RMV | N07 § 2.2 | D.4 |
| N07-11 | Declaración ONP: vía PLAME mensual (no tiene archivo separado como AFPnet) | N07 § 2.2 | D.9 |
| N07-12 | Cambio SNP→SPP es irreversible (salvo excepciones muy puntuales); el sistema no debe permitir cambio de AFP a ONP | N07 § 2.4 | D.4 |
| N07-13 | EsSalud: aporte empleador 9% sobre remuneración; base mínima = RMV aunque el empleado ganó menos en el período | N07 § 3.2 | D.4 |
| N07-14 | EsSalud régimen general D.Leg. 728: 9% empleador; MYPE Micro: 0% (trabajador a SIS); MYPE Pequeña: 9% empleador | N07 § 3.2 | D.4 |
| N07-15 | Subsidio incapacidad temporal EsSalud: empleador paga días 1-20; EsSalud paga desde día 21 hasta 340/año | N07 § 3.3 | D.4 |
| N07-16 | Subsidio maternidad: 98 días (49 pre + 49 post); 128 días en parto múltiple o discapacidad del bebé | N07 § 3.3 | D.4 |
| N07-17 | CITT (Certificado de Incapacidad Temporal para el Trabajo): documento electrónico EsSalud que sustenta el descanso médico; sin CITT no se procesa subsidio | N07 § 3.4 | D.4 |
| N07-18 | Latencia EsSalud post-cese: 2 meses de cobertura por cada 5 meses de aportes continuos previos; máximo 12 meses | N07 § 3.5 | D.12 (nota) |
| N07-19 | Crédito EPS: 2.25% de la remuneración asegurable se deduce del aporte EsSalud del empleador (paga 6.75% efectivo a EsSalud) | N07 § 4.3 | D.4 |
| N07-20 | Tope del crédito EPS: 10 RMV × número de trabajadores cubiertos por EPS | N07 § 4.3 | D.4 |
| N07-21 | EPS: marcador por empleado "cobertura EPS sí/no"; cálculo crédito automático y factura EPS como egreso separado | N07 § 4.4 | D.4 |
| N07-22 | SCTR obligatorio solo para actividades de alto riesgo (minería, construcción, hidrocarburos, electricidad, química, pesca); MVP D-A puede marcar como "no aplica" para régimen 728 oficinas | N07 § 5.2 | D.4 (nota) |
| N07-23 | SCTR tiene dos coberturas: SCTR Salud (accidentes/enfermedades laborales) y SCTR Pensiones (invalidez/sobrevivencia); deben declararse como conceptos separados en PLAME (0803, 0804) | N07 § 5.3 | D.2 |
| N07-24 | SENATI: 0.75% sobre planilla, solo empleadores de industria manufacturera con más de 20 trabajadores; concepto PLAME 0805 | N07 § 6.1 | D.2 (nota MVP) |
| N07-25 | SENCICO: 0.2% sobre planilla, solo empleadores del sector construcción; concepto PLAME 0806 | N07 § 6.2 | D.2 (nota MVP) |
| N07-26 | Seguro de Vida Ley 29549: obligatorio desde el primer día de labor; cobertura mínima 16 rem. muerte natural, 32 rem. muerte accidental, 32 rem. invalidez total permanente | N07 § 6.4 | D.4 |
| N07-27 | RMA se actualiza trimestralmente por SBS; el sistema debe tener tabla de RMA versionada por trimestre con `valid_from`/`valid_to` | N07 § 1.4 | D.2 |
| N07-28 | Tasas AFP deben actualizarse desde SBS cada licitación trienal; sistema necesita carga de tasas con vigencia por período | N07 § 1.2 | D.2 |

---

### 5.3 N08 — Beneficios Sociales (CTS, Gratificaciones, Vacaciones, Asignación Familiar, Utilidades)

| # | Rule | Citation | Phase affected |
|---|------|----------|----------------|
| N08-01 | CTS fórmula general: `(Rem. Computable ÷ 12 × meses) + (Rem. Computable ÷ 360 × días)` | N08 § 1.3 | D.7 |
| N08-02 | CTS remuneración computable incluye: remuneración básica + asignación familiar + 1/6 de la última gratificación percibida antes del depósito | N08 § 1.4 | D.7 |
| N08-03 | CTS remuneración computable incluye promedio de conceptos variables del semestre si se percibieron 3 o más veces: horas extras, comisiones, bonificaciones por producción/eficiencia, bonos puntualidad/asistencia | N08 § 1.4 | D.7 |
| N08-04 | CTS remuneración computable excluye (Art. 19-20 LPCL): gratificaciones extraordinarias, utilidades, movilidad supeditada a asistencia, refrigerio no principal, asignaciones por eventos personales, condiciones de trabajo, canasta de Navidad | N08 § 1.4 | D.7 |
| N08-05 | CTS depósito Mayo: semestre noviembre-abril; plazo límite 15 de mayo; remuneración computable tomada al 30 de abril | N08 § 1.5 | D.7 |
| N08-06 | CTS depósito Noviembre: semestre mayo-octubre; plazo límite 15 de noviembre; remuneración computable tomada al 31 de octubre | N08 § 1.5 | D.7 |
| N08-07 | CTS trunca al cese: misma fórmula con meses y días desde el último depósito hasta fecha de cese; pago directo al trabajador en 48 horas (no depósito en cuenta CTS) | N08 § 1.6 | D.12 |
| N08-08 | Ley 32322 (2025): disponibilidad 100% del fondo CTS hasta 31/12/2026 como medida temporal; históricamente solo 50% del excedente de 4 sueldos era disponible | N08 § 1.7 | D.7 (nota) |
| N08-09 | Gratificación Fiestas Patrias: pago hasta el 15 de julio; base semestre enero-junio | N08 § 2.2 | D.8 |
| N08-10 | Gratificación Navidad: pago hasta el 15 de diciembre; base semestre julio-diciembre | N08 § 2.2 | D.8 |
| N08-11 | Fórmula gratificación: `Rem. Computable × (meses trabajados en el semestre ÷ 6)` | N08 § 2.3 | D.8 |
| N08-12 | Gratificación remuneración computable: incluye asignación familiar y promedio de variables (≥3 veces/semestre); NO incluye 1/6 de gratificación anterior (diferencia con CTS) | N08 § 2.4 | D.8 |
| N08-13 | Bonificación Extraordinaria Ley 30334: 9% del monto de la gratificación si en EsSalud; 6.75% si tiene cobertura EPS | N08 § 2.5 | D.8 |
| N08-14 | Bonificación Extraordinaria Ley 30334: NO afecta AFP/ONP/EsSalud ni descuentos; SÍ afecta Renta 5ta | N08 § 2.5 | D.8 |
| N08-15 | Bonificación Extraordinaria Ley 30334: se paga junto con la gratificación en el mismo plazo | N08 § 2.5 | D.8 |
| N08-16 | Para percibir gratificación completa el trabajador debe estar en planilla al 15 de julio (FP) o 15 de diciembre (Navidad); si cesa antes aplica trunca | N08 § 2.7 | D.8 |
| N08-17 | Gratificación trunca al cese: `Rem. Computable × (meses completos ÷ 6)`; derecho solo si cumplió al menos un mes completo en el semestre | N08 § 2.6 | D.12 |
| N08-18 | Vacaciones: 30 días calendario por cada año completo de servicios, cumpliendo récord vacacional | N08 § 3.2 | D.4 |
| N08-19 | Récord vacacional jornada 6 días/semana: mínimo 260 días efectivos trabajados en el año | N08 § 3.2 | D.4 |
| N08-20 | Récord vacacional jornada 5 días/semana: mínimo 210 días efectivos trabajados en el año | N08 § 3.2 | D.4 |
| N08-21 | Remuneración vacacional: equivalente a la remuneración regular del trabajador en el mes de su goce | N08 § 3.3 | D.4 |
| N08-22 | Reducción vacacional: el trabajador puede vender hasta 15 días por escrito; queda con descanso mínimo de 15 días | N08 § 3.4 | D.4 (nota) |
| N08-23 | Acumulación vacacional: hasta 2 períodos consecutivos por acuerdo escrito | N08 § 3.4 | D.4 (nota) |
| N08-24 | Triple remuneración vacacional por no goce (Ley 30012): trabajador que no gozó vacaciones dentro del año siguiente a su adquisición recibe triple pago (1 rem. trabajo efectivo + 1 rem. descanso no gozado + 1 rem. indemnizatoria) | N08 § 3.5 | D.4 |
| N08-25 | Vacaciones truncas al cese: `Rem. Computable × (meses + días/30) ÷ 12`; si no se alcanzó el año completo, solo indemnización proporcional | N08 § 3.6 | D.12 |
| N08-26 | Incapacidad temporal: primeros 60 días cuentan como efectivos para el récord vacacional | N08 § 3.7 | D.4 (nota) |
| N08-27 | Utilidades: aplica a empresas del régimen general IR 3ra categoría con más de 20 trabajadores | N08 § 4.2 | D.4 (nota) |
| N08-28 | Porcentajes utilidades por sector: pesqueras/telecomunicaciones/industriales 10%, mineras/comercio/restaurantes 8%, otras actividades 5% | N08 § 4.3 | D.4 (nota) |
| N08-29 | Distribución utilidades: 50% por días efectivamente laborados (proporcional asistencia) + 50% por monto de remuneraciones percibidas en el ejercicio | N08 § 4.4 | D.4 (nota) |
| N08-30 | Tope utilidades por trabajador: máximo 18 remuneraciones mensuales; excedente va a FONDOEMPLEO | N08 § 4.5 | D.4 (nota) |
| N08-31 | Plazo pago utilidades: 30 días naturales tras presentación de DJ Anual IR | N08 § 4.6 | D.4 (nota) |
| N08-32 | Excluidos de utilidades: practicantes, trabajadores CAS, trabajadores a domicilio, MYPE en régimen especial | N08 § 4.7 | D.4 (nota) |
| N08-33 | Asignación familiar: 10% de la RMV vigente; 2026 = S/ 113 (RMV S/ 1,130 × 10%) | N08 § 5.3 | D.4 |
| N08-34 | Asignación familiar: derecho para trabajadores con uno o más hijos menores de 18 años, o hasta 24 si cursan estudios superiores/universitarios | N08 § 5.2 | D.4 |
| N08-35 | Asignación familiar: monto fijo independiente del número de hijos; afecta CTS, gratificaciones, vacaciones, Renta 5ta, EsSalud, AFP/ONP | N08 § 5.4 | D.4 |
| N08-36 | Asignación familiar requiere acreditación: partida de nacimiento; para hijos 18-24, constancia de estudios superiores vigente anualmente | N08 § 5.5 | D.4 |
| N08-37 | Conceptos NO remunerativos (no forman RC): gratificaciones extraordinarias, utilidades, bonificación extraordinaria Ley 30334, movilidad, refrigerio, condiciones de trabajo, canasta navideña, asignaciones por fallecimiento/matrimonio/nacimiento | N08 § 6.1 | D.2 |
| N08-38 | Liquidación de beneficios sociales al cese: plazo legal 48 horas tras el cese (Art. 3 Ley 27321, SUNAFIL exige cumplimiento estricto) | N08 § 7.1 | D.12 |
| N08-39 | Conceptos típicos en liquidación: CTS trunca + gratificación trunca + vacaciones truncas/indemnización no goce + remuneración pendiente + bonif. extraordinaria 30334 + indemnización despido arbitrario (si aplica) + descuentos pendientes | N08 § 7.2 | D.12 |
| N08-40 | Documentos a entregar al cese: Hoja de Liquidación firmada, Certificado de Trabajo (Art. 45 LPCL), constancia de cese para T-Registro, certificado de retenciones Renta 5ta del año | N08 § 7.3 | D.12 |
| N08-41 | Indemnización despido arbitrario: 1.5 remuneraciones por año de servicio, tope 12 remuneraciones; solo para causales despido arbitrario/indirecto | N08 § 7.2 | D.12 |
| N08-42 | Prescripción laboral: 4 años desde el día siguiente al cese (Ley 27321); el sistema debe conservar toda la data de planilla para reconstruir el histórico | N08 § 8 | D.4 |
| N08-43 | Horas extras en CTS: computan solo si se percibieron 3 o más veces en el semestre (promedio); si <3 veces, no computan | N08 § 9 | D.7 |
| N08-44 | Gratificación anterior (1/6) en CTS: incluida en CTS pero NO en gratificación siguiente; es asimétrica | N08 § 9 | D.7 |

---

### 5.4 N09 — Impuesto a la Renta de 5ta Categoría

| # | Rule | Citation | Phase affected |
|---|------|----------|----------------|
| N09-01 | UIT 2026: S/ 5,500 (D.S. 301-2025-EF); deducción automática de 7 UIT = S/ 38,500 | N09 § 3.1 | D.4 |
| N09-02 | Deducción fija de 7 UIT: si RBA proyectada ≤ 7 UIT → retención mensual = 0; no se retiene nada | N09 § 3.2 | D.4 |
| N09-03 | Deducción adicional hasta 3 UIT (D.Leg. 1258, S/ 16,500 en 2026): SOLO aplica en regularización anual; NUNCA en retención mensual | N09 § 3.3 | D.4 (nota) |
| N09-04 | Escala progresiva Renta 5ta (2025-2026): hasta 5 UIT = 8%, 5-20 UIT = 14%, 20-35 UIT = 17%, 35-45 UIT = 20%, más de 45 UIT = 30% | N09 § 4 | D.4 |
| N09-05 | Tramos en soles 2026: 0–27,500 (8%), 27,500–110,000 (14%), 110,000–192,500 (17%), 192,500–247,500 (20%), 247,500+ (30%) | N09 § 4.1 | D.4 |
| N09-06 | Paso 1 RBA: `Rem. mensual × meses restantes del año (incl. actual) + Rem. percibidas meses anteriores + Gratificaciones ordinarias del año (jul y dic proyectadas o percibidas) + Bonificación Extraordinaria Ley 30334 (proyectada) + otros ingresos regulares proyectables` | N09 § 5.1 | D.4 |
| N09-07 | Ingresos extraordinarios (bono único, utilidades, reintegros, gratificación extraordinaria) NO se proyectan; se adicionan al mes en que se pagan | N09 § 5.1 | D.4 |
| N09-08 | Paso 2 Renta Neta Anual Proyectada: `RNAP = RBA − 7 UIT`; si RNAP ≤ 0 → no hay retención | N09 § 5.2 | D.4 |
| N09-09 | Paso 3 Impuesto Anual Proyectado (IAP): aplicar escala progresiva a RNAP tramo por tramo | N09 § 5.3 | D.4 |
| N09-10 | Paso 4 Retención mensual: `IAP ÷ denominador del mes` | N09 § 5.4 | D.4 |
| N09-11 | Denominadores mensuales: Enero=12, Feb=12, Mar=12, Abr=9, May=8, Jun=8, Jul=8, Ago=5, Sep=4, Oct=4, Nov=4 | N09 § 5.4 | D.4 |
| N09-12 | Diciembre — ajuste final: `Retención dic = IAP(definitivo) − Retenciones acumuladas ene-nov`; NO hay denominador; regulariza el impuesto definitivo del año | N09 § 5.5 | D.4 |
| N09-13 | Retención mensual no puede ser negativa; si la regularización da negativa, se arrastra como crédito para el siguiente mes | N09 § 11.4 | D.4 |
| N09-14 | Total retenido en el año no puede exceder el IAP definitivo; el exceso es devolución al trabajador | N09 § 11.4 | D.4 |
| N09-15 | Certificado de Rentas y Retenciones: emisión anual antes del 1 de marzo del año siguiente; y al cese si el trabajador cesa durante el año | N09 § 7.1 | D.12 |
| N09-16 | Conceptos NO afectos a Renta 5ta: CTS, indemnizaciones (despido arbitrario, vacacional, por muerte), condiciones de trabajo (movilidad, refrigerio, ropa, EPP), subsidios (incapacidad, maternidad, lactancia, sepelio), movilidad supeditada a asistencia | N09 § 10 | D.2 |
| N09-17 | Bonificación Extraordinaria Ley 30334: NO afecta EsSalud/AFP/ONP pero SÍ afecta Renta 5ta | N09 § 10 | D.4 |
| N09-18 | Extranjeros no domiciliados: retención 30% sobre monto bruto sin deducción, sin escala progresiva; cambia a régimen domiciliados tras 183 días continuos | N09 § 9.5 | D.4 |
| N09-19 | Prácticas pre/profesionales (Ley 28518): subvenciones NO son renta 5ta; NO se retiene 5ta, NO se aporta EsSalud ni AFP/ONP obligatorio | N09 § 9.4 | D.4 |
| N09-20 | Cambios retroactivos (ajuste salarial mid-year): el motor debe recalcular RBA desde enero del año fiscal; Event Sourcing permite reconstrucción de cualquier mes histórico | N09 § 11.3 | D.4 |
| N09-21 | UIT es anual (fijada por D.S. de fin del año anterior); no puede haber cambio de UIT a mitad del ejercicio | N09 § 11.3 | D.4 |
| N09-22 | Regularización anual: trabajadores con más de un empleador; o que apliquen deducción 3 UIT; lo gestiona el trabajador ante SUNAT (no el empleador) | N09 § 8 | D.4 (nota) |
| N09-23 | Empleado régimen 276: se retiene 5ta sobre remuneración total excepto aguinaldos (aguinaldos no afectan 5ta) | N09 § 11.4 | D.4 (nota) |
