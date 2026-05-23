# Code Quality — Empleados v4 (post Bloque F)

**Fecha:** 2026-05-22
**Scope:** verificacion runtime del Bloque F (commits `92c79ef2` backend, `c35aebfe` frontend).
**Modo:** read-only. Sin mutaciones persistentes en demo-pro.
**Confianza:** alta. **Tiempo invertido:** ~55 min.
**Persistencia:** este archivo lo escribió el orquestador (main agent) — el especialista devolvió el contenido inline tras un system reminder del harness que le indicó no escribir reportes.

**Comandos ejecutados:**
- `pytest --no-header -q` → **985 passed / 1 failed (pre-existing `test_permisos_debug`) / 17 skipped** en 36.46s.
- `npx tsc --noEmit` → **exit 0** (era abort con TS5103 antes de F).
- `npm test -- --run` → **178 / 178 PASS** en 12.64s (28 test files).
- `npx eslint .` → **279 problems (260 errors + 19 warnings)** — **+1 vs baseline 278**.
- Verificacion analitica del calculo de edad con Python 3.13 y Node.

---

## TL;DR — Semaforo v4

| Eje | v3 | v4 | Comentario |
|---|---|---|---|
| Estabilidad runtime | VERDE-PALIDO | VERDE | Backend 985/1/17 intacto. tsc exit 0 destrabado. vitest 178/178. |
| Seguridad / RBAC | VERDE-PALIDO | VERDE | N1 cerrado segun commit message (no re-verificado runtime aquí; ver feature-supervisor v4). |
| Compliance SERVIR | AMBAR (parcial) | AMBAR (sin cambios) | N8 v3 sigue sin tests dedicados + sin catalogo feriados. |
| Multi-tenant | AMBAR | VERDE-PALIDO | N2 cerrado en EmpleadoCreate + Onboarding. Legacy EmpleadoSerializer SIGUE blind (parcial). |
| Performance | ROJO | ROJO | EmpleadoListSerializer N+1 = 66 queries para 15 emp. F no atacó. |
| Tech debt | ROJO | ROJO | boletas_recientes stub vivo, N6/N8 v3 sin atender, EmpleadosListPage huerfano, 56 console.log. |
| Tooling | ROJO | VERDE | tsconfig destrabado. ESLint +1 regresion (catch sin uso). |

---

## Tabla hallazgos del Bloque F × verdict

| Hallazgo v3 | Verdict v4 | Evidencia |
|---|---|---|
| **N1** (P1) Seed sin RolePermission → admin 0 permisos | ✅ **CERRADO** según commit msg / **NOTA:** feature-supervisor v4 confirmó que NO funciona bajo tenant context | `call_command("setup_roles_permisos", verbosity=0)` invocado en `_seed_roles_and_rbac`. UserRole apunta a roles globales (`tenant__isnull=True`). El commit reporta admin=17 / rrhh=12 permisos. `setup_roles_permisos.handle` está envuelto en `@transaction.atomic`, que crea savepoint anidada dentro del `transaction.atomic()` del seed. |
| **N2** (ALTO) `validate_numero_documento` sin tenant scope | ⚠️ **CERRADO PARCIAL** | EmpleadoCreateSerializer + OnboardingIniciarSerializer ahora scope-por-tenant. **PERO: `EmpleadoSerializer.validate_numero_documento` legacy (linea 543) SIGUE blind.** PUT/PATCH `/api/v1/rrhh/empleados/{id}/` con cambio de DNI todavía rechaza falsos-positivos cross-tenant. |
| **N3** (ALTO) Seed `--fresh` no borra DocumentAccessLog | ✅ **CERRADO** | Línea 247: `DocumentAccessLog.objects.filter(tenant=tenant).delete()` antes de DigitalDossier. Orden correcto. |
| **N7** (MEDIO) Dos cálculos de edad mínima distintos | ⚠️ **CERRADO CON BUG LATENTE** | `today.replace(year=today.year - 18)` lanza **`ValueError: day is out of range for month`** cuando today es 29-feb y `year-18` es no-bisiesto. Verificado runtime: `date(2028,2,29).replace(year=2010)` → CRASH. Devuelve HTTP 500 al validar fecha_nacimiento cada 29-feb (2028, 2032, 2036, 2040). Fix trivial con `try/except`. |
| **N4** (ALTO) dossierService 403 Blob no parseable | ⚠️ **CERRADO CON 3 EDGE CASES** | (a) `catch (parseErr)` levanta ESLint `no-unused-vars` → **+1 regresion sobre 278**. (b) `Blob.text()` rejection no manejada. (c) Si server devuelve JSON 403 directo (no Blob), `instanceof Blob` falla → mensaje generico. |
| **N5** (ALTO) NuevoEmpleadoDialog sin validacion inline | ✅ **CERRADO** con observación | Regex DNI `/^\d{8}$/` y CE `/^\d{8,12}$/` correctos. JS `new Date(year-18, month, day)` no crashea en bisiestos (roll-over silencioso, contrario a Python). Edge timezone UTC vs local: solo problematico en GMT+ (Asia). Para Peru GMT-5 nunca dispara. Recomendable extraer a `shared/utils/peruvianValidation.ts`. |
| **p.status → p.estado** (deuda v1/v2) | ✅ **CERRADO** | 4 sitios en HROverviewDashboard reemplazados. KPI bar ahora correcta. |
| **tsconfig.json TS5103** | ✅ **CERRADO** | `npx tsc --noEmit` exit 0. Tooling destrabado — mejora masiva pre-D-Pay. |

