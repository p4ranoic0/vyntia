# PM — Audit Empleados (2026-05-22)

**Orquestador:** main agent en rol PM (el sub-agente `vyntia-pm` no puede delegar — ver `2026-05-22-smoke-test-status-general.md`).
**Scope:** módulo Empleados completo (core B.4 + ATS B.9 + Legajos B.12 + datos personales/familiares/académicos/laborales + reporte integral).
**Especialistas lanzados (4, en paralelo):** feature-supervisor, code-quality, ui-modular, hr-tester.
**Reportes fuente:** todos persistidos en `docs/agent-reports/{agente}/2026-05-22-empleados.md`.

---

## TL;DR — Verdict ejecutivo

🟡 **AMARILLO con bordes rojos.** El módulo es funcionalmente robusto (114 tests propios + 25 B.12 docs + 14 access-log, todos pasando; baseline 982/1/17 intacto) y D (Vyntia Pay) puede construir encima. **Pero** existen 3 bloqueos previos a comercialización:

1. **Compliance legal en riesgo** (Ley 29733 + SUNAFIL): `permission_level` modelado pero NO enforced; `DocumentAccessLog` instanciable pero NO invocado en flujo real de descarga.
2. **Producto NO es modular comercialmente:** cero feature flags por tenant/plan. ATS (B.9), Legajo (B.12), Pay están accesibles a cualquier tenant cuyo rol RBAC lo permita. Sin esto, VYNTIA no se vende por planes Starter/Pro/Enterprise — es todo-o-nada.
3. **Bugs de runtime que pasan inadvertidos:** `EmpleadosListPage.tsx:100` referencia `isRRHH`/`isSupervisor` sin declararlos (ReferenceError al cargar la lista); `HROverviewDashboard.tsx:479,589,658` lee `p.status` cuando el modelo expone `p.estado` (KPI de planilla siempre cae a 10% borrador); `Employee.boletas_recientes()` retorna stub vacío con código muerto.

**D-Pay readiness:** ⚠️ "sí-con-fixes" según code-quality. Régimen 728 / MyPE / CAS / locación de servicios no están parametrizados ni testeados — bloqueo directo para arrancar planilla peruana real.

---

## Hallazgos top (consolidado de los 4 especialistas)

### 🔴 Críticos (bloquean comercialización)

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 1 | Permission level (PL 1-9) NO se enforcea en API B.12 | feature-supervisor | `access_service.can_access()` existe pero `DossierSectionViewSet`/`DigitalDossierViewSet`/`DocumentGenerationViewSet` no la llaman | CORTO |
| 2 | DocumentAccessLog NO se invoca en flujo real | feature-supervisor | `consolidated_pdf`, descarga de DigitalDocument no llaman `log_access()`; Ley 29733 requiere log | CORTO |
| 3 | NO existe sistema de feature flags por plan | ui-modular | 0 matches de `useFeatureFlag`, `tenant.modules`, `ModuleGate`, `UpgradePrompt` en BE+FE | LARGO (sub-proyecto E nuevo) |
| 4 | `EmpleadosListPage.tsx:100` referencia variables undefined | code-quality | `isRRHH`/`isSupervisor` no declarados → ReferenceError al cargar; tsc del proyecto no lo captura (página huérfana, solo barrel) | CORTO |
| 5 | Régimen 728 / MyPE / CAS no parametrizados ni testeados | hr-tester | `calcular_vacaciones_pendientes` hardcodea 30 días (`employment_data.py:288`); locación mezclada en `EmploymentData` sin filtro | CORTO+LARGO |

