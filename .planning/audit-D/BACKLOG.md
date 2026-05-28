# Vyntia Pay (D) — Backlog (D.0 audit)

> Prioritized list of actionable items derived from `INVENTORY.md`. Each item maps to a phase D.X.
> Audit date: 2026-05-23.

## Priority legend

- **P0** — blocks Starter tier launch
- **P1** — important but not launch-blocking; can ship in later phase
- **P2** — nice-to-have; may be deferred to post-D sub-project

## Type legend

- **regulatory** — rule derived from cartilla SUNAT / ley / D.S.
- **bug** — defect in existing code
- **parity** — feature in INTRANET legacy not yet ported (only if D-I greenfield finds anything worth porting)
- **new** — model/service from spec § 4 to build
- **tenant** — multi-tenant readiness fix
- **deuda** — debt cleanup

---

## Summary

- **Total items:** 118
- **P0:** 58 · **P1:** 43 · **P2:** 17

### By phase

| Phase | P0 | P1 | P2 | Total |
|-------|---:|---:|---:|------:|
| D.1   | 10 |  2 |  3 |    15 |
| D.2   | 14 |  9 |  2 |    25 |
| D.3   |  2 |  2 |  0 |     4 |
| D.4   | 14 |  9 |  4 |    27 |
| D.5   |  2 |  2 |  0 |     4 |
| D.6   |  4 |  4 |  0 |     8 |
| D.7   |  4 |  2 |  1 |     7 |
| D.8   |  4 |  2 |  1 |     7 |
| D.9   |  2 |  2 |  2 |     6 |
| D.10  |  2 |  2 |  1 |     5 |
| D.11  |  0 |  2 |  2 |     4 |
| D.12  |  0 |  5 |  1 |     6 |
| D.13  |  0 |  0 |  0 |     0 |
| D.14  |  0 |  0 |  0 |     0 |

> **Note on D.1 split:** D.1 is a candidate for a D.1a / D.1b split (confirmed in Task 9 ROADMAP-D). D.1a = migrate external consumers of legacy models/services (backend views, frontend service layer stubs); D.1b = drop legacy payroll schema + squash migrations. Items below tagged `Phase: D.1` are annotated with `[D.1a]` or `[D.1b]` to signal intended split placement.

---

## Backlog

