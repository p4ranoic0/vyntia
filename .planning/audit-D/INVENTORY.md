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

(Filled by Task 3.)

## Section 3 — Frontend payroll legacy + portal empleado

(Filled by Task 4.)

## Section 4 — Cross-cutting deuda técnica affecting D

(Filled by Task 5.)

## Section 5 — Regulatory rules inventory (N06-N09)

(Filled by Task 6.)
