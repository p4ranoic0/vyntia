# HR Tester — Contracts (audit v1)

**Fecha:** 2026-05-23
**Invocado por:** audit-only sobre módulo CONTRACTS (pre-D / Vyntia Pay)
**Specs consultadas:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`; modelos+servicios en `apps/api/apps/contracts/`
**Tests corridos:** 118 (108 baseline + 10 nuevos) | **Pasaron:** 115 | **xfailed (bugs):** 3 | **Nuevos creados:** 10 (1 archivo)
**Confianza:** alta (bugs confirmados por ejecución directa de los cómputos, no por lectura)
**Tiempo invertido:** ~35 min

## Resumen ejecutivo
- VERDICT GLOBAL: 🔴 — `severance_service` tiene 1 bug CRÍTICO (crash) y 2 bugs ALTOS de sobrepago que D (Vyntia Pay) heredaría directamente en cálculo de planilla.
- CONFIRMADAS las 2 sospechas del code-quality pair: (a) cese 29-feb lanza `ValueError`; (b) `_months_between` sobrecuenta por `+1` inclusivo. Refutada solo la ubicación exacta del 29-feb: el crash está en `_compute_vac_truncas` (línea 100-106), no en la 103 aislada.
- El sobrepago de `_months_between` afecta vacaciones truncas SIEMPRE (+2.5 días por cálculo) y CTS/grati en fracciones de mes; en CTS/grati el `min(meses, 6)` enmascara el exceso en plazos largos pero NO en fracciones cortas.
- Flujos legales 1 (tope 5 años) y 2 (desnaturalización modal→indefinido) NO EXISTEN en código — gap funcional que D necesitará para clasificar beneficios.
- Período de prueba por régimen (flujo 3) y T-Registro (flujo 5) están OK en lo verificado.

## Estado por flujo
| Flujo | Estado |
|-------|--------|
| 1. Renovación / tope 5 años (728) | 🔴 GAP — sin validación ni alerta |
| 2. Conversión modal→indefinido (desnaturalización) | 🔴 GAP — lógica inexistente |
| 3. Período de prueba por régimen (90/180/365) | 🟢 OK |
| 4. Severance / liquidación | 🔴 1 CRÍTICO + 2 ALTO |
| 5. T-Registro alta/baja | 🟢 OK (cobertura previa B.10 verde) |

## Casos diseñados
| # | Caso | Tipo | Estado | Test |
|---|------|------|--------|------|
| 1 | Prueba régimen común 90d | Golden | ✅ PASS | `TestProbationPorRegimen::test_comun_90_dias` |
| 2 | Prueba calificado 180d | Golden | ✅ PASS | `::test_calificado_180_dias` |
| 3 | Prueba dirección 365d | Golden | ✅ PASS | `::test_direccion_365_dias` |
| 4 | Fijo > 5 años aceptado sin validar | Edge RRHH-PE (gap) | ✅ PASS (documenta gap) | `TestTope5AniosFijo::test_contrato_fijo_excede_5_anios_sin_validacion` |
| 5 | Sin lógica desnaturalización | Edge RRHH-PE (gap) | ✅ PASS (documenta gap) | `TestDesnaturalizacion::test_no_existe_logica_desnaturalizacion` |
| 6 | Cese 29-feb crashea | Edge RRHH-PE (bug) | ❌ XFAIL | `TestSeveranceEdgeCases::test_cese_29_feb_no_crashea` |
| 7 | Vac truncas 1 mes = 2.5 días | Edge RRHH-PE (bug) | ❌ XFAIL | `::test_vac_truncas_1_mes_exacto_paga_2_5_dias` |
| 8 | CTS fracción de mes no es mes completo | Edge RRHH-PE (bug) | ❌ XFAIL | `::test_cts_fraccion_de_mes_no_cuenta_mes_completo` |
| 9 | Renuncia sin indemnización | Golden regresión | ✅ PASS | `::test_renuncia_no_genera_indemnizacion` |
| 10 | Cese fin de mes (31) computa | Golden regresión | ✅ PASS | `TestSeveranceFinDeMes::test_cese_fin_de_mes_31_computa` |

## Hallazgos

### [CRÍTICO] Cese 29-feb crashea el cálculo de liquidación
- **Caso afectado:** #6
- **Esperado:** un cese con `fecha_cese = 29-feb` (año bisiesto) debe computar la liquidación.
- **Observado:** `ValueError: day is out of range for month`.
- **Causa:** en `_compute_vac_truncas` (`apps/api/apps/contracts/services/severance_service.py`, líneas 100-106) se construye `date(fecha_cese.year - 1, fecha_cese.month, fecha_cese.day)`. Para `fecha_cese = 2024-02-29`, `year-1 = 2023` no es bisiesto → no existe 2023-02-29.
- **Repro:**
  ```
  cd apps/api; pytest apps/contracts/tests/test_contracts_hr_audit_v1.py -k cese_29_feb
  ```
  (xfail confirma; quitar el `@pytest.mark.xfail` reproduce el crash crudo). Verificado además vía cómputo directo: `_compute_vac_truncas(Decimal('3000'), date(2020,1,1), date(2024,2,29))` → `ValueError`.
- **Impacto en D:** todo cese efectivo el 29-feb (renuncia, despido, vencimiento) tumba el endpoint de liquidación. ~1 día cada 4 años, pero bloqueo total ese día.

### [ALTO] Vacaciones truncas sobrepagan 1 mes (2.5 días) en todo cálculo
- **Caso afectado:** #7
- **Esperado:** 1 mes completo de servicio → 2.5 días truncas → con sueldo 3000 (jornal 100) = **250.00**.
- **Observado:** **500.00** (5 días). El `_months_between(date(2024,1,1), date(2024,2,1))` devuelve **2** en vez de 1.
- **Causa:** `_months_between` (líneas 40-47) suma `+1` cuando `end.day >= start.day`. Es un conteo "inclusivo" incorrecto para devengo proporcional. Ej. medidos: 1 mes exacto → 2; mismo mes calendario → 1; 6 meses exactos → 7; 12 meses → capeado.
- **Repro:** `pytest ... -k vac_truncas_1_mes`. Directo: ver tabla de mediciones en el cuerpo del test.
- **Impacto en D:** sobrepago sistemático de vacaciones truncas (+2.5 días por liquidación). En planilla masiva es plata real de más en cada cese.

### [ALTO] CTS cuenta fracción de mes como mes completo
- **Caso afectado:** #8
- **Esperado:** 15 días de servicio (1-15 jun) → ~0.5 mes de CTS, no mes completo. CTS legal = `(sueldo/12)×meses + (sueldo/360)×días`.
- **Observado:** `_compute_cts(3000, 2024-06-01, 2024-06-15)` → **500.00** (= sueldo/6, mes completo).
- **Causa:** mismo `+1` inclusivo de `_months_between`; la fórmula del servicio `(sueldo × meses)/6` además ignora la componente de días/360.
- **Nota:** en plazos largos `min(meses, 6)` enmascara el +1 (queda capeado a 6), pero NO en periodos cortos / fracciones, donde es donde más se nota.
- **Impacto en D:** sobrepago de CTS proporcional en altas/ceses recientes. La fórmula simplificada está marcada como "minimum legal (ADR-B.9)", pero el redondeo de mes hacia arriba sí es defecto, no decisión documentada.

### [MEDIO/GAP] Sin validación del tope de 5 años en contratos modales (728)
- **Caso afectado:** #4
- **Esperado:** D.Leg. 728 art. 74 — máximo 5 años acumulados a plazo fijo; superado, se desnaturaliza a indeterminado.
- **Observado:** `Contract.clean()` solo valida `fecha_fin > fecha_inicio` y coherencia indefinido/fijo. Un `LEY_728_FIJO` de 6 años se persiste sin error ni flag.
- **Repro:** `pytest ... -k excede_5_anios`.
- **Impacto en D:** empleados etiquetados "fijo" que legalmente ya son indeterminados → beneficios (CTS plena, indemnización) mal asignados.

### [MEDIO/GAP] Sin lógica de desnaturalización modal→indefinido
- **Caso afectado:** #5
- **Esperado:** D.S. 001-96-TR art. 77 — conversión a indeterminado por exceso de plazo / renovaciones fraudulentas / continuación vencido el plazo.
- **Observado:** no existe método (`desnaturalizar`, `esta_desnaturalizado`) en modelo ni servicios.
- **Impacto en D:** misma raíz que el gap anterior; D requerirá clasificar correctamente para calcular beneficios.

## Tests nuevos creados
- `apps/api/apps/contracts/tests/test_contracts_hr_audit_v1.py` — 10 tests:
  - 5 golden/regresión que PASAN (período de prueba por régimen, renuncia sin indemnización, cese fin de mes).
  - 2 tests que documentan gaps legales (tope 5 años, desnaturalización) — PASAN afirmando la ausencia.
  - 3 `xfail(strict=True)` que fijan los bugs CRÍTICO/ALTO; viran a XPASS (fallo) cuando se arreglen, forzando actualización del test.
- Suite de contracts: **115 passed + 3 xfailed** (baseline previo 108 passed — sin regresión).

## Acciones recomendadas
- [ ] CORTO — Reescribir `_months_between` en `apps/api/apps/contracts/services/severance_service.py` para conteo de meses completos sin `+1` inclusivo (devolver `meses` y `días_residuales` por separado). Resuelve hallazgos ALTO #7 y #8.
- [ ] CORTO — Endurecer la ventana de `_compute_vac_truncas` (líneas 100-106) contra fechas 29-feb: usar desplazamiento seguro de año (p.ej. `dateutil.relativedelta` o clamp al último día del mes). Resuelve CRÍTICO #6.
- [ ] CORTO — Incluir la componente días/360 en `_compute_cts` para fracciones de mes (alinear con D.S. 001-97-TR), si D no la va a recalcular aguas abajo.
- [ ] LARGO — Añadir validación/alerta de tope 5 años + servicio de desnaturalización modal→indefinido antes de que D consuma la clasificación de contrato.
- [ ] LARGO — Suite de propiedad (property-based) sobre `_months_between` y los 4 componentes de severance para barrer fechas límite (fin de mes, bisiestos, jornadas de 1 día).

## Pregunta para humano
La fórmula CTS `(sueldo × meses)/6` de `_compute_cts` está rotulada como "minimum legal (ADR-B.9)" e ignora a propósito días/360 y grati histórica. ¿El sobrepago por fracción de mes (#8) se considera defecto a corregir aquí, o se delega íntegro a D (Vyntia Pay) y este servicio se marca como "no usar para liquidación final"? Esto define si #8 es bug o limitación documentada.
