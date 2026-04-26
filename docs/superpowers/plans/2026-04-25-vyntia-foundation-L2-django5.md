# VYNTIA Foundation L2 — Django 4.2 → 5.2 Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Subir el backend de Django 4.2.30 a Django 5.2 LTS, ajustar la deprecación de `STATICFILES_STORAGE`/`DEFAULT_FILE_STORAGE` (reemplazadas por `STORAGES` en 5.x), validar que tests + `manage.py check --deploy` queden limpios, sin tocar modelos ni estructura de apps (eso es L3).

**Architecture:** Upgrade en sitio. El único cambio de configuración semántico es migrar 4 archivos de settings de los settings legacy `STATICFILES_STORAGE` / `DEFAULT_FILE_STORAGE` al nuevo dict `STORAGES`. Todas las dependencias terceras instaladas (DRF 3.17.1, simplejwt 5.5.1, drf-spectacular 0.29.0, django-cors-headers 4.9.0, django-filter 25.1, django-extensions 4.1, django-redis 6.0.0, django-storages 1.14.6, celery 5.6.3, factory-boy 3.3.3) ya soportan Django 5.x — no requieren bumps coordinados.

**Tech Stack:** Django 5.2 (LTS hasta abril 2028), pip + pyproject.toml, pytest, PostgreSQL.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L2 — Upgrade Django 4.2 → Django 5"

> **Nota sobre versión target:** El spec dice `Django>=5.0,<5.1`. Como 5.2 LTS está disponible y todas las dependencias del proyecto ya la soportan, este plan apunta directamente a 5.2 LTS para evitar un segundo upgrade en 6 meses cuando 5.0 EOL. La constraint final es `Django>=5.2,<5.3`.

**Pre-condiciones:**
- L1 mergeado a master: commit `49e7248e Merge L1: rebrand superficial`. Verifica con `git log --oneline -2`.
- venv en `D:/VYNTIA/.venv/` con Python 3.11.x. Activación: `source D:/VYNTIA/.venv/Scripts/activate`.
- BD `bd_vyntia` provisionada con esquema migrado (Task L1.8 entregó esto).
- `apps/api/.env` local con `DB_NAME=bd_vyntia` y `DB_PASSWORD` ASCII-pure.
- Postgres 15+ corriendo en `localhost:5432`.

**Definition of Done global:**
- [ ] `python -c "import django; print(django.get_version())"` retorna `5.2.x`
- [ ] `python manage.py check --settings=vyntia.settings.development` retorna `System check identified no issues`
- [ ] `python manage.py check --deploy --settings=vyntia.settings.production` retorna sin warnings RemovedInDjango60Warning ni equivalentes
- [ ] `pytest` retorna **125 passed, 44 failed, 3 skipped** (baseline preservado)
- [ ] `python manage.py runserver` arranca y responde HTTP 200/302 en `http://127.0.0.1:8000/api/docs/`
- [ ] No queda ninguna referencia a `STATICFILES_STORAGE` ni `DEFAULT_FILE_STORAGE` en `apps/api/vyntia/settings/*.py`; ahora se usa `STORAGES = {...}`
- [ ] Branch `vyntia/L2-django5-upgrade` con commits `chore(L2):` (uno por task que commitea) mergeada a master con `--no-ff`
- [ ] `git status` limpio al final
- [ ] Memoria del proyecto actualizada: `tech_stack.md` con Django 5.2

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Modify | `apps/api/pyproject.toml` | `Django>=4.2.0,<5.0.0` → `Django>=5.2,<5.3`; bump `django-filter`/`setuptools` constraints si es necesario |
| Modify | `apps/api/vyntia/settings/production.py` | Reemplazar `STATICFILES_STORAGE` + `DEFAULT_FILE_STORAGE` por dict `STORAGES` |
| Modify | `apps/api/vyntia/settings/testing.py` | Reemplazar `STATICFILES_STORAGE` por `STORAGES` |
| Modify | `apps/api/vyntia/settings/testing_new.py` | Reemplazar `STATICFILES_STORAGE` por `STORAGES` |
| Modify (cond) | `apps/api/vyntia/settings/base.py` | Si surgen warnings de deprecación, agregar `STORAGES` por defecto aquí |
| Modify | `D:/VYNTIA/CLAUDE.md` | "Django 4.2 + DRF backend" → "Django 5.2 + DRF backend"; quitar nota L2 ⏳, marcar ✅ |

