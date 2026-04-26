# 11. Reclutamiento y Selección (ATS avanzado)

> Módulo de atracción y selección de talento. Cubre desde la publicación de vacantes hasta la contratación, articulando con el módulo 03 (Gestión del Empleo) y el núcleo regulatorio peruano. Soporta tanto procesos privados como **concursos públicos** bajo SERVIR.

---

## 1. Alcance funcional

### 1.1 Sub-procesos cubiertos

- **11.1 Planificación de la convocatoria** (vacante, perfil, presupuesto).
- **11.2 Publicación multi-portal** (LinkedIn, Bumeran, Computrabajo, propio).
- **11.3 Atracción y recepción** de postulantes.
- **11.4 Tamizaje automático** con IA.
- **11.5 Evaluaciones** (técnicas, psicométricas, competencias).
- **11.6 Entrevistas** programadas y grabadas.
- **11.7 Evaluación final** y selección.
- **11.8 Propuesta y negociación salarial**.
- **11.9 Generación del contrato** (handoff al módulo 03).

---

## 2. Particularidades del sector público

El ATS debe soportar el **proceso de selección pública** conforme:
- **Ley 30057** (Ley del Servicio Civil) y reglamento.
- **RPE 313-2017-SERVIR-PE** — Directiva de Concursos Públicos.
- **RPE 330-2017-SERVIR-PE** — Gestión del proceso de selección.

### 2.1 Etapas del concurso público SERVIR

1. **Convocatoria** publicada por al menos 10 días en portal institucional + SERVIR Talento + diario de mayor circulación.
2. **Postulación** vía plataforma digital (con DNI/RUC, CV documentado).
3. **Evaluación curricular** (cumplimiento de requisitos mínimos).
4. **Evaluación de conocimientos** (prueba escrita).
5. **Evaluación psicológica** (opcional según puesto).
6. **Entrevista personal** ante Comité de Selección.
7. **Publicación de resultados preliminares** con recurso de reconsideración.
8. **Resultados finales**.
9. **Contratación** del ganador.

**Plazos mínimos** entre cada etapa establecidos en la Directiva.

### 2.2 Comité de Selección

Para cada convocatoria pública:
- Presidente (generalmente de la Oficina de RRHH).
- Representante del área solicitante.
- Representante técnico (jefe de gestión del conocimiento o afín).

---

## 3. Modelo de datos

### 3.1 Entidades principales

```sql
-- Vacante / Convocatoria
CREATE TABLE vacante (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  codigo VARCHAR(50) NOT NULL,
  titulo VARCHAR(200) NOT NULL,
  posicion_id UUID REFERENCES posicion(id),
  tipo_convocatoria VARCHAR(30),        -- interna | externa | mixta | publica_servir
  numero_vacantes INT DEFAULT 1,
  estado VARCHAR(30),                    -- borrador | publicada | en_evaluacion | cerrada | anulada
  fecha_apertura DATE NOT NULL,
  fecha_cierre DATE NOT NULL,
  salario_rango_min NUMERIC(10,2),
  salario_rango_max NUMERIC(10,2),
  jefe_solicitante_id UUID,
  comite_seleccion JSONB,                -- miembros + roles
  descripcion TEXT,
  requisitos JSONB,                      -- estructurados
  funciones JSONB,
  portales_publicados JSONB,             -- array de canales
  costo_estimado NUMERIC(10,2),
  UNIQUE (tenant_id, codigo)
);

-- Candidato (postulante)
CREATE TABLE candidato (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  dni VARCHAR(15),
  nombres VARCHAR(200),
  apellidos VARCHAR(200),
  email VARCHAR(200),
  celular VARCHAR(20),
  linkedin VARCHAR(300),
  cv_archivo_id UUID,
  cv_parseado JSONB,                     -- extracción estructurada con IA
  score_global NUMERIC(5,2),             -- evaluación IA 0-100
  fuente VARCHAR(50),                    -- linkedin | bumeran | propio | referido
  consentimiento_datos BOOLEAN,          -- Ley 29733
  consentimiento_timestamp TIMESTAMP,
  creado_en TIMESTAMP DEFAULT NOW()
);

-- Postulación (candidato × vacante)
CREATE TABLE postulacion (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  vacante_id UUID NOT NULL REFERENCES vacante(id),
  candidato_id UUID NOT NULL REFERENCES candidato(id),
  etapa_actual VARCHAR(50),              -- postulacion | filtro | tecnica | entrevista | propuesta | contratado | descartado
  fecha_postulacion TIMESTAMP DEFAULT NOW(),
  pretension_salarial NUMERIC(10,2),
  disponibilidad VARCHAR(100),
  score_ajuste NUMERIC(5,2),             -- match candidato-vacante
  estado_descarte VARCHAR(50),           -- activo | descartado_automatico | descartado_manual | desistido
  motivo_descarte TEXT,
  UNIQUE (tenant_id, vacante_id, candidato_id)
);

-- Evaluaciones
CREATE TABLE evaluacion_aplicada (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  postulacion_id UUID NOT NULL REFERENCES postulacion(id),
  tipo VARCHAR(30),                      -- tecnica | psicometrica | competencias | juicio
  instrumento_id UUID,
  puntaje NUMERIC(5,2),
  resultado VARCHAR(30),                 -- aprobado | desaprobado | en_rango
  evaluador_id UUID,
  fecha DATE,
  archivo_evidencia_id UUID
);

-- Entrevistas
CREATE TABLE entrevista (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  postulacion_id UUID NOT NULL,
  tipo VARCHAR(30),                      -- rrhh | tecnica | final | comite_publico
  fecha TIMESTAMP,
  duracion_min INT,
  entrevistadores JSONB,                 -- array de usuarios
  modalidad VARCHAR(20),                 -- presencial | virtual | hibrida
  link_reunion VARCHAR(500),
  grabacion_id UUID,                     -- consentimiento requerido
  notas TEXT,
  calificacion NUMERIC(5,2),
  estado VARCHAR(20)                     -- programada | realizada | reprogramada | cancelada
);
```

