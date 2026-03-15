# Phase 1: Onboarding Self-Service - Research

**Researched:** 2026-03-13
**Domain:** Django DRF + React/TypeScript — Onboarding flow with file uploads, routing guards, and RRHH monitoring
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Employee view structure**
- Tabbed layout with 4 tabs: Personal | Familiar | Academico | Laboral
- Progress bar displayed prominently at the top of the page, above the tabs — always visible showing global % completion
- Tab Personal includes: profile photo section (prominent, at the top with Avatar component) + editable personal data fields (telefono, direccion, fecha_nacimiento) + document upload zones (DNI, carne de extranjeria)
- Each document zone shows document name + upload date + status badge after upload ('Pendiente revision', 'Aprobado', 'Rechazado')
- When a document is rejected, the employee sees the rejection reason (observaciones field) and can upload a replacement
- When onboarding is completed and validated by RRHH: show success message + redirect to normal panel

**Document upload UX**
- Drag-and-drop zone (also clickable to browse files) for each document
- One zone per document type — sections requiring multiple documents show separate zones
- After upload: zone transforms to show filename + upload date + status badge 'Pendiente revision', button changes to 'Reemplazar'
- Progress percentage updates immediately after successful upload
- Accepted formats: PDF only for all documents; photos (JPG/PNG) only for profile photo
- Maximum file size: 10 MB per file. Show clear error if exceeded.

**RRHH monitoring panel**
- Filterable table with columns: Empleado | Estado | Progreso (%) | Fecha inicio | Alerta | Acciones
- Progress shown as progress bar + % value in the table row
- Filters: by estado, by % completion range, by date range (fecha_inicio), by alerta de 5 dias, by employee name or DNI
- Actions per row: Ver detalle, Reenviar credenciales, Validar/Rechazar onboarding, Ver documentos pendientes
- Alerta column shows warning when employee has not submitted any document AND 5+ days have passed since welcome email

**Email failure handling**
- When RRHH creates an onboarding and email_enviado=false: show visible alert banner with two buttons: [Reintentar enviar] and [Corregir correo y reintentar]
- "Corregir correo" opens an inline field to edit the email address before retrying
- Backend already returns email_enviado flag in the response — frontend uses this to trigger the alert

**5-day no-response alerts**
- Alert condition: employee has not made their first successful login AND 5+ days have passed since fecha_email_bienvenida
- Detection: calculated in real time when RRHH loads the monitoring panel (no cron needed)
- Alert indicator: warning badge in the Alerta column + filter "Con alertas"
- Internal notification: sent once when 5 days are reached, then daily reminder until employee logs in AND submits at least one document
- Notifications appear in the system's notification panel (header)

