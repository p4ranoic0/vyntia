# Sub-project D — Vyntia Pay — Design Spec

**Status:** approved (brainstorm 2026-05-23) · ready for `superpowers:writing-plans`
**Branch convention:** `vyntia/D<N>-<short-name>` merged with `--no-ff`
**Commit prefix:** `feat(payroll):` or `feat(D-pay):` per sub-fase
**Target tag at close-out:** `d-vyntia-pay-complete`
**Prerequisite tag:** `b-vyntia-core-complete` (2026-05-19) ✓
**Spec drivers:**
- `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` (Foundation A constraints)
- `docs/superpowers/summaries/2026-05-19-vyntia-B-vyntia-core-summary.md` (B constraints D inherits)
- `docs/modulos/04_gestion_compensacion.md` (Módulo 04 product vision)
- `docs/normativa/N06-N09` (regulatory ground truth)
- `docs/agent-reports/pm/2026-05-23-empleados-v5.md` (empleados sealed-for-D)

---

## 0. Executive summary

D-Pay ships a Peruvian régimen 728 payroll engine that lets a Starter-tier tenant (1-50 employees, 1 régimen, 1-2 sedes) run a full monthly close: compute gross+deductions+employer contributions, CTS semestral deposits, gratificaciones FP/Navidad, severance settlement on cese (within 48h legal SLA), and export validated PLAME/T-Registro/AFPnet files for manual upload to the regulator. The employee sees their boleta on `/mis-boletas`.

D-Pay is the smallest viable scope to **unlock Starter tier sales** (per `docs/ROADMAP_SUBPROJECTS.md`). All non-728 régimes, full SUNAT/AFPnet API submission, digital signature PKI, event-sourced replay, and accounting integration are explicit deferrals to post-D sub-projects.

Architecture leans on Strategy Pattern + date-versioned `RegimenConfig` so future régimes (CAS, MYPE, SERVIR, etc.) plug in as new strategy classes without engine refactor. Persistence is CRUD with `audit_lite` event payloads shaped for forward-compatibility with event sourcing if it ever becomes justified.

15 sub-fases (D.0 audit → D.14 close-out), estimated 3-4 calendar weeks. 4 phases require regulatory sign-off (D.4 engine, D.7 CTS, D.8 grati, D.12 liquidación) gated by user (compensation analyst + ex-jefe RRHH) acting as external advisor.

---

## 1. Decisions log

Nine binding decisions made in brainstorming. Each frames a specific scope or architecture choice.

| ID | Decision | Why this and not alternatives |
|---|---|---|
| **D-A** | **Régimen 728 only en MVP.** Strategy Pattern + `RegimenConfig` versionado (`valid_from`/`valid_to`) listo para inyectar otros regímenes/cambios legales sin refactor. | 728 cubre ~80% del mercado privado peruano. Multi-régimen from day 1 infla scope 2-3×. Strategy Pattern lo hace extensible sin parent rewrite. Normativa cambia (Ley 32322 CTS 100% disponibilidad) → versioning explícito mandatorio. |
| **D-B** | **Sub-módulos:** IN 04.1+04.2+04.3+04.4+04.6+04.7. IN-light 04.5 (PDF sin PKI). OUT 04.8 (CSV bruto). OUT-parcial 04.9 (REOPENED manual, sin replay). | 04.7 liquidación es non-negotiable (B.14 dejó minimum legal; sin completar, cese rompe SLA 48h). 04.8 provisiones es un sub-proyecto contable propio. 04.9 replay automático justifica Event Sourcing full — diferido. |
| **D-C** | **Persistencia: CRUD tradicional + `audit_lite` (B.1 canonical)** con shape payload ES-compatible (`event_type` / `payload_json` / `schema_version`). | Event Sourcing full agrega ~3 fases (event store, projections, snapshot scheduling) sin payoff en MVP. ADR-B.2 ya canonicalizó audit_lite — ES contradice contrato B. Shape ES-compat preserva forward path. |
| **D-D** | **Integración SUNAT/AFP: file-only** (PLAME ZIP + AFPnet XLSX + T-Reg .txt) + validador interno PVS-like. Operador descarga + sube manual a portal. `PayrollRun.plame_operation_number` campo manual para acuse. | B.10 ya estableció el patrón. Submission real exige cert PKI per tenant, OAuth SUNAT, retry/idempotencia — sub-proyecto propio post-D. Cliente Starter ya hace upload manual hoy. |
| **D-E** | **Catálogo regulatorio híbrido vendor+tenant.** `TaxParameter` y `RegimenConfig` vendor-managed sin tenant FK (versioned). `PayrollConcept` Tabla 22 oficial vendor-seeded (`tenant=NULL`); custom de tenant con `parent_concept FK` al oficial (hereda flags). | Maestro § 2.2 explícito: conceptos custom mapean a códigos Tabla 22 oficiales. Permitir tenant editar UIT = facilitar evasión. Tenant custom para bonos internos sí es legítimo. |
| **D-F** | **Boleta empleado en `/mis-boletas`** reusando `EmployeeLayout` existente. No construir portal nuevo. | `EmployeeLayout` + rutas `/empleados/datos-personales` etc. ya existen; discriminadas por `user.tipo_usuario === 'empleado'`. Solo agrega 1 ruta + 1 página. |
| **D-G** | **Decomposición: 15 sub-fases pattern-A** (audit-first + polish + per-feature). D.0 audit + D.1 polish + D.2-D.13 features + D.14 close-out + Playwright lifecycle. | Replica B pattern (132 items audit B.0 catched bugs antes de codificar). Sub-fases pequeñas (1-3 días) = recovery rápido. Macro-fases (alternativa B) = scope opaco; vertical slices (alternativa C) = sin cliente piloto activo. |
| **D-H** | **Validación: 4 tiers.** Tier 1 pytest unit (golden fixtures con citas SUNAT). Tier 2 pytest integration (lifecycle + API + tenant isolation). Tier 3 Playwright opt-in (release gate D.14). Tier 4 NUEVO: sign-off regulatorio humano por fase D.4/D.7/D.8/D.12 (user en rol asesor externo). | Validación regulatoria pura via cartilla es falsa defensa legal. Contador externo es bloqueante. User es analista de compensaciones + ex-jefe RRHH = capacidad técnica + responsabilidad explícita. Sign-off gated en `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md`. |
| **D-I** | **Legacy payroll: Greenfield.** D.1 polish dropea los 9 modelos + 2 services + 2 migrations del `apps.payroll/` legacy. D.0 audit confirma cero-consumo antes de borrar. | Legacy es skeleton del intranet sin consumers productivos. Refactor in-place fuerza naming bilingüe + asunciones legacy chocan con D-A..D-E. Strangler fig agrega dual-maintenance sin valor. |

