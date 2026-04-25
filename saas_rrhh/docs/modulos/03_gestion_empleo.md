# Módulo 03 — Gestión del Empleo

> **Criticidad:** ALTA · **Tier:** Starter · **Dependencias:** Módulo 02 (Puestos)
>
> Gestiona el ciclo de vida completo del trabajador: desde la selección hasta la desvinculación. Cubre los procesos SERVIR 5-13.

---

## 1. Alcance y sub-módulos

| Código | Sub-módulo | Proceso SERVIR | Aplicación |
|--------|-----------|----------------|-----------|
| 03.1 | Selección | 5 | Privado + Público |
| 03.2 | Vinculación | 6 | Privado + Público |
| 03.3 | Inducción | 7 | Privado + Público (RPE 265-2017) |
| 03.4 | Período de prueba | 8 | Privado + Público |
| 03.5 | Administración de Legajos | 9 | Privado + Público |
| 03.6 | Desplazamiento | 11 | Principalmente Público |
| 03.7 | Desvinculación | 13 | Privado + Público |

(El proceso SERVIR 10 "Control de asistencia" se gestiona en el Módulo 08; el 12 "Procedimiento disciplinario" en el Módulo 09.)

---

## 2. Sub-módulo 03.1 — Selección

### 2.1 Alcance
Gestiona el proceso de búsqueda, evaluación y selección de candidatos para un puesto vacante.

### 2.2 Funcionalidades
- Requisición de personal (alta autorizada por jefatura + RRHH + finanzas)
- Publicación de convocatoria (interna, externa, mixta)
- **Convocatoria pública** (sector público) con bases oficiales, plazos obligatorios y cumplimiento de transparencia
- Recepción de candidaturas
- Filtros automáticos (match con perfil del puesto → Módulo 02)
- Evaluaciones: curricular, conocimientos, psicolaboral, entrevistas
- Calificación por etapas (con puntajes y pesos)
- Cuadro de méritos
- Resultado final y comunicación a candidatos
- Generación de lista de espera
- Integración con Módulo 11 (ATS avanzado)

### 2.3 Flujo de selección sector público (SERVIR)
```
1. Solicitud de requerimiento de personal
2. Aprobación y autorización presupuestal
3. Elaboración de bases
4. Publicación en portal institucional + SERVIR (7 días hábiles mínimo)
5. Recepción de postulaciones
6. Evaluación curricular (eliminatoria)
7. Prueba de conocimientos (eliminatoria, nota mínima 14/20)
8. Evaluación psicolaboral (referencial)
9. Entrevista personal (eliminatoria)
10. Cuadro de méritos final
11. Publicación de resultados
12. Notificación al ganador
13. Vinculación
```

### 2.4 Entidades
```
PersonnelRequisition
├── JobPosting
│   ├── JobApplication
│   │   ├── Candidate
│   │   └── ApplicationDocuments
│   ├── SelectionStage
│   │   └── CandidateEvaluation
│   └── MeritRanking
```

---

## 3. Sub-módulo 03.2 — Vinculación

### 3.1 Alcance
Formalización del vínculo laboral: contrato, registros oficiales, entrega de documentos.

### 3.2 Funcionalidades
- Generación automática de contrato según régimen y tipo contractual (modalidad)
- Firma electrónica del contrato
- **Registro en T-Registro SUNAT** (alta) dentro de plazo legal
- Registro en EsSalud / EPS
- Afiliación a AFP / ONP (o validación si ya está afiliado)
- Apertura de cuenta haberes (si aplica)
- Entrega de documentos obligatorios:
  - Copia del contrato
  - Reglamento Interno de Trabajo (RIT)
  - Reglamento Interno de SST
  - Código de ética
  - Política de protección de datos (consentimiento expreso)
  - Manual de funciones del puesto
- Registro para efectos de SCTR si aplica

