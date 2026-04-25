# C03. Estrategia de Onboarding de Clientes

> El momento más crítico de la relación comercial. Si el onboarding falla, el churn del primer año es garantizado. Si funciona, el NRR crece año contra año.

---

## 1. Principios rectores

1. **Time to First Value (TTFV) medible**: el cliente debe obtener el primer valor tangible (primera planilla correcta calculada) en los primeros 15-45 días según tier.
2. **Configuración guiada con defaults inteligentes**: el tenant llega con configuraciones precargadas por sector/tamaño, no con formularios vacíos.
3. **Migración de data no negociable**: el cliente siempre viene de un sistema previo (Excel, ERP, otro SaaS). Si no resolvemos la migración, no hay onboarding.
4. **Validación paralela obligatoria**: la primera planilla real debe correrse en paralelo con el sistema viejo al menos 1 mes para construir confianza.

---

## 2. Fases genéricas del onboarding

### Fase 0 — Preventa (antes del contrato)

- **Diagnóstico rápido**: cantidad de empleados, regímenes, sedes, sistemas existentes, integraciones necesarias.
- **Demo personalizada** con data del sector del prospecto.
- **Propuesta técnica y comercial** con cronograma de onboarding.
- **SOW** firmado con entregables específicos, plazos, responsables del lado cliente.

### Fase 1 — Kickoff (día 0)

- Reunión con sponsor del cliente, equipo técnico (IT), equipo RRHH, y nuestro equipo (CSM + Consultor técnico + Consultor laboral).
- Validar alcance, entregables, responsables y RACI.
- Accesos al sistema, canal de comunicación (Slack compartido / Teams).
- Cronograma Gantt compartido.

### Fase 2 — Descubrimiento y Diseño (días 1-15)

- **Inventario de data**: empleados, contratos, histórico de remuneraciones, asistencia, capacitaciones.
- **Mapa de procesos actuales**: workflows de aprobación, políticas vigentes, roles internos.
- **Configuración de tenant**: empresa(s), sedes, áreas, cargos, regímenes activos, estructura organizacional.
- **Diseño de custom fields** y workflows específicos.
- **Validación legal** de políticas con el consultor laboral (ej. revisión de contratos tipo, RIT, política de vacaciones).

### Fase 3 — Migración de Data (días 15-30)

- **Templates de carga**: CSV/Excel con campos obligatorios + validaciones en línea.
- **Data cleansing**: detectar duplicados, DNIs inválidos, fechas imposibles, sueldos fuera de rango.
- **Carga en ambiente staging**: no toca producción; validación con el cliente.
- **Reconciliación**: el cliente firma que la data migrada es correcta.
- **Promoción a producción**.

### Fase 4 — Configuración de Módulos (días 30-60)

- **Módulo planilla**: estructuras salariales, conceptos personalizados, exportadores.
- **Módulo asistencia**: turnos, biometría, políticas de tardanza.
- **Módulo ausencias**: políticas de vacaciones, licencias, workflows de aprobación.
- **Módulo autoservicio**: activación del portal empleado con comunicación del lanzamiento.
- **Módulos adicionales según tier**: selección, desempeño, capacitación, SST.

### Fase 5 — Paralelo (días 60-90)

- Correr la planilla real en el nuevo sistema en paralelo con el sistema viejo.
- Comparar concepto por concepto y detectar diferencias.
- Iterar configuración hasta lograr coincidencia exacta.
- **Este es el paso más delicado**: requiere paciencia y precisión.

### Fase 6 — Go-live (día 90 estándar)

- Anuncio oficial a los empleados.
- Lanzamiento app móvil y portal.
- Primera planilla real en producción.
- Monitoreo intensivo las primeras 2 semanas.

### Fase 7 — Estabilización (días 90-180)

- Reuniones semanales con CSM.
- Resolución rápida de tickets.
- Ajustes finos de configuración.
- Training adicional por rol (RRHH admin, jefes, empleados).

### Fase 8 — Adopción y Expansión (meses 6-12)

- Activación de módulos adicionales.
- Revisión trimestral del uso vs. licenciado.
- Identificación de oportunidades de upsell (módulos, tier).
- Casos de éxito para marketing conjunto.

---

## 3. Onboarding por tier — diferencias clave

