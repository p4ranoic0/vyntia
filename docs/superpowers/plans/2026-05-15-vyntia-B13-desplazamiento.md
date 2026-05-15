# B.13 Desplazamiento Implementation Plan (Module 03.6)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 03.6 — Desplazamiento — covering the 7 SERVIR/DL 276 tipos
de desplazamiento (rotación, encargatura, destaque, comisión de servicios,
designación, transferencia, permuta) plus the missing API/UI for LocationHistory.

**Architecture:**
- **organization app:** `Displacement` (header with kind + origen + destino +
  fechas + status + resolution_number) and `DisplacementExtension` (renovaciones
  con SLA y motivo). Workflow lifecycle: draft → pending_supervisor →
  pending_hr → pending_titular → approved → active → completed | cancelled.
  Sector público SERVIR es el caso primario; sector privado puede usarlo para
  rotaciones internas (`kind=rotacion`).
- **LocationHistory (existing):** add the missing REST endpoints + admin UI
  (#101).

**Branch:** `vyntia/B13-desplazamiento`
**Backlog items in scope:**
- #101 LocationHistory REST + UI (P1, 1w)
- #122 Displacement + 7 kinds + workflow (P1, 2w)

**User-confirmed scope (work-without-pause 2026-05-15):**
- Single B.13 PR covering both items.
- Workflow es lineal (no aprobaciones paralelas / committees). 3 approvers
  fijos: supervisor → HR → titular. Quien dispara cada approve es el
  `request.user`; un futuro phase puede generalizar a per-tenant config.
- Resolution number is opaque CharField (no auto-correlativo) — auto-gen
  defer; we accept user-supplied or empty.
- Resolution PDF is reused from `pdf_generator._html_to_pdf` chain via a
  single `resolucion.html` template.

**Out of scope (deferred):**
- Notificaciones a Tesorería si afecta planilla (separate notifications phase).
- Integración con SUT (Sistema Único de Trámites SERVIR) → external.
- Correlativo de resoluciones administrativas → post-B.
- Approval committee model with per-tenant configurable steps → M11 / workflow engine.

**Test baselines (post-B.12 SHA `935b1068`):**
- pytest 767/1/17, vitest 121/19, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.13 expected:
- pytest **815+/1/17**, vitest **130+/21+**, ESLint flat, tsc 1, build clean.

---

## Task 1: Branch + plan + scaffold

## Task 2: Displacement + DisplacementExtension models
Files:
- `apps/api/apps/organization/models/displacement.py`
- `apps/api/apps/organization/models/__init__.py`
- `apps/api/apps/organization/migrations/0011_b13_displacement.py`
- `apps/api/apps/organization/tests/test_b13_displacement_models.py`

Kinds: rotacion / encargatura / destaque / comision / designacion / transferencia / permuta.
Status: draft → pending_supervisor → pending_hr → pending_titular → approved → active → completed | cancelled.
~12 tests.

## Task 3: displacement_service
Files:
- `apps/api/apps/organization/services/__init__.py`
- `apps/api/apps/organization/services/displacement_service.py`
- `apps/api/templates/desplazamiento/resolucion.html`
- `apps/api/apps/organization/tests/test_b13_displacement_service.py`

Actions: submit / approve_supervisor / approve_hr / approve_titular / activate /
complete / cancel / extend. render_resolution_html + render_resolution_pdf.
~10 tests.

## Task 4: API surface
Files:
- `apps/api/api/v1/organization/displacement_views.py`
- `apps/api/api/v1/organization/displacement_serializers.py`
- `apps/api/api/v1/organization/urls.py` (extend)
- `apps/api/apps/organization/tests/test_b13_api_smoke.py`

Endpoints under `/api/v1/organization/`:
```
GET/POST/DETAIL  displacements/
POST             displacements/<id>/submit/
POST             displacements/<id>/approve-supervisor/
POST             displacements/<id>/approve-hr/
POST             displacements/<id>/approve-titular/
POST             displacements/<id>/activate/
POST             displacements/<id>/complete/
POST             displacements/<id>/cancel/
GET              displacements/<id>/resolution-pdf/

GET/POST         displacement-extensions/
GET/POST         location-histories/    (LocationHistory CRUD — #101)
```
~16 smoke tests.

## Task 5: Frontend services + admin pages
Files:
- `apps/web/src/features/organization/services/displacementService.ts` + tests
- `apps/web/src/features/organization/services/locationHistoryService.ts` + tests
- `apps/web/src/features/organization/pages/DisplacementListPage.tsx`
- Route `/desplazamiento`

~14 vitest cases.

## Task 6: Final verification + merge
Standard close-out.
