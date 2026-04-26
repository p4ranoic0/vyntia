# VYNTIA Foundation L3.9 — Extract `onboarding` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer el último modelo de dominio (`OnboardingEmpleado`) **y su service** (`onboarding_service.py` ~581 líneas, contiene `OnboardingService` + `OnboardingNotificationService`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/onboarding/`. Class names quedan en español — el rename a inglés (`OnboardingEmpleado → OnboardingProcess`) es L3.10.

**Architecture:** L3.9 es **el último sub-PR de extracción** antes del rename masivo en L3.10. Solo 1 modelo + 1 service file, pero el service tiene **muchos consumers**: ~10 inline (in-method) imports de `OnboardingService` y `OnboardingNotificationService` en `api/v1/rrhh/views.py`, 2 en `api/v1/rrhh/serializers.py`, 3 en tests, y 1 en conftest. **LR14 aplica** porque hay 2 multi-line parenthesized blocks `from app_rrhh.services.onboarding_service import (\nOnboardingNotificationService,\nOnboardingService,\n)` en views.py que sed no captura. Después de este merge, `app_rrhh/models/__init__.py` queda vacío (`__all__ = []`) — el último modelo de dominio se ha ido.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy, Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.9; § 3.2 "División de modelos" (`onboarding.py → OnboardingProcess`); § 3.3 "Mapeo de services" (`onboarding_service.py → onboarding`)

**Scope decision (alineada con L3.1-L3.8 pattern):**
- Class names en español; rename a inglés (`OnboardingEmpleado → OnboardingProcess`, `OnboardingService → OnboardingProcessService`) en L3.10
- `OnboardingNotificationService` (segunda clase en mismo archivo) se mueve junto con `OnboardingService` — son del mismo dominio
- `app_rrhh/tasks.py` (Celery tasks) **queda en app_rrhh** — usado por `send_email_html_task.apply_async()` en `onboarding_service.py:10`. El import `from app_rrhh.tasks import send_email_html_task` debe preservarse post-move (continúa funcionando como absolute import)
- `app_rrhh/services/empleado_report_service.py` — pertenece a `employees` app per spec § 3.3 pero L3.4 lo difirió. Sigue out of scope (cleanup en L3.11)

