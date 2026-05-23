# UI Modular — Empleados v3 (post-sprint Hot-fix backend)

**Fecha:** 2026-05-22
**Scope:** `apps/web/src/features/employees/*` + cruces a `dossierService`, `workspaceService`, `tenantContext`, tooling
**Audit previo:** v1 `2026-05-22-empleados.md` · v2 `2026-05-22-empleados-bd-poblada.md`
**Modo:** READ-ONLY (no edits)
**Confianza:** alta (estática; tsc + eslint corridos)
**Tiempo invertido:** ~25 min

---

## TL;DR — verdicts post-sprint

| Lente | Verdict v2 | Verdict v3 | Cambio |
|-------|------------|------------|--------|
| Diseño / consistencia VYNTIA | WARN | **WARN** | Sin cambios. Los 5 commits del sprint son 100% backend. Los hallazgos B1-B10 del v1 + los 3 P0 frontend del v2 **siguen idénticos**. |
| Modularidad comercial | FAIL (con matiz) | **FAIL** (idéntico) | Sin progreso. `TenantContext.tsx:15-21` sigue sin `plan`. Cero feature flags. El sprint backend NO añadió surface para gating. |
| **Riesgo nuevo introducido por sprint** | — | **🟠 medio** | El backend ahora retorna 403 PL gate, validaciones DNI/edad estrictas, y `permission_level__lte` filter. El frontend NO está preparado para ninguno de esos cambios. |

**Conclusión:** el sprint backend resolvió 12 P0/P1 a costa de **abrir 3 brechas FE nuevas** que el v2 no detectó. El frontend del módulo Empleados es ahora **menos consistente con el backend** que antes del sprint.

---

## 1. Re-verificación de los 3 hallazgos frontend del v2

### 1.1 `EmpleadosListPage.tsx:100` — ReferenceError de `isRRHH`/`isSupervisor`

**Estado:** ABIERTO sin cambio.

Evidencia:
- `EmpleadosListPage.tsx:60-67` destructura solo `permissions, canViewEmployeeList, getEmployeeFilter, canAccessEmployeeData, currentEmployeeId, isEmployee`.
- `EmpleadosListPage.tsx:100` referencia `isRRHH, isSupervisor, isEmployee` dentro de un `console.log`.
- **Ruteo:** `App.tsx:23, 322-326` ratifica que `/empleados` → `Empleados` (no `EmpleadosListPage`). El único importador real de `EmpleadosListPage` es el re-export en `pages/index.ts:8`.
- ESLint sobre el archivo: **sin warnings emitidos** (la config no atrapa `no-undef` para variables undef en console.log).

**Veredicto:** sigue siendo **deuda muerta** (página huérfana). Pero el archivo trae 29 console.log + 5 modales rotos enganchados. **Decisión recomendada: BORRAR** (`EmpleadosListPage.tsx` + `pages/index.ts:8` + `modals/Datos*Modal.tsx` ×4 + `modals/index.ts`). Si alguien lo reusa por accidente (ej. nuevo dev importa `from '@/features/employees/pages'` y autocomplete sugiere `EmpleadosListPage`), entra en runtime.

### 1.2 `HROverviewDashboard.tsx:479,496,589,658` — `p.status` vs `p.estado`

**Estado:** ABIERTO sin cambio. **Confirmado runtime-breaking con BD poblada.**

Run-trace con demo-pro (1 posting/aplicación etc., 0 planillas seedeadas):
- `usePlanillasMes()` (línea 140-152) hace `GET /api/v1/payroll/monthly-runs/?page_size=6` → con `demo-pro` sin planillas → `planillas = []` → branch `!planillas.length` (línea 472) → render "Sin planillas registradas". **OK sin data**.
- Si se seedean planillas con el shape de `MonthlyRunSerializer` (que emite `estado: 'borrador'`):
  - Línea 479 `(p.status ?? 'borrador').toLowerCase()` → `p.status` es `undefined` → fallback `'borrador'` → **PCT siempre 10%**.
  - Línea 496 `{p.estado_texto ?? p.status ?? '—'}` → `p.estado_texto` puede estar; si no, fallback a `—`.
  - Línea 589 `(latest.status ?? '').toLowerCase()` → string vacío → ninguna alerta tipo "aprobada/pagada/calculada/borrador/anulado" se dispara → KPI alert engañoso.
  - Línea 658 `(latestPlanilla?.status ?? 'borrador').toLowerCase()` → siempre `'borrador'` → KPI barra siempre 10%.

