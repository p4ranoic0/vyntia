# ADR-001: Mantener Django/DRF como backend principal

## Estado

Aceptado

## Contexto

El sistema RRHH ya esta implementado sobre Django/DRF con dominio complejo (empleados, contratos, documentos, vacaciones, permisos) y frontend React en produccion de desarrollo activo. Se evaluo migrar a Java Spring Boot por afinidad tecnica, pero existe alto costo de reescritura y riesgo operativo.

## Decision

Mantener Django/DRF como stack principal y evolucionar incrementalmente con mejoras de escalabilidad (cache, async tasks, observabilidad, arquitectura limpia) en lugar de migrar todo a Spring Boot.

## Consecuencias

### Positivas

- Aprovecha el codigo existente y reduce riesgo de regresiones.
- Time-to-market mas corto para mejoras funcionales y tecnicas.
- Menor costo total de propiedad en el corto y mediano plazo.

### Negativas

- Menor rendimiento bruto frente a Java en escenarios de muy alta concurrencia.
- Requiere disciplina de optimizacion para escalar (cache, workers, tuning SQL).

## Alternativas Evaluadas

- Migracion total a Spring Boot.
- Enfoque hibrido por microservicios para modulos de alto costo computacional.

## Fecha

2026-03-07
