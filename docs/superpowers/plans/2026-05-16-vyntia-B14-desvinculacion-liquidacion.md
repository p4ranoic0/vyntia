# Phase B.14 — Desvinculación + liquidación (Module 03.7)

**Branch:** `vyntia/B14-desvinculacion-liquidacion`
**Spec:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`
**Master roadmap:** `docs/superpowers/plans/2026-05-09-vyntia-B-vyntia-core-master-roadmap.md`
**Backlog items:** #123 (Termination), #124 (SeveranceSettlement), #125 (WorkCertificate), #126 (SystemsOffboarding + ExitInterview + HandoverChecklist), #127 (Baja T-Registro + 48h SLA alert)
**ADR baseline:** ADR-B.9 (severance minimum legal scope) — followed strictly.

## Goal

Ship the complete *cese* / offboarding flow for a contracted employee: termination model with régimen-aware causales (728/276/CAS), minimum-legal severance computation (CTS proporcional + vacaciones truncas + gratificación trunca + indemnización despido arbitrario), Art. 45 LPCL Constancia de Trabajo PDF generator, SystemsOffboarding + ExitInterview + HandoverChecklist coordination, and reuse of B.10 T-Registro client for the baja declaration with a 48h pago SLA alert.

Out-of-scope per ADR-B.9: full payroll engine (D), AFP/ONP detractions, multi-régimen variants, Cesantía/Jubilación.

## Tasks

### Task 1 — Plan + branch (DONE)

### Task 2 — Backend models
Files to create:
- `apps/api/apps/contracts/models/termination.py` — `Termination` (OneToOne with Contract; régimen + causal + workflow draft → in_progress → completed → liquidated → baja_t_registro_done | cancelled; reason + effective_date + last_day_worked + carta_renuncia_file + acta_cese_file).
- `apps/api/apps/contracts/models/severance_settlement.py` — `SeveranceSettlement` (OneToOne with Termination; computed_at + paid_at + paid_total + manual_override JSON + 48h SLA helpers) + `SeveranceLine` (component enum cts/vac_truncas/grat_trunca/indemnizacion/otros + amount + base_calculation + formula_note).
- `apps/api/apps/documents/models/work_certificate.py` — `WorkCertificate` (FK Termination + employee + contract; fecha_emision + numero_constancia + signed_by + pdf_file). Art. 45 LPCL.
- `apps/api/apps/onboarding/models/exit_flow.py` — `ExitInterview` (OneToOne Termination + 6 standard questions JSON + sentiment enum + comments + interviewer + interview_date), `HandoverChecklist` (OneToOne Termination + status draft → in_progress → completed; signed_by_outgoing + signed_by_incoming + receiving_user FK), `HandoverItem` (FK checklist + kind enum (proyecto/documento/equipo/acceso/credencial/otro) + name + description + status pendiente/entregado/no_aplica + delivered_at + notes), `SystemsOffboarding` (OneToOne Termination + 6 standard systems checks JSON + checklist status enum + completed_at).

Migrations:
- `contracts/migrations/0007_b14_termination.py`
- `contracts/migrations/0008_b14_severance_settlement.py`
- `documents/migrations/0008_b14_work_certificate.py`
- `onboarding/migrations/0004_b14_exit_flow.py`

Re-exports in each app's `models/__init__.py`.

### Task 3 — Services
- `apps/api/apps/contracts/services/termination_service.py`
  - `initiate_termination(contract, causal, fecha_cese, last_day_worked, motivo='', user=None)` — creates Termination(status='in_progress'); refuses if Contract is not ACTIVO.
  - `complete_termination(termination, user)` — transitions in_progress → completed; stamps `completed_at`/`completed_by`; flips Contract.status → TERMINADO.
  - `liquidate(termination, user)` — requires SeveranceSettlement.paid_at; transitions completed → liquidated.
  - `mark_baja_tregistro_done(termination, declaration_id)` — links to existing TRegistroDeclaration(declaration_type='baja') and transitions to `baja_t_registro_done`.
  - `cancel(termination, reason, user)` — soft cancel anywhere up to liquidated.
  - `list_pending_baja_tregistro_48h(tenant=None)` — completions older than 48h without baja submitted (SLA alert).
- `apps/api/apps/contracts/services/severance_service.py`
  - `compute_settlement(termination)` per ADR-B.9 — pulls Contract + EmploymentData (for sueldo) + vacation balance (best-effort, defaults 0 if vacation module not seeded for this empleado) — generates 4 lines.
  - Formulas:
    - **CTS proporcional**: sueldo × (months_in_semester / 6) + 1/6 grati last semester (simplified: sueldo × months/12 for the partial period from last semestre depósito or contract start, whichever is later, up to fecha_cese). Cap at sueldo.
    - **Vacaciones truncas**: (sueldo / 30) × (días_acumulados or pro-rated por trabajo no gozado del último año). Days = floor(meses_trabajados_año × 2.5) − días_gozados.
    - **Gratificación trunca**: sueldo × (months_in_semester / 6). Semester boundaries Ene–Jun (paga Julio) / Jul–Dic (paga Diciembre).
    - **Indemnización despido arbitrario**: only if causal in `{'despido_arbitrario', 'despido_indirecto'}`. = 1.5 sueldos × years_worked, capped at 12 sueldos.
  - Persists 4 SeveranceLine rows; returns SeveranceSettlement.
  - `mark_paid(settlement, paid_total, paid_at)` — stamps paid_total + paid_at; raises if total mismatch >5%.
- `apps/api/apps/documents/services/work_certificate_service.py`
  - `generate_certificate(termination, user)` — builds template context (employee name, doc, fecha_inicio, fecha_cese, cargo, area, motivo_cese textual), renders HTML, delegates to PDFGenerator chain, saves WorkCertificate row + PDF file.
- `apps/api/apps/onboarding/services/exit_flow_service.py`
  - `scaffold_exit_flow(termination, user=None)` — creates ExitInterview (empty), HandoverChecklist (empty + 4 default items: proyecto, documento, equipo, accesos), SystemsOffboarding (with 6 default systems checks: correo/vpn/erp/ad/badge/llaves).
  - `mark_interview_done(interview, answers, sentiment, comments, interviewer)`.
  - `mark_item_delivered(item, notes='')`.
  - `complete_handover(checklist, signed_by_outgoing, signed_by_incoming)` — requires all required items delivered or no_aplica.
  - `complete_systems_offboarding(offboarding, performed_checks)` — fills checks JSON + completed_at.

Templates:
- `apps/api/templates/cese/constancia_trabajo.html` — Art. 45 LPCL (full HTML; same chain handles PDF).

### Task 4 — API surface + smoke tests

Routes under `/api/v1/contracts/` (extend `apps/api/api/v1/contracts/urls.py`):
- `terminations/` — CRUD + actions: `complete`, `liquidate`, `mark-baja-tregistro-done`, `cancel`, `alertas-48h-sla` (collection).
- `severance-settlements/` — CRUD + actions: `compute`, `mark-paid`.

Routes under `/api/v1/documents/` (extend `apps/api/api/v1/documents/urls.py`):
- `work-certificates/` — CRUD + actions: `generate` (per termination), `download-pdf` (file response).

Routes under `/api/v1/onboarding/` (extend `apps/api/api/v1/onboarding/urls.py`):
- `exit-interviews/` — CRUD + actions: `submit`.
- `handover-checklists/` — CRUD + actions: `complete`.
- `handover-items/` — CRUD + actions: `deliver`.
- `systems-offboardings/` — CRUD + actions: `complete`.

All ViewSets use `TenantAwareViewSetMixin` + `RRHHPermission`. Smoke tests:
- `apps/contracts/tests/test_b14_api_smoke.py` (≥ 6 tests: terminations CRUD + 2 actions + auth gating).
- `apps/documents/tests/test_b14_api_smoke.py` (≥ 4 tests: work-certificates routing + auth gating).
- `apps/onboarding/tests/test_b14_api_smoke.py` (≥ 4 tests: 4 viewsets routing).

Model/service tests:
- `apps/contracts/tests/test_b14_termination.py` (lifecycle + cancel + relations).
- `apps/contracts/tests/test_b14_termination_service.py` (initiate + complete + liquidate + 48h SLA list).
- `apps/contracts/tests/test_b14_severance.py` (SeveranceSettlement + Line clean rules).
- `apps/contracts/tests/test_b14_severance_service.py` (4 formula tests + integration).
- `apps/documents/tests/test_b14_work_certificate.py` (generate path).
- `apps/onboarding/tests/test_b14_exit_flow.py` (scaffold + complete chain).

### Task 5 — Frontend services + admin pages

Services:
- `apps/web/src/features/contracts/services/terminationService.ts`
- `apps/web/src/features/contracts/services/severanceSettlementService.ts`
- `apps/web/src/features/documents/services/workCertificateService.ts`
- `apps/web/src/features/onboarding/services/exitInterviewService.ts`
- `apps/web/src/features/onboarding/services/handoverChecklistService.ts`
- `apps/web/src/features/onboarding/services/systemsOffboardingService.ts`

Pages (lazy + AdminRoute):
- `apps/web/src/features/contracts/pages/TerminationListPage.tsx` — list + workflow actions + 48h SLA alerts strip.
- `apps/web/src/features/contracts/pages/SeveranceSettlementListPage.tsx` — list + compute + mark-paid + line-breakdown drawer.
- `apps/web/src/features/onboarding/pages/ExitFlowListPage.tsx` — combined view: ExitInterview + Handover + SystemsOffboarding per termination.

Routes:
- `/cese/terminaciones` → TerminationListPage
- `/cese/liquidaciones` → SeveranceSettlementListPage
- `/cese/flujo` → ExitFlowListPage

Vitest tests for each service file (shape coverage only).

### Task 6 — Final baseline + merge

Verification:
- `pytest` (compare against B.13 baseline 767/1/17 — expect new tests added).
- `npm run lint` (preserve 278).
- `npm run typecheck` (preserve 1).
- `npm run build` (clean).
- `python manage.py check --settings=vyntia.settings.development` (0 silenced).

Merge with `--no-ff` to master. Update `subproject_b_progress.md` memory with B.14 close-out.