---

## 2. Overview & goals

### 2.1 Qué entrega D-Pay

Motor de planilla peruano régimen 728 listo para sellar Starter tier:

- Empleador 1-50 trabajadores, 1 régimen (728), 1-2 sedes
- Procesa remuneraciones mensuales: ingresos (básico, asig familiar, horas extras desde input, bonos), descuentos (AFP/ONP, Renta 5ta progresiva), aportes empleador (EsSalud)
- Calcula CTS semestral (mayo y noviembre) con remuneración computable correcta (Art. 1.4 N08)
- Calcula gratificaciones FP/Navidad + Bonificación Extraordinaria Ley 30334
- Liquidación al cese dentro del SLA 48h legal (extiende B.14 SeveranceSettlement con fórmulas reales)
- Exporta PLAME (10 archivos + ZIP), AFPnet (XLSX 25 columnas por AFP), T-Registro deltas (altas/bajas/modif) validados internamente
- Empleado entra a `/mis-boletas` y descarga su boleta PDF

### 2.2 Qué NO entrega D-Pay

- Otros regímenes (CAS, 276, SERVIR, MYPE, Agrario, Construcción, Minero, etc.) — arquitectura lista, implementación en sub-fases post-D
- Submission real SUNAT/AFPnet — operador descarga + sube manual
- Firma digital PKI de boletas — reusa B.10 `DocumentSignature` canvas/typed si caller integra
- Provisiones contables automáticas — solo CSV bruto en D.13
- Reliquidaciones con replay automático — REOPENED manual + audit log en D.13
- Asientos contables, integración bancaria, SBS API auto-tasas, EsSalud CITT electrónico

### 2.3 Goal criteria (releasable as "Starter ready")

1. Cliente piloto procesa cierre mensual completo sin Excel paralelo
2. Archivo PLAME pasa PVS SUNAT al primer intento (KPI maestro §9: >99%)
3. Boleta del cliente coincide al céntimo con cálculo de Sentinel/Buk en 30 escenarios golden
4. Cese genera liquidación dentro del SLA 48h legal
5. Empleado descarga su boleta sin pasar por RRHH

### 2.4 Tag final

`d-vyntia-pay-complete` al cerrar D.14. Bloqueado si alguna fase regulatoria (D.4/D.7/D.8/D.12) queda con `regulatory_audit: pending`.

---

## 3. Architecture

### 3.1 Patrón general

Strategy Pattern para regímenes + parámetros versionados por fecha + audit_lite con shape ES-compatible + CRUD tenant-scoped (patrón B canonical).

### 3.2 Diagrama de bloques

```
┌──────────────────────────── apps.payroll (greenfield) ────────────────────────────┐
│                                                                                     │
│  Capa Catálogo (vendor-managed, global, sin tenant FK)                              │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │  TaxParameter      (UIT, RMV, asig_fam, tasas AFP, prima SISCO, RMA, …)  │    │
│  │  PayrollConcept    (Tabla 22 SUNAT oficial + tenant custom mapped)       │    │
│  │  RegimenConfig     (728: vacaciones=30d, asig_fam_aplica=True, …)        │    │
│  │       ↑ todas con valid_from/valid_to                                    │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                ↓ leídos por                                          │
│  Capa Strategy                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │  RegimenStrategy (ABC) ──> Regime728Strategy(impl)                       │    │
│  │     .compute_payslip(employee, period) → PaySlipSnapshot                 │    │
│  │     .compute_cts(employee, semester) → CtsResult                         │    │
│  │     .compute_gratification(employee, semester) → GratiResult             │    │
│  │     .compute_severance(employee, termination_date, cause) → SettleResult │    │
│  │     .compute_renta_5ta(employee, period, accumulated) → Decimal          │    │
│  │  RegimenStrategyFactory.get(regimen_code, as_of_date)                    │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                ↓ orquestada por                                      │
│  Capa Domain (tenant-scoped, TenantAwareViewSetMixin)                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │  Compensation        (employee_id FK, valid_from, salario, AFP/ONP,      │    │
│  │                       has_asig_familiar, CCI, banco) — versionado        │    │
│  │  PayrollRun          (tenant, period_year/month, status DRAFT→…→CLOSED,  │    │
│  │                       snapshot al cierre)                                 │    │
│  │  PaySlip             (run_id FK, employee_id, totals, concepts JSON,     │    │
│  │                       audit_event_id) + permission_level (B.12 reuse)    │    │
│  │  PayrollLine         (slip_id, concept_id, amount, source/formula_ref)   │    │
│  │  CtsDeposit          (employee, semester, amount, deposit_date, bank)    │    │
│  │  Gratification       (employee, period FP/Navidad, amount, paid_date)    │    │
│  │  PayrollAdjustment   (run_id FK, employee_id, concept, amount, reason)   │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
│                                ↓ exportada por                                       │
│  Capa Export (file-only)                                                             │
│  ┌──────────────────────────────────────────────────────────────────────────┐    │
│  │  PlameExporter       → 10 .txt + .zip + PVS-internal validator           │    │
│  │  AfpnetExporter      → .xlsx 25 columnas por AFP                         │    │
│  │  TRegistroDelta      → reusa B.10 TRegistroDeclaration                   │    │
│  │  ProvisionesCsv      → CSV bruto (no formato contable específico)        │    │
│  └──────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘

                ↓ extiende ↓                          ↓ persiste ↓
┌──────────────────────────────────┐    ┌────────────────────────────────────────┐
│ apps.contracts.SeveranceSettlement│    │ apps.audit_lite.AuditEvent             │
│ ← stub minimo legal de B.14       │    │ event_type: payroll.run.calculated     │
│ ← D.12 lo recompone llamando      │    │             payroll.run.approved       │
│   Regime728Strategy.compute_      │    │             payroll.run.closed         │
│   severance() con fórmulas reales │    │             payroll.run.reopened       │
└──────────────────────────────────┘    │             payroll.slip.calculated    │
                                        │             cts.deposit.computed       │
                                        │             gratification.computed     │
                                        │ payload_json: snapshot completo        │
                                        │ schema_version: 1 (ES-compat futuro)   │
                                        └────────────────────────────────────────┘
```

