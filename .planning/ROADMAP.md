# Roadmap: Sistema de Gestión de RRHH — Intranet

## Overview

The intranet is built in five sequential phases. Phase 0 unblocks all development by fixing four confirmed defects that corrupt data or crash the system. Phase 1 delivers employee self-service onboarding — the entry point of the single-source-of-truth legajo. Phase 2 surfaces the legajo to RRHH and adds the data-change approval workflow and document generation. Phase 3 builds the complete payroll workflow: calculation, boleta delivery, and statutory exports (AFP Net, PDT-PLAME). Phase 4 closes vacaciones: employee self-service saldo queries, fraccionamiento, and the full RRHH reporting suite. Each phase delivers one verifiable capability; the next phase depends on it being complete.

## Phases

**Phase Numbering:**
- Integer phases (0, 1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 0: Infrastructure Fixes** - Eliminate four blocking defects before any feature work begins (completed 2026-03-13)
- [ ] **Phase 1: Onboarding Self-Service** - Employees receive credentials, register their data (personal/familiar/academic/laboral), preview and upload documents with per-document approval feedback, and receive email notifications (reopened 2026-03-15: expanded scope)
- [ ] **Phase 1.1: Onboarding Datos Completos** - Complete personal data (banking, domicile, pension system), document viewer for uploaded files, section-level approval status, and document upload integrated within familiar/academic/laboral forms
- [ ] **Phase 2: Legajo Digital y Gestion de Informacion** - RRHH unified legajo view, document generation, and employee data-change approval workflow
- [ ] **Phase 3: Remuneraciones** - Monthly payroll calculation, boleta delivery, and statutory Excel exports
- [ ] **Phase 4: Vacaciones** - Employee saldo self-service, fraccionamiento, and RRHH vacation reporting suite

## Phase Details

### Phase 0: Infrastructure Fixes
**Goal**: The system runs correctly on MySQL, generates real PDF content, and does not silently corrupt file-size data or crash on startup
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04
**Success Criteria** (what must be TRUE):
  1. Django starts in production without errors (the duplicate ADMIN_URL syntax error is gone)
  2. Running migrations against the development settings uses MySQL, not PostgreSQL
  3. A generated PDF (certificate, contract, or boleta) contains actual document content — not the placeholder text "DOCUMENTO GENERADO"
  4. Reading `tamano_archivo_legible` on a DocumentosDigitales instance does not alter the value stored in the database
**Plans**: 3 plans

Plans:
- [x] 00-01-PLAN.md — Fix production.py SyntaxError and align development.py + requirements.txt to PostgreSQL (INFRA-01, INFRA-02)
- [ ] 00-02-PLAN.md — Fix tamano_archivo_legible mutation bug with unit tests (INFRA-04)
- [ ] 00-03-PLAN.md — Fix PDF generation to produce real content via xhtml2pdf (INFRA-03)

### Phase 1: Onboarding Self-Service
**Goal**: Employees in onboarding receive credentials, log in to a restricted view, register all their data (personal, N dependents with required docs per relationship type, N academic records, N courses/diplomados, N work certs, N professional titles, laboral files only), preview documents before submitting with an explicit send button, track per-document approval status, and receive email notifications on approval/rejection — RRHH approves/rejects each document individually and validates or rejects the full onboarding
**Depends on**: Phase 0
**Requirements**: ONBD-01 through ONBD-15
**Success Criteria** (what must be TRUE):
  1. When RRHH creates an onboarding user, the employee receives a welcome email with their credentials
  2. An employee logged in during onboarding sees only their own data sections and cannot access the admin panel
  3. Employee fills all personal data fields (nombres, apellidos, DNI, fecha_nacimiento, telefono, direccion, foto)
  4. Employee registers N family dependents; required docs per relationship: hijo(a) → DNI + partida nacimiento; conyuge/conviviente → DNI + acta matrimonio or cert union de hecho; padres → DNI + partida nacimiento
  5. Employee uploads 1 copy of own DNI/carnet de extranjeria (required mandatory field)
  6. Employee registers N certificados de estudio (institucion, fecha inicio, fecha fin) each with file upload
  7. Employee registers N cursos/diplomados (institucion, nombre, fecha inicio, fecha fin, horas) each with file upload
  8. Employee registers N constancias/certificados de trabajo (fecha inicio, fecha fin) each with file upload
  9. Employee registers N titulos profesionales/bachiller/maestria/doctorado (institucion, carrera, tipo, fecha inicio, fecha fin) each with file upload
  10. Laboral tab: employee only uploads files (DDJJ, CV, carta recomendacion) — no editing of RRHH fields
  11. Before submitting any file: employee sees preview (PDF viewer or image) and confirms with explicit "Enviar" button
  12. Each uploaded document shows individual status: pendiente_revision / aprobado / rechazado — rejection reason visible, "Corregir y reenviar" option available
  13. Onboarding progress bar updates as documents are approved (not just uploaded)
  14. Employee receives email when full onboarding is approved; receives email with observations when rejected/observed
  15. RRHH approves or rejects each document individually from admin panel; can approve/reject full onboarding
  16. Toast/notification feedback on every action: upload success, upload error, file too large, invalid format, server error
**Plans**: 7 completed + 6 new plans

Plans (completed — Waves 0-4):
- [x] 01-01-PLAN.md — Wave 0: Test scaffold — conftest.py + test_onboarding_service.py + test_onboarding_api.py
- [x] 01-02-PLAN.md — Wave 1: Backend serializer (last_login) + corregir-correo endpoint
- [x] 01-03-PLAN.md — Wave 1: Backend subir-foto + subir-documento actions
- [x] 01-04-PLAN.md — Wave 2: Frontend routing guard + DocumentUploadZone + upload service + types
- [x] 01-05-PLAN.md — Wave 3: Employee self-service tabbed page (OnboardingEmployeePage + 4 tabs)
- [x] 01-06-PLAN.md — Wave 3: RRHH admin panel enhancements (progress bars, alerts, email correction flow)
- [x] 01-07-PLAN.md — Wave 4: Human verification checkpoint

Plans (new — Waves 5-8):
- [x] 01-08-PLAN.md — Wave 5: Backend models — CursosCertificaciones + DocumentoFamiliar linking + DatosAcademicos FK to DocumentosDigitales
- [x] 01-09-PLAN.md — Wave 5: Backend endpoints — employee CRUD for familiares/academicos/cursos/titulos + per-document approve/reject + notification emails
- [x] 01-10-PLAN.md — Wave 6: Frontend — N-item dynamic forms (familiar+docs, certificados, cursos, titulos, laboral uploads)
- [x] 01-11-PLAN.md — Wave 6: Frontend — document preview modal (PDF.js + image) + explicit Enviar button flow
- [x] 01-12-PLAN.md — Wave 7: Frontend — per-document status feedback + Corregir y reenviar flow + improved toast/error handling
- [x] 01-13-PLAN.md — Wave 8: Human verification checkpoint (ONBD-01 through ONBD-15)

### Phase 1.1: Onboarding Datos Completos
**Goal**: The employee onboarding form captures all personal data required by HR (banking details, full domicile, pension system with AFP conditional fields), employees can view any previously uploaded document, a section-level status panel shows progress per section (PERSONAL/FAMILIAR/ACADÉMICO/LABORAL), and documents can be uploaded directly within the add-item dialogs for familiares, académicos, and laboral entries
**Depends on**: Phase 1
**Requirements**: ONBD-16, ONBD-17, ONBD-18, ONBD-19, ONBD-20, ONBD-21
**Success Criteria** (what must be TRUE):
  1. Personal tab shows and saves: género, estado civil, RUC, distrito/provincia/departamento domicilio, entidad bancaria, nro. cuenta, CCI, sistema de pensiones (AFP PRIMA/INTEGRA/PROFUTURO/HABITAT, ONP, PENSIONISTAS, SIN PENSION)
  2. When AFP is selected, the form shows: CUSPP code field, tipo comisión selector (flujo / mixta)
  3. Employee can click any uploaded document badge/icon to open a preview of that document (using the existing DocumentPreviewModal or a viewer equivalent)
  4. A section status panel shows PERSONAL / FAMILIAR / ACADÉMICO / LABORAL each with an indicator: ✓ Completo / ⏳ En revisión / ⚠ Observado / ○ Pendiente
  5. The "Agregar dependiente" dialog includes optional document upload fields for the applicable doc type (DNI, partida nacimiento, or acta matrimonio per parentesco)
  6. The "Agregar" dialogs for académico entries include an optional document upload within the same dialog
  7. The "Agregar experiencia laboral" dialog includes an optional constancia de trabajo upload within the same dialog
**Plans**: TBD

### Phase 2: Legajo Digital y Gestion de Informacion
**Goal**: RRHH has a single unified view of every employee's complete record with document download and audit trail; employees can propose data changes that RRHH approves before they take effect; the system generates certificates, contracts, and AIRHSP export files on demand
**Depends on**: Phase 1
**Requirements**: LEGJ-01, LEGJ-02, LEGJ-03, LEGJ-04, INFO-01, INFO-02, INFO-03, INFO-04, INFO-05, INFO-06, INFO-07
**Success Criteria** (what must be TRUE):
  1. RRHH opens any employee's legajo and sees all sections (personal, familiar, academico, laboral, contratos, documentos) in a single tabbed view with document status indicators (presentado / pendiente / vencido)
  2. RRHH can download any document from the legajo directly from that view
  3. Every legajo access and document modification is recorded with the acting user and timestamp, and RRHH can view this audit trail
  4. An employee proposes a change to their personal, contact, or family data; RRHH receives an alert, reviews the change, and approves or rejects it — the change only appears in the record after RRHH approval
  5. RRHH receives an alert before a contract or adenda expires and can generate a report of upcoming expirations broken down by office
  6. The system generates certificates of employment and work clearances, contracts and adendas, and AIRHSP bulk-load Excel files for new hires and departures — all downloadable as real files with actual content
**Plans**: TBD

### Phase 3: Remuneraciones
**Goal**: RRHH can configure payroll parameters, run the monthly payroll correctly bifurcated by labor regime, produce the statutory AFP Net and PDT-PLAME Excel exports, load bulk discounts, and issue downloadable boletas — while employees can view and download their own boleta from the portal
**Depends on**: Phase 0
**Requirements**: REMU-01, REMU-02, REMU-03, REMU-04, REMU-05, REMU-06, REMU-07, REMU-08, REMU-09, REMU-10, REMU-11, REMU-12, REMU-13
**Success Criteria** (what must be TRUE):
  1. RRHH configures salary parameters (base pay, bonuses, gratificaciones, deductible and non-deductible discounts, retentions, social charges by regime) and the payroll engine uses those parameters without hardcoded fallbacks
  2. The monthly payroll is generated with correct calculations per regime (DL 728, DL 276, DL 1057, locacion): AFP/ONP deductions, EsSalud at the correct rate for CAS, and fourth-category retention for locacion workers
  3. RRHH uploads a bulk discount file (Excel) and the discounts are applied to the correct employees in the next payroll run
  4. An employee logs in to the portal and can view and download their boleta de pago for any closed period
  5. RRHH downloads AFP Net and PDT-PLAME 601 Excel files whose column layout and content exactly match the current AFP and SUNAT specifications
  6. RRHH downloads all supplementary Excel reports (by bank/modality, by discount modality, by pension system, net income summary, zipped planilla web) and the Certificados de Retencion de 4ta and 5ta categoria in PDF
**Plans**: TBD

### Phase 4: Vacaciones
**Goal**: Employees can check their vacation balance and submit requests online; the two-stage approval workflow (jefe + RRHH) operates correctly; RRHH has the full vacation reporting suite required by SUNAFIL audits
**Depends on**: Phase 2
**Requirements**: VACA-01, VACA-02, VACA-03, VACA-04, VACA-05, VACA-06, VACA-07, VACA-08, VACA-09, VACA-10
**Success Criteria** (what must be TRUE):
  1. An employee sees their current vacation balance online and can submit a vacation request (including fractional days) from the portal
  2. The jefe inmediato receives a notification and approves or rejects the request; if approved, RRHH is notified and can make a final decision; the employee is notified of the outcome at each step
  3. The system accumulates vacation days correctly per labor regime and contract type following DL 713, and integrates vacation periods into liquidation calculations
  4. RRHH reviews all pending requests in one view, identifies scheduling conflicts or overlaps, approves or rejects, and the employee's balance updates automatically upon approval
  5. RRHH generates all required vacation reports: record vacacional per employee, vacaciones no gozadas and truncas, total by office, and the monthly provisional report for finanzas (calculated by month/day worked, discounting unpaid leaves)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 0 → 1 → 2 → 3 → 4
(Phase 3 depends on Phase 0 only — can run in parallel with Phases 1-2 if desired, but sequential is safer)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Infrastructure Fixes | 3/3 | Complete   | 2026-03-13 |
| 1. Onboarding Self-Service | 8/13 | In Progress|  |
| 2. Legajo Digital y Gestion de Informacion | 0/TBD | Not started | - |
| 3. Remuneraciones | 0/TBD | Not started | - |
| 4. Vacaciones | 0/TBD | Not started | - |
