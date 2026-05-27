# PM — Contracts v1 audit cycle (2026-05-23)

**Orquestador:** main agent en rol PM (siguiendo playbook `.claude/agents/vyntia-pm.md`).
**Scope:** módulo CONTRACTS (`apps/api/apps/contracts/` + `api/v1/contracts/` + legacy `api/v1/rrhh/contratos_*` + `apps/web/src/features/contracts/`).
**Motivo:** replicar el ciclo audit→fix→audit que selló empleados (v1→v5, 29 fixes) ahora sobre contracts, para destapar bugs latentes ANTES de que el sub-proyecto **D — Vyntia Pay** los consuma (D usa Contract + EmploymentData + severance_service masivamente para cálculo de planilla).
**Especialistas lanzados (4, en 2 pares para evitar el abort por rate-limit — lección PM v5):**
- Par 1: `vyntia-feature-supervisor` + `vyntia-code-quality`
- Par 2: `vyntia-hr-tester` + `vyntia-ui-modular`
**Reportes fuente (todos persistidos en disco):**
- `docs/agent-reports/feature-supervisor/2026-05-23-contracts-v1.md`
- `docs/agent-reports/code-quality/2026-05-23-contracts-v1.md`
- `docs/agent-reports/hr-tester/2026-05-23-contracts-v1.md`
- `docs/agent-reports/ui-modular/2026-05-23-contracts-v1.md`

---

## TL;DR — Verdict ejecutivo

🔴 **ROJO para "listo-para-D" / 🟡 AMARILLO para el módulo en general.**

La cobertura de features está completa y cableada (feature-supervisor 🟢), pero los **2 especialistas de comportamiento convergen en el mismo punto caliente**: `severance_service.py` arrastra un crash y dos sobrepagos que D-Pay heredaría tal cual en planilla. Hay además un bug funcional ya ACTIVO hoy (dashboard reporta 0 contratos) y un AttributeError latente en `EmploymentData`. El módulo NO debe entrar a D sin un ciclo de fix dirigido (Bloque-H-contracts). La modularidad comercial (gating por plan) está ausente, pero eso es un sub-proyecto aparte, no un blocker de contracts.

**3 bloqueos numerados para D:**
1. `severance_service.py` crashea con cese 29-feb (`ValueError`) y sobrepaga vacaciones truncas/CTS por `+1` mes inclusivo — **confirmado por ejecución directa por 2 agentes independientes**.
2. `EmploymentData.__str__` / `generar_codigo_empleado` usan campos inexistentes en `Department` (`nombre_area`, `codigo_area`) → AttributeError en admin/logging — mismo bug que empleados-v3 cerró en `location_history.py`, EmploymentData quedó fuera del barrido.
3. Reportes/estadísticas de contratos filtran `status` en minúscula contra datos en MAYÚSCULA → dashboard RRHH muestra 0 activos/vencidos/terminados **silenciosamente, hoy**.

---

## Hallazgos top (consolidado de los 4 especialistas)

### 🔴 Críticos / Altos

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 1 | Cese 29-feb crashea con `ValueError: day is out of range` — `_compute_vac_truncas` construye `date(year-1, 2, 29)` que no existe en año no bisiesto | code-quality + **hr-tester (confirmado a runtime)** | `severance_service.py:100-106` | CORTO |
| 2 | `_months_between` sobrecuenta por `+1` inclusivo → vacaciones truncas y CTS **sobrepagan siempre** (1 mes exacto paga 5 días en vez de 2.5) | code-quality + **hr-tester (confirmado a runtime)** | `severance_service.py:40-47` | CORTO |
| 3 | Reportes/estadísticas filtran `status="activo/vencido/terminado"` (minúscula) pero el modelo guarda MAYÚSCULA → dashboard reporta **0 silenciosamente** (bug ACTIVO) | code-quality | `api/v1/rrhh/contratos_views.py:149,229-256,300-319` (vs `renovar_contrato:372` correcto) | CORTO |
| 4 | `EmploymentData.__str__` y `generar_codigo_empleado` usan `area.nombre_area`/`area.codigo_area` — campos inexistentes en `Department` → AttributeError | code-quality | `employment_data.py:169,341` | CORTO |
| 5 | Sin validación tope 5 años régimen 728 (D.Leg.728 art.74) ni desnaturalización modal→indefinido (D.S.001-96-TR art.77) — D necesita esto para clasificar beneficios | hr-tester (+ feature-supervisor) | `contract.py` (`clean()` ausente), ningún service | MEDIO |
| 6 | **Modularidad comercial inexistente:** 0 feature flags en FE; `Tenant.plan` existe pero no gobierna nada; T-Registro/liquidaciones/ceses expuestos en todo plan y burlables vía API (backend tampoco gatea) | ui-modular | grep `useFeatureFlag/hasModule/upsell`→0; `tenant.py:34`; `App.tsx:162` | LARGO (sub-proyecto) |

