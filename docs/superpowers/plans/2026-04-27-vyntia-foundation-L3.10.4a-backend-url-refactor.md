# VYNTIA Foundation L3.10.4a — Backend URL Refactor (English paths) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar URL paths nuevos en inglés que mapean a los mismos ViewSets ya existentes, alineados con spec § 3.4. Las URLs viejas (`/api/v1/rrhh/empleados/`, `/api/v1/rrhh/contratos-adendas/`, etc.) se PRESERVAN en paralelo durante la transición — frontend (L3.10.4b) consumirá las nuevas, viejas se remueven en L3.11.

**Architecture:** L3.10.4a es backend-only. No toca frontend. No toca lógica de negocio. Solo agrega entradas en `api/v1/urls.py` que routean a app-specific URL configs nuevos en `api/v1/{identity,employees,organization,contracts,documents,payroll,time_off,onboarding}/`. Cada app config registra los viewsets ya existentes (en `api/v1/rrhh/views.py`, `contratos_views.py`, etc.) con `basename` distintos para evitar collision con las URLs legacy.

**Tech Stack:** Django 5.2, DRF DefaultRouter, URL include() pattern.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 3.4 "URL structure resultante".

**Scope decision (Option B — sub-PR de L3.10):**
- L3.10.1 ✅ Class names rename (33 clases)
- L3.10.2 ✅ Audit fields + state literals + PKs UUID
- L3.10.3 ✅ Contract split
- **L3.10.4a (este plan)** — backend URL refactor: nuevas URLs en inglés. Backend-only, sin tocar frontend.
- L3.10.4b ⏳ Frontend rename: services TS + tipos + componentes consume las URLs nuevas.

**Pre-condiciones:**
- L3.10.3 mergeada a master (commit `e7bcf132`)
- Django 5.2.13 operativo, todas las apps con viewsets registrados en `api/v1/rrhh/urls.py` (legacy)
- pytest baseline: **161 passed, 8 failed, 3 skipped**
- venv en `D:/VYNTIA/.venv/`

---

## Tabla canónica de URL refactor

### Antes de L3.10.4a (post-L3.10.3)

```
/api/v1/auth/login/
/api/v1/auth/logout/
/api/v1/auth/menu/
/api/v1/rrhh/empleados/
/api/v1/rrhh/areas/
/api/v1/rrhh/usuarios/
/api/v1/rrhh/roles/
/api/v1/rrhh/permisos/
/api/v1/rrhh/modulos/
/api/v1/rrhh/rol-permisos/
/api/v1/rrhh/usuario-roles/
/api/v1/rrhh/datos-familiares/
/api/v1/rrhh/datos-academicos/
/api/v1/rrhh/cursos-certificaciones/
/api/v1/rrhh/datos-laborales/
/api/v1/rrhh/contratos-adendas/
/api/v1/rrhh/adendas/
/api/v1/rrhh/documentos-digitales/
/api/v1/rrhh/configuracion-empresa/
/api/v1/rrhh/onboarding/
/api/v1/rrhh/planillas-mensuales/
/api/v1/rrhh/detalles-planilla/
/api/v1/rrhh/descuentos-masivos/
/api/v1/rrhh/boletas-pago/
/api/v1/rrhh/calendarios-pago/
/api/v1/rrhh/configuracion-afp/
/api/v1/rrhh/configuracion-uit/
/api/v1/rrhh/configuracion-remuneraciones/
/api/v1/rrhh/documentos/generar-contrato/
/api/v1/rrhh/documentos/generar-adenda/
/api/v1/rrhh/documentos/generar-certificado/
/api/v1/vacaciones/...
```

### Después de L3.10.4a (URLs viejas + URLs nuevas en paralelo)

URLs nuevas agregadas (legacy preserved):

