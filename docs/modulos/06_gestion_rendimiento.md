# Módulo 06 — Gestión del Rendimiento (Evaluación de Desempeño)

> **Criticidad:** MEDIA-ALTA · **Tier:** Pro · **Dependencias:** M02 (competencias), M05 (capacitación deriva de brechas)
> **Proceso SERVIR cubierto:** 14 (Evaluación de desempeño)

---

## 1. Alcance

Permite evaluar, retroalimentar y desarrollar el rendimiento de los colaboradores de forma estructurada y periódica.

---

## 2. Sub-módulos

### 2.1 Ciclos de evaluación configurables
- Periodicidad: anual, semestral, trimestral, continua
- Tipos:
  - **90°**: jefe evalúa al colaborador
  - **180°**: jefe + autoevaluación
  - **360°**: jefe + pares + subordinados + autoevaluación + (clientes externos opcional)
  - **Evaluación por objetivos/OKRs**: seguimiento continuo

### 2.2 Formularios de evaluación
- Plantillas configurables por tenant
- Componentes típicos:
  - Cumplimiento de objetivos
  - Evaluación de competencias (técnicas + blandas)
  - Comportamientos esperados según cultura
  - Retroalimentación cualitativa
- Escalas: numéricas (1-5, 1-7), cualitativas (Excelente/Muy bueno/Bueno/Regular/Deficiente)
- Peso relativo de cada componente

### 2.3 OKRs (Objectives and Key Results)
- Definición trimestral/semestral
- Cascada: OKRs organizacionales → departamentales → individuales
- Key Results medibles (SMART)
- Check-ins periódicos (semanal/quincenal)
- % confianza/avance
- Calificación final: aspirational (0.7 = éxito) vs committed (1.0 esperado)

### 2.4 Gestión continua del desempeño
- 1-on-1s programados
- Feedback continuo (reconocimientos, sugerencias)
- Notas del manager
- Historial conversacional

### 2.5 Nine-Box Matrix (Performance × Potencial)
```
Potencial
  ↑
  │  Enigma     │  High Potential │  Star
  │  (P:B P:A)  │  (P:B P:M)      │  (P:A P:A)
  │─────────────┼────────────────┼──────────────
  │  Dilema     │  Core Player   │  High Performer
  │  (P:B P:B)  │  (P:M P:M)      │  (P:A P:M)
  │─────────────┼────────────────┼──────────────
  │  Risk       │  Sólido        │  Subutilizado
  │  (P:B P:B)  │  (P:M P:B)      │  (P:A P:B)
  │─────────────┴────────────────┴──────────────→
                                           Performance
```
- Clasificación automática según performance histórico + potencial
- Identificación de sucesores y HiPo
- Vinculación con M05 (planes de desarrollo diferenciados)

### 2.6 Planes de mejora del desempeño (PIP)
Para colaboradores con desempeño bajo:
- Acuerdo firmado con objetivos específicos
- Plazo definido (típicamente 30-90 días)
- Apoyo del manager
- Reevaluación al cierre
- Posibles resultados: ratificación, extensión, desvinculación

### 2.7 Evaluación SERVIR (sector público)
**Obligatoria según Ley 30057** y su reglamento:
- Formato oficial SERVIR
- Periodicidad anual
- Categorías: personal de rendimiento distinguido, buen rendimiento, rendimiento sujeto a observación, desaprobado
- Consecuencias:
  - Distinguido → beneficios (capacitación prioritaria, ascenso)
  - Observación → capacitación obligatoria, PIP
  - Desaprobado (2 años consecutivos) → causal de cese por bajo rendimiento
- Reporte a SERVIR (SIDEP)
- Derecho a impugnación ante Tribunal del Servicio Civil

---

## 3. Entidades principales

