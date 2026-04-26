# 12. Analítica y People Analytics

> Módulo de inteligencia de datos para decisiones estratégicas de RRHH. Transforma los datos operativos de los otros 11 módulos en indicadores ejecutivos, diagnósticos y predicciones. Cubre reporting regulatorio obligatorio en Perú y análisis avanzados con IA.

---

## 1. Alcance funcional

### 1.1 Tres capas de analítica

| Capa | Pregunta que responde | Ejemplo |
|---|---|---|
| **Descriptiva** | ¿Qué pasó? | Headcount por área, rotación mensual, costo laboral |
| **Diagnóstica** | ¿Por qué pasó? | Análisis de causas de rotación por área/jefe/generación |
| **Predictiva** | ¿Qué pasará? | Probabilidad de renuncia de cada empleado en 6 meses |

### 1.2 Dashboards objetivo

1. **Dashboard Ejecutivo** (CEO, GG): visión general 360°.
2. **Dashboard RRHH Operativo**: gestión del día a día.
3. **Dashboard por Gerencia/Área**: KPIs del área y comparativos.
4. **Dashboard de Compensación**: costo, equidad, tendencias.
5. **Dashboard SST y Bienestar**: indicadores preventivos y reactivos.
6. **Dashboard Talento**: selección, desempeño, sucesión.
7. **Dashboard Regulatorio**: cumplimiento normativo.

---

## 2. KPIs nucleares

### 2.1 Headcount y estructura

| KPI | Fórmula |
|---|---|
| **Dotación actual** | Total empleados activos al cierre |
| **Headcount por área, sede, régimen** | Distribución |
| **Ratio de mandos** | Jefes / Total empleados |
| **Span of control** | Empleados promedio por jefe |
| **Antigüedad promedio** | Años promedio en la organización |
| **Edad promedio** | Edad promedio de la dotación |
| **Pirámide generacional** | Distribución Boomer/X/Millennial/Z |

### 2.2 Rotación

| KPI | Fórmula |
|---|---|
| **Turnover total** | Ceses del período / Dotación promedio × 100 |
| **Turnover voluntario** | Renuncias / Dotación promedio × 100 |
| **Turnover involuntario** | Despidos / Dotación promedio × 100 |
| **Early turnover** | Ceses de trabajadores con <1 año / Contrataciones × 100 |
| **Tenure at exit** | Antigüedad promedio al momento del cese |
| **Rotation hotspots** | Áreas/jefes con mayor turnover |

### 2.3 Ausentismo

| KPI | Fórmula |
|---|---|
| **Índice de ausentismo** | Días ausentes / Días programados × 100 |
| **Frecuencia** | Ausencias / Empleados promedio |
| **Duración promedio** | Días de ausencia / Ausencias |
| **Costo del ausentismo** | Días × Costo promedio diario |
| **Ausentismo por causa** | Médico, personal, injustificado, etc. |

### 2.4 Costo laboral

| KPI | Fórmula |
|---|---|
| **Costo total** | Suma de remuneraciones + aportes + beneficios |
| **Costo por empleado** | Costo total / Dotación promedio |
| **Costo por venta** | Costo total / Ventas del período |
| **Costo por área** | Distribución relativa |
| **Variación costo laboral** | Mes actual vs mes anterior; año vs año |
| **Horas extras como % de planilla** | HE / Total planilla × 100 |

### 2.5 Selección

| KPI | Fórmula |
|---|---|
| **Time to fill** | Días entre apertura de vacante y contratación |
| **Time to hire** | Días entre primera postulación y aceptación |
| **Conversion rate por etapa** | Candidatos que avanzan / Candidatos en la etapa × 100 |
| **Cost per hire** | Costo del proceso / Contrataciones |
| **Offer acceptance rate** | Ofertas aceptadas / Ofertas × 100 |
| **Source effectiveness** | Contratados por portal / Postulantes del portal |
| **Quality of hire** | Desempeño a 6 meses de contratados nuevos |

### 2.6 Desempeño y talento

| KPI | Fórmula |
|---|---|
| **% con evaluación completa** | Evaluaciones cerradas / Total empleados × 100 |
| **Distribución de calificaciones** | % en cada banda (alto, medio, bajo) |
| **Nine-box distribution** | Distribución de la matriz talento |
| **High potentials %** | HiPo identificados / Dotación × 100 |
| **Gap de competencias** | % empleados con gaps críticos sin plan |
| **Internal mobility rate** | Promociones internas / Vacantes × 100 |
| **Successor coverage** | Puestos críticos con sucesor identificado / Puestos críticos × 100 |

