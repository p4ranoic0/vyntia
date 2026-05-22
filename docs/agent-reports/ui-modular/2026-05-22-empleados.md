# UI Modular — Empleados (frontend)

**Fecha:** 2026-05-22
**Scope:** `apps/web/src/features/employees/` (pages, components, modals, hooks, services)
**Modo:** READ-ONLY (auditoría)
**Confianza:** alta
**Tiempo invertido:** ~35 min

---

## TL;DR

| Lente | Verdict | Resumen |
|-------|---------|---------|
| Diseño / consistencia con brand VYNTIA | **WARN** | Los pages "vivos" (Empleados, EmpleadoReport, HROverviewDashboard) están limpios y usan Shadcn/Tabs correctamente. Pero hay tres caminos UI paralelos (Empleados vs EmpleadosListPage vs DatosXxxPage standalone), 29 `console.log` debug en producción, y 5 imports rotos (`@/shared/ui/loading-spinner` no existe). El reporte usa gradient azul hardcoded en lugar de tokens `--primary`. |
| Modularidad comercial | **FAIL** | **No existe sistema de feature flags ni concepto de "plan/módulo contratado".** El `TenantProvider` solo resuelve subdomain → no expone `tenant.modules[]`. El `menuService.filterMenuByPermissions` retorna el menú entero sin filtrar por módulo. Todo se gobierna por **rol RBAC**, no por **plan**. Cualquier tenant ve TODAS las features (Empleados, ATS B.9, Legajo B.12, etc.) si su rol lo permite. **No hay upsell, no hay placeholders bloqueados, no hay `useFeature(flag)`**. |

---

## 1. Inventario del scope

| Archivo | Propósito | Estado |
|--------|-----------|--------|
| `pages/Empleados.tsx` (652 ln) | **Página activa** montada en `/empleados` (App.tsx:322) | OK — la más cuidada |
| `pages/EmpleadosListPage.tsx` (622 ln) | Vista alternativa, **no ruteada** en App.tsx | Huérfana / muerta |
| `pages/HROverviewDashboard.tsx` (903 ln) | KPI panel, animaciones, sparklines | Excelente (con caveats) |
| `pages/EmpleadoReportPage.tsx` (527 ln) | Reporte ficha por empleado, printable | Sólida |
| `pages/Datos{Personales,Laborales,Familiares,Academicos}Page.tsx` | Self-service del empleado (`EmployeeLayout`) | Funcional pero duplicado con Tabs* |
| `components/Tab{Personales,Laborales,Familiares,Academicos}.tsx` | Tabs dentro del modal admin de Empleados.tsx | OK |
| `components/AdminDocUpload.tsx` | Dropzone PDF/IMG | OK |
| `modals/Datos{Personales,Laborales,Familiares,Academicos}Modal.tsx` | Modales legacy referenciados solo por EmpleadosListPage | Huérfanos |
| `hooks/useEmployees.ts` | React Query | OK |
| `hooks/useEmployeePermissions.ts` | RBAC fino (NO modular) | Ver L2 |
| `services/employeesService.ts` | API client | OK |
| `services/legajoContentService.ts` | B.12 (WorkExp, SwornDecl, JobHistory) | OK — pero sin gating |

---

## 2. Lente 1 — Diseño

### 2.1 Consistencia con design tokens

**Hay DOS fuentes de verdad para tokens y NO se cruzan:**

- `packages/design-tokens/tokens.json` — brand VYNTIA: `primary #6C63FF`, Inter, escala `1..6` (4/8/16/24/32/48)
- `apps/web/src/shared/utils/design-tokens.ts` — sistema empleado/solicitud/documento usando HSL (verde/naranja/rojo). NO refleja `#6C63FF`.

Ninguno de los 13 archivos del módulo Empleados importa nada de `design-tokens.ts` ni del paquete. Todo el color de estado vive en `className="bg-green-600"`, `bg-green-100`, `bg-green-500`, `bg-amber-50`, `bg-blue-600 to-blue-800` (gradient en `EmpleadoReportPage.tsx:257`), `text-red-500`. **Estos hardcodes hacen imposible reskinning por tenant** y rompen dark-mode parcialmente.