```
# identity
/api/v1/identity/users/
/api/v1/identity/roles/
/api/v1/identity/permissions/
/api/v1/identity/modules/
/api/v1/identity/role-permissions/
/api/v1/identity/user-roles/

# organization
/api/v1/organization/departments/
/api/v1/organization/companies/

# employees
/api/v1/employees/
/api/v1/employees/family-members/
/api/v1/employees/academic-records/
/api/v1/employees/certifications/

# contracts
/api/v1/contracts/
/api/v1/contracts/amendments/
/api/v1/contracts/employment-data/

# documents
/api/v1/documents/digital/
/api/v1/documents/generate-contract/
/api/v1/documents/generate-amendment/
/api/v1/documents/generate-certificate/

# payroll
/api/v1/payroll/monthly-runs/
/api/v1/payroll/details/
/api/v1/payroll/concepts/
/api/v1/payroll/mass-deductions/
/api/v1/payroll/payslips/
/api/v1/payroll/payment-schedules/
/api/v1/payroll/afp-configurations/
/api/v1/payroll/tax-parameters/
/api/v1/payroll/compensation-configurations/

# time-off
/api/v1/time-off/configurations/
/api/v1/time-off/periods/
/api/v1/time-off/requests/
/api/v1/time-off/grants/
/api/v1/time-off/history/

# onboarding
/api/v1/onboarding/processes/
```

**No se tocan:** `/api/v1/auth/`, `/api/v1/rrhh/...` (legacy), `/api/v1/vacaciones/...` (legacy), `/api/docs/`, `/api/schema/`.

**`/api/v1/employees/family-members/` vs nested `/api/v1/employees/<id>/family-members/`:** El plan usa **flat URL** (`/family-members/`) porque los viewsets actuales no usan nested routes (DRF nested routers requeriría refactor mayor). Filtros por empleado se hacen via query param `?empleado=<id>` (mismo patrón actual).

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/api/v1/identity/__init__.py` | empty |
| Create | `apps/api/api/v1/identity/urls.py` | registra viewsets de identity con basename `*-en` |
| Create | `apps/api/api/v1/organization/__init__.py` | empty |
| Create | `apps/api/api/v1/organization/urls.py` | |
| Create | `apps/api/api/v1/employees/__init__.py` | empty |
| Create | `apps/api/api/v1/employees/urls.py` | |
| Create | `apps/api/api/v1/contracts/__init__.py` | empty |
| Create | `apps/api/api/v1/contracts/urls.py` | |
| Create | `apps/api/api/v1/documents/__init__.py` | empty |
| Create | `apps/api/api/v1/documents/urls.py` | |
| Create | `apps/api/api/v1/payroll/__init__.py` | empty |
| Create | `apps/api/api/v1/payroll/urls.py` | |
| Create | `apps/api/api/v1/time_off/__init__.py` | empty (notar: `time_off` con underscore, URL prefix es `time-off`) |
| Create | `apps/api/api/v1/time_off/urls.py` | |
| Create | `apps/api/api/v1/onboarding/__init__.py` | empty |
| Create | `apps/api/api/v1/onboarding/urls.py` | |
| Modify | `apps/api/api/v1/urls.py` | include() de los nuevos app urls |

**NO se toca en L3.10.4a:**
- ViewSets (siguen donde están: `api/v1/rrhh/views.py`, `contratos_views.py`, etc.)
- Serializers
- Modelos
- Frontend
- URLs legacy `/api/v1/rrhh/...` (siguen funcionando)
- `vyntia/urls.py` (root config)

**`basename` strategy:** Los nuevos routers usan basenames con sufijo `-en` para evitar collision con los basenames legacy. Ejemplo:
- Legacy: `router.register(r'empleados', EmpleadoViewSet, basename='empleado')` → URL name `empleado-list`
- Nuevo: `router.register(r'', EmpleadoViewSet, basename='employee')` → URL name `employee-list`

Así `reverse('rrhh:empleado-list')` y `reverse('api_v1:employees:employee-list')` ambos funcionan.

---

## Definition of Done

- [ ] 8 nuevos directorios creados en `apps/api/api/v1/{identity,organization,employees,contracts,documents,payroll,time_off,onboarding}/`
- [ ] 8 archivos `urls.py` nuevos con DefaultRouter registrando los viewsets existentes
- [ ] `apps/api/api/v1/urls.py` actualizado para incluir todos los nuevos paths
- [ ] URLs legacy `/api/v1/rrhh/...` siguen funcionando (no se tocan)
- [ ] URLs nuevas `/api/v1/{app}/...` responden HTTP 200 (con auth) o 401 (sin auth)
- [ ] `python manage.py check` clean
- [ ] `pytest`: 161 passed, 8 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200; nuevas URLs aparecen en schema
- [ ] Branch `vyntia/L3.10.4a-backend-url-refactor` mergeada a master con `--no-ff`
- [ ] Roadmap + memory actualizados — L3.10.4a ✅, L3.10.4b NEXT

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd, master limpio post-L3.10.3**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -5
```

