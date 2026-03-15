# Phase 1: Onboarding Self-Service - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Employees in onboarding receive their credentials, log in to a restricted view, upload their documents section by section, and see their own progress — while RRHH can monitor completion across all employees and receive alerts when employees don't respond.

Creating the employee record (CRUD de empleados) and the legajo unified view for RRHH are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Employee view structure
- Tabbed layout with 4 tabs: Personal | Familiar | Académico | Laboral
- Progress bar displayed prominently at the top of the page, above the tabs — always visible showing global % completion
- Tab Personal includes: profile photo section (prominent, at the top with Avatar component) + editable personal data fields (teléfono, dirección, fecha_nacimiento) + document upload zones (DNI, carné de extranjería)
- Each document zone shows document name + upload date + status badge after upload ('Pendiente revisión', 'Aprobado', 'Rechazado')
- When a document is rejected, the employee sees the rejection reason (observaciones field) and can upload a replacement
- When onboarding is completed and validated by RRHH: show success message + redirect to normal panel

### Document upload UX
- Drag-and-drop zone (also clickable to browse files) for each document
- One zone per document type — sections requiring multiple documents show separate zones (e.g., Familiar has separate zones for DNI familiar and Partida de nacimiento)
- After upload: zone transforms to show filename + upload date + status badge 'Pendiente revisión', button changes to 'Reemplazar'
- Progress percentage updates immediately after successful upload
- Accepted formats: PDF only for all documents; photos (JPG/PNG) only for profile photo
- Maximum file size: 10 MB per file. Show clear error if exceeded.

### RRHH monitoring panel
- Filterable table with columns: Empleado | Estado | Progreso (%) | Fecha inicio | Alerta | Acciones
- Progress shown as progress bar + % value in the table row
- Filters available: by estado (pendiente_datos / pendiente_documentos / pendiente_validacion / observado / completado), by % completion range, by date range (fecha_inicio), by alerta de 5 días, and by employee name or DNI (search)
- Actions per row: Ver detalle, Reenviar credenciales, Validar/Rechazar onboarding, Ver documentos pendientes (expand or tooltip)
- Alerta column shows ⚠ when employee has not submitted any document AND 5+ days have passed since welcome email

### Email failure handling
- When RRHH creates an onboarding and email_enviado=false: show visible alert banner "¡Onboarding creado! El correo no se pudo enviar." with two buttons: [Reintentar enviar] and [Corregir correo y reintentar]
- "Corregir correo" opens an inline field to edit the email address before retrying
- Backend already returns email_enviado flag in the response — frontend uses this to trigger the alert

### 5-day no-response alerts
- Alert condition: employee has not made their first successful login AND 5+ days have passed since fecha_email_bienvenida
- Detection: calculated in real time when RRHH loads the monitoring panel (no cron needed)
- Alert indicator: ⚠ badge in the Alerta column of the table + filter "Con alertas" to show only these rows
- Internal notification: sent once when 5 days are reached, then daily reminder until employee logs in AND submits at least one document
- Notifications appear in the system's notification panel (header)

