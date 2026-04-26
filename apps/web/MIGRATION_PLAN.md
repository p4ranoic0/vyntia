# Plan Detallado de Migración - Frontend Reorganización

## 📊 Resumen de Migraciones por Feature

### Feature: AUTH
**Components a migrar:**
- `src/components/auth/LoginForm` → `src/features/auth/components/`
- `src/components/auth/*` → `src/features/auth/components/`

**Pages a migrar:**
- `src/pages/ChangePasswordPage.tsx` → `src/features/auth/pages/`
- `src/pages/ResetPasswordPage.tsx` → `src/features/auth/pages/`

**Services existentes:**
- `src/services/authService.ts` → `src/features/auth/services/index.ts`

**Context a migrar:**
- `src/context/AuthContext.tsx` → `src/features/auth/context/AuthContext.tsx`

**Hooks existentes:**
- `src/hooks/useAuth.ts` → `src/features/auth/hooks/useAuth.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: EMPLEADOS
**Components a migrar:**
- `src/components/empleados/*` → `src/features/empleados/components/`

**Pages a migrar:**
- `src/pages/Empleados.tsx` → `src/features/empleados/pages/`
- `src/pages/empleados/*` → `src/features/empleados/pages/`

**Services existentes:**
- `src/services/employeesService.ts` → `src/features/empleados/services/index.ts`

**Hooks pendientes:**
- `useEmpleados()` - CREATE
- `useEmpleado(id)` - CREATE
- `useCreateEmpleado()` - CREATE
- `useUpdateEmpleado()` - CREATE

**Status:** `🔴 Pendiente migración`

---

### Feature: VACACIONES
**Components a migrar:**
- `src/components/vacaciones/*` → `src/features/vacaciones/components/`

**Pages a migrar:**
- `src/pages/vacaciones/*` → `src/features/vacaciones/pages/`

**Services existentes:**
- `src/services/vacacionesService.ts` → `src/features/vacaciones/services/index.ts`

**Hooks pendientes:**
- `useVacaciones()` - CREATE
- `useSolicitud(id)` - CREATE
- `useCrearSolicitud()` - CREATE

**Status:** `🔴 Pendiente migración`

---

### Feature: AREAS
**Components a migrar:**
- `src/components/areas/*` → `src/features/areas/components/`

**Pages a migrar:**
- `src/pages/areas/*` → `src/features/areas/pages/`

**Services existentes:**
- `src/services/areasService.ts` → `src/features/areas/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: USUARIOS
**Components a migrar:**
- `src/components/users/*` → `src/features/usuarios/components/`

**Pages a migrar:**
- `src/pages/users/*` → `src/features/usuarios/pages/`

**Services existentes:**
- `src/services/usersService.ts` → `src/features/usuarios/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: CONTRATOS
**Pages a migrar:**
- `src/pages/contratos/*` → `src/features/contratos/pages/`

**Services existentes:**
- `src/services/contratosService.ts` → `src/features/contratos/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: LEGAJO
**Pages a migrar:**
- `src/pages/legajo/*` → `src/features/legajo/pages/`

**Services existentes:**
- `src/services/legajoService.ts` → `src/features/legajo/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: ONBOARDING
**Pages a migrar:**
- `src/pages/onboarding/*` → `src/features/onboarding/pages/`

**Services existentes:**
- `src/services/onboardingService.ts` → `src/features/onboarding/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: SECURITY
**Pages a migrar:**
- `src/pages/security/*` → `src/features/security/pages/`

**Services existentes:**
- `src/services/securityService.ts` → `src/features/security/services/index.ts`

**Status:** `🔴 Pendiente migración`

---

### Feature: ADMIN
**Pages a migrar:**
- `src/pages/admin/*` → `src/features/admin/pages/`

**Status:** `🔴 Pendiente migración`

---

## 🔄 Pasos de Migración (Manual o Automático)

### Paso 1: Migrar Services → Types
Para cada feature, extraer types de services en `types/index.ts`:

**Antes:**
```typescript
// src/services/employeesService.ts
interface Empleado {
  id: number
  nombre: string
}

export const employeesService = { ... }
```

**Después:**
```typescript
// src/features/empleados/types/index.ts
export interface Empleado {
  id: number
  nombre: string
}

// src/features/empleados/services/index.ts
import type { Empleado } from '../types'

export const empleadosService = { ... }
```

### Paso 2: Crear React Query Hooks
Para cada feature, crear hooks con React Query:

```typescript
// src/features/empleados/hooks/index.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { empleadosService } from '../services'

export const useEmpleados = () => {
  return useQuery({
    queryKey: ['empleados'],
    queryFn: () => empleadosService.list(),
  })
}
```

### Paso 3: Actualizar Componentes
Actualizar componentes para usar nuevos paths:

**Antes:**
```typescript
import { useApi } from '@/hooks/useApi'
import { employeesService } from '@/services/employeesService'
```

**Después:**
```typescript
import { useEmpleados } from '@/features/empleados/hooks'
```

### Paso 4: Actualizar App.tsx
Cambiar imports de pages:

**Antes:**
```typescript
import { Empleados } from '@/pages/Empleados'
import EmpleadosListPage from '@/pages/empleados/EmpleadosListPage'
```

**Después:**
```typescript
import { EmpleadosListPage } from '@/features/empleados'
```

---

## 📋 Checklist de Ejecución

### Por cada Feature (Ej: Auth)

**Paso 1: Preparar Types**
- [ ] Crear `src/features/auth/types/index.ts`
- [ ] Copiar/extraer interfaces de `authService.ts`
- [ ] Actualizar `authService.ts` para importar types

**Paso 2: Preparar Services**
- [ ] Migrar `src/services/authService.ts` → `src/features/auth/services/index.ts`
- [ ] Verificar imports de types

**Paso 3: Preparar Hooks**
- [ ] Crear hooks con React Query en `hooks/index.ts`
- [ ] Migrar `useAuth` hook si existe

**Paso 4: Preparar Components**
- [ ] Copiar componentes de `components/auth/` → `features/auth/components/`
- [ ] Actualizar imports en componentes
- [ ] Actualizar `components/index.ts`

**Paso 5: Preparar Pages**
- [ ] Copiar pages → `features/auth/pages/`
- [ ] Actualizar imports en pages
- [ ] Actualizar `pages/index.ts`

**Paso 6: Actualizar Contexto (si aplica)**
- [ ] Migrar `AuthContext.tsx` a `features/auth/context/`
- [ ] Crear `context/index.ts` para exports

**Paso 7: Actualizar App.tsx**
- [ ] Cambiar imports de `@/pages/` a `@/features/`
- [ ] Cambiar imports de `@/context/` a `@/features/`
- [ ] Cambiar imports de `@/hooks/` a `@/features/`

**Paso 8: Testing**
- [ ] `npm run dev` - Verificar que todo funciona
- [ ] `npm run build` - Verificar build sin errores
- [ ] `npm run lint` - Verificar no hay errores de lint

**Paso 9: Cleanup Old Folders**
- [ ] Eliminar `src/components/auth/`
- [ ] Eliminar `src/pages/ChangePasswordPage.tsx`
- [ ] Eliminar `src/pages/ResetPasswordPage.tsx`
- [ ] Eliminar archivos migrados

---

## 🎯 Prioridad de Migraciones

### Fase 1: Fundamentals (Auth + Shared)
1. ✅ `src/features/` - Estructura creada
2. ⬜ **AUTH** - Critical, necesario para todo
3. ⬜ **SHARED** - Components/hooks generales

### Fase 2: Core Features
4. ⬜ **EMPLEADOS** - Módulo principal
5. ⬜ **VACACIONES** - Módulo principal
6. ⬜ **AREAS** - Comúnmente usado

### Fase 3: Support Features
7. ⬜ **USUARIOS** - Roles/permisos
8. ⬜ **SECURITY** - Permisos detallados
9. ⬜ **ADMIN** - Panel administrativo

### Fase 4: Complementarios
10. ⬜ **CONTRATOS** - Menos frecuente
11. ⬜ **LEGAJO** - Menos frecuente
12. ⬜ **ONBOARDING** - Menos frecuente

---

## 🔗 Versión 1 de App.tsx (Referencia para actualización)

```typescript
import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/queryClient'

// Auth
import { AuthProvider } from '@/features/auth'
import { useAuth } from '@/features/auth/hooks'

// Layout
import { Layout } from '@/layout/Layout'
import { AdminLayout } from '@/layout/AdminLayout'

// Shared
import { Toaster } from '@/shared/components'
import { LoadingSpinner } from '@/shared/components'

// Features
import { EmpleadosListPage } from '@/features/empleados'
import { VacacionesListPage } from '@/features/vacaciones'
import { AreasListPage } from '@/features/areas'
import { UsersListPage } from '@/features/usuarios'
import { SecurityPage } from '@/features/security'
import { AdminDashboard } from '@/features/admin'
import { LegajoPage } from '@/features/legajo'
import { ContratosPage } from '@/features/contratos'
import { OnboardingPage } from '@/features/onboarding'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <Routes>
      {!isAuthenticated ? (
        <>
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </>
      ) : (
        <>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/empleados" element={<EmpleadosListPage />} />
            <Route path="/vacaciones" element={<VacacionesListPage />} />
            <Route path="/areas" element={<AreasListPage />} />
            <Route path="/contratos" element={<ContratosPage />} />
            <Route path="/legajo" element={<LegajoPage />} />
          </Route>

          <Route element={<AdminLayout />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/usuarios" element={<UsersListPage />} />
            <Route path="/seguridad" element={<SecurityPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
          </Route>
        </>
      )}
    </Routes>
  )
}

export default function AppWithProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <App />
          <Toaster />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  )
}
```

---

## 🚀 Siguientes Pasos

1. **Step 6 (Continuación):** Completar migración de todas las features
2. **Step 7:** Implementar React Query completo + hooks personalizados
3. **Step 8:** Generar TypeScript types desde OpenAPI schema
4. **Step 9:** Crear Design System y componentes reutilizables
5. **Step 10:** Frontend README + CI/CD workflows

---

## 📝 Notas Importantes

- Los archivos antiguos (`src/components/`, `src/pages/`, `src/services/`) seguirán existiendo hasta que todo esté migrado
- Migrar gradualmente (feature por feature) para evitar breaking changes
- Ejecutar `npm run build` después de cada feature para detectar errores temprano
- Los index.ts permiten re-exports limpios y refactoring más fácil después