Expected: HEAD = `51d6ecd4 docs(L3.10.3): mark L3.10.3 merged, L3.10.4 (frontend rename) as next` o más reciente. `git status` shows ONLY plan file untracked.

- [ ] **Step 2: Activar venv y confirmar Django**

```bash
source D:/VYNTIA/.venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `5.2.13`.

- [ ] **Step 3: Confirmar baseline pytest**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped`.

- [ ] **Step 4: Snapshot of current legacy URLs**

```bash
cd D:/VYNTIA/apps/api
echo "=== Current registered URL paths under /api/v1/rrhh/ ==="
python manage.py show_urls 2>/dev/null | grep "/api/v1/rrhh/" | head -40 || \
  grep -E "router.register" api/v1/rrhh/urls.py
cd D:/VYNTIA
```

Save list for verification post-refactor.

- [ ] **Step 5: Crear branch L3.10.4a**

```bash
git checkout -b vyntia/L3.10.4a-backend-url-refactor
git status --short
```

---

## Task 2: Comitear el plan

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-27-vyntia-foundation-L3.10.4a-backend-url-refactor.md
git commit -m "docs(L3.10.4a): add backend URL refactor plan (English paths in parallel)"
```

---

## Task 3: Create `api/v1/identity/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/identity
touch api/v1/identity/__init__.py
```

Use Write tool to create `apps/api/api/v1/identity/urls.py`:

```python
"""URLs for identity bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    ModulosViewSet,
    PermisoViewSet,
    RolPermisosViewSet,
    RolViewSet,
    UsuarioViewSet,
)
from api.v1.rrhh.usuario_roles_views import UsuarioRolesViewSet

app_name = "identity"

router = DefaultRouter()
router.register(r"users", UsuarioViewSet, basename="user")
router.register(r"roles", RolViewSet, basename="role")
router.register(r"permissions", PermisoViewSet, basename="permission")
router.register(r"modules", ModulosViewSet, basename="module")
router.register(r"role-permissions", RolPermisosViewSet, basename="role-permission")
router.register(r"user-roles", UsuarioRolesViewSet, basename="user-role")

urlpatterns = [
    path("", include(router.urls)),
]
```

Note: ViewSet class names still match L3.10.1 state — `UsuarioViewSet`, `RolViewSet`, etc. — these classes in `api/v1/rrhh/views.py` were NOT renamed (only the model classes inside were renamed). The viewsets keep their Spanish names; only the URL paths change.

Verify:
```bash
grep -nE "router.register" D:/VYNTIA/apps/api/api/v1/identity/urls.py
```

---

## Task 4: Create `api/v1/organization/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/organization
touch api/v1/organization/__init__.py
```

Use Write tool to create `apps/api/api/v1/organization/urls.py`:

```python
"""URLs for organization bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    AreaViewSet,
    ConfiguracionEmpresaViewSet,
)

app_name = "organization"

router = DefaultRouter()
router.register(r"departments", AreaViewSet, basename="department")
router.register(r"companies", ConfiguracionEmpresaViewSet, basename="company")