**Pre-condiciones:**
- L3.8 mergeada a master (commit `87420769`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization,employees,contracts,documents,payroll,time_off}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/onboarding/` existe con `apps.py`, `models/`, `services/`, `migrations/`
- [ ] Modelo `OnboardingEmpleado` movido a `apps/onboarding/models/onboarding.py`
- [ ] Service `onboarding_service.py` (con `OnboardingService` + `OnboardingNotificationService`) movido a `apps/onboarding/services/onboarding_service.py`
- [ ] `app_rrhh/models/onboarding.py` eliminado
- [ ] `app_rrhh/services/onboarding_service.py` eliminado
- [ ] `OnboardingConfig` en `LOCAL_APPS`
- [ ] **Internal updates en archivos movidos:**
  - `apps/onboarding/models/onboarding.py:103` inline import `from apps.documents.models import DocumentosDigitales` preservado (ya correcto post-L3.6)
  - `apps/onboarding/services/onboarding_service.py:6` `from app_rrhh.models import OnboardingEmpleado` → `from ..models import OnboardingEmpleado` (relative within new same-app)
  - `apps/onboarding/services/onboarding_service.py:10` `from app_rrhh.tasks import send_email_html_task` PRESERVADO (tasks.py queda en app_rrhh)
- [ ] FK strings cross-app (`'employees.Empleado'`, `'identity.Usuario'`) preservados (ya correctos pre-move)
- [ ] **LR9 defensive check:** 0 stale `'app_rrhh.OnboardingEmpleado'` strings (verified pre-move N/A)
- [ ] **LR10 defensive sed:** procesa single + double quote
- [ ] **LR11 defensive check:** 0 relative `from .models import OnboardingEmpleado` en `app_rrhh/*.py` (verified pre-move N/A)
- [ ] **LR13 N/A:** `onboarding_service.py:17` usa `getLogger(__name__)` (auto-resolve, no string literal)
- [ ] **LR14 fix:** 2 multi-line `from app_rrhh.services.onboarding_service import (\nOnboardingNotificationService,\nOnboardingService,\n)` blocks en `api/v1/rrhh/views.py:2449-2452, 2530-2533` actualizados manualmente
- [ ] `app_rrhh/models/__init__.py` queda con `__all__ = []` (último modelo de dominio extraído)
- [ ] `apps/onboarding/services/__init__.py` exporta `OnboardingService` + `OnboardingNotificationService`
- [ ] Imports actualizados across ~6 archivos (views.py + serializers.py + 3 tests + conftest)
- [ ] Migraciones regeneradas: app_rrhh sin OnboardingEmpleado; onboarding con 1 modelo
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] `pyproject.toml` `packages` incluye `"apps.onboarding"`
- [ ] **LR12 sequence:** drop → CREATE bd_vyntia → makemigrations → migrate
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.9-onboarding-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/onboarding/__init__.py` | empty |
| Create | `apps/api/apps/onboarding/apps.py` | `OnboardingConfig(AppConfig)` con `name="apps.onboarding"`, `label="onboarding"` |
| Create | `apps/api/apps/onboarding/models/__init__.py` | re-exporta el modelo |
| Create | `apps/api/apps/onboarding/services/__init__.py` | re-exporta los 2 service classes |
| Move | `app_rrhh/models/onboarding.py` → `apps/api/apps/onboarding/models/onboarding.py` | 1 modelo. FKs salientes ya correctos (`'employees.Empleado'`, `'identity.Usuario'`); inline import L103 a `apps.documents.models` ya correcto |
| Move | `app_rrhh/services/onboarding_service.py` → `apps/api/apps/onboarding/services/onboarding_service.py` | Internal `from app_rrhh.models import OnboardingEmpleado` → `from ..models import OnboardingEmpleado`. `from app_rrhh.tasks import send_email_html_task` PRESERVADO |
| Create | `apps/api/apps/onboarding/migrations/__init__.py` | empty |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar `from .onboarding import OnboardingEmpleado` y entry `"OnboardingEmpleado"` en `__all__`. Resultado: `__all__ = []` (vacío post-L3.9) |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.onboarding.apps.OnboardingConfig"` a `LOCAL_APPS` (después de time_off, antes de app_rrhh) |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.onboarding"` a `packages` |
| Modify (~6 files) | `api/v1/rrhh/{views,serializers}.py`, `tests/{test_onboarding_service,test_onboarding_api,conftest}.py` | replace `from app_rrhh.models import OnboardingEmpleado` → `from apps.onboarding.models import OnboardingEmpleado`. Replace `from app_rrhh.services.onboarding_service import (OnboardingService\|OnboardingNotificationService)` → `from apps.onboarding.services import ...`. Multi-line blocks en `views.py:2449-2452, 2530-2533` requieren fix manual (LR14) |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` + `0003_initial.py` | regenerated |
| Delete | `apps/{identity,organization,employees,contracts,documents,payroll,time_off}/migrations/0001_initial.py` (+ 0002 si existe) | regenerated |

**NO se toca en L3.9:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- `app_rrhh/tasks.py` (Celery — queda hasta L3.11 cleanup)
- `app_rrhh/services/empleado_report_service.py` (employees app per spec, deferred)
- `app_rrhh/permission_service.py` (sigue siendo usado por vacation_approval, deferred)
- `app_rrhh/managers/{contratos_manager,usuario_manager}.py` (orphan post-L3.5/L3.2)
- `app_rrhh/managers.py`, `app_rrhh/models.py` (flat shadow files, dead code)
- `app_rrhh/validators.py` (queda — usado por validations en otros lugares)

**Lecciones aplicadas (LR9-LR14):**
- **LR9** (stale `'app_rrhh.X'` strings): pre-move grep confirma **0 hits** — N/A. Defensive check.
- **LR10** (sed con single + double quote): defensive en Task 6.
- **LR11** (relative imports en archivos legacy): pre-move grep en `app_rrhh/*.py` esperado **0 hits** — N/A. Defensive check.
- **LR12** (sequence drop → CREATE → makemigrations → migrate): aplicada en Task 13.
- **LR13** N/A: `onboarding_service.py:17` usa `getLogger(__name__)` (no string literal).
- **LR14 SÍ APLICA**: 2 multi-line `from app_rrhh.services.onboarding_service import (\n...,\n)` blocks en `api/v1/rrhh/views.py`. Sed solo captura single-line — Task 9 incluye step explícito de manual fix.

**Inventario de inbound FK strings (verificado pre-move):**
- 0 inbound `'OnboardingEmpleado'` references desde modelos en otros apps
- 0 stale `'app_rrhh.OnboardingEmpleado'` strings

**Inventario de imports a actualizar (verificado pre-move, ~6 archivos):**

| Archivo | Línea(s) | Pattern actual | Notas |
|---|---|---|---|
| `app_rrhh/services/onboarding_service.py` | 6 | single-line: `from app_rrhh.models import OnboardingEmpleado` | **archivo se mueve**; cambiar a relative `from ..models import OnboardingEmpleado` |
| `app_rrhh/services/onboarding_service.py` | 10 | single-line: `from app_rrhh.tasks import send_email_html_task` | **PRESERVADO** — tasks.py queda en app_rrhh, absolute import sigue funcionando post-move |
| `tests/conftest.py` | 15 | single-line: `from app_rrhh.models import OnboardingEmpleado` | replace módulo |
| `tests/test_onboarding_service.py` | 13 | single-line: `from app_rrhh.models import OnboardingEmpleado` | replace módulo |
| `tests/test_onboarding_service.py` | 14 | single-line submodule: `from app_rrhh.services.onboarding_service import OnboardingService` | replace path |
| `tests/test_onboarding_api.py` | 14 | single-line mixto: `from app_rrhh.models import DocumentosDigitales, OnboardingEmpleado` (post-L3.6 verificar — DocumentosDigitales ya está en apps.documents) | **debe estar ya** `from app_rrhh.models import OnboardingEmpleado` después de L3.6 fix-up. Verificar pre-edit. |
| `api/v1/rrhh/views.py` | 9 | single-line: `from app_rrhh.models import OnboardingEmpleado` | replace módulo |
| `api/v1/rrhh/views.py` | 2395, 2421, 2499, 2571, 2594, 2624, 2650, 2716 | inline (in-method): `from app_rrhh.services.onboarding_service import OnboardingService` | replace path (sed handles whitespace-prefix single-line) |
| `api/v1/rrhh/views.py` | 2449-2452 | **LR14 multi-line**: `from app_rrhh.services.onboarding_service import (\nOnboardingNotificationService,\nOnboardingService,\n)` | **manual fix** — sed no captura |
| `api/v1/rrhh/views.py` | 2530-2533 | **LR14 multi-line**: same pattern | **manual fix** |
| `api/v1/rrhh/serializers.py` | 6 | single-line: `from app_rrhh.models import OnboardingEmpleado` | replace módulo |
| `api/v1/rrhh/serializers.py` | 1266, 1301 | inline single-line: `from app_rrhh.services.onboarding_service import OnboardingService` | replace path |

Adicionales a verificar por grep durante ejecución (Task 9 Step 1 inventario):
- `app_rrhh/{views,serializers,services.py,tests.py,managers.py}.py` (LR11 defensive)
- `app_rrhh/management/commands/` (puede tener imports)

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.8**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `0c4a5c7a docs(L3.8): mark L3.8 merged, L3.9 as next; document LR14 multi-line service sed lesson` o más reciente.

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.9.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.9.dump
```

Expected: dump ~244-500 KB.

- [ ] **Step 5: Crear branch L3.9**

```bash
git checkout -b vyntia/L3.9-onboarding-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.9-onboarding.md
git commit -m "docs(L3.9): add onboarding app extraction plan"
```

---

## Task 3: Crear estructura `apps/onboarding/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/onboarding/models
mkdir -p apps/api/apps/onboarding/services
mkdir -p apps/api/apps/onboarding/migrations
touch apps/api/apps/onboarding/__init__.py
touch apps/api/apps/onboarding/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/onboarding/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.onboarding` Django app — VYNTIA new-employee onboarding.

Owns the onboarding workflow:
- OnboardingEmpleado (per-employee onboarding state machine: pendiente_datos →
  pendiente_documentos → pendiente_validacion → completado/observado)
  - Tracks completeness checklist: datos_personales, datos_laborales, dni,
    declaraciones_juradas, certificados_academicos, certificados_trabajo,
    documentos_familiares
  - Tracks RRHH validation, welcome-email status, completion timestamps

Owned services (onboarding orchestration):
- onboarding_service.py — contains:
  - OnboardingService: main workflow (crear_onboarding_completo, actualizar_estado_onboarding,
    obtener_documentos_pendientes, reenviar_email_bienvenida, etc.)
  - OnboardingNotificationService: email notifications + status change events

Bounded context boundary: onboarding owns the new-employee setup workflow and
its state machine. Personal data lives in `apps.employees`, document storage
in `apps.documents`. The Celery task `send_email_html_task` lives in
`app_rrhh.tasks` (deferred legacy module — used by both onboarding_service
and other email-sending paths; will be relocated in L3.11 cleanup).

Future rename (deferred to L3.10):
- OnboardingEmpleado → OnboardingProcess
- OnboardingService → OnboardingProcessService
- OnboardingNotificationService → OnboardingNotificationService (keep — already English)
"""

from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    name = "apps.onboarding"
    label = "onboarding"
    verbose_name = "VYNTIA Onboarding"
```

- [ ] **Step 3: Crear placeholder `apps/onboarding/models/__init__.py`**

```python
"""Onboarding models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

- [ ] **Step 4: Crear placeholder `apps/onboarding/services/__init__.py`**

```python
"""Onboarding services — re-exports for backward-compatible imports.

Populated when services are physically moved.
"""
```

---

## Task 4: Mover los 2 archivos con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` el modelo y el service**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/onboarding.py apps/api/apps/onboarding/models/onboarding.py
git mv apps/api/app_rrhh/services/onboarding_service.py apps/api/apps/onboarding/services/onboarding_service.py
```

- [ ] **Step 3: Verificar layout**

```bash
ls apps/api/apps/onboarding/
ls apps/api/apps/onboarding/models/
ls apps/api/apps/onboarding/services/
echo "---"
ls apps/api/app_rrhh/models/onboarding.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/onboarding_service.py 2>&1 || echo "OK: removed"
echo "---"
echo "=== app_rrhh/models/ remaining (should be just __init__.py + __pycache__) ==="
ls apps/api/app_rrhh/models/
echo "=== app_rrhh/services/ remaining (should be __init__.py + empleado_report_service.py + __pycache__) ==="
ls apps/api/app_rrhh/services/
```

Expected:
- 1 model file in onboarding/models/, 1 service in onboarding/services/, 2 originals removed
- `app_rrhh/models/` queda con solo `__init__.py` (último modelo extraído!)
- `app_rrhh/services/` queda con `__init__.py` + `empleado_report_service.py` (deferred to L3.11)

---

## Task 5: Verify FK strings DENTRO de los archivos movidos (read-only)

`onboarding.py` y `onboarding_service.py` ya usan strings lazy correctos cross-app. Verificar:

- [ ] **Step 1: Verificar FKs salientes en `apps/onboarding/models/onboarding.py`**

```bash
cd D:/VYNTIA/apps/api
echo "=== Cross-app lazy FKs en onboarding.py ==="
grep -n "ForeignKey\|OneToOneField" apps/onboarding/models/onboarding.py
echo ""
echo "=== Bare cross-app strings — should be 0 ==="
grep -rn "'Empleado'\b\|\"Empleado\"\|'Usuario'\b\|\"Usuario\"" apps/onboarding/models/ --include="*.py" || echo "OK: cero"
echo ""
echo "=== Inline import L103 (apps.documents) verifica ==="
grep -n "from apps.documents.models import\|from app_rrhh\.models import" apps/onboarding/models/onboarding.py
cd ../..
```

Expected:
- Cross-app FKs usan prefixed lazy strings: `'employees.Empleado'` (OneToOne), `'identity.Usuario'` (OneToOne + ForeignKey validado_por)
- "OK: cero" para bare strings
- 1 hit `from apps.documents.models import DocumentosDigitales` (línea 103 inline en `progreso_aprobado` property)

---

## Task 6: LR9 defensive sed (single + double quote — N/A pre-move)

Pre-move grep verificado: 0 stale refs.

- [ ] **Step 1: Bulk sed defensivo**

```bash
cd D:/VYNTIA/apps/api
find apps -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/onboarding/*" -print0 | xargs -0 sed -i \
  -e "s|'app_rrhh\.OnboardingEmpleado'|'onboarding.OnboardingEmpleado'|g" \
  -e 's|"app_rrhh\.OnboardingEmpleado"|"onboarding.OnboardingEmpleado"|g'
cd ../..
```

- [ ] **Step 2: Verify (defensive — esperado: 0 hits)**

```bash
cd D:/VYNTIA/apps/api
echo "=== onboarding.OnboardingEmpleado refs (expected: 0 — N/A) ==="
grep -rn "'onboarding\.OnboardingEmpleado'\|\"onboarding\.OnboardingEmpleado\"" apps --include="*.py" || echo "OK: cero (N/A)"
echo ""
echo "=== Stale 'app_rrhh.OnboardingEmpleado' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.OnboardingEmpleado'\|\"app_rrhh\.OnboardingEmpleado\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

- [ ] **Step 3: Bare-string sanity check**

```bash
cd D:/VYNTIA/apps/api
grep -rn "'OnboardingEmpleado'\b\|\"OnboardingEmpleado\"" apps app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`.

---

## Task 7: Crear `apps/onboarding/models/__init__.py` con re-exports

Use Write tool en `apps/api/apps/onboarding/models/__init__.py`:

```python
"""Onboarding models — re-exports for backward-compatible imports."""

from .onboarding import OnboardingEmpleado

__all__ = [
    "OnboardingEmpleado",
]
```

- [ ] **Smoke parse check**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/onboarding/models/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/onboarding/models/onboarding.py').read()); print('OK parse onboarding')"
cd ../..
```

Expected: 2x `OK parse`.

---

## Task 8: Update internal imports en service movido + create services/__init__.py

- [ ] **Step 1: Update `apps/onboarding/services/onboarding_service.py:6`** — model import

Use Edit tool en `apps/api/apps/onboarding/services/onboarding_service.py`:
- old_string: `from app_rrhh.models import OnboardingEmpleado`
- new_string: `from ..models import OnboardingEmpleado`

NOTE: line 10 (`from app_rrhh.tasks import send_email_html_task`) **NO se toca** — `app_rrhh/tasks.py` queda en app_rrhh, absolute import sigue funcionando.

- [ ] **Step 2: Verify**

```bash
cd D:/VYNTIA/apps/api
echo "=== Should be 1 hit 'from ..models import OnboardingEmpleado' ==="
grep -n "from \.\.models import\|from app_rrhh\.models" apps/onboarding/services/onboarding_service.py
echo ""
echo "=== Should preserve 'from app_rrhh.tasks import send_email_html_task' ==="
grep -n "from app_rrhh\.tasks import" apps/onboarding/services/onboarding_service.py
cd ../..
```

Expected:
- 1 hit `from ..models import OnboardingEmpleado` (line 6)
- 0 hits `from app_rrhh.models`
- 1 hit `from app_rrhh.tasks import send_email_html_task` (line 10 — preserved)

- [ ] **Step 3: Crear `apps/onboarding/services/__init__.py` con re-exports**

Use Write tool:

```python
"""Onboarding services — re-exports for backward-compatible imports.

Onboarding workflow orchestration and notifications.
"""

from .onboarding_service import OnboardingNotificationService, OnboardingService

__all__ = [
    "OnboardingNotificationService",
    "OnboardingService",
]
```

- [ ] **Step 4: Smoke parse check**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/onboarding/services/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/onboarding/services/onboarding_service.py').read()); print('OK parse onboarding_service')"
cd ../..
```

Expected: 2x `OK parse`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern A:** `from app_rrhh.models import OnboardingEmpleado` → `from apps.onboarding.models import OnboardingEmpleado`
**Pattern B:** `from app_rrhh.services.onboarding_service import (X|X, Y)` → `from apps.onboarding.services import ...`

- [ ] **Step 1: Inventario completo (LR11 + LR13 + LR14 defensive)**

```bash
cd D:/VYNTIA/apps/api
echo "=== ABSOLUTE imports model (~5 expected) ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "OnboardingEmpleado" | sort
echo ""
echo "=== ABSOLUTE imports services (~12 expected — many inline) ==="
grep -rn "from app_rrhh\.services\.onboarding_service\|from app_rrhh\.services import.*Onboarding" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations | sort
echo ""
echo "=== LR11 — RELATIVE imports en app_rrhh/*.py (expected: 0) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep "OnboardingEmpleado" || echo "OK: cero (LR11 N/A para L3.9)"
echo ""
echo "=== LR14 — Multi-line service blocks (expected: 2 hits in views.py) ==="
grep -rn -B 0 -A 5 "from app_rrhh\.services\.onboarding_service import (" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations
echo ""
echo "=== LR13 — Stale logger-name strings (expected: 0) ==="
grep -rn "logger=['\"]app_rrhh\.services\.onboarding\|getLogger(['\"]app_rrhh\.services\.onboarding" --include="*.py" || echo "OK: cero (LR13 N/A)"
cd ../..
```

Expected: ~5 model imports, ~12 service imports (many inline single-line), LR11 OK, **2 multi-line blocks** (LR14), LR13 OK.

- [ ] **Step 2: Sed for single-import lines (Pattern A models)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/onboarding/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(OnboardingEmpleado\)$|from apps.onboarding.models import \1|g'
cd ../..
```

- [ ] **Step 3: Sed for single-import services (Pattern B single-name)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/onboarding/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.services\.onboarding_service import \(OnboardingService\)$|from apps.onboarding.services import \1|g' \
  -e 's|^from app_rrhh\.services\.onboarding_service import \(OnboardingNotificationService\)$|from apps.onboarding.services import \1|g'
cd ../..
```

- [ ] **Step 4: Sed for inline imports (whitespace-prefix, `-E` con `#`)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/onboarding/*" \
  -print0 | xargs -0 sed -i -E \
  -e 's#^([[:space:]]+)from app_rrhh\.services\.onboarding_service import (OnboardingService)$#\1from apps.onboarding.services import \2#g' \
  -e 's#^([[:space:]]+)from app_rrhh\.services\.onboarding_service import (OnboardingNotificationService)$#\1from apps.onboarding.services import \2#g'
cd ../..
```

Verify all inline (in-method) hits in views.py updated (should be ~8 single-line inline imports):
```bash
grep -n "from app_rrhh.services.onboarding_service import\|from apps.onboarding.services import" apps/api/api/v1/rrhh/views.py | head -15
```

Expected: 0 hits `app_rrhh.services.onboarding_service` (single-line); ~8 hits `apps.onboarding.services` for single-name inline imports.

- [ ] **Step 5: LR14 — Manual fix multi-line parenthesized blocks en views.py:2449-2452, 2530-2533**

Read context:
```bash
sed -n '2447,2455p' apps/api/api/v1/rrhh/views.py
echo "---"
sed -n '2528,2536p' apps/api/api/v1/rrhh/views.py
```

Both blocks should be identical:
```python
        from app_rrhh.services.onboarding_service import (
            OnboardingNotificationService,
            OnboardingService,
        )
```

Use Edit tool with `replace_all=true`:
- old_string:
```python
        from app_rrhh.services.onboarding_service import (
            OnboardingNotificationService,
            OnboardingService,
        )
```
- new_string:
```python
        from apps.onboarding.services import (
            OnboardingNotificationService,
            OnboardingService,
        )
```
- replace_all: true

Verify:
```bash
grep -rn -B 0 -A 5 "from app_rrhh\.services\.onboarding_service import (" --include="*.py" apps/api --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK: cero"
grep -rn -B 0 -A 5 "from apps\.onboarding\.services import (" --include="*.py" apps/api --exclude-dir=__pycache__ --exclude-dir=migrations
```

Expected: 0 multi-line `app_rrhh.services.onboarding_service` blocks. 2 multi-line `apps.onboarding.services` blocks.

- [ ] **Step 6: Manual fix mixed-line imports (defensive)**

```bash
cd D:/VYNTIA/apps/api
echo "=== Mixed model imports ==="
grep -rn "from app_rrhh\.models import.*OnboardingEmpleado" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations | head -5
echo ""
echo "=== Mixed service imports ==="
grep -rn "from app_rrhh\.services\.onboarding_service import.*\(OnboardingService\|OnboardingNotificationService\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations | head -5
cd ../..
```

Expected: 0 hits each (sed Steps 2-4 + LR14 Step 5 should have caught all single + multi-line).

- [ ] **Step 7: Self-absolute import check on moved files**

```bash
cd D:/VYNTIA/apps/api
echo "=== Models self-absolute (should be cero) ==="
grep -rn "from apps\.onboarding\.models import" apps/onboarding/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Services internal (should use ..models, no app_rrhh.models) ==="
grep -rn "from \.\.models\|from apps\.onboarding\.models\|from app_rrhh\.models" apps/onboarding/services --include="*.py"
echo ""
echo "=== Services preserves app_rrhh.tasks ==="
grep -rn "from app_rrhh\.tasks" apps/onboarding/services --include="*.py"
cd ../..
```

Expected:
- 0 self-absolute in models
- 1 hit `from ..models import OnboardingEmpleado` in onboarding_service.py
- 0 hits `from app_rrhh.models` in services
- 1 hit `from app_rrhh.tasks import send_email_html_task` (preserved)

- [ ] **Step 8: LR11 defensive check**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep "OnboardingEmpleado" || echo "OK: cero (LR11 N/A para L3.9)"
cd ../..
```

Expected: `OK: cero (LR11 N/A para L3.9)`.

- [ ] **Step 9: LR13 defensive check**

```bash
cd D:/VYNTIA/apps/api
grep -rn "logger=['\"]app_rrhh\.services\.onboarding\|getLogger(['\"]app_rrhh\.services\.onboarding" --include="*.py" || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`.

- [ ] **Step 10: Verificación final exhaustiva**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import OnboardingEmpleado ==="
grep -rn "from app_rrhh\.models import" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "OnboardingEmpleado" || echo "OK"
echo ""
echo "=== B: from .onboarding (relative en app_rrhh) ==="
grep -rn "from \.onboarding" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: from .models import OnboardingEmpleado (LR11) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep "OnboardingEmpleado" || echo "OK"
echo ""
echo "=== D: from app_rrhh.services.onboarding_service (Pattern B single + multi) ==="
grep -rn "from app_rrhh\.services\.onboarding_service" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== E: bare 'OnboardingEmpleado' en app_rrhh non-migrations ==="
grep -rn "'OnboardingEmpleado'\b\|\"OnboardingEmpleado\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: stale 'app_rrhh.OnboardingEmpleado' anywhere LR9 ==="
grep -rn "'app_rrhh\.OnboardingEmpleado'\|\"app_rrhh\.OnboardingEmpleado\"" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== G: app_rrhh.models.onboarding submodule path ==="
grep -rn "from app_rrhh\.models\.onboarding" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== H: LR13 logger strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.onboarding\|getLogger(['\"]app_rrhh\.services\.onboarding" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 10: Update `app_rrhh/models/__init__.py` — quitar último export

**Significant moment:** Después de esta task, `app_rrhh/models/__init__.py` queda con `__all__ = []`. El último modelo de dominio se ha extraído.

- [ ] **Step 1: Read current state**

```bash
cat apps/api/app_rrhh/models/__init__.py
```

Expected current content (post-L3.8):
```python
# -*- coding: utf-8 -*-
"""..."""

# Importar todos los modelos para mantener compatibilidad
# from .contratos import ContratoAdenda  # Comentado para evitar conflicto de tabla

from .onboarding import OnboardingEmpleado

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    # Modelo de onboarding
    "OnboardingEmpleado",
]
```

- [ ] **Step 2: Use Edit tool — remove import line**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string: `from .onboarding import OnboardingEmpleado`
- new_string: (empty)

Or use multi-line edit removing both the import and surrounding blank line cleanly.

- [ ] **Step 3: Use Edit tool — remove `"OnboardingEmpleado"` y header del `__all__`**

Use Edit tool:
- old_string:
```python
__all__ = [
    # Modelo de onboarding
    "OnboardingEmpleado",
]
```
- new_string:
```python
__all__ = []
```

- [ ] **Step 4: Verificar limpieza**

```bash
grep -n "OnboardingEmpleado\|onboarding" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
cat apps/api/app_rrhh/models/__init__.py
```

Expected: `OK: removed`. File ahora minimal — `__all__ = []`.

---

## Task 11: Update settings — registrar `OnboardingConfig`

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
    "apps.time_off.apps.TimeOffConfig",
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
    "apps.onboarding.apps.OnboardingConfig",
    "app_rrhh",
]
```

Verify:
```bash
grep -A 11 "LOCAL_APPS = \[" apps/api/vyntia/settings/base.py
```

---

## Task 12: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Expected current: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll", "apps.time_off"]`

Use Edit tool en `apps/api/pyproject.toml`:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll", "apps.time_off"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents", "apps.payroll", "apps.time_off", "apps.onboarding"]`

Reinstall:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Smoke check:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

---

## Task 13: NUCLEAR DB regenerate (LR12 sequence: drop → CREATE → makemigrations → migrate)

- [ ] **Step 1: Drop bd_vyntia (kill procs first)**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

- [ ] **Step 2: CREATE bd_vyntia (LR12)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

- [ ] **Step 3: Eliminar migration files existentes**

```bash
cd D:/VYNTIA/apps/api/app_rrhh/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"
git rm 0003_initial.py 2>&1 | tail -2 || echo "no 0003"

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

cd D:/VYNTIA/apps/api/apps/time_off/migrations
git rm 0001_initial.py 2>&1 | tail -2

cd D:/VYNTIA
```

NOTE: NO se borra `apps/onboarding/migrations/`.

- [ ] **Step 4: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -30
cd ../..
```

Expected migrations for: app_rrhh (**no models — should generate nothing or empty**), identity, organization, employees, contracts, documents, payroll, time_off, **onboarding (with 1 model — NEW)**.

NOTE: After this, `app_rrhh` may not generate any migration since it has no models. That's expected. If Django complains "No changes detected", that's fine for app_rrhh.

Verify:
```bash
echo "=== onboarding 0001 (expected: 1 model definition) ==="
grep -E "name='OnboardingEmpleado'" apps/api/apps/onboarding/migrations/0001_initial.py | wc -l
echo "=== app_rrhh migrations after move ==="
ls apps/api/app_rrhh/migrations/ 2>&1 | grep -v __pycache__
```

Expected: `1` for onboarding. app_rrhh may have no migration files (only `__init__.py`).

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK`. Sin errors.

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'onboarding_empleado', COUNT(*) FROM onboarding_empleado;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, onboarding_empleado = 0.

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
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l39.log 2>&1 &
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

- [ ] **Step 3: Cleanup greps finales (8 patterns A-H)**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import OnboardingEmpleado ==="
grep -rn "from app_rrhh\.models import" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep "OnboardingEmpleado" || echo "OK"
echo "=== B: from .onboarding (relative en app_rrhh) ==="
grep -rn "from \.onboarding" app_rrhh --include="*.py" || echo "OK"
echo "=== C: bare 'OnboardingEmpleado' en app_rrhh non-migrations ==="
grep -rn "'OnboardingEmpleado'\b\|\"OnboardingEmpleado\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo "=== D: app_rrhh.models.onboarding submodule ==="
grep -rn "from app_rrhh\.models\.onboarding" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo "=== E: stale 'app_rrhh.OnboardingEmpleado' (LR9) ==="
grep -rn "'app_rrhh\.OnboardingEmpleado'\|\"app_rrhh\.OnboardingEmpleado\"" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo "=== F: from app_rrhh.services.onboarding_service (Pattern B single + multi) ==="
grep -rn "from app_rrhh\.services\.onboarding_service" --include="*.py" --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo "=== G: LR11 from .models import OnboardingEmpleado (relative en app_rrhh) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep "OnboardingEmpleado" || echo "OK"
echo "=== H: LR13 logger strings ==="
grep -rn "logger=['\"]app_rrhh\.services\.onboarding\|getLogger(['\"]app_rrhh\.services\.onboarding" --include="*.py" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 16: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -50
git add apps/api/
git commit -m "chore(L3.9): extract onboarding app (OnboardingEmpleado + OnboardingService + OnboardingNotificationService) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.9-onboarding-app ^master | head -5
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
git merge --no-ff vyntia/L3.9-onboarding-app -m "Merge L3.9: extract onboarding app (OnboardingEmpleado + OnboardingService + OnboardingNotificationService)"
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

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` Status column: L3.9 → ✅ con merge SHA. L3.10 → ⏳ NEXT.

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.9): mark L3.9 merged, L3.10 (rename ES→EN) as next in roadmap"
```

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/onboarding/{__init__.py, apps.py, models/{__init__.py, onboarding.py}, services/{__init__.py, onboarding_service.py}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/onboarding.py` y `app_rrhh/services/onboarding_service.py` removidos
- [ ] `app_rrhh/models/__init__.py` queda con `__all__ = []` (último modelo extraído)
- [ ] `apps/onboarding/services/__init__.py` exporta `OnboardingService` + `OnboardingNotificationService`
- [ ] LOCAL_APPS incluye `OnboardingConfig`; pyproject incluye `apps.onboarding`
- [ ] LR12 fix: makemigrations corrió DESPUÉS de CREATE DATABASE
- [ ] LR14 fix: 2 multi-line blocks `from app_rrhh.services.onboarding_service import (...)` en views.py:2449, 2530 actualizados manualmente
- [ ] Migrations regenerated; onboarding con 1 modelo; app_rrhh sin modelos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0, onboarding_empleado = 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] All 8 cleanup greps OK (A-H)
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.9 ✅, L3.10 NEXT

---

## Después de L3.9

**Próximo plan:** L3.10 — Rename español → inglés masivo. Aplicar tabla del spec § 3.6:
- Class names: `Empleado→Employee`, `OnboardingEmpleado→OnboardingProcess`, `ContratosAdendas→Contract+ContractAmendment` (split + rename), `DatosLaborales→EmploymentData`, etc.
- Field names: `nombres→first_name`, `apellido_paterno→last_name`, `fecha_nacimiento→birth_date`, etc.
- Frontend services + tipos TS también
- Migration `RenameModel` + `AlterField` masiva
- L3.10 será el sub-PR más grande (toca todo el codebase)

---

## Notas para el ejecutor

- **Patrón NUCLEAR + LR12 sequence** — drop → CREATE → makemigrations → migrate.
- **PGPASSWORD env var** explícito por known issue.
- **Class names en español** — rename inglés en L3.10.
- **Último sub-PR de extracción** — L3.10 es rename masivo, L3.11 es cleanup. Después de L3.9, `app_rrhh/models/__init__.py` queda con `__all__ = []`.
- **`app_rrhh/services/onboarding_service.py:10`** — `from app_rrhh.tasks import send_email_html_task` PRESERVADO post-move. Tasks.py queda en app_rrhh.
- **LR14 SÍ APLICA** (segunda vez): 2 multi-line `from app_rrhh.services.onboarding_service import (\n...,\n)` blocks en views.py:2449, 2530. Sed solo captura single-line — Task 9 Step 5 dedicado a manual fix.
- **Múltiples inline imports** — views.py tiene ~8 inline imports adicionales single-line (sed handles those en Step 4).
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
- **`empleado_report_service.py` queda en app_rrhh** — pertenece a employees per spec § 3.3 pero L3.4 lo difirió. Cleanup en L3.11.
