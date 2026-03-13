# Feature Landscape

**Domain:** HR Intranet — Peruvian Public Sector (Sistema de Gestión de RRHH)
**Researched:** 2026-03-13
**Confidence note:** External web tools unavailable during this session. All findings based on: (1) direct codebase analysis of existing models, (2) HIGH-confidence training knowledge of Peruvian labor law (DL 276, DL 728, DL 1057 CAS, SUNAT normativa, AFP Net format, PDT-PLAME structure) current as of August 2025. Legal framework is stable — these are statutory obligations, not trends.

---

## Existing Model Inventory (What the Codebase Already Has)

Before categorizing features, it is essential to know what data models already exist, as they determine implementation complexity:

| Model | Status | Key Fields |
|-------|--------|-----------|
| `Empleado` | Exists | DNI, sistema_pensiones (ONP/AFP), tipo_comision, cuspp, tipo_seguro |
| `DatosLaborales` | Exists | regimen_laboral (276/728/1057/locacion), cargo, sueldo_basico, asignacion_familiar, jefe_directo |
| `ContratosAdendas` | Exists | area FK, tipo, fechas |
| `DocumentosDigitales` | Exists | tipo_documento (28 types), categoria, estado, nivel_acceso, validado_por |
| `OnboardingEmpleado` | Exists | checklist booleans, email_bienvenida_enviado, estado_onboarding |
| `PlanillaMensual` | Exists | periodo, modalidad, totales (essalud, afp, onp, neto) |
| `DetallePlanilla` | Exists | dias_laborados, aporte_afp, comision_afp, prima_seguro, onp, renta_quinta, essalud, banco |
| `ConfiguracionAfp` | Exists | aporte_obligatorio_pct, comision_flujo_pct, comision_mixta_pct, prima_seguro_pct |
| `ConfiguracionUit` | Exists | valor_uit, tope_renta_cuarta_uit (45 UITs), porcentaje_renta_cuarta (8%) |
| `BoletaPago` | Exists | archivo_pdf, estado, hash_documento, fecha_envio_email |
| `DescuentoMasivo` | Exists | archivo_origen, estado, errores_log |
| `SolicitudVacaciones` | Exists | tipo_solicitud, aprobado_por_jefe, aprobado_por_rrhh, fraccionamiento |
| `PeriodoVacacional` | Exists | dias_correspondientes, dias_gozados, dias_pendientes, fecha_vencimiento |
| `GoceVacaciones` | Exists | fecha_reincorporacion, motivo_interrupcion |

**Conclusion:** The data model is largely complete. The milestone work is mostly about building the **views, workflows, and export logic** — not new data modeling.

---

## Table Stakes

Features users (HR staff, employees) expect. Missing = product feels broken or legally non-compliant.

### Onboarding

| Feature | Why Expected | Complexity | Legal Basis | Notes |
|---------|--------------|------------|-------------|-------|
| Email de bienvenida al crear usuario | Estándar de toda plataforma. Bug actual: `ggarcia` no lo recibió | Low | — | Model field `email_bienvenida_enviado` already exists; only Django email config + trigger missing |
| Vista restringida del empleado en onboarding | Empleado no debe ver datos de otros ni panel admin | Low | — | Requires permission check on existing views; no new model needed |
| Carga de foto de perfil | Toda plataforma HR moderna lo requiere | Low | — | `DocumentosDigitales` tipo `foto` already exists; need upload endpoint + frontend form |
| Subida de DNI / carnet de extranjería | Documento de identidad obligatorio en legajo peruano | Low | Normativa SUNAFIL legajo | tipo `dni`/`carnet_extranjeria` already in DocumentosDigitales |
| Subida de DDJJ (Declaración Jurada) | Obligatorio en entidades públicas peruanas (Ley 27482 y reglamentos) | Low | DL 27482, SERVIR | tipo `declaracion_jurada` already in DocumentosDigitales |
| Subida de certificados académicos y de trabajo | Documentación de antecedentes laborales | Low | — | tipos ya existen en DocumentosDigitales |
| Checklist de progreso visible al empleado | UX básica — empleado sabe qué falta | Low | — | `progreso_porcentaje` property already on OnboardingEmpleado model |
| Flujo observado/corrección: RRHH puede rechazar y solicitar re-subida | Sin esto RRHH no puede gestionar errores | Medium | — | Estado `observado` ya existe en modelo |
| Notificación a RRHH cuando onboarding pasa a `pendiente_validacion` | RRHH necesita saber cuándo revisar | Low | — | Django signals o post_save hook |