### 3.3 Cross-cutting

- **FK cross-app via string lazy** (regla roadmap): `ForeignKey('employees.Employee')`, `ForeignKey('contracts.EmploymentData')`, etc.
- **Decimal precision:** `Decimal(14,4)` intermedio + `Decimal(12,2)` final (PEN céntimos). Redondeo `ROUND_HALF_UP` estándar SUNAT. Policy locked en **ADR-D.2**.
- **Business days:** consume `apps.core.business_days` (terminal-2 prep work).
- **Tenant isolation:** modelos domain usan `TenantAwareViewSetMixin` (B canonical). Catálogo (vendor-managed) es global por diseño.
- **Permission level reuse:** `PaySlip.permission_level` reusa B.12 (`apps.documents.services.access_service`). Empleado (PL3) ve solo su `net_pay/gross_income/concepts_summary`; HR (PL6) ve detalle; Contabilidad (PL9) ve CCI/audit_trail.
- **REOPENED policy:** abrir un período cerrado emite `payroll.run.reopened` con reason + actor; recálculo manual (admin re-calcula desde UI). Sin replay automático.
- **Concurrency:** `PayrollRun` con `select_for_update()` al transicionar status. Sin optimistic locking en MVP. **ADR-D.4**.

---

## 4. Data model

Convenciones implícitas (no repetidas por modelo): todos los modelos domain tienen `tenant FK` + `created_at` + `updated_at` + `created_by FK` (audit fields canonical post-L3.10.2). Catálogo NO tiene tenant FK. PKs son `UUIDField` (post-L3.10.4e). Naming inglés.

### 4.1 Capa Catálogo (vendor-managed, global)

**`TaxParameter`** — parámetros regulatorios versionados.

| Campo | Tipo | Notas |
|---|---|---|
| `code` | CharField | `UIT`, `RMV`, `ASIG_FAMILIAR`, `AFP_INTEGRA_FLUJO`, `AFP_INTEGRA_MIXTA_RMA`, `PRIMA_SISCO`, `ONP_RATE`, `ESSALUD_RATE`, `RENTA_5TA_TRAMO_1_UIT`, … |
| `value` | DecimalField(14,4) | |
| `valid_from` | DateField | |
| `valid_to` | DateField nullable | |
| `unit` | CharField | `PEN`, `RATE`, `UIT` |
| `source_law` | TextField | ej. "D.S. 218-2025-EF" |
| `metadata` | JSONField | ej. `{"tramo_min": 0, "tramo_max": 27500}` para tramos renta 5ta |

- **Unique:** `(code, valid_from)`
- **Lookup:** `TaxParameter.get(code, as_of_date)` retorna row vigente

**`PayrollConcept`** — Tabla 22 SUNAT + custom de tenant.

| Campo | Tipo | Notas |
|---|---|---|
| `code` | CharField | código interno — `BASIC_SALARY`, `OVERTIME_25`, custom `BONO_PRODUCTIVIDAD_Q3` |
| `sunat_code` | CharField(4) | `0101`, `0102`, etc. |
| `name` | CharField | |
| `category` | CharField | `INCOME` / `DEDUCTION` / `CONTRIBUTION_EMPLOYER` / `TAX` |
| `subcategory` | CharField | `BASIC`, `VARIABLE`, `EXTRAORDINARY`, `PENSION`, `HEALTH`, `INCOME_TAX` |
| `affects_income_tax` | BooleanField | |
| `affects_afp_onp` | BooleanField | |
| `affects_essalud` | BooleanField | |
| `affects_cts` | BooleanField | |
| `affects_gratification` | BooleanField | |
| `formula_code` | CharField nullable | ID de la fórmula registrada en Strategy. Conceptos manuales lo dejan nulo |
| `parent_concept` | FK self nullable | custom hereda flags de su parent oficial |
| `tenant` | FK nullable | NULL=oficial vendor; not-null=custom del tenant |
| `is_active` | BooleanField | |

- **Unique:** `(tenant, code)`
- **Constraint:** custom hereda flags de parent en `clean()` (NO permite override)

**`RegimenConfig`** — parámetros versionados POR régimen laboral.

| Campo | Tipo | Notas |
|---|---|---|
| `regimen_code` | CharField | `728`, futuro `MYPE_PEQUENA`, `CAS_1057`, etc. |
| `valid_from` | DateField | |
| `valid_to` | DateField nullable | |
| `vacation_days_annual` | IntegerField | ej. 30 para 728 |
| `applies_asignacion_familiar` | BooleanField | True para 728 con hijos <18 |
| `applies_cts` | BooleanField | |
| `applies_gratification` | BooleanField | |
| `cts_deposit_months` | JSONField | `[5, 11]` para mayo/noviembre |
| `gratification_months` | JSONField | `[7, 12]` |
| `severance_indemnization_formula` | CharField | `1_5_SALARIES_PER_YEAR_CAPPED_12` |
| `essalud_rate_override` | DecimalField nullable | null=usar `TaxParameter.ESSALUD_RATE` |
| `policy_notes` | TextField | citas normativas |