**Decisión recomendada:** P0. Reemplazar `p.status` → `p.estado` en las 4 líneas (la interface ya declara `estado?`, línea 69). 10 min de fix. Riesgo cero.

### 1.3 5 imports rotos `@/shared/ui/loading-spinner`

**Estado:** ABIERTO sin cambio. **Confirmados los 5/5** (grep en §0):

```
EmpleadosListPage.tsx:19
modals/DatosFamiliaresModal.tsx:25
modals/DatosLaboralesModal.tsx:23
modals/DatosAcademicosModal.tsx:25
modals/DatosPersonalesModal.tsx:23
```

Run de `npx tsc --noEmit` desde `apps/web/`:
```
tsconfig.json(8,27): error TS5103: Invalid value for '--ignoreDeprecations'.
```

**Confirmado:** `tsconfig.json:8` (`"ignoreDeprecations": "6.0"`) hace que `tsc` aborte ANTES de typechecking. **El repo lleva semanas sin red de seguridad de tipos.** ESLint sobre `features/employees/` también pasa silencioso. Los 5 imports rotos son completamente invisibles a la toolchain actual.

**Acción urgente:** corregir `tsconfig.json:8` a `"5.0"` o eliminar la línea (TS 5.x deprecated `--ignoreDeprecations`). Tras el fix, tsc va a empezar a reportar estos 5 errores + posiblemente otros que el repo lleva ocultos.

---

## 2. Modularidad — verificación post-sprint

### 2.1 ¿Hubo progreso?

**No.** Inventario sin cambios desde v2:

| Pieza | Estado v2 | Estado v3 |
|-------|-----------|-----------|
| `Tenant.plan` BE | ✅ Existe | ✅ Existe |
| `/api/v1/workspaces/` devuelve `plan` | ✅ Existe (`workspaceService.ts:3-9` declara `plan: string`) | ✅ Existe |
| `useFeature(flag)` hook | ❌ | ❌ |
| `<ModuleGate>` componente | ❌ | ❌ |
| `TenantContext.tsx` expone `plan` | ❌ | ❌ (verificado, líneas 15-21) |
| Sidebar / `menuService` filtra por módulo | ❌ | ❌ |

`TenantContext.tsx` sigue siendo idéntico: 70 líneas, solo `{type, slug, host}`. **Ninguna llamada a `/api/v1/workspaces/` desde el TenantProvider.** El frontend, para fines de modularidad, está exactamente donde estaba en v1.

### 2.2 Test de bloqueo (idéntico v2)

| URL | Tenant `demo-pro` (plan=pro) | Tenant hipotético `demo-starter` |
|-----|------------------------------|-----------------------------------|
| `/empleados` | Renderiza completo (correcto pro) | **Incorrecto:** renderiza completo |
| `/empleados/reporte/:id` | Renderiza PDF | **Incorrecto:** renderiza |
| `/recruitment/jobs` | Renderiza (B.9) | **Incorrecto:** renderiza (debería ser `hire` only) |
| `/legajos-digitales` | Renderiza (B.12) | **Incorrecto:** renderiza |

**0/4 bloqueos correctos.** El sprint no movió esta aguja.

---

## 3. Hallazgos NUEVOS — el sprint backend tocó endpoints que el FE consume sin filtro

### 3.1 🟠 `dossierService.downloadConsolidatedPdf` no maneja 403 PL gate

**Severidad:** ALTA · **Archivo:** `apps/web/src/features/documents/services/dossierService.ts:127-132` · **Llamado desde:** `DigitalDossierListPage.tsx:60`

El sprint Block B (commit `78a6895a`) cerró #118: ahora `consolidated_pdf` invoca `access_service.can_access()` y retorna **403 con `APIResponse.error()`** cuando el `permission_level` del user es insuficiente.

