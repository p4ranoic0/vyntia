# Sub-project D — Vyntia Pay — Master Roadmap

> Tentative phase structure for sub-project D. Will be **CONFIRMED** by D.0 audit (Task 13 of D.0 plan).
> Source spec: `docs/superpowers/specs/2026-05-23-vyntia-D-vyntia-pay-design.md` (commit `bdbe7c02`).
> Spec date: 2026-05-23. Roadmap version: **TENTATIVE** (pre-D.0 audit).

## Phase table

| Fase | Branch | Scope | Necesita | Plan detallado | Sign-off | Merge SHA |
|------|--------|-------|----------|----------------|----------|-----------|
| D.0  | `vyntia/D0-audit` | Audit & inventory (legacy payroll cero-consumo confirm, BACKLOG ~80-120 regulatory rules, 8 ADRs) | A, C, B | `2026-05-23-vyntia-D0-audit.md` | — | TBD |
| D.1  | `vyntia/D1-polish-baseline` | Polish wave: drop 9 modelos legacy + skeleton greenfield apps.payroll/ + audit_lite payroll payloads | D.0 | TBD | — | TBD |
| D.2  | `vyntia/D2-catalogo-regulatorio` | TaxParameter + PayrollConcept (Tabla 22 oficial) + RegimenConfig + seed `seed_payroll_catalog` | D.1 | TBD | — | TBD |
| D.3  | `vyntia/D3-compensation-contract` | Compensation modelo versionado + admin CRUD + migrate command desde EmploymentData | D.2 | TBD | — | TBD |
| D.4  | `vyntia/D4-engine-728` | Regime728Strategy.compute_payslip completo (ingresos, descuentos, Renta 5ta, EsSalud, AFP/ONP) + ~30 golden cartilla SUNAT | D.2, D.3 | TBD | ⚠️ | TBD |
| D.5  | `vyntia/D5-payroll-run-lifecycle` | PayrollRun state machine + service + PayrollAdjustment + admin UI lifecycle + audit events | D.4 | TBD | — | TBD |
| D.6  | `vyntia/D6-payslip-portal` | PaySlip + PayrollLine persistidos + PDF generator + /api/v1/payroll/payslips/ + /mis-boletas (EmployeeLayout) | D.5 | TBD | — | TBD |
| D.7  | `vyntia/D7-cts` | CtsDeposit + compute_cts (rem. computable, semestre, trunca) + admin UI alertas vencimiento + Ley 32322 nota | D.4 | TBD | ⚠️ | TBD |
| D.8  | `vyntia/D8-gratificaciones` | Gratification + compute_gratification (FP/Navidad) + Bonif Extra Ley 30334 + trunca | D.4 | TBD | ⚠️ | TBD |
| D.9  | `vyntia/D9-plame-exporter` | PlameExporter (10 .txt + ZIP) + validator interno PVS-like + benchmark Sentinel/Buk | D.5 | TBD | — | TBD |
| D.10 | `vyntia/D10-tregistro-deltas` | PayrollRun.close() auto-genera TRegistroDeclaration (altas/bajas/modif) reusando B.10 | D.5 + B.10 | TBD | — | TBD |
| D.11 | `vyntia/D11-afpnet-exporter` | AfpnetExporter (.xlsx 25 columnas exactas) + endpoint per AFP | D.5 | TBD | — | TBD |
| D.12 | `vyntia/D12-liquidacion-bbss` | Extiende contracts.severance_service llamando Regime728Strategy.compute_severance + SLA 48h workflow | D.4, D.7, D.8 + B.14 | TBD | ⚠️ | TBD |
| D.13 | `vyntia/D13-csv-reopen-adjust` | ProvisionesCsvExporter bruto + UI REOPENED + PayrollAdjustment modal | D.5 | TBD | — | TBD |
| D.14 | `vyntia/D14-e2e-close-out` | Playwright lifecycle test (RUN_DPAY_E2E=1) + docs sweep + tag `d-vyntia-pay-complete` | D.6-D.13 | TBD | — | TBD |

