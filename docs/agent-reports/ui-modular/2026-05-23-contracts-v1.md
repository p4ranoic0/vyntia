# UI Modular — Contracts (frontend)

**Fecha:** 2026-05-23
**Invocado por:** /vyntia-ui-audit contracts (v1)
**Confianza:** alta (lectura completa de las 5 páginas + menuService FE/BE + AdminRoute + Tenant model + tokens)
**Tiempo invertido:** ~18min
**Modo:** AUDIT-ONLY (read-only — sin fixes aplicados)

## Resumen ejecutivo

- **Verdict global: 🔴 (por modularidad).** La calidad de diseño es 🟡 aceptable-pero-incoherente, pero la modularidad comercial es 🔴 inexistente: T-Registro, liquidaciones y ceses (features avanzadas) están 100% expuestas a cualquier admin/RRHH sin importar el `tenant.plan`. Un tenant **starter** ve y ejecuta planilla avanzada igual que uno **enterprise**.
- **No existe ningún sistema de feature flags por módulo en el frontend.** Grep de `FEATURE_FLAG|useFeatureFlag|tenant.modules|hasModule|subscription|upgrade|upsell` en `apps/web/src` → 0 resultados. El `AuthContext` ni siquiera expone `tenant.plan`.
- **El gating es solo RBAC binario (admin/RRHH sí, resto no).** `AdminRoute` (App.tsx:162) y el `MenuService` backend (`menu_service.py`) filtran por permisos de usuario, NO por plan/módulo contratado del tenant. El modelo `Tenant` tiene un campo `plan` (starter/pro/enterprise/govtech) pero **no hay mapping plan→módulos en ninguna capa**.
- **Inconsistencia visual fuerte dentro del propio módulo:** `ContratosPage` (madura, tabla + stats + dialogs shadcn, `h1 text-3xl`) vs las 4 páginas B.10-B.14 (T-Registro/Probation/Severance/Termination) que son tarjetas simples con `h1 text-2xl`, `window.prompt()` para inputs, sin stats, sin filtros, sin búsqueda, sin estado de error. No alcanzan el pulido de Empleados v5.
- **Colores hardcodeados fuera del brand token.** Iconos y badges usan `text-blue-600`, `bg-blue-700`, `text-emerald-700`, `text-rose-600`, `bg-red-100` en lugar del primario de marca `#6C63FF` (token `--primary`). Cada página inventó su propio color de acento.

---

## Lente diseño

### Estado general
| Dimensión | Calificación | Notas |
|-----------|--------------|-------|
| Consistencia con brand VYNTIA | 5/10 | Acentos hardcodeados (`blue-600`, `emerald-700`, `rose-600`) en vez de `--primary` `#6C63FF`. Cada página eligió su color. |
| Coherencia inter-páginas | 4/10 | ContratosPage (tabla rica) vs 4 páginas card-only divergen en layout, tamaño de heading (text-3xl vs text-2xl), patrones de input. |
| Jerarquía visual | 6/10 | `h1 text-3xl font-bold tracking-tight` en ContratosPage; `h1 text-2xl font-bold` en las otras 4. Brand kit pide H1=28px (~text-3xl). |
| Accesibilidad (WCAG AA) | 5/10 | `window.prompt()` para razones/montos (Probation, Severance, Termination) — no accesible, no estilable, rompe foco. Checkbox nativo en certificado (ContratosPage:751). Filas de tabla clicables sin `role`/teclado. |
| Estados (vacío/loading/error) | 6/10 | Empty states OK. Loading inconsistente (`<LoadingSpinner/>` vs `<p>Cargando…</p>`). **Sin estado de error** en las 4 páginas nuevas (solo toast); ContratosPage sí tiene bloque de error con reintentar. |
| Micro-interacciones | 5/10 | Sin transiciones/hover deliberado salvo `cursor-pointer`. Botones con spinner solo en ContratosPage; las 4 nuevas solo deshabilitan vía `busyId`. |

### Hallazgos visuales

1. **Acento de marca ignorado (todas las páginas).** Brand kit define Primary `#6C63FF` (token `--primary`). En su lugar:
   - `ContratosPage.tsx:562` — `className="bg-blue-600 hover:bg-blue-700"` en botón Renovar.
   - `ContratosPage.tsx:79-81` — badges `bg-red-100 text-red-800` / `bg-yellow-100 text-yellow-800` hardcoded en vez de variantes de `Badge`.
   - `TRegistroListPage.tsx:109` — `<ShieldAlert className="... text-blue-600" />`.
   - `ProbationPeriodListPage.tsx:84` — `<Timer className="... text-blue-600" />`.
   - `SeveranceSettlementListPage.tsx:87` — `<Wallet className="... text-emerald-700" />`.
   - `TerminationListPage.tsx:101` — `<UserX className="... text-rose-600" />`.
   - Recomendación: unificar el icono de header con `text-primary` (o un set semántico documentado), y reemplazar badges ad-hoc por `variant` del componente `Badge`.