### 2.7 Capacitación

| KPI | Fórmula |
|---|---|
| **Horas de capacitación por empleado** | Total horas / Dotación |
| **% del PDP ejecutado** | Actividades completadas / Actividades planificadas × 100 |
| **Inversión por empleado** | Presupuesto capacitación / Dotación |
| **ROI capacitación** | Productividad post-capacitación vs baseline |

### 2.8 Clima y engagement

| KPI | Fórmula |
|---|---|
| **eNPS** | % Promotores − % Detractores |
| **% Satisfacción general** | Encuesta de clima |
| **Participación en encuestas** | Respondieron / Invitados × 100 |
| **Índice de clima por dimensión SERVIR** | 5 dimensiones oficiales |

### 2.9 SST

| KPI | Fórmula |
|---|---|
| **Índice de frecuencia** | (Accidentes × 1,000,000) / Horas hombre trabajadas |
| **Índice de severidad** | (Días perdidos × 1,000,000) / Horas hombre trabajadas |
| **Índice de accidentabilidad** | Frecuencia × Severidad / 1,000 |
| **% EMO al día** | EMO vigentes / Empleados × 100 |
| **Cumplimiento Plan SST** | Actividades ejecutadas / Planificadas × 100 |
| **Incidentes sin lesión** | Reportes preventivos |

### 2.10 Equidad salarial (Ley 30709)

| KPI | Fórmula |
|---|---|
| **Brecha salarial global** | (Sueldo varones − Sueldo mujeres) / Sueldo varones × 100 |
| **Brecha por categoría** | Análisis por categoría del CCF |
| **% mujeres en mandos** | Mujeres jefas / Total jefes × 100 |
| **Ratio de ascensos por género** | Distribución de promociones |

---

## 3. Análisis predictivo con IA

### 3.1 Predicción de fuga de talento (attrition risk)

**Modelo**: clasificación binaria (renuncia / no renuncia en próximos 6 meses).

**Features típicos**:
- Antigüedad, edad, régimen, área, jefe.
- Tenure en el cargo actual.
- Tiempo sin aumento salarial.
- Resultado última evaluación.
- Número de ausencias recientes.
- Participación en capacitación.
- Resultado encuesta de clima individual.
- Eventos recientes (cambio de jefe, reorganización).

**Output**: score 0-100 de riesgo.

**Uso**: alertas a RRHH y al jefe directo para intervención preventiva (conversación, plan retención, ajuste salarial).

**Ética**: el score no debe usarse para despidos anticipados ni discriminación. Uso exclusivo para retención.

### 3.2 Predicción de éxito en selección

**Modelo**: regresión sobre candidatos históricos.

**Features**: CV parseado + resultados de evaluaciones + fuente.

**Output**: probabilidad de ser un empleado "A-player" (top 20% desempeño al año).

### 3.3 Predicción de ausentismo

**Modelo**: series temporales + clasificación.

**Output**: proyección de días de ausencia por área, útil para planificación de turnos.

### 3.4 Análisis de redes organizacionales (ONA)

- Quién se comunica con quién (mail, Slack, Teams).
- Detección de "brokers" informales (personas clave para comunicación).
- Identificación de silos.
- Relevante para gestión del cambio.

**Cuidado**: requiere consentimiento y anonimización agresiva.

### 3.5 Análisis de texto (NLP) en encuestas

- Agrupación automática de comentarios abiertos.
- Análisis de sentimiento.
- Detección de temas emergentes.
- Alertas ante menciones de hostigamiento, fraude, corrupción.

---

## 4. Reportes regulatorios obligatorios (Perú)

### 4.1 MTPE / SUNAFIL

| Reporte | Periodicidad |
|---|---|
| Estadística mensual SST | Mensual |
| Libro de planillas (archivo electrónico) | Anual |
| Memoria anual SST | Anual |
| Reporte anual de hostigamiento sexual | Anual |
| Reporte anual Ley 30709 | Anual |

### 4.2 SUNAT

| Reporte | Periodicidad |
|---|---|
| PLAME | Mensual |
| T-Registro (altas/bajas/modificaciones) | Continua |
| Certificado de Rentas y Retenciones | Anual (antes 1 marzo año siguiente) |
| DJ Anual IR (por empleador) | Anual |

