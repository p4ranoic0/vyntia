# Módulo 05 — Gestión del Desarrollo y Capacitación

> **Criticidad:** MEDIA-ALTA · **Tier:** Pro · **Dependencias:** M02 (competencias por puesto), M06 (brechas del desempeño)
> **Procesos SERVIR cubiertos:** 17 (Capacitación), 18 (Progresión en la carrera)

---

## 1. Alcance

Cierra brechas de competencias mediante capacitación estructurada y soporta la progresión en la carrera de los colaboradores.

---

## 2. Sub-módulos

### 2.1 Diagnóstico de Necesidades de Capacitación (DNC)
- Identificación de brechas a partir de:
  - Evaluación de desempeño (M06)
  - Perfiles de puesto (M02)
  - Objetivos estratégicos (M01)
  - Cambios normativos
  - Solicitudes individuales
- Priorización de brechas (criticidad vs volumen)
- Matriz de competencias por rol

### 2.2 Plan de Desarrollo de las Personas (PDP)
**Obligatorio en sector público** (SERVIR).
- Plan anual aprobado
- Actividades por competencia/persona
- Presupuesto asignado
- Responsables y proveedores
- Indicadores de resultado

### 2.3 Gestión de capacitaciones
- Tipos:
  - **Formación laboral**: competencias para el puesto actual (corto plazo)
  - **Formación profesional**: desarrollo del servidor a mediano-largo plazo
  - **Inducción**: cubierta en M03.3
- Modalidades: presencial, virtual (síncrono/asíncrono), autoinstructivo, on-the-job
- Catálogo de actividades (ofertas internas + externas)
- Inscripciones y listas de espera
- Registro de asistencia
- Evaluación del participante (conocimiento, satisfacción)
- Evaluación del impacto (post-3 meses)
- Certificados digitales

### 2.4 LMS (Learning Management System) integrado
- Biblioteca de cursos e-learning (SCORM/xAPI)
- Videos, PDFs, podcasts, quizzes
- Rutas de aprendizaje por competencia/puesto
- Progreso individual
- Gamificación (puntos, badges, leaderboards)
- Microlearning (píldoras de 5-10 min)

### 2.5 Metodología 70-20-10 para PDI
- **70%**: aprendizaje experiencial (proyectos, asignaciones desafiantes)
- **20%**: aprendizaje social (mentoring, coaching, feedback)
- **10%**: aprendizaje formal (cursos, talleres)
- Plan de Desarrollo Individual (PDI) personalizado
- Seguimiento con el líder directo

### 2.6 Compromiso Post-Capacitación (obligación de permanencia)
Para capacitaciones significativas (>X horas o >X monto):
- Acuerdo firmado de permanencia mínima
- Penalidad por cese anticipado (reembolso proporcional)
- Integración con M04 (descuento de liquidación si aplica)

### 2.7 Progresión en la carrera
**Sector público:** concursos internos de ascenso con:
- Convocatoria interna
- Evaluación por comité
- Méritos (tiempo de servicios, capacitación, desempeño)
- Resolución de ascenso

**Sector privado:** líneas de carrera por familia de puestos:
- Mapa de carrera (de puesto A a puesto B)
- Requisitos para saltar de nivel
- Programas de identificación de alto potencial (HiPo)
- Nine-Box de performance × potencial (vinculado a M06)

---

## 3. Entidades principales