### Claude's Discretion
- Skeleton loading states while fetching data
- Exact spacing, typography, and color palette within existing design system
- Error state handling for failed API calls
- Exact animation/transition details for upload zones
- How to store last_login for alert detection (can use Django's last_login field on Usuario or a separate tracking field)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ONBD-01 | Sistema envia correo de bienvenida al empleado cuando se crea su usuario de onboarding | OnboardingService.enviar_email_bienvenida already exists with Celery + sync fallback. The bug is that email_enviado may be false when SMTP is misconfigured. Frontend needs to show the alert banner. Backend needs a "corregir correo + reenviar" endpoint. |
| ONBD-02 | Empleado en onboarding accede a una vista restringida — solo ve sus propias secciones | App.tsx has `/onboarding` route (unauthenticated to all). The missing piece: users with pending OnboardingEmpleado must be redirected to `/onboarding` and blocked from admin/regular routes. Needs an `isOnboardingUser()` guard in AppRoutes. |
| ONBD-03 | Empleado puede subir su foto de perfil desde la seccion de datos personales | Empleado.ruta_fotografia is a CharField (path), not a FileField. DocumentosDigitales has tipo_documento='foto'. Upload of profile photo should create/update a DocumentosDigitales record AND update ruta_fotografia on the Empleado. Needs a dedicated photo upload endpoint or the existing legajo upload endpoint with tipo_documento='foto'. |
| ONBD-04 | Empleado puede subir documentos PDF en datos personales (DNI, carne de extranjeria) | DocumentosDigitales model fully supports this. OnboardingService.actualizar_estado_onboarding checks for dni_subido. The personal tab needs upload zones for 'dni' and 'carnet_extranjeria' tipos. |
| ONBD-05 | Empleado puede subir documentos PDF en datos familiares | DocumentosDigitales supports 'dni_familiar' and 'certificado_nacimiento'. OnboardingService checks documentos_familiares_subidos. Familiar tab needs upload zones. |
| ONBD-06 | Empleado puede subir documentos PDF en datos academicos | DocumentosDigitales supports 'certificado_estudios', 'titulo_profesional', 'diploma'. OnboardingService checks certificados_academicos_subidos. |
| ONBD-07 | Empleado puede subir documentos PDF en datos laborales sin editar campos que gestiona RRHH | DocumentosDigitales supports 'declaracion_jurada', 'cv', 'certificado_trabajo', 'carta_recomendacion'. The laboral tab must be read-only for DatosLaborales fields (cargo, area, regimen) — employee only uploads documents. |
| ONBD-08 | RRHH puede ver el porcentaje de completitud del onboarding de cada empleado | OnboardingViewSet.list exists with progreso_porcentaje in serializer. OnboardingAdminPage exists but lacks: progress bar in table rows, alert column, range/date filters, inline email correction flow. |
</phase_requirements>

---

## Summary

Phase 1 builds on a substantial foundation that already exists. The backend has a complete `OnboardingEmpleado` model with a state machine, a full `OnboardingService`, an `OnboardingViewSet` with all CRUD and custom actions (`mi_onboarding`, `validar`, `reenviar_email`, `actualizar-estado`), and `DocumentosDigitales` model for file management. The frontend has stub pages (`OnboardingPage`, `OnboardingAdminPage`), an `onboardingService`, and all required UI components available in `src/components/ui/`.

What does NOT exist yet is: (1) the routing guard that redirects onboarding employees away from the admin panel, (2) the redesigned employee self-service view with tabbed layout + drag-and-drop upload zones + per-document status badges, (3) the "Corregir correo y reintentar" flow with an inline email edit + a backend endpoint to update the correo before resending, (4) the 5-day alert calculation logic in the RRHH monitoring panel, and (5) the enhanced RRHH panel with progress bars in rows, alert column, and expanded filters.

The `ggarcia` bug referenced in success criteria is likely a real test case where onboarding was created for an employee but `email_enviado=false` because SMTP was not configured or the address was wrong. The fix has two parts: the frontend alert banner (already partially designed in the CONTEXT decision) and a backend endpoint that accepts a new email address before retrying.

**Primary recommendation:** Build the new tabbed self-service view in `front/src/features/onboarding/` (currently empty stubs), add the routing guard in App.tsx, enhance the RRHH admin page in-place, add a `corregir_correo` backend action, and wire the 5-day alert purely via frontend calculation on the existing `fecha_email_bienvenida` + `last_login` fields.

---

## Standard Stack

### Core (all already installed in project)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Django DRF ViewSet | 4.2 | Backend API for onboarding CRUD | Already wired in urls.py |
| React Query v5 | @tanstack/react-query | Server state, caching, refetch | Project standard, QueryClientProvider in App.tsx |
| react-hook-form + zod | latest | Form validation for personal data edits | Project standard for all forms |
| Shadcn/ui (Radix) | latest | Card, Tabs, Progress, Badge, Avatar, Dialog, Table | All already in src/components/ui/ |
| sonner | latest | Toast notifications | Project standard |
| axios (apiClient) | latest | HTTP client | src/lib/api.ts |
| lucide-react | latest | Icons | Project standard |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-dropzone | ^14 | Drag-and-drop file upload zones | Each document upload zone in the tabbed employee view |
| Django FileField + MEDIA | built-in | File storage on disk | DocumentosDigitales.archivo already uses it |

**react-dropzone is the only new dependency.** It integrates cleanly with React and produces a stable `onDrop` callback that extracts the File object, after which the existing `legajoService.create()` pattern (FormData POST) can be reused unchanged.

**Installation (frontend only):**
```bash
cd D:/INTRANET/front && npm install react-dropzone
```

---

## Architecture Patterns

### Recommended Project Structure

The feature directories already exist as stubs. Fill them in:

```
front/src/features/onboarding/
├── components/
│   ├── DocumentUploadZone.tsx     # Reusable drag-and-drop zone per document type
│   ├── OnboardingProgressBar.tsx  # Global % progress bar shown above tabs
│   ├── OnboardingTabPersonal.tsx  # Tab: photo + personal fields + DNI zones
│   ├── OnboardingTabFamiliar.tsx  # Tab: familiar document zones
│   ├── OnboardingTabAcademico.tsx # Tab: academic document zones
│   ├── OnboardingTabLaboral.tsx   # Tab: laboral document zones (read-only fields)
│   └── OnboardingCompleteBanner.tsx  # Shown when estado == 'completado'
├── pages/
│   └── OnboardingEmployeePage.tsx # Full self-service page — wraps tabs + progress
├── services/
│   └── onboardingUploadService.ts # Thin wrapper: upload doc, update onboarding state
└── types/
    └── onboarding.ts              # Re-export from generated types + local additions

back/api/v1/rrhh/views.py (existing OnboardingViewSet):
  + corregir_correo action  # PATCH to update empleado.correo_personal + resend email
```

The `OnboardingAdminPage` at `front/src/pages/onboarding/OnboardingAdminPage.tsx` is enhanced in place (not moved) since it is already wired in App.tsx routing.

### Pattern 1: Routing Guard for Onboarding Users

**What:** In `AppRoutes`, before rendering normal routes, check if the authenticated user has an active (non-completed) onboarding. If so, restrict them to `/onboarding` only.

**When to use:** Any authenticated user with `tipo_usuario == 'empleado'` and an active OnboardingEmpleado record.

**Key insight:** The user object returned by the login endpoint already contains `tipo_usuario`. We can add an `is_in_onboarding` boolean to the user payload from the backend, OR derive it in the frontend by calling `mi_onboarding` endpoint on mount when `tipo_usuario == 'empleado'`.

**Recommended approach (lower backend change, uses React Query):**

```typescript
// In AppRoutes, after the requiere_cambio_password guard:
// Source: existing App.tsx pattern — replicate the forced-redirect block
function OnboardingRoute({ children }: { children: React.ReactNode }) {
  const { user } = useAuth()
  const { data: onboarding, isLoading } = useQuery({
    queryKey: ['mi-onboarding'],
    queryFn: () => onboardingService.getMiOnboarding(),
    enabled: user?.tipo_usuario === 'empleado',
    retry: false,
  })

  if (isLoading) return <LoadingSpinner />
  // If employee has an active onboarding, redirect everything to /onboarding
  if (onboarding && onboarding.estado_onboarding !== 'completado') {
    return <Navigate to="/onboarding" replace />
  }
  return <>{children}</>
}
```

This is a **React Query-based guard** — no extra API endpoint needed. The `mi_onboarding` endpoint already returns a 404 when there is no active onboarding, so `retry: false` prevents infinite retries.

**Critical note:** Do NOT apply this guard to non-employee users (`tipo_usuario !== 'empleado'`). The check must be behind `enabled: user?.tipo_usuario === 'empleado'`.

### Pattern 2: DocumentUploadZone Component

**What:** A single reusable zone per document type using `react-dropzone`.

**When to use:** Each upload slot in tabs Personal, Familiar, Academico, Laboral.

```typescript
// Source: react-dropzone docs https://react-dropzone.js.org/
import { useDropzone } from 'react-dropzone'

interface DocumentUploadZoneProps {
  tipoDocumento: string
  categoria: string
  label: string
  acceptImages?: boolean  // true only for profile photo
  existingDoc?: { nombre: string; fecha_subida: string; estado: string; observaciones?: string } | null
  onUploadSuccess: () => void
  empleadoId: number
}

function DocumentUploadZone({ ... }: DocumentUploadZoneProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: acceptImages
      ? { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] }
      : { 'application/pdf': ['.pdf'] },
    maxSize: 10 * 1024 * 1024,  // 10 MB
    multiple: false,
    onDropAccepted: (files) => handleUpload(files[0]),
    onDropRejected: (rejections) => {
      const code = rejections[0]?.errors[0]?.code
      if (code === 'file-too-large') toast.error('Archivo supera los 10 MB')
      else toast.error('Formato no permitido')
    },
  })
  // ...
}
```

**After upload state:** If `existingDoc` is provided, render the filename, date, and status badge instead of the dropzone prompt. Show "Reemplazar" button that re-opens the dropzone.

### Pattern 3: Progress Update After Upload

**What:** After each successful document upload, invalidate the React Query cache for `mi_onboarding`, which triggers a refetch and updates the progress bar.

```typescript
// Source: @tanstack/react-query v5 docs
import { useQueryClient } from '@tanstack/react-query'

const queryClient = useQueryClient()

const handleUploadSuccess = () => {
  queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
}
```

This ensures the progress bar updates immediately without a full page reload.

### Pattern 4: 5-Day Alert Calculation (Frontend)

**What:** Calculate on the frontend when RRHH loads the monitoring table. No cron needed.

**Logic (confirmed by CONTEXT.md):**
- Alert condition: `last_login IS NULL` AND `fecha_email_bienvenida` is >= 5 days ago
- `last_login` is Django's standard field on Usuario, already populated by the auth backend
- `fecha_email_bienvenida` is a field on OnboardingEmpleado

```typescript
// Source: existing onboarding types
function hasAlert(o: OnboardingStatus): boolean {
  if (!o.fecha_email_bienvenida) return false
  if (o.last_login) return false  // employee has logged in
  const daysSince = differenceInDays(new Date(), new Date(o.fecha_email_bienvenida))
  return daysSince >= 5
}
```

**What needs to be added to the serializer:** `last_login` (from `onboarding.usuario.last_login`) must be included in `OnboardingEmpleadoSerializer`. Currently the serializer exposes `usuario_username` but likely not `last_login`. This is a small serializer change.

### Pattern 5: Email Correction + Retry Flow

**What:** Backend action to update `Empleado.correo_personal` and `Usuario.email` before resending.

**What needs to be built:** A new `@action(detail=True, methods=['post'], url_path='corregir-correo')` on `OnboardingViewSet`:

```python
# Source: existing reenviar_email action pattern in views.py
@action(detail=True, methods=["post"], url_path="corregir-correo")
@require_hr()
def corregir_correo(self, request, pk=None):
    """Actualiza el correo del empleado y reenvía el email de bienvenida."""
    nuevo_correo = request.data.get("correo_personal", "").strip()
    if not nuevo_correo:
        return APIResponse.error(message="correo_personal requerido")
    onboarding = self.get_object()
    onboarding.empleado.correo_personal = nuevo_correo
    onboarding.empleado.save(update_fields=["correo_personal"])
    onboarding.usuario.email = nuevo_correo
    onboarding.usuario.save(update_fields=["email"])
    result = OnboardingService.reenviar_email_bienvenida(onboarding.onboarding_id)
    if result and result["email_enviado"]:
        return APIResponse.success(message="Correo corregido y email reenviado")
    return APIResponse.error(message="Correo actualizado pero el email no pudo enviarse",
                             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Anti-Patterns to Avoid

- **Calling `actualizar_estado_onboarding` from the frontend manually after each upload.** Instead, the backend `mi_onboarding` endpoint already recalculates state on every GET. Use React Query cache invalidation to trigger that recalculation.
- **Building a custom drag-and-drop implementation.** Use `react-dropzone`. The edge cases (multiple files, MIME validation, size limits, accessibility) are handled by the library.
- **Using `prompt()` for rejection reasons** (currently in `OnboardingAdminPage.tsx`). Replace with a Dialog-based form to stay consistent with the design system.
- **Making the onboarding routing guard synchronous.** The `mi_onboarding` API call is async; must show a LoadingSpinner while pending, not block the render.
- **Allowing employees to submit the laboral tab fields.** The Laboral tab is intentionally read-only for RRHH-managed fields (cargo, area, regimen). Only document uploads are interactive for employees.
- **Using FileField on Empleado for ruta_fotografia.** The existing `ruta_fotografia` field is a `CharField(max_length=255)`. Profile photo uploads should create a `DocumentosDigitales` record (tipo_documento='foto') and then set `ruta_fotografia` to the file path. Do not change the model field type.
- **Trying to use Django last_login directly in alert filter without serializer support.** The `last_login` field is on the `Usuario` model. It must be exposed via `OnboardingEmpleadoSerializer` (through `usuario.last_login`). If it is absent from the serializer, the frontend has no way to compute the alert.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop file upload | Custom div with onDragOver/onDrop handlers | `react-dropzone` | Handles MIME validation, maxSize, multiple files, accessibility (keyboard file select), browser quirks |
| File size validation | Manual `file.size > limit` check in onChange | `react-dropzone` maxSize option | Library reports exact error code ('file-too-large') enabling precise error messaging |
| Progress percentage calculation | Custom frontend percentage logic | Backend `progreso_porcentaje` property on `OnboardingEmpleado` | Backend has the canonical calculation tied to 7 boolean checklist flags |
| 5-day alert cron job | Celery beat task or DB-stored alert flags | Frontend `differenceInDays` on `fecha_email_bienvenida` | CONTEXT.md explicitly says "calculated in real time when RRHH loads the monitoring panel (no cron needed)" |
| Email send queue | Custom retry queue | Existing Celery `send_email_html_task` with sync fallback | Already handles retry (max_retries=3, countdown=60) and falls back to synchronous send |
| State machine for onboarding | Custom transition logic | `OnboardingEmpleado.actualizar_estado()` + `OnboardingService.actualizar_estado_onboarding()` | Already implemented; just call the endpoint |
| Token/auth for restricted onboarding view | Custom permission class | Existing `@require_authenticated()` + check `onboarding.usuario == request.user` | Already enforced in `retrieve` and `mi_onboarding` actions |

---

## Common Pitfalls

### Pitfall 1: `unique_together` Violation on Document Re-upload

**What goes wrong:** `DocumentosDigitales` has `unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]`. If an employee tries to "replace" a document and the old record is not updated to `es_version_actual=False` first, the new upload will fail with an IntegrityError.

**Why it happens:** The "Reemplazar" flow calls `legajoService.create()` which POSTs a new record without deactivating the old one.

**How to avoid:** The upload endpoint should: (1) check if a current-version document of that tipo_documento already exists for the employee, (2) if yes, set `es_version_actual=False` on the old one before creating the new one. The `DocumentosDigitales.crear_nueva_version()` method already does this — use it instead of a plain `create()`.

**Warning signs:** HTTP 400/500 on second upload of the same document type.

### Pitfall 2: Profile Photo Field Mismatch

**What goes wrong:** `Empleado.ruta_fotografia` is a `CharField`, not a `FileField` or `ImageField`. If code tries to access `.url` on it like a FileField, it raises `AttributeError`.

**Why it happens:** Developer assumes it's a FileField because the model stores a path.

**How to avoid:** Profile photo uploads create a `DocumentosDigitales` record (tipo_documento='foto', categoria='personal'). After upload, set `empleado.ruta_fotografia = documento.archivo.name` via the backend endpoint. Frontend displays the photo using `documento.archivo` URL from the DocumentosDigitales response, not from `empleado.ruta_fotografia` directly.

### Pitfall 3: Onboarding Routing Guard Creates Infinite Loop

**What goes wrong:** The routing guard calls `mi_onboarding`, which returns 404 for non-onboarding users. React Query retries the call, triggering re-renders.

**Why it happens:** React Query default retry=1 causes a second fetch on 404 before recognizing failure.

**How to avoid:** Set `retry: false` on the `mi_onboarding` query used in the routing guard. Also set `enabled: user?.tipo_usuario === 'empleado'` so the query never runs for admin/rrhh users.

### Pitfall 4: Email_enviado Flag is Backend-Authoritative, Not Frontend-Authoritative

**What goes wrong:** After RRHH creates an onboarding, the response body contains `email_enviado: false`. But the frontend component that reads `onboardings` via `.getAll()` fetches the list, which does NOT include `email_enviado` in list items (pagination payload). The alert banner only appears in the creation result dialog, not in subsequent panel views.

**Why it happens:** The alert banner must be shown at creation time from the creation response, not from the list. The list does include `email_bienvenida_enviado` as part of the serializer — verify this is serialized in `OnboardingEmpleadoSerializer`.

**How to avoid:** Show the alert banner in the `CreateOnboardingDialog` success state (immediately after create). For re-display in the panel, the table row can show a "no email enviado" indicator based on `email_bienvenida_enviado=false` from the list response. Verify `OnboardingEmpleadoSerializer` includes `email_bienvenida_enviado`.

### Pitfall 5: File Upload via FormData Requires Correct Content-Type

**What goes wrong:** `apiClient.post(url, data)` where `data` is a `FormData` object works correctly IF axios detects the FormData type and sets `Content-Type: multipart/form-data` with the boundary automatically. But if the interceptor manually sets `Content-Type: application/json`, the upload will fail.

**Why it happens:** Some axios configurations set a global Content-Type header.

**How to avoid:** Check `src/lib/api.ts` interceptors. When sending FormData, either pass `{ headers: { 'Content-Type': 'multipart/form-data' } }` explicitly or verify that the interceptor does NOT override Content-Type when the payload is FormData (best practice: `if (config.data instanceof FormData) delete config.headers['Content-Type']`).

### Pitfall 6: `last_login` Not in OnboardingEmpleadoSerializer

**What goes wrong:** The 5-day alert calculation requires `onboarding.usuario.last_login` in the API response. If `OnboardingEmpleadoSerializer` does not include this field, the frontend has no way to compute alerts without an additional API call per row.

**How to avoid:** Add `last_login = serializers.DateTimeField(source='usuario.last_login', read_only=True)` to `OnboardingEmpleadoSerializer`. Confirm this is included before building the alert column.

---

## Code Examples

### Upload via FormData (existing legajoService pattern)

```typescript
// Source: front/src/services/legajoService.ts (inferred from OnboardingPage.tsx usage)
const formData = new FormData()
formData.append('empleado', String(empleadoId))
formData.append('tipo_documento', tipoDocumento)
formData.append('categoria', categoria)
formData.append('nombre_documento', nombreDocumento)
formData.append('archivo', file)
formData.append('estado_documento', 'pendiente_revision')
formData.append('nivel_acceso', 'restringido')

