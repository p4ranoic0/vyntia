# VYNTIA Foundation L3.8 — Extract `time_off` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los 5 modelos de vacaciones (`ConfiguracionVacaciones`, `PeriodoVacacional`, `SolicitudVacaciones`, `GoceVacaciones`, `HistorialSolicitudVacaciones`), **sus 5 active managers** (heredados de la división original), **y sus 5 services** (`vacation_service`, `vacation_approval_service`, `vacation_admin_service`, `vacation_calculation_service`, `vacation_report_service`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/time_off/`. Class names quedan en español — el rename a inglés y el split (`SolicitudVacaciones → VacationRequest + VacationBalance`) son L3.10.

**Architecture:** L3.8 es **el sub-PR con más componentes hasta ahora**: 5 modelos + 5 active managers (file `vacation_managers.py`) + 5 services. Diferente de L3.1-L3.7: los modelos usan `objects = XManager()` activos (no comentados como otros apps). El managers file `app_rrhh/managers/vacation_managers.py` debe moverse junto con los modelos a `apps/time_off/managers.py` (single file). LR11 SÍ aplica esta vez: `app_rrhh/validators.py:155, 256` tiene 2 inline `from .models import SolicitudVacaciones` que deben actualizarse. LR13 N/A: los 5 services usan `logger = logging.getLogger(__name__)` que se auto-resuelve al nuevo path.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2-L3.7), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.8; § 3.2 "División de modelos"; § 3.3 "Mapeo de services" (5 vacation services → `time_off`)

**Scope decision (alineada con L3.1-L3.7 pattern):**
- Class names en español; rename a inglés en L3.10
- Spec § 3.2 menciona `vacaciones.py → VacationRequest + VacationBalance (split)` — **deferido a L3.10** junto con rename, igual que se difirió ContratosAdendas split en L3.5
- App name uses **underscore convention**: `apps.time_off` (Python module path), `time_off` (Django label)

