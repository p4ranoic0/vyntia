# Code Quality - CONTRACTS (v1)

**Fecha:** 2026-05-23
**Invocado por:** /vyntia-quality contracts (audit-only, read-only)
**Scope:** apps/api/apps/contracts/, apps/api/api/v1/contracts/, legacy apps/api/api/v1/rrhh/contratos_views.py, apps/web/src/features/contracts/
**Linters:** ruff (OK), mypy (NO INSTALADO - gap), tsc (OK), eslint (OK)
**Tests:** pytest apps/contracts/tests/ (108 passed), vitest src/features/contracts/ (27 passed)
**Confianza:** alta (verificado a runtime)
**Tiempo:** ~35min

## Resumen ejecutivo
- Verdict: AMARILLO - sin blockers de seguridad, pero 2 bugs latentes que D-Pay activara y 1 bug funcional ya activo en reportes/estadisticas.
- 9 hallazgos: 0 criticos / 3 altos / 4 medios / 2 bajos
- Horizonte: 6 corto plazo / 3 largo plazo
- Tests scope: backend 108/108, frontend 27/27 - sin regresion.
- Baselines: NO se regresiono nada. tsc modulo = 0; eslint modulo = 0.

## Hallazgos CORTO PLAZO

### [ALTO] EmploymentData.__str__ y generar_codigo_empleado usan campos de Area inexistentes
- Donde: apps/api/apps/contracts/models/employment_data.py:169 y :341
- Que: __str__ retorna ({self.area.nombre_area}) y generar_codigo_empleado hace self.area.codigo_area[:3]. Verificado a runtime: Department NO tiene nombre_area ni codigo_area (solo siglas_area, nombre_unidad_organica, nombre_organo, property nombre_completo). Ambos lanzan AttributeError.
- Por que importa: __str__ se invoca en admin, logging, reprs de error y cualquier str(obj). Es el MISMO bug que empleados-v3 cerro en location_history.py (comentario #53 was using non-existent nombre_area en organization/models/location_history.py:162). EmploymentData quedo fuera de ese barrido. D-Pay consume EmploymentData masivamente.
- Como arreglar: linea 169 usar area.nombre_unidad_organica; linea 341 usar area.siglas_area[:3].upper() con fallback GEN.
- Esfuerzo: ~20 min.

### [ALTO] _compute_vac_truncas crashea con fecha de cese = 29 de febrero
- Donde: apps/api/apps/contracts/services/severance_service.py:103
- Que: date(fecha_cese.year-1, fecha_cese.month, fecha_cese.day): si el cese cae 29-feb (bisiesto), el anio anterior no es bisiesto y date() lanza ValueError. Verificado a runtime con cese=2024-02-29.
- Por que importa: POST /api/v1/severance-settlements/{id}/compute/ devuelve HTTP 400 criptico para CUALQUIER trabajador cesado un 29-feb. D-Pay basa la liquidacion en este service.
- Como arreglar: resta robusta de un anio (relativedelta(years=1) con clamp). Eliminar linea 100 (dead code, se reasigna en linea 101).
- Esfuerzo: ~30 min.

### [ALTO] Reportes/estadisticas filtran status en minusculas - devuelven SIEMPRE 0
- Donde: apps/api/api/v1/rrhh/contratos_views.py:149, 229-231, 236, 245, 256, 300, 304-305, 319
- Que: Contract.ESTADO_CHOICES almacena MAYUSCULA (ACTIVO/VENCIDO/TERMINADO). Pero alertas_vencimiento, reporte_contratos y estadisticas filtran con status=activo/vencido/terminado (minuscula). renovar_contrato (linea 372) si usa mayuscula, confirmando la inconsistencia.
- Por que importa: contratos_activos, contratos_vencidos, contratos_terminados, valor_total_activos, contratos_por_vencer y alertas reportan 0 silenciosamente. Bug funcional ACTIVO hoy en dashboard RRHH, no solo latente.
- Como arreglar: reemplazar literales por mayuscula + test de regresion por endpoint.
- Esfuerzo: ~45 min.

### [MEDIO] _compute_vac_truncas sobrecuenta por el +1 inclusivo de _months_between
- Donde: severance_service.py:95-122 + _months_between:40-47
- Que: _months_between suma +1 cuando end.day >= start.day (para CTS/grati). Reusado en vac truncas infla dias: inicio 2025-06-01 / cese 2026-03-31 da meses=10 (-> 25 dias). El bloque inicio_anio (100-106) es ilegible.
- Por que importa: sobreestima vacaciones truncas -> liquidacion inflada. D-Pay heredara el sesgo.
- Como arreglar: separar meses devengados de vacaciones de _months_between; testear contra casos legales.
- Esfuerzo: ~2h.

### [MEDIO] except Exception ancho convierte errores de programacion en HTTP 400
- Donde: termination_views.py, probation_views.py, views.py:72,96,110, rrhh/contratos_views.py:286,350
- Que: handlers capturan except Exception -> APIResponse.error(400). Un AttributeError/ValueError interno (p.ej. crash Feb-29) se enmascara como bad request del cliente.
- Por que importa: oculta bugs 500 reales y miente sobre la causa.
- Como arreglar: capturar solo ValidationError/DoesNotExist -> 400; dejar el resto propagar -> 500.
- Esfuerzo: ~1h.

### [BAJO] Limpieza ruff: imports/variables sin usar
- Donde: probation_service.py:18, test_b10_api_smoke.py:9, test_b14_severance_service.py:7,54 (E741), test_b11_probation_service.py:72. 12 hallazgos, 10 autofix.
- Por que importa: ruido cosmetico, ningun bug.
- Esfuerzo: ~5 min (ruff check --fix).

## Hallazgos LARGO PLAZO

### [MEDIO] Decimal vs float: fugas a float en serializacion de calculos legales
- Donde: rrhh/contratos_views.py:268-269 (float salario_promedio, float valor_total_activos), termination.py:230-234 (hours_since_completion float).
- Que: montos de severance/settlement en Decimal correctamente (ADR-B.9), pero reportes agregados castean a float para JSON.
- Por que importa: D-Pay debe ser Decimal end-to-end. Estos float() son display-OK pero no deben alimentar planilla aguas abajo.
- Propuesta: ADR que agregados de reporte son display-only; D-Pay recalcula desde Decimal.
- Esfuerzo: discusion + ~medio dia al iniciar D.

### [MEDIO] submit_declaration T-Registro es stub in-process - sin idempotencia para SUNAT real
- Donde: apps/contracts/services/tregistro_service.py:225-236
- Que: submit_declaration no hace HTTP; transiciona estado. Seam bien aislado (elogiable), pero constraint unique_active_t_registro_per_contract solo cubre submitted/accepted; sin manejo async/reintentos.
- Por que importa: al integrar SUNAT real faltan idempotency keys y manejo de respuestas async. Deuda de diseno, no bug actual.
- Propuesta: idempotency key + tabla de intentos + webhook/poll.
- Esfuerzo: sub-proyecto propio.

### [BAJO] _months_between reutilizado para 3 semanticas distintas (CTS, grati, vac)
- Donde: severance_service.py:40-47 consumido por _compute_cts, _compute_grat_trunca, _compute_vac_truncas.
- Que: una funcion con regla +1-inclusivo sirve a tres componentes con devengos distintos.
- Propuesta: en el motor real de D, separar calculadoras por componente con tabla de casos legales.
- Esfuerzo: absorbido por D.

## Verificacion de patterns CLAUDE.md
- Count(id) en contratos_views.py:235,244,313,330: OK - Contract/ContractAmendment PK se llama literalmente id (UUIDField). Count(contrato_id) aplica a legacy con PK custom; aqui no. No es bug.
- Area via DatosLaborales: OK - Contract y ContractAmendment SI tienen FK area directo a Department (correcto por diseno). EmploymentData tambien. Antipatron empleado.area directo NO aparece.
- FK cross-app lazy (string): OK - todas las FK usan string lazy. Sin import cycles.
- APIResponse.error() status_code: OK en views nuevas (400/404 explicitos). Legacy:287,351 omite -> default 400, deseado ahi. Aceptable.
- Permisos: views nuevas con RRHHPermission; legacy con require_hr/require_admin/require_authenticated. Sin views desprotegidas.
- N+1: viewsets nuevos usan select_related/prefetch_related (severance con prefetch_related lines). Legacy tambien. Sin N+1. Nota menor: len(queryset) en mensajes (termination_views:154, probation_views:103) fuerza evaluacion temprana - inocuo.

## Seguridad
- Sin credenciales hardcoded, sin SQL raw, sin XSS reflejado en el scope.
- Mutaciones de estado via services con transaction.atomic y validacion de transiciones.

## Baselines
| Metrica | Antes | Ahora (scope) | Estado |
|---------|-------|---------------|--------|
| pytest apps/contracts/tests/ | parte de 982 | 108 passed | OK sin regresion |
| vitest src/features/contracts/ | parte de 178 | 27 passed | OK sin regresion |
| tsc errors (modulo) | 1 pre-exist BlankEnum fuera scope | 0 en contracts | OK |
| eslint warnings (modulo) | <=278 global | 0 en contracts | OK |
| ruff (modulo) | - | 12 (10 autofix, cosmeticos) | ruido, no regresion |
| mypy | asumido | NO INSTALADO en venv | gap de tooling |

## Acciones recomendadas (priorizado)
- [ ] CORTO #1 - [ALTO] EmploymentData.__str__:169 + generar_codigo_empleado:341. ~20min.
- [ ] CORTO #2 - [ALTO] Crash Feb-29 en _compute_vac_truncas:103 + borrar dead code linea 100. ~30min.
- [ ] CORTO #3 - [ALTO] Filtros status minuscula->MAYUSCULA en contratos_views.py. ~45min.
- [ ] CORTO #4 - [MEDIO] Estrechar except Exception -> ValidationError. ~1h.
- [ ] CORTO #5 - [MEDIO] Fijar convencion de devengo de vacaciones truncas. ~2h.
- [ ] CORTO #6 - [BAJO] ruff check --fix sobre apps/contracts/. ~5min.
- [ ] LARGO - Decimal end-to-end para D-Pay (frontera display-only).
- [ ] LARGO - Integracion SUNAT real con idempotencia para T-Registro.
- [ ] TOOLING - Instalar mypy en el venv o documentar que no se corre.

## Pregunta para humano
1. Confirmas la convencion legal de vacaciones truncas (dias por mes del ultimo periodo vacacional) para fijar el calculo antes de que D-Pay lo consuma? Hoy sobrecuenta por el +1 inclusivo.
2. El bug de status minuscula en reportes (CORTO #3) es promovible a /gsd-fast ya, dado que es un bug FUNCIONAL ACTIVO (no solo latente) que muestra 0 contratos activos en el dashboard RRHH?