| # | Item | Area | Type | Prio | Phase | Deps | Estimation | Source/Cita |
|---|------|------|------|------|-------|------|-----------|-------------|
| 1 | ✅ **[D.1a] Migrate `api/v1/rrhh/views.py` + `serializers.py`** — remove imports of `AfpConfiguration`, `CompensationConfiguration` from `apps.payroll.models`; replace with stub 404 or redirect to new D.2 endpoints when available | backend | deuda | P0 | D.1 | — | 2h | INV § 1 consumer audit |
| 2 | ✅ **[D.1a] Migrate `remuneraciones_views.py`** — replace `PlanillaCalculoService` + `DescuentoMasivoService` instantiation with stub 501 responses; add TODO comment pointing to D.4 + D.13 | backend | deuda | P0 | D.1 | — | 3h | INV § 1 consumer audit |
| 3 | ✅ **[D.1a] Guard `HROverviewDashboard.tsx` `/api/v1/payroll/monthly-runs/` call** — wrap in `try/catch` with graceful degradation or feature flag until D.5 provides live endpoint | frontend | deuda | P0 | D.1 | — | 1h | INV § 1 consumer audit |
| 4 | ✅ **[D.1a] Preserve legacy `/api/v1/payroll/*` endpoint URIs** — ensure backend returns at least 501/503 JSON (not 404) so frontend `payrollService.ts` (47 calls) doesn't hard-crash | backend | deuda | P0 | D.1 | — | 1h | INV § 1 consumer audit; INV § 3 |
| 5 | ✅ **[D.1b] Drop 9 legacy payroll models** — `AfpConfiguration`, `CompensationConfiguration`, `MonthlyPayroll`, `PayrollDetail`, `PayrollConcept`, `MassDeduction`, `PaySlip`, `PaymentSchedule`, `TaxParameter` | backend | deuda | P0 | D.1 | 1, 2 | 2h | INV § 1 disposition table |
| 6 | ✅ **[D.1b] Drop legacy `PlanillaCalculoService` + `DescuentoMasivoService`** — delete `services/planilla_calculo_service.py` + `services/descuento_masivo_service.py` | backend | deuda | P0 | D.1 | 2 | 30m | INV § 1 disposition table |
| 7 | ✅ **[D.1b] Drop legacy payroll migrations** — done via `0003_drop_legacy_payroll` (DeleteModel × 9), keeping 0001/0002 for graph consistency instead of squash — see D1b plan Decisions | backend | deuda | P0 | D.1 | 5 | 1h | INV § 1 migration disposition |
| 8 | ✅ **[D.1b] Drop `seed_remuneraciones_config` management command** — delete `apps/payroll/management/commands/seed_remuneraciones_config.py` and package markers | backend | deuda | P0 | D.1 | 5 | 15m | INV § 1 disposition table |
| 9 | ✅ **Add `schema_version` field to `audit_lite.AuditEvent`** — `models.IntegerField(default=1, help_text="Payload schema version for forward-compat")`; create Django migration | backend | new | P0 | D.1 | — | 1h | INV § 2 AuditEvent; ADR-D.3 |
| 10 | ✅ **Register `payroll.*` audit action namespaces** — document canonical action names (e.g. `payroll.run.closed`, `payroll.payslip.generated`, `payroll.cts.deposited`) so all D phases use consistent naming | backend | new | P0 | D.1 | 9 | 1h | INV § 2 AuditEvent |
| 11 | ✅ **Verify `App.tsx` payroll page routing imports** — confirm 7 payroll page components still resolve after D.1b drops; no dead imports | frontend | deuda | P1 | D.1 | 5 | 30m | INV § 1 consumer audit (App.tsx) |
| 12 | ✅ **Add pytest regression suite for D.1 drop** — confirm 0 import errors after legacy drop via `manage.py check` + pytest full run | backend | new | P1 | D.1 | 5,6,7,8 | 1h | INV § 4 baselines |
| 13 | ✅ **Document D.1a/D.1b split decision in ROADMAP-D** — add note explaining that migration tasks (1-4) must land before drop tasks (5-8) in the same phase or via explicit D.1a/D.1b sub-milestones | docs | deuda | P2 | D.1 | — | 30m | INV § 1 pre-D-I migration table |
| 14 | **Add `get_request_tenant()` shared helper in `apps/core/`** — extract repeated `getattr(request, "tenant", None)` pattern (30+ view sites) into a single utility; D views use `TenantAwareViewSetMixin` which already has this, but RRHH legacy views still use raw getattr | backend | deuda | P2 | D.1 | — | 1h | INV § 4 open deuda |
| 15 | **Seed Tabla 22 ~25 conceptos oficiales** — create `PayrollConcept` (new D.2 model) seed rows for all SUNAT Tabla 22 codes used in MVP: 0101 Rem.básica, 0102 Alimentación especie, 0103 Comisiones, 0104 Asig.familiar, 0106 Horas extras, 0107 Vacaciones, 0108 Reintegros, 0109 Grati FP, 0110 Grati Nav, 0111 Grati trunca, 0115 Movilidad, 0116 Refrigerio, 0120 CTS, 0501 Indem.vac.no gozadas, 0503 Indem.despido arbitrario, 0601 AFP fondo, 0605 Renta 5ta, 0606 Comisión/Prima AFP, 0607 AFP voluntario, 0801 EsSalud 9%, 0803 SCTR Salud, 0804 SCTR Pensiones, 0805 SENATI (nota), 0806 SENCICO (nota) | backend | regulatory | P0 | D.2 | — | 4h | N06-20..N06-39; N07-23,24,25 |
| 16 | **Each `PayrollConcept` row must include JSONB afectación matrix** — fields: `afecta_renta_5ta`, `afecta_afp`, `afecta_onp`, `afecta_essalud`, `afecta_cts`, `afecta_gratificacion` (booleans per N06 Tabla 22) | backend | regulatory | P0 | D.2 | 15 | 2h | N06-41 |
| 17 | **`codigo_sunat` field required on `PayrollConcept` form** — validation: must be non-empty 4-char code mapped to SUNAT Tabla 22; prevent creating concepts without SUNAT code | backend | regulatory | P0 | D.2 | 15 | 1h | N06-42 |
| 18 | **Seed SUNAT Tabla paramétricas versionadas** — create model `SunatTable` (or `PayrollCatalog`) with fields `table_number`, `code`, `description`, `valid_from`, `valid_to`; seed: Tabla 1 (tipo doc), Tabla 8 (tipo trabajador), Tabla 9 (CIUO-08 ocupación), Tabla 11 (régimen pensionario), Tabla 12 (tipo contrato), Tabla 13 (régimen salud), Tabla 17 (motivo cese), Tabla 18 (tipo jornada) | backend | regulatory | P0 | D.2 | — | 3h | N06-11..N06-18; N06-40 |
| 19 | **Seed AFP/ONP/EsSalud `TaxParameter` rows** — create new D.2 `TaxParameter` model with `unit` field + versioning; seed: AFP tasas (Integra, Prima, Profuturo, Habitat — flujo + mixta), ONP 13%, EsSalud 9%, RMA tope trimestral (S/12,598.91 Abr-Jun 2026), UIT 2026 (S/5,500) | backend | regulatory | P0 | D.2 | — | 3h | N07-01..N07-05; N07-27,28; N09-01 |
| 20 | **`TaxParameter.unit` + versioning fields** — add `unit` (e.g. `percentage`, `soles`, `uit_multiple`), `valid_from`, `valid_to` date fields; deprecate single `anio` field from legacy shape | backend | new | P0 | D.2 | — | 1h | INV § 1 (TaxParameter legacy gaps) |
| 21 | **Seed RMA trimestral table** — `TaxParameter` rows for Remuneración Máxima Asegurable (AFP prima SISCO tope); `valid_from`/`valid_to` quarterly; seed 2025-2027 | backend | regulatory | P0 | D.2 | 19,20 | 1h | N07-03; N07-27 |
| 22 | **Tabla 19 — Tipo Suspensión codes** — seed: 11 Maternidad, 12 Incapacidad temporal, 14 Vacaciones, 21 Licencia sin goce, 22 Huelga; required for PLAME JORNA file | backend | regulatory | P0 | D.2 | 18 | 1h | N06-19 |
| 23 | **Non-remunerative concepts list** — document and seed `PayrollConcept.es_remunerativo=False` for: gratif. extraordinarias, utilidades, bonif. extraord. Ley 30334, movilidad, refrigerio, condiciones de trabajo, canasta navideña, asignaciones por fallecimiento/matrimonio/nacimiento | backend | regulatory | P0 | D.2 | 15 | 1h | N08-37; N09-16 |
| 24 | **SCTR concepts seeded as `aplica=False` for MVP** — 0803 SCTR Salud + 0804 SCTR Pensiones present in catalog but flagged `applies_to_regime='alto_riesgo'`; MVP D-A marks as not-applicable for régimen 728 oficinas | backend | regulatory | P1 | D.2 | 15 | 30m | N07-22,23 |
| 25 | **SENATI + SENCICO seeded as notes** — 0805 + 0806 present in catalog as `aplica=False`; note: SENATI only industria manufacturera >20 workers; SENCICO only construcción | backend | regulatory | P1 | D.2 | 15 | 30m | N07-24,25 |
| 26 | **`seed_payroll_catalog` management command** — replace legacy `seed_remuneraciones_config.py`; seeds all Tabla 22 concepts + TaxParameter rows + Tablas paramétricas atomically; idempotent (upsert by code+valid_from) | backend | new | P0 | D.2 | 15,18,19 | 3h | INV § 1 (seed_remuneraciones_config disposition) |
| 27 | **Concepto 0102 Alimentación especie — afectación completa** — `afecta_renta_5ta=True, afecta_afp=True, afecta_essalud=True, afecta_cts=True` | backend | regulatory | P1 | D.2 | 16 | 30m | N06-21 |
| 28 | **Concepto 0103 Comisiones regulares — afectación condicional CTS** — `afecta_cts` only if perceived ≥3 times in semester (promedio); requires flag `es_variable=True` + `frecuencia_minima_cts=3` on concept | backend | regulatory | P1 | D.2 | 16 | 1h | N06-22; N08-03 |
| 29 | **Concepto 0106 Horas extras — afectación condicional CTS/grati** — same `es_variable=True`, `frecuencia_minima_cts=3` pattern; N08-43 confirms | backend | regulatory | P1 | D.2 | 16 | 1h | N06-24; N08-03,43 |
| 30 | **Gratificación conceptos 0109/0110/0111 — EsSalud exclusión Ley 30334** — seed with `afecta_essalud=False` (Ley 30334); Bonif. Extraordinaria Ley 30334 = separate concept seeded as `afecta_renta_5ta=True, afecta_essalud=False` | backend | regulatory | P0 | D.2 | 16 | 1h | N06-27,28,29; N08-13,14 |
| 31 | **CTS concepto 0120 — fully excluded from all tributes** — `afecta_renta_5ta=False, afecta_afp=False, afecta_onp=False, afecta_essalud=False, afecta_cts=False` | backend | regulatory | P0 | D.2 | 16 | 30m | N06-32 |
| 32 | **T-Registro Tabla 14 — Régimen pensionario codes** — confirm model stores `regimen_pensionario` as code `04`/`21`/`22`/`23`/`25`/`32`; add validator mapping `Employee.sistema_pensiones` → N06 Tabla 14 code | backend | regulatory | P1 | D.2 | 18 | 1h | N06-14 |
| 33 | **T-Registro Tabla 12 — tipo contrato mapping** — `Contract.tipo_documento` (`LEY_728_FIJO`, `LEY_728_INDETERMINADO`, etc.) → SUNAT Tabla 12 codes (01–04); add mapping function | backend | regulatory | P1 | D.2 | 18 | 1h | N06-15 |
| 34 | **CIUO-08 `codigo_ocupacion` field on `Employee` or `EmploymentData`** — T-Registro requires 4-digit CIUO-08 occupational code; currently missing; D.2 adds field + seed partial CIUO-08 catalog for common Peruvian HR roles | backend | regulatory | P1 | D.2 | 18 | 2h | N06-13 |
| 35 | **Tipo documento SUNAT mapping** — `Employee.tipo_documento` (`DNI`/`CE`/`PASAPORTE`/`OTROS`) → SUNAT Tabla 1 codes (01/04/07/00); add mapping util | backend | regulatory | P0 | D.2 | 18 | 1h | N06-11 |
| 36 | **Tipo jornada mapping** — `EmploymentData.jornada_laboral` (`completa`/`parcial`/`por_horas`) → SUNAT Tabla 18 codes (1/4 Reducida); add mapping | backend | regulatory | P1 | D.2 | 18 | 1h | N06-18 |
| 37 | **Tipo trabajador Tabla 8 codes** — seed codes 10 (Indeterminado 728) + 11 (Plazo fijo 728) as MVP scope; others (276, CAS, MYPE, agrario) seeded but flagged `post_mvp=True` | backend | regulatory | P2 | D.2 | 18 | 30m | N06-12 |
| 38 | **Régimen salud Tabla 13 codes** — seed 01 (EsSalud) + 04 (EsSalud+EPS); map from `Employee.tipo_seguro_salud` (`ESSALUD`→01, `EPS`→04) | backend | regulatory | P2 | D.2 | 18 | 30m | N06-16 |
| 39 | **`Compensation` model — single source of truth for salary** — create `apps/payroll/models/compensation.py` with `Compensation` model: `employee` FK, `tenant`, `effective_date`, `base_salary`, `asignacion_familiar`, `source` (choices: `manual`, `contract_amendment`), `contract_snapshot` FK (nullable) | backend | new | P0 | D.3 | — | 3h | INV § 2 salary divergence; INV § 2 EmploymentData.sueldo_basico |
| 40 | **Reconcile `Contract.salario_bruto` vs `EmploymentData.sueldo_basico` divergence** — D.3 migration script: for each employee, compare both values; if divergent, create `Compensation` row from the higher (or most recent `ContractAmendment.nuevo_salario`) + audit log the divergence | backend | bug | P0 | D.3 | 39 | 2h | INV § 2 Contract salary divergence warning |
| 41 | **`Compensation` as salary reader in D.4 engine** — `Regime728Strategy.compute_payslip()` reads `Compensation.base_salary` (not `EmploymentData.sueldo_basico` directly); falling back to `sueldo_basico` if no `Compensation` row exists | backend | new | P1 | D.3 | 39 | 1h | INV § 2 EmploymentData.sueldo_basico notes |
| 42 | **`Compensation` salary history API** — viewset for listing salary history per employee; used in D.3 admin screen and D.12 settlement computations | backend | new | P1 | D.3 | 39 | 2h | INV § 2 ContractAmendment |
| 43 | **`EmploymentData.REGIMENES_PLANILLA` filter verified** — add explicit test that D.4 engine only processes employees with `regimen_laboral in ('728',)` for MVP; assert `276`, `1057`, `practicas`, `locacion`, `consultoria` are excluded from PayrollRun | backend | regulatory | P0 | D.4 | — | 1h | INV § 2 REGIMENES_PLANILLA; N06-12 |
| 44 | **Renta 5ta engine — Step 1 RBA computation** — `RBA = rem_mensual × meses_restantes + rem_acumuladas + grati_proyectada + bonif_ext_30334 + otros_regulares`; gratificaciones ordinarias (Jul + Dic) projected using expected formula if not yet paid | backend | regulatory | P0 | D.4 | 43 | 4h | N09-06 |
| 45 | **Renta 5ta engine — Step 2 RNAP = RBA − 7 UIT** — if RNAP ≤ 0 → retención = 0; UIT loaded from `TaxParameter` for fiscal year | backend | regulatory | P0 | D.4 | 44 | 1h | N09-02,08 |
| 46 | **Renta 5ta engine — Step 3 IAP progressive scale** — apply 5-bracket scale (8%/14%/17%/20%/30%) tramo-by-tramo to RNAP | backend | regulatory | P0 | D.4 | 45 | 2h | N09-04,05,09 |
| 47 | **Renta 5ta engine — Step 4 monthly retention with denominators** — denominator table: Jan=12, Feb=12, Mar=12, Apr=9, May=8, Jun=8, Jul=8, Aug=5, Sep=4, Oct=4, Nov=4 | backend | regulatory | P0 | D.4 | 46 | 1h | N09-10,11 |
| 48 | **Renta 5ta engine — December adjustment** — `retención_dic = IAP_definitivo − retenciones_acumuladas_ene_nov`; no denominador; regularización definitiva; retention cannot be negative (carry forward as credit) | backend | regulatory | P0 | D.4 | 47 | 2h | N09-12,13,14 |
| 49 | **AFP fondo 10% computation** — apply to `remuneración_asegurable`; `Employee.sistema_pensiones` drives AFP vs ONP branch | backend | regulatory | P0 | D.4 | 43 | 1h | N07-01 |
| 50 | **AFP prima SISCO 1.37%** — apply to `remuneración_asegurable` capped at RMA (from `TaxParameter`); excess over RMA pays no prima but still pays fondo + comisión | backend | regulatory | P0 | D.4 | 49 | 1h | N07-02,03 |
| 51 | **AFP comisión by `Employee.tipo_comision`** — `FLUJO`: rate by AFP × remuneración_mensual; `MIXTA`: annual rate × fondo_acumulado; rates from `TaxParameter` | backend | regulatory | P0 | D.4 | 49 | 2h | N07-04,05,06 |
| 52 | **ONP 13% with base mínima RMV** — apply if `sistema_pensiones='ONP'`; minimum base = RMV (S/1,130 para 2026) even if employee earned less | backend | regulatory | P0 | D.4 | 43 | 1h | N07-10 |
| 53 | **EsSalud 9% employer contribution** — apply to `remuneración_asegurable`; base mínima = RMV (same period) even if employee earned less that period | backend | regulatory | P0 | D.4 | 43 | 1h | N07-13 |
| 54 | **EPS crédito 2.25%** — if `Employee.tipo_seguro_salud='EPS'`: employer pays 6.75% EsSalud + 2.25% EPS credit; tope crédito = 10 RMV × nro trabajadores cubiertos | backend | regulatory | P0 | D.4 | 53 | 2h | N07-19,20,21 |
| 55 | **Asignación familiar computation** — `Employee.es_padre_familia=True` AND active `FamilyMember` child ≤18 (or ≤24 in estudios superiores) → AF = 10% RMV (S/113 en 2026); verify stored `EmploymentData.asignacion_familiar` amount matches | backend | regulatory | P0 | D.4 | 43 | 2h | N08-33,34,35,36 |
| 56 | **Vacaciones récord vacacional check** — at PayrollRun open, flag employees who have completed 1 year of service + met récord (260 days for 6-day week / 210 days for 5-day week) | backend | regulatory | P0 | D.4 | 43 | 2h | N08-18,19,20 |
| 57 | **Vacaciones remuneración vacacional** — compute vacacional pay = rem. regular del mes del goce; same as monthly base salary; D.4 engine includes vacation pay line in PaySlip when vacation period overlaps the run | backend | regulatory | P1 | D.4 | 56 | 1h | N08-21 |
| 58 | **Triple remuneración vacacional (Ley 30012) flag** — detect employees who have un-taken vacation beyond +1 year; flag for RRHH review; out-of-scope for automated deduction in MVP D-A | backend | regulatory | P1 | D.4 | 56 | 1h | N08-24 |
| 59 | **`Suspension` T-Registro Tabla 21** — store suspension records (maternidad, incapacidad temporal, vacaciones, licencia, huelga) per employee per period for PLAME JORNA file; link to `time_off` models | backend | regulatory | P1 | D.4 | 18,22 | 2h | N06-19 |
| 60 | **Subsidio incapacidad temporal — employer vs EsSalud split** — days 1-20: employer pays via PaySlip; day 21+: EsSalud pays (exclude from payroll, mark as EsSalud subsidio); requires CITT document reference | backend | regulatory | P1 | D.4 | 59 | 2h | N07-15,17 |
| 61 | **Subsidio maternidad** — 98 days (49+49) / 128 days twin/disability; mark period as EsSalud subsidio; exclude from employer payroll | backend | regulatory | P1 | D.4 | 59 | 1h | N07-16 |
| 62 | **Extranjeros no domiciliados — 30% flat retention** — if employee marked `no_domiciliado` + `tipo_documento='PASAPORTE'` or CE < 183 days; skip 7 UIT deduction + progressive scale; 30% on bruto | backend | regulatory | P1 | D.4 | 44 | 2h | N09-18 |
| 63 | **Practicantes (Ley 28518) — no renta 5ta / no EsSalud / no AFP** — if `regimen_laboral='practicas'`: compute subvención only; no 5ta retention, no EsSalud, no AFP/ONP mandatory | backend | regulatory | P1 | D.4 | 43 | 1h | N09-19 |
| 64 | **Licitación AFP 2025-2027 — Profuturo enforced for new affiliates** — validate: if `codigo_cuspp` created between 01/06/2025 and 31/05/2027 → `sistema_pensiones` must be `AFP PROFUTURO`; warn if mismatched | backend | regulatory | P2 | D.4 | 51 | 1h | N07-07 |
| 65 | **SNP→SPP change irreversibility guard** — prevent changing `Employee.sistema_pensiones` from any AFP back to ONP via UI; validation error in serializer | backend | regulatory | P2 | D.4 | — | 1h | N07-12 |
| 66 | **UIT annual fixture — cannot change mid-year** — `TaxParameter` UIT rows validated: only one UIT value per fiscal year; reject creating two different UITs for same `anio` | backend | regulatory | P2 | D.4 | 19 | 30m | N09-21 |
| 67 | **Vacaciones acumuladas / reducción — nota** — system records vacation reduction agreements (up to 15 days sold); not auto-computed in PaySlip; stored as `time_off` note for RRHH | backend | regulatory | P2 | D.4 | — | 1h | N08-22,23 |
| 68 | **Data retention 4 years (Ley 27321)** — `PayrollRun` + `PaySlip` records must not be deletable by normal users; soft-delete only; RRHH can archive but not permanently destroy | backend | regulatory | P1 | D.4 | — | 1h | N08-42 |
| 69 | **SCTR flag per employee** — `EmploymentData` or `Compensation`: `aplica_sctr=False` for MVP D-A (oficinas 728); engine skips SCTR line in PaySlip if False | backend | regulatory | P1 | D.4 | 23,24 | 1h | N07-22 |
| 70 | **`PayrollRun` model + state machine** — create `apps/payroll/models/payroll_run.py`: states `borrador→procesando→generada→aprobada→cerrada→anulada`; FK to `Tenant`; period fields; `close()` method triggers T-Registro baja | backend | new | P0 | D.5 | 43 | 4h | INV § 1 MonthlyPayroll disposition |
| 71 | **`PayrollRunDetail` model** — per-employee line within `PayrollRun`; snapshot of all haberes/descuentos/neto (replaces `PayrollDetail`) | backend | new | P0 | D.5 | 70 | 3h | INV § 1 PayrollDetail disposition |
| 72 | **`PayrollRun` viewset + API endpoints** — expose CRUD + state transitions (`generar`, `calcular`, `preview`, `aprobar`, `cerrar`) at `/api/v1/payroll/runs/`; replaces legacy `/api/v1/payroll/monthly-runs/` | backend | new | P1 | D.5 | 70,71 | 4h | INV § 3 payrollService.ts endpoint list |
| 73 | **`PaymentSchedule` model (new)** — payment calendar per `PayrollRun`; scheduled vs executed dates; replaces legacy model | backend | new | P1 | D.5 | 70 | 2h | INV § 1 PaymentSchedule disposition |
| 74 | **`PaySlip` (new D.6 model)** — 1-to-1 with `PayrollRunDetail`; `archivo_pdf` + `hash_documento` + `permission_level`; replaces legacy `PaySlip` | backend | new | P0 | D.6 | 71 | 3h | INV § 1 PaySlip disposition |
| 75 | **PaySlip PDF generation** — create `apps/api/templates/boletas/boleta_pago.html`; `PaySlip.generate_pdf()` via ReportLab; reuse employee header pattern from `contratos/contrato_728.html` | backend | new | P0 | D.6 | 74 | 4h | INV § 3.4 boleta template missing |
| 76 | **PaySlip boleta content requirements** — template must show: period, employee ID, DNI, cargo, área, salary components by Tabla 22 code, descuentos (AFP/ONP/EsSalud/Renta5ta), neto a pagar; complies with D.S. 001-98-TR boleta format | backend | regulatory | P0 | D.6 | 75 | 2h | N06 § 3.16 |
| 77 | **Decide PaySlip access pattern (ADR-D.7)** — decide: (a) inherit from `DigitalDocument`, (b) parallel `PaySlipAccessLog`, or (c) adapt `can_access` to accept any object with `permission_level`; ADR must be written before D.6 coding starts | backend | new | P1 | D.6 | 74 | 1h | INV § 2 access_service |
| 78 | **PaySlip permission gate via `access_service`** — after ADR-D.7 decision: wire `check_and_log` on every boleta view/download; `permission_level=3` (personal) for employee self-access; `permission_level=5` (departamental) for RRHH | backend | new | P1 | D.6 | 77 | 2h | INV § 2 access_service; ADR-D.7 |
| 79 | **`/mis-boletas` employee portal route** — add route in `App.tsx` + `EmployeeLayout` tab; `MisBoletasPage` component shows list of boletas for authenticated employee; uses `/api/v1/payroll/payslips/my/` endpoint | frontend | new | P0 | D.6 | 74,78 | 3h | INV § 3.2 EmployeeLayout; INV § 3.3 routes |
| 80 | **`payrollService.ts` boleta methods** — add `getMyBoletas()`, `downloadBoleta(id)` to existing service; replaces legacy `list` + `downloadBoletaPdf` pointing at legacy endpoints | frontend | new | P1 | D.6 | 74,79 | 2h | INV § 3 payrollService.ts |
| 81 | **AFPnet CUSPP pre-validation** — before generating PLAME, validate all AFP employees have non-empty `Employee.codigo_cuspp`; return list of missing CUSPPs as blocking error | backend | regulatory | P1 | D.6 | — | 1h | N06-43 |
| 82 | **CTS `Compensation` computable formula** — `RemuComputable_CTS = base_salary + asig_familiar + (1/6) × ultima_gratificacion_percibida`; asymmetric: CTS includes 1/6 grati; gratificación does NOT include 1/6 of itself | backend | regulatory | P0 | D.7 | 39,43 | 3h | N08-01,02,44 |
| 83 | **CTS variable concepts averaging** — include average of horas_extras + comisiones + bonos puntualidad IF ≥3 times in semester; field `es_variable=True` + `frecuencia_minima_cts=3` on PayrollConcept | backend | regulatory | P0 | D.7 | 82,28,29 | 2h | N08-03,43 |
| 84 | **CTS exclusion list** — exclude: gratif. extraordinarias, utilidades, movilidad, refrigerio, asignaciones por eventos personales, condiciones de trabajo, canasta Navidad | backend | regulatory | P0 | D.7 | 82 | 1h | N08-04 |
| 85 | **CTS deposit scheduling** — May deposit (semestre Nov-Apr, remuneración computable at Apr-30, deadline May-15); Nov deposit (semestre May-Oct, remuneración computable at Oct-31, deadline Nov-15); use `business_days.next_business_day()` for deadline if 15th is holiday | backend | regulatory | P0 | D.7 | 82,84 | 2h | N08-05,06 |
| 86 | **CTS trunca in D.7 (non-cese context)** — if employee hired mid-semester, compute partial CTS for fractional months/days from `fecha_ingreso` to end of semester | backend | regulatory | P1 | D.7 | 82,85 | 2h | N08-01 (fórmula general) |
| 87 | **Ley 32322 (2025) nota** — document in `CtsDeposit` model as informational flag: `disponibilidad_100pct_vigente=True` until 31/12/2026; no enforcement logic needed (bank-side rule) | backend | regulatory | P1 | D.7 | 85 | 30m | N08-08 |
| 88 | **CTS deposit alert service** — alert RRHH when deadline approaching (15-May / 15-Nov); uses `business_days.is_business_day()` + `next_business_day()` for feriados peruanos | backend | new | P2 | D.7 | 85 | 1h | INV § 2 business_days (CLOSED); N08-05,06 |
| 89 | **Gratificación FP formula** — `Rem_Computable_Grati × (meses_trabajados_semestre_ene-jun ÷ 6)`; pago antes del 15-jul; base remuneración computable al cierre del período | backend | regulatory | P0 | D.8 | 43,55 | 3h | N08-09,11,12 |
| 90 | **Gratificación Navidad formula** — same formula for semestre jul-dic; pago antes del 15-dic | backend | regulatory | P0 | D.8 | 89 | 1h | N08-10,11 |
| 91 | **Bonificación Extraordinaria Ley 30334** — 9% grati for EsSalud employees; 6.75% for EPS; paid same date as grati; `afecta_renta_5ta=True`, does NOT affect AFP/ONP/EsSalud | backend | regulatory | P0 | D.8 | 89,90 | 2h | N08-13,14,15 |
| 92 | **Gratificación derecho — active-on-cutoff check** — employee must be on planilla on 15-Jul (FP) or 15-Dic (Nav); if cese before those dates → trunca only | backend | regulatory | P0 | D.8 | 89,90 | 1h | N08-16 |
| 93 | **Gratificación remuneración computable** — includes asig_familiar + promedio variables ≥3/semestre; does NOT include 1/6 gratificación anterior (asymmetry with CTS) | backend | regulatory | P1 | D.8 | 89 | 1h | N08-12,44 |
| 94 | **Gratificación `PayrollConcept` Renta 5ta** — grati SÍ afecta Renta 5ta; include gratificación proyectada in RBA Step 1; when actually paid, reconcile in December adjustment | backend | regulatory | P1 | D.8 | 30,44 | 1h | N06-27,28; N09-06 |
| 95 | **Gratificación trunca — note for D.12** — `Rem_Computable × (meses_completos ÷ 6)`; requires ≥1 complete month in semester; computed at cese; D.12 calls this from settlement engine | backend | regulatory | P2 | D.8 | 92 | 1h | N08-17 |
| 96 | **PLAME 10-file generator** — produce 10 ASCII pipe-delimited files: PLANI, JORNA, PDT, IMP, DERECH, PRACT, CUART, TERCE, EMPAL, ESTAB; all in one ZIP per period | backend | regulatory | P0 | D.9 | 70,71 | 8h | N06-01,02,03 |
| 97 | **PLAME PVS-equivalent validation** — before export: (1) field count exact, (2) type+length, (3) parametric table existence, (4) sector enablement, (5) mandatory field presence, (6) no duplicates in structures 4/5/6/9/10 | backend | regulatory | P0 | D.9 | 96 | 4h | N06-09,10 |
| 98 | **PLAME submission deadline alert** — alert RRHH of PLAME filing deadline per RUC last digit (day 11–24 of following month); configurable per-tenant | backend | regulatory | P1 | D.9 | 96 | 2h | N06-04 |
| 99 | **ONP declaración via PLAME** — ONP workers declared via PLAME monthly (no separate AFPnet file); ensure ONP employees appear in PLAME DERECH file correctly | backend | regulatory | P1 | D.9 | 96 | 1h | N07-11 |
| 100 | **PLAME admin page** — replace `ReportesRemuneracionesPage.tsx` with PLAME export trigger UI; shows period, last export status, download ZIP button | frontend | new | P2 | D.9 | 96 | 3h | INV § 3 ReportesRemuneracionesPage disposition |
| 101 | **PLAME SCTR lines** — if any employee has `aplica_sctr=True`, include 0803/0804 lines in PLAME; MVP D-A: all employees `aplica_sctr=False` so these lines are omitted | backend | regulatory | P2 | D.9 | 96,24 | 1h | N07-23 |
| 102 | **T-Registro alta auto-generation** — on `Employee` create (728 regimen): auto-create `TRegistroDeclaration(declaration_type='alta')`; deadline = first day of work (no grace period) | backend | regulatory | P0 | D.10 | 18 | 3h | N06-05,08; INV § 2 TRegistroDeclaration |
| 103 | **T-Registro baja from `PayrollRun.close()`** — iterate employees with `Termination.status='completed'` in closed period; auto-create `TRegistroDeclaration(declaration_type='baja')`; link to `Termination.baja_t_registro`; deadline = cese date | backend | regulatory | P0 | D.10 | 70,102 | 3h | N06-06,08; INV § 2 TRegistroDeclaration D.10 trigger |
| 104 | **T-Registro modificación** — when key employee data changes (salary, regime, AFP, cargo): auto-trigger `TRegistroDeclaration(declaration_type='modificacion')`; deadline = 5 days after change | backend | regulatory | P1 | D.10 | 102 | 2h | N06-07,08 |
| 105 | **T-Registro baja/alta sync with PLAME** — events that generate T-Registro declarations must also update PLAME; prevent desync between T-Reg and PLAME (alta not in PLAME = rejection) | backend | regulatory | P1 | D.10 | 102,96 | 2h | N06-44 |
| 106 | **T-Registro `pvs_errors` validation** — before `mark_validated()`: run PVS-equivalent checks on `TRegistroDeclaration`; `pvs_errors` must be `[]`; expose validation endpoint at `/api/v1/payroll/t-registro/{id}/validate/` | backend | new | P2 | D.10 | 102 | 2h | INV § 2 TRegistroDeclaration pvs_errors |
| 107 | **AFPnet Excel 25-column export** — generate Excel file per AFP per period: CUSPP, tipo_doc, nro_doc, apellidos, nombres, fecha_nacimiento, sexo, relación_laboral, fechas, días laborados/subsidiados/no laborados, motivo excepción, remuneración_asegurable, aportes voluntarios, aporte empleador, tipo trabajo | backend | regulatory | P1 | D.11 | 70,71 | 4h | N07-08 |
| 108 | **AFPnet DNP vs DYP type** — system must generate both: DNP (declaración sin pago) for periods with exceptions; DYP (declaración y pago) normal; flag selectable per export | backend | regulatory | P1 | D.11 | 107 | 1h | N07-09 |
| 109 | **AFPnet CUSPP pre-validation before export** — warn if any AFP employee has `codigo_cuspp=null`; block export until all CUSPPs registered | backend | regulatory | P2 | D.11 | 107 | 1h | N06-43 |
| 110 | **AFPnet multi-AFP split** — single PayrollRun may have employees across 4 AFP funds; generate one AFPnet file per AFP (Integra, Prima, Profuturo, Habitat) | backend | regulatory | P2 | D.11 | 107 | 1h | N07-04 |
| 111 | **CTS trunca in D.12 settlement** — call `Regime728Strategy.compute_cts()` with `meses_desde_ultimo_deposito` + `dias`; D.12 replaces B.14 minimal formula (add 1/6 grati to remuneración computable) | backend | regulatory | P2 | D.12 | 82,84 | 3h | N08-07; INV § 2 SeveranceSettlement gaps |
| 112 | **Vacaciones truncas in D.12 settlement** — `Rem_Computable × (meses + dias/30) ÷ 12`; D.12 should consult actual `time_off` accrual records vs proportional formula (whichever higher) | backend | regulatory | P1 | D.12 | 56 | 2h | N08-25; INV § 2 SeveranceLine vac_truncas |
| 113 | **Gratificación trunca in D.12 settlement** — `Rem_Computable × (meses_completos ÷ 6)`; ≥1 complete month required | backend | regulatory | P1 | D.12 | 89,92 | 1h | N08-17; INV § 2 SeveranceLine grat_trunca |
| 114 | **Indemnización despido arbitrario in D.12 settlement** — `sueldo × 1.5 × (años)`, capped 12 sueldos; only for `causal='despido_arbitrario'` or `'despido_indirecto'` | backend | regulatory | P1 | D.12 | 43 | 1h | N08-41; INV § 2 SeveranceLine indemnizacion |
| 115 | **Certificado de Rentas y Retenciones** — generate annual certificate before March 1 of following year; also on-demand at cese; shows all monthly retenciones 5ta | backend | regulatory | P1 | D.12 | 48 | 2h | N09-15 |
| 116 | **Liquidación documents at cese** — D.12 generates: Hoja de Liquidación + Certificado de Trabajo (Art. 45 LPCL) + Certificado Rentas 5ta del año; `SeveranceSettlement.generate_documents()` | backend | regulatory | P1 | D.12 | 115 | 3h | N08-40 |
| 117 | **B.9 viewsets tenant consistency** — 3 onboarding viewsets (`SelectionStage`, `CandidateEvaluation`, `MeritRanking`) use custom `posting__tenant` filter instead of `TenantAwareViewSetMixin`; document as architectural inconsistency; resolve post-D or standalone cleanup sprint | backend | deuda | P2 | D.1 | — | 2h | INV § 4 open deuda |
| 118 | **Motivo cese Tabla 17 codes** — map `Termination.causal` values to SUNAT Tabla 17 codes: 01 Renuncia, 02 Despido, 03 Término contrato, 04 Fallecimiento, 08 Mutuo disenso, 11 Despido arbitrario, 12 Despido falta grave; required for T-Registro baja + PLAME | backend | regulatory | P0 | D.2 | 18 | 1h | N06-17 |