2. **Heading inconsistente.** `ContratosPage.tsx:987` usa `text-3xl font-bold tracking-tight`; las 4 páginas nuevas usan `text-2xl font-bold` (líneas 108, 83, 86, 100 respectivamente). Empleados v5 usa el patrón `text-3xl`. Estandarizar a `text-3xl font-bold tracking-tight` para alinear con H1=28px del brand kit.

3. **`window.prompt()` como input de negocio.** `ProbationPeriodListPage.tsx:66`, `SeveranceSettlementListPage.tsx:66`, `TerminationListPage.tsx:83` capturan razón de no-renovación, monto pagado y motivo de cancelación con `window.prompt()`. Es inaccesible, no validable, fuera de brand y rompe la experiencia. Migrar a `Dialog` shadcn con `Input`/`Textarea` (como hace ContratosPage para Renovar/Certificado).

4. **Sin layout contenedor consistente.** ContratosPage usa `container mx-auto p-6 space-y-6`; las 4 nuevas usan `p-6 space-y-6` (sin `container mx-auto`). Diferencia de ancho máximo y centrado entre vistas del mismo módulo.

5. **Falta de KPIs/filtros en las 4 vistas nuevas.** ContratosPage tiene stats cards + banner de alertas + filtros + búsqueda. T-Registro/Probation/Severance no tienen búsqueda ni filtros (problemático a escala: una empresa con 200 declaraciones T-Registro tendrá una grilla de cards inmanejable). Termination tiene banner de alertas SLA (bien), pero sin filtros.

6. **Checkbox nativo sin componente shadcn.** `ContratosPage.tsx:751-757` usa `<input type="checkbox">` crudo en lugar del `Checkbox` de shadcn/radix — rompe consistencia de foco y estilo.

7. **Locale de fechas inconsistente.** ContratosPage formatea con `toLocaleDateString('es-PE', {...})` (línea 68); las 4 nuevas usan `new Date(...).toLocaleDateString()` sin locale (líneas Probation:115, Severance, Termination:151) → formato dependiente del navegador. Unificar a `es-PE`.

---

## Lente modularidad comercial

### Estado del sistema de feature flags
- ¿Existe? **No (frontend). Parcial-inútil (backend).**
- ¿Dónde? Solo existe el campo `Tenant.plan` en `apps/api/apps/tenancy/models/tenant.py:34` (choices: starter/pro/enterprise/govtech). **No hay tabla/relación plan→módulos, ni `module_enabled`, ni chequeo de plan en ninguna vista/endpoint/ruta.**
- ¿El menú lo respeta? **No.** `apps/api/apps/identity/services/menu_service.py` filtra `Module` solo por `estado_modulo="activo"` global + intersección de **permisos RBAC del usuario** (`_is_visible`, líneas 47-71). No consulta el plan del tenant. El menú es idéntico para starter y enterprise si el usuario es admin.
- ¿El FE respeta el menú? El sidebar consume `menuService.getUserMenu()` (`apps/web/src/shared/api/menuService.ts`), pero `filterMenuByPermissions` (líneas 104-116) **devuelve el menú entero sin filtrar** si hay `usuario_id`. Las rutas de contracts en `App.tsx` están hardcodeadas, no derivadas del menú, así que aunque el menú ocultara algo, la URL directa seguiría sirviendo la vista.
- ¿La UI guía al upsell? **No.** No existe ningún componente de upgrade prompt / paywall / "módulo no incluido en tu plan" en todo `apps/web/src`.

### Test de bloqueo (análisis estático — no se levantó `npm run dev`)
| Módulo / vista | URL | Tenant starter sin el módulo → qué pasa | Esperado | Estado |
|----------------|-----|------------------------------------------|----------|--------|
| Contratos | `/contratos` (ruta base) | Si es admin/RRHH: vista completa. Sin rol: redirect `/acceso-denegado`. | Si plan no incluye → upgrade prompt | 🟡 solo RBAC, no plan |
| T-Registro SUNAT | `/vinculacion/t-registro` | Admin/RRHH ve y puede Validar PVS/Enviar/descargar Anexo3 sin importar plan | Oculto o bloqueado-con-upsell en starter | 🔴 expuesto |
| Período de prueba | `/periodo-prueba` | Admin/RRHH ratifica / no-renueva sin importar plan | Gating por plan | 🔴 expuesto |
| Liquidaciones | `/cese/liquidaciones` | Admin/RRHH recomputa y marca-pagado sin importar plan | Feature avanzada → upsell en starter | 🔴 expuesto |
| Ceses / Desvinculación | `/cese/terminaciones` | Admin/RRHH completa/liquida/cancela sin importar plan | Feature avanzada → upsell en starter | 🔴 expuesto |

