# Sub-project B — Vyntia Core Functional — Close-out summary

**Period:** 2026-05-09 → 2026-05-19 (10 days)
**Tag:** `b-vyntia-core-complete`
**Branch convention:** `vyntia/B<N>-<short-name>` merged with `--no-ff`
**Spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`
**Master roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`
**Audit:** `.planning/audit-B/{INVENTORY,BACKLOG,ROADMAP-B,ADRS}.md`

## What sub-project B delivered

After Foundation (A) and Multi-tenancy (C), VYNTIA had a tenant-scoped
schema and a polished frontend reorg — but most of Module 03 (the
employment lifecycle) was still 70%-done legacy code with stale L3.x
consumers and missing pieces. Sub-project B closed every functional
gap that blocks selling **Vyntia Core** in Starter tier.

It also absorbed sub-projects E (Extensión Organización) and F
(Policies) per the B-spec decision — both fit naturally into the
Module 01 / Module 02 phases that B already had to do, so spinning
them up as separate sub-projects would have duplicated planning
overhead.

### Modules delivered

**Module 01 — Planificación + Políticas:**
- B.15a: Policy + PolicyVersion + ApprovalFlow + Publication + Acknowledgment.
- B.15b: HRStrategicPlan + StrategicObjective + KPI; WorkforcePlan +
  HeadcountProjection + SuccessionPlan + KeyPosition + SuccessorCandidate;
  ComplianceMatrix + ComplianceObligation + Evidence + alerts.

**Module 02 — Estructura organizacional:**
- B.6: Position (versioned per ADR-B.7) + PositionProfile + Plaza + OrgChart.
- B.7: Category (Ley 30709) + SalaryBand + CCF documents.
- B.8: MPP + CPE + PositionRegister (SERVIR / DL 276/728).

**Module 03 — Ciclo de vida laboral:**
- B.9: Selección (PersonnelRequisition + JobPosting + Candidate +
  SelectionStage + CandidateEvaluation + MeritRanking).
- B.10: Vinculación + T-Registro (TRegistroDeclaration + SUNAT alta).
- B.11: Inducción + Período de prueba (InductionPlan + Tasks + Materials;
  ProbationPeriod + Evaluation).
- B.12: Legajos digitales completos (LegajoIndex + retention + search).
- B.13: Desplazamiento (Displacement + DisplacementExtension + LocationHistory).
- B.14: Desvinculación + liquidación (Termination + SeveranceSettlement +
  SeveranceLine + WorkCertificate + ExitInterview + HandoverChecklist +
  SystemsOffboarding) — minimum-legal scope per ADR-B.9.

**Cross-cutting polish (B.1-B.5b):**
- TenantAwareViewSetMixin (centralized `perform_create` + `get_queryset`
  tenant filtering across all 6 Core apps).
- audit_lite app (AuditEvent for high-stakes mutations, per ADR-B.2).
- L3.10.3 stale consumer audit in contracts (4 critical bugs fixed).
- L3.11 stale consumer audit in documents (~14 DocumentGenerationViewSet
  bugs fixed).
- Media filesystem segregation per tenant (ADR-B.4: TenantStorage).
- Email branding sweep (5 onboarding templates: "Intranet" → "VYNTIA").
- Login bypass + JWT `intentos_fallidos` counter fixes.
- ESLint ignore for `src/generated/`.

## Phase-by-phase log

See master roadmap `## Phase table` for the full table with merge SHAs.

```
B.0  Audit & inventory                      4bb747b9 2026-05-09
B.1  Polish baseline                         dff98e67 2026-05-09
B.2  Polish identity                         b529b149 2026-05-10
B.3  Polish organization                     a98e3891 2026-05-10
B.4  Polish employees                        0b3a3c99 2026-05-10
B.5  Polish contracts                        c5e152d1 2026-05-10
B.5b Polish documents + onboarding           0059cd7f 2026-05-10
B.6  Positions + OrgChart                    79ccb27e 2026-05-10
B.7  CCF + SalaryBand                        28265dcf 2026-05-10
B.8  MPP + CPE                               bb4130a0 2026-05-10
B.9  Selección                               48c93ab7 2026-05-10
B.10 Vinculación + T-Registro                4dde71d9 2026-05-14
B.11 Inducción + Período de prueba           206a663a 2026-05-14
B.12 Legajos completos                       935b1068 2026-05-14
B.13 Desplazamiento                          ec1c04f8 2026-05-15
B.14 Desvinculación + liquidación            f16f05f1 2026-05-16
B.15a Policy Manager (Module 01)             98f1bbf5 2026-05-17
B.15b Strategic + Workforce + Compliance     ce1534d1 2026-05-17
B.16 E2E + close-out                         (this commit)        2026-05-19
```

