# L5 — Foundation Cleanup Final

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove all remaining `app_rrhh` code from the active codebase by relocating its active modules to proper bounded-context apps; clean up frontend stragglers (`pages/`, `hooks/`, `context/`); rewrite stale CI workflows; and create the two missing spec-required docs — leaving Foundation sub-project A complete.

**Architecture:** Three sub-PRs executed sequentially: L5.1 (backend module relocation), L5.2 (frontend cleanup), L5.3 (CI + docs + final DoD audit). Each sub-PR ends with a `manage.py check` + `pytest` or `npm run build` + `npm test` gate before merge.

**Tech Stack:** Django 5.2 + DRF, React 18 + Vite + TypeScript, GitHub Actions, pytest 161/8/3 baseline, vitest 7 baseline, tsc 1 pre-existing error (BlankEnum.ts), lint 634 warnings baseline.

---

## Baseline snapshot (must be preserved or improved at every commit)

| Check | Command | Expected |
|---|---|---|
| Django system | `cd apps/api && python manage.py check --settings=vyntia.settings.development` | No errors |
| Backend tests | `cd apps/api && pytest` | 161 passed / 8 failed / 3 skipped |
| Frontend build | `cd apps/web && npm run build` | Exit 0, ~8-9 s |
| Frontend types | `cd apps/web && npx tsc --noEmit -p tsconfig.app.json` | 1 error (BlankEnum.ts — pre-existing) |
| Frontend tests | `cd apps/web && npm test -- --run` | 7 passed |

---

## Sub-PR L5.1 — Backend: Relocate `app_rrhh` active modules

Branch: `vyntia/L5.1-backend-app-rrhh-relocation`

**Files to create:**
- `apps/api/apps/core/constants.py`
- `apps/api/apps/core/permission_service.py`
- `apps/api/apps/core/tasks.py`
- `apps/api/apps/identity/services/__init__.py`
- `apps/api/apps/identity/services/menu_service.py`
- `apps/api/apps/time_off/validators.py`
- `apps/api/apps/employees/services/__init__.py`
- `apps/api/apps/employees/services/employee_report_service.py`
- `apps/api/apps/identity/management/__init__.py`
- `apps/api/apps/identity/management/commands/__init__.py`
- `apps/api/apps/identity/management/commands/seed_menu.py`
- `apps/api/apps/identity/management/commands/setup_roles_permisos.py`
- `apps/api/apps/identity/management/commands/audit_rbac.py`
- `apps/api/apps/documents/management/__init__.py`
- `apps/api/apps/documents/management/commands/__init__.py`
- `apps/api/apps/documents/management/commands/seed_plantillas_default.py`
- `apps/api/apps/payroll/management/__init__.py`
- `apps/api/apps/payroll/management/commands/__init__.py`
- `apps/api/apps/payroll/management/commands/seed_remuneraciones_config.py`

**Files to modify:**
- `apps/api/apps/core/decorators.py` — update 2 imports
- `apps/api/apps/core/permissions.py` — update 2 imports
- `apps/api/apps/time_off/services/vacation_approval_service.py` — update 2 imports
- `apps/api/api/v1/vacaciones/permissions.py` — update 2 imports
- `apps/api/api/v1/vacaciones/validators.py` — update 1 import
- `apps/api/api/v1/auth/views.py` — update 1 import
- `apps/api/apps/onboarding/services/onboarding_service.py` — update 1 import
- `apps/api/apps/time_off/services/vacation_service.py` — update 1 import
- `apps/api/api/v1/rrhh/views.py` — remove dead `from app_rrhh import services`, implement inline ORM replacements, fix 2 EmpleadoReportService imports
- `apps/api/vyntia/settings/base.py` — remove `app_rrhh` from LOCAL_APPS + LOGGING
- `apps/api/pyproject.toml` — remove `app_rrhh` from packages list

**Files to delete:** entire `apps/api/app_rrhh/` directory

---

### Task 1: Relocate `constants.py` → `apps/core/constants.py`

**Files:**
- Create: `apps/api/apps/core/constants.py`
- Modify: `apps/api/apps/core/decorators.py`
- Modify: `apps/api/apps/core/permissions.py`
- Modify: `apps/api/apps/time_off/services/vacation_approval_service.py`
- Modify: `apps/api/api/v1/vacaciones/permissions.py`

- [ ] **Step 1.1: Create `apps/core/constants.py` with identical content**

```python
# apps/api/apps/core/constants.py
"""Role and permission constants — avoid magic strings in authorization code."""


class Roles:
    SUPER_ADMIN = "Super Administrador"
    ADMIN_RRHH = "Administrador RRHH"
    JEFE_AREA = "Jefe de Area"
    ANALISTA_RRHH = "Analista RRHH"
    EMPLEADO = "Empleado"

    ADMIN_ROLES = [SUPER_ADMIN, ADMIN_RRHH]
    HR_ROLES = [SUPER_ADMIN, ADMIN_RRHH, ANALISTA_RRHH, JEFE_AREA]
    MANAGER_ROLES = [SUPER_ADMIN, ADMIN_RRHH, JEFE_AREA]
    EMPLOYEE_ROLES = [EMPLEADO, ANALISTA_RRHH, JEFE_AREA, ADMIN_RRHH, SUPER_ADMIN]


class Permissions:
    # Dashboard
    VIEW_DASHBOARD = "ver_dashboard"
    VIEW_DASHBOARD_STATS = "ver_estadisticas_dashboard"

    # Empleados
    VIEW_EMPLOYEES = "ver_empleados"
    CREATE_EMPLOYEE = "crear_empleado"
    EDIT_EMPLOYEE = "editar_empleado"
    DELETE_EMPLOYEE = "eliminar_empleado"
    EXPORT_EMPLOYEES = "exportar_empleados"
    VIEW_OWN_DATA = "ver_datos_propios"
    EDIT_OWN_DATA = "editar_datos_propios"

    # Vacaciones
    VIEW_VACATIONS = "ver_solicitudes_vacaciones"
    CREATE_VACATION = "crear_solicitud_vacaciones"
    APPROVE_VACATION = "aprobar_solicitud_vacaciones"
    ADMIN_VACATION_PERIODS = "administrar_periodos_vacaciones"
    CONFIG_VACATION_MODULE = "configurar_modulo_vacaciones"

    # Administracion
    MANAGE_USERS = "gestionar_usuarios"
    MANAGE_ROLES = "gestionar_roles"
    MANAGE_PERMISSIONS = "gestionar_permisos"
    MANAGE_MODULES = "gestionar_modulos"

    # Reportes
    VIEW_REPORTS = "ver_reportes"
    EXPORT_REPORTS = "exportar_reportes"
```

- [ ] **Step 1.2: Update 4 import sites** — replace `from app_rrhh.constants import` with `from apps.core.constants import`:

In `apps/api/apps/core/decorators.py` line ~6:
```python
# Before:
from app_rrhh.constants import Roles
# After:
from apps.core.constants import Roles
```

In `apps/api/apps/core/permissions.py` line ~5:
```python
# Before:
from app_rrhh.constants import Roles
# After:
from apps.core.constants import Roles
```

In `apps/api/apps/time_off/services/vacation_approval_service.py` line ~6:
```python
# Before:
from app_rrhh.constants import Roles
# After:
from apps.core.constants import Roles
```

