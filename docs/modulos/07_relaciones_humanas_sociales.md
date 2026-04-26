# Módulo 07 — Gestión de Relaciones Humanas y Sociales

> **Criticidad:** ALTA · **Tier:** Pro (privado) / GovTech (público) · **Dependencias:** Módulo 03 (Empleados), Módulo 10 (Portal)
>
> Este módulo agrupa los 5 procesos SERVIR del Subsistema de Relaciones Humanas y Sociales. Es obligatorio para sector público y estratégico para sector privado (retención, cultura, cumplimiento Ley 29783 SST y Ley 27942 hostigamiento).

---

## 1. Alcance funcional

### 1.1 Sub-módulos (los 5 procesos SERVIR)
| Código | Sub-módulo | Proceso SERVIR | Marco normativo |
|--------|-----------|----------------|------------------|
| 07.1 | Relaciones Laborales individuales y colectivas | 19 | DLeg 25593, convenios colectivos |
| 07.2 | Seguridad y Salud en el Trabajo | 20 | Ley 29783 + D.S. 005-2012-TR |
| 07.3 | Bienestar Social | 21 | SERVIR Subsistema |
| 07.4 | Cultura y Clima Organizacional | 22 | RPE 150-2017-SERVIR-PE |
| 07.5 | Comunicación Interna | 23 | RPE 151-2017-SERVIR-PE |

---

## 2. Sub-módulo 07.1 — Relaciones Laborales

### 2.1 Alcance
Gestión de la relación entre la organización y los colectivos laborales (sindicatos) y el tratamiento de reclamos individuales.

### 2.2 Funcionalidades
- Registro de sindicatos afiliados (razón social, tipo, dirigentes)
- Padrón de trabajadores sindicalizados
- Gestión de cuotas sindicales (descuento en planilla → integración Módulo 04)
- Pliegos de reclamos y negociación colectiva
- Convenios colectivos vigentes (vigencia, cláusulas, beneficios pactados)
- Registro de reclamos individuales
- Actas de reunión con sindicatos
- Registro de huelgas, paros, medidas de fuerza

### 2.3 Entidades principales
```
Union (sindicato)
├── UnionMembership (afiliación trabajador)
├── CollectiveBargaining (negociación colectiva)
│   ├── BargainingRound (ronda de negociación)
│   └── CollectiveAgreement (convenio firmado)
├── IndividualClaim (reclamo individual)
└── LaborAction (huelga/paro)
```

### 2.4 Workflows clave
- **Negociación colectiva:** pliego → instalación mesa → rondas → acta → convenio → registro MTPE
- **Reclamo individual:** recepción → análisis → respuesta → escalamiento si no resuelto

### 2.5 Integración sector público
- Registro en **Tabla Paramétrica 37 SUNAT** (Organizaciones Sindicales de Servidores Públicos, incorporada por RM 170-2023-TR)
- Reporte automático a SERVIR

---

## 3. Sub-módulo 07.2 — Seguridad y Salud en el Trabajo (SST)

### 3.1 Alcance
Cumplimiento total de la **Ley 29783** y su reglamento D.S. 005-2012-TR. Este es el sub-módulo con mayor densidad normativa.

### 3.2 Obligaciones por tamaño de empresa
| # Trabajadores | Obligación | Soporte SaaS |
|---------------|-----------|--------------|
| <20 | Supervisor de SST | Registro y agenda |
| ≥20 | Comité paritario de SST + Reglamento Interno SST | Módulo completo |
| Actividades de riesgo | SCTR obligatorio | Integración con planilla |

### 3.3 Los 9 registros obligatorios (Ley 29783)
| # | Registro | Periodicidad |
|---|----------|-------------|
| 1 | Accidentes de trabajo e incidentes peligrosos | Cuando ocurre + reporte MTPE si >1 día perdido |
| 2 | Exámenes médicos ocupacionales (EMO) | Pre-ocupacional, periódico, retiro |
| 3 | Monitoreo de agentes (físicos, químicos, biológicos, ergonómicos, psicosociales) | Anual mínimo |
| 4 | Inspecciones internas de seguridad y salud | Mensual/trimestral |
| 5 | Estadísticas de SST | Mensual |
| 6 | Equipos de seguridad o emergencia | Cuando se entregan |
| 7 | Inducción, capacitación, entrenamiento y simulacros | Cuando ocurren |
| 8 | Auditorías | Anual |
| 9 | Actas del Comité de SST | Por reunión (mínimo mensual) |

### 3.4 Funcionalidades SST en el SaaS

#### 3.4.1 Comité de SST
- Constitución paritaria (empleador + trabajadores)
- Elección de representantes
- Calendario de sesiones (mínimo mensual)
- Actas digitales con firmas
- Acuerdos y seguimiento

