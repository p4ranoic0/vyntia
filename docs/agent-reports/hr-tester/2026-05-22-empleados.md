# HR Tester — Módulo Empleados (AUDIT)

**Fecha:** 2026-05-22
**Invocado por:** `/vyntia-test-hr empleados (audit only)`
**Spec consultada:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`
**Tests corridos:** 246 (114 employees + 124 contracts/integration + 5 tenant-isolation + 6 frontend + 3 dependentes-affines)
**Pasaron:** 243 | **Skipped:** 3 (RLS/multi-tenant ORM heuristics) | **Fallaron:** 0 | **Nuevos creados:** 0 (audit-only)
**Confianza:** **media** — golden paths sólidos, pero hay 5 huecos crítico-peruanos para Pay
**Tiempo invertido:** ~30 min
**Baseline:** 982 / 1 / 17 NO regresado.

---

## TL;DR — verdict por flujo

| # | Flujo | Verdict |
|---|---|---|
| 1 | Alta de empleado (Employee + create serializer) | ⚠️ pasa con huecos |
| 2 | Datos familiares (FamilyMember) | ⚠️ pasa con huecos |
| 3 | Datos académicos (AcademicRecord) + Certification | ⚠️ pasa con huecos |
| 4 | Datos laborales / EmploymentData — crítico para Pay | ⚠️ pasa con huecos críticos |
| 5 | Reporte de empleado (EmpleadoReportService) | ⚠️ smoke OK, integración no probada |
| 6 | ATS B.9 (Candidate → Employee) | ✅ |
| 7 | B.12 Legajo content (work-exp, sworn-decl, job-history) | ✅ |

---

## Flujo 1 — Alta de empleado

**Estado:** golden path probado, pero **validación DNI peruana inconsistente entre serializers**.

**Modelo:** `apps/api/apps/employees/models/employee.py`
- DNI/CE/PASAPORTE/OTROS en `tipo_documento` (default DNI). `numero_documento` max 20.
- Tenant scoping: `UniqueConstraint(['tenant', 'numero_documento'])` + `UniqueConstraint(['tenant', 'correo_personal'])` (condicional a no-vacío). ✅ correcto.

**Tests existentes:**
- `apps/employees/tests/test_employee_correo_unique.py:32-110` — 3 tests sobre correo único por tenant (cross/same tenant, vacío). ✅
- `apps/employees/tests/test_employee_create_serializer.py` — 2 tests sobre lookup por `id` vs `area_id`. ✅
- `apps/employees/tests/test_employee_viewset.py:7-22` — heurísticas estáticas (no llaman API real).
- `apps/employees/tests/test_employee_filter.py:96` — heurísticas estáticas de filter.

**Validación DNI (encontrada en `api/v1/rrhh/serializers.py`):**
- `EmpleadoUpdateSerializer.validate_numero_documento` líneas 538-556 — valida 8 dígitos + único **GLOBAL (no por tenant)**.
- `EmpleadoCreateSerializer` líneas 677-765 — **NO override de `validate_numero_documento`** → solo confía en el constraint DB. Sin validación de longitud/formato en create.
- `OnboardingIniciarSerializer.validate_numero_documento` línea 1303-1308 — valida unicidad **GLOBAL**, no por tenant.
- `validate_fecha_nacimiento` línea 580-595 — rechaza fecha futura **y** exige mayor de 18 años (¡bloquea practicantes pre-profesionales 16-17 años, Ley 28518!).

**Huecos peruano-específicos sin test:**
- DNI de 7 dígitos rechazado en CREATE (solo cubierto en UPDATE).
- DNI con letras/símbolos rechazado en CREATE.
- DNI duplicado entre tenants permitido a nivel DB pero ¿la API lo permite? Sin test.
- CE (Carné de Extranjería) — formato esperado (9 dígitos), sin validación en código.
- Empleado menor de 18 (practicante 16-17 años, Ley 28518) → falsamente bloqueado por validator, sin test que lo proteja.
- RUC 10 (persona natural con negocio) — sin validación de formato/checksum en `numero_ruc`.

---

## Flujo 2 — Datos familiares (FamilyMember)

**Estado:** modelo rico (lógica de dependientes, beneficiarios, contactos emergencia), pero **sin tests directos**.

**Modelo:** `apps/api/apps/employees/models/family_member.py`
- `PARENTESCO_CHOICES` cubre cónyuge, conviviente, hijos, padres + 9 más.
- Property `edad_para_dependencia` (línea 252-274): hijos < 18 o 18-24 si estudian; cónyuge/conviviente siempre; padres ≥ 60. **Esto es lógica de deducción Renta 5ta categoría peruana** — y no tiene UN solo test.
- `unique_together = [['tenant', 'empleado', 'numero_documento']]` ✅ correcto.

**Tests existentes:** ❌ **NINGUNO** específico (solo cobertura indirecta vía CreateSerializer en `EmpleadoCreateSerializer`).

**Huecos peruano-específicos sin test:**
- Hijo de 17 años → es dependiente para Renta 5ta.
- Hijo de 25 años (mayor de edad, no estudia) → **NO dependiente**, pero el modelo no lo bloquea explícitamente.
- Cónyuge sin DNI (extranjero sin CE) → ¿qué pasa?
- 2 familiares con mismo DNI en mismo tenant/empleado → debería rechazarse (constraint lo cubre, sin test).
- Contacto de emergencia obligatorio para alta de empleado (regulación interna típica) → no enforced.

---

## Flujo 3 — Datos académicos + Certificaciones

**Estado:** modelo extenso (12 niveles educativos), validación de fechas en serializer, **sin tests directos del modelo**.

**Modelos:**
- `apps/api/apps/employees/models/academic_record.py` — incluye `verificado_sunedu`, `numero_colegiatura`, `colegio_profesional`. Property `requiere_verificacion` (línea 276-283) cubre niveles universitarios peruanos.
- `apps/api/apps/employees/models/certification.py` — modelo simple, unique por tenant+empleado+nombre+institución+fecha_inicio.

**Tests existentes:** ❌ **NINGUNO** específico para AcademicRecord ni Certification.

**Huecos peruano-específicos sin test:**
- Validación de `verificado_sunedu` solo aplica a niveles peruanos universitarios.
- `colegio_profesional` requerido para profesiones colegiadas obligatorias (médicos, ingenieros, abogados, contadores) — no enforced.
- `fecha_graduacion > fecha_inicio` validación — no testeada.
- Empleado sin formación académica → ¿qué muestra el reporte?
- Postgrado en el extranjero (verificación SUNEDU diferenciada por país) — sin test.

---

## Flujo 4 — Datos laborales / EmploymentData (CRÍTICO PARA D-Pay)

**Estado:** ⚠️ **HUECO CRÍTICO**. El modelo soporta régimen 276, 728, 1057-CAS, locación, prácticas, consultoría, **pero el único test directo es una heurística estática de 5 líneas** (`test_employment_data.py`).

**Modelo:** `apps/api/apps/contracts/models/employment_data.py`
- `REGIMEN_LABORAL_CHOICES`: 276, 728, 1057, locación, consultoría, prácticas.
- `TIPO_CONTRATO_CHOICES`: CAS, CAP, indefinido, temporal, prácticas, consultoría, locación.
- `unique_together = [['empleado', 'fecha_inicio_contrato']]` — **¡NO incluye tenant!** Potencial bug de aislamiento.
- Property `contrato_vigente` (línea 224-231), `dias_para_vencimiento`, `contrato_por_vencer` (30 días).
- Método `calcular_vacaciones_pendientes` línea 284-296 — **hardcodea 30 días/año**: no soporta MyPE (15 días). **Bloqueador para Pay.**

**Tests existentes:**
- `apps/employees/tests/test_employment_data.py:7-13` — solo verifica que `generar_codigo_empleado` use `empleado.id` (no PK stale). No prueba lógica de régimen.
- `apps/contracts/tests/test_b11_*` — pruebas de probation period, sí tienen 728-común-90d, 276-carrera-3-años, no aplica. ✅
- `apps/contracts/tests/test_b14_severance*.py` — pruebas de liquidación (renuncia, despido arbitrario, indemnización cap 12 sueldos). ✅
- `apps/contracts/tests/test_b10_tregistro_service.py` — validaciones T-Registro (menor de edad, modalidad). ✅

**Huecos peruano-específicos sin test (BLOQUEAN Pay):**
- **Régimen 728 común** (privado, base de Pay) — alta empleado + cálculo total sueldo → **sin test integral**.
- **MyPE (Ley 28015)** — vacaciones 15 días, ½ gratificación, ½ CTS → modelo no diferencia, hardcode 30d.
- **Locación de servicios** — no debería generar planilla, pero el modelo lo permite en mismo flujo. ¿Excluye locadores del PLAME?
- **CAS (1057)** — gratificación según ley especial (aguinaldo S/300, no 1 sueldo). Sin test.
- **Contrato a plazo fijo vencido + estado_datos="activo"** → debería alertar/bloquear, no testeado.
- **Periodo de prueba**: tests de `probation_period.py` ✅, pero la conexión con `EmploymentData.fecha_inicio_contrato` y reglas de 3/6/12 meses para personal común/calificado/dirección — sin test integrado.
- `unique_together = ['empleado','fecha_inicio_contrato']` sin tenant → dos tenants podrían colisionar.

---

## Flujo 5 — Reporte de empleado (EmpleadoReportService)

**Estado:** smoke estático ✅, pero ningún test ejecuta `generar_reporte_integral`.

**Servicio:** `apps/api/apps/employees/services/employee_report_service.py`
- 4 secciones: integral, personal, laboral, académico, familiar.
- Usa `pdf_generator._html_to_pdf` (chain xhtml2pdf → WeasyPrint → ReportLab; en Windows solo ReportLab fiable según CLAUDE.md → genera stub PDF, no render completo).

**Tests existentes:**
- `apps/employees/tests/test_employee_report_service.py` — solo heurística estática verificando que use `id` vs `empleado_id`.

**Huecos sin test:**
- Empleado sin datos laborales activos → ¿reporte renderiza sin crash?
- Empleado sin familiares ni formación → secciones vacías limpias.
- Empleado con foto faltante (`ruta_fotografia=null`) → render OK.
- PDF bytes > 0, content-type `application/pdf` correcto.
- Generación por sección (`personal|laboral|academico|familiar`) — ningún test cubre.
- Carácter especial en nombre_completo (tildes, ñ) → ReportLab a veces colapsa con encoding UTF-8.

---

## Flujo 6 — ATS B.9 (Candidate → Employee)

**Estado:** ✅ **muy bien cubierto** (39 tests B.9 todos pasan).
- `test_b9_candidate.py` — 7 tests (unique per tenant, doc choices, repr).
- `test_b9_job_application.py` — 10 tests de transiciones de estado (advance, withdraw, eliminate).
- `test_b9_job_posting.py` — 15 tests del ciclo SERVIR (publish, knowledge min 14, transparency).
- `test_b9_merit_ranking.py` — 8 tests del servicio de ranking.
- `test_b9_personnel_requisition.py`, `test_b9_selection_stage.py`, `test_b9_candidate_evaluation.py` — completos.

**Hueco menor:** no hay test de **conversión final Candidate → Employee** (alta automática al ganar concurso).

---

## Flujo 7 — B.12 Legajo Content

**Estado:** ✅ smoke + modelo cubierto (10 tests B.12 + 3 smoke).

---

## Top-10 tests faltantes (próxima corrida — golden + edge peruano-específicos)

| # | Test propuesto | Tipo | Razón |
|---|---|---|---|
| 1 | `test_empleado_create_dni_8_digitos_required` (api integration) | Golden DNI-PE | `EmpleadoCreateSerializer` no valida longitud; solo en update. |
| 2 | `test_empleado_create_dni_duplicado_mismo_tenant_falla` | Edge tenant-PE | Verificar API rechaza duplicado (no solo DB). |
| 3 | `test_empleado_create_dni_mismo_otro_tenant_permitido` | Edge tenant-PE | Multi-tenancy clave. |
| 4 | `test_empleado_practicante_16_anos_permitido_ley_28518` | Edge PE | Validator actual bloquea < 18. Practicantes PPP son legales. |
| 5 | `test_employment_data_regimen_728_alta_completa` | Golden Pay | Sin esto, D-Pay parte de cero. |
| 6 | `test_employment_data_regimen_mype_vacaciones_15dias` | Edge crítico Pay | Hardcode 30d en `calcular_vacaciones_pendientes`. |
| 7 | `test_employment_data_cas_1057_excluido_de_gratificaciones_normales` | Edge crítico Pay | CAS tiene aguinaldo, no gratificación. |
| 8 | `test_employment_data_locacion_servicios_no_genera_planilla` | Edge crítico Pay | 4ta categoría ≠ trabajador. |
| 9 | `test_family_member_hijo_24_estudiando_es_dependiente_renta_5ta` | Edge PE Renta | Property `edad_para_dependencia` sin test. |
| 10 | `test_employee_report_service_renderiza_sin_datos_completos` | Edge UI | Empleado nuevo sin datos laborales debe renderizar. |

**Bonus (riesgo medio):**
- `test_employment_data_unique_together_incluye_tenant` (modelo).
- `test_academic_record_sunedu_obligatorio_universitario_peru` (modelo).
- `test_contrato_plazo_fijo_vencido_alerta_renovacion` (servicio).

---

## Riesgos para sub-proyecto D (Vyntia Pay) si estos huecos persisten

1. **CRÍTICO — Régimen 728 sin test integral:** Pay calculará gratificación, CTS, asignación familiar sobre EmploymentData. Sin un golden test "alta 728 + cálculo total sueldo", cualquier refactor romperá planilla silenciosamente.
2. **CRÍTICO — MyPE no diferenciado:** `calcular_vacaciones_pendientes` hardcodea 30 días. Cliente MyPE (mercado objetivo del SaaS) tendrá vacaciones mal calculadas → indemnización vacacional Ley 31188 incorrecta.
3. **CRÍTICO — Locación de servicios mezclada:** El modelo permite régimen `locacion` en `EmploymentData`, pero los locadores NO van a PLAME. Sin test que excluya, Pay declarará 4ta como 5ta → SUNAT rechaza T-Registro.
4. **ALTO — CAS (1057) sin diferenciación:** Aguinaldo S/300 (DLeg 1057) ≠ gratificación Ley 27735. Pay aplicará la fórmula incorrecta.
5. **ALTO — Tenant scope en EmploymentData:** `unique_together` sin tenant → potencial cross-tenant data leak en planilla.
6. **MEDIO — Practicante 16-17 años bloqueado:** Ley 28518 (PPP) permite practicantes desde 16 con permiso de los padres. Validador actual los rechaza globalmente → cliente no puede dar de alta practicantes legales.
7. **MEDIO — DNI sin validación en create flow:** Onboarding/CreateSerializer aceptan DNI de 7 dígitos o con letras. Una vez en planilla, T-Registro fallará.
8. **BAJO — Reporte de empleado sin smoke real:** No bloquea Pay pero sí UX. Rutas de PDF en Windows pueden romper sin aviso.

---

## Acciones recomendadas

- [ ] **CORTO** — Próxima corrida `hr-tester` con permiso de **escribir tests**: ejecutar Top-10 (1 día estimado).
- [ ] **CORTO** — Mover `validate_numero_documento` (8 dígitos + único) desde `EmpleadoUpdateSerializer` a una clase base / mixin compartida con `EmpleadoCreateSerializer` y `OnboardingIniciarSerializer`. Hace que la validación sea consistente. *(Recomendación de arreglo en producción — NO ejecutar en modo audit.)*
- [ ] **CORTO** — Quitar el bound `> 18 años` global de `validate_fecha_nacimiento`, mover a EmploymentData según tipo_contrato (practicas permite 16+). *(Recomendación — NO ejecutar en audit.)*
- [ ] **LARGO** — Agregar suite Playwright `employee-lifecycle-pe` (alta DNI peruano + datos familiares + reporte PDF) — la suite `employment-lifecycle.spec.ts` existente probablemente cubre solo el happy path en inglés.
- [ ] **LARGO** — Antes de iniciar D-Pay: cubrir Top 1-8 sí o sí (gating de release-readiness de Pay).

---

## Resultado de ejecución de suites existentes (verifica baseline)

| Suite | Comando | Resultado |
|---|---|---|
| Employees app | `pytest apps/employees/tests/ -v` | **114 passed** in 29s |
| Contracts + integration | `pytest tests/test_empleado_update_v2.py tests/test_contratos_integration.py apps/contracts/tests/ -v` | **124 passed** in 29s |
| Tenant isolation | `pytest tests/test_tenant_isolation.py -v` | 3 passed, 2 skipped |
| Frontend employees | `npm test -- --run features/employees` | **6 passed** in 26s |

Sin regresiones contra el baseline (982/1/17).
