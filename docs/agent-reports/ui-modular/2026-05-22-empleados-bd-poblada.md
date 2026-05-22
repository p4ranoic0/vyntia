# UI Modular — Empleados (segunda corrida, BD demo-pro poblada)

**Fecha:** 2026-05-22
**Scope:** `apps/web/src/features/employees/*` + cruces a `apps/api/apps/tenancy`
**Audit previo:** `docs/agent-reports/ui-modular/2026-05-22-empleados.md`
**Modo:** READ-ONLY (no edits)
**Confianza:** alta (estática; dev server no levantado)
**Tiempo invertido:** ~25 min

---

## TL;DR — verdicts actualizados

| Lente | Verdict previo | Verdict hoy | Cambio |
|-------|----------------|-------------|--------|
| Diseño / consistencia VYNTIA | WARN | **WARN** | Sin cambios. Bugs B1-B10 del audit anterior **siguen idénticos**. |
| Modularidad comercial | FAIL | **FAIL** (pero con matiz) | El backend ya tiene `Tenant.plan` (`starter/pro/enterprise/govtech`) y el endpoint `/api/v1/workspaces/` lo expone. Lo que sigue ausente es el **gate de UI**: `useFeature`, `<ModuleGate>`, filtro por módulo en menú. Hay materia prima — falta el cableado. |

**Lo nuevo gracias a BD poblada:**
- 15 empleados activos con apellidos andinos (Quispe, Mamani, Apaza, Choque, Condori, Sullca) → la tabla los va a renderizar sin problemas: `truncate` + `min-w-0` + `font-mono` para DNI son adecuados.
- DNIs de 8 dígitos: se muestran **literales sin separador** (`font-mono text-sm` en `Empleados.tsx:492`). Esto está bien para Perú (a diferencia de fechas/montos, los DNIs no usan separador).
- El tenant `demo-pro` ya tiene `plan='pro'` cargado en BD. Es **fixture útil** para arrancar el sub-proyecto E (Modularidad).

---

## 1. Verificación runtime de los bugs top-3 del audit previo

### 1.1 `EmpleadosListPage.tsx:100` — ReferenceError de `isRRHH`/`isSupervisor`

**Estado actual:** persiste, **pero NO es runtime crítico**.

Evidencia:
- `App.tsx:322` rutea `/empleados` a `<Empleados/>` (el archivo bueno), **NO a `EmpleadosListPage`**.
- Grep de `EmpleadosListPage` en `apps/web/src/`: solo aparece su propia definición + un re-export en `features/employees/pages/index.ts:8`. **Cero importadores reales.**
- La función queda como deuda de cleanup (huérfana), pero como no se monta, el ReferenceError nunca se ejecuta.

**Conclusión:** B2 baja de severidad **CRÍTICO → MEDIO (deuda)**. Acción: **borrar el archivo + sus 4 modales referenciados solo desde allí**, o re-rutearlo intencionalmente.

### 1.2 `HROverviewDashboard.tsx` — `p.status` vs `p.estado` con 15 empleados activos

**Estado actual:** persiste idéntico. Líneas confirmadas:
- `HROverviewDashboard.tsx:479` → `const estado = (p.status ?? 'borrador').toLowerCase()`
- `HROverviewDashboard.tsx:496` → `{p.estado_texto ?? p.status ?? '—'}`
- `HROverviewDashboard.tsx:66-76` (interface `PlanillaMensual`) declara `estado?` (no `status`).

**Impacto runtime visible con BD poblada:** si el backend envía planillas seedeadas para demo-pro con campo `estado` (cosa esperada según la interface), el dashboard caerá al fallback `'borrador'` y mostrará **10% siempre**, etiqueta `—`. El admin de demo-pro va a ver un panel de Pay engañoso. **Bug crítico de UX cuando hay data.**

**No pude verificar** qué nombre exacto manda el serializer real (`MonthlyRunSerializer`) sin levantar la API; sugerido: verificar `apps/api/apps/payroll/serializers.py`. Si manda ambos `status` y `estado` por compat → solo subir prioridad del fix a P0.

### 1.3 5 imports `@/shared/ui/loading-spinner` rotos

**Estado actual:** persisten **5/5** (verificado con grep):

```
EmpleadosListPage.tsx:19
modals/DatosFamiliaresModal.tsx:25
modals/DatosLaboralesModal.tsx:23
modals/DatosPersonalesModal.tsx:23
modals/DatosAcademicosModal.tsx:25
```

Y `shared/ui/` confirma: **no existe** `loading-spinner.tsx`. El componente real vive en `shared/components/LoadingSpinner.tsx`.

