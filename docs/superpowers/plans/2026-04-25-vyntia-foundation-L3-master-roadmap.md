# VYNTIA Foundation L3 — Master Roadmap

> **Este NO es un plan ejecutable.** Es un índice y orden de ejecución para los 11 sub-PRs que componen L3 (división de `app_rrhh` en bounded contexts). Cada sub-PR tiene su propio plan detallado en `docs/superpowers/plans/2026-04-25-vyntia-foundation-L3.X-<name>.md`.

**Spec de origen:** `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` § 4 "L3 — División de apps Django"

**Pre-condiciones (mismas para todos los sub-PRs):**
- L2 mergeado a master: commit `cbd2fb8f Merge L2: Django 4.2 → 5.2 LTS upgrade`
- Django 5.2.13 activo
- BD `bd_vyntia` provisionada (esquema `app_rrhh_*` actual)
- pytest baseline: 125 passed, 44 failed, 3 skipped

**Filosofía de ejecución:**
- Un sub-PR = una branch = un merge a master con `--no-ff`
- Cada sub-PR debe preservar el baseline pytest (125/44/3) post-merge
- Los planes detallados se generan **uno a la vez** — el siguiente plan se escribe DESPUÉS del merge del anterior, para incorporar lecciones del previo
- Si un sub-PR descubre que la división propuesta no funciona (ej. circular imports irresolvibles), se ajusta el plan del siguiente, no se rompe la regla de un-merge-por-sub-PR

---

## Estructura objetivo (al final de L3.11)

```
apps/api/
├── manage.py
├── pyproject.toml
├── vyntia/                              # Django settings (post-L1)
├── apps/                                # NUEVO en L3.1 — namespace de bounded contexts
│   ├── __init__.py
│   ├── core/                            # ← L3.1 (sin modelos: APIResponse, paginación, decorators, middleware)
│   ├── identity/                        # ← L3.2 (User, Role, Permission, auth)
│   ├── organization/                    # ← L3.3 (Department, Location, Company, SystemSetting)
│   ├── employees/                       # ← L3.4 (Employee, FamilyMember, AcademicRecord, Certification)
│   ├── contracts/                       # ← L3.5 (Contract + ContractAmendment, EmploymentData)
│   ├── documents/                       # ← L3.6 (DigitalDocument, DocumentTemplate, PDF generators)
│   ├── payroll/                         # ← L3.7 (Compensation, MonthlyPayroll, TaxParameter)
│   ├── time_off/                        # ← L3.8 (VacationRequest, VacationBalance, vacation services)
│   └── onboarding/                      # ← L3.9 (OnboardingProcess)
├── api/v1/
│   ├── identity/
│   ├── employees/
│   ├── contracts/
│   ├── documents/
│   ├── payroll/
│   ├── time-off/
│   └── onboarding/
├── tests/
└── (app_rrhh/ se elimina en L3.11)
```

---

## Sub-PR Index

