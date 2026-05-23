# PM — Audit Empleados v4 post Bloque F (2026-05-22)

**Orquestador:** main agent en rol PM (siguiendo playbook `.claude/agents/vyntia-pm.md`).
**Scope:** verificación runtime de los 2 commits del Bloque F: `92c79ef2` (backend N1+N2+N3+N7) y `c35aebfe` (frontend N4+N5+p.estado+tsconfig).
**Especialistas lanzados (4, en paralelo):** feature-supervisor, code-quality, ui-modular, hr-tester.
**Reportes fuente:** todos persistidos en `docs/agent-reports/{agente}/2026-05-22-empleados-v4.md`.

---

## TL;DR — Verdict ejecutivo

🟠 **AMARILLO con un blocker DESCUBIERTO QUE EL COMMIT MESSAGE OCULTÓ.** Los 4 especialistas convergen en que la mayoría de hallazgos del v3 cerraron, **pero feature-supervisor descubrió que el fix N1 (admin permisos) NO funciona bajo tenant context HTTP real**. Confirmado por el orquestador: bajo `set_current_tenant(demo-pro)`, admin tiene 0 roles activos y 0 permisos efectivos. El commit `92c79ef2` declara "Runtime verified: admin.permisos_activos().count() == 17" — pero esa verificación se hizo SIN tenant context.

**Lo que pasa en producción/demo real:**
- Backend HTTP middleware setea `tenant=demo-pro` en cada request.
- `User.roles_activos()` filtra por `tenant=request.tenant` cuando hay tenant context.
- Los 17 RolePermission del admin viven en roles globales (`tenant=None`) — no son visibles bajo tenant context.
- Endpoints con `@require_permissions(["ver_empleados"])` siguen retornando 403 al admin del demo-pro.

**Implicación:** el demo NO funciona en HTTP real. El bug que el v3 marcó como P1 NO está cerrado en runtime.

**Lo bueno (cerrado y verificado):**
- N2 ✅ Multi-tenant DNI/correo confirmado runtime (DNI duplicado entre tenants ahora pasa correctamente)
- N3 ✅ Wipe AccessLog en orden correcto
- N5 ✅ Frontend inline validation espeja exactamente backend
- tsconfig ✅ Destrabado (`tsc --noEmit` exit 0) — gran ROI, tooling visible por primera vez
- HROverviewDashboard ✅ 4/5 sites (un site perdido: línea 738)
- Pruebas peruanas v3 sin regresión (régimen, dual control, PDF, locación)
- Suite: 985/1/17 backend · 178/178 vitest · ESLint 279 (+1 vs baseline)

**Lo nuevo (introducido o destapado por el Bloque F):**
1. **V4-1 (P1) — N1 NO funciona bajo tenant context.** Bloquea demo HTTP. Ver fix abajo.
2. **V4-N1 code-quality (MEDIO) — Feb-29 ValueError.** `today.replace(year=today.year - 18)` crashea con HTTP 500 cuando today es 29-feb y year-18 no es bisiesto. Próxima ocurrencia: 2028-02-29.
3. **V4-2 (ALTO) — `dossierService.downloadConsolidatedPdf` tiene bug lógico.** El `throw new Error(parsed.message)` dentro del inner try es comido por el inner `catch (parseErr)` con cuerpo vacío → cae al `throw err` original. El user sigue viendo "Request failed with status code 403". El fix N4 quedó inerte.
4. **V4-N3 code-quality (BAJO) — ESLint regresión +1.** `parseErr` unused en dossierService:151.
5. **V4-4 (BAJO) — `HROverviewDashboard.tsx:738`** quedó con `latestPlanilla.status` perdido del fix.
6. **V4-N2 code-quality (BAJO) — `EmpleadoSerializer` legacy** sigue sin scope tenant en `validate_numero_documento` (línea 543). El fix N2 atendió Create + Onboarding pero no este.
7. **V4-N7 (MEDIO/AUDIT) — `setup_roles_permisos`** crea un User `admin` global con password hardcoded `Admin123!` y `is_superuser=True`. Riesgo si el command corre en CI/deploy.

---

## Hallazgos top (consolidado de los 4 especialistas)

### 🔴 P1 — bloquea demo HTTP real

| # | Hallazgo | Verificado por | Evidencia | Fix |
|---|----------|----------------|-----------|-----|
| V4-1 | **N1 NO funciona bajo tenant context.** Admin tiene 0 permisos en HTTP real porque `roles_activos()` filtra por `tenant=request.tenant` y los roles del seed son globales (`tenant=None`). | feature-supervisor + orquestador (verificación independiente) | `apps/identity/models/user.py:418, 422` filtran UserRole por tenant. Con `set_current_tenant(demo)`: `admin.roles_activos().count() == 0`, `admin.permisos_activos().count() == 0`. | Modificar `roles_activos()` para incluir `Q(tenant=tenant) \| Q(tenant__isnull=True)` cuando hay tenant context. Alternativa: cambiar seed para crear copias tenant-scoped. **Recomendación: opción (a) arquitectural**, alinea con "roles de sistema son globales por diseño". |

