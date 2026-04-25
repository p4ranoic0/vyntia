# Módulo 01 — Planificación de Políticas de RRHH

> **Criticidad:** MEDIA · **Tier:** Pro · **Dependencias:** base (ninguna operativa) — referencia para todos los demás módulos
> **Procesos SERVIR cubiertos:** 1 (Estrategias, políticas y procedimientos), 2 (Planificación de RR.HH.)

---

## 1. Alcance

Soporta la **gobernanza de RRHH**: cómo se definen las estrategias, políticas internas, procedimientos, y cómo se planifica la fuerza laboral a futuro.

---

## 2. Sub-módulos

### 2.1 Gestión de Políticas y Procedimientos
- Repositorio documental de políticas corporativas
- Tipos: política corporativa, política de RRHH, política SST, código de ética, RIT, Reglamento SST, directivas internas
- Versionado con trazabilidad de cambios
- Flujo de elaboración → revisión → aprobación → publicación → derogación
- Difusión con acuse de recibo del colaborador
- Alertas de vencimiento (ej. RIT requiere actualización bianual)
- Biblioteca accesible desde portal del empleado

### 2.2 Plan Anual/Estratégico de RRHH
- Objetivos anuales alineados a objetivos estratégicos
- KPIs con meta y responsable
- Presupuesto asignado por línea de acción
- Seguimiento trimestral/semestral

### 2.3 Planificación de la Fuerza Laboral (Workforce Planning)
- Proyección de headcount por área/período
- Análisis de brechas (futuro vs actual)
- Plan de sucesión para puestos clave
- Rotación esperada y planes de retención

### 2.4 Matriz de Cumplimiento Normativo
- Catálogo de obligaciones legales aplicables (MTPE, SUNAFIL, MINSA, SERVIR, SUNAT)
- Estado de cumplimiento por obligación
- Responsable designado
- Evidencias documentales
- Alertas preventivas de vencimientos
- Dashboard ejecutivo de compliance

---

## 3. Entidades principales

```
Policy
├── PolicyType (CORPORATIVA, RRHH, SST, RIT, ETICA, DIRECTIVA)
├── PolicyVersion (histórico)
├── PolicyApprovalFlow
├── PolicyPublication
└── PolicyAcknowledgment (acuse del colaborador)

HRStrategicPlan (anual)
├── StrategicObjective
│   └── KPI
│       ├── Target
│       └── Measurement
└── BudgetLine

WorkforcePlan
├── HeadcountProjection (por área × período)
├── GapAnalysis
└── SuccessionPlan
    └── KeyPosition
        └── SuccessorCandidate

ComplianceMatrix
├── ComplianceObligation
│   ├── LegalReference
│   ├── Deadline
│   ├── Owner
│   ├── Status (CUMPLIDO/EN_CURSO/VENCIDO)
│   └── Evidence
```

---

## 4. Workflows clave

### 4.1 Ciclo de vida de una política
```
BORRADOR → REVISIÓN LEGAL → REVISIÓN SST (si aplica) 
→ APROBACIÓN GERENCIAL → PUBLICACIÓN → DIFUSIÓN 
→ VIGENTE → ACTUALIZACIÓN o DEROGACIÓN
```

### 4.2 Ejecución del plan anual
```
1. Enero: carga de plan aprobado
2. Mensual: actualización de avance de KPIs
3. Trimestral: revisión gerencial con ajustes
4. Diciembre: cierre + balance + propuesta para siguiente año
```

---

## 5. Integraciones con otros módulos
- **M02** Organización → puestos necesarios según plan de workforce
- **M03** Empleo → contrataciones autorizadas según plan
- **M05** Capacitación → actividades del plan alineadas
- **M07** SST → RIT, Reglamento SST como políticas tipificadas
- **M12** Analítica → dashboards de avance

---

## 6. KPIs del módulo
- % políticas vigentes sin vencer
- % acuse de recibo del colaborador en políticas críticas
- % cumplimiento de obligaciones normativas
- Desviación del plan anual (%)

---

## 7. Consideraciones sector público (SERVIR)
- Alineación con Plan Estratégico Institucional (PEI)
- Plan Operativo Institucional (POI) de RRHH
- **Plan de Desarrollo de las Personas (PDP)** integrado con M05
- Reportes obligatorios a SERVIR sobre avance
