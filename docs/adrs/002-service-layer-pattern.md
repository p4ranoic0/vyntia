# ADR-002: Usar Service Layer para la logica de negocio

## Estado

Aceptado

## Contexto

La logica de negocio del sistema RRHH crecio en complejidad: aprobaciones multinivel, calculos de vacaciones, flujos de onboarding, generacion de documentos y reglas por rol. Colocar logica en views o serializers incrementa acoplamiento y dificulta pruebas.

## Decision

Centralizar la logica de negocio en servicios de dominio dentro de `back/app_rrhh/services/`, manteniendo views/serializers enfocados en transporte HTTP y validacion de entrada/salida.

## Consecuencias

### Positivas

- Mejor separacion de responsabilidades.
- Mayor testabilidad unitaria e integracion por caso de negocio.
- Reutilizacion de reglas en distintos endpoints/acciones.

### Negativas

- Mayor numero de clases/archivos a mantener.
- Requiere convenciones de estructura para evitar dispersion.

## Alternativas Evaluadas

- Fat views (ViewSets con toda la logica).
- Logica distribuida entre modelos y serializers.

## Fecha

2026-03-07
