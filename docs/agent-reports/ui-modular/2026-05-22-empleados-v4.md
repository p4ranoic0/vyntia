# UI Modular — Empleados v4 (post Bloque F frontend, commit `c35aebfe`)

**Fecha:** 2026-05-22
**Scope:** verificación de los 4 fixes UI del Bloque F + re-confirmación de pendientes v3
**Audit previo:** v3 `2026-05-22-empleados-v3.md`, PM v3 `pm/2026-05-22-empleados-v3.md`
**Modo:** READ-ONLY (no edits)
**Confianza:** alta (tsc exit 0 confirmado, vitest 178/178, ESLint corrido)
**Tiempo invertido:** ~20 min

---

## TL;DR

🟢 **3.5 de 4 fixes confirmados** — el Bloque F cerró los hallazgos N4 y N5 del PM v3 y destrabó el tooling de tipos (tsconfig + HROverview). Sin embargo, **`HROverviewDashboard.tsx:738` quedó con un `latestPlanilla.status` residual** que el commit perdió. Modularidad sigue FAIL idéntico (sub-proyecto E pendiente).

| Lente | Verdict v3 | Verdict v4 | Cambio |
|-------|-----------|-----------|--------|
| Diseño / consistencia VYNTIA | WARN | **WARN** | 3 fixes UX cerrados, 1 parcial. Pendientes v3 (imports rotos, console.log, página huérfana, badges) **siguen intactos**. |
| Modularidad comercial | FAIL | **FAIL** (idéntico) | Sin progreso. Sketch sub-proyecto E (4.5h / ~305 LOC) sigue válido sin cambios. |
| Tooling de tipos | 🔴 Ciego (tsc abortaba TS5103) | **🟢 Operativo** | tsc exit 0 destrabado. Sorprendente: **no reveló los 5 imports rotos** de `loading-spinner` — están en código no compilado en el grafo activo. Investigar. |

---

## 1. Verificación de los 4 fixes del Bloque F

| # | Fix | Archivo | Verdict | Notas |
|---|-----|---------|---------|-------|
| 1 | `tsconfig.json` quitar `ignoreDeprecations` | `tsconfig.json` | ✅ **FIX CONFIRMADO** | `npx tsc --noEmit` exit code **0**. La línea `"ignoreDeprecations": "6.0"` ya no existe (archivo limpio 13 líneas, solo `baseUrl` + `paths`). |
| 2 | `HROverviewDashboard p.status` → `p.estado` | `pages/HROverviewDashboard.tsx` | ⚠️ **PARCIAL** | 4 sites previos OK (479, 496, 589, 658). **Pero línea 738 sigue con `latestPlanilla.status`** dentro del KPI card "Planilla más reciente". El commit pasó por encima del 5º site. |
| 3 | `dossierService` 403 Blob parser | `features/documents/services/dossierService.ts:127-157` | ✅ **FIX CONFIRMADO** | try/catch correcto, parsea Blob → JSON → `parsed.message`. **Caveats abajo (§1.3)**. |
| 4 | `NuevoEmpleadoDialog` validación inline + DRF field error parser | `features/employees/pages/Empleados.tsx:184-242` | ✅ **FIX CONFIRMADO** | Regex DNI `/^\d{8}$/`, CE `/^\d{8,12}$/`, edad >= 18 con `today.replace(year=-18)` (consistente con N7 PM v3). Parser DRF robusto (Array.isArray + string fallback). |

### 1.1 tsc destrabado — sí, pero los 5 imports rotos siguen invisibles

`npx tsc --noEmit` ahora retorna **exit code 0 sin output**. Esto significa una de dos cosas:

- **(a)** los archivos `EmpleadosListPage.tsx` + 4 `modals/Datos*Modal.tsx` **no entran al grafo de compilación** de `tsconfig.app.json` (ej. están excluidos por algún `include` selectivo, o no se importan desde nada que sí esté en el grafo).
- **(b)** El módulo `@/shared/ui/loading-spinner` existe y solo el grep falló — improbable, ya que el v2/v3 confirmaron que el path correcto es `@/shared/components/LoadingSpinner`.

**Verificable:** los 5 imports siguen presentes literalmente (grep en §0 abajo coincide con v3):
```
src/features/employees/pages/EmpleadosListPage.tsx:19
src/features/employees/modals/DatosFamiliaresModal.tsx:25
src/features/employees/modals/DatosLaboralesModal.tsx:23
src/features/employees/modals/DatosAcademicosModal.tsx:25
src/features/employees/modals/DatosPersonalesModal.tsx:23
```

**Hipótesis (a) es probable:** los 4 modales `Datos*Modal.tsx` solo se referencian desde `EmpleadosListPage.tsx` (página huérfana, no ruteada — confirmado v3 §1.1 vía `App.tsx:23, 322-326`). Si `EmpleadosListPage.tsx` no se importa desde ningún archivo "vivo" del grafo (Empleados.tsx ruteado, no la lista), TypeScript no los visita.