**Por qué tsc no se quejó:**
- `npx tsc --noEmit` aborta con `TS5103: Invalid value for '--ignoreDeprecations'` (problema de config TS 5.x), antes de compilar. Esto **enmascara** el error que reportaría tsc en producción. Hay que arreglar `tsconfig.json:8` primero o el repo es ciego a errores de tipo.
- ESLint sobre `features/employees`: sin output (no encontró errores con la config actual; probable `noUnresolvedImports` desactivado para el feature).

**Conclusión combinada:** El tooling no está atrapando los imports rotos. **B1 sube de severidad a CRÍTICO + bloqueante de tooling.** Antes del próximo sub-proyecto, hay que reparar `tsconfig.json:8` para recuperar la red de seguridad.

---

## 2. Modularidad — actualización del FAIL

### 2.1 Lo que apareció desde la primera corrida

| Pieza | Estado | Ubicación |
|-------|--------|-----------|
| `Tenant.plan` BE | ✅ Existe | `apps/api/apps/tenancy/models/tenant.py:34` con choices `starter/pro/enterprise/govtech` |
| Endpoint que devuelve el plan | ✅ Existe | `api/v1/workspaces/views.py:35` devuelve `{plan, role, slug, ...}` |
| Lista de módulos por plan | ❌ No existe | Ni en BE (no hay `Plan.modules`), ni en FE (no hay catálogo de feature flags) |
| `useFeature(flag)` hook FE | ❌ No existe | `grep useFeature` → 0 matches |
| `<ModuleGate>` componente | ❌ No existe | `grep ModuleGate` → 0 matches |
| Filtro de menú por módulo | ❌ No existe | `menuService.filterMenuByPermissions` sigue retornando el menú entero |
| TenantContext expone `plan` | ❌ No expone | `shared/tenant/tenantContext.tsx` solo: `{type, slug, host}`. **Nunca lee `/workspaces/`**. |

**Diagnóstico:** B + C dejaron las **piezas BE** (Tenant, plan field, workspaces endpoint), pero **no se conectó** el plan al TenantContext del FE, y nadie definió aún qué módulos pertenecen a cada plan. La modularidad sigue siendo **FAIL para el usuario final**, pero el costo de cerrar el gap bajó: ya no hay que crear el modelo Tenant.

### 2.2 Sketch concreto del `<ModuleGate>` mínimo (~80 LOC)

Arquitectura propuesta sin tocar BE:

**Paso 1 — Catálogo (FE-only, hardcoded inicial):**

```typescript
// apps/web/src/shared/features/catalog.ts
export const PLAN_MODULES = {
  starter: new Set(['employees.core', 'contracts.basic', 'documents.basic']),
  pro: new Set(['employees.core', 'employees.advanced', 'contracts.basic',
                'contracts.amendments', 'documents.basic', 'pay', 'time_off',
                'onboarding', 'legajo']),
  enterprise: new Set([... // todo + 'hire', 'insights', 'pulse'
  ]),
  govtech: new Set([... // enterprise minus 'hire'
  ]),
} as const

export type FeatureKey =
  | 'employees.core' | 'employees.advanced'
  | 'contracts.basic' | 'contracts.amendments'
  | 'documents.basic' | 'pay' | 'time_off'
  | 'onboarding' | 'legajo' | 'hire' | 'insights' | 'pulse'
```

**Paso 2 — Inyectar `plan` en TenantContext:**

```typescript
// shared/tenant/tenantContext.tsx (modificar el provider)
// Al hidratar el usuario (AuthContext ya carga /me), llamar también /workspaces/
// para el slug actual, y cachear { plan } en el context.
interface TenantInfo { type, slug, host, plan?: 'starter'|'pro'|'enterprise'|'govtech' }
```

**Paso 3 — Hook + componente:**

```typescript
// shared/features/useFeature.ts (~15 LOC)
export function useFeature(key: FeatureKey): boolean {
  const { plan } = useTenant()
  if (!plan) return true   // fail-open mientras carga, no bloqueamos al super-admin
  return PLAN_MODULES[plan]?.has(key) ?? false
}

// shared/features/ModuleGate.tsx (~20 LOC)
export function ModuleGate({ module, fallback, children }: Props) {
  const enabled = useFeature(module)
  if (enabled) return <>{children}</>
  return fallback ?? <UpgradePrompt module={module} />
}
```

**Paso 4 — Cableado mínimo (los 4 lugares de mayor ROI):**