| # | Sub-PR | Branch | Scope | Tasks (est.) | Riesgo | Dependencias | Status |
|---|---|---|---|---|---|---|---|
| L3.1 | `core` extraction | `vyntia/L3.1-core-app` | Mover `apps/api/core/` → `apps/api/apps/core/`, registrar como Django app, actualizar 33 import lines + 11 settings strings | ~10 | Bajo | — | ✅ merged `faa108a3` |
| L3.2 | `identity` app | `vyntia/L3.2-identity-app` | Crear `apps/api/apps/identity/`, mover `Usuario`/`Rol`/`Permiso`/`UsuarioRoles`/`RolPermisos`/`Modulos`/`ModuloPermiso` + `auth.py` + `UsuarioManager`. NUCLEAR DB: drop bd_vyntia + delete 27 migrations + regenerate fresh + reseed via management commands. Class names en español; rename a inglés es L3.10 | ~15 | Alto (AUTH_USER_MODEL change) | L3.1 | ✅ merged `7184e271` |
| L3.3 | `organization` app | `vyntia/L3.3-organization-app` | Mover `Area`/`HistorialUbicaciones`/`ConfiguracionEmpresa` a `apps/api/apps/organization/` con FKs lazy. Sistema ya estaba en identity (L3.2) | ~12 | Medio | L3.1, L3.2 | ✅ merged `36573111` |
| L3.4 | `employees` app | `vyntia/L3.4-employees-app` | Mover `Empleado`/`DatosFamiliares`/`DatosAcademicos`/`CursosCertificaciones` a `apps/api/apps/employees/`. 11 FK strings updated (incluye 1 con double-quote pescado). Stale `'app_rrhh.Empleado'` en identity/organization corregidos | ~18 | Alto (Empleado es el hub) | L3.1, L3.2, L3.3 | ✅ merged `2f71a8a0` |
| L3.5 | `contracts` app | `vyntia/L3.5-contracts-app` | Mover `ContratosAdendas`/`DatosLaborales` a `apps/api/apps/contracts/`. 2 inbound FKs actualizadas (vacaciones single-quote + remuneracion double-quote — LR10). 4 archivos legacy `app_rrhh/{views,serializers,services,tests}.py` con relative imports `from .models import` actualizados (LR11 nueva). Class names en español; split `→ Contract + ContractAmendment` y rename inglés diferidos a L3.10 | ~16 | Medio | L3.4 | ✅ merged `af405b85` |
| L3.6 | `documents` app | `vyntia/L3.6-documents-app` | Mover `DocumentosDigitales`/`PlantillaDocumento` + 3 services PDF/Word (`pdf_generator`, `template_service`, `word_template_service`). Primer sub-PR moviendo services. 3 stale `'app_rrhh.DocumentosDigitales'` heredados de L3.4 limpiados (LR9). LR12 sequence (CREATE DB before makemigrations) aplicada al primer intento. Stale logger string en test_pdf_generation.py:150 detectado y arreglado (LR13 nueva) | ~17 | Medio | L3.4 | ✅ merged `91581e7b` |
| L3.7 | `payroll` app | `vyntia/L3.7-payroll-app` | Mover 9 modelos en 2 archivos (`remuneracion.py` con 8: PlanillaMensual/DetallePlanilla/ConceptoPlanilla/ConfiguracionAfp/ConfiguracionRemuneracion/DescuentoMasivo/BoletaPago/CalendarioPago + `configuracion_uit.py` con ConfiguracionUit) + 2 services (`planilla_calculo`, `descuento_masivo`). Sub-PR más limpio hasta ahora: LR9/10/11/13 todas N/A confirmadas pre-move (0 incidencias). LR12 sequence aplicada al primer intento. Same-module FKs preservadas como class refs (no string lazy) | ~17 | Medio | L3.4 | ✅ merged `84ba7467` |
| L3.8 | `time_off` app | `vyntia/L3.8-timeoff-app` | Mover 5 modelos vacaciones + 5 services + active managers (`vacation_managers.py` movido como flat file `apps/time_off/managers.py`). LR11 fix real: 2 inline `from .models import SolicitudVacaciones` en `app_rrhh/validators.py:155,256`. LR14 nueva detectada: sed Pattern B no captura multi-line service blocks (views.py:14-19 pescado en code review). Split `VacationRequest`+`VacationBalance` deferido a L3.10 | ~18 | Alto (5 services + active managers) | L3.4 | ✅ merged `87420769` |
| L3.9 | `onboarding` app | `vyntia/L3.9-onboarding-app` | Mover `OnboardingEmpleado` (último modelo de dominio) + `services/onboarding_service.py` (con OnboardingService + OnboardingNotificationService). LR14 fix: 2 multi-line blocks `from app_rrhh.services.onboarding_service import (...)` en views.py:2449,2530. `from app_rrhh.tasks import send_email_html_task` preservado. **HITO: `app_rrhh/models/__init__.py` queda con `__all__ = []` — última extracción de dominio** | ~12 | Bajo | L3.4 | ✅ merged `8d9f575a` |
| L3.10 | Spanish → English rename | (split en 4 sub-PRs) | Aplicar spec § 3.2 + § 3.6 al codebase. Por scope (~30+ tasks, riesgo crítico) se descompuso en 4 sub-PRs ejecutables independientemente | — | **Crítico** | L3.1–L3.9 | ⏳ EN PROGRESO |
| L3.10.1 | Class names ES→EN | `vyntia/L3.10.1-rename-classes` | Renombrar 33 clases Python (Empleado→Employee, Usuario→User, etc.) + 17 archivos modelo (`git mv`) + 43 FK strings cross-app (single + double quote, LR10) + 170+ imports en consumers + AUTH_USER_MODEL=identity.User. Field names + `db_table` español PRESERVADOS. NUCLEAR DB regen con clases inglesas + tablas físicas españolas idénticas. **LR15 nueva**: `git mv` no actualiza imports relativos al nombre viejo (sed identifier-only no captura paths). **LR16 nueva**: rename de modelo cambia reverse-accessor auto-generado (`area_set`→`department_set`). 117 archivos cambiados (1988+/1956-) | ~21 | Medio | L3.9 | ✅ merged `7bccc348` |
| L3.10.2 | Audit fields + PKs + state literales ES→EN (Option B) | `vyntia/L3.10.2-rename-fields` | **Scope reducido** vs roadmap original: SOLO audit fields (54 — `fecha_creacion→created_at` etc), state literales (10 — `estado→status`, `activo→is_active`), PKs (31 → `id` UUID). **Domain vocabulary HR queda en español** (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `estado_empleado`, etc.) — extensión spec § 3.5 regla 7. Pytest **MEJORÓ** 125/44/3 → 161/8/3 (+36). Lecciones LR17-LR20 nuevas. 72 archivos, 848+/798- en commit principal | ~20 | Medio-alto | L3.10.1 | ✅ merged `a9ec4a80` |
| L3.10.3 | Contract split | `vyntia/L3.10.3-contract-split` | **Scope reducido (Option A)**: solo `Contract`→`Contract`+`ContractAmendment` (partition por tipo_documento). VacationRequest split DESCARTADO — VacationPeriod ya cumple rol de balance (spec § 3.2.1 clarification). 21 archivos cambiados (432+/178-). Pytest 161/8/3 baseline preservado al primer intento. LR21 nueva: model splits requieren update de consumers con choice lists hardcoded | ~15 | Medio (no data migration en bd_vyntia vacía — NUCLEAR regen) | L3.10.2 | ✅ merged `e7bcf132` |
| L3.10.4 | Frontend rename | (split en 4 sub-PRs: 4a + 4b + 4c + 4d) | URL refactor backend + frontend URL refactor + frontend field rename + frontend file renames. Dividido para reducir scope por PR | — | — | L3.10.3 | ⏳ EN PROGRESO |
| L3.10.4a | Backend URL refactor | `vyntia/L3.10.4a-backend-url-refactor` | Agregar URLs en inglés en paralelo con legacy: `/api/v1/identity/`, `/api/v1/employees/`, `/api/v1/contracts/`, `/api/v1/payroll/`, `/api/v1/time-off/`, etc. (8 nuevos URL configs). Legacy `/api/v1/rrhh/...` y `/api/v1/vacaciones/...` PRESERVADOS hasta L3.11. Estructura flat (no nested) por simplicidad DRF. Backend-only — no toca frontend | ~14 | Bajo | L3.10.3 | ✅ merged `4aeee01e` |
| L3.10.4b | Frontend URL refactor | `vyntia/L3.10.4b-frontend-url-refactor` | 19 archivos frontend (11 services + lib/api.ts + 4 features/onboarding + 4 pages/components) consumen las URLs nuevas en inglés. 230 URL refs replaced 1:1 (201 `/api/v1/rrhh/` + 29 `/api/v1/vacaciones/`). `/api/v1/auth/` preservado. Custom action suffixes (`renovar_contrato/`, `mi-onboarding/`, `aprobar_planilla/`, etc.) preservados verbatim. `/api/v1/documents/documents/` doble-prefix correcto. Field renames + file renames diferidos a L3.10.4c/4d. `generated/` no tocado | ~21 | Bajo | L3.10.4a | ✅ merged `8d3666e8` |
| L3.10.4c | Frontend field rename | `vyntia/L3.10.4c-frontend-field-rename` | TS interfaces alineadas con backend post-L3.10.2: `empleado_id: number` → `id: string` UUID, `fecha_creacion`→`created_at`, `fecha_actualizacion`→`updated_at`, `creado_por`→`created_by`, `estado`→`status`, `activo`→`is_active`. Domain HR vocabulary preservado en español (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, etc.). ~726 audit/PK refs + 179 state refs + 50 component refs | ~25 | Medio | L3.10.4b | ⏳ NEXT |
| L3.10.4d | Frontend file renames | `vyntia/L3.10.4d-frontend-file-renames` | `git mv contratosService.ts contractsService.ts`, `areasService.ts → departmentsService.ts`, `empresaService.ts → companyService.ts`, `vacacionesService.ts → timeOffService.ts`, `remuneracionesService.ts → payrollService.ts`, `plantillasService.ts → templatesService.ts`, `legajoService.ts` (preservado — domain term), `services/normalizers/rrhhNormalizers.ts → identityNormalizers.ts` (o split por dominio). 82 imports en consumers actualizados. `generated/api/services/` regenerado del schema actualizado | ~12 | Bajo | L3.10.4c | ⏳ |
| L3.11 | `app_rrhh` removal | `vyntia/L3.11-cleanup-app-rrhh` | Borrar carpeta vacía `apps/api/app_rrhh/`, actualizar URL raíz, eliminar redirects 301 que se pusieron en L3.2-L3.9. Cleanup de dead-code refs detectados durante L3.10.1 (`rol_set`, `permiso_set` en `app_rrhh/services.py:370` y `api/v1/rrhh/views.py:393`) | ~8 | Bajo | L3.10.4 | ⏳ |