In `apps/api/api/v1/vacaciones/permissions.py` line ~3:
```python
# Before:
from app_rrhh.constants import Roles
# After:
from apps.core.constants import Roles
```

- [ ] **Step 1.3: Run Django system check**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
```

Expected: No errors (app_rrhh.constants still exists, so the old module is still importable — this step just verifies the new one works)

- [ ] **Step 1.4: Commit**

```bash
git add apps/api/apps/core/constants.py \
        apps/api/apps/core/decorators.py \
        apps/api/apps/core/permissions.py \
        apps/api/apps/time_off/services/vacation_approval_service.py \
        apps/api/api/v1/vacaciones/permissions.py
git commit -m "chore(L5.1): relocate constants.py from app_rrhh → apps/core"
```

---

### Task 2: Relocate `permission_service.py` → `apps/core/permission_service.py`

**Files:**
- Create: `apps/api/apps/core/permission_service.py`
- Modify: `apps/api/apps/core/decorators.py`
- Modify: `apps/api/apps/core/permissions.py`
- Modify: `apps/api/apps/time_off/services/vacation_approval_service.py`
- Modify: `apps/api/api/v1/vacaciones/permissions.py`
- Modify: `apps/api/app_rrhh/menu_service.py` (temp — will be moved in Task 4)

- [ ] **Step 2.1: Create `apps/core/permission_service.py`**

```python
# apps/api/apps/core/permission_service.py
"""Centralized service for role and permission checks."""

from typing import Iterable, Set

from apps.core.constants import Roles


class PermissionService:
    """Single source of truth for authorization checks."""

    @staticmethod
    def get_user_role_names(usuario) -> Set[str]:
        if not usuario or not getattr(usuario, "is_authenticated", False):
            return set()
        return {rol.nombre_rol for rol in usuario.roles_activos()}

    @staticmethod
    def get_user_permission_names(usuario) -> Set[str]:
        if not usuario or not getattr(usuario, "is_authenticated", False):
            return set()
        permisos = usuario.permisos_activos()
        if permisos == "*":
            return {"*"}
        if hasattr(permisos, "values_list"):
            return set(permisos.values_list("nombre_permiso", flat=True))
        return set()

    @staticmethod
    def is_super_admin(usuario) -> bool:
        if not usuario:
            return False
        if getattr(usuario, "is_superuser", False):
            return True
        return Roles.SUPER_ADMIN in PermissionService.get_user_role_names(usuario)

    @staticmethod
    def has_any_role(usuario, required_roles: Iterable[str]) -> bool:
        if PermissionService.is_super_admin(usuario):
            return True
        user_roles = PermissionService.get_user_role_names(usuario)
        return any(role in user_roles for role in required_roles)

    @staticmethod
    def has_any_permission(usuario, required_permissions: Iterable[str]) -> bool:
        if PermissionService.is_super_admin(usuario):
            return True
        user_permissions = PermissionService.get_user_permission_names(usuario)
        return any(perm in user_permissions for perm in required_permissions)
```

- [ ] **Step 2.2: Update 5 import sites** — replace `from app_rrhh.permission_service import PermissionService` with `from apps.core.permission_service import PermissionService`:

Files to update (replace the import line in each):
- `apps/api/apps/core/decorators.py`
- `apps/api/apps/core/permissions.py`
- `apps/api/apps/time_off/services/vacation_approval_service.py`
- `apps/api/api/v1/vacaciones/permissions.py`
- `apps/api/app_rrhh/menu_service.py` (temp — file moves in Task 4)

- [ ] **Step 2.3: Run check + tests**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, pytest 161/8/3.

- [ ] **Step 2.4: Commit**

```bash
git add apps/api/apps/core/permission_service.py \
        apps/api/apps/core/decorators.py \
        apps/api/apps/core/permissions.py \
        apps/api/apps/time_off/services/vacation_approval_service.py \
        apps/api/api/v1/vacaciones/permissions.py \
        apps/api/app_rrhh/menu_service.py
git commit -m "chore(L5.1): relocate permission_service.py from app_rrhh → apps/core"
```

---

### Task 3: Relocate `tasks.py` → `apps/core/tasks.py`

**Files:**
- Create: `apps/api/apps/core/tasks.py`
- Modify: `apps/api/apps/onboarding/services/onboarding_service.py`
- Modify: `apps/api/apps/time_off/services/vacation_service.py`

- [ ] **Step 3.1: Create `apps/core/tasks.py`**

```python
# apps/api/apps/core/tasks.py
"""Cross-cutting Celery tasks (email, notifications)."""

import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_html_task(self, subject, from_email, recipients, text_content, html_content):
    """Send HTML email asynchronously with retry on failure."""
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Email sent successfully to %s", recipients)
    except Exception as exc:
        logger.error("Error sending email to %s: %s", recipients, exc)
        raise self.retry(exc=exc, countdown=60)
```

- [ ] **Step 3.2: Update 2 import sites**

In `apps/api/apps/onboarding/services/onboarding_service.py` line ~10:
```python
# Before:
from app_rrhh.tasks import send_email_html_task
# After:
from apps.core.tasks import send_email_html_task
```

In `apps/api/apps/time_off/services/vacation_service.py` line ~16:
```python
# Before:
from app_rrhh.tasks import send_email_html_task
# After:
from apps.core.tasks import send_email_html_task
```

- [ ] **Step 3.3: Run check + tests**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, 161/8/3.

- [ ] **Step 3.4: Commit**

```bash
git add apps/api/apps/core/tasks.py \
        apps/api/apps/onboarding/services/onboarding_service.py \
        apps/api/apps/time_off/services/vacation_service.py
git commit -m "chore(L5.1): relocate tasks.py from app_rrhh → apps/core"
```

---

### Task 4: Relocate `menu_service.py` → `apps/identity/services/menu_service.py`

**Files:**
- Create: `apps/api/apps/identity/services/__init__.py`
- Create: `apps/api/apps/identity/services/menu_service.py`
- Modify: `apps/api/api/v1/auth/views.py`

- [ ] **Step 4.1: Create `apps/identity/services/__init__.py`**

```python
# apps/api/apps/identity/services/__init__.py
```

(empty — Python package marker)

- [ ] **Step 4.2: Create `apps/identity/services/menu_service.py`**

Copy verbatim from `app_rrhh/menu_service.py`, updating only the import:

```python
# apps/api/apps/identity/services/menu_service.py
"""Menu service — builds permission-filtered navigation tree from DB."""

from typing import Any, Dict, List, Optional, Set

from apps.core.permission_service import PermissionService
from apps.identity.models import Module
from django.db.models import Prefetch


