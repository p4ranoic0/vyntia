# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

Full-stack HR intranet system (Sistema de Gestion de RRHH). Monorepo with:
- `back/` — Django 4.2 + DRF backend (Python, `.venv` at repo root)
- `front/` — React 18 + TypeScript + Vite frontend

---

## Commands

### Backend (`D:\INTRANET\back\`)

```bash
# Activate virtualenv (always required — venv is at D:\INTRANET\.venv)
D:/INTRANET/.venv/Scripts/python.exe manage.py <command>
# OR activate first: source D:/INTRANET/.venv/Scripts/activate

# Dev server
python manage.py runserver 8000 --settings=config.settings.development

# Migrations
python manage.py makemigrations app_rrhh
python manage.py migrate

# Tests (run from back/ directory)
make test                             # All tests (pytest, recommended)
make test-auth                        # Auth tests only
make test-api                         # API tests only
make test-models                      # Model tests only
make test-coverage                    # With coverage report
pytest tests/test_login_api.py -v    # Single test file
pytest tests/ -k "test_create"       # Tests matching a pattern
pytest tests/ -m "not slow"          # Skip slow tests

# Django shell (with DB)
python manage.py shell --settings=config.settings.development

# Validate template (no DB needed)
python -c "
import os, sys, django; sys.path.insert(0, '.'); os.environ['DJANGO_SETTINGS_MODULE']='config.settings.development'; django.setup()
from django.template.loader import get_template; get_template('reportes/reporte_empleado.html'); print('OK')
"
```

### Frontend (`D:\INTRANET\front\`)

```bash
npm run dev          # Dev server (proxies /api and /media to localhost:8000)
npm run build        # Production build
npm run lint         # ESLint
npm run test         # Vitest unit tests
npm run test:coverage
npm run playwright   # E2E tests
```

---

## Architecture

### Backend

**Settings**: `config/settings/{base,development,production,staging,testing}.py`
Active settings are selected via `DJANGO_SETTINGS_MODULE`. Tests use `config.settings.testing`.

**URL structure**:
```
/api/v1/auth/        → api/v1/auth/views.py
/api/v1/rrhh/        → api/v1/rrhh/views.py + contratos_views.py + remuneraciones_views.py
/api/v1/rrhh/documentos/  → api/v1/app_rrhh/document_generation_views.py
/api/v1/vacaciones/  → api/v1/vacaciones/
/api/docs/           → Swagger UI
```

**The only Django app** is `app_rrhh`. Its models are split into files under `app_rrhh/models/` and re-exported from `app_rrhh/models/__init__.py`. Key models: `Empleado`, `Area`, `Usuario`, `ContratosAdendas`, `DatosLaborales`, `DocumentosDigitales`, `PlanillaMensual`, `OnboardingEmpleado`, `Rol`, `Permiso`.

**`core/` utilities** — used across all views:
- `core/responses.py` — `APIResponse` class. All endpoints return this. `APIResponse.error()` defaults to **HTTP 400**, not 500. Use `status_code=status.HTTP_500_INTERNAL_SERVER_ERROR` explicitly when needed.
- `core/pagination.py` — `StandardResultsSetPagination` (20/page), `LargeResultsSetPagination` (50/page), `SmallResultsSetPagination` (10/page).
- `core/decorators.py` — `@require_hr()`, `@require_admin()`, `@require_authenticated()`, etc.

**Paginated response shape** (frontend must handle this):
```json
{ "success": true, "message": "...", "data": [...], "meta": { "pagination": { "total_items": N, "current_page": N, ... } } }
```

**Services layer** (`app_rrhh/services/`): Business logic lives here, not in views. Key services: `TemplateService` (HTML rendering), `PDFGenerator` (PDF generation), `EmpleadoReportService`, `onboarding_service`.

**PDF generation**: Chain is xhtml2pdf → WeasyPrint → ReportLab. Only ReportLab is reliably available on Windows. ReportLab generates a stub PDF (not full HTML render). Templates are at `templates/reportes/`, `templates/certificados/`, `templates/contratos/`.

**Django template gotcha**: Django's template lexer does not support multi-line `{% %}` or `{{ }}` tags (regex lacks `re.DOTALL`). All template tags must open and close on the **same line**.

### Backend ORM Patterns

```python
# CORRECT — custom PKs
Count('contrato_id')    # NOT Count('id')
Count('empleado_id')

# Empleado has NO direct area FK
# To get area, go through DatosLaborales
empleado.datos_laborales.filter(estado_datos='activo').select_related('area').first()

# ContratosAdendas HAS direct area FK
ContratosAdendas.objects.select_related('area')

# Area model — NO 'nombre' field
area.nombre_completo   # property
area.siglas_area       # e.g. "RRHH"
area.nombre_unidad_organica  # full name
```

### Frontend

**API client**: `src/lib/api.ts` — axios instance that reads Bearer token from localStorage, redirects to login on 401. Proxy in `vite.config.ts` routes `/api/*` to `http://127.0.0.1:8000`.

**Response unwrapping**: The backend wraps everything in `{ success, message, data, meta }`. Services in `src/services/` unwrap it:
```typescript
// Common pattern in services
const raw = response.data
return raw?.data?.results ?? raw?.results ?? raw?.data ?? raw
// Pagination:
const pagination = rawData?.meta?.pagination || {}
count = pagination.total_items || items.length
```

**Data fetching**: React Query v5 (`@tanstack/react-query`) for all server state. `QueryClientProvider` is in `App.tsx`. Custom hooks in `src/hooks/useApi.ts` and `src/hooks/useRemuneraciones.ts` wrap common queries.

**Routing** (`App.tsx`):
- Unauthenticated → `LoginForm`
- `user.requiere_cambio_password` → forced redirect to `/cambiar-password`
- Admin/RRHH routes wrapped in `<AdminRoute>` which checks `isAdminOrRRHH()`
- Admin panel pages use `<AdminLayout>` inside `<Layout>`

**Service pattern**: Each domain has a service file (`employeesService`, `contratosService`, `onboardingService`, etc.) that encapsulates all API calls. Services are called directly from components or hooks — no Redux/Zustand.

**Forms**: `react-hook-form` + `zod` for validation. Shadcn/ui (`@radix-ui` wrappers) for all UI primitives. Toast notifications via `sonner`.

### Database

MySQL `bd_rrhh_intranet` on localhost:3306. The `base.py` settings show `postgres` defaults, but the actual running environment uses MySQL. Override via environment variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

---

## Key File Locations

| What | Path |
|------|------|
| Main API views | `back/api/v1/rrhh/views.py` (85KB) |
| Contratos views | `back/api/v1/rrhh/contratos_views.py` |
| Remuneraciones views | `back/api/v1/rrhh/remuneraciones_views.py` |
| Document generation | `back/api/v1/app_rrhh/document_generation_views.py` |
| All serializers | `back/api/v1/rrhh/serializers.py` (41KB) |
| Empleado model | `back/app_rrhh/models/empleado.py` |
| PDF generator | `back/app_rrhh/services/pdf_generator.py` |
| Template service | `back/app_rrhh/services/template_service.py` |
| HTML templates | `back/templates/` |
| App routing | `front/src/App.tsx` |
| Auth context | `front/src/context/AuthContext.tsx` |
| API hooks | `front/src/hooks/useApi.ts` |
| Employees page | `front/src/pages/Empleados.tsx` |
| HR dashboard | `front/src/pages/HROverviewDashboard.tsx` |