```
EvaluationCycle
├── CycleType (ANUAL, SEMESTRAL, TRIMESTRAL, CONTINUA)
├── CycleScope (90_GRADOS, 180_GRADOS, 360_GRADOS, OBJETIVOS)
├── Period (start, end)
├── EvaluationForm (plantilla)
│   ├── FormSection
│   │   ├── SectionType (OBJETIVOS, COMPETENCIAS, COMPORTAMIENTOS)
│   │   ├── Weight
│   │   └── Question/Criterion
│   └── Scale
└── EvaluationInstance (por empleado)
    ├── Evaluator (jefe, self, par, subordinado)
    ├── Response
    ├── FinalScore
    └── Status (PENDIENTE, EN_CURSO, COMPLETADO, VALIDADO)

Objective (OKR)
├── Type (ORG, DEPT, INDIVIDUAL)
├── OwnerEmployee
├── KeyResult (SMART)
│   ├── BaselineValue
│   ├── TargetValue
│   ├── CurrentValue
│   └── Confidence (0-100%)
├── CheckIn
│   ├── Date
│   ├── ProgressNotes
│   └── UpdatedConfidence
└── FinalScore

OneOnOne
├── ScheduledDate
├── AgendaItem
├── MeetingNotes
└── FollowUpAction

FeedbackEntry
├── From, To
├── Type (RECONOCIMIENTO, SUGERENCIA, OBSERVACION)
├── Visibility (PRIVADO, COMPARTIDO, PUBLICO)
└── Content

TalentGrid (Nine-Box)
├── Employee
├── PerformanceRating (B/M/A)
├── PotentialRating (B/M/A)
├── Box (uno de los 9)
└── AssessmentDate

PerformanceImprovementPlan (PIP)
├── Employee
├── StartDate, EndDate
├── Objectives
├── Support
├── CheckPoints
└── Outcome (RATIFICACION, EXTENSION, DESVINCULACION)

ServirEvaluation (sector público)
├── Employee
├── Period
├── Rating (DISTINGUIDO, BUENO, OBSERVACION, DESAPROBADO)
├── Comments
├── SidepReport
└── AppealToServirTribunal
```

---

## 4. Workflows clave

### 4.1 Ciclo de evaluación 360°
```
1. Setup del ciclo (RRHH define periodo, plantilla, alcance)
2. Preparación (cada evaluado selecciona pares, subordinados)
3. Apertura de formularios
4. Autoevaluación → Evaluación pares → Evaluación subordinados → Evaluación jefe
5. Consolidación (score ponderado)
6. Sesión de feedback 1-on-1 con el jefe
7. Acuerdo de plan de desarrollo (vincula con M05)
8. Clasificación en Nine-Box
9. Reporte ejecutivo
10. Cierre del ciclo
```

### 4.2 OKRs trimestrales
```
Trimestre:
  Semana 1: definición OKRs (top-down + bottom-up)
  Semanas 2-12: check-ins quincenales
  Semana 13: calificación final + retrospectiva
```

### 4.3 Evaluación SERVIR anual
```
1. Planificación anual (RRHH + gerentes)
2. Capacitación a evaluadores (obligatoria)
3. Ejecución según formato oficial
4. Revisión por Comité de Evaluación
5. Notificación a evaluados
6. Periodo de impugnación (reconsideración 15 días)
7. Resolución de impugnaciones
8. Apelación al Tribunal del Servicio Civil (si aplica)
9. Reporte a SERVIR vía SIDEP
10. Consecuencias (beneficios, PIP, cese)
```

---

## 5. Integraciones con otros módulos
- **M02** Organización → competencias y KPIs del puesto
- **M03** Empleo → legajo con historial de evaluaciones
- **M04** Compensación → ajustes salariales y bonos basados en desempeño
- **M05** Capacitación → brechas detectadas alimentan PDI
- **M11** ATS → sucesión desde candidatos internos

---

## 6. Consideraciones técnicas

### 6.1 Confidencialidad
- Evaluaciones de pares y subordinados: **anónimas por default** en 360°
- Feedback individual tiene permission level alto (6+)
- Reportes agregados protegen identidad (mínimo N=3 evaluadores)

### 6.2 Sesgo del evaluador
- Calibración obligatoria entre evaluadores
- Distribución forzada opcional (% esperado por categoría)
- Detección de patrones de sesgo (inflación, sesgo central, sesgo por género)

### 6.3 Adaptación cultural
- Escalas en español natural
- Consideración de enfoque intercultural SERVIR
- Plantillas distintas por rol (directivo, mando medio, contribuidor individual)

---

## 7. KPIs del módulo
- Tasa de completitud de evaluaciones (% ciclo cerrado a tiempo)
- Distribución de calificaciones (identifica sesgos)
- Correlación entre evaluación y retención
- % colaboradores con OKRs definidos
- % colaboradores con PDI activo
- Tasa de 1-on-1s realizados vs planificados
- NPS del proceso de evaluación

---

## 8. Referencias normativas
- [Ley 30057 — Servicio Civil (Capítulo Evaluación)](https://www.servir.gob.pe/)
- [D.S. 040-2014-PCM — Reglamento Ley 30057](https://www.servir.gob.pe/)
- [SERVIR — Directivas de Evaluación de Desempeño](https://www.servir.gob.pe/)
- [SERVIR — SIDEP](https://www.servir.gob.pe/)

---

## 9. MDs relacionados
- `modulos/05_gestion_desarrollo_capacitacion.md`
- `modulos/02_organizacion_trabajo.md`
- `modulos/04_gestion_compensacion.md`
