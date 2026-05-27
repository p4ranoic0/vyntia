# Code Quality - contracts v2 (NARROW SEAL re-audit, Bloque-H-contracts)

**Fecha:** 2026-05-23
**Invocado por:** /vyntia-quality contracts v2 (narrow seal, read-only)
**Scope:** verificar los 4 fixes de Bloque-H-contracts (commits 76460893 + 83af3886) + su blast radius. NO es un barrido completo.
**Linters:** ruff (touched files). mypy: no instalado, skip. tsc/eslint: N/A (sin cambios FE).
**Tests:** pytest apps/contracts/tests (118), test_contracts_hr_audit_v1.py (10 guards), manage.py check.
**Confianza:** alta

---

## VEREDICTO: NOT-SEALED (AMARILLO)

Los 4 fixes estan correctos y completos dentro de su scope. Pero el blast-radius del Fix #2 (status MAYUSCULA) destapo un quinto sitio con el MISMO bug-class sobre el MISMO modelo Contract, fuera del scope del audit v1 y del fix de Bloque-H. No regresiona baselines y NO fue introducido por estos commits, pero es un bug FUNCIONAL ACTIVO sobre Contract.status. Por contrato de seal (si encuentras un NEW issue, no green-ees), marco AMARILLO hasta decision humana. Si el humano considera word_template_service.py:216 fuera del alcance de contracts (es app documents), contracts puede promoverse a VERDE tal cual: los 4 fixes estan limpios.

---

## Resumen ejecutivo
- 4 fixes verificados: 4 cerrados / 0 incompletos (dentro de scope).
- 1 hallazgo NUEVO (fuera de scope, no introducido): word_template_service.py:216 filtra Contract con status activo minuscula.
- Tests del scope: contracts 118/118 (incl. 10 regression guards 29-feb/vac-truncas/CTS). manage.py check 0 issues.
- Baselines: NO se regresiono nada. ruff sobre archivos tocados = solo deuda pre-existente (F401, F601), ninguna en lineas tocadas por los fixes.
- Horizonte: 1 corto plazo (hallazgo nuevo) / 0 largo plazo.

---

## Confirmacion punto-por-punto de los 4 fixes

### Fix #1 (CERRADO) - severance_service.py (apps/contracts/services/severance_service.py)
- _minus_one_year() (L56-65): try d.replace(year=d.year-1) / except ValueError d.replace(year=d.year-1, day=28). Correcto: el unico date que lanza ValueError en replace(year) es 29-feb hacia anio no bisiesto; fallback mantiene month=2, day=28 -> 28-feb. Sin otros bordes (30/31 no aplican a cambio de solo-anio).
- _months_between() (L40-53): reescrito. Eliminado el +1 inclusivo; ahora if end.day menor que start.day entonces months -= 1. Cuenta meses COMPLETOS reales. Correcto.
- Callers verificados, ninguno roto: _compute_cts (L96), _compute_vac_truncas (L122), _compute_grat_trunca (L144) usan la nueva semantica. _compute_indemnizacion (L169) NO lo usa (usa days/365), intencional y documentado.
- _compute_vac_truncas (L113-137): bloque viejo inicio_anio=date(...)+max(...) condicional reemplazado por inicio_anio=max(fecha_inicio,_minus_one_year(fecha_cese)). Sin dead code.
- Decimal handling intacto. ruff sobre el archivo: 0 errores. Regression guards: 10 passed.

### Fix #2 (CERRADO dentro de archivo) - contratos_views.py (apps/api/api/v1/rrhh/contratos_views.py)
- 8 ocurrencias lowercase -> UPPERCASE aplicadas (alertas_vencimiento, reporte_contratos x4, estadisticas x3). Grep status lowercase sobre el archivo: 0 restantes (exit 1). 10 refs UPPERCASE.
- Valores coinciden EXACTO con Contract.ESTADO_CHOICES (contract.py:43-50): ACTIVO/VENCIDO/TERMINADO.
- Nota: L111 filter(status=estado) pasa query-param crudo (caller-controlled); aceptable.

### Fix #3 (CERRADO) - employment_data.py (apps/contracts/models/employment_data.py)
- __str__ (L168-170): siglas_area con guard self.area_id (FK id, sin AttributeError si None). Correcto.
- generar_codigo_empleado (L342-344): siglas_area[:3].upper() con guard (self.area_id and self.area.siglas_area) else GEN. Correcto.
- siglas_area es campo real de Department (department.py:56). nombre_area/codigo_area NO existen. Confirmado.