### 🟡 Medios

| # | Hallazgo | Fuente | Evidencia | Horizonte |
|---|----------|--------|-----------|-----------|
| 7 | `except Exception` ancho enmascara 500s reales como 400 | code-quality | viewsets contracts | CORTO |
| 8 | Fugas Decimal→float en agregados de reporte | code-quality | reportes contratos | MEDIO |
| 9 | T-Registro `submit` es stub sin idempotencia (OK para ahora, riesgo para SUNAT real) | code-quality | `tregistro_service.py` | LARGO |
| 10 | 4 páginas B.10-B.14 usan `window.prompt()` para capturar montos/razones — inaccesible, fuera de brand, no alcanzan pulido de Empleados v5 | ui-modular | `TRegistro/Probation/Severance/Termination ListPage.tsx` | MEDIO |
| 11 | Acento de marca ignorado: colores hardcoded (`text-blue-600`, `bg-red-100`) en vez de token `--primary #6C63FF` y variantes `Badge` | ui-modular | 4 nuevas pages | MEDIO |
| 12 | `/contract-amendments/` CRUD vivo pero sin consumidor frontend (endpoint huérfano; adendas solo vía PDF) | feature-supervisor | `api/v1/contracts/urls.py` | MEDIO |

### ✅ Lo que SÍ está bien

- Cobertura completa: 7/7 features construidas y alcanzables; 7 viewsets registrados, 5 páginas ruteadas, 6 entradas de menú seedeadas, services FE→endpoints reales (feature-supervisor).
- `manage.py check` 0 issues; sin migraciones pendientes.
- Régimen 728/CAS/276 completo con clasificación determinado/indeterminado (`contract.py:34-37`) — listo para planilla.
- Período de prueba 90/180/365 días correcto (hr-tester 🟢 flujo 3); T-Registro alta/baja/modificación correcto (🟢 flujo 5).
- `Count('id')` correcto aquí (PK literal `id` en Contract/Amendment), FK área directo por diseño, FK cross-app lazy sin ciclos, sin N+1 en viewsets nuevos, mutaciones con `transaction.atomic` y `RRHHPermission` (code-quality verificado vs CLAUDE.md).
- Tests del módulo verdes: backend 108→115 passed +3 xfailed (hr-tester codificó los 3 bugs como `xfail(strict=True)`), vitest 27/27, tsc 0 errores en contracts, eslint 0 warnings en contracts. **Sin regresión de baselines.**

---

## Trends que vemos cruzando los 4 reportes

