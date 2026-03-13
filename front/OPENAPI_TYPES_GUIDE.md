# TypeScript Generation from OpenAPI Guide

## 🎯 Step 8: Generar TypeScript Types desde OpenAPI

### Objetivo

Generar automáticamente tipos TypeScript completos desde el schema OpenAPI del backend, reemplazando types manuales con tipos verificados en tiempo de compilación.

---

## 📋 Proceso

### 1. Configuración Inicial

**Archivo:** `openapi.config.json`
```json
{
  "input": "http://localhost:8000/api/schema/",
  "output": "src/generated/api",
  "httpClientType": "axios",
  "exportSchemas": true,
  "exportServices": true,
  "exportModels": true
}
```

### 2. Scripts Disponibles

**Windows:** `npm run generate:api` → ejecuta `scripts/generate-api-types.bat`
**Mac/Linux:** `npm run generate:api` → ejecuta `scripts/generate-api-types.sh`

### 3. Generar Tipos

```bash
# Asegurar que backend está corriendo
cd back && python manage.py runserver

# En otra terminal - frontend
npm run generate:api
```

**Resultado:**
```
src/generated/api/
├── models/          # Interfases de tipos
├── services/        # Servicios API
├── schemas/         # JSON Schemas
└── README.md        # Este archivo
```

---

## 🏗️ Estructura Generada

### models/
Interfases TypeScript para cada modelo del backend:

```typescript
// auto-generated
export interface Empleado {
  id: number
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento: string | null
  departamento_id: number
  estado: 'activo' | 'inactivo'
  created_at: string
  updated_at: string
}

export interface CreateEmpleadoInput {
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento?: string | null
  departamento_id: number
}
```

### services/
Servicios pre-generados (opcional, podemos usar nuestros propios):

```typescript
// auto-generated
export class EmpleadosService {
  static async list(): Promise<Empleado[]> { ... }
  static async get(id: number): Promise<Empleado> { ... }
  static async create(data: CreateEmpleadoInput): Promise<Empleado> { ... }
}
```

### schemas/
Esquemas JSON para validación adicional (si usas JSON Schema).

---

## 🔄 Workflow de Migración

### Fase 1: Generar Tipos

```bash
npm run generate:api
# Outputs: src/generated/api/models/ con todos los types
```

### Fase 2: Actualizar Features

**Para cada feature (Ej: Empleados):**

**ANTES:**
```typescript
// src/features/empleados/types/index.ts

export interface Empleado {
  id: number
  nombre: string
  apellido: string
  // ... 20+ campos manuales
}

export interface CreateEmpleadoInput {
  nombre: string
  apellido: string
  // ... más campos
}
```

**DESPUÉS:**
```typescript
// src/features/empleados/types/index.ts

// Importar desde tipos generados
export type { 
  Empleado, 
  CreateEmpleadoInput,
  UpdateEmpleadoInput,
  EmpleadoListParams,
} from '@/generated/api/models'

// O crear aliases si necesitas customización:
export interface EmpleadoWithFormatted extends Empleado {
  nombreCompleto: string
}
```

### Fase 3: Actualizar Services

```typescript
// ANTES
export const empleadosService = {
  list: async (params?: EmpleadoListParams): Promise<Empleado[]> => {
    // custom implementation
  }
}

// DESPUÉS - types verificados automáticamente
import type { Empleado, CreateEmpleadoInput } from '@/generated/api/models'

export const empleadosService = {
  list: async (params?: Record<string, any>): Promise<Empleado[]> => {
    const { data } = await axios.get('/api/v1/empleados/', { params })
    return data // TypeScript verifica que `data` es Empleado[]
  },
  
  create: async (input: CreateEmpleadoInput): Promise<Empleado> => {
    const { data } = await axios.post('/api/v1/empleados/', input)
    return data // TypeScript verifica tipos automáticamente
  }
}
```

---

## ✨ Beneficios

### 1. Zero Manual Type Definitions
```typescript
// Ya no necesitas escribir interfaces manualmente
// Los tipos se generan automáticamente desde el backend
```

### 2. Type Safety en Build Time
```typescript
// ❌ Error caught at compile time
const emp: Empleado = {
  id: 1,
  nombre: 'Juan',
  tipoFonetico: 'JUAN' // ❌ Property doesn't exist
}

// ✅ Correct
const emp: Empleado = {
  id: 1,
  nombre: 'Juan',
  apellido: 'Pérez' // ✅ Verified against generated types
}
```

