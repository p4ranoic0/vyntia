# CLAUDE.md — VYNTIA

> Guidance for Claude Code when working in `D:\VYNTIA`. **Read MEMORY.md first** for project state.

---

## Project Overview

**VYNTIA** is a modular HR SaaS for Peru. The product vision lives in `docs/00_VYNTIA_MAESTRO.md` (37 documents under `docs/`). Currently in active migration from a legacy intranet codebase.

**Tagline:** *Donde el talento se convierte en valor.*

**Active sub-project:** **Next: B — Migración funcional Vyntia Core** (Sub-projects A + C COMPLETE)
- Foundation spec: `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
- Sub-projects roadmap: `docs/ROADMAP_SUBPROJECTS.md`

---

## Repo Structure (post-L0)

```
D:\VYNTIA\
├── apps/
│   ├── api/              # Django 5.2 LTS + DRF backend
│   │   ├── manage.py
│   │   ├── vyntia/       # settings module (renamed from config/ in L1)
│   │   ├── apps/             # 9 bounded-context Django apps (core, identity, organization, employees, contracts, documents, payroll, time_off, onboarding)
│   │   ├── api/v1/       # views grouped by domain
│   │   ├── core/         # APIResponse, pagination, decorators
│   │   ├── tests/, templates/, media/, scripts/
│   │   ├── requirements.txt    # to be replaced by pyproject.toml in L1
│   │   ├── Makefile, pytest.ini, conftest.py
│   └── web/              # React 18 + TS + Vite frontend
│       └── src/{pages, features, shared/, hooks/, context/, ...}
├── packages/             # empty placeholder for shared libs (design-tokens, types)
├── docs/
│   ├── 00_VYNTIA_MAESTRO.md      # SaaS master plan (read first for product vision)
│   ├── arquitectura/, modulos/, normativa/, comercial/   # 37 product docs
│   ├── superpowers/specs/        # design specs from brainstorming
│   └── superpowers/plans/        # implementation plans from writing-plans
├── scripts/, .github/workflows/
├── package.json          # npm workspaces (apps/web + packages/*)
├── .gitignore            # consolidated monorepo (NOTE: missing some custom rules — see MEMORY.md)
└── README.md             # VYNTIA placeholder
```

---

## Commands

### Setup (fresh clone)

```bash
cd D:/VYNTIA
python -m venv .venv
source .venv/Scripts/activate    # Windows Git Bash
pip install -e "apps/api[dev]"
cd apps/web && npm install && cd ../..
```

### Backend (`D:/VYNTIA/apps/api/`)

```bash
# Activate venv (always required — at D:/VYNTIA/.venv/)
source D:/VYNTIA/.venv/Scripts/activate
cd apps/api

# Dev server (NOTE: currently fails locally with PostgreSQL UnicodeDecodeError — env issue, not code)
python manage.py runserver --settings=vyntia.settings.development

# System check (works without DB connect — use this to verify code structure)
python manage.py check --settings=vyntia.settings.development

# Migrations
python manage.py makemigrations <app_name>
python manage.py migrate

# Tests (pytest, run from apps/api/ directory)
pytest                               # Full suite
pytest tests/test_login_api.py -v    # Single file
pytest tests/ -k "test_create"       # Pattern match
pytest tests/ -m "not slow"          # Skip slow tests
make test-coverage                   # With coverage