1. **`severance_service.py` es el epicentro (señal fuerte).** code-quality lo marcó por inspección; hr-tester lo confirmó ejecutando los cómputos. Dos agentes independientes, mismo archivo, mismos 2 bugs (#1, #2). Es el riesgo #1 para D-Pay porque D basa la liquidación en este service.
2. **Bugs "campo inexistente en Department" reaparecen.** El mismo patrón que empleados-v3 arregló en `location_history.py` sigue vivo en `EmploymentData` (#4). Indica que el barrido de empleados v3-v5 no cruzó el límite de app a contracts → vale un grep global de `area.nombre_area|area.codigo_area|area.nombre`.
3. **Inconsistencia mayúscula/minúscula en `status`** (#3) es del mismo género que el punto anterior: convención de datos no centralizada en choices/constantes → bugs silenciosos de filtrado.
4. **Dos generaciones de UI conviven** (ContratosPage maduro vs 4 páginas B.10-B.14 con `window.prompt`). Deuda de pulido coherente con lo que v5 hizo en Empleados — contracts no recibió esa pasada.
5. **Gating comercial ausente en TODO el producto** (#6) — no es específico de contracts, pero contracts lo expone porque sus features avanzadas (T-Registro, liquidaciones, ceses) son justo las que un plan starter no debería ver.

---

## 3 acciones priorizadas

1. **CORTO — Abrir Bloque-H-contracts (fix dirigido) ANTES de que D consuma severance.** Alcance mínimo: bugs #1 (29-feb), #2 (`+1` inclusivo), #3 (status minúscula), #4 (`EmploymentData` campos inexistentes). Los 3 xfail de hr-tester (`test_contracts_hr_audit_v1.py`) virarán a XPASS y validarán el fix automáticamente. Esfuerzo bajo, impacto alto, desbloquea D.
2. **MEDIO — Resolver gaps legales 728 antes de planilla retroactiva:** validación tope 5 años (#5) y desnaturalización modal→indefinido. D necesita la clasificación correcta de beneficios. Decidir aquí la pregunta abierta de hr-tester: ¿el sobrepago por fracción de mes es bug a corregir o limitación documentada de "ADR-B.9 mínimo legal"?
3. **LARGO — Tratar la capa de modularidad comercial (plan→módulos) como sub-proyecto propio**, no como fix de contracts. Decisión arquitectónica bloqueante (pregunta de ui-modular): modelo (A) plan-tier→set fijo de módulos vs (B) add-ons por tenant. Backend primero (`TenantModule` o mapping + DRF permission), luego hook FE + `<ModuleRoute>` + upsell.

---

## ¿Más ciclos v2/v3 o sale a Bloque-H-contracts?

**Recomendación: → Bloque-H-contracts (1 ciclo de fix), NO más ciclos de audit.**

El audit v1 ya destapó hallazgos concretos, accionables y con tests que los codifican (xfail estricto). Repetir audit v2 sin fix primero sólo re-descubriría lo mismo. El patrón empleados fue audit→**fix**→audit; toca el fix. Tras Bloque-H-contracts, un audit v2 **estrecho** (solo severance + EmploymentData + status filter, vía hr-tester re-ejecutando los xfail) basta para sellar contracts-for-D. La modularidad (#6) se saca del scope de contracts y se agenda como su propio brainstorm+spec.

---

## Notas de proceso / persistencia

- Los 4 especialistas persistieron su reporte en disco al primer intento (sin necesidad de que el PM los rescatara). Contrato cumplido.
- **Cambios en working tree NO commiteados (fuera del scope de este audit, se dejan intactos y se reportan):**
  - `M apps/api/api/v1/rrhh/serializers.py` y `M apps/api/api/v1/rrhh/views.py` — N+1 fix de **empleados** ("audit: 66 queries para 15 empleados"). NO es trabajo de contracts ni de ningún agente de este ciclo; es WIP de otra terminal/sesión (empleados v5). El PM no lo toca ni lo commitea.
  - `?? apps/api/apps/contracts/tests/test_contracts_hr_audit_v1.py` — creado por hr-tester (10 tests, 3 xfail estrictos que codifican los bugs #1/#2). Se deja sin commitear por la regla "solo reportes"; **recomendado commitearlo junto al Bloque-H-contracts** para que los xfail→XPASS validen el fix.
  - `?? apps/api/tests/test_audit_temp_hr_v5.py` — pre-existente desde antes de esta sesión.
- **Gap de tooling:** `mypy` NO está instalado en el venv (`No module named mypy`); el playbook lo asume. Recomendado instalarlo o documentar que no se corre.

## Sugerencia para afinar el equipo de agentes (opcional)

**Agente:** `vyntia-code-quality`. **Observación:** asume `mypy` disponible y reporta su ausencia como hallazgo cada corrida (ruido). **Cambio propuesto:** añadir a su `.md`, en la sección de comandos, una nota: "Si `mypy` no está instalado en el venv, omítelo silenciosamente y nótalo una sola vez en 'Gap de tooling' — no lo trates como hallazgo de código." **¿Aplicar?** — pendiente de "ok" del humano.
