# ADR-003: Autenticacion JWT con cookies HttpOnly

## Estado

Aceptado

## Contexto

El frontend React consume API DRF en navegador. Guardar tokens en `localStorage` simplifica implementacion pero aumenta superficie de ataque ante XSS.

## Decision

Usar JWT con cookies HttpOnly y endpoint de refresh, manteniendo CORS controlado y `CORS_ALLOW_CREDENTIALS=True`.

## Consecuencias

### Positivas

- Reduce exposicion del token frente a scripts del cliente.
- Mejor alineacion con practicas de seguridad para apps web corporativas.

### Negativas

- Requiere configuracion cuidadosa de CORS/CSRF y dominios.
- El debugging de sesiones puede ser menos directo.

## Alternativas Evaluadas

- JWT en localStorage/sessionStorage.
- Sesion tradicional server-side sin JWT.

## Fecha

2026-03-07