### 3.3 Tipos de contrato (régimen 728)
| Tipo | Plazo máx | Característica |
|------|-----------|----------------|
| Indefinido (indeterminado) | Sin plazo | Estabilidad plena |
| Por inicio o incremento de actividad | 3 años | Nueva actividad |
| Por necesidad de mercado | 5 años | Incremento coyuntural |
| Por reconversión empresarial | 2 años | Cambio tecnológico |
| Ocasional | 6 meses | Necesidad transitoria |
| De suplencia | Sin plazo (mientras dure) | Reemplazar titular |
| De emergencia | Según dure la emergencia | Caso fortuito |
| Obra determinada o servicio específico | Según obra | Proyectos |
| Intermitente | Indefinido | Labor discontinua |
| De temporada | Cada temporada | Labor estacional |
| A tiempo parcial | Sin plazo | <4 horas diarias |

**Tope conjunto de contratos sujetos a modalidad:** 5 años. Superado este plazo se **desnaturaliza** a indeterminado (Art. 77 LPCL).

### 3.4 Integración T-Registro (alta)
- Archivo de texto plano estructurado según Anexo 3 SUNAT
- Validación con PVS antes de carga
- Plazo: hasta el primer día de prestación efectiva de servicios
- Campos obligatorios: datos del empleador, del trabajador, del contrato, régimen laboral, régimen pensionario, régimen de salud, derechohabientes

### 3.5 Entidades
```
Contract
├── ContractType (modalidad)
├── ContractRegimen (728/CAS/276/etc.)
├── ContractStatus (VIGENTE/SUSPENDIDO/TERMINADO)
├── ContractDocument
├── TRegistroDeclaration
└── ContractAddendum (modificaciones)
```

---

## 4. Sub-módulo 03.3 — Inducción

### 4.1 Alcance (RPE 265-2017-SERVIR-PE)
Proceso de integración del nuevo servidor/trabajador al entorno institucional, puesto, y equipo.

### 4.2 Tipos de inducción
| Tipo | Contenido | Duración |
|------|-----------|----------|
| **General** | Misión, visión, valores, estructura, políticas generales | 1-3 días |
| **Específica** | Funciones del puesto, procesos del área, herramientas | 1-4 semanas |
| **Técnica** | Capacitación técnica específica si corresponde | Variable |

### 4.3 Funcionalidades
- Plan de inducción personalizado por puesto/área
- Checklist de tareas de primer día, primera semana, primer mes
- Material multimedia (videos, PDFs, interactivos)
- Asignación de "buddy" o mentor
- Reuniones de bienvenida agendadas
- Evaluación post-inducción
- Certificado de finalización
- **Sector público**: inducción puede ser en **lengua originaria** si corresponde al ámbito territorial

### 4.4 Entidades
```
InductionPlan
├── InductionTask
├── InductionMaterial
├── InductionMentor
└── InductionEvaluation
```

---

## 5. Sub-módulo 03.4 — Período de Prueba

### 5.1 Marco normativo
| Régimen | Duración | Observaciones |
|---------|----------|---------------|
| 728 - Personal común | 3 meses | Superado = estabilidad |
| 728 - Trabajadores calificados | 6 meses | Con pacto escrito |
| 728 - Personal de dirección / confianza | 12 meses | Con pacto escrito |
| MYPE Pequeña | 3 meses | |
| CAS | No aplica | Contrato a plazo |
| 276 | 3 años para adquirir Carrera | Concurso previo |

### 5.2 Funcionalidades
- Alerta de vencimiento de período de prueba (configurable: 30 días antes, 15 días antes)
- Evaluación del período de prueba
- Decisión: ratificación o no renovación
- Notificación al trabajador
- Actualización del estado contractual

---

## 6. Sub-módulo 03.5 — Administración de Legajos

### 6.1 Alcance
Expediente digital completo y permanente del trabajador.

### 6.2 Contenido obligatorio del legajo
1. **Datos personales** (DNI, fotografía, dirección, estado civil, derechohabientes)
2. **Datos académicos** (diplomas, certificados, colegiatura, constancias)
3. **Experiencia laboral previa**
4. **Contrato vigente y addendas**
5. **Declaraciones juradas** (no parentesco, no incompatibilidad, impedimentos, intereses)
6. **Documentos de identidad y CUSPP**
7. **Historial de puestos ocupados en la entidad**
8. **Evaluaciones de desempeño**
9. **Capacitaciones recibidas**
10. **Reconocimientos y felicitaciones**
11. **Sanciones disciplinarias**
12. **Licencias otorgadas**
13. **Exámenes médicos ocupacionales** (acceso restringido permlevel 9)
14. **Accidentes laborales** (acceso restringido)
15. **Documentos de cese** (cuando aplique)