#### 3.4.2 IPERC (Identificación de Peligros, Evaluación de Riesgos y Controles)
- Matriz IPERC por área/puesto
- Metodología Magnitud × Frecuencia × Probabilidad
- Clasificación: Trivial, Tolerable, Moderado, Importante, Intolerable
- Controles propuestos (jerarquía: eliminación > sustitución > ingeniería > administrativos > EPP)
- Versionado y revisión periódica

#### 3.4.3 Mapa de Riesgos
- Plano de instalaciones con riesgos georreferenciados
- Señalización por zona
- Descarga para impresión/exposición

#### 3.4.4 Exámenes Médicos Ocupacionales (EMO)
- Catálogo por puesto/riesgo
- Calendario de EMO periódicos
- Alertas de vencimiento (retiro <3 meses, periódico <6 meses)
- Resultados médicos (campos con permlevel 9, privacidad máxima)
- Recomendaciones de aptitud (apto, apto con restricciones, no apto)
- **CRÍTICO:** los datos de salud son **datos sensibles** (Ley 29733) — cifrado obligatorio

#### 3.4.5 Accidentes e Incidentes
- Registro con clasificación (leve, incapacitante temporal, incapacitante permanente, mortal)
- Investigación con árbol de causas
- Plan de acción correctiva
- **Reporte automático al MTPE** si corresponde (accidente mortal en 24h, incapacitante en 10 días)
- Integración con descanso médico (Módulo 08)

#### 3.4.6 Plan Anual SST
Obligatorio, con 9 componentes mínimos:
1. Alcance y objetivos
2. Reglamento Interno SST
3. Política SST
4. IPERC actualizada
5. Organización y responsabilidades
6. Capacitación y entrenamiento
7. Procedimientos
8. Inspecciones, auditorías y EMO
9. Presupuesto

#### 3.4.7 Capacitaciones de SST
- Mínimo 4 capacitaciones al año
- Contenidos por rol/riesgo
- Registro de asistencia con firma
- Certificados

### 3.5 Entidades principales
```
SSTCommittee
├── CommitteeMember
├── CommitteeMeeting
│   └── MeetingMinutes
IPERCMatrix
├── Hazard
├── Risk
└── Control
RiskMap
EMOCatalog
├── EMOScheduled
└── EMOResult (cifrado)
Accident
├── AccidentInvestigation
└── AccidentCorrectiveAction
AnnualSSTPlan
SSTTraining
└── SSTTrainingAttendance
```

### 3.6 Infracciones SUNAFIL (recordatorio)
- Leves: 0.45 - 4.5 UIT (1-10 trab.) hasta 11.07 - 26.12 UIT (+1000 trab.)
- Graves: 1.35 - 22.50 UIT hasta 38.36 - 77.61 UIT
- **Muy graves: 4.50 - 45 UIT hasta 131.73 - 233.13 UIT**
- Tope conjunto: 300 UIT (= S/ 1,650,000 en 2026)

> **Detalle completo:** → `normativa/N10_sst_ley29783.md`

---

## 4. Sub-módulo 07.3 — Bienestar Social

### 4.1 Alcance (según RPE SERVIR)
Actividades orientadas a propiciar un buen ambiente de trabajo y mejorar la calidad de vida.

### 4.2 Tipologías
| Tipo | Ejemplos |
|------|----------|
| Asistencial | Seguro complementario, apoyo por enfermedad, apoyo por fallecimiento familiar |
| Recreativo | Paseos, actividades deportivas, campeonatos internos |
| Cultural | Eventos culturales, visitas guiadas, conciertos |
| Deportivo | Campeonatos, maratones, clases grupales |
| Celebraciones | Día del trabajador, aniversario institucional, fiestas navideñas |
| Familiar | Día del niño, convenios con colegios, navidad del niño |

### 4.3 Funcionalidades
- Plan Anual de Bienestar Social
- Catálogo de convenios corporativos (descuentos, beneficios)
- Gestión de eventos (invitaciones, inscripciones, asistencia)
- Encuestas de satisfacción post-evento
- Presupuesto asignado y ejecutado
- Galería fotográfica

### 4.4 Entidades principales
```
WelfareProgram (anual)
├── WelfareActivity
│   ├── ActivityRegistration
│   └── ActivityFeedback
├── WelfarePartner (convenio)
│   └── PartnerBenefit
└── WelfareBudget
```

---

## 5. Sub-módulo 07.4 — Cultura y Clima Organizacional