- **Unique:** `(regimen_code, valid_from)`
- **Lookup:** `RegimenConfig.get(regimen, as_of_date)`

### 4.2 Capa Domain (tenant-scoped)

**`Compensation`** — estructura salarial vigente del empleado. Versionada.

| Campo | Tipo | Notas |
|---|---|---|
| `employee` | FK 'employees.Employee' | string lazy |
| `valid_from` | DateField | |
| `valid_to` | DateField nullable | |
| `base_salary` | DecimalField(12,2) | |
| `has_family_allowance` | BooleanField | |
| `regimen_laboral` | CharField | `728`, etc. — copy del EmploymentData al crear, NO FK por lifecycle |
| `pension_regime` | CharField | `AFP_INTEGRA`, `AFP_PRIMA`, `AFP_HABITAT`, `AFP_PROFUTURO`, `ONP` |
| `afp_commission_type` | CharField nullable | `FLUJO`, `MIXTA`, `SALDO`. Null si ONP |
| `cuspp` | CharField(12) nullable | Código Único Sistema Pensiones |
| `health_regime` | CharField | `ESSALUD`, `EPS` |
| `eps_provider` | CharField nullable | placeholder libre por ahora; modelo formal post-D |
| `cci` | CharField(20) | PL9 |
| `bank_code` | CharField | |
| `bank_account` | CharField | PL9 |
| `permission_level` | IntegerField default 6 | HR ve; empleado no ve su CCI |

- **Unique:** `(employee, valid_from)`
- **Lookup:** `Compensation.current_for(employee, as_of_date)`

**`PayrollRun`** — corrida de planilla mensual.

| Campo | Tipo | Notas |
|---|---|---|
| `period_year` | IntegerField | |
| `period_month` | IntegerField | 1-12 |
| `period_type` | CharField | `REGULAR`, `CTS_DEPOSIT_MAY`, `CTS_DEPOSIT_NOV`, `GRATIFICATION_FP`, `GRATIFICATION_NAV`, `LIQUIDATION` |
| `status` | CharField | `DRAFT` → `CALCULATED` → `APPROVED` → `CLOSED` ⇄ `REOPENED` |
| `closed_at` | DateTimeField nullable | |
| `closed_by` | FK identity.User nullable | |
| `reopened_at` | DateTimeField nullable | |
| `reopened_reason` | TextField nullable | |
| `plame_operation_number` | CharField nullable | operador pega manualmente acuse SUNAT |
| `total_gross` | DecimalField(14,2) | denormalizado al CALCULATED |
| `total_net` | DecimalField(14,2) | |
| `total_employer_contributions` | DecimalField(14,2) | |

- **Unique:** `(tenant, period_year, period_month, period_type)`

**`PaySlip`** — boleta individual.

| Campo | Tipo | Notas |
|---|---|---|
| `payroll_run` | FK PayrollRun | |
| `employee` | FK 'employees.Employee' | string lazy |
| `compensation` | FK Compensation | snapshot del vigente al CALCULATED |
| `days_worked` | IntegerField | |
| `days_subsidized` | IntegerField | ej. CITT EsSalud |
| `days_absent` | IntegerField | |
| `gross_income` | DecimalField(12,2) | |
| `total_deductions` | DecimalField(12,2) | |
| `total_employer_contributions` | DecimalField(12,2) | informativo |
| `net_pay` | DecimalField(12,2) | |
| `concepts_snapshot` | JSONField | array de `{concept_code, sunat_code, amount, formula_ref, base}` |
| `permission_level` | IntegerField default 6 | empleado dueño tiene PL3 override en service |
| `delivered_at` | DateTimeField nullable | cuando se publica al portal `/mis-boletas` |
| `audit_event` | FK audit_lite.AuditEvent nullable | snapshot inmutable |

- **Unique:** `(payroll_run, employee)`

**`PayrollLine`** — línea individual del PaySlip (concept × amount).

| Campo | Tipo | Notas |
|---|---|---|
| `payslip` | FK PaySlip | |
| `concept` | FK PayrollConcept | |
| `amount` | DecimalField(12,2) | |
| `base_amount` | DecimalField(12,2) nullable | base sobre la que se calculó |
| `source` | CharField | `BASE` / `CALCULATED` / `MANUAL_ADJUSTMENT` / `IMPORTED` |
| `formula_ref` | CharField nullable | ID de la fórmula del Strategy, para trazabilidad |

- **Unique:** `(payslip, concept)`

**`CtsDeposit`** — depósito CTS semestral.

| Campo | Tipo | Notas |
|---|---|---|
| `employee` | FK 'employees.Employee' | string lazy |
| `semester` | CharField | `2026-H1` para nov2025-abr2026; `2026-H2` para may-oct2026 |
| `period_start` | DateField | |
| `period_end` | DateField | |
| `computable_remuneration` | DecimalField(12,2) | |
| `amount` | DecimalField(12,2) | |
| `bank_account` | CharField | PL9; copy de Compensation al cómputo |
| `deposit_due_date` | DateField | 15 mayo / 15 noviembre, ajustado a día hábil |
| `deposit_paid_date` | DateField nullable | |
| `is_truncated` | BooleanField | true si trunca al cese |
| `audit_event` | FK audit_lite.AuditEvent nullable | |

- **Unique:** `(employee, semester)`

**`Gratification`** — gratificación FP/Navidad.

