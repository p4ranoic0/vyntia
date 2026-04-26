# VYNTIA Foundation L3.6 — Extract `documents` App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extraer los modelos del dominio documental (`DocumentosDigitales`, `PlantillaDocumento`) **y sus 3 services** (`pdf_generator.py`, `template_service.py`, `word_template_service.py`) desde `app_rrhh/` hacia una nueva Django app en `apps/api/apps/documents/`. Class names quedan en español — el rename a inglés (`DocumentosDigitales → DigitalDocument`, `PlantillaDocumento → DocumentTemplate`) es L3.10.

**Architecture:** L3.6 es **el primer sub-PR de L3 que mueve services**, no solo modelos. Los 3 services PDF/Word (`pdf_generator.py`, `template_service.py`, `word_template_service.py`) son el motor de generación de PDFs/Word del producto y dependen de `DocumentosDigitales` + `ContratosAdendas` (apps.contracts) + `Empleado` (apps.employees) + `Area` (apps.organization). El consumer principal de los services es `api/v1/app_rrhh/document_generation_views.py`. Patrón establecido en L3.2-L3.5: mover modelos, actualizar FK strings, NUCLEAR DB. Riesgo nuevo: re-wiring de service imports cruzados (`from app_rrhh.services import TemplateService` → `from apps.documents.services import TemplateService`). Sin cambio de AUTH_USER_MODEL ni split de modelos.

**Tech Stack:** Django 5.2 `AppConfig`, NUCLEAR DB strategy (validada en L3.2/L3.3/L3.4/L3.5), Django management commands para reseed.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django" sub-PR L3.6; § 3.2 "División de modelos"; § 3.3 "Mapeo de services" (3 services PDF/Word a `documents`)

**Scope decision (alineada con L3.1-L3.5 pattern):**
- Class names en español; rename a inglés es L3.10
- `empleado_report_service.py` queda en `app_rrhh/services/` — pertenece a `employees` app per spec § 3.3, pero L3.4 lo difirió. **NO se toca en L3.6**
- Manager `DocumentosDigitalesManager` en `app_rrhh/managers.py` está comentado (orphan code) — cleanup en L3.11

**Pre-condiciones:**
- L3.5 mergeada a master (commit `af405b85`)
- Django 5.2.13, `apps/api/apps/{core,identity,organization,employees,contracts}/` operativos
- pytest baseline: 125 passed, 44 failed, 3 skipped
- `bd_vyntia` provisionada con esquema actual; rol > 0, permiso > 0, modulos > 0
- venv en `D:/VYNTIA/.venv/`

**Definition of Done:**
- [ ] `apps/api/apps/documents/` existe con `apps.py`, `models/`, `services/`, `migrations/`
- [ ] Modelos `DocumentosDigitales`, `PlantillaDocumento` movidos a `apps/documents/models/`
- [ ] Services `pdf_generator.py`, `template_service.py`, `word_template_service.py` movidos a `apps/documents/services/`
- [ ] `app_rrhh/models/{documentos_digitales,plantilla_documento}.py` eliminados
- [ ] `app_rrhh/services/{pdf_generator,template_service,word_template_service}.py` eliminados
- [ ] `DocumentsConfig` en `LOCAL_APPS`
- [ ] **LR9 fix:** 3 stale FK strings `'app_rrhh.DocumentosDigitales'` actualizados a `'documents.DocumentosDigitales'`:
  - `apps/employees/models/datos_academicos.py:118`
  - `apps/employees/models/cursos_certificaciones.py:26`
  - `apps/organization/models/ubicacion.py:81`
- [ ] FK strings `'identity.Usuario'` y `'employees.Empleado'` y `'employees.DatosFamiliares'` dentro de modelos movidos preservados (ya correctos pre-move)
- [ ] **LR11 fix:** relative imports `from .models import` en `app_rrhh/{views,serializers,services.py,tests.py,managers.py,managers/}` actualizados a `from apps.documents.models import`
- [ ] `app_rrhh/services/__init__.py` ya no exporta `TemplateService`; nuevo re-export en `apps/documents/services/__init__.py`
- [ ] Imports `from app_rrhh.services import TemplateService` y `from app_rrhh.services.{pdf_generator,word_template_service} import X` actualizados
- [ ] Migraciones regeneradas: app_rrhh sin DocumentosDigitales/PlantillaDocumento; documents con ambos
- [ ] `bd_vyntia` recreada y reseeded (rol > 0, permiso > 0, modulos > 0)
- [ ] Imports actualizados across ~20 archivos (modelos + services)
- [ ] `pyproject.toml` `packages` incluye `"apps.documents"`
- [ ] `python manage.py check` clean
- [ ] `pytest`: 125 passed, 44 failed, 3 skipped (baseline preservado)
- [ ] `runserver` arranca y `/api/docs/` retorna 200
- [ ] Branch `vyntia/L3.6-documents-app` mergeada a master con `--no-ff`

---

## File Structure Overview