### 4.3 AFPnet / SBS

| Reporte | Periodicidad |
|---|---|
| Archivo AFPnet .xlsx | Mensual |
| DNP / DYP | Mensual |

### 4.4 EsSalud

| Reporte | Periodicidad |
|---|---|
| Declaración EsSalud (vía PLAME) | Mensual |
| Subsidios CITT | Según caso |
| Acreditación de trabajadores | Continua |

### 4.5 Sector público adicional

| Reporte | Periodicidad | Destino |
|---|---|---|
| AIRHSP | Mensual | SERVIR |
| Declaración Jurada Bienes y Rentas | Anual | Contraloría |
| Informe Plan Anual Capacitación | Anual | SERVIR |
| Informe Plan Cultura y Clima | Anual | SERVIR |

### 4.6 Otros (según sector)

- OSINERGMIN (minería, electricidad, hidrocarburos).
- SUNASA / SUSALUD.
- ONP.
- Superintendencia de Banca y Seguros (entidades financieras).

---

## 5. Arquitectura del módulo analítico

### 5.1 Capa de datos

**Data Warehouse analítico separado del transaccional**:
- Proyecciones denormalizadas de los events de Payroll (A06).
- ETL periódico (diario u horario) desde tablas operativas.
- Schemas dimensionales (star schema) para performance.

### 5.2 Stack recomendado

| Capa | Tecnología |
|---|---|
| ETL | dbt, Airbyte, procesos Python |
| Data Warehouse | PostgreSQL + particiones / BigQuery / Redshift |
| Cálculo in-memory | DuckDB para queries ad-hoc |
| Visualización | Metabase, Apache Superset (embedded), Power BI |
| ML | Python scikit-learn, XGBoost, MLflow para tracking |
| Serving ML | FastAPI + modelo serializado |

### 5.3 Refresh de datos

- **Real-time (< 1 min)**: KPIs críticos del día (asistencia, marcaciones).
- **Near real-time (≤ 1 hora)**: dashboards operativos.
- **Batch diario**: reportes ejecutivos, predicciones.
- **Batch mensual**: reportes regulatorios.

---

## 6. Funcionalidades del módulo

### 6.1 Dashboards drag-and-drop
- Biblioteca de widgets: chart, tabla, KPI card, mapa, heatmap, funnel.
- Filtros globales: período, área, sede, régimen.
- Permisos por dashboard (ver A04).
- Compartir con permalink firmado.

### 6.2 Exploración ad-hoc
- Query builder visual para usuarios no técnicos.
- SQL console para usuarios avanzados (Enterprise).
- Exportación a Excel, PDF, CSV.

### 6.3 Alertas automáticas
- Umbrales: "alertar si turnover > 5% mensual".
- Cambios bruscos: "alertar si costo laboral crece >10% mes vs mes".
- Predicciones: "alertar si empleado X tiene riesgo de fuga >70%".
- Canales: email, Slack, Teams, push móvil.

### 6.4 Reportes programados
- Entrega automática por email/Slack en días y horas definidos.
- Plantillas por audiencia (ejecutiva, operativa, regulatoria).

### 6.5 Benchmarking anónimo
- Comparación del tenant contra el promedio del sector (anonimizado y agregado).
- Solo disponible en Enterprise/GovTech con opt-in explícito.

---

## 7. Modelo de datos analítico (dimensional)

### 7.1 Hechos (fact tables)

- `fact_planilla` (grano: empleado × período × concepto).
- `fact_asistencia` (grano: empleado × día).
- `fact_ausencia` (grano: solicitud de ausencia).
- `fact_evaluacion_desempeno` (grano: empleado × ciclo).
- `fact_postulacion` (grano: candidato × vacante × etapa).
- `fact_capacitacion` (grano: empleado × actividad).
- `fact_accidente_sst` (grano: incidente).

### 7.2 Dimensiones

- `dim_empleado` (slowly changing dimension Type 2).
- `dim_tiempo` (día, semana, mes, trimestre, año).
- `dim_area`, `dim_sede`, `dim_posicion`.
- `dim_regimen`, `dim_categoria`, `dim_banda_salarial`.
- `dim_concepto_planilla` (mapeado a Tabla 22 SUNAT).
- `dim_candidato`.

---

## 8. Cumplimiento y privacidad (articulación con N11)