urlpatterns = [
    path("", include(router.urls)),
]
```

---

## Task 5: Create `api/v1/employees/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/employees
touch api/v1/employees/__init__.py
```

Use Write tool to create `apps/api/api/v1/employees/urls.py`:

```python
"""URLs for employees bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    CursosCertificacionesViewSet,
    DatosAcademicosViewSet,
    DatosFamiliaresViewSet,
    EmpleadoViewSet,
)

app_name = "employees"

router = DefaultRouter()
router.register(r"", EmpleadoViewSet, basename="employee")
router.register(r"family-members", DatosFamiliaresViewSet, basename="family-member")
router.register(r"academic-records", DatosAcademicosViewSet, basename="academic-record")
router.register(r"certifications", CursosCertificacionesViewSet, basename="certification")

urlpatterns = [
    path("", include(router.urls)),
]
```

**Note:** `r""` registration with `r"family-members"`, etc. in same router will collide on `/list` URL. Need to inspect — the `EmpleadoViewSet` registered at `r""` makes the prefix `/api/v1/employees/`. Then `family-members` would be `/api/v1/employees/family-members/`. That's a sub-path, not nested. DRF DefaultRouter might generate conflicting URL patterns.

If collision occurs at runtime (router throws "ImproperlyConfigured"), separate the EmpleadoViewSet registration into its own router or use prefix `r"list"` etc. — but that's ugly.

**Alternative:** put `EmpleadoViewSet` at root path `/api/v1/employees/` and the others at `/api/v1/employees/family-members/`, etc. — but DRF nests them as sub-paths under the empty-prefix viewset, which causes URL conflicts because EmpleadoViewSet's `<pk>` URL pattern catches `family-members` as a PK.

**Workaround:** put EmpleadoViewSet on a separate URL conf, OR use `r"list"` prefix, OR accept the collision and use plural URL only:

Better approach — put `EmpleadoViewSet` at separate path, family/academic/cert as siblings:

```python
router.register(r"employees", EmpleadoViewSet, basename="employee")
router.register(r"family-members", DatosFamiliaresViewSet, basename="family-member")
router.register(r"academic-records", DatosAcademicosViewSet, basename="academic-record")
router.register(r"certifications", CursosCertificacionesViewSet, basename="certification")
```

And include this router at `/api/v1/` (not `/api/v1/employees/`). Then URLs become:
- `/api/v1/employees/`
- `/api/v1/family-members/`
- `/api/v1/academic-records/`
- `/api/v1/certifications/`

This deviates from § 3.4 (which has nested `/api/v1/employees/<id>/family-members/`) but is simpler and avoids router conflicts. Document this deviation in the spec.

**Decision for this plan:** Use the simpler flat approach. Update the file content to:

```python
"""URLs for employees bounded context — English paths per spec § 3.4 (flat, not nested)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    CursosCertificacionesViewSet,
    DatosAcademicosViewSet,
    DatosFamiliaresViewSet,
    EmpleadoViewSet,
)

app_name = "employees"

router = DefaultRouter()
router.register(r"employees", EmpleadoViewSet, basename="employee")
router.register(r"family-members", DatosFamiliaresViewSet, basename="family-member")
router.register(r"academic-records", DatosAcademicosViewSet, basename="academic-record")
router.register(r"certifications", CursosCertificacionesViewSet, basename="certification")

urlpatterns = [
    path("", include(router.urls)),
]
```

This is included at `/api/v1/` (not `/api/v1/employees/`). Same pattern for other apps with multiple viewsets.

**Update file content to the version above.**

---

## Task 6: Create `api/v1/contracts/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/contracts
touch api/v1/contracts/__init__.py
```

Use Write tool to create `apps/api/api/v1/contracts/urls.py`:

```python
"""URLs for contracts bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.contratos_views import (
    ContractAmendmentViewSet,
    ContratosAdendasViewSet,
)
from api.v1.rrhh.views import DatosLaboralesViewSet

app_name = "contracts"

router = DefaultRouter()
router.register(r"contracts", ContratosAdendasViewSet, basename="contract")
router.register(r"contract-amendments", ContractAmendmentViewSet, basename="contract-amendment-en")
router.register(r"employment-data", DatosLaboralesViewSet, basename="employment-data")

urlpatterns = [
    path("", include(router.urls)),
]
```

**Note:** `basename="contract-amendment-en"` to avoid collision with legacy `basename='contract-amendment'` registered in `api/v1/rrhh/urls.py` (Task added in L3.10.3 Batch 4).

---

## Task 7: Create `api/v1/documents/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/documents
touch api/v1/documents/__init__.py
```

Use Write tool to create `apps/api/api/v1/documents/urls.py`:

```python
"""URLs for documents bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import DocumentosDigitalesViewSet

app_name = "documents"

router = DefaultRouter()
router.register(r"documents", DocumentosDigitalesViewSet, basename="document")