```
TrainingNeedAnalysis
├── CompetencyGap
│   ├── Competency
│   ├── CurrentLevel
│   ├── RequiredLevel
│   └── AffectedEmployees

PersonDevelopmentPlan (PDP anual - sector público)
├── DevelopmentAction
├── Budget
└── Owner

TrainingProgram
├── TrainingType (INDUCCION, FORMACION_LABORAL, FORMACION_PROFESIONAL)
├── DeliveryMode (PRESENCIAL, VIRTUAL_SINCRONO, VIRTUAL_ASINCRONO, MIXTO)
├── TrainingSession
│   ├── Schedule
│   ├── Instructor
│   ├── MaxCapacity
│   └── Location
├── Enrollment
│   ├── Employee
│   ├── Status (INSCRITO, EN_LISTA_ESPERA, APROBADO, RECHAZADO, COMPLETADO)
│   ├── Attendance
│   ├── Evaluation
│   └── Certificate
└── CommitmentAgreement (compromiso de permanencia)

LearningPath
├── PathStage
└── EnrolledPath

CareerProgression
├── CareerMap
│   └── CareerStep (puesto A → puesto B)
├── PromotionRequirements
├── PromotionContest (sector público)
└── HiPoIdentification
    └── NineBoxClassification
```

---

## 4. Workflows clave

### 4.1 Ciclo anual de capacitación (PDP)
```
Nov-Dic año anterior: DNC + levantamiento de necesidades
Diciembre: elaboración PDP
Enero: aprobación del PDP + presupuesto
Feb-Nov: ejecución de actividades
Mensual: seguimiento de avance
Diciembre: evaluación de impacto + reporte anual
```

### 4.2 Inscripción a capacitación
```
1. Colaborador ve catálogo / recibe invitación
2. Solicita inscripción con autorización del jefe
3. Jefe aprueba/rechaza
4. RRHH valida y confirma
5. Participante recibe confirmación + accesos
6. Asistencia y evaluación
7. Generación de certificado
8. Registro en legajo (M03.5)
```

### 4.3 Promoción/ascenso sector público (concurso interno)
```
1. Publicación de convocatoria interna
2. Postulación de servidores interesados
3. Evaluación de requisitos
4. Prueba de conocimientos
5. Evaluación de desempeño
6. Evaluación de capacitación
7. Cuadro de méritos
8. Resolución de ascenso
9. Actualización de nivel en CPE
10. Actualización de remuneración (M04)
```

---

## 5. Integraciones con otros módulos
- **M02** Organización → competencias del puesto
- **M03** Empleo → inducción, legajo (certificados)
- **M04** Compensación → descuento por compromiso incumplido
- **M06** Desempeño → brechas detectadas
- **M08** Asistencia → permisos por capacitación

---

## 6. Consideraciones especiales sector público

### 6.1 Tipos de capacitación SERVIR (Ley 30057)
- **Formación profesional**: financiada por el Estado, con compromiso de permanencia de 2x tiempo de la capacitación
- **Formación laboral**: capacitación de corto plazo vinculada al puesto actual
- **Capacitación obligatoria por ley**: ética, integridad, igualdad de género, prevención de hostigamiento, SST

### 6.2 Registro SERVIR
- Reporte periódico de capacitaciones ejecutadas
- Integración con SIDEP (Sistema de Información de Desempeño y Evaluación)

---

## 7. KPIs del módulo
- % cumplimiento PDP
- Horas de capacitación per cápita
- Inversión de capacitación / remuneración anual
- Tasa de asistencia a capacitaciones programadas
- Tasa de aprobación de evaluaciones
- NPS de capacitaciones
- % trabajadores con PDI activo
- Tasa de promoción interna vs externa
- ROI de capacitación (si se mide impacto en negocio)

---

## 8. Referencias normativas
- [Ley 30057 — Servicio Civil (Capítulo de Capacitación)](https://www.servir.gob.pe/)
- [D.S. 040-2014-PCM — Reglamento General Ley 30057](https://www.servir.gob.pe/)
- [D.S. 009-2010-ED — Capacitación en sector público](https://www.gob.pe/institucion/minedu/normas-legales/)
- [SERVIR — Directivas sobre capacitación](https://www.servir.gob.pe/)

---

## 9. MDs relacionados
- `modulos/02_organizacion_trabajo.md`
- `modulos/06_gestion_rendimiento.md`
- `modulos/03_gestion_empleo.md`
