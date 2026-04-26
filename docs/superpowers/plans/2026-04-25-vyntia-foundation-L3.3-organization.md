# VYNTIA Foundation L3.3 — Extract `organization` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los modelos de organización (`Area`, `HistorialUbicaciones`, `ConfiguracionEmpresa`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/organization/`. Class names quedan en español — el rename a inglés (Area→Department, etc.) es scope L3.10.

**Architecture:** L3.3 es **riesgo medio** — patrón establecido en L3.1+L3.2 ya validado: crear app, mover modelos, actualizar FK strings cross-app, NUCLEAR DB regenerate. Sin cambio de `AUTH_USER_MODEL` (eso fue L3.2). Lo nuevo en L3.3: Area es referenciado por `datos_laborales.py` y `contratos_adendas.py` (que se quedan en app_rrhh), por lo que sus FK strings same-app `'Area'` deben convertirse a string lazy `'organization.Area'`.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.3; § 3.2 "División de modelos"

> **Nota sobre `sistema.py`:** El spec § 3.2 mapea `sistema.py → SystemSetting` para organization. Pero `sistema.py` ya fue movido a `apps/identity/` en L3.2 porque su contenido (`Modulos`, `ModuloPermiso`, `RolPermisos`, `UsuarioRoles`) es claramente RBAC/identity, no organization. El "SystemSetting" del spec es un modelo NUEVO que no existe todavía — se creará cuando haga falta config global de tenant en sub-proyecto C (multi-tenancy). L3.3 NO crea SystemSetting; solo mueve los 3 archivos existentes.

**Pre-condiciones:**
- L3.2 mergeado a master (commit `7184e271`)
- Django 5.2.13, `apps/api/apps/{core,identity}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual (rol=5, permiso=23, modulos=31, usuarios=1)
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/organization/` existe con `apps.py`, `models/`, `migrations/`
- [ ] Modelos `Area`, `HistorialUbicaciones`, `ConfiguracionEmpresa` movidos a `apps/organization/models/`
- [ ] `app_rrhh/models/{area,ubicacion,configuracion_empresa}.py` eliminados
- [ ] `OrganizationConfig` en `LOCAL_APPS`
- [ ] FK strings `'Area'` en `app_rrhh/models/datos_laborales.py` y `contratos_adendas.py` actualizados a `'organization.Area'`
- [ ] FK strings `'Empleado'`, `'DocumentosDigitales'` en `apps/organization/models/ubicacion.py` actualizados a `'app_rrhh.Empleado'`, `'app_rrhh.DocumentosDigitales'`
- [ ] `apps/identity/models/usuario.py:371` inline import actualizado: `from apps.organization.models import Area`
- [ ] `app_rrhh/models/empleado.py:255,271` actualizados: `from apps.organization.models import HistorialUbicaciones`
- [ ] `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` regenerated SIN Area/HistorialUbicaciones/ConfiguracionEmpresa
- [ ] `apps/identity/migrations/0001_initial.py` + posibles `0002_*` regenerated
- [ ] `apps/organization/migrations/0001_initial.py` regenerated CON los 3 modelos
- [ ] `bd_vyntia` recreada con esquema fresco; rol > 0, permiso > 0, modulos > 0
- [ ] Imports actualizados: cero `from app_rrhh.models import {Area|HistorialUbicaciones|ConfiguracionEmpresa}` en código activo
- [ ] `pyproject.toml` `packages` incluye `"apps.organization"`
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.3-organization-app` mergeada a master con `--no-ff`
- [ ] L3 master roadmap actualizado: L3.3 → ✅, L3.4 → NEXT

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/organization/__init__.py` | empty |
| Create | `apps/api/apps/organization/apps.py` | `OrganizationConfig(AppConfig)` con `name="apps.organization"`, `label="organization"` |
| Create | `apps/api/apps/organization/models/__init__.py` | re-exporta `Area`, `HistorialUbicaciones`, `ConfiguracionEmpresa` |
| Move | `app_rrhh/models/area.py` → `apps/api/apps/organization/models/area.py` | sin cambios internos (FK `'self'` queda) |
| Move | `app_rrhh/models/ubicacion.py` → `apps/api/apps/organization/models/ubicacion.py` | actualizar FK strings: `'Empleado'`→`'app_rrhh.Empleado'`, `'DocumentosDigitales'`→`'app_rrhh.DocumentosDigitales'`. `'Area'` se queda igual (mismo app ahora). `'identity.Usuario'` ya estaba bien |
| Move | `app_rrhh/models/configuracion_empresa.py` → `apps/api/apps/organization/models/configuracion_empresa.py` | sin FKs, sin cambios |
| Create | `apps/api/apps/organization/migrations/__init__.py` | empty |
| Modify | `apps/api/app_rrhh/models/datos_laborales.py` | FK string `'Area'` → `'organization.Area'` |
| Modify | `apps/api/app_rrhh/models/contratos_adendas.py` | FK string `'Area'` → `'organization.Area'` |
| Modify | `apps/api/apps/identity/models/usuario.py` | inline `from app_rrhh.models import Area` (línea 371) → `from apps.organization.models import Area` |
| Modify | `apps/api/app_rrhh/models/empleado.py` | inline `from .ubicacion import HistorialUbicaciones` (líneas 255, 271) → `from apps.organization.models import HistorialUbicaciones` |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar exports de Area, HistorialUbicaciones, ConfiguracionEmpresa |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.organization.apps.OrganizationConfig"` a `LOCAL_APPS` |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.organization"` a `packages` |
| Modify (~12 files) | varios en `api/v1/`, `app_rrhh/services/`, `scripts/`, `tests/` | replace `from app_rrhh.models import ... {Area|HistorialUbicaciones|ConfiguracionEmpresa}` → `from apps.organization.models import ...` (mixed imports split) |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` (post-L3.2) | regenerated by `makemigrations` |
| Delete | `apps/identity/migrations/0001_initial.py` (post-L3.2) | regenerated |