### Starter — Self-service + checklist

Todo por portal web + videotutoriales. El cliente debe poder configurar y arrancar sin reuniones. Soporte por email para dudas.

**Entregables**:
- Tenant creado con defaults del sector elegido.
- Templates CSV para carga de empleados.
- Bot asistente en el portal guiando siguiente paso.
- Biblioteca de videos (10-15 min cada uno).
- Checklist de 20 puntos con barra de progreso.
- Primera planilla calculada (día 15 target).

**Riesgos**:
- Cliente se atasca y abandona. Mitigación: alerta automática si 3 días sin avance + email proactivo.

### Pro — Consultor remoto

Consultor dedicado 15-25 horas totales, distribuidas en 30-45 días. Reuniones semanales.

**Entregables adicionales a Starter**:
- Sesión inicial de descubrimiento 2h.
- Configuración asistida de estructuras salariales complejas.
- Workflows custom diseñados junto al cliente.
- Migración con validación asistida.
- 1 mes de paralelo con consultor supervisando.

### Enterprise — Consultor dedicado

Equipo de proyecto: CSM + Consultor técnico + Consultor laboral + QA. 60-120 horas totales distribuidas en 60-90 días.

**Entregables adicionales a Pro**:
- Kickoff on-site (Lima) o remoto con video.
- ETL personalizado para migración masiva desde ERPs (SAP, Oracle HCM, PeopleSoft, Starsoft).
- Integraciones diseñadas (SSO, webhooks, conectores).
- Capacitación por rol (mínimo 4 sesiones de 2h).
- Documentación interna generada para el cliente.
- Paralelo de 2-3 meses con reuniones quincenales.

### GovTech — Proyecto con equipo extendido

Equipo completo: CSM senior + Consultor técnico + Consultor laboral sector público + Consultor legal + QA + Arquitecto. 120-200 horas en 90-180 días.

**Entregables adicionales a Enterprise**:
- Adaptación completa a los 7 subsistemas y 23 procesos SERVIR.
- Configuración de régimen 276, CAS, transición Ley 30057.
- Migración desde AIRHSP con verificación normativa.
- Plan de Cultura y Clima inicial (RPE 150-2017).
- Plan de Comunicación Interna inicial (RPE 151-2017).
- Reglamento Interno SST actualizado (Ley 29783).
- DB dedicada en infraestructura Perú.
- Auditoría externa previa al go-live.
- Due diligence de compliance.

---

## 4. Migraciones típicas desde sistemas preexistentes

| Sistema origen | Complejidad | Estrategia |
|---|---|---|
| Excel (muy común en Pymes) | Media | Templates CSV por ETL propio + data cleansing asistido |
| Starsoft | Media-Alta | ETL directo a la BD Starsoft (SQL Server) + mapeo de conceptos |
| Buk | Media | Export via API Buk + importer nuestro |
| Talana | Media | Export nativo + importer |
| Ofisis | Alta | Servicios web + ETL |
| SAP HCM / Success Factors | Alta | Connector SAP OData |
| Meta4 / PeopleSoft | Alta | ETL personalizado con validación exhaustiva |
| AIRHSP | Alta | Export normalizado + carga con validaciones SERVIR |
| Sistema hecho a medida | Muy alta | Dump SQL + análisis caso por caso |

**Regla común**: nunca migrar **planillas históricas recalculables**. Se migra el estado actual (empleados, contratos, estructuras, balances) + las **planillas cerradas como snapshot inmutable** (PDF firmado + JSON con los conceptos pagados). Con esto cumplimos auditoría SUNAT sin arrastrar la complejidad de recalcular históricos.

---

## 5. Riesgos del onboarding y mitigaciones

| Riesgo | Señal temprana | Mitigación |
|---|---|---|
| Cliente no prioriza migración | 2 semanas sin avance | Escalamiento a sponsor + revisión cronograma |
| Data del cliente muy sucia | DNIs inválidos, duplicados | Cleansing asistido + extender plazo sin penalidad |
| Expectativas desalineadas con scope | Requests fuera de SOW | RACI + Change Request formal |
| Cambio de stakeholder | Sponsor cambia | Kickoff re-hecho con nuevo sponsor |
| Regímenes más complejos de lo declarado | Descubrimiento de casos en fase migración | Escalar a consultor senior + eventual re-cotización |
| Integración externa bloqueada | IT del cliente no responde | Escalar + plan B manual |
| Paralelo detecta diferencias persistentes | Discrepancias >1% no explicadas | War room + inmersión a BD origen |

