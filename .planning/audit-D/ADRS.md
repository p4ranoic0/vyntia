# Sub-project D — Architectural Decision Records

> 8 cross-cutting decisions to lock before D.1 starts coding. Each ADR follows the format:
> Title / Context / Decision / Consequences / Status (proposed | accepted | superseded).

## ADR-D.1: Strategy Pattern interface

**Status:** accepted

**Context:**
Per D-A, D-Pay ships 728-only but the architecture must support inyectar otros regímenes (CAS, 276, SERVIR, MYPE, Agrario, etc.) sin refactor del engine. Strategy Pattern via ABC con factory.

**Decision:**
Define `RegimenStrategy` (ABC) in `apps/api/apps/payroll/strategies/base.py` con métodos:

```python
class RegimenStrategy(ABC):
    @abstractmethod
    def compute_payslip(self, employee, period: PayrollPeriod) -> PaySlipSnapshot: ...

    @abstractmethod
    def compute_cts(self, employee, semester: CtsSemester) -> CtsResult: ...

    @abstractmethod
    def compute_gratification(self, employee, semester: GratiPeriod) -> GratiResult: ...

    @abstractmethod
    def compute_severance(self, employee, termination_date: date, cause: str) -> SettleResult: ...

    @abstractmethod
    def compute_renta_5ta(self, employee, period: PayrollPeriod, accumulated: Decimal) -> Decimal: ...
```

Dataclass returns son IMMUTABLE (`@dataclass(frozen=True)`).

Factory en `apps/api/apps/payroll/strategies/__init__.py`:

```python
class RegimenStrategyFactory:
    _registry: dict[str, type[RegimenStrategy]] = {}

    @classmethod
    def register(cls, regimen_code: str, strategy_cls: type[RegimenStrategy]) -> None: ...

    @classmethod
    def get(cls, regimen_code: str, as_of_date: date) -> RegimenStrategy:
        cls = cls._registry[regimen_code]
        regimen_config = RegimenConfig.get(regimen_code, as_of_date)
        return cls(regimen_config)
```

`Regime728Strategy` se registra en `apps/api/apps/payroll/strategies/regime_728.py` con `RegimenStrategyFactory.register("728", Regime728Strategy)`.

**Consequences:**
- D.1 crea el skeleton (ABC + factory + stub Regime728Strategy).
- D.4 implementa Regime728Strategy completo.
- Cualquier régimen futuro (post-D) registra su Strategy + RegimenConfig sin tocar el engine.
- Tests del engine son fixture-driven sobre `strategy.compute_*` (puros, sin DB).
- Pros: clean DI, extensible, testable.
- Contras: indirection extra cuando solo hay 1 régimen (acceptable cost for forward-compat).

## ADR-D.2: Decimal precision policy

**Status:** accepted

**Context:**
Cálculos de planilla son finanzas peruanas en soles. SUNAT y AFPnet exigen valores en céntimos (2 decimales) pero los cálculos intermedios (tasas, promedios, divisiones por 360) necesitan más precisión para evitar drift.