# Django shell
python manage.py shell --settings=vyntia.settings.development
```

### Frontend (`D:/VYNTIA/apps/web/`)

```bash
cd apps/web
npm run dev          # Dev server (proxies /api and /media to localhost:8000)
npm run build        # Production build
npm run lint         # ESLint
npm test             # Vitest unit tests
npm run playwright   # E2E tests
```

### From repo root (npm workspaces)

```bash
cd D:/VYNTIA
npm run dev:web      # = npm run dev --workspace=apps/web
npm run build:web
npm run test:web
npm run lint:web
```

---

## Architecture (current — pre-L3 split)

### Backend

**Settings**: `apps/api/config/settings/{base,development,production,staging,testing}.py`
Active settings via `DJANGO_SETTINGS_MODULE=vyntia.settings.development`. Tests use `vyntia.settings.testing`.
**L1 done:** module renamed to `vyntia/`, settings module is `vyntia.settings.*`.

**URL structure (current)**:
```
/api/v1/auth/                       → api/v1/auth/views.py
/api/v1/rrhh/                       → api/v1/rrhh/views.py + contratos_views.py + remuneraciones_views.py
/api/v1/rrhh/documentos/            → api/v1/app_rrhh/document_generation_views.py
/api/v1/vacaciones/                 → api/v1/vacaciones/
/api/docs/                          → Swagger UI
```
**L3 plan:** split into `/api/v1/identity/`, `/api/v1/employees/`, `/api/v1/contracts/`, `/api/v1/payroll/`, `/api/v1/time-off/`, `/api/v1/documents/`, `/api/v1/organization/`, `/api/v1/onboarding/`.

**9 bounded-context Django apps**: `apps/core` (utility), `apps/identity` (User, Role, Permission, RBAC, modules/menu), `apps/organization` (Department, CompanyConfig), `apps/employees` (Employee, FamilyData, AcademicData), `apps/contracts` (Contract, ContractAmendment, EmploymentData), `apps/documents` (DocumentFile, DocumentTemplate + PDF/Word services), `apps/payroll` (9 payroll models + 2 services), `apps/time_off` (5 vacation models + 5 services), `apps/onboarding` (OnboardingProcess + 2 services). FK cross-app via string lazy only.

**`apps/api/apps/core/`** — utilities used across all views:
- `core/responses.py` — `APIResponse` class. All endpoints return this. **`APIResponse.error()` defaults to HTTP 400, not 500.** Use `status_code=status.HTTP_500_INTERNAL_SERVER_ERROR` explicitly when needed.
- `core/pagination.py` — `StandardResultsSetPagination` (20/page), `LargeResultsSetPagination` (50/page), `SmallResultsSetPagination` (10/page).
- `core/decorators.py` — `@require_hr()`, `@require_admin()`, `@require_authenticated()`.
- `core/constants.py` — `Roles` and `Permissions` constants.
- `core/permission_service.py` — `PermissionService` class.
- `core/tasks.py` — `send_email_html_task` Celery task.

**Paginated response shape**:
```json
{ "success": true, "message": "...", "data": [...], "meta": { "pagination": { "total_items": N, "current_page": N, ... } } }
```

**Services layer**: Business logic lives in `apps/<context>/services/`. Key services: `TemplateService`, `PDFGenerator` (documents), `EmpleadoReportService` (employees), `OnboardingService` (onboarding), vacation services (time_off, 5 files), `MenuService` (identity).

**PDF generation**: Chain is xhtml2pdf → WeasyPrint → ReportLab. Only ReportLab is reliably available on Windows. ReportLab generates a stub PDF (not full HTML render). Templates at `apps/api/templates/{reportes,certificados,contratos}/`.

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
area.nombre_completo            # property
area.siglas_area                # e.g. "RRHH"
area.nombre_unidad_organica     # full name
```

### Frontend

**API client**: `apps/web/src/lib/api.ts` — axios instance reads Bearer token from localStorage, redirects to login on 401. Proxy in `vite.config.ts` routes `/api/*` to `http://127.0.0.1:8000`.

**Response unwrapping** — backend wraps everything; services unwrap:
```typescript
const raw = response.data
return raw?.data?.results ?? raw?.results ?? raw?.data ?? raw
const pagination = rawData?.meta?.pagination || {}
count = pagination.total_items || items.length
```

**Data fetching**: React Query v5 (`@tanstack/react-query`). `QueryClientProvider` in `App.tsx`. Custom hooks in `src/hooks/useApi.ts`, `src/features/payroll/hooks/useRemuneraciones.ts`.

**Routing** (`App.tsx`):
- Unauthenticated → `LoginForm`
- `user.requiere_cambio_password` → forced redirect to `/cambiar-password`
- Admin/RRHH routes wrapped in `<AdminRoute>` (checks `isAdminOrRRHH()`)
- Admin pages use `<AdminLayout>` inside `<Layout>`

**Service pattern**: Each domain has a service file (`employeesService`, `contratosService`, `onboardingService`). Services called directly from components or hooks — no Redux/Zustand.

**Forms**: `react-hook-form` + `zod`. Shadcn/ui (`@radix-ui` wrappers). Toasts via `sonner`.

### Database

PostgreSQL `bd_vyntia` on localhost:5432. Legacy `bd_rrhh_intranet` left intact for reference. Override via env: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
**L1 plan:** create new `bd_vyntia` from scratch.

