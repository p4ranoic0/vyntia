# API Errors - RRHH Intranet

## Formato de Error Estandar

Las respuestas de error del backend siguen la estructura base de `core.responses` y `core.exceptions`:

```json
{
  "success": false,
  "message": "Descripcion del error",
  "errors": {
    "campo": ["detalle"]
  },
  "error_code": "CODIGO_OPCIONAL"
}
```

## Codigos HTTP Usados

- `400 Bad Request`: datos invalidos o regla de negocio incumplida.
- `401 Unauthorized`: token ausente/invalido.
- `403 Forbidden`: usuario autenticado sin permisos.
- `404 Not Found`: recurso no existe.
- `409 Conflict`: conflicto de unicidad o estado.
- `422 Unprocessable Entity`: validacion de negocio semantica.
- `500 Internal Server Error`: error no controlado.

## Casos Frecuentes

### 1) Error de autenticacion

`401 Unauthorized`

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid"
}
```

### 2) Error de permisos

`403 Forbidden`

```json
{
  "success": false,
  "message": "No tienes permisos para acceder a este recurso"
}
```

### 3) Error de validacion de serializer

`400 Bad Request`

```json
{
  "success": false,
  "message": "Datos invalidos",
  "errors": {
    "email": ["Enter a valid email address."]
  }
}
```

### 4) Regla de negocio (vacaciones)

`400` o `422` segun implementacion del endpoint

```json
{
  "success": false,
  "message": "No hay saldo suficiente para la solicitud"
}
```

## Recomendacion para Frontend

- Tratar `401` como sesion expirada y redirigir a login.
- Mostrar `message` como feedback principal.
- Si existe `errors`, mapear por campo en formularios.
- Registrar `500` en logging de cliente con contexto del endpoint.
