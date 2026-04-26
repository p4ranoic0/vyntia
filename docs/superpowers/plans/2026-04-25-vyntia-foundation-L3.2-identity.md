# VYNTIA Foundation L3.2 — Extract `identity` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los modelos de identidad (`Usuario`, `Rol`, `Permiso`, `RolPermisos`, `UsuarioRoles`, `Modulos`, `ModuloPermiso`) + custom auth backend (`CustomAuthBackend`) + `UsuarioManager` desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/identity/`. Cambiar `AUTH_USER_MODEL = "app_rrhh.Usuario"` → `"identity.Usuario"`. Class names quedan en español (Usuario/Rol/Permiso) — el rename inglés se hace en L3.10.

**Architecture:** L3.2 es **alto riesgo** porque cambia `AUTH_USER_MODEL` mid-project. Estrategia adoptada: **NUCLEAR** — `bd_vyntia` está casi vacío (0 usuarios/roles/permisos, 6 modulos seed regenerable), así que dropeamos la BD, eliminamos `app_rrhh/migrations/00*.py` (27 archivos) y regeneramos fresh. Esto evita las acrobacias de `SeparateDatabaseAndState` y deja una baseline limpia de migraciones para L3.3-L3.9. Los seeds se restauran via management commands existentes (`setup_roles_permisos`, `seed_menu`).

**Tech Stack:** Django 5.2 `AppConfig`, custom user model migration, `pg_dump` backup (paranoia), Django management commands para re-seed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.2; § 3.2 "División de modelos"

**Pre-condiciones:**
- L3.1 mergeado a master (commit `faa108a3`)
- Django 5.2.13, `apps/api/apps/core/` operativo
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual + 6 modulos seed
- venv en `D:/VYNTIA/.venv/`
- PowerShell access para `psql.exe` (path: `C:/Program Files/PostgreSQL/15/bin/psql.exe`)

