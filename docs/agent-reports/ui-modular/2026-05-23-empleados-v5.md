# UI Modular — Empleados v5 (post Bloque G frontend, commit `ebb039b9`)

**Fecha:** 2026-05-23
**Scope:** verificación de los 3 fixes frontend del Bloque G (V4-2 / V4-N3 / V4-4) + re-confirmación de pendientes v3/v4
**Audit previo:** v4 `ui-modular/2026-05-22-empleados-v4.md`, PM v4 `pm/2026-05-22-empleados-v4.md`
**Modo:** READ-ONLY
**Confianza:** alta (tsc exit 0, vitest 178/178, ESLint exactamente 278)
**Tiempo invertido:** ~15 min

---

## TL;DR

🟢 **3/3 fixes del Bloque G confirmados.** El commit `ebb039b9` cerró los blockers V4-2 (parser 403 con bug lógico anidado), V4-N3 (regresión ESLint 279→278) y V4-4 (último `.status` perdido en HROverview:738). Las 3 verificaciones independientes coinciden con lo prometido en el commit message. **Modularidad sigue FAIL idéntico** (sub-proyecto E intacto). **Pendientes v3/v4 de diseño** (página huérfana + 29 console.log + 5 imports rotos + 3 badges duplicados + V4-3 con 6 services blob sin parser) **siguen abiertos** — el Bloque G no los tocó por diseño (alcance acotado a v4 blockers).

| Lente | Verdict v4 | Verdict v5 | Cambio |
|-------|-----------|-----------|--------|
| Diseño / consistencia VYNTIA | WARN | **WARN** | 3 bugs nuevos cerrados; deuda v3/v4 intacta. No mueve la aguja. |
| Modularidad comercial | FAIL | **FAIL** (idéntico) | Sin cambios en TenantContext, workspaceService, menuService, App.tsx. Sketch E (4.5h / ~305 LOC) sigue válido. |
| Tooling de tipos | 🟢 Operativo | **🟢 Operativo** | tsc exit 0 mantiene. Sin nuevos errores expuestos. |

---

## 1. Verificación de los 3 fixes del Bloque G

| # | Fix v4 | Archivo | Verdict v5 | Notas |
|---|--------|---------|------------|-------|
| V4-2 | `dossierService.downloadConsolidatedPdf` parser 403: parse-first, throw-outside | `features/documents/services/dossierService.ts:127-159` | ✅ **CONFIRMADO** | Estructura correcta: `let parsed: { message?: string } \| null = null` declarado FUERA del inner try (línea 147). `JSON.parse(text)` dentro del try (líneas 148-150). `catch { parsed = null }` sin variable (151-153). `if (parsed?.message) throw new Error(parsed.message)` AFUERA del inner try (líneas 154-156). El `throw err` outer queda al final (línea 158) como fallback. **Bug lógico v4 cerrado.** |
| V4-N3 | ESLint regresión `parseErr` unused | `features/documents/services/dossierService.ts:151` | ✅ **CONFIRMADO** | `npx eslint src --max-warnings 999` retorna **278 problems (259 errors, 19 warnings)** — back to baseline. Grep `parseErr` en `src/` → 0 matches. Catch sin variable usado. |
| V4-4 | `HROverviewDashboard.tsx:738` quinta site `.status` | `features/employees/pages/HROverviewDashboard.tsx:738` | ✅ **CONFIRMADO** | `grep "\.status" HROverviewDashboard.tsx` → **0 matches**. La línea 738 ahora dice `${latestPlanilla.estado_texto ?? latestPlanilla.estado ?? '—'}` (todos los sites del módulo migrados). |

### 1.1 V4-2 — refactor parse-first análisis

Lectura literal del código vigente (dossierService.ts:127-159):

```ts
async downloadConsolidatedPdf(id: string): Promise<Blob> {
  try {
    const r = await apiClient.get<Blob>(`${DOSSIERS}/${id}/consolidated-pdf/`, {
      responseType: 'blob',
    })
    return r.data
  } catch (err: unknown) {
    const e = err as { response?: { status?: number; data?: unknown }; message?: string }
    const status = e?.response?.status
    const data = e?.response?.data
    if (status && status >= 400 && data instanceof Blob) {
      // Parse first (do not throw inside the try — the inner catch would
      // swallow the friendly Error and we'd fall through to `throw err`).
      let parsed: { message?: string } | null = null
      try {
        const text = await data.text()
        parsed = JSON.parse(text) as { message?: string }
      } catch {
        parsed = null
      }
      if (parsed?.message) {
        throw new Error(parsed.message)
      }
    }
    throw err
  }
}
```

