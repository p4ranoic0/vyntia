# Generated API Types & Services

Este directorio contiene tipos y servicios generados automáticamente desde el schema OpenAPI del backend.

## 📁 Estructura

```
src/generated/api/
├── models/           # TypeScript interfaces generadas
├── services/         # Servicios API para axios
├── schemas/          # JSON Schemas
└── index.ts         # Re-exports principales
```

## 🔄 Regeneación

Cuando el backend cambia (nuevos endpoints, tipos modificados):

```bash
npm run generate:api
```

**Requisitos:**
- Backend corriendo en `http://localhost:8000`
- Endpoint `/api/schema/` disponible (OpenAPI/Swagger)

## 📦 Cómo Usar

### Importar Types

```typescript
import type { Empleado, Usuario, Vacacion } from '@/generated/api/models'

interface MyComponent {
  empleado: Empleado
  usuarios: Usuario[]
}
```

### Usar en Features

**ANTES (Types manuales):**
```typescript
// src/features/empleados/types/index.ts
export interface Empleado {
  id: number
  nombre: string
  // ... 20+ campos manuales
}
```

**DESPUÉS (Types generados):**
```typescript
// src/features/empleados/types/index.ts
export type { Empleado } from '@/generated/api/models'

// O re-exportar con alias
export type { 
  Empleado as EmpleadoModel,
  CreateEmpleadoInput,
} from '@/generated/api/models'
```

## 🎯 Patrones de Uso

### En Services (React Query)

```typescript
import type { Empleado, CreateEmpleadoInput } from '@/generated/api/models'

export const empleadosService = {
  list: async (): Promise<Empleado[]> => {
    const { data } = await axios.get('/api/v1/empleados/')
    return data
  },
  create: async (input: CreateEmpleadoInput): Promise<Empleado> => {
    const { data } = await axios.post('/api/v1/empleados/', input)
    return data
  }
}
```

### En Componentes

```typescript
import type { Empleado } from '@/generated/api/models'
import { useEmpleados } from '@/features/empleados/hooks'

interface EmpleadoCardProps {
  empleado: Empleado
  onEdit: (empleado: Empleado) => void
}

export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({ 
  empleado, 
  onEdit 
}) => {
  return (
    <div>
      <h3>{empleado.nombre} {empleado.apellido}</h3>
      <button onClick={() => onEdit(empleado)}>Editar</button>
    </div>
  )
}
```

## ✅ Validación

El build fallará si usas tipos que no existen en el schema:

```typescript
// ❌ TypeError si 'telefono' no existe en Empleado
const phone: Empleado['telefono']

// ✅ TypeScript previene el error
const nombre: Empleado['nombre']
```

## 🔗 Referencia

- [OpenAPI Spec](http://localhost:8000/api/docs/) - Documentación interactiva
- [OpenAPI Schema JSON](http://localhost:8000/api/schema/) - Schema crudo
- [openapi-typescript-codegen](https://github.com/ferdikozcan/openapi-typescript-codegen)

## 📝 Notas

- ⚠️ No editar archivos en este directorio manualmente
- 🔄 Regenerar después de cambios en backend
- 📦 Los tipos actualizados están listos para usar sin `npm install`
- 🎯 Full type coverage de toda la API con 0 esfuerzo manual
