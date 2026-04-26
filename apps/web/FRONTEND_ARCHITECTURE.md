# Arquitectura Frontend - Feature-Based Structure

## 📁 Estructura Propuesta

```
src/
├── features/                      # Módulos de negocio (cada feature es autónoma)
│   ├── auth/                     # Autenticación y autorización
│   │   ├── components/           # Componentes específicos (LoginForm, LogoutButton)
│   │   ├── pages/                # Páginas (LoginPage, ResetPasswordPage)
│   │   ├── hooks/                # Hooks específicos (useLogin, useRefreshToken)
│   │   ├── services/             # API calls y lógica de autenticación
│   │   ├── context/              # Auth context y providers
│   │   ├── types/                # TypeScript types/interfaces
│   │   └── index.ts              # Re-exports públicos
│   │
│   ├── empleados/                # Gestión de empleados
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── index.ts
│   │
│   ├── vacaciones/               # Gestión de vacaciones
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── index.ts
│   │
│   ├── areas/                    # Gestión de areas
│   ├── usuarios/                 # Gestión de usuarios/roles
│   ├── contratos/                # Gestión de contratos
│   ├── legajo/                   # Legajo del empleado
│   ├── onboarding/               # Onboarding de empleados
│   ├── security/                 # Permisos y seguridad
│   └── admin/                    # Panel de administración
│
├── shared/                        # Código compartido entre features
│   ├── components/               # Componentes reusables (Button, Modal, Table)
│   ├── hooks/                    # Hooks globales (useToast, useDebounce)
│   ├── utils/                    # Funciones utilitarias (format, validation)
│   ├── types/                    # Types globales (User, Empleado, etc)
│   └── index.ts
│
├── layout/                        # Componentes de layout (no son features)
│   ├── AdminLayout.tsx
│   ├── Layout.tsx
│   └── ...
│
├── lib/                          # Librerías y configuraciones (axios, etc)
├── mocks/                        # Mock data para desarrollo/testing
├── test/                         # Configuración y utilidades de testing
├── App.tsx                       # Routing principal
├── main.tsx                      # Entry point
└── vite-env.d.ts
```

---

## 📚 Guía de Migración

### 1. Estructura de una Feature (Ejemplo: Empleados)

```typescript
// src/features/empleados/index.ts - Re-exports públicos
export * from './types'
export * from './services'
export * from './hooks'
export * from './components'
export * from './pages'
```

### 2. Types (Modelos de datos)

```typescript
// src/features/empleados/types/index.ts
export interface Empleado {
  id: number
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento?: string
}

export interface CreateEmpleadoInput {
  nombre: string
  apellido: string
  email: string
}
```

### 3. Services (API calls)

```typescript
// src/features/empleados/services/index.ts
import axios from '@/lib/axios'
import type { Empleado, CreateEmpleadoInput } from '../types'

export const empleadosService = {
  list: async (filters?: Record<string, any>) => {
    const { data } = await axios.get<Empleado[]>('/api/v1/empleados/', { params: filters })
    return data
  },

  get: async (id: number) => {
    const { data } = await axios.get<Empleado>(`/api/v1/empleados/${id}/`)
    return data
  },

  create: async (input: CreateEmpleadoInput) => {
    const { data } = await axios.post<Empleado>('/api/v1/empleados/', input)
    return data
  },

  update: async (id: number, input: Partial<CreateEmpleadoInput>) => {
    const { data } = await axios.patch<Empleado>(`/api/v1/empleados/${id}/`, input)
    return data
  },

  delete: async (id: number) => {
    await axios.delete(`/api/v1/empleados/${id}/`)
  }
}
```

### 4. Hooks (React Query + lógica personalizada)

```typescript
// src/features/empleados/hooks/index.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { empleadosService } from '../services'
import type { Empleado, CreateEmpleadoInput } from '../types'

export const useEmpleados = (filters?: Record<string, any>) => {
  return useQuery({
    queryKey: ['empleados', filters],
    queryFn: () => empleadosService.list(filters),
  })
}

export const useEmpleado = (id: number) => {
  return useQuery({
    queryKey: ['empleado', id],
    queryFn: () => empleadosService.get(id),
  })
}

export const useCreateEmpleado = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: (input: CreateEmpleadoInput) => empleadosService.create(input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['empleados'] })
    }
  })
}

export const useUpdateEmpleado = () => {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: Partial<CreateEmpleadoInput> }) =>
      empleadosService.update(id, input),
    onSuccess: (data) => {
      queryClient.setQueryData(['empleado', data.id], data)
      queryClient.invalidateQueries({ queryKey: ['empleados'] })
    }
  })
}
```

### 5. Components (Componentes específicos)