**Punto-a-punto contra la promesa del commit:**

- ✅ `let parsed: ... = null` declarado FUERA del inner try (línea 147). Permite `if (parsed?.message)` después del inner try.
- ✅ `JSON.parse(text)` dentro del inner try (línea 150) — sólo este path lanza la excepción capturada.
- ✅ `throw new Error(parsed.message)` después del inner try (línea 155) — vive en el outer catch pero fuera del nested try, así NO es interceptado por el `catch { parsed = null }`.
- ✅ Cobertura del catch ampliada: condición pasó de `status === 403` (Bloque F) a `status >= 400 && data instanceof Blob` (línea 144) — **bien**, captura 401/403/404/422 si vienen con Blob body. Más defensivo.
- ✅ `parsed = null` explícito en el catch interno — más legible que `parsed` quedándose en `undefined`.

**Veredicto:** el fix V4-2 es estructuralmente impecable. **El path 403 con Blob ahora surfaceará el mensaje del backend** ("No tiene permisos para descargar el PDF consolidado" o el que emita la APIResponse). Cierra el blocker UX de PL gates en B.12 dossier.

**Caveat residual (carry-over v4 §1.3 caveat #3):** sigue sin test del 403 path en `__tests__/dossierService.test.ts`. El happy path es lo único cubierto. 15 LOC P1 de cobertura defensiva.

### 1.2 V4-N3 — ESLint baseline restaurado

```
$ npx eslint src --max-warnings 999 | tail -3
  334:3   error  'Forget' is defined but never used         @typescript-eslint/no-unused-vars
  340:42  error  Unexpected any. Specify a different type   @typescript-eslint/no-explicit-any

✖ 278 problems (259 errors, 19 warnings)
```

**Exacto 278**, no 279. Baseline ≤278 mantenida. Los 2 errores finales en cola pertenecen a `src/generated/` (pre-existente, no causado por el commit). Regresión cerrada.

### 1.3 V4-4 — HROverview limpio

```
$ grep "\.status" HROverviewDashboard.tsx → 0 matches
$ grep "latestPlanilla.estado" HROverviewDashboard.tsx → 1 match (línea 738)
```

Línea 738 ahora:
```tsx
sub={latestPlanilla ? `${formatPeriodo(latestPlanilla.periodo)} · ${latestPlanilla.estado_texto ?? latestPlanilla.estado ?? '—'}` : 'Sin planillas'}
```

5/5 sites migrados. KPI legible cuando hay planillas seedeadas que emitan `estado`.

---

## 2. V4-3 — services blob sin parser 403 (carry-over crítico)

El v4 §1.3 listó 6-7 services con `responseType: 'blob'` SIN el parser 403. **Confirmado v5: ninguno fue tocado por el Bloque G** (alcance focal). Re-listado con verificación de existencia:

| # | Service / endpoint | Archivo | ¿Parser 403? | Backend PL gating |
|---|--------------------|---------|--------------|--------------------|
| 1 | Work certificate PDF | `features/documents/services/workCertificateService.ts` | ❌ No | Probable (B.13) |
| 2 | Payslip PDF | `features/payroll/services/payrollService.ts` | ❌ No | Post-D |
| 3 | Induction certificate | `features/onboarding/services/inductionService.ts` | ❌ No | Posible |
| 4 | MPP register | `features/organization/services/publicPositionService.ts` | ❌ No | Probable |
| 5 | Resolution PDF | `features/organization/services/displacementService.ts` | ❌ No | Posible |
| 6 | Anexo3 TXT | `features/contracts/services/tRegistroService.ts` | ❌ No | Probable |
| 7 | CCF Excel | `features/compensation/services/ccfService.ts` | ❌ No | Posible |
| — | DigitalDossier PDF | `features/documents/services/dossierService.ts` | ✅ Sí | Confirmed (B.12 #118) |

**Recomendación (sin cambios vs v4):** extraer helper `unwrapBlobError(err, fallback)` en `shared/api/blobErrors.ts` + cablear los 7 sites + 1 test del 403 path en dossierService (15 LOC). **Estimado: 30-45 min, 0 risk, mucho ROI** cuando D-Pay y B.13 produzcan más PL gates.

---

## 3. Pendientes del v3/v4 (re-confirmados, intactos)

| # | Hallazgo | Estado v4 | Estado v5 | Notas |
|---|----------|-----------|-----------|-------|
| 1 | 5 imports rotos `@/shared/ui/loading-spinner` | ABIERTO | **ABIERTO** | grep confirma 5/5 (EmpleadosListPage:19, modals/Datos*Modal ×4). Invisible a tsc porque viven en código muerto (página huérfana). |
| 2 | 29 console.log en `EmpleadosListPage.tsx` | ABIERTO | **ABIERTO** | grep count = 29 (29 occurrences in 1 file). |
| 3 | `EmpleadosListPage.tsx` huérfana (no ruteada) | ABIERTO | **ABIERTO** | App.tsx ruteo sin cambios. **Borrar página + 4 modales + entries en index cierra simultáneamente #1+#2+#3.** |
| 4 | 3 badges "Activo" duplicados | ABIERTO | **ABIERTO** | grep `Activo` → 11 ocurrencias en 6 files (varias variantes); las duplicaciones específicas v3 siguen sin tocar. |
| 5 | `EmpleadoReportPage.tsx:123` `Number(id)` con UUID | ABIERTO | **ABIERTO** | Sin observabilidad mientras IDs sigan int en demo-pro. |
| 6 | Hardcoded `/api/v1/rrhh/...` en `src/generated/api/services/RrhhService.ts` | ABIERTO | **ABIERTO** | Cliente generado muerto. |
| 7 | `DigitalDossierListPage` sin banner PL filtrado | ABIERTO | **ABIERTO** | UX no auto-explicativa. |
| V4-3 | 6-7 services blob sin parser 403 | ABIERTO | **ABIERTO** | Ver §2 arriba. |
| 8 | Modularidad — 0/4 bloqueos correctos | ABIERTO | **ABIERTO** | TenantContext sigue sin `plan`. Sub-proyecto E intacto. |

---

## 4. Hallazgos NUEVOS de v5

### 4.1 🟢 Ninguno crítico

`npx tsc --noEmit` exit **0** (sin output) — los fixes de V4-2 no introdujeron regresiones de tipos. `npm test -- --run` mantiene **178/178** sin caídas. ESLint **278** baseline exacta. No hay side-effects detectables en otros components que importen `dossierService`.

### 4.2 🟢 dossierService caller path verificado

`DigitalDossierListPage.tsx` (caller del `downloadConsolidatedPdf`) sigue capturando con `e instanceof Error` y mostrando `toast.error(e.message)`. Con el nuevo `throw new Error(parsed.message)` el toast ahora mostrará el mensaje humano del backend (PL gate denied). **Cadena E2E completa funcional.**

### 4.3 🟡 Cobertura V4-2 — sigue sin test del 403 path

Persiste del v4 (§1.3 caveat #3). No es regresión, es deuda. Sugerencia: agregar el test al próximo bloque "polish pre-D".

---

## 5. Status diseño + modularidad

### 5.1 Diseño — sigue WARN (idéntico v4)

Razón: el Bloque G fue 100% scope acotado a los 3 blockers v4. Los pendientes UX (página huérfana, 29 console.log, 5 imports rotos, 3 badges duplicados, V4-3 7 services) **no movieron**. Limpieza acumulada estimada: ~1.5 h. Un mini-sprint "Bloque H — polish pre-D" lo cerraría todo.

### 5.2 Modularidad — sigue FAIL (idéntico)

Sin cambios. `TenantContext.tsx`, `workspaceService`, `menuService`, `App.tsx` intactos. El bloqueo modular sigue siendo:

- Backend `MenuService` retorna todos los items autorizados; **no filtra por módulos contratados** (plan tier).
- Frontend Sidebar renderiza lo que el backend devuelve; **sin gating client-side por plan**.
- URLs como `/empleados`, `/contratos`, `/payroll` accesibles sin chequeo de feature-flag → no hay upgrade prompt ni 403 amigable.

**Sketch sub-proyecto E sigue válido sin cambios:** 4.5h / ~305 LOC. Pre-requisito antes de D-Pay si se quiere demo modular real.

---

## 6. Test runs

```
$ npx tsc --noEmit; echo "EXIT=$?"
EXIT=0

$ npm test -- --run | tail
Test Files  28 passed (28)
     Tests  178 passed (178)
  Duration  38.53s

$ npx eslint src --max-warnings 999 | tail -3
  334:3   error  'Forget' is defined but never used         @typescript-eslint/no-unused-vars
  340:42  error  Unexpected any. Specify a different type   @typescript-eslint/no-explicit-any
✖ 278 problems (259 errors, 19 warnings)

$ git log --oneline -1
ebb039b9 fix(identity): Bloque G — close v4 audit blockers (admin permisos under tenant context)

$ grep "@/shared/ui/loading-spinner" src/  → 5 matches (sin cambios)
$ grep "\.status" HROverviewDashboard.tsx  → 0 matches (V4-4 cerrado)
$ grep "parseErr" src/                      → 0 matches (V4-N3 cerrado)
$ grep "console\.log" features/employees/   → 29 (sin cambios, EmpleadosListPage huérfana)
```

---

## 7. Verdict diseño + modularidad — resumen

- **Diseño:** 🟡 WARN. Los 3 blockers v4 (UX + ESLint) cerrados con calidad estructural alta. Deuda v3/v4 (huérfana, console.log, imports rotos, badges, V4-3) **no atendida** por scope. Recomendación: mini-bloque H pre-D ~1.5 h.
- **Modularidad:** 🔴 FAIL. **Idéntico** a v3 y v4. Sub-proyecto E intacto. **Pre-requisito comercial sigue abierto** antes de arrancar D-Pay si se quiere demo modular real.
- **Tooling tipo:** 🟢 Operativo. tsc exit 0. ESLint baseline 278. Vitest 178/178. Cero regresiones técnicas.

---

## 8. Top-3 acciones priorizadas para sub-proyecto E (Modularidad)

| # | Prio | Horizonte | Acción | Estimado |
|---|------|-----------|--------|----------|
| **1** | **P1** | corto (próximo sprint) | **Crear `TenantContext.plan`**: agregar campo `plan: 'starter' \| 'pro' \| 'enterprise'` al payload de `/api/v1/auth/me/` y exponerlo vía `useTenant()`. El Sidebar y `App.tsx` rutean condicionalmente. Base de toda la modularidad. | ~1 h backend + 1 h frontend |
| **2** | **P1** | corto | **Filtrar `MenuService.get_menu_for_user()`** por `tenant.plan` — sólo retornar items cuyos módulos estén contratados. Sidebar refleja UX correcta sin cambios extra. | ~1 h backend |
| **3** | **P1** | corto | **Guard de ruteo `<FeatureRoute module="..."/>`** + componente `UpgradePromptCard` cuando user fuerza URL de módulo no contratado. Cierra el último gap UX modular (no 404 ni vista vacía). | ~1.5 h frontend |

**Total sub-proyecto E**: 4.5 h / ~305 LOC (sin cambios vs sketch v3/v4). Sigue siendo el camino más corto de "demo HR genérico" a "demo SaaS modular vendible".

---

## 9. Cambios aplicados

Ninguno. READ-ONLY conforme al brief.

---

## 10. Pregunta pendiente al humano

¿**Bloque H** (polish pre-D: borrar página huérfana + 4 modales + 29 console.log + 5 imports rotos + V4-3 helper Blob + tests cobertura ≈ 1.5 h) **antes** o **paralelo** al sub-proyecto E (Modularidad ~4.5 h)? Recomendación: secuencial Bloque H → E. El polish destraba ESLint y deja el módulo Empleados limpio antes de meter feature flags encima. Si la priorización del negocio es "vender ya en modo modular", arrancar E directamente y dejar el polish para post-D.