class MenuService:
    """Builds dynamic menu from DB filtered by user permissions."""

    @staticmethod
    def get_menu_for_user(usuario) -> List[Dict[str, Any]]:
        """Return visible menu for an authenticated user."""
        is_super_admin = PermissionService.is_super_admin(usuario)
        user_permissions: Optional[Set[str]] = None

        if not is_super_admin:
            user_permissions = PermissionService.get_user_permission_names(usuario)

        submodulos_prefetch = Prefetch(
            "submodulos",
            queryset=(
                Module.objects.filter(estado_modulo="activo")
                .order_by("orden_visualizacion")
                .prefetch_related("modulo_permisos__permiso")
            ),
        )

        modulos_raiz = (
            Module.objects.filter(estado_modulo="activo", modulo_padre__isnull=True)
            .order_by("orden_visualizacion")
            .prefetch_related(
                "modulo_permisos__permiso",
                submodulos_prefetch,
            )
        )

        return [
            MenuService._build_item(modulo, user_permissions)
            for modulo in modulos_raiz
            if MenuService._is_visible(modulo, user_permissions)
        ]

    @staticmethod
    def _is_visible(modulo: Module, user_permissions: Optional[Set[str]]) -> bool:
        required_permissions = {
            rel.permiso.nombre_permiso
            for rel in modulo.modulo_permisos.all()
            if rel.permiso and rel.permiso.nombre_permiso
        }
        if not required_permissions:
            return True
        if user_permissions is None:
            return True
        return bool(required_permissions & user_permissions)

    @staticmethod
    def _build_item(modulo: Module, user_permissions: Optional[Set[str]]) -> Dict[str, Any]:
        item = {
            "id": f"modulo-{modulo.modulo_id}",
            "title": modulo.nombre_modulo,
            "icon": modulo.icono_modulo or "circle",
            "path": modulo.ruta_modulo or f"/{modulo.nombre_modulo.lower()}",
            "order": modulo.orden_visualizacion,
        }
        children = [
            MenuService._build_item(child, user_permissions)
            for child in modulo.get_children()
            if MenuService._is_visible(child, user_permissions)
        ]
        if children:
            item["submenu"] = children
        return item
```

- [ ] **Step 4.3: Update import in `api/v1/auth/views.py`**

```python
# Before:
from app_rrhh.menu_service import MenuService
# After:
from apps.identity.services.menu_service import MenuService
```

- [ ] **Step 4.4: Run check + tests**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, 161/8/3.

- [ ] **Step 4.5: Commit**

```bash
git add apps/api/apps/identity/services/ \
        apps/api/api/v1/auth/views.py
git commit -m "chore(L5.1): relocate menu_service.py from app_rrhh → apps/identity/services"
```

---

### Task 5: Relocate `validators.py` → `apps/time_off/validators.py`

**Files:**
- Create: `apps/api/apps/time_off/validators.py`
- Modify: `apps/api/api/v1/vacaciones/validators.py`

- [ ] **Step 5.1: Create `apps/time_off/validators.py`**

Copy the full content of `apps/api/app_rrhh/validators.py` verbatim to `apps/api/apps/time_off/validators.py`. No import changes needed — the only cross-app import inside it (`from apps.time_off.models import VacationRequest`) already uses the canonical path.

- [ ] **Step 5.2: Update import in `api/v1/vacaciones/validators.py`**

```python
# Before:
from app_rrhh.validators import VacacionesValidator, VacacionesBusinessRules
# After:
from apps.time_off.validators import VacacionesValidator, VacacionesBusinessRules
```

- [ ] **Step 5.3: Run check + tests**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, 161/8/3.

- [ ] **Step 5.4: Commit**

```bash
git add apps/api/apps/time_off/validators.py \
        apps/api/api/v1/vacaciones/validators.py
git commit -m "chore(L5.1): relocate validators.py from app_rrhh → apps/time_off"
```

---

### Task 6: Relocate `empleado_report_service.py` + fix dead `services.*` calls in `views.py`

**Context:** `api/v1/rrhh/views.py` line 8 has `from app_rrhh import services` — this imports an empty `__init__.py` (`__all__ = []`). Lines 305, 334, 867, 905, 948, 1616 call `services.AreaService`, `services.EmpleadoService`, and `services.UsuarioService` — all `AttributeError` at runtime. Plus lines 981 and 999 have `from app_rrhh.services.empleado_report_service import EmpleadoReportService`.

**Files:**
- Create: `apps/api/apps/employees/services/__init__.py`
- Create: `apps/api/apps/employees/services/employee_report_service.py` (git mv)
- Modify: `apps/api/api/v1/rrhh/views.py`

- [ ] **Step 6.1: Create `apps/employees/services/__init__.py`**

```python
# apps/api/apps/employees/services/__init__.py
```

- [ ] **Step 6.2: Move the report service via git mv**

```bash
cd apps/api
git mv app_rrhh/services/empleado_report_service.py \
       apps/employees/services/employee_report_service.py
```

- [ ] **Step 6.3: Fix the dead `from app_rrhh import services` import + all call sites in `views.py`**

Open `apps/api/api/v1/rrhh/views.py`. Make the following changes:

**Remove line 8:** `from app_rrhh import services`

**Add these imports** near the top of the file (after the existing model imports), adjusting the import block:

```python
from datetime import timedelta