### 6.3 Funcionalidades
- Upload de documentos con OCR
- Clasificación automática por tipo
- Firma electrónica de documentos
- Versionado
- **Control de acceso granular por tipo de documento** (permission levels)
- Búsqueda full-text
- Exportación completa del legajo (PDF consolidado)
- Retención según norma (mínimo 5 años post-cese)

### 6.4 Protección de datos (Ley 29733)
- Datos sensibles (salud, biometría): cifrado AES-256
- Registro del banco de datos ante ANPD
- Consentimiento expreso para tratamiento
- Derechos ARCO
- Portabilidad (el trabajador puede solicitar exportación completa)

### 6.5 Entidades
```
DigitalDossier (unique per employee)
├── DossierSection (13 secciones mínimas)
│   └── DossierDocument
│       ├── DocumentMetadata
│       ├── DocumentVersion
│       └── DocumentAccessLog (audit)
```

---

## 7. Sub-módulo 03.6 — Desplazamiento

### 7.1 Alcance (principalmente sector público)
Movimientos del servidor dentro de la administración pública.

### 7.2 Tipos de desplazamiento (D.Leg. 276 y normas SERVIR)
| Tipo | Descripción | Duración | Remuneración |
|------|-------------|----------|--------------|
| **Rotación** | Cambio dentro de misma entidad | Permanente o temporal | Mantiene |
| **Encargatura** | Asumir temporalmente otro puesto | Hasta 1 año | Asume la del puesto encargado |
| **Destaque** | Prestación de servicios en otra entidad | Hasta 12 meses prorrogable | Origen asume |
| **Comisión de servicios** | Desempeño de labor específica fuera | Según comisión | Origen asume + viáticos |
| **Designación** | Asumir cargo de confianza | Mientras dure designación | Del cargo designado |
| **Transferencia** | Cambio definitivo a otra entidad | Permanente | Según nueva entidad |
| **Permuta** | Intercambio de puestos entre servidores | Permanente | Según acuerdo |

### 7.3 Funcionalidades
- Solicitud formal de desplazamiento
- Flujo de aprobaciones según tipo (jefe directo → RRHH → titular)
- Resolución administrativa generada automáticamente
- Actualización del registro del servidor
- Notificación a Tesorería si afecta planilla
- Fecha efectiva de inicio y término
- Renovaciones y prórrogas

### 7.4 Entidades
```
Displacement
├── DisplacementType
├── DisplacementResolution
├── DisplacementOrigin (puesto/entidad origen)
├── DisplacementDestination (puesto/entidad destino)
└── DisplacementExtension
```

---

## 8. Sub-módulo 03.7 — Desvinculación

### 8.1 Causales
#### 8.1.1 Régimen 728
| Causal | Consecuencia económica |
|--------|------------------------|
| Renuncia voluntaria | Liquidación sin indemnización |
| Mutuo disenso | Liquidación + posibles pactos |
| Cumplimiento de condición / plazo | Liquidación por término de contrato |
| Fallecimiento | Herederos reciben BBSS |
| Invalidez absoluta permanente | Liquidación + prestaciones EsSalud |
| Jubilación | Liquidación completa |
| Despido (causa justa) | Liquidación sin indemnización |
| **Despido arbitrario (sin causa justa)** | **Liquidación + indemnización 1.5 rem/mes × años laborados (tope 12 rem)** |
| Despido por falta grave | Liquidación sin indemnización (CTS sí; depende de causa) |

#### 8.1.2 Régimen 276
- Renuncia voluntaria
- Fallecimiento
- Jubilación (edad/tiempo)
- Cese por causa justificada (PAD)
- Destitución por falta grave (PAD)
- Incapacidad permanente
- Inhabilitación

#### 8.1.3 Régimen CAS
- No renovación de contrato
- Resolución por causa grave
- Mutuo acuerdo
- Fallecimiento

