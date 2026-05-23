# PM — Contracts v2 seal audit (2026-05-23)

**Orquestador:** main agent en rol PM (playbook `.claude/agents/vyntia-pm.md`).
**Scope:** re-audit ESTRECHO post-Bloque-H-contracts — confirmar que los 4 fixes de v1 cierran sin introducir deuda, para sellar contracts-for-D (Vyntia Pay). NO es un sweep completo.
**Especialistas lanzados (2, en paralelo):** `vyntia-hr-tester` + `vyntia-code-quality`.
**Reportes fuente:**
- `docs/agent-reports/hr-tester/2026-05-23-contracts-v2.md`
- `docs/agent-reports/code-quality/2026-05-23-contracts-v2.md`
**Commits del ciclo:** `76460893` (contracts v1 fixes), `83af3886` (time_off sweep), + el commit de cierre v2 (este).

---

## TL;DR — Verdict ejecutivo

🟢 **SEALED-FOR-D** (tras cerrar 2 hallazgos que la propia v2 destapó).

La v2 hizo exactamente lo que debía: confirmó que los 3 bugs de v1 están bien arreglados **y** atrapó 2 problemas nuevos antes del sello — uno de ellos un defecto en el propio fix de v1. Ambos se corrigieron y re-verificaron en el mismo ciclo. Contracts queda verde con baseline intacta.

**Recorrido del veredicto:** ambos especialistas devolvieron 🟡 (no-sellar) por sendos hallazgos ALTO; tras corregirlos y re-correr, el sello pasa a 🟢.

---

## Hallazgos v2 y su resolución

### 🔴→✅ Confirmado arreglado de v1 (regression guards verdes)
| Bug v1 | Verificación v2 | Estado |
|--------|-----------------|--------|
| Cese 29-feb crash | `_minus_one_year` → 28-feb; liquidación computa; +tricky dates (28-feb, 01-mar, 30-abr, 31-dic) sin crash | ✅ |
| Vac truncas +1 inclusivo | 1 mes = 2.5d = 250 (antes 500); 3 meses = 7.5d; 1 año = 30d | ✅ |
| CTS fracción de mes | 15 días = 0 meses = 0.00 (antes mes completo) | ✅ |
| Status filter minúscula | 8 ocurrencias UPPERCASE, grep lowercase = 0, valores = `Contract.ESTADO_CHOICES` | ✅ |
| EmploymentData area refs | guards `self.area_id`, `siglas_area` real | ✅ |
| time_off nombre_area | 3 spots → `nombre_unidad_organica` | ✅ |

Golden paths intactos: renuncia=0 indemnización, despido_arbitrario=12000, cap 12 sueldos=24000, idempotencia.

### 🔴 NUEVO #1 [ALTO, en contracts] — el fix de v1 sobre-corrigió → subconteo a fin de mes (FIXED en v2)
**Fuente:** hr-tester. **Evidencia:** `severance_service._months_between`. Al quitar el `+1` inclusivo, el conteo por aniversario día-de-mes pasó a **subcontar 1 mes cuando el cese cae el último día del mes** (Jul1→Dic31 daba 5 meses → grati 2500 en vez de 3000). Como ~99% de ceses peruanos son a fin de mes, **subpagaba casi toda liquidación real** — y un subpago en un cálculo "mínimo legal" es la dirección legalmente peligrosa.
**Fix aplicado:** `_months_between` ahora completa el mes cuando `_is_month_end(end)` (trata el cese a fin de mes como día 1 del mes siguiente). Doctrina "mes calendario completo" (Ley 27735 / D.S. 005-2002-TR grati, D.S. 001-97-TR CTS, D.S. 012-92-TR vacaciones). El xfail de hr-tester (`test_grat_trunca_fin_de_semestre_paga_completo`) viró a XPASS → convertido a regression guard.

