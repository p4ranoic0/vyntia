# Requirements: Sistema de Gestión de RRHH — Intranet

**Defined:** 2026-03-13
**Core Value:** El servidor completa su información una sola vez al ingresar, y esa información alimenta todos los procesos posteriores sin volver a pedírsela.

## v1 Requirements

### Infrastructure (Fixes bloqueantes)

- [x] **INFRA-01**: El sistema arranca en producción sin errores de sintaxis en settings
- [x] **INFRA-02**: `requirements.txt` declara `psycopg2-binary` (PostgreSQL) y el driver está instalado en el .venv; todos los settings usan `django.db.backends.postgresql`
- [x] **INFRA-03**: Los PDFs generados contienen contenido real (no stub "DOCUMENTO GENERADO") usando xhtml2pdf como motor principal en Windows
- [x] **INFRA-04**: La propiedad `tamano_archivo_legible` no muta el campo en la base de datos

### Onboarding

- [x] **ONBD-01**: El sistema envía correo de bienvenida al empleado cuando se crea su usuario de onboarding
- [x] **ONBD-02**: El empleado en onboarding accede a una vista restringida — solo ve sus propias secciones de carga, sin acceso al panel de administración
- [x] **ONBD-03**: El empleado puede subir su foto de perfil desde la sección de datos personales
- [x] **ONBD-04**: El empleado puede subir documentos PDF en datos personales (DNI, carné de extranjería)
- [x] **ONBD-05**: El empleado puede subir documentos PDF en datos familiares (DNI de familiar, partida de nacimiento de dependiente)
- [x] **ONBD-06**: El empleado puede subir documentos PDF en datos académicos (certificados de estudios, diplomas)
- [x] **ONBD-07**: El empleado puede subir documentos PDF en datos laborales (DDJJ, CV, certificado de trabajo anterior, carta de recomendación) — sin editar los campos laborales que gestiona RRHH
- [x] **ONBD-08**: RRHH puede ver el porcentaje de completitud del onboarding de cada empleado

### Legajo Digital

- [ ] **LEGJ-01**: RRHH accede a una vista unificada del legajo digital de cada empleado con todas sus secciones (personal, familiar, académico, laboral, documentos)
- [ ] **LEGJ-02**: El legajo muestra el estado de cada documento (presentado / pendiente / vencido)
- [ ] **LEGJ-03**: RRHH puede descargar cualquier documento del legajo directamente desde la vista
- [ ] **LEGJ-04**: El sistema registra quién y cuándo accede o modifica documentos del legajo (auditoría)

### Información Personal y Laboral

- [ ] **INFO-01**: El empleado puede proponer cambios en sus datos personales, de contacto y familiares
- [ ] **INFO-02**: RRHH recibe alerta de cambios propuestos y puede aprobar o rechazar antes de que se registren oficialmente
- [ ] **INFO-03**: El sistema genera certificados y constancias de trabajo en PDF según datos laborales del empleado
- [ ] **INFO-04**: RRHH recibe alertas de vencimiento de contratos y adendas
- [ ] **INFO-05**: El sistema genera reportes de vencimiento de contratos/adendas desagregados por oficina
- [ ] **INFO-06**: El sistema genera contratos y adendas en PDF
- [ ] **INFO-07**: El sistema genera archivos Excel para carga masiva de altas y bajas en AIRHSP

### Remuneraciones

- [ ] **REMU-01**: RRHH configura parámetros salariales (remuneración fija, bonos, gratificaciones, descuentos deducibles/no deducibles, retenciones, cargas sociales por régimen)
- [ ] **REMU-02**: El sistema genera planilla detallada por meta presupuestal diferenciando regímenes (plazo indeterminado, determinado, subsidios)
- [ ] **REMU-03**: RRHH puede realizar carga masiva de descuentos desde archivo Excel
- [ ] **REMU-04**: El colaborador puede visualizar y descargar su boleta de pago desde el portal
- [ ] **REMU-05**: El sistema genera reporte de planilla por banco y modalidad en Excel
- [ ] **REMU-06**: El sistema genera reporte de descuentos por modalidad en Excel
- [ ] **REMU-07**: El sistema genera reporte por sistema de pensiones (AFP/ONP) en Excel
- [ ] **REMU-08**: El sistema exporta planilla en formato AFP Net (Excel con columnas exactas del spec AFP)
- [ ] **REMU-09**: El sistema exporta planilla en formato PDT-PLAME / PDT 601 (Excel con estructura SUNAT)
- [ ] **REMU-10**: El sistema genera archivo Excel de ingresos, descuentos y sueldo neto por servidor
- [ ] **REMU-11**: El sistema genera archivo Excel zipeado para carga de planilla web
- [ ] **REMU-12**: El sistema genera Certificado de Retención de 4ta categoría (anual y a fecha de cese) en PDF
- [ ] **REMU-13**: El sistema genera Certificado de Rentas de 5ta categoría en PDF

### Vacaciones

- [ ] **VACA-01**: El empleado registra solicitud de goce vacacional desde el portal
- [ ] **VACA-02**: El jefe inmediato aprueba o rechaza la solicitud de vacaciones con notificación al empleado
- [ ] **VACA-03**: El empleado consulta su saldo vacacional vigente en línea
- [ ] **VACA-04**: El sistema acumula días de vacaciones según tipo de contrato y antigüedad (DL 713)
- [ ] **VACA-05**: El empleado puede solicitar días fraccionados de vacaciones según calendario laboral
- [ ] **VACA-06**: RRHH gestiona solicitudes, revisa conflictos/superposiciones, aprueba/rechaza y actualiza saldos
- [ ] **VACA-07**: El sistema genera reporte de récord vacacional por servidor
- [ ] **VACA-08**: El sistema genera reporte de vacaciones no gozadas y vacaciones truncas
- [ ] **VACA-09**: El sistema genera reporte total de récord vacacional por oficinas
- [ ] **VACA-10**: El sistema genera reporte provisional mensual para finanzas (cálculo por mes/día trabajado, descontando licencias sin goce)