from apps.contracts.models import EmploymentData
from apps.identity.models import User
```

(Check if `timedelta` and `User` are already imported — add only what's missing.)

**Replace each dead service call:**

Line ~305, `AreaService.get_area_statistics()`:
```python
# Before:
stats = services.AreaService.get_area_statistics(area.pk)
# After:
stats = {
    "total_empleados": EmploymentData.objects.filter(
        area_id=area.pk, estado_datos="activo"
    ).values("empleado").distinct().count(),
}
```

Line ~334, `AreaService.get_areas_summary()`:
```python
# Before:
areas_summary = services.AreaService.get_areas_summary()
# After:
from apps.organization.models import Department
areas_summary = [
    {
        "id": str(dept.pk),
        "nombre": dept.nombre_unidad_organica,
        "siglas": dept.siglas_area,
        "total_empleados": EmploymentData.objects.filter(
            area=dept, estado_datos="activo"
        ).values("empleado").distinct().count(),
    }
    for dept in Department.objects.all().order_by("nombre_unidad_organica")
]
```

Line ~867, `EmpleadoService.get_complete_employee_data()` — this is complex; return 501:
```python
# Before:
complete_data = services.EmpleadoService.get_complete_employee_data(empleado.pk)
return APIResponse.success(data=complete_data, message="Datos completos del empleado obtenidos exitosamente")
# After:
return APIResponse.error(
    message="Endpoint not yet implemented — use individual /datos-personales, /datos-laborales, /datos-familiares endpoints",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
```

Line ~905, `EmpleadoService.transferir_empleado()`:
```python
# Before:
services.EmpleadoService.transferir_empleado(empleado.pk, area_destino_id, fecha_inicio)
# After:
EmploymentData.objects.filter(
    empleado_id=empleado.pk, estado_datos="activo"
).update(area_id=area_destino_id)
```

Line ~948, `EmpleadoService.get_employee_statistics()`:
```python
# Before:
stats = services.EmpleadoService.get_employee_statistics()
# After:
from apps.employees.models import Employee
stats = {
    "total": Employee.objects.count(),
    "activos": Employee.objects.filter(estado_empleado="activo").count(),
    "inactivos": Employee.objects.filter(estado_empleado="inactivo").count(),
    "cesados": Employee.objects.filter(estado_empleado="cesado").count(),
}
```

Line ~1616, `UsuarioService.usuarios_sin_login_reciente()`:
```python
# Before:
usuarios = services.UsuarioService.usuarios_sin_login_reciente(dias)
# After:
threshold = timezone.now() - timedelta(days=dias)
usuarios = User.objects.filter(
    is_active=True,
    last_login__lt=threshold,
).order_by("last_login")
```

- [ ] **Step 6.4: Fix the `EmpleadoReportService` imports (lines ~981, ~999)**

Both are local imports inside a function body. Update them:
```python
# Before:
from app_rrhh.services.empleado_report_service import EmpleadoReportService
# After:
from apps.employees.services.employee_report_service import EmpleadoReportService
```

- [ ] **Step 6.5: Run check + tests**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, 161/8/3.

- [ ] **Step 6.6: Commit**

```bash
git add apps/api/apps/employees/services/ \
        apps/api/api/v1/rrhh/views.py
git commit -m "chore(L5.1): relocate employee_report_service + fix dead services.* calls in views.py"
```

---

### Task 7: Relocate management commands

**Files to create per target app:**

| Source | Destination |
|---|---|
| `app_rrhh/management/commands/seed_menu.py` | `apps/identity/management/commands/seed_menu.py` |
| `app_rrhh/management/commands/setup_roles_permisos.py` | `apps/identity/management/commands/setup_roles_permisos.py` |
| `app_rrhh/management/commands/audit_rbac.py` | `apps/identity/management/commands/audit_rbac.py` |
| `app_rrhh/management/commands/seed_plantillas_default.py` | `apps/documents/management/commands/seed_plantillas_default.py` |
| `app_rrhh/management/commands/seed_remuneraciones_config.py` | `apps/payroll/management/commands/seed_remuneraciones_config.py` |

- [ ] **Step 7.1: Create management package init files**

```bash
# identity (management/ and management/commands/ __init__.py)
touch apps/api/apps/identity/management/__init__.py
touch apps/api/apps/identity/management/commands/__init__.py

# documents
touch apps/api/apps/documents/management/__init__.py
touch apps/api/apps/documents/management/commands/__init__.py

# payroll
touch apps/api/apps/payroll/management/__init__.py
touch apps/api/apps/payroll/management/commands/__init__.py
```

- [ ] **Step 7.2: git mv the 5 command files**

```bash
cd apps/api
git mv app_rrhh/management/commands/seed_menu.py \
       apps/identity/management/commands/seed_menu.py

git mv app_rrhh/management/commands/setup_roles_permisos.py \
       apps/identity/management/commands/setup_roles_permisos.py

git mv app_rrhh/management/commands/audit_rbac.py \
       apps/identity/management/commands/audit_rbac.py

git mv app_rrhh/management/commands/seed_plantillas_default.py \
       apps/documents/management/commands/seed_plantillas_default.py

git mv app_rrhh/management/commands/seed_remuneraciones_config.py \
       apps/payroll/management/commands/seed_remuneraciones_config.py
```

- [ ] **Step 7.3: Verify commands are discoverable**

```bash
cd apps/api
python manage.py help --settings=vyntia.settings.development | grep -E "seed_menu|setup_roles|audit_rbac|seed_plantillas|seed_remun"
```

Expected: all 5 commands listed.

- [ ] **Step 7.4: Run check + tests**

```bash
python manage.py check --settings=vyntia.settings.development
pytest tests/ -x -q
```

Expected: check clean, 161/8/3.

- [ ] **Step 7.5: Commit**

```bash
git add apps/api/apps/identity/management/ \
        apps/api/apps/documents/management/ \
        apps/api/apps/payroll/management/
git commit -m "chore(L5.1): relocate 5 management commands from app_rrhh → identity/documents/payroll"
```

---

### Task 8: Remove `app_rrhh` from INSTALLED_APPS and delete the folder

- [ ] **Step 8.1: Update `vyntia/settings/base.py`**

Remove `"app_rrhh"` from LOCAL_APPS list (line ~43).

Remove the `"app_rrhh"` logger entry from the LOGGING dict (lines ~285-289):
```python
# Delete this block:
"app_rrhh": {
    "handlers": ["console", "file"],
    "level": "DEBUG",
    "propagate": False,
},
```

- [ ] **Step 8.2: Update `pyproject.toml`**

Remove `"app_rrhh"` from the packages list (line ~75):
```toml
# Before:
packages = ["vyntia", "app_rrhh", "api", "apps", ...]
# After:
packages = ["vyntia", "api", "apps", ...]
```

- [ ] **Step 8.3: Delete `app_rrhh/` directory**

At this point `app_rrhh/` should only contain empty stubs and the already-moved files. Verify nothing remains:

```bash
cd apps/api
grep -r "." app_rrhh/ --include="*.py" -l
```

Expected output — only stub files:
```
app_rrhh/__init__.py
app_rrhh/apps.py
app_rrhh/migrations/__init__.py
app_rrhh/services/__init__.py
app_rrhh/management/__init__.py
app_rrhh/management/commands/__init__.py
```

If any unexpected `.py` files appear, stop and investigate before deleting.

Delete the directory:
```bash
cd apps/api
git rm -r app_rrhh/
```

- [ ] **Step 8.4: Final backend verification**

```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -q
```

Expected: check clean; pytest 161/8/3 (no regression).

Grep DoD check for app_rrhh:
```bash
grep -ri "app_rrhh" apps/api/ --include="*.py"
```

Expected: **zero matches**.

- [ ] **Step 8.5: Commit**

```bash
git add apps/api/vyntia/settings/base.py \
        apps/api/pyproject.toml
git commit -m "chore(L5.1): remove app_rrhh from INSTALLED_APPS, pyproject, and delete folder"
```

- [ ] **Step 8.6: Merge L5.1 to master**

```bash
git checkout master
git merge --no-ff vyntia/L5.1-backend-app-rrhh-relocation \
  -m "Merge L5.1: backend app_rrhh relocation (L5 backend DONE)"
```

---

## Sub-PR L5.2 — Frontend: Clean up `pages/`, `hooks/`, `context/`

Branch: `vyntia/L5.2-frontend-cleanup`

**Current state (confirmed):**
- `src/pages/` has 4 remaining files: `Dashboard.tsx`, `AccessDeniedPage.tsx`, `LoadingDemo.tsx`, `admin/AdminDashboard.tsx`
- `App.tsx` imports `AccessDeniedPage`, `AdminDashboard`, `Dashboard` from `@/pages/...`
- `src/hooks/` has `useApi.ts` (imported by `Empleados.tsx` + `TabLaborales.tsx`) and `useApi-deprecated.ts` (no consumers)
- `src/context/` has only `ThemeContext.tsx` (imported by `App.tsx` as `@/context/ThemeContext`)

**Files to create:**
- `apps/web/src/shared/pages/Dashboard.tsx`
- `apps/web/src/shared/pages/AccessDeniedPage.tsx`
- `apps/web/src/features/identity/pages/AdminDashboard.tsx`
- `apps/web/src/features/employees/hooks/useEmployees.ts`
- `apps/web/src/features/organization/hooks/__init__` (dir creation)
- `apps/web/src/features/organization/hooks/useDepartments.ts`
- `apps/web/src/shared/context/ThemeContext.tsx`

**Files to modify:**
- `apps/web/src/App.tsx` — update 3 page imports + 1 ThemeContext import
- `apps/web/src/features/identity/pages/index.ts` — add AdminDashboard export
- `apps/web/src/features/employees/pages/Empleados.tsx` — update useEmpleados import
- `apps/web/src/features/employees/components/TabLaborales.tsx` — update useAreas import

**Files to delete:**
- `apps/web/src/pages/` directory (all 4 files + `admin/` subdir)
- `apps/web/src/hooks/useApi.ts`
- `apps/web/src/hooks/useApi-deprecated.ts`
- `apps/web/src/hooks/` directory (if empty after deletions)
- `apps/web/src/context/ThemeContext.tsx`
- `apps/web/src/context/` directory

---

### Task 9: Move `AdminDashboard` → `features/identity/pages/`

**Files:**
- Create: `apps/web/src/features/identity/pages/AdminDashboard.tsx`
- Modify: `apps/web/src/features/identity/pages/index.ts`
- Modify: `apps/web/src/App.tsx`

- [ ] **Step 9.1: git mv AdminDashboard to identity**

```bash
git mv apps/web/src/pages/admin/AdminDashboard.tsx \
       apps/web/src/features/identity/pages/AdminDashboard.tsx
```

- [ ] **Step 9.2: Add AdminDashboard to identity pages barrel**

Open `apps/web/src/features/identity/pages/index.ts`. Add at the end:
```typescript
export { default as AdminDashboard } from './AdminDashboard'
```

- [ ] **Step 9.3: Update App.tsx import**

```typescript
// Before:
import AdminDashboard from '@/pages/admin/AdminDashboard'
// After:
import AdminDashboard from '@/features/identity/pages/AdminDashboard'
```

- [ ] **Step 9.4: Build check**

```bash
cd apps/web
npm run build 2>&1 | tail -5
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -20
```

Expected: build success, no new tsc errors.

- [ ] **Step 9.5: Commit**

```bash
git add apps/web/src/features/identity/pages/AdminDashboard.tsx \
        apps/web/src/features/identity/pages/index.ts \
        apps/web/src/App.tsx
git commit -m "chore(L5.2): move AdminDashboard → features/identity/pages"
```

---

### Task 10: Move `Dashboard.tsx` + `AccessDeniedPage.tsx` to `shared/pages/`, delete `LoadingDemo.tsx`, delete `pages/` dir

**Files:**
- Create: `apps/web/src/shared/pages/Dashboard.tsx`
- Create: `apps/web/src/shared/pages/AccessDeniedPage.tsx`
- Modify: `apps/web/src/App.tsx`
- Delete: `apps/web/src/pages/LoadingDemo.tsx`
- Delete: `apps/web/src/pages/` directory

- [ ] **Step 10.1: git mv the two live pages**

```bash
mkdir -p apps/web/src/shared/pages

git mv apps/web/src/pages/Dashboard.tsx \
       apps/web/src/shared/pages/Dashboard.tsx

git mv apps/web/src/pages/AccessDeniedPage.tsx \
       apps/web/src/shared/pages/AccessDeniedPage.tsx
```

- [ ] **Step 10.2: Delete LoadingDemo.tsx (dev demo, no consumers)**

```bash
# Verify it has no consumers first:
grep -r "LoadingDemo" apps/web/src/ --include="*.tsx" --include="*.ts"
# Expected: zero matches in App.tsx or other files (only in the file itself)

git rm apps/web/src/pages/LoadingDemo.tsx
```

- [ ] **Step 10.3: Delete now-empty `pages/` directory**

```bash
# Verify it's empty:
ls apps/web/src/pages/
# Expected: nothing (admin/ subdir is now empty too since AdminDashboard moved in Task 9)

git rm -r apps/web/src/pages/
```

- [ ] **Step 10.4: Update App.tsx imports**

```typescript
// Before:
import AccessDeniedPage from '@/pages/AccessDeniedPage'
import { Dashboard } from '@/pages/Dashboard'
// After:
import AccessDeniedPage from '@/shared/pages/AccessDeniedPage'
import { Dashboard } from '@/shared/pages/Dashboard'
```

- [ ] **Step 10.5: Build check**

```bash
cd apps/web
npm run build 2>&1 | tail -5
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -20
```

Expected: build success, no new errors.

- [ ] **Step 10.6: Commit**

```bash
git add apps/web/src/shared/pages/ \
        apps/web/src/App.tsx
git commit -m "chore(L5.2): move Dashboard+AccessDenied → shared/pages, delete LoadingDemo, remove pages/ dir"
```

---

### Task 11: Migrate `useApi.ts` hooks → feature hooks, delete `hooks/`

**Context:** `useApi.ts` exports `useEmpleados` (used by `Empleados.tsx`) and `useAreas` (used by `TabLaborales.tsx`). Both call methods on `apiClient` from `@/shared/api/api`. The remaining exports (`useCreateEmpleado`, `useUpdateEmpleado`, `useDeleteEmpleado`, `useBoletas`, `useUsuarios`, `useRoles`) have no active consumers. `useApi-deprecated.ts` has zero consumers.

**Files:**
- Create: `apps/web/src/features/employees/hooks/useEmployees.ts`
- Create: `apps/web/src/features/organization/hooks/useDepartments.ts`
- Modify: `apps/web/src/features/employees/pages/Empleados.tsx`
- Modify: `apps/web/src/features/employees/components/TabLaborales.tsx`
- Delete: `apps/web/src/hooks/useApi.ts`
- Delete: `apps/web/src/hooks/useApi-deprecated.ts`
- Delete: `apps/web/src/hooks/` (directory will be empty)

- [ ] **Step 11.1: Verify no other consumers of `useApi.ts`**

```bash
grep -r "from '@/hooks/useApi'" apps/web/src/ --include="*.ts" --include="*.tsx"
```

Expected exactly 2 hits: `Empleados.tsx` (line 42) and `TabLaborales.tsx` (line 11).

- [ ] **Step 11.2: Create `features/employees/hooks/useEmployees.ts`**

```typescript
// apps/web/src/features/employees/hooks/useEmployees.ts
import { apiClient } from "@/shared/api/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export interface PaginationParams {
  page?: number;
  page_size?: number;
  search?: string;
  [key: string]: any;
}