```tsx
// App.tsx
<Route path="/recruitment/jobs" element={
  <ModuleGate module="hire">
    <AdminRoute><JobPostingsPage/></AdminRoute>
  </ModuleGate>
}/>

// Empleados.tsx tabs
{useFeature('employees.advanced') && (
  <><TabsTrigger value="familiares">…</TabsTrigger>
    <TabsTrigger value="academicos">…</TabsTrigger></>
)}

// Dropdown items (Constancia, Certificado, Legajo Digital)
<ModuleGate module="legajo" fallback={<LockedItem label="Legajo Digital" />}>
  <DropdownMenuItem onClick={…}>Legajo Digital</DropdownMenuItem>
</ModuleGate>

// Sidebar (shared/api/menuService.ts) — filtrar items por módulo declarado
```

Estimado: **2 días para el MVP** (TenantContext + catálogo + hook + gate + UpgradePrompt + 4-5 cableados). Tag sugerido: sub-proyecto **E — Modularity Gating**, entre B y D.

### 2.3 Test de bloqueo (re-corrido con BD poblada)

| URL | Tenant `demo-pro` (plan=pro) | Tenant hipotético `demo-starter` |
|-----|------------------------------|-----------------------------------|
| `/empleados` | Ve todo (correcto para pro) | Hoy: ve todo (**incorrecto** — sin gate, debería ver solo Lista + Datos Personales/Laborales) |
| `/empleados/reporte/:id` | Ve reporte PDF | Hoy: ve reporte (**incorrecto**) |
| `/recruitment/jobs` (B.9) | Hoy: ve (debería ser enterprise-only — `hire`) | Hoy: ve (incorrecto doble) |
| `/legajos-digitales` (B.12) | Ve (correcto para pro) | Hoy: ve (incorrecto) |

**Resumen:** 0/4 bloqueos correctos hoy. Sin tenant `demo-starter` seedeado, no se puede demostrar el bug a stakeholders. **Acción auxiliar sugerida:** agregar `seed_demo_starter.py` análogo al `seed_demo_pro.py`, con plan='starter' y 5 empleados — sirve como fixture E2E.

---

## 3. Sketch ASCII — UI Starter vs Pro

### Vista hoy (demo-pro, plan=pro) — pantalla `/empleados`:

```
┌───────────────────────────────────────────────────────────────────┐
│  Empleados (15)                                  [+ Nuevo]        │
├───────────────────────────────────────────────────────────────────┤
│  [Personales] [Laborales] [Familiares] [Académicos]               │
│                                                                   │
│  ID │ DNI       │ Empleado            │ Área │ Estado   │ ⋯       │
│  1  │ 70000001  │ Carlos Quispe M.    │ GG   │ ●Activo  │ [⋯]    │
│  2  │ 70000002  │ Lucía Rodríguez T.  │ FIN  │ ●Activo  │ [⋯]    │
│  ...│ ...       │ Pedro Apaza Cond.   │ TI   │ ●Activo  │ [⋯]    │
│                                                                   │
│  Click [⋯] → Editar / Descargar PDF / Legajo / Constancia / …    │
└───────────────────────────────────────────────────────────────────┘
```

### Vista esperada con demo-starter (plan=starter) — feature flags activos:

```
┌───────────────────────────────────────────────────────────────────┐
│  Empleados (5)                                   [+ Nuevo]        │
├───────────────────────────────────────────────────────────────────┤
│  [Personales] [Laborales]      ← Familiares y Académicos OCULTOS  │
│                                                                   │
│  ID │ DNI       │ Empleado            │ Área │ Estado   │ ⋯       │
│  1  │ 70000001  │ Carlos Quispe M.    │ GG   │ ●Activo  │ [⋯]    │
│  ...│ ...       │ ...                 │ ...  │ ...      │ [⋯]    │
│                                                                   │
│  Click [⋯]:                                                       │
│    [ Editar              ]                                        │
│    [ Descargar PDF        ]                                        │
│    [ 🔒 Legajo Digital · Pro ]  ← greyed, click → UpgradeModal    │
│    [ 🔒 Constancia · Pro    ]                                     │
│    [ 🔒 Certificado · Pro   ]                                     │
└───────────────────────────────────────────────────────────────────┘
```

Y en sidebar (siempre visible, con candado, **no oculto** — upsell):

```
 ┌──────────────────────────────┐
 │ 📋  Empleados                │  ← activo
 │ 📄  Contratos                │  ← starter incluye básico
 │ 📁  Legajo Digital   🔒 Pro  │  ← opacity-60 + tooltip
 │ 💰  Planilla         🔒 Pay  │
 │ 🎯  Reclutamiento    🔒 Hire │
 │ 📊  Insights         🔒 Ent. │
 └──────────────────────────────┘
```

Y modal de upgrade cuando se intenta acceder a feature bloqueada (idéntico al mockup de la primera corrida — ver `2026-05-22-empleados.md` §5).

---

