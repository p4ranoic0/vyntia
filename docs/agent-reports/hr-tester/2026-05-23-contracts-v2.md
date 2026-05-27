# HR Tester — Contracts (SEAL re-audit v2)

**Fecha:** 2026-05-23
**Invocado por:** NARROW v2 SEAL AUDIT — verificar fixes Bloque-H-contracts (commits 76460893 + 83af3886)
**Spec consultada:** `apps/api/apps/contracts/services/severance_service.py`; reporte v1 `docs/agent-reports/hr-tester/2026-05-23-contracts-v1.md`
**Tests corridos:** 144 (118 baseline + 26 nuevos) | **Pasaron:** 144 | **xfailed:** 1 (hallazgo nuevo) | **Fallaron:** 0 | **Nuevos creados:** 26 (1 archivo)
**Confianza:** alta (verificado por cómputo directo de funciones puras + suite)
**Tiempo invertido:** ~25 min

---

## VERDICT: 🟡 NO sellar (sellable con caveat documentado)

Los **3 bugs de v1 están correctamente arreglados** y no hay regresión. PERO el fix introdujo un **subconteo de 1 mes en el caso de cese a fin de mes** — el escenario MÁS común en RRHH-PE. Esto NO es un crash ni rompe la suite, pero subpaga grati / CTS / vac truncas en casi toda liquidación real. Por eso **no marco verde**: D (Vyntia Pay) heredaría un subpago sistemático, que es tan grave para nómina como el sobrepago que v1 detectó.

- Si D va a recalcular la liquidación final con su propio motor (y este servicio queda como "estimación mínima"), entonces el caveat es aceptable → 🟢 condicional.
- Si D consume estos montos como definitivos → 🔴, debe corregirse el conteo de "mes calendario completo" antes del sello.

---

## Tabla de edge-cases verificados

| Caso | Input | Esperado | Real | ✓/✗ |
|------|-------|----------|------|-----|
| **29-feb cese (fix crash)** | `_minus_one_year(2024-02-29)` | 2023-02-28 (no bisiesto) | 2023-02-28 | ✓ |
| 29-feb otro año | `_minus_one_year(2020-02-29)` | 2019-02-28 | 2019-02-28 | ✓ |
| 28-feb | `_minus_one_year(2023-02-28)` | 2022-02-28 | 2022-02-28 | ✓ |
| 01-mar | `_minus_one_year(2024-03-01)` | 2023-03-01 | 2023-03-01 | ✓ |
| 31-dic | `_minus_one_year(2023-12-31)` | 2022-12-31 | 2022-12-31 | ✓ |
| 30-abr | `_minus_one_year(2024-04-30)` | 2023-04-30 | 2023-04-30 | ✓ |
| Liquidación 29-feb-2024 (no crash) | settlement cese 2024-02-29, inicio 2020-01-01 | status=computed, sin ValueError | computed | ✓ |
| Leap 29-feb-2024, inicio leap 2020-02-29 | `_compute_vac_truncas` | 12m → 30d → 3000 | 3000.00 | ✓ |
| **_months_between sin +1** | 1 mes exacto (Ene1→Feb1) | 1 | 1 | ✓ |
| 3 meses | Ene1→Abr1 | 3 | 3 | ✓ |
| 6 meses | Ene1→Jul1 | 6 | 6 | ✓ |
| 12 meses | Ene1→Ene1 | 12 | 12 | ✓ |
| fracción 14 días | Ene1→Ene15 | 0 | 0 | ✓ |
| fracción 20 días | Ene1→Ene21 | 0 | 0 | ✓ |
| **Vac truncas 1 mes** | sueldo 3000, Ene1→Feb1 | 2.5d → 250.00 | 250.00 | ✓ |
| Vac truncas 3 meses | Ene1→Abr1 | 7.5d → 750.00 | 750.00 | ✓ |
| Vac truncas 6 meses | Ene1→Jul1 | 15d → 1500.00 | 1500.00 | ✓ |
| Vac truncas fracción 20d | Ene1→Ene21 | 0d → 0.00 | 0.00 | ✓ |
| **CTS 15 días ≠ mes** | sueldo 3000, Jun1→Jun15 | 0 meses → 0.00 | 0.00 | ✓ |
| CTS 1 mes exacto | May1→Jun1 | 1 mes → 500.00 | 500.00 | ✓ |
| **Golden renuncia** | causal=renuncia | indemnización 0.00 | 0.00 | ✓ |
| **Golden despido_arbitrario** | 2 años, sueldo 4000 | 12000.00 | 12000.00 | ✓ |
| **Golden cap 12 sueldos** | 20 años, sueldo 2000 | 24000.00 (cap) | 24000.00 | ✓ |
| **Golden idempotencia** | recompute x2 | mismo pk, 4 líneas, mismo total | OK | ✓ |
| **🔴 NUEVO: grat fin de semestre** | Jul1→Dic31 (semestre completo) | 3000.00 (6/6) | **2500.00 (5/6)** | ✗ |
| 🔴 NUEVO: grat Ene1→Jun30 | semestre ene-jun completo | 3000.00 | **2500.00** | ✗ |
| 🔴 NUEVO: CTS May1→Oct31 | semestre completo | 3000.00 | **2500.00** | ✗ |
| 🔴 NUEVO: vac Jul1-2023→Jun30-2024 | 1 año completo | 3000.00 (30d) | **2750.00 (27.5d)** | ✗ |

