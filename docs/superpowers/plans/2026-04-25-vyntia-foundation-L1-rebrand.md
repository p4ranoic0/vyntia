# VYNTIA Foundation L1 — Rebrand Superficial Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebrandear el monorepo de "INTRANET" a "VYNTIA" en la superficie: nombre del módulo Django (`config/` → `vyntia/`), base de datos nueva (`bd_vyntia`), paquete `pyproject.toml`, design tokens VYNTIA (#6C63FF + Inter), wordmark en topbar/sidebar, copy de login, y referencias en docs. Sin tocar `app_rrhh/*` internals (esa es L3).

**Architecture:** Cambios mecánicos sobre archivos existentes, más un nuevo workspace `packages/design-tokens` y un nuevo `apps/api/pyproject.toml`. La capa de modelo/lógica queda intacta — el rebrand es cosmético + estructural en config. Verificación a lo largo del plan via `python manage.py check --settings=vyntia.settings.development` (no `runserver`, por el known issue de UnicodeDecodeError) + `pytest` (usa SQLite, no toca PG) + `npm run build` y `npm test`.

**Tech Stack:** Django (renombre módulo), pip + pyproject.toml (PEP 621), PostgreSQL (createdb + migrate), JSON (design tokens), CSS variables (HSL), Tailwind (fontFamily), React/Vite (Inter desde Google Fonts).

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L1 — Rebrand superficial"

**Pre-condiciones:**
- L0 completo: branch `master` tiene `apps/api/`, `apps/web/`, `packages/`, `docs/`, `package.json` raíz. Verifica con `git log --oneline -5` que el commit más reciente es `74e134b7 docs: rewrite CLAUDE.md for VYNTIA monorepo (post-L0)` o más reciente.
- venv activo en `D:/VYNTIA/.venv/`. Activación: `source D:/VYNTIA/.venv/Scripts/activate` (Git Bash) o `.venv\Scripts\activate.bat` (cmd).
- Postgres corriendo en `localhost:5432` con un superuser cuya password sea ASCII puro (sin `ñ`/`ó`/etc) — esto destraba el known issue del UnicodeDecodeError.
- Node 20+ y npm 10+.
- `bd_rrhh_intranet` (legacy) puede seguir existiendo intacta — no se toca.

**Definition of Done global:**
- [ ] `python manage.py check --settings=vyntia.settings.development` retorna `System check identified no issues`
- [ ] `pytest` retorna **125 passed, 44 failed, 3 skipped** (baseline exacto, no regresiones)
- [ ] `npm run build` (en `apps/web/`) construye sin errores
- [ ] `npm test -- --run` mantiene su baseline (7 passed, 1 file load-failure pre-existente)
- [ ] BD `bd_vyntia` existe y tiene el esquema migrado
- [ ] `grep -ri "INTRANET\|Sistema RRHH\|HR Intranet\|HR Sistema\|hr-intranet" apps/web/` → solo coincidencias en archivos generados (`generated/`) o legacy domain terms. Cero matches en componentes activos
- [ ] `grep -rin "config\.settings\|config\.urls\|config\.wsgi\|config\.asgi" apps/api/ --include="*.py" --include="*.ini" --include="*.template" --include="*.example" --include="Makefile"` → cero matches
- [ ] Visualmente: sidebar dice **VYNTIA**, primary color es violeta `#6C63FF`, font es **Inter**, login copy menciona VYNTIA
- [ ] Branch `vyntia/L1-rebrand-surface` con commits `chore(L1):` (uno por task que commitea)
- [ ] `git status` limpio al final

---

## File Structure Overview

| Acción | Archivo / Path | Notas |
|---|---|---|
| Modify | `.gitignore` (raíz) | Restaurar reglas custom perdidas en L0 (Task 2) |
| Create | `packages/design-tokens/package.json` | Workspace npm |
| Create | `packages/design-tokens/tokens.json` | Source of truth de colores/fonts/spacing |
| Create | `packages/design-tokens/index.js` | Export del JSON para consumo desde web |
| Create | `apps/api/pyproject.toml` | Reemplaza `requirements.txt` |
| Delete | `apps/api/requirements.txt` | Después de validar pyproject |
| Rename | `apps/api/config/` → `apps/api/vyntia/` | `git mv` + replace_all en imports |
| Modify | `apps/api/manage.py` | `config.settings.development` → `vyntia.settings.development` |
| Modify | `apps/api/conftest.py` | `config.settings.testing` → `vyntia.settings.testing` |
| Modify | `apps/api/pytest.ini` | Idem |
| Modify | `apps/api/.env.template`, `.env.example` | DB_NAME, DJANGO_SETTINGS_MODULE |
| Modify | `apps/api/vyntia/asgi.py`, `wsgi.py`, `celery.py` | Strings DJANGO_SETTINGS_MODULE + docstrings + Celery name |
| Modify | `apps/api/vyntia/settings/base.py` | `ROOT_URLCONF`, `WSGI_APPLICATION`, SPECTACULAR title/description |
| Modify | `apps/api/scripts/*.py` | Múltiples scripts referencian `config.settings.development` |
| Modify | `apps/api/Makefile` | Sin cambios si no menciona `config.*`; verificar |
| Modify | `apps/api/{README,SETUP,DEPLOYMENT}.md` | Strings INTRANET → VYNTIA y `config.*` → `vyntia.*` |
| Modify | `apps/web/index.html` | `<title>`, meta description, link Inter, lang |
| Modify | `apps/web/package.json` | `name: "hr-intranet-system"` → `"vyntia-web"` |
| Modify | `apps/web/tailwind.config.js` | `fontFamily.sans` y `heading` a Inter |
| Create | `apps/web/src/styles/tokens.css` | Variables CSS VYNTIA (consume design-tokens conceptualmente) |
| Modify | `apps/web/src/index.css` | Importar `./styles/tokens.css` en lugar de `./styles/colors.css` |
| Delete | `apps/web/src/styles/colors.css` | Reemplazado por tokens.css |
| Create | `apps/web/public/vyntia-logo.svg` | Logo placeholder (nodos+curvas) |
| Create | `apps/web/src/components/brand/VyntiaWordmark.tsx` | Componente reutilizable |
| Modify | `apps/web/src/components/layout/Sidebar.tsx` | "HR Sistema" → `<VyntiaWordmark />` |
| Modify | `apps/web/src/components/auth/LoginForm.tsx` | "Acceso Seguro RRHH" → copy VYNTIA |
| Modify | `D:/VYNTIA/CLAUDE.md` | Eliminar referencia a `config/` y `bd_rrhh_intranet`, dejar `vyntia/` y `bd_vyntia` |
| Modify | `D:/VYNTIA/README.md` | Texto y comandos actualizados con `vyntia.settings.*` |
| Modify | `D:/VYNTIA/docs/QUICKSTART.md` | Reemplazar paths `D:\INTRANET` y `bd_rrhh_intranet` |

NO se tocan en L1: `apps/api/app_rrhh/**`, `apps/api/api/v1/**`, `apps/api/core/**`, `apps/api/templates/**`, ningún `.py` con lógica de negocio. Esos quedan para L3.

---

## Task 1: Confirmar baseline y crear branch L1

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Confirmar pwd y git limpio**

Run desde la raíz del repo:
```bash
pwd
git status --short
git log --oneline -3
```

Expected:
- `pwd`: `/d/VYNTIA` (o equivalente Windows)
- `git status`: salida vacía
- `git log`: muestra `74e134b7 docs: rewrite CLAUDE.md for VYNTIA monorepo (post-L0)` o más reciente como HEAD de master

Si `git status` no está limpio, **detente** — committea o stashea antes de seguir.

- [ ] **Step 2: Activar venv**

Run:
```bash
source .venv/Scripts/activate
which python
python --version
```

Expected: ruta al `python.exe` dentro de `.venv/`, versión `Python 3.11.x` o superior.

- [ ] **Step 3: Confirmar baseline pytest pre-L1 (debe coincidir con el documentado en MEMORY)**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected (literal): `125 passed, 44 failed, 3 skipped` (puede mostrar también `1 warning`).

Si los números difieren, **detente** y consulta al usuario antes de continuar — el plan asume estos exactos counts.

- [ ] **Step 4: Confirmar baseline frontend pre-L1**

Run:
```bash
cd apps/web
npm test -- --run --reporter=basic 2>&1 | tail -8
cd ../..
```

Expected: `Test Files  1 failed | 2 passed (3)` (file fail = `tests/e2e/auth.test.js`, pre-existing) y `Tests  7 passed (7)`. Anota cualquier desviación.

- [ ] **Step 5: Crear branch L1**

Run:
```bash
git checkout -b vyntia/L1-rebrand-surface
git status
```

Expected: `On branch vyntia/L1-rebrand-surface`, working tree limpio.

---

## Task 2: Pre-L1 patch — restaurar reglas perdidas en `.gitignore`

**Files:**
- Modify: `D:/VYNTIA/.gitignore`