**Estimación total:** 8–15 días working alone. Escala con interrupciones.

---

## Reglas duras (mismas que el spec, recordadas aquí)

1. **FK cross-app SOLO con string lazy**: `models.ForeignKey('employees.Employee', ...)`. Nunca `from apps.employees.models import Employee` desde otra app de dominio.
2. **Imports cross-app prohibidos**. Si una app necesita lógica de otra, va por **service public API** exportada en `apps/<other>/services/__init__.py`.
3. **`apps.core` NO depende de ninguna app de dominio** — solo es utilidad pura.
4. **Cada app tiene su propio** `urls.py`, `serializers.py`, `views/`, `services/`, `tests/`.
5. **Naming en inglés** (en L3.10) para todo el código Python y TypeScript. Strings UI en español. Términos legales peruanos preservados (DNI, RUC, CTS, PLAME, T-Registro, SUNAT).
6. **Test baseline 125/44/3** se preserva en cada merge a master. Si cambia, se diagnostica antes del merge.

---

## Patrón de migración por sub-PR (L3.2 a L3.9)

Cada sub-PR de extracción de modelos sigue esta plantilla. Los planes individuales detallan los pasos exactos.

1. **Pre-flight:** branch + baseline pytest
2. **Crear nueva app Django**: `apps/api/apps/<name>/` con `apps.py`, `__init__.py`, `models/__init__.py`, `migrations/__init__.py`, `tests/__init__.py`
3. **Registrar en INSTALLED_APPS** (`vyntia/settings/base.py`)
4. **Mover modelos**: `git mv apps/api/app_rrhh/models/<file>.py apps/api/apps/<name>/models/<file>.py`
5. **Actualizar `app_rrhh/models/__init__.py`** para que ya no exporte los modelos movidos
6. **Generar migration de movimiento**: Django soporta `--rename-app` indirectamente vía `db_table` lock + `Meta.app_label`. Se usa `migrations.SeparateDatabaseAndState` para mover el modelo lógicamente sin alterar la tabla física (que mantiene su nombre original)
7. **Cambiar FKs cross-app a string lazy**: `'employees.Employee'` en lugar de `Empleado` directo
8. **Mover serializers/views/services** asociados a la nueva app
9. **Mantener URL legacy** vía wildcard redirect 301 en `vyntia/urls.py` (`/api/v1/rrhh/empleados/` → `/api/v1/employees/`)
10. **Smoke tests**: pytest baseline + manage.py check + runserver smoke
11. **Commit + merge**