urlpatterns = [
    path("", include(router.urls)),
    # Document generation endpoints (function-based views) keep existing URL conf
    path("documents/", include("api.v1.app_rrhh.document_generation_urls")),
]
```

**Note:** The document generation function-based views are in a separate URL conf at `api/v1/app_rrhh/document_generation_urls.py` and currently mounted at `/api/v1/rrhh/documentos/`. We re-mount them at `/api/v1/documents/` (without changing the conf file itself).

---

## Task 8: Create `api/v1/payroll/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/payroll
touch api/v1/payroll/__init__.py
```

Use Write tool to create `apps/api/api/v1/payroll/urls.py`:

```python
"""URLs for payroll bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.remuneraciones_views import (
    BoletaPagoViewSet,
    CalendarioPagoViewSet,
    ConfiguracionAfpViewSet,
    ConfiguracionRemuneracionViewSet,
    ConfiguracionUitViewSet,
    DescuentoMasivoViewSet,
    DetallePlanillaViewSet,
    PlanillaMensualViewSet,
)

app_name = "payroll"

router = DefaultRouter()
router.register(r"monthly-runs", PlanillaMensualViewSet, basename="monthly-run")
router.register(r"details", DetallePlanillaViewSet, basename="payroll-detail")
router.register(r"mass-deductions", DescuentoMasivoViewSet, basename="mass-deduction")
router.register(r"payslips", BoletaPagoViewSet, basename="payslip")
router.register(r"payment-schedules", CalendarioPagoViewSet, basename="payment-schedule")
router.register(r"afp-configurations", ConfiguracionAfpViewSet, basename="afp-configuration")
router.register(r"tax-parameters", ConfiguracionUitViewSet, basename="tax-parameter")
router.register(r"compensation-configurations", ConfiguracionRemuneracionViewSet, basename="compensation-configuration")

urlpatterns = [
    path("", include(router.urls)),
]
```

**Note:** The legacy basenames in `api/v1/rrhh/urls.py` are `'planilla-mensual'`, `'detalle-planilla'`, etc. The new basenames here use English names without collision.

---

## Task 9: Create `api/v1/time_off/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/time_off
touch api/v1/time_off/__init__.py
```

**Find existing vacaciones URL conf:**

```bash
cat D:/VYNTIA/apps/api/api/v1/vacaciones/urls.py | head -40
```

The file imports viewsets from `api/v1/vacaciones/views.py`. We replicate the registrations under English paths.

Use Write tool to create `apps/api/api/v1/time_off/urls.py`. Read the source file first to see the exact viewsets imported and their basename. Replicate with English-translated path names.

Generic structure (adjust based on actual viewsets in vacaciones/views.py):

```python
"""URLs for time-off bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Import viewsets from existing vacaciones module (preserve original location)
from api.v1.vacaciones.views import (
    ConfiguracionVacacionesViewSet,
    GoceVacacionesViewSet,
    HistorialSolicitudVacacionesViewSet,
    PeriodoVacacionalViewSet,
    SolicitudVacacionesViewSet,
)

app_name = "time_off"

router = DefaultRouter()
router.register(r"configurations", ConfiguracionVacacionesViewSet, basename="vacation-configuration")
router.register(r"periods", PeriodoVacacionalViewSet, basename="vacation-period")
router.register(r"requests", SolicitudVacacionesViewSet, basename="vacation-request-en")
router.register(r"grants", GoceVacacionesViewSet, basename="vacation-grant")
router.register(r"history", HistorialSolicitudVacacionesViewSet, basename="vacation-request-history")

urlpatterns = [
    path("", include(router.urls)),
]
```

**Adjust the imports to match the actual viewsets in `api/v1/vacaciones/views.py`.** Read it first.

---

## Task 10: Create `api/v1/onboarding/urls.py`

```bash
cd D:/VYNTIA/apps/api
mkdir -p api/v1/onboarding
touch api/v1/onboarding/__init__.py
```

Use Write tool to create `apps/api/api/v1/onboarding/urls.py`:

```python
"""URLs for onboarding bounded context — English paths per spec § 3.4 (flat)."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import OnboardingViewSet

app_name = "onboarding"

router = DefaultRouter()
router.register(r"processes", OnboardingViewSet, basename="onboarding-process")

urlpatterns = [
    path("", include(router.urls)),
]
```

---

## Task 11: Update `api/v1/urls.py` root config

Read current state:

```bash
cat D:/VYNTIA/apps/api/api/v1/urls.py
```

Current content (likely):
```python
"""URLs principales para API v1."""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('rrhh/', include('api.v1.rrhh.urls')),
    path('vacaciones/', include('api.v1.vacaciones.urls')),
]
```

Use Edit tool to update with new app includes:

```python
"""URLs principales para API v1.