---

## 6. KPIs del onboarding

- **TTFV por tier**: ≤15 días (Starter), ≤45 días (Pro), ≤90 días (Enterprise), ≤180 días (GovTech).
- **Onboarding Completion Rate (OCR)**: ≥85% target; <70% señal crítica.
- **Satisfacción cliente post-golive (CSAT 90 días)**: ≥4.2/5.
- **Tickets críticos primer mes post-golive**: ≤3.
- **Diferencia vs. planilla anterior en mes de paralelo**: 0% en conceptos obligatorios.
- **Adopción app móvil al mes 3**: ≥60% de empleados activos.

---

## 7. Equipo de Customer Success

### 7.1 Roles

| Rol | Responsabilidad | Ratio |
|---|---|---|
| **CSM (Customer Success Manager)** | Relación comercial, upsell, renovación | 1 por cada 10 Enterprise / 30 Pro / 100 Starter |
| **Consultor Técnico** | Configuración, integraciones, migración | 1 por cada 5 proyectos concurrentes |
| **Consultor Laboral** | Asesoría normativa peruana | 1 por cada 10 proyectos; sector público requiere senior |
| **Soporte L1** | Tickets del día a día | 1 por cada 500 tenants |
| **Soporte L2** | Casos escalados técnicos | 1 por cada 2000 tenants |
| **Soporte L3 (Engineering)** | Bugs críticos | Compartido con equipo de desarrollo |

### 7.2 Rituales

- Reunión semanal CSM + cliente durante onboarding.
- Quarterly Business Review (QBR) para Enterprise/GovTech.
- Newsletter mensual con novedades de producto.
- Health score por cliente (adopción, tickets, actividad) revisado quincenalmente.

---

## 8. Recursos de autoaprendizaje

Todos los tiers tienen acceso a:

- **Knowledge Base** (KB) pública: cientos de artículos.
- **Academia online** con cursos certificables: "Administrador de planilla en [MiApp]", "Jefe de equipo", "Developer API".
- **Comunidad** de usuarios con foro moderado.
- **Webinars mensuales** sobre novedades normativas peruanas (p. ej. nueva UIT, cambios AFP, reformas SERVIR).
- **Changelog público** del producto.

---

## 9. Checklist maestro del onboarding (resumen)

```
[ ] Kickoff realizado con SOW firmado
[ ] Equipos del lado cliente y proveedor identificados
[ ] Acceso al sistema configurado
[ ] Configuración base del tenant completa (empresa, sedes, áreas, cargos)
[ ] Regímenes laborales activados
[ ] Estructuras salariales definidas
[ ] Conceptos de planilla mapeados a Tabla 22 SUNAT
[ ] Workflows de aprobación configurados
[ ] Data migrada y validada en staging
[ ] Reconciliación firmada por el cliente
[ ] Data promovida a producción
[ ] Primera planilla calculada en paralelo
[ ] Diferencias vs. sistema anterior resueltas
[ ] Exportadores PLAME, T-Registro, AFPnet validados con data real
[ ] Portal empleado lanzado con comunicación
[ ] App móvil instalada por empleados clave
[ ] Capacitaciones realizadas (RRHH, jefes, empleados)
[ ] Go-live ejecutado
[ ] Post-golive: monitoreo 2 semanas
[ ] CSAT 90 días levantado
[ ] Plan de expansión definido con cliente
```

---

## 10. Métricas de éxito del programa de onboarding (agregadas)

| Métrica | Objetivo año 1 | Objetivo año 2 |
|---|---|---|
| NPS post-onboarding | ≥40 | ≥50 |
| % clientes que activan módulo adicional en mes 6 | ≥30% | ≥50% |
| Churn primer año | ≤15% | ≤10% |
| TTFV promedio | Reducción 20% | Reducción 40% |
| Ratio onboarding concurrentes por consultor | 3-5 | 5-8 |
| Horas de consultor por onboarding (Pro) | 25-30 | 15-20 (por eficiencia) |