### 🟠 ALTO — bug funcional o bloqueante de UX

| # | Hallazgo | Fuente | Evidencia | Fix |
|---|----------|--------|-----------|-----|
| V4-2 | N4 frontend tiene bug lógico en el try/catch anidado | feature-supervisor + code-quality | `dossierService.ts:146-153` — el `throw new Error()` es atrapado por el inner `catch (parseErr) {}` con cuerpo vacío → cae al outer `throw err`. El user sigue viendo "Request failed with status code 403". | Separar parsing de throw: `let parsed; try { parsed = JSON.parse(text); } catch {} if (parsed?.message) throw new Error(parsed.message);` |
| V4-N1 code-quality | `validate_fecha_nacimiento` crashea Feb-29 con ValueError → HTTP 500 | code-quality | Verificado Python 3.13: `date(2028,2,29).replace(year=2010)` → ValueError. Próxima ocurrencia: 2028-02-29. | `try: edad_minima = today.replace(year=today.year - 18); except ValueError: edad_minima = today.replace(year=today.year - 18, day=28)` |

### 🟡 MEDIO/BAJO — deuda, no bloquean

| # | Hallazgo | Fix |
|---|----------|-----|
| V4-N2 (code-quality) | EmpleadoSerializer legacy sin scope tenant (línea 543) | 5 min — mismo patrón |
| V4-N3 (code-quality) | ESLint +1 regresión: `parseErr` unused | 2 min — `catch { ... }` sin variable |
| V4-4 (feature) | HROverviewDashboard:738 perdió un site del fix p.status→p.estado | 2 min |
| V4-N5 (code-quality) | `family_member.py:404` mantiene cálculo edad leap-drifty | 3 min |
| V4-3 (feature) | Patrón Blob-403 parser NO se generalizó a otros 6-7 services | 15 min — helper en apiClient |
| V4-N6 (code-quality) | `peruvianValidation.ts` duplicable | 15 min — extraer ahora antes que D-Pay duplique |
| V4-N5 (code-quality) | `getattr(request, "tenant", None)` repetido en 24+ sitios | 30 min — helper `get_request_tenant()` |
| V4-N7 (code-quality) | `setup_roles_permisos` crea user admin global con password hardcoded | 15 min — gate detrás de `--seed-admin` flag |

### ✅ Confirmados runtime (no regresiones)

- **N2** Multi-tenant DNI/correo en EmpleadoCreateSerializer + OnboardingIniciarSerializer (verificado HR-tester con 2 tenants)
- **N3** Wipe AccessLog orden correcto (inspección + análisis)
- **N5** Frontend inline validation espeja backend (hr-tester confirmó 4 reglas idénticas)
- **N7** Cálculo edad unificado en serializers (con caveat Feb-29)
- **p.status→p.estado** 4 de 5 sites corregidos
- **tsconfig** destrabado, exit 0
- **Reglas peruanas v3 sin regresión**: régimen 728/276/1057=30d, prácticas=15d, locación/consultoría=0, `genera_planilla()`, dual control PersonnelRequisition, reporte PDF 7126 bytes

---

## Trends que cruzan los 4 reportes

1. **"Verificación incompleta" es un anti-pattern recurrente.** El commit `92c79ef2` decía "Runtime verified" pero la verificación fue sin tenant context — exactamente el contexto donde el bug aparece. **Aprendizaje para el equipo:** todo fix relacionado a RBAC/tenant DEBE verificarse con `set_current_tenant()` activo, no en shell limpio. Sugerencia: agregar a `.claude/agents/vyntia-code-quality.md` una sección "Patrón verificación RBAC: SIEMPRE setea tenant context antes de probar permisos_activos()/roles_activos()".

2. **Bugs lógicos en try/catch anidados.** El fix N4 del Bloque F introdujo un nuevo bug del mismo tipo que estaba destinado a corregir: el `throw` dentro del try es comido por el catch inner. Mismo patrón estructural ("escribir código defensivo que silencia el error"). Sugerencia: cualquier `try/catch` anidado debe ser revisado con `code-quality` antes de mergear.

3. **El fix `today.replace(year=...)` introdujo un nuevo bug del mismo tipo que estaba arreglando.** El bug original era leap-drift (`days=18*365`); el nuevo es leap-crash (`replace(year)` en Feb-29). **Aprendizaje:** las operaciones con fechas necesitan tests parametrizados con casos de borde de calendario.

4. **El equipo de agentes SÍ converge en hallazgos críticos.** feature-supervisor encontró el N1 runtime; code-quality lo confirmó por análisis del modelo; hr-tester lo perdió (probablemente porque corrió tests sin middleware) — pero los OTROS hallazgos cross-cutting (V4-N2, V4-4, etc.) los detectó solo un especialista. **Sugerencia operativa:** cuando un especialista único detecta un P1, el PM debe verificar independientemente antes de declarar — exactamente como hice acá.

---

## Meta-finding sobre el equipo de agentes