**Por qué:** El L0 consolidó `.gitignore` pero descartó reglas custom heredadas (`.planning/`, `.claude/`, exceptions de env files, etc.). Restaurarlas ahora antes de que aparezcan untracked.

- [ ] **Step 1: Leer `.gitignore` actual y confirmar que las reglas a añadir no están ya**

Run:
```bash
grep -E "\.planning|\.claude|\.playwright-mcp|\.env\.example|\.vscode/extensions" .gitignore || echo "OK: reglas faltantes confirmadas"
```

Expected: `OK: reglas faltantes confirmadas`.

- [ ] **Step 2: Añadir bloque al final de `.gitignore`**

Usa la herramienta `Edit` con `old_string` siendo la última sección actual del archivo y append. Concretamente, abre `D:/VYNTIA/.gitignore`, localiza el bloque final:

```
# === VYNTIA specific ===
apps/api/media/
apps/api/staticfiles/
apps/api/logs/
```

Y reemplázalo por:

```
# === VYNTIA specific ===
apps/api/media/
apps/api/staticfiles/
apps/api/logs/

# === Claude / agent state (restored from legacy) ===
.planning/
.claude/
.playwright-mcp/

# === VS Code (allow shareable configs only) ===
!.vscode/extensions.json
!.vscode/tasks.json

# === Env file exceptions (allow templates) ===
!.env.example
!**/.env.example
!**/.env.template

# === Local-only logs and scratch (legacy patterns) ===
backend_foreground.log
server_err*.log
test_output.log
nul
tests/data/*.json
tests/html/
back/package-lock.json
```

- [ ] **Step 3: Verificar que `.gitignore` no introduce nuevos archivos a rastrear**

Run:
```bash
git status --short
```

Expected: solo `M .gitignore`. Sin archivos nuevos untracked apareciendo "por error".

- [ ] **Step 4: Commit**

Run:
```bash
git add .gitignore
git commit -m "chore(L1): restore custom .gitignore rules lost in L0"
```

Expected: 1 file changed.

---

## Task 3: Crear workspace `packages/design-tokens`

**Files:**
- Create: `packages/design-tokens/package.json`
- Create: `packages/design-tokens/tokens.json`
- Create: `packages/design-tokens/index.js`
- Create: `packages/design-tokens/README.md`

**Por qué:** Es la fuente de verdad de la marca VYNTIA (colores, fonts, spacing, layout). Lo consumirá `apps/web` directamente vía npm workspace.

- [ ] **Step 1: Crear `packages/design-tokens/package.json`**

Crear archivo `packages/design-tokens/package.json` con contenido exacto:

```json
{
  "name": "@vyntia/design-tokens",
  "version": "0.1.0",
  "private": true,
  "description": "VYNTIA design tokens — single source of truth for brand colors, typography, spacing and layout",
  "main": "index.js",
  "files": [
    "tokens.json",
    "index.js"
  ]
}
```

- [ ] **Step 2: Crear `packages/design-tokens/tokens.json`**

Crear archivo con contenido exacto:

```json
{
  "color": {
    "primary": "#6C63FF",
    "primaryHsl": "244 100% 69%",
    "dark": "#0F172A",
    "darkHsl": "222 47% 11%",
    "light": "#FFFFFF",
    "lightHsl": "0 0% 100%",
    "gray": "#E5E7EB",
    "grayHsl": "220 13% 91%",
    "success": "#22C55E",
    "successHsl": "142 71% 45%",
    "error": "#EF4444",
    "errorHsl": "0 84% 60%",
    "darkBgCard": "#1E293B",
    "darkBgCardHsl": "217 33% 17%",
    "darkText": "#E5E7EB"
  },
  "font": {
    "family": "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
    "size": {
      "h1": "28px",
      "h2": "20px",
      "body": "14px",
      "caption": "12px"
    },
    "weight": {
      "regular": 400,
      "medium": 500,
      "semibold": 600,
      "bold": 700
    }
  },
  "spacing": {
    "1": "4px",
    "2": "8px",
    "3": "16px",
    "4": "24px",
    "5": "32px",
    "6": "48px"
  },
  "layout": {
    "sidebarWidth": "240px",
    "topbarHeight": "72px",
    "contentPadding": "24px"
  },
  "brand": {
    "name": "VYNTIA",
    "slogan": "Donde el talento se convierte en valor.",
    "modules": [
      "Vyntia Core",
      "Vyntia People",
      "Vyntia Pulse",
      "Vyntia Pay",
      "Vyntia Hire",
      "Vyntia Insights"
    ]
  }
}
```

- [ ] **Step 3: Crear `packages/design-tokens/index.js`**

Crear archivo:

```javascript
const tokens = require('./tokens.json');

module.exports = tokens;
module.exports.default = tokens;
```

- [ ] **Step 4: Crear `packages/design-tokens/README.md`**

Crear archivo:

```markdown
# @vyntia/design-tokens

Source of truth for VYNTIA brand tokens — colors, typography, spacing, layout.

Consumed by `apps/web` via npm workspaces. Editing `tokens.json` propagates to consumers; CSS variables in `apps/web/src/styles/tokens.css` are kept in sync manually for now.

## Usage

```js
const tokens = require('@vyntia/design-tokens');
console.log(tokens.color.primary); // "#6C63FF"
```

## Source

Brand kit: `vyntia_brand_ui.md`, `vyntia_full_system.md` (originally in `C:/Users/zeeke/Downloads/`).
```

- [ ] **Step 5: Reinstalar workspaces y verificar que npm reconoce `@vyntia/design-tokens`**

Run desde la raíz del repo:
```bash
npm install
npm ls --workspaces --depth=0 2>&1 | head -10
```

Expected: lista incluye `@vyntia/design-tokens@0.1.0` y `hr-intranet-system@1.0.0` (el de `apps/web`, aún sin renombrar — eso es Task 11).

- [ ] **Step 6: Commit**

Run:
```bash
git add packages/design-tokens/
git commit -m "chore(L1): add @vyntia/design-tokens workspace with brand source-of-truth"
```

---

## Task 4: Crear `apps/api/pyproject.toml`

**Files:**
- Create: `apps/api/pyproject.toml`

**Por qué:** Spec L1 manda reemplazar `requirements.txt` con `pyproject.toml` (package name `vyntia-api`). La eliminación de `requirements.txt` se hará al final de Task 5 cuando se valide que pip install funciona.

- [ ] **Step 1: Crear `apps/api/pyproject.toml`**

Crear archivo con contenido exacto:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "vyntia-api"
version = "0.1.0"
description = "VYNTIA API — backend Django del SaaS modular de RRHH para Perú"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "Proprietary" }
authors = [
    { name = "VYNTIA team" },
]

dependencies = [
    # Core Django
    "Django>=4.2.0,<5.0.0",
    "djangorestframework>=3.14.0",
    "djangorestframework-simplejwt>=5.2.0",
    "django-cors-headers>=4.0.0",
    "django-filter>=23.0",
    "django-extensions>=3.2.0",

    # Database
    "psycopg2-binary>=2.9.0",

    # API documentation
    "drf-spectacular>=0.26.0",

    # Production
    "gunicorn>=20.1.0",
    "whitenoise>=6.0.0",

    # Monitoring
    "sentry-sdk>=1.25.0",

    # Utilities
    "Pillow>=9.0.0",
    "python-decouple>=3.6",
    "celery>=5.2.0",
    "redis>=4.5.0",
    "django-redis>=5.4.0",
    "hiredis>=2.2.0",

    # PDF generation
    "reportlab>=4.0.0",
    "xhtml2pdf>=0.2.17",
    "weasyprint>=60.0",
    "jinja2>=3.1.0",

    # Excel
    "openpyxl>=3.1.0",

    # Storage
    "django-storages[s3]>=1.14.0",
    "boto3>=1.28.0",
]

[project.optional-dependencies]
dev = [
    "ipython>=8.0.0",
    "pytest>=7.0.0",
    "pytest-django>=4.5.0",
    "pytest-cov>=4.0.0",
    "pytest-html>=3.1.0",
    "pytest-xdist>=3.0.0",
    "factory-boy>=3.2.0",
    "faker>=18.0.0",
]