| Acción | Path | Notas |
|---|---|---|
| Create | `apps/api/apps/documents/__init__.py` | empty |
| Create | `apps/api/apps/documents/apps.py` | `DocumentsConfig(AppConfig)` con `name="apps.documents"`, `label="documents"` |
| Create | `apps/api/apps/documents/models/__init__.py` | re-exporta los 2 modelos |
| Create | `apps/api/apps/documents/services/__init__.py` | re-exporta los 3 services |
| Move | `app_rrhh/models/documentos_digitales.py` → `apps/api/apps/documents/models/documentos_digitales.py` | FKs salientes ya correctas (`'employees.Empleado'`, `'employees.DatosFamiliares'`, `'identity.Usuario'`) |
| Move | `app_rrhh/models/plantilla_documento.py` → `apps/api/apps/documents/models/plantilla_documento.py` | FK saliente ya correcta (`'identity.Usuario'`) |
| Move | `app_rrhh/services/pdf_generator.py` → `apps/api/apps/documents/services/pdf_generator.py` | Imports cross-app a actualizar; relative `.template_service` se preserva (mismo destino) |
| Move | `app_rrhh/services/template_service.py` → `apps/api/apps/documents/services/template_service.py` | Imports cross-app a actualizar |
| Move | `app_rrhh/services/word_template_service.py` → `apps/api/apps/documents/services/word_template_service.py` | Inline `from apps.contracts.models import ContratosAdendas` ya OK por L3.5 |
| Create | `apps/api/apps/documents/migrations/__init__.py` | empty |
| Modify | `apps/api/apps/employees/models/datos_academicos.py` | **LR9:** FK `'app_rrhh.DocumentosDigitales'` → `'documents.DocumentosDigitales'` (línea 118) |
| Modify | `apps/api/apps/employees/models/cursos_certificaciones.py` | **LR9:** FK `'app_rrhh.DocumentosDigitales'` → `'documents.DocumentosDigitales'` (línea 26) |
| Modify | `apps/api/apps/organization/models/ubicacion.py` | **LR9:** FK `'app_rrhh.DocumentosDigitales'` → `'documents.DocumentosDigitales'` (línea 81) |
| Modify | `apps/api/app_rrhh/models/__init__.py` | quitar `from .documentos_digitales import DocumentosDigitales`, `from .plantilla_documento import PlantillaDocumento`, y entries en `__all__` (`"DocumentosDigitales"`, `"PlantillaDocumento"`) |
| Modify | `apps/api/app_rrhh/services/__init__.py` | quitar `from .template_service import TemplateService` y entry en `__all__` |
| Modify | `apps/api/app_rrhh/models/onboarding.py` | inline import línea 103: `from app_rrhh.models.documentos_digitales import DocumentosDigitales` → `from apps.documents.models import DocumentosDigitales` |
| Modify | `apps/api/vyntia/settings/base.py` | añadir `"apps.documents.apps.DocumentsConfig"` a `LOCAL_APPS` (después de contracts, antes de app_rrhh) |
| Modify | `apps/api/pyproject.toml` | añadir `"apps.documents"` a `packages` |
| Modify (~17 files) | varios en `api/v1/`, `app_rrhh/{views,serializers,services.py,tests.py,managers.py,services/onboarding_service.py,services/empleado_report_service.py,management/commands/}`, `tests/` | replace `from app_rrhh.models import ... {DocumentosDigitales\|PlantillaDocumento}` → `from apps.documents.models import ...`. Replace `from app_rrhh.services import TemplateService` → `from apps.documents.services import TemplateService`. Replace `from app_rrhh.services.{pdf_generator,word_template_service} import X` → `from apps.documents.services import X`. **LR11:** incluir relative `from .models import` en archivos legacy `app_rrhh/*.py` |
| Delete | `app_rrhh/migrations/0001_initial.py` + `0002_initial.py` | regenerated |
| Delete | `apps/identity/migrations/0001_initial.py` | regenerated |
| Delete | `apps/organization/migrations/0001_initial.py` | regenerated |
| Delete | `apps/employees/migrations/0001_initial.py` (+ `0002_initial.py` si existe) | regenerated |
| Delete | `apps/contracts/migrations/0001_initial.py` + `0002_initial.py` | regenerated |

**NO se toca en L3.6:**
- Class names (rename a inglés es L3.10)
- Field names
- Frontend
- `empleado_report_service.py` (queda en app_rrhh — pertenece a employees app per spec § 3.3, deferred)
- Vacaciones (queda en app_rrhh hasta L3.8)
- Remuneracion + ConfiguracionUit (queda en app_rrhh hasta L3.7)
- OnboardingEmpleado modelo (queda en app_rrhh hasta L3.9; **PERO** sus inline imports a DocumentosDigitales se actualizan en este plan)
- Manager `DocumentosDigitalesManager` en `app_rrhh/managers.py` (orphan, cleanup en L3.11)

**Lecciones aplicadas (LR9-LR12) explícitamente:**
- **LR9:** 3 stale `'app_rrhh.DocumentosDigitales'` lazy-FK strings detectadas pre-move (heredadas de L3.4) en `apps/{employees,organization}/models/`. Sed bulk + verify.
- **LR10:** sed procesa **single + double quote** forms (`'X'` y `"X"`). Inventario pre-move muestra 0 double-quote refs a estos modelos pero el sed lo cubre por defensiva.
- **LR11:** Task 9 incluye step explícito de grep `from \.models import` en `app_rrhh/*.py` (no solo absoluto). **Pre-move grep result: 0 hits** — los archivos legacy `app_rrhh/{views,serializers,services,tests,managers}.py` no referencian DocumentosDigitales/PlantillaDocumento (post Phase-3 fix-up de L3.5). Step 10 se mantiene como **defensive check** para no introducir regresión.
- **LR12:** Task 12 secuencia es `drop → CREATE bd_vyntia → makemigrations → migrate` (no `drop → makemigrations → CREATE → migrate`). `makemigrations` requiere DB existente para `check_consistent_history`.

**Inventario de inbound FK strings (verificado pre-move, single + double quote):**

| Archivo | Línea | Pattern actual | Pattern post-L3.6 |
|---|---|---|---|
| `apps/employees/models/datos_academicos.py` | 118 | `'app_rrhh.DocumentosDigitales'` | `'documents.DocumentosDigitales'` |
| `apps/employees/models/cursos_certificaciones.py` | 26 | `'app_rrhh.DocumentosDigitales'` | `'documents.DocumentosDigitales'` |
| `apps/organization/models/ubicacion.py` | 81 | `'app_rrhh.DocumentosDigitales'` | `'documents.DocumentosDigitales'` |

(0 inbound FK strings desde modelos que se quedan en `app_rrhh` — verificado por grep `'DocumentosDigitales'\|"DocumentosDigitales"` que solo retorna __init__.py exports y migrations.)

**Inventario de imports a actualizar (verificado pre-move, ~17 archivos):**

