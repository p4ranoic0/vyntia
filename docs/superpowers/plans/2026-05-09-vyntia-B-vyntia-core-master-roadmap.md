# Sub-project B — Master Roadmap (confirmed by B.0 audit)

> Confirmed phase structure for sub-project B. Each phase is a separate branch and PR, mergeable independently.
> Source spec: `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`.
> Audit date: 2026-05-09. Roadmap version: **CONFIRMED** (Task 13 of B.0 audit complete).

## Phase table

| Fase | Branch | Scope | Necesita | Plan detallado |
|------|--------|-------|----------|----------------|
| B.0  | `vyntia/B0-audit` | Audit & inventory (this phase) | A, C | `2026-05-09-vyntia-B0-audit.md` |
| B.1  | `vyntia/B1-polish-baseline` | Polish wave: bug-fix baseline (pytest, tsc, lint, tenant audit fixes) | B.0 | TBD post-B.0 |
| B.2  | `vyntia/B2-polish-identity` | Polish wave: identity (users, roles, RBAC UI) | B.1 | TBD |
| B.3  | `vyntia/B3-polish-organization` | Polish wave: organization (departments, locations, company config) | B.1 | TBD |
| B.4  | `vyntia/B4-polish-employees` | Polish wave: employees (Empleado + datos personales/familiares/académicos) | B.1 | TBD |
| B.5  | `vyntia/B5-polish-contracts` | Polish wave: contracts + L3.10.3 stale consumer audit + ViewSet tenant gaps | B.1 | TBD |
| B.5b | `vyntia/B5b-polish-documents-onboarding` | Polish wave: documents + onboarding (L3.11 + media segregation + email branding) | B.1 | TBD |
| B.6  | `vyntia/B6-positions-orgchart` | Módulo 02: Position + OrgChart | B.3 | TBD |
| B.7  | `vyntia/B7-ccf-salaryband` | Módulo 02: CCF (Ley 30709) + SalaryBand | B.6 | TBD |
| B.8  | `vyntia/B8-mpp-cpe` | Módulo 02: MPP + CPE (SERVIR) | B.6 | TBD |
| B.9  | `vyntia/B9-seleccion` | Módulo 03.1: Selección (7-model module) | B.6 | TBD |
| B.10 | `vyntia/B10-vinculacion-tregistro` | Módulo 03.2: Vinculación + T-Registro | B.5 | TBD |
| B.11 | `vyntia/B11-induccion-prueba` | Módulo 03.3+4: Inducción + Período de prueba | B.10 | TBD |
| B.12 | `vyntia/B12-legajos-completos` | Módulo 03.5: Legajos digitales completos | B.5b | TBD |
| B.13 | `vyntia/B13-desplazamiento` | Módulo 03.6: Desplazamiento (rotación, encargatura, destaque) | B.10 | TBD |
| B.14 | `vyntia/B14-desvinculacion-liquidacion` | Módulo 03.7: Desvinculación + liquidación | B.10 | TBD |
| B.15 | `vyntia/B15-policies` | Módulo 01: Policies | B.1 | TBD |
| B.16 | `vyntia/B16-e2e-close-out` | E2E + docs + tag b-vyntia-core-complete | B.1-B.15 | TBD |

## Order and dependencies

Diagram:

```
B.0 → B.1 → B.2-B.4 (polish wave, parallel)
            B.5 → B.5b → B.6 → B.7 (CCF)
                             → B.8 (MPP/CPE)
                             → B.9 (Selección)
                             → B.10 (Vinculación)
                                  │
                                  ▼
                                B.11 → B.13 → B.14
                                B.12 (parallel to B.10+)
            ▼
          B.15 (Policies, parallel to B.6+)
            ▼
          B.16 (close-out)
```

## Adjustments by audit (confirmed 2026-05-09)

The 16-phase tentative outline from the spec was confirmed with these adjustments after audit:

### 1. B.5 split into B.5 + B.5b