[tool.setuptools]
# Backend package layout: solo se distribuyen estos top-levels.
# Cuando L3 cree apps/api/apps/, este `packages` debe actualizarse.
packages = ["vyntia", "app_rrhh", "api", "core"]
include-package-data = true
```

- [ ] **Step 2: Verificar que `pyproject.toml` parsea**

Run:
```bash
cd apps/api
python -c "import tomllib; tomllib.load(open('pyproject.toml','rb')); print('OK: pyproject.toml is valid TOML')"
cd ../..
```

Expected: `OK: pyproject.toml is valid TOML`.

Si Python <3.11 no tiene `tomllib`, usar `python -c "import tomli; tomli.load(open('apps/api/pyproject.toml','rb'))"` o instalar `tomli` previamente.

- [ ] **Step 3: Smoke test — instalar el paquete editable**

Run:
```bash
cd apps/api
pip install -e ".[dev]" 2>&1 | tail -10
cd ../..
```

Expected: termina sin errores. Puede haber warnings de `pkg_resources` o `setuptools` deprecation — esos son OK. Si hay `ERROR:` real, anotarlo y diagnosticar antes de seguir.

- [ ] **Step 4: Verificar que Django/pytest siguen funcionando con la nueva instalación**

Run:
```bash
cd apps/api
python -c "import django; print('Django OK', django.get_version())"
python -c "import pytest; print('pytest OK', pytest.__version__)"
cd ../..
```

Expected: ambos OK.

- [ ] **Step 5: Commit (sin borrar requirements.txt todavía)**

Run:
```bash
git add apps/api/pyproject.toml
git commit -m "chore(L1): add apps/api/pyproject.toml as new package source-of-truth"
```

---

## Task 5: Renombrar módulo `config/` → `vyntia/` y actualizar todas las referencias

**Files:**
- Move: `apps/api/config/` → `apps/api/vyntia/`
- Modify: `apps/api/manage.py`
- Modify: `apps/api/conftest.py`
- Modify: `apps/api/pytest.ini`
- Modify: `apps/api/.env.template`
- Modify: `apps/api/.env.example` (si tiene referencias)
- Modify: `apps/api/vyntia/asgi.py` (post-rename)
- Modify: `apps/api/vyntia/wsgi.py`
- Modify: `apps/api/vyntia/celery.py`
- Modify: `apps/api/vyntia/settings/base.py`
- Modify: `apps/api/scripts/*.py` (varios)
- Modify: `apps/api/Makefile` (si referencia config.*)
- Modify: `apps/api/pyproject.toml` (packages: ya menciona `vyntia`, OK)

**Por qué:** Spec § 4 L1: `config/` → `vyntia/` y `DJANGO_SETTINGS_MODULE` → `vyntia.settings.development`. Es el cambio de mayor impacto del L1.

- [ ] **Step 1: Asegurarse que ningún proceso Python tiene file handles abiertos en `config/`**

Run (Git Bash):
```bash
ps -W 2>/dev/null | grep -iE "python|gunicorn" || tasklist | grep -iE "python|gunicorn" || echo "no python procs"
```

Si aparecen procesos Python que podrían venir de un `runserver`/`pytest` previo, terminarlos antes del `git mv`. En Windows: `taskkill //PID <pid> //F`.

- [ ] **Step 2: `git mv` el módulo**

Run:
```bash
git mv apps/api/config apps/api/vyntia
ls apps/api/vyntia
```

Expected: `apps/api/vyntia/` existe con `__init__.py`, `asgi.py`, `celery.py`, `modules_config.py`, `settings/`, `spectacular_settings.py`, `urls.py`, `wsgi.py`.

`apps/api/config/` ya no existe.

- [ ] **Step 3: Verificar (esperado fallo) que sin actualizar imports, el sistema falla**

Run:
```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: error con `ModuleNotFoundError: No module named 'config'` proveniente de `ROOT_URLCONF = "config.urls"` o similar. Esto es esperado — confirma que el rename está captando los lugares correctos.

- [ ] **Step 4: Actualizar `apps/api/manage.py`**

Editar `apps/api/manage.py` línea 26: cambiar `"config.settings.development"` → `"vyntia.settings.development"`.

Use Edit tool:
- old_string: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")`
- new_string: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.development")`

También: línea 40 tiene un `main()` duplicado bug — déjalo como está, no es scope L1.

- [ ] **Step 5: Actualizar `apps/api/conftest.py`**

Editar `apps/api/conftest.py`:
- old_string: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.testing")`
- new_string: `os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.testing")`

- [ ] **Step 6: Actualizar `apps/api/pytest.ini`**

Editar línea 2:
- old_string: `DJANGO_SETTINGS_MODULE = config.settings.testing`
- new_string: `DJANGO_SETTINGS_MODULE = vyntia.settings.testing`

- [ ] **Step 7: Actualizar `apps/api/vyntia/asgi.py`**

Reemplazar el archivo completo con:

```python
"""
ASGI config for VYNTIA project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')

application = get_asgi_application()
```

- [ ] **Step 8: Actualizar `apps/api/vyntia/wsgi.py`**

Lee el archivo, luego usa Edit para reemplazar:
- En el docstring: `WSGI config for project_intranet project.` → `WSGI config for VYNTIA project.`
- En el `setdefault`: `'config.settings.development'` → `'vyntia.settings.development'`

- [ ] **Step 9: Actualizar `apps/api/vyntia/celery.py`**

Reemplazar el archivo completo con:

```python
"""Celery app configuration for VYNTIA."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.development")

app = Celery("vyntia")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug helper task for local verification."""
    print(f"Request: {self.request!r}")
```

- [ ] **Step 10: Actualizar `apps/api/vyntia/settings/base.py` (ROOT_URLCONF, WSGI_APPLICATION, docstring, SPECTACULAR)**

Edita `apps/api/vyntia/settings/base.py`:

a) Línea 1 docstring:
- old_string: `"""Configuración base de Django para project_intranet."""`
- new_string: `"""Configuración base de Django para VYNTIA."""`

b) Línea 57 ROOT_URLCONF:
- old_string: `ROOT_URLCONF = "config.urls"`
- new_string: `ROOT_URLCONF = "vyntia.urls"`

c) Línea 75 WSGI_APPLICATION:
- old_string: `WSGI_APPLICATION = "config.wsgi.application"`
- new_string: `WSGI_APPLICATION = "vyntia.wsgi.application"`

d) SPECTACULAR_SETTINGS title/description (líneas ~337-338):
- old_string:
```python
    "TITLE": "Intranet RRHH API",
    "DESCRIPTION": "API para el sistema de gestión de recursos humanos de la intranet corporativa",
```
- new_string:
```python
    "TITLE": "VYNTIA API",
    "DESCRIPTION": "API del SaaS modular VYNTIA — gestión de Recursos Humanos para Perú",
```

- [ ] **Step 11: Actualizar docstrings de `apps/api/vyntia/settings/{development,production,staging,testing,testing_new}.py`**

Para cada archivo, reemplazar `"""Configuración de <X> para project_intranet."""` por `"""Configuración de <X> para VYNTIA."""`. Mantener el resto del archivo intacto.

Run para listar:
```bash
grep -n "project_intranet" apps/api/vyntia/settings/*.py
```

Expected después de editar: salida vacía.

- [ ] **Step 12: Actualizar `apps/api/.env.template`**

- old_string: `DJANGO_SETTINGS_MODULE=config.settings.development`
- new_string: `DJANGO_SETTINGS_MODULE=vyntia.settings.development`

(El cambio de `DB_NAME` se hace en Task 7 — aquí solo el module path).

- [ ] **Step 13: Actualizar `apps/api/.env.example` (si tiene la referencia)**

Run:
```bash
grep -n "config\.settings" apps/api/.env.example || echo "OK: no config.settings en .env.example"
```

Si aparece, edita esa línea a `vyntia.settings.development`. Si no, skip.

- [ ] **Step 14: Actualizar todos los scripts en `apps/api/scripts/`**

Lista de archivos con la referencia (confirmados):
- `apps/api/scripts/check_admin_empleado.py`
- `apps/api/scripts/check_perms.py`
- `apps/api/scripts/generate_schema.py`
- `apps/api/scripts/generate_openapi_schema.py` (si existe)
- `apps/api/scripts/load_demo_data.py`
- `apps/api/scripts/seed_vacaciones_historial_demo.py`
- `apps/api/scripts/set_admin_password.py`
- `apps/api/scripts/verify_password.py`
- `apps/api/scripts/migrate_mysql_to_postgresql.ps1` (PowerShell — string literal, igual reemplazo)

Para cada archivo, reemplazar todas las apariciones literales de `config.settings.development` → `vyntia.settings.development`.

Forma rápida vía PowerShell (desde la raíz):
```powershell
Get-ChildItem -Path apps/api/scripts -Recurse -Include *.py,*.ps1 | ForEach-Object {
    (Get-Content $_.FullName) -replace 'config\.settings\.development', 'vyntia.settings.development' | Set-Content $_.FullName -Encoding UTF8
}
```

O Bash con sed:
```bash
find apps/api/scripts -type f \( -name "*.py" -o -name "*.ps1" \) -print0 | xargs -0 sed -i 's/config\.settings\.development/vyntia.settings.development/g'
```

Verificar:
```bash
grep -rn "config\.settings" apps/api/scripts/ || echo "OK: scripts limpios"
```

Expected: `OK: scripts limpios`.

- [ ] **Step 15: Verificar que `apps/api/Makefile` no referencia `config.*`**

Run:
```bash
grep -n "config\." apps/api/Makefile || echo "OK: Makefile sin config.*"
```

Si aparece algo, editarlo. Hoy debería decir solo `OK`.

- [ ] **Step 16: Smoke test — `manage.py check`**

Run:
```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

Si aparece `ModuleNotFoundError: No module named 'config'` o similar, **buscar el archivo culpable**:

```bash
grep -rn "config\.settings\|config\.urls\|config\.wsgi\|config\.asgi\|from config\|import config\b" apps/api/ --include="*.py" --include="*.ini" --include="*.template" --include="*.example" --include="Makefile" --include="*.toml"
```

Editar cada match. Repetir el `manage.py check` hasta que pase.

- [ ] **Step 17: Smoke test — pytest no regresa**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: **125 passed, 44 failed, 3 skipped**. Si los counts cambiaron, diagnosticar inmediatamente — el rename rompió algo.

- [ ] **Step 18: Commit**

Run:
```bash
git add apps/api/
git status --short  # debería estar limpio después
git commit -m "chore(L1): rename apps/api/config to apps/api/vyntia and update all imports"
```

---

## Task 6: Eliminar `apps/api/requirements.txt`

**Files:**
- Delete: `apps/api/requirements.txt`

**Por qué:** Spec L1: "pyproject.toml reemplaza requirements.txt". Después de Task 4 + Task 5, pyproject está validado funcionando. Eliminamos el legacy para evitar drift.

- [ ] **Step 1: Confirmar que el venv tiene los paquetes del pyproject.toml**

Run:
```bash
pip list 2>&1 | grep -iE "django|drf|spectacular|reportlab|gunicorn" | head -10
```

Expected: lista incluye Django, djangorestframework, drf-spectacular, reportlab, gunicorn (etc).

- [ ] **Step 2: Eliminar el archivo**

Run:
```bash
git rm apps/api/requirements.txt
ls apps/api/requirements.txt 2>&1
```

Expected: `ls: cannot access 'apps/api/requirements.txt': No such file or directory`

- [ ] **Step 3: Confirmar que pytest sigue verde**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -3
cd ../..
```

Expected: **125 passed, 44 failed, 3 skipped**.

- [ ] **Step 4: Commit**

Run:
```bash
git commit -m "chore(L1): remove apps/api/requirements.txt (replaced by pyproject.toml)"
```

---

## Task 7: Actualizar `.env.template` y `.env.example` para apuntar a `bd_vyntia`

**Files:**
- Modify: `apps/api/.env.template`
- Modify: `apps/api/.env.example`

**Por qué:** Antes de crear la BD, el `.env` debe describir el target VYNTIA para que el dev sepa qué configurar. Cambios mínimos — solo nombres de DB y comentarios de marca.

- [ ] **Step 1: Actualizar `apps/api/.env.template`**

Cambios:

a) Bloque "Database":
- old_string:
```
DB_NAME=bd_rrhh_intranet
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=prefer
DB_CONNECT_TIMEOUT=10
DB_TEST_NAME=test_bd_rrhh_intranet
```
- new_string:
```
DB_NAME=bd_vyntia
DB_USER=postgres
DB_PASSWORD=change-me
DB_HOST=localhost
DB_PORT=5432
DB_SSLMODE=prefer
DB_CONNECT_TIMEOUT=10
DB_TEST_NAME=test_bd_vyntia
```

b) Bloque "Optional read-replica":
- old_string: `DB_READ_NAME=bd_rrhh_intranet`
- new_string: `DB_READ_NAME=bd_vyntia`

- [ ] **Step 2: Actualizar `apps/api/.env.example`**

Buscar:
```bash
grep -n "bd_rrhh_intranet\|INTRANET RRHH\|intranet.local\|intranet" apps/api/.env.example
```

Para cada match, decidir:
- `DB_NAME=bd_rrhh_intranet` → `DB_NAME=bd_vyntia`
- `DB_NAME=test_bd_rrhh_intranet` → `DB_NAME=test_bd_vyntia`
- `INTRANET RRHH - VARIABLES DE AMBIENTE` (header comment) → `VYNTIA - VARIABLES DE AMBIENTE`
- `*.intranet.local` (ALLOWED_HOSTS) → `*.vyntia.local`
- Cualquier otro `intranet` en comentarios literales → `vyntia`

Editar cada match con `Edit` tool.

- [ ] **Step 3: Verificar que el `.env` real (si existe en el sandbox del usuario) no se commitea**

Run:
```bash
git status --short | grep "\.env$" && echo "WARN: .env real en git status" || echo "OK: no .env tracked"
```

Expected: `OK: no .env tracked` (debería estar en `.gitignore`).

- [ ] **Step 4: Commit**

Run:
```bash
git add apps/api/.env.template apps/api/.env.example
git commit -m "chore(L1): update .env templates to point at bd_vyntia"
```

---

## Task 8: Crear base de datos `bd_vyntia` y migrar el esquema

**Files:** ninguno (cambios en Postgres, no en el repo)

**Por qué:** Spec L1: "BD nueva `bd_vyntia` creada con `python manage.py migrate` (esquema actual)". La BD vieja `bd_rrhh_intranet` queda intacta como backup.

**Pre-requisito crítico:** El `DB_PASSWORD` en el `.env` real debe ser ASCII puro (sin `ñ`, `ó`, etc.) para evitar el known issue de UnicodeDecodeError. Si el password actual tiene caracteres no-ASCII, **detente** y pide al usuario:
1. Cambiar la password de Postgres a una ASCII pura: `psql -U postgres -c "ALTER USER postgres WITH PASSWORD '<nueva_password_ascii>';"`
2. Actualizar el `.env` local correspondientemente.

- [ ] **Step 1: Confirmar que Postgres está corriendo**

Run:
```bash
psql -U postgres -h localhost -c "SELECT version();" 2>&1 | head -3
```

Expected: `PostgreSQL X.Y on ...`. Si error, arrancar el servicio Postgres antes de seguir.

- [ ] **Step 2: Crear la BD `bd_vyntia` (idempotente)**

Run:
```bash
psql -U postgres -h localhost -c "CREATE DATABASE bd_vyntia WITH ENCODING 'UTF8' TEMPLATE template0;" 2>&1
```

Expected: `CREATE DATABASE`. Si dice `database "bd_vyntia" already exists`, también OK — significa que ya existe.

- [ ] **Step 3: Cargar `.env` y aplicar migraciones**

Run (asumiendo que existe `apps/api/.env` con `DB_NAME=bd_vyntia` y password ASCII):

```bash
cd apps/api
python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -30
cd ../..
```

Expected: una secuencia de `Applying contenttypes.0001_initial... OK`, `Applying auth.0001_initial... OK`, ..., `Applying app_rrhh.XXXX... OK`, terminando sin errores.

Si aparece `UnicodeDecodeError`, **detente**: el password aún tiene caracteres no-ASCII. Resolver y reintentar.

Si la BD ya estaba migrada de un intento previo, debería decir `No migrations to apply` — también OK.

- [ ] **Step 4: Verificar el esquema**

Run:
```bash
psql -U postgres -h localhost -d bd_vyntia -c "\dt app_rrhh_*" 2>&1 | head -25
```

Expected: lista de tablas `app_rrhh_*` (al menos 18 tablas: `app_rrhh_usuario`, `app_rrhh_empleado`, `app_rrhh_area`, etc.).

- [ ] **Step 5: Smoke test — verificar conexión desde Django**

Run:
```bash
cd apps/api
python manage.py check --database default --settings=vyntia.settings.development
cd ../..
```

Expected: `System check identified no issues (0 silenced).` (no debe fallar al verificar la BD).

- [ ] **Step 6: NO commit (esta task no toca el repo)**

Documentar en el handoff al user que `bd_vyntia` ya existe con esquema. La BD vieja `bd_rrhh_intranet` puede borrarse manualmente cuando el user lo decida — fuera del scope L1.

---

## Task 9: Crear `apps/web/src/styles/tokens.css` con palette VYNTIA

**Files:**
- Create: `apps/web/src/styles/tokens.css`
- Modify: `apps/web/src/index.css` (cambiar import)
- Delete: `apps/web/src/styles/colors.css`

**Por qué:** Reemplazar la paleta azul corporativa (legacy) con la paleta VYNTIA violeta (#6C63FF) + Inter. Mantenemos los nombres de variables CSS (`--primary`, `--background`, etc.) para no romper Tailwind/shadcn.

- [ ] **Step 1: Crear `apps/web/src/styles/tokens.css`**

Crear archivo con contenido exacto:

```css
/* =====================================================
   VYNTIA — Design Tokens
   =====================================================
   Source of truth: packages/design-tokens/tokens.json
   Esta capa CSS espeja esos valores en variables HSL
   consumidas por Tailwind y shadcn/ui.
   ===================================================== */

