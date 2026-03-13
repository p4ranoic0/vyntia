# Project Research Summary

**Project:** Sistema de Gestión de RRHH — Intranet
**Domain:** HR Intranet, Peruvian Public Sector
**Researched:** 2026-03-13
**Confidence:** HIGH

## Executive Summary

This is a mature, partially-built HR intranet for a Peruvian public sector entity operating under DL 276, DL 728, DL 1057, and locación de servicios regimes. Research confirms that the data model is largely complete — all key models (Empleado, DatosLaborales, PlanillaMensual, DetallePlanilla, SolicitudVacaciones, DocumentosDigitales, OnboardingEmpleado, ConfiguracionAfp, BoletaPago) are already defined and migrated. The work remaining is primarily views, workflows, export logic, and configuration — not new modeling. The recommended approach is to fix blocking infrastructure issues first (settings mismatch, production syntax error, email silent failures, ReportLab stub), then build user-facing feature layers in strict dependency order: onboarding self-service before legajo, legajo before payroll exports, and payroll calculation before payroll exports.

The most significant technical risk is the Windows PDF generation chain. WeasyPrint always fails on Windows due to missing GTK, and the current ReportLab fallback outputs a hardcoded stub ("DOCUMENTO GENERADO") rather than actual document content. This means all currently generated PDFs — contracts, certificates, and boletas — contain no real content. xhtml2pdf must be established as the primary HTML-to-PDF engine for templated documents (certificates, contracts), and ReportLab Platypus must be built out for structured payroll documents (boletas). A secondary structural risk is that development.py points to PostgreSQL while the actual runtime uses MySQL — this means any developer running migrations or tests against the default settings is operating against the wrong engine.

Legally, the Peruvian payroll calculation must correctly bifurcate by labor regime: DL 728 and DL 276 employees contribute to AFP or ONP, CAS employees have EsSalud calculated as 9% of 45% UIT monthly (not 9% of full salary), and locación/consultoría workers are subject to 8% fourth-category retention rather than payroll deductions. AFP Net and PDT-PLAME exports are statutory monthly obligations and must conform to fixed SUNAT/AFP formats. Gratificaciones and CTS are correctly identified as out of scope for v1 and must be deferred.

## Key Findings

### Recommended Stack

The stack requires minimal change — almost everything is already installed. The only required dependency change is replacing `psycopg2-binary` with `mysqlclient` in `requirements.txt` and aligning `development.py` to use `django.db.backends.mysql`. On the frontend, `react-dropzone` is the one new package needed for drag-and-drop file upload UX; everything else (`react-pdf`, `react-hook-form`, `axios`, `@tanstack/react-query`, `openpyxl`, `reportlab`, `xhtml2pdf`, `celery`, `redis`, `pillow`) is already installed.

See `.planning/research/STACK.md` for full details.

**Core technologies:**
- `Django 4.2 + DRF`: Backend API — already in use; extend with new ViewSets following existing patterns
- `openpyxl`: Excel export (AFP Net, PDT-PLAME, descuentos) — already installed; build export service
- `xhtml2pdf + ReportLab`: PDF generation — already installed; fix engine priority order and replace stub
- `react-dropzone`: Frontend file upload UI — new addition; integrates with existing react-hook-form
- `Celery + Redis`: Async email — already configured; requires Celery worker running in deployment
- `mysqlclient`: MySQL driver — already in venv; needs requirements.txt fix to match runtime

**Critical configuration gaps (no new libraries):**
- Email SMTP settings missing from `production.py` / `staging.py`
- `development.py` DATABASE ENGINE must be changed to MySQL
- `FILE_UPLOAD_MAX_MEMORY_SIZE` not set to 10MB in settings
- Media URL serving not wired in `config/urls.py` for development
- `production.py` has a syntax error at EOF that will crash production startup

### Expected Features

See `.planning/research/FEATURES.md` for full details, legal citations, and model field mappings.

