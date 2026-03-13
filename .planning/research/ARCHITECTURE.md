# Architecture Patterns

**Domain:** HR Intranet — Sistema de Gestión de RRHH
**Researched:** 2026-03-13
**Confidence:** HIGH (based on direct codebase inspection)

---

## Existing Architecture (Baseline)

The codebase already has a clear, working layered architecture. All new modules must conform to it rather than introduce new patterns.

```
Browser (React 18 + TypeScript)
  └── src/services/*.ts          (API call wrappers, unwrap APIResponse envelope)
       └── src/hooks/useApi.ts   (React Query v5 query/mutation hooks)
            └── src/pages/**     (Pages and page-level components)

Django (DRF)
  └── api/v1/<domain>/views.py  (ViewSets + @action decorators)
       └── api/v1/<domain>/serializers.py
            └── app_rrhh/services/<domain>_service.py  (business logic)
                 └── app_rrhh/models/<model>.py         (ORM + model methods)
                      └── MySQL bd_rrhh_intranet
```

### Core Constraints Already Established

- **Single Django app**: All models live in `app_rrhh`. No new apps.
- **All responses**: Must use `APIResponse` from `core/responses.py`. Shape: `{ success, message, data, meta }`.
- **All access control**: Must use `@require_hr()`, `@require_admin()`, `@require_authenticated()`, or `@require_roles([...])` from `core/decorators.py`.
- **Pagination**: Use `StandardResultsSetPagination` (20/page), `LargeResultsSetPagination` (50/page), or `SmallResultsSetPagination` (10/page) from `core/pagination.py`.
- **File uploads**: Use Django `FileField` on `DocumentosDigitales` model — the upload path pattern is `documentos_empleados/%Y/%m/`. Files served via `/media/`.
- **PDF generation**: ReportLab only (WeasyPrint fails on Windows due to GTK). Chain in `pdf_generator.py` falls back to ReportLab already.
- **Email**: Django `EmailMultiAlternatives` with Celery task `send_email_html_task`. Falls back to synchronous send if Celery unavailable.
- **Custom PKs**: Every model uses `<modelname>_id` as AutoField primary key. ORM aggregations must use `Count('documento_id')`, not `Count('id')`.

---

## Component Boundaries

### Backend Components

| Component | Path | Responsibility | Communicates With |
|-----------|------|---------------|-------------------|
| **Auth layer** | `api/v1/auth/` | Login, token, password change | `Usuario`, `Rol`, `Permiso` models |
| **RRHH ViewSets** | `api/v1/rrhh/views.py` | Empleado, DatosLaborales, Familiares, Academicos CRUD | services, serializers |
| **Contratos ViewSets** | `api/v1/rrhh/contratos_views.py` | ContratosAdendas CRUD, PDF generation | TemplateService, PDFGenerator |
| **Remuneraciones ViewSets** | `api/v1/rrhh/remuneraciones_views.py` | PlanillaMensual, BoletaPago, DescuentoMasivo, AFP config | PlanillaCalculoService, DescuentoMasivoService |
| **Vacaciones ViewSets** | `api/v1/vacaciones/views.py` | SolicitudVacaciones, PeriodoVacacional, GoceVacaciones | VacationApprovalService, VacationCalculationService, VacationService |
| **Document generation** | `api/v1/app_rrhh/document_generation_views.py` | PDF/Word generation endpoints | TemplateService, PDFGenerator, EmpleadoReportService |
| **Onboarding ViewSets** | (partially in `api/v1/rrhh/views.py`) | OnboardingEmpleado CRUD, validation | OnboardingService |
| **Services layer** | `app_rrhh/services/` | All business logic | Models only (no cross-service calls with exceptions) |
| **Email tasks** | `app_rrhh/tasks.py` | Async email via Celery; sync fallback | Django email backend |
| **Core utilities** | `core/` | APIResponse, decorators, pagination, exceptions | Used by all ViewSets |

### Frontend Components