---

## 4. Pipeline Kanban configurable

### 4.1 Etapas default (procesos privados)

```
[Postulación] → [Filtro CV] → [Prueba técnica] → [Entrevista RRHH] 
→ [Entrevista Técnica] → [Entrevista Final] → [Propuesta] → [Contratado]
```

### 4.2 Etapas concurso público SERVIR

```
[Postulación] → [Evaluación Curricular] → [Evaluación Conocimientos] 
→ [Evaluación Psicológica] → [Entrevista Comité] → [Resultados Preliminares]
→ [Reconsideración] → [Resultados Finales] → [Contratación]
```

### 4.3 Configuración por tenant

El tenant define su propio pipeline en el módulo de Workflows (A03). Cada etapa tiene:
- Nombre y orden.
- Responsable (rol o usuario).
- Criterios de avance (puntaje mínimo, evaluación requerida).
- SLA (días máximos en la etapa).
- Acciones automáticas (email de agradecimiento, asignación de prueba, etc.).

---

## 5. Publicación multi-portal

### 5.1 Portales integrados (Perú)

| Portal | Integración | Notas |
|---|---|---|
| **LinkedIn** | API nativa | Requiere cuenta corporativa |
| **Bumeran** | API | El más usado en Perú |
| **Computrabajo** | API | Alto volumen |
| **Aptitus** | API | Perfiles senior |
| **SERVIR Talento** | Scraper / API si se expone | Sector público obligatorio |
| **Portal propio del cliente** | Nativo | Microsite white-label |
| **Portal de universidades** (PUCP, ULima, UPC) | Caso por caso | Convenios |

### 5.2 Sincronización de candidatos

- Candidato postula desde el portal externo → llega al sistema vía webhook o API.
- Deduplicación automática por DNI/email.
- Mantenimiento del estado actualizado en el portal origen.

---

## 6. Parsing de CV con IA

### 6.1 Capacidades
- Extracción estructurada: nombre, contacto, educación, experiencia, certificaciones, idiomas, habilidades.
- Clasificación de experiencia por área.
- Score de match contra la vacante (similitud semántica con embeddings).
- Detección de inconsistencias (fechas que no cuadran).

### 6.2 Modelo
- LLM (Anthropic Claude, OpenAI, modelo local según tier del cliente).
- Prompt template con el perfil de la vacante.
- Salida JSON estructurada validada con schema.

### 6.3 Privacidad (articulación con N11)
- Consentimiento explícito del candidato para procesamiento con IA.
- Los CVs no se usan para entrenar modelos (configuración enterprise).
- Retención limitada post-proceso.

---

## 7. Evaluaciones automatizadas

### 7.1 Técnicas
- Pruebas de conocimiento configurables (banco de preguntas).
- Tests de código (para desarrolladores) con autoevaluación.
- Assessments en habilidades ofimáticas (para administrativos).

### 7.2 Psicométricas
- Integración con proveedores autorizados (DiSC, 16PF, Hogan, PDA, Cleaver).
- Tests de personalidad, competencias, valores, fit cultural.
- Licenciamiento por cuenta del cliente o del SaaS según contrato.

### 7.3 Entrevistas estructuradas
- Guías por competencia (STAR: Situación, Tarea, Acción, Resultado).
- Calificación rubricada.
- Sin sesgos: rotación de entrevistadores, preguntas iguales para todos.

### 7.4 Grabación con consentimiento
- Consentimiento previo del candidato (Ley 29733).
- Almacenamiento cifrado.
- Retención limitada (ej. 90 días tras el cierre del proceso).

---

## 8. Programación de entrevistas