| Campo | Tipo | Notas |
|---|---|---|
| `employee` | FK 'employees.Employee' | string lazy |
| `period_year` | IntegerField | |
| `period_type` | CharField | `FIESTAS_PATRIAS`, `NAVIDAD` |
| `computable_remuneration` | DecimalField(12,2) | |
| `months_worked` | IntegerField | 1-6 |
| `gross_amount` | DecimalField(12,2) | |
| `bonification_extra` | DecimalField(12,2) | 9% EsSalud / 6.75% EPS Ley 30334 |
| `paid_date` | DateField nullable | debe ser ≤ 15 jul / ≤ 15 dic |
| `is_truncated` | BooleanField | true si trunca al cese |
| `audit_event` | FK audit_lite.AuditEvent nullable | |

- **Unique:** `(employee, period_year, period_type)`

**`PayrollAdjustment`** — ajuste manual aplicado a un PayrollRun.

| Campo | Tipo | Notas |
|---|---|---|
| `payroll_run` | FK PayrollRun | |
| `employee` | FK 'employees.Employee' | string lazy |
| `concept` | FK PayrollConcept | |
| `amount` | DecimalField(12,2) | puede ser negativo |
| `reason` | TextField | |
| `applied_by` | FK identity.User | |
| `audit_event` | FK audit_lite.AuditEvent | |

Use case: corrige error en PaySlip individual sin recalcular toda la corrida. Aplicado solo en `CALCULATED`. Re-recalcula el PaySlip afectado al guardar.

### 4.3 Modelos reusados / extendidos

**`apps.contracts.SeveranceSettlement` + `SeveranceLine`** (existen desde B.14).
- D.12 NO crea nuevo modelo — extiende `contracts.services.severance_service.compute_settlement()` para llamar `Regime728Strategy.compute_severance()`.
- Resultado: las 4 SeveranceLine que B.14 dejó (CTS, vac_truncas, grat_trunca, indemnización) vienen calculadas con fórmulas reales 728 + ajuste Renta 5ta cese + componentes adicionales.
- ADR-B.9 ya canonical: B = minimum legal, D = full.

**`apps.contracts.TRegistroDeclaration`** (existe desde B.10).
- D.10 NO crea nuevo modelo — extiende service para que `PayrollRun.close()` detecte altas/bajas/modif del período y auto-genere `TRegistroDeclaration` correspondiente (status `draft`).

**`apps.audit_lite.AuditEvent`** (existe desde B.1).
- D persiste eventos con `event_type` prefijado `payroll.*` / `cts.*` / `gratification.*` / `severance.*`. Shape `{type, actor_id, target_type, target_id, payload_json, schema_version, timestamp}`.

### 4.4 Modelos diferidos (NO en D)

- `PayrollProvision` — solo exportador CSV bruto en D; modelo en futuro sub-proyecto contabilidad.
- `BankPaymentBatch` — post-D.
- `EpsProvider` — placeholder CharField libre por ahora; modelo formal cuando un cliente Starter use EPS.

---

## 5. Sub-fases roadmap

15 sub-fases (1 audit + 1 polish + 12 features + 1 close-out). Estimado calendario: 3-4 semanas si nada se traba en sign-off regulatorio. Camino crítico secuencial: D.0 → D.1 → D.2 → D.3 → D.4 → D.5 → D.6 → D.14 = ~14-17 días. Con paralelización post-D.5: ~10-12 días.