export function useEmpleados(params?: PaginationParams) {
  const transformedParams = params
    ? {
        ...params,
        ...(params.estado === "true" && { estado: "activo" }),
        ...(params.estado === "false" && { estado: "inactivo" }),
      }
    : params;

  const cleanParams = transformedParams
    ? Object.fromEntries(
        Object.entries(transformedParams).filter(
          ([, v]) => v !== undefined && v !== null && v !== "",
        ),
      )
    : transformedParams;

  return useQuery({
    queryKey: ["empleados", cleanParams],
    queryFn: () => apiClient.getEmpleados(cleanParams),
    keepPreviousData: true,
  });
}

export function useCreateEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => apiClient.createEmpleado(data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}

export function useUpdateEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) =>
      apiClient.updateEmpleado(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}

export function useDeleteEmpleado() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiClient.deleteEmpleado(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["empleados"] }),
  });
}
```

Note: `id` type changed from `number` to `string` (UUIDs from L3.10.4e).

- [ ] **Step 11.3: Create `features/organization/hooks/useDepartments.ts`**

First verify the `hooks/` directory doesn't already exist in organization:
```bash
ls apps/web/src/features/organization/
```
If no `hooks/` dir, create it:
```bash
mkdir -p apps/web/src/features/organization/hooks
```

```typescript
// apps/web/src/features/organization/hooks/useDepartments.ts
import { apiClient } from "@/shared/api/api";
import { useQuery } from "@tanstack/react-query";

