# Módulo 09 — Procedimiento Disciplinario

> **Criticidad:** MEDIA · **Tier:** Pro · **Dependencias:** M03 (empleados), M05 (capacitación), M06 (desempeño)
> **Proceso SERVIR cubierto:** 12 (Procedimiento disciplinario)

---

## 1. Alcance

Gestiona el ciclo disciplinario completo: desde la detección de la falta hasta la ejecución de la sanción, con plena garantía procesal.

**Dualidad crítica:**
- **Sector privado**: PID (Procedimiento Interno Disciplinario) según RIT y LPCL
- **Sector público**: PAD (Procedimiento Administrativo Disciplinario) según Ley 30057 y su reglamento

---

## 2. Sector privado — PID (D.Leg. 728 + RIT)

### 2.1 Marco normativo
- Art. 23-34 LPCL (causas justas de despido)
- Reglamento Interno de Trabajo (RIT) de la empresa
- Jurisprudencia del Tribunal Constitucional sobre debido proceso

### 2.2 Tipificación de faltas (ejemplos de RIT típico)
**Faltas leves:**
- Tardanzas reiteradas
- Falta de diligencia menor
- Incumplimiento de políticas internas no críticas

**Faltas graves:**
- Inasistencias injustificadas
- Incumplimiento de instrucciones del jefe
- Disminución deliberada del rendimiento
- Daño a propiedad de la empresa
- Agresión verbal

**Faltas muy graves (causal de despido — Art. 25 LPCL):**
- Apropiación consumada o frustrada
- Uso o entrega a terceros de información reservada
- Concurrencia reiterada en estado de embriaguez o drogas
- Actos de violencia, grave indisciplina o injuria
- Daño intencional a bienes
- Abandono de trabajo (ausencia 3+ días consecutivos o 5 no consecutivos en 30 días)
- Condena penal por delito doloso

### 2.3 Sanciones (según RIT)
| Sanción | Condiciones |
|---------|-------------|
| Amonestación verbal | Faltas leves, primer caso |
| Amonestación escrita | Faltas leves reiteradas o grave menor |
| Suspensión sin goce (1-30 días) | Faltas graves |
| Despido | Falta grave muy grave o reiterancia (Art. 25) |

### 2.4 Procedimiento (Art. 31-33 LPCL)
```
1. Detección de la falta (jefe, auditoría, denuncia)
2. Carta de preaviso/imputación
   - Descripción de los hechos
   - Tipificación de la falta
   - Plazo para descargo: mínimo 6 días naturales
3. Descargo del trabajador
4. Análisis del descargo por RRHH + área legal
5. Carta de despido (si se mantiene) o sanción alternativa
6. Trabajador puede impugnar judicialmente en 30 días hábiles
```

---

## 3. Sector público — PAD (Ley 30057 + D.Leg. 276)

### 3.1 Marco normativo
- **Ley 30057** (Servicio Civil) — régimen disciplinario unificado
- **D.S. 040-2014-PCM** — Reglamento
- **Directiva 02-2015-SERVIR/GPGSC**
- Para régimen 276 remanente: aplica PAD con adecuaciones

### 3.2 Ámbito de aplicación del PAD
Se aplica a:
- Servidores D.Leg. 276 (Carrera Administrativa)
- Servidores D.Leg. 728 del sector público
- Servidores CAS D.Leg. 1057
- Servidores bajo Ley 30057

### 3.3 Faltas graves y muy graves (Art. 85 Ley 30057)
Categorías relevantes:
- Incumplimiento de deberes
- Falta de probidad
- Negligencia en el desempeño
- Ausencias injustificadas
- Uso de la función para favorecimiento personal
- Hostigamiento sexual (tipo extremo de falta)
- Consumo de drogas en horario
- Actos contra la administración pública

### 3.4 Sanciones (Art. 88)
| Sanción | Autoridad competente |
|---------|---------------------|
| Amonestación verbal | Jefe inmediato |
| Amonestación escrita | Jefe inmediato con copia a legajo |
| Suspensión sin goce (1-365 días) | Titular de la entidad (previo PAD) |
| Destitución | Titular de la entidad (previo PAD) |