### Legajo Digital

| Feature | Why Expected | Complexity | Legal Basis | Notes |
|---------|--------------|------------|-------------|-------|
| Vista unificada RRHH: todos los datos y documentos por sección | Reemplaza el legajo físico — funcionalidad core | Medium | SUNAFIL: legajo de trabajador | Requiere frontend tabbed view; datos ya están en BD |
| Descarga individual de cada documento | Sin esto el legajo no sirve | Low | — | `url_descarga` property ya existe en DocumentosDigitales |
| Filtrado y búsqueda de documentos por tipo/categoría | Legajo con decenas de docs necesita buscador | Low | — | Backend filter already in DocumentosDigitales |
| Indicador de documentos pendientes/vencidos | RRHH necesita alertas de cumplimiento | Low | — | `requiere_atencion` property ya existe |
| Empleado puede ver su propio legajo (solo lectura) | Transparencia y autoservicio | Low | — | Permission layer needed |
| Historial de cambios auditado | Trazabilidad legal obligatoria | Low | SUNAFIL | `subido_por`, `validado_por`, timestamps ya existen |
| Flujo de aprobación de cambios de datos personales (empleado propone, RRHH aprueba) | Sin esto RRHH pierde control de datos maestros | Medium | — | Requiere modelo de solicitud de cambio — NO existe aún |

### Remuneraciones

| Feature | Why Expected | Complexity | Legal Basis | Notes |
|---------|--------------|------------|-------------|-------|
| Cálculo de planilla mensual con AFP/ONP/EsSalud | Core de nómina — sin esto no hay sistema | High | DL 728, DL 276, DL 1057 | Modelos completos; falta lógica de cálculo en views |
| Descuento AFP correcto (aporte 10% + comisión flujo/mixta + prima seguro) | Error aquí = problema legal con AFP | High | Res. SBS AFP | ConfiguracionAfp model tiene todos los campos; comision_flujo_pct, comision_mixta_pct, prima_seguro_pct |
| Descuento ONP: 13% de remuneración asegurable | Obligatorio para afiliados a ONP | Medium | DL 19990 | Campo `aporte_onp` ya existe en DetallePlanilla |
| EsSalud 9% a cargo del empleador | Obligación del empleador — aparece en planilla de costos | Medium | Ley 26790 | Campo `essalud` en DetallePlanilla; empleador paga, no descuenta al trabajador |
| Retención renta 5ta categoría (escala anual proyectada) | Obligatorio para dependientes | High | LIR Art. 75, DS 215-2006-EF | Campo `renta_quinta_categoria` en DetallePlanilla; ConfiguracionUit tiene UIT y tope |
| Boleta de pago descargable por el empleado | Obligatorio — empleador debe entregar boleta | Medium | DL 728 Art. 19, DS 001-98-TR | Modelo `BoletaPago` y campo `archivo_pdf` ya existen |
| Carga masiva de descuentos (préstamos, judiciales) | Sin esto RRHH ingresa uno a uno | Medium | — | Modelo `DescuentoMasivo` y `archivo_origen` ya existen |
| Exportación Excel para AFP Net | AFP exige este formato mensual | High | AFP Net specs | Formato fijo AFP Net: DNI, CUSPP, tipo comisión, aportes, remuneración asegurable |
| Exportación Excel para PDT-PLAME | SUNAT exige este archivo mensual | High | RS 183-2011-SUNAT, PDT 601/PLAME | Incluye empleados, tipos de renta, aportes; formato SUNAT fijo |
| Exportación Excel ingresos/descuentos/neto | Para control interno y finanzas | Low | — | Derivado de DetallePlanilla |
| Certificado de retención de 5ta categoría (anual) | Obligatorio al cierre de año o cese | Medium | LIR Art. 75 | Empleador debe entregar certificado Form. 1652 equivalente |
| Configuración de parámetros salariales maestros | Sin esto el cálculo no puede parametrizarse | Medium | — | `ConfiguracionRemuneracion` y `ConfiguracionAfp` ya existen |
| Estado de planilla con workflow (borrador → generada → aprobada → pagada) | Control del proceso de cierre de planilla | Medium | — | Estados ya existen en `PlanillaMensual` |