## Key architectural decisions (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| B.1 | i18n strategy: code English, UI Spanish, legal terms preserved (DNI/RUC/CTS/SUNAT) | Aligns with team familiarity; preserves Peruvian regulatory readability |
| B.2 | `audit_lite` app vs full event sourcing | Minimum AuditEvent suffices for compliance; full sourcing deferred to X |
| B.3 | Inline approval flows per workflow, not generic engine | Workflow engine = sub-project T; B keeps approval scope narrow |
| B.4 | `TenantStorage` filesystem layout `media/<tenant_id>/<category>/YYYY/MM/` | Hard isolation, no shared symlinks |
| B.5 | Three-tier testing: pytest unit + pytest integration + opt-in Playwright lifecycle | Per-phase CI stays fast; release gate covers composition |
| B.6 | Sector field on tenant (`private` / `public`) drives SERVIR vs LCT branching | Avoids module duplication; conditional logic at field level |
| B.7 | Inline versioning (`parent_version` FK + `is_current` boolean) for Position/Contract | Queryable historical references; simpler than `django-simple-history` |
| B.8 | `@xyflow/react` for OrgChart frontend | Bundle size acceptable; rich interactions out of the box |
| B.9 | Severance: minimum legal in B (4 components: CTS + vac_truncas + grat_trunca + indemnización capped) | Full payroll engine ships in D |

## Metrics: B.0 baseline vs B.16 final

| Métrica | B.0 baseline (post-C) | B.16 final | Spec target |
|---|:---:|:---:|:---:|
| Apps Django con tests de aislamiento | 1 | 7 | 7 ✓ |
| Modelos tenant-scoped | ~20 | ~62 | ~50 ✓ |
| Endpoints REST documentados | ~80 | ~230 | ~200 ✓ |
| Pytest passed | 271 | **982** | ≥ 350 ✓ |
| Vitest passed | 32 | **178** | ≥ 50 ✓ |
| Playwright e2e suites | 1 (tenant-isolation, opt-in) | 2 (+ lifecycle, opt-in) | ≥ 8 cases ✓ |

All metrics meet or exceed the spec § 8 targets.

## Lecciones aprendidas

1. **Audit-first works.** B.0 (3-5 day pure audit, zero code) produced
   the 132-item BACKLOG and the 9-ADR set that drove the next 17 phases.
   Phases that referenced the audit by item number were faster to plan
   and easier to verify than ad-hoc phases. Worth repeating in D.

2. **Polish wave before greenfield.** Doing B.1-B.5b (cross-cutting
   fixes + tenant gaps + stale consumer cleanup) before the Module 02/03
   work made the new modules cheaper to build — they inherited a clean
   ViewSet pattern, audit_lite, and TenantStorage out of the box.

3. **Phase splits when scope grows.** B.5 split into B.5 + B.5b
   (contracts vs documents+onboarding) and B.15 split into B.15a +
   B.15b (Policy manager vs Strategic/Workforce/Compliance) avoided
   4-week single phases. Same heuristic in C worked there too.

4. **Module 02 before Module 03.** Positions + CCF + MPP are
   prerequisites that almost every Module 03 module touches. Doing
   Module 02 first saved string FK fixups later.

5. **Opt-in heavy E2E.** ADR-B.5 three-tier strategy held up — no
   single phase took on Playwright work mid-feature; B.16 absorbed it
   as a release gate.

6. **L3 stale-consumer debt.** The L3.10.x → L3.11 rename wave left
   ~24 silent consumer bugs (FieldError, AttributeError) that the
   B.0 audit surfaced via grep. Cleanup recipe: `replace_all`
   reverberates further than one suspects (LR22-LR29 in subproject_b_progress).

## What's deferred (post-B)

- **Vyntia Pay (D):** full payroll engine — PLAME, T-Registro deltas,
  AFPnet, CTS calculation, gratificaciones, full severance with all
  régimen variants.
- **Workflow engine (T):** generic approval/state-machine engine.
  Current approval flows are inline per workflow.
- **Cron infrastructure (cron_celery):** real cron for compliance
  vencimiento alerts, probation reminders, ack reminders. Today all
  are exposed as manual endpoints.
- **DocType engine (U):** metadata-driven forms.
- **Permissions v2 (V):** RBAC + permlevel 0-9 + ABAC.
- **Notifications (W):** email/push/in-app channels.
- **Audit Log v2 (X):** event-sourced trail (today: audit_lite).

## How to consume this summary

This document is the canonical hand-off for the next sub-project
brainstorm (D). When `gsd-new-milestone` or
`superpowers:brainstorming` opens D, point it at this file plus
`docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`
for the constraints that B locked in (TenantStorage, audit_lite,
TenantAwareViewSetMixin, etc.).