**NO se toca en L3.3:**
- Class names (`Area`, `HistorialUbicaciones`, `ConfiguracionEmpresa` quedan en español; rename a `Department`, `Location`, `Company` es L3.10)
- Field names (`area_id`, `nombre_completo`, etc. quedan en español)
- Frontend (cero cambios — endpoints siguen siendo los mismos)
- Otros modelos en `app_rrhh/models/` (Empleado, Contratos, etc. — esos van en L3.4-L3.9)

**Estrategia destructiva (NUCLEAR — validada en L3.2):**
- Drop `bd_vyntia`, recrear, migrar fresh
- Eliminar migrations existentes y regenerarlas
- Re-seed via management commands existentes

---

## Task 1: Pre-flight — branch, baseline, backup

**Files:** ninguno (verificación)

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.2**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected:
- `pwd`: `/d/VYNTIA`
- `git status`: vacío (puede tener este plan untracked)
- HEAD: `673f1daa docs(L3.2): mark L3.2 merged, L3.3 as next` o más reciente

- [ ] **Step 2: Activar venv y confirmar versions**

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.3.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.3.dump
```

Expected: dump file ~250-500 KB. Si falla, **detente**.

- [ ] **Step 5: Crear branch L3.3**

```bash
git checkout -b vyntia/L3.3-organization-app
git status --short
```

Expected: `On branch vyntia/L3.3-organization-app`, working tree limpio (excepto plan untracked).

---

## Task 2: Comitear el plan L3.3 en la branch

- [ ] **Step 1: Stage y commit**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.3-organization.md
git commit -m "docs(L3.3): add organization app extraction plan"
```

Expected: 1 file changed.

---

## Task 3: Crear estructura del package `apps/organization/`

**Files:**
- Create: `apps/api/apps/organization/__init__.py` (empty)
- Create: `apps/api/apps/organization/apps.py`
- Create: `apps/api/apps/organization/models/__init__.py` (placeholder, populado en Task 5)
- Create: `apps/api/apps/organization/migrations/__init__.py` (empty)

