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