### 3.5 Órganos del PAD (Art. 93)
- **Órgano Instructor (ORI)**: conduce la fase instructiva
  - Jefe inmediato (para sanciones menores)
  - Oficina de RRHH (para sanciones mayores sobre personal general)
  - Secretario Técnico de Procesos Disciplinarios (apoyo)
- **Órgano Sancionador (OS)**: decide la sanción
  - Titular de la entidad (destitución)
  - Jefe de RRHH (suspensión)

### 3.6 Fases del PAD

**Fase Instructiva (ORI)**:
```
1. Pre-calificación de hechos (evaluar si amerita PAD)
2. Inicio del PAD — Resolución que da por iniciado
3. Notificación al servidor (con imputación detallada)
4. Plazo para descargo: 5 días hábiles (prorrogable hasta 5 más)
5. Actuación de pruebas
6. Informe del ORI con propuesta de sanción o archivo
```

**Fase Sancionadora (OS)**:
```
7. OS recibe expediente del ORI
8. Plazo para emitir resolución: 10 días hábiles
9. Notificación de resolución al servidor
```

**Recursos impugnatorios**:
```
10. Reconsideración: 15 días hábiles, ante mismo OS, con nueva prueba
11. Apelación: 15 días hábiles, ante Tribunal del Servicio Civil
12. Tribunal del Servicio Civil — resolución última instancia administrativa
13. Vía judicial: proceso contencioso administrativo (excepcional)
```

### 3.7 Plazos totales
- Desde inicio hasta resolución: **máximo 1 año** (salvo suspensión por medidas extraordinarias)
- Prescripción para iniciar PAD: **3 años** desde la comisión o conocimiento

### 3.8 Tribunal del Servicio Civil
- Resuelve apelaciones de sanciones (suspensión y destitución)
- Decisiones de observancia obligatoria se publican en El Peruano
- No susceptibles de recurso administrativo adicional

---

## 4. Registro Nacional de Sanciones de Destitución y Despido (RNSDD)

Obligación SERVIR: toda sanción firme de destitución y despido debe registrarse en el RNSDD para impedir que el servidor sancionado sea contratado en otra entidad pública.

---

## 5. Entidades principales

```
DisciplinaryCase
├── Employee
├── CaseType (PID / PAD)
├── Regime (728, CAS, 276, SERVIR)
├── Status (PRE_CALIFICACION, INICIADO, EN_DESCARGO, EN_RESOLUCION, RESUELTO, IMPUGNADO, FIRME)
├── OpeningDate
├── PrescriptionDeadline (3 años para PAD)

Infraction
├── Description
├── Classification (LEVE, GRAVE, MUY_GRAVE)
├── LegalBasis (artículo LPCL / Ley 30057 / RIT)
├── EvidenceDocument
└── WitnessStatements

ProcessStage
├── StageType (PRE_CALIFICACION, IMPUTACION, DESCARGO, PRUEBAS, INFORME_ORI, RESOLUCION_OS, IMPUGNACION)
├── StartDate, EndDate, Deadline
├── Responsible (jefe, ORI, OS, Tribunal)
├── Documents
└── Notifications (con acuse)

Hearing
├── Type (ORAL, ESCRITA)
├── Date
├── Attendees
└── Minutes

Discharge (descargo del servidor)
├── Date
├── Arguments
├── EvidencePresented
└── RequestedActions

Decision
├── Sanction (AMONESTACION_VERBAL, AMONESTACION_ESCRITA, SUSPENSION_X_DIAS, DESTITUCION, ABSOLUCION)
├── IssuedBy
├── IssuedDate
├── Justification
└── LegalBase

Appeal
├── Type (RECONSIDERACION, APELACION)
├── FiledBy
├── FiledDate
├── Grounds
└── Resolution
    ├── FAVORABLE
    ├── DESFAVORABLE
    └── PARCIAL

RNSDDRecord (sector público)
├── Employee
├── Sanction (DESTITUCION)
├── Date
├── Entity
└── SanctionDuration (si aplica inhabilitación)
```

---

## 6. Workflows clave

### 6.1 PID privado completo
```
1. Detección (jefe, auditoría, denuncia)
2. Evaluación inicial por RRHH + legal
3. Carta de preaviso (con hechos, tipificación, plazo descargo)
4. Descargo del trabajador
5. Evaluación del descargo
6. Decisión (sanción o archivo)
7. Carta de sanción / despido
8. Registro en legajo
9. Impacto en planilla (si aplica descuento o cese)
10. Cierre del caso
11. (Si hay demanda judicial) seguimiento externo
```