---

## Hallazgos

### [ALTO] NUEVO — Cese a fin de mes subcuenta 1 mes ("mes calendario completo")
- **Caso afectado:** test `test_grat_trunca_fin_de_semestre_paga_completo` (xfail strict)
- **Comportamiento esperado:** un trabajador que labora del 1 al último día de un mes trabajó **un mes calendario completo** (doctrina peruana "mes calendario completo": Ley 27735 + D.S. 005-2002-TR para grati; D.S. 001-97-TR para CTS; D.S. 012-92-TR para vacaciones cuenta días efectivos). Jul1→Dic31 = 6 meses → grati 6/6 = 1 sueldo (3000).
- **Comportamiento observado:** `_months_between` cuenta por aniversario día-de-mes: Jul1→Dic31 = 5 meses (el 6º "completa" el Jul1 siguiente). Grati = 5/6 = 2500. Mismo subconteo en CTS (May1→Oct31 = 2500 en vez de 3000) y vac truncas (1 año completo a fin de mes = 27.5d en vez de 30d).
- **Por qué importa:** el **99% de ceses en RRHH-PE son a fin de mes** (renuncia con 30 días, fin de contrato, despido a fin de período). El fix de v1 corrigió un sobrepago (+1 inclusivo) pero pasó al extremo opuesto: ahora subpaga 1 mes en casi toda liquidación real. Para nómina, subpago = contingencia laboral (demanda por liquidación diminuta) tan grave como el sobrepago.
- **Repro:**
  ```
  cd D:/VYNTIA/apps/api
  python -c "import django; django.setup(); from datetime import date; from decimal import Decimal; from apps.contracts.services import severance_service as s; print(s._compute_grat_trunca(Decimal('3000'), date(2024,7,1), date(2024,12,31))[0])"
  # -> 2500.00  (esperado 3000.00)
  ```
  (DJANGO_SETTINGS_MODULE=vyntia.settings.testing)
- **Fix sugerido (no aplicado — es código de producción):** en `_months_between`, normalizar `end` al día siguiente cuando es el último día calendario de su mes (o tratar "1 al último día" como mes completo), o devolver `(meses, días_residuales)` y que CTS/grati/vac computen los días residuales por la componente días/360 (D.S. 001-97-TR). Esto resuelve el subconteo sin reintroducir el +1 inclusivo de v1 (la fracción real <mes seguiría sin contarse como mes completo).

---

## Estado de los 3 bugs de v1

| Bug v1 | Severidad v1 | Estado v2 |
|--------|--------------|-----------|
| #6 Cese 29-feb crashea (`ValueError`) | 🔴 CRÍTICO | ✅ ARREGLADO — `_minus_one_year` clampa a 28-feb; no crash; liquidación computa |
| #7 Vac truncas +1 inclusivo (1 mes = 5d) | 🟠 ALTO | ✅ ARREGLADO — 1 mes = 2.5d = 250.00 |
| #8 CTS fracción = mes completo | 🟠 ALTO | ✅ ARREGLADO — 15 días = 0 meses = 0.00 |

Los gaps legales de v1 (tope 5 años #flujo1, desnaturalización #flujo2) siguen sin tocar — fuera del scope de este narrow re-audit, ya documentados como gaps en v1.

---

## Tests nuevos creados
- `apps/api/apps/contracts/tests/test_contracts_hr_audit_v2_seal.py` — 27 ítems:
  - 6 parametrize `_minus_one_year` (29-feb + vecinos) — PASAN
  - 8 parametrize `_months_between` (sin +1 inclusivo) — PASAN
  - 5 parametrize vac truncas proporcional (2.5d/mes) — PASAN
  - 2 CTS fracción/mes exacto — PASAN
  - 5 parametrize tricky cese dates no-crash (29-feb leap, 28-feb, 01-mar, 30-abr, 31) — PASAN
  - 1 `xfail(strict=True)` que fija el hallazgo nuevo (grati fin de semestre = sueldo completo); vira a XPASS cuando se corrija el conteo de mes calendario.

Suite contracts: **144 passed + 1 xfailed** (baseline 118 → sin regresión, +26 tests).

---

## Acciones recomendadas
- [ ] CORTO — Decidir con humano: ¿severance_service es estimación mínima (D recalcula) o liquidación definitiva? Define si el subconteo fin-de-mes es bug a corregir aquí o limitación documentada.
- [ ] CORTO (si definitiva) — Corregir `_months_between` para tratar "1 al último día del mes" como mes calendario completo, sin reintroducir el +1 inclusivo de v1.
- [ ] LARGO — Heredado de v1: validación tope 5 años + servicio de desnaturalización modal→indefinido antes de que D consuma la clasificación.

## Pregunta para humano (bloqueante del sello verde)
¿`severance_service` entrega montos **definitivos** de liquidación o una **estimación mínima** que D (Vyntia Pay) recalcula con su motor de nómina? De la respuesta depende si el subconteo de mes calendario (hallazgo nuevo) es 🔴 bug a corregir antes del sello, o 🟢 limitación aceptable documentada en ADR-B.9.
