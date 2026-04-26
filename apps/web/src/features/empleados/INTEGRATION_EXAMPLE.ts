/**
 * EJEMPLO: Empleados Feature - DESPUÉS de usar tipos generados
 *
 * Muestra cómo la feature se simplifica y tipo-verifica usando
 * types generados desde OpenAPI.
 */

// ============================================================================
// 1. types/index.ts - SIMPLIFICADO
// ============================================================================

// ✅ Solo re-exportar de tipos generados
// ✅ Agregar tipos de formulario si es necesario
export type {
  Empleado,
  CreateEmpleadoInput,
  UpdateEmpleadoInput,
  PaginatedResponse,
} from '@/generated/api/models'

// Tipos adicionales específicos de la feature (no del backend)
export interface EmpleadoFilters {
  search?: string
  departamento_id?: number
  estado?: 'activo' | 'inactivo'
  sort_by?: 'nombre' | 'apellido' | '-nombre' | '-apellido'
}

// ============================================================================
// 2. services/index.ts - SIMPLIFICADO
// ============================================================================

import axios from '@/lib/axios'
import type {
  Empleado,
  CreateEmpleadoInput,
  UpdateEmpleadoInput,
  PaginatedResponse,
} from '../types'

export const empleadosService = {
  // Tipos verificados automáticamente desde OpenAPI
  list: async (
    filters?: Record<string, any>
  ): Promise<PaginatedResponse<Empleado>> => {
    const { data } = await axios.get('/api/v1/empleados/', { params: filters })
    return data
  },

  get: async (id: number): Promise<Empleado> => {
    const { data } = await axios.get(`/api/v1/empleados/${id}/`)
    return data
  },

  create: async (input: CreateEmpleadoInput): Promise<Empleado> => {
    const { data } = await axios.post('/api/v1/empleados/', input)
    return data
  },

  update: async (
    id: number,
    input: UpdateEmpleadoInput
  ): Promise<Empleado> => {
    const { data } = await axios.patch(`/api/v1/empleados/${id}/`, input)
    return data
  },

  delete: async (id: number): Promise<void> => {
    await axios.delete(`/api/v1/empleados/${id}/`)
  },
}

// ============================================================================
// 3. hooks/index.ts - SIMPLIFICADO CON TIPOS VERIFICADOS
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { empleadosService } from '../services'
import type { Empleado, CreateEmpleadoInput, UpdateEmpleadoInput } from '../types'
import { useToast } from '@/shared/hooks'

// Query keys
const EMPLEADOS_KEY = ['empleados'] as const

export const empleadosKeys = {
  all: [...EMPLEADOS_KEY],
  lists: () => [...EMPLEADOS_KEY, 'list'],
  list: (filters?: Record<string, any>) => [...empleadosKeys.lists(), filters],
  details: () => [...EMPLEADOS_KEY, 'detail'],
  detail: (id: number) => [...empleadosKeys.details(), id],
}

/**
 * Hook para listar empleados
 * TypeScript verifica que el retorno es PaginatedResponse<Empleado>
 */
export const useEmpleados = (filters?: Record<string, any>) => {
  return useQuery({
    queryKey: empleadosKeys.list(filters),
    queryFn: () => empleadosService.list(filters),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  })
}

/**
 * Hook para obtener un empleado
 * TypeScript verifica que el retorno es Empleado | undefined
 */
export const useEmpleado = (id: number) => {
  return useQuery({
    queryKey: empleadosKeys.detail(id),
    queryFn: () => empleadosService.get(id),
    enabled: !!id,
  })
}

/**
 * Hook para crear empleado
 * TypeScript verifica que CreateEmpleadoInput tiene los campos correctos
 */
export const useCreateEmpleado = () => {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: (input: CreateEmpleadoInput) =>
      empleadosService.create(input),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      queryClient.setQueryData(empleadosKeys.detail(data.id), data)
      toast.success('Empleado creado')
    },
    onError: () => {
      toast.error('Error al crear empleado')
    },
  })
}

/**
 * Hook para actualizar empleado
 * TypeScript verifica que UpdateEmpleadoInput coincide con Empleado
 */
export const useUpdateEmpleado = () => {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: UpdateEmpleadoInput }) =>
      empleadosService.update(id, input),
    onSuccess: (data) => {
      queryClient.setQueryData(empleadosKeys.detail(data.id), data)
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      toast.success('Empleado actualizado')
    },
    onError: () => {
      toast.error('Error al actualizar')
    },
  })
}

// ============================================================================
// 4. components/EmpleadoCard.tsx - CON TIPOS VERIFICADOS
// ============================================================================

import React from 'react'

interface EmpleadoCardProps {
  // ✅ Tipo verificado desde OpenAPI
  empleado: Empleado
  onEdit?: (id: number) => void
  onDelete?: (id: number) => void
}