### Fix #4 (CERRADO) - time_off (vacation.py, vacation_admin_service.py)
- VacationConfiguration.__str__ (vacation.py:163): nombre_unidad_organica dentro de guard.
- vacation_admin_service.py:222 y :288: nombre_unidad_organica con guard datos_laborales and datos_laborales.area else Sin area.
- nombre_unidad_organica es campo real de Department (department.py:55). Diff 83af3886 solo cambio las lineas area_nombre. 3 spots fixed.

### FRESH global grep nombre_area / codigo_area en apps/api
- Solo 2 ocurrencias en api/v1/vacaciones/serializers.py:18-19,40-41, hasattr-guardadas (caen al fallback). Aceptables per scope. No bugs.
- 0 ocurrencias unguarded restantes.

---

## Hallazgos CORTO PLAZO

### [ALTO] word_template_service.py filtra Contract con status lowercase - mismo bug-class que Fix #2, fuera de scope del seal
- Donde: apps/api/apps/documents/services/word_template_service.py:215-216
- Que: Contract.objects.filter(empleado=empleado, status=activo) con activo minuscula. Contract usa choices UPPERCASE (ACTIVO). El filtro matchea 0 filas siempre.
- Por que importa: bug FUNCIONAL ACTIVO (no latente). Al generar certificados Word con salario (incluir_salario=True), el ultimo contrato activo nunca se encuentra -> salario queda vacio silenciosamente. Mismo sintoma silencioso que el dashboard RRHH del Fix #2.
- Por que NO esta en este seal: el audit v1 (contracts-v1.md L36) acoto el bug a contratos_views; NO menciono word_template_service. El fix Bloque-H respeto ese scope. Es app documents. Lo destape en el blast-radius check.
- Como arreglar: status=activo -> status=ACTIVO en L216. Es el unico Contract-filter lowercase en documents/.
- Esfuerzo: ~10 min. Promovible a /gsd-fast.

### Otros lowercase status (NO bugs - modelos distintos, verificados)
- remuneraciones_serializers.py:124, remuneraciones_views.py:152,181 -> TaxParameter (UIT), choices lowercase activo/inactivo. Correcto.
- compliance_service.py:168,172 -> policies, status lowercase vencido. Correcto.
- Ninguno toca el modelo Contract.

---

## Baselines
| Metrica | Baseline (post-fix) | Ahora | Estado |
|---|---|---|---|
| pytest contracts | 118 | 118 | OK |
| hr audit guards | 10 | 10 passed | OK |
| manage.py check | 0 issues | 0 issues | OK |
| ruff severance_service.py | clean | 0 errores | OK |
| Full backend (no re-corrido) | 1031/1f/17s | sub-suites OK | OK (sin regresion observada) |

Nota: deuda ruff F401 (unused imports: contratos_views.py x8, vacation.py x2, employment_data.py x2) y F601 (dict-key id duplicado en vacation_admin_service.py:127/129 y 287/289) es PRE-EXISTENTE (confirmado via diff: ninguna en lineas tocadas). No introducida por Bloque-H. Out of scope.

## Gap de tooling
- mypy: no instalado -> skip silencioso per playbook. No bloquea el seal.
- Cobertura time_off: NO existe test que ejercite VacationAdminService ni VacationConfiguration.__str__ directamente. Fix #4 verificado por inspeccion + manage.py check (import integrity). Gap pre-existente, no introducido. Largo plazo: agregar tests de time_off services.

## Acciones recomendadas
- [ ] CORTO #1: Arreglar word_template_service.py:216 status activo -> ACTIVO (10 min, /gsd-fast). Despues, contracts queda VERDE sin reservas.
- [ ] (Deuda) Limpiar F401 unused imports + F601 dict-key dup.
- [ ] (Largo plazo) Cobertura de tests para time_off services.

## Pregunta para humano
Contracts per-se esta VERDE (4 fixes limpios, completos, sin regresion). Veredicto global AMARILLO solo por el hallazgo en app documents (word_template_service.py:216), mismo bug-class que Fix #2 sobre el mismo modelo Contract. Consideras word_template_service dentro del alcance de contracts sealed-for-D? Si SI -> arregla esa 1 linea y re-seal a VERDE. Si NO (scope aparte de documents) -> contracts es VERDE ya y el hallazgo va a ticket separado.