**Pre-condiciones:**
- L3.7 mergeada a master (commit `84ba7467`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization,employees,contracts,documents,payroll}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/time_off/` existe con `apps.py`, `models/`, `services/`, `managers.py`, `migrations/`
- [ ] 5 modelos movidos a `apps/time_off/models/vacaciones.py`
- [ ] 5 services movidos a `apps/time_off/services/`
- [ ] `vacation_managers.py` movido a `apps/time_off/managers.py` (single file, plano)
- [ ] `app_rrhh/models/vacaciones.py` eliminado
- [ ] `app_rrhh/services/vacation_*.py` (5 archivos) eliminados
- [ ] `app_rrhh/managers/vacation_managers.py` eliminado
- [ ] `TimeOffConfig` en `LOCAL_APPS`
- [ ] **Internal manager import updated:** `vacaciones.py` línea 14 `from ..managers import (...)` → `from .managers import (...)` (relative within new same-app)
- [ ] FK strings `'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`, `'contracts.ContratosAdendas'` dentro de modelos movidos preservados (ya correctos pre-move)
- [ ] Same-module FKs (PeriodoVacacional, ConfiguracionVacaciones, SolicitudVacaciones) preservadas como class refs
- [ ] **LR9 defensive check:** 0 stale `'app_rrhh.{vacation-models}'` strings (verified pre-move N/A)
- [ ] **LR10 defensive sed:** procesa single + double quote
- [ ] **LR11 fix:** `app_rrhh/validators.py:155, 256` inline `from .models import SolicitudVacaciones` → `from apps.time_off.models import SolicitudVacaciones`
- [ ] **LR13 N/A:** los 5 services usan `getLogger(__name__)` (auto-resolve), no string literals (verified)
- [ ] `app_rrhh/services/__init__.py` ya no exporta los 5 vacation services
- [ ] `app_rrhh/managers/__init__.py` ya no exporta los 5 vacation managers
- [ ] `apps/time_off/services/__init__.py` exporta los 5 services
- [ ] Imports actualizados across ~13 archivos (incluye 5 services internal + scripts + api/v1/vacaciones/* + tests)
- [ ] Migraciones regeneradas: app_rrhh sin vacation models; time_off con 5 modelos
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] `pyproject.toml` `packages` incluye `"apps.time_off"`
- [ ] **LR12 sequence:** drop → CREATE bd_vyntia → makemigrations → migrate
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.8-timeoff-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/time_off/__init__.py` | empty |
| Create | `apps/api/apps/time_off/apps.py` | `TimeOffConfig(AppConfig)` con `name="apps.time_off"`, `label="time_off"` |
| Create | `apps/api/apps/time_off/models/__init__.py` | re-exporta los 5 modelos |
| Create | `apps/api/apps/time_off/services/__init__.py` | re-exporta los 5 services |
| Move | `app_rrhh/models/vacaciones.py` → `apps/api/apps/time_off/models/vacaciones.py` | 5 modelos. FKs cross-app ya correctos (`'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`, `'contracts.ContratosAdendas'`); same-module FKs son class refs. Internal manager import en línea 14 será actualizado en Task 8 |
| Move | `app_rrhh/managers/vacation_managers.py` → `apps/api/apps/time_off/managers.py` | 5 managers como single file (plano, no package) |
| Move | `app_rrhh/services/vacation_service.py` → `apps/api/apps/time_off/services/vacation_service.py` | Internal `from app_rrhh.models.vacaciones import (...)` → relative `from ..models import (...)` |
| Move | `app_rrhh/services/vacation_approval_service.py` → `apps/api/apps/time_off/services/vacation_approval_service.py` | Internal updates + `from app_rrhh.permission_service import PermissionService` queda intacto (permission_service stays in app_rrhh) |
| Move | `app_rrhh/services/vacation_admin_service.py` → `apps/api/apps/time_off/services/vacation_admin_service.py` | Internal updates |
| Move | `app_rrhh/services/vacation_calculation_service.py` → `apps/api/apps/time_off/services/vacation_calculation_service.py` | Internal updates |
| Move | `app_rrhh/services/vacation_report_service.py` → `apps/api/apps/time_off/services/vacation_report_service.py` | Internal updates |
| Create | `apps/api/apps/time_off/migrations/__init__.py` | empty |
| Modify | `apps/api/apps/time_off/models/vacaciones.py:14` | post-move: `from ..managers import (...)` → `from .managers import (...)` (relative within new app) |
| Modify | `apps/api/app_rrhh/validators.py:155` | **LR11:** inline `from .models import SolicitudVacaciones` → `from apps.time_off.models import SolicitudVacaciones` |
| Modify | `apps/api/app_rrhh/validators.py:256` | **LR11:** inline `from .models import SolicitudVacaciones` → `from apps.time_off.models import SolicitudVacaciones` |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar bloque `from .vacaciones import (...)` (5 modelos) y entries en `__all__` (5) |
| Modify | `apps/api/app_rrhh/services/__init__.py` | quitar 5 imports de vacation services + 5 entries en `__all__` |
| Modify | `apps/api/app_rrhh/managers/__init__.py` | quitar `from .vacation_managers import (...)` y 5 entries en `__all__` |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.time_off.apps.TimeOffConfig"` a `LOCAL_APPS` (después de payroll, antes de app_rrhh) |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.time_off"` a `packages` |
| Modify (~8 files) | `api/v1/vacaciones/{views,permissions,serializers,filters,validators,tests}.py`, `scripts/seed_vacaciones_*.py` | replace `from app_rrhh.models.vacaciones import (...)` → `from apps.time_off.models import (...)`. Replace `from app_rrhh.services import VacationService` and `from app_rrhh.services.vacation_service import VacationService` → `from apps.time_off.services import VacationService` |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/{identity,organization,employees,contracts,documents,payroll}/migrations/0001_initial.py` (+ 0002 si existe) | regenerated |

**NO se toca en L3.8:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- Split de `SolicitudVacaciones → VacationRequest + VacationBalance` (deferido a L3.10)
- `OnboardingEmpleado` modelo (queda en app_rrhh hasta L3.9)
- `app_rrhh/permission_service.py` (queda — usado por vacation_approval_service vía `from app_rrhh.permission_service import PermissionService`)
- `app_rrhh/managers/{contratos_manager.py, usuario_manager.py}` (orphan code post-L3.5/L3.2, cleanup en L3.11)
- `app_rrhh/managers.py` (flat shadow file, dead code)

**Lecciones aplicadas (LR9-LR13):**
- **LR9** (stale `'app_rrhh.X'` strings): pre-move grep confirma **0 hits** — N/A. Defensive check se mantiene.
- **LR10** (sed con single + double quote): aplica defensive en Task 6.
- **LR11** (relative imports `from .models import` en archivos legacy): **SÍ APLICA esta vez.** `app_rrhh/validators.py:155, 256` tiene inline imports de `SolicitudVacaciones`. Task 9 Step 10 los actualiza.
- **LR12** (sequence drop → CREATE → makemigrations → migrate): aplicada en Task 13.
- **LR13** (stale logger-name strings): N/A — los 5 services usan `getLogger(__name__)` (no string literals). Defensive grep en Task 9 Step 11.

**Inventario de inbound FK strings (verificado pre-move):**
- 0 inbound `'X'` references desde modelos en otros apps (verificado por grep)
- 0 stale `'app_rrhh.{vacation-models}'` strings (verificado por grep)
- Same-module FKs preservadas como class refs:
  - `PeriodoVacacional.configuracion = ForeignKey(ConfiguracionVacaciones, ...)`
  - `SolicitudVacaciones.periodo_vacacional = ForeignKey(PeriodoVacacional, ...)`
  - `GoceVacaciones.solicitud_vacaciones = OneToOneField(SolicitudVacaciones, ...)`
  - `GoceVacaciones.periodo_vacacional = ForeignKey(PeriodoVacacional, ...)`
  - `HistorialSolicitudVacaciones.solicitud_vacaciones = ForeignKey(SolicitudVacaciones, ...)`

**Outbound cross-app FKs (verificado pre-move — todos correctos con prefix):**
- `'employees.Empleado'` (múltiples)
- `'organization.Area'` (1)
- `'identity.Usuario'` (múltiples)
- `'contracts.ContratosAdendas'` (línea 177)

**Inventario de imports a actualizar (verificado pre-move, ~13 archivos):**

| Archivo | Línea(s) | Pattern actual | Notas |
|---|---|---|---|
| `app_rrhh/services/vacation_service.py` | 10-15 | multi-line: `from app_rrhh.models.vacaciones import (...)` (4 modelos) | **archivo se mueve** a apps.time_off/services/; cambiar a relative `from ..models import (...)` |
| `app_rrhh/services/vacation_approval_service.py` | 9 | single-line: `from app_rrhh.models.vacaciones import HistorialSolicitudVacaciones, SolicitudVacaciones` | **archivo se mueve**; cambiar a relative `from ..models import (...)` |
| `app_rrhh/services/vacation_admin_service.py` | 13-18 | multi-line: `from app_rrhh.models.vacaciones import (...)` (4 modelos) | **archivo se mueve**; relative |
| `app_rrhh/services/vacation_calculation_service.py` | 14 | single-line: `from app_rrhh.models.vacaciones import ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones` | **archivo se mueve**; relative |
| `app_rrhh/services/vacation_report_service.py` | 12 | single-line: `from app_rrhh.models.vacaciones import GoceVacaciones, PeriodoVacacional, SolicitudVacaciones` | **archivo se mueve**; relative |
| `app_rrhh/validators.py` | 155 | inline (LR11): `from .models import SolicitudVacaciones` | replace con `from apps.time_off.models import SolicitudVacaciones` |
| `app_rrhh/validators.py` | 256 | inline (LR11): `from .models import SolicitudVacaciones` | mismo replace |
| `api/v1/vacaciones/views.py` | 7-12 | multi-line submodule: `from app_rrhh.models.vacaciones import (...)` (5 modelos) | replace path: `from apps.time_off.models import (...)` |
| `api/v1/vacaciones/permissions.py` | 5-10 | multi-line submodule: 5 modelos | replace path |
| `api/v1/vacaciones/serializers.py` | 5-10 | multi-line submodule: 5 modelos | replace path |
| `api/v1/vacaciones/serializers.py` | 12 | service: `from app_rrhh.services import VacationService` | replace: `from apps.time_off.services import VacationService` |
| `api/v1/vacaciones/filters.py` | 8 | single-line submodule: `from app_rrhh.models.vacaciones import ConfiguracionVacaciones, GoceVacaciones, PeriodoVacacional, SolicitudVacaciones` | replace path |
| `api/v1/vacaciones/validators.py` | 7-10 | multi-line submodule: 4 modelos | replace path |
| `api/v1/vacaciones/tests.py` | 10-13 | multi-line submodule: 4 modelos | replace path |
| `scripts/seed_vacaciones_reporte_demo.py` | 13 | single-line submodule: 4 modelos | replace path |
| `scripts/seed_vacaciones_historial_demo.py` | 27-32 | multi-line submodule: 4 modelos | replace path |
| `scripts/seed_vacaciones_historial_demo.py` | 33 | service: `from app_rrhh.services.vacation_service import VacationService` | replace: `from apps.time_off.services import VacationService` |

Adicionales a verificar por grep durante ejecución (Task 9 Step 1 inventario):
- `app_rrhh/{views,serializers,services.py,tests.py,managers.py,managers/}.py` (LR11 defensive)
- `app_rrhh/permission_service.py` (queda en app_rrhh — verifica que no importe vacation models)
- `app_rrhh/management/commands/seed_menu.py`

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.7**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `eadd5730 docs(L3.7): mark L3.7 merged, L3.8 as next in roadmap` o más reciente.

- [ ] **Step 2: Activar venv y confirmar Django 5.2.13**

```bash
source .venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `5.2.13`.

- [ ] **Step 3: Confirmar baseline pytest**

```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

- [ ] **Step 4: Backup bd_vyntia (paranoia)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.8.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.8.dump
```

Expected: dump ~244-500 KB.

- [ ] **Step 5: Crear branch L3.8**

```bash
git checkout -b vyntia/L3.8-timeoff-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.8-time_off.md
git commit -m "docs(L3.8): add time_off app extraction plan"
```

---

## Task 3: Crear estructura `apps/time_off/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/time_off/models
mkdir -p apps/api/apps/time_off/services
mkdir -p apps/api/apps/time_off/migrations
touch apps/api/apps/time_off/__init__.py
touch apps/api/apps/time_off/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/time_off/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.time_off` Django app — VYNTIA vacations & leave management.

Owns the time-off and vacation entities of the HR system:
- ConfiguracionVacaciones (per-area/employee/cargo vacation rules: days/year, accrual,
  approval levels, fragmentation policy)
- PeriodoVacacional (annual vacation period per employee with corresponding/used/pending days)
- SolicitudVacaciones (vacation request workflow: borrador → enviada → aprobada → en_goce → finalizada)
- GoceVacaciones (actual vacation enjoyment record with start/end dates and interruptions)
- HistorialSolicitudVacaciones (audit trail of all state transitions on requests)

Owned services (vacation workflow engines):
- vacation_service.py — main vacation request orchestration
- vacation_approval_service.py — jefe + RRHH approval workflow
- vacation_admin_service.py — configuracion/periodo CRUD
- vacation_calculation_service.py — periodo creation, day calculation, advances
- vacation_report_service.py — historical reports and summaries

Owned managers (custom QuerySet methods):
- ConfiguracionVacacionesManager, PeriodoVacacionalManager, SolicitudVacacionesManager,
  GoceVacacionesManager, HistorialSolicitudVacacionesManager (in managers.py)

Bounded context boundary: time_off owns the vacation entitlement, request workflow,
and enjoyment tracking. Personal data lives in `apps.employees`, contract data in
`apps.contracts`, and approval permissions still go through `app_rrhh.permission_service`
(deferred legacy module).

Future split (deferred to L3.10):
- SolicitudVacaciones → VacationRequest + VacationBalance (model split + data migration)

Future rename (deferred to L3.10):
- ConfiguracionVacaciones → VacationPolicy
- PeriodoVacacional → VacationPeriod
- SolicitudVacaciones → VacationRequest
- GoceVacaciones → VacationLeave
- HistorialSolicitudVacaciones → VacationRequestHistory
"""

from django.apps import AppConfig


class TimeOffConfig(AppConfig):
    name = "apps.time_off"
    label = "time_off"
    verbose_name = "VYNTIA Time Off"
```

- [ ] **Step 3: Crear placeholder `apps/time_off/models/__init__.py`**

```python
"""Time off models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

- [ ] **Step 4: Crear placeholder `apps/time_off/services/__init__.py`**

```python
"""Time off services — re-exports for backward-compatible imports.

Populated when services are physically moved.
"""
```

---

## Task 4: Mover los 7 archivos con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` el archivo de modelos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/vacaciones.py apps/api/apps/time_off/models/vacaciones.py
```

- [ ] **Step 3: `git mv` el archivo de managers (a single file plano, no package)**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/managers/vacation_managers.py apps/api/apps/time_off/managers.py
```

- [ ] **Step 4: `git mv` los 5 services**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/services/vacation_service.py apps/api/apps/time_off/services/vacation_service.py
git mv apps/api/app_rrhh/services/vacation_approval_service.py apps/api/apps/time_off/services/vacation_approval_service.py
git mv apps/api/app_rrhh/services/vacation_admin_service.py apps/api/apps/time_off/services/vacation_admin_service.py
git mv apps/api/app_rrhh/services/vacation_calculation_service.py apps/api/apps/time_off/services/vacation_calculation_service.py
git mv apps/api/app_rrhh/services/vacation_report_service.py apps/api/apps/time_off/services/vacation_report_service.py
```

- [ ] **Step 5: Verificar layout**

```bash
ls apps/api/apps/time_off/
ls apps/api/apps/time_off/models/
ls apps/api/apps/time_off/services/
echo "---"
ls apps/api/app_rrhh/models/vacaciones.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/managers/vacation_managers.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/vacation_*.py 2>&1 || echo "OK: removed"
```

Expected: 1 model file + `__init__.py` en time_off/models/. 5 service files + `__init__.py` en time_off/services/. `managers.py` (flat) + `apps.py` + `__init__.py` en time_off/. 7 originales removidos.

---

## Task 5: Verify FK strings DENTRO de los archivos movidos (no editar)

`vacaciones.py` y los 5 services usan strings lazy correctos cross-app y class refs same-module. Verificar:

- [ ] **Step 1: Verificar FKs salientes en `apps/time_off/models/vacaciones.py`**

```bash
cd D:/VYNTIA/apps/api
echo "=== Cross-app lazy FKs en vacaciones.py ==="
grep -n "ForeignKey\|OneToOneField" apps/time_off/models/vacaciones.py | head -30
echo ""
echo "=== Bare cross-app strings — should be 0 ==="
grep -rn "'Empleado'\b\|\"Empleado\"\|'Usuario'\b\|\"Usuario\"\|'Area'\b\|\"Area\"\|'ContratosAdendas'\b\|\"ContratosAdendas\"" apps/time_off/models/ --include="*.py" || echo "OK: cero"
cd ../..
```

Expected:
- Cross-app FKs usan prefixed lazy strings: `'employees.Empleado'`, `'organization.Area'`, `'identity.Usuario'`, `'contracts.ContratosAdendas'`
- Same-module FKs son class refs (ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones — sin quotes)
- "OK: cero" para bare cross-app strings

- [ ] **Step 2: Verificar `from ..managers import` aún existe en línea 14 (será actualizada en Task 8)**

```bash
grep -n "from \.\.managers import\|from \.managers import" apps/api/apps/time_off/models/vacaciones.py
```

Expected: 1 hit `from ..managers import (...)` (still pointing to OLD relative path — Task 8 fixes it).

---

## Task 6: Update FK strings entrantes (LR9 defensive — N/A)

Pre-move grep verificado: 0 stale refs. Defensive sed se mantiene.

- [ ] **Step 1: Bulk sed defensivo (single + double quote — LR10)**

```bash
cd D:/VYNTIA/apps/api
find apps -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/time_off/*" -print0 | xargs -0 sed -i \
  -e "s|'app_rrhh\.ConfiguracionVacaciones'|'time_off.ConfiguracionVacaciones'|g" \
  -e 's|"app_rrhh\.ConfiguracionVacaciones"|"time_off.ConfiguracionVacaciones"|g' \
  -e "s|'app_rrhh\.PeriodoVacacional'|'time_off.PeriodoVacacional'|g" \
  -e 's|"app_rrhh\.PeriodoVacacional"|"time_off.PeriodoVacacional"|g' \
  -e "s|'app_rrhh\.SolicitudVacaciones'|'time_off.SolicitudVacaciones'|g" \
  -e 's|"app_rrhh\.SolicitudVacaciones"|"time_off.SolicitudVacaciones"|g' \
  -e "s|'app_rrhh\.GoceVacaciones'|'time_off.GoceVacaciones'|g" \
  -e 's|"app_rrhh\.GoceVacaciones"|"time_off.GoceVacaciones"|g' \
  -e "s|'app_rrhh\.HistorialSolicitudVacaciones'|'time_off.HistorialSolicitudVacaciones'|g" \
  -e 's|"app_rrhh\.HistorialSolicitudVacaciones"|"time_off.HistorialSolicitudVacaciones"|g'
cd ../..
```

- [ ] **Step 2: Verify (defensive — esperado: 0 hits)**

```bash
cd D:/VYNTIA/apps/api
echo "=== time_off.X refs (expected: 0 — N/A) ==="
grep -rn "'time_off\.\(ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\)'\|\"time_off\." apps --include="*.py" || echo "OK: cero (N/A)"
echo ""
echo "=== Stale 'app_rrhh.X' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.\(ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\)'" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

- [ ] **Step 3: Bare-string sanity check**

```bash
cd D:/VYNTIA/apps/api
grep -rn "'ConfiguracionVacaciones'\b\|\"ConfiguracionVacaciones\"\|'PeriodoVacacional'\b\|\"PeriodoVacacional\"\|'SolicitudVacaciones'\b\|\"SolicitudVacaciones\"\|'GoceVacaciones'\b\|\"GoceVacaciones\"\|'HistorialSolicitudVacaciones'\b\|\"HistorialSolicitudVacaciones\"" apps app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`.

---

## Task 7: Crear `apps/time_off/models/__init__.py` con re-exports

Use Write tool en `apps/api/apps/time_off/models/__init__.py`:

```python
"""Time off models — re-exports for backward-compatible imports."""

from .vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)

__all__ = [
    "ConfiguracionVacaciones",
    "GoceVacaciones",
    "HistorialSolicitudVacaciones",
    "PeriodoVacacional",
    "SolicitudVacaciones",
]
```

- [ ] **Smoke parse check (app no registrada todavía)**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/time_off/models/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/time_off/models/vacaciones.py').read()); print('OK parse vacaciones')"
python -c "import ast; ast.parse(open('apps/time_off/managers.py').read()); print('OK parse managers')"
cd ../..
```

Expected: 3x `OK parse`.

---

## Task 8: Update internal imports en archivos movidos

### Step 1: Update `apps/time_off/models/vacaciones.py:14` — relative manager import

El `from ..managers import (...)` actual apunta a OLD `app_rrhh/managers/`. Después del move, los managers viven en `apps/time_off/managers.py`. Cambiar a relative within new app: `from .managers import (...)`.

Use Edit tool en `apps/api/apps/time_off/models/vacaciones.py`:
- old_string:
```python
from ..managers import (
    ConfiguracionVacacionesManager,
    PeriodoVacacionalManager,
    SolicitudVacacionesManager,
    GoceVacacionesManager,
    HistorialSolicitudVacacionesManager
)
```
- new_string:
```python
from .managers import (
    ConfiguracionVacacionesManager,
    PeriodoVacacionalManager,
    SolicitudVacacionesManager,
    GoceVacacionesManager,
    HistorialSolicitudVacacionesManager
)
```

NOTE: `..managers` viene de cuando vacaciones.py vivía en `app_rrhh/models/`, donde `..` apunta a `app_rrhh/` y `managers` era el package. Después del move: vacaciones.py vive en `apps/time_off/models/`, donde `..` apunta a `apps/time_off/` y `managers` es ahora un single-file module — el import cambia de `..managers` a `.managers` (la diferencia: ahora ES same-app).

Wait, mejor explicación: Post-move, `apps/time_off/models/vacaciones.py` está dentro de `apps/time_off/models/`. El `.managers` es relative a `apps/time_off/models/__init__.py`'s package, que SÍ tiene un `..managers` apuntando a `apps/time_off/managers.py`. Pero también `from .managers import` desde dentro de `apps/time_off/models/vacaciones.py` apuntaría a un archivo `apps/time_off/models/managers.py` que NO existe.

**Corrección:** post-move, el import correcto es `from ..managers import (...)` (sigue siendo `..` porque managers.py vive en `apps/time_off/`, no en `apps/time_off/models/`). NO cambiar el import — la sintaxis relativa funciona idéntica.

Actualizado: **NO se requiere cambio**. Verificar:

```bash
cd D:/VYNTIA/apps/api
python -c "
import ast
tree = ast.parse(open('apps/time_off/models/vacaciones.py').read())
imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
for imp in imports:
    if isinstance(imp, ast.ImportFrom) and imp.module is None and imp.level == 2:
        print('Found relative import (..managers):', [n.name for n in imp.names])
"
cd ../..
```

Expected: prints `Found relative import (..managers): ['ConfiguracionVacacionesManager', 'PeriodoVacacionalManager', 'SolicitudVacacionesManager', 'GoceVacacionesManager', 'HistorialSolicitudVacacionesManager']`.

**El import relativo `from ..managers import (...)` se preserva tal cual.** Post-move, `..managers` resuelve a `apps/time_off/managers.py` (correctamente). Re-verify after Task 11 (manage.py check).

### Step 2: Update internal imports en los 5 services (cross-app vacation models → relative)

Los 5 services tienen `from app_rrhh.models.vacaciones import (...)`. Después del move, ambos archivos viven en `apps/time_off/`. Cambiar a relative `from ..models import (...)`.

**Archivo 1: `apps/time_off/services/vacation_service.py:10-15`**

Use Edit tool:
- old_string:
```python
from app_rrhh.models.vacaciones import (
    ConfiguracionVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
```
- new_string:
```python
from ..models import (
    ConfiguracionVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
```

**Archivo 2: `apps/time_off/services/vacation_approval_service.py:9`**

Use Edit tool:
- old_string: `from app_rrhh.models.vacaciones import HistorialSolicitudVacaciones, SolicitudVacaciones`
- new_string: `from ..models import HistorialSolicitudVacaciones, SolicitudVacaciones`

NOTE: la línea 10 (`from app_rrhh.permission_service import PermissionService`) **NO se toca** — `permission_service` queda en app_rrhh (out of scope L3.8).

**Archivo 3: `apps/time_off/services/vacation_admin_service.py:13-18`**

Use Edit tool:
- old_string:
```python
from app_rrhh.models.vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
```
- new_string:
```python
from ..models import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
```

**Archivo 4: `apps/time_off/services/vacation_calculation_service.py:14`**

Use Edit tool:
- old_string: `from app_rrhh.models.vacaciones import ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones`
- new_string: `from ..models import ConfiguracionVacaciones, PeriodoVacacional, SolicitudVacaciones`

**Archivo 5: `apps/time_off/services/vacation_report_service.py:12`**

Use Edit tool:
- old_string: `from app_rrhh.models.vacaciones import GoceVacaciones, PeriodoVacacional, SolicitudVacaciones`
- new_string: `from ..models import GoceVacaciones, PeriodoVacacional, SolicitudVacaciones`

### Step 3: Verify all 5 services have updated imports

```bash
cd D:/VYNTIA/apps/api
echo "=== Should be 5 hits with 'from ..models import' ==="
grep -n "from \.\.models import" apps/time_off/services/*.py
echo ""
echo "=== Should be 0 hits with 'from app_rrhh.models' ==="
grep -n "from app_rrhh\.models" apps/time_off/services/*.py || echo "OK: cero"
cd ../..
```

Expected: 5 hits with `from ..models import`, 0 hits with `app_rrhh.models`.

### Step 4: Crear `apps/time_off/services/__init__.py` con re-exports

Use Write tool:

```python
"""Time off services — re-exports for backward-compatible imports.

Vacation workflow engines.
"""

from .vacation_admin_service import VacationAdminService
from .vacation_approval_service import VacationApprovalService
from .vacation_calculation_service import VacationCalculationService
from .vacation_report_service import VacationReportService
from .vacation_service import VacationService

__all__ = [
    "VacationAdminService",
    "VacationApprovalService",
    "VacationCalculationService",
    "VacationReportService",
    "VacationService",
]
```

### Step 5: Smoke parse check (5 services + __init__)

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/time_off/services/__init__.py').read()); print('OK parse __init__')"
for f in vacation_service vacation_approval_service vacation_admin_service vacation_calculation_service vacation_report_service; do
  python -c "import ast; ast.parse(open('apps/time_off/services/$f.py').read()); print('OK parse $f')"
done
cd ../..
```

Expected: 6x `OK parse`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern A:** `from app_rrhh.models.vacaciones import (...)` → `from apps.time_off.models import (...)`
**Pattern B:** `from app_rrhh.services import VacationService` y `from app_rrhh.services.vacation_service import VacationService` → `from apps.time_off.services import VacationService`

- [ ] **Step 1: Inventario completo (incluye LR11 + LR13 defensive)**

```bash
cd D:/VYNTIA/apps/api
echo "=== ABSOLUTE imports model (~9 expected) ==="
grep -rn "from app_rrhh\.models\.vacaciones import\|from app_rrhh\.models import.*\(ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations | sort
echo ""
echo "=== ABSOLUTE imports services (~2 expected) ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "VacationService|VacationApprovalService|VacationAdminService|VacationCalculationService|VacationReportService|vacation_service|vacation_approval_service|vacation_admin_service|vacation_calculation_service|vacation_report_service" | sort
echo ""
echo "=== LR11 — RELATIVE imports en app_rrhh/*.py (validators.py expected: 2 hits) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" | sort
echo ""
echo "=== LR13 — Stale logger-name strings (expected: 0) ==="
grep -rn "logger=['\"]app_rrhh\.services\.vacation\|getLogger(['\"]app_rrhh\.services\.vacation" --include="*.py" || echo "OK: cero (LR13 N/A)"
cd ../..
```

Expected: ~9 model imports, 2 service imports, 2 LR11 hits in `app_rrhh/validators.py`, LR13 OK.

- [ ] **Step 2: Sed for submodule path imports (Pattern A — most common)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/time_off/*" \
  -print0 | xargs -0 sed -i \
  -e 's|from app_rrhh\.models\.vacaciones import |from apps.time_off.models import |g'
cd ../..
```

This handles BOTH single-line and multi-line submodule imports (`from app_rrhh.models.vacaciones import (\n    ...,\n)` becomes `from apps.time_off.models import (\n    ...,\n)`).

Verify:
```bash
grep -rn "from app_rrhh\.models\.vacaciones" apps/api --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK: cero"
```

- [ ] **Step 3: Sed for service imports (Pattern B)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/time_off/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.services import \(VacationService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services import \(VacationApprovalService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services import \(VacationAdminService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services import \(VacationCalculationService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services import \(VacationReportService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services\.vacation_service import \(VacationService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services\.vacation_approval_service import \(VacationApprovalService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services\.vacation_admin_service import \(VacationAdminService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services\.vacation_calculation_service import \(VacationCalculationService\)$|from apps.time_off.services import \1|g' \
  -e 's|^from app_rrhh\.services\.vacation_report_service import \(VacationReportService\)$|from apps.time_off.services import \1|g'
cd ../..
```

Verify:
```bash
grep -rn "from app_rrhh\.services" apps/api --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "VacationService|VacationApprovalService|VacationAdminService|VacationCalculationService|VacationReportService|vacation_service|vacation_approval_service|vacation_admin_service|vacation_calculation_service|vacation_report_service" || echo "OK: cero"
```

- [ ] **Step 4: Manual fix mixed-line imports**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.services import.*\(VacationService\|VacationApprovalService\|VacationAdminService\|VacationCalculationService\|VacationReportService\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations | head -10
cd ../..
```

If hits with comma (mixed import line), Read + Edit to split.

Expected: 0 hits (Pattern B sed should have caught the 2 known cases).

- [ ] **Step 5: LR11 — fix `app_rrhh/validators.py:155, 256`**

These 2 inline imports are `from .models import SolicitudVacaciones` (relative). Post-move, SolicitudVacaciones lives in `apps.time_off.models`. The relative `.models` would still try to find it in `app_rrhh.models`, which will fail.

**Edit 1 — line 155 area:**

Read context first:
```bash
sed -n '150,165p' apps/api/app_rrhh/validators.py
```

Use Edit tool en `apps/api/app_rrhh/validators.py`:
- old_string: `        from .models import SolicitudVacaciones`
- new_string: `        from apps.time_off.models import SolicitudVacaciones`

NOTE: this Edit string appears TWICE (lines 155 and 256). Use `replace_all=true` since both need the same replacement:

Use Edit tool:
- old_string: `        from .models import SolicitudVacaciones`
- new_string: `        from apps.time_off.models import SolicitudVacaciones`
- replace_all: true

Verify:
```bash
grep -n "from .models import SolicitudVacaciones\|from apps.time_off.models import SolicitudVacaciones" apps/api/app_rrhh/validators.py
```

Expected: 0 hits `from .models`. 2 hits `from apps.time_off.models import SolicitudVacaciones`.

- [ ] **Step 6: LR11 defensive check across `app_rrhh/`**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero` (after Step 5 fix).

- [ ] **Step 7: LR13 defensive check (logger strings)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "logger=['\"]app_rrhh\.services\.vacation\|getLogger(['\"]app_rrhh\.services\.vacation" --include="*.py" || echo "OK: cero (LR13 N/A — services use __name__)"
cd ../..
```

Expected: `OK: cero`.

- [ ] **Step 8: Self-absolute import check en moved files**

```bash
cd D:/VYNTIA/apps/api
echo "=== Models self-absolute (should be cero) ==="
grep -rn "from apps\.time_off\.models import" apps/time_off/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Services to apps.time_off.models (relative ..models preferred) ==="
grep -rn "from \.\.models\|from apps\.time_off\.models\|from app_rrhh\.models" apps/time_off/services --include="*.py"
cd ../..
```

Expected: 0 self-absolute en models. Services use `from ..models import` (relative — set in Task 8). 0 imports of `app_rrhh.models`.

- [ ] **Step 9: Update `app_rrhh/services/__init__.py` — quitar 5 vacation services**

Read current state:
```bash
cat apps/api/app_rrhh/services/__init__.py
```

Use Edit tool — Edit 1 (remove imports):
- old_string:
```python
# Servicios de vacaciones
from .vacation_admin_service import VacationAdminService
from .vacation_approval_service import VacationApprovalService
from .vacation_calculation_service import VacationCalculationService
from .vacation_report_service import VacationReportService
from .vacation_service import VacationService

__all__ = [
```
- new_string:
```python
__all__ = [
```

Edit 2 (remove from __all__):
- old_string:
```python
__all__ = [
    "VacationService",
    "VacationApprovalService",
    "VacationAdminService",
    "VacationCalculationService",
    "VacationReportService",
]
```
- new_string:
```python
__all__ = []
```

Verify:
```bash
grep -n "vacation\|Vacation" apps/api/app_rrhh/services/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

- [ ] **Step 10: Update `app_rrhh/managers/__init__.py` — quitar 5 vacation managers**

Read current state:
```bash
cat apps/api/app_rrhh/managers/__init__.py
```

Use Edit tool — Edit 1 (remove block import):
- old_string:
```python
from .contratos_manager import ContratosAdendasManager
from .usuario_manager import UsuarioManager
from .vacation_managers import (
    ConfiguracionVacacionesManager,
    PeriodoVacacionalManager,
    SolicitudVacacionesManager,
    GoceVacacionesManager,
    HistorialSolicitudVacacionesManager
)
```
- new_string:
```python
from .contratos_manager import ContratosAdendasManager
from .usuario_manager import UsuarioManager
```

Edit 2 (remove from __all__):
- old_string:
```python
__all__ = [
    'ContratosAdendasManager',
    'UsuarioManager',
    'ConfiguracionVacacionesManager',
    'PeriodoVacacionalManager',
    'SolicitudVacacionesManager',
    'GoceVacacionesManager',
    'HistorialSolicitudVacacionesManager',
]
```
- new_string:
```python
__all__ = [
    'ContratosAdendasManager',
    'UsuarioManager',
]
```

Verify:
```bash
grep -n "vacation\|Vacation" apps/api/app_rrhh/managers/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

- [ ] **Step 11: Verificación final exhaustiva**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models.vacaciones / .models import {vacation-models} ==="
grep -rn "from app_rrhh\.models\.vacaciones\|from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" || echo "OK"
echo ""
echo "=== B: from .vacaciones (relative en app_rrhh) ==="
grep -rn "from \.vacaciones" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: from .models import {vacation-models} (LR11) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" || echo "OK"
echo ""
echo "=== D: from app_rrhh.services {vacation services} (Pattern B) ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "VacationService|VacationApprovalService|VacationAdminService|VacationCalculationService|VacationReportService|vacation_service|vacation_approval_service|vacation_admin_service|vacation_calculation_service|vacation_report_service" || echo "OK"
echo ""
echo "=== E: bare 'X' / \"X\" en app_rrhh non-migrations ==="
grep -rn "'ConfiguracionVacaciones'\b\|\"ConfiguracionVacaciones\"\|'PeriodoVacacional'\b\|\"PeriodoVacacional\"\|'SolicitudVacaciones'\b\|\"SolicitudVacaciones\"\|'GoceVacaciones'\b\|\"GoceVacaciones\"\|'HistorialSolicitudVacaciones'\b\|\"HistorialSolicitudVacaciones\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: stale 'app_rrhh.X' anywhere LR9 ==="
grep -rn "'app_rrhh\.\(ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\)'" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== G: from app_rrhh.managers (vacation managers) ==="
grep -rn "from app_rrhh\.managers" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ConfiguracionVacacionesManager|PeriodoVacacionalManager|SolicitudVacacionesManager|GoceVacacionesManager|HistorialSolicitudVacacionesManager" || echo "OK"
echo ""
echo "=== H: LR13 logger strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.vacation\|getLogger(['\"]app_rrhh\.services\.vacation" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 10: Update `app_rrhh/models/__init__.py` — quitar exports

- [ ] **Step 1: Read current state**

```bash
sed -n '1,40p' apps/api/app_rrhh/models/__init__.py
```

Verify lines:
- Block `from .vacaciones import (\n    ConfiguracionVacaciones,\n    GoceVacaciones,\n    HistorialSolicitudVacaciones,\n    PeriodoVacacional,\n    SolicitudVacaciones,\n)` (líneas ~12-17)
- 5 `__all__` entries

- [ ] **Step 2: Use Edit tool — remove import block**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string:
```python
from .vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
```
- new_string: (empty — the entire block is removed)

- [ ] **Step 3: Use Edit tool — remove 5 `__all__` entries**

Read first to see exact format:
```bash
sed -n '15,40p' apps/api/app_rrhh/models/__init__.py
```

Then Edit (use surrounding lines for uniqueness):

old_string (probable):
```python
    # Modelos de vacaciones
    "ConfiguracionVacaciones",
    "PeriodoVacacional",
    "SolicitudVacaciones",
    "GoceVacaciones",
    "HistorialSolicitudVacaciones",
```
new_string: (empty — delete the comment header + 5 entries)

- [ ] **Step 4: Verificar limpieza**

```bash
grep -n "ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\|vacaciones" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

---

## Task 11: Update settings — registrar `TimeOffConfig`

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payroll.apps.PayrollConfig",
    "app_rrhh",
]
```
- new_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payroll.apps.PayrollConfig",
    "apps.time_off.apps.TimeOffConfig",
    "app_rrhh",
]
```

Verify:
```bash
grep -A 10 "LOCAL_APPS = \[" apps/api/vyntia/settings/base.py
```

---

## Task 12: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Expected current: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll"]`

Use Edit tool:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll", "apps.time_off"]`

Reinstall:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`.

Smoke check:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

If fails con ImportError, **investigar** — algún import o legacy file no fue actualizado.

---

## Task 13: NUCLEAR DB regenerate (LR12 sequence)

- [ ] **Step 1: Drop bd_vyntia (kill procs first)**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

- [ ] **Step 2: CREATE bd_vyntia (LR12 — antes de makemigrations)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

- [ ] **Step 3: Eliminar migration files existentes**

```bash
cd D:/VYNTIA/apps/api/app_rrhh/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/identity/migrations
git rm 0001_initial.py 2>&1 | tail -2

cd D:/VYNTIA/apps/api/apps/organization/migrations
git rm 0001_initial.py 2>&1 | tail -2

cd D:/VYNTIA/apps/api/apps/employees/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/contracts/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/documents/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA/apps/api/apps/payroll/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"

cd D:/VYNTIA
```

NOTE: NO se borra `apps/time_off/migrations/` (solo contiene `__init__.py` empty).

- [ ] **Step 4: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -30
cd ../..
```

Expected migrations for: app_rrhh (without vacation models — only OnboardingEmpleado), identity, organization, employees, contracts, documents, payroll, **time_off (with 5 models — NEW)**.

Verify:
```bash
echo "=== time_off 0001 (expected: 5 model definitions) ==="
grep -E "name='(ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones)'" apps/api/apps/time_off/migrations/0001_initial.py | wc -l
echo "=== app_rrhh 0001 (expected: 0 vacation models) ==="
grep -E "name='(ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones)'" apps/api/app_rrhh/migrations/0001_initial.py | wc -l
```

Expected: `5` y `0`.

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: sequence `Applying X.0001_initial... OK` para todos los apps. Sin errors.

---

## Task 14: Re-seed

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Verify counts:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'configuracion_vacaciones', COUNT(*) FROM configuracion_vacaciones UNION ALL SELECT 'periodos_vacacionales', COUNT(*) FROM periodos_vacacionales UNION ALL SELECT 'solicitudes_vacaciones', COUNT(*) FROM solicitudes_vacaciones;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, vacation tables = 0.

---

## Task 15: Smoke tests

- [ ] **Step 1: Django check + pytest baseline**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected:
- check: `System check identified no issues (0 silenced).`
- pytest: `125 passed, 44 failed, 3 skipped` — baseline preservado

- [ ] **Step 2: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l38.log 2>&1 &
SERVER_PID=$!
sleep 8
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: `HTTP 200 /api/docs/`.

- [ ] **Step 3: Cleanup greps finales (8 patterns)**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models.vacaciones / .models import {vacation-models} ==="
grep -rn "from app_rrhh\.models\.vacaciones\|from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" || echo "OK"
echo ""
echo "=== B: from .vacaciones (relative en app_rrhh) ==="
grep -rn "from \.vacaciones" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: bare 'X' en app_rrhh non-migrations ==="
grep -rn "'ConfiguracionVacaciones'\b\|\"ConfiguracionVacaciones\"\|'PeriodoVacacional'\b\|\"PeriodoVacacional\"\|'SolicitudVacaciones'\b\|\"SolicitudVacaciones\"\|'GoceVacaciones'\b\|\"GoceVacaciones\"\|'HistorialSolicitudVacaciones'\b\|\"HistorialSolicitudVacaciones\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== D: from app_rrhh.services {vacation services} ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "VacationService|VacationApprovalService|VacationAdminService|VacationCalculationService|VacationReportService|vacation_service|vacation_approval_service|vacation_admin_service|vacation_calculation_service|vacation_report_service" || echo "OK"
echo ""
echo "=== E: stale 'app_rrhh.X' (LR9) ==="
grep -rn "'app_rrhh\.\(ConfiguracionVacaciones\|PeriodoVacacional\|SolicitudVacaciones\|GoceVacaciones\|HistorialSolicitudVacaciones\)'" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: from app_rrhh.managers (vacation managers) ==="
grep -rn "from app_rrhh\.managers" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "ConfiguracionVacacionesManager|PeriodoVacacionalManager|SolicitudVacacionesManager|GoceVacacionesManager|HistorialSolicitudVacacionesManager" || echo "OK"
echo ""
echo "=== G: LR11 from .models import (relative in app_rrhh) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "ConfiguracionVacaciones|PeriodoVacacional|SolicitudVacaciones|GoceVacaciones|HistorialSolicitudVacaciones" || echo "OK"
echo ""
echo "=== H: LR13 logger strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.vacation\|getLogger(['\"]app_rrhh\.services\.vacation" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 16: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -50
git add apps/api/
git commit -m "chore(L3.8): extract time_off app (5 vacation models + 5 services + active managers) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.8-timeoff-app ^master | head -5
git status --short
```

Expected: 2 commits, working tree empty.

---

## Task 17: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.8-timeoff-app -m "Merge L3.8: extract time_off app (5 vacation models + 5 services + active managers)"
git log --oneline -5
```

- [ ] **Step 3: Smoke test post-merge**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: ambos verdes con baseline 125/44/3.

- [ ] **Step 4: Update roadmap + memoria post-merge**

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` Status column: L3.8 → ✅ con merge SHA. L3.9 → ⏳ NEXT.

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.8): mark L3.8 merged, L3.9 as next in roadmap"
```

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/time_off/{__init__.py, apps.py, managers.py, models/{__init__.py, vacaciones.py}, services/{__init__.py, 5 service files}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/vacaciones.py` removido
- [ ] `app_rrhh/services/vacation_*.py` (5 files) removidos
- [ ] `app_rrhh/managers/vacation_managers.py` removido
- [ ] LR11 fix: `app_rrhh/validators.py:155, 256` actualizadas a `from apps.time_off.models import SolicitudVacaciones`
- [ ] `app_rrhh/services/__init__.py` no exporta vacation services
- [ ] `app_rrhh/managers/__init__.py` no exporta vacation managers
- [ ] `apps/time_off/services/__init__.py` exporta los 5 services
- [ ] LOCAL_APPS incluye `TimeOffConfig`; pyproject incluye `apps.time_off`
- [ ] LR12 fix: makemigrations corrió DESPUÉS de CREATE DATABASE
- [ ] Migrations regenerated; time_off con 5 modelos; app_rrhh sin ellos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] All 8 cleanup greps OK (A-H)
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.8 ✅, L3.9 NEXT

---

## Después de L3.8

**Próximo plan:** L3.9 — extract `onboarding` app (`OnboardingEmpleado` modelo + `onboarding_service.py`).

L3.9 será el sub-PR más pequeño: 1 modelo + 1 service. Es el último sub-PR de extracción antes del rename masivo en L3.10.

---

## Notas para el ejecutor

- **Patrón NUCLEAR + LR12 sequence** — drop → CREATE → makemigrations → migrate.
- **PGPASSWORD env var** explícito por known issue.
- **Class names en español** — rename inglés en L3.10. Split `SolicitudVacaciones → VacationRequest + VacationBalance` también deferido.
- **Sub-PR con más componentes hasta ahora**: 5 modelos + 5 services + active managers (1 archivo). Sub-PR de "alto riesgo" per roadmap.
- **Active managers** — primer sub-PR donde los managers no son orphan. Se mueven juntos a `apps/time_off/managers.py` (single file plano). Verificar import relativo `from ..managers` en vacaciones.py post-move.
- **LR11 SÍ APLICA esta vez** — `app_rrhh/validators.py:155, 256` tiene 2 inline imports a actualizar. Task 9 Step 5 dedicado.
- **`app_rrhh/permission_service.py` queda en app_rrhh** — `vacation_approval_service.py` lo importa vía `from app_rrhh.permission_service import PermissionService`. Out of scope L3.8 (cleanup en L3.11 o sub-fase posterior).
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
- **NO se toca `app_rrhh/managers.py` (flat shadow file)** — dead code, cleanup en L3.11.