- [ ] **Step 1: Crear directorios**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/organization/models
mkdir -p apps/api/apps/organization/migrations
touch apps/api/apps/organization/__init__.py
touch apps/api/apps/organization/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/organization/apps.py`**

Use Write tool en `D:/VYNTIA/apps/api/apps/organization/apps.py` con contenido EXACTO:

```python
"""AppConfig for the `apps.organization` Django app — VYNTIA organizational structure.

Owns the structural entities of a tenant organization:
- Area (departments / org units)
- HistorialUbicaciones (employee location/area movement history)
- ConfiguracionEmpresa (company-level configuration / branding)

Bounded context boundary: organization defines WHERE work happens (which
department, which physical location). It does not define employees themselves
(that's `apps.employees` in L3.4) nor identity (that's `apps.identity`).
"""

from django.apps import AppConfig


class OrganizationConfig(AppConfig):
    name = "apps.organization"
    label = "organization"
    verbose_name = "VYNTIA Organization"
```

- [ ] **Step 3: Crear placeholder `apps/organization/models/__init__.py`**

```python
"""Organization models — re-exports for backward-compatible imports.

Populated when models are physically moved in Task 4.
"""
```

---

## Task 4: Mover los 3 model files con `git mv`

**Files:**
- Move: `apps/api/app_rrhh/models/area.py` → `apps/api/apps/organization/models/area.py`
- Move: `apps/api/app_rrhh/models/ubicacion.py` → `apps/api/apps/organization/models/ubicacion.py`
- Move: `apps/api/app_rrhh/models/configuracion_empresa.py` → `apps/api/apps/organization/models/configuracion_empresa.py`

- [ ] **Step 1: Defensive — kill any stale Python procs**

```bash
ps -W 2>/dev/null | grep -iE "python" | grep VYNTIA || echo "no VYNTIA python procs"
```

If any appear:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force
```

- [ ] **Step 2: `git mv` los 3 archivos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/area.py apps/api/apps/organization/models/area.py
git mv apps/api/app_rrhh/models/ubicacion.py apps/api/apps/organization/models/ubicacion.py
git mv apps/api/app_rrhh/models/configuracion_empresa.py apps/api/apps/organization/models/configuracion_empresa.py
```

- [ ] **Step 3: Verificar layout**

```bash
ls apps/api/apps/organization/models/
ls apps/api/app_rrhh/models/area.py 2>&1 || echo "OK: removed from app_rrhh"
```

Expected: organization/models/ tiene `__init__.py`, `area.py`, `ubicacion.py`, `configuracion_empresa.py`.

---

## Task 5: Update FK strings dentro de `apps/organization/models/ubicacion.py`

**Files:**
- Modify: `apps/api/apps/organization/models/ubicacion.py`

**Por qué:** Después de moverse, `ubicacion.py` está en `apps/organization/`. Sus FKs:
- `'Empleado'` (línea 39) — Empleado vive en `app_rrhh` → debe ser `'app_rrhh.Empleado'`
- `'Area'` (líneas 45, 53) — Area ahora vive en mismo app `organization` → queda `'Area'`
- `'DocumentosDigitales'` (línea 81) — vive en `app_rrhh` → `'app_rrhh.DocumentosDigitales'`
- `'identity.Usuario'` (línea 114) — ya está bien (L3.2 lo dejó así)

- [ ] **Step 1: Update Empleado FK**

Use Edit tool en `D:/VYNTIA/apps/api/apps/organization/models/ubicacion.py`:

- old_string:
```python
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.CASCADE,
        related_name='historial_ubicaciones',
        help_text='ID del empleado'
    )
```
- new_string:
```python
    empleado = models.ForeignKey(
        'app_rrhh.Empleado',
        on_delete=models.CASCADE,
        related_name='historial_ubicaciones',
        help_text='ID del empleado'
    )
