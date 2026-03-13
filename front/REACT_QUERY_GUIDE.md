# Step 7: React Query Implementation Guide

## 🎯 Objetivo

Migrar todos los datos fetching de `useApi` hook genérico a React Query con hooks específicos por feature.

**Beneficios:**
- ✅ Cache automático y smart invalidation
- ✅ Sincronización de estado global sin Redux
- ✅ Loading/error states built-in
- ✅ Background refetching automático
- ✅ Deduplication de requests
- ✅ Offline support potencial

---

## 📋 Checklist por Feature

### Fase 1: Setup Global
- [x] Crear `lib/queryClient.ts` con configuración
- [x] Crear hooks compartidos: `usePermission`, `useDebounce`, `useToast`
- [ ] Actualizar `main.tsx` para agregar `<QueryClientProvider>`
- [ ] Actualizar `App.tsx` para usar queryClient

### Fase 2: Auth Feature
- [ ] Implementar `services/index.ts` con authService
- [ ] Crear hooks: `useLogin`, `useLogout`, `useRefreshToken`
- [ ] Actualizar componentes para usar hooks
- [ ] Actualizar `context/AuthContext.tsx`

### Fase 3: Empleados Feature
- [x] Template created (REACT_QUERY_EXAMPLE.ts)
- [ ] Implementar `types/index.ts`
- [ ] Implementar `services/index.ts`
- [ ] Implementar `hooks/index.ts`
- [ ] Actualizar/crear componentes
- [ ] Actualizar pages

### Fase 4-10: Otras Features
- [ ] Vacaciones
- [ ] Areas
- [ ] Usuarios
- [ ] Contratos
- [ ] Legajo
- [ ] Onboarding
- [ ] Security
- [ ] Admin

---

## 👣 Pasos para Implementar en una Feature

### 1. Definir Types (`features/{feature}/types/index.ts`)

```typescript
export interface Empleado {
  id: number
  nombre: string
  // ... más campos
}

export interface CreateEmpleadoInput {
  nombre: string
  // ... más campos
}
```

### 2. Implementar Services (`features/{feature}/services/index.ts`)

```typescript
import axios from '@/lib/axios'

export const empleadosService = {
  list: async (params?) => {
    const { data } = await axios.get('/api/v1/empleados/', { params })
    return data
  },
  get: async (id) => {
    const { data } = await axios.get(`/api/v1/empleados/${id}/`)
    return data
  },
  // ... rest de métodos
}
```

### 3. Crear Query Keys (`features/{feature}/hooks/index.ts`)

```typescript
const EMPLEADOS_KEY = ['empleados'] as const

export const empleadosKeys = {
  all: [...EMPLEADOS_KEY],
  lists: () => [...EMPLEADOS_KEY, 'list'],
  list: (params?) => [...empleadosKeys.lists(), params],
  details: () => [...EMPLEADOS_KEY, 'detail'],
  detail: (id) => [...empleadosKeys.details(), id],
}
```

### 4. Crear Query Hooks

```typescript
export const useEmpleados = (params?) => {
  return useQuery({
    queryKey: empleadosKeys.list(params),
    queryFn: () => empleadosService.list(params),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}
```

### 5. Crear Mutation Hooks

```typescript
export const useCreateEmpleado = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input) => empleadosService.create(input),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      toast.success('Creado exitosamente')
    },
  })
}
```

### 6. Usar en Componentes

**OLD (useApi):**
```typescript
const { data: empleados, loading } = useApi('/api/v1/empleados/')
```

**NEW (React Query):**
```typescript
const { data, isLoading } = useEmpleados()
```

---

## 🔄 Invalidation Patterns

### Cuando invalidar qué:

**Crear nuevo item:**
```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
}
```

**Actualizar item:**
```typescript
onSuccess: (data) => {
  // Actualizar cache directamente
  queryClient.setQueryData(empleadosKeys.detail(data.id), data)
  // Refresco en background
  queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
}
```

**Eliminar item:**
```typescript
onSuccess: (_, id) => {
  // Remover del cache
  queryClient.removeQueries({ queryKey: empleadosKeys.detail(id) })
  // Refresco de lista
  queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
}
```

---

## 🎮 Ejemplos de Uso en Componentes

### Lista simple:
```typescript
const { data: empleados, isLoading, error } = useEmpleados()

if (isLoading) return <Spinner />
if (error) return <Error />

return empleados.map(e => <Card key={e.id} {...e} />)
```

### Crear:
```typescript
const { mutate, isPending } = useCreateEmpleado()

const handleSubmit = (formData) => {
  mutate(formData, {
    onSuccess: () => {
      toast.success('Creado')
      // ... más lógica
    }
  })
}
```

### Detalle + Actualizar:
```typescript
const { data: empleado } = useEmpleado(idParam)
const { mutate: update, isPending } = useUpdateEmpleado()

const handleUpdate = (changes) => {
  update({ id: empleado.id, input: changes })
}
```

---

## 🚨 Patrones de Error

**Manejar errores en mutations:**
```typescript
const { mutate } = useMutation({
  mutationFn: (data) => API.call(data),
  onError: (error: AxiosError) => {
    if (error.response?.status === 400) {
      toast.error('Validación fallida')
    } else if (error.response?.status === 401) {
      // Redirigir a login
    } else {
      toast.error('Error inesperado')
    }
  }
})
```

---

## 🔐 Manejo de Autenticación

Auth ya está en context, pero con React Query:

```typescript
export const useAuth = () => {
  const { user, token } = useContext(AuthContext)
  
  const login = useMutation({
    mutationFn: (creds) => authService.login(creds),
    onSuccess: (data) => {
      // Guardar token en context
      // Guardar user en cache
      queryClient.setQueryData(authKeys.user(), data.user)
    }
  })
  
  return { user, login, logout, ... }
}
```

---

## 📊 DevTools (Desarrollo)

Agregar React Query DevTools:

```bash
npm install @tanstack/react-query-devtools
```

```typescript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* ... app content */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

---

## 🎯 Key Principles

1. **Query Keys**: Deben ser consistentes y previsibles
2. **Stale Time**: Qué tan viejo puede ser un dato antes de refetchar
3. **GC Time (gcTime/cacheTime)**: Cuánto tiempo mantener en cache sin usar
4. **Smart Invalidation**: Solo invalidar lo necesario
5. **Mutations first**: Actualizar cache optimistically si es posible
6. **Error boundaries**: Manejar errores consistentemente

---

## 📚 Referencias

- [React Query Docs](https://tanstack.com/query/latest)
- [Query Keys Guide](https://tanstack.com/query/latest/docs/react/guides/important-defaults#querykey)
- [Mutations](https://tanstack.com/query/latest/docs/react/guides/mutations)
- [Invalidation Strategy](https://tanstack.com/query/latest/docs/react/guides/query-invalidation)

---

## ✅ Validation Before Merging

- [ ] `npm run dev` - sin errores
- [ ] `npm run build` - build exitoso
- [ ] `npm run lint` - no hay warnings
- [ ] Múltiples requests al mismo endpoint solo hacen 1 request
- [ ] Datos se cachean correctamente
- [ ] React Query DevTools muestra queries esperadas