Nota: "expuesto" = la vista renderiza y las acciones de negocio se ejecutan. No crashea (bien), pero **no hay gating comercial**, que es justamente lo que el equipo quiere para vender por módulos. El backend tampoco bloquea por plan, así que el riesgo no es solo cosmético: un tenant starter podría usar planilla avanzada vía API directa.

### Hallazgos de modularidad

1. **CRÍTICO — No hay capa de "módulo contratado por tenant".** El `plan` es un enum suelto sin semántica de capacidades. Falta: (a) un catálogo de módulos por plan (o tabla `TenantModule`), (b) un endpoint que exponga los módulos habilitados al FE, (c) un hook `useModuleEnabled('contracts.t_registro')`, (d) un guard de ruta + un guard de menú que lo respeten, (e) un componente de upsell. Reportar como **sub-proyecto aparte** (no construir aquí; es lógica de negocio/arquitectura, fuera del alcance de un audit de UI).

2. **CRÍTICO — Backend no aplica gating por plan.** `MenuService` y los endpoints de contracts no consultan el plan. Cualquier sistema de flags que se construya solo en FE sería burlable. El gating debe nacer en backend (DRF permission por plan/módulo) y reflejarse en FE. Reportar para el sub-proyecto.

3. **MEDIO — Las rutas no derivan del menú dinámico.** `App.tsx` hardcodea las rutas de contracts. Aunque MenuService ocultara T-Registro para starter, `/vinculacion/t-registro` seguiría montando el componente. El guard debe vivir en la ruta (envoltorio tipo `<ModuleRoute module="...">`), no solo en el menú.

4. **MEDIO — Nomenclatura no comunica "módulo".** Las páginas mencionan "Module 03.2 / 03.4 / 03.7" en el subtítulo (jerga interna del roadmap, no de cara al cliente). No hay badge de plan, ni breadcrumb "Módulo Contratos › T-Registro", ni tile de entrada. Para una UX modular-comercial conviene rotular cada vista con su módulo de venta (Vyntia Pay / Vyntia Core) en lugar de "Module 03.x".

---

## Cambios aplicados

Ninguno — auditoría read-only por instrucción explícita.

## Acciones recomendadas

- [ ] LARGO — Modularidad (sub-proyecto nuevo): diseñar capa plan→módulos (backend `TenantModule` + DRF permission por plan), endpoint de capacidades, hook FE `useModuleEnabled`, `<ModuleRoute>`, componente de upsell/paywall. Backend primero.
- [ ] CORTO — Visual: estandarizar `h1` a `text-3xl font-bold tracking-tight` en las 4 páginas B.10-B.14 para alinear con ContratosPage y Empleados v5.
- [ ] CORTO — Visual: reemplazar acentos hardcodeados (`text-blue-600`, `text-emerald-700`, `text-rose-600`, `bg-blue-600/700`) por token `--primary`/`text-primary` o variantes semánticas de `Badge`.
- [ ] CORTO — A11y/UX: migrar los 3 `window.prompt()` (Probation:66, Severance:66, Termination:83) a `Dialog` shadcn con `Input`/`Textarea`.
- [ ] CORTO — Visual: envolver las 4 páginas en `container mx-auto` para igualar ancho/centrado con ContratosPage.
- [ ] CORTO — Visual: unificar locale de fechas a `es-PE` en las 4 páginas nuevas.
- [ ] CORTO — UX: reemplazar `<input type="checkbox">` crudo (ContratosPage:751) por `Checkbox` shadcn.
- [ ] MEDIO — Escalabilidad UX: añadir búsqueda/filtros a T-Registro, Probation y Severance (grillas de cards no escalan).
- [ ] MEDIO — Producto: reemplazar "Module 03.x" por nombres de módulo comercial en subtítulos.

## Pregunta para humano

El campo `Tenant.plan` ya existe pero no gobierna nada. ¿La decisión de "vender por módulos" se modela como **(A) plan-tier → set fijo de módulos** (starter incluye X, pro incluye Y), o **(B) add-ons individuales activables por tenant** (TenantModule m2m)? Esto define si el sub-proyecto de feature flags se construye sobre el enum `plan` actual o sobre una tabla de módulos contratados. Bloquea el diseño de la capa de gating.