## v2 Requirements

### Proceso de Selección y Reclutamiento
- Publicación y gestión de ofertas laborales
- Banco de preguntas y evaluaciones automáticas
- Portal del candidato (CV, certificados, formularios)
- Filtros avanzados y puntuación automática
- Agenda de entrevistas y comité de selección
- Reportes de reclutamiento

### Liquidaciones
- Cálculo automático de liquidación final (sueldos proporcionales, vacaciones truncas, CTS, indemnización)
- Excel planilla AFP Net para liquidaciones
- Notificación a áreas (finanzas, TI, seguridad) sobre fecha de salida

### Inducción Virtual
- Módulo de inducción con videos, manuales y evaluaciones
- Seguimiento de progreso por responsable
- Formulario de retroalimentación de inducción

### Desplazamiento
- Registro de desplazamientos temporales (rotación, traslados, licencias sin goce, teletrabajo)
- Reporte consolidado para planilla y liquidaciones

### Desvinculación
- Checklist de desvinculación multi-área (RRHH, logística, TI, finanzas)
- Gestión de entrevistas de salida
- Alertas anticipadas para baja de accesos y equipos

### Capacitación
- Portal de inscripción y seguimiento de capacitaciones
- Registro de necesidades de capacitación validado por jefe
- Plan de Desarrollo de Personas (PDP)

### Diseño de Puesto y Organigrama
- CRUD de perfiles de puesto con competencias y jerarquía
- Vinculación de perfiles con reclutamiento y rendimiento

### Comunicación Interna
- Avisos y comunicados segmentados por área/nivel
- Confirmación de lectura y métricas de alcance

### Gestión de Rendimiento
- Registro y validación de metas (POI, PEI) con firma digital
- Seguimiento y puntuación por jefe inmediato
- Reportes para SERVIR en Excel y PDF

## Out of Scope

| Feature | Reason |
|---------|--------|
| Gratificaciones y CTS en v1 | Dependen de historial salarial multi-período — deuda técnica si se fuerzan en v1 |
| WeasyPrint en Windows | Falla por dependencia GTK — usar xhtml2pdf + ReportLab (Platypus) |
| Portal externo de candidatos | Alta complejidad, no es prioridad v1 |
| Firma digital nativa | Requiere integración con sistema externo (e.g. FirmaPerú) — diferir |
| Integración cloud storage (S3) | django-storages instalado pero no activar en v1 — storage local primero |
| Chat / mensajería interna | No es core RRHH operativo |

## Traceability

| Requirement | Phase | Phase Name | Status |
|-------------|-------|------------|--------|
| INFRA-01 | Phase 0 | Infrastructure Fixes | Pending |
| INFRA-02 | Phase 0 | Infrastructure Fixes | Pending |
| INFRA-03 | Phase 0 | Infrastructure Fixes | Pending |
| INFRA-04 | Phase 0 | Infrastructure Fixes | Pending |
| ONBD-01 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-02 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-03 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-04 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-05 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-06 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-07 | Phase 1 | Onboarding Self-Service | Complete |
| ONBD-08 | Phase 1 | Onboarding Self-Service | Complete |
| LEGJ-01 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| LEGJ-02 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| LEGJ-03 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| LEGJ-04 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-01 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-02 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-03 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-04 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-05 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-06 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| INFO-07 | Phase 2 | Legajo Digital y Gestion de Informacion | Pending |
| REMU-01 | Phase 3 | Remuneraciones | Pending |
| REMU-02 | Phase 3 | Remuneraciones | Pending |
| REMU-03 | Phase 3 | Remuneraciones | Pending |
| REMU-04 | Phase 3 | Remuneraciones | Pending |
| REMU-05 | Phase 3 | Remuneraciones | Pending |
| REMU-06 | Phase 3 | Remuneraciones | Pending |
| REMU-07 | Phase 3 | Remuneraciones | Pending |
| REMU-08 | Phase 3 | Remuneraciones | Pending |
| REMU-09 | Phase 3 | Remuneraciones | Pending |
| REMU-10 | Phase 3 | Remuneraciones | Pending |
| REMU-11 | Phase 3 | Remuneraciones | Pending |
| REMU-12 | Phase 3 | Remuneraciones | Pending |
| REMU-13 | Phase 3 | Remuneraciones | Pending |
| VACA-01 | Phase 4 | Vacaciones | Pending |
| VACA-02 | Phase 4 | Vacaciones | Pending |
| VACA-03 | Phase 4 | Vacaciones | Pending |
| VACA-04 | Phase 4 | Vacaciones | Pending |
| VACA-05 | Phase 4 | Vacaciones | Pending |
| VACA-06 | Phase 4 | Vacaciones | Pending |
| VACA-07 | Phase 4 | Vacaciones | Pending |
| VACA-08 | Phase 4 | Vacaciones | Pending |
| VACA-09 | Phase 4 | Vacaciones | Pending |
| VACA-10 | Phase 4 | Vacaciones | Pending |

**Coverage:**
- v1 requirements: 41 total
- Mapped to phases: 41
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-13*
*Last updated: 2026-03-13 after roadmap creation*