@layer base {
  :root {
    /* ═══════════════════════════════════════════════════
       PALETA VYNTIA — TEMA CLARO
       Primary #6C63FF (violet), Light #FFFFFF
       ═══════════════════════════════════════════════════ */

    /* --- Fondos principales --- */
    --background: 0 0% 100%;            /* #FFFFFF */
    --foreground: 222 47% 11%;          /* #0F172A */

    /* --- Superficies --- */
    --card: 0 0% 100%;
    --card-foreground: 222 47% 11%;
    --popover: 0 0% 100%;
    --popover-foreground: 222 47% 11%;
    --surface-1: 220 14% 96%;
    --surface-2: 220 13% 91%;           /* #E5E7EB */
    --surface-3: 218 11% 85%;

    /* --- Marca / Primary --- */
    --primary: 244 100% 69%;            /* #6C63FF — VYNTIA violet */
    --primary-foreground: 0 0% 100%;

    /* --- Secondary & Muted --- */
    --secondary: 220 13% 91%;
    --secondary-foreground: 222 47% 11%;
    --muted: 220 14% 96%;
    --muted-foreground: 220 9% 46%;

    /* --- Accent (violet wash) --- */
    --accent: 244 100% 96%;
    --accent-foreground: 244 60% 45%;

    /* --- Destructive --- */
    --destructive: 0 84% 60%;           /* #EF4444 */
    --destructive-foreground: 0 0% 100%;

    /* --- Bordes & Inputs --- */
    --border: 220 13% 91%;              /* #E5E7EB */
    --input: 220 13% 91%;
    --ring: 244 100% 69%;
    --radius: 0.625rem;

    /* --- Colores semánticos --- */
    --success: 142 71% 45%;             /* #22C55E */
    --success-foreground: 0 0% 100%;
    --warning: 38 92% 50%;
    --warning-foreground: 0 0% 100%;
    --info: 244 100% 69%;
    --info-foreground: 0 0% 100%;

    /* --- Charts (violet-led palette) --- */
    --chart-1: 244 100% 69%;            /* primary violet */
    --chart-2: 142 71% 45%;             /* success green */
    --chart-3: 38 92% 50%;              /* amber */
    --chart-4: 280 65% 60%;             /* magenta */
    --chart-5: 199 89% 48%;             /* sky */

    /* --- Tipografía VYNTIA --- */
    --font-heading: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-body: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;

    /* --- Sombras (tinte violeta sutil) --- */
    --shadow-xs: 0 1px 2px hsl(244 100% 69% / 0.04);
    --shadow-sm: 0 1px 3px hsl(244 100% 69% / 0.06), 0 1px 2px hsl(244 100% 69% / 0.04);
    --shadow-md: 0 4px 6px -1px hsl(244 100% 69% / 0.06), 0 2px 4px -2px hsl(244 100% 69% / 0.04);
    --shadow-lg: 0 10px 15px -3px hsl(244 100% 69% / 0.06), 0 4px 6px -4px hsl(244 100% 69% / 0.04);
    --shadow-xl: 0 20px 25px -5px hsl(244 100% 69% / 0.08), 0 8px 10px -6px hsl(244 100% 69% / 0.04);
    --shadow-colored: 0 4px 14px -2px hsl(244 100% 69% / 0.20);

    /* --- Sidebar --- */
    --sidebar-bg: 0 0% 100%;
    --sidebar-border: 220 13% 91%;
    --sidebar-active: 244 100% 69%;
    --sidebar-active-bg: 244 100% 69% / 0.10;
    --sidebar-hover: 220 14% 96%;

    /* --- Header --- */
    --header-bg: 0 0% 100%;
    --header-border: 220 13% 91%;
    --header-shadow: 0 1px 3px hsl(244 100% 69% / 0.04);
  }

  .dark {
    /* ═══════════════════════════════════════════════════
       PALETA VYNTIA — TEMA OSCURO
       Background #0F172A, Cards #1E293B, Text #E5E7EB
       ═══════════════════════════════════════════════════ */

    --background: 222 47% 11%;          /* #0F172A */
    --foreground: 220 13% 91%;          /* #E5E7EB */

    --card: 217 33% 17%;                /* #1E293B */
    --card-foreground: 220 13% 91%;
    --popover: 217 33% 17%;
    --popover-foreground: 220 13% 91%;
    --surface-1: 222 47% 13%;
    --surface-2: 217 33% 17%;
    --surface-3: 215 28% 22%;

    --primary: 244 100% 75%;            /* slightly brighter on dark */
    --primary-foreground: 222 47% 11%;

    --secondary: 215 28% 17%;
    --secondary-foreground: 220 13% 91%;
    --muted: 215 28% 17%;
    --muted-foreground: 220 9% 65%;

    --accent: 244 50% 25%;
    --accent-foreground: 244 100% 80%;

    --destructive: 0 63% 45%;
    --destructive-foreground: 0 0% 100%;

    --border: 215 28% 22%;
    --input: 215 28% 22%;
    --ring: 244 100% 75%;

    --success: 142 71% 45%;
    --success-foreground: 0 0% 100%;
    --warning: 38 92% 55%;
    --warning-foreground: 0 0% 100%;
    --info: 244 100% 75%;
    --info-foreground: 0 0% 100%;

    --chart-1: 244 100% 75%;
    --chart-2: 142 71% 45%;
    --chart-3: 38 92% 55%;
    --chart-4: 280 65% 65%;
    --chart-5: 199 89% 55%;

    --font-heading: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-body: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;

    --shadow-xs: 0 1px 2px hsl(0 0% 0% / 0.3);
    --shadow-sm: 0 1px 3px hsl(0 0% 0% / 0.4), 0 1px 2px hsl(0 0% 0% / 0.3);
    --shadow-md: 0 4px 6px -1px hsl(0 0% 0% / 0.4), 0 2px 4px -2px hsl(0 0% 0% / 0.3);
    --shadow-lg: 0 10px 15px -3px hsl(0 0% 0% / 0.4), 0 4px 6px -4px hsl(0 0% 0% / 0.3);
    --shadow-xl: 0 20px 25px -5px hsl(0 0% 0% / 0.5), 0 8px 10px -6px hsl(0 0% 0% / 0.3);
    --shadow-colored: 0 4px 14px -2px hsl(244 100% 75% / 0.25);

    --sidebar-bg: 217 33% 17%;
    --sidebar-border: 215 28% 22%;
    --sidebar-active: 244 100% 75%;
    --sidebar-active-bg: 244 100% 75% / 0.12;
    --sidebar-hover: 215 28% 22%;

    --header-bg: 217 33% 17%;
    --header-border: 215 28% 22%;
    --header-shadow: 0 1px 3px hsl(0 0% 0% / 0.4);
  }
}
```

- [ ] **Step 2: Modificar `apps/web/src/index.css` para importar `tokens.css` en lugar de `colors.css`**

Editar `apps/web/src/index.css`:

- old_string:
```css
/* ========================================
   SISTEMA DE DISEÑO - HR INTRANET
   ======================================== */

