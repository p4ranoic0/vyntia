# Sub-project D — Master Roadmap (confirmed by D.0 audit)

> Confirmed phase structure for sub-project D. Each phase is a separate branch and PR, mergeable independently.
> Source spec: `docs/superpowers/specs/2026-05-23-vyntia-D-vyntia-pay-design.md`.
> Roadmap version: CONFIRMED 2026-05-23 (D.1 split into D.1a + D.1b post cero-consumo FAIL — see Adjustments section).

## Phase table

| Fase | Branch | Scope | Necesita | Plan detallado | Sign-off |
|------|--------|-------|----------|----------------|----------|
| D.0  | `vyntia/D0-audit` | Audit & inventory (this phase) | A, C, B | `2026-05-23-vyntia-D0-audit.md` | — |
| D.1a | `vyntia/D1a-migrate-consumers` | Migrate 5 consumers (views.py, serializers.py, remuneraciones_views.py, payrollService.ts, HROverviewDashboard) to call new stub endpoints OR preserve via deprecation wrapper | D.0 | TBD post-D.0 | — |
| D.1b | `vyntia/D1b-drop-legacy` | Drop 9 legacy models + 2 services + 2 migrations + 1 management command + AuditEvent.schema_version migration | D.1a | TBD | — |
| D.2  | `vyntia/D2-catalogo-regulatorio` | TaxParameter + PayrollConcept + RegimenConfig + seed | D.1b | TBD | — |
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

## Adjustments by audit (filled by Task 9)

### Adjustment 1: D.1 SPLIT into D.1a + D.1b (CRITICAL)

**Trigger:** Task 2 cero-consumo audit FAILED. Decision D-I (greenfield drop) cannot proceed without first migrating 5 active consumers.

**Evidence:**
- `apps/api/api/v1/rrhh/views.py` + `serializers.py` import `AfpConfiguration` + `CompensationConfiguration` from `apps.payroll`
- `apps/api/api/v1/rrhh/remuneraciones_views.py` instantiates `PlanillaCalculoService` + `DescuentoMasivoService`
- Frontend `payrollService.ts` makes 47 calls across 8 admin pages
- `HROverviewDashboard` calls `/api/v1/payroll/monthly-runs/`

**New structure:**
- **D.1a — Migrate consumers** (~2-3 days)
  - Stub backend endpoints `/api/v1/payroll/*` to return 410 Gone or proxy to new endpoints (TBD strategy in D.1a plan)
  - Replace `from apps.payroll.models import ...` in views/serializers with deprecation shim
  - Frontend `payrollService.ts` switch to new endpoints (47 calls)
  - HROverviewDashboard endpoint switch
- **D.1b — Drop legacy + schema_version migration** (~1 day)
  - Drop 9 legacy models + 2 services + 2 migrations + 1 mgmt command
  - Add `AuditEvent.schema_version` field via migration
  - Verify pytest stays green

**Dependency cascade:** D.2 now depends on D.1b (not D.1). Updated in phase table above.

**BACKLOG split:** D.1's 15 items (10 P0 / 2 P1 / 3 P2) annotated `[D.1a]` / `[D.1b]` in BACKLOG.md.

---

### Adjustment 2: Roadmap phase count grows 15 → 16

Total phases now: D.0, D.1a, D.1b, D.2, D.3, D.4, D.5, D.6, D.7, D.8, D.9, D.10, D.11, D.12, D.13, D.14.

---

### Adjustment 3: D.4 split deferred

D.4 has 32 BACKLOG items (14 P0 + 14 P1 + 4 P2) — densest phase in the roadmap. Candidate split identified:
- D.4a: engine ingresos + descuentos no-tributarios
- D.4b: Renta 5ta + EsSalud + golden cartilla validation

**Decision:** keep D.4 as a single phase in ROADMAP-D for now. Most items are independent rules within the engine and can be implemented sequentially without architectural risk. Revisit during D.4 kickoff: if real complexity emerges (e.g. Renta 5ta requires a separate compute pass), split into D.4a + D.4b at that time.

---

### Adjustment 4: D.4/D.7 blockers CLEARED

Terminal-2 prep work landed `business_days_between` + `holidays.py` (merged, verified by Task 3/Task 5). Original "BLOCKER for D.4/D.7" status downgraded to "available — verified by Task 5". D.4 and D.7 can now proceed without prerequisite work outside the D sub-project.

Pending: `AuditEvent.schema_version` migration — addressed in D.1b scope.

---

### Adjustment 5: All 8 ADRs accepted

ADR-D.1 through ADR-D.8 status = `accepted` (set by Task 8). No `proposed` status remaining. D.1a can proceed immediately after D.0 merges.

---

### Roadmap version: CONFIRMED 2026-05-23