export function useAreas(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["areas", params],
    queryFn: () => apiClient.getAreas(params),
  });
}
```

- [ ] **Step 11.4: Update import in `Empleados.tsx`**

```typescript
// Before (line 42):
import { useEmpleados } from '@/hooks/useApi'
// After:
import { useEmpleados } from '@/features/employees/hooks/useEmployees'
```

- [ ] **Step 11.5: Update import in `TabLaborales.tsx`**

```typescript
// Before (line 11):
import { useAreas } from '@/hooks/useApi'
// After:
import { useAreas } from '@/features/organization/hooks/useDepartments'
```

- [ ] **Step 11.6: Delete the old hook files**

```bash
git rm apps/web/src/hooks/useApi.ts
git rm apps/web/src/hooks/useApi-deprecated.ts
# Directory should now be empty — git rm it
rmdir apps/web/src/hooks/ 2>/dev/null || git rm -r apps/web/src/hooks/
```

- [ ] **Step 11.7: Build + test check**

```bash
cd apps/web
npm run build 2>&1 | tail -5
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -20
npm test -- --run
```

Expected: build success, no new tsc errors, 7 vitest tests pass.

- [ ] **Step 11.8: Commit**

```bash
git add apps/web/src/features/employees/hooks/useEmployees.ts \
        apps/web/src/features/organization/hooks/useDepartments.ts \
        apps/web/src/features/employees/pages/Empleados.tsx \
        apps/web/src/features/employees/components/TabLaborales.tsx
git commit -m "chore(L5.2): migrate useEmpleados/useAreas to feature hooks, delete hooks/ dir"
```

---

### Task 12: Move `ThemeContext.tsx` → `shared/context/`, delete `context/`

**Files:**
- Create: `apps/web/src/shared/context/ThemeContext.tsx`
- Modify: `apps/web/src/App.tsx`
- Delete: `apps/web/src/context/`

- [ ] **Step 12.1: git mv ThemeContext**

```bash
mkdir -p apps/web/src/shared/context
git mv apps/web/src/context/ThemeContext.tsx \
       apps/web/src/shared/context/ThemeContext.tsx
```

- [ ] **Step 12.2: Update App.tsx import**

```typescript
// Before (line ~8):
import { ThemeProvider } from '@/context/ThemeContext'
// After:
import { ThemeProvider } from '@/shared/context/ThemeContext'
```

- [ ] **Step 12.3: Check for any other consumers**

```bash
grep -r "ThemeContext\|ThemeProvider" apps/web/src/ --include="*.ts" --include="*.tsx"
```

Expected: only `App.tsx` + the file itself. If more consumers appear, update those imports too.

- [ ] **Step 12.4: Delete empty `context/` directory**

```bash
git rm -r apps/web/src/context/ 2>/dev/null || echo "already removed"
```

- [ ] **Step 12.5: Full frontend verification**

```bash
cd apps/web
npm run build 2>&1 | tail -5
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | head -20
npm test -- --run
```

Expected: build success, 1 pre-existing tsc error (BlankEnum.ts only), 7 vitest tests pass.

- [ ] **Step 12.6: Commit + merge L5.2**

```bash
git add apps/web/src/shared/context/ThemeContext.tsx \
        apps/web/src/App.tsx
git commit -m "chore(L5.2): move ThemeContext → shared/context, delete context/ dir"

git checkout master
git merge --no-ff vyntia/L5.2-frontend-cleanup \
  -m "Merge L5.2: frontend cleanup — pages, hooks, context (L5 frontend DONE)"
```

---

## Sub-PR L5.3 — CI Workflows + Docs + Final DoD Audit

Branch: `vyntia/L5.3-ci-docs-final`

---

### Task 13: Rewrite CI workflows

**Context:** Both existing workflow files are completely stale — they reference pre-L0 paths (`back/`, `front/`), old settings (`config.settings.testing`), old DB name (`bd_rrhh_test`), and old install method (`pip install -r back/requirements.txt`). Replace both with a single unified `ci.yml`.

**Files:**
- Create: `apps/api/.github/workflows/ci.yml` — actually at root: `.github/workflows/ci.yml`
- Delete: `.github/workflows/backend-ci.yml`
- Delete: `.github/workflows/frontend-ci.yml`

- [ ] **Step 13.1: Delete stale workflow files**

```bash
git rm .github/workflows/backend-ci.yml
git rm .github/workflows/frontend-ci.yml
```

- [ ] **Step 13.2: Create `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20.x'
  DJANGO_SETTINGS_MODULE: vyntia.settings.testing