```

- [ ] **Step 2: Update DocumentosDigitales FK**

- old_string:
```python
    documento = models.ForeignKey(
        'DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ubicaciones_documento',
        help_text='ID del documento adjunto'
    )
```
- new_string:
```python
    documento = models.ForeignKey(
        'app_rrhh.DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ubicaciones_documento',
        help_text='ID del documento adjunto'
    )
```

- [ ] **Step 3: Verificar que `'Area'` y `'identity.Usuario'` quedan intactos**

```bash
grep -n "'Area'\|'identity.Usuario'" apps/api/apps/organization/models/ubicacion.py
```

Expected: 2 matches `'Area'` (líneas 45, 53) y 1 match `'identity.Usuario'` (línea 114).

- [ ] **Step 4: Verificar update completo**

```bash
grep -n "ForeignKey" apps/api/apps/organization/models/ubicacion.py | head -10
```

Expected: 5 ForeignKey lines, todas con strings correctos (Empleado lazy, Area same-app, DocumentosDigitales lazy, Usuario already-lazy).

---

## Task 6: Update FK strings `'Area'` en modelos que se quedan en `app_rrhh`

**Files:**
- Modify: `apps/api/app_rrhh/models/datos_laborales.py`
- Modify: `apps/api/app_rrhh/models/contratos_adendas.py`

**Por qué:** Estos modelos siguen en `app_rrhh` pero antes Area era same-app (`'Area'`). Ahora Area vive en `organization`, entonces deben referenciarla como `'organization.Area'`.

- [ ] **Step 1: Update `datos_laborales.py`**

Use Edit tool en `apps/api/app_rrhh/models/datos_laborales.py`:

- old_string:
```python
    area = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='empleados_laborales'
    )
```
- new_string:
```python
    area = models.ForeignKey(
        'organization.Area',
        on_delete=models.PROTECT,
        related_name='empleados_laborales'
    )
```

- [ ] **Step 2: Update `contratos_adendas.py`**

Use Edit tool:
- old_string:
```python
    area = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='contratos_adendas_area',
        help_text='Área donde se ejecuta el contrato'
    )
```
- new_string:
```python
    area = models.ForeignKey(
        'organization.Area',
        on_delete=models.PROTECT,
        related_name='contratos_adendas_area',
        help_text='Área donde se ejecuta el contrato'
    )
```

- [ ] **Step 3: Verificar que cero FKs same-app `'Area'` quedan en app_rrhh**

```bash
grep -rn "ForeignKey.*'Area'\|ForeignKey.*\"Area\"\|to=.*'Area'\b" apps/api/app_rrhh/models --include="*.py" || echo "OK: cero same-app Area refs"
```

Expected: `OK`.

---

## Task 7: Update inline imports que usan organization-models desde otros files

**Files:**
- Modify: `apps/api/apps/identity/models/usuario.py` (línea 371)
- Modify: `apps/api/app_rrhh/models/empleado.py` (líneas 255, 271)

- [ ] **Step 1: `apps/identity/models/usuario.py:371` — inline import en `areas_accesibles()`**

Read primero para confirmar contexto:
```bash
grep -n "from app_rrhh.models import Area\|from apps.organization" apps/api/apps/identity/models/usuario.py
```

Expected: 1 match en línea ~371.

Use Edit tool:
- old_string: `        from app_rrhh.models import Area`
- new_string: `        from apps.organization.models import Area`

- [ ] **Step 2: `app_rrhh/models/empleado.py:255,271` — inline imports**

```bash
grep -n "from .ubicacion import\|from apps.organization" apps/api/app_rrhh/models/empleado.py
```

Expected: 2 matches `from .ubicacion import HistorialUbicaciones`.

Use Edit tool con `replace_all=true`:
- old_string: `from .ubicacion import HistorialUbicaciones`
- new_string: `from apps.organization.models import HistorialUbicaciones`

Verifica:
```bash
grep -n "from .ubicacion\|from apps.organization" apps/api/app_rrhh/models/empleado.py
```

Expected: 0 matches `from .ubicacion`; 2 matches `from apps.organization.models import HistorialUbicaciones`.

---

## Task 8: Crear `apps/organization/models/__init__.py` con re-exports

**Files:**
- Modify: `apps/api/apps/organization/models/__init__.py` (replace placeholder)

- [ ] **Step 1: Use Write con contenido**

```python
"""Organization models — re-exports for backward-compatible imports."""