### Vacaciones

| Feature | Why Expected | Complexity | Legal Basis | Notes |
|---------|--------------|------------|-------------|-------|
| Consulta de saldo vacacional vigente | Autoservicio básico — todo empleado lo pide | Low | DL 713 | `dias_pendientes` en PeriodoVacacional |
| Solicitud de vacaciones por el empleado | Reemplaza formulario en papel | Low | DL 713 | `SolicitudVacaciones` con tipo_solicitud y estados ya existe |
| Aprobación por jefe inmediato (1er nivel) | DL 713 requiere autorización de empleador | Low | DL 713 | `aprobado_por_jefe`, `jefe_aprobador` ya en modelo |
| Aprobación final por RRHH (2do nivel) | Entidades públicas peruanas exigen doble aprobación | Low | SERVIR | `aprobado_por_rrhh` ya en modelo |
| Fraccionamiento de vacaciones | Legal: pueden fraccionarse con acuerdo de partes | Low | DL 713 Art. 17 | `tipo_solicitud='fraccionamiento'` y `min_dias_por_fraccion` ya en modelo |
| Cálculo de días por tipo de contrato y régimen | DL 276: 30 días; DL 728: 30 días; CAS: proporcional | Medium | DL 276, DL 728, DL 1057 | `ConfiguracionVacaciones` con `tipo_calculo` y `dias_por_ano` ya existe |
| Registro de goce efectivo y reincorporación | RRHH necesita control de cuándo regresa el servidor | Low | — | `GoceVacaciones` con `fecha_reincorporacion_real` ya existe |
| Historial de solicitudes auditado | Trazabilidad para SUNAFIL | Low | SUNAFIL | `HistorialSolicitudVacaciones` ya existe |
| Reporte récord vacacional por servidor | Exigido en auditorías SUNAFIL | Medium | SUNAFIL | Derivado de PeriodoVacacional + GoceVacaciones |
| Alertas de vacaciones vencidas (días no gozados) | Pasado el período legal, son deuda — riesgo legal | Medium | DL 713 Art. 23 | `dias_vencidos` en PeriodoVacacional |

---

## Differentiators

Features que distinguen el sistema y agregan valor más allá del cumplimiento básico.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Generación automática de planilla desde datos laborales (sin ingreso manual) | Reduce error humano; raro en sistemas públicos peruanos | High | Requiere motor de cálculo que lea DatosLaborales y ConfiguracionAfp |
| Exportación Excel zipeado para carga web (AIRHSP) | Automatiza proceso que hoy es manual en muchas entidades | Medium | Formato específico AIRHSP; requiere spec del sistema receptor |
| Alerta de contratos por vencer con reporte por oficina | RRHH actúa preventivamente en vez de reactivamente | Low | `contrato_por_vencer` property ya en DatosLaborales; falta vista de reporte |
| Suspensión de retención 4ta categoría con control de tope anual | Locadores presentan formulario de suspensión — sistema lo controla | Medium | `tiene_suspension_renta_cuarta` y `tope_suspension_anual` ya en DetallePlanilla |
| Certificado de retención 4ta categoría (para locadores, al cese) | Obligación del pagador — raro verlo automatizado | Medium | 8% retención; tope 45 UIT anuales; ConfiguracionUit ya tiene ambos valores |
| Integración automática de vacaciones aprobadas en liquidaciones | Evita error de doble conteo al calcular liquidaciones en v2 | High | Requiere que Vacaciones y Remuneraciones compartan datos de período |
| Reporte provisional mensual de vacaciones para finanzas (con cálculo proporcional) | Finanzas necesita provisionar gasto antes del cierre | High | Cálculo: (sueldo/30) * días_acumulados descontando licencias sin goce |
| Cambio de datos con flujo de aprobación RRHH (empleado propone, RRHH valida) | Datos maestros consistentes sin dependencia de RRHH para cada cambio | Medium | Requiere nuevo modelo `SolicitudCambioDatos` — no existe aún |
| Panel de cumplimiento de onboarding (RRHH ve todos los pendientes) | Vista de gestión para seguimiento masivo | Medium | Derivado de OnboardingEmpleado; falta vista de dashboard |
| Validación de documentos con observaciones detalladas | RRHH puede indicar exactamente qué corregir | Low | `observaciones_validacion` ya existe en DocumentosDigitales |