⚠️ = **Regulatory sign-off gate** — merge bloqueado hasta que el user firme `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md` con `APPROVED`.

## Order and dependencies

```
D.0 → D.1 → D.2 → D.3
                   ↓
                  D.4 ⚠️
                   ↓
                  D.5 → D.6
                   ↓     ↓
        ┌──────────┼─────────────────┐
        ↓          ↓          ↓     ↓
       D.7⚠️     D.8⚠️       D.9  D.10  D.11  D.13
        └──────────┘                    (todas paralelas tras D.5)
              ↓
            D.12 ⚠️ (necesita D.7 + D.8)
              ↓
            D.14 (close-out)
```

**Camino crítico secuencial:** D.0 → D.1 → D.2 → D.3 → D.4 → D.5 → D.6 → D.14 = ~14-17 días.
**Con paralelización post-D.5:** ~10-12 días (D.7∥D.8 luego D.12; D.9∥D.10∥D.11 paralelas; D.13 paralela).
**Hazard:** paralelización requiere git worktree por terminal (ver memoria `concurrent_terminals_git_hazard.md`) para evitar resets cruzados sobre tree compartido.

## Design decisions carried from spec § 1

Las 9 decisiones aprobadas en brainstorm gobiernan todas las fases:

| ID | Decisión | Fases afectadas |
|---|---|---|
| **D-A** | Régimen 728 only en MVP. Strategy Pattern + `RegimenConfig` versionado. | D.2, D.4, D.7, D.8, D.12 |
| **D-B** | IN 04.1-04.4+04.6+04.7. IN-light 04.5 (PDF sin PKI). OUT 04.8 (CSV bruto). OUT-parcial 04.9 (REOPENED manual). | D.4-D.13 |
| **D-C** | CRUD + audit_lite shape ES-compatible. | D.1, D.5 |
| **D-D** | File-only PLAME/T-Reg/AFPnet. Submission real diferido. | D.9, D.10, D.11 |
| **D-E** | Catálogo regulatorio híbrido (vendor + tenant custom mapped). | D.2 |
| **D-F** | Boleta empleado en `/mis-boletas` reusando EmployeeLayout existente. | D.6 |
| **D-G** | 15 sub-fases pattern-A audit-first. | TODAS |
| **D-H** | 4-tier validation con sign-off regulatorio humano. | D.4, D.7, D.8, D.12 (gated) |
| **D-I** | Greenfield apps.payroll/ (drop legacy en D.1). | D.0, D.1 |

## ADRs específicos D (producir en D.0)

D.0 audit produce el set de 8 ADRs antes que D.1 toque código:

- ADR-D.1 Strategy Pattern interface (signatures + dataclass returns)
- ADR-D.2 Decimal precision (14,4 intermedio + 12,2 final + ROUND_HALF_UP)
- ADR-D.3 audit_lite payload shape `payroll.*` (schema_version 1)
- ADR-D.4 PayrollRun concurrency (select_for_update en transitions)
- ADR-D.5 Renta 5ta correction al cese (algoritmo regularización N09)
- ADR-D.6 Tax year cutoff (diciembre 2026 → enero 2027 boundary)
- ADR-D.7 PVS validator scope (qué reglas replicamos)
- ADR-D.8 Regulatory sign-off workflow (.planning/dpay/D<N>/REGULATORY-SIGNOFF.md template)

## Adjustments anticipated by audit

D.0 audit puede ajustar la roadmap. Anticipated adjustments (a confirmar):

### Posible split de D.4

D.4 engine integra cálculo de ingresos + descuentos + Renta 5ta + EsSalud + AFP/ONP. Si BACKLOG cuenta >40 items en D.4, considerar split:
- **D.4 (ingresos + descuentos no-tributarios):** sueldo + asig fam + horas extras + AFP/ONP + EsSalud
- **D.4b (Renta 5ta):** algoritmo progresivo + denominadores mensuales + ajuste anual

### Posible split de D.9