**Problema FE:** el método pide `responseType: 'blob'`. Cuando el servidor retorna 403 con JSON body (`{success: false, message: "Sin permisos para PL 9"}`), axios devuelve un `Blob` con el JSON serializado dentro, NO un objeto error parseado. El `catch` en `DigitalDossierListPage.tsx:62-65` solo hace:

```ts
toast.error(`Error descargando: ${e instanceof Error ? e.message : 'desconocido'}`)
```

→ El usuario verá `"Error descargando: Request failed with status code 403"`, NO el mensaje legible del backend. El mensaje útil (`"Sin permisos para PL 9"`) queda atrapado dentro del blob.

**Patrón correcto** (no aplicado):
```ts
catch (e) {
  if (e.response?.status === 403 && e.response?.data instanceof Blob) {
    const text = await e.response.data.text()
    const json = JSON.parse(text)
    toast.error(json.message ?? 'Sin permisos')
  } else { ... }
}
```

`errorUtils.ts:68-70` ya expone `isAuthorizationError(error)`. **Cero call sites lo usan** (grep en `features/` → no matches).

### 3.2 🟠 Validaciones DNI/edad: backend ahora estricto, frontend permisivo

**Severidad:** MEDIA · **Archivo:** `apps/web/src/features/employees/pages/Empleados.tsx:184-201` (NuevoEmpleadoDialog)

El sprint Block A (commit `d07155c6`) movió `validate_numero_documento` y `validate_fecha_nacimiento` a `EmpleadoCreateSerializer`. Ahora:
- DNI `"1234567"` (7 dígitos) → 400
- DNI `"ABC12345"` → 400
- Edad < 18 → 400

**Problema FE:** `Empleados.tsx:184-188` solo valida truthy:
```ts
if (!form.nombres_empleado || !form.apellido_paterno || !form.numero_documento || !form.correo_personal) {
  toast.error('Completa los campos obligatorios')
  return
}
```

No hay regex de DNI, no hay date picker con `max=today-18y`, no hay maxLength=8 estricto (el `Input` línea 251 usa `maxLength={12}` para soportar también CE/pasaporte). El usuario puede teclear "ABC" y el form intenta POST → backend responde 400 → toast genérico vía `getErrorMessage`. 

**El mensaje de error de DRF se propaga** porque `getErrorMessage` (`errorUtils.ts:17-32`) sabe leer `data.errors[fieldKey]`. Verificable: si DRF responde `{success:false, errors:{numero_documento:["DNI debe tener 8 dígitos"]}}`, el toast mostrará "DNI debe tener 8 dígitos". **Aceptable como UX mínima**, pero ideal sería validación inline en el form para feedback inmediato.

### 3.3 🟡 `permission_level__lte` filter en DigitalDocument: el FE no muestra empty state diferenciado

**Severidad:** MEDIA-BAJA · **Archivo:** `apps/web/src/features/documents/pages/DigitalDossierListPage.tsx`

El backend ahora filtra documentos por `permission_level__lte=user_level`. Un usuario `nivel_acceso='personal'` (level bajo) verá la misma URL **con menos resultados** que un admin.

**Problema FE:** No hay UI que comunique "estás viendo X de Y documentos según tu nivel de acceso". El user puede pensar que faltan documentos cuando en realidad están filtrados por seguridad. Tampoco hay banner ni tooltip. La lista simplemente se ve "vacía" o "incompleta" sin explicación.

**Fix sugerido (no urgente):** badge en el header de la lista con tooltip explicando el filtro PL.

### 3.4 🟡 Hardcoded legacy URLs en `src/generated/api/services/RrhhService.ts`

**Severidad:** BAJA (código generado, no activo) · **Archivo:** `src/generated/api/services/RrhhService.ts:69-620`

30+ paths con prefijo `/api/v1/rrhh/...` (legacy pre-L3 split). El L3 movió esto a `/api/v1/employees/`, `/api/v1/family-members/`, `/api/v1/academic-records/`, `/api/v1/employment-data/`. **Si algún componente usa el cliente generado en lugar de los services manuales, los endpoints van a fallar con 404.**