await apiClient.post('/api/v1/rrhh/legajo/', formData)
```

### React Query invalidation after upload

```typescript
// Source: @tanstack/react-query v5 standard pattern
const queryClient = useQueryClient()
queryClient.invalidateQueries({ queryKey: ['mi-onboarding'] })
```

### react-dropzone with MIME + size validation

```typescript
// Source: react-dropzone docs https://react-dropzone.js.org/
const { getRootProps, getInputProps, isDragActive } = useDropzone({
  accept: { 'application/pdf': ['.pdf'] },
  maxSize: 10 * 1024 * 1024,
  multiple: false,
  onDropAccepted: ([file]) => handleUpload(file),
  onDropRejected: ([rejection]) => {
    const code = rejection.errors[0]?.code
    if (code === 'file-too-large') toast.error('El archivo supera los 10 MB permitidos')
    else toast.error('Solo se permiten archivos PDF')
  },
})
```

### 5-day alert calculation

```typescript
// Source: date-fns (already in project via shadcn/ui dependency)
import { differenceInCalendarDays } from 'date-fns'

function computeAlert(o: OnboardingStatus): boolean {
  if (!o.fecha_email_bienvenida) return false
  if (o.last_login != null) return false
  const days = differenceInCalendarDays(new Date(), new Date(o.fecha_email_bienvenida))
  return days >= 5
}
```

### Backend serializer addition for last_login

```python
# Source: back/api/v1/rrhh/serializers.py (OnboardingEmpleadoSerializer — to be added)
last_login = serializers.DateTimeField(source='usuario.last_login', read_only=True)
```

### Backend corregir_correo action

```python
# Source: existing reenviar_email pattern in back/api/v1/rrhh/views.py:2230
@action(detail=True, methods=["post"], url_path="corregir-correo")
@require_hr()
def corregir_correo(self, request, pk=None):
    nuevo_correo = request.data.get("correo_personal", "").strip()
    if not nuevo_correo:
        return APIResponse.error(message="correo_personal es requerido")
    onboarding = self.get_object()
    onboarding.empleado.correo_personal = nuevo_correo
    onboarding.empleado.save(update_fields=["correo_personal"])
    onboarding.usuario.email = nuevo_correo
    onboarding.usuario.save(update_fields=["email"])
    result = OnboardingService.reenviar_email_bienvenida(onboarding.onboarding_id)
    if result and result["email_enviado"]:
        return APIResponse.success(message="Correo actualizado y email reenviado")
    return APIResponse.error(
        message="Correo actualizado pero el email no pudo enviarse",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
```

---

## State of the Art

| Old Approach (current OnboardingPage.tsx) | New Approach (Phase 1 target) | Impact |
|------------------------------------------|-------------------------------|--------|
| Single-page linear steps (card per step, no tabs) | Tabbed layout with global progress bar above tabs | Matches locked decision; cleaner UX |
| Upload via Dialog (file input only) | Drag-and-drop zone per document type (react-dropzone) | Locked decision; standard UX pattern |
| Document list shows pending vs. not pending | Per-document status badge (Pendiente / Aprobado / Rechazado) + rejection reason visible | Locked decision |
| RRHH table shows % as plain text | Progress bar + % in each table row; Alerta column | Locked decision |
| No email correction flow | Alert banner + inline email edit + corregir-correo endpoint | Fixes ggarcia bug |
| No routing guard for onboarding employees | OnboardingRoute guard redirects to /onboarding | ONBD-02 |
| prompt() for rejection reasons | Dialog-based rejection form | Code quality + UX |

**Deprecated in this phase:**
- The existing `OnboardingPage.tsx` linear step layout is replaced entirely by `OnboardingEmployeePage.tsx` in the feature directory.
- The upload Dialog pattern (single file input) is replaced by `DocumentUploadZone` components.

---

## Open Questions

1. **Does `OnboardingEmpleadoSerializer` already expose `email_bienvenida_enviado`?**
   - What we know: The field exists on the model. The serializer at `back/api/v1/rrhh/serializers.py` is 41KB — not read in full during research.
   - What's unclear: Whether `email_bienvenida_enviado` and `fecha_email_bienvenida` are already serialized.
   - Recommendation: Check serializer for these fields before planning the alert column task. If absent, add a small serializer task in Wave 0.

2. **Profile photo display: should it show the DocumentosDigitales archivo URL or Empleado.ruta_fotografia?**
   - What we know: `ruta_fotografia` is a CharField (just a path string, not a Django file field). `DocumentosDigitales.archivo` is a proper FileField with `.url` support.
   - What's unclear: Whether there is existing backend logic that populates `ruta_fotografia` from the photo document.
   - Recommendation: Use `DocumentosDigitales` as the canonical photo storage, and update `ruta_fotografia` as a secondary side-effect for backward compatibility with any template that may use it.

3. **Internal notification system for 5-day alerts: does it already exist?**
   - What we know: CONTEXT.md says "Notifications appear in the system's notification panel (header)." There is a notification panel in the header.
   - What's unclear: Whether the notification model/API exists in the backend, or this is a purely frontend concern.
   - Recommendation: If a notification API endpoint does not exist, the 5-day alert notification is a frontend-only concern (show a red dot / count in the header notification panel derived from the onboarding list query). Verify before planning the notification task.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest + pytest-django (back), Vitest (front) |
| Config file | `back/pytest.ini` or `back/Makefile` (`make test`), `front/vite.config.ts` |
| Quick run command | `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/test_onboarding*.py -x -v` |
| Full suite command | `cd D:/INTRANET/back && make test` / `cd D:/INTRANET/front && npm run test` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ONBD-01 | Email bienvenida enviado (or email_enviado=false returned) when onboarding created | unit | `pytest tests/test_onboarding_service.py -x` | No — Wave 0 |
| ONBD-01 | corregir-correo action updates correo and returns email_enviado | unit | `pytest tests/test_onboarding_api.py::test_corregir_correo -x` | No — Wave 0 |
| ONBD-02 | Employee with active onboarding cannot access /admin routes | manual (routing guard) | N/A — browser test | N/A |
| ONBD-03 | Profile photo upload creates DocumentosDigitales with tipo='foto' and updates ruta_fotografia | unit | `pytest tests/test_onboarding_api.py::test_photo_upload -x` | No — Wave 0 |
| ONBD-04 | DNI upload via legajo endpoint marks dni_subido=True after actualizar_estado | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_dni -x` | No — Wave 0 |
| ONBD-05 | Familiar document upload marks documentos_familiares_subidos=True | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_familiar -x` | No — Wave 0 |
| ONBD-06 | Academic document upload marks certificados_academicos_subidos=True | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_academico -x` | No — Wave 0 |
| ONBD-07 | Laboral document upload marks declaraciones_juradas_subidas/certificados_trabajo_subidos=True | unit | `pytest tests/test_onboarding_service.py::test_actualizar_estado_laboral -x` | No — Wave 0 |
| ONBD-08 | /onboarding/ list returns progreso_porcentaje + last_login for all employees | unit | `pytest tests/test_onboarding_api.py::test_list_includes_progreso -x` | No — Wave 0 |

### Sampling Rate

- **Per task commit:** `cd D:/INTRANET/back && D:/INTRANET/.venv/Scripts/python.exe -m pytest tests/test_onboarding*.py -x`
- **Per wave merge:** `cd D:/INTRANET/back && make test && cd D:/INTRANET/front && npm run test`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `back/tests/test_onboarding_service.py` — covers ONBD-01, ONBD-04, ONBD-05, ONBD-06, ONBD-07 service-level assertions
- [ ] `back/tests/test_onboarding_api.py` — covers ONBD-01 (corregir-correo), ONBD-03 (photo upload), ONBD-08 (list response fields)
- [ ] `back/tests/conftest.py` — check if onboarding fixtures exist; add `onboarding_factory` fixture if absent

---

## Sources

### Primary (HIGH confidence)

- Codebase (direct file reads): `back/app_rrhh/models/onboarding.py`, `back/app_rrhh/models/documentos_digitales.py`, `back/app_rrhh/models/empleado.py`, `back/app_rrhh/models/usuario.py`, `back/app_rrhh/services/onboarding_service.py`, `back/api/v1/rrhh/views.py` (lines 2070-2268), `back/app_rrhh/tasks.py`, `front/src/App.tsx`, `front/src/pages/onboarding/OnboardingPage.tsx`, `front/src/pages/onboarding/OnboardingAdminPage.tsx`, `front/src/services/onboardingService.ts`, `front/src/context/AuthContext.tsx`
- `.planning/phases/01-onboarding-self-service/01-CONTEXT.md` — locked decisions
- `.planning/REQUIREMENTS.md` — requirement IDs and descriptions

### Secondary (MEDIUM confidence)

- react-dropzone docs pattern (library is well-established, v14 stable API) — https://react-dropzone.js.org/
- @tanstack/react-query v5 `invalidateQueries` pattern — standard documented usage

### Tertiary (LOW confidence)

- date-fns assumed to be in project (shadcn/ui commonly depends on it); verify with `npm list date-fns` before use. If absent, use plain `(new Date() - new Date(fecha)) / 86400000` instead.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in the project except react-dropzone; react-dropzone is the de-facto standard for drag-and-drop uploads in React
- Architecture: HIGH — based on direct reading of existing codebase; patterns follow existing project conventions
- Pitfalls: HIGH — all pitfalls are derived from directly observed code issues (unique_together constraint, CharField vs FileField, routing guard async behavior, serializer field gaps)
- Open questions: accurately flagged as needing verification before planning

**Research date:** 2026-03-13
**Valid until:** 2026-04-13 (stable codebase, no fast-moving external dependencies)

---

---

## NEW SCOPE RESEARCH

**Researched:** 2026-03-15
**Scope:** Wave 5-8 — Expanded onboarding (N-item dynamic forms, document preview modal, per-document approval workflow, email notifications, improved toast/error handling)
**Confidence:** HIGH

---

<new_phase_requirements>
## New Phase Requirements (ONBD-09 through ONBD-15)

| ID | Description | Research Support |
|----|-------------|-----------------|
| ONBD-09 | Employee can register N dependents with per-parentesco required document rules | DatosFamiliares model exists (familiar_id PK, empleado FK, parentesco, nombres_familiar, apellido_paterno, apellido_materno, fecha_nacimiento, numero_documento). No employee-write permission yet. Needs: get_permissions() override on DatosFamiliaresViewSet + owner-scoped queryset for employees. |
| ONBD-10 | Employee can register N academic records: certificados, cursos/diplomados (NEW model), titulos | DatosAcademicos exists for titulos/certificados (nivel_educativo distinguishes them). CursosCertificaciones does NOT exist in DB — new model needed with fields: nombre_curso, institucion, fecha_inicio, fecha_fin, horas, empleado FK, documento FK nullable. |
| ONBD-11 | Employee can register N work history entries linked to uploaded documents | No separate "experiencia laboral" model — use DocumentosDigitales with tipo='certificado_trabajo' and populate entidad_emisora (empresa), fecha_emision (fecha_inicio), fecha_vencimiento (fecha_fin). No new model needed. |
| ONBD-12 | Document preview modal opens before upload — employee confirms before POST | react-pdf v10.3.0 already installed. Pre-upload preview uses URL.createObjectURL(file). Post-upload PDF served from Django MEDIA_URL — use iframe for already-uploaded docs. Preview modal needs two buttons: Cancelar (discard file) and Enviar documento (trigger POST). |
| ONBD-13 | Per-document approve/reject by RRHH in onboarding detail view | DocumentosDigitales.validar_documento() and rechazar_documento() methods already exist. Need two new @action endpoints on OnboardingViewSet: aprobar_documento and rechazar_documento (nested under onboarding/{id}/documentos/{doc_id}/). |
| ONBD-14 | Email notifications: doc rejected, onboarding approved, onboarding rejected/observed | OnboardingService pattern established. Need 3 new email templates + service methods for each notification type. Trigger from view after state change. |
| ONBD-15 | Comprehensive toast/error handling for all upload and form actions | DocumentUploadZone already calls toast.error() for size/format errors. Needs: network error detection (axios interceptor pattern), form save error distinction (field errors vs. server errors), "Corregir y reenviar" flow that calls crear_nueva_version then sets state back to pendiente_revision. |
</new_phase_requirements>

---

### NS-1: Backend Model — CursosCertificaciones (NEW)

**Finding:** CursosCertificaciones does NOT exist in the database. The latest migration is `0024_configuracionempresa_and_more.py`. A new migration must be created.

**Confirmed fields needed (from CONTEXT.md expansion):**
- nombre_curso (CharField)
- institucion (CharField)
- fecha_inicio (DateField)
- fecha_fin (DateField, nullable)
- horas (IntegerField or DecimalField, nullable)
- empleado FK → Empleado (CASCADE)
- documento FK → DocumentosDigitales (SET_NULL, nullable) — links the PDF cert

**Migration approach:** Standard `makemigrations app_rrhh` after adding model to `back/app_rrhh/models/` and registering in `__init__.py`. Migration number will be `0025_cursos_certificaciones.py`.

**db_table name:** Use `cursos_certificaciones` to follow the existing snake_case convention (datos_familiares, datos_academicos, documentos_digitales).

**Custom PK pattern:** All project models use named PKs (familiar_id, academico_id, documento_id). Use `curso_id = models.AutoField(primary_key=True)`.

**unique_together:** `[['empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]` to prevent duplicates while allowing same course at different institutions or dates.

```python
# Source: direct reading of back/app_rrhh/models/datos_academicos.py + datos_familiares.py
class CursosCertificaciones(models.Model):
    curso_id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE, related_name='cursos_certificaciones')
    nombre_curso = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horas = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    documento = models.ForeignKey(
        'DocumentosDigitales', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='curso_certificacion'
    )
    estado_registro = models.CharField(max_length=20, default='activo')
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cursos_certificaciones'
        unique_together = [['empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]
```

---

### NS-2: Backend Model — DocumentoFamiliar Linking

**Decision (from CONTEXT.md):** Add nullable FK `familiar` to DocumentosDigitales OR create a junction model. Research determines the right tradeoff.

**Finding after reading the model:** `DocumentosDigitales` already has `unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]`. Adding a `familiar` FK to the same table does NOT break this constraint because the unique constraint does not include `familiar`.

**Recommendation: Add nullable FK directly to DocumentosDigitales.** Rationale:
1. Simpler — one FK on existing table, one migration, no junction model overhead.
2. The `familiar` FK is always nullable (personal docs don't have a familiar). `SET_NULL` on delete preserves document history if familiar is removed.
3. Querying "all docs for familiar X" is `DocumentosDigitales.objects.filter(familiar_id=X)` — trivially simple.
4. A junction model would add complexity (3-way join for every document query) with no benefit at this scale.

**Migration:** Add `familiar = models.ForeignKey('DatosFamiliares', on_delete=models.SET_NULL, null=True, blank=True, related_name='documentos')` to `DocumentosDigitales`.

**Migration risk:** This is an `ALTER TABLE documentos_digitales ADD COLUMN familiar_id INT NULL` — safe on PostgreSQL with existing data. No data loss.

---

### NS-3: Backend Model — DatosAcademicos → DocumentosDigitales FK

**Decision (from CONTEXT.md):** Add nullable FK `documento` to DocumentosDigitales in DatosAcademicos.

**Finding after reading the model:** `DatosAcademicos` currently stores document paths as `ruta_certificado`, `ruta_titulo`, `ruta_diploma` (all `CharField(max_length=255)`). The expansion requires replacing this with a proper FK.

**Recommendation: Add `documento` nullable FK to DatosAcademicos** (mirroring the familiar approach). Do NOT remove the existing CharField fields in this migration — leave them as deprecated but nullable to avoid data loss on existing records.

```python
# Add to DatosAcademicos
documento = models.ForeignKey(
    'DocumentosDigitales', on_delete=models.SET_NULL, null=True, blank=True,
    related_name='dato_academico'
)
```

**Note:** The `ruta_certificado`, `ruta_titulo`, `ruta_diploma` fields on DatosAcademicos are CharField paths, not FKs. They should be left intact (nullable, blank=True already via existing code) to avoid a complex data migration. New records set `documento` FK; legacy records keep the old path fields.

---

### NS-4: Employee-Accessible Endpoints — Permission Override Pattern

**Finding:** `DatosFamiliaresViewSet` and `DatosAcademicosViewSet` currently have `permission_classes = [RRHHPermission]` at class level. The `list`, `retrieve` methods already use `@require_authenticated()` (they work for employees to READ), but `create`, `update`, `partial_update` use `@require_hr()` (employees cannot write).

**Established pattern in this codebase (from OnboardingViewSet.get_permissions()):**

```python
# Source: back/api/v1/rrhh/views.py line 2112-2116
def get_permissions(self):
    """Allow authenticated employees to use upload actions."""
    if self.action in ("subir_foto", "subir_documento", "mi_onboarding", "retrieve"):
        return [permissions.IsAuthenticated()]
    return super().get_permissions()
```

**Recommendation for DatosFamiliaresViewSet:** Override both `get_permissions()` AND `create`/`update` methods to check ownership. The key security requirement is: employees can only create/update records for their own `empleado_id`.

```python
# Source: pattern from DocumentosDigitalesViewSet.create() lines 1797-1806
def create(self, request, *args, **kwargs):
    empleado_id = request.data.get("empleado")
    user = request.user
    if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
        if not user.empleado or user.empleado.empleado_id != int(empleado_id):
            return APIResponse.error(
                message="Solo puede registrar familiares para su propio legajo",
                status_code=status.HTTP_403_FORBIDDEN,
            )
    return super().create(request, *args, **kwargs)
```

**get_queryset() scoping for employees:**

```python
def get_queryset(self):
    queryset = super().get_queryset()
    user = self.request.user
    # Employees see only their own records
    if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
        if user.empleado:
            queryset = queryset.filter(empleado=user.empleado)
        else:
            queryset = queryset.none()
    empleado_id = self.request.query_params.get("empleado")
    if empleado_id:
        queryset = queryset.filter(empleado_id=empleado_id)
    return queryset
```

**CRITICAL:** The `subir-documento` endpoint on OnboardingViewSet already maps `tipo_documento` → `categoria`. For familiar documents, the endpoint must also accept an optional `familiar_id` parameter and set `documento.familiar_id = familiar_id` after creation. This links the uploaded document to the correct DatosFamiliares record.

---

### NS-5: PDF Preview Before Upload — react-pdf v10 Already Installed

**Finding:** `react-pdf` v10.3.0 is already in `front/package.json`. No new dependency needed.

**Two preview scenarios:**

**Scenario A: Pre-upload preview (file selected but not yet POSTed)**
- Use `URL.createObjectURL(file)` to create a blob URL
- Feed the blob URL to react-pdf `<Document url={blobUrl}>` or a plain `<iframe src={blobUrl}>`
- Must call `URL.revokeObjectURL(blobUrl)` on modal close to release memory

**Scenario B: Already-uploaded document preview**
- Document URL is `documento.archivo_url` from the API response
- Use `<iframe src={archivoUrl}>` for simplicity — reliable across all browsers without extra libs
- react-pdf is useful for page-by-page rendering but adds complexity; iframe is sufficient for preview-only UX

**Decision for this codebase:** Use iframe for both scenarios in the preview modal. Rationale:
1. `react-pdf` requires a Worker setup (`pdfjs-dist/build/pdf.worker.min.mjs`) that adds Vite config complexity
2. Iframe works in all modern browsers for PDF display without additional config
3. The preview modal is lightweight — user just confirms the file looks correct before submitting
4. CONTEXT.md expansion explicitly says "use `<iframe src={url}>` for PDFs already uploaded; for pre-upload use URL.createObjectURL(file)"

**Preview modal pattern:**

```typescript
// Source: CONTEXT.md expansion + Radix Dialog (already in src/components/ui/dialog.tsx)
interface PreviewModalProps {
  file: File | null        // pre-upload scenario
  archivoUrl?: string | null  // post-upload scenario
  label: string
  onConfirm: () => void    // triggers the actual POST
  onCancel: () => void     // discards the file
}

function DocumentPreviewModal({ file, archivoUrl, label, onConfirm, onCancel }: PreviewModalProps) {
  const previewUrl = file ? URL.createObjectURL(file) : archivoUrl
  // cleanup blob URL on unmount
  useEffect(() => {
    return () => { if (file && previewUrl) URL.revokeObjectURL(previewUrl) }
  }, [])
  return (
    <Dialog open onOpenChange={onCancel}>
      <DialogContent className="max-w-2xl h-[80vh]">
        <iframe src={previewUrl ?? ''} className="w-full h-full" title={label} />
        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onCancel}>Cancelar</Button>
          <Button onClick={onConfirm}>Enviar documento</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

**Integration with DocumentUploadZone:** The existing `DocumentUploadZone` component calls `handleUpload(file)` immediately on `onDropAccepted`. The change is: intercept at `onDropAccepted`, set `pendingFile` state, open the preview modal. Only call `handleUpload(file)` when the modal "Enviar documento" button is clicked.

---

### NS-6: Per-Document Approve/Reject Endpoints

**Finding:** `DocumentosDigitales.validar_documento(usuario, observaciones)` and `rechazar_documento(usuario, motivo)` methods already exist on the model. The OnboardingViewSet needs two new `@action` endpoints.

**URL structure:** `POST /api/v1/rrhh/onboarding/{id}/documentos/{doc_id}/aprobar/` and `.../rechazar/`

**DRF pattern for nested resource actions:** DRF `@action` with a `url_path` that includes a positional segment is supported using `url_path='documentos/(?P<doc_id>[^/.]+)/aprobar'`:

```python
# Source: DRF @action docs — url_path supports regex groups
@action(detail=True, methods=["post"], url_path=r"documentos/(?P<doc_id>[^/.]+)/aprobar")
@require_hr()
def aprobar_documento(self, request, pk=None, doc_id=None):
    onboarding = self.get_object()
    try:
        doc = DocumentosDigitales.objects.get(
            documento_id=doc_id,
            empleado=onboarding.empleado,
            es_version_actual=True,
        )
    except DocumentosDigitales.DoesNotExist:
        return APIResponse.error(message="Documento no encontrado", status_code=404)
    doc.validar_documento(request.user)
    # Trigger approval email notification
    OnboardingNotificationService.notificar_documento_aprobado(onboarding, doc)
    return APIResponse.success(
        message=f"Documento '{doc.nombre_documento}' aprobado",
        data={"documento_id": doc.documento_id, "estado_documento": doc.estado_documento}
    )

@action(detail=True, methods=["post"], url_path=r"documentos/(?P<doc_id>[^/.]+)/rechazar")
@require_hr()
def rechazar_documento(self, request, pk=None, doc_id=None):
    motivo = request.data.get("motivo", "").strip()
    if not motivo:
        return APIResponse.error(message="motivo es requerido para rechazar un documento")
    onboarding = self.get_object()
    try:
        doc = DocumentosDigitales.objects.get(
            documento_id=doc_id,
            empleado=onboarding.empleado,
            es_version_actual=True,
        )
    except DocumentosDigitales.DoesNotExist:
        return APIResponse.error(message="Documento no encontrado", status_code=404)
    doc.rechazar_documento(request.user, motivo)
    # Trigger rejection email notification
    OnboardingNotificationService.notificar_documento_rechazado(onboarding, doc, motivo)
    return APIResponse.success(
        message=f"Documento '{doc.nombre_documento}' rechazado",
        data={"documento_id": doc.documento_id, "estado_documento": doc.estado_documento}
    )
```

**CRITICAL:** After approval/rejection, the onboarding status must be recalculated. Call `OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)` at the end of each action.

---

### NS-7: Email Notifications — Service Pattern

**Finding:** `OnboardingService` currently handles: welcome email, resend welcome email, email correction. The new notifications follow the same pattern — render template, send via `send_email_html_task` with sync fallback.

**Three new notification types needed:**

| Trigger | Recipient | Template to create |
|---------|-----------|-------------------|
| Document rejected | Employee | `emails/documento_rechazado.html` + `.txt` |
| Onboarding approved | Employee | `emails/onboarding_aprobado.html` + `.txt` |
| Onboarding rejected/observed | Employee | `emails/onboarding_observado.html` + `.txt` |

**Recommendation:** Create `OnboardingNotificationService` as a separate class in `back/app_rrhh/services/onboarding_service.py` (or a new file `back/app_rrhh/services/onboarding_notification_service.py`) to avoid bloating `OnboardingService`.

**Pattern for each notification (mirrors enviar_email_bienvenida):**

```python
# Source: OnboardingService.enviar_email_bienvenida pattern
@staticmethod
def notificar_documento_rechazado(onboarding, documento, motivo):
    empleado = onboarding.empleado
    context = {
        "nombre_empleado": empleado.nombre_completo,
        "nombre_documento": documento.nombre_documento,
        "motivo": motivo,
        "frontend_url": getattr(settings, "FRONTEND_URL", "http://localhost:5173"),
    }
    html_content = render_to_string("emails/documento_rechazado.html", context)
    text_content = render_to_string("emails/documento_rechazado.txt", context)
    recipient = empleado.correo_personal
    # Same Celery-with-sync-fallback pattern as enviar_email_bienvenida
    try:
        send_email_html_task.apply_async(...)
    except Exception:
        OnboardingService._enviar_email_sincrono(...)
```

**Django template single-line rule:** All `{% %}` and `{{ }}` tags in the email templates MUST be on single lines. Django's template lexer does not support multi-line template tags.

---

### NS-8: N-Item Dynamic Forms — useFieldArray Pattern

**Finding:** `react-hook-form` v7.47.0 is installed (confirmed from `package.json`). `useFieldArray` is part of react-hook-form core — no new dependency needed. No existing usage of `useFieldArray` was found in the codebase (all current forms are single-record).

**Recommendation: Use `useFieldArray` for all N-item sections.** It handles: adding items, removing items, reordering, per-item validation, and dirty state tracking — all without custom state management.

**Pattern for familiar section:**

```typescript
// Source: react-hook-form v7 docs — useFieldArray
import { useForm, useFieldArray } from 'react-hook-form'

interface FamiliarFormItem {
  nombres_familiar: string
  apellido_paterno: string
  apellido_materno: string
  parentesco: string
  fecha_nacimiento: string
  numero_documento: string
  tipo_documento: string
  // document IDs for per-familiar upload zones
  dni_familiar_doc_id?: number | null
  partida_nacimiento_doc_id?: number | null
  acta_matrimonio_doc_id?: number | null
}

const { control, register, handleSubmit } = useForm<{ familiares: FamiliarFormItem[] }>({
  defaultValues: { familiares: [] }
})
const { fields, append, remove } = useFieldArray({ control, name: 'familiares' })
```

**Per-item document upload:** Each familiar card (a `fields[i]` entry) shows `DocumentUploadZone` components for required documents. The zone must pass `familiar_id` (once the familiar is saved) to the upload endpoint so the document is linked. This means the upload happens in two steps: (1) save DatosFamiliares record → get familiar_id back, (2) upload document with familiar_id.

**Accordion for each category:** `@radix-ui/react-accordion` v1.1.2 is installed (in `package.json`) but no `accordion.tsx` component exists in `src/components/ui/`. The planner must add a Wave 5 task to scaffold the Accordion shadcn component (`npx shadcn-ui@latest add accordion`) OR build a simple expand/collapse with Radix directly.

**Alternative to Accordion (if not added):** Use Radix `Collapsible` or simple `details`/`summary` HTML with Tailwind styling — both work without a new component. The planner can decide.

---

### NS-9: "Corregir y Reenviar" Flow for Rejected Documents

**Finding:** The existing `DocumentUploadZone` already shows rejection reason and a "Reemplazar" button (which calls `handleUpload` with the new file). The expanded requirement adds: after replacement upload, the document must go back to `pendiente_revision` (which already happens — `subir-documento` endpoint sets `estado_documento='pendiente_revision'` on the new document via `crear_nueva_version`).

**Key behavior confirmed from existing code:**
- `subir-documento` calls `crear_nueva_version` when an existing current document exists
- `crear_nueva_version` sets old doc to `es_version_actual=False` and new doc to `estado_documento` is set by the caller
- The view sets `estado_documento='pendiente_revision'` explicitly

**The expanded requirement is a UX rename**: "Reemplazar" → "Corregir y reenviar" when `estado_documento === 'rechazado'`. The underlying upload logic is identical. This is a frontend-only change to the `DocumentUploadZone` component.

**Preview modal integration for resubmission:** When employee clicks "Corregir y reenviar", the new file selection triggers the preview modal before the actual POST. This is the same preview flow as a first-time upload.

---

### NS-10: Progress Recalculation — Approved Docs Only

**Finding from CONTEXT.md expansion:** "Progress should reflect approved documents (not just uploaded). Recalculate: progreso_porcentaje = (docs aprobados / total docs requeridos) * 100"

**Current behavior (from onboarding.py):** `progreso_porcentaje` counts the 7 boolean checklist flags (each flag = one category complete). The flags are set to True by `actualizar_estado_onboarding` when ANY document in that category has `estado_documento in ['activo', 'pendiente_revision', 'aprobado']`.

**Change required:** In `actualizar_estado_onboarding`, the document filter for each flag must be changed from `estado_documento__in=["activo", "pendiente_revision", "aprobado"]` to `estado_documento='aprobado'` only. This changes the progress semantics from "uploaded" to "approved".

**RISK:** This is a behavior change that affects the existing 7-flag logic. The existing test `test_actualizar_estado_dni` (and similar) test that uploading marks the flag True — they will break if the filter is changed to `aprobado` only, because uploaded docs are `pendiente_revision` not `aprobado`.

**Resolution approach:** Keep the upload-based flags for the STATE MACHINE transitions (employee needs to be able to progress to `pendiente_validacion` without RRHH approving each doc). Change ONLY the `progreso_porcentaje` calculation to count approved docs separately from the checklist flags.

**Recommended:** Add a new `progreso_aprobado` property to `OnboardingEmpleado` that counts approved documents, while leaving `progreso_porcentaje` (and its checklist flags) unchanged. Expose `progreso_aprobado` in the serializer. Frontend displays `progreso_aprobado` in the progress bar.

---

### NS-11: Accordion Component Gap

**Finding:** `@radix-ui/react-accordion` v1.1.2 is installed but there is NO `accordion.tsx` in `front/src/components/ui/`. The CONTEXT.md expansion specifies "each category is a separate accordion/section with 'Agregar' button."

**Options:**
1. Add the shadcn accordion component: `npx shadcn-ui@latest add accordion` — generates `src/components/ui/accordion.tsx`. This is the cleanest approach.
2. Use Radix primitives directly (`@radix-ui/react-accordion` Primitive) without a shadcn wrapper — more verbose but no new file required.
3. Use a simple CSS-based expand/collapse (no library) — sufficient but loses Radix accessibility features.

**Recommendation:** Plan Wave 5 to add the accordion component via shadcn-ui CLI as a Wave 0 task (infra). This gives the planner a clean `<Accordion>`, `<AccordionItem>`, `<AccordionTrigger>`, `<AccordionContent>` API.

---

### NS-12: CursosCertificaciones ViewSet and Serializer

**Finding:** No ViewSet or serializer exists for CursosCertificaciones. Must be created from scratch following the DatosAcademicosViewSet pattern.

**Required:**
- `CursosCertificacionesSerializer` in `back/api/v1/rrhh/serializers.py`
- `CursosCertificacionesViewSet` in `back/api/v1/rrhh/views.py` (class-level `RRHHPermission`, `get_permissions()` override for employee write)
- Router registration: `router.register(r'cursos-certificaciones', CursosCertificacionesViewSet, basename='curso-certificacion')` in `back/api/v1/rrhh/urls.py`
- Import in `back/app_rrhh/models/__init__.py`

**Serializer fields:** `curso_id` (read_only), `empleado`, `nombre_curso`, `institucion`, `fecha_inicio`, `fecha_fin`, `horas`, `documento` (FK write-as ID, read as documento_id).

---

### NS-13: subir-documento Endpoint — New Type Mappings

**Finding:** The existing `subir-documento` action has a hardcoded `_TIPO_CATEGORIA_MAP` dict with 10 tipos. The expanded scope adds new document types:

New types needed:
- `acta_matrimonio` → `familiar` (for conyuge/conviviente)
- `certificado_union_hecho` → `familiar` (for conviviente)
- `constancia_trabajo` → `laboral` (for work history entries — CONTEXT.md uses "constancias/certificados de trabajo")
- `certificado_capacitacion` → `academico` (for cursos/diplomados)

The endpoint also needs an optional `familiar_id` parameter to link the document to a DatosFamiliares record, and an optional `academico_id` or `curso_id` parameter to link to DatosAcademicos or CursosCertificaciones respectively.

```python
# After doc creation in subir-documento, add optional linking:
familiar_id = request.data.get("familiar_id")
if familiar_id:
    try:
        from app_rrhh.models import DatosFamiliares
        familiar = DatosFamiliares.objects.get(
            familiar_id=familiar_id, empleado=empleado
        )
        doc.familiar = familiar
        doc.save(update_fields=["familiar"])
    except DatosFamiliares.DoesNotExist:
        pass  # silently ignore invalid familiar_id
```

---

### NS-14: Toast/Error Handling — Complete Spec

**Current state (confirmed from DocumentUploadZone.tsx):**
- `toast.error('El archivo supera los 10 MB permitidos')` — already present
- `toast.error('Solo se permiten imágenes JPG o PNG')` / `'Solo se permiten archivos PDF'` — already present
- `toast.error(msg ?? 'Error al subir ${label}')` — already present

**Missing (per CONTEXT.md expansion):**
- Upload success: `toast.success('Documento enviado correctamente')` — the current code uses `toast.success(\`${label} subido exitosamente\`)`, which is close but not the specified message
- Form save success/error: currently no form save toasts
- Network error detection: currently catches all errors as generic upload error

**Network error detection pattern:**

```typescript
// Detect network errors vs. server errors in axios
const isNetworkError = (err: unknown): boolean => {
  const axiosErr = err as { code?: string; response?: unknown }
  return axiosErr.code === 'ERR_NETWORK' || axiosErr.code === 'ECONNABORTED' || !axiosErr.response
}

// In catch block:
if (isNetworkError(err)) {
  toast.error('Sin conexion. Verifica tu internet.')
} else {
  const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
  toast.error(msg ?? 'Error al subir el documento. Intenta nuevamente.')
}
```

---

## New Scope — Architecture Patterns

### N-Item Form Architecture (useFieldArray)

```
OnboardingTabFamiliar (NEW — replaces current stub)
├── useFieldArray({ control, name: 'familiares' }) — manages list state
├── For each field:
│   ├── FamiliarCard (new component)
│   │   ├── Form fields: nombres, apellidos, parentesco, fecha_nacimiento, documento
│   │   ├── "Guardar familiar" button → POST /api/v1/rrhh/datos-familiares/
│   │   └── After save: show DocumentUploadZone slots per parentesco rules
│   └── Per-parentesco required docs (derived from parentesco value):
│       ├── hijo: DNI familiar + partida de nacimiento
│       ├── conyuge/conviviente: DNI familiar + acta de matrimonio OR cert union hecho
│       └── padre/madre: DNI familiar + partida de nacimiento del empleado
└── "Agregar dependiente" button → append({ ...emptyItem })

OnboardingTabAcademico (NEW — replaces current stub)
├── CertificadosSection (useFieldArray 'certificados')
│   ├── Each item: institucion, fecha_inicio, fecha_fin + DocumentUploadZone
│   └── "Agregar certificado" button
├── CursosSection (useFieldArray 'cursos')
│   ├── Each item: nombre_curso, institucion, fecha_inicio, fecha_fin, horas + upload zone
│   └── "Agregar curso" button
└── TitulosSection (useFieldArray 'titulos')
    ├── Each item: tipo (nivel_educativo), nombre_carrera, institucion, fechas + upload zone
    └── "Agregar titulo" button
```

### Two-Step Upload Flow (Preview Modal)

```
1. Employee drops/selects file
2. onDropAccepted fires → setPendingFile(file) → setShowPreview(true)
3. DocumentPreviewModal renders:
   - <iframe src={URL.createObjectURL(pendingFile)}>
   - "Cancelar" button → setPendingFile(null), setShowPreview(false)
   - "Enviar documento" button → handleUpload(pendingFile), close modal
4. On upload success: invalidate ['mi-onboarding'] query
5. On modal unmount: URL.revokeObjectURL(blobUrl)
```

### RRHH Per-Document Approval Flow

```
OnboardingDetailPage (new page OR expanded existing detail view)
├── Document list (all DocumentosDigitales for this empleado, es_version_actual=True)
│   For each doc:
│   ├── Preview button → open DocumentPreviewModal with archivoUrl
│   ├── "Aprobar" button (green) → POST /onboarding/{id}/documentos/{doc_id}/aprobar/
│   └── "Rechazar" button (red) → open RejectionDialog (motivo input) → POST /rechazar/
└── After each approve/reject: invalidate onboarding query to refresh progress
```

---

## New Scope — Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| N-item dynamic form state | useState array + manual add/remove | `useFieldArray` from react-hook-form | Already installed; handles dirty state, validation, array manipulation |
| PDF viewer before upload | pdf.js Worker setup + react-pdf config | `<iframe src={URL.createObjectURL(file)}>` | Zero config, works in all modern browsers, CONTEXT.md explicitly specifies this approach |
| Document approval/rejection logic | Custom state changes on DocumentosDigitales | Existing `validar_documento()` / `rechazar_documento()` model methods | Already implemented with correct field updates (validado_por, fecha_validacion, observaciones_validacion) |
| Email queuing for notifications | Custom task | Existing `send_email_html_task` with sync fallback | Same pattern as welcome email — reuse entirely |
| CursosCertificaciones form validation | Custom JS validation | `zod` schema + react-hook-form `resolver` | Project standard for all forms |
| Accordion UI for sections | Custom expand/collapse | Radix accordion component (add via shadcn-ui CLI) | Already installed as dependency, just needs scaffolding |

---

## New Scope — Common Pitfalls

### Pitfall 7: familiar_id Not Available at Upload Time

**What goes wrong:** Employee adds a familiar and tries to upload their document in the same form interaction. But the familiar_id (PK from DB) is not known until after the DatosFamiliares POST succeeds.

**How to avoid:** The flow MUST be two sequential steps: (1) POST DatosFamiliares → get familiar_id in response, (2) enable document upload zones with the received familiar_id. Never show upload zones before the familiar is saved. Use React Query mutation with `onSuccess` callback to enable the upload zones.

### Pitfall 8: DatosAcademicos unique_together Breaks Multi-Record Scenarios

**What goes wrong:** `DatosAcademicos` has `unique_together = [['empleado', 'nivel_educativo', 'nombre_carrera', 'nombre_institucion']]`. An employee with two degrees from the same career at different institutions will violate this constraint if the institution name matches.

**How to avoid:** Serializer validation must check for this constraint before creating. On IntegrityError (409-like), return a clear error: "Ya existe un registro con el mismo nivel educativo, carrera e institución." The frontend must show this validation error inline on the form item.

### Pitfall 9: URL.createObjectURL Memory Leak

**What goes wrong:** Creating a blob URL with `URL.createObjectURL(file)` and never calling `URL.revokeObjectURL(url)` causes the browser to hold the file in memory indefinitely.

**How to avoid:** In the preview modal component, use `useEffect` cleanup:
```typescript
useEffect(() => {
  const blobUrl = URL.createObjectURL(file)
  setBlobPreviewUrl(blobUrl)
  return () => URL.revokeObjectURL(blobUrl)
}, [file])
```

### Pitfall 10: Nested URL Action Regex Must Match Router

**What goes wrong:** DRF `@action(url_path=r"documentos/(?P<doc_id>[^/.]+)/aprobar")` works but the router may not pass `doc_id` to the view if the regex doesn't match the router's URL conf.

**How to avoid:** Test the URL resolution with a known onboarding_id and doc_id immediately after adding the actions. The pattern `r"documentos/(?P<doc_id>[^/.]+)/aprobar"` is confirmed to work with DRF routers for nested resource actions. Alternatively, use a simpler flat endpoint: `POST /api/v1/rrhh/documentos/{doc_id}/aprobar/` on `DocumentosDigitalesViewSet` — simpler routing, same result.

**Flat endpoint alternative (LOW complexity):**

```python
# On DocumentosDigitalesViewSet instead — simpler URL
@action(detail=True, methods=["post"], url_path="aprobar")
@require_hr()
def aprobar(self, request, pk=None):
    doc = self.get_object()
    doc.validar_documento(request.user)
    # find onboarding and send notification
    onboarding = OnboardingEmpleado.objects.filter(empleado=doc.empleado).first()
    if onboarding:
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
    return APIResponse.success(data={"estado_documento": doc.estado_documento})
```

URL: `POST /api/v1/rrhh/legajo/{doc_id}/aprobar/` — avoids nested regex entirely.

### Pitfall 11: OnboardingEmpleado Progress Logic Change Breaks Tests

**What goes wrong:** Changing `actualizar_estado_onboarding` to count only `aprobado` documents breaks 7 existing tests in `test_onboarding_service.py` that verify flags become True on upload (where estado is `pendiente_revision`).

**How to avoid:** Do NOT change the existing 7 boolean flag logic. Add a separate `progreso_aprobado` property. See NS-10 above.

---

## New Scope — Test Map (Wave 5-8)

| Req ID | Behavior | Test Type | Command | File |
|--------|----------|-----------|---------|------|
| ONBD-09 | Employee can POST DatosFamiliares for own empleado_id | unit | `pytest tests/test_datos_familiares_api.py -x` | New — Wave 5 |
| ONBD-09 | Employee CANNOT POST DatosFamiliares for another empleado_id | unit | `pytest tests/test_datos_familiares_api.py::test_permission_denied -x` | New — Wave 5 |
| ONBD-10 | CursosCertificaciones migration creates table | unit | `pytest tests/test_cursos_model.py -x` | New — Wave 5 |
| ONBD-10 | Employee can POST CursosCertificaciones for own empleado_id | unit | `pytest tests/test_cursos_api.py -x` | New — Wave 5 |
| ONBD-12 | Preview modal opens on file drop, POST only on confirm | manual | N/A — browser test | N/A |
| ONBD-13 | POST .../aprobar/ sets estado_documento='aprobado' | unit | `pytest tests/test_onboarding_api.py::test_aprobar_documento -x` | New — Wave 6 |
| ONBD-13 | POST .../rechazar/ requires motivo, sets estado='rechazado' | unit | `pytest tests/test_onboarding_api.py::test_rechazar_documento -x` | New — Wave 6 |
| ONBD-14 | notificar_documento_rechazado sends email to empleado | unit | `pytest tests/test_onboarding_service.py::test_notif_rechazo -x` | New — Wave 6 |
| ONBD-14 | notificar_onboarding_aprobado sends email to empleado | unit | `pytest tests/test_onboarding_service.py::test_notif_aprobado -x` | New — Wave 6 |
| ONBD-15 | Network error shows correct toast message | unit | Vitest component test | New — Wave 7 |

---

## New Scope — Sources

### Primary (HIGH confidence)
- Direct codebase reads (2026-03-15): `back/app_rrhh/models/datos_familiares.py`, `back/app_rrhh/models/datos_academicos.py`, `back/app_rrhh/models/documentos_digitales.py`, `back/app_rrhh/models/onboarding.py`, `back/app_rrhh/services/onboarding_service.py`, `back/api/v1/rrhh/views.py` (lines 949-1065, 1757-1836, 2090-2424), `back/api/v1/rrhh/serializers.py` (lines 108-193), `back/api/v1/rrhh/urls.py`, `back/app_rrhh/models/__init__.py`, `front/src/features/onboarding/components/DocumentUploadZone.tsx`, `front/src/features/onboarding/components/OnboardingTabFamiliar.tsx`, `front/src/features/onboarding/components/OnboardingTabAcademico.tsx`, `front/src/features/onboarding/types/onboarding.ts`, `front/src/features/onboarding/services/onboardingUploadService.ts`, `front/package.json`
- `.planning/phases/01-onboarding-self-service/01-CONTEXT.md` (Phase 1 Expansion section, 2026-03-15)

### Secondary (MEDIUM confidence)
- react-hook-form v7 `useFieldArray` docs — confirmed installed at v7.47.0; API is stable since v7.0
- react-pdf v10 iframe approach — CONTEXT.md explicitly specifies iframe approach; confirmed react-pdf v10.3.0 installed
- DRF nested @action with regex url_path — documented DRF feature; tested pattern in Django community

### Tertiary (LOW confidence)
- `npx shadcn-ui@latest add accordion` command — verify the shadcn-ui CLI version before running; command syntax may vary
- Accordion component availability — @radix-ui/react-accordion v1.1.2 confirmed installed but shadcn wrapper must be generated

---

## New Scope — Metadata

**Confidence breakdown:**
- Model changes (CursosCertificaciones, FK additions): HIGH — direct model inspection, no external dependencies
- Permission overrides: HIGH — established get_permissions() pattern already in OnboardingViewSet
- PDF preview: HIGH — CONTEXT.md explicitly specifies iframe approach; react-pdf confirmed installed
- useFieldArray: HIGH — react-hook-form v7.47.0 confirmed; useFieldArray is core API
- Email notifications: HIGH — existing OnboardingService email pattern is clear and reusable
- Per-document approve/reject endpoints: HIGH — model methods exist; URL pattern is standard DRF
- Accordion component: MEDIUM — library installed but scaffold step required

**Research date:** 2026-03-15
**Valid until:** 2026-04-15