### 5.1 Alcance (según RPE 150-2017-SERVIR-PE)
**Cultura organizacional**: forma característica de pensar y hacer las cosas. Principios, valores, creencias, conductas, normas, símbolos.
**Clima organizacional**: percepción colectiva de satisfacción de los servidores sobre el ambiente de trabajo.

### 5.2 Proceso SERVIR (obligatorio para sector público)
```
Compromiso alta dirección
    ↓
Medición y análisis
    ↓
Comunicación de resultados
    ↓
Plan de acción de mejora
    ↓
Ejecución del plan
    ↓
(ciclo anual)
```

### 5.3 Funcionalidades del sub-módulo

#### 5.3.1 Definición de cultura
- Registro de misión, visión, valores
- Comportamientos esperados por cada valor
- Símbolos culturales (logo, mascota, lemas)
- Historias (storytelling organizacional)

#### 5.3.2 Encuestas de clima
- **Plantillas pre-cargadas alineadas con SERVIR** (5 dimensiones oficiales):
  1. **Ambiente**: seguridad de instalaciones, entorno de trabajo, trato entre servidores, prejuicios/discriminación, equilibrio vida-trabajo
  2. **Motivación y sentido de pertenencia**: trabajo en equipo, aporte a objetivos, orgullo, identificación con valores
  3. **Dirección y liderazgo**: comportamiento ético del liderazgo, comunicación del jefe, retroalimentación
  4. **Desarrollo profesional**: igualdad de oportunidades, reconocimiento, capacitación, línea de carrera
  5. **Gestión del recurso humano**: procesos de bienestar, selección justa, evaluación de desempeño
- Plantillas adicionales: Great Place To Work, Hay Group, eNPS
- Encuestas anónimas con cohortes (área, sede, género, edad, antigüedad)
- Integración con app móvil (respuestas rápidas)
- Análisis automático (promedios, brechas, outliers)
- Análisis cualitativo con NLP sobre respuestas abiertas

#### 5.3.3 Dashboards de clima
- eNPS (Employee Net Promoter Score)
- Índice de clima por dimensión
- Evolución histórica
- Comparación entre áreas
- Mapa de calor

#### 5.3.4 Plan de acción cultural/clima
- Por cada brecha detectada, definir iniciativas
- Responsables, fechas, recursos
- Seguimiento de ejecución
- Medición de impacto

### 5.4 Entidades principales
```
CultureDefinition (misión, visión, valores)
├── CultureValue
│   └── ExpectedBehavior
ClimateSurveyTemplate
├── SurveyDimension (5 oficiales SERVIR)
│   └── SurveyQuestion
ClimateSurvey
├── SurveyResponse (anónima)
├── SurveyAnalysis
└── SurveyReport
CultureActionPlan
└── CultureInitiative
```

### 5.5 Ejemplo de dimensiones y preguntas (SERVIR)

**Dimensión: Ambiente**
- "Me siento seguro en mis instalaciones de trabajo"
- "El trato entre servidores es respetuoso"
- "Existe equilibrio entre mi vida laboral y familiar"
- "No he percibido discriminación en mi entorno laboral"

**Dimensión: Motivación y sentido de pertenencia**
- "Me siento orgulloso de trabajar en esta entidad"
- "Conozco cómo mi trabajo contribuye a los objetivos"
- "Me identifico con los valores de la organización"

**Dimensión: Dirección y liderazgo**
- "Mi jefe actúa con ética e integridad"
- "Recibo retroalimentación periódica sobre mi desempeño"
- "Mi jefe comunica claramente las expectativas"

---

## 6. Sub-módulo 07.5 — Comunicación Interna

### 6.1 Alcance (según RPE 151-2017-SERVIR-PE)
> "Transmitir los objetivos, misión, visión, metas y valores estratégicos de la entidad, lo que genera compromiso y sentido de pertenencia. Permite que los servidores puedan comunicarse con la alta dirección."

### 6.2 Proceso SERVIR
```
Diagnóstico de necesidades de comunicación
    ↓
Identificación de audiencia de interés
    ↓
Definición del mensaje
    ↓
Identificación de medios/canales
    ↓
Período oportuno para transmitir
    ↓
Transmisión
    ↓
Medición de efectividad
```

### 6.3 Funcionalidades

#### 6.3.1 Canales de comunicación
- **Feed institucional** (timeline tipo red social interna)
- **Newsletter digital** (periodicidad configurable, segmentable)
- **Mensajería directa** con RRHH y con jefaturas
- **Notificaciones push** (app móvil)
- **Cartelera digital** (para zonas sin acceso PC)
- **Streaming en vivo** (town halls, eventos institucionales)
- **Encuestas rápidas / pulse surveys**

#### 6.3.2 Gestión de campañas
- Planificador editorial
- Segmentación de audiencia (área, sede, región lingüística, puesto)
- Aprobación por el oficial de comunicaciones
- Programación de envío
- Métricas de alcance y engagement