**Known issue:** local `runserver` fails with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3` from psycopg2.connect — `DB_PASSWORD` env var likely contains non-ASCII char (ñ, ó, etc.). Workaround: use `manage.py check` instead of `runserver` for code verification. pytest uses its own testing settings and works fine.

---

## Key File Locations

| What | Path |
|------|------|
| Main API views | `apps/api/api/v1/rrhh/views.py` |
| Contratos views | `apps/api/api/v1/rrhh/contratos_views.py` |
| Remuneraciones views | `apps/api/api/v1/rrhh/remuneraciones_views.py` |
| Document generation | `apps/api/api/v1/app_rrhh/document_generation_views.py` |
| All serializers | `apps/api/api/v1/rrhh/serializers.py` |
| Employee model | `apps/api/apps/employees/models/employee.py` |
| PDF generator | `apps/api/apps/documents/services/pdf_generator.py` |
| Template service | `apps/api/apps/documents/services/template_service.py` |
| HTML templates | `apps/api/templates/` |
| constants / permissions | `apps/api/apps/core/constants.py`, `apps/api/apps/core/permission_service.py` |
| Menu service | `apps/api/apps/identity/services/menu_service.py` |
| Employee report | `apps/api/apps/employees/services/employee_report_service.py` |
| Vacation validators | `apps/api/apps/time_off/validators.py` |
| Email tasks | `apps/api/apps/core/tasks.py` |
| Management commands | `apps/api/apps/{identity,documents,payroll}/management/commands/` |
| App routing | `apps/web/src/App.tsx` |
| Auth context | `apps/web/src/features/auth/context/AuthContext.tsx` |
| Employees hook | `apps/web/src/features/employees/hooks/useEmployees.ts` |
| Departments hook | `apps/web/src/features/organization/hooks/useDepartments.ts` |
| Theme context | `apps/web/src/shared/context/ThemeContext.tsx` |
| Employees page | `apps/web/src/features/employees/pages/Empleados.tsx` |
| HR dashboard | `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` |
| App-level dashboard | `apps/web/src/shared/pages/Dashboard.tsx` |
| Admin dashboard | `apps/web/src/features/identity/pages/AdminDashboard.tsx` |
| Layout components | `apps/web/src/shared/layout/` (AdminLayout, Layout, Sidebar, Header, etc.) |
| Menu service (FE) | `apps/web/src/shared/api/menuService.ts` |
| **Foundation spec** | `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` |
| **Sub-projects roadmap** | `docs/ROADMAP_SUBPROJECTS.md` |
| **Master product vision** | `docs/00_VYNTIA_MAESTRO.md` |
| Brand kit | `C:/Users/zeeke/Downloads/vyntia_brand_ui.md`, `vyntia_full_system.md` |

---

## Migration Roadmap (sub-projects)

| Code | Sub-project | Status | Notes |
|------|-------------|--------|-------|
| **A** | Foundation (rebrand + restructure + cleanup) | **✅ COMPLETE (L0-L5 done)** | All layers merged |
| **C** | Multi-tenancy + RLS | **✅ COMPLETE (C.0-C.8 done)** | Enables SaaS sales |
| **B** | Migración funcional Vyntia Core | **NEXT** | Needs A + C |
| D | Vyntia Pay (planilla peruana real) | not started | Starter MVP |
| ~20 más | See `docs/ROADMAP_SUBPROJECTS.md` | — | Each = own brainstorm + spec + plan |

**Foundation layers (L0-L5):**
- L0 ✅ Bootstrap monorepo (apps/api, apps/web, packages, docs)
- L1 ✅ Rebrand superficial done (BD `bd_vyntia`, `config/`→`vyntia/`, design tokens VYNTIA, Inter font)
- L2 ✅ Django 5.2 LTS upgrade done
- L3 ✅ Split `app_rrhh` into 8 Django apps (L3.1–L3.11 complete)
- L4 ✅ Reorganize frontend by feature (L4.1–L4.11 complete)
- L5 ✅ Cleanup final + docs + CI

---

## Test Baselines (preserved through L0)

- Backend pytest: **161 passed, 7-8 failed (pre-existing accepted), 3 skipped** — DO NOT regress
- Frontend vitest: **7 passed, 1 file load-failure** (Playwright e2e captured by vitest, pre-existing config bug)

The 44 backend failures are pre-existing in master and were accepted as known issues (auth fixtures + DRF/pytest fixture compat bugs). They are NOT to be fixed as part of Foundation — separate sub-project.

---

## Quick references for next session

- **Read first:** `MEMORY.md` (in this Claude memory folder) for active state
- **Spec source of truth:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
- **Working branch convention:** `vyntia/L<N>-<short-name>` (e.g., `vyntia/L1-rebrand-surface`)
- **Commit prefix:** `chore(L<N>):` for refactor commits during Foundation
- **Verification commands:** `manage.py check` (not `runserver` due to env issue) + `pytest` + `npm run build`