**NO se tocan en L2:** ningún `.py` con lógica de modelos, views, services, serializers. La regla "L2 no toca estructura de apps ni modelos" es del spec — los warnings de `null=True` en CharField/TextField (pre-existentes, ~50+ matches en `app_rrhh/models/`) se dejan para L3 cuando se renombren modelos.

---

## Task 1: Pre-flight — branch, baseline, venv

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Confirmar pwd, master limpio, baseline L1 mergeada**

Run desde la raíz:
```bash
pwd
git status --short
git log --oneline -3
```

Expected:
- `pwd`: `/d/VYNTIA`
- `git status`: vacío
- `git log`: HEAD = `49e7248e Merge L1: rebrand superficial (...)` o más reciente

Si `git status` no está limpio, **detente** y commitea/stashea antes de seguir.

- [ ] **Step 2: Activar venv y confirmar Django 4.2 (baseline pre-L2)**

Run:
```bash
source .venv/Scripts/activate
python -c "import django; print(django.get_version())"
```

Expected: `4.2.30` (o un 4.2.x). Esto confirma el punto de partida.

- [ ] **Step 3: Confirmar baseline pytest pre-L2**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected literal: `125 passed, 44 failed, 3 skipped` (puede mostrar `1 warning` también).

Si los counts difieren, **detente** y consulta — el plan asume estos exactos counts.

- [ ] **Step 4: Crear branch L2**

Run:
```bash
git checkout -b vyntia/L2-django5-upgrade
git status
```

Expected: `On branch vyntia/L2-django5-upgrade`, working tree limpio.

---

## Task 2: Auditar dependencias y bump Django a 5.2 en pyproject.toml

**Files:**
- Modify: `apps/api/pyproject.toml`

**Por qué:** El spec L2 manda `Django>=5.0,<5.1`. Como 5.2 LTS está disponible (estable hasta abril 2028) y todas las deps actuales lo soportan, apuntamos directo a la LTS para no hacer un segundo upgrade en 6 meses.

- [ ] **Step 1: Snapshot del paquete-grafo actual**

Run desde la raíz:
```bash
pip list --outdated 2>&1 | head -10
echo "---"
pip show django 2>&1 | grep -E "^Name|^Version|^Requires" | head -5
```

Expected: `Django 4.2.30 → 5.2.x` aparece en outdated. Anota esto en la PR/commit message si lo deseas.

- [ ] **Step 2: Bump constraint Django en `apps/api/pyproject.toml`**

Edita `apps/api/pyproject.toml` línea 18:

- old_string: `    "Django>=4.2.0,<5.0.0",`
- new_string: `    "Django>=5.2,<5.3",`

- [ ] **Step 3: Reinstalar paquete editable forzando upgrade de Django**

Run:
```bash
cd apps/api
pip install -e ".[dev]" --upgrade 2>&1 | tail -15
cd ../..
```

Expected: pip resuelve `Django>=5.2,<5.3`, descarga 5.2.x, lo instala. Mensajes esperados: `Successfully installed Django-5.2.X` (junto con cualquier dep transitiva que pip decida actualizar). Warnings de paquetes terceros sobre Django <5 son OK.

- [ ] **Step 4: Verificar que la versión activa es 5.2.x**

Run:
```bash
python -c "import django; print(django.get_version())"
```

Expected: `5.2.x` (ej. `5.2.13`). Si sigue mostrando 4.2, el upgrade no tomó — investiga `pip install` output del Step 3.

- [ ] **Step 5: Commit del cambio en pyproject + lockfile cambios**

Run:
```bash
git status --short
```