**Inconsistencia de Badge "Activo"** (mismo concepto, tres estilos):
- `Empleados.tsx:330` → `<Badge variant="default" className="bg-green-600">`
- `EmpleadosListPage.tsx:256` → `<Badge variant="default" className="bg-green-100 text-green-800">`
- `EmpleadoReportPage.tsx:283` → `<Badge ... className="bg-green-500 text-white hover:bg-green-600">`

Debería ser `<StatusBadge status="activo">` (ya existe `shared/ui/status-badge.tsx`, pero no se usa aquí).

### 2.2 Tipografía

- Inter sí está cargado a nivel global (font-family viene del CSS).
- H1 sizes inconsistentes:
  - `Empleados.tsx:403` — `text-3xl font-bold tracking-tight`
  - `EmpleadosListPage.tsx:306` — `text-2xl sm:text-3xl font-bold tracking-tight`
  - `EmpleadoReportPage.tsx:218` — `text-xl sm:text-2xl font-bold` (sin tracking-tight)
  - `HROverviewDashboard.tsx:677` — `text-2xl font-bold tracking-tight`
  - `DatosPersonalesPage` — el `<EmployeeLayout>` se encarga (no se ve en la página directa)
- Token brand kit dice `h1: 28px` → `text-2xl (24px)` o `text-3xl (30px)`. Ninguno encaja exacto.

### 2.3 Estados (loading / empty / error)

| Página | Loading | Empty | Error |
|--------|---------|-------|-------|
| `Empleados.tsx` | ✅ Skeleton bien detallado (l.342-368) | ✅ Card con icon + texto (l.470-481) | ✅ Reintentar (l.370-383) |
| `EmpleadosListPage.tsx` | LoadingSpinner (l.266-272) | Empty básico | ❌ Solo `toast.error`, sin fallback UI |
| `HROverviewDashboard.tsx` | ✅ Skeletons por widget | ✅ "Sin alertas activas" | ⚠️ Badge "Error al cargar" pero la tabla queda en blanco |
| `EmpleadoReportPage.tsx` | ✅ Skeleton (l.177-192) | ✅ `<EmptyState>` reutilizable (l.519-525) | ✅ Botón volver (l.194-205) |
| `DatosPersonalesPage.tsx` | LoadingSpinner básico | ❌ Solo `<p>` | ❌ Solo `<p>` |
| `DatosLaboralesPage.tsx` | LoadingSpinner básico | ❌ — | ❌ `.catch(() => {})` silencia errores |
| `DatosFamiliaresPage.tsx` | LoadingSpinner básico | ❌ Cae a estado vacío con `setEmpleado(default)` | ❌ swallow |
| `DatosAcademicosPage.tsx` | LoadingSpinner básico | ❌ idem | ❌ swallow |

### 2.4 Accesibilidad

- Labels sí están casi siempre. ✅
- En `Empleados.tsx` el `<TableRow>` clickeable (`onClick={() => handleVerDetalle}`) no tiene `role="button"` ni keyboard handler. Un usuario por teclado no puede navegar a la ficha del empleado.
- `EmpleadosListPage.tsx:457-547` — el `TableRow` no es clickeable (mejor), pero el `<Button variant="ghost" className="h-8 w-8 p-0">` del menú tiene `sr-only` "Abrir menú" ✅.
- `AdminDocUpload.tsx:79-86` — `useDropzone` no expone `aria-label`. El área de drop solo tiene texto visible.
- Contrastes: `bg-green-100 + text-green-800` en EmpleadosListPage ~ 7:1 OK; el gradient azul de EmpleadoReportPage tiene `text-white` sobre `from-blue-600 to-blue-800` ~ 6.5:1 OK.
- `DatosPersonalesPage.tsx:269-275` — `<SelectItem value="M">Masculino</SelectItem>` pero el form se inicializa con `data.genero_empleado` que puede venir `"masculino"` (lowercase). Mismatch → el select queda vacío.

