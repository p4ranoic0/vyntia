# B.12 Legajos Digitales Completos Implementation Plan (Module 03.5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Land Module 03.5 — Administración de Legajos — covering the 15-section
permanent digital expediente per worker, with permission-level access control,
audit logging per Ley 29733, consolidated PDF export, and the missing legajo-
content models (WorkExperience, SwornDeclaration, JobHistory) that the maestro
demands.

**Architecture:**
- **documents app:** `DigitalDossier` (OneToOne per Employee) is the legajo
  header. `DossierSection` (15 per dossier, seeded at creation) bins the
  existing `DigitalDocument` entries by maestro § 03.5 categories. Each section
  has a `permission_level` (PL 1-9 per maestro § 6.3) gating who can read it
  (médicos = 9). `DocumentAccessLog` records every access per Ley 29733 +
  SUNAFIL audit obligations.
- **employees app:** 3 missing legajo-content models — `WorkExperience`
  (previous-employer experience), `SwornDeclaration` (no parentesco / no
  incompatibilidad / intereses / impedimentos), `JobHistory` (timeline of
  puestos ocupados in the tenant).
- **DigitalDocument.contract FK:** direct FK so a document can attach
  unambiguously to a contract (currently inferred indirectly).

**Branch:** `vyntia/B12-legajos-completos`
**Backlog items in scope:**
- #94 WorkExperience model (P1, 2d)
- #95 SwornDeclaration model (P1, 2d)
- #96 JobHistory model + UI (P2, 2d)
- #117 DigitalDossier + 15 sections + DocumentAccessLog + retention 5y + cifrado AES-256 (P1, 2w)
- #118 Permission level enforcement per document type (P1, 1w)
- #119 Exportación consolidada PDF del legajo (P1, 0.5w)
- #120 DigitalDocument.contract direct FK (P2, 1d)
- #121 DocumentAccessLog Ley 29733 + SUNAFIL audit trail (P1, 1w)

**User-confirmed scope (work-without-pause mode 2026-05-14):**
- Single B.12 PR.
- 15 sections per § 6.2: datos personales, datos académicos, experiencia
  laboral previa, contratos+adendas, declaraciones juradas, identidad+CUSPP,
  historial puestos, evaluaciones, capacitaciones, reconocimientos, sanciones,
  licencias, exámenes médicos, accidentes laborales, documentos de cese.
- Permission levels: standard sections PL 3 (HR), médicos+accidentes PL 9.
- AES-256 at-rest cifrado deferred (infra concern; out-of-scope).
- OCR + auto-classification deferred (M11 / external).
- Full-text search deferred (Postgres FTS / Elasticsearch — setup is post-B).
- Consolidated PDF is a table-of-contents page + DigitalDocument metadata
  listing (the actual content files stay separate; downloading the dossier
  bundle as a single PDF stitched together is post-B).
- ARCO derecho de portabilidad (export-all-data zip) → post-B compliance phase.

**Out of scope (deferred):**
- AES-256 at-rest encryption (infrastructure decision, requires KMS).
- OCR / auto-classification of uploaded documents (M11).
- Full-text search across document contents (post-B FTS phase).
- PDF stitching of all DigitalDocument files into one (resource-intensive,
  best handled async via Celery — post-B).
- Derecho ARCO portability export (export to zip with all data + manifest) —
  separate compliance feature.

**Test baselines (post-B.11 SHA `206a663a`):**
- pytest 706/1/17, vitest 110/17, ESLint 278, tsc 1 (BlankEnum), build clean.

After B.12 expected:
- pytest **780+/1/17**, vitest **125+/19+**, ESLint flat, tsc 1, build clean.

---

## Task 1: Branch + plan + scaffold
Branch created from master at `206a663a`. Place plan, commit.