**Decision:**
- **Intermedios:** `Decimal(14, 4)` — 14 dígitos total, 4 decimales. Suficiente para `999_999_999.9999` (largest realistic intermediate).
- **Finales (montos persisted en `PayrollLine.amount`, `PaySlip.*`, `CtsDeposit.amount`, etc.):** `Decimal(12, 2)` — 12 dígitos total, 2 decimales. Permite `9_999_999_999.99` (suficiente para corporativo grande).
- **Tasas (`TaxParameter.value` cuando `unit='RATE'`):** `Decimal(14, 4)` — ej. `0.0137` para prima SISCO.
- **Redondeo:** `ROUND_HALF_UP` en cada conversion intermedio→final. Estándar SUNAT (verificado en cartilla PVS).
- **Quantize policy:** después de cada `compute_*` retornar montos con `.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.

**Consequences:**
- Modelos: `DecimalField(max_digits=12, decimal_places=2)` para campos `amount` finales; `DecimalField(max_digits=14, decimal_places=4)` para `TaxParameter.value` y cómputos intermedios persistidos.
- Test helpers: `assert_money_equal(a, b)` con tolerancia `Decimal("0.00")` (zero tolerance una vez se aplicó quantize).
- Riesgo: divisor 360 en CTS+vac truncas — usar `Decimal` desde input, NO float.

## ADR-D.3: audit_lite payload shape `payroll.*`

**Status:** accepted

> **Audit confirmation (INV § 2):** Task 3 confirmed `audit_lite.AuditEvent.schema_version` field DOES NOT EXIST in the current model. The D.1 migration to add this field is **required** (not optional). Status promoted from pending to accepted.

**Context:**
Per D-C, persistencia es CRUD pero audit_lite registra eventos high-stakes con payload shape ES-compatible para forward-compat. Cada fase regulatoria debe emitir eventos persistidos.

**Decision:**
Cada evento payroll persisted en `apps.audit_lite.AuditEvent` con shape:

```json
{
  "event_type": "payroll.run.calculated",
  "schema_version": 1,
  "actor_id": "<UUID identity.User>",
  "tenant_id": "<UUID tenant>",
  "target_type": "PayrollRun",
  "target_id": "<UUID>",
  "payload": {
    "period_year": 2026,
    "period_month": 5,
    "period_type": "REGULAR",
    "total_gross": "150000.00",
    "total_net": "120000.00",
    "total_employer_contributions": "13500.00",
    "slip_count": 50,
    "calculation_duration_ms": 1234
  },
  "occurred_at": "2026-06-01T10:23:45Z"
}
```

Event types canonical:
- `payroll.run.created` (DRAFT)
- `payroll.run.calculated` (DRAFT→CALCULATED)
- `payroll.run.approved` (CALCULATED→APPROVED)
- `payroll.run.closed` (APPROVED→CLOSED)
- `payroll.run.reopened` (CLOSED→REOPENED)
- `payroll.slip.calculated` (per-employee snapshot)
- `payroll.adjustment.applied`
- `cts.deposit.computed`
- `cts.deposit.paid`
- `gratification.computed`
- `gratification.paid`
- `severance.settlement.computed`
- `severance.settlement.paid`

`apps.audit_lite.AuditEvent` does NOT have `schema_version` field (confirmed by INV § 2 audit). D.1 adds it via migration (preserves backward-compat: `default=1`):

```python
models.IntegerField(default=1, help_text="Payload schema version for forward-compat")
```

**Consequences:**
- D.1 migration adds `schema_version` to AuditEvent (REQUIRED — confirmed missing by audit).
- D.5 service emits events on every state transition.
- D.7/D.8/D.12 services emit their respective events.
- Future ES migration can replay these payloads to reconstruct state.

## ADR-D.4: PayrollRun concurrency

**Status:** accepted

**Context:**
PayrollRun pasa por estados (DRAFT→CALCULATED→APPROVED→CLOSED→REOPENED). Dos operadores podrían intentar cerrar el mismo run simultáneamente. ¿Lock pessimistic o optimistic?

**Decision:**
**Pessimistic locking** via `select_for_update()` en todas las transiciones de status del PayrollRun. Razones:
- Operaciones de cierre son raras (1 por mes) — overhead de lock es trivial.
- Cálculo (CALCULATED transition) puede tomar 30s+ para 50 empleados — ventana para race condition.
- Optimistic locking requiere version field + retry loop — más complejidad para mismo resultado.

Implementación en `PayrollRunService`:

```python
@transaction.atomic
def calculate(self, payroll_run_id: UUID, actor: User) -> None:
    run = PayrollRun.objects.select_for_update().get(pk=payroll_run_id)
    if run.status != "DRAFT":
        raise InvalidTransition(f"Cannot calculate from status={run.status}")
    # ... compute slips ...
    run.status = "CALCULATED"
    run.save()
    AuditEvent.objects.create(event_type="payroll.run.calculated", ...)
```

`PayrollAdjustment` también usa `select_for_update()` sobre el `PayrollRun` para evitar adjustes simultáneos en runs CALCULATED.

**Consequences:**
- Tests deben usar `transaction.atomic` + `pytest.mark.django_db(transaction=True)` para verificar lock real.
- Postgres-only (SQLite local respeta la sintaxis pero no aplica lock real — tests integration corren contra Postgres).
- Sin retry loop necesario.

## ADR-D.5: Renta 5ta correction al cese

**Status:** accepted

> **Audit confirmation (INV § 5 N09):** Task 6 extracted N09 rules. Rule N09-12 (December final adjustment), N09-13 (non-negative monthly retention), and N09-14 (excess is refunded) confirm the regularización formula below. Status promoted from pending to accepted. Specific rule references added in Decision section.

**Context:**
N09 § 5 defines an ALGORITHMO PROYECTIVO mensual (RBA = rem mes × meses_restantes + ...) that assumes the worker remains through December. When a worker ceases before December, the projection was incorrect — regularización is required.

**Decision:**
En `Regime728Strategy.compute_renta_5ta` cuando `compute_severance` lo llama (i.e., en contexto cese), aplicar la regularización:

```
1. Calcular Renta real anual:
   real_anual = remuneraciones_pagadas_ene_a_cese + grati_pagadas_ene_a_cese
   renta_neta_real = max(0, real_anual - 7 × UIT_vigente_cese)
   impuesto_anual_real = aplicar_escala_progresiva(renta_neta_real)

