# Módulo 02 — Organización del Trabajo y Distribución

> **Criticidad:** ALTA · **Tier:** Starter · **Dependencias:** ninguna operativa
> **Procesos SERVIR cubiertos:** 3 (Diseño de puestos), 4 (Administración de puestos)

---

## 1. Alcance

Define la estructura organizativa y los puestos de trabajo. Es el **prerrequisito lógico de Empleo (M03) y Compensación (M04)**.

---

## 2. Sub-módulos

### 2.1 Organigrama dinámico
- Estructura jerárquica navegable
- Unidades orgánicas (UO): dirección, gerencia, subgerencia, oficina, área, equipo
- Vinculación con centros de costo
- Historial de cambios estructurales
- Exportación a imagen / PDF / visio

### 2.2 Diseño de puestos (perfiles de puesto)
- Ficha del puesto con:
  - Identificación (código, nombre, área)
  - Misión del puesto
  - Funciones principales y secundarias
  - Competencias requeridas (técnicas, blandas)
  - Requisitos mínimos (formación, experiencia, idiomas)
  - Condiciones del puesto (jornada, ubicación, viajes)
  - Reporta a / supervisa a
  - Indicadores de desempeño (KPIs)
  - Riesgos asociados (vinculación con SST)
- Categoría ocupacional (ejecutivo/empleado/obrero — Tabla 10 SUNAT)
- Ocupación CIUO-08 (Tabla 9 SUNAT)

### 2.3 Administración de puestos
- Catálogo maestro de puestos (distinto al número de ocupantes)
- Plazas (puesto ocupado) vs Vacantes
- Cuadro de Asignación de Personal (CAP) — sector público
- **Cuadro de Puestos de la Entidad (CPE)** — sector público SERVIR
- **Manual de Perfiles de Puestos (MPP)** — sector público SERVIR

### 2.4 Bandas salariales y Cuadro de Categorías y Funciones (CCF)
- **Obligación Ley 30709**: toda organización con trabajadores debe tener CCF
- Agrupación de puestos en categorías con criterios objetivos:
  - Responsabilidad
  - Esfuerzo
  - Condiciones de trabajo
  - Complejidad
- Bandas salariales (mínimo, punto medio, máximo) por categoría
- Política salarial documentada
- Análisis de equidad interna
- Análisis de competitividad externa (benchmarking)

---

## 3. Entidades principales

```
OrgStructure
├── OrgUnit (unidad orgánica)
│   ├── UnitType (DIRECCION, GERENCIA, OFICINA, AREA, EQUIPO)
│   ├── CostCenter
│   └── ParentUnit (jerarquía)
│
Position (puesto — definición)
├── PositionProfile
│   ├── Mission
│   ├── Function
│   ├── RequiredCompetency
│   ├── RequiredEducation
│   ├── RequiredExperience
│   └── ReportsTo (position_id)
├── OccupationalCategory (Tabla 10 SUNAT)
├── CIUOCode (Tabla 9 SUNAT)
├── SalaryBand
│   ├── MinSalary
│   ├── MidSalary
│   └── MaxSalary
└── PositionRiskProfile (vinculado a SST)

Plaza (posición asignada)
├── Position (definición)
├── PlazaStatus (OCUPADA, VACANTE, CONGELADA)
├── CurrentEmployee (si ocupada)
└── History

CategoryFunctionTable (CCF — Ley 30709)
├── Category (jerárquica)
├── ObjectiveCriteria
├── PositionsInCategory
└── SalaryBandLink
```

---

## 4. Sector público: CPE, MPP, CAP

### 4.1 Cuadro de Puestos de la Entidad (CPE)
Documento oficial que contiene todos los puestos de la entidad bajo el régimen Ley 30057 (SERVIR):
- Nombre del puesto
- Código
- Nivel organizacional
- Grupo de servidor (DS, SP, SEC)
- Familia de puestos
- Nivel remunerativo
- Número de plazas

### 4.2 Manual de Perfiles de Puestos (MPP)
Documento con los perfiles detallados de todos los puestos del CPE. Requisitos:
- Aprobado por Titular de la entidad
- Registrado en SERVIR
- Base para concursos públicos

### 4.3 Cuadro de Asignación de Personal (CAP) Provisional
Documento del régimen 276/728 público que lista plazas:
- Código de plaza
- Nombre del cargo
- Clasificación (FP, EC, SP-DS, SP-EJ, SP-ES, SP-AP, RE)
- Situación (ocupada, vacante, prevista)

---

## 5. Funcionalidades técnicas clave

### 5.1 Versionado de estructura
Cada cambio estructural (reorganización, fusión de áreas) debe:
- Quedar registrado con fecha efectiva
- Mantener historia navegable
- No afectar reportes históricos (consultas a fecha)
- Integrarse con eventos de desplazamiento (M03.6)

### 5.2 Generación de organigrama
- Visualización jerárquica interactiva
- Niveles expandibles/colapsables
- Búsqueda por nombre, puesto, área
- Exportación en formatos estándar

### 5.3 Análisis de brechas salariales (Ley 30709)
- Comparación de salarios dentro de misma categoría
- Detección de diferencias por género, edad, antigüedad
- Reporte auto-generado para fiscalización SUNAFIL
- Plan de nivelación automático sugerido

### 5.4 Importación masiva
- Carga de organigrama desde Excel (plantilla predefinida)
- Validación de integridad referencial
- Preview antes de confirmar

---

## 6. Workflows clave

### 6.1 Creación de nuevo puesto
```
1. Solicitud del área usuaria (justificación + presupuesto)
2. Validación RRHH (consistencia con MPP / CCF)
3. Validación Finanzas (disponibilidad presupuestal)
4. Aprobación gerencial
5. Alta en catálogo de puestos
6. Actualización del CAP / CPE
7. Habilitación para convocatoria (M11)
```

### 6.2 Actualización del CCF (Ley 30709)
```
1. Revisión anual (obligatoria)
2. Análisis de nuevos puestos a clasificar
3. Reajuste de bandas salariales
4. Validación de política de no discriminación
5. Aprobación gerencial
6. Difusión al personal
7. Informe a SUNAFIL si requerido
```

---

## 7. Integraciones con otros módulos
- **M03** Empleo → selección contra perfil del puesto
- **M04** Compensación → banda salarial fija techo/piso
- **M05** Capacitación → brecha de competencias por puesto
- **M06** Desempeño → KPIs del puesto son base de evaluación
- **M07** SST → riesgos del puesto para IPERC

---

## 8. KPIs del módulo
- % puestos con perfil actualizado
- % puestos dentro de su banda salarial
- Tiempo de aprobación de nuevos puestos
- % plazas ocupadas vs CAP/CPE
- Índice de equidad salarial (brecha género/edad)

---

## 9. Referencias normativas
- [Ley 30709 — Igualdad Salarial](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [D.S. 002-2018-TR — Reglamento Ley 30709](https://www.gob.pe/institucion/mtpe/normas-legales/)
- [SERVIR — Guía para elaboración de MPP](https://www.servir.gob.pe/)
- [SERVIR — Instructivo CPE](https://www.servir.gob.pe/)
- [CIUO-08 OIT](https://www.ilo.org/public/spanish/bureau/stat/isco/)

---

## 10. MDs relacionados
- `normativa/N12_ley_igualdad_salarial_30709.md`
- `modulos/03_gestion_empleo.md`
- `modulos/04_gestion_compensacion.md`