---

## Anti-Features

Features a NO construir en esta versión para mantener el scope.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Firma digital electrónica de documentos (PKI) | Requiere proveedor de firma electrónica (DigiCert, Certitool, SUNAT SOL) — alta complejidad legal y técnica | Subida de PDF ya firmado físicamente; el campo `requiere_firma_digital` en DocumentosDigitales puede marcar el req para v2 |
| Cálculo de gratificaciones (julio/diciembre) | Depende de liquidaciones completas con lógica de promedio semestral — alta complejidad | Documentar fórmula; diferir a cuando Remuneraciones base esté estable |
| Cálculo de CTS | Requiere historial de remuneraciones + lógica de depósito semestral (mayo/noviembre) — depende de período largo de datos | Diferir a v2 junto con liquidaciones |
| Portal de autoservicio separado (app mobile) | Stack fijo Django + React; portal separado implica app nueva | Vista restringida del sistema existente sirve para onboarding |
| Integración directa con AFP Net API | AFP Net no tiene API pública — solo acepta carga de archivo Excel | Exportar Excel en formato AFP Net para carga manual |
| Integración directa con SUNAT PDT | PDT-PLAME es archivo local — no hay API de envío automatizado | Exportar archivo Excel en estructura PDT para carga manual en PDT 601 |
| Módulo de selección y reclutamiento | Fuera de scope v1 según PROJECT.md | Diferir a v2 |
| Módulo de desvinculación/liquidaciones completo | Depende de Remuneraciones completo — fuera de scope v1 | Diferir a v2; registrar fecha_cese en DatosLaborales |
| Inducción virtual (videos, evaluaciones) | Requiere plataforma e-learning — diferir a v2 | |
| Gestión de rendimiento (metas SERVIR, evaluación 360) | Alta complejidad normativa SERVIR — fuera de scope v1 | |
| Rol de jefe con panel completo de gestión de equipo | Jefe solo necesita aprobar vacaciones en v1 | Solo la acción de aprobación en v1 |
| Cálculo de horas extra / sobretiempo | No aplica en sector público peruano bajo DL 276/CAS | Fuera de contexto |

---

## Feature Dependencies

```
Email bienvenida → Django email settings (SMTP) configurado
Vista onboarding empleado → Permisos granulares por estado_onboarding
Carga foto perfil → Endpoint upload + DocumentosDigitales tipo 'foto'
Carga documentos onboarding → Vista restringida (debe ir después de vista)
Legajo digital RRHH → Todos los documentos subidos (depende de onboarding)

Planilla mensual → ConfiguracionAfp por vigencia_mes
Planilla mensual → ConfiguracionUit por año (para renta 5ta)
Planilla mensual → DatosLaborales activo del empleado (sueldo_basico, sistema_pensiones)
Boleta de pago → DetallePlanilla (debe existir detalle aprobado)
Exportación AFP Net → DetallePlanilla (sistema_pensiones = AFP*, cuspp, tipo_comision)
Exportación PDT-PLAME → DetallePlanilla (todos los aportes y retenciones)
Exportación PDT-PLAME incluye renta 5ta → Cálculo renta 5ta correcto en DetallePlanilla
Certificado retención 5ta → Planillas de todo el año del empleado
Certificado retención 4ta → DetallePlanilla con tiene_suspension_renta_cuarta

Solicitud vacaciones → PeriodoVacacional activo del empleado
Solicitud vacaciones → jefe_directo configurado en DatosLaborales (para 1er nivel aprobación)
Reporte provisión vacaciones → PeriodoVacacional + GoceVacaciones + DatosLaborales (sueldo)
Integración vacaciones en liquidaciones → PeriodoVacacional (V2 dependency)

Cambio datos con aprobación → Nuevo modelo SolicitudCambioDatos (no existe — debe crearse)
Alertas contratos vencimiento → DatosLaborales.fecha_fin_contrato (datos ya existen)
```