**Must have — Onboarding:**
- Email de bienvenida al crear usuario (known bug: ggarcia never received it)
- Vista restringida del empleado: only own data visible during onboarding
- Per-section document upload: DNI, DDJJ, certificados académicos, foto de perfil
- Checklist de progreso visible al empleado (model property already exists)
- Flujo observado/corrección: RRHH rechaza y solicita re-subida
- Notificación a RRHH cuando onboarding pasa a `pendiente_validacion`

**Must have — Legajo Digital:**
- Vista RRHH unificada por sección (todos los datos y documentos del empleado)
- Descarga individual de documentos, filtrado por tipo y categoría
- Indicador de documentos pendientes / vencidos
- Vista de solo lectura del empleado sobre su propio legajo

**Must have — Remuneraciones:**
- Motor de cálculo planilla bifurcado por régimen (728/276/1057/locación)
- AFP descuento correcto (aporte 10% + comisión flujo/mixta + prima seguro)
- ONP 13%, EsSalud 9% empleador, retención renta 5ta (escala progresiva anual)
- Boleta de pago descargable por el empleado (DL 728 Art. 19 — obligatorio)
- Exportación Excel AFP Net (formato fijo por AFP regulación)
- Exportación Excel PDT-PLAME 601 (formato SUNAT fijo, mapeo de códigos por régimen)
- Carga masiva de descuentos (préstamos, judiciales)
- Estado de planilla con workflow (borrador → generada → aprobada → pagada)

**Must have — Vacaciones:**
- Solicitud y saldo vacacional en autoservicio
- Aprobación doble: jefe directo + RRHH (obligatorio en sector público peruano)
- Fraccionamiento, registro de goce efectivo y reincorporación
- Reporte récord vacacional por servidor (exigido en auditorías SUNAFIL)
- Alertas de vacaciones vencidas (riesgo legal DL 713 Art. 23)

**Should have (differentiators):**
- Generación automática de planilla desde DatosLaborales sin ingreso manual
- Alerta de contratos por vencer con reporte por oficina
- Suspensión retención 4ta categoría con control de tope anual
- Panel cumplimiento onboarding para RRHH (todos los pendientes en una vista)
- Exportación ZIP para carga en sistema AIRHSP

**Defer to v2+:**
- Gratificaciones julio/diciembre (promedio semestral — depende de historial estable)
- CTS (depósito semestral — depende de historial de períodos)
- Liquidaciones de cese completo
- Firma digital electrónica (PKI — alta complejidad legal)
- Módulo de cambio de datos con aprobación (requiere modelo `SolicitudCambioDatos` nuevo)
- Selección y reclutamiento, desvinculación, inducción virtual, rendimiento SERVIR

### Architecture Approach

The existing layered architecture must be followed without exception: React services unwrap the `{ success, message, data, meta }` APIResponse envelope; Django ViewSets call services for business logic and return `APIResponse` for JSON endpoints (never bypassed — except for file download responses which use raw `HttpResponse` with MIME type). All models stay in `app_rrhh`. All access control uses the existing decorator set (`@require_hr()`, `@require_admin()`, `@require_authenticated()`). The critical addition is an ownership filter: any endpoint accessible to non-RRHH users must scope results to `empleado_id=request.user.empleado.empleado_id`.

See `.planning/research/ARCHITECTURE.md` for full data flows, extension patterns, and anti-patterns.

**Major components:**
1. **Onboarding flow** — `OnboardingService` + `DocumentosDigitalesViewSet` + employee-scoped permission; email fix is independent
2. **Legajo digital** — Backend aggregation action on Empleado ViewSet returning all sections in one response; frontend tabbed view consuming single endpoint
3. **Payroll engine** — `PlanillaCalculoService` (exists) + Excel export actions on `PlanillaMensualViewSet` using openpyxl; non-APIResponse pattern for downloads
4. **Vacation reports** — New `@action` endpoints on Vacaciones ViewSet for saldo, récord, provisión mensual; approval workflow already implemented
5. **PDF generation** — xhtml2pdf primary for templated documents; ReportLab Platypus for boletas; WeasyPrint disabled on Windows