Estructura:
- /api/v1/auth/        - autenticación (legacy + canonical)
- /api/v1/rrhh/...     - LEGACY URLs (preservadas hasta L3.11)
- /api/v1/vacaciones/  - LEGACY URLs (preservadas hasta L3.11)
- /api/v1/identity/    - NUEVO (English path) per spec § 3.4
- /api/v1/organization/ - NUEVO
- /api/v1/employees/, /family-members/, /academic-records/, /certifications/ - NUEVO (flat under /api/v1/)
- /api/v1/contracts/, /contract-amendments/, /employment-data/ - NUEVO (flat under /api/v1/)
- /api/v1/documents/   - NUEVO
- /api/v1/payroll/     - NUEVO
- /api/v1/time-off/    - NUEVO
- /api/v1/onboarding/  - NUEVO
"""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication
    path('auth/', include('api.v1.auth.urls')),

    # Legacy URLs (Spanish paths) — preserved until L3.11 cleanup
    path('rrhh/', include('api.v1.rrhh.urls')),
    path('vacaciones/', include('api.v1.vacaciones.urls')),

    # New canonical URLs (English paths) per spec § 3.4
    path('identity/', include('api.v1.identity.urls')),
    path('organization/', include('api.v1.organization.urls')),
    path('', include('api.v1.employees.urls')),     # /api/v1/employees/, /family-members/, /academic-records/, /certifications/
    path('', include('api.v1.contracts.urls')),     # /api/v1/contracts/, /contract-amendments/, /employment-data/
    path('documents/', include('api.v1.documents.urls')),
    path('payroll/', include('api.v1.payroll.urls')),
    path('time-off/', include('api.v1.time_off.urls')),
    path('onboarding/', include('api.v1.onboarding.urls')),
]
```

**Note on `path('', include(...))`:** For employees and contracts apps, the registered URL prefixes `r"employees"`, `r"family-members"`, etc. already include the resource name. So we mount their app urls at root `/api/v1/`.

For other apps where the prefix is e.g. `r"users"` and we want it at `/api/v1/identity/users/`, we mount at `/api/v1/identity/`.

---

## Task 12: Smoke tests

### Step 1: Django check

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -10
cd D:/VYNTIA
```

Expected: `System check identified no issues (0 silenced).`

If errors:
- "Reverse for 'X' not found" → basename collision; rename one of them
- "ImproperlyConfigured: A url path can't have both" → router conflict; check Task 5/6 employees/contracts root mount
- ImportError → check that the viewset is exported from the source module

### Step 2: pytest

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

Expected: `161 passed, 8 failed, 3 skipped` (baseline preservado).

### Step 3: runserver smoke test — verify legacy + new URLs both work

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l3104a.log 2>&1 &
SERVER_PID=$!
sleep 10

echo "=== Legacy URLs (should work) ==="
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/rrhh/empleados/\n" http://127.0.0.1:8000/api/v1/rrhh/empleados/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/rrhh/contratos-adendas/\n" http://127.0.0.1:8000/api/v1/rrhh/contratos-adendas/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/rrhh/usuarios/\n" http://127.0.0.1:8000/api/v1/rrhh/usuarios/

echo ""
echo "=== New URLs (should work) ==="
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/employees/\n" http://127.0.0.1:8000/api/v1/employees/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/contracts/\n" http://127.0.0.1:8000/api/v1/contracts/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/contract-amendments/\n" http://127.0.0.1:8000/api/v1/contract-amendments/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/identity/users/\n" http://127.0.0.1:8000/api/v1/identity/users/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/identity/roles/\n" http://127.0.0.1:8000/api/v1/identity/roles/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/organization/departments/\n" http://127.0.0.1:8000/api/v1/organization/departments/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/payroll/monthly-runs/\n" http://127.0.0.1:8000/api/v1/payroll/monthly-runs/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/time-off/requests/\n" http://127.0.0.1:8000/api/v1/time-off/requests/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/onboarding/processes/\n" http://127.0.0.1:8000/api/v1/onboarding/processes/
curl -s -o /dev/null -w "HTTP %{http_code} /api/v1/documents/documents/\n" http://127.0.0.1:8000/api/v1/documents/documents/

kill $SERVER_PID 2>/dev/null
sleep 1
cd D:/VYNTIA
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected:
- Legacy: HTTP 401 (auth required) for protected endpoints, 200 for /api/docs/
- New: HTTP 401 (auth required) for protected endpoints, NOT 404

If any new URL returns 404, that endpoint isn't registered correctly. Investigate.

### Step 4: Verify schema includes new URLs

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_schema.log 2>&1 &
SERVER_PID=$!
sleep 10
curl -s http://127.0.0.1:8000/api/schema/ | grep -oE "'/api/v1/[^']+'" | sort -u | head -40
kill $SERVER_PID 2>/dev/null
sleep 1
cd D:/VYNTIA
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: schema includes both `/api/v1/rrhh/...` (legacy) and `/api/v1/{app}/...` (new) paths.

---

## Task 13: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -20
git add apps/api/
git commit -m "$(cat <<'EOF'
chore(L3.10.4a): backend URL refactor — English paths per spec § 3.4

Adds new English URL paths in parallel to legacy Spanish ones. Same ViewSets
(no logic changes), new basename suffixes to avoid reverse-URL collision.

New URL configs (8 apps):
- /api/v1/identity/{users,roles,permissions,modules,role-permissions,user-roles}/
- /api/v1/organization/{departments,companies}/
- /api/v1/{employees,family-members,academic-records,certifications}/
- /api/v1/{contracts,contract-amendments,employment-data}/
- /api/v1/documents/{documents,generate-contract,generate-amendment,generate-certificate}/
- /api/v1/payroll/{monthly-runs,details,mass-deductions,payslips,payment-schedules,afp-configurations,tax-parameters,compensation-configurations}/
- /api/v1/time-off/{configurations,periods,requests,grants,history}/
- /api/v1/onboarding/processes/

Legacy URLs preserved (Spanish paths under /api/v1/rrhh/ and /api/v1/vacaciones/)
— removed in L3.11 once frontend has migrated.

Files added:
- 8 new directories: api/v1/{identity,organization,employees,contracts,documents,payroll,time_off,onboarding}/
- Each with __init__.py and urls.py
- api/v1/urls.py updated to include all new app URL configs

manage.py check clean. pytest baseline 161/8/3 preserved. /api/docs/ HTTP 200.
All new URLs respond 401 (auth required) — endpoints registered correctly.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

Verify:
```bash
git log --oneline vyntia/L3.10.4a-backend-url-refactor ^master
git status --short
```

Expected: 2 commits (`docs(L3.10.4a) plan`, `chore(L3.10.4a)`), `git status` clean.

---

## Task 14: Merge a master + roadmap update

- [ ] **Confirmar autorización del usuario.**

```bash
git checkout master
git merge --no-ff vyntia/L3.10.4a-backend-url-refactor -m "Merge L3.10.4a: backend URL refactor (English paths in parallel)"
git log --oneline -5
```

Post-merge smoke:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
PGPASSWORD='Demenci4@' pytest --tb=no -q 2>&1 | tail -3
cd D:/VYNTIA
```

### Update roadmap

Edit `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md`:
- L3.10.4 → split en L3.10.4a ✅ + L3.10.4b ⏳ NEXT
- Document the rationale (URL refactor done; frontend rename next)

Update memory `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- L3.10.4a ✅ merged
- Next: L3.10.4b

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.10.4a): mark L3.10.4a merged, L3.10.4b (frontend rename) as next"
```

---

## Después de L3.10.4a

**Próximo plan:** L3.10.4b — frontend rename. Frontend ahora puede consumir las URLs nuevas en inglés:
- 14 services TS en `apps/web/src/services/` actualizan URL constants a `/api/v1/employees/`, `/api/v1/contracts/`, etc.
- Renombrar archivos service donde el dominio es renombrado (`contratosService.ts` → `contractsService.ts`)
- TS interfaces: `empleado_id: number` → `id: string` UUID, `fecha_creacion → created_at`
- 50+ component refs a campos individuales
- 366 frontend refs identificadas pre-L3.10.2

Después L3.11 (cleanup `app_rrhh/` carpeta vacía + remover URLs legacy + dead-code refs).

---

## Notas para el ejecutor

- **Backend-only refactor** — frontend no se toca aquí.
- **Legacy URLs preservadas** — frontend sigue funcionando con `/api/v1/rrhh/...` hasta que L3.10.4b lo migre.
- **Basenames con sufijo `-en` o nombre EN distinto** — previenen collision con basenames legacy.
- **Function-based document generation views** se re-mount sin renombrar el archivo de URL conf.
- **`path('', include(...))` para employees y contracts** — sus URL configs registran prefijos `r"employees"`, `r"contracts"`, etc. ya completos, así que se incluyen en root `/api/v1/`.
- **Vacaciones legacy `/api/v1/vacaciones/`** queda separado del nuevo `/api/v1/time-off/` — ambos funcionan.
- **drf-spectacular schema** auto-detecta los nuevos URL paths y los expone en `/api/docs/` y `/api/schema/` — útil para frontend regenerar tipos en L3.10.4b.
- **Riesgo bajo** — solo agrega URL aliases, no toca lógica.