Esperarás ver `M apps/api/pyproject.toml`. Si Python instaló `Django.dist-info` dentro de `.venv/`, eso queda fuera de git (gitignored). Sin cambios en el repo más allá de pyproject.

```bash
git add apps/api/pyproject.toml
git commit -m "chore(L2): bump Django constraint to >=5.2,<5.3 (LTS)"
```

---

## Task 3: Diagnóstico inicial — `manage.py check` + pytest sobre Django 5.2

**Files:** ninguno (solo verificación; cualquier fix vive en tasks posteriores)

**Por qué:** Antes de tocar settings, queremos ver QUÉ rompe. Las dos categorías esperadas:
- **Errores duros**: el código no arranca (poco probable porque las deps son compatibles).
- **Warnings de deprecación**: `STATICFILES_STORAGE` y `DEFAULT_FILE_STORAGE` (sí los tenemos). Eso es Task 4.

- [ ] **Step 1: `manage.py check` con warnings explícitos**

Run:
```bash
cd apps/api
python -W default::DeprecationWarning -W default::PendingDeprecationWarning manage.py check --settings=vyntia.settings.development 2>&1 | tail -30
cd ../..
```

Expected: `System check identified no issues (0 silenced).` + posiblemente warnings de `RemovedInDjango60Warning` o `STATICFILES_STORAGE/DEFAULT_FILE_STORAGE`.

**Si aparecen warnings:** anótalos. Lo más probable que veas:
- `RemovedInDjango60Warning: The 'STATICFILES_STORAGE' setting is deprecated. Use 'STORAGES' instead.`
- `RemovedInDjango60Warning: The 'DEFAULT_FILE_STORAGE' setting is deprecated. Use 'STORAGES' instead.`

Esos los resuelve Task 4. Otros warnings inesperados → reporta al controller.

**Si aparecen errores** (no warnings, errores hard): detente y diagnostica. Lo más probable es un import roto en una dep terceira que aún no soporta 5.2. Verifica versions con `pip show <pkg>`.

- [ ] **Step 2: Pytest baseline en Django 5.2**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: **125 passed, 44 failed, 3 skipped**. Si aumentan los failed, Django 5.2 introdujo regresiones — investiga inmediatamente:

```bash
cd apps/api
pytest --tb=short --no-header -q -x 2>&1 | tail -50
```

El `-x` para en el primer fallo nuevo. Si el fallo es por una API removida en Django 5 (ej. `make_random_password`, `timezone.utc`), ese es scope del L2 — fix en task posterior. Si es algo no relacionado a Django, posiblemente es una dependencia de cache que cambió — reporta.

**Si el baseline sigue siendo 125/44/3:** perfecto, sigue al Step 3.

- [ ] **Step 3: Documentar findings (no commit)**

Anota en una nota mental (o en la PR description al merge) los warnings que vio el Step 1. Esos son el input para Task 4.

---

## Task 4: Migrar `STATICFILES_STORAGE`/`DEFAULT_FILE_STORAGE` al setting `STORAGES`

**Files:**
- Modify: `apps/api/vyntia/settings/production.py`
- Modify: `apps/api/vyntia/settings/testing.py`
- Modify: `apps/api/vyntia/settings/testing_new.py`

**Por qué:** En Django 4.2 estos settings ya estaban en deprecación; en Django 5 disparan `RemovedInDjango60Warning`. El reemplazo correcto es el dict `STORAGES`. La forma del dict cubre ambos `default` (file storage) y `staticfiles` en una sola estructura.

**Equivalencias:**

```python
# Old (Django 4.2 style)
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"  # implicit default

# New (Django 5+ style)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

Para `production.py` que usa S3 como `DEFAULT_FILE_STORAGE` cuando hay credenciales AWS:

```python
# Conditional STORAGES with S3 fallback (production)
if AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
```

- [ ] **Step 1: Leer `apps/api/vyntia/settings/production.py` para ubicar las líneas exactas**

Run:
```bash
grep -n "STATICFILES_STORAGE\|DEFAULT_FILE_STORAGE\|AWS_STORAGE_BUCKET_NAME" apps/api/vyntia/settings/production.py | head -15
```

Expected output (líneas aprox):
- línea ~67: `STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'`
- línea ~75: `DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'`
- También debería haber un bloque `if AWS_STORAGE_BUCKET_NAME:` previo (Step 2 inspecciona).