| # | Fase | Scope | Deps | Días | Sign-off |
|---|---|---|---|---|---|
| **D.0** | **Audit & inventory** | Inventory de `apps.payroll/` legacy (confirmar cero-consumo), BACKLOG de reglas regulatorias (~80-120 items derivados de N06-N09), 8 ADRs específicos D (ver § 5.2), `INVENTORY.md` + `BACKLOG.md` + `ROADMAP-D.md` + `ADRS.md` en `.planning/audit-D/` | — | 1-2 | — |
| **D.1** | **Polish baseline** | Drop 9 modelos legacy + 2 services + 2 migrations + 1 management command. Crear nuevo skeleton `apps.payroll/`: `models/{catalog,domain,export}.py`, `services/`, `strategies/{base,regime_728}.py` (stubs). Audit_lite payloads payroll-flavor registrados. Settings, URLs, permisos en core. | D.0 | 1 | — |
| **D.2** | **Catálogo regulatorio** | `TaxParameter` + `PayrollConcept` + `RegimenConfig` modelos + admin views (read-only). Seed via management command: `seed_payroll_catalog` (UIT/RMV/asig 2024-2027 + tramos renta 5ta + ~70 conceptos Tabla 22 + RegimenConfig 728). Tests: lookup por fecha, custom hereda flags de parent. | D.1 | 2 | — |
| **D.3** | **Compensation contract** | `Compensation` modelo versionado + admin CRUD + service `Compensation.current_for(employee, date)` + endpoint `/api/v1/payroll/compensations/`. Management command `migrate_employment_to_compensation` snapshot `EmploymentData.sueldo_basico` actual a `Compensation` inicial. Frontend: admin page "Estructura salarial" | D.2 | 2 | — |
| **D.4** | **Engine 728** ⚠️ | `Regime728Strategy.compute_payslip(employee, period)` completo: cálculo ingresos (basico, asig fam, horas extras input), descuentos (AFP/ONP, EsSalud, Renta 5ta progresiva), aportes empleador. NO persiste — solo retorna `PaySlipSnapshot` dataclass. Tests fixture-driven con ~30 escenarios cartilla SUNAT N06-N09. | D.2, D.3 | 3-4 | ⚠️ |
| **D.5** | **PayrollRun lifecycle** | `PayrollRun` modelo + state machine + service `PayrollRunService.create_run/calculate/approve/close/reopen`. `PayrollAdjustment` modelo + service. Admin UI lifecycle. Audit events emitted per transition. | D.4 | 2-3 | — |
| **D.6** | **PaySlip + portal empleado** | `PaySlip` + `PayrollLine` persistidos por `PayrollRunService.calculate`. PDF generator (template `boleta_728.html`). Endpoint `/api/v1/payroll/payslips/` con PL gate. Frontend: `/mis-boletas` (EmployeeLayout, lista + descargar) + admin tab "Boletas" en cierre. | D.5 | 2-3 | — |
| **D.7** | **CTS** ⚠️ | `CtsDeposit` modelo + `Regime728Strategy.compute_cts(employee, semester)`. Service crea registros mayo y noviembre + trunca al cese (callable desde D.12). Admin UI con due date alertas. Notas Ley 32322 (disponibilidad 100% vigente). | D.4 | 2-3 | ⚠️ |
| **D.8** | **Gratificaciones** ⚠️ | `Gratification` modelo + `Regime728Strategy.compute_gratification(employee, semester)` + Bonif Extra 9% EsSalud / 6.75% EPS Ley 30334. Service crea FP (jul) y Navidad (dic) + trunca al cese. Admin UI. | D.4 | 2 | ⚠️ |
| **D.9** | **PLAME exporter** | `PlameExporter.generate(payroll_run)` → 10 archivos .txt + ZIP per § 6.1 maestro. Validator interno con ~15 reglas PVS-like. Tests: archivo generado pasa validator + benchmark Sentinel/Buk. Endpoint `/api/v1/payroll/runs/{id}/plame-zip/` + UI "Descargar PLAME". | D.5 | 3 | — |
| **D.10** | **T-Registro deltas** | Service extension: `PayrollRunService.close()` detecta altas/bajas/modif del período. Auto-genera `TRegistroDeclaration` (status `draft`) reusando B.10. UI lista declaraciones pendientes per run. | D.5 + B.10 | 1-2 | — |
| **D.11** | **AFPnet exporter** | `AfpnetExporter.generate(payroll_run, afp_code)` → .xlsx 25 columnas exactas per § 6.2 maestro. Una corrida por AFP afiliada. Endpoint con dropdown AFP. | D.5 | 2 | — |
| **D.12** | **Liquidación BBSS** ⚠️ | Extiende `apps.contracts.services.severance_service.compute_settlement()` para llamar `Regime728Strategy.compute_severance(termination)`. Resultado: SeveranceSettlement con líneas reales (CTS trunca D.7, grat trunca D.8, vac truncas, indemnización 1.5 sueldos/año cap 12, Renta 5ta cese, componentes adicionales). SLA 48h workflow alert. | D.4, D.7, D.8 + B.14 | 2-3 | ⚠️ |
| **D.13** | **CSV provisiones + REOPENED + ajustes** | `ProvisionesCsvExporter` (CSV bruto). Admin UI workflow REOPENED: reabrir + audit reason + recalcular + cerrar (sin replay automático). UI `PayrollAdjustment` modal en PaySlip detail. | D.5 | 2 | — |
| **D.14** | **E2E + close-out** | Playwright lifecycle test (opt-in `RUN_DPAY_E2E=1`): tenant provision → empleado + contract + compensation → cierre mes regular → PLAME validado → cese trabajador → liquidación SLA 48h → boleta empleado visible. Docs sweep. Tag `d-vyntia-pay-complete`. | D.6-D.13 | 1-2 | — |

### 5.1 Paralelización post-D.5

Con 2-3 terminales paralelas (cuidando hazard de tree compartido — usar git worktree por terminal):
- D.7 (CTS) ∥ D.8 (Grati) — sólo deps D.4
- D.9 (PLAME) ∥ D.10 (T-Reg) ∥ D.11 (AFPnet) — sólo dep D.5
- D.13 (CSV + REOPENED) — sólo dep D.5
- D.12 (Liquidación) requiere D.7 + D.8 — sale después

### 5.2 ADRs específicos D (producir en D.0)

- **ADR-D.1** Strategy Pattern interface — método signatures + dataclass returns (`PaySlipSnapshot`, `CtsResult`, etc.)
- **ADR-D.2** Decimal precision policy — `Decimal(14,4)` intermedio + `Decimal(12,2)` final + `ROUND_HALF_UP` estándar SUNAT
- **ADR-D.3** audit_lite payload shape `payroll.*` — `schema_version: 1` + campos requeridos
- **ADR-D.4** PayrollRun concurrency — `select_for_update()` en transiciones de status
- **ADR-D.5** Renta 5ta correction al cese — algoritmo regularización (Anexo cartilla N09)
- **ADR-D.6** Tax year cutoff — diciembre 2026 usa UIT 2026, enero 2027 usa UIT 2027; ¿qué si PLAME de diciembre se genera en enero?
- **ADR-D.7** PVS validator scope — qué reglas replicamos (las 11 de B.10 + cuántas más)
- **ADR-D.8** Regulatory sign-off workflow — `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md` template + estado `regulatory_audit: pending|approved`

---

## 6. Validation strategy

Cuatro tiers. Tiers 1-3 heredan ADR-B.5 (3-tier B canonical). Tier 4 nuevo y específico de D.

### 6.1 Tier 1 — pytest unit (motor matemático)

Scope: cálculos puros del Strategy + validator interno PVS-like + invariantes de modelo.

Ubicación:

```
apps/api/apps/payroll/tests/
├── unit/
│   ├── test_regime_728_payslip.py
│   ├── test_regime_728_cts.py
│   ├── test_regime_728_gratification.py
│   ├── test_regime_728_severance.py
│   ├── test_regime_728_renta5ta.py
│   ├── test_catalog_lookup.py
│   ├── test_plame_validator.py
│   └── test_decimal_precision.py
└── golden/
    ├── cartilla_sunat/
    │   ├── n09_renta5ta_ejemplo_1.json     # cita: "N09 § 2.3 ejemplo 1"
    │   ├── n08_cts_ejemplo_1.json          # cita: "N08 § 1.8 ejemplo 1"
    │   └── ...                              # ~30 escenarios golden
    └── sentinel_benchmark/
        ├── case_01_sueldo_plano.json
        └── ...
```