/* Colores y tokens configurables — editar styles/colors.css para personalizar temas */
@import './styles/colors.css';
```

- new_string:
```css
/* ========================================
   VYNTIA — DESIGN SYSTEM
   ======================================== */

/* Tokens de marca — editar packages/design-tokens/tokens.json
   y reflejar en styles/tokens.css */
@import './styles/tokens.css';
```

- [ ] **Step 3: Eliminar `apps/web/src/styles/colors.css`**

Run:
```bash
git rm apps/web/src/styles/colors.css
ls apps/web/src/styles/
```

Expected: `tokens.css` (y solo eso, si no había otros archivos en `styles/`).

- [ ] **Step 4: Smoke test build frontend**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -10
cd ../..
```

Expected: `✓ built in Xs` sin errores. Si hay errores de tipo o referencias rotas, identifica el archivo culpable y arregla.

- [ ] **Step 5: Smoke test vitest**

Run:
```bash
cd apps/web
npm test -- --run --reporter=basic 2>&1 | tail -8
cd ../..
```

Expected: mismo baseline (7 passed, 1 file load-failure pre-existente).

- [ ] **Step 6: Commit**

Run:
```bash
git add apps/web/src/styles/ apps/web/src/index.css
git commit -m "chore(L1): replace colors.css with VYNTIA tokens.css (#6C63FF + Inter)"
```

---

## Task 10: Actualizar `apps/web/tailwind.config.js` (Inter como font default)

**Files:**
- Modify: `apps/web/tailwind.config.js`

**Por qué:** El config actual usa `Lexend`/`Source Sans 3`. Spec L1 manda Inter como font único.

- [ ] **Step 1: Editar `apps/web/tailwind.config.js`**

Localiza el bloque `fontFamily`:

- old_string:
```js
  		fontFamily: {
  			sans:    ['Source Sans 3', 'system-ui', 'sans-serif'],
  			heading: ['Lexend',         'system-ui', 'sans-serif'],
  		},
```
- new_string:
```js
  		fontFamily: {
  			sans:    ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
  			heading: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
  		},
```