---

## Riesgos transversales L3

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|:---:|:---:|---|
| LR1 | Circular imports al separar apps | Alta | Medio | FK string lazy + service public API. Cada plan incluye grep de `from apps.X import` cruzados |
| LR2 | Migración `RenameModel` rompe BD | Media | Alto | Usar `SeparateDatabaseAndState` para que la tabla física no cambie, solo el state lógico de Django. Test rollback antes de aplicar a `bd_vyntia` |
| LR9 | Stale lazy-FK strings `'app_rrhh.X'` se acumulan al mover modelos | **Cierta** | Medio | **L3.5+ debe** grep `'app_rrhh.<MovedModel>'` y `"app_rrhh.<MovedModel>"` (single + double quotes) **across TODOS los apps** después de cada move. L3.4 pescó 2 stale refs heredados de L3.2/L3.3 (identity/usuario.py y organization/ubicacion.py) |
| LR10 | Bulk sed con FK strings solo matchea single-quote `'X'`, perdiéndose double-quote `"X"` | Cierta | Medio | **L3.5+ sed debe procesar ambas formas** o pre-normalizar quotes. L3.4 pescó `remuneracion.py:226 ForeignKey("Empleado", ...)` por grep manual post-sed |
| LR3 | Frontend rompe por URLs cambiadas | Alta | Medio | URLs viejas mantienen redirect 301 hasta el final de L4 (frontend reorg). El frontend sigue llamando `/api/v1/rrhh/empleados/` durante L3 |
| LR4 | Signal handlers ocultos en `app_rrhh` | Media | Alto | Antes de L3.2 ejecutar `grep -r "@receiver\|signal\|@app.task" apps/api/app_rrhh/` y catalogar TODO. Cada sub-PR mueve los signals que pertenezcan a sus modelos |
| LR5 | Tests legacy hardcoded a `app_rrhh.X` paths | Alta | Bajo | Cada sub-PR de extracción actualiza imports en `tests/test_*.py` correspondientes. Los 44 fails pre-existing se preservan; nuevos fails son red flag |
| LR6 | Inicialización de drf_spectacular schema con duplicados | Cierta | Bajo | Los 254 W001 actuales (de L2) se eliminan progresivamente conforme L3.X mueve serializers. Verificable post-L3.10 |
| LR7 | `AUTH_USER_MODEL = 'app_rrhh.Usuario'` en L3.2 | Cierta | Crítico | Cambiar `AUTH_USER_MODEL` requiere drop+recreate de tablas auth/sessions o migration cuidadosa. L3.2 detalla el procedimiento exacto |
| LR8 | App label collisions (Django built-in vs nuestras) | Baja | Medio | Si elegimos `apps.core` como label, Django lo registra como `core`. Si choca con `django.core` (no debería, son módulos no apps), renombrar app_label en `apps.py` |
| LR11 | Relative imports `from .models import` en archivos legacy `app_rrhh/{views,serializers,services,tests}.py` no se detectan con grep para `from app_rrhh.models` | **Cierta** | Medio | **L3.6+ plan template DEBE incluir** explícitamente step de grep `from \.models import` en `app_rrhh/*.py` (no solo absoluto). L3.5 lo perdió en la copia del template L3.4 y rompió `manage.py check` post-Phase 3 (vyntia/urls.py → app_rrhh.urls → app_rrhh/views.py:20 import roto). 4 archivos fixed retroactivamente |
| LR12 | `makemigrations` requiere DB existente para `check_consistent_history` | Cierta | Bajo | El plan L3.5 ordenaba `makemigrations` antes de `CREATE DATABASE`. **L3.6+ debe** crear bd_vyntia ANTES de makemigrations, o hacer el sequence: drop → create → makemigrations → migrate (no drop → makemigrations → create → migrate). L3.6 aplicó la corrección y funcionó al primer intento |
| LR13 | Stale logger-name strings (`logger='app_rrhh.services.X'` en `caplog.at_level` o `logging.getLogger`) sobreviven al move porque grep `from ... import` no los detecta | Cierta | Bajo | **L3.7+ plan template DEBE incluir** step explícito de grep `logger=['"]app_rrhh\.\|getLogger.*['"]app_rrhh\.` cuando se mueven modules con loggers nombrados. L3.6 tenía `tests/test_pdf_generation.py:150 caplog.at_level(..., logger='app_rrhh.services.pdf_generator')` — pescado por code-quality reviewer, no por los greps de imports |
| LR14 | Sed Pattern B con `^from app_rrhh.services import X$` solo captura single-line imports; multi-line parenthesized blocks `from app_rrhh.services import (\nA,\nB,\n)` quedan intocados | Cierta | Medio | **L3.9+ plan template DEBE incluir** un grep multi-line `grep -rn -B 0 -A 10 "from app_rrhh\.services import (" --include="*.py"` antes del sed Pattern B. L3.8 tenía `api/v1/vacaciones/views.py:14-19` con bloque multi-line de 4 vacation services — sed lo perdió, spec reviewer lo pescó. Plan debe incluir manual fix step para multi-line service blocks (igual que se hace para multi-line model blocks) |

---

## Cómo empezar

**Ahora:** generar el plan detallado de L3.1 → ejecutar → merge → verificar baseline.

**Después de cada merge:** actualizar este roadmap (`Status` column → ✅ con merge SHA), generar el siguiente plan, ejecutar.

Cuando los 11 sub-PRs estén ✅, L3 está completo. Comenzamos L4 (frontend reorg).

---

## Notas sobre el spec

El spec § 4 lista L3 como una sola sección de 8-15 días. Este roadmap descompone esa sección en 11 sub-PRs concretos siguiendo el mismo orden (L3.1 a L3.11) que el spec ya definió. No hay deviation del spec — solo separación física de los planes.

La numeración decimal (`L3.1`, `L3.2`, ...) es para distinguir sub-PRs dentro de L3. El branch convention sigue: `vyntia/L3.<N>-<short-name>`. El commit prefix sigue: `chore(L3.<N>):` / `docs(L3.<N>):`.