| Component | Path | Responsibility | Communicates With |
|-----------|------|---------------|-------------------|
| **Auth context** | `src/context/AuthContext.tsx` | JWT token storage, user state, 401 redirect | `authService` |
| **API client** | `src/lib/api.ts` | Axios instance, Bearer token injection, 401 intercept | All services |
| **Domain services** | `src/services/*.ts` | Unwrap `{ success, data, meta }` envelope, typed returns | `api.ts` |
| **Query hooks** | `src/hooks/useApi.ts` | React Query wrappers for common queries | Domain services |
| **Page components** | `src/pages/<domain>/` | Route-level components, compose smaller components | hooks, services |
| **Admin layout** | `<AdminLayout>` inside `<Layout>` | RRHH/Admin panel chrome | `AdminRoute` permission guard |
| **Route guards** | `AdminRoute`, `isAdminOrRRHH()` | Redirect unauthorized users | `AuthContext` |

---

## Data Flow

### Onboarding Email Flow

```
RRHH creates employee in OnboardingAdminPage
  → POST /api/v1/rrhh/onboarding/
    → OnboardingService.crear_onboarding_completo()
      → Creates Empleado + Usuario + OnboardingEmpleado (atomic transaction)
      → Calls send_email_html_task.delay() [Celery]
        → Falls back to msg.send() if Celery unavailable
      → Sets onboarding.email_bienvenida_enviado = True
    → Returns OnboardingCreateResponse { username, email_enviado, ... }
  → Frontend shows success toast with email_enviado status
```

### Per-Section File Upload Flow

```
Employee uploads document in OnboardingPage section
  → POST /api/v1/rrhh/documentos/ (multipart/form-data)
    → DocumentosDigitales.save() auto-fills tamano_archivo, formato_archivo
    → OnboardingService.actualizar_estado_onboarding(empleado_id) called
      → Recalculates boolean flags (dni_subido, certificados_*, etc.)
      → Updates estado_onboarding via onboarding.actualizar_estado()
  → Frontend refetches OnboardingStatus to update progress bar
```

The upload path is `documentos_empleados/%Y/%m/` (date-partitioned). The `DocumentosDigitales` model already supports all document types needed: `dni`, `declaracion_jurada`, `certificado_estudios`, `titulo_profesional`, `certificado_trabajo`, `foto`, plus `familiar` category for family documents.

### Legajo Digital (RRHH view) Flow

```
RRHH opens LegajoPage for an employee
  → GET /api/v1/rrhh/empleados/{id}/ (full employee data)
  → GET /api/v1/rrhh/documentos/?empleado={id} (all documents by category)
  → GET /api/v1/rrhh/onboarding/?empleado={id} (onboarding status)
  → GET /api/v1/rrhh/contratos/?empleado={id} (contracts)
  → GET /api/v1/rrhh/remuneraciones/?empleado={id} (payroll history)
  → Frontend aggregates into tabbed legajo view
```

This is a read-only aggregation view on the frontend. No new API endpoints needed — it reuses existing ones. The `legajoService.ts` file already exists.

### Payroll Excel Export Flow

```
RRHH requests export in ReportesRemuneracionesPage
  → GET /api/v1/rrhh/planillas/{id}/exportar_excel/?formato=afp_net
    → View generates in-memory openpyxl Workbook
    → Returns HttpResponse(content_type='application/vnd.openxmlformats...')
      with Content-Disposition: attachment; filename="afp_net_PERIODO.xlsx"
  → Browser triggers download
```

Excel exports must NOT use `APIResponse` — they return raw `HttpResponse` with MIME type. This is the same pattern used for PDF downloads in the existing `document_generation_views.py`.

### Vacation Approval Workflow Flow

```
Employee submits vacation request in NuevaSolicitudPage
  → POST /api/v1/vacaciones/solicitudes/
    → SolicitudVacaciones created with estado='borrador'
  → Employee submits (enviar action)
    → PATCH /api/v1/vacaciones/solicitudes/{id}/enviar/
      → estado → 'en_revision'

Manager (jefe directo) approves in VacacionesManagementPage
  → POST /api/v1/vacaciones/solicitudes/{id}/aprobar_jefe/
    → VacationApprovalService.aprobar_por_jefe()
      → If config.requiere_aprobacion_rrhh: estado → 'aprobada_jefe'
      → Else: estado → 'aprobada' + descontar dias

RRHH approves in VacacionesManagementPage
  → POST /api/v1/vacaciones/solicitudes/{id}/aprobar_rrhh/
    → VacationApprovalService.aprobar_por_rrhh()
      → estado → 'aprobada' + descontar dias
      → HistorialSolicitudVacaciones entry created

All state transitions logged in HistorialSolicitudVacaciones.
```

---

## How to Extend Existing Patterns

### Adding a New ViewSet (standard pattern)