### 🟠 Altos (deuda relevante)

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 6 | Batch import CSV de empleados ausente (#130 B.4) | feature-supervisor | onboarding cliente 200+ trabajadores = trabajo manual semanas; bloquea D | CORTO |
| 7 | `HROverviewDashboard.tsx` usa `p.status` vs modelo `p.estado` | ui-modular | KPI de planilla siempre = 10% borrador; líneas 479, 589, 658 | CORTO (15 min) |
| 8 | `PersonnelRequisition` permite mismo User aprobar HR + Finance | code-quality | dual control roto; constante `MIN_PUBLIC_OPEN_BUSINESS_DAYS=7` comparada contra días calendario | CORTO |
| 9 | `EmpleadoCreateSerializer` no valida DNI (8 dígitos) | hr-tester | Solo `EmpleadoUpdateSerializer` valida; `OnboardingIniciarSerializer` valida unicidad global en vez de por tenant | CORTO |
| 10 | Sidebar item `/legajos-digitales` falta en seed_menu | feature-supervisor | ruta existe pero `seed_menu.py` no la registra; feature inalcanzable salvo escribiendo URL | CORTO (5 min) |
| 11 | 3 viewsets B.9 sin `TenantAwareViewSetMixin` | feature-supervisor | SelectionStage, CandidateEvaluation, MeritRanking — aislamiento depende de cadena FK sin validación explícita | MEDIO |
| 12 | 5 imports rotos en frontend empleados | ui-modular | `@/shared/ui/loading-spinner` no existe; archivos huérfanos no ruteados | CORTO |
| 13 | Doble registro de `/desplazamiento` en App.tsx | feature-supervisor | línea 539 = página real, línea 650 = stub "Modulo en desarrollo" | CORTO (residuo seed) |

### 🟡 Medios (mejora continua)

- `Employee.boletas_recientes()` stub con código muerto (`return []` duplicado, `fecha_limite` calculada y descartada) — D va a reescribir, mejor borrar antes (code-quality)
- 29 `console.log` debug en frontend empleados (ui-modular)
- Badge "Activo" reimplementado 3 veces con colores Tailwind hardcoded (ui-modular)
- Dos fuentes de design tokens (`packages/design-tokens` vs `shared/utils/design-tokens.ts`) que nunca se cruzan (ui-modular)
- Tests faltantes top-5: PL-9-deny, transferir empleado, datos académicos auto-edit cross-employee, certificaciones, B.9 cross-tenant (feature-supervisor)
- `validate_fecha_nacimiento` bloquea practicantes 16-17 años (ilegal según Ley 28518) (hr-tester)

### ✅ Lo que SÍ está bien (no tocar)

- 114 tests del scope pasan sin regresión contra baseline 982/1/17
- Modelo de datos core (Employee + EmploymentData + FamilyMember + AcademicRecord) sólido y testeado
- B.9 ATS completo: 7 modelos + 7 viewsets + 14 acciones de lifecycle + tests
- B.12 Legajos: 3 modelos contenido + DigitalDossier + 15 secciones seeded + PDF consolidado
- Páginas activas (`Empleados.tsx`, `HROverviewDashboard.tsx`, `EmpleadoReportPage.tsx`) tienen skeletons, empty states, Shadcn/ui y animaciones decentes
- `manage.py check` 0 issues, migraciones sync
- Tenant uniqueness constraints correctos en Employee

---

## Trends que vemos cruzando los 4 reportes

1. **"Skeleton built, call sites missing"** — patrón recurrente: el modelo y el service existen y tienen unit tests verdes, pero el viewset/component que los debería invocar no los llama. Ejemplos: `access_service.can_access()`, `DocumentAccessLog.log_access()`, feature flags por plan. **Implicación:** la fase de "wire it up" se está saltando sistemáticamente al cerrar sub-fases. Sugerencia para sub-proyecto D: agregar "verificación de call-site" al checklist de cierre.

2. **Drift ES → EN parcial** — `api/v1/employees/` (EN) coexiste con `api/v1/rrhh/` (ES legacy). Vistas críticas como `EmpleadoViewSet` siguen en `rrhh/views.py`. Code-quality y feature-supervisor convergen en que esto es deuda visible.

3. **Validaciones peruanas dispersas e incompletas** — DNI, régimen laboral, edad mínima de practicantes (Ley 28518), MyPE vs régimen general no están centralizadas. hr-tester argumenta fuerte que esto debe quedar resuelto antes de tocar Pay.

4. **El frontend tiene 3 caminos paralelos para empleados** — `Empleados.tsx` vs `EmpleadosListPage.tsx` (huérfana, con bug) vs las 4 páginas `Datos*Page.tsx` standalone. ui-modular y code-quality coinciden: hay que decidir el canónico y borrar los otros.

---

## 3 acciones priorizadas

### 1. CORTO PLAZO — Sprint "pre-D Empleados Polish" (estimado ~2-3 días)
**Responsable:** Henrry / sesión con executing-plans.
**Alcance:**
- Cerrar #118 (enforcement `permission_level` en 3 viewsets B.12) → resuelve hallazgo crítico #1
- Invocar `log_access()` en `consolidated_pdf` y descarga `DigitalDocument` → resuelve #2
- Fix `EmpleadosListPage.tsx:100` (declarar `isRRHH`/`isSupervisor` o borrar la página huérfana) → #4
- Fix `HROverviewDashboard.tsx` `p.status`→`p.estado` (3 líneas) → #7
- Validar DNI en `EmpleadoCreateSerializer`, dejar `OnboardingIniciarSerializer` unicidad por tenant → #9
- Parametrizar `calcular_vacaciones_pendientes` para régimen (30 / 15 / 0 días) → #5 parcial
- Añadir item sidebar para `/legajos-digitales` en `seed_menu.py` → #10
- Borrar `Employee.boletas_recientes()` stub muerto → bonus medio
**Impacto:** desbloquea comercialización legal de B (Vyntia Core) y deja el módulo listo para que D construya encima.

### 2. MEDIO PLAZO — Decisión: ¿sub-proyecto E (Modularidad/Plans) ahora o después de D?
**Responsable:** Henrry (decisión de producto).
**Contexto:** ui-modular argumenta que VYNTIA no es vendible por planes hoy. Cero feature flags. Ningún tenant ve un "upgrade prompt" cuando intenta entrar a un módulo no contratado. Trade-off:
- **Si se mete ANTES de D:** Pay sale con feature-gating correcto desde el día 1, pero retrasa Pay 2-3 semanas.
- **Si se mete DESPUÉS de D:** Pay sale rápido pero hay que re-fachar todos los módulos existentes (Empleados, Contratos, Documentos, Vacaciones, Onboarding) con `<ModuleGate>` después. Riesgo: cliente Starter contrata y ve features que no debería ver.

Sugerencia mía como PM: brainstorm formal con `superpowers:brainstorming` para decidir scope + secuencia. No es decisión trivial.

### 3. LARGO PLAZO — D.0 ADR (cuando D arranque)
**Responsable:** sesión de brainstorming + writing-plans para D.
**Decisiones a tomar:**
- Vendor PDF para boletas peruanas (xhtml2pdf vs WeasyPrint vs ReportLab — ReportLab hoy genera stub no-HTML)
- Modelo de régimen laboral parametrizado (728 / MyPE 15-días / CAS / locación 4ta categoría) con tabla referencial vs hardcoded
- Implementar batch import CSV de empleados como pre-requisito (no opcional)
- Snapshot "planilla del mes X" (test que recorre `Employee.datos_laborales.filter(estado_datos='activo', cese__isnull=True)` en una fecha de corte)
- Agregar `TenantAwareViewSetMixin` a los 3 viewsets B.9 que faltan, o documentar por qué no aplica

---

## Sugerencia para afinar el propio equipo de agentes

**Agente:** `vyntia-feature-supervisor`.
**Observación:** este agente devolvió su reporte completo **inline en el mensaje al orquestador** y dijo explícitamente "Per instructions I should NOT write a report file". Eso rompe el contrato del equipo (todos los reportes deben persistirse en `docs/agent-reports/{agente}/`). El orquestador (yo) tuvo que copiar manualmente el contenido al archivo esperado. Los otros 3 especialistas escribieron correctamente.

**Causa raíz probable:** el prompt del agente en `.claude/agents/vyntia-feature-supervisor.md` no es lo suficientemente enfático sobre el contrato de salida (escribir Y devolver inline), o el agente lo interpretó como una opción.

**Cambio textual propuesto:** en `.claude/agents/vyntia-feature-supervisor.md`, bajo "Output contract" o equivalente, agregar:

> **CRÍTICO — Persistencia obligatoria:**
> Tu output **DEBE** existir en disco en `docs/agent-reports/feature-supervisor/YYYY-MM-DD-{scope}.md` antes de retornar. Esto NO es opcional. Después de escribir, devuelve al orquestador un resumen ≤200 palabras + ruta absoluta del archivo. Si no puedes escribir (permisos, error), aborta y reporta el error — NO devuelvas el reporte solo inline.

**Bonus — sugerencia secundaria:** el agente `vyntia-pm` original (sub-agente) no puede delegar (limitación del harness Claude Code: no recursion). El smoke test de hoy lo confirmó. El modelo correcto es **main agent en rol PM** (este reporte usa ese patrón). Sugerencia: reescribir `.claude/agents/vyntia-pm.md` como un **prompt-template** que el main agent invoca con `Skill`, NO como un sub-agente con su propio file. Lo desarrollo en un brainstorming aparte si lo apruebas.
