# Generated API Types

⚠️ **IMPORTANTE:** Este directorio es generado automáticamente.

## 🔄 Cómo regenerar

```bash
npm run generate:api
```

Requiere:
- Backend corriendo en `http://localhost:8000`
- Endpoint `/api/schema/` disponible (OpenAPI)

## 📦 Estructura

- `models/` - TypeScript interfaces generadas
- `services/` - Servicios API (opcional, pod emos usar nuestros propios)
- `schemas/` - JSON Schemas

Usa estos types en tus features:

```typescript
import type { Empleado } from '@/generated/api/models'
```

Ver [README.md](./README.md) para más detalles.