from .area import Area
from .configuracion_empresa import ConfiguracionEmpresa
from .ubicacion import HistorialUbicaciones

__all__ = [
    "Area",
    "ConfiguracionEmpresa",
    "HistorialUbicaciones",
]
```

- [ ] **Step 2: Smoke import check**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.organization.models import Area, HistorialUbicaciones, ConfiguracionEmpresa; print('OK')"
cd ../..
```

Expected: `OK`. Si falla, hay un import roto en uno de los 3 model files (probablemente algo de `area.py` que importaba `.empleado` u otro relative).

NOTE: `manage.py check` aún NO va a pasar hasta Task 11 (el LOCAL_APPS no incluye organization todavía).

---

## Task 9: Update `app_rrhh/models/__init__.py` — quitar exports de organization

**Files:**
- Modify: `apps/api/app_rrhh/models/__init__.py`

- [ ] **Step 1: Read file y identificar líneas a remover**

```bash
grep -n "from .area\|from .ubicacion\|from .configuracion_empresa\|\"Area\"\|\"HistorialUbicaciones\"\|\"ConfiguracionEmpresa\"" apps/api/app_rrhh/models/__init__.py
```

- [ ] **Step 2: Eliminar las líneas con Edit tool**

Use Edit tool 3 veces:
- old_string: `from .area import Area`
- new_string: (remove the line completely — replace with empty or merge with adjacent)

Mejor: usa Read para obtener el contexto exacto antes y después de cada line, luego Edit con suficiente contexto para hacer un replacement clean. Por ejemplo:

- old_string:
```python
# Importar todos los modelos para mantener compatibilidad
from .area import Area

# from .contratos import ContratoAdenda  # Comentado para evitar conflicto de tabla
from .configuracion_empresa import ConfiguracionEmpresa
```
- new_string:
```python
# Importar todos los modelos para mantener compatibilidad

# from .contratos import ContratoAdenda  # Comentado para evitar conflicto de tabla
```

Y similar para `from .ubicacion import HistorialUbicaciones`.

En `__all__`, eliminar `"Area"`, `"HistorialUbicaciones"`, `"ConfiguracionEmpresa"`.

- [ ] **Step 3: Verificar limpieza**

```bash
grep -n "from .area\|from .ubicacion\|from .configuracion_empresa\|\"Area\"\|\"HistorialUbicaciones\"\|\"ConfiguracionEmpresa\"" apps/api/app_rrhh/models/__init__.py || echo "OK: removed from app_rrhh"
```

Expected: `OK`.

---

## Task 10: Bulk update absolute imports across the codebase

**Files (~12):** archivos en `api/v1/`, `app_rrhh/services/`, `scripts/`, `tests/`. Lista exacta sale del grep.

**Patrón:** `from app_rrhh.models import {Area|HistorialUbicaciones|ConfiguracionEmpresa}` → `from apps.organization.models import ...`

- [ ] **Step 1: Inventario pre-replace**

```bash
cd D:/VYNTIA/apps/api
grep -rln "from app_rrhh\.models import.*\(Area\|HistorialUbicaciones\|ConfiguracionEmpresa\)" --include="*.py" | sort
```

Expected: ~7-12 archivos en api/v1/, scripts/, tests/, app_rrhh/services/.