2. Sumar retenciones aplicadas previamente:
   total_retenido = sum(payslip.renta_5ta_amount for payslip in periodos_anteriores)

3. Ajuste cese:
   ajuste = impuesto_anual_real - total_retenido
   # Si ajuste > 0: trabajador debe pagar más → descuento adicional en liquidación
   # Si ajuste < 0: trabajador tiene retención excesiva → devolución en liquidación
```

Normativa base: N09 § 5.5 (ajuste diciembre, mismo mecanismo para cese anticipado) + N09 § 11.4 (exceso es devolución, N09-14).

El ajuste se persiste como `SeveranceLine` con `concept='renta_5ta_regularizacion_cese'` y monto positivo o negativo (signed).

**Consequences:**
- D.4 expone `compute_renta_5ta(employee, period, accumulated, mode='monthly'|'cese')`.
- D.12 invoca el modo cese.
- Test fixture: trabajador con sueldo 5000 cesa en agosto → comparar vs cálculo manual.
- Riesgo: trabajadores recontratados en mismo año (cese + reingreso) → fuera de scope MVP, se acumula como dos periods independientes (D.0 NOTA: si surge en cliente piloto, abrir D.x).

## ADR-D.6: Tax year cutoff

**Status:** accepted

**Context:**
UIT, RMV, asig familiar cambian cada año (TaxParameter con `valid_from`/`valid_to`). PayrollRun de diciembre 2026 usa UIT 2026 = S/5500. PayrollRun de enero 2027 usa UIT 2027 = S/X. ¿Qué pasa si el PLAME de diciembre se genera en enero (operador cerró tarde)?

**Decision:**
- **Cómputo usa los parámetros vigentes en el ÚLTIMO día del período**, no la fecha de cálculo. Ejemplo:
  - PayrollRun de período Y=2026, M=12, M.last_day=2026-12-31 → usa UIT 2026.
  - PayrollRun de período Y=2027, M=1, M.last_day=2027-01-31 → usa UIT 2027.
- **Lookup:** `TaxParameter.get(code="UIT", as_of_date=period_end_date)`.
- **PayrollRun.create_run** valida que `RegimenConfig.get(regimen, period_end_date)` exista para el régimen del empleado. Si no, error explícito al admin.
- **Grati Navidad pagada en enero por retraso operativo**: el PayrollRun debe ser período 2026-12 con TypePeriod=GRATIFICATION_NAV — los parámetros se calculan con cutoff 2026-12-31 aunque el pago real se ejecute en enero.

**Consequences:**
- D.2 `seed_payroll_catalog` siembra UIT/RMV/asig 2024, 2025, 2026, 2027 (los 4 años cubren retroactivos + forward).
- D.4 nunca usa `today` para parámetros — siempre `period_end_date` derivado del PayrollRun.
- Tests: verificar que cambiar `period_year` cambia UIT usada.

## ADR-D.7: PVS validator scope

**Status:** accepted

**Context:**
B.10 introdujo 11 reglas en `apps.contracts.services.tregistro_service.validate_pvs()` (RUC checksum, longitudes, fechas, choices, etc.). D.9 PlameExporter necesita validator más completo para los 10 archivos.

**Decision:**
Replicar las reglas de PVS oficial razonablemente conocidas (sin ingeniería inversa del binario PVS real). Set inicial:

**Heredadas de B.10 (11):**
1. RUC empleador: 11 dígitos numéricos + checksum mod 11
2. Documento trabajador: longitud según tipo (DNI=8, CE=9-12)
3. Fecha nacimiento ≤ today
4. Fecha ingreso ≥ fecha nacimiento + 18 años
5. Régimen pensionario ∈ choices oficiales
6. Régimen salud ∈ choices oficiales
7. Modalidad contractual ∈ choices oficiales
8. Tipo trabajo ∈ choices oficiales (N/C/M/P)
9. Sexo ∈ {M, F}
10. Días laborados ∈ [0, 31]
11. Sumatoria (días lab + días subs + días no lab) ≤ días del mes

**Nuevas D.9 (estimación 8-12 más):**
12. Cada PayrollLine.concept.sunat_code está en Tabla 22 vigente
13. Total ingresos PLANI.txt = sum(PayrollLine donde concept.category=INCOME)
14. Total descuentos PLANI.txt = sum(PayrollLine donde concept.category=DEDUCTION)
15. AFP CUSPP presente si pension_regime ∈ AFP_*
16. Aporte AFP empleador en PLANI = remuneración asegurable × 10% (tolerancia ±0.01)
17. Aporte EsSalud = sum_ingresos_afectos × 9% (tolerancia ±0.01)
18. Renta 5ta retenida ≤ tope progresivo (sanity)
19. Asig familiar = 10% RMV vigente período (si applicable)
20. (otros TBD durante implementación D.9)

**Consequences:**
- D.9 implementa `apps/api/apps/payroll/services/pvs_validator.py` con ~20 reglas + tests fixture-driven.
- Si el cliente piloto reporta PLAME rechazado por SUNAT con regla no replicada, D.x agrega la regla retrospectivamente.
- NO replica reglas de business semánticas (ej. "el sueldo no puede ser <RMV") — eso es validación del modelo en D.3.

## ADR-D.8: Regulatory sign-off workflow

**Status:** accepted

**Context:**
D-H decision: validation tier 4 requires user sign-off antes de merge de fases regulatorias D.4, D.7, D.8, D.12.

**Decision:**
Template `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md` con shape:

```markdown
# D.<N> <PhaseName> — Regulatory Sign-off

