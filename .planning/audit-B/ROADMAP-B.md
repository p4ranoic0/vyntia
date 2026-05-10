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