- [ ] **Step 2: Leer el bloque completo (líneas 60-80) de production.py**

Use Read tool con offset=60, limit=25 sobre `apps/api/vyntia/settings/production.py`. Esto te da contexto exacto del bloque a editar.

- [ ] **Step 3: Reemplazar el bloque en `production.py`**

El reemplazo depende de la estructura exacta del archivo actual. Asumiendo que tiene algo como:

```python
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# AWS S3 Configuration for production
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
...

if AWS_STORAGE_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

(Si la estructura difiere, adapta el patch al archivo real.)

Reemplaza el bloque que contiene `STATICFILES_STORAGE = ...` y el bloque `if AWS_STORAGE_BUCKET_NAME: DEFAULT_FILE_STORAGE = ...` por:

```python
# Storage backends (Django 5+ uses STORAGES dict)
if os.environ.get('AWS_STORAGE_BUCKET_NAME') and os.environ.get('AWS_ACCESS_KEY_ID'):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
```

Asegúrate de que cualquier `AWS_STORAGE_BUCKET_NAME = os.environ.get(...)` que estuviera arriba del bloque condicional siga existiendo (el bloque conditional referenciaba `AWS_STORAGE_BUCKET_NAME` directo; si la nueva versión usa `os.environ.get(...)` inline no necesita la variable módulo, pero mantenla si hay otros consumers en el archivo).

Verifica:
```bash
grep -n "STATICFILES_STORAGE\|DEFAULT_FILE_STORAGE\|STORAGES" apps/api/vyntia/settings/production.py
```

Expected: solo coincidencias con `STORAGES = {` (ningún `STATICFILES_STORAGE = ` ni `DEFAULT_FILE_STORAGE = `).

- [ ] **Step 4: Migrar `testing.py`**

Run:
```bash
grep -n "STATICFILES_STORAGE" apps/api/vyntia/settings/testing.py
```

Expected: una línea (≈70) con `STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'`.

Edit `apps/api/vyntia/settings/testing.py`:

- old_string:
```python
# Configuración de archivos estáticos para pruebas
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

- new_string:
```python
# Configuración de archivos estáticos para pruebas (Django 5+ STORAGES)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

(Si el comentario inmediatamente arriba difiere, ajusta el `old_string` al texto real.)

- [ ] **Step 5: Migrar `testing_new.py`**

Análogo al anterior. Run:
```bash
grep -n "STATICFILES_STORAGE" apps/api/vyntia/settings/testing_new.py
```

Edit `apps/api/vyntia/settings/testing_new.py` reemplazando la línea de `STATICFILES_STORAGE` por el bloque `STORAGES = {...}` mostrado en Step 4.

- [ ] **Step 6: Verificación global**

Run:
```bash
grep -rn "STATICFILES_STORAGE\|DEFAULT_FILE_STORAGE" apps/api/vyntia/settings/ --include="*.py" || echo "OK: cero matches"
```

Expected: `OK: cero matches`.

- [ ] **Step 7: Smoke test post-migración**

Run:
```bash
cd apps/api
python -W default::DeprecationWarning manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected:
- check: `System check identified no issues (0 silenced).` sin warnings sobre `STATICFILES_STORAGE` ni `DEFAULT_FILE_STORAGE`
- pytest: `125 passed, 44 failed, 3 skipped`

Si hay warnings residuales sobre storages, alguna línea quedó sin migrar — investiga.

- [ ] **Step 8: Commit**

Run:
```bash
git add apps/api/vyntia/settings/production.py apps/api/vyntia/settings/testing.py apps/api/vyntia/settings/testing_new.py
git commit -m "chore(L2): migrate STATICFILES_STORAGE/DEFAULT_FILE_STORAGE to Django 5 STORAGES dict"
```

---

## Task 5: Aplicar migraciones de Django 5 (si Django agregó nuevas migraciones built-in)

**Files:** ninguno (cambios en Postgres, no en el repo)

**Por qué:** Entre versiones de Django, las apps built-in (auth, contenttypes, sessions) a veces agregan migraciones (ej. agregar fields a `auth_user`). Hay que aplicarlas a `bd_vyntia` para que el esquema esté al día con Django 5.

- [ ] **Step 1: Ver migraciones pendientes**

Run:
```bash
cd apps/api
python manage.py showmigrations --settings=vyntia.settings.development 2>&1 | grep -E "\[ \]" | head -10
cd ../..
```

Expected: o salida vacía (no hay migraciones pendientes), o una lista corta de migraciones built-in nuevas (ej. `auth.0013_alter_*`, `admin.0004_*`). Las custom de `app_rrhh` no deberían aparecer porque no las modificamos.

- [ ] **Step 2: Aplicar migraciones (si las hay)**

Run:
```bash
cd apps/api
python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -15
cd ../..
```

Expected: o `No migrations to apply.`, o una lista corta de `Applying X.Y... OK` para migraciones built-in.

Si Django manda una migración a `app_rrhh` (que NO debería ocurrir porque no tocamos modelos), **detente** — eso indica que el upgrade detectó algo a regenerar. Investiga con:
```bash
python manage.py makemigrations --dry-run --settings=vyntia.settings.development
```

Si reporta cambios en `app_rrhh`, son scope L3 (modelos). En ese caso, NO crees la migración — déjala para L3.

- [ ] **Step 3: Verificación final**

Run:
```bash
cd apps/api
python manage.py showmigrations --settings=vyntia.settings.development 2>&1 | grep -E "\[ \]" | head -5 || echo "OK: todas las migraciones aplicadas"
cd ../..
```

Expected: `OK: todas las migraciones aplicadas`.

- [ ] **Step 4: NO commit (Postgres-only change)**

Esta task no toca el repo. Si hubo `makemigrations` autogenerado por error, descártalo con `git checkout -- apps/api/` y diagnostica.

---

## Task 6: `manage.py check --deploy` y limpieza de warnings finales

**Files:** posiblemente `apps/api/vyntia/settings/production.py`, dependiendo de los warnings

**Por qué:** El DoD del spec dice "App arranca sin warnings de deprecación". `--deploy` activa una capa adicional de checks que pueden surface temas de seguridad y deprecaciones. Aceptamos los relacionados a infra (HTTPS, HSTS) — esos son scope deployment, no L2. Resolvemos los relacionados a deprecaciones código.

- [ ] **Step 1: Ejecutar `--deploy` contra production settings**

Run:
```bash
cd apps/api
python manage.py check --deploy --settings=vyntia.settings.production 2>&1 | tail -30
cd ../..
```

Esperarás warnings tipo `W004 SECURE_HSTS_SECONDS not set` o `W018 DEBUG=True`. Esos son **infra warnings** y se aceptan en L2 (no son deprecaciones).

**Lo que NO se acepta**: cualquier `RemovedInDjango60Warning` o `RemovedInDjango61Warning` sobre código de la app. Si aparece uno, identifica el archivo culpable y arréglalo.

Si todo lo que vez son `W004`, `W008`, `W009`, `W018`, `W020`, `W021` (security infra), **es OK** — anótalos en el commit message como "infra-only, deferred to deploy phase" y avanza.

- [ ] **Step 2 (condicional): Si aparecen warnings de deprecación de código**

Identifica el archivo con `python -W error::DeprecationWarning manage.py check --settings=vyntia.settings.development 2>&1 | head -30` (esto convierte el primer warning en error y muestra el traceback con la línea exacta).

Repara según corresponda. Patrones comunes:
- `force_text` → `force_str` (ya estamos usando `force_str`, debería estar OK)
- `ugettext` → `gettext`
- `re_path` con regex obsoleto → `path` o `re_path` modernizado
- `null=True` en CharField/TextField → **NO TOCAR**, son scope L3 (rename de modelos)

Si encontraste deprecaciones de código y las arreglaste, vuelve al Step 1 hasta que `--deploy` solo muestre infra warnings.

- [ ] **Step 3: Re-verificar `--deploy` con development settings**

Run:
```bash
cd apps/api
python manage.py check --deploy --settings=vyntia.settings.development 2>&1 | tail -15
cd ../..
```

Expected: `System check identified N issues (0 silenced)` donde N son solo infra warnings (DEBUG=True etc.). El `0 silenced` es lo importante.

- [ ] **Step 4: Pytest sigue verde**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

- [ ] **Step 5: Commit (si hubo cambios en Step 2)**

Si Step 2 modificó archivos:
```bash
git add apps/api/
git commit -m "chore(L2): fix Django 5 deprecation warnings in code"
```

Si no hubo cambios, salta el commit. Reporta en el next-task handoff que Step 2 no requirió fixes.

---

## Task 7: Smoke test `runserver` con bd_vyntia

**Files:** ninguno (solo verificación)

**Por qué:** L1 documentaba un known issue con `runserver` (UnicodeDecodeError en psycopg2). En L1 el `.env` se reconfiguró con password ASCII y se creó `bd_vyntia` — `runserver` debería arrancar sin problemas ahora. Este task es la verificación de que toda la cadena Django 5 + bd_vyntia + .env está sana.

- [ ] **Step 1: Arrancar runserver en background**

Run:
```bash
cd apps/api
python manage.py runserver --settings=vyntia.settings.development 2>&1 > /tmp/runserver.log &
SERVER_PID=$!
sleep 6
cd ../..
```

(Si `/tmp/` no funciona en Windows Git Bash, usa `/d/VYNTIA/runserver.log` y limpia después.)

- [ ] **Step 2: Verificar que arrancó sin errores**

Run:
```bash
head -20 /tmp/runserver.log
```

Expected: `Starting development server at http://127.0.0.1:8000/` aparece. NO debe haber `UnicodeDecodeError`, `OperationalError`, `ImportError`.

Si aparece error, mata el server (`kill $SERVER_PID`) y diagnostica. Lo más probable:
- `OperationalError: database "bd_vyntia" does not exist` → la BD no se creó (revisita L1 Task 8)
- `psycopg2.OperationalError: password authentication failed` → `.env` tiene password incorrecto
- `UnicodeDecodeError` → `.env` con caracter no-ASCII

- [ ] **Step 3: Hacer un GET a `/api/docs/`**

Run:
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/api/docs/
```

Expected: `HTTP 200` o `HTTP 301`/`HTTP 302`. Si retorna `HTTP 000` (curl falla), el server no está respondiendo — revisa el log.

- [ ] **Step 4: Hacer un GET a `/api/schema/` (drf-spectacular)**

Run:
```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8000/api/schema/
```

Expected: `HTTP 200`. Si falla, drf-spectacular tuvo un problema con Django 5 — investiga.

- [ ] **Step 5: Matar el server y limpiar logs**

Run:
```bash
kill $SERVER_PID 2>/dev/null
sleep 1
ps -W 2>/dev/null | grep python | grep -v grep || echo "OK: no python procs"
rm -f /tmp/runserver.log
```

Expected: `OK: no python procs`. Asegurarte que mataste todos los runservers para no bloquear futuras tasks (L0 tuvo problemas con stale processes).

- [ ] **Step 6: NO commit (verificación pura)**

Esta task documenta que el upgrade es funcional end-to-end. Si todo pasó, marca el checkbox y avanza.

---

## Task 8: Actualizar CLAUDE.md y memoria del proyecto

**Files:**
- Modify: `D:/VYNTIA/CLAUDE.md`

**Por qué:** CLAUDE.md actual dice "Django 4.2 + DRF backend" en varias líneas. Update a Django 5.2 para que futuras sesiones empiecen con la realidad correcta.

- [ ] **Step 1: Identificar líneas con "Django 4.2"**

Run:
```bash
grep -n "Django 4.2\|django.*4\.2" D:/VYNTIA/CLAUDE.md
```

Expected: matches en (aproximadamente) la sección "Repo Structure" y posibles otras menciones.

- [ ] **Step 2: Reemplazar referencias a Django 4.2 → 5.2**

Use Edit con `replace_all=true` para reemplazos seguros:

- replace_all: `Django 4.2 + DRF backend` → `Django 5.2 + DRF backend`

Verifica también la línea que dice algo como "L2 ⏳ Django 4.2 → Django 5". Cámbiala a `L2 ✅ Django 5.2 upgrade done`.

Para encontrarla:
```bash
grep -n "L2 .*Django\|Django.*4\.2.*5\|L2.*upgrade" D:/VYNTIA/CLAUDE.md
```

Edita la línea correspondiente:

- old_string: `- L2 ⏳ Django 4.2 → Django 5 upgrade`
- new_string: `- L2 ✅ Django 5.2 LTS upgrade done`

(Ajusta el `old_string` exacto al contenido literal del archivo.)

- [ ] **Step 3: Verificación final**

Run:
```bash
grep -n "Django 4.2\|django.*4\.2" D:/VYNTIA/CLAUDE.md || echo "OK: cero matches"
```

Expected: `OK: cero matches` (o solo coincidencias en contexto histórico legítimo, ej. "originally Django 4.2 in L0/L1").

- [ ] **Step 4: Commit**

Run:
```bash
git add CLAUDE.md
git commit -m "docs(L2): update CLAUDE.md to reflect Django 5.2 upgrade"
```

---

## Task 9: Smoke tests finales y verificación de DoD

**Files:** ninguno (solo verificación end-to-end)

- [ ] **Step 1: Verificación de versión activa**

Run:
```bash
source D:/VYNTIA/.venv/Scripts/activate
python -c "import django; print('Django', django.get_version())"
```

Expected: `Django 5.2.x`.

- [ ] **Step 2: `manage.py check` development**

Run:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: `manage.py check --deploy` production (solo infra warnings)**

Run:
```bash
cd D:/VYNTIA/apps/api
python manage.py check --deploy --settings=vyntia.settings.production 2>&1 | tail -10
cd ../..
```

Expected: warnings deben ser solo `security.W004`/`W008`/`W009`/`W018`/`W020`/`W021` (infra, deferred a deploy phase). NO debe haber `RemovedInDjango60Warning` ni `RemovedInDjango61Warning`.

- [ ] **Step 4: Pytest baseline**

Run:
```bash
cd D:/VYNTIA/apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: `125 passed, 44 failed, 3 skipped`.

- [ ] **Step 5: Frontend NO debería verse afectado, pero sanity check**

Run:
```bash
cd D:/VYNTIA/apps/web
npm run build 2>&1 | tail -3
cd ../..
```

Expected: `✓ built in Xs`. (L2 es backend-only, pero verificamos que el build frontend sigue funcionando — no debería cambiar nada.)

- [ ] **Step 6: Greps de cleanup**

```bash
echo "=== A: storages legacy ==="
grep -rn "STATICFILES_STORAGE\|DEFAULT_FILE_STORAGE" apps/api --include="*.py" || echo "OK: cero matches"

echo "=== B: pyproject Django constraint ==="
grep "Django>=" apps/api/pyproject.toml

echo "=== C: still on Django 4.2? ==="
python -c "import django; assert django.VERSION[:2] == (5, 2), f'Django {django.get_version()} != 5.2.x'; print('OK: Django 5.2.x')"
```

Expected:
- A: `OK: cero matches`
- B: `    "Django>=5.2,<5.3",`
- C: `OK: Django 5.2.x`

- [ ] **Step 7: Verificar git history y tree**

Run:
```bash
git log --oneline vyntia/L2-django5-upgrade ^master | head -10
git status --short
```

Expected:
- 4-6 commits con prefijo `chore(L2):` / `docs(L2):`
- `git status` vacío

---

## Task 10: Merge a master

**Files:** ninguno

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta: ¿Mergear directo a master local con `--no-ff` (consistente con L0/L1), o mantener la branch para review adicional?

**NO mergear sin autorización explícita.**

- [ ] **Step 2: (Si autoriza) merge `--no-ff` directo**

Run:
```bash
git checkout master
git merge --no-ff vyntia/L2-django5-upgrade -m "Merge L2: Django 4.2 → 5.2 LTS upgrade (STORAGES dict, deprecation cleanup)"
git log --oneline -5
```

Expected: merge commit visible en log; `Merge L2: ...` como HEAD.

- [ ] **Step 3: Smoke test post-merge**

Run:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: ambos verdes con baseline preservado.

- [ ] **Step 4: Branch L2 puede borrarse (con autorización)**

Pregunta al usuario si quiere borrar `vyntia/L2-django5-upgrade`. Si sí:
```bash
git branch -d vyntia/L2-django5-upgrade
```

Si no, déjala — no hay costo de mantenerla local.

---

## Definition of Done — checklist final

Marcar cada item solo cuando esté verificado:

- [ ] `python -c "import django; print(django.get_version())"` → `5.2.x`
- [ ] `apps/api/pyproject.toml` declara `"Django>=5.2,<5.3"`
- [ ] `manage.py check --settings=vyntia.settings.development` → `System check identified no issues`
- [ ] `manage.py check --deploy --settings=vyntia.settings.production` → solo infra warnings (security.W004/W008/W009/W018/W020/W021), CERO RemovedInDjango60/61Warning
- [ ] `pytest` desde `apps/api/` → exactamente 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca sin UnicodeDecodeError ni OperationalError; `/api/docs/` y `/api/schema/` responden 200
- [ ] `apps/api/vyntia/settings/{production,testing,testing_new}.py` ya no contienen `STATICFILES_STORAGE` ni `DEFAULT_FILE_STORAGE` — usan `STORAGES = {...}`
- [ ] CLAUDE.md actualizado: "Django 5.2 + DRF backend" y L2 marcado ✅
- [ ] Branch `vyntia/L2-django5-upgrade` con commits `chore(L2):`/`docs(L2):` mergeada a master con `--no-ff`
- [ ] `git status` limpio
- [ ] Memoria actualizada (manual del controller después del merge): `tech_stack.md` con Django 5.2, `active_subproject.md` con L2 ✅

---

## Después de L2

**Próximo plan:** L3 — División de `app_rrhh` en 8 Django apps (el más grande, 11 sub-PRs L3.1 → L3.11).

Cuando termines L2:
1. Verificar visualmente con el user que el dev server arranca y la app responde.
2. Actualizar memoria del proyecto: `active_subproject.md` (L2 → ✅, L3 → NEXT), `tech_stack.md` (Django 5.2).
3. Solicitar generar el plan de L3 invocando `superpowers:writing-plans` con el sub-spec L3.

---

## Notas para el ejecutor

- **Cada task es atómica y commiteable.** Si Task N rompe, `git reset --hard HEAD~1` y reintenta.
- **NO toques modelos ni `app_rrhh/` internals en L2.** La regla del spec es estricta: `null=True` en text fields, métodos viejos en services, etc., todo va a L3.
- **Si tests aumentan los fallos** (>44 failed), Django 5 introdujo una regresión real — investiga inmediatamente; no acumules deuda.
- **`--deploy` warnings infra (HSTS, DEBUG, SSL_REDIRECT)** se aceptan en L2 — son configuración de despliegue, no código. El DoD habla de "warnings de deprecación", no de security infra.
- **Windows Git Bash:** forward slashes y `source .venv/Scripts/activate`.
- **Si pip install falla por dep transitiva incompatible**, captura el error completo. Lo más probable es alguna lib indirecta (no en nuestro pyproject) que pinneó Django <5. Solución: instalar versión más reciente de esa lib o pin Django a 5.0 (el target más conservador) hasta que la lib soporte 5.2.