| Archivo | Línea(s) | Pattern actual | Notas |
|---|---|---|---|
| `app_rrhh/models/onboarding.py` | 103 | inline submodule: `from app_rrhh.models.documentos_digitales import DocumentosDigitales` | replace path |
| `app_rrhh/services/onboarding_service.py` | 7 | multi-line block: `DocumentosDigitales,` | split |
| `app_rrhh/services/empleado_report_service.py` | 5 | single-line: `from app_rrhh.models import DocumentosDigitales` | replace módulo (note: este service queda en app_rrhh) |
| `app_rrhh/services/template_service.py` | 16 | single-line: `from app_rrhh.models import DocumentosDigitales` | **archivo se mueve a apps.documents/services/**; ajustar import a `from apps.documents.models import DocumentosDigitales` o relative `from ..models import DocumentosDigitales` (preferir relative since same-app) |
| `app_rrhh/services/pdf_generator.py` | 47 | single-line: `from app_rrhh.models import DocumentosDigitales` | **archivo se mueve**; mismo trato que template_service.py |
| `app_rrhh/management/commands/seed_plantillas_default.py` | 20 | single-line: `from app_rrhh.models import PlantillaDocumento` | replace módulo |
| `api/v1/rrhh/views.py` | 12 | multi-line block: `DocumentosDigitales,` | split |
| `api/v1/rrhh/serializers.py` | 9 | multi-line block: `from app_rrhh.models import (\n    ...\n    DocumentosDigitales,\n    ...\n)` | split |
| `api/v1/rrhh/contratos_serializers.py` | 15 | single-line: `from app_rrhh.models import DocumentosDigitales` | replace módulo |
| `api/v1/app_rrhh/document_generation_views.py` | 9-14 + 18-19 + 44 | multi-line block (DocumentosDigitales, PlantillaDocumento) + service imports `from app_rrhh.services import TemplateService`, `from app_rrhh.services.word_template_service import WordTemplateService`, `from app_rrhh.services.pdf_generator import PDFGenerator` (inline en función) | split + service path replace |
| `tests/test_documentos_digitales_onboarding.py` | 12 | single-line: `from app_rrhh.models import DocumentosDigitales` | replace módulo |
| `tests/test_documentos_model.py` | 11 | submodule path: `from app_rrhh.models.documentos_digitales import DocumentosDigitales` | replace path |
| `tests/test_contratos_integration.py` | 17 | single-line: `from app_rrhh.models import DocumentosDigitales` | replace módulo |
| `tests/test_onboarding_api.py` | 14 | single-line mixto: `from app_rrhh.models import DocumentosDigitales, OnboardingEmpleado` | split: keep OnboardingEmpleado en app_rrhh, mover DocumentosDigitales a apps.documents.models |
| `tests/test_pdf_generation.py` | 19 | service: `from app_rrhh.services.pdf_generator import PDFGenerator` | replace path |
| **LR11 — relative imports en app_rrhh/*.py (PRE-MOVE GREP RESULT: 0 hits)** | | | |
| `app_rrhh/views.py` | — | 0 refs a DocumentosDigitales/PlantillaDocumento (verificado pre-move) | N/A — Phase 3 fix-up de L3.5 dejó este archivo limpio |
| `app_rrhh/serializers.py` | — | 0 refs (verificado pre-move) | N/A |
| `app_rrhh/services.py` | — | 0 refs activos (solo 1 comment en línea 321) | N/A — comment legacy, irrelevante |
| `app_rrhh/tests.py` | — | 0 refs (verificado pre-move) | N/A |
| `app_rrhh/managers.py` | 537 | clase orphan `DocumentosDigitalesManager` (no usado) | N/A — orphan code, cleanup en L3.11 |
| `app_rrhh/urls.py` | 3-8 | `from app_rrhh.views import (...)` | views.py reload — sin cambios directos a urls.py |

Adicionales a verificar por grep durante ejecución (Task 9 Step 1 inventario):
- `app_rrhh/models.py` (flat shadow file — likely dead, but verify)
- `app_rrhh/serializers_optimized.py`
- `app_rrhh/managers/__init__.py`, `app_rrhh/managers/contratos_manager.py`

---

## Task 1: Pre-flight — branch, baseline, backup

- [ ] **Step 1: Confirmar pwd y master limpio post-L3.5**

```bash
cd D:/VYNTIA
pwd
git status --short
git log --oneline -3
```

Expected: HEAD = `e82c544a docs(L3.5): mark L3.5 merged, L3.6 as next` o más reciente. `git status` vacío excepto este plan untracked.

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
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/pg_dump.exe" -U postgres -h localhost -d bd_vyntia -F c -f /tmp/bd_vyntia_pre_L3.6.dump 2>&1 | tail -3
ls -lh /tmp/bd_vyntia_pre_L3.6.dump
```

Expected: dump ~250-500 KB.

- [ ] **Step 5: Crear branch L3.6**

```bash
git checkout -b vyntia/L3.6-documents-app
git status --short
```

---

## Task 2: Comitear el plan en la branch

```bash
cd D:/VYNTIA
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.6-documents.md
git commit -m "docs(L3.6): add documents app extraction plan"
```

---

## Task 3: Crear estructura `apps/documents/`

- [ ] **Step 1: Crear directorios + empty `__init__.py`**

```bash
cd D:/VYNTIA
mkdir -p apps/api/apps/documents/models
mkdir -p apps/api/apps/documents/services
mkdir -p apps/api/apps/documents/migrations
touch apps/api/apps/documents/__init__.py
touch apps/api/apps/documents/migrations/__init__.py
```

- [ ] **Step 2: Crear `apps/documents/apps.py`**

Use Write tool con contenido EXACTO:

```python
"""AppConfig for the `apps.documents` Django app — VYNTIA digital documents.

Owns the document-management entities of the HR system:
- DocumentosDigitales (digital file storage for employee records — DNI scans,
  diplomas, certificates, contracts as PDF, etc., with versioning, validation
  state, access control levels, and metadata for SUNAT/legal compliance)
- PlantillaDocumento (Word .docx templates with {{PLACEHOLDER}} markers used
  to generate certificates, constancias, contracts, and adendas)

Owned services (PDF/Word generation engines):
- pdf_generator.py — chain xhtml2pdf → WeasyPrint → ReportLab fallback
- template_service.py — HTML template rendering for PDF output
- word_template_service.py — python-docx based .docx generation

Bounded context boundary: documents owns the legajo digital and template
engines. Personal data lives in `apps.employees`. Contract data lives in
`apps.contracts`. Compensation data lives in `apps.payroll` (L3.7).

Future rename (deferred to L3.10):
- DocumentosDigitales → DigitalDocument
- PlantillaDocumento → DocumentTemplate
"""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = "apps.documents"
    label = "documents"
    verbose_name = "VYNTIA Documents"
```

- [ ] **Step 3: Crear placeholder `apps/documents/models/__init__.py`**

```python
"""Documents models — re-exports for backward-compatible imports.

Populated when models are physically moved.
"""
```

- [ ] **Step 4: Crear placeholder `apps/documents/services/__init__.py`**

```python
"""Documents services — re-exports for backward-compatible imports.

Populated when services are physically moved.
"""
```

---

## Task 4: Mover los 2 model files con `git mv`

- [ ] **Step 1: Defensive — kill stale Python procs**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*VYNTIA*"} | Stop-Process -Force -ErrorAction SilentlyContinue
```

- [ ] **Step 2: `git mv` los 2 archivos de modelos**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/models/documentos_digitales.py apps/api/apps/documents/models/documentos_digitales.py
git mv apps/api/app_rrhh/models/plantilla_documento.py apps/api/apps/documents/models/plantilla_documento.py
```

- [ ] **Step 3: `git mv` los 3 services**

```bash
cd D:/VYNTIA
git mv apps/api/app_rrhh/services/pdf_generator.py apps/api/apps/documents/services/pdf_generator.py
git mv apps/api/app_rrhh/services/template_service.py apps/api/apps/documents/services/template_service.py
git mv apps/api/app_rrhh/services/word_template_service.py apps/api/apps/documents/services/word_template_service.py
```

- [ ] **Step 4: Verificar layout**

```bash
ls apps/api/apps/documents/models/
ls apps/api/apps/documents/services/
ls apps/api/app_rrhh/models/documentos_digitales.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/models/plantilla_documento.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/pdf_generator.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/template_service.py 2>&1 || echo "OK: removed"
ls apps/api/app_rrhh/services/word_template_service.py 2>&1 || echo "OK: removed"
```

Expected: 2 model files + `__init__.py` en documents/models/. 3 service files + `__init__.py` en documents/services/. 5 originales removidos.

---

## Task 5: Verify FK strings DENTRO de los archivos movidos (no editar)

Los modelos `documentos_digitales.py` y `plantilla_documento.py` ya usan strings lazy correctas. No se requieren cambios internos. Verificar:

- [ ] **Step 1: Verificar FKs salientes de los 2 modelos**

```bash
cd D:/VYNTIA/apps/api
echo "=== Outbound FKs en documentos_digitales.py ==="
grep -n "ForeignKey" apps/documents/models/documentos_digitales.py
echo ""
echo "=== Outbound FKs en plantilla_documento.py ==="
grep -n "ForeignKey" apps/documents/models/plantilla_documento.py
echo ""
echo "=== Bare 'Empleado'/'Area'/'Usuario'/'DatosFamiliares' en documents/models/ — should be 0 ==="
grep -rn "'Empleado'\b\|\"Empleado\"\|'Area'\b\|\"Area\"\|'Usuario'\b\|\"Usuario\"\|'DatosFamiliares'\b\|\"DatosFamiliares\"" apps/documents/models/ --include="*.py" || echo "OK: cero"
cd ../..
```

Expected:
- Las FKs deben usar prefixed lazy strings: `'employees.Empleado'`, `'employees.DatosFamiliares'`, `'identity.Usuario'`. La FK `documento_padre` usa `'self'` (recursive) — eso queda igual.
- "OK: cero" para bare refs.

Si algún grep encuentra match sin prefix, **detener y corregir** antes de continuar.

---

## Task 6: Update FK strings entrantes en archivos de apps ya extraídas (LR9 fix)

**Files (3 stale `'app_rrhh.DocumentosDigitales'` heredados de L3.4):**
- Modify: `apps/api/apps/employees/models/datos_academicos.py:118`
- Modify: `apps/api/apps/employees/models/cursos_certificaciones.py:26`
- Modify: `apps/api/apps/organization/models/ubicacion.py:81`

**Por qué:** Después del move, `DocumentosDigitales` vive en `documents`. Las stale refs `'app_rrhh.DocumentosDigitales'` en otros apps son **LR9 candidates** y deben actualizarse a `'documents.DocumentosDigitales'`.

- [ ] **Step 1: Bulk replace ambas formas (single + double quote) — LR9 + LR10**

```bash
cd D:/VYNTIA/apps/api
find apps -type f -name "*.py" -not -path "*/__pycache__/*" -not -path "*/migrations/*" -not -path "*/documents/*" -print0 | xargs -0 sed -i \
  -e "s|'app_rrhh\.DocumentosDigitales'|'documents.DocumentosDigitales'|g" \
  -e 's|"app_rrhh\.DocumentosDigitales"|"documents.DocumentosDigitales"|g' \
  -e "s|'app_rrhh\.PlantillaDocumento'|'documents.PlantillaDocumento'|g" \
  -e 's|"app_rrhh\.PlantillaDocumento"|"documents.PlantillaDocumento"|g'
cd ../..
```

- [ ] **Step 2: Verificar updates (single + double quote, both models, LR9-style)**

```bash
cd D:/VYNTIA/apps/api
echo "=== documents.DocumentosDigitales refs (expected: 3) ==="
grep -rn "'documents\.DocumentosDigitales'\|\"documents\.DocumentosDigitales\"" apps --include="*.py"
echo ""
echo "=== Stale 'app_rrhh.DocumentosDigitales' anywhere (LR9) — should be 0 ==="
grep -rn "'app_rrhh\.DocumentosDigitales'\|\"app_rrhh\.DocumentosDigitales\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
echo ""
echo "=== Stale 'app_rrhh.PlantillaDocumento' anywhere — should be 0 ==="
grep -rn "'app_rrhh\.PlantillaDocumento'\|\"app_rrhh\.PlantillaDocumento\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: 3 hits `'documents.DocumentosDigitales'`. 0 stale `'app_rrhh.X'` refs.

- [ ] **Step 3: Bare-string sanity check (defensive)**

```bash
cd D:/VYNTIA/apps/api
echo "=== Bare 'DocumentosDigitales'/'PlantillaDocumento' (single + double) en TODOS los apps non-migrations ==="
grep -rn "'DocumentosDigitales'\b\|\"DocumentosDigitales\"\|'PlantillaDocumento'\b\|\"PlantillaDocumento\"" apps app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK: cero"
cd ../..
```

Expected: `OK: cero`. Si aparecen bare refs (sin app prefix), son inbound FK strings desde modelos que se quedan — debe detenerse y actualizar a `'documents.X'`.

---

## Task 7: Crear `apps/documents/models/__init__.py` con re-exports

Use Write tool en `apps/api/apps/documents/models/__init__.py`:

```python
"""Documents models — re-exports for backward-compatible imports."""

from .documentos_digitales import DocumentosDigitales
from .plantilla_documento import PlantillaDocumento

__all__ = [
    "DocumentosDigitales",
    "PlantillaDocumento",
]
```

- [ ] **Smoke parse check (app no registrada todavía hasta Phase 3)**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/documents/models/__init__.py').read()); print('OK parse')"
python -c "import ast; ast.parse(open('apps/documents/models/documentos_digitales.py').read()); print('OK parse')"
python -c "import ast; ast.parse(open('apps/documents/models/plantilla_documento.py').read()); print('OK parse')"
cd ../..
```

Expected: 3x `OK parse`.

---

## Task 8: Update services internos + `apps/documents/services/__init__.py`

Los 3 services se movieron en Task 4 pero sus imports internos referencian `app_rrhh.models`. Necesitan actualizarse para apuntar a `apps.documents.models` (o usar relative `..models`).

- [ ] **Step 1: Update `apps/documents/services/template_service.py:16`**

Use Edit tool:
- old_string: `from app_rrhh.models import DocumentosDigitales`
- new_string: `from apps.documents.models import DocumentosDigitales`

- [ ] **Step 2: Update `apps/documents/services/pdf_generator.py:47`**

Use Edit tool:
- old_string: `from app_rrhh.models import DocumentosDigitales`
- new_string: `from apps.documents.models import DocumentosDigitales`

- [ ] **Step 3: Verify `apps/documents/services/word_template_service.py:173` inline import**

Read líneas 170-180. La línea inline `from apps.contracts.models import ContratosAdendas` ya fue actualizada por L3.5 Phase 2 sed — verificar que sigue correcta.

```bash
grep -n "from apps.contracts.models import\|from app_rrhh\.models" apps/api/apps/documents/services/word_template_service.py
```

Expected: 1 hit `from apps.contracts.models import ContratosAdendas`. 0 hits de `app_rrhh.models`.

- [ ] **Step 4: Verify relative `.template_service` import en pdf_generator.py:50**

`pdf_generator.py` tiene `from .template_service import TemplateService` (relative). Esto sigue funcionando porque ambos archivos viven en `apps/documents/services/`.

```bash
grep -n "from \.template_service\|from .template_service" apps/api/apps/documents/services/pdf_generator.py
```

Expected: 1 hit `from .template_service import TemplateService`.

- [ ] **Step 5: Crear `apps/documents/services/__init__.py` con re-exports**

Use Write tool en `apps/api/apps/documents/services/__init__.py`:

```python
"""Documents services — re-exports for backward-compatible imports.

PDF/Word generation engines for the HR document workflow.
"""

from .pdf_generator import PDFGenerator
from .template_service import TemplateService
from .word_template_service import WordTemplateService

__all__ = [
    "PDFGenerator",
    "TemplateService",
    "WordTemplateService",
]
```

- [ ] **Step 6: Smoke parse check**

```bash
cd D:/VYNTIA/apps/api
python -c "import ast; ast.parse(open('apps/documents/services/__init__.py').read()); print('OK parse __init__')"
python -c "import ast; ast.parse(open('apps/documents/services/pdf_generator.py').read()); print('OK parse pdf_generator')"
python -c "import ast; ast.parse(open('apps/documents/services/template_service.py').read()); print('OK parse template_service')"
python -c "import ast; ast.parse(open('apps/documents/services/word_template_service.py').read()); print('OK parse word_template_service')"
cd ../..
```

Expected: 4x `OK parse`.

---

## Task 9: Bulk update absolute imports across the codebase

**Pattern A:** `from app_rrhh.models import {DocumentosDigitales|PlantillaDocumento}` → `from apps.documents.models import ...`. Y submodule paths.

**Pattern B:** `from app_rrhh.services import TemplateService` → `from apps.documents.services import TemplateService`. Y service submodule paths (`from app_rrhh.services.{pdf_generator,word_template_service} import X`).

- [ ] **Step 1: Inventario completo (incluye LR11 — relative imports en app_rrhh/)**

```bash
cd D:/VYNTIA/apps/api
echo "=== ABSOLUTE imports model (~13 expected) ==="
grep -rn "from app_rrhh\.models" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DocumentosDigitales|PlantillaDocumento|documentos_digitales|plantilla_documento" | sort
echo ""
echo "=== ABSOLUTE imports services (~4 expected) ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "TemplateService|PDFGenerator|WordTemplateService|template_service|pdf_generator|word_template_service" | sort
echo ""
echo "=== LR11: RELATIVE imports en app_rrhh/*.py — should mostly be relative .models ==="
grep -rn "from \.models import\|from \.services import" app_rrhh --include="*.py" \
  | grep -E "DocumentosDigitales|PlantillaDocumento|TemplateService|PDFGenerator|WordTemplateService" | sort
cd ../..
```

Expected: ~13 absolute model imports, ~4 absolute service imports, varios relative imports (LR11 candidates).

- [ ] **Step 2: Sed para imports puros models (single-import lines exactos)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/documents/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.models import \(DocumentosDigitales\)$|from apps.documents.models import \1|g' \
  -e 's|^from app_rrhh\.models import \(PlantillaDocumento\)$|from apps.documents.models import \1|g'
cd ../..
```

- [ ] **Step 3: Sed para inline imports en funciones (whitespace-prefix, both single + multiple)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/documents/*" \
  -print0 | xargs -0 sed -i -E \
  -e 's#^([[:space:]]+)from app_rrhh\.models import (DocumentosDigitales|PlantillaDocumento)$#\1from apps.documents.models import \2#g'
cd ../..
```

(NOTE: usa `#` como sed delimiter porque `|` colisiona con regex alternation — lección de L3.5.)

- [ ] **Step 4: Sed para submodule path imports models**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/documents/*" \
  -print0 | xargs -0 sed -i \
  -e 's|from app_rrhh\.models\.documentos_digitales import \(DocumentosDigitales\)|from apps.documents.models import \1|g' \
  -e 's|from app_rrhh\.models\.plantilla_documento import \(PlantillaDocumento\)|from apps.documents.models import \1|g'
cd ../..
```

Verify:
```bash
grep -rn "from app_rrhh\.models\.documentos_digitales\|from app_rrhh\.models\.plantilla_documento" apps/api --include="*.py" || echo "OK: cero"
```

- [ ] **Step 5: Sed para imports puros services (Pattern B)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/documents/*" \
  -print0 | xargs -0 sed -i \
  -e 's|^from app_rrhh\.services import \(TemplateService\)$|from apps.documents.services import \1|g' \
  -e 's|^from app_rrhh\.services\.pdf_generator import \(PDFGenerator\)$|from apps.documents.services import \1|g' \
  -e 's|^from app_rrhh\.services\.word_template_service import \(WordTemplateService\)$|from apps.documents.services import \1|g' \
  -e 's|^from app_rrhh\.services\.template_service import \(TemplateService\)$|from apps.documents.services import \1|g'
cd ../..
```

- [ ] **Step 6: Sed para inline imports services (whitespace-prefix)**

```bash
cd D:/VYNTIA/apps/api
find . -type f -name "*.py" \
  -not -path "*/migrations/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/apps/documents/*" \
  -print0 | xargs -0 sed -i -E \
  -e 's#^([[:space:]]+)from app_rrhh\.services\.pdf_generator import (PDFGenerator)$#\1from apps.documents.services import \2#g' \
  -e 's#^([[:space:]]+)from app_rrhh\.services\.word_template_service import (WordTemplateService)$#\1from apps.documents.services import \2#g' \
  -e 's#^([[:space:]]+)from app_rrhh\.services\.template_service import (TemplateService)$#\1from apps.documents.services import \2#g'
cd ../..
```

Specifically verify the inline service import in `api/v1/app_rrhh/document_generation_views.py:44`:
```bash
grep -n "from apps.documents.services\|from app_rrhh\.services" apps/api/api/v1/app_rrhh/document_generation_views.py
```

- [ ] **Step 7: Update inline submodule import en `app_rrhh/models/onboarding.py:103`**

Read context primero:
```bash
sed -n '100,108p' apps/api/app_rrhh/models/onboarding.py
```

Use Edit tool en `apps/api/app_rrhh/models/onboarding.py`:
- old_string: `        from app_rrhh.models.documentos_digitales import DocumentosDigitales`
- new_string: `        from apps.documents.models import DocumentosDigitales`

Verify:
```bash
grep -n "from apps.documents.models\|from app_rrhh\.models\.documentos_digitales" apps/api/app_rrhh/models/onboarding.py
```

Expected: 1 hit `from apps.documents.models import DocumentosDigitales`. 0 hits de submodule path.

- [ ] **Step 8: Manual fix para imports mezclados (single-line con coma)**

```bash
cd D:/VYNTIA/apps/api
grep -rn "from app_rrhh\.models import.*\(DocumentosDigitales\|PlantillaDocumento\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | head -30
cd ../..
```

Para cada match con coma:
- `api/v1/rrhh/contratos_serializers.py:15` quedó como single import después de L3.5 — verificar que no esté mezclado con otro modelo
- Si hay mixed-line, split en `from app_rrhh.models import <otros>` + `from apps.documents.models import <documentos>` (alfabético)

- [ ] **Step 9: Manual fix para imports multi-línea con parens**

```bash
cd D:/VYNTIA/apps/api
grep -rn -B 0 -A 12 "from app_rrhh\.models import (" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations 2>&1 | head -120
cd ../..
```

Para cada bloque que contenga `DocumentosDigitales` o `PlantillaDocumento`:
- Read file para ver bloque exacto
- Edit: remove la(s) línea(s) del bloque app_rrhh
- Add new line `from apps.documents.models import DocumentosDigitales[, PlantillaDocumento]` (alfabético)

Casos esperados (verificar con grep):
- `api/v1/rrhh/views.py:9-15` — DocumentosDigitales en bloque
- `api/v1/rrhh/serializers.py` — verificar bloque
- `api/v1/app_rrhh/document_generation_views.py:9-14` — bloque mixto con ambos models + DatosLaborales/ContratosAdendas que ya están en `apps.contracts`. Re-verify contents post-L3.5.
- `app_rrhh/services/onboarding_service.py:6-9` — bloque con DocumentosDigitales

- [ ] **Step 10: LR11 — Defensive check para relative imports `from .models import` en app_rrhh/*.py**

**Pre-move grep verificado: 0 hits.** Los archivos legacy `app_rrhh/{views,serializers,services.py,tests.py,managers.py}` no contienen relative imports a DocumentosDigitales/PlantillaDocumento (post Phase-3 fix-up de L3.5). Este step se mantiene como verificación defensiva — si aparecen hits inesperados, hay regresión a corregir.

```bash
cd D:/VYNTIA/apps/api
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "DocumentosDigitales|PlantillaDocumento" || echo "OK: cero (LR11 N/A para L3.6)"
cd ../..
```

Expected: `OK: cero (LR11 N/A para L3.6)`.

Si aparecen matches inesperados, son regresiones — para cada uno:
- Read context
- Edit: remove la(s) línea(s) del bloque relative
- Add new line `from apps.documents.models import DocumentosDigitales[, PlantillaDocumento]` (alfabético)
- Si el bloque relative queda vacío, eliminarlo entero

- [ ] **Step 11: Update `app_rrhh/services/__init__.py` — quitar export TemplateService**

Read current state:
```bash
cat apps/api/app_rrhh/services/__init__.py
```

Use Edit tool en `apps/api/app_rrhh/services/__init__.py`:
- old_string: `from .template_service import TemplateService\n`
- new_string: (línea borrada)

Y borrar `"TemplateService",` del `__all__`.

Use Edit tool segundo:
- old_string:
```python
    "VacationReportService",
    "TemplateService",
    "DescuentoMasivoService",
```
- new_string:
```python
    "VacationReportService",
    "DescuentoMasivoService",
```

Verify:
```bash
grep -n "TemplateService\|template_service" apps/api/app_rrhh/services/__init__.py || echo "OK: removed"
```

- [ ] **Step 12: Self-absolute import check en moved files**

```bash
cd D:/VYNTIA/apps/api
echo "=== Models self-absolute (should be cero o relative) ==="
grep -rn "from apps\.documents\.models import" apps/documents/models --include="*.py" || echo "OK: cero"
echo ""
echo "=== Services cross-imports (relative .template_service preserved) ==="
grep -rn "from \.template_service\|from .template_service\|from \.\.models" apps/documents/services --include="*.py"
echo ""
echo "=== Services to apps.documents.models (preferred over app_rrhh.models) ==="
grep -rn "from apps\.documents\.models\|from app_rrhh\.models" apps/documents/services --include="*.py"
cd ../..
```

Expected: services importan de `apps.documents.models` (o relative `..models` — ambos válidos). 0 imports de `app_rrhh.models`.

- [ ] **Step 13: Verificación final exhaustiva**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {documents-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DocumentosDigitales|PlantillaDocumento" || echo "OK"
echo ""
echo "=== B: from app_rrhh.models.documentos_digitales / .plantilla_documento ==="
grep -rn "from app_rrhh\.models\.documentos_digitales\|from app_rrhh\.models\.plantilla_documento" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== C: from .models import {documents-models} (LR11 — relative en app_rrhh) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "DocumentosDigitales|PlantillaDocumento" || echo "OK"
echo ""
echo "=== D: from app_rrhh.services import TemplateService / .pdf_generator / .word_template_service ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "TemplateService|PDFGenerator|WordTemplateService|template_service|pdf_generator|word_template_service" || echo "OK"
echo ""
echo "=== E: bare 'DocumentosDigitales'/'PlantillaDocumento' FK strings ANY app non-migrations ==="
grep -rn "'DocumentosDigitales'\b\|\"DocumentosDigitales\"\|'PlantillaDocumento'\b\|\"PlantillaDocumento\"" apps app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: stale 'app_rrhh.DocumentosDigitales' / 'app_rrhh.PlantillaDocumento' ANY (LR9) ==="
grep -rn "'app_rrhh\.DocumentosDigitales'\|'app_rrhh\.PlantillaDocumento'\|\"app_rrhh\.DocumentosDigitales\"\|\"app_rrhh\.PlantillaDocumento\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 10: Update `app_rrhh/models/__init__.py` — quitar exports

- [ ] **Step 1: Read current state**

```bash
grep -n "from .documentos_digitales\|from .plantilla_documento\|\"DocumentosDigitales\"\|\"PlantillaDocumento\"" apps/api/app_rrhh/models/__init__.py
```

- [ ] **Step 2: Use Edit tool — remove import lines**

Use Edit tool en `apps/api/app_rrhh/models/__init__.py`:
- old_string:
```python
from .documentos_digitales import DocumentosDigitales
from .onboarding import OnboardingEmpleado
from .plantilla_documento import PlantillaDocumento
```
- new_string:
```python
from .onboarding import OnboardingEmpleado
```

- [ ] **Step 3: Use Edit tool — remove `"DocumentosDigitales"` del `__all__`**

Use Edit tool:
- old_string:
```python
    "DocumentosDigitales",
```
- new_string: (línea borrada — usar contexto suficiente para uniqueness, o usar `replace_all` si solo aparece una vez)

Read primero para ver contexto exacto:
```bash
grep -n "DocumentosDigitales\|PlantillaDocumento" apps/api/app_rrhh/models/__init__.py
```

- [ ] **Step 4: Use Edit tool — remove `"PlantillaDocumento"` del `__all__`**

Probable bloque a editar (verificar contexto):
- old_string:
```python
    # Plantillas Word
    "PlantillaDocumento",
```
- new_string: (líneas borradas)

- [ ] **Step 5: Verificar limpieza**

```bash
grep -n "DocumentosDigitales\|PlantillaDocumento\|documentos_digitales\|plantilla_documento" apps/api/app_rrhh/models/__init__.py || echo "OK: removed"
```

Expected: `OK: removed`.

---

## Task 11: Update settings — registrar `DocumentsConfig`

Use Edit tool en `apps/api/vyntia/settings/base.py`:
- old_string:
```python
LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
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
    "app_rrhh",
]
```

Verify:
```bash
grep -A 8 "LOCAL_APPS = \[" apps/api/vyntia/settings/base.py
```

---

## Task 12: Update `pyproject.toml`

```bash
grep "packages" apps/api/pyproject.toml
```

Expected current: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts"]`

Use Edit tool en `apps/api/pyproject.toml`:
- old_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts"]`
- new_string: `packages = ["vyntia", "app_rrhh", "api", "apps", "apps.core", "apps.identity", "apps.organization", "apps.employees", "apps.contracts", "apps.documents"]`

Reinstall:
```bash
source D:/VYNTIA/.venv/Scripts/activate
cd D:/VYNTIA/apps/api
pip install -e ".[dev]" 2>&1 | tail -3
cd ../..
```

Expected: `Successfully installed vyntia-api-0.1.0`.

Smoke check (debería pasar tras Task 9 + 10 + 11 + 12):
```bash
cd D:/VYNTIA/apps/api
python manage.py check --settings=vyntia.settings.development 2>&1 | tail -5
cd ../..
```

Expected: `System check identified no issues (0 silenced).` Si falla con ImportError o RuntimeError, **investigar** — algún import o legacy file (LR11) no fue actualizado.

---

## Task 13: NUCLEAR DB regenerate (LR12 sequence: drop → CREATE → makemigrations → migrate)

**LR12:** El plan L3.5 ordenaba `makemigrations` antes de `CREATE DATABASE` y eso falló porque `check_consistent_history` requiere conexión. **L3.6 corrige el orden.**

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

cd D:/VYNTIA
```

NOTE: NO se borra `apps/documents/migrations/` (solo contiene `__init__.py` empty — primera migration genera en Step 4).

- [ ] **Step 4: Generar fresh migrations (DB ya existe per LR12)**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py makemigrations --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected:
- `Migrations for 'app_rrhh':` (sin DocumentosDigitales/PlantillaDocumento; con OnboardingEmpleado, Vacaciones, Remuneracion, ConfiguracionUit)
- `Migrations for 'identity':` (con Usuario, Rol, Permiso, etc.)
- `Migrations for 'organization':` (con Area, HistorialUbicaciones, ConfiguracionEmpresa)
- `Migrations for 'employees':` (con Empleado, DatosFamiliares, DatosAcademicos, CursosCertificaciones)
- `Migrations for 'contracts':` (con ContratosAdendas, DatosLaborales)
- `Migrations for 'documents':` con DocumentosDigitales, PlantillaDocumento — NEW
- Posibles `0002_initial.py` para FK ordering cross-app

Verify:
```bash
echo "=== documents 0001 (expected: 2 model definitions) ==="
grep -E "name='(DocumentosDigitales|PlantillaDocumento)'" apps/api/apps/documents/migrations/0001_initial.py | wc -l
echo "=== app_rrhh 0001 (expected: 0 documents models) ==="
grep -E "name='(DocumentosDigitales|PlantillaDocumento)'" apps/api/app_rrhh/migrations/0001_initial.py | wc -l
```

Expected: `2` y `0`.

- [ ] **Step 5: Aplicar migraciones**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py migrate --settings=vyntia.settings.development 2>&1 | tail -25
cd ../..
```

Expected: secuencia `Applying X.0001_initial... OK` para todos los apps. Sin errors. Tablas `documentos_digitales` y `app_rrhh_plantilla_documento` (per `Meta.db_table`) creadas en BD.

---

## Task 14: Re-seed (incluye plantillas si aplica)

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py setup_roles_permisos --settings=vyntia.settings.development 2>&1 | tail -10
PGPASSWORD='Demenci4@' python manage.py seed_menu --settings=vyntia.settings.development 2>&1 | tail -10
cd ../..
```

(El management command `seed_plantillas_default` requiere archivos `.docx` reales; no se ejecuta en CI/dev por defecto. Solo se ejecuta manualmente cuando se necesitan plantillas. Verificar que está disponible:)

```bash
cd D:/VYNTIA/apps/api
python manage.py help seed_plantillas_default --settings=vyntia.settings.development 2>&1 | tail -3
cd ../..
```

Expected: comando reconocido (sin error). NO ejecutar — solo verificar que el comando se descubre tras el move.

Verify counts:
```bash
PGPASSWORD='Demenci4@' "/c/Program Files/PostgreSQL/15/bin/psql.exe" -U postgres -h localhost -d bd_vyntia -c "SELECT 'rol' AS t, COUNT(*) FROM rol UNION ALL SELECT 'permiso', COUNT(*) FROM permiso UNION ALL SELECT 'modulos', COUNT(*) FROM modulos UNION ALL SELECT 'empleado', COUNT(*) FROM empleado UNION ALL SELECT 'contratos_adendas', COUNT(*) FROM contratos_adendas UNION ALL SELECT 'documentos_digitales', COUNT(*) FROM documentos_digitales UNION ALL SELECT 'app_rrhh_plantilla_documento', COUNT(*) FROM app_rrhh_plantilla_documento;" 2>&1 | tail -10
```

Expected: rol > 0, permiso > 0, modulos > 0, empleado = 0, contratos_adendas = 0, documentos_digitales = 0, app_rrhh_plantilla_documento = 0.

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

Si pytest divergir, **investigar** — puede ser un test legacy hardcoded a `app_rrhh.X` paths.

- [ ] **Step 2: runserver smoke**

```bash
cd D:/VYNTIA/apps/api
PGPASSWORD='Demenci4@' python manage.py runserver --settings=vyntia.settings.development > /tmp/runserver_l36.log 2>&1 &
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

- [ ] **Step 3: Cleanup greps finales (todos los patterns LR9-LR11)**

```bash
cd D:/VYNTIA/apps/api
echo "=== A: from app_rrhh.models import {documents-models} ==="
grep -rn "from app_rrhh\.models import" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "DocumentosDigitales|PlantillaDocumento" || echo "OK"
echo ""
echo "=== B: from .documentos_digitales / .plantilla_documento (relative en app_rrhh) ==="
grep -rn "from \.documentos_digitales\|from \.plantilla_documento" app_rrhh --include="*.py" || echo "OK"
echo ""
echo "=== C: same-app 'DocumentosDigitales'/'PlantillaDocumento' bare en app_rrhh non-migrations ==="
grep -rn "'DocumentosDigitales'\b\|\"DocumentosDigitales\"\|'PlantillaDocumento'\b\|\"PlantillaDocumento\"" app_rrhh --include="*.py" --exclude-dir=migrations || echo "OK"
echo ""
echo "=== D: app_rrhh.models.{documentos_digitales|plantilla_documento} submodule path ==="
grep -rn "app_rrhh\.models\.\(documentos_digitales\|plantilla_documento\)" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== E: stale 'app_rrhh.DocumentosDigitales' / 'app_rrhh.PlantillaDocumento' (LR9) ==="
grep -rn "'app_rrhh\.DocumentosDigitales'\|'app_rrhh\.PlantillaDocumento'\|\"app_rrhh\.DocumentosDigitales\"\|\"app_rrhh\.PlantillaDocumento\"" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations || echo "OK"
echo ""
echo "=== F: from app_rrhh.services import {documents-services} ==="
grep -rn "from app_rrhh\.services" --include="*.py" \
  --exclude-dir=__pycache__ --exclude-dir=migrations \
  | grep -E "TemplateService|PDFGenerator|WordTemplateService|template_service|pdf_generator|word_template_service" || echo "OK"
echo ""
echo "=== G: LR11 — from .models import {documents-models} (relative en app_rrhh) ==="
grep -rn "from \.models import" app_rrhh --include="*.py" \
  | grep -E "DocumentosDigitales|PlantillaDocumento" || echo "OK"
cd ../..
```

Expected: ALL `OK`.

---

## Task 16: Atomic commit

```bash
cd D:/VYNTIA
git status --short | head -50
git add apps/api/
git commit -m "chore(L3.6): extract documents app (DocumentosDigitales, PlantillaDocumento + 3 PDF/Word services) — fresh migrations after BD nuke + reseed"
```

Verificar:
```bash
git log --oneline vyntia/L3.6-documents-app ^master | head -5
git status --short
```

Expected: 2 commits (`docs(L3.6)` + `chore(L3.6)`), `git status` empty.

---

## Task 17: Merge a master

- [ ] **Step 1: Confirmar autorización del usuario.**

**NO mergear sin autorización.**

- [ ] **Step 2: Merge `--no-ff`**

```bash
git checkout master
git merge --no-ff vyntia/L3.6-documents-app -m "Merge L3.6: extract documents app (DocumentosDigitales, PlantillaDocumento + PDF/Word services)"
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

Update `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md` Status column: L3.6 → ✅ con merge SHA. L3.7 → ⏳ NEXT.

Commit:
```bash
git add docs/superpowers/plans/2026-04-25-vyntia-foundation-L3-master-roadmap.md
git commit -m "docs(L3.6): mark L3.6 merged, L3.7 as next in roadmap"
```

---

## Definition of Done — checklist final

- [ ] `apps/api/apps/documents/{__init__.py, apps.py, models/{__init__.py, documentos_digitales.py, plantilla_documento.py}, services/{__init__.py, pdf_generator.py, template_service.py, word_template_service.py}, migrations/{__init__.py, 0001_initial.py}}`
- [ ] `app_rrhh/models/{documentos_digitales, plantilla_documento}.py` removidos
- [ ] `app_rrhh/services/{pdf_generator, template_service, word_template_service}.py` removidos
- [ ] LR9 fix: 3 stale `'app_rrhh.DocumentosDigitales'` actualizados a `'documents.DocumentosDigitales'` (datos_academicos.py:118, cursos_certificaciones.py:26, ubicacion.py:81)
- [ ] LR11 fix: 5 archivos `app_rrhh/{views,serializers,services.py,tests.py,managers.py}` con relative `from .models import` actualizados
- [ ] Inline import `from app_rrhh.models.documentos_digitales import DocumentosDigitales` en `app_rrhh/models/onboarding.py:103` → `from apps.documents.models import DocumentosDigitales`
- [ ] `app_rrhh/services/__init__.py` ya no exporta `TemplateService`
- [ ] `apps/documents/services/__init__.py` exporta `PDFGenerator`, `TemplateService`, `WordTemplateService`
- [ ] LOCAL_APPS incluye `DocumentsConfig`; pyproject incluye `apps.documents`
- [ ] LR12 fix: makemigrations corrió DESPUÉS de CREATE DATABASE (no antes)
- [ ] Migrations regenerated; documents con 2 modelos; app_rrhh sin ellos
- [ ] bd_vyntia recreada; rol > 0, permiso > 0, modulos > 0, documentos_digitales = 0, app_rrhh_plantilla_documento = 0
- [ ] `manage.py check` clean; pytest 125/44/3; `/api/docs/` HTTP 200
- [ ] 0 stale `'app_rrhh.{DocumentosDigitales|PlantillaDocumento}'` strings (single + double-quote) anywhere (LR9)
- [ ] 0 bare `'DocumentosDigitales'`/`'PlantillaDocumento'` strings en `app_rrhh/` non-migrations (LR10 sed cubrió ambas formas)
- [ ] 0 relative `from .models import {DocumentosDigitales|PlantillaDocumento}` en `app_rrhh/*.py` (LR11)
- [ ] 0 `from app_rrhh.services import {TemplateService|PDFGenerator|WordTemplateService}` anywhere (Pattern B)
- [ ] Branch mergeada a master con `--no-ff`
- [ ] Memoria + roadmap actualizados post-merge: L3.6 ✅, L3.7 NEXT

---

## Después de L3.6

**Próximo plan:** L3.7 — extract `payroll` app (`Remuneracion` + 8 modelos relacionados, `ConfiguracionUit`, + services `planilla_calculo_service.py`, `descuento_masivo_service.py`).

L3.7 introduce más complejidad: el archivo `app_rrhh/models/remuneracion.py` define ~9 modelos (PlanillaMensual, BoletaPago, ConfiguracionAfp, ConceptoPlanilla, DetallePlanilla, DescuentoMasivo, CalendarioPago, ConfiguracionRemuneracion, etc.) que se mueven juntos. `services/planilla_calculo_service.py` será el primer service "computacional" (no solo PDF gen).

---

## Notas para el ejecutor

- **Patrón NUCLEAR + LR12 sequence** — drop → CREATE bd_vyntia → makemigrations → migrate. **NO** drop → makemigrations → CREATE → migrate.
- **PGPASSWORD env var** explícito por known issue (Windows env con caracteres no-ASCII).
- **Class names en español** — rename inglés en L3.10.
- **First sub-PR moviendo services** — los 3 services PDF/Word se mueven junto con sus modelos. Mantienen relative imports entre sí (`pdf_generator.py` → `from .template_service import TemplateService`).
- **`app_rrhh/services/__init__.py`** debe limpiarse (quitar TemplateService re-export).
- **`empleado_report_service.py` queda en app_rrhh** — pertenece a employees app per spec § 3.3 pero L3.4 lo difirió. Su import a `DocumentosDigitales` debe actualizarse en este plan a `from apps.documents.models import DocumentosDigitales`.
- **LR11 (relative imports en app_rrhh/*.py)** — la lección más importante de L3.5. Task 9 Step 10 dedicado.
- **LR9 (3 stale refs heredados)** — confirmados pre-move; Task 6 los arregla con sed bulk.
- **LR12 (sequence)** — Task 13 ordena CREATE DATABASE antes de makemigrations.
- **Manager `DocumentosDigitalesManager`** — está orphan en `app_rrhh/managers.py` (comentado), cleanup en L3.11.
- **Stale Python procs:** Si `psql DROP` falla con "in use", PowerShell kill primero.
- **`api/v1/app_rrhh/document_generation_views.py`** — el consumer principal de los services. Tiene tanto modelo imports como service imports — verificar que ambos se actualicen correctamente.