```typescript
// src/features/empleados/components/EmpleadoCard.tsx
import React from 'react'
import type { Empleado } from '../types'

interface EmpleadoCardProps {
  empleado: Empleado
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
}

export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({ 
  empleado, 
  onEdit, 
  onDelete 
}) => {
  return (
    <div className="card">
      <h3>{empleado.nombre} {empleado.apellido}</h3>
      <p>{empleado.email}</p>
      <div className="actions">
        {onEdit && <button onClick={() => onEdit(empleado.id)}>Editar</button>}
        {onDelete && <button onClick={() => onDelete(empleado.id)}>Eliminar</button>}
      </div>
    </div>
  )
}
```

### 6. Pages (Páginas completas)

```typescript
// src/features/empleados/pages/EmpleadosListPage.tsx
import React from 'react'
import { useEmpleados } from '../hooks'
import { EmpleadoCard } from '../components'
import { LoadingSpinner } from '@/shared/components'

export const EmpleadosListPage: React.FC = () => {
  const { data: empleados, isLoading, error } = useEmpleados()

  if (isLoading) return <LoadingSpinner />
  if (error) return <div>Error: {error.message}</div>

  return (
    <div>
      <h1>Empleados</h1>
      <div className="grid">
        {empleados?.map(emp => (
          <EmpleadoCard key={emp.id} empleado={emp} />
        ))}
      </div>
    </div>
  )
}
```

---

## 🔄 Cómo Importar (Path Aliases)

### tsconfig.json (ya configurado)

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/features/*": ["src/features/*"],
      "@/shared/*": ["src/shared/*"],
      "@/layout/*": ["src/layout/*"],
      "@/*": ["src/*"]
    }
  }
}
```

### Importaciones Limpias

```typescript
// ✅ BIEN - Importar desde el index de la feature
import { useEmpleados, EmpleadoCard } from '@/features/empleados'

// ✅ BIEN - Importar desde shared
import { LoadingSpinner, Button } from '@/shared/components'

// ❌ EVITAR - Importar directamente de archivos internos
import EmpleadoCard from '@/features/empleados/components/EmpleadoCard'

// ❌ EVITAR - Importar desde la raíz de features
import useEmpleados from '@/features/empleados/hooks'
```

---

## 🎯 Principios de Diseño

### 1. **Encapsulación**
   - Cada feature es autónoma y autosuficiente
   - Los detalles internos están ocultos (exportar solo a través de index.ts)
   - Las dependencias entre features deben ser mínimas

### 2. **Reusabilidad**
   - Componentes genéricos van en `shared/`
   - Hooks específicos van en la feature correspondiente
   - Types comunes van en `shared/types`

### 3. **Escalabilidad**
   - Nueva feature: crear carpeta en `features/`
   - Nuevo componente compartido: agregarlo a `shared/`
   - Sin necesidad de modificar rutas globales

### 4. **Testing**
   - Tests cerca del código: `EmpleadoCard/__tests__/EmpleadoCard.test.tsx`
   - O en carpeta `test/` separada con la misma estructura

---

## 🔀 Rutas Principales (App.tsx)

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from '@/features/auth'
import { useAuth } from '@/shared/hooks'

// Pages
import { EmpleadosListPage } from '@/features/empleados'
import { VacacionesListPage } from '@/features/vacaciones'
import { AdminDashboard } from '@/features/admin'

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/empleados" element={<EmpleadosListPage />} />
          <Route path="/vacaciones" element={<VacacionesListPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          {/* ... más rutas */}
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
```

---

## 📋 Checklist de Migración por Feature

- [ ] Crear carpeta `features/{nombre}/`
- [ ] Crear subcarpetas: components/, pages/, hooks/, services/, types/
- [ ] Crear index.ts en cada subcarpeta
- [ ] Crear index.ts en la raíz de la feature
- [ ] Mover componentes de `old-components/{nombre}` → `features/{nombre}/components`
- [ ] Mover pages de `old-pages/{nombre}` → `features/{nombre}/pages`
- [ ] Mover services de `old-services/{nombre}Service.ts` → `features/{nombre}/services/index.ts`
- [ ] Actualizar imports en los archivos movidos
- [ ] Crear types/index.ts con interfaces específicas
- [ ] Crear hooks si no existen
- [ ] Verificar que funciona: `npm run dev`
- [ ] Actualizar tests (si existen)
- [ ] Eliminar carpetas antiguas

---

## 🚀 Next Steps

### Step 7: Implementar React Query + Hooks
- Convertir todos los useAPI() a React Query
- Crear hooks específicos por feature
- Centralizar error handling

### Step 8: Generar TypeScript Types desde OpenAPI
- Correr openapi-typescript-codegen
- Generar types automáticamente desde /api/schema/
- Reemplazar types manuales

### Step 9: Design System
- Crear componentes de UI reutilizables
- Documentar con Storybook
- Mantener consistencia visual

---

## 📖 Referencias

- [Feature-Based Architecture](https://www.patterns.dev/posts/module-pattern/)
- [React Best Practices](https://react.dev)
- [React Query](https://tanstack.com/query/latest)
- [TypeScript](https://www.typescriptlang.org/)
