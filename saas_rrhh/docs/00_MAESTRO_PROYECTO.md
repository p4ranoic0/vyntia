# 📘 MD MAESTRO — SaaS Modular de Gestión de Recursos Humanos para Perú

> **Versión:** 3.0 · **Fecha:** Abril 2026 · **Arquitectura base:** [github.com/p4ranoic0/INTRANET](https://github.com/p4ranoic0/INTRANET)
>
> Este documento es la **fuente única de verdad** del proyecto. Define el marco, los módulos, la estrategia comercial modular, y referencia los MDs hijos con las reglas de negocio detalladas por módulo.
>
> **Estado v3.0:** 28 MDs hijos completados y disponibles individualmente (12 módulos + 13 normativos + 8 arquitectura + 3 comercial + maestro). Proyecto listo para revisión e ingreso a fase de implementación.

---

## 0. Índice de documentos hijos

Todos los MDs hijos están **generados y disponibles**. Cada uno es una unidad independiente con reglas de negocio, entidades, flujos, ejemplos de cálculo y referencias oficiales.

### 📂 Módulos funcionales (12 documentos)
| # | Documento | Alcance | Estado |
|---|-----------|---------|:---:|
| 01 | `modulos/01_planificacion_politicas.md` | Planificación estratégica de RRHH, políticas, procedimientos | ✅ |
| 02 | `modulos/02_organizacion_trabajo.md` | Diseño y administración de puestos, MPP, CAP, CPE, CCF | ✅ |
| 03 | `modulos/03_gestion_empleo.md` | Selección, vinculación, inducción, desvinculación, legajo digital | ✅ |
| 04 | `modulos/04_gestion_compensacion.md` | Planilla multi-régimen, remuneraciones, pensiones | ✅ |
| 05 | `modulos/05_gestion_desarrollo_capacitacion.md` | Capacitación, LMS, progresión de carrera, PDI | ✅ |
| 06 | `modulos/06_gestion_rendimiento.md` | Evaluación de desempeño, OKRs, Nine-Box, 360° | ✅ |
| 07 | `modulos/07_relaciones_humanas_sociales.md` | Relaciones laborales, SST, bienestar, cultura, clima, comunicación interna | ✅ |
| 08 | `modulos/08_control_asistencia_tiempo.md` | Marcaciones, turnos, vacaciones, permisos, desplazamientos | ✅ |
| 09 | `modulos/09_procedimiento_disciplinario.md` | PID/PAD, faltas, sanciones, Tribunal del Servicio Civil | ✅ |
| 10 | `modulos/10_autoservicio_portal_empleado.md` | Portal y app móvil del colaborador | ✅ |
| 11 | `modulos/11_reclutamiento_ats.md` | ATS avanzado, concursos públicos SERVIR, multi-portal | ✅ |
| 12 | `modulos/12_analitica_people_analytics.md` | BI, dashboards, KPIs, IA predictiva, reportes regulatorios | ✅ |

### 📂 Dominios normativos transversales (13 documentos)
| # | Documento | Alcance | Estado |
|---|-----------|---------|:---:|
| N1 | `normativa/N01_regimen_privado_728.md` | D.Leg. 728 — régimen general privado | ✅ |
| N2 | `normativa/N02_regimen_cas_1057.md` | D.Leg. 1057 — Contratación Administrativa de Servicios | ✅ |
| N3 | `normativa/N03_regimen_publico_276.md` | D.Leg. 276 — Carrera Administrativa (URP, bonificaciones, MUC) | ✅ |
| N4 | `normativa/N04_regimen_servir_ley30057.md` | Ley 30057 — Régimen del Servicio Civil | ✅ |
| N5 | `normativa/N05_regimenes_especiales.md` | MYPE, Agrario 31110, Construcción, Minero, Hogar, Pesquero, Textil | ✅ |
| N6 | `normativa/N06_planilla_electronica_sunat.md` | T-Registro, PLAME, Tablas paramétricas Anexo 2 | ✅ |
| N7 | `normativa/N07_aportes_pensiones_salud.md` | AFP, ONP, EsSalud, EPS, SCTR, SENATI, SENCICO | ✅ |
| N8 | `normativa/N08_beneficios_sociales.md` | CTS, Gratificaciones, Vacaciones, Utilidades, Asignación Familiar | ✅ |
| N9 | `normativa/N09_renta_5ta_categoria.md` | Impuesto a la Renta de 5ta con escala progresiva 2026 | ✅ |
| N10 | `normativa/N10_sst_ley29783.md` | Seguridad y Salud en el Trabajo, 9 registros obligatorios | ✅ |
| N11 | `normativa/N11_proteccion_datos_personales.md` | Ley 29733 + D.S. 016-2024-JUS vigente desde 30/03/2025 | ✅ |
| N12 | `normativa/N12_ley_igualdad_salarial_30709.md` | Cuadro de Categorías y Funciones (CCF) | ✅ |
| N13 | `normativa/N13_hostigamiento_sexual_27942.md` | Canal de denuncias + Comité de Intervención | ✅ |

### 📂 Arquitectura y base técnica (8 documentos)
| # | Documento | Alcance | Estado |
|---|-----------|---------|:---:|
| A1 | `arquitectura/A01_arquitectura_general.md` | DDD, bounded contexts, stack tecnológico, integración con INTRANET | ✅ |
| A2 | `arquitectura/A02_multitenancy_rls.md` | Estrategia multi-tenant con RLS Postgres, upgrade path | ✅ |
| A3 | `arquitectura/A03_motor_workflows.md` | Motor declarativo (estados, transiciones, SLAs, actores) | ✅ |
| A4 | `arquitectura/A04_rbac_permisos.md` | RBAC + permission levels 0-9 + ABAC | ✅ |
| A5 | `arquitectura/A05_campos_personalizados.md` | Custom fields híbrido (JSONB + promoción a DDL) | ✅ |
| A6 | `arquitectura/A06_event_sourcing_payroll.md` | Event sourcing acotado al contexto Payroll + snapshots | ✅ |
| A7 | `arquitectura/A07_strategy_regimenes.md` | Strategy Pattern para los 13 regímenes peruanos | ✅ |
| A8 | `arquitectura/A08_apis_integraciones.md` | REST, GraphQL, webhooks, SUNAT/AFPnet/bancos | ✅ |

### 📂 Comercial y go-to-market (3 documentos)
| # | Documento | Alcance | Estado |
|---|-----------|---------|:---:|
| C1 | `comercial/C01_tiers_planes_comerciales.md` | Planes Starter/Pro/Enterprise/GovTech con límites y pricing | ✅ |
| C2 | `comercial/C02_paquetes_sectoriales.md` | Paquetes Minería, Construcción, Agro, Retail, Sector Público | ✅ |
| C3 | `comercial/C03_estrategia_onboarding_clientes.md` | Implementación, migración, KPIs de CS | ✅ |

**Total: 36 documentos** (1 maestro + 12 módulos + 13 normativos + 8 arquitectura + 3 comercial = 37 documentos incluyendo este maestro).

---

## 1. Visión del producto

**Nombre del proyecto (working title):** INTRANET HCM Perú

**Propósito:** SaaS modular de Gestión de Capital Humano **localizado 100% al Perú**, configurable, multitenant, escalable desde microempresas hasta grandes corporaciones y **entidades públicas** sujetas al marco SERVIR.

**Propuesta de valor diferenciada:**
1. **Cobertura normativa total desde día 1**: todos los regímenes laborales peruanos (728, CAS, 276, Servir 30057, MYPE, Agrario 31110, Construcción Civil, Minero, Hogar, Pesquero).
2. **Venta modular negociable**: el cliente compra solo los módulos que necesita, con upgrade progresivo y descuentos por bundle.
3. **Arquitectura metadata-driven** (estilo Frappe DocType): cada tenant puede extender el sistema sin fork de código.
4. **Motor de cálculo auditable**: event sourcing en planilla — recálculos retroactivos, trazabilidad absoluta, cumplimiento SUNAT/SUNAFIL.
5. **APIs abiertas de primera clase**: REST + GraphQL documentados (ventaja sobre 80% del mercado local).
6. **Módulo regional Perú nativo**: generador de archivos PLAME, T-Registro, AFPnet, sin intermediarios.

---

## 2. Dos mundos, un solo producto: privado + público

Una decisión arquitectónica crítica: **el sistema debe servir tanto al sector privado como al sector público peruano**. Esto lo diferencia de 90% del mercado y multiplica el TAM.

### 2.1 Sector privado → modelo operativo de la imagen de referencia
Usamos los procesos clásicos HR (planilla, asistencia, desempeño, cultura, etc.) adaptados a los **regímenes privados peruanos** (728, MYPE, Agrario, etc.).

### 2.2 Sector público → modelo SERVIR de 23 subsistemas
La imagen aportada por el usuario muestra el **Sistema Administrativo de Gestión de Recursos Humanos (SAGRH)** establecido por SERVIR mediante la Directiva N° 002-2014-SERVIR/GDRSH. Se organiza en **7 subsistemas** con **23 procesos**:

| Subsistema | Procesos (23 total) |
|------------|---------------------|
| **1. Planificación de Políticas** | 1. Estrategias, políticas y procedimientos · 2. Planificación de RRHH |
| **2. Organización del Trabajo** | 3. Diseño de puestos · 4. Administración de puestos |
| **3. Gestión del Empleo** | 5. Selección · 6. Vinculación · 7. Inducción · 8. Período de prueba · 9. Administración de legajos · 10. Control de asistencia · 11. Desplazamiento · 12. Procedimiento disciplinario · 13. Desvinculación |
| **4. Gestión del Rendimiento** | 14. Evaluación de desempeño |
| **5. Gestión de la Compensación** | 15. Administración de compensaciones · 16. Administración de pensiones |
| **6. Gestión del Desarrollo y Capacitación** | 17. Capacitación · 18. Progresión en la carrera |
| **7. Gestión de Relaciones Humanas y Sociales** | 19. Relaciones laborales · 20. Seguridad y salud en el trabajo · 21. Bienestar Social · 22. Cultura y clima laboral · 23. Comunicación interna |

**Referencias normativas SERVIR clave:**
- Directiva N° 002-2014-SERVIR/GDRSH — Normas para la gestión del SAGRH
- RPE N° 150-2017-SERVIR-PE — Guía de Cultura y Clima Organizacional
- RPE N° 151-2017-SERVIR-PE — Guía de Comunicación Interna
- RPE N° 265-2017-SERVIR-PE — Guía de Inducción
- RPE N° 238-2014-SERVIR-PE — aprueba Directiva 002-2014
- Ley N° 30057 — Ley del Servicio Civil
- D.Leg. N° 276 — Ley de Bases de la Carrera Administrativa
- D.Leg. N° 1057 — Régimen CAS
- Ley N° 32199 (2024) — modifica D.Leg. 276 (nuevos rangos licencia sin goce, CTS)

### 2.3 Mapeo dual: módulos del SaaS cubren ambos mundos

| Módulo SaaS | Subsistema SERVIR (público) | Aplicación privada |
|-------------|----------------------------|---------------------|
| 01 Planificación Políticas | 1, 2 | Política de RRHH corporativa |
| 02 Organización Trabajo | 3, 4 | Job descriptions, organigrama |
| 03 Gestión Empleo | 5, 6, 7, 8, 9, 13 | Onboarding, legajo, offboarding |
| 04 Gestión Compensación | 15, 16 | Planilla 728/MYPE/Agrario/etc. |
| 05 Desarrollo y Capacitación | 17, 18 | LMS + planes de carrera |
| 06 Gestión Rendimiento | 14 | Desempeño 180°/360°, OKRs |
| 07 Relaciones HH y Sociales | 19, 20, 21, 22, 23 | Sindicatos, SST, cultura, clima |
| 08 Control Asistencia | 10, 11 | Marcaciones, turnos, vacaciones |
| 09 Procedimiento Disciplinario | 12 | PAD (público) / PID (privado) |
| 10 Portal Empleado | Transversal | Autoservicio, app móvil |
| 11 Reclutamiento ATS | 5 | ATS avanzado + multiposting |
| 12 Analítica | Transversal | Dashboards, IA |

---

## 3. Catálogo maestro de módulos del SaaS

### Módulo 01 — Planificación de Políticas de RRHH
**Propósito:** soportar la definición de estrategias, políticas, directivas internas y planes de RRHH.

**Funcionalidades clave:**
- Gestor documental de políticas (versionado, aprobación, difusión)
- Plan de RRHH anual con objetivos y KPIs
- Matriz de cumplimiento normativo
- Alertas de vencimiento de directivas

**Entidades principales:** `Policy`, `PolicyVersion`, `HRPlan`, `HRPlanObjective`, `ComplianceMatrix`

**Tier comercial:** Pro (todos los sectores)

**Detalle completo:** → `modulos/01_planificacion_politicas.md`

---

### Módulo 02 — Organización del Trabajo y Distribución
**Propósito:** diseñar y administrar los puestos de trabajo, el organigrama y las estructuras.

**Funcionalidades clave:**
- Catálogo de puestos / perfiles de puesto (job description)
- Organigrama dinámico navegable
- **Cuadro de Categorías y Funciones (CCF)** → obligación Ley 30709 igualdad salarial
- Banda salarial por categoría
- **Manual de Perfiles de Puestos (MPP)** y **Cuadro de Puestos de la Entidad (CPE)** → sector público SERVIR
- Versionado histórico de estructura

**Entidades principales:** `Position`, `PositionProfile`, `OrgUnit`, `SalaryBand`, `CategoryFunctionTable`

**Tier comercial:** Starter + (obligatorio para cumplir Ley 30709)

**Detalle completo:** → `modulos/02_organizacion_trabajo.md`

---

### Módulo 03 — Gestión del Empleo
**Propósito:** gestionar el ciclo de vida del trabajador desde el ingreso hasta el cese.

**Sub-procesos:**
- **03.1 Selección** → proceso de selección con fases, criterios, evaluaciones
- **03.2 Vinculación** → generación de contrato, firma electrónica, registro en T-Registro
- **03.3 Inducción** → plan de inducción (general + específica) según RPE 265-2017-SERVIR-PE
- **03.4 Período de prueba** → seguimiento, extensión, evaluación
- **03.5 Administración de Legajos** → expediente digital completo del trabajador
- **03.6 Desplazamiento** → rotación, encargatura, destaque, comisión de servicios, permuta, designación (sector público)
- **03.7 Desvinculación** → renuncia, cese, despido, liquidación automática de beneficios sociales

**Entidades principales:** `Employee`, `Contract`, `DigitalDossier`, `OnboardingPlan`, `ProbationPeriod`, `Displacement`, `Termination`, `SeveranceSettlement`

**Tier comercial:** Starter (core HR)

**Detalle completo:** → `modulos/03_gestion_empleo.md`

---

### Módulo 04 — Gestión de la Compensación (Planilla)
**Propósito:** el núcleo de cumplimiento. Motor de cálculo multi-régimen con auditabilidad total.

**Sub-módulos:**
- **04.1 Planilla de Remuneraciones** → cálculo multi-régimen con Strategy Pattern
- **04.2 Administración de Pensiones** → AFP, ONP, pensionistas
- **04.3 Beneficios Sociales** → CTS, gratificaciones, vacaciones, utilidades
- **04.4 Retenciones y Aportes** → Renta 5ta, EsSalud, AFP, ONP, judiciales
- **04.5 Generación de Boletas Electrónicas** → firma digital
- **04.6 Exportadores Oficiales** → PLAME (.txt), T-Registro, AFPnet (.xlsx), SUNAT virtual, bancos
- **04.7 Liquidación de Beneficios Sociales** → motor automático al cese (48h)

**Regímenes soportados en el motor:**
- D.Leg. 728 (Régimen General Privado)
- D.Leg. 1057 (CAS)
- D.Leg. 276 (Carrera Administrativa — sistema URP)
- Ley 30057 (SERVIR)
- Ley 32353 (MYPE integral)
- Ley 31110 (Agrario — con dos sistemas de pago)
- Ley 727 + CAPECO (Construcción Civil)
- D.S. 014-92-EM (Minero)
- Ley 31047 (Trabajadores del Hogar)
- Régimen Pesquero / Textil

**Entidades principales:** `PayrollRun`, `PayrollConcept` (mapeado a Tabla 22 SUNAT), `SalaryStructure`, `Payslip`, `Contribution`, `Deduction`, `RegimeStrategy` (interfaz)

**Patrones aplicados:** Event Sourcing (append-only), Strategy Pattern (regímenes), CQRS (dashboards denormalizados)

**Tier comercial:** Starter (imprescindible)

**Detalle completo:** → `modulos/04_gestion_compensacion.md`

---

### Módulo 05 — Gestión del Desarrollo y Capacitación
**Propósito:** cerrar brechas de competencias y gestionar la progresión en la carrera.

**Funcionalidades clave:**
- **Diagnóstico de Necesidades de Capacitación (DNC)**
- **Plan de Desarrollo de las Personas (PDP)** → obligatorio en sector público (SERVIR)
- LMS integrado (cursos e-learning, videos, documentos, evaluaciones)
- Ruta de aprendizaje por competencia o por puesto
- Metodología **70-20-10** para PDI
- Compromisos post-capacitación (obligación de permanencia)
- **Progresión en la carrera** (ascensos por concurso — sector público)
- Certificados digitales

**Entidades principales:** `TrainingProgram`, `TrainingSession`, `Enrollment`, `LearningPath`, `DevelopmentPlan`, `CareerProgression`, `CommitmentAgreement`

**Tier comercial:** Pro

**Detalle completo:** → `modulos/05_gestion_desarrollo_capacitacion.md`

---

### Módulo 06 — Gestión del Rendimiento
**Propósito:** evaluar el desempeño de los trabajadores.

**Funcionalidades clave:**
- Ciclos de evaluación configurables (90°, 180°, 360°)
- OKRs y KPIs con seguimiento continuo
- **Matriz Nine-Box** (performance vs potencial)
- Feedback continuo (1-on-1s, check-ins)
- Evaluación obligatoria SERVIR (sector público) con formato oficial
- Planes de mejora derivados

**Entidades principales:** `EvaluationCycle`, `EvaluationForm`, `EvaluationResponse`, `Objective` (OKR), `KeyResult`, `TalentGrid`, `FeedbackEntry`

**Tier comercial:** Pro

**Detalle completo:** → `modulos/06_gestion_rendimiento.md`

---

### Módulo 07 — Gestión de Relaciones Humanas y Sociales
**Propósito:** gestionar todo lo que atañe al vínculo trabajador-organización más allá de la compensación.

**Sub-módulos (los 5 procesos SERVIR):**
- **07.1 Relaciones Laborales** → sindicatos, pliegos de reclamos, convenios colectivos, negociación
- **07.2 Seguridad y Salud en el Trabajo (SST)** → Ley 29783 completa (9 registros obligatorios, Comité SST, IPERC, mapa de riesgos, EMO, plan anual SST)
- **07.3 Bienestar Social** → plan de bienestar, convenios, actividades recreativas, culturales, deportivas
- **07.4 Cultura y Clima Organizacional** → encuestas de clima (con dimensiones SERVIR), eNPS, plan de acción de cultura
- **07.5 Comunicación Interna** → newsletter, canales de comunicación, mensajes segmentados, feed interno, medición de efectividad

**Entidades principales:** `Union`, `CollectiveAgreement`, `SSTCommittee`, `IPERCMatrix`, `RiskMap`, `WelfareProgram`, `ClimateSurvey`, `CultureProgram`, `CommunicationCampaign`

**Tier comercial:** Pro (core para sector público, add-on para privado)

**Detalle completo:** → `modulos/07_relaciones_humanas_sociales.md`

---

### Módulo 08 — Control de Asistencia, Tiempo y Turnos
**Propósito:** gestionar las marcaciones, turnos, ausencias y permisos.

**Funcionalidades clave:**
- Integración biométrica (ZKTeco, Suprema, etc.)
- Marcación móvil con geofencing + reconocimiento facial
- Planificador de turnos rotativos (4x3, 6x1, 14x7 minería)
- Gestión de vacaciones (programación, goce, venta, truncas)
- Licencias y permisos (con y sin goce de haber)
- Descansos médicos con CITT EsSalud
- **Desplazamiento** (sector público): rotación, destaque, encargatura, comisión, permuta

**Entidades principales:** `Attendance`, `Shift`, `Schedule`, `TimeOff`, `Leave`, `MedicalRest`, `Displacement`

**Tier comercial:** Starter (core)

**Detalle completo:** → `modulos/08_control_asistencia_tiempo.md`

---

### Módulo 09 — Procedimiento Disciplinario
**Propósito:** gestionar faltas, procedimientos y sanciones.

**Dualidad crítica:**
- **Sector privado:** PID (Procedimiento Interno Disciplinario) según RIT y LPCL
- **Sector público:** PAD (Procedimiento Administrativo Disciplinario) según Ley 30057, con fases de instrucción (ORI) y sanción (OS), recursos ante Tribunal del Servicio Civil

**Funcionalidades clave:**
- Registro de faltas con tipificación
- Instrucción del expediente con línea de tiempo
- Derecho de defensa (descargos, plazos)
- Resolución con sanción (amonestación, suspensión, destitución)
- Recursos administrativos (reconsideración, apelación)
- Integración con Registro de Sanciones SERVIR (sector público)

**Entidades principales:** `DisciplinaryCase`, `Infraction`, `Hearing`, `DisciplinarySanction`, `Appeal`

**Tier comercial:** Pro

**Detalle completo:** → `modulos/09_procedimiento_disciplinario.md`

---

### Módulo 10 — Portal del Empleado y App Móvil
**Propósito:** empoderar al trabajador con autoservicio.

**Funcionalidades clave:**
- Descarga de boletas y certificados
- Solicitud de vacaciones, permisos, adelantos
- Actualización de datos personales
- Firma electrónica de documentos
- Chat con RRHH / ticketing interno
- Feed institucional (conecta con Módulo 07.5)
- Notificaciones push

**Tier comercial:** incluido desde Starter

**Detalle completo:** → `modulos/10_autoservicio_portal_empleado.md`

---

### Módulo 11 — Reclutamiento y Selección (ATS avanzado)
**Propósito:** profesionalizar el proceso de atracción.

**Funcionalidades clave:**
- Publicación multi-portal (LinkedIn, Bumeran, Computrabajo, API)
- Pipeline Kanban de candidatos
- Parsing de CV con IA
- Evaluaciones online (técnicas, psicométricas)
- Programación automática de entrevistas
- Integración con Módulo 03 (vinculación)
- **Convocatoria pública** para sector público (con cumplimiento de transparencia)

**Tier comercial:** Pro (add-on)

**Detalle completo:** → `modulos/11_reclutamiento_ats.md`

---

### Módulo 12 — Analítica y People Analytics
**Propósito:** dashboards ejecutivos e inteligencia de datos.

**Funcionalidades clave:**
- KPIs de RRHH (headcount, rotación, ausentismo, costo laboral)
- Predicción de fuga de talento (ML)
- Análisis de brecha salarial (Ley 30709)
- Análisis de encuestas con NLP
- Reportes regulatorios (MTPE, MINSA, SUNAT, CEPLAN)
- Exportadores a Power BI / Tableau / Looker

**Tier comercial:** Enterprise

**Detalle completo:** → `modulos/12_analitica_people_analytics.md`

---

## 4. Estrategia comercial de venta modular

### 4.1 Planes base

| Plan | Público objetivo | Módulos incluidos | Precio referencial (mensual) |
|------|------------------|-------------------|-------------------------------|
| **Starter** | Microempresas, PYMES | 02, 03, 04, 08, 10 | Desde US$ 3 por usuario |
| **Pro** | Mid-market (50-500 trab.) | Starter + 01, 05, 06, 07, 09, 11 | Desde US$ 6 por usuario |
| **Enterprise** | Grandes empresas (>500) | Todos + 12 + SLA premium + BI embebido | Desde US$ 9 por usuario |
| **GovTech** | Entidades públicas | Todos + módulo regional SERVIR + PAD Ley 30057 | Cotización por entidad |

### 4.2 Lógica de negociación modular

Cada módulo es **independientemente activable**. Durante el proceso de venta:
1. El cliente puede arrancar con **solo Planilla + Asistencia + Portal** (núcleo operativo).
2. Se negocian add-ons por módulo (ej. +Desempeño, +ATS, +LMS).
3. Se ofrecen **paquetes sectoriales** prediseñados (ver `comercial/C02_paquetes_sectoriales.md`):
   - **Pack Minería**: Starter + SST reforzado + Turnos 14x7 + régimen minero
   - **Pack Construcción Civil**: Starter + régimen jornales + CAPECO + BUC
   - **Pack Agroindustrial**: Starter + régimen 31110 con dos sistemas de pago
   - **Pack Sector Público**: GovTech completo con los 23 procesos SERVIR
4. **Descuentos por bundle** (3+ módulos = -10%; 6+ módulos = -20%).
5. **Early-bird** para clientes fundadores: precio Pro por Starter durante 12 meses.

---

## 5. Arquitectura técnica (resumen)

### 5.1 Stack recomendado sobre base INTRANET
Sobre la arquitectura existente en **github.com/p4ranoic0/INTRANET**, se propone evolución:

- **Backend:** Django/FastAPI (Python) o NestJS (TypeScript) — decisión según estado actual del repo
- **Base de datos:** PostgreSQL 15+ con **Row-Level Security (RLS)** por `tenant_id`
- **Caché/Queue:** Redis + RabbitMQ o Celery
- **Frontend:** React/Next.js con design system propio
- **Mobile:** React Native o Flutter
- **Auth:** Keycloak o Auth0 con SSO + MFA
- **Storage:** S3-compatible (MinIO autoalojado o AWS S3)
- **Infra:** Kubernetes (multi-AZ) + Terraform
- **Observabilidad:** Prometheus + Grafana + Loki
- **CI/CD:** GitHub Actions

### 5.2 Patrones de diseño aplicados
- **DDD con bounded contexts** (uno por subsistema SERVIR)
- **Metadata-driven schema** (estilo Frappe DocType) → configurabilidad sin fork
- **Strategy Pattern** para regímenes laborales peruanos
- **Event Sourcing acotado al contexto Payroll** → auditoría SUNAT/SUNAFIL
- **CQRS parcial** para dashboards (proyecciones denormalizadas)
- **Multi-tenancy híbrido**: pool + RLS baseline; DB dedicada como tier premium
- **Permission Levels 0-9 por campo** → campos sensibles (CCI, sueldo, salud)
- **Workflow Engine declarativo** → State Machines configurables por tenant
- **Custom Fields híbridos** → JSONB + DDL real para campos estratégicos
- **Temporal tables (SCD Type 2)** → contratos, salarios, asignaciones

### 5.3 Módulo regional Perú (el diferenciador)
Equivalente a `hrms/regional/india/` en Frappe HR. Contiene:
- Todas las tablas paramétricas SUNAT (Anexo 2)
- Generador de archivos PLAME (.txt Anexo 3)
- Generador T-Registro
- Generador AFPnet (.xlsx con 25 columnas)
- Calculadora de Renta 5ta con escala progresiva auto-actualizable
- Integración SBS para tasas AFP
- Cronograma tributario SUNAT
- Validador PVS integrado

**Detalle completo:** → `arquitectura/A01_arquitectura_general.md` y siguientes

---

## 6. Roadmap de desarrollo por fases

### FASE 1 — Fundamentos normativos (Meses 1-6)
Objetivo: motor de planilla infalible para los 4 regímenes más usados (728, CAS, MYPE, Agrario).
- Módulo 02 (puestos)
- Módulo 03 (empleo básico)
- Módulo 04 (planilla + boletas + exportadores)
- Módulo 08 (asistencia básica)
- Módulo 10 (portal web)
- **Entregable comercial:** Plan Starter operativo

### FASE 2 — Configurabilidad y extensibilidad (Meses 6-12)
- Motor de workflows configurable (estilo Frappe)
- Campos personalizados dinámicos
- APIs públicas (REST + GraphQL)
- App móvil
- Módulos 01, 05, 06
- **Entregable comercial:** Plan Pro operativo

### FASE 3 — Relaciones humanas y sector público (Meses 12-18)
- Módulos 07, 09, 11
- Módulo regional Perú completo (todos los regímenes especiales)
- Cumplimiento total SERVIR (los 23 procesos)
- **Entregable comercial:** Plan Enterprise + GovTech

### FASE 4 — Inteligencia y escalamiento (Meses 18-24)
- Módulo 12 (People Analytics con IA)
- Integraciones iPaaS
- IA predictiva de retención
- Marketplace de integraciones
- **Entregable comercial:** Add-ons premium

---

## 7. KPIs del producto

| KPI | Meta |
|-----|------|
| Tiempo de implementación llave en mano | 15-30 días |
| Precisión de validación PLAME/AFPnet | 100% |
| Disponibilidad del servicio (SLA) | 99.9% |
| NPS de clientes | >50 |
| Churn anual | <5% |
| Tiempo de cálculo de planilla para 1000 trabajadores | <30 segundos |
| Adopción de app móvil (empleados) | >70% |

---

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Cambios normativos frecuentes (UIT, RMV, reforma pensional, SERVIR) | Equipo legal-tributario dedicado + arquitectura de parámetros actualizables sin redeploy |
| Competencia consolidada (Buk, Talana, Ofisis) | Diferenciación por cobertura sector público + precio Pyme + APIs abiertas |
| Migración de datos desde legacy | ETL resiliente con ingesta masiva sin formatos restrictivos |
| Seguridad y datos personales (Ley 29733 + D.S. 016-2024-JUS) | Cifrado AES-256, RLS, ODP designado, auditorías, 48h notificación ANPD |
| Dependencia de contadores para adopción | Certificación técnica + convenios con colegios de contadores |
| Fallo en cálculo crítico (multa SUNAFIL) | Event sourcing + recálculos + testing exhaustivo + seguro de responsabilidad civil |

---

## 9. Referencias oficiales clave

- [SUNAT - Planilla Electrónica](https://orientacion.sunat.gob.pe/planilla-electronica)
- [SUNAT - Tablas paramétricas Anexo 2](https://orientacion.sunat.gob.pe/7086-12-tablas-parametricas)
- [SUNAT - Tabla 22 Conceptos PLAME](https://orientacion.sunat.gob.pe/sites/default/files/inline-files/Tabla%20N22%20Definici%C3%B3n%20Conceptos%20Plame_011025.pdf)
- [SERVIR - Normativa Servicio Civil](https://www.servir.gob.pe/rectoria/normatividad-del-servicio-civil-a-indice-dleg-276/)
- [AFPnet](https://www.afpnet.com.pe/)
- [MTPE - Gob.pe](https://www.gob.pe/mtpe)
- [SUNAFIL - Gob.pe](https://www.gob.pe/sunafil)
- [D.Leg. 276 - Texto actualizado](https://lpderecho.pe/ley-bases-carrera-administrativa-decreto-legislativo-276/)
- [Ley 30057 - Servicio Civil](https://www.gob.pe/institucion/servir/normas-legales/)
- [Ley 29733 - Protección de Datos + D.S. 016-2024-JUS](https://kom.pe/reglamento-ds-016-2024-jus-datos-personales/)

---

## 10. Control de versiones de este documento

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Abril 2026 | Versión inicial con 10 secciones |
| 2.0 | Abril 2026 | Adopción modelo SERVIR (sector público), dualidad privado/público, 12 módulos SaaS definidos, MDs hijos referenciados, integración con INTRANET |
| **3.0** | **Abril 2026** | **Todos los MDs hijos generados y disponibles individualmente (36 documentos totales). Separación de los normativos N04, N05, N07, N08, N09, N10, N11, N12, N13 en archivos individuales. Separación de módulos 11 y 12. MDs arquitectura A02-A08 y comerciales C01-C03 completados. Inventario verificado.** |

---

> **Estado actual del proyecto:** Documentación completa para iniciar desarrollo. Base sólida de conocimiento técnico-funcional-normativo disponible para equipos de producto, ingeniería y comercial.
>
> **Siguiente fase sugerida:** priorizar implementación de la Fase 1 del roadmap (meses 1-6): módulos 02, 03, 04, 08, 10 para alcanzar el tier Starter comercializable. Los MDs normativos N01, N02, N06, N07, N08, N09 son lectura obligatoria para cualquier desarrollador del módulo 04 (planilla).