### 8.1 Integración de calendarios
- Google Calendar / Outlook / Exchange.
- Candidato elige horarios del entrevistador con disponibilidad visible.
- Envío automático de invitaciones con enlaces de reunión (Google Meet, Zoom, Teams).

### 8.2 Recordatorios
- 24h antes.
- 1h antes.
- Email + SMS + push móvil.

---

## 9. Diversidad e inclusión

### 9.1 Métricas (articulación con N12 igualdad salarial)
- Distribución por sexo en el pipeline.
- Edad.
- Discapacidad (Ley 29973 — cuota 3% para empresas 50+).
- Procedencia regional.

### 9.2 Políticas de sesgo
- Ocultación de nombre, foto, edad, sexo en la evaluación curricular (blind screening opcional).
- Panel de entrevistadores mixto.
- Rubros de evaluación estandarizados.

### 9.3 Prohibiciones
- Prohibidas preguntas sobre:
  - Estado civil.
  - Embarazo / planes familiares.
  - Religión.
  - Orientación sexual.
  - Afiliación política / sindical.
- Alertas en el sistema si un entrevistador formula estas preguntas (registrable por el candidato).

---

## 10. Propuesta y negociación

### 10.1 Simulador de propuesta
- Sueldo bruto → neto calculado con reglas peruanas (Renta 5ta, AFP, EsSalud).
- Visualización de total cost to company (con aportes patronales).
- Comparación contra la banda salarial del CCF (módulo 02).

### 10.2 Carta oferta electrónica
- Generada automáticamente con datos del proceso.
- Firma electrónica.
- Plazo de aceptación.
- Condiciones (fecha de inicio, período de prueba, beneficios).

### 10.3 Handoff al módulo 03
Al aceptar la oferta:
- Se crea el `Empleado` en módulo 03.
- Se genera el contrato con el tipo adecuado (728, MYPE, CAS, etc.).
- Se dispara el proceso de onboarding (inducción, legajo, alta en T-Registro).

---

## 11. Métricas clave del ATS

### 11.1 Tiempo
- **Time to fill**: días desde apertura hasta contratación.
- **Time to hire**: días desde primera postulación al contratado hasta su aceptación.
- **Source effectiveness**: tiempo y costo por portal.

### 11.2 Calidad
- **Conversion rate** por etapa.
- **Offer acceptance rate**.
- **First-year retention** (retención al año del contratado).
- **Quality of hire** (evaluación a 6 meses del contratado).

### 11.3 Costo
- **Cost per hire** por canal.
- **Cost per offer accepted**.

### 11.4 Equidad
- Distribución por género, edad, región.
- Tasas de aprobación por demografía.

---

## 12. Integraciones del módulo

- **Módulo 02 Organización**: catálogo de posiciones + CCF.
- **Módulo 03 Gestión del empleo**: handoff de contratado.
- **Módulo 05 Capacitación**: onboarding automático.
- **Módulo 09 Procedimiento Disciplinario**: check de antecedentes si aplica.
- **Módulo 12 Analytics**: dashboards de reclutamiento.
- **A03 Workflows**: pipeline configurable.
- **N11 Protección de datos**: consentimiento y retención de candidatos no contratados.
- **N12 Igualdad salarial**: dashboard de equidad del funnel.

---

## 13. Tier comercial

### 13.1 Plan Pro
- Pipeline Kanban básico.
- Publicación en 1-2 portales.
- Parsing CV.
- Evaluaciones básicas.
- Programación de entrevistas.

### 13.2 Plan Enterprise
- Multi-portal (5+).
- IA avanzada de matching.
- Assessments psicométricos integrados.
- Videoentrevistas grabadas.
- Workflows personalizados.
- API abierta para integradores.

### 13.3 Plan GovTech
- Proceso de selección pública SERVIR completo.
- Publicación automática en SERVIR Talento.
- Comité de Selección con roles dedicados.
- Recursos administrativos con plazos legales.
- Transparencia (portal público de convocatorias).
- Reporte al Registro Nacional de Sanciones SERVIR antes de contratar.

---

## 14. Checklist

- [ ] Modelo de datos con vacante, candidato, postulación, evaluación, entrevista
- [ ] Pipeline Kanban configurable por tenant
- [ ] Pipelines específicos privado y público SERVIR
- [ ] Integración al menos con 3 portales peruanos + LinkedIn
- [ ] Parsing CV con IA y score de match
- [ ] Evaluaciones técnicas y psicométricas
- [ ] Programación de entrevistas con calendario
- [ ] Grabación con consentimiento
- [ ] Métricas ATS en dashboard
- [ ] Blind screening opcional
- [ ] Alertas de preguntas prohibidas
- [ ] Simulador de propuesta bruto/neto
- [ ] Carta oferta con firma electrónica
- [ ] Handoff automático al módulo 03
- [ ] Cumplimiento Ley 29733 para candidatos (consentimiento + retención)
- [ ] Sector público: proceso SERVIR completo con Comité de Selección