**Phase:** D.<N> · **Branch:** vyntia/D<N>-<name> · **Date generated:** YYYY-MM-DD

## Test results summary

- Tier 1 pytest unit: <N>/<N> passed
- Tier 2 pytest integration: <N>/<N> passed
- Cartilla SUNAT golden cases: <N>/<N> matched
- Benchmark Sentinel/Buk (opcional): <N>/<N> matched within ±0.01 PEN

## Scenarios computed

| # | Caso | Input (resumen) | Expected (cita normativa) | Computed | Match | Sentinel/Buk |
|---|------|----------------|---------------------------|----------|-------|--------------|
| 1 | Sueldo plano 3000, 30 días | basico=3000, dias=30, sin asig fam | gross=3000, AFP=300, neto=2700 (N07 § 1.2) | gross=3000, AFP=300, neto=2700 | ✓ | S/2700 ✓ |
| 2 | ... | ... | ... | ... | ✓/✗ | ... |
| ... (30 casos) | | | | | | |

## Notes / observaciones del autor

(El autor de la fase explica decisiones edge-case, qué reglas se omiten/postergan, etc.)

## Sign-off

- [ ] **APPROVED** — <user>, <ISO date>, comentario opcional
- [ ] **CHANGES_REQUESTED** — <user>, <ISO date>, razón obligatoria

## Estado actual

`regulatory_audit: pending | approved | changes_requested`
```

**Workflow:**
1. Al cerrar la fase D.<N>, el autor (Claude o user) genera el file llenando la tabla con los resultados de los tests + cita normativa per row.
2. Authors solicitan sign-off al user pegando link al file en mensaje de la terminal.
3. User abre el file, revisa, escribe APPROVED o CHANGES_REQUESTED y commitea el cambio en mismo branch.
4. Merge del PR queda gated en script `scripts/check_regulatory_signoff.sh` (D.0 BACKLOG agrega ese script como item de D.1) que verifica:
   - Si fase es D.4/D.7/D.8/D.12: existe `REGULATORY-SIGNOFF.md` con `APPROVED` checked
   - Si checked CHANGES_REQUESTED o ambos vacíos: exit 1
5. Tag final `d-vyntia-pay-complete` (D.14) verifica las 4 phases tienen sign-off APPROVED commiteado en master.

**Consequences:**
- 4 phases con artefactos extra de ~50-200 líneas c/u.
- ~1-2 días de latency por sign-off (acceptable, fase queda en branch).
- Trazabilidad regulatoria: ante reclamo SUNAFIL, los `REGULATORY-SIGNOFF.md` commiteados son evidencia de que el cálculo fue revisado por persona con expertise.