### Claude's Discretion
- Skeleton loading states while fetching data
- Exact spacing, typography, and color palette within existing design system
- Error state handling for failed API calls
- Exact animation/transition details for upload zones
- How to store last_login for alert detection (can use Django's last_login field on Usuario or a separate tracking field)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `OnboardingEmpleado` model: fully built with state machine, progreso_porcentaje property, items_pendientes, email tracking fields
- `OnboardingService`: crear_onboarding_completo, enviar_email_bienvenida (Celery + sync fallback), actualizar_estado_onboarding, reenviar_email_bienvenida, validar_onboarding — all implemented
- `OnboardingViewSet`: CRUD, mi_onboarding endpoint, validar/rechazar actions — all exist
- Email templates: back/templates/emails/bienvenida.html and bienvenida.txt already exist
- Celery task: send_email_html_task exists in back/app_rrhh/tasks.py
- UI components: Card, Tabs, Progress, Badge, Avatar, Skeleton, Dialog, Table, Button — all available in front/src/components/ui/
- Frontend feature structure: front/src/features/onboarding/{components,pages,services,types}/ directories exist but are empty (stub index.ts only)
- Generated API types: OnboardingEmpleado, OnboardingIniciarRequest, EstadoOnboardingEnum, OnboardingValidacion types are already generated in front/src/generated/api/

### Established Patterns
- API responses wrapped in APIResponse: { success, message, data, meta } — frontend services must unwrap
- React Query v5 for all server state — follow existing hooks pattern in src/hooks/useApi.ts
- Service layer pattern: onboarding API calls should live in front/src/features/onboarding/services/
- @require_hr() decorator for RRHH-only endpoints, @require_authenticated() for mixed access
- Django's last_login field is set automatically on each login — usable for the 5-day alert detection

### Integration Points
- Employee restricted view: App.tsx routing — onboarding employees must be redirected to onboarding view, not the admin panel
- RRHH panel: likely a new page under AdminLayout, linked from the existing Sidebar
- Document uploads: reuse/extend DocumentosDigitales model and existing upload infrastructure

</code_context>

<specifics>
## Specific Ideas

- Alert banner on email failure must include "Corregir correo" option — user explicitly requested ability to fix wrong email before retry
- 5-day alert reminder is daily, stopping only when employee logs in AND submits at least one document (not just login)
- Alerta de 5 días visible both in table row (⚠ column) AND as internal notification to RRHH

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

---

## Phase 1 Expansion — New Requirements (2026-03-15)

Phase 1 was reopened. The following requirements are added on top of the completed Waves 0-4.

### What is CONFIRMED COMPLETE (do not rebuild)
- Document upload infrastructure (subir-foto, subir-documento actions)
- DocumentUploadZone component with drag-and-drop, status badges, rejection reason display
- OnboardingProgressBar
- RRHH admin panel with progress bars, alerts, email correction
- OnboardingRoute guard (blocks admin panel)
- Welcome email + corregir-correo flow

### New Data Registration Requirements

**Personal tab (extends existing)**
- Employee must fill: nombres, apellidos, DNI/doc_identidad, fecha_nacimiento, telefono_celular, direccion_domicilio, foto de perfil
- Must upload 1 copy of DNI/carnet de extranjeria/documento de identidad (REQUIRED — mandatory)

**Familiar tab (major expansion)**
- Employee can register N dependents (DatosFamiliares records via employee-accessible API)
- Per dependent: nombres, apellidos, parentesco, fecha_nacimiento, DNI/documento
- Required documents by parentesco (enforced validation — cannot submit without):
  - hijo(a): DNI del familiar + partida de nacimiento
  - conyuge / conviviente: DNI del familiar + acta de matrimonio OR certificado de union de hecho
  - padre / madre: DNI del familiar + partida de nacimiento del empleado (acredita vinculo)
- UI: "Agregar dependiente" button opens form; each dependent card shows required docs with upload zones

**Academico tab (major expansion — replaces current simple upload)**
- Employee registers N certificados de estudio: institucion, fecha_inicio, fecha_fin → upload archivo PDF
- Employee registers N cursos/diplomados: nombre del curso, institucion, fecha_inicio, fecha_fin, horas → upload archivo PDF
  - NOTE: CursosCertificaciones is a NEW model (not in DatosAcademicos) — needs to be created
- Employee registers N titulos profesionales: tipo (bachiller | titulo_profesional | maestria | doctorado | especializacion), nombre de carrera, institucion, fecha_inicio, fecha_fin → upload archivo PDF
  - Stored in DatosAcademicos with nivel_educativo matching tipo
- UI: each category is a separate accordion/section with "Agregar" button; each item is a card with its own upload zone

**Laboral tab (partial change)**
- Employee registers N constancias/certificados de trabajo: empresa, fecha_inicio, fecha_fin → upload archivo PDF
  - NOTE: work experience linked to DocumentosDigitales (new simple linking — empresa+fechas stored in documento's entidad_emisora + fechas)
- RRHH-managed fields remain read-only (cargo, area, regimen, sueldo) — no change
- Employee still uploads: DDJJ, CV, carta de recomendacion

### Document Preview + Explicit Submit Flow

**Before any file is submitted:**
1. User selects/drops file → preview modal opens automatically
2. Modal shows: PDF viewer (PDF.js or iframe) OR image preview, filename, file size
3. Modal has two buttons: "Cancelar" (discard) and "Enviar documento" (confirm upload)
4. Only after confirming does the POST to the API happen
5. On success: zone updates to show filename + "Pendiente revision" badge

### Per-Document Status Feedback (extends existing)

**Each uploaded document zone shows:**
- pendiente_revision → amber badge "Pendiente revisión"
- aprobado → green badge "Aprobado" + green checkmark
- rechazado → red badge "Rechazado" + motivo de rechazo visible + button "Corregir y reenviar"
  - "Corregir y reenviar" re-opens the upload zone (same preview flow) + clears rejection and sets back to pendiente_revision on upload

**Progress bar update:**
- Progress should reflect approved documents (not just uploaded)
- Recalculate: progreso_porcentaje = (docs aprobados / total docs requeridos) * 100

### Email Notifications (new)

- **Documento rechazado**: cuando RRHH rechaza un documento individual → email al empleado con nombre del doc + motivo
- **Onboarding aprobado**: cuando RRHH valida y aprueba el onboarding completo → email de felicitacion al empleado con instrucciones de acceso completo
- **Onboarding rechazado/observado**: cuando RRHH marca como observado → email al empleado con observaciones y que debe corregir

### Toast / Error Handling (new)

Every user action must trigger a toast notification:
- Upload success: "Documento enviado correctamente"
- Upload error (server): "Error al subir el documento. Intenta nuevamente."
- File too large (>10MB): "El archivo supera el límite de 10MB"
- Invalid format: "Solo se aceptan archivos PDF" / "Solo se aceptan imágenes JPG o PNG"
- Form save success: "Datos guardados correctamente"
- Form save error: "Error al guardar. Verifica los campos."
- Network error: "Sin conexión. Verifica tu internet."

### RRHH Admin Panel — Per-Document Approval (new)

- In the onboarding detail view for an employee: show list of all uploaded documents with current estado
- Each document row: preview button, approve button, reject button (with motivo input)
- Endpoint needed: POST /api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/aprobar/
- Endpoint needed: POST /api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/rechazar/ (body: motivo)

### Technical Notes

- CursosCertificaciones model MUST be created (does not exist in DB)
- DatosFamiliares → DocumentosDigitales linking: add FK `familiar` (nullable) to DocumentosDigitales OR create DocumentoFamiliar junction model
- DatosAcademicos → DocumentosDigitales: add nullable FK `documento` to DocumentosDigitales in DatosAcademicos
- Employee-accessible endpoints: DatosFamiliaresViewSet, DatosAcademicosViewSet need IsAuthenticated permission for employee's own records (currently RRHH-only)
- PDF preview: use `<iframe src={url}>` for PDFs already uploaded; for pre-upload use URL.createObjectURL(file)

*Phase expansion context gathered: 2026-03-15*

*Phase: 01-onboarding-self-service*
*Context gathered: 2026-03-13 (original) + 2026-03-15 (expansion)*