Si los 10 archivos PLAME se vuelven 10 implementaciones distintas, considerar split:
- **D.9 (PLAME header + workers):** PLANI.txt + JORNA.txt + DERECH.txt (3 archivos críticos)
- **D.9b (PLAME complementarios):** los 7 restantes (CONCEPTOS, INCAPACIDAD, BAJAS, etc.)

### Posible adición de D.4c o D.7b

Si user al hacer sign-off de D.4 detecta gap (ej. componente faltante de la remuneración computable), se inserta D.4c antes de D.5 con el fix. Mismo patrón para D.7/D.8.

## Dependencies verified (tentative, pre-audit)

- D.0 (audit) depende de A, C, B ✓ (todos completos)
- D.1 (polish) depende de D.0 ✓
- D.2 (catalogo) depende de D.1 ✓
- D.3 (Compensation) depende de D.2 ✓
- D.4 (engine) depende de D.2 + D.3 ✓
- D.5 (lifecycle) depende de D.4 ✓
- D.6 (PaySlip + portal) depende de D.5 ✓ (B.12 PL gate disponible)
- D.7 (CTS) depende de D.4 ✓ (no de D.5 — compute es puro, persistencia separada)
- D.8 (Grati) depende de D.4 ✓ (mismo argumento)
- D.9 (PLAME) depende de D.5 ✓ (necesita PayrollRun closed)
- D.10 (T-Reg deltas) depende de D.5 + B.10 ✓
- D.11 (AFPnet) depende de D.5 ✓
- D.12 (Liquidación) depende de D.4 + D.7 + D.8 + B.14 ✓
- D.13 (CSV + REOPENED) depende de D.5 ✓
- D.14 (close-out) depende de D.6 a D.13 ✓

## Estimated effort

~3-4 semanas calendario para los 15 fases (3-4× más rápido que B porque scope técnico es menor — 11 modelos nuevos vs 62 de B; pero densidad calculatoria es mayor).

Por fase:
- D.0 audit: 1-2 días (1 person)
- D.1 polish: 1 día
- D.2-D.3 setup: 2 días c/u
- D.4 engine: 3-4 días + sign-off latency
- D.5-D.6: 2-3 días c/u
- D.7-D.8: 2-3 días c/u + sign-off latency
- D.9: 3 días, D.10: 1-2 días, D.11: 2 días
- D.12: 2-3 días + sign-off latency
- D.13: 2 días
- D.14: 1-2 días

**Sign-off latency riesgo:** D.4/D.7/D.8/D.12 quedan en branch hasta que user confirme. Si latency es >24h promedio, calendario sale a 4-5 semanas.

## Baselines a preservar (no regresar en ninguna fase)

| Métrica | Pre-D actual | Target post-D |
|---|---|---|
| Backend pytest passing | 985 | ~1100+ |
| Backend pytest failing | 1 (`test_permisos_debug` pre-existing) | 1 (mismo) |
| Frontend vitest | 178/28 files | ~200+/35+ |
| Frontend tsc | 1 (BlankEnum.ts pre-existing) | 1 (mismo) |
| Frontend ESLint | ≤ 278 | ≤ 290 |
| Frontend build | clean ~10s | clean |
| Playwright opt-in suites | 2 (tenant-isolation + lifecycle) | 3 (+ dpay-lifecycle) |
| `manage.py check` | 0 silenced | 0 silenced |

Por sub-fase, gates ANTES de merge:

```bash
cd apps/api && pytest                                            # all green vs baseline
cd apps/web && npm run lint && npm test && npm run build && npx tsc --noEmit
```

## Status legend

- ⬜ Not started
- 🟡 In progress
- ✅ Merged
- ⚠️ Regulatory sign-off pending
- ❌ Blocked (sign-off CHANGES_REQUESTED or test red)

## Next step

D.0 audit plan ya está disponible en `docs/superpowers/plans/2026-05-23-vyntia-D0-audit.md`. Para arrancarlo:
- Execute via `superpowers:subagent-driven-development` (recomendado — fresh subagent per task, review entre tareas) o `superpowers:executing-plans` (inline session).