### 8.1 Segregación de datos
- **Analítica agregada**: siempre disponible.
- **Datos individuales**: solo con permisos específicos.
- **Datos sensibles** (salud, desempeño individual): permlevel alto.

### 8.2 Anonimización en benchmark
- Benchmark inter-tenant solo con datos agregados que no permiten identificación.
- K-anonimity k≥5 para evitar reidentificación.

### 8.3 Explicabilidad de modelos ML
- Todo modelo usado para decisiones sobre empleados debe ser explicable.
- SHAP values disponibles para cada predicción.
- Auditoría de sesgos en datasets de entrenamiento.

### 8.4 Derecho a no decisión automatizada (Art. nuevo Reglamento D.S. 016-2024-JUS)
- Las predicciones son insumo, no decisión automática.
- Siempre hay revisión humana antes de acción sobre el empleado.

---

## 9. Casos de uso concretos

### 9.1 "¿Por qué sube la rotación en operaciones?"
Análisis diagnóstico:
1. Turnover por área → operaciones +15%.
2. Desglose por jefe → jefe X 25%, jefe Y 8%.
3. Encuesta de salida → "falta de reconocimiento" 40%, "sueldo" 30%.
4. Cruce con encuesta de clima → jefe X tiene score bajo en liderazgo.
5. Recomendación: coaching al jefe X, revisión de política de reconocimiento.

### 9.2 "¿Cuánto más nos costaría ajustar brecha salarial?"
Simulador:
- Brecha global actual: 8%.
- Costo de ajustar 50% de la brecha: S/ 45,000/mes.
- Costo de ajustar 100%: S/ 90,000/mes.
- Empleados beneficiados: 47.

### 9.3 "¿Qué empleados están en riesgo de renuncia en Q2?"
Listado priorizado:
- 23 empleados con riesgo >70%.
- Agrupados por área.
- Plan de acción sugerido por empleado.

### 9.4 "¿Cumplimos el Plan SST del año?"
Dashboard cumplimiento:
- Inspecciones: 12/12 ✓
- Capacitaciones: 45/50 (90%).
- EMO: 378/400 (94%).
- Simulacros: 3/4 — falta uno.
- Alerta proactiva: programar simulacro antes del cierre del año.

---

## 10. Tier comercial

### 10.1 Starter
- Dashboards predefinidos básicos (headcount, rotación, ausentismo, costo).
- Exportación a Excel/PDF.
- Sin predicciones.

### 10.2 Pro
- Dashboards + ad-hoc query builder visual.
- Reportes programados.
- Alertas de umbrales.
- KPIs operativos completos.

### 10.3 Enterprise
- Todo lo anterior.
- Análisis predictivo (attrition, éxito selección).
- NLP en encuestas abiertas.
- Benchmark sectorial anónimo.
- API analítica para BI externo (Power BI, Tableau, Looker).
- Data lake del cliente con export nativo.

### 10.4 GovTech
- Todo Enterprise.
- Reportes regulatorios SERVIR, Contraloría, MEF.
- Exportación automática AIRHSP.
- Dashboards públicos (transparencia ciudadana) configurables.

---

## 11. Checklist

- [ ] Data warehouse analítico separado del transaccional
- [ ] ETL periódico desde events Payroll + tablas operativas
- [ ] Modelo dimensional (fact + dim) implementado
- [ ] Dashboards predefinidos por audiencia (Ejecutivo, Operativo, Gerencial, etc.)
- [ ] Dashboards drag-and-drop configurables
- [ ] Query builder visual + SQL console (Enterprise)
- [ ] Alertas automáticas por umbral, cambio, predicción
- [ ] Reportes programados con entrega multi-canal
- [ ] Generación automatizada de reportes regulatorios (PLAME, T-Registro, etc.)
- [ ] Predicciones ML con explicabilidad (SHAP)
- [ ] NLP en encuestas abiertas
- [ ] Anonimización para benchmark inter-tenant (k-anonimity)
- [ ] Permisos granulares por dashboard y por campo
- [ ] API analítica para BI externo (Enterprise+)
- [ ] Módulo GovTech con reportes SERVIR/Contraloría/MEF

---

## 12. Referencias

- Módulo A06 Event Sourcing Payroll (fuente de verdad para data de planilla).
- Módulo A04 RBAC (permisos granulares).
- Módulo N11 Protección de datos (anonimización, explicabilidad).
- Módulo 07 Relaciones Humanas (cultura, clima, SST — fuentes de data).
- SUNAT Planilla Electrónica (N06).