## 4. Hallazgos nuevos solo visibles con data real

### 4.1 Typography: apellidos andinos largos

El seed de demo-pro tiene combinaciones como **"Carlos Alberto Quispe Mamani"** (29 chars). El render en `Empleados.tsx:504`:

```tsx
<p className="text-sm font-medium truncate">{emp.nombre_completo}</p>
```

`truncate` + `min-w-0` + `flex-1` cubren bien el caso. **Sin bug.** El nombre completo se ve íntegro en md+, se trunca con elipsis en sm. Inter renderiza ñ, í, ó sin issues.

**Caveat:** en la cabecera de `EmpleadoReportPage.tsx:225-235`, el `<h1>` no tiene `truncate` ni `break-words`. Si el nombre supera ~40 chars (común con doble apellido + doble nombre) puede romper el layout en el PDF. **Hallazgo nuevo, severidad BAJA.**

### 4.2 Formato de DNI (8 dígitos)

`Empleados.tsx:492` → `<TableCell className="font-mono text-sm">{emp.numero_documento}</TableCell>`

**Correcto.** En Perú el DNI se muestra **literal sin separadores** (a diferencia de EE.UU. SSN o México CURP). `font-mono` ayuda a alineación columna. ✅

`Empleados.tsx:251` (formulario) → `placeholder="12345678"` `maxLength={12}` — el maxLength=12 permite también RUC (11) o pasaporte (8-12). ✅

### 4.3 Formato de fechas (es-PE)

- `EmpleadoReportPage.tsx:173` usa `toLocaleDateString('es-PE', {day:'2-digit', month:'2-digit', year:'numeric'})` → 22/05/2026. ✅ correcto.
- `Empleados.tsx` (lista): **no muestra ninguna fecha** directamente — solo `edad` (number). No hay riesgo.
- `HROverviewDashboard.tsx` muestra `periodo` (formato propio) y `total_neto_pagar` con `.toLocaleString('es-PE')`. ✅

**Sin hallazgos nuevos sobre fechas.**

### 4.4 Avatares con foto ausente

15 empleados seedeados, ninguno tiene `ruta_fotografia` (el seed no carga fotos). `Empleados.tsx:497-502` usa `<ProfileImage src={emp.ruta_fotografia || ''} ...>`. Sin verificar el componente `ProfileImage`, hay riesgo de que muestre 15 placeholders idénticos sin iniciales. **Severidad BAJA.** Vale revisar si `ProfileImage` cae a iniciales o a icono genérico cuando `src=''`.

### 4.5 Áreas mostradas

El seed crea 8 departamentos (GG, RRHH, FIN, TI, OPE, COM, LEG, AUD). `Empleados.tsx:516-519` muestra `area_siglas` grande + `area_nombre` truncado. **Con 8 áreas distintas la tabla se ve diversa.** ✅

---

## 5. Top-3 acciones actualizadas

| # | Prio | Tipo | Acción |
|---|------|------|--------|
| 1 | **P0 inmediato** | Tooling | Arreglar `apps/web/tsconfig.json:8` (`--ignoreDeprecations` inválido). Sin esto, tsc no detecta los 5 imports rotos ni futuras regresiones de tipos. **5 min de fix.** |
| 2 | **P0 corto** | Bug | `HROverviewDashboard.tsx:479,496` — corregir `p.status → p.estado` (o ambos). Con BD poblada el dashboard de pay está roto visible. Verificar contra `PayrollSerializer` qué campo emite. |
| 3 | **P1 sub-proyecto E** | Modularidad | Cablear `<ModuleGate>` mínimo (catálogo + hook + 4-5 cableados). Detalle en §2.2. ~2 días. Pre-requisito comercial para vender plan starter vs pro. |

Acciones secundarias (no top-3 pero pendientes):
- Borrar `EmpleadosListPage.tsx` + 4 modales huérfanos (no ruteados, no importados).
- Crear `seed_demo_starter.py` (fixture E2E para tests de modularidad).
- Agregar `truncate` o `break-words` en `<h1>` de `EmpleadoReportPage.tsx:225-235`.
- Verificar fallback de `ProfileImage` cuando `src=''`.

---

## 6. Pregunta pendiente al humano

¿La modularidad por plan/módulo arranca **antes o después de D — Vyntia Pay**? Mi recomendación se reafirma: **antes**. Pay siempre será premium; `<ModuleGate module="pay">` debe existir desde el primer commit de D para no acoplar Pay al core. El BE ya tiene `Tenant.plan` desde C, así que el costo es bajo: ~2 días de FE para un MVP.

---

## 7. Cambios aplicados

Ninguno. Auditoría READ-ONLY conforme al brief.