### 2.5 Bugs visuales / técnicos detectados (read-only, no editados)

| # | Severidad | Archivo:línea | Problema |
|---|-----------|---------------|----------|
| B1 | **CRÍTICO** | `EmpleadosListPage.tsx:19, 100` | Import `LoadingSpinner from '@/shared/ui/loading-spinner'` — **ese path NO EXISTE**. El módulo correcto es `@/shared/components/LoadingSpinner`. Misma falla en los 4 modales `Datos*Modal.tsx:25`. Si esta ruta llegara a renderizarse caería en build. La página no está ruteada en App.tsx, pero los modales se importarían vía EmpleadosListPage si alguien lo monta. |
| B2 | **CRÍTICO** | `EmpleadosListPage.tsx:100` | Referencia variables `isRRHH`, `isSupervisor`, `isEmployee` en un `console.log` pero **solo `isEmployee` está destructurado** (línea 60-67). `isRRHH`/`isSupervisor` son `undefined` → no rompe en runtime por ser `console.log`, pero indica código no probado. |
| B3 | ALTO | `EmpleadosListPage.tsx` (todo el archivo) | 29 `console.log` con emojis 🔍/❌/✅ en producción. Filtra ruido y revela estructura interna al inspector. |
| B4 | ALTO | `HROverviewDashboard.tsx:479, 589, 658` | Usa `p.status` pero `interface PlanillaMensual` (l.66-76) declara `estado?`. Inconsistencia: si el backend envía `estado`, el dashboard cae a `'borrador'` siempre. |
| B5 | MEDIO | `Empleados.tsx:484-488` | `<TableRow onClick=...>` no tiene `tabIndex={0}` ni `onKeyDown`. No accesible por teclado. |
| B6 | MEDIO | `EmpleadoReportPage.tsx:123` | `apiClient.getEmpleadoDetail(Number(id))` — `id` es string UUID en otros lugares pero acá lo casteamos a number. Si el backend espera UUID, `Number("a1b2-...")` da `NaN`. |
| B7 | BAJO | `Empleados.tsx:329-340` | `getEstadoBadge` reimplementa lo que ya hace `shared/ui/status-badge.tsx`. |
| B8 | BAJO | `DatosPersonalesPage.tsx:264-276` | `genero_empleado` se compara con `"M"/"F"` pero el resto del codebase usa `"masculino"/"femenino"` (cf. `Empleados.tsx:166-170`). |
| B9 | BAJO | `DatosFamiliaresPage.tsx:96` y `DatosAcademicosPage.tsx:91` | `.catch(() => { setEmpleado(default) })` — ningún feedback al usuario en caso de error de red. |
| B10 | BAJO | `Empleados.tsx:62-65` | `useEmployeePermissions` exporta `currentEmployeeId` como `user.empleado?.id` pero en `EmpleadosListPage.tsx:170` se compara `emp.id === currentEmployeeId` — `emp.id` es number, `currentEmployeeId` puede ser string. |

### 2.6 Calidad por página

| Página | Diseño | Notas |
|--------|--------|-------|
| `Empleados.tsx` | 8/10 | Skeleton + empty + error completos. Solo falta token y a11y de fila. |
| `HROverviewDashboard.tsx` | 8/10 | Sparklines/Donut hechos a mano (sin lib) — muy limpio. CSV de bug `p.status`. |
| `EmpleadoReportPage.tsx` | 7/10 | Gradient hardcode; usa `border-primary` ✅ en print header. |
| `EmpleadosListPage.tsx` | 3/10 | 29 console.log, imports rotos, vars no destructuradas. Huérfana del router → **borrarla**. |
| `DatosPersonalesPage.tsx` | 5/10 | Solo lectura/edición lineal, sin secciones colapsables; 3 cards una sobre otra. |
| `DatosLaboralesPage.tsx` | 5/10 | Igual. |
| `DatosFamiliaresPage.tsx` | 5/10 | Igual + estado mal mapeado. |
| `DatosAcademicosPage.tsx` | 5/10 | Igual. |