---

## Peruvian Labor Law Specifics

### Regímenes Laborales en el sistema

El sistema ya modela correctamente los tres regímenes principales peruanos:

| Régimen | Código en modelo | Pensiones | Vacaciones | EsSalud |
|---------|-----------------|-----------|------------|---------|
| DL 276 (servicios civiles) | `'276'` | ONP o AFP | 30 días/año | 9% empleador |
| DL 728 (actividad privada) | `'728'` | ONP o AFP | 30 días/año | 9% empleador |
| CAS DL 1057 | `'1057'` | ONP o AFP | 30 días/año proporcional | 9% sobre 45% UIT mensual |
| Locación de Servicios | `'locacion'` | Ninguna (4ta categoría) | Ninguna | Ninguna (pagador retiene 8%) |
| Consultoría | `'consultoria'` | Ninguna (4ta categoría) | Ninguna | Ninguna |

**Implicación crítica:** El cálculo de planilla debe bifurcar por régimen. CAS tiene EsSalud calculado diferente (9% × 45% UIT / 12). Locación/Consultoría no entra en planilla de haberes sino en planilla de honorarios con retención 4ta.

### AFP Net — Formato de Exportación (HIGH confidence — formato estable)

El archivo Excel para AFP Net debe contener por empleado AFP:
- Tipo de registro (T = titular)
- Período (AAAAMM)
- Tipo de documento + número (DNI)
- CUSPP (campo `cuspp` en DetallePlanilla)
- Tipo de comisión: FLUJO o MIXTA (campo `tipo_comision_afp`)
- Remuneración asegurable (remuneración base sujeta a descuento)
- Aporte obligatorio (10% de rem. asegurable)
- Comisión AFP (porcentaje según tipo)
- Prima de seguro
- Total descuento AFP
- Nombre de la AFP

El sistema ya tiene todos estos campos en `DetallePlanilla` y `ConfiguracionAfp`.

### PDT-PLAME — Estructura (HIGH confidence — formato DS 018-2007-TR)

PDT-PLAME 601 incluye dos secciones principales:
1. **Empleadores**: RUC, período, totales de aportes
2. **Trabajadores por registro**: DNI, apellidos/nombres, días laborados, tipo de trabajador (código SUNAT), tipo de contrato, remuneración, asignación familiar, aporte AFP/ONP, retención renta 5ta, EsSalud

El código de tipo de trabajador SUNAT varía por régimen:
- DL 728: código 01
- DL 276: código 10
- CAS: código 21
- Pensionistas: código 41-43

**Implicación:** El sistema necesita mapear `regimen_laboral` del modelo a código SUNAT en la exportación PDT.

### Renta 5ta Categoría — Cálculo (HIGH confidence — LIR Art. 75)

Escala progresiva anual 2025:
- Hasta 5 UIT: 0% (mínimo no imponible)
- 5 UIT hasta 20 UIT: 8%
- 20 UIT hasta 35 UIT: 14%
- 35 UIT hasta 45 UIT: 17%
- Más de 45 UIT: 20%

Cálculo mensual: Proyectar ingreso anual → aplicar escala → dividir entre 12 → ajustar por meses transcurridos. El campo `ConfiguracionUit.valor_uit` ya existe para parametrizar esto.

### Renta 4ta Categoría — Locadores (HIGH confidence — LIR Art. 74)

- Retención: 8% del honorario bruto
- Suspensión si el locador presenta formulario SUNAT cuando sus ingresos anuales no superan 45 UITs
- El campo `tiene_suspension_renta_cuarta` y `tope_suspension_anual` ya existen en `DetallePlanilla`

### CTS — Compensación por Tiempo de Servicios (HIGH confidence — DL 650)