The original B.5 had 21 backlog items spanning 3 apps (contracts, documents, onboarding). Workload distribution was unbalanced:
- **L3.10.3 stale consumers in contracts:** 8 items (items #59-66 in BACKLOG, ~1.5w effort)
- **L3.11 stale consumers in documents:** 10 items (items #22-30 in BACKLOG, ~1.5w effort)
- **Onboarding + documents Polish:** 3 items (items #32, #33, #80-86 in BACKLOG, ~1.5w effort)

Splitting avoids a 4.5-week single phase and maintains clean app boundary:

- **B.5 (contracts polish):** ~10 items, ~1.5 weeks
  - L3.10.3 stale consumer audit (ContractAmendment field renames, EmploymentData.generar_codigo_empleado, ContratosAdendasViewSet query bugs)
  - ViewSet tenant gaps (perform_create orphans, permission enforcement on ContractAmendmentViewSet)
  - DatosLaboralesViewSet filter/field bugs (non-existent fields in search, ordering, filtering)
  - Pytest gap additions (smoke tests for ContratosAdendasViewSet, DatosLaboralesViewSet)

- **B.5b (documents + onboarding polish):** ~11 items, ~1.5 weeks
  - L3.11 stale consumers in DocumentGenerationViewSet (14 critical bugs: Contract/Employee field renames, documento_id AttributeErrors, creada_por kwarg mismatch, regex UUID mismatches, ID query param collisions)
  - TemplateService stale consumer fixes (estado_display, creado_por_id attributes, hardcoded config)
  - WordTemplateService stale consumer fixes (contrato.numero_adenda AttributeError, Contract.estado field)
  - Media filesystem segregation (cross-tenant upload leak risk, auth-walled /media/)
  - Onboarding polish (ViewSet tenant filtering, OnboardingService field bugs, email branding cleanup)
  - Document generation smoke tests + ViewSet migration from `api/v1/app_rrhh/` to `api/v1/documents/views.py`

### 2. Dependency adjustment: B.10 now depends on B.5 instead of B.6

With the B.5 split:
- B.5 (contracts polish) must complete before B.10 (Vinculación + T-Registro) due to contract tenancy fixes
- B.5b (documents + onboarding) must complete before B.12 (Legajos) due to document system polish

### 3. Phase numbering preserved

No cascade renumbering applied. B.5 and B.5b coexist; subsequent phases B.6-B.16 keep original numbers.
**Total phase count:** 18 (B.0, B.1, B.2, B.3, B.4, B.5, B.5b, B.6, B.7, B.8, B.9, B.10, B.11, B.12, B.13, B.14, B.15, B.16)

### 4. Dependencies verified

- B.2-B.4 (polish phases) depend on B.1 ✓
- B.5, B.5b depend on B.1 ✓
- B.6 (Position + OrgChart) depends on B.3 (organization polish) ✓
- B.6 requires cargo string→FK migration as backlog item #104 ✓ (flagged as data migration risk)
- B.7-B.8 depend on B.6 (sector/role boundaries) ✓
- B.9 (Selección) depends on B.6 ✓
- B.10 (Vinculación + T-Registro) depends on B.5 (contracts polish) ✓
- B.11 (Inducción + prueba) depends on B.10 (can't induct without contract) ✓
- B.12 (Legajos) depends on B.5b (documents polish) ✓
- B.13 (Desplazamiento) depends on B.10 (moves already-contracted employee) ✓
- B.14 (Desvinculación) depends on B.10 (termination needs contract context) ✓
- B.15 (Policies) is independent, can run parallel to B.6+ ✓
- B.16 (E2E close-out) depends on all B.1-B.15 ✓

### 5. Estimated effort

~22-25 weeks across 18 phases (matches original spec upper-bound estimate "~15-18 phases"). The 18-phase total reflects the depth of L3 stale consumer cleanup in contracts/documents, which was underestimated in the initial spec.

### 6. No phases removed

All 18 phases retain at least 1 backlog item. B.16 (E2E close-out) has 1 verification item by design (item #132: Playwright lifecycle test).

### 7. B.7 and B.8 NOT merged

Despite small item counts (4 each):
- **B.7 (CCF + SalaryBand):** targets private sector (Ley 30709 LCT compliance) — 1w each
- **B.8 (MPP + CPE):** targets public sector (SERVIR) — 1w each
Per ADR-B.6, distinct sector boundaries require separate phases for clean RBAC and reporting. Both are P1 and ship in the same quarter, but code isolation is important for long-term maintenance.

### 8. B.9 (Selección) kept as single phase

Despite 1 backlog item (item #110), the scope is large: 7-model module (PersonnelRequisition, JobPosting, JobApplication, Candidate, SelectionStage, CandidateEvaluation, MeritRanking) with full workflow. Backlog item count is not the only signal of phase weight; effort estimate dominates (2w).

## Cross-references

- **Backlog:** `.planning/audit-B/BACKLOG.md` (132 items, 22-25 weeks estimated effort)
- **Inventory:** `.planning/audit-B/INVENTORY.md` (source material from Tasks 1-10)
- **ADRs:** `.planning/audit-B/ADRS.md` (6 architectural decision records)
- **Audit plan:** `docs/superpowers/plans/2026-05-09-vyntia-B0-audit.md` (Tasks 1-13 + learnings)
