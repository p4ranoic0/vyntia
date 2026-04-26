# VYNTIA Foundation L3.1 — Extract `core` as Django App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mover `apps/api/core/` (Python module top-level, sin modelos) a `apps/api/apps/core/` (Django app dentro del nuevo namespace `apps/`), registrarlo como Django app con `AppConfig`, y actualizar las 33 import lines + 11 settings strings que lo referencian. Esto inaugura la estructura `apps/api/apps/<bounded-context>/` que L3.2–L3.9 poblarán.

**Architecture:** El módulo `core/` ya está extraído desde L0 como package Python con 10 utilidades (responses, pagination, decorators, middleware, exceptions, validators, logging, permissions, database router). Tiene CERO modelos. L3.1 lo mueve un nivel adentro (a `apps/core/`), lo registra en `INSTALLED_APPS`, y reemplaza todos los `from core.X` por `from apps.core.X`. Es un rename de namespace puro — sin cambios de lógica ni schema BD.

**Tech Stack:** Bash + git mv + bulk Python find/replace. Django 5.2 AppConfig.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" (sub-PR L3.1) y § 3.1 "Estructura de directorios"

**Pre-condiciones:**
- L2 mergeado a master (`cbd2fb8f Merge L2: Django 4.2 → 5.2 LTS upgrade`)
- Django 5.2.13 activo
- pytest baseline: 125 passed, 44 failed, 3 skipped
- BD `bd_vyntia` provisionada
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/core/` ya no existe; `apps/api/apps/core/` sí existe con todos los archivos del módulo previo + `apps.py`
- [ ] `apps/api/apps/__init__.py` existe (namespace package vacío)
- [ ] `'apps.core'` está en `INSTALLED_APPS` de `vyntia/settings/base.py`
- [ ] Cero matches de `from core\.\|from core import\|import core\b` en `apps/api/` (excepto `django.core` que es stdlib)
- [ ] Cero matches de `"core\.\|'core\.` en `apps/api/vyntia/settings/` excepto `django.core` o `cache.backends`
- [ ] `pyproject.toml` `packages` incluye `"apps"` y `"apps.core"`
- [ ] `python manage.py check --settings=vyntia.settings.development` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] Branch `vyntia/L3.1-core-app` con commits `chore(L3.1):` mergeada a master con `--no-ff`
- [ ] `git status` limpio
- [ ] L3 master roadmap actualizado: L3.1 marcado ✅ con merge SHA

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/__init__.py` | Vacío — solo hace `apps/` un Python package |
| Move | `apps/api/core/` → `apps/api/apps/core/` | Mantiene los 10 archivos `.py` adentro |
| Create | `apps/api/apps/core/apps.py` | `class CoreConfig(AppConfig): name = 'apps.core'; label = 'core_utils'` |
| Modify | `apps/api/vyntia/settings/base.py` | INSTALLED_APPS += `'apps.core'`; reemplazar `core.middleware.X` → `apps.core.middleware.X`, `core.database` → `apps.core.database`, `core.permissions` → `apps.core.permissions`, `core.pagination` → `apps.core.pagination`, `core.exceptions` → `apps.core.exceptions` |
| Modify (16 files) | `apps/api/api/**/*.py`, `apps/api/app_rrhh/services/**/*.py`, `apps/api/app_rrhh/views.py`, etc. | Replace `from core.X` → `from apps.core.X` |
| Modify | `apps/api/pyproject.toml` | `[tool.setuptools].packages` añade `"apps"` y `"apps.core"` |

**¿Por qué `label = 'core_utils'` en lugar de `label = 'core'`?**
Django usa el `label` como prefijo de tabla y cookie de identidad. `core` chocaría con muchas convenciones internas y con la utility-vs-bounded-context distinction. `core_utils` es explícito sobre que esta app es de utilidades, no un dominio de negocio. Como `core` no tiene modelos, el `label` casi no aparece en la BD — es seguridad simbólica.

**NO se toca en L3.1:**
- Ningún archivo dentro de `apps/api/core/*.py` (su contenido)
- Ningún modelo, view, serializer
- BD: ningún cambio de esquema (core no tiene modelos)
- Frontend: nada (L3.1 es backend-only)

---

## Task 1: Pre-flight — branch, baseline, venv

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Confirmar pwd y master limpio post-L2**

Run desde la raíz:
```bash
pwd
git status --short
git log --oneline -3
```

Expected:
- `pwd`: `/d/VYNTIA`
- `git status`: vacío (puede tener el plan L3 master + este plan untracked, eso es OK)
- `git log`: HEAD = `cbd2fb8f Merge L2: ...` o más reciente

- [ ] **Step 2: Activar venv y confirmar Django 5.2.13**

Run:
```bash
source .venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `5.2.13` (o un 5.2.x).

- [ ] **Step 3: Confirmar baseline pytest**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`. Si difiere, **detente**.

- [ ] **Step 4: Inventario rápido de uso de `core`**

Run desde `apps/api/`:
```bash
cd apps/api
echo "=== Imports from core ==="
grep -rn "^from core\.\|^from core import\|^import core\b" --include="*.py" | wc -l
echo "files:"
grep -rln "^from core\.\|^from core import\|^import core\b" --include="*.py" | wc -l
echo ""
echo "=== Settings strings 'core.X' ==="
grep -rn "\"core\.\|'core\." vyntia/settings/ --include="*.py" | grep -v "django.core\|cache.backends" | wc -l
cd ../..
```

Expected (aproximadamente):
- 33 import lines en 16 files
- 11 settings strings (en `vyntia/settings/base.py`)

Si los counts son MUY distintos (>20% drift), reporta — el plan asume estos órdenes de magnitud.

- [ ] **Step 5: Crear branch L3.1**

Run:
```bash
git checkout -b vyntia/L3.1-core-app
git status
```

Expected: `On branch vyntia/L3.1-core-app`, working tree limpio (excepto plans untracked, que comiteas en Task 2).

---

## Task 2: Comitear el roadmap L3 + plan L3.1 (precursor)

**Files:**
- `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` (untracked)
- `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.1-core.md` (untracked)

**Por qué:** Igual que en L1/L2, el plan que ejecutamos vive en git. Lo comiteamos en la nueva branch para que llegue a master con el merge.

- [ ] **Step 1: Verificar archivos untracked**

Run:
```bash
git status --short | grep "L3"
```

Expected: 2 archivos: el roadmap master y este plan.

- [ ] **Step 2: Stage y commit**

Run:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.1-core.md
git commit -m "docs(L3.1): add L3 master roadmap and L3.1 core extraction plan"
```

Expected: 2 files changed, ~XXX insertions.

---

## Task 3: Crear `apps/api/apps/__init__.py` (namespace package)

**Files:**
- Create: `apps/api/apps/__init__.py`

**Por qué:** Para que `apps/` sea un Python package importable como `apps.core`, `apps.identity`, etc. en futuras layers. Empty `__init__.py` is enough — no docstring needed.

- [ ] **Step 1: Verificar que `apps/api/apps/` no existe todavía**

Run:
```bash
ls D:/VYNTIA/apps/api/apps 2>&1 || echo "OK: apps/ doesn't exist yet"
```

Expected: `OK: apps/ doesn't exist yet`. Si existe (de un intento previo), borra: `rm -rf D:/VYNTIA/apps/api/apps`.

- [ ] **Step 2: Crear directorio + `__init__.py`**

Run:
```bash
mkdir -p D:/VYNTIA/apps/api/apps
touch D:/VYNTIA/apps/api/apps/__init__.py
ls -la D:/VYNTIA/apps/api/apps/
```

Expected: directorio existe con `__init__.py` (0 bytes).

- [ ] **Step 3: NO commit todavía** (lo combinamos con el move + rename en Task 5 commit final).

---

## Task 4: `git mv` core/ a apps/core/

**Files:**
- Move: `apps/api/core/` → `apps/api/apps/core/`

- [ ] **Step 1: Antes del move — verificar que no hay procesos Python con file handles en `core/`**

Run:
```bash
ps -W 2>/dev/null | grep -iE "python|gunicorn" | grep -v grep || echo "OK: no python procs"
```

Si aparecen procesos `python` con paths que contienen `D:/VYNTIA` o `core/`, mátalos primero:
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
```

(Ya nos pasó en L0 con runserver stale procs.)

- [ ] **Step 2: `git mv core` a `apps/core`**

Run:
```bash
cd D:/VYNTIA
git mv apps/api/core apps/api/apps/core
ls apps/api/apps/core/
```

Expected: `apps/api/apps/core/` ahora contiene los 10 archivos: `__init__.py`, `database.py`, `decorators.py`, `exceptions.py`, `logging.py`, `middleware.py`, `pagination.py`, `permissions.py`, `responses.py`, `validators.py`. `apps/api/core/` ya no existe.

- [ ] **Step 3: Diagnostic — confirmar que sin actualizar imports el sistema falla**

Run:
```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: error tipo `ModuleNotFoundError: No module named 'core'` (porque `vyntia/settings/base.py` aún tiene strings `core.middleware.X`). Esto es **esperado** — confirma que las strings que vamos a updating sí están en uso.

---

## Task 5: Crear `apps.py` con AppConfig en `apps/core/`

**Files:**
- Create: `apps/api/apps/core/apps.py`

**Por qué:** Django requiere un `AppConfig` para registrar una carpeta como app. La config explicita `name = 'apps.core'` y `label = 'core_utils'` (label distinto del nombre Python para evitar confusiones simbólicas con `django.core` y para reflejar que esta app es de utilidades, no dominio de negocio).

- [ ] **Step 1: Crear `apps/api/apps/core/apps.py` con contenido exacto**

```python
"""AppConfig for the `apps.core` Django app — VYNTIA platform utilities.

This app contains transversal utilities used across all bounded contexts:
- APIResponse, pagination, exception handler (DRF integration)
- Decorators for auth/role checks
- Custom middleware (security headers, JWT cookie, audit, performance)
- Database router
- Validators (email, phone, RUT)

`apps.core` has NO models — it's pure utility. Bounded contexts (employees,
contracts, payroll, etc.) depend on `apps.core` but never the reverse.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core_utils"
    verbose_name = "VYNTIA Core Utilities"
```

- [ ] **Step 2: Verificar archivo creado correctamente**

Run:
```bash
cat D:/VYNTIA/apps/api/apps/core/apps.py | head -25
```

Expected: contenido exacto del Step 1.

---

## Task 6: Registrar `apps.core` en INSTALLED_APPS

**Files:**
- Modify: `apps/api/vyntia/settings/base.py`

- [ ] **Step 1: Editar `LOCAL_APPS` para incluir `apps.core`**

El bloque actual (líneas 33-35 aprox.) es:
```python
LOCAL_APPS = [
    "app_rrhh",
]
```

Reemplazarlo con:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "app_rrhh",
]
```

(`app_rrhh` se queda mientras L3.2–L3.9 sigan moviendo cosas afuera. Se eliminará en L3.11.)

Use Edit tool:
- old_string:
```python
LOCAL_APPS = [
    "app_rrhh",
]
```
- new_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "app_rrhh",
]
```

---

## Task 7: Reemplazar strings `core.X` → `apps.core.X` en `vyntia/settings/base.py`

**Files:**
- Modify: `apps/api/vyntia/settings/base.py`

**Por qué:** Django usa estos strings para resolver clases (middleware, routers, DRF defaults). Sin update, las imports fallarán.

- [ ] **Step 1: Listar exactamente qué strings hay**

Run:
```bash
grep -n "\"core\.\|'core\." apps/api/vyntia/settings/base.py | grep -v "django.core\|cache.backends"
```

Expected output:
```
41:    "core.middleware.SecurityHeadersMiddleware",
42:    "core.middleware.HealthCheckMiddleware",
47:    "core.middleware.JWTCookieMiddleware",
49:    "core.middleware.RequestLoggingMiddleware",
50:    "core.middleware.PerformanceMonitoringMiddleware",
51:    "core.middleware.AuditMiddleware",
52:    # "core.middleware.RateLimitingMiddleware",  # Deshabilitado temporalmente (requiere Redis)
122:DATABASE_ROUTERS = ["core.database.DatabaseRouter"]
139:        "core.permissions.IsAuthenticated",
146:    "DEFAULT_PAGINATION_CLASS": "core.pagination.StandardResultsSetPagination",
156:    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
```

- [ ] **Step 2: Bulk replace `core.` → `apps.core.` en strings**

Use Edit tool con `replace_all=true` sobre `apps/api/vyntia/settings/base.py`:

- old_string: `"core.middleware.`
- new_string: `"apps.core.middleware.`

- old_string: `"core.database.`
- new_string: `"apps.core.database.`

- old_string: `"core.permissions.`
- new_string: `"apps.core.permissions.`

- old_string: `"core.pagination.`
- new_string: `"apps.core.pagination.`

- old_string: `"core.exceptions.`
- new_string: `"apps.core.exceptions.`

(Cada uno como un Edit tool call separado con replace_all=true.)

- [ ] **Step 3: Verificar replacement**

Run:
```bash
grep -n "\"core\.\|'core\." apps/api/vyntia/settings/base.py | grep -v "django.core\|cache.backends" || echo "OK: cero core.X strings residuales"
```

Expected: `OK: cero core.X strings residuales`.

- [ ] **Step 4: Confirmar que `apps.core.X` strings ahora están**

Run:
```bash
grep -n "apps\.core\." apps/api/vyntia/settings/base.py | head -15
```

Expected: ~11 matches con prefijo `apps.core.middleware.`, `apps.core.database.`, etc.

---

## Task 8: Bulk replace `from core.X` → `from apps.core.X` en código Python

**Files (16):**
- `apps/api/api/v1/app_rrhh/document_generation_views.py`
- `apps/api/api/v1/auth/views.py`
- `apps/api/api/v1/rrhh/contratos_views.py`
- `apps/api/api/v1/rrhh/permissions.py`
- `apps/api/api/v1/rrhh/remuneraciones_views.py`
- `apps/api/api/v1/rrhh/serializers.py`
- `apps/api/api/v1/rrhh/usuario_roles_serializers.py`
- `apps/api/api/v1/rrhh/usuario_roles_views.py`
- `apps/api/api/v1/rrhh/views.py`
- `apps/api/api/v1/vacaciones/views.py`
- `apps/api/app_rrhh/services/vacation_admin_service.py`
- `apps/api/app_rrhh/services/vacation_approval_service.py`
- `apps/api/app_rrhh/services/vacation_calculation_service.py`
- (otros que aparezcan en el grep — la lista exacta sale del Step 1)

**Por qué:** 16 files con un total de 33 import lines apuntan a `core.X`. Bulk sed los actualiza atómicamente.

- [ ] **Step 1: Snapshot pre-replace**

Run:
```bash
cd D:/VYNTIA/apps/api
grep -rln "^from core\.\|^from core import\|^import core\b" --include="*.py" | sort | tee /tmp/core_files.txt
echo "Total files: $(wc -l < /tmp/core_files.txt)"
cd ../..
```

Expected: 16 archivos listados.

- [ ] **Step 2: Bulk replace usando sed**

Run desde la raíz:
```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" -not -path "*/apps/core/*" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's/^from core\./from apps.core./g' \
  -e 's/^from core import/from apps.core import/g'
cd ../..
```

NOTA: `-not -path "*/apps/core/*"` excluye los archivos del nuevo `apps/core/` mismo (que pueden tener `from core.X` referenciando módulos hermanos — pero como el módulo se llama ahora `apps.core.X`, esos imports se romperían si los reemplazamos). Sin embargo, dentro del nuevo `apps/core/`, los imports relativos (`from .responses import X`) son los correctos y NO los tocamos porque son `from .` no `from core.`. Verificación adicional en Step 3.

- [ ] **Step 3: Verificar que cero `from core.` lines quedan**

Run:
```bash
cd D:/VYNTIA/apps/api
grep -rn "^from core\.\|^from core import\|^import core\b" --include="*.py" 2>&1 | head -10 || echo "OK: cero matches"
cd ../..
```

Expected: `OK: cero matches`.

- [ ] **Step 4: Verificar que ahora hay `from apps.core.` en su lugar**

Run:
```bash
cd D:/VYNTIA/apps/api
grep -rn "^from apps\.core\." --include="*.py" | wc -l
cd ../..
```

Expected: ≈33 (mismo número que el inventario Task 1 Step 4).

- [ ] **Step 5: Verificar que `apps/core/` mismo NO se rompió**

Run:
```bash
cd D:/VYNTIA/apps/api
grep -rn "^from apps\.core\." apps/core/ --include="*.py" 2>&1 | head -5 || echo "OK: apps/core/ no se autoreferencia"
cd ../..
```

Expected: vacío o `OK: ...`. Si dentro de `apps/core/` algún archivo dice `from apps.core.X`, es porque se modificó cuando no debía. Manualmente revierte esos archivos:

```bash
cd D:/VYNTIA/apps/api/apps/core
grep -rln "from apps\.core\." --include="*.py" | while read f; do
  sed -i 's/from apps\.core\./from ./g' "$f"
done
cd D:/VYNTIA
```

(Reemplaza con relative imports que es lo que originalmente debería haber sido.)

---

## Task 9: Update `pyproject.toml` packages list

**Files:**
- Modify: `apps/api/pyproject.toml`

**Por qué:** El `[tool.setuptools].packages` list sigue diciendo `["vyntia", "app_rrhh", "api", "core"]`. Como `core` se movió a `apps.core`, hay que actualizar.

- [ ] **Step 1: Editar `apps/api/pyproject.toml`**

Bloque actual:
```toml
[tool.setuptools]
# Backend package layout: solo se distribuyen estos top-levels.
# Cuando L3 cree apps/api/apps/, este `packages` debe actualizarse.
packages = ["vyntia", "app_rrhh", "api", "core"]
include-package-data = true
```

Reemplazar por:
```toml
[tool.setuptools]
# Backend package layout. `apps` namespace contiene bounded contexts (L3+).
# Cada nueva app L3.X (identity, organization, employees, ...) se añade aquí.
packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core"]
include-package-data = true
```

Use Edit tool:
- old_string:
```toml
[tool.setuptools]
# Backend package layout: solo se distribuyen estos top-levels.
# Cuando L3 cree apps/api/apps/, este `packages` debe actualizarse.
packages = ["vyntia", "app_rrhh", "api", "core"]
include-package-data = true
```

- new_string:
```toml
[tool.setuptools]
# Backend package layout. `apps` namespace contiene bounded contexts (L3+).
# Cada nueva app L3.X (identity, organization, employees, ...) se añade aquí.
packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core"]
include-package-data = true
```

- [ ] **Step 2: Reinstalar editable**

Run:
```bash
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -5
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0` (sin errors). Si hay error de "package directory 'apps.core' does not exist", revisa Step 1 — el path debe matchear el filesystem.

---

## Task 10: Smoke tests + commit

**Files:** ninguno nuevo (verificación + commit acumulativo)

- [ ] **Step 1: `manage.py check` clean**

Run:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

Si aparece `ModuleNotFoundError: No module named 'core'`, hay strings residuales en algún settings file. Hunt:
```bash
grep -rn "\"core\.\|'core\." apps/api/vyntia/settings/ --include="*.py" | grep -v "django.core\|cache.backends"
```

Si aparece `ImportError: cannot import name X from apps.core.Y`, algún archivo dentro de `apps/core/` está mal — revisa relative imports.

- [ ] **Step 2: pytest baseline preservado**

Run:
```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`. Si los counts cambian, NUEVA regresión introducida — diagnostica antes del commit.

- [ ] **Step 3: runserver smoke (opcional pero recomendado)**

Run:
```bash
cd D:/VYNTIA/apps/api
python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver.log 2>&1 &
SERVER_PID=$!
sleep 6
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

Expected: `HTTP 200 /api/docs/`. Si curl falla o el server no arrancó, lee `/tmp/runserver.log` para encontrar el error.

Mata cualquier proceso residual:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 4: `git status` y stage del commit**

Run:
```bash
git status --short
```

Expected (orden aproximado):
```
A  apps/api/apps/__init__.py
A  apps/api/apps/core/apps.py
R  apps/api/core/__init__.py        -> apps/api/apps/core/__init__.py
R  apps/api/core/database.py        -> apps/api/apps/core/database.py
R  apps/api/core/decorators.py      -> apps/api/apps/core/decorators.py
... (10 archivos R)
M  apps/api/pyproject.toml
M  apps/api/vyntia/settings/base.py
M  apps/api/api/v1/.../views.py     (varios)
M  apps/api/app_rrhh/services/vacation_*.py (3 archivos)
... (16 archivos M con import updates)
```

- [ ] **Step 5: Commit acumulativo**

Run:
```bash
git add apps/api/
git commit -m "chore(L3.1): extract core to apps.core (Django app, 33 imports + 11 settings strings updated)"
```

Expected: ~30 files changed.

---

## Task 11: Final verification + DoD checklist

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Cleanup greps**

Run:
```bash
echo "=== A: Old core. imports ==="
grep -rn "^from core\.\|^from core import\|^import core\b" apps/api/ --include="*.py" || echo "OK"
echo ""
echo "=== B: Old core. settings strings ==="
grep -rn "\"core\.\|'core\." apps/api/vyntia/ --include="*.py" | grep -v "django.core\|cache.backends" || echo "OK"
echo ""
echo "=== C: Directory layout ==="
ls D:/VYNTIA/apps/api/core 2>&1 | head -3 || echo "OK: apps/api/core/ removed"
ls D:/VYNTIA/apps/api/apps/core/apps.py
echo ""
echo "=== D: pyproject ==="
grep "packages" apps/api/pyproject.toml
```

Expected:
- A: `OK`
- B: `OK`
- C: `OK: apps/api/core/ removed` + el archivo `apps.py` listed
- D: línea con `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core"]`

- [ ] **Step 2: Final pytest**

Run:
```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

- [ ] **Step 3: Git history clean**

Run:
```bash
git log --oneline vyntia/L3.1-core-app ^master | head -5
git status --short
```

Expected:
- 2 commits visible (`docs(L3.1): add ... plan` + `chore(L3.1): extract core ...`)
- `git status` vacío

---

## Task 12: Merge to master

**Files:** ninguno

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta: ¿Mergear directo a master con `--no-ff`?

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

Run:
```bash
git checkout master
git merge --no-ff vyntia/L3.1-core-app -m "Merge L3.1: extract core to apps.core (Django app)"
git log --oneline -3
```

Expected: merge commit como HEAD.

- [ ] **Step 3: Smoke test post-merge**

Run:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: ambos verdes con baseline 125/44/3.

---

## Definition of Done — checklist final

- [ ] `apps/api/core/` ya no existe
- [ ] `apps/api/apps/__init__.py` existe (vacío)
- [ ] `apps/api/apps/core/` existe con los 10 archivos `.py` originales + `apps.py` nuevo
- [ ] `INSTALLED_APPS` en `vyntia/settings/base.py` incluye `"apps.core.apps.CoreConfig"`
- [ ] Cero `from core.X` lines (excepto `django.core` que es stdlib)
- [ ] Cero `"core.X"` strings en settings (excepto `django.core` / `cache.backends`)
- [ ] `pyproject.toml` lists `["vyntia", "app_rrhh", "api", "apps", "apps.core"]`
- [ ] `pip install -e ".[dev]"` ejecuta sin errors
- [ ] `manage.py check` clean
- [ ] `pytest`: 125/44/3 baseline preservado
- [ ] `runserver` arranca y `/api/docs/` retorna HTTP 200
- [ ] Branch `vyntia/L3.1-core-app` con 2 commits (docs + chore) mergeada a master con `--no-ff`
- [ ] L3 master roadmap actualizado: L3.1 → ✅ con merge SHA
- [ ] Memoria del proyecto actualizada (handoff after merge): `active_subproject.md` con L3.1 ✅

---

## Después de L3.1

**Próximo plan:** L3.2 — extract `identity` app (Usuario → User, Rol, Permiso, auth views).

L3.2 es **alto riesgo** porque cambia `AUTH_USER_MODEL`. Requiere:
- Crear `apps/api/apps/identity/` con `User` model (rename de `Usuario`)
- Migración Django de RenameModel + AlterField
- Mover `app_rrhh/auth.py` → `apps/identity/auth.py`
- Mover auth views/serializers a la nueva app
- Cambiar `AUTH_USER_MODEL = "app_rrhh.Usuario"` → `"identity.User"`
- Coordinar tablas auth/sessions

Antes de L3.2, leer cuidadosamente:
- Spec § 3.2 (modelo identity)
- Django docs sobre `AUTH_USER_MODEL` migration: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#substituting-a-custom-user-model

Ejecutar el plan de L3.1 → merge → confirmar → solicitar `genera el plan de L3.2`.

---

## Notas para el ejecutor

- **`from .X import Y` (relative imports) dentro de `apps/core/` no se tocan.** Solo se tocan `from core.X` absolute imports.
- **`label = 'core_utils'`** es deliberado — evita colisión simbólica con `django.core`.
- **`apps.core` no tiene modelos**, así que NO hay migrations que correr para esta sub-PR. `manage.py makemigrations apps.core` no debe generar nada.
- **El `[tool.setuptools].packages` list crece con cada L3.X.** En L3.2: añade `"apps.identity"`. En L3.3: `"apps.organization"`. Etc.
- **drf_spectacular schema collisions (W001)** no se reducen en L3.1 — siguen vivas hasta que L3.10 elimine `app_rrhh/serializers.py`.
- **Windows Git Bash:** `find ... -print0 | xargs -0 sed -i` funciona; `sed -i` requiere `-i ''` en macOS pero no en Git Bash for Windows.