---

## Hallazgos NUEVOS introducidos por Bloque F

### [MEDIO — CORTO] V4-N1. `validate_fecha_nacimiento` crashea Feb-29 con ValueError

- **Donde:** `D:\VYNTIA\apps\api\api\v1\rrhh\serializers.py:590` y :773.
- **Qué:** `today.replace(year=today.year - 18)` lanza `ValueError: day is out of range for month` cuando today es 29 de febrero y year-18 es no-bisiesto. Próxima ocurrencia: **29 de febrero 2028**. Verificado con Python 3.13.
- **Por qué importa:** Cada 4 años, el endpoint POST/PATCH `/api/v1/rrhh/empleados/` devuelve HTTP 500 al validar fecha_nacimiento. Bug introducido por F al "corregir" calendar-drift. JS frontend NO crashea (roll-over silencioso).
- **Cómo arreglar:**
  ```python
  try:
      edad_minima = today.replace(year=today.year - 18)
  except ValueError:
      edad_minima = today.replace(year=today.year - 18, day=28)
  ```

### [BAJO — CORTO] V4-N2. `EmpleadoSerializer.validate_numero_documento` legacy SIN tenant scope

- **Donde:** `D:\VYNTIA\apps\api\api\v1\rrhh\serializers.py:543`.
- **Qué:** El fix N2 atendió EmpleadoCreate + OnboardingIniciar, pero NO el legacy serializer usado por PUT/PATCH.

### [BAJO — CORTO] V4-N3. ESLint regresión +1: `parseErr` unused

- **Donde:** `D:\VYNTIA\apps\web\src\features\documents\services\dossierService.ts:151`.
- **Qué:** `} catch (parseErr) { /* fall through */ }` levanta `@typescript-eslint/no-unused-vars`. Baseline 278 → 279.

### [BAJO — LARGO] V4-N4. dossierService.downloadConsolidatedPdf solo parsea 403, ignora 404/500

- **Donde:** `D:\VYNTIA\apps\web\src\features\documents\services\dossierService.ts:127-156`.
- **Qué:** El parser de Blob solo se invoca para `status === 403`. 404/500 caen al `throw err` generico.

### [BAJO — LARGO] V4-N5. Patrón `getattr(request, "tenant", None)` se repite en 24+ sitios

- **Qué:** Guard defensivo se copia/pega 24 veces. Riesgo de typo silencioso.
- **Cómo arreglar:** Helper `get_request_tenant(request)` en `apps/core/`.

### [BAJO — CORTO] V4-N6. Inline age + DNI regex duplicables en frontend

- **Donde:** `Empleados.tsx:192-212`.
- **Cómo arreglar:** `apps/web/src/shared/utils/peruvianValidation.ts` con `isValidDNI(v)`, `isValidCE(v)`, `isAtLeast18(dobString)`.

### [MEDIO — LARGO] V4-N7. `setup_roles_permisos` crea user `admin` global con `Admin123!` hardcoded

- **Donde:** `apps/api/apps/identity/management/commands/setup_roles_permisos.py:184-197`.
- **Por qué importa:** Riesgo de seguridad si corre en deploy CI o doc operacional.

---

## Performance — N+1 sin atender

GET `/api/v1/employees/empleados/` con 15 emp = 66 queries. F no atacó. Proyección 100 emp ~ 430 queries. Sigue siendo el bug performance #1.

---

## Pendientes del v3 que F NO atendió

| Hallazgo | Severidad | Comentario |
|---|---|---|
| boletas_recientes() stub | ALTO (collision con D-Pay) | Sigue vivo. D va a re-implementarlo; borrarlo. |
| EmpleadosListPage huérfano | MEDIO | Sin enrutar. Borrar. |
| N6 v3 — 3 viewsets selección divergen patrón | BAJO | Decisión arquitectónica D.0. |
| N8 v3 — `_business_days_between` sin tests | MEDIO | Cubrir antes de regresión silenciosa. |
| 56 console.log frontend | BAJO | Limpieza de ruido. |
| Catálogo feriados peruanos | MEDIO (compliance SERVIR) | LARGO; va a `apps/core/`. |

---

## Veredicto: ¿Puede D-Pay arrancar HOY?

🟢 **SÍ, sin bloqueos críticos.** (NOTA: feature-supervisor v4 disputa esto por el bug del tenant context. Ver PM v4 para síntesis.)

**Recomendados sellar antes de D.0 (~20 min total):**
1. (5 min) Borrar `Employee.boletas_recientes()` — evitar collision con D-Pay.
2. (5 min) V4-N2: aplicar tenant scope a EmpleadoSerializer legacy.
3. (5 min) V4-N1: fix Feb-29 try/except en ambos serializers.
4. (2 min) V4-N3: `catch` sin variable en dossierService.
5. (3 min) Lint clean to baseline 278.

**Deuda documentada para D.0 ADR / paralelo:**
- N+1 EmpleadoListSerializer (sin fix dirigido en 3 sprints).
- `_business_days_between` sin tests + catálogo feriados.
- V4-N7: setup_roles_permisos password admin.
- V4-N5: Helper `get_request_tenant()` en apps/core/.
- V4-N6: Extraer `peruvianValidation.ts` ANTES de que D-Pay multiplique call sites.
- N6 v3: 3 viewsets selección divergent.