```python
# api/v1/rrhh/views.py (or a new <domain>_views.py file)
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from core.responses import APIResponse
from core.decorators import require_hr, require_authenticated
from core.pagination import StandardResultsSetPagination

class NuevoViewSet(viewsets.ModelViewSet):
    queryset = NuevoModelo.objects.all()
    serializer_class = NuevoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @require_authenticated()
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset().filter(...)
        return APIResponse.paginated(qs, page, page_size, NuevoSerializer)

    @require_hr()
    @action(detail=True, methods=['post'])
    def accion_especial(self, request, pk=None):
        try:
            resultado = NuevoService.ejecutar(pk, request.user)
            return APIResponse.success(data=resultado, message="OK")
        except Exception as e:
            return APIResponse.error(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### Adding a New Service (standard pattern)

```python
# app_rrhh/services/nuevo_service.py
import logging
from django.db import transaction
from app_rrhh.models import NuevoModelo

logger = logging.getLogger(__name__)

class NuevoService:
    @staticmethod
    @transaction.atomic
    def ejecutar(pk, usuario):
        # Business logic here
        # Raise exceptions with descriptive messages — views catch them
        instance = NuevoModelo.objects.get(nuevo_id=pk)
        # ... process ...
        logger.info("Accion ejecutada para %s por %s", pk, usuario.username)
        return instance
```

### Adding an Excel Export Action (non-APIResponse pattern)

```python
import openpyxl
from django.http import HttpResponse

@require_hr()
@action(detail=True, methods=['get'], url_path='exportar_excel')
def exportar_excel(self, request, pk=None):
    planilla = self.get_object()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Planilla"
    # ... populate worksheet ...
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="planilla_{planilla.periodo}.xlsx"'
    wb.save(response)
    return response
```

### Adding a File Upload Endpoint

Multipart/form-data. The serializer must use `FileField` or `ImageField`. The view must NOT use `@require_authenticated()` as a decorator on the same method as `parser_classes` — set `parser_classes` on the ViewSet class or action level:

```python
from rest_framework.parsers import MultiPartParser, FormParser

class DocumentosDigitalesViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    # ...
    def create(self, request, *args, **kwargs):
        # request.FILES['archivo'] contains the uploaded file
        # Serializer handles saving to DocumentosDigitales
```

### Adding a Frontend Service (standard pattern)

```typescript
// src/services/nuevoService.ts
import { apiClient } from '@/lib/api'

interface NuevoItem { ... }