#### 6.3.3 Consideraciones especiales SERVIR
- **Enfoque de interculturalidad**: soporte de lenguas originarias (quechua, aimara, awajún, shipibo, etc.) en ámbitos con lengua oficial
- **Enfoque de género**: lenguaje inclusivo
- **Enfoque de discapacidad**: accesibilidad (lectores de pantalla, subtítulos, traducción a lengua de señas)

#### 6.3.4 Comunicación descendente, ascendente y horizontal
- **Descendente**: desde la alta dirección hacia los trabajadores (comunicados, boletines)
- **Ascendente**: desde los trabajadores hacia la alta dirección (buzón de sugerencias, encuestas pulse)
- **Horizontal**: entre pares / áreas (foros, canales temáticos)

### 6.4 Entidades principales
```
CommunicationPlan (anual)
├── CommunicationAudience
├── CommunicationChannel
├── CommunicationCampaign
│   ├── Post / Newsletter / Notification
│   ├── AudienceSegment
│   └── CampaignMetrics
├── FeedPost (timeline institucional)
│   ├── PostReaction
│   └── PostComment
├── SuggestionBox
└── PulseSurvey
```

### 6.5 Métricas de comunicación interna
- Tasa de apertura (newsletters, emails)
- Tasa de clics
- Engagement por post (reacciones, comentarios)
- Alcance por segmento
- Tiempo promedio de lectura
- eNPS específico de comunicación
- Encuestas de percepción sobre información recibida

---

## 7. Dualidad sector privado / sector público

| Aspecto | Sector privado | Sector público (SERVIR) |
|---------|----------------|-------------------------|
| Obligatoriedad SST | Sí (Ley 29783) | Sí + reportes adicionales a SERVIR |
| Encuesta de clima | Recomendada | Obligatoria (RPE 150-2017) |
| Plan de comunicación interna | Recomendado | Obligatorio (RPE 151-2017) |
| Plan Anual Bienestar | Recomendado | Obligatorio |
| Idiomas | Español | Español + lenguas originarias cuando aplique |
| Registro sindicatos | MTPE | Tabla Paramétrica 37 SUNAT |
| Cuotas sindicales | Descuento voluntario | Descuento regulado |

---

## 8. Integraciones con otros módulos

| Módulo | Interacción |
|--------|-------------|
| 04 Compensación | Cuotas sindicales, SCTR, subsidios EsSalud |
| 08 Asistencia | Descansos médicos por accidente, licencias sindicales |
| 10 Portal empleado | Encuestas, feed, newsletter, eventos, sugerencias |
| 12 Analítica | Dashboards de clima, eNPS, riesgos SST |

---

## 9. Consideraciones de datos personales (Ley 29733 + D.S. 016-2024-JUS)

Este módulo maneja **datos sensibles**:
- Datos de salud (EMO, accidentes, descansos médicos): permlevel 9, cifrado AES-256
- Respuestas de encuestas: anonimización obligatoria
- Pertenencia sindical: dato sensible, tratamiento con consentimiento expreso

**Obligaciones del sistema:**
- Registro del banco de datos ante ANPD
- Política de retención (EMO: 5 años post-cese mínimo)
- Notificación de incidentes a ANPD en 48h
- Derechos ARCO + portabilidad + no decisiones automatizadas

> **Detalle completo:** → `normativa/N11_proteccion_datos_personales.md`

---

## 10. Referencias normativas
- [SERVIR - Guía Cultura y Clima RPE 150-2017](https://storage.servir.gob.pe//normatividad/Resoluciones/PE-2017/Res150-2017-SERVIR-PE.pdf)
- [SERVIR - Guía Comunicación Interna RPE 151-2017](https://cdn.www.gob.pe/uploads/document/file/1347113/)
- [Ley 29783 - SST](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [D.S. 005-2012-TR - Reglamento SST](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [Ley 27942 - Hostigamiento Sexual](https://www.gob.pe/institucion/mimp/normas-legales/)
- [Directiva 002-2014-SERVIR/GDRSH](https://www.servir.gob.pe/)

---

## 11. Roadmap de implementación
1. **Fase 2a** — SST básico (Comité, registros 1, 4, 5, 9)
2. **Fase 2b** — Clima (encuestas con dimensiones SERVIR + dashboards)
3. **Fase 3a** — Comunicación interna (feed + newsletter + segmentación)
4. **Fase 3b** — Bienestar (plan anual + convenios)
5. **Fase 3c** — Relaciones laborales completas (sindicatos + negociación)
6. **Fase 4** — IA para análisis cualitativo + streaming en vivo