---

## 3. Lente 2 — Modularidad comercial

### 3.1 ¿Existe sistema de feature flags?

**NO.** Grep exhaustivo en `apps/web/src/` y `apps/api/`:

- `FEATURE_FLAG` → 0 matches
- `useFeatureFlag` → 0 matches
- `tenant.modules` → 0 matches
- `is_module_enabled` → 0 matches
- `FeatureGate` / `UpgradePrompt` → 0 matches
- `subscription` / `plan_id` → 0 matches
- `useFeature(` → 0 matches

`shared/tenant/tenantContext.tsx` solo expone `{ type: 'tenant'|'admin'|'app'|'www', slug, host }` — **no hay concepto de plan ni de módulos contratados**.

El único filtrado existente es por **rol RBAC** (`useEmployeePermissions.ts`): `Super Administrador`, `Administrador RRHH`, `Analista RRHH`, `Jefe de Area`, empleado. Esto controla **qué puede hacer un usuario**, no **qué módulo compró su tenant**.

### 3.2 ¿El menú respeta lo contratado?

**NO.** `shared/api/menuService.ts:104-116` (`filterMenuByPermissions`): si hay `userData.user.usuario_id`, **retorna el menú entero sin filtrar**. La función `filterMenuItems` (l.121-155) que sí podría filtrar por `requiredPermissions`/`requiredRoles` **nunca se llama**. El backend (`apps/api/apps/identity/services/menu_service.py`) puede enviar items según permisos del usuario, pero ningún flag de tenant filtra por módulo contratado.

### 3.3 ¿Las features avanzadas tienen gating?

Buscando `Candidate`, `MeritRanking`, `JobPosting`, `JobApplication`, `LegajoContent`:

- `App.tsx:83-89` registra rutas `/recruitment/*` y `/candidates-dashboard` con **`lazy()`**, pero solo envueltas en `<AdminRoute>` (RBAC), **no en ningún `<ModuleGate module="ats">`**.
- `App.tsx:111, 527` registra `/legajos-digitales` (B.12) sin gating de módulo.
- `services/legajoContentService.ts` accede a `/api/v1/work-experiences/` etc. sin ninguna verificación previa de "este tenant contrató Legajo Premium".

**Cualquier tenant con un rol admin puede acceder a ATS + Legajo + Pay** independientemente de lo que pagó. La única barrera es que ese tenant no tenga datos seedeados en esas tablas.

### 3.4 Diff esperado — qué se debería esconder según plan

Mapeo propuesto VYNTIA Starter / Pro / Enterprise basado en `docs/00_VYNTIA_MAESTRO.md` y `packages/design-tokens/tokens.json.brand.modules`:

| Plan | Módulos visibles | Empleados → submenú |
|------|------------------|---------------------|
| **Starter** | Vyntia Core (Empleados + Contratos básicos) | Lista, Datos personales, Datos laborales, **Reporte simple** |
| **Pro** | + People + Pulse + Pay + Hire básico | + Familiares, Académicos, **Reporte integral PDF**, Legajo Digital, ATS lista candidatos |
| **Enterprise** | + Insights + B.9 ATS completo + B.12 Legajo content | + MeritRanking, JobPosting editor, WorkExperience, SwornDeclaration, JobHistory, Onboarding completo |

Componentes del scope que deberían estar **escondidos** en Starter pero hoy se muestran:
- `Empleados.tsx:127-130` — Tab "Academicos" (es Pro+)
- `Empleados.tsx:141-147` — Tab "Familiares" (es Pro+)
- `Empleados.tsx:560-587` — DropdownMenuItem "Constancia/Certificado" (es Pro+, dependen de Documents service)
- `Empleados.tsx:565-568` — "Legajo Digital" (es Pro+)
- `EmpleadoReportPage` — el PDF integral (es Pro+)
- `HROverviewDashboard.tsx` — los KPIs cruzados con `payroll/monthly-runs` (l.144) y `contracts/estadisticas` (es Pro+ porque depende de Pay+Contratos)