- [ ] **Step 2: Smoke test build**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -5
cd ../..
```

Expected: build verde.

- [ ] **Step 3: Commit**

Run:
```bash
git add apps/web/tailwind.config.js
git commit -m "chore(L1): switch tailwind fontFamily to Inter for VYNTIA brand"
```

---

## Task 11: Actualizar `apps/web/index.html` (Inter, title, meta, lang)

**Files:**
- Modify: `apps/web/index.html`

- [ ] **Step 1: Reemplazar `apps/web/index.html` completo**

Sobrescribir con:

```html
<!doctype html>
<html lang="es-PE">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vyntia-logo.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="VYNTIA — SaaS modular de gestión de Recursos Humanos para Perú. Donde el talento se convierte en valor." />
    <meta name="theme-color" content="#6C63FF" />
    <title>VYNTIA</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 2: Verificar que el favicon path usado existe (lo creamos en Task 13)**

Por ahora `/vyntia-logo.svg` no existe. Si `npm run dev` lanzara, vería 404 del favicon — eso es OK, no rompe nada. Lo creamos en Task 13.

- [ ] **Step 3: Smoke test build**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -5
cd ../..
```

Expected: build verde (Vite no falla por favicons faltantes).

- [ ] **Step 4: Commit**

Run:
```bash
git add apps/web/index.html
git commit -m "chore(L1): rebrand index.html to VYNTIA with Inter font and theme-color"
```

---

## Task 12: Renombrar `apps/web/package.json` `name` a `vyntia-web`

**Files:**
- Modify: `apps/web/package.json`

- [ ] **Step 1: Editar `apps/web/package.json` líneas 2-4**

- old_string:
```json
  "name": "hr-intranet-system",
  "private": true,
  "version": "1.0.0",
```
- new_string:
```json
  "name": "vyntia-web",
  "private": true,
  "version": "0.1.0",
```

- [ ] **Step 2: Reinstalar workspaces (npm puede haber cacheado el nombre viejo)**

Run desde la raíz:
```bash
npm install
npm ls --workspaces --depth=0
```

Expected: lista incluye `vyntia-web@0.1.0` y `@vyntia/design-tokens@0.1.0`.

- [ ] **Step 3: Verificar que `npm run dev:web` desde raíz aún funciona**

Run desde la raíz:
```bash
npm run dev:web 2>&1 &
DEV_PID=$!
sleep 8
kill $DEV_PID 2>/dev/null || true
```

Expected: dentro de 8s aparece `VITE vX.X.X ready in Xms` y `Local: http://localhost:XXXX/`.

- [ ] **Step 4: Commit**

Run:
```bash
git add apps/web/package.json package-lock.json
git commit -m "chore(L1): rename apps/web npm package to vyntia-web"
```

---

## Task 13: Crear logo VYNTIA placeholder (SVG)

**Files:**
- Create: `apps/web/public/vyntia-logo.svg`
- Create: `apps/web/src/components/brand/VyntiaLogo.tsx`
- Create: `apps/web/src/components/brand/VyntiaWordmark.tsx`

**Por qué:** Necesitamos un asset funcional para el favicon e iconos del sidebar. El logo definitivo vendrá del diseño profesional — esto es placeholder con la estética del brand kit (nodos+curvas, geométrico, violeta).

- [ ] **Step 1: Crear `apps/web/public/vyntia-logo.svg`**

Crear archivo con contenido exacto (placeholder geométrico — círculo + nodos conectados):

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" role="img" aria-label="VYNTIA logo">
  <defs>
    <linearGradient id="vyntiaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6C63FF" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="14" fill="url(#vyntiaGrad)" />
  <g fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round">
    <circle cx="20" cy="20" r="3.2" fill="#FFFFFF" stroke="none" />
    <circle cx="44" cy="20" r="3.2" fill="#FFFFFF" stroke="none" />
    <circle cx="32" cy="44" r="3.2" fill="#FFFFFF" stroke="none" />
    <path d="M20 20 Q32 8 44 20" />
    <path d="M44 20 Q50 36 32 44" />
    <path d="M32 44 Q14 36 20 20" />
  </g>
</svg>
```

- [ ] **Step 2: Crear `apps/web/src/components/brand/VyntiaLogo.tsx`**

Crear archivo:

```tsx
import { cn } from '@/lib/utils'

interface VyntiaLogoProps {
  readonly className?: string
  readonly size?: number
}

/**
 * VYNTIA logo (placeholder geometric mark — nodos conectados + violeta).
 * Definitive logo will replace this once branding deliverables arrive.
 */
export function VyntiaLogo({ className, size = 32 }: VyntiaLogoProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label="VYNTIA logo"
      className={cn('flex-shrink-0', className)}
    >
      <defs>
        <linearGradient id="vyntiaLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#6C63FF" />
          <stop offset="100%" stopColor="#3B82F6" />
        </linearGradient>
      </defs>
      <rect width="64" height="64" rx="14" fill="url(#vyntiaLogoGrad)" />
      <g fill="none" stroke="#FFFFFF" strokeWidth={2.4} strokeLinecap="round">
        <circle cx={20} cy={20} r={3.2} fill="#FFFFFF" stroke="none" />
        <circle cx={44} cy={20} r={3.2} fill="#FFFFFF" stroke="none" />
        <circle cx={32} cy={44} r={3.2} fill="#FFFFFF" stroke="none" />
        <path d="M20 20 Q32 8 44 20" />
        <path d="M44 20 Q50 36 32 44" />
        <path d="M32 44 Q14 36 20 20" />
      </g>
    </svg>
  )
}
```

- [ ] **Step 3: Crear `apps/web/src/components/brand/VyntiaWordmark.tsx`**

Crear archivo:

```tsx
import { cn } from '@/lib/utils'
import { VyntiaLogo } from './VyntiaLogo'

interface VyntiaWordmarkProps {
  readonly className?: string
  readonly logoSize?: number
  readonly hideText?: boolean
}

/**
 * VYNTIA wordmark — logo + nombre. Usado en sidebar header y login.
 */