Grep rápido confirma que las `pages/` y `features/employees/services/employeesService.ts` usan los paths nuevos (líneas 118, 221, 249, 309). **El cliente generado parece muerto**, pero su existencia es trampa potencial. Acción: regenerar OpenAPI client o borrar `src/generated/`.

### 3.5 🟡 `EmpleadoReportPage.tsx:123` — cast `Number(id)` con UUID

**Severidad:** BAJA · ya reportado en v1 (B6) — sigue ABIERTO.

El sprint Block D (commit `59fa55d8`) fixeó el reporte PDF backend (`carrera_especialidad` + ImportError). Ahora el reporte de 6516 bytes se genera correctamente. **Pero `EmpleadoReportPage.tsx:123` hace `Number(id)`.** Si `id` es un UUID string (post-sub-C los empleados pueden tener `id` UUID en serializers nuevos), `Number("550e8400-...")` → `NaN` → `getEmpleadoDetail(NaN)` → 404 backend.

Verificable solo con BD poblada — en demo-pro los IDs son ints todavía, así que el bug está latente pero no observable hoy.

---

## 4. Sketch refinado para sub-proyecto E (Modularidad)

Versión refinada del sketch v2 §2.2, con paths exactos y orden de cableado:

### 4.1 Arquitectura (no implementar hoy)

**Catálogo** — `apps/web/src/shared/features/catalog.ts` (nuevo, ~30 LOC):

```ts
export type FeatureKey =
  | 'employees.core'        // lista + datos personales/laborales
  | 'employees.advanced'    // familiares + académicos + report PDF
  | 'contracts.basic'
  | 'contracts.amendments'
  | 'documents.basic'
  | 'documents.legajo'      // B.12 DigitalDossier
  | 'pay'                   // futuro D
  | 'time_off'
  | 'onboarding'
  | 'hire'                  // B.9 ATS
  | 'insights'              // dashboards cruzados
  | 'pulse'

export const PLAN_MODULES: Record<string, Set<FeatureKey>> = {
  starter:    new Set(['employees.core','contracts.basic','documents.basic']),
  pro:        new Set([...starter,'employees.advanced','contracts.amendments',
                       'documents.legajo','pay','time_off','onboarding']),
  enterprise: new Set([...pro, 'hire','insights','pulse']),
  govtech:    new Set([...enterprise].filter(k => k !== 'hire')),
}
```

**Hook + componente** — `apps/web/src/shared/features/` (nuevo, ~40 LOC):

```ts
// useFeature.ts
export function useFeature(key: FeatureKey): boolean {
  const { plan } = useTenant()  // <-- TenantContext debe exponer plan
  return plan ? (PLAN_MODULES[plan]?.has(key) ?? false) : true  // fail-open mientras carga
}

// ModuleGate.tsx
export function ModuleGate({ module, fallback, children }) {
  return useFeature(module) ? <>{children}</> : (fallback ?? <UpgradePrompt module={module} />)
}
```

**Modificar `TenantContext`** — `apps/web/src/shared/tenant/tenantContext.tsx:15-21`:

```diff
 export interface TenantContextValue {
   type: TenantHostType
   slug: string
   host: string
+  plan?: 'starter'|'pro'|'enterprise'|'govtech'
+  isLoading: boolean
 }
```

Hidratación: en `TenantProvider`, hacer `useQuery(['workspace', slug], () => fetchWorkspaces())` y matchear el current slug → setear `plan`. Reusa `workspaceService.fetchWorkspaces` que **ya existe**.

### 4.2 Cableado mínimo (orden de ROI)

1. **`Empleados.tsx:122-148`** — esconder tabs Familiares + Académicos si `!useFeature('employees.advanced')`. Ajustar `grid-cols-4` → dinámico. **+15 min**.
2. **`Empleados.tsx:560-587`** — envolver "Legajo Digital" y "Constancia/Certificado" en `<ModuleGate module="documents.legajo">`. **+10 min**.
3. **`EmpleadoReportPage.tsx`** entero — wrap `<ModuleGate module="employees.advanced">`. El reporte integral es Pro+. **+5 min**.
4. **`App.tsx:83-89, 111, 527`** — envolver lazy routes B.9 (`/recruitment/*`, `/candidates-dashboard`) en `<ModuleGate module="hire">`; B.12 (`/legajos-digitales`) en `<ModuleGate module="documents.legajo">`. **+10 min**.
5. **Sidebar** (`apps/web/src/shared/api/menuService.ts`) — agregar al `MenuItem` shape un `requiredFeature?: FeatureKey`; filtrar en `filterMenuByPermissions`. **+20 min**.