### 6.2 PAD público completo
```
Fase Pre-PAD (Secretaría Técnica):
  1. Evaluación de hechos
  2. Determinación de ORI competente
  3. Resolución de inicio de PAD

Fase Instructiva (ORI):
  4. Notificación al servidor
  5. Descargo (5 días hábiles + prórroga)
  6. Actuación de pruebas
  7. Informe del ORI con propuesta

Fase Sancionadora (OS):
  8. Recepción del expediente
  9. Resolución (10 días hábiles)
  10. Notificación

Fase Impugnatoria:
  11. Reconsideración (15 días)
  12. Apelación al Tribunal del Servicio Civil
  13. Resolución firme

Ejecución:
  14. Cumplimiento de la sanción
  15. Registro en legajo
  16. Registro en RNSDD (si destitución)
  17. Impacto en planilla
```

---

## 7. Garantías procesales (obligatorias)

- **Debido proceso**: derecho fundamental (Art. 139 Constitución)
- **Derecho de defensa**: abogado, testigos, pruebas
- **Motivación**: toda resolución debe fundamentarse
- **Proporcionalidad**: sanción debe ser proporcional a la falta
- **Non bis in idem**: no puede sancionarse dos veces por el mismo hecho
- **Tipicidad**: la falta debe estar previa y claramente tipificada
- **Presunción de inocencia**: hasta prueba de responsabilidad
- **Plazos razonables**: cumplimiento estricto de los plazos legales

---

## 8. Integraciones con otros módulos
- **M03** Empleo → legajo con historial disciplinario, baja en caso de destitución
- **M04** Compensación → descuento por suspensión sin goce, liquidación por destitución
- **M08** Asistencia → inasistencia injustificada como evidencia
- **M06** Desempeño → bajo desempeño reiterado como causal de PAD (sector público)
- **M07.1** Relaciones Laborales → hostigamiento sexual (tratamiento especial Ley 27942)

---

## 9. Consideraciones especiales

### 9.1 Hostigamiento sexual (Ley 27942 + D.S. 014-2019-MIMP)
- Tratamiento especial con **Comité de Intervención** paritario
- Medidas de protección en 1 día hábil
- Procedimiento distinto al PAD común
- Confidencialidad extrema
- Ver `normativa/N13_hostigamiento_sexual_27942.md`

### 9.2 Rehabilitación de sanciones
Sector público: después de cumplida la sanción y transcurrido un plazo (1 año para suspensión, 5 años para destitución bajo condiciones), puede pedirse rehabilitación administrativa que elimina el antecedente del legajo.

### 9.3 Medidas cautelares
Durante el PAD, el OS puede dictar medidas cautelares:
- Separación preventiva del puesto
- Cambio de puesto
- Rotación a otra sede
Con pago de remuneración mientras se resuelve.

---

## 10. KPIs del módulo
- Número de casos abiertos / cerrados por período
- Tiempo promedio de resolución (meta: <1 año para PAD)
- Distribución por tipo de falta
- Tasa de impugnaciones favorables
- Casos prescritos (indicador de mala gestión)
- Recurrencia disciplinaria (% reincidencia)

---

## 11. Referencias normativas
- [Ley 30057 — Servicio Civil (Título V Régimen Disciplinario)](https://www.servir.gob.pe/)
- [D.S. 040-2014-PCM — Reglamento](https://www.servir.gob.pe/)
- [Directiva 02-2015-SERVIR/GPGSC](https://www.servir.gob.pe/)
- [D.Leg. 728 TUO — Arts. 23-34 LPCL](https://infopublic.bpaprocorp.com/)
- [Ley 27942 — Hostigamiento Sexual](https://www.gob.pe/institucion/mimp/normas-legales/)
- [Tribunal del Servicio Civil — Precedentes](https://www.servir.gob.pe/)

---

## 12. MDs relacionados
- `normativa/N13_hostigamiento_sexual_27942.md`
- `modulos/03_gestion_empleo.md`
- `modulos/04_gestion_compensacion.md`