export const EmpleadoCard: React.FC<EmpleadoCardProps> = ({
  empleado,
  onEdit,
  onDelete,
}) => {
  return (
    <div className="card p-4 border rounded">
      {/* ✅ TypeScript verifica que estos campos existen */}
      <h3 className="font-bold">
        {empleado.nombre} {empleado.apellido}
      </h3>
      <p className="text-sm text-gray-600">{empleado.email}</p>

      {/* ✅ TypeScript verifica que estado es 'activo' | 'inactivo' */}
      <span className={`badge ${empleado.estado === 'activo' ? 'bg-green' : 'bg-red'}`}>
        {empleado.estado}
      </span>

      <div className="flex gap-2 mt-4">
        {onEdit && (
          <button onClick={() => onEdit(empleado.id)} className="btn btn-sm">
            Editar
          </button>
        )}
        {onDelete && (
          <button onClick={() => onDelete(empleado.id)} className="btn btn-sm btn-danger">
            Eliminar
          </button>
        )}
      </div>
    </div>
  )
}

// ============================================================================
// 5. components/EmpleadoForm.tsx - CON REACT HOOK FORM + ZOD
// ============================================================================

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import type { CreateEmpleadoInput } from '../types'

// ✅ Schema Zod - validación en frontend que coincide con backend
const createEmpleadoSchema = z.object({
  nombre: z.string().min(1, 'Nombre requerido').max(255),
  apellido: z.string().min(1, 'Apellido requerido').max(255),
  email: z.string().email('Email inválido'),
  fecha_nacimiento: z.string().optional().nullable(),
  departamento_id: z.number().min(1, 'Departamento requerido'),
})

type CreateEmpleadoFormData = z.infer<typeof createEmpleadoSchema>

interface EmpleadoFormProps {
  onSubmit: (data: CreateEmpleadoInput) => void
  isLoading?: boolean
}

export const EmpleadoForm: React.FC<EmpleadoFormProps> = ({
  onSubmit,
  isLoading,
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateEmpleadoFormData>({
    resolver: zodResolver(createEmpleadoSchema),
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label>Nombre</label>
        <input {...register('nombre')} placeholder="Juan" />
        {errors.nombre && <span className="error">{errors.nombre.message}</span>}
      </div>

      <div>
        <label>Apellido</label>
        <input {...register('apellido')} placeholder="Pérez" />
        {errors.apellido && <span className="error">{errors.apellido.message}</span>}
      </div>

      <div>
        <label>Email</label>
        <input type="email" {...register('email')} placeholder="juan@example.com" />
        {errors.email && <span className="error">{errors.email.message}</span>}
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Guardando...' : 'Crear Empleado'}
      </button>
    </form>
  )
}

// ============================================================================
// 6. pages/EmpleadosListPage.tsx - PÁGINA COMPLETA
// ============================================================================

import { useEmpleados, useDeleteEmpleado } from '../hooks'
import { EmpleadoCard } from '../components/EmpleadoCard'
import { LoadingSpinner } from '@/shared/components'

export const EmpleadosListPage: React.FC = () => {
  // ✅ TypeScript sabe que data es PaginatedResponse<Empleado> | undefined
  const { data, isLoading, error } = useEmpleados()
  const { mutate: deleteEmpleado } = useDeleteEmpleado()

  if (isLoading) return <LoadingSpinner />
  if (error) return <div>Error: {error.message}</div>
  if (!data?.results) return <div>Sin empleados</div>

  return (
    <div className="space-y-4">
      <h1>Empleados ({data.count})</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* ✅ map verifica que results es Empleado[] */}
        {data.results.map((emp) => (
          <EmpleadoCard
            key={emp.id}
            empleado={emp}
            onDelete={(id) => {
              if (confirm('¿Eliminar empleado?')) {
                deleteEmpleado(id)
              }
            }}
          />
        ))}
      </div>

      {/* Paginación */}
      {data.next && (
        <button className="btn">Siguiente página</button>
      )}
    </div>
  )
}

// ============================================================================
// COMPARACIÓN: ANTES vs DESPUÉS
// ============================================================================

/**
 * CÓDIGO ANTES (Types manuales)
 * 
 * types/index.ts:
 * - 50+ líneas de interfaces manuales
 * - Propenso a errores
 * - Debe sincronizarse con backend manualmente
 * - Sin validación en typecheck
 * 
 * services/index.ts:
 * - Tipos inconsistentes
 * - Sin intellisense
 * - Cambios en backend requieren actualización manual
 * 
 * CÓDIGO DESPUÉS (Types generados)
 * 
 * types/index.ts:
 * - 3 líneas de re-exports
 * - Sincronizado automáticamente con backend
 * - Full type coverage
 * 
 * services/index.ts:
 * - Tipos verificados automáticamente
 * - Intellisense completo
 * - npm run generate:api y listo
 */

export {}