### 8.2 Flujo automático de desvinculación
```
1. Registro del cese con causal y fecha
2. Motor calcula liquidación automática (ver Módulo 04.7)
3. Generación de documentos:
   - Carta de aceptación de renuncia (si aplica)
   - Liquidación de Beneficios Sociales
   - Certificado de Trabajo (Art. 45 LPCL - obligatorio)
   - Constancia de no adeudo (si aplica)
4. Bloqueo de accesos a sistemas (integración con IT)
5. Recepción de entregables (equipos, credenciales)
6. Pago de liquidación en plazo legal (48h máximo)
7. Baja en T-Registro SUNAT
8. Baja en EsSalud / EPS
9. Comunicación a AFP (si aplica aporte pendiente)
10. Archivo del legajo con estado CERRADO (retención mínima 5 años)
```

### 8.3 Certificado de Trabajo (obligatorio)
Contenido mínimo (Art. 45 LPCL):
- Datos del empleador
- Datos del trabajador
- Tiempo de servicios
- Cargos desempeñados
- Fecha de inicio y término
- **Remuneración al momento del cese** (opcional según acuerdo)

El certificado NO debe incluir información desfavorable, calificaciones subjetivas ni motivos de cese.

### 8.4 Entidades
```
Termination
├── TerminationCause
├── TerminationSettlement (→ Módulo 04.7)
├── WorkCertificate
├── ExitInterview
├── HandoverChecklist
└── SystemsOffboarding
```

---

## 9. Workflows integrados

### 9.1 Onboarding completo (end-to-end)
```
Selección → Oferta → Aceptación → Vinculación (contrato + T-Registro) 
    → Día 1: Inducción general + entrega de equipos + accesos 
    → Primera semana: Inducción específica + asignación de mentor 
    → Primer mes: Seguimiento + evaluación temprana 
    → Fin período de prueba: Evaluación formal + ratificación
```

### 9.2 Offboarding completo
```
Notificación de cese → Cálculo de liquidación → Checklist de devolución 
    → Entrevista de salida → Bloqueo de accesos 
    → Pago de liquidación → Entrega de certificado 
    → Baja en T-Registro → Archivo de legajo
```

---

## 10. Configurabilidad

### 10.1 Workflows configurables
Cada etapa del ciclo debe ser configurable por tenant:
- Número de etapas de selección
- Aprobadores por etapa
- SLAs (tiempos máximos por etapa)
- Plantillas de contratos editables
- Checklist de inducción personalizable
- Documentos obligatorios en legajo (configurables)
- Tipos de desplazamiento habilitados (solo sector público)
- Plazos de período de prueba por tipo de contrato

### 10.2 Campos personalizados
Cada tenant puede extender:
- `Employee` (con campos sensibles a su industria: ej. n° colegiatura médica, n° registro CIP)
- `Contract` (cláusulas especiales)
- `DigitalDossier` (secciones adicionales)

---

## 11. KPIs del módulo
- **Time-to-fill**: días desde requisición hasta cobertura
- **Time-to-productivity**: días desde ingreso hasta productividad esperada
- **Rate de ratificación**: % que supera período de prueba
- **Completitud del legajo**: % legajos con 100% documentos obligatorios
- **Tiempo de procesamiento de liquidación**: horas desde cese hasta pago (meta <48h)
- **Tasa de rotación voluntaria**: indicador clave de retención

---

## 12. Referencias
- [D.Leg. 728 TUO (D.S. 003-97-TR) - Contratos](https://infopublic.bpaprocorp.com/banco-de-leyes/decreto-supremo-003-97-tr)
- [SERVIR - Guía de Inducción RPE 265-2017](https://storage.servir.gob.pe/normatividad/Resoluciones/PE-2017/Res265-2017-SERVIR-PE.pdf)
- [SUNAT T-Registro](https://www.sunat.gob.pe/)
- [Art. 45 LPCL - Certificado de trabajo](https://lpderecho.pe/)

---

## 13. Dependencias
- `modulos/04_gestion_compensacion.md` → motor de liquidación
- `modulos/02_organizacion_trabajo.md` → perfiles de puesto para selección
- `modulos/11_reclutamiento_ats.md` → ATS avanzado (si el cliente lo contrata)
- `normativa/N01_regimen_privado_728.md` → tipos de contrato
- `normativa/N03_regimen_publico_276.md` → desplazamientos públicos
- `normativa/N11_proteccion_datos_personales.md` → legajo digital