- Régimen DL 728: 1 remuneración + 1/6 asignación familiar por año. Depósito en mayo y noviembre.
- Régimen DL 276: equivalente gestionado por ONP/tesoro (no hay depósito privado)
- CAS DL 1057: no tiene CTS (incluida en remuneración mensual conceptualmente)
- **No entra en scope v1** — pero el sistema debe registrar `fecha_ingreso` correctamente (ya lo hace) para calcularla en v2.

### Gratificaciones — Julio y Diciembre (HIGH confidence — Ley 27735)

- DL 728: media remuneración en julio y diciembre (promedio últimos 6 meses)
- DL 276: equivalente por ley
- CAS: no aplica gratificación extraordinaria (la tiene incorporada)
- **No entra en scope v1** — diferir junto con liquidaciones.

### Asignación Familiar (HIGH confidence — Ley 25129)

- 10% del sueldo mínimo vital (RMV) mensual si el trabajador tiene hijos menores de 18 años (o hasta 24 en estudios superiores)
- RMV 2025: S/ 1,025 → Asignación familiar: S/ 102.50
- Campo `asignacion_familiar` ya existe en `DatosLaborales` y `DetallePlanilla`

---

## MVP Recommendation

Priorizar en este orden dentro del milestone:

**Grupo 1 — Desbloqueadores (sin estos lo demás no funciona):**
1. Email de bienvenida en onboarding (bug existente — bloquea toda la UX)
2. Vista restringida del empleado en onboarding (seguridad — debe ir antes de cualquier frontend)
3. Permisos granulares por estado_onboarding

**Grupo 2 — Onboarding + Legajo (valor visible para usuarios):**
4. Carga de foto de perfil
5. Upload de documentos por sección (DNI, DDJJ, certificados, familiares)
6. Vista legajo RRHH unificada por sección
7. Flujo observado/corrección
8. Panel cumplimiento onboarding para RRHH

**Grupo 3 — Remuneraciones (mayor complejidad técnica):**
9. Motor de cálculo planilla (bifurcado por régimen: 728, 276, 1057, locación)
10. Renta 5ta categoría (escala progresiva proyectada anual)
11. Generación de boletas PDF por empleado
12. Exportación AFP Net (Excel formato fijo)
13. Exportación PDT-PLAME (Excel con mapeo de códigos SUNAT)
14. Carga masiva de descuentos
15. Certificados de retención (4ta y 5ta)

**Grupo 4 — Vacaciones (flujo de workflow):**
16. Flujo completo solicitud → aprobación jefe → aprobación RRHH
17. Saldo vacacional en tiempo real
18. Reportes: récord vacacional, vacaciones pendientes, reporte por oficina
19. Reporte provisional mensual para finanzas

**Diferir explícitamente:**
- Gratificaciones: diferir a v2 (depende de estabilidad de Remuneraciones)
- CTS: diferir a v2 (depende de historial completo de períodos)
- Liquidaciones: diferir a v2 (scope explícito en PROJECT.md)
- Módulo cambio datos con aprobación: puede ir en v1.5 (requiere modelo nuevo)

---

## Sources

- Codebase directo: `D:/INTRANET/back/app_rrhh/models/` (remuneracion.py, vacaciones.py, onboarding.py, datos_laborales.py, documentos_digitales.py, empleado.py, configuracion_uit.py)
- Legislación peruana (HIGH confidence — conocimiento de training, normativa estable):
  - Decreto Legislativo 728 (Ley de Productividad y Competitividad Laboral)
  - Decreto Legislativo 276 (Bases de la Carrera Administrativa)
  - Decreto Legislativo 1057 (Régimen CAS)
  - Decreto Legislativo 713 (Descansos Remunerados)
  - Decreto Legislativo 650 (CTS)
  - Ley 25129 (Asignación Familiar)
  - Ley 27735 (Gratificaciones julio/diciembre)
  - Ley 26790 (Modernización de la Seguridad Social — EsSalud 9%)
  - Decreto Legislativo 19990 (ONP 13%)
  - LIR Art. 74-75 (Retenciones renta 4ta y 5ta categoría)
  - Resolución SBS AFP Net (formato de archivo mensual)
  - RS 183-2011-SUNAT / DS 018-2007-TR (PDT-PLAME 601 estructura)