Cada golden case incluye: `cita_normativa` (ej. "N08 § 1.8 ejemplo 1"), `input`, `expected_*`, opcional `sentinel_comparison`.

### 6.2 Tier 2 — pytest integration (lifecycle + API)

Scope: PayrollRun full lifecycle, API smoke per ViewSet, tenant isolation, audit_lite events, REOPENED workflow, permission_level gating.

Tests críticos por fase:
- D.5: `test_payroll_run_lifecycle.py` — DRAFT → CALCULATED → APPROVED → CLOSED → REOPENED + audit events
- D.6: `test_payslip_pl_gating.py` — empleado (PL3) vs HR (PL6) vs Contabilidad (PL9)
- D.9: `test_plame_full_pipeline.py` — PayrollRun → 10 archivos → validator pasa → ZIP descargable
- D.10: `test_tregistro_auto_deltas.py` — close PayrollRun con alta → genera TRegistroDeclaration
- D.12: `test_severance_uses_engine.py` — Termination llama severance_service → matches Regime728Strategy
- Cross-cutting: `test_tenant_isolation_payroll.py`, `test_payroll_api_smoke.py`

### 6.3 Tier 3 — Playwright lifecycle (opt-in release gate)

Gated por env `RUN_DPAY_E2E=1`. NO corre en CI default — release gate manual antes de tag.

Ubicación: `apps/web/tests/e2e/dpay-lifecycle.test.js`. Runbook: `docs/operations/run-dpay-e2e.md`.

### 6.4 Tier 4 — Regulatory sign-off (gate manual)

Aplica a fases regulatorias: **D.4, D.7, D.8, D.12**.

Workflow:
1. Pre-merge artefacto: `.planning/dpay/D<N>/REGULATORY-SIGNOFF.md` con tabla escenario × input × expected × computed × cita normativa × benchmark Sentinel opcional × match.
2. User review: revisas cálculos contra tu criterio + opcional benchmark Sentinel/Buk.
3. Outcome: `APPROVED` (escribes firma) o `CHANGES_REQUESTED` (escribes razón).
4. Tag `d-vyntia-pay-complete` bloqueado si alguna fase regulatoria queda `regulatory_audit: pending`.

ADR-D.8 formaliza este workflow.

### 6.5 Baselines a preservar

| Métrica | Pre-D | Target post-D |
|---|---|---|
| Backend pytest passing | 985 | ~1100+ |
| Backend pytest failing | 1 (pre-existing) | 1 (mismo) |
| Frontend vitest | 178/28 | ~200+/35+ |
| Frontend tsc | 1 (BlankEnum) | 1 (mismo) |
| Frontend ESLint | ≤ 278 | ≤ 290 |
| Frontend build | clean ~10s | clean |
| Playwright opt-in suites | 2 | 3 (+ dpay-lifecycle) |
| manage.py check | 0 silenced | 0 silenced |

Por sub-fase, checks que corren ANTES de merge:

```bash
cd apps/api && pytest
cd apps/web && npm run lint && npm test && npm run build && npx tsc --noEmit
```

### 6.6 Tests NO en MVP D (diferidos)

- Test régimenes cruzados — N/A (solo 728)
- Test retroactivo replay — N/A (REOPENED manual)
- Test volumen 10k boletas <60s — postergar a perf phase post-D
- Test SUNAT submission real — fuera de scope
- Test signature PKI — fuera de scope

---

## 7. Out-of-scope (deferrals)

### 7.1 Regímenes no-728

Cada uno es sub-fase futura post-D.14 (arquitectura ya lo permite sin refactor).

| Régimen | Sub-fase futura | Diferencias críticas vs 728 |
|---|---|---|
| MYPE Micro (Ley 32353) | D.15 | Sin CTS, sin grati, vacaciones 15d, sin asig familiar obligatoria |
| MYPE Pequeña | D.16 | CTS reducida (15 d/año, tope 90d), grati reducida (½ rem) |
| Construcción Civil (Ley 727 + CAPECO-FTCCP) | D.17 | Jornal diario + bonificaciones por tipo de obra (BUC, BAE) |
| Agrario SP-1 (Ley 31110) | D.18 | Remuneración diaria incluye 16.66% grati + 9.72% CTS |
| Agrario SP-2 | D.18 | Mensual con grati y CTS separadas |
| CAS (DL 1057) | D.19 | Sin CTS, grati 1 sueldo/semestre, EsSalud, sin AFP/ONP obligatoria |
| 276 Carrera Admin | D.20 | Bonificaciones MUC, sin LCT, escalas DL 276 |
| SERVIR 30057 | D.21 | Grupos FP/DP/CC, escala ServirGOB |
| Minero (DS 014-92-EM) | D.22 | Bonificación por riesgo, BUC minero |
| Hogar (Ley 31047) | D.23 | EsSalud subsidiado, CTS y grati reducidos |
| Pesquero | post-D | Régimen de nicho |
| Textil/Confecciones (Ley 29245) | post-D | Variantes promocionales |

Política: ningún régimen entra a D mientras 728 no esté regulatory-signed-off + cliente piloto activo.

### 7.2 Sub-módulos Módulo 04 diferidos

| Sub-módulo | Estado en D | Destino futuro |
|---|---|---|
| 04.5 Boletas firmadas PKI (DS 052-2008-PCM) | NO. D entrega PDF + reusa `DocumentSignature` canvas/typed de B.10 | sub-proyecto **firma-pki** |
| 04.6 Submission real SUNAT/AFPnet | NO. File-only + manual upload | sub-proyecto **integracion-sunat** |
| 04.8 Provisiones contables automáticas | NO. D entrega CSV bruto en D.13 | sub-proyecto **provisiones-contables** |
| 04.9 Replay retroactivo con event sourcing | NO. REOPENED manual en D.13 | sub-proyecto **payroll-replay** |