export function VyntiaWordmark({
  className,
  logoSize = 32,
  hideText = false,
}: VyntiaWordmarkProps) {
  return (
    <div className={cn('flex items-center gap-2 min-w-0', className)}>
      <VyntiaLogo size={logoSize} />
      {!hideText && (
        <span className="text-lg sm:text-xl font-bold tracking-tight text-foreground truncate">
          VYNTIA
        </span>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Verificar build compila**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -5
cd ../..
```

Expected: build verde.

- [ ] **Step 5: Commit**

Run:
```bash
git add apps/web/public/vyntia-logo.svg apps/web/src/components/brand/
git commit -m "chore(L1): add VYNTIA logo placeholder and brand components"
```

---

## Task 14: Aplicar wordmark VYNTIA en `Sidebar.tsx`

**Files:**
- Modify: `apps/web/src/components/layout/Sidebar.tsx`

- [ ] **Step 1: Editar el bloque del header del sidebar (líneas ~512-528)**

Localiza:

```tsx
        {/* Header */}
        <div className="flex items-center justify-between p-3 sm:p-4 border-b border-sidebar-border">
          <div className="flex items-center space-x-2 min-w-0">
            <div className="flex items-center justify-center w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-primary/10">
              <Building2 className="w-5 h-5 sm:w-6 sm:h-6 text-primary flex-shrink-0" />
            </div>
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-lg sm:text-xl font-bold text-foreground truncate">HR Sistema</span>
                {user && (
                  <Badge variant={isAdminOrRRHH() ? 'default' : 'secondary'} className="text-[10px] mt-0.5 w-fit">
                    {isAdminOrRRHH() ? 'Administrador' : 'Personal'}
                  </Badge>
                )}
              </div>
            )}
          </div>
```

Y reemplaza el bloque `<div className="flex items-center space-x-2 min-w-0">...</div>` (líneas 514-528) con:

```tsx
          <div className="flex items-center gap-2 min-w-0">
            <VyntiaLogo size={isCollapsed ? 32 : 36} className="flex-shrink-0" />
            {!isCollapsed && (
              <div className="flex flex-col min-w-0">
                <span className="text-lg sm:text-xl font-bold tracking-tight text-foreground truncate">
                  VYNTIA
                </span>
                {user && (
                  <Badge variant={isAdminOrRRHH() ? 'default' : 'secondary'} className="text-[10px] mt-0.5 w-fit">
                    {isAdminOrRRHH() ? 'Administrador' : 'Personal'}
                  </Badge>
                )}
              </div>
            )}
          </div>
```

- [ ] **Step 2: Añadir el import en la cabecera del archivo**

En el bloque de imports (~línea 10-12), añade:

```tsx
import { VyntiaLogo } from '@/components/brand/VyntiaLogo'
```

- [ ] **Step 3: Eliminar el import de `Building2` si ya no se usa en el archivo**

Run:
```bash
grep -c "Building2" apps/web/src/components/layout/Sidebar.tsx
```

Si el resultado es `1` (solo el import), quitar `Building2` del bloque de lucide-react imports en `Sidebar.tsx`.

Si el resultado es `2+`, dejar el import (sigue usándose en algún otro lugar).

- [ ] **Step 4: Smoke test build**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -8
cd ../..
```

Expected: build verde.

- [ ] **Step 5: Commit**

Run:
```bash
git add apps/web/src/components/layout/Sidebar.tsx
git commit -m "chore(L1): replace sidebar 'HR Sistema' wordmark with VYNTIA logo"
```

---

## Task 15: Actualizar copy en `LoginForm.tsx`

**Files:**
- Modify: `apps/web/src/components/auth/LoginForm.tsx`

**Por qué:** "Acceso Seguro RRHH" se preserva el término RRHH (legítimo dominio peruano), pero el contexto pasa a hablar de VYNTIA. También cambiar el headline para reflejar la propuesta de valor de la marca.

- [ ] **Step 1: Editar la sección de marketing del login (líneas ~195-220)**

Localiza:
```tsx
        <section className="hidden rounded-3xl border border-slate-700/60 bg-slate-900/65 p-10 text-slate-100 shadow-2xl backdrop-blur-md lg:block">
          <div className="inline-flex items-center gap-2 rounded-full bg-cyan-400/20 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-200">
            <ShieldCheck className="h-3.5 w-3.5" />
            Acceso Seguro RRHH
          </div>
          <h1 className="mt-5 text-4xl font-black leading-tight text-white">
            Controla planillas, legajos y procesos laborales en un solo portal.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-300">
            Administra remuneraciones, vacaciones y documentación del personal con trazabilidad y permisos por rol.
          </p>
```

Reemplazar `Acceso Seguro RRHH`, `<h1>` y `<p>` con:

```tsx
        <section className="hidden rounded-3xl border border-slate-700/60 bg-slate-900/65 p-10 text-slate-100 shadow-2xl backdrop-blur-md lg:block">
          <div className="inline-flex items-center gap-2 rounded-full bg-[#6C63FF]/20 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-[#A5A0FF]">
            <ShieldCheck className="h-3.5 w-3.5" />
            VYNTIA · Acceso seguro
          </div>
          <h1 className="mt-5 text-4xl font-black leading-tight text-white">
            Donde el talento se convierte en valor.
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-relaxed text-slate-300">
            VYNTIA conecta a tu equipo con datos, decisiones y procesos de RRHH en una sola plataforma.
          </p>
```

- [ ] **Step 2: Smoke test build**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -5
cd ../..
```

Expected: verde.

- [ ] **Step 3: Commit**

Run:
```bash
git add apps/web/src/components/auth/LoginForm.tsx
git commit -m "chore(L1): rebrand LoginForm copy to VYNTIA value proposition"
```

---

## Task 16: Actualizar referencias a `intranet` y `config.*` en docs

**Files:**
- Modify: `D:/VYNTIA/CLAUDE.md`
- Modify: `D:/VYNTIA/README.md`
- Modify: `D:/VYNTIA/docs/QUICKSTART.md`
- Modify: `apps/api/README.md`
- Modify: `apps/api/SETUP.md`
- Modify: `apps/api/DEPLOYMENT.md`

**Por qué:** Spec L1: "Todos los `.md` actualizan referencias INTRANET → VYNTIA". También los comandos en docs deben reflejar `vyntia.settings.*` en lugar de `config.settings.*`.

- [ ] **Step 1: `D:/VYNTIA/CLAUDE.md`**

Cambios puntuales (ejecutar uno por uno con Edit):

a) Estructura del repo:
- old_string: `│   ├── api/              # Django 4.2 + DRF backend (was D:\INTRANET\back\)`
- new_string: `│   ├── api/              # Django 4.2 + DRF backend`
- old_string: `│   │   ├── config/       # settings module — rename to vyntia/ in L1`
- new_string: `│   │   ├── vyntia/       # settings module (renamed from config/ in L1)`
- old_string: `│   └── web/              # React 18 + TS + Vite frontend (was D:\INTRANET\front\)`
- new_string: `│   └── web/              # React 18 + TS + Vite frontend`

b) Comandos:
- replace_all: `config.settings.development` → `vyntia.settings.development`
- replace_all: `config.settings.testing` → `vyntia.settings.testing`

c) Sección Database:
- old_string: ``PostgreSQL `bd_rrhh_intranet` on localhost:5432 (legacy). Override via env: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.``
- new_string: ``PostgreSQL `bd_vyntia` on localhost:5432. Legacy `bd_rrhh_intranet` left intact for reference. Override via env: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.``

d) Sección "L1 plan":
- old_string: ``**L1 plan:** rename `config/` → `vyntia/`, settings module → `vyntia.settings.*`.``
- new_string: ``**L1 done:** module renamed to `vyntia/`, settings module is `vyntia.settings.*`.``

e) Setup section — `pip install -r apps/api/requirements.txt`:
- old_string: `pip install -r apps/api/requirements.txt`
- new_string: `pip install -e "apps/api[dev]"`

f) Sección "L0/L1 status" (al final):
- old_string: `- L1 ⏳ Rebrand superficial (BD `bd_vyntia`, `config/`→`vyntia/`, design tokens VYNTIA, Inter font)`
- new_string: `- L1 ✅ Rebrand superficial done (BD `bd_vyntia`, `config/`→`vyntia/`, design tokens VYNTIA, Inter font)`

Después de las ediciones, verifica:
```bash
grep -in "config\.settings\|bd_rrhh_intranet\|D:.INTRANET" D:/VYNTIA/CLAUDE.md
```

Expected: cero matches (excepto la referencia legítima a la BD legacy en la sección Database, que ya no debería aparecer).

- [ ] **Step 2: `D:/VYNTIA/README.md`**

a) Setup backend:
- old_string:
```
### Backend
```bash
cd apps/api
python -m venv ../../.venv
source ../../.venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt
python manage.py migrate --settings=config.settings.development
python manage.py runserver --settings=config.settings.development
```
```
- new_string:
```
### Backend
```bash
cd apps/api
python -m venv ../../.venv
source ../../.venv/Scripts/activate  # Windows Git Bash
pip install -e ".[dev]"
python manage.py migrate --settings=vyntia.settings.development
python manage.py runserver --settings=vyntia.settings.development
```
```

b) Estado del proyecto:
- old_string:
```
VYNTIA está en migración desde el proyecto INTRANET previo. Ver
`docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
para el plan completo.

**Capa actual:** L0 — Bootstrap del monorepo.
```
- new_string:
```
VYNTIA está en migración desde un repo intranet legacy. Ver
`docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md`
para el plan completo.

**Capa actual:** L1 — Rebrand superficial. Próximo: L2 — Django 5 upgrade.
```

- [ ] **Step 3: `D:/VYNTIA/docs/QUICKSTART.md`**

Este es legacy del repo viejo. El cambio mínimo es reemplazar paths:

- replace_all en el archivo: `d:\INTRANET` → `d:\VYNTIA` (case-insensitive — ojo: hacer dos pasadas por `d:\INTRANET` y `D:\INTRANET`)
- replace_all: `D:\INTRANET` → `D:\VYNTIA`
- replace_all: `bd_rrhh_intranet` → `bd_vyntia`
- replace_all: `RRHH Intranet` → `VYNTIA`

Tras los reemplazos, verificar:
```bash
grep -in "INTRANET\|bd_rrhh_intranet" D:/VYNTIA/docs/QUICKSTART.md || echo "OK: limpio"
```

Si hay residuos legítimos (links a documentos legacy), déjalos; el grep solo debe surface menciones legítimas.

- [ ] **Step 4: `apps/api/README.md`, `SETUP.md`, `DEPLOYMENT.md`**

Para cada archivo, ejecutar replace_all:
- `config.settings.development` → `vyntia.settings.development`
- `config.settings.testing` → `vyntia.settings.testing`
- `config.settings.production` → `vyntia.settings.production`
- `config.settings.staging` → `vyntia.settings.staging`
- `config.wsgi` → `vyntia.wsgi`
- `config.urls` → `vyntia.urls`
- `bd_rrhh_intranet` → `bd_vyntia`
- `Intranet RRHH` → `VYNTIA`

Vía Bash:
```bash
for f in apps/api/README.md apps/api/SETUP.md apps/api/DEPLOYMENT.md; do
  sed -i \
    -e 's/config\.settings\.development/vyntia.settings.development/g' \
    -e 's/config\.settings\.testing/vyntia.settings.testing/g' \
    -e 's/config\.settings\.production/vyntia.settings.production/g' \
    -e 's/config\.settings\.staging/vyntia.settings.staging/g' \
    -e 's/config\.wsgi/vyntia.wsgi/g' \
    -e 's/config\.urls/vyntia.urls/g' \
    -e 's/bd_rrhh_intranet/bd_vyntia/g' \
    -e 's/Intranet RRHH/VYNTIA/g' \
    "$f"