- [ ] **Step 2: Sed para imports puros (single-import lines)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" -not -path "*/migrations/*" -not -path "*/__pycache__/*" -not -path "*/apps/organization/*" -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(Area\)$|from apps.organization.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(HistorialUbicaciones\)$|from apps.organization.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(ConfiguracionEmpresa\)$|from apps.organization.models import \1|g'
```

- [ ] **Step 3: Manual fix para imports mezclados (single-line con coma)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import" --include="*.py" | grep -E "Area|HistorialUbicaciones|ConfiguracionEmpresa" | head -15
```

Para cada match, Read el archivo, identificar la línea import, y Edit:
- Si línea es `from app_rrhh.models import A, Area, B` → split en `from app_rrhh.models import A, B` + `from apps.organization.models import Area`
- Mantener orden alfabético de los names organization en el nuevo import

Organization model names a reconocer: `Area`, `HistorialUbicaciones`, `ConfiguracionEmpresa`.

- [ ] **Step 4: Manual fix para imports multi-línea con parens**

```bash
cd D:/VYNTIA/apps/api
grep -rn -B 0 -A 8 "from app_rrhh\.models import (" --include="*.py" | head -60
```

Para cada match, refactor:
```python
from app_rrhh.models import (
    Empleado,
    Area,
    OtraCosa,
)
```
→
```python
from app_rrhh.models import (
    Empleado,
    OtraCosa,
)
from apps.organization.models import (
    Area,
)
```

- [ ] **Step 5: Update inline imports inside function bodies**

```bash
cd D:/VYNTIA/apps/api
grep -rn "    from app_rrhh\.models import" --include="*.py" | grep -E "Area|HistorialUbicaciones|ConfiguracionEmpresa"
```

Para cada match, Edit replacing `app_rrhh.models` → `apps.organization.models` (preservando indentación).

- [ ] **Step 6: Verificación final**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(Area\|HistorialUbicaciones\|ConfiguracionEmpresa\)" --include="*.py" || echo "OK: cero matches"
```

Expected: `OK: cero matches`. Si aparece algún match, tipo `Area2` o `AreaSomething`, ajustar regex; si es genuino missed import, edit manualmente.

---

## Task 11: Update settings — registrar `OrganizationConfig`

**Files:**
- Modify: `apps/api/vyntia/settings/base.py`

- [ ] **Step 1: Update `LOCAL_APPS`**

Current state:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "app_rrhh",
]
```

Use Edit tool:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "app_rrhh",
]
```
- new_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "app_rrhh",
]
```

- [ ] **Step 2: Verificar**

```bash
grep -A 6 "^LOCAL_APPS" apps/api/vyntia/settings/base.py
```

Expected: ve los 4 elementos en orden.

---

## Task 12: Update `pyproject.toml` packages

**Files:**
- Modify: `apps/api/pyproject.toml`

- [ ] **Step 1: Edit packages list**

Current (post-L3.2):
```toml
packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity"]
```

Use Edit tool:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization"]`

- [ ] **Step 2: Reinstall editable**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`. Si falla con "package directory 'apps.organization' does not exist", verifica que `apps/api/apps/organization/__init__.py` y `apps/api/apps/organization/models/__init__.py` existen.

---

## Task 13: NUCLEAR DB — drop bd_vyntia + delete migrations + regenerate

**Files:**
- Delete: `apps/api/app_rrhh/migrations/0001_initial.py` y `0002_initial.py`
- Delete: `apps/api/apps/identity/migrations/0001_initial.py`
- Auto-create: nuevas `0001_initial.py` (y posibles `0002_initial.py` por FK ordering) para los 4 apps: app_rrhh, identity, organization, y demás Django built-in

**Patrón validado en L3.2.** Backup en `/tmp/bd_vyntia_pre_L3.3.dump` como red de seguridad.

- [ ] **Step 1: Drop bd_vyntia**

Kill any Python procs first:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

Expected: `DROP DATABASE`.

- [ ] **Step 2: Delete existing migration files (post-L3.2 fresh ones)**

```bash
cd D:/VYNTIA/apps/api/app_rrhh/migrations
git rm 0001_initial.py 2>&1 | tail -2
git rm 0002_initial.py 2>&1 | tail -2 || echo "no 0002"
ls
cd D:/VYNTIA/apps/api/apps/identity/migrations
git rm 0001_initial.py 2>&1 | tail -2
ls
cd D:/VYNTIA
```

Expected: solo `__init__.py` en cada `migrations/` directory.

- [ ] **Step 3: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

NOTE: PGPASSWORD env var es necesario por el known issue UnicodeDecodeError documented en L3.2.

Expected output:
- `Migrations for 'app_rrhh':` con `0001_initial.py` (sin Area/Ubicacion/ConfiguracionEmpresa, sin Usuario/Rol/Permiso)
- `Migrations for 'identity':` con `0001_initial.py` (Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso)
- `Migrations for 'organization':` con `0001_initial.py` (Area, HistorialUbicaciones, ConfiguracionEmpresa)
- Posibles `0002_initial.py` para resolver FK ordering circular

- [ ] **Step 4: Verificar migration content**

```bash
echo "=== organization 0001 ==="
grep -E "name='(Area|HistorialUbicaciones|ConfiguracionEmpresa)'" apps/api/apps/organization/migrations/0001_initial.py | head -5
echo "(expected: 3)"
echo ""
echo "=== app_rrhh 0001 — should NOT have Area/Ubicacion/Empresa ==="
grep -E "name='(Area|HistorialUbicaciones|ConfiguracionEmpresa)'" apps/api/app_rrhh/migrations/0001_initial.py | head -5
echo "(expected: 0)"
echo ""
echo "=== identity 0001 — same as L3.2, should have 7 ==="
grep -E "name='(Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso)'" apps/api/apps/identity/migrations/0001_initial.py | wc -l
echo "(expected: 7)"
```

- [ ] **Step 5: Recrear bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

Expected: `CREATE DATABASE`.

- [ ] **Step 6: Aplicar migrations**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -20
cd ../..
```

Expected: secuencia de `Applying X.0001_initial... OK` para auth, contenttypes, sessions, identity, organization, app_rrhh, etc.

Si error de FK ordering, Django debería resolverlo via dependencies. Si persiste, añadir manualmente `('app_rrhh', '0001_initial')` a `dependencies` en `apps/identity/migrations/0001_initial.py` (o vice versa según necesidad).

- [ ] **Step 7: Verificar schema**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\dt" 2>&1 | grep -cE "^ public"
```

Expected: ~40+ tables.

---

## Task 14: Re-seed via management commands

- [ ] **Step 1: Run setup_roles_permisos**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Si falla con `ImportError: cannot import name X from app_rrhh.models`, el comando fue actualizado en L3.2 — re-revisa imports.

- [ ] **Step 2: Run seed_menu**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

- [ ] **Step 3: Verificar seed**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'usuarios', COUNT(*) FROM usuarios UNION ALL SELECT 'area', COUNT(*) FROM area;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, usuarios >= 0, area = 0 (no seed for areas yet — that's fine).

---

## Task 15: Smoke tests

- [ ] **Step 1: `manage.py check`**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 2: pytest baseline**

```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`. Si shifts, diagnose.

- [ ] **Step 3: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l33.log 2>&1 &
SERVER_PID=$!
sleep 8
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

Then kill stragglers:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

Expected: HTTP 200.

- [ ] **Step 4: Cleanup greps**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: app_rrhh.models import of organization-models ==="
grep -rn "from app_rrhh\.models import" --include="*.py" | grep -E "Area|HistorialUbicaciones|ConfiguracionEmpresa" || echo "OK: cero matches"
echo ""
echo "=== B: same-app FK 'Area' in app_rrhh ==="
grep -rn "ForeignKey.*'Area'\|to=.*'Area'\b" apps/api/app_rrhh/models --include="*.py" || echo "OK: cero matches"
echo ""
echo "=== C: relative .ubicacion / .area / .configuracion_empresa imports ==="
grep -rn "from .ubicacion\|from .area\|from .configuracion_empresa" --include="*.py" || echo "OK: cero matches"
cd ../..
```

Expected: ALL sections return `OK`.

---

## Task 16: Final commit

- [ ] **Step 1: Review git status**

```bash
cd D:/VYNTIA
git status --short | head -30
```

Expected: ~10-25 files (3 renames, 4 new files in organization/, modifications across settings/pyproject/imports/migrations).

- [ ] **Step 2: Stage all + atomic commit**

```bash
git add apps/api/
git commit -m "chore(L3.3): extract organization app (Area, HistorialUbicaciones, ConfiguracionEmpresa) — fresh migrations after BD nuke + reseed"
```

- [ ] **Step 3: Verificar git history**

```bash
git log --oneline vyntia/L3.3-organization-app ^master | head -5
git status --short
```

Expected:
- 2 commits: `docs(L3.3): add organization app extraction plan` + `chore(L3.3): extract organization app ...`
- `git status` empty

---

## Task 17: Merge a master

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta: ¿Mergear `vyntia/L3.3-organization-app` a master con `--no-ff`?

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.3-organization-app -m "Merge L3.3: extract organization app (Area, HistorialUbicaciones, ConfiguracionEmpresa)"
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

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/organization/{__init__.py, apps.py, models/{__init__.py, area.py, ubicacion.py, configuracion_empresa.py}, migrations/{__init__.py, 0001_initial.py}}` existen
- [ ] `app_rrhh/models/{area, ubicacion, configuracion_empresa}.py` removidos
- [ ] FK strings same-app `'Area'` en `app_rrhh/models/{datos_laborales, contratos_adendas}.py` actualizadas a `'organization.Area'`
- [ ] FK strings dentro de `apps/organization/models/ubicacion.py`: `'Empleado'`→`'app_rrhh.Empleado'`, `'DocumentosDigitales'`→`'app_rrhh.DocumentosDigitales'`
- [ ] Inline imports actualizados en `apps/identity/models/usuario.py:371` y `app_rrhh/models/empleado.py:255,271`
- [ ] `app_rrhh/models/__init__.py` no exporta Area/HistorialUbicaciones/ConfiguracionEmpresa
- [ ] `apps/organization/models/__init__.py` re-exporta los 3 modelos
- [ ] `LOCAL_APPS` en `vyntia/settings/base.py` incluye `OrganizationConfig`
- [ ] `pyproject.toml` `packages` incluye `"apps.organization"`
- [ ] Migrations regenerated; organization tiene los 3 modelos; app_rrhh ya no
- [ ] bd_vyntia recreada con esquema fresco; rol > 0, permiso > 0, modulos > 0
- [ ] `manage.py check` clean
- [ ] `pytest`: 125/44/3
- [ ] runserver `/api/docs/` HTTP 200
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.3 ✅, L3.4 NEXT

---

## Después de L3.3

**Próximo plan:** L3.4 — extract `employees` app (Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones).

L3.4 es **el más grande de los sub-PRs middle** porque Empleado es el HUB del modelo de datos — casi todos los modelos de dominio le hacen FK. Riesgos previstos:
- Muchos FK strings `'Empleado'` cross-app que actualizar
- DatosFamiliares, DatosAcademicos, CursosCertificaciones todos referencian Empleado
- empleado.py es 700+ líneas, con muchos métodos que importan otros modelos

L3.4 puede tomar 2-3 horas de ejecución.

---

## Notas para el ejecutor

- **Patrón NUCLEAR validado en L3.2** — re-aplicar sin modificaciones.
- **`PGPASSWORD='Demenci4@'` env var** explícito con cada `manage.py` por el known issue UnicodeDecodeError.
- **Class names quedan en español** — rename a inglés es L3.10.
- **`apps/organization/models/ubicacion.py` `'Area'` FK** queda igual porque ahora Area es same-app dentro de organization.
- **`'Empleado'` FK strings dentro de ubicacion.py** deben ser `'app_rrhh.Empleado'` hasta que L3.4 mueva Empleado.
- **Stale Python procs:** Si `psql DROP DATABASE` falla con "in use", mata procesos python con PowerShell y retry.
- **Windows Git Bash**: forward slashes; `psql.exe` ruta absoluta.