### Critical Pitfalls

See `.planning/research/PITFALLS.md` for full details, warning signs, and per-phase warnings.

1. **Celery email silent failure** — `send_email_html_task.delay()` fails silently if Redis/Celery not running; bare `except` swallows both Celery and SMTP errors; employee created with no credentials. Fix: validate email delivery result in `crear_onboarding_completo` and log at ERROR level on failure; never silently swallow.

2. **ReportLab stub produces blank PDFs** — On Windows, the fallback always reaches ReportLab which outputs "DOCUMENTO GENERADO" placeholder text, not actual document content. All current generated PDFs are empty stubs. Fix: establish xhtml2pdf as primary engine; build real Platypus layouts for boletas; add integration test asserting PDF size > 5KB.

3. **Settings mismatch: development.py points to PostgreSQL, runtime is MySQL** — Fresh installs will fail; MySQL/PostgreSQL behavioral differences (case sensitivity, JSON fields, `AUTO_INCREMENT` vs `SERIAL`) mask bugs in testing. Fix: align `development.py` to MySQL immediately; this is a pre-requisite for all phases.

4. **Decimal precision loss in payroll** — `float()` wrapping of Decimal values before JSON serialization loses centimos; AFP rates may fall back to hardcoded outdated values if no `ConfiguracionAfp` record exists for the period; `renta_quinta_categoria` field name is misleading (stores 4th-category retention). Fix: use `str()` or `Decimal.quantize()`; require `ConfiguracionAfp` per period with no silent fallback.

5. **`tamano_archivo_legible` property mutates DB field** — The property divides `self.tamano_archivo` in-place, corrupting the instance and persisting wrong values on `save()`. Fix immediately before bulk document upload goes live.

6. **`production.py` syntax error at EOF** — Duplicate `ADMIN_URL` line will crash Django startup in production. Fix immediately and add CI settings import check.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 0: Infrastructure Fixes
**Rationale:** Three immediate defects block every subsequent phase. These must be resolved before any feature work begins. No new behavior is built here — only correctness.
**Delivers:** Working settings for MySQL, email that does not silently fail, PDFs that contain real content, no production startup crash.
**Addresses:** Settings mismatch (Pitfall 3), production syntax error (Pitfall 12), `tamano_archivo_legible` mutation bug (Pitfall 14), email silent failure root cause (Pitfall 1).
**Actions:**
- Fix `development.py` DB engine to MySQL; add `mysqlclient` to `requirements.txt`, remove `psycopg2-binary`
- Fix `production.py` EOF syntax error
- Fix `tamano_archivo_legible` property mutation
- Configure email backend: `locmem` for testing, `filebased` for development, SMTP for production/staging
- Set `FILE_UPLOAD_MAX_MEMORY_SIZE = 10MB` and `DATA_UPLOAD_MAX_MEMORY_SIZE = 10MB` in `base.py`
- Wire MEDIA URL serving in `config/urls.py` for development
- Fix PDF engine priority: xhtml2pdf primary, skip WeasyPrint on `sys.platform == 'win32'`, ReportLab stub last (marked emergency-only)

### Phase 1: Onboarding Self-Service
**Rationale:** This is the highest-priority user-visible gap. The known bug (ggarcia no email) is the entry point. Employee-scoped permissions are a security prerequisite for all employee self-service. File upload must come before legajo (legajo is meaningless without documents).
**Delivers:** Employees can receive credentials, log in, upload their documents section by section, and track onboarding progress. RRHH can review, observe, and approve documents.
**Addresses:** Email de bienvenida, vista restringida empleado, upload DNI/DDJJ/certificados/foto, flujo observado/corrección, notificación RRHH, panel cumplimiento onboarding.
**Avoids:** Pitfall 1 (email silent failure — fixed in Phase 0), Pitfall 4 (file size enforcement — add `validate_file_size` validator), Pitfall 10 (Windows path separators — use `pathlib.Path.as_posix()`).
**Research flag:** Standard patterns; no research-phase needed. `OnboardingService`, `DocumentosDigitales`, and `OnboardingEmpleado` are fully modeled.