done
```

Verificar:
```bash
grep -in "config\.settings\|bd_rrhh_intranet\|Intranet RRHH" apps/api/README.md apps/api/SETUP.md apps/api/DEPLOYMENT.md || echo "OK"
```

Expected: `OK`.

- [ ] **Step 5: Commit**

Run:
```bash
git add CLAUDE.md README.md docs/QUICKSTART.md apps/api/README.md apps/api/SETUP.md apps/api/DEPLOYMENT.md
git commit -m "docs(L1): update INTRANET→VYNTIA references and config→vyntia paths in docs"
```

---

## Task 17: Smoke tests finales y verificación de DoD

**Files:** ninguno (solo verificación)

- [ ] **Step 1: Backend `manage.py check`**

Run:
```bash
cd apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -3
cd ../..
```

Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 2: Backend pytest**

Run:
```bash
cd apps/api
pytest --tb=no -q 2>&1 | tail -5
cd ../..
```

Expected: **125 passed, 44 failed, 3 skipped** (baseline exacto).

- [ ] **Step 3: Frontend build**

Run:
```bash
cd apps/web
npm run build 2>&1 | tail -10
cd ../..
```

Expected: `✓ built in Xs`. Sin errores TS ni de Vite.

- [ ] **Step 4: Frontend test**

Run:
```bash
cd apps/web
npm test -- --run --reporter=basic 2>&1 | tail -8
cd ../..
```

Expected: 7 passed, 1 file load-failure (pre-existing). No nuevas regresiones.

- [ ] **Step 5: Frontend dev smoke (visual)**

Run desde la raíz:
```bash
npm run dev:web 2>&1 &
DEV_PID=$!
sleep 10
echo "Visit http://localhost:5173 in browser. Expected: VYNTIA wordmark in sidebar, violet primary, Inter font."
kill $DEV_PID 2>/dev/null || true
```

**Verificación visual** (manual): el dev server arranca, el browser carga `localhost:5173`, y la app muestra:
- Sidebar con logo violeta + texto "VYNTIA"
- Color primario violeta (#6C63FF) en botones, links, badges
- Font Inter (no Source Sans 3 ni Lexend)
- Login: copy "Donde el talento se convierte en valor." y pill "VYNTIA · Acceso seguro"

Si algo no se ve, anotar en checklist y diagnosticar antes de mergear.

- [ ] **Step 6: Verificación de greps de cleanup**

Run:
```bash
echo "=== A: imports config.* en código backend ==="
grep -rn "config\.settings\|config\.urls\|config\.wsgi\|config\.asgi" apps/api/ --include="*.py" --include="*.ini" --include="*.template" --include="*.example" --include="Makefile" --include="*.toml" || echo "OK: cero matches"

echo "=== B: marca legacy en frontend activo (excluyendo generated/) ==="
grep -rn "INTRANET\|HR Intranet\|HR Sistema\|hr-intranet" apps/web/src apps/web/index.html apps/web/package.json --include="*.ts" --include="*.tsx" --include="*.css" --include="*.html" --include="*.json" 2>/dev/null | grep -v "/generated/" || echo "OK: cero matches en código activo"

echo "=== C: DB legacy en docs/configs ==="
grep -rin "bd_rrhh_intranet" apps/api/ CLAUDE.md README.md docs/QUICKSTART.md --include="*.md" --include="*.template" --include="*.example" --include="*.py" --include="*.ini" 2>/dev/null || echo "OK: cero matches"
```

Expected: cada bloque termina con `OK: cero matches`.

Si alguno tiene matches, son trabajo pendiente de L1 — completarlos antes de seguir.

- [ ] **Step 7: Verificar git history y cleanup**

Run:
```bash
git log --oneline vyntia/L1-rebrand-surface ^master | head -25
git status --short
```

Expected:
- `git log`: ~12-15 commits con prefijos `chore(L1):` y `docs(L1):`
- `git status`: salida vacía

---

## Task 18: Merge a master (con autorización del usuario)

**Files:** ninguno

- [ ] **Step 1: Confirmar con el usuario antes de mergear**

Pregunta al usuario:
- ¿Mergear `vyntia/L1-rebrand-surface` a master ahora, o crear PR para review?
- Si quiere review, push: `git push -u origin vyntia/L1-rebrand-surface` y crear PR via `gh pr create`.
- Si autoriza merge directo local: continúa al Step 2.

**NO mergear sin autorización del usuario.**

- [ ] **Step 2: (Si autoriza) merge directo**

Run:
```bash
git checkout master
git merge vyntia/L1-rebrand-surface --no-ff -m "Merge L1: rebrand superficial (VYNTIA module + bd_vyntia + design tokens)"
git log --oneline -10
```

Expected: merge commit visible. Branch `vyntia/L1-rebrand-surface` puede borrarse si user lo confirma (`git branch -d vyntia/L1-rebrand-surface`).

- [ ] **Step 3: Verificar smoke test post-merge**

Run:
```bash
cd apps/api && pytest --tb=no -q 2>&1 | tail -3 && cd ../..
cd apps/web && npm run build 2>&1 | tail -3 && cd ../..
```

Expected: ambos verdes.

---

## Definition of Done — checklist final

Marcar cada item solo cuando esté verificado:

- [ ] `python manage.py check --settings=vyntia.settings.development` → `System check identified no issues`
- [ ] `pytest` desde `apps/api/` → exactamente 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `npm run build` desde `apps/web/` → `✓ built in Xs`
- [ ] `npm test -- --run` desde `apps/web/` → 7 passed (baseline preservado)
- [ ] `apps/api/vyntia/` existe; `apps/api/config/` ya NO existe
- [ ] `apps/api/pyproject.toml` existe; `apps/api/requirements.txt` ya NO existe
- [ ] `packages/design-tokens/tokens.json` con paleta VYNTIA y `npm ls --workspaces` lista `@vyntia/design-tokens`
- [ ] `apps/web/src/styles/tokens.css` existe; `colors.css` ya NO existe
- [ ] `apps/web/tailwind.config.js` usa Inter como `sans` y `heading`
- [ ] `apps/web/index.html` tiene `<title>VYNTIA</title>`, font Inter, theme-color `#6C63FF`
- [ ] `apps/web/package.json` `name` es `vyntia-web`
- [ ] Sidebar muestra `<VyntiaLogo />` + texto "VYNTIA" (no "HR Sistema")
- [ ] LoginForm copy menciona VYNTIA y slogan "Donde el talento se convierte en valor."
- [ ] BD `bd_vyntia` existe en Postgres con esquema migrado
- [ ] `.env.template` y `.env.example` apuntan a `bd_vyntia` y `vyntia.settings.development`
- [ ] `.gitignore` raíz tiene reglas restauradas (`.planning/`, `.claude/`, `.playwright-mcp/`, etc.)
- [ ] CLAUDE.md, README.md, docs/QUICKSTART.md, apps/api/{README,SETUP,DEPLOYMENT}.md sin referencias a `config.settings.*` ni `bd_rrhh_intranet`
- [ ] Branch `vyntia/L1-rebrand-surface` con ~12-15 commits `chore(L1):`/`docs(L1):`
- [ ] `git status` limpio
- [ ] (Opcional) Branch mergeada a master con autorización del user

---

## Después de L1

**Próximo plan:** L2 — Upgrade Django 4.2 → Django 5 (auditoría de paquetes terceros, ajuste de deprecaciones, `manage.py check --deploy` limpio).

Cuando termines L1:
1. Confirmar visualmente con el user (browser en `localhost:5173`) que el rebrand quedó bien.
2. Actualizar memoria del proyecto (MEMORY.md): mover L1 de "⏳" a "✅" en `active_subproject.md`, marcar known issue de `.gitignore` y UnicodeDecodeError como resueltos.
3. Solicitar generar el plan de L2 invocando `superpowers:writing-plans` con el sub-spec L2.

---

## Notas para el ejecutor

- **Cada task es atómica y commiteable.** Si algo sale mal en task N, `git reset --hard HEAD~1` y reintenta.
- **`runserver` NO es smoke test fiable** por el known issue de UnicodeDecodeError con DB_PASSWORD no-ASCII. Usar `manage.py check` para validar código y `pytest` (SQLite, no toca PG) para validar comportamiento.
- **Task 5 es la más riesgosa.** El `git mv config vyntia` debe ir acompañado de la actualización inmediata de TODAS las referencias antes del próximo `manage.py check`. Si se commitea sin actualizar, master queda roto.
- **No tocar `app_rrhh/*` internals.** Si encuentras strings "intranet" en `app_rrhh/services/` o models, déjalos — son scope L3. Solo brand strings visibles externamente (sidebar, login, swagger title) y módulo Django (`config/`) son scope L1.
- **Task 8 (crear BD) requiere password ASCII.** Si el user tiene `ñ` o similar en DB_PASSWORD del `.env`, el migrate fallará. Pedir al user actualizar la password ANTES de Task 8.
- **Windows Git Bash**: forward slashes `/` y `source .venv/Scripts/activate`.
- **shadcn UI components** consumen las variables CSS via Tailwind. Cambiar las variables en `tokens.css` actualiza automáticamente todos los componentes (Button, Card, Badge, etc.) sin tocar su código.