### 7.3 Integraciones diferidas

| Integración | Estado en D | Destino |
|---|---|---|
| SUNAT PDT PLAME submission real | file-only | post-D: **integracion-sunat** |
| SUNAT T-Registro submission real | file-only (B.10 manual) | post-D: **integracion-sunat** |
| AFPnet web scraping | file-only por AFP | post-D: **integracion-afpnet** per AFP |
| SBS API auto-tasas AFP | NO | post-D: cron job mensual |
| EsSalud CITT electrónico | NO. Campo manual `days_subsidized` | post-D: **integracion-essalud** |
| Bancos (BCP/BBVA/etc) archivos transferencia | NO | post-D: **bank-payment-batches** |
| Email envío boletas | NO. Empleado descarga del portal | post-D: sub-proyecto W **notifications** |
| Firma digital Llama.pe/Digiflow | NO | post-D: **firma-pki** |
| ZKTeco/Suprema biométricos | NO | post-D: sub-proyecto N **Asistencia** |

### 7.4 Features de plataforma diferidas

| Feature | Por qué |
|---|---|
| Cron infrastructure (cron_celery) para alertas vencimiento CTS/grati/PLAME | Ya canonical-diferido en B.16 summary. D usa endpoints manuales. |
| Sub-proyecto E - Modularidad/Plans | NO bloquea D técnicamente. Modelo comercial se enforce post-D. |
| Permissions v2 (sub-proyecto V) | D reusa B.12 permission_level (PL 3/6/9). |
| DocType Engine (sub-proyecto U) | D usa serializers DRF estándar. |
| People Analytics (sub-proyecto R) | D entrega datos brutos; analytics es R. |
| App móvil (sub-proyecto P React Native) | Boletas mobile = `/mis-boletas` responsive con Tailwind. |

### 7.5 Cosas que parecen D pero NO son D

| Item | Razón |
|---|---|
| Asistencia (módulo 08, sub-proyecto N) | Días trabajados/subsidiados llegan como input externo. D NO calcula asistencia. |
| Hora extra autorizada (workflow) | Sub-proyecto N. D solo CONSUME monto aprobado. |
| Vacaciones lifecycle (solicitud, aprobación, goce) | Existe parcial en `apps.time_off/`. D solo CONSUME `dias_vacaciones_gozados`. |
| LMS / multimedia boletas | Sub-proyecto G. |
| Performance / OKRs / 360° | Sub-proyecto H (Vyntia Pulse). |
| Reclutamiento / ATS | Sub-proyecto Q (Vyntia Hire). |
| Renta 5ta projection "what-if" | Out. D calcula la real del período. |
| Multi-idioma boletas (Quechua, Aymara) | Sub-proyecto Z (i18n). |
| DNI checksum módulo 11 | Diferido permanentemente (opcional, no regulatorio). |
| Multi-vínculo (mismo trabajador 2 contratos paralelos) | Out scope MVP. Si surge, sub-fase D.x. |

### 7.6 Prerequisitos externos a D (que D consume)

NO los entrega D pero los consume. Si no están al iniciar D.4, D.4 los integra como sub-tareas internas.

- Catálogo feriados peruanos Ley 29408 + `business_days_between` (terminal-2 en curso)
- Batch CSV import de empleados (terminal-2 en curso)
- N+1 fix `EmpleadoListSerializer` (terminal-2 en curso)
- Borrar `Employee.boletas_recientes()` stub muerto (terminal-2 en curso)

---

## 8. References

### 8.1 Specs y summaries previos

- `docs/superpowers/specs/2026-04-25-vyntia-foundation-design.md` — Foundation A
- `docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md` — Multi-tenancy C
- `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md` — Core B
- `docs/superpowers/summaries/2026-05-19-vyntia-B-vyntia-core-summary.md` — B close-out (constraints D inherits)

### 8.2 Product vision

- `docs/00_VYNTIA_MAESTRO.md` — Master product vision
- `docs/modulos/04_gestion_compensacion.md` — Módulo 04 full scope
- `docs/comercial/C01_tiers_planes_comerciales.md` — Starter tier definition

### 8.3 Regulatory ground truth

- `docs/normativa/N01_regimen_privado_728.md` — Régimen 728 base
- `docs/normativa/N06_planilla_electronica_sunat.md` — Tabla 22 + PLAME + T-Registro
- `docs/normativa/N07_aportes_pensiones_salud.md` — AFP, ONP, EsSalud, EPS
- `docs/normativa/N08_beneficios_sociales.md` — CTS, gratis, vacaciones, utilidades
- `docs/normativa/N09_renta_5ta_categoria.md` — Algoritmo Renta 5ta
- SUNAT Tablas paramétricas: https://orientacion.sunat.gob.pe/7086-12-tablas-parametricas
- SUNAT Cartilla PDT PLAME: http://contenido.app.sunat.gob.pe/insc/PLAME/CARTILLA_PDT+PLAME_12FEB2013.pdf

### 8.4 Architecture references

- `docs/arquitectura/A06_event_sourcing_payroll.md` — Event Sourcing detail (referenced for forward-compat shape)
- `docs/arquitectura/A07_strategy_regimenes.md` — Strategy Pattern detail

### 8.5 Operational

- `docs/agent-reports/pm/2026-05-23-empleados-v5.md` — Empleados sealed-for-D + deuda diferida a D.0 ADR
- `docs/operations/run-lifecycle-e2e.md` — Playwright opt-in runbook pattern (D.14 reusará)

---

## 9. Next step

Invoke `superpowers:writing-plans` to produce the master roadmap + per-phase plans (one PLAN.md per sub-fase). D.0 audit will refine the BACKLOG and produce the 8 ADRs before D.1 starts coding.