jobs:
  backend-test:
    name: Backend — pytest
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: bd_vyntia_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -e "apps/api[dev]"

      - name: Run migrations
        run: |
          cd apps/api
          python manage.py migrate --settings=vyntia.settings.testing
        env:
          DB_NAME: bd_vyntia_test
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost

      - name: Run pytest
        run: |
          cd apps/api
          pytest tests/ -q --tb=short
        env:
          DB_NAME: bd_vyntia_test
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost

  backend-check:
    name: Backend — Django system check
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ env.PYTHON_VERSION }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -e "apps/api[dev]"

      - name: Django system check
        run: |
          cd apps/api
          python manage.py check --settings=vyntia.settings.testing
        env:
          DB_NAME: bd_vyntia_test
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost

      - name: Check for pending migrations
        run: |
          cd apps/api
          python manage.py makemigrations --dry-run --check --settings=vyntia.settings.testing
        env:
          DB_NAME: bd_vyntia_test
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost

  frontend-test:
    name: Frontend — vitest
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: apps/web/package-lock.json

      - name: Install dependencies
        run: cd apps/web && npm ci

      - name: Run vitest
        run: cd apps/web && npm test -- --run

  frontend-build:
    name: Frontend — build + typecheck
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: apps/web/package-lock.json

      - name: Install dependencies
        run: cd apps/web && npm ci

      - name: TypeScript check
        run: cd apps/web && npx tsc --noEmit -p tsconfig.app.json

      - name: Build
        run: cd apps/web && npm run build

  frontend-lint:
    name: Frontend — ESLint
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node ${{ env.NODE_VERSION }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: apps/web/package-lock.json

      - name: Install dependencies
        run: cd apps/web && npm ci

      - name: ESLint
        run: cd apps/web && npm run lint
```

- [ ] **Step 13.3: Verify workflow syntax**

```bash
# Check that the YAML is valid:
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "YAML valid"
```

Expected: `YAML valid`

- [ ] **Step 13.4: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "chore(L5.3): rewrite CI — unified ci.yml for vyntia monorepo (drop stale back/front paths)"
```

---

### Task 14: Create `docs/ROADMAP_SUBPROJECTS.md`

Required by Foundation spec § 8 DoD: "docs/ROADMAP_SUBPROJECTS.md con los ~23 sub-proyectos identificados".

- [ ] **Step 14.1: Create `docs/ROADMAP_SUBPROJECTS.md`**

```markdown
# VYNTIA — Sub-Projects Roadmap

> Source of truth for the post-Foundation build plan. Derived from Foundation Design Spec § 6 (2026-04-25).
> **Foundation (sub-project A) is complete.** Start from row 2.

| # | Code | Sub-project | Needs before | Tier unlocked |
|---|------|-------------|--------------|---------------|
| 1 | **A** | Foundation (rebrand + restructure + cleanup) | — | — |
| 2 | **C** | Multi-tenancy + Row-Level Security | A | Enables SaaS sales |
| 3 | **B** | Migración funcional Vyntia Core | A, C | Vyntia Core with tenant |
| 4 | **D** | Vyntia Pay (planilla peruana real — PLAME, T-Registro, AFPnet, CTS, gratificaciones) | B | **Starter tier** |
| 5 | **N** | Asistencia + turnos | D | Starter + Attendance |
| 6 | **P** | App móvil (React Native) | B | Employee mobile portal |
| 7 | **S** | Billing SaaS (suscripciones, planes) | C | Automated billing |
| 8 | **H** | Vyntia Pulse (gestión rendimiento) | B | **Pro tier** |
| 9 | **G** | Learning + Career | B | Pro tier |
| 10 | **Q** | Vyntia Hire (ATS — reclutamiento) | B | Pro tier |
| 11 | **E** | Extensión Organización (positions, org chart) | B | Core extension |
| 12 | **F** | Policies (gestión políticas SERVIR) | B | GovTech tier |
| 13 | **I** | Labor Relations (relaciones laborales) | B | GovTech tier |
| 14 | **J** | Safety (seguridad y salud) | B | GovTech tier |
| 15 | **K** | Welfare (bienestar) | B | GovTech tier |
| 16 | **L** | Engagement (clima organizacional) | B | GovTech tier |
| 17 | **M** | Communications (comunicaciones internas) | B | GovTech tier |
| 18 | **O** | Discipline (procedimiento disciplinario) | B | GovTech tier |
| 19 | **R** | Vyntia Insights (People Analytics) | B + real data | **Enterprise tier** |
| 20 | **T** | Workflow Engine (motor declarativo) | B | Platform maturity |
| 21 | **U** | DocType Engine (metadata-driven forms) | B | Platform maturity |
| 22 | **V** | Permissions v2 (RBAC + permlevel 0-9 + ABAC) | C | Platform maturity |
| 23 | **W** | Notifications (email, push, in-app) | B | Platform maturity |
| 24 | **X** | Audit Log (transversal audit trail) | B | Platform maturity |

## Commercial brand mapping

| VYNTIA module | Sub-projects | Django apps |
|---|---|---|
| **Vyntia Core** | A, B, C, E, F | identity, organization, employees, contracts, documents, onboarding |
| **Vyntia Pay** | D, N | payroll, time_off, attendance, regional_pe |
| **Vyntia People** | G, H, I-M | learning, career, performance, labor_relations, welfare, engagement, communications |
| **Vyntia Hire** | Q | recruitment |
| **Vyntia Insights** | R | analytics |
| **Vyntia Safety** | J | safety |

## Architecture rules (enforced across all sub-projects)

1. **FK cross-app ONLY via string lazy**: `ForeignKey('employees.Employee', ...)` — never import from another app.
2. **Cross-app logic via service public API**: `from apps.employees.services import get_employee_data`.
3. **`core` has zero domain app dependencies** — pure utility only.
4. **New Django apps only when real code exists** (no speculative empty apps).
5. **English for code; Spanish for UI strings** (i18n in sub-project Z).
6. **Peruvian legal terms preserved**: DNI, RUC, CTS, PLAME, SUNAT, T-Registro, AFP, ONP, ESSALUD.
```

- [ ] **Step 14.2: Commit**

```bash
git add docs/ROADMAP_SUBPROJECTS.md
git commit -m "docs(L5.3): create ROADMAP_SUBPROJECTS.md — 24 sub-projects post-Foundation"
```

---

### Task 15: Create `docs/CONTRIBUTING.md`

Required by Foundation spec § 4 L5 scope: "Crear docs/CONTRIBUTING.md con convenciones".

- [ ] **Step 15.1: Create `docs/CONTRIBUTING.md`**

```markdown
# Contributing to VYNTIA

## Quick start

```bash
# 1. Clone and set up Python venv
cd D:/VYNTIA
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
pip install -e "apps/api[dev]"

# 2. Install Node dependencies
cd apps/web && npm install && cd ../..

# 3. Start dev servers (two terminals)
cd apps/api && python manage.py runserver --settings=vyntia.settings.development
cd apps/web && npm run dev
```

## Branch + PR conventions

| What | Convention |
|---|---|
| Branch name | `vyntia/L<N>.<sub>-short-description` or `vyntia/<feature-slug>` |
| Commit prefix | `chore(L<N>):`, `feat(<module>):`, `fix(<module>):`, `docs(<scope>):` |
| Merge style | `--no-ff` to preserve layer history |
| PR granularity | One PR per sub-layer or bounded change. No big-bang PRs |

## Backend (Django)

- **Settings module**: `vyntia.settings.{development,testing,production}`
- **Run server**: `python manage.py runserver --settings=vyntia.settings.development`
- **Run tests**: `cd apps/api && pytest` (161 pass / 8 pre-existing fail / 3 skip baseline)
- **Django check**: `python manage.py check --settings=vyntia.settings.development`
- **New migration**: `python manage.py makemigrations <app> && python manage.py migrate`
- **DB**: `bd_vyntia` on localhost:5432. Override via `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` env vars.

### Architecture rules

- FK cross-app: `ForeignKey('employees.Employee', on_delete=CASCADE)` — string lazy always
- No imports across bounded-context apps — use service public APIs
- `apps/core` is utility-only, zero domain model dependencies
- PKs are UUID (`id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`)
- Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`
- Domain HR vocabulary stays in Spanish: `estado_empleado`, `tipo_documento`, `nombres`, etc.
- Platform state fields: `status`, `is_active`
- All responses through `APIResponse` from `apps.core.responses`

### App structure template

```
apps/api/apps/<bounded_context>/
├── __init__.py
├── apps.py              # AppConfig
├── models/
│   ├── __init__.py      # re-exports all models
│   └── <model>.py
├── serializers.py
├── views/
│   ├── __init__.py
│   └── <viewset>.py
├── urls.py
├── services/
│   ├── __init__.py
│   └── <service>.py
├── tests/
│   ├── __init__.py
│   └── test_<x>.py
└── migrations/
```

## Frontend (React + Vite)

- **Dev server**: `cd apps/web && npm run dev` (proxies `/api/*` → `http://127.0.0.1:8000`)
- **Build**: `npm run build`
- **TypeScript check**: `npx tsc --noEmit -p tsconfig.app.json`
- **Tests**: `npm test -- --run` (7 vitest tests)
- **Lint**: `npm run lint`

### Feature structure template

```
apps/web/src/features/<bounded_context>/
├── index.ts             # public re-exports
├── components/
│   └── index.ts
├── hooks/
│   └── use<Feature>.ts
├── pages/
│   ├── index.ts
│   └── <Page>.tsx
└── services/
    └── <feature>Service.ts
```

### API conventions

- API client: `import { apiClient } from '@/shared/api/api'`
- All responses unwrapped: `response.data?.data?.results ?? response.data?.results ?? response.data`
- React Query v5 for data fetching; no Redux/Zustand
- Forms: `react-hook-form` + `zod`
- UI primitives: Shadcn/ui at `@/shared/ui/`
- UUIDs for all entity IDs — `id: string`, never `id: number`

## Test philosophy

- **Backend**: Every new view action needs at least one happy-path test in `apps/api/tests/`
- **Frontend**: Feature-level vitest tests for hooks and services
- Do NOT mock the database in backend tests — tests hit `bd_vyntia_test` via Django test runner
- Preserve baselines: pytest 161/8/3, vitest 7

## Common pitfalls

| Pitfall | Fix |
|---|---|
| `UnicodeDecodeError` from `psycopg2.connect` on `runserver` | `DB_PASSWORD` contains non-ASCII char — use `manage.py check` for local code verification |
| `replace_all` renames both field reads AND query param strings | Use per-file context — `?estado=activo` query params stay Spanish |
| Django template multi-line tags break | All `{% %}` and `{{ }}` must open and close on the same line |
| `app_rrhh` references in code | There should be zero — grep: `grep -ri "app_rrhh" apps/` |
```

- [ ] **Step 15.2: Commit**

```bash
git add docs/CONTRIBUTING.md
git commit -m "docs(L5.3): create CONTRIBUTING.md with dev setup + architecture conventions"
```

---

### Task 16: Final DoD audit + CLAUDE.md update

- [ ] **Step 16.1: Run all DoD grep checks**

```bash
# Check 1: no app_rrhh references in Python/TS code
grep -ri "app_rrhh" apps/ --include="*.py" --include="*.ts" --include="*.tsx"
# Expected: zero matches

# Check 2: no INTRANET references in code (docs/ exempted)
grep -ri "intranet" apps/ --include="*.py" --include="*.ts" --include="*.tsx"
# Expected: zero matches

# Check 3: no rrhh_ prefix (old BD/field names)
grep -ri "rrhh_\|bd_rrhh" apps/ --include="*.py" --include="*.ts" --include="*.tsx" --include="*.yml"
# Expected: zero matches (the old ci.yml files are deleted)

# Check 4: no stale back/ or front/ path references in CI
grep -r "back/\|front/" .github/ --include="*.yml"
# Expected: zero matches
```

If any matches remain, fix them before proceeding.

- [ ] **Step 16.2: Run full test suite**

```bash
# Backend
cd apps/api
python manage.py check --settings=vyntia.settings.development
pytest tests/ -q

# Frontend
cd ../../apps/web
npm run build
npm test -- --run
npx tsc --noEmit -p tsconfig.app.json 2>&1 | grep -v BlankEnum | wc -l
```

Expected:
- `manage.py check`: clean
- pytest: 161 passed / 8 failed / 3 skipped (or better)
- `npm run build`: exit 0
- `npm test`: 7 passed
- tsc: 0 new errors (only BlankEnum.ts pre-existing)

- [ ] **Step 16.3: Update `CLAUDE.md` — mark L5 complete and update sub-project status**

In `D:/VYNTIA/CLAUDE.md`, update the Migration Roadmap table:

```markdown
| **A** | Foundation (rebrand + restructure + cleanup) | **✅ COMPLETE (L0-L5 done)** | All layers merged |
```

Update the Foundation layers list:
```markdown
- L5 ✅ Cleanup final + docs + CI
```

Update the "Active sub-project" line:
```markdown
**Active sub-project:** Next: **C — Multi-tenancy + RLS** (next after Foundation complete)
```

Update the "Key File Locations" table to remove any `app_rrhh` references, and add:
```markdown
| constants / permissions | `apps/api/apps/core/constants.py`, `apps/api/apps/core/permission_service.py` |
| Menu service | `apps/api/apps/identity/services/menu_service.py` |
| Employee report | `apps/api/apps/employees/services/employee_report_service.py` |
| Vacation validators | `apps/api/apps/time_off/validators.py` |
| Email tasks | `apps/api/apps/core/tasks.py` |
| Management commands | `apps/api/apps/{identity,documents,payroll}/management/commands/` |
| App-level dashboard | `apps/web/src/shared/pages/Dashboard.tsx` |
| Admin dashboard | `apps/web/src/features/identity/pages/AdminDashboard.tsx` |
| Employees hook | `apps/web/src/features/employees/hooks/useEmployees.ts` |
| Departments hook | `apps/web/src/features/organization/hooks/useDepartments.ts` |
| Theme context | `apps/web/src/shared/context/ThemeContext.tsx` |
```

- [ ] **Step 16.4: Update memory file**

Update `C:/Users/zeeke/.claude/projects/D--VYNTIA/memory/active_subproject.md`:
- Mark L5 as ✅ COMPLETE
- Change "What's next" to: sub-project C (Multi-tenancy + RLS)

- [ ] **Step 16.5: Commit + merge L5.3**

```bash
git add CLAUDE.md \
        docs/ROADMAP_SUBPROJECTS.md \
        docs/CONTRIBUTING.md
git commit -m "docs(L5.3): final CLAUDE.md update — Foundation sub-project A COMPLETE"

git checkout master
git merge --no-ff vyntia/L5.3-ci-docs-final \
  -m "Merge L5.3: CI + docs + final DoD audit (FOUNDATION COMPLETE)"
```

- [ ] **Step 16.6: Tag Foundation complete**

```bash
git tag -a "foundation-complete" -m "Foundation sub-project A complete (L0-L5)"
```

---

## Self-Review

### Spec coverage check

| Spec requirement (§ 4 L5 + § 8 DoD) | Covered by task |
|---|---|
| Borrar archivos huérfanos | Task 10 (LoadingDemo.tsx), Task 11 (useApi-deprecated.ts) |
| Eliminar imports muertos | Task 6 (dead services.* in views.py), Task 11 |
| Borrar scripts legacy | app_rrhh/ folder deleted in Task 8 |
| Actualizar CLAUDE.md | Task 16 |
| Actualizar docs/00_VYNTIA_MAESTRO.md | Not required — maestro doc reflects vision, not implementation; CI handles it |
| Crear docs/ROADMAP_SUBPROJECTS.md | Task 14 |
| Crear docs/CONTRIBUTING.md | Task 15 |
| CI workflow `.github/workflows/ci.yml` | Task 13 |
| `grep app_rrhh apps/` → zero matches | Task 8 + Task 16 DoD audit |
| CI verde en GitHub Actions | Task 13 (requires GitHub remote push — manual step after L5) |
| `git clone && make setup && make dev` in <30 min | CONTRIBUTING.md covers it; Makefile already exists in apps/api |

### Gaps noted

- **CONTRIBUTING.md** covers `source .venv/Scripts/activate` (Windows Git Bash) — on Linux CI the path would be `.venv/bin/activate`. The CI workflow doesn't activate venv because pip installs directly.
- **`docs/00_VYNTIA_MAESTRO.md`** — spec mentions updating it, but it's a 37-doc master vision that was last updated during L0. The product vision hasn't changed. No update needed; mark as N/A.
- **`grep -ri "Empleado\|Contrato\|Vacacion" apps/api/apps/`** (second DoD check in spec § 8) — Note: this check targets Spanish *model class names* in Python code. With L3.10.1 complete, all class names are English. However, Spanish *field names* and *string literals* remain by spec (Option B). This grep may return false positives from field names in managers/validators. This DoD check is best interpreted as "no Spanish *class names*" — verify during Task 16 audit.

### Type consistency

- `useUpdateEmpleado` and `useDeleteEmpleado` in Task 11 use `id: string` (UUID) — consistent with L3.10.4e which changed all entity PKs from `number` to `string`.
- `EmploymentData.objects.filter(area_id=area.pk, estado_datos="activo")` in Task 6 — `area_id` and `estado_datos` are domain Spanish field names preserved per spec Option B.

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-07-vyntia-foundation-L5-cleanup-final.md`.**