**Consecuencia:** el fix de tsconfig (Bloque F #1) **destrabó el typecheck pero no expuso los bugs latentes** porque viven en código muerto. Reafirma la recomendación v3: **borrar `EmpleadosListPage.tsx` + 4 modales + entries en `pages/index.ts` / `modals/index.ts`**. Una vez fuera, los 5 imports rotos desaparecen (y los 29 console.log también — todos viven en el huérfano).

### 1.2 HROverview — un 5º site quedó

Site exacto **no atendido**:

```tsx
// HROverviewDashboard.tsx:738
sub={latestPlanilla ? `${formatPeriodo(latestPlanilla.periodo)} · ${latestPlanilla.estado_texto ?? latestPlanilla.status ?? '—'}` : 'Sin planillas'}
```

**Impacto runtime:** idéntico a los 4 sites del v3 — con planillas seedeadas que emitan `estado` (no `status`), el KPI mostrará `—` en vez del estado real (fallback chain `estado_texto ?? status ?? '—'` salta directo al final). UX-leve, no crítico, pero rompe el patrón.

**Fix sugerido (5 seg):** `latestPlanilla.status` → `latestPlanilla.estado` en línea 738.

### 1.3 dossierService — robusto pero con 1 caveat

El try/catch en `dossierService.ts:127-157` es correcto y maneja:
- ✅ Caso happy path → retorna Blob
- ✅ Caso 403 con Blob JSON → parsea, throw `Error(parsed.message)`
- ✅ Caso 403 sin Blob (data ya parseada) → fall through al `throw err` original
- ✅ Caso Blob 403 pero no-JSON → catch interno silencia parseErr y cae al `throw err` final

**Caveat #1 — caller debe esperar `Error` ahora.** Antes el catch en `DigitalDossierListPage.tsx:62-65` esperaba `e instanceof Error` (siempre verdadero para axios errors). Ahora recibe un `Error` nativo construido por el service. **Verificar que el toast del caller use `err.message`** y no `err.response?.data?.message`. Lectura rápida v3 sugería `toast.error(e.message)` ya estaba ahí → OK.

**Caveat #2 — solo `dossierService` tiene este fix.** Otros 5 endpoints download de PDF con `responseType: 'blob'` **siguen sin el mismo guardarail**:

| Endpoint | Archivo:línea | ¿Backend gating? |
|----------|---------------|-------------------|
| Work certificate PDF | `features/documents/services/workCertificateService.ts:77-82` | Probable (B.13) |
| Payslip PDF | `features/payroll/services/payrollService.ts:708-716` | Probable (post-D) |
| Induction certificate | `features/onboarding/services/inductionService.ts:155-160` | Posible |
| MPP register | `features/organization/services/publicPositionService.ts:192-198` | Probable |
| Resolution PDF | `features/organization/services/displacementService.ts:176-181` | Posible |
| Anexo3 TXT | `features/contracts/services/tRegistroService.ts:178-184` | Probable |
| CCF Excel template | `features/compensation/services/ccfService.ts:291-295` | Posible |

**Recomendación CORTA (no urgente):** extraer el parser 403 a un helper en `shared/api/blobErrors.ts`:

```ts
export async function unwrapBlobError(err: unknown, fallback: string): Promise<never> {
  const e = err as { response?: { status?: number; data?: Blob } }
  if (e.response?.status === 403 && e.response.data instanceof Blob) {
    const text = await e.response.data.text()
    try {
      const parsed = JSON.parse(text)
      throw new Error(parsed?.message || fallback)
    } catch { /* fall through */ }
  }
  throw err
}
```

Luego envolver cada download como:
```ts
try { ... return r.data } catch (e) { await unwrapBlobError(e, 'No tiene permisos') }
```

Estimado: 30 min para crear helper + cablear 6 sites. **Cero risk, mucho ROI** si el equipo backend planea cerrar más PL gates.

**Caveat #3 — no hay test del 403 path.** `__tests__/dossierService.test.ts:47-56` solo cubre happy path (Blob de éxito). El branch 403 nunca se ejercita en CI. Agregar:

```ts
it('downloadConsolidatedPdf surfaces 403 message from Blob body', async () => {
  const errBlob = new Blob([JSON.stringify({ message: 'Sin permisos PL 9' })])
  vi.mocked(apiClient.get).mockRejectedValueOnce({ response: { status: 403, data: errBlob } } as never)
  await expect(dossierService.downloadConsolidatedPdf('d1')).rejects.toThrow('Sin permisos PL 9')
})
```

15 LOC. P1 deuda de cobertura.

### 1.4 NuevoEmpleadoDialog — validación inline robusta

Análisis archivo Empleados.tsx:184-242:

- ✅ **DNI regex** `/^\d{8}$/` correcto (8 dígitos numéricos exactos, espeja backend Block A `validate_numero_documento`).
- ✅ **CE regex** `/^\d{8,12}$/` razonable (la realidad: el CE peruano son 9 dígitos, pero rango 8-12 es defensivo). El Input línea 292 usa `maxLength={12}` → match.
- ✅ **Edad** `new Date(today.getFullYear() - 18, today.getMonth(), today.getDate())` — consistente con la recomendación del PM v3 N7 (no usa la heurística `18*365` con off-by-one). Bien.
- ✅ **Future date check** previo a edad — bonus, no estaba en el brief.
- ✅ **DRF field error parser** (línea 222-237):
  - Lee `err.response.data.data ?? err.response.data` → cubre tanto el shape envuelto por `APIResponse.error()` (`{success, message, data: {field: [msgs]}}`) como el shape raw DRF (`{field: [msgs]}`). **Robusto.**
  - Trata Array (DRF estándar) y string (errores no-field) → cubre `non_field_errors` también.
  - Concatena `field: msg` con ` · ` separador (tono consistente con otros toasts del módulo).
- ⚠️ **Tono inconsistente menor:** los mensajes inline (líneas 193, 197, 206, 210) usan punto final ("...numéricos.", "...años."); el toast del DRF parser no agrega punto. Cosmético. No bloquea.
- ⚠️ **Pasaporte/CE de otra nacionalidad no validado.** Si `tipoDoc` cae en el `else` (ni DNI ni CE — ej. `'PASAPORTE'`), no se ejecuta ningún regex. El backend lo rechazará → fallback al DRF parser. Aceptable.
- ✅ Mensaje **"El empleado debe tener al menos 18 años"** matchea casi-textualmente lo que el backend Block A emite (`"...mínimo 18 años (Ley 28518)"`). Probable doble-toast si user submitea con edad inválida ANTES del fix inline (race). Recomendación: usar el mismo wording exacto para evitar inconsistencia perceptible.

**Verdict:** parser e validación inline cumplen el contrato del PM v3 N5.

---

## 2. Hallazgos pendientes del v3 (re-confirmados)

| # | Hallazgo v3 | Estado v4 | Notas |
|---|------------|-----------|-------|
| 1 | 5 imports rotos `@/shared/ui/loading-spinner` | **ABIERTO** | Confirmados los 5/5 (grep §0). tsc no los ve porque viven en `EmpleadosListPage` huérfana. |
| 2 | 29 console.log en `EmpleadosListPage.tsx` | **ABIERTO** | grep count = 29 (idéntico). |
| 3 | `EmpleadosListPage.tsx` página huérfana | **ABIERTO** | App.tsx ruteo sin cambios. **Borrar resuelve simultáneamente #1, #2, #3.** |
| 4 | 3 badges "Activo" duplicados | **ABIERTO** | No tocado por el Bloque F. |
| 5 | `EmpleadoReportPage.tsx:123` `Number(id)` con UUID | **ABIERTO** | No tocado. Sin observabilidad hoy (IDs aún int en demo-pro). |
| 6 | Hardcoded `/api/v1/rrhh/...` en `src/generated/api/services/RrhhService.ts` | **ABIERTO** | tsc operativo ahora — si algún componente lo importara, se vería. Sigue siendo cliente generado muerto. |
| 7 | `DigitalDossierListPage` sin banner PL filtrado | **ABIERTO** | No tocado. |
| 8 | Modularidad — 0/4 bloqueos correctos | **ABIERTO** | TenantContext sigue sin `plan`. Sub-proyecto E intacto. |

---

## 3. Nuevos hallazgos del v4

### 3.1 🟡 `HROverviewDashboard.tsx:738` — 5º site `.status` perdido en el fix

Severidad: BAJA · UX-leve (KPI muestra `—` en vez del estado real cuando hay planillas).
Fix: 5 segundos, una línea. Reportado en §1.2.

### 3.2 🟡 `dossierService.downloadConsolidatedPdf` sin test del 403 path

Severidad: MEDIA (deuda de cobertura) · Riesgo: regresión silenciosa si el helper Blob parser se modifica.
Fix: 15 LOC en `__tests__/dossierService.test.ts`. Sugerido en §1.3 caveat #3.

### 3.3 🟡 6 endpoints download Blob NO replican el patrón 403-aware

Severidad: MEDIA · listado completo en §1.3 caveat #2.
Fix: helper compartido + 6 cableados ≈ 30 min. P1 si el equipo backend planea cerrar más PL gates en otros módulos (B.13 work certificate parece candidato natural).

### 3.4 🟢 ESLint subió 1 problema (278 → 279)

Severidad: NINGUNA (debajo del baseline ≤299 oficial).
`260 errors + 19 warnings = 279 problems`. El v3 reportaba ≤278. Posible nuevo `any` o nombre no usado introducido por el commit Block F. Triagable cuando se haga limpieza de baseline.

### 3.5 🟢 `tsconfig` destrabado — efecto secundario positivo confirmado

**Test baseline observable**: `npx tsc --noEmit` ahora retorna `exit 0` (antes: nonzero TS5103). **El repo recuperó su red de seguridad de tipos.** Cualquier regresión futura va a ser visible localmente y en CI. **Este es el ROI más grande del Bloque F.** Próxima vez que alguien tipee `p.status` donde la interface declara `estado?`, tsc va a quejarse.

---

## 4. Status diseño + modularidad

### 4.1 Diseño — sigue WARN

Razón: 3.5/4 fixes cerrados pero los pendientes v3 (página huérfana, 29 console.log, 5 imports rotos, badges duplicados) sumados al residual `latestPlanilla.status` (§1.2) acumulan ~1 h de limpieza pendiente. **No es bloqueador**, pero el módulo Empleados sigue con deuda visible.

### 4.2 Modularidad — sigue FAIL (idéntico)

Sin cambios en `TenantContext.tsx`, `workspaceService`, `menuService`, `App.tsx`. El sketch del v3 §4 (4.5h / ~305 LOC) sigue siendo el camino correcto. **El Bloque F no movió la aguja modular.** Pre-requisito comercial sigue abierto antes de D-Pay.

---

## 5. Acciones recomendadas

| # | Prio | Horizonte | Acción |
|---|------|-----------|--------|
| 1 | **P0** | 5 seg | `HROverviewDashboard.tsx:738`: `latestPlanilla.status` → `latestPlanilla.estado`. Cierra el 5º site. |
| 2 | **P1** | 5 min | Borrar `EmpleadosListPage.tsx` + `modals/Datos*Modal.tsx` ×4 + entries en `pages/index.ts:8` y `modals/index.ts`. Limpia 5 imports rotos + 29 console.log + página huérfana en un commit. |
| 3 | **P2** | 30 min | Extraer helper `unwrapBlobError(err, fallback)` en `shared/api/blobErrors.ts` + cablear los 6 downloads Blob restantes (workCertificate, payslip, induction cert, MPP, displacement, tRegistro, ccf template). Test del 403 path en dossierService. |
| 4 | **P1** | 4.5 h | **Sub-proyecto E (Modularidad)** — sin cambios vs sketch v3 §4. Pre-requisito antes de arrancar D-Pay. |
| 5 | P3 | 5 min | Triagar el +1 ESLint problem (278 → 279) si emerge en el próximo `code-quality` audit. |

---

## 6. Cambios aplicados

Ninguno. READ-ONLY conforme al brief.

---

## 7. Pregunta pendiente al humano

Sigue idéntica a v3: **¿abro brainstorm para sub-proyecto E (Modularidad) antes de D-Pay, o consolido primero un mini-sprint "Bloque G" con la acción #1+#2 (~10 min) + las 6 downloads Blob (#3)?** El Bloque F cerró 3.5/4 fixes en una corrida; un Bloque G corto puede dejar todo el módulo Empleados limpio antes de meter feature flags encima.

---

## 0. Apéndice — Evidencia ejecutada

```
$ cd D:/VYNTIA/apps/web && npx tsc --noEmit; echo "EXIT=$?"
EXIT=0

$ npm test -- --run | tail
Test Files  28 passed (28)
     Tests  178 passed (178)
  Duration  14.16s

$ npx eslint src --max-warnings 999 | tail
✖ 279 problems (260 errors, 19 warnings)

$ grep "@/shared/ui/loading-spinner" src/
EmpleadosListPage.tsx:19
modals/DatosFamiliaresModal.tsx:25
modals/DatosLaboralesModal.tsx:23
modals/DatosAcademicosModal.tsx:25
modals/DatosPersonalesModal.tsx:23
(5 matches — idéntico v3, tsc no los visita por código muerto)

$ grep "\.status" src/features/employees/pages/HROverviewDashboard.tsx
738:  sub={latestPlanilla ? ... latestPlanilla.estado_texto ?? latestPlanilla.status ?? ... }
(1 match — site faltante)

$ grep "responseType.*blob" src/ -l
shared/api/api.ts
features/onboarding/services/inductionService.ts
features/payroll/services/payrollService.ts
features/documents/services/workCertificateService.ts
features/documents/services/dossierService.ts         <-- único con 403 parser
features/organization/services/publicPositionService.ts
features/organization/services/displacementService.ts
features/contracts/services/tRegistroService.ts
features/compensation/services/ccfService.ts
```