### 🔴 NUEVO #2 [ALTO, en documents — mismo bug-class que Fix #2] (FIXED en v2)
**Fuente:** code-quality. **Evidencia:** `apps/api/apps/documents/services/word_template_service.py:216` — `Contract.objects.filter(empleado=…, status='activo')` en minúscula contra choices UPPERCASE → matchea 0 filas → certificados Word salían **sin sueldo silenciosamente**. El audit v1 acotó el bug a `contratos_views`; este sitio quedó fuera.
**Fix aplicado:** `'activo'` → `'ACTIVO'`. Suite documents 112 passed.

### ✅ Sweep de bug-class confirmado limpio
Grep global `Contract…status='<lowercase>'`: 0 restantes tras los 2 fixes. Grep `.nombre_area`/`.codigo_area`: solo 2 hits hasattr-guardados en `vacaciones/serializers.py` (caen al fallback correcto — no son bugs). Otros `status="activo"` que quedan son de OTROS modelos (UIT/remuneraciones, onboarding, policies) con sus propios choices en minúscula — correctos.

---

## Verificación final (evidencia)

- Contracts suite: **145 passed, 0 xfailed** (v1: 118 → +26 tests v2 seal +1 ex-xfail).
- Documents suite: **112 passed**.
- Full backend: **1058 passed, 1 failed (`test_permisos_debug` pre-existente), 17 skipped** — sin regresión.
- `manage.py check`: **0 issues**.
- ruff `severance_service.py`: **0 errores**. (Las 3 ruff F401 en `word_template_service.py:9-12` son imports sin usar **pre-existentes**, no en líneas tocadas — deuda separada.)

---

## Trends cruzando v1 + v2

1. **El bug-class "mayúscula/minúscula en `Contract.status`" tenía más de un sitio.** v1 lo acotó a un archivo; v2 destapó otro (documents). Lección: cuando un bug nace de una convención no centralizada (status como string libre), hay que hacer grep global del bug-class, no solo del archivo reportado. → acción largo plazo: centralizar en `Contract.Status` TextChoices y usar `Status.ACTIVO` en vez de literales.
2. **El bug-class "campo inexistente en Department" también era multi-sitio** (contracts + time_off). Mismo aprendizaje.
3. **Un fix puede introducir el bug opuesto.** El `+1` inclusivo (sobrepago) se corrigió a un subconteo (subpago). El audit de re-verificación (v2) es lo que lo atrapó — valida el patrón audit→fix→**audit** que empleados usó (v1→v5).

---

## 3 acciones priorizadas

1. **CORTO — ✅ HECHO en este ciclo:** month-end completion en `_months_between` + status fix en `word_template_service`. Contracts sellado.
2. **MEDIO — Gaps legales 728 (siguen abiertos, fuera de Bloque-H):** validación tope 5 años + desnaturalización modal→indefinido. D los necesita para clasificar beneficios. Los tests v1 ya documentan los gaps (pasan asertando la ausencia).
3. **LARGO — Deuda de bug-class:** (a) migrar `Contract.status` a TextChoices tipadas para matar la clase mayúscula/minúscula de raíz; (b) limpiar imports F401 en `word_template_service.py`; (c) capa de modularidad comercial plan→módulos (sub-proyecto propio, ver v1).

---

## ¿Más ciclos o sellado?

**SELLADO 🟢. No se requiere v3 sobre la ruta de severance.** v2 cumplió su rol de red de seguridad (atrapó el subconteo que v1 introdujo). Los items abiertos (gaps 728, modularidad) son scope de otros sub-proyectos/brainstorms, no de contracts-for-D. La ruta crítica que D consume (Contract + EmploymentData + severance_service) está verde y con guards de regresión.

## Nota de proceso
- Ambos especialistas persistieron su reporte al primer intento. ✅
- code-quality respetó el tune de mypy (skip silencioso, notado bajo "Gap de tooling"). ✅
- Archivo huérfano `apps/api/tests/test_audit_temp_hr_v5.py` sin trackear (pre-existente de empleados, fuera de scope) — ambos agentes lo notaron; se deja intacto.