### 3. Auto-Sync con Backend
Cuando backend cambia:
```bash
npm run generate:api  # Re-génera tipos
npm run build         # Detecta breaking changes
```

### 4. IDE Autocomplete
```typescript
// IDE sugiere automáticamente todos los campos
const empleado: Empleado = {
  id: 1,
  nombre: 'Juan',
  // <-- IDE autocomplete muestra:
  // - apellido
  // - email
  // - fecha_nacimiento
  // - etc.
}
```

---

## 🔄 Mantener Tipos Actualizados

### Cuando Regenerar

1. **Backend - Nuevo modelo**
   ```python
   # models.py - agregar campo nuevo
   fecha_contratacion = models.DateField()
   ```
   
   → Fronted: `npm run generate:api`

2. **Backend - Cambiar endpoint**
   ```python
   # Cambiar response format de Empleado
   ```
   
   → Frontend: `npm run generate:api`

3. **Backend - Nueva versión de API**
   ```python
   # v2/serializers.py con nuevos campos
   ```
   
   → Frontend: `npm run generate:api`

### Checklist

- [ ] Backend tiene OpenAPI schema en `/api/schema/` (desde Step 3 ✅)
- [ ] Backend está corriendo en `http://localhost:8000`
- [ ] Ejecutar `npm run generate:api`
- [ ] Verificar archivos generados en `src/generated/api/`
- [ ] Actualizar imports en features
- [ ] `npm run build` para verificar tipos
- [ ] Commit cambios

---

## 📊 Ejemplo Completo: Feature Empleados

### 1. Generar tipos
```bash
npm run generate:api
```

### 2. Usar en feature

**types/index.ts:**
```typescript
// Re-export de tipos generados
export type {
  Empleado,
  CreateEmpleadoInput,
  UpdateEmpleadoInput,
} from '@/generated/api/models'
```

**services/index.ts:**
```typescript
import axios from '@/lib/axios'
import type { Empleado, CreateEmpleadoInput } from '../types'

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

**hooks/index.ts:**
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { empleadosService } from '../services'
import type { Empleado } from '../types'

export const useEmpleados = () => {
  return useQuery<Empleado[]>({
    queryKey: ['empleados'],
    queryFn: () => empleadosService.list(),
  })
}
```

### 3. Usar en componentes
```typescript
import { useEmpleados } from '@/features/empleados/hooks'
import type { Empleado } from '@/features/empleados/types'

export const EmpleadosList = () => {
  const { data: empleados, isLoading } = useEmpleados()
  
  // TypeScript verifica automáticamente que `empleados` es Empleado[]
  return empleados?.map(emp => (
    <div key={emp.id}>
      {emp.nombre} {emp.apellido}
    </div>
  ))
}
```

---

## 🚨 Troubleshooting

### Error: "Cannot reach backend API"
```bash
# Verificar que backend está corriendo
cd back
python manage.py runserver
```

### Error: "/api/schema/ no encontrado"
```bash
# Verificar que Spectacular está configurado (Step 3)
# En backend: curl http://localhost:8000/api/schema/
```

### Types no se actualizaron
```bash
# Limpiar y regenerar
rm -rf src/generated/api
npm run generate:api
npm run build  # Verificar tipos
```

---

## 🎯 Next Steps

### Step 9: Design System
- Crear componentes reutilizables
- shadcn/ui integration
- Tema consistente

### Step 10: Frontend README + CI/CD
- Guía de setup frontend
- GitHub Actions workflow
- Testing e2e

---

## 📚 Referencias

- [OpenAPI Spec](http://localhost:8000/api/docs/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [openapi-typescript-codegen](https://github.com/ferdikozcan/openapi-typescript-codegen)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

---

## ✅ Validation

Antes de proceder a Step 9:

- [ ] `npm run generate:api` ejecuta sin errores
- [ ] Archivos en `src/generated/api/` se generan correctamente
- [ ] `npm run build` pasa sin type errors
- [ ] Types están disponibles: `import type { Empleado } from '@/generated/api/models'`
- [ ] IDE muestra autocomplete para tipos generados
- [ ] Setup documentation completado