Diff esperado por archivo:

```diff
// apps/web/src/features/employees/pages/Empleados.tsx
-<TabsList className="grid w-full grid-cols-4">
+<TabsList className={`grid w-full grid-cols-${tabsVisibles.length}`}>
   <TabsTrigger value="personales">Personales</TabsTrigger>
   <TabsTrigger value="laborales">Laborales</TabsTrigger>
-  <TabsTrigger value="familiares">Familiares</TabsTrigger>
-  <TabsTrigger value="academicos">...</TabsTrigger>
+  {hasModule('employees.advanced') && (
+    <>
+      <TabsTrigger value="familiares">Familiares</TabsTrigger>
+      <TabsTrigger value="academicos">...</TabsTrigger>
+    </>
+  )}
 </TabsList>
```

```diff
// apps/web/src/App.tsx (B.9 ATS)
-<Route path="/recruitment/jobs" element={<AdminRoute>...
+<Route path="/recruitment/jobs" element={
+  <ModuleGate module="hire">
+    <AdminRoute>...
+  </ModuleGate>
+}/>
```

### 3.5 Test de bloqueo (forzar URL sin plan)

| URL | Sin módulo contratado → qué pasa hoy | Esperado |
|-----|---------------------------------------|----------|
| `/empleados` | Si rol es Admin → renderiza completo (no hay gate) | Upgrade prompt si plan = Starter sin Empleados |
| `/empleados/reporte/:id` (PDF integral) | Renderiza | Banner "El reporte integral requiere Plan Pro" |
| `/recruitment/jobs` | Renderiza (B.9) | "Vyntia Hire no está incluido en tu plan — Solicitar demo" |
| `/legajos-digitales` | Renderiza (B.12) | "Legajo Digital Premium — Upgrade" |

**Hoy = 0/4 bloqueos correctos.**

### 3.6 Lo que se necesita para implementar feature flags (acción larga, NO la construyo aquí)

Sub-proyecto sugerido **"E — Modularidad / Plans"** (encaja después de D — Vyntia Pay):

1. **Backend:**
   - Modelo `Tenant.plan` + `Plan.modules` (M2M) en `apps/identity/models`.
   - Endpoint `GET /api/v1/auth/me` debe devolver `tenant: { plan, modules_enabled: ['employees.core', 'employees.advanced', 'hire', 'legajo.premium', 'pay'] }`.
   - `MenuService` filtra items con `requiredModule` no contenido en `modules_enabled`.
2. **Frontend:**
   - `shared/tenant/featureFlags.tsx` con `<ModuleGate module="hire" fallback={<UpgradePrompt />}>` y `useFeature('hire')`.
   - `shared/components/UpgradePrompt.tsx` (ver mockup §5).
   - Envolver lazy routes en `App.tsx`, tabs en `Empleados.tsx`, items de dropdown.
3. **Catálogo:**
   - `packages/feature-flags/catalog.ts` — fuente única de verdad de los 6 módulos del brand kit (`Vyntia Core/People/Pulse/Pay/Hire/Insights`).

Estimado: 5-8 días, sub-proyecto independiente.

---

## 4. Top-5 mejoras priorizadas