### Phase 2: Legajo Digital
**Rationale:** Depends on Phase 1 — a legajo view without documents is empty. The backend aggregation approach (single `/api/v1/rrhh/empleados/{id}/legajo_completo/` action) is recommended over N frontend queries to reduce round trips. `legajoService.ts` and `LegajoPage.tsx` already exist.
**Delivers:** RRHH has a unified tabbed view of all employee data (personal, laboral, contratos, documentos, remuneraciones). Employee has read-only view of own legajo. Inline PDF and image document preview.
**Addresses:** Vista RRHH unificada, descarga individual, indicador documentos pendientes, empleado ve propio legajo, historial auditado.
**Avoids:** Pitfall 8 (`unique_together` null behavior — add application-level dedup before creating new document versions).
**Research flag:** Standard patterns; no research-phase needed. All data already exists in models; work is aggregation and frontend composition.

### Phase 3: Remuneraciones — Calculation and Exports
**Rationale:** The payroll engine (`PlanillaCalculoService`) exists but Excel exports do not. This phase has no dependency on onboarding or legajo — it can be scoped independently. However, the calculation must be correct before exports are built, since AFP Net and PDT-PLAME are statutory and errors have legal consequences.
**Delivers:** Complete monthly payroll workflow: calculation by regime, boleta PDF download per employee, AFP Net Excel export, PDT-PLAME Excel export, descuentos masivos, retención certificates.
**Addresses:** Motor cálculo planilla (bifurcado 728/276/1057/locación), renta 5ta progresiva, EsSalud CAS especial, boleta PDF, AFP Net, PDT-PLAME, descuentos masivos, certificados retención 4ta y 5ta.
**Avoids:** Pitfall 5 (decimal precision — use `str()`/`Decimal.quantize()`, require `ConfiguracionAfp` per period), Pitfall 9 (Excel column mapping — DNI as zero-padded string, dates as `DD/MM/YYYY` string), Pitfall 11 (`APIResponse.error()` 400 default — use explicit 500 for server-side calculation failures).
**Research flag:** AFP Net and PDT-PLAME column schemas need validation against current official specifications before implementation. The field mapping is well understood but the exact sheet layout and header rows should be confirmed against a real AFP Net sample file and the current PDT 601 format. Flag for research-phase during planning.

### Phase 4: Vacaciones — Completion and Reporting
**Rationale:** The approval workflow (two-stage jefe + RRHH) is already implemented. The missing pieces are the employee-facing saldo query, fraccionamiento validation UI, and report generation. This phase is largely finishing existing work.
**Delivers:** Employee self-service saldo vacacional, RRHH full vacation reporting suite (récord vacacional per employee, vacaciones no gozadas/truncas, reporte por oficina, reporte mensual provisión para finanzas).
**Addresses:** Consulta saldo vacacional, alertas vacaciones vencidas, reporte récord vacacional, reporte provisión mensual finanzas.
**Avoids:** Pitfall 7 (consecutive contract accrual — validate with HR team whether accrual is per-contract or continuous before building the calculation).
**Research flag:** Confirm accrual rule for consecutive CAS contracts with the HR team before building `PeriodoVacacional` accrual logic. This is a business rule, not a technical pattern.

### Phase Ordering Rationale

- Phase 0 before everything: settings mismatch and production syntax error are blockers for all development; the `tamano_archivo_legible` mutation is a data integrity bug that must not reach production.
- Phase 1 before Phase 2: legajo requires documents to exist; documents require onboarding upload to work.
- Phase 3 independent of 1 and 2: payroll has no dependency on onboarding or legajo at the data level; it can run in parallel with Phases 1–2 if team capacity allows, or sequentially after.
- Phase 4 last: vacation reporting extends already-working approval workflow; no other phase depends on it.