**Definition of Done:**
- [ ] `apps/api/apps/identity/` existe con `apps.py`, `models/`, `migrations/`, `auth.py`, `managers.py`
- [ ] Modelos `Usuario`, `Rol`, `Permiso`, `RolPermisos`, `UsuarioRoles`, `Modulos`, `ModuloPermiso` movidos a `apps/identity/models/`
- [ ] `app_rrhh/models/{usuario,roles,sistema}.py` eliminados
- [ ] `app_rrhh/auth.py` eliminado; `apps/identity/auth.py` existe con `CustomAuthBackend`
- [ ] `apps/identity/managers.py` contiene `UsuarioManager`
- [ ] `AUTH_USER_MODEL = "identity.Usuario"` en `vyntia/settings/base.py`
- [ ] `AUTHENTICATION_BACKENDS` apunta a `apps.identity.auth.CustomAuthBackend`
- [ ] `apps.identity.apps.IdentityConfig` en `LOCAL_APPS`
- [ ] `app_rrhh/migrations/00XX*.py` (27 archivos) eliminados; re-generated `app_rrhh/migrations/0001_initial.py` (sin Usuario/Rol/Permiso/etc.)
- [ ] `apps/identity/migrations/0001_initial.py` existe con todos los modelos identity
- [ ] `bd_vyntia` recreada y migrada con esquema nuevo
- [ ] 6 modulos re-seeded via `manage.py seed_menu`
- [ ] Imports actualizados: cero `from app_rrhh.models import Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso` en el código (excepto en backups/legacy)
- [ ] `apps/core/{decorators,middleware,permissions}.py` actualizados: ya no importan de `app_rrhh.models`, ahora importan de `apps.identity.models`
- [ ] `pyproject.toml` `packages` incluye `"apps.identity"` y submódulos relevantes
- [ ] `python manage.py check --settings=vyntia.settings.development` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.2-identity-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/identity/__init__.py` | empty |
| Create | `apps/api/apps/identity/apps.py` | `IdentityConfig(AppConfig)` con `name="apps.identity"`, `label="identity"` |
| Create | `apps/api/apps/identity/models/__init__.py` | re-exporta Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso |
| Move | `app_rrhh/models/usuario.py` → `apps/api/apps/identity/models/usuario.py` | con FK a Empleado convertido a string lazy `"app_rrhh.Empleado"` |
| Move | `app_rrhh/models/roles.py` → `apps/api/apps/identity/models/roles.py` | sin cambios estructurales |
| Move | `app_rrhh/models/sistema.py` → `apps/api/apps/identity/models/sistema.py` | FKs a Usuario/Rol/Permiso siguen siendo same-app, no necesitan strings |
| Move | `app_rrhh/auth.py` → `apps/api/apps/identity/auth.py` | actualizar imports a relative |
| Create | `apps/api/apps/identity/managers.py` | `UsuarioManager` extraído de `app_rrhh/managers.py` |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar exports de Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso |
| Modify | `apps/api/app_rrhh/managers.py` | quitar `UsuarioManager` (movido a identity) |
| Create | `apps/api/apps/identity/migrations/__init__.py` | empty |
| Create (auto) | `apps/api/apps/identity/migrations/0001_initial.py` | autogenerado por `makemigrations` |
| Delete | `apps/api/app_rrhh/migrations/00*.py` (27 archivos) | mantener `__init__.py` |
| Create (auto) | `apps/api/app_rrhh/migrations/0001_initial.py` | autogenerado, sin Usuario/Rol/Permiso |
| Modify | `apps/api/vyntia/settings/base.py` | AUTH_USER_MODEL, AUTHENTICATION_BACKENDS, LOCAL_APPS |
| Modify (~12 files) | `apps/api/api/v1/**/*.py`, `apps/api/app_rrhh/management/commands/*.py`, `apps/api/app_rrhh/filters.py`, `apps/api/apps/core/{decorators,middleware,permissions}.py` | replace `from app_rrhh.models import {Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso}` → `from apps.identity.models import ...` |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.identity"`, `"apps.identity.models"`, `"apps.identity.migrations"` a `packages` |

**NO se toca en L3.2:**
- Class names (`Usuario` queda en español; rename a `User` es L3.10)
- Field names (`nombres_usuario`, `apellidos_usuario`, etc. quedan en español)
- `app_rrhh/migrations/__init__.py` (queda vacío para mantener el package)
- Frontend (cero cambios — los endpoints siguen siendo los mismos: `/api/v1/auth/`)
- Otros modelos en `app_rrhh/models/` (Area, Empleado, etc. — esos van en L3.3, L3.4, etc.)

**Estrategia destructiva (NUCLEAR):**
- Eliminar 27 migraciones existentes en `app_rrhh/migrations/`
- Drop `bd_vyntia`, recrear, migrar fresh
- Re-seed con management commands
- Razón: bd_vyntia tiene casi cero datos productivos (0 users/rol/permisos, 6 modulos regenerables); preservar migraciones via SeparateDatabaseAndState requiere acrobacias que se repetirían 8 veces más en L3.3-L3.9

---

## Task 1: Pre-flight — branch, baseline, backup paranoia

**Files:** ninguno (verificación + branch + backup BD)

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.1**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected:
- `pwd`: `/d/VYNTIA`
- `git status`: vacío (puede tener el plan L3.2 untracked, OK)
- HEAD: `f54da901 docs(L3.1): mark L3.1 merged, L3.2 as next` o más reciente

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

- [ ] **Step 4: Backup bd_vyntia (paranoia — task is destructive)**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.2.dump 2>&1 | tail -5
ls -lh /tmp/bd_vyntia_pre_L3.2.dump
```

Expected: dump file ~100KB-1MB (depends on schema + 6 modulos rows). Si pg_dump falla, **detente** — el backup es seguro de NO PROCEDER.

NOTA: El password ASCII confirmado en L1 es `Demenci4@`.

- [ ] **Step 5: Document state pre-task**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\dt" 2>&1 | wc -l
echo "rows:"
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'usuarios:' as t, COUNT(*) FROM usuarios UNION ALL SELECT 'modulos:', COUNT(*) FROM modulos UNION ALL SELECT 'rol:', COUNT(*) FROM rol UNION ALL SELECT 'permiso:', COUNT(*) FROM permiso;"
```

Expected: ~46 lines from `\dt`; usuarios/rol/permiso count 0; modulos count 6.

Si los counts difieren significativamente (ej. usuarios > 0), **detente** — alguien sembró datos productivos que se perderían en el nuke. Coordina antes de continuar.

- [ ] **Step 6: Crear branch L3.2**

```bash
git checkout -b vyntia/L3.2-identity-app
git status
```

Expected: `On branch vyntia/L3.2-identity-app`.

---

## Task 2: Comitear el plan L3.2 en la branch

**Files:**
- `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.2-identity.md` (untracked)

- [ ] **Step 1: Stage y commit**

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.2-identity.md
git commit -m "docs(L3.2): add identity app extraction plan"
```

Expected: 1 file changed.

---

## Task 3: Crear estructura del package `apps/identity/`

**Files:**
- Create: `apps/api/apps/identity/__init__.py` (empty)
- Create: `apps/api/apps/identity/apps.py`
- Create: `apps/api/apps/identity/models/__init__.py` (placeholder por ahora — se popula en Task 5)
- Create: `apps/api/apps/identity/migrations/__init__.py` (empty)

- [ ] **Step 1: Crear directorios**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/identity/models
mkdir -p apps/api/apps/identity/migrations
touch apps/api/apps/identity/__init__.py
touch apps/api/apps/identity/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/identity/apps.py`**

Use Write tool en `D:/VYNTIA/apps/api/apps/identity/apps.py` con contenido EXACTO:

```python
"""AppConfig for the `apps.identity` Django app — VYNTIA identity & access management.

Owns the User model (custom AUTH_USER_MODEL), Roles, Permissions and the
RBAC junction tables. Also hosts the custom authentication backend.

Bounded context boundary: identity defines WHO can access the system; it does
not define WHAT they can do in business processes (that's per-domain via
service-layer permission checks).
"""

from django.apps import AppConfig


class IdentityConfig(AppConfig):
    name = "apps.identity"
    label = "identity"
    verbose_name = "VYNTIA Identity & Access"
```

- [ ] **Step 3: Crear placeholder `apps/identity/models/__init__.py`**

```python
"""Identity models — re-exports for backward-compatible imports.

Populated when models are physically moved in Task 5.
"""
```

(Placeholder. Task 5 lo popula con re-exports reales.)

---

## Task 4: Crear `apps/identity/managers.py` con `UsuarioManager`

**Files:**
- Create: `apps/api/apps/identity/managers.py`
- Modify: `apps/api/app_rrhh/managers.py` (eliminar `UsuarioManager`)

- [ ] **Step 1: Inspeccionar `UsuarioManager` actual**

```bash
cd D:/VYNTIA
grep -n "class UsuarioManager" apps/api/app_rrhh/managers.py
```

Identifica las líneas donde empieza y termina la clase. Lee el bloque completo:

```bash
grep -n "^class " apps/api/app_rrhh/managers.py
```

Esto te da los limites entre `UsuarioManager` y la siguiente clase. Lee ese rango con la tool Read.

- [ ] **Step 2: Crear `apps/identity/managers.py` con la clase `UsuarioManager` extraída literalmente**

Sub-step 2a — Leer la clase del archivo original:

```bash
cd D:/VYNTIA
grep -n "^class " apps/api/app_rrhh/managers.py
```

Esto te da los rangos de las clases. Anota la línea de inicio de `class UsuarioManager` y la línea de la siguiente `class X` (que marca el fin de UsuarioManager).

Sub-step 2b — Leer el bloque exacto de UsuarioManager:

Use el Read tool sobre `apps/api/app_rrhh/managers.py` con offset = línea inicio de UsuarioManager, limit = (línea siguiente clase) - (línea inicio UsuarioManager). Anota la docstring, los imports que usa, y los método bodies completos.

Sub-step 2c — Verificar imports al inicio de `app_rrhh/managers.py`:

```bash
sed -n '1,15p' apps/api/app_rrhh/managers.py
```

Anota qué imports están al top — `UsuarioManager` puede usar algunos de ellos. Imports comunes: `from datetime import datetime, timedelta`, `from typing import ...`, `from django.contrib.auth.models import BaseUserManager`, `from django.db import models`, `from django.db.models import Count, Q`, `from django.utils import timezone`.

Sub-step 2d — Crear `apps/api/apps/identity/managers.py` con Write tool. El contenido tiene tres bloques:

1. Module docstring (1 línea):
```python
"""Custom managers for identity models."""
```

2. Imports (copia LITERALMENTE los imports que UsuarioManager necesita — solo esos, no agregues `BaseUserManager` si la clase original no lo usa). Identifica los imports usados leyendo el body de UsuarioManager.

3. La clase `UsuarioManager` completa, copiada VERBATIM desde `app_rrhh/managers.py`. Mantén indentación, docstrings, methods. NO modifiques nada del body excepto si hay un `from .models import Usuario` (que sigue siendo correcto en la nueva ubicación porque `.models` resuelve a `apps.identity.models`).

Sub-step 2e — Verificar parse syntax:

```bash
python -c "import ast; ast.parse(open('D:/VYNTIA/apps/api/apps/identity/managers.py').read()); print('OK: parses')"
```

Expected: `OK: parses`. Si AST falla, hay error sintáctico — revisa indentación.

- [ ] **Step 3: Eliminar `UsuarioManager` de `app_rrhh/managers.py`**

Use Edit tool para eliminar la clase `UsuarioManager` y dejar solo `AreaManager`, `EmpleadoManager`, etc. (las que existan en ese archivo).

Verifica:
```bash
grep -n "class UsuarioManager" apps/api/app_rrhh/managers.py || echo "OK: removed from app_rrhh/managers.py"
grep -n "class UsuarioManager" apps/api/apps/identity/managers.py
```

Expected: A: `OK`. B: 1 match.

---

## Task 5: Mover modelos `usuario.py`, `roles.py`, `sistema.py` a `apps/identity/models/`

**Files:**
- Move: `apps/api/app_rrhh/models/usuario.py` → `apps/api/apps/identity/models/usuario.py`
- Move: `apps/api/app_rrhh/models/roles.py` → `apps/api/apps/identity/models/roles.py`
- Move: `apps/api/app_rrhh/models/sistema.py` → `apps/api/apps/identity/models/sistema.py`
- Modify: `apps/api/apps/identity/models/__init__.py` (re-exports)
- Modify: `apps/api/app_rrhh/models/__init__.py` (eliminar exports movidos)

- [ ] **Step 1: `git mv` los 3 archivos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/usuario.py apps/api/apps/identity/models/usuario.py
git mv apps/api/app_rrhh/models/roles.py apps/api/apps/identity/models/roles.py
git mv apps/api/app_rrhh/models/sistema.py apps/api/apps/identity/models/sistema.py
```

- [ ] **Step 2: Update `usuario.py` — FKs a Empleado deben ser lazy strings cross-app**

Read `apps/api/apps/identity/models/usuario.py`. Encuentra la línea `empleado = models.OneToOneField("Empleado", ...)`. Como `Empleado` queda en `app_rrhh` (hasta L3.4), debe referenciarse como string lazy con app_label:

Use Edit tool:
- old_string:
```python
    empleado = models.OneToOneField(
        "Empleado",
        on_delete=models.CASCADE,
        related_name="usuario",
        null=True,
        blank=True,
    )
```
- new_string:
```python
    empleado = models.OneToOneField(
        "app_rrhh.Empleado",
        on_delete=models.CASCADE,
        related_name="usuario",
        null=True,
        blank=True,
    )
```

También: el import `from ..managers import UsuarioManager` ahora debe ser `from ..managers import UsuarioManager` desde `apps.identity.models.usuario` apunta a `apps.identity.managers` (porque el `..` sube de `models/` a `identity/`). Eso es correcto. Verifica el import permaneció:

```bash
grep -n "UsuarioManager" apps/api/apps/identity/models/usuario.py
```

Expected: 1 import line + 1 usage line.

- [ ] **Step 3: Update `usuario.py` — el import `from .area import Area`**

Buscar:
```bash
grep -n "from .area\|from .empleado\|from .roles\|from .sistema" apps/api/apps/identity/models/usuario.py
```

Si encuentras `from .area import Area` (línea ~371 era cuando estaba en app_rrhh/models/), cambia a `from app_rrhh.models import Area` para reflejar que Area aún vive en app_rrhh:

Use Edit tool:
- old_string: `from .area import Area`
- new_string: `from app_rrhh.models import Area`

(Hasta L3.3, Area queda en app_rrhh.)

Similar para `from .roles import Rol` (es relative al mismo dir, queda OK ya que roles también se movió a identity):

```bash
grep -n "from .roles import\|from .sistema import" apps/api/apps/identity/models/usuario.py
```

Estas son intra-identity, ya están bien — no se modifican.

- [ ] **Step 4: Update `sistema.py` — FK refs**

Read `apps/api/apps/identity/models/sistema.py`. Las FKs que referencian Usuario/Rol/Permiso/Modulos son same-app, no cambian. Verifica:

```bash
grep -n "ForeignKey\|OneToOneField" apps/api/apps/identity/models/sistema.py | head -10
```

Si alguna FK referencia "Empleado" o algo de app_rrhh, conviértela a `"app_rrhh.X"`. Si todas son a Usuario/Rol/Permiso/Modulos/self → quedan igual.

- [ ] **Step 5: Update `apps/identity/models/__init__.py` con re-exports completos**

Use Write para reemplazar el placeholder con:

```python
"""Identity models — re-exports for backward-compatible imports."""

from .roles import Permiso, Rol
from .sistema import ModuloPermiso, Modulos, RolPermisos, UsuarioRoles
from .usuario import Usuario

__all__ = [
    "Modulos",
    "ModuloPermiso",
    "Permiso",
    "Rol",
    "RolPermisos",
    "Usuario",
    "UsuarioRoles",
]
```

- [ ] **Step 6: Update `app_rrhh/models/__init__.py` — eliminar exports movidos**

Read `apps/api/app_rrhh/models/__init__.py`. Las líneas a eliminar:
- `from .roles import Permiso, Rol`
- `from .sistema import ModuloPermiso, Modulos, RolPermisos, UsuarioRoles`
- `from .usuario import Usuario`
- En `__all__`, los strings: `"Permiso"`, `"Rol"`, `"ModuloPermiso"`, `"Modulos"`, `"RolPermisos"`, `"Usuario"`, `"UsuarioRoles"`

Use Edit tool con cada `old_string` específico para eliminar/reemplazar.

Verifica final:
```bash
grep -E "from .roles|from .sistema|from .usuario|\"Usuario\"|\"Rol\"|\"Permiso\"" apps/api/app_rrhh/models/__init__.py || echo "OK: removed from app_rrhh"
```

Expected: `OK: removed from app_rrhh`.

- [ ] **Step 7: Smoke check imports work**

```bash
cd D:/VYNTIA/apps/api
python -c "from apps.identity.models import Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso; print('OK')"
```

Expected: `OK`. Si falla, hay un import roto en uno de los 3 model files.

NOTE: `manage.py check` NO va a pasar todavía hasta que actualicemos AUTH_USER_MODEL en Task 8. Por eso usamos `python -c` para test mínimo.

---

## Task 6: Mover `auth.py` (CustomAuthBackend) a `apps/identity/`

**Files:**
- Move: `apps/api/app_rrhh/auth.py` → `apps/api/apps/identity/auth.py`

- [ ] **Step 1: `git mv` el archivo**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/auth.py apps/api/apps/identity/auth.py
```

- [ ] **Step 2: Update import en el archivo movido**

Read `apps/api/apps/identity/auth.py`. La primera línea del original era:
```python
from .models import Usuario
```

Como ahora vive en `apps/identity/`, el `.models` ahora apunta a `apps/identity/models/__init__.py` que exporta `Usuario`. **No hay que cambiar nada** — la import relative sigue siendo correcta.

Verifica:
```bash
cat apps/api/apps/identity/auth.py
```

Expected: import `from .models import Usuario`, class `CustomAuthBackend(ModelBackend)`. Sin modificaciones necesarias.

---

## Task 7: Bulk update imports `from app_rrhh.models import {Usuario|Rol|...}` → `from apps.identity.models import ...`

**Files:** ~15 archivos en `apps/api/`. Lista exacta sale del grep.

- [ ] **Step 1: Inventario pre-replace**

```bash
cd D:/VYNTIA/apps/api
grep -rln "from app_rrhh\.models import.*\(Usuario\|Rol\|Permiso\|UsuarioRoles\|RolPermisos\|Modulos\|ModuloPermiso\)\|from app_rrhh\.auth" --include="*.py" | sort
```

Expected output (aproximado):
```
api/v1/auth/serializers.py
api/v1/auth/views.py
api/v1/rrhh/filters.py
api/v1/rrhh/usuario_roles_serializers.py
api/v1/rrhh/usuario_roles_views.py
api/v1/rrhh/views.py
app_rrhh/management/commands/audit_rbac.py
app_rrhh/management/commands/seed_menu.py
app_rrhh/management/commands/setup_roles_permisos.py
apps/core/decorators.py
apps/core/middleware.py
apps/core/permissions.py
```

(El número exacto varía; >=10 esperado.)

- [ ] **Step 2: Bulk sed para imports `from app_rrhh.models import` que solo contienen identity-models**

Esto es delicado: `from app_rrhh.models import Empleado, Usuario, Area` mezcla identity y otras. La sed naïve no funciona. Necesitamos process file-by-file con AST-like cuidado.

**Approach pragmático**: para cada archivo del grep, agregar una nueva línea `from apps.identity.models import {names_de_identity}` y eliminar esos names de la línea original `from app_rrhh.models import`.

Vía sed con patrones específicos para imports puros de identity:

```bash
cd D:/VYNTIA/apps/api
# Patrón 1: imports que SOLO contienen identity models
find . -type f -name "*.py" -not -path "*/migrations/*" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's/^from app_rrhh\.models import \(Usuario\)$/from apps.identity.models import \1/g' \
  -e 's/^from app_rrhh\.models import \(Permiso\)$/from apps.identity.models import \1/g' \
  -e 's/^from app_rrhh\.models import \(Rol\)$/from apps.identity.models import \1/g'

# Patrón 2: from app_rrhh.auth import → from apps.identity.auth import
find . -type f -name "*.py" -not -path "*/__pycache__/*" -print0 | xargs -0 sed -i \
  -e 's/^from app_rrhh\.auth import/from apps.identity.auth import/g' \
  -e 's/^from app_rrhh\.auth\b/from apps.identity.auth/g'
```

Esto NO maneja imports mezclados (multi-line ni `from app_rrhh.models import Empleado, Usuario`). Esos requieren handling manual en Step 3.

- [ ] **Step 3: Manual fix para imports mezclados**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import" --include="*.py" | grep -E "Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso"
```

Para cada match, edit el archivo manualmente. El patrón:
- Si la línea es `from app_rrhh.models import A, B, Usuario, C` → split en dos:
  - `from app_rrhh.models import A, B, C`
  - `from apps.identity.models import Usuario`

Use Read + Edit por cada archivo. La lista completa esperada es ~5-8 archivos con imports mezclados.

- [ ] **Step 4: Manejar imports multi-línea (parens)**

Patrón típico:
```python
from app_rrhh.models import (
    Empleado,
    Usuario,
    Area,
    Rol,
)
```

Para cada match (visto en `views.py`, `filters.py`, etc.), refactor a:
```python
from app_rrhh.models import (
    Empleado,
    Area,
)
from apps.identity.models import (
    Rol,
    Usuario,
)
```

Use grep multi-line para encontrarlos:
```bash
cd D:/VYNTIA/apps/api
grep -rn -A 10 "from app_rrhh\.models import (" --include="*.py" | head -60
```

Edit cada uno con Edit tool.

- [ ] **Step 5: Update inline imports dentro de funciones**

Hay imports inline (dentro de método/función body) tipo:
```python
def some_method(self):
    from app_rrhh.models import UsuarioRoles
    ...
```

Buscarlos:
```bash
grep -rn "    from app_rrhh\.models import" --include="*.py" | grep -E "Usuario|Rol|Permiso"
```

Para cada match, replace `app_rrhh.models` con `apps.identity.models` (preserving identation).

- [ ] **Step 6: Update `apps/core/{decorators,middleware,permissions}.py` específicamente**

Estos files tienen `from app_rrhh.models import Usuario` (anti-pattern desde L3.1 — apps.core no debería depender de modelos de dominio, pero por ahora sí):

```bash
grep -n "from app_rrhh\.models" apps/api/apps/core/decorators.py apps/api/apps/core/middleware.py apps/api/apps/core/permissions.py
```

Replace cada uno a `from apps.identity.models import {Usuario|Rol|Permiso}`.

- [ ] **Step 7: Verificación final — cero imports de identity-models desde app_rrhh.models**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(Usuario\|Rol\|Permiso\|UsuarioRoles\|RolPermisos\|Modulos\|ModuloPermiso\)" --include="*.py" | head -10
```

Expected: vacío. Si aparece algo, edita manualmente.

```bash
grep -rn "from app_rrhh\.auth" --include="*.py" || echo "OK: app_rrhh.auth no se importa"
```

Expected: `OK`.

- [ ] **Step 8: Commit progreso (NO smoke test todavía — falta AUTH_USER_MODEL update)**

NO commit aquí — el sistema está roto (modelos están en identity pero AUTH_USER_MODEL aún apunta a app_rrhh.Usuario). Continuar a Task 8.

---

## Task 8: Update settings — AUTH_USER_MODEL, AUTHENTICATION_BACKENDS, INSTALLED_APPS

**Files:**
- Modify: `apps/api/vyntia/settings/base.py`

- [ ] **Step 1: AUTH_USER_MODEL**

Run:
```bash
grep -n "AUTH_USER_MODEL" apps/api/vyntia/settings/base.py
```

Expected: línea ~126: `AUTH_USER_MODEL = "app_rrhh.Usuario"`.

Use Edit tool:
- old_string: `AUTH_USER_MODEL = "app_rrhh.Usuario"`
- new_string: `AUTH_USER_MODEL = "identity.Usuario"`

(Notar: `identity` corresponde al `label` declarado en `IdentityConfig`. Django usa el label, no el name, para AUTH_USER_MODEL.)

- [ ] **Step 2: AUTHENTICATION_BACKENDS**

Run:
```bash
grep -A 4 "AUTHENTICATION_BACKENDS" apps/api/vyntia/settings/base.py
```

Expected:
```python
AUTHENTICATION_BACKENDS = [
    "app_rrhh.auth.CustomAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]
```

Use Edit tool:
- old_string: `"app_rrhh.auth.CustomAuthBackend"`
- new_string: `"apps.identity.auth.CustomAuthBackend"`

- [ ] **Step 3: LOCAL_APPS — registrar IdentityConfig**

Current state (after L3.1):
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "app_rrhh",
]
```

Use Edit tool:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "app_rrhh",
]
```
- new_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "app_rrhh",
]
```

- [ ] **Step 4: Verificar settings**

```bash
grep -n "AUTH_USER_MODEL\|AUTHENTICATION_BACKENDS\|LOCAL_APPS\|apps.identity" apps/api/vyntia/settings/base.py
```

Expected: AUTH_USER_MODEL apunta a `identity.Usuario`; LOCAL_APPS incluye `IdentityConfig`; AUTHENTICATION_BACKENDS apunta a `apps.identity.auth.CustomAuthBackend`.

---

## Task 9: Update `pyproject.toml` packages

**Files:**
- Modify: `apps/api/pyproject.toml`

- [ ] **Step 1: Update packages list**

Current (post-L3.1):
```toml
packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core"]
```

Use Edit tool:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity"]`

- [ ] **Step 2: Reinstall editable**

```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`. Si falla con `package directory 'apps.identity' does not exist`, verifica que `apps/api/apps/identity/__init__.py` existe.

---

## Task 10: NUCLEAR — drop bd_vyntia, eliminar app_rrhh/migrations, regenerar

**Files:**
- Delete: `apps/api/app_rrhh/migrations/0001_initial.py` through `0027_move_contratos_under_empleados.py` (27 archivos)
- Keep: `apps/api/app_rrhh/migrations/__init__.py`
- Auto-create: `apps/api/app_rrhh/migrations/0001_initial.py` (nueva, sin Usuario/Rol/Permiso/etc.)
- Auto-create: `apps/api/apps/identity/migrations/0001_initial.py` (nueva, con todos los identity models)

**ATENCIÓN:** Esta task es destructiva. El backup `pg_dump` de Task 1 Step 4 es la red de seguridad.

- [ ] **Step 1: Drop bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "DROP DATABASE IF EXISTS bd_vyntia;" 2>&1
```

Expected: `DROP DATABASE`. Si falla con "database is being accessed by other users", mata cualquier conexión:

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force
```

Y reintenta.

- [ ] **Step 2: Eliminar `app_rrhh/migrations/00*.py`**

```bash
cd D:/VYNTIA/apps/api/app_rrhh/migrations
ls 00*.py | wc -l
echo "Files to delete (expected 27):"
git rm 00*.py 2>&1 | tail -3
ls
```

Expected: solo `__init__.py` y `__pycache__/` quedan.

- [ ] **Step 3: Generar fresh migrations**

```bash
cd D:/VYNTIA/apps/api
python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -20
cd ../..
```

Expected: 
- `Migrations for 'app_rrhh':` con `0001_initial.py` listando ~15-20 modelos (Empleado, Area, Contratos, etc., SIN Usuario/Rol/Permiso)
- `Migrations for 'identity':` con `0001_initial.py` listando los 7 identity models (Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso)

Si Django se queja de circular dependencies entre app_rrhh ↔ identity, los strings lazy `"app_rrhh.Empleado"` y `"identity.Usuario"` deben resolverlas. Si falla, revisa los FKs.

- [ ] **Step 4: Verificar migration files generados**

```bash
ls apps/api/app_rrhh/migrations/
ls apps/api/apps/identity/migrations/
```

Expected:
- `app_rrhh/migrations/`: `__init__.py`, `0001_initial.py`
- `apps/identity/migrations/`: `__init__.py`, `0001_initial.py`

- [ ] **Step 5: Inspect migration content (sanity check)**

```bash
grep -E "name='(Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso)'" apps/api/apps/identity/migrations/0001_initial.py | head -10
echo "---"
grep -E "name='(Usuario|Rol|Permiso|UsuarioRoles|RolPermisos|Modulos|ModuloPermiso)'" apps/api/app_rrhh/migrations/0001_initial.py | head -10
```

Expected:
- Section 1 (identity): 7 matches (Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso)
- Section 2 (app_rrhh): empty (these models are NOT in app_rrhh anymore)

Si app_rrhh aún tiene Usuario/Rol/etc., algún `__init__.py` no se actualizó — vuelve a Task 5 Step 6.

- [ ] **Step 6: Recrear bd_vyntia**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d postgres -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

Expected: `CREATE DATABASE`.

- [ ] **Step 7: Aplicar migrations**

```bash
cd D:/VYNTIA/apps/api
python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -20
cd ../..
```

Expected: secuencia de `Applying X.0001_initial... OK` para todas las apps (auth, contenttypes, sessions, identity, app_rrhh, etc.). Sin errors.

Si error de FK ordering (`identity.0001_initial` quiere referenciar `app_rrhh.Empleado` antes de que exista), Django debería resolver automáticamente via dependencies declarations. Si falla, revisa que `0001_initial.py` de identity tenga `dependencies = [..., ('app_rrhh', '0001_initial'), ...]`.

- [ ] **Step 8: Verificar schema**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "\dt" 2>&1 | tail -50
```

Expected: ~46 tabletas (auth_*, django_*, usuarios, rol, permiso, rol_permisos, usuario_roles, modulos, modulo_permisos, empleado, area, etc.). Igual que pre-L3.2 menos las 6 modulos de seed (que ya no se aplican porque eliminamos las migraciones data).

---

## Task 11: Re-seed datos default

**Files:** ninguno (DB-only changes)

- [ ] **Step 1: Run setup_roles_permisos**

```bash
cd D:/VYNTIA/apps/api
python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -20
cd ../..
```

Expected: comando ejecuta sin errors. Output aproximado: "Creando rol Super Administrador...", "Creando permiso..." etc. Algunos roles/permisos creados.

Si comando falla con `ImportError: cannot import name 'Usuario' from 'app_rrhh.models'`, el comando `setup_roles_permisos.py` aún no fue actualizado en Task 7 — vuelve a actualizar imports.

- [ ] **Step 2: Run seed_menu para los 6 modulos**

```bash
cd D:/VYNTIA/apps/api
python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Expected: comando ejecuta. Crea modulos default. Output específico depende de implementación del comando.

- [ ] **Step 3: Verificar seed**

```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT COUNT(*) AS rol FROM rol; SELECT COUNT(*) AS permiso FROM permiso; SELECT COUNT(*) AS modulos FROM modulos;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0. Counts exactos dependen de los management commands.

---

## Task 12: Smoke tests

**Files:** ninguno

- [ ] **Step 1: `manage.py check`**

```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

Si falla con `models.E022 (auth.User.X clashes with...)` o similar AUTH_USER_MODEL warnings, revisa AUTH_USER_MODEL en settings — debe ser `"identity.Usuario"`.

- [ ] **Step 2: pytest baseline**

```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`. Baseline preservado.

Si los counts difieren significativamente (ej. >50 failed), el AUTH_USER_MODEL change rompió fixtures o tests. Investiga:

```bash
cd D:/VYNTIA/apps/api
pytest --tb=short -x 2>&1 | tail -30
```

Identifica el primer fallo NUEVO. Si es `LookupError: No installed app with label 'app_rrhh'.` o `cannot import name 'Usuario' from 'app_rrhh.models'`, hay un test que aún tiene el viejo path — actualiza.

- [ ] **Step 3: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l32.log 2>&1 &
SERVER_PID=$!
sleep 8
curl -s -o /dev/null -w "HTTP %{http_code} /api/docs/\n" http://127.0.0.1:8000/api/docs/
curl -s -o /dev/null -w "HTTP %{http_code} /api/schema/\n" http://127.0.0.1:8000/api/schema/
kill $SERVER_PID 2>/dev/null
sleep 1
cd ../..
```

Expected: ambos retornan 200. Si falla, lee `/tmp/runserver_l32.log`.

Mata cualquier proceso residual:
```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force
```

- [ ] **Step 4: Verificar imports finales**

```bash
echo "=== A: app_rrhh import de identity models ==="
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(Usuario\|Rol\|Permiso\|UsuarioRoles\|RolPermisos\|Modulos\|ModuloPermiso\)" --include="*.py" || echo "OK: cero matches"
echo ""
echo "=== B: app_rrhh.auth imports ==="
grep -rn "from app_rrhh\.auth\|import app_rrhh.auth" --include="*.py" || echo "OK: cero matches"
echo ""
echo "=== C: AUTH_USER_MODEL ==="
grep -n "AUTH_USER_MODEL" vyntia/settings/base.py
cd ../..
```

Expected: A: `OK`. B: `OK`. C: `AUTH_USER_MODEL = "identity.Usuario"`.

---

## Task 13: Final commit + git history check

**Files:** ninguno (commit acumulativo de Tasks 3-12)

- [ ] **Step 1: Review git status**

```bash
cd D:/VYNTIA
git status --short | head -30
```

Expected (orden aproximado):
- New: `apps/api/apps/identity/__init__.py`
- New: `apps/api/apps/identity/apps.py`
- New: `apps/api/apps/identity/managers.py`
- New: `apps/api/apps/identity/auth.py`  (rename from app_rrhh/auth.py)
- New: `apps/api/apps/identity/models/__init__.py`
- New: `apps/api/apps/identity/models/usuario.py` (rename)
- New: `apps/api/apps/identity/models/roles.py` (rename)
- New: `apps/api/apps/identity/models/sistema.py` (rename)
- New: `apps/api/apps/identity/migrations/__init__.py`
- New: `apps/api/apps/identity/migrations/0001_initial.py`
- New: `apps/api/app_rrhh/migrations/0001_initial.py`
- Deleted: 27× `apps/api/app_rrhh/migrations/00*.py`
- Modified: `apps/api/app_rrhh/models/__init__.py`
- Modified: `apps/api/app_rrhh/managers.py`
- Modified: `apps/api/vyntia/settings/base.py`
- Modified: `apps/api/pyproject.toml`
- Modified: ~12 archivos en `api/v1/`, `apps/core/`, `app_rrhh/management/commands/`, `app_rrhh/filters.py`

- [ ] **Step 2: Stage all + commit**

```bash
git add apps/api/
git commit -m "chore(L3.2): extract identity app (Usuario, Rol, Permiso, RBAC) — AUTH_USER_MODEL=identity.Usuario, fresh migrations after BD nuke + reseed"
```

Expected: ~30+ files changed.

- [ ] **Step 3: Verificar git history y tree**

```bash
git log --oneline vyntia/L3.2-identity-app ^master | head -5
git status --short
```

Expected:
- 2 commits: `docs(L3.2): add identity app extraction plan` + `chore(L3.2): extract identity app ...`
- `git status` vacío

---

## Task 14: Merge a master

**Files:** ninguno

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta: ¿Mergear `vyntia/L3.2-identity-app` a master con `--no-ff` (consistente con L0/L1/L2/L3.1)?

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.2-identity-app -m "Merge L3.2: extract identity app (Usuario, Rol, Permiso, RBAC) with AUTH_USER_MODEL change"
git log --oneline -5
```

Expected: merge commit visible.

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

- [ ] `apps/api/apps/identity/{__init__.py, apps.py, auth.py, managers.py, models/__init__.py, models/usuario.py, models/roles.py, models/sistema.py, migrations/__init__.py, migrations/0001_initial.py}` existen
- [ ] `app_rrhh/models/{usuario,roles,sistema}.py` removidos
- [ ] `app_rrhh/auth.py` removido
- [ ] `app_rrhh/migrations/00XX_*` (27 archivos) removidos; nuevo `0001_initial.py` regenerado SIN Usuario/Rol/Permiso
- [ ] `apps/identity/migrations/0001_initial.py` contiene Usuario, Rol, Permiso, UsuarioRoles, RolPermisos, Modulos, ModuloPermiso
- [ ] `vyntia/settings/base.py`: `AUTH_USER_MODEL = "identity.Usuario"`, `AUTHENTICATION_BACKENDS` apunta a `apps.identity.auth.CustomAuthBackend`, `LOCAL_APPS` incluye `IdentityConfig`
- [ ] `pyproject.toml` `packages` incluye `"apps.identity"`
- [ ] Cero `from app_rrhh.models import {identity-models}` o `from app_rrhh.auth` en código activo
- [ ] `bd_vyntia` recreada con esquema fresco; counts: usuarios=0 (default), rol>0, permiso>0, modulos>0
- [ ] `manage.py check` clean
- [ ] `pytest`: 125 passed / 44 failed / 3 skipped
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.2-identity-app` con commits `docs(L3.2)` + `chore(L3.2)` mergeada a master con `--no-ff`
- [ ] Memoria del proyecto actualizada post-merge: `active_subproject.md` con L3.2 ✅, L3.3 NEXT
- [ ] Roadmap master actualizado: L3.2 → ✅ con merge SHA

---

## Después de L3.2

**Próximo plan:** L3.3 — extract `organization` app (Area, Ubicacion, ConfiguracionEmpresa, Sistema/Modulos).

Lecciones aprendidas de L3.2 que aplicar a L3.3-L3.9:
- El patrón `git mv models + update __init__ exports + update imports + regenerate migrations` está validado
- La estrategia NUCLEAR (drop+regenerate) es más simple que SeparateDatabaseAndState para sub-PRs siguientes
- Cada sub-PR siguiente tendrá MÁS fresh migrations (porque L3.2 dejó sólo 1 migration por app, fácil de regenerar)
- Los management commands se actualizan junto con cada sub-PR — están en `app_rrhh/management/commands/` por ahora, se mueven en L3.11

---

## Notas para el ejecutor

- **`bd_vyntia` se DROPEA** en Task 10. El backup `pg_dump` de Task 1 Step 4 es la red de seguridad — restorable con `pg_restore`.
- **Migraciones se regeneran completas** porque la nuclear strategy es más simple que SeparateDatabaseAndState. Documentar en commit message que esto fue intencional.
- **Class names quedan en español** (Usuario, Rol, Permiso, etc.). Inglés viene en L3.10. NO renombrar campos ni clases en L3.2.
- **`apps/identity/auth.py` import `from .models import Usuario`** queda sin cambio — `.models` es el `apps/identity/models/__init__.py` que re-exporta Usuario.
- **El label de la app es `identity`** (no `apps.identity`). Por eso `AUTH_USER_MODEL = "identity.Usuario"` en lugar de `"apps.identity.Usuario"`.
- **Stale Python procs:** Si `psql` falla con "database is being accessed", mata todos los procesos Python con PowerShell antes de retry.
- **Windows Git Bash**: `psql.exe` requiere ruta absoluta `/c/Program Files/PostgreSQL/15/bin/psql.exe`.
- **Tests fallidos (44 baseline) ya tienen Usuario references** — esos quedan como está, son pre-existing failures que no se intentan arreglar en Foundation.