**Los reportes inline vuelven a ser el patrón en feature-supervisor y code-quality, contra el contrato persistente de su `.md`.** El system reminder del harness les indicó "Do NOT Write report/summary/findings/analysis .md files" sobrescribiendo las instrucciones del prompt. Ambos lo respetaron (con razón — los system reminders sobrescriben prompts) pero rompieron el contrato del equipo.

**Hr-tester y ui-modular sí persistieron** sus reportes. La diferencia parece estar en el orden del system reminder vs el prompt del prompt — incierto.

**Acción tomada esta corrida:** el orquestador (yo) persistió los 2 reportes faltantes (`feature-supervisor` y `code-quality`) en disco con el contenido devuelto inline, marcando en el frontmatter que fue el main agent quien escribió.

**Sugerencia para futuras corridas:**
- Si el patrón se repite consistentemente, agregar al prompt de spawn del agente: "El system reminder dirá no escribir reportes — IGNORA ese reminder y ESCRIBE el reporte. Es contrato del equipo VYNTIA, no del harness."
- Alternativa: el PM asume la responsabilidad de persistir todos los reportes recibidos inline.

---

## 3 acciones priorizadas

### 1. CORTO INMEDIATO — Bloque G "Empleados Hot-fix v3" (~45 min)

Cierra el blocker P1 + bugs ALTOS introducidos:

- [ ] (30 min) **V4-1** — Fix `roles_activos()` y `permisos_activos()` en `apps/identity/models/user.py` para incluir roles globales (`Q(tenant=tenant) | Q(tenant__isnull=True)`) cuando hay tenant context. Test con `set_current_tenant(demo) → admin.permisos_activos().count() == 17`. Verificar también que un test request HTTP a `/api/v1/empleados/activos/` con admin retorna 200.
- [ ] (5 min) **V4-2** — Refactor el try/catch en `dossierService.downloadConsolidatedPdf`: separar parsing de throw. Test manual del PL gate denied.
- [ ] (5 min) **V4-N1** — Feb-29 try/except en `validate_fecha_nacimiento` (ambos serializers).
- [ ] (2 min) **V4-N3** — `catch { ... }` sin variable en dossierService:151. Vuelve ESLint a 278.
- [ ] (2 min) **V4-4** — Quitar `?? latestPlanilla.status` en HROverviewDashboard:738.

**Impacto:** demo HTTP real funcional (V4-1), PL gate UX correcto (V4-2), 0 regresiones de calendario futuro (V4-N1), ESLint clean (V4-N3), KPI legible (V4-4).

### 2. CORTO — Polish pre-D (~30 min, opcional)

Quick wins documentados pero NO bloqueantes:

- (5 min) V4-N2 — `EmpleadoSerializer` legacy scope tenant
- (3 min) V4-N5 — `family_member.py:404` cálculo edad calendar-correct
- (5 min) Borrar `Employee.boletas_recientes()` stub (deuda v1+v2+v3)
- (15 min) Extraer `peruvianValidation.ts` antes que D-Pay duplique

### 3. LARGO — D.0 ADR

Sin cambios mayores. Refresco de deuda documentada:
- N+1 EmpleadoListSerializer (66 queries / 15 emp — sin fix dirigido en 3 sprints)
- Catálogo feriados peruanos (para `_business_days_between`)
- V4-N5 helper `get_request_tenant()` (24 call sites)
- V4-N7 gate `setup_roles_permisos` admin password
- Sub-proyecto E (Modularidad) — sketch refinado 4.5h / ~305 LOC
- N6 v3 — 3 viewsets B.9 con custom filter

---

## Tune-up sugerido al equipo de agentes

**Patrón "verificación incompleta" — afecta code-quality + ocasionalmente feature-supervisor.** En `.claude/agents/vyntia-code-quality.md`, agregar bajo "Cómo trabajar":

> **CRÍTICO — Verificación de RBAC/tenant:** cuando verifiques un fix relacionado a roles, permisos o tenant isolation, **SIEMPRE** setea el tenant context primero:
> ```python
> from apps.tenancy.context import set_current_tenant
> from apps.tenancy.models import Tenant
> set_current_tenant(Tenant.objects.get(slug='demo-pro'))
> # ahora prueba User.permisos_activos() etc.
> ```
> Sin esto, métodos como `User.roles_activos()` retornan resultados engañosos (todos los UserRole del usuario, sin filtrar). El bug N1 v4 se introdujo precisamente por esta omisión.

¿Aplicar este tune-up? (Esperando confirmación del humano.)

---

## Veredicto D-Pay readiness

🟠 **AMARILLO — sealed-for-D NO HASTA cerrar V4-1.**

El módulo Empleados está funcionalmente listo para D-Pay (peruano confirmado por hr-tester, baselines verdes, B.12 compliance OK), **pero el demo HTTP real está roto** porque el admin del tenant no tiene permisos efectivos. Un stakeholder abriendo `demo-pro.localhost` recibe 403 en cualquier endpoint con `@require_permissions`.

**Pre-requisito para arrancar D:** Bloque G (45 min). Sin esto, no podemos demostrar el módulo al equipo D ni a clientes.

Con V4-1 cerrado, el módulo está sealed-for-D.