export const nuevoService = {
  async listar(params?: Record<string, string>): Promise<NuevoItem[]> {
    const response = await apiClient.get('/api/v1/rrhh/nuevo/', { params })
    const raw = response.data
    return raw?.data?.results ?? raw?.results ?? raw?.data ?? raw
  },

  async crear(data: Partial<NuevoItem>): Promise<NuevoItem> {
    const response = await apiClient.post('/api/v1/rrhh/nuevo/', data)
    return response.data?.data
  },

  async descargarExcel(id: number): Promise<void> {
    const response = await apiClient.get(`/api/v1/rrhh/planillas/${id}/exportar_excel/`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `planilla_${id}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }
}
```

---

## Module-Specific Architecture Notes

### Onboarding Email Flow

**What exists:** `OnboardingService.crear_onboarding_completo()` already sends the email. The `email_bienvenida_enviado` flag and `fecha_email_bienvenida` fields exist on `OnboardingEmpleado`. Celery task `send_email_html_task` with sync fallback exists. Email templates (`bienvenida.html`, `bienvenida.txt`) exist.

**What is missing:** The bug is that `enviar_email_bienvenida()` calls `send_email_html_task.delay()` but this requires Celery to be running. If Celery is not configured/running in the deployment environment, the sync fallback path also fails if `DEFAULT_FROM_EMAIL` / SMTP settings are wrong. Investigation needed: check `settings/development.py` for email backend config. The `reenviar_email_bienvenida()` method already exists for the fix case (user `ggarcia`).

**Build order:** Email fix is independent of all other modules. Fix first.

### Per-Section File Uploads

**What exists:** `DocumentosDigitales` model is fully built. It supports all needed `tipo_documento` values. The `OnboardingService.actualizar_estado_onboarding()` already recalculates checklist flags from document existence. `documento_upload_path` and `FileField` are defined.

**What is missing:**
- A `DocumentosDigitalesViewSet` with `MultiPartParser` support — may exist in views.py or may be partial
- Employee-scoped permission: an employee in onboarding should only be able to upload to their own `empleado_id`. The current `@require_authenticated()` decorator must be combined with an ownership check in the view.
- Photo upload for profile picture needs a dedicated endpoint or reuses `tipo_documento='foto'` in `DocumentosDigitales`.

**Build order:** Must come after the onboarding email fix (employee needs credentials to upload).

### Legajo Digital

**What exists:** `legajoService.ts` exists. `LegajoPage.tsx` exists. `EmpleadoReportService` generates PDFs per section. `DocumentosDigitales.documentos_por_empleado()` classmethod returns all documents organized by category.

**What is missing:** The legajo view needs to aggregate data from 5+ endpoints. The implementation question is whether this is done in the frontend (parallel React Query calls) or the backend (a dedicated `/api/v1/rrhh/empleados/{id}/legajo_completo/` aggregation action). Recommend: backend aggregation action on the Empleado ViewSet to avoid N+1 on frontend and reduce round trips. Single action returns all sections in one response.

**Build order:** Depends on file uploads being complete (legajo is meaningless without documents).

### Payroll Excel Exports

**What exists:** `PlanillaCalculoService` handles all calculation logic. `remuneraciones_views.py` has the ViewSet structure. `openpyxl` is likely already in requirements (check before assuming). Multiple export formats are needed: AFP Net, PDT-PLAME, ingresos/descuentos, and ZIP bundle.

**What is missing:** The actual `@action` methods for each export format. Each format is a separate `@action(detail=True, methods=['get'])` on `PlanillaMensualViewSet`. The ZIP bundle (for planilla web upload) needs `zipfile` from Python stdlib — no new dependencies.

**Build order:** Requires `PlanillaCalculoService` to be fully functional (calculation must run before export). Independent of onboarding and legajo.

### Vacation Approval Workflow

**What exists:** The approval workflow is fully modeled: `SolicitudVacaciones`, `PeriodoVacacional`, `GoceVacaciones`, `HistorialSolicitudVacaciones` models. `VacationApprovalService` with `aprobar_por_jefe()`, `aprobar_por_rrhh()`, `rechazar_solicitud()`, `cancelar_solicitud()`. Two-stage permission: jefe directo then RRHH. History logging on every state transition. Frontend pages: `NuevaSolicitudPage`, `SolicitudesPage`, `VacacionesManagementPage`, `PeriodosPage`, `ReportesPage`.

**What is missing:** Vacation balance display (saldo vacacional) and accrual calculation on the employee-facing side. Report generation (récord vacacional, vacaciones no gozadas, reporte por oficina, reporte mensual para finanzas) — these likely need new `@action` endpoints on the vacation ViewSet.

**Build order:** Core approval workflow may already work. Missing pieces are the reports and the employee-facing saldo query.

---

## Suggested Build Order

Dependencies determine order. Each layer must be stable before the next is built on top of it.

```
Phase 1: Foundations (bugs + missing email plumbing)
  └── Fix onboarding email (email backend config + verify Celery/sync path)
  └── Fix employee-scoped permissions on document upload
      (prerequisite for all employee self-service features)

Phase 2: Onboarding Self-Service (employee data entry)
  └── Employee restricted view (only their own sections visible)
  └── File upload endpoints per section (DNI, familiares, academico, laboral)
  └── Photo/profile upload
  └── Progress tracking (OnboardingService.actualizar_estado_onboarding already exists)

Phase 3: Legajo Digital (RRHH aggregation view)
  └── Backend legajo_completo aggregation action on Empleado ViewSet
  └── Frontend LegajoPage tabbed view consuming aggregation endpoint
  └── Document viewer (PDF inline / image preview)
      Depends on: Phase 2 (documents must exist to view)

Phase 4: Payroll Exports (standalone, no cross-dependencies)
  └── AFP Net Excel export action
  └── PDT-PLAME Excel export action
  └── Ingresos/descuentos/neto Excel export action
  └── ZIP bundle for planilla web
  └── Retención 4ta categoría PDF (uses existing ReportLab path)
  └── Rentas 5ta categoría PDF

Phase 5: Vacation Workflow Completion
  └── Employee saldo vacacional query (PeriodoVacacional balance)
  └── Fraccionamiento validation (min dias per fraccion already in ConfiguracionVacaciones)
  └── Report actions: récord, no gozadas/truncas, por oficina, mensual finanzas
      Depends on: approval workflow (already exists), period calculation (already exists)
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Business Logic in Views

**What:** Putting calculation, validation, or state transitions directly in ViewSet methods.
**Why bad:** The entire codebase puts logic in `app_rrhh/services/`. Views that contain business logic are untestable and duplicate logic across endpoints.
**Instead:** Create or extend a service class. The view calls one service method and wraps the result in `APIResponse`.

### Anti-Pattern 2: Bypassing APIResponse for JSON Endpoints

**What:** Returning `Response({...})` directly instead of `APIResponse.success()`.
**Why bad:** Frontend services (`src/services/*.ts`) all unwrap the `{ success, message, data, meta }` envelope. Bypassing it breaks the frontend unwrapping logic silently.
**Instead:** Only bypass `APIResponse` for file download endpoints (`HttpResponse` with MIME type). All JSON endpoints must use `APIResponse`.

### Anti-Pattern 3: New Models Outside app_rrhh

**What:** Creating a second Django app for a new module.
**Why bad:** All models must be importable from `app_rrhh.models`. Cross-app FK relationships in a single-app project cause circular imports and migration complexity.
**Instead:** Add models to `app_rrhh/models/` as new files, re-export from `app_rrhh/models/__init__.py`.

### Anti-Pattern 4: Employee Accessing Other Employees' Data

**What:** An endpoint with `@require_authenticated()` that returns data without scoping to the requesting employee.
**Why bad:** An employee in onboarding can read another employee's documents if the ViewSet doesn't filter by ownership.
**Instead:** In ViewSet methods accessible to non-RRHH users, add `empleado_id=request.user.empleado.empleado_id` filter. Use `@require_hr()` for admin endpoints and ownership checks for employee-self endpoints.

### Anti-Pattern 5: Importing Serializers Across View Files

**What:** Remuneraciones views importing from RRHH serializers, or vice versa.
**Why bad:** The existing structure keeps `serializers.py`, `contratos_serializers.py`, `remuneraciones_serializers.py` separate. Cross-imports create coupling.
**Instead:** Each domain view file imports from its own serializer file. Shared serializers go in `serializers.py`.

### Anti-Pattern 6: Sync File Processing Blocking the Request

**What:** Running image compression, PDF validation, or virus scanning synchronously inside the upload view.
**Why bad:** Large file uploads + processing = slow responses + worker timeouts.
**Instead:** Accept the upload, save the file, return 201. If processing is needed (e.g., thumbnail), enqueue a Celery task. For v1, just accept and store.

### Anti-Pattern 7: Multi-Line Django Template Tags

**What:** Template tags that span multiple lines: `{% if condition\n    and other %}`.
**Why bad:** Django's template lexer uses a regex without `re.DOTALL`. The tag will not parse correctly.
**Instead:** All `{% %}` and `{{ }}` template tags must open and close on the same line.

---

## Scalability Considerations

| Concern | Current Scale (50-200 employees) | At 1K employees | Notes |
|---------|----------------------------------|-----------------|-------|
| File storage | Local `media/` directory | S3 or similar object storage | Django `DEFAULT_FILE_STORAGE` makes this swappable |
| Email sending | Celery with sync fallback | Celery required, broker must be stable | Add retry + DLQ for production |
| Excel export | In-request, blocking | Move to async Celery task, return task_id | openpyxl is fast; 200 rows is fine synchronously |
| Vacation report | DB queries per report | Add DB indexes on `fecha_inicio`, `estado_solicitud` (already indexed) | Already well-indexed |
| Payroll calculation | Synchronous, already transactional | No change needed at 1K | PlanillaCalculoService handles this |

---

## Sources

- Direct inspection of `back/app_rrhh/models/` (onboarding.py, documentos_digitales.py, vacaciones.py)
- Direct inspection of `back/app_rrhh/services/` (onboarding_service.py, vacation_approval_service.py, planilla_calculo_service.py, empleado_report_service.py)
- Direct inspection of `back/core/` (responses.py, decorators.py)
- Direct inspection of `back/api/v1/rrhh/remuneraciones_views.py`
- Direct inspection of `front/src/services/onboardingService.ts`
- `.planning/PROJECT.md` for requirements and decisions
- `CLAUDE.md` for architectural constraints (PDF chain, ORM patterns, MySQL, template lexer behavior)