### 4.3 UpgradePrompt — componente

`apps/web/src/shared/features/UpgradePrompt.tsx` (nuevo, ~50 LOC). Mockup detallado en v1 §5.

### 4.4 Estimación realista

| Pieza | LOC | Tiempo |
|-------|-----|--------|
| Catálogo + tipos | 30 | 15 min |
| TenantContext + hidratación con `/workspaces` | 25 | 30 min |
| `useFeature` + `ModuleGate` | 40 | 30 min |
| `UpgradePrompt` (con copy + mockup) | 50 | 45 min |
| Cableado de 5 puntos (§4.2) | 60 | 1 h |
| `seed_demo_starter.py` para tests E2E | 40 | 30 min |
| Test vitest del catálogo + ModuleGate | 60 | 1 h |
| **Total MVP** | **~305 LOC** | **~4.5 h** |

**Encaja en 1 día de trabajo focused.** Mucho más liviano que el "5-8 días sub-proyecto independiente" que estimé en v1 §3.6.

---

## 5. Top-3 acciones priorizadas

| # | Prio | Tipo | Acción |
|---|------|------|--------|
| 1 | **CORTO P0** (15 min) | Tooling + Bug | Fix `tsconfig.json:8` (`"6.0"` → `"5.0"` o eliminar) y, una vez tsc emita errores, arreglar los 5 imports `@/shared/ui/loading-spinner` → `@/shared/components/LoadingSpinner`. Sin el tsc fix, cualquier futura regresión de tipos queda invisible. |
| 2 | **CORTO P0** (10 min) | Bug runtime | `HROverviewDashboard.tsx:479, 496, 589, 658` — reemplazar `p.status` → `p.estado` (o `latest.status` → `latest.estado`). Con planillas reales, el dashboard de Pay muestra 10% siempre y alerts mudas. |
| 3 | **MEDIO** (4.5 h) | Modularidad | Sub-proyecto E — cablear `<ModuleGate>` mínimo según §4. Pre-requisito comercial para vender Starter vs Pro. **Antes** de arrancar D (Vyntia Pay), para que Pay nazca detrás del gate. |

**Acciones secundarias (no top-3 pero pendientes):**
- Cerrar deuda muerta: borrar `EmpleadosListPage.tsx` + 4 modales + sus entries en `pages/index.ts` y `modals/index.ts` (29 console.log + 5 imports rotos desaparecen de un golpe).
- Agregar handler 403 a `dossierService.downloadConsolidatedPdf` (parsear Blob → mensaje legible). Usar el helper `isAuthorizationError` que ya existe.
- Validación frontend mirror para DNI (regex `^\d{8}$` o `^[A-Z0-9]{8,12}$`) y edad min en NuevoEmpleadoDialog.
- Borrar `src/generated/api/services/RrhhService.ts` (30+ paths legacy `/api/v1/rrhh/`) — riesgo de uso accidental.
- Cast UUID en `EmpleadoReportPage.tsx:123` — eliminar `Number(id)`, pasar string directo.
- Banner explicando filtro PL en `DigitalDossierListPage`.

---

## 6. Cambios aplicados

Ninguno. READ-ONLY conforme al brief.

---

## 7. Pregunta pendiente al humano

Sigo recomendando lo mismo que v1+v2: **sub-proyecto E (Modularidad) antes de D (Vyntia Pay)**. La estimación bajó de 5-8 días a 4.5 horas con el inventario refinado en §4. Pay será siempre premium; nace mejor detrás del gate desde el primer commit.

**Pregunta concreta:** ¿abro brainstorm para E ya, o consolido primero un sprint de "Frontend Hot-fix" (los 2 P0 de §5 #1+#2 + cleanup de página huérfana) que limpie deuda visible antes de meter feature flags encima?