### Research Flags

Phases needing deeper research during planning:
- **Phase 3 (Remuneraciones):** AFP Net exact column schema and PDT-PLAME 601 current format need validation against a live sample file or current SUNAT/AFP documentation before building export service. The field mapping is known; the exact layout is not confirmed from codebase alone.

Phases with standard patterns (skip research-phase):
- **Phase 0:** Pure bug fixes and configuration — well-understood, no ambiguity.
- **Phase 1:** All models and services exist; onboarding patterns are established in the codebase.
- **Phase 2:** Aggregation endpoint and tabbed frontend view — standard DRF + React Query pattern.
- **Phase 4:** Approval workflow already implemented; reports are standard queryset + export pattern.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Based on direct codebase inspection of requirements.txt, installed venv, and settings files. The only uncertainty is AFP Net/PDT-PLAME exact column formats. |
| Features | HIGH | Legal framework (DL 276/728/1057, LIR, AFP regs, SUNAT PDT) is statutory and stable. Model inventory verified by direct code read. |
| Architecture | HIGH | Based on direct codebase inspection of services, views, models, and frontend. Patterns are consistent and well-established. |
| Pitfalls | HIGH | Critical pitfalls 1, 2, 3, 12, and 14 are confirmed from direct code inspection, not inference. |

**Overall confidence:** HIGH

### Gaps to Address

- **AFP Net / PDT-PLAME column schema:** Exact column positions, header row format, and sheet names for AFP Net; exact record layout and type codes for PDT-PLAME 601. Resolve before building Excel export service in Phase 3. Action: obtain a sample AFP Net submission file from HR and a current SUNAT PDT 601 spec.
- **CAS vacation accrual for consecutive contracts:** Whether vacation days accumulate across consecutive CAS contracts or reset per contract is a business rule, not a technical question. Resolve with the HR team before building `VacationCalculationService` accrual in Phase 4.
- **AFP commission rates currency:** `ConfiguracionAfp` must be populated with current AFP rates (they change annually per SBS resolution). The hardcoded fallback values in `PlanillaCalculoService` are likely outdated. Resolve by populating `ConfiguracionAfp` records for all active periods before running any payroll calculation.
- **AIRHSP export format:** AIRHSP (planilla web AIRHSP) export format was mentioned as a differentiator. The exact spec was not researchable from the codebase. Resolve with the entity's IT or finance team.

## Sources

### Primary (HIGH confidence)
- Direct codebase — `back/app_rrhh/models/` (empleado.py, remuneracion.py, vacaciones.py, onboarding.py, documentos_digitales.py, configuracion_uit.py)
- Direct codebase — `back/app_rrhh/services/` (onboarding_service.py, planilla_calculo_service.py, vacation_approval_service.py, pdf_generator.py)
- Direct codebase — `back/config/settings/` (base.py, development.py, production.py)
- Direct codebase — `back/core/` (responses.py, decorators.py, pagination.py)
- Direct codebase — `back/api/v1/rrhh/` (remuneraciones_views.py, serializers.py)
- Direct codebase — `front/src/services/` (onboardingService.ts, legajoService.ts)
- Django 4.2 official documentation — email, file upload, static/media serving, validators
- `CLAUDE.md` and `back/logs/django.log` — MySQL backend confirmation

### Secondary (MEDIUM confidence)
- Peruvian labor law training knowledge (DL 276, DL 728, DL 1057, DL 713, Ley 25129, Ley 26790, LIR Art. 74-75, AFP Net format, PDT-PLAME 601 structure) — normativa estable al agosto 2025
- openpyxl library capabilities — training knowledge (docs access restricted during session)

### Tertiary (LOW confidence)
- AFP Net exact column schema — needs validation against current AFP documentation or sample file
- PDT-PLAME 601 current format — needs validation against current SUNAT PDT documentation
- AIRHSP export format — not in codebase; needs spec from entity

---
*Research completed: 2026-03-13*
*Ready for roadmap: yes*