## Task 2: DigitalDossier + DossierSection
Files:
- `apps/api/apps/documents/models/digital_dossier.py`
- `apps/api/apps/documents/models/__init__.py`
- `apps/api/apps/documents/migrations/0006_b12_dossier.py`
- `apps/api/apps/documents/tests/test_b12_dossier_models.py`

15 seeded sections per § 6.2 with permission_level. ~10 tests.

## Task 3: WorkExperience + SwornDeclaration + JobHistory
Files:
- `apps/api/apps/employees/models/legajo_content.py`
- `apps/api/apps/employees/models/__init__.py`
- `apps/api/apps/employees/migrations/0011_b12_legajo_content.py`
- `apps/api/apps/employees/tests/test_b12_legajo_content.py`

WorkExperience (employer + position + dates + sector), SwornDeclaration (4
kinds — no parentesco, no incompatibilidad, intereses, impedimentos),
JobHistory (Employee → Position timeline). ~12 tests.

## Task 4: DocumentAccessLog + permission levels + Contract FK
Files:
- `apps/api/apps/documents/models/document_access_log.py`
- Edits: `apps/api/apps/documents/models/digital_document.py` — add `contract` FK + `permission_level`
- `apps/api/apps/documents/migrations/0007_b12_access_log_contract_fk.py`
- `apps/api/apps/documents/services/access_service.py`
- `apps/api/apps/documents/tests/test_b12_access_log.py`

`access_service.log_access(document, user, action, ip)` + `can_access(user, document)` checking permission_level vs user.nivel_acceso. ~10 tests.

## Task 5: dossier_service (build, consolidated PDF, attach)
Files:
- `apps/api/apps/documents/services/dossier_service.py`
- `apps/api/templates/legajo/consolidated_index.html`
- `apps/api/apps/documents/tests/test_b12_dossier_service.py`

build_dossier_for_employee (seeds 15 sections), attach_document_to_section
(infers section_id from document's tipo_documento), render_consolidated_index_html
(TOC + section list with document counts), render_consolidated_pdf
(delegate to PDFGenerator._html_to_pdf). ~10 tests.

## Task 6: API surface
Files:
- `apps/api/api/v1/documents/dossier_views.py`
- `apps/api/api/v1/employees/legajo_views.py`
- `apps/api/api/v1/documents/urls.py` (extend)
- `apps/api/api/v1/employees/urls.py` (extend)
- `apps/api/api/v1/documents/serializers_b12.py`
- `apps/api/api/v1/employees/serializers_b12.py`
- API smoke tests in both apps.

Endpoints:
```
GET    /api/v1/documents/digital-dossiers/
POST   /api/v1/documents/digital-dossiers/                (calls service)
GET    /api/v1/documents/digital-dossiers/<id>/
POST   /api/v1/documents/digital-dossiers/<id>/build/
GET    /api/v1/documents/digital-dossiers/<id>/consolidated-pdf/
GET    /api/v1/documents/dossier-sections/?dossier=<id>
GET    /api/v1/documents/document-access-logs/?document=<id>

GET    /api/v1/work-experiences/
POST   /api/v1/work-experiences/
GET    /api/v1/sworn-declarations/
POST   /api/v1/sworn-declarations/
GET    /api/v1/job-histories/
POST   /api/v1/job-histories/
```
~20 smoke tests.

## Task 7: Frontend services + admin pages
Files:
- `apps/web/src/features/documents/services/dossierService.ts` + tests
- `apps/web/src/features/employees/services/legajoContentService.ts` + tests
- `apps/web/src/features/documents/pages/DigitalDossierViewerPage.tsx` (15-section tree + download)
- Routes: `/legajo-digital/:employee_id`

~14 vitest cases.

## Task 8: Final verification + merge
Standard close-out: pytest, vitest, tsc, lint, build, memory update,
`git merge --no-ff` to master.

**Done criteria:**
- Backlog items #94, #95, #96, #117, #118, #119, #120, #121 closed.
- Baselines preserved.
