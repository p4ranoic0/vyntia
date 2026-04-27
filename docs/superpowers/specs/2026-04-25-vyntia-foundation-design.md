# VYNTIA Foundation — Design Spec

> **Sub-proyecto A** del programa de migración INTRANET → VYNTIA.
> **Fecha:** 2026-04-25
> **Estado:** Draft → en revisión por el usuario
> **Autor:** Brainstorming session (Claude + Henrry)
> **Sucesores:** sub-proyectos B (Migración funcional), C (Multi-tenancy), D (Vyntia Pay), … X.

---

## 1. Contexto y propósito

### 1.1 Origen
El proyecto actual `D:\INTRANET\` es una intranet HR funcional pero desordenada. Tiene un backend Django 4.2 monolítico (una sola app `app_rrhh` con 18 modelos mezclados) y un frontend React+Vite con `pages/` y `features/` superpuestos. Funciona parcialmente, fue creciendo sin rumbo, y mezcla branding "INTRANET" con código sin convenciones consistentes.

Paralelamente, en `saas_rrhh/docs/` existen 37 documentos de diseño (v3.0 abril 2026) que definen la visión completa del producto: 12 módulos funcionales, 13 dominios normativos peruanos, 8 documentos de arquitectura, 3 comerciales — un SaaS HR multi-tenant para Perú, vendible modularmente.

El usuario quiere transformar esto en **VYNTIA**, un producto comercializable. La marca VYNTIA está definida en dos documentos (`vyntia_brand_ui.md`, `vyntia_full_system.md`): paleta violeta #6C63FF, tipografía Inter, slogan "Donde el talento se convierte en valor", módulos comerciales Core/People/Pulse/Pay/Hire/Insights.

### 1.2 Problema que Foundation resuelve
La intranet actual NO está lista para venderse como SaaS. Antes de añadir multi-tenancy, billing o módulos nuevos, es necesario **una base limpia**: estructura modular, naming coherente, branding aplicado, código en bounded contexts. Esa base se llama **Foundation**.

### 1.3 Qué NO resuelve Foundation (scope guard)
Foundation **NO** implementa:
- Multi-tenancy (sub-proyecto C)
- Billing/suscripciones (sub-proyecto S)
- Módulos nuevos del doc maestro: policies, learning, performance, recruitment, analytics, etc. (cada uno en su sub-proyecto)
- Migración a FastAPI o Next.js (decisión deferida)
- Workflow engine, DocType engine, custom fields (sub-proyectos T, U)
- App móvil (sub-proyecto P)
- Migración de datos productivos (script opcional)
- i18n inglés/quechua

Foundation **SOLO** reorganiza, renombra y limpia lo que ya existe.

---

## 2. Decisiones tomadas durante el brainstorming

| # | Decisión | Justificación |
|---|---|---|
| D1 | Foundation es un sub-proyecto independiente | El alcance total (24 sub-proyectos identificados) es demasiado grande para un solo spec. Cada sub-proyecto tiene su propio brainstorming → spec → plan → ejecución |
| D2 | Código actual ya fue copiado a un repo nuevo por el usuario | El repo `INTRANET` queda archivado. El nombre del nuevo repo lo confirma el usuario antes de L0 (default sugerido: `vyntia`) |
| D3 | Backend: upgrade Django 4.2 → Django 5 | Mantener framework, ganar versión moderna sin reescribir. FastAPI queda deferido |
| D4 | Backend dividido en una Django app por bounded context | Alineado con DDD del doc maestro. Permite vender módulos independientes a futuro |
| D5 | Frontend: React + Vite reorganizado por features | Cero migración de framework. Next.js queda deferido |
| D6 | Monorepo `apps/api/ + apps/web/ + packages/shared/` con npm workspaces | Convención SaaS estándar. Sin Turborepo/Nx hasta que haga falta |
| D7 | Aplicar design tokens VYNTIA (colores, Inter, logo). Mantener layouts existentes | Cambio visual inmediato sin riesgo. Sidebar nuevo y dashboard estilo Vyntia se hacen en sub-proyecto UI Refresh |
| D8 | BD nueva `bd_vyntia` desde cero, esquema limpio | Cero deuda de migraciones históricas. Script opcional para migrar datos de `bd_rrhh_intranet` si hace falta |
| D9 | Rebrand textual completo: archivos, módulos, BD, configs, docs, branding visible | Coherencia interna y externa. La palabra "rrhh" sobrevive solo donde es término del dominio (rol "Oficina RRHH") |
| D10 | Mantener todos los tests; ajustar imports y rutas durante la migración | Red de seguridad real. Suite verde es criterio de éxito de cada PR |
| D11 | Mover `saas_rrhh/docs/` a `docs/` raíz como fuente de verdad de la visión | Cerca del código. Renombrar `00_MAESTRO_PROYECTO.md` a `00_VYNTIA_MAESTRO.md` |
| D12 | Naming en inglés para entidades, procesos, modelos, fields, URLs, tipos TS | UI sigue en español (i18n posterior). Términos legales peruanos (DNI, RUC, CTS, PLAME, SUNAT) se mantienen como nombres propios |
| D13 | Enfoque incremental por capas L0→L5, cada capa = 1 PR mergeable | Repo siempre verde, rollback granular, paralelizable. Big-bang descartado |
| D14 | NO crear apps Django vacías para módulos futuros | Deuda muerta. Cada módulo se crea en su propio sub-proyecto cuando exista código real |
| D15 | `Department` (no `OrgUnit`) para áreas/unidades organizativas | Decisión del usuario; alineable con sector público en sub-proyectos GovTech |

---

## 3. Arquitectura objetivo

### 3.1 Estructura de directorios

```
vyntia/                                   ← repo nuevo
├── apps/
│   ├── api/                              ← backend Django (era D:\INTRANET\back\)
│   │   ├── manage.py
│   │   ├── pyproject.toml                ← reemplaza requirements.txt
│   │   ├── Makefile
│   │   ├── pytest.ini
│   │   ├── conftest.py
│   │   ├── vyntia/                       ← antes "config/"
│   │   │   ├── settings/
│   │   │   │   ├── base.py
│   │   │   │   ├── development.py
│   │   │   │   ├── production.py
│   │   │   │   ├── staging.py
│   │   │   │   └── testing.py
│   │   │   ├── urls.py
│   │   │   ├── wsgi.py
│   │   │   └── asgi.py
│   │   ├── apps/                         ← bounded contexts (cada uno = Django app)
│   │   │   ├── core/                     ← APIResponse, paginación, decorators (sin modelos)
│   │   │   ├── identity/                 ← User, Role, Permission, auth, MFA futura
│   │   │   ├── organization/             ← Company, Department, Location, SystemSetting
│   │   │   ├── employees/                ← Employee, FamilyMember, AcademicRecord, Certification
│   │   │   ├── contracts/                ← Contract, ContractAmendment, EmploymentData
│   │   │   ├── documents/                ← DigitalDocument, DocumentTemplate, generador PDF/Word
│   │   │   ├── payroll/                  ← Compensation, MonthlyPayroll, TaxParameter
│   │   │   ├── time_off/                 ← VacationRequest, VacationBalance
│   │   │   └── onboarding/               ← OnboardingProcess
│   │   ├── tests/                        ← integration tests cross-app
│   │   ├── templates/                    ← templates HTML para PDFs
│   │   ├── media/                        ← uploads
│   │   └── scripts/                      ← scripts admin one-off
│   │
│   └── web/                              ← frontend React+Vite (era D:\INTRANET\front\)
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       ├── playwright.config.ts
│       ├── public/
│       └── src/
│           ├── main.tsx
│           ├── App.tsx
│           ├── app/                      ← layouts, providers, routing top-level
│           │   ├── layouts/
│           │   ├── providers/
│           │   └── routing/
│           ├── features/                 ← una carpeta por bounded context backend
│           │   ├── identity/
│           │   ├── organization/
│           │   ├── employees/
│           │   ├── contracts/
│           │   ├── documents/
│           │   ├── payroll/
│           │   ├── time-off/
│           │   └── onboarding/
│           ├── shared/                   ← UI primitives, hooks, utils reutilizables
│           │   ├── ui/                   ← shadcn components
│           │   ├── api/                  ← axios client, react-query setup
│           │   ├── hooks/
│           │   └── lib/
│           └── styles/
│               └── tokens.css            ← consume packages/design-tokens
│
├── packages/
│   ├── shared/                           ← tipos TS compartidos
│   │   ├── package.json
│   │   └── src/types/
│   │
│   └── design-tokens/                    ← colores, espaciado, tipografía VYNTIA
│       ├── package.json
│       └── tokens.json                   ← single source of truth
│
├── docs/                                 ← era saas_rrhh/docs/
│   ├── 00_VYNTIA_MAESTRO.md              ← renombrado
│   ├── ROADMAP_SUBPROJECTS.md            ← nuevo
│   ├── arquitectura/
│   ├── modulos/
│   ├── normativa/
│   ├── comercial/
│   └── superpowers/specs/                ← este spec vive aquí
│
├── scripts/                              ← migración datos opcional, seeds
│   └── migrate-from-intranet.py          ← solo si hay datos productivos
│
├── .github/workflows/                    ← CI/CD
├── .gitignore
├── README.md                             ← rebrand VYNTIA
├── CLAUDE.md                             ← actualizado para nueva estructura
└── package.json                          ← root con npm workspaces
```

### 3.2 División de modelos (mapeo `app_rrhh/models/` → nuevas apps)

| App nueva | Modelos absorbidos (origen → destino) | Responsabilidad |
|---|---|---|
| **identity** | `usuario.py → User`, `roles.py → Role + Permission` | Auth, usuarios, roles, permisos |
| **organization** | `area.py → Department`, `ubicacion.py → Location`, `configuracion_empresa.py → Company`, `sistema.py → SystemSetting` | Empresa cliente, áreas, ubicaciones, config global |
| **employees** | `empleado.py → Employee`, `datos_familiares.py → FamilyMember`, `datos_academicos.py → AcademicRecord`, `cursos_certificaciones.py → Certification` | Persona empleado, datos personales, familia, formación |
| **contracts** | `contratos_adendas.py → Contract + ContractAmendment` (split), `datos_laborales.py → EmploymentData` | Vínculo laboral, contratos, adendas, datos del puesto |
| **documents** | `documentos_digitales.py → DigitalDocument`, `plantilla_documento.py → DocumentTemplate` | Legajo digital, plantillas, generación PDF/Word |
| **payroll** | `remuneracion.py → Compensation`, `configuracion_uit.py → TaxParameter` | Remuneraciones, parámetros tributarios. `MonthlyPayroll` se crea nuevo si hace falta |
| **time_off** | `vacaciones.py → VacationRequest + VacationBalance` (split) | Vacaciones, balances, permisos |
| **onboarding** | `onboarding.py → OnboardingProcess` | Proceso de inducción |
| **core** | (sin modelos) `APIResponse`, paginación, decorators, mixins | Utilidad transversal |

### 3.2.1 Scope clarification (L3.10.3)

L3.10.3 implementa solo el split `Contract → Contract + ContractAmendment`. El split listado en § 3.2 para `VacationRequest → VacationRequest + VacationBalance` se DESCARTA por análisis posterior:

- `VacationRequest` actual NO contiene fields de balance — solo solicitud/aprobación/rechazo/cancelación con `dias_solicitados`, `motivo_solicitud`, `estado_solicitud`, etc.
- Los fields de balance (`dias_correspondientes`, `dias_adicionales`, `dias_totales`, `dias_gozados`, `dias_pendientes`, `dias_vencidos`) ya viven en `VacationPeriod`. `VacationPeriod` cumple efectivamente el rol de "balance" por período anual.
- Crear un nuevo `VacationBalance` separado de `VacationPeriod` agregaría complejidad sin valor — sería un modelo 1:1 OneToOne con VacationPeriod.

**Decisión:** mantener la estructura actual de 5 modelos en time_off (`VacationConfiguration`, `VacationPeriod`, `VacationRequest`, `VacationGrant`, `VacationRequestHistory`). VacationPeriod es el balance per period.

### 3.3 Mapeo de services

| App | Services absorbidos (de `app_rrhh/services/`) |
|---|---|
| **employees** | `empleado_report_service.py` |
| **documents** | `pdf_generator.py`, `template_service.py`, `word_template_service.py` |
| **payroll** | `planilla_calculo_service.py`, `descuento_masivo_service.py` |
| **time_off** | `vacation_service.py`, `vacation_admin_service.py`, `vacation_approval_service.py`, `vacation_calculation_service.py`, `vacation_report_service.py` |
| **onboarding** | `onboarding_service.py` |

### 3.4 URL structure resultante

```
/api/v1/identity/auth/login
/api/v1/identity/users
/api/v1/identity/roles
/api/v1/organization/companies
/api/v1/organization/departments
/api/v1/organization/locations
/api/v1/employees
/api/v1/employees/{id}/family-members
/api/v1/employees/{id}/academic-records
/api/v1/contracts
/api/v1/contracts/{id}/amendments
/api/v1/documents/templates
/api/v1/documents/digital
/api/v1/payroll/compensations
/api/v1/payroll/monthly-runs
/api/v1/time-off/vacations
/api/v1/time-off/vacations/{id}/balance
/api/v1/onboarding/processes
/api/docs/                                ← Swagger sin cambios
```

### 3.5 Reglas duras de la arquitectura

1. **FK cross-app SOLO con string lazy**: `models.ForeignKey('employees.Employee', ...)`. Nunca `from apps.employees.models import Employee` en otra app.
2. **Imports de Python cross-app prohibidos**. Si una app necesita lógica de otra, va por **service public API** (función exportada en `apps/<other>/services/__init__.py`).
3. **Lecturas cross-app via FK** sí están permitidas a nivel ORM: `compensation.employee.first_name` está bien. Lo prohibido es el `import`.
4. **`core` NO depende de ninguna app de dominio** — solo es utilidad pura.
5. **Cada app tiene su propio** `urls.py`, `serializers.py`, `views/`, `services/`, `tests/`.
6. **Naming en inglés** para todo el código Python y TypeScript. Strings UI en español (i18n posterior).
7. **Términos legales peruanos preservados**: DNI, RUC, CTS, PLAME, T-Registro, SUNAT, etc.

### 3.6 Convención de fields

| Patrón viejo (español) | Patrón nuevo (inglés) |
|---|---|
| `nombres`, `apellido_paterno`, `apellido_materno` | `first_name`, `last_name`, `second_last_name` |
| `fecha_nacimiento`, `fecha_ingreso` | `birth_date`, `hire_date` |
| `estado` | `status` |
| `activo` | `is_active` |
| `creado_en`, `actualizado_en` | `created_at`, `updated_at` |
| `creado_por`, `actualizado_por` | `created_by`, `updated_by` |
| PK específicas (`empleado_id`, `contrato_id`) | `id` UUID |

### 3.6.1 Scope decision (L3.10.2 Option B)

L3.10.2 aplica § 3.6 SOLO a fields **genéricos de plataforma**:
- Audit timestamps (`fecha_creacion`, `fecha_actualizacion`, `fecha_registro`, `fecha_modificacion`)
- Audit FKs (`creado_por`, `modificado_por`)
- State literales (`estado`, `activo`)
- PKs (`<modelo>_id` → `id` UUID)

**Domain vocabulary HR peruano se PRESERVA en español** (`nombres_empleado`, `apellido_paterno`, `tipo_documento`, `numero_cuspp`, `estado_empleado`, `estado_civil`, `vigencia_estado_seguro`, etc.). Esta es una extensión natural de la regla 7 ("términos legales peruanos preservados") aplicada al vocabulario de dominio HR. Domain audit-like fields (`validado_por`, `digitalizado_por`, `subido_por`) también quedan en español.

Frontend rename de los fields renombrados se hace en L3.10.4. Entre L3.10.2 merge y L3.10.4 merge, el frontend romperá en uses de `empleado_id`, `fecha_creacion`, etc. — accepted tradeoff (solo dev, no production users).

---

## 4. Plan de capas (L0 → L5)

Cada capa = 1 PR mergeable. Repo siempre verde y desplegable.

### L0 — Bootstrap del monorepo (1-2 días)

**Cambios:**
- Crear `apps/`, `packages/`, `docs/`, `scripts/`, `.github/` en raíz
- `git mv back/ apps/api/`, `git mv front/ apps/web/`, `git mv saas_rrhh/docs/* docs/`
- Crear `package.json` raíz con npm workspaces
- Consolidar `.gitignore`
- README placeholder VYNTIA

**Definition of done:**
- `cd apps/api && python manage.py runserver` arranca como antes
- `cd apps/web && npm run dev` arranca como antes
- Suite pytest + vitest verde sin cambios

**NO toca:** código Python ni TS.

---

### L1 — Rebrand superficial (3-5 días)

**Cambios:**
- BD nueva `bd_vyntia` creada con `python manage.py migrate` (esquema actual)
- Renombrar `config/` → `vyntia/`
- `DJANGO_SETTINGS_MODULE` → `vyntia.settings.development`
- `pyproject.toml` reemplaza `requirements.txt`, package name `vyntia-api`
- `packages/design-tokens/tokens.json` con paleta VYNTIA (#6C63FF, Inter, espaciado)
- `apps/web/src/styles/tokens.css` consume design-tokens
- Logo + wordmark VYNTIA en topbar/sidebar
- Inter font cargada
- Tema base usa colores VYNTIA
- Todos los `.md` actualizan referencias INTRANET → VYNTIA
- `.env.example` con variables nuevas

**Definition of done:**
- App funcional con BD nueva
- Visualmente dice VYNTIA, colores violetas, Inter
- Tests verdes
- `grep -ri intranet apps/` solo devuelve menciones legítimas pendientes de L3

**NO toca:** división de apps Django, modelos, lógica.

---

### L2 — Upgrade Django 4.2 → Django 5 (2-4 días)

**Cambios:**
- `Django>=5.0,<5.1` en `pyproject.toml`
- Auditoría de paquetes: `pip list --outdated` + matrix de compatibilidad
- Ajustar deprecaciones (USE_L10N, transaction.on_commit, etc.)
- Verificar DRF, drf-spectacular, django-cors-headers, etc.

**Definition of done:**
- `python manage.py check --deploy` limpio
- Suite pytest verde
- App arranca sin warnings de deprecación

**NO toca:** estructura de apps, modelos.

---

### L3 — División de apps Django (8-15 días, el más grande)

Sub-PRs secuenciales:

- **L3.1 — `core`**: extraer utilidades sin modelos
- **L3.2 — `identity`**: mover usuario, roles, auth views
- **L3.3 — `organization`**: mover area, ubicacion, configuracion_empresa, sistema
- **L3.4 — `employees`**: mover empleado, familiares, académicos, certificaciones
- **L3.5 — `contracts`**: mover contratos, datos_laborales; split a Contract + ContractAmendment
- **L3.6 — `documents`**: mover documentos_digitales, plantilla_documento + services PDF/Word
- **L3.7 — `payroll`**: mover remuneracion, configuracion_uit + planilla services
- **L3.8 — `time_off`**: mover vacaciones + 5 vacation services
- **L3.9 — `onboarding`**: mover onboarding + service
- **L3.10 — Renombre español → inglés**: aplica tabla Sección 3 a TODOS los modelos. Migración Django RenameModel + AlterField. Actualiza serializers, views, tests, frontend services
- **L3.11 — Eliminar `app_rrhh`**: carpeta vacía se borra. URLs raíz actualizadas

**Definition of done por sub-PR:**
- App nueva creada con `models/`, `views/`, `serializers.py`, `urls.py`, `tests/`
- Migración Django generada y aplicada limpiamente sobre `bd_vyntia`
- Suite pytest verde con imports actualizados
- Frontend sigue funcionando: las URLs viejas (`/api/v1/rrhh/...`) responden via wildcard view en `vyntia/urls.py` que redirige 301 a las URLs nuevas (`/api/v1/employees/...`). Los redirects se eliminan al final de L4 cuando el frontend ya consume las nuevas

**Riesgo principal:** circular imports y FKs cruzadas.
**Mitigación:** string lazy `'employees.Employee'` en TODOS los FK cross-app.

---

### L4 — Reorganización del frontend (5-8 días)

**Cambios:**
- `pages/` y `features/` consolidados en `features/<bounded-context>/`
- Cada feature: `api.ts`, `hooks/`, `components/`, `pages/`, `types.ts`
- Services renombrados según tabla
- URLs API en frontend actualizadas a rutas nuevas en inglés
- `shared/ui/` consolida shadcn
- `shared/api/` consolida axios + react-query
- Tipos TS movidos a `packages/shared/src/types/`

**Definition of done:**
- `npm run build` sin errores
- `npm test` (vitest) verde
- Playwright smoke tests críticos verdes (login, lista empleados, crear contrato, descargar PDF, crear vacación)
- Navegación manual: todas las páginas cargan

---

### L5 — Cleanup final (2-3 días)

**Cambios:**
- Borrar archivos huérfanos
- Eliminar imports muertos (ts-prune, vulture)
- Borrar scripts legacy
- Consolidar `.gitignore`
- Actualizar `CLAUDE.md` con nueva estructura completa
- Actualizar `docs/00_VYNTIA_MAESTRO.md` para reflejar arquitectura real
- Crear `docs/ROADMAP_SUBPROJECTS.md` con los ~23 sub-proyectos identificados (ver Sección 6 del spec)
- Crear `docs/CONTRIBUTING.md` con convenciones
- CI workflow `.github/workflows/ci.yml`: lint + test backend + test frontend + build

**Definition of done:**
- `grep -ri "app_rrhh\|intranet\|rrhh_" apps/` → cero matches (excepto dominio legítimo)
- CI verde en GitHub Actions
- Onboarding doc: `git clone && make setup && make dev` arranca todo en <30 min

---

## 5. Cobertura de los 12 módulos del doc maestro

Foundation **NO implementa** los 12 módulos completos. Reorganiza lo que YA existe y deja la arquitectura preparada para que cada módulo futuro encaje sin reestructurar.

### 5.1 Mapa de cobertura

| # | Módulo maestro | App responsable | Estado en Foundation | Sub-proyecto que lo construye |
|---|---|---|---|:---:|
| 01 | Planificación Políticas | `policies` *(no existe)* | ❌ Vacío | F |
| 02 | Organización Trabajo | `organization` (parcial) + `positions` *(falta)* | ⚠️ Solo áreas/ubicaciones/empresa | E (extensión) |
| 03 | Gestión Empleo | `employees` + `contracts` + `onboarding` (parciales) + `selection` + `terminations` + `displacements` | ⚠️ Empleado/contrato/onboarding básico | E (MVP comercial) |
| 04 | Compensación | `payroll` (parcial) + `benefits` + `pensions` + `regional_pe` | ⚠️ Solo remuneración básica. Falta motor multi-régimen, Strategy 13 regímenes, event sourcing, PLAME, T-Registro, AFPnet, CTS, gratificaciones, Renta 5ta | **D — Vyntia Pay** |
| 05 | Desarrollo y Capacitación | `learning` + `career` *(no existen)* | ❌ Vacío | G |
| 06 | Gestión Rendimiento | `performance` *(no existe)* | ❌ Vacío | H — Vyntia Pulse |
| 07 | Relaciones HH y Sociales | `labor_relations` + `safety` + `welfare` + `engagement` + `communications` | ❌ Vacío (5 apps nuevas — sub-procesos SERVIR) | I, J, K, L, M |
| 08 | Asistencia/Tiempo | `time_off` (parcial) + `attendance` + `shifts` | ⚠️ Solo vacaciones | N |
| 09 | Procedimiento Disciplinario | `discipline` *(no existe)* | ❌ Vacío | O |
| 10 | Portal Empleado y App Móvil | `apps/web` (parcial) + `apps/mobile` *(no existe)* | ⚠️ Web parcial. Móvil cero | P |
| 11 | Reclutamiento ATS | `recruitment` *(no existe)* | ❌ Vacío | Q — Vyntia Hire |
| 12 | Analítica People Analytics | `analytics` *(no existe)* | ❌ Vacío | R — Vyntia Insights |

### 5.2 Marca comercial VYNTIA → módulos maestros agrupados

| Módulo VYNTIA (sidebar) | Módulos maestros que agrupa | Apps Django |
|---|---|---|
| Vyntia Core | 01, 02, 03 (parcial) + transversales | identity, organization, employees, contracts, documents, onboarding (+ `policies` cuando exista — sub-proyecto F) |
| Vyntia People | 03 completo, 05, 06, 07 | selection, terminations, displacements, learning, career, performance, labor_relations, welfare, engagement, communications |
| Vyntia Pulse | 06 + 07.4 + 07.5 | performance, engagement, communications |
| Vyntia Pay | 04 + 08 (parte) | payroll, benefits, pensions, regional_pe, time_off, attendance |
| Vyntia Hire | 11 | recruitment |
| Vyntia Insights | 12 | analytics |
| Vyntia Safety (GovTech) | 07.2 | safety |
| Vyntia Discipline (GovTech) | 09 | discipline |

### 5.3 Apps transversales (capa de plataforma)

| App / paquete | Sub-proyecto |
|---|---|
| `tenancy` (multi-tenant + RLS) | C |
| `billing` (suscripciones, planes) | S |
| `workflows` (motor declarativo) | T |
| `doctypes` (metadata-driven) | U |
| `events` (event bus, event sourcing payroll) | parte de D |
| `permissions` (RBAC + permlevel 0-9 + ABAC) | V |
| `notifications` (email, push, in-app) | W |
| `audit` (audit log transversal) | X |
| `regional_pe` (tablas SUNAT, PLAME, T-Registro, AFPnet) | parte de D |
| `apps/mobile` (React Native) | P |

---

## 6. Roadmap de sub-proyectos post-Foundation

| Orden | Sub-proyecto | Necesita antes | Tier comercial habilitado |
|---|---|---|---|
| 1 | A — Foundation *(este spec)* | — | — |
| 2 | C — Multi-tenancy + RLS | A | Habilita venta SaaS |
| 3 | B — Migración funcional Vyntia Core | A, C | Vyntia Core funcional con tenant |
| 4 | D — Vyntia Pay (planilla peruana real) | B | **Starter comercializable** |
| 5 | N — Asistencia + turnos | D | Starter + Asistencia |
| 6 | P — App móvil | B | Portal móvil empleado |
| 7 | S — Billing SaaS | C | Cobros automáticos |
| 8 | H — Vyntia Pulse (rendimiento) | B | **Pro tier** |
| 9 | G — Learning + Career | B | Pro tier |
| 10 | Q — Vyntia Hire (ATS) | B | Pro tier |
| 11-15 | I, J, K, L, M — Relaciones HH | B | Pro/GovTech |
| 16 | R — Vyntia Insights (analytics) | B + datos reales | **Enterprise tier** |
| 17 | F, O — Policies + Discipline | B | GovTech tier |
| Resto | T, U, V, W, X — Plataforma avanzada | progresivo | Madurez |

---

## 7. Riesgos y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|:---:|:---:|---|
| R1 | Migraciones Django rompen al renombrar (datos perdidos) | Alta | Bajo | BD `bd_vyntia` desde cero. Vieja `bd_rrhh_intranet` intacta. Script export/import opcional |
| R2 | Circular imports entre apps al dividir | Alta | Medio | FK string lazy `'employees.Employee'`. Imports cross-app prohibidos — usar services |
| R3 | URLs antiguas rompen frontend durante L3 antes de L4 | Media | Alto | Mantener URLs viejas como redirects 301 → nuevas durante L3. Eliminar al final de L4 |
| R4 | Django 5 rompe paquetes terceros | Media | Medio | L2 incluye auditoría compatibilidad. Si algo no soporta 5, queda en 4.2 LTS |
| R5 | Reorganización front rompe rutas | Media | Medio | L4 mantiene paths viejos con redirects React Router durante 1 release |
| R6 | Tests pytest fallan por imports | Alta | Bajo | Cada sub-PR L3 actualiza imports. PR no se mergea si suite roja |
| R7 | Pérdida de tiempo decidiendo nombres mid-flight | Media | Bajo | Tabla naming Sección 3 es contrato. Cambios solo en revisión final del spec |
| R8 | Pérdida de funcionalidad sutil (signal handler oculto, celery task) | Media | Alto | Antes de L3, escanear `grep -r "signal\|receiver\|@app.task" apps/api/`. Cada hallazgo va a su nueva app explícitamente |
| R9 | `media/` (uploads) se rompe al cambiar paths | Baja | Alto | `MEDIA_ROOT`/`MEDIA_URL` no cambian. Solo se mueve dentro del directorio. Sin paths absolutos en BD |
| R10 | Templates HTML PDFs rompen | Media | Medio | L3.6 verifica cada template render con script smoke test |
| R11 | Branch divergence con trabajo paralelo en INTRANET viejo | Alta | Bajo | INTRANET viejo se congela. Solo VYNTIA recibe cambios |
| R12 | Estimación 3-5 semanas se duplica | Alta | Medio | Capas mergeables independientes. Pausas no pierden trabajo |
| R13 | Frontend types desincronizados con backend | Media | Medio | Generar tipos TS desde drf-spectacular OpenAPI con `openapi-typescript` en CI (opcional) |

---

## 8. Definition of Done para Foundation completo

Foundation se considera terminado cuando **TODAS** estas condiciones se cumplen:

- [ ] `grep -ri "app_rrhh\|INTRANET\|bd_rrhh_intranet" apps/` → cero matches (excepto referencias legítimas en `docs/` heredados)
- [ ] `grep -ri "Empleado\|Contrato\|Vacacion" apps/api/apps/` → cero matches en código Python (sí en strings UI español)
- [ ] `cd apps/api && pytest` → todos los tests verdes
- [ ] `cd apps/web && npm test && npm run build` → verde
- [ ] `cd apps/web && npx playwright test` → smoke tests críticos verdes
- [ ] `git clone && make setup && make dev` arranca todo en <30 min
- [ ] CI GitHub Actions verde
- [ ] `docs/00_VYNTIA_MAESTRO.md` con título VYNTIA y referencias correctas
- [ ] `docs/ROADMAP_SUBPROJECTS.md` con los ~23 sub-proyectos identificados (ver Sección 6)
- [ ] `CLAUDE.md` actualizado con nueva estructura
- [ ] README muestra wordmark VYNTIA, instrucciones correctas
- [ ] BD `bd_vyntia` migrada limpia con esquema final
- [ ] Visualmente: app dice VYNTIA, colores #6C63FF, Inter, logo nuevo

---

## 9. Estimación

**Total: 3-5 semanas** trabajando solo, full-time.

| Capa | Estimación |
|---|---|
| L0 — Bootstrap | 1-2 días |
| L1 — Rebrand superficial | 3-5 días |
| L2 — Django 5 upgrade | 2-4 días |
| L3 — División apps Django (11 sub-PRs: L3.1 a L3.11) | 8-15 días |
| L4 — Reorganización frontend | 5-8 días |
| L5 — Cleanup final | 2-3 días |

Multiplicador realista por interrupciones: ×1.5 → **4-7 semanas calendar time**.

---

## 10. Apéndices

### 10.1 Tabla completa de renombres (modelos)

Ver Sección 3 del spec. Tabla congelada — no se modifica sin revisión del spec.

### 10.2 Referencias

- Doc maestro proyecto: `docs/00_VYNTIA_MAESTRO.md` (era `saas_rrhh/docs/00_MAESTRO_PROYECTO.md`)
- Brand kit: `vyntia_brand_ui.md`, `vyntia_full_system.md` (origen: `C:\Users\zeeke\Downloads\`). Copiar a `docs/branding/` durante L1
- Arquitectura general: `docs/arquitectura/A01_arquitectura_general.md`
- Multi-tenancy: `docs/arquitectura/A02_multitenancy_rls.md` (referencia para sub-proyecto C)
- Estado actual del repo INTRANET: `D:\INTRANET\CLAUDE.md`

### 10.3 Próximos pasos después de aprobar este spec

1. Spec auto-revisado por Claude (placeholder scan, consistencia, scope, ambigüedad)
2. Usuario revisa spec final
3. Invocar skill `superpowers:writing-plans` para generar plan de implementación L0→L5 con tareas atómicas
4. Comenzar ejecución de L0