| # | Prio | Tipo | Archivo:línea | Acción |
|---|------|------|---------------|--------|
| 1 | P0 | Modularidad | nuevo sub-proyecto | **Construir feature-flag system por tenant** (ver §3.6). Sin esto, VYNTIA no es vendible por módulos. |
| 2 | P0 | Bug | `EmpleadosListPage.tsx:19`, `modals/Datos*Modal.tsx:25` (×4) | Quitar/corregir el import `@/shared/ui/loading-spinner` → `@/shared/components/LoadingSpinner` o **borrar `EmpleadosListPage.tsx` y sus 4 modales huérfanos** (no están ruteados). |
| 3 | P1 | Bug | `HROverviewDashboard.tsx:479,589,658` | Reemplazar `p.status` por `p.estado` (o renombrar el field del interface). Hoy el KPI "Planilla más reciente" siempre muestra `10%` (borrador) por defecto. |
| 4 | P1 | Diseño | `Empleados.tsx:329-340`, `EmpleadosListPage.tsx:253-264`, `EmpleadoReportPage.tsx:283` | Usar el `<StatusBadge status="activo">` de `shared/ui/status-badge.tsx` en lugar de tres reimplementaciones distintas. Eliminar `bg-green-{100,500,600}` hardcoded. |
| 5 | P2 | A11y + design tokens | `Empleados.tsx:484-487` y todo el módulo | (a) `tabIndex={0}` + `onKeyDown` en `<TableRow>` clickeable. (b) Mover colores de estado a `shared/utils/design-tokens.ts > colors.empleado` (ya existe, solo no se usa). (c) Reemplazar gradient azul de `EmpleadoReportPage.tsx:257` por `bg-gradient-to-r from-primary to-primary/80` para soporte tenant-skin. |

---

## 5. Mockup textual — feature bloqueado en plan Starter

Ejemplo: usuario Starter abre la lista `/empleados` y hace click en "Legajo Digital" del dropdown de un empleado.

```
┌──────────────────────────────────────────────────────────────┐
│  Modal centrado · max-w-md · rounded-lg · shadow-xl          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│        ┌──────────┐                                          │
│        │ [icon]   │   Lock (lucide) en círculo bg-primary/10 │
│        │  🔒      │   color text-primary                     │
│        └──────────┘                                          │
│                                                              │
│   Legajo Digital · Plan Pro                                  │
│   ──────────────────────────                                 │
│   text-xl font-semibold tracking-tight                       │
│                                                              │
│   Centraliza contratos, certificados, declaraciones          │
│   juradas y documentos del empleado en un solo lugar.        │
│   text-sm text-muted-foreground                              │
│                                                              │
│   Incluye:                                                   │
│   ✓ Subida masiva PDF/imagen                                 │
│   ✓ Versionado de contratos                                  │
│   ✓ Alertas de vencimiento                                   │
│   ✓ Acceso por nivel (público/restringido/confidencial)      │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐   │
│   │  Tu plan actual:  Starter                            │   │
│   │  Necesitas:       Plan Pro o superior                │   │
│   └──────────────────────────────────────────────────────┘   │
│                                                              │
│   ┌──────────────┐  ┌────────────────────────┐               │
│   │  Tal vez luego│  │ Hablar con ventas  →   │               │
│   │  variant=ghost│  │ variant=default bg-primary             │
│   └──────────────┘  └────────────────────────┘               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Y en el sidebar el item se vería siempre presente con un candado pequeño + tooltip "Disponible en Plan Pro":

```
 ┌──────────────────────────────────────┐
 │  📋  Empleados              ⌃         │
 │  📁  Legajo Digital     🔒 Pro       │  <- opacity-60, click → modal arriba
 │  💰  Planilla           🔒 Pay       │
 │  🎯  Reclutamiento      🔒 Hire      │
 └──────────────────────────────────────┘
```

Reglas:
- Nunca **ocultar totalmente** las features superiores en el sidebar — eso es upsell perdido. Mostrarlas con candado.
- En tabs internas (ej. Empleados → tab "Familiares" en Starter): **ocultar la tab** (no hay espacio para candado en `<TabsTrigger>` y rompería el grid). Mostrar un banner pequeño sobre el card: "Familiares es parte de Vyntia People — [Solicitar demo]".
- En acciones de dropdown (Constancia, Certificado): mostrar con candado + click → modal upsell.

---

## 6. Acciones aplicadas

Ninguna. Auditoría READ-ONLY conforme al brief.

---

## 7. Pregunta para humano

¿La modularidad por plan/módulo debe arrancar **antes o después de D — Vyntia Pay**? Mi recomendación: **antes**, porque Pay siempre será premium y conviene tener `<ModuleGate>` para no acoplar Pay al core. Si va después, hay que hacer un freeze de UI para refactorizar todos los lazy routes.
