/**
 * EXAMPLE: Empleados Feature Con React Query
 *
 * Este archivo muestra el patrón correcto para implementar React Query
 * en una feature. Usarlo como template para las demás features.
 *
 * Estructura:
 * 1. Types (TypeScript interfaces)
 * 2. API Service (llamadas HTTP)
 * 3. React Query Hooks (useQuery, useMutation)
 * 4. Componentes que consumen los hooks
 */

// ============================================================================
// 1. TYPES - Definir interfaces en types/index.ts
// ============================================================================

export interface Empleado {
  id: number
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento?: string
  departamento_id: number
  estado: 'activo' | 'inactivo'
  created_at: string
  updated_at: string
}

export interface CreateEmpleadoInput {
  nombre: string
  apellido: string
  email: string
  fecha_nacimiento?: string
  departamento_id: number
}

export interface UpdateEmpleadoInput extends Partial<CreateEmpleadoInput> {}

export interface EmpleadoListParams {
  page?: number
  limit?: number
  search?: string
  departamento_id?: number
  estado?: 'activo' | 'inactivo'
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ============================================================================
// 2. API SERVICE - Definir en services/index.ts
// ============================================================================

import axios from '@/lib/axios'

export const empleadosService = {
  /**
   * Listar empleados con filtros opcionales
   */
  list: async (params?: EmpleadoListParams) => {
    const { data } = await axios.get<PaginatedResponse<Empleado>>(
      '/api/v1/empleados/',
      { params }
    )
    return data
  },

  /**
   * Obtener un empleado específico
   */
  get: async (id: number) => {
    const { data } = await axios.get<Empleado>(`/api/v1/empleados/${id}/`)
    return data
  },

  /**
   * Crear nuevo empleado
   */
  create: async (input: CreateEmpleadoInput) => {
    const { data } = await axios.post<Empleado>('/api/v1/empleados/', input)
    return data
  },

  /**
   * Actualizar empleado
   */
  update: async (id: number, input: UpdateEmpleadoInput) => {
    const { data } = await axios.patch<Empleado>(
      `/api/v1/empleados/${id}/`,
      input
    )
    return data
  },

  /**
   * Eliminar empleado
   */
  delete: async (id: number) => {
    await axios.delete(`/api/v1/empleados/${id}/`)
  },

  /**
   * Cambiar estado de empleado
   */
  changeStatus: async (id: number, estado: 'activo' | 'inactivo') => {
    const { data } = await axios.patch<Empleado>(
      `/api/v1/empleados/${id}/`,
      { estado }
    )
    return data
  },
}

// ============================================================================
// 3. REACT QUERY HOOKS - Definir en hooks/index.ts
// ============================================================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/shared/hooks'

// Query Keys - organizados por feature
const EMPLEADOS_KEY = ['empleados'] as const

export const empleadosKeys = {
  all: [...EMPLEADOS_KEY],
  lists: () => [...EMPLEADOS_KEY, 'list'],
  list: (params?: EmpleadoListParams) => [...empleadosKeys.lists(), params],
  details: () => [...EMPLEADOS_KEY, 'detail'],
  detail: (id: number) => [...empleadosKeys.details(), id],
}

/**
 * Obtener lista de empleados con posibles filtros
 *
 * Uso:
 * const { data, isLoading, error } = useEmpleados({ departamento_id: 1 })
 */
export const useEmpleados = (params?: EmpleadoListParams) => {
  return useQuery({
    queryKey: empleadosKeys.list(params),
    queryFn: () => empleadosService.list(params),
    // Mantener datos en cache por 5 minutos
    staleTime: 5 * 60 * 1000,
    // Garbage Collection después de 10 minutos sin uso
    gcTime: 10 * 60 * 1000,
  })
}

/**
 * Obtener un empleado específico
 *
 * Uso:
 * const { data: empleado, isLoading } = useEmpleado(123)
 */
export const useEmpleado = (id: number) => {
  return useQuery({
    queryKey: empleadosKeys.detail(id),
    queryFn: () => empleadosService.get(id),
    enabled: !!id, // Solo fetch si tenemos un ID válido
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * Crear nuevo empleado
 *
 * Uso:
 * const { mutate: createEmpleado, isPending } = useCreateEmpleado()
 * createEmpleado(
 *   { nombre: 'Juan', ... },
 *   {
 *     onSuccess: (data) => { ... }
 *   }
 * )
 */
export const useCreateEmpleado = () => {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: (input: CreateEmpleadoInput) => empleadosService.create(input),
    onSuccess: (data) => {
      // Invalidar lista para que se refresque
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      // Setear el nuevo empleado en cache
      queryClient.setQueryData(empleadosKeys.detail(data.id), data)
      toast.success('Empleado creado exitosamente')
    },
    onError: (error) => {
      toast.error('Error al crear empleado')
      console.error(error)
    },
  })
}

/**
 * Actualizar empleado
 *
 * Uso:
 * const { mutate: updateEmpleado } = useUpdateEmpleado()
 * updateEmpleado({ id: 123, input: { nombre: 'Juan Carlos' } })
 */
export const useUpdateEmpleado = () => {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: ({ id, input }: { id: number; input: UpdateEmpleadoInput }) =>
      empleadosService.update(id, input),
    onSuccess: (data) => {
      // Actualizar el empleado en cache
      queryClient.setQueryData(empleadosKeys.detail(data.id), data)
      // Invalidar lista para refresco en background
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      toast.success('Empleado actualizado')
    },
    onError: (error) => {
      toast.error('Error al actualizar empleado')
      console.error(error)
    },
  })
}

/**
 * Eliminar empleado
 *
 * Uso:
 * const { mutate: deleteEmpleado } = useDeleteEmpleado()
 * deleteEmpleado(123)
 */
export const useDeleteEmpleado = () => {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: (id: number) => empleadosService.delete(id),
    onSuccess: (_, id) => {
      // Remover del cache
      queryClient.removeQueries({ queryKey: empleadosKeys.detail(id) })
      // Invalidar lista
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
      toast.success('Empleado eliminado')
    },
    onError: (error) => {
      toast.error('Error al eliminar empleado')
      console.error(error)
    },
  })
}

/**
 * Cambiar estado de un empleado
 */
export const useChangeEmpleadoStatus = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, estado }: { id: number; estado: 'activo' | 'inactivo' }) =>
      empleadosService.changeStatus(id, estado),
    onSuccess: (data) => {
      queryClient.setQueryData(empleadosKeys.detail(data.id), data)
      queryClient.invalidateQueries({ queryKey: empleadosKeys.lists() })
    },
  })
}

// ============================================================================
// 4. EJEMPLOS DE COMPONENTES CONSUMIENDO LOS HOOKS
// ============================================================================

/**
 * EJEMPLO 1: Componente de lista con carga de datos
 */

import React from 'react'

interface EmpleadosListProps {
  departamentoId?: number
}

export const EmpleadosList: React.FC<EmpleadosListProps> = ({ departamentoId }) => {
  // Usar el hook para obtener datos
  const { data: response, isLoading, error, isError } = useEmpleados({
    departamento_id: departamentoId,
  })

  if (isLoading) {
    return <div>Cargando empleados...</div>
  }

  if (isError) {
    return <div>Error: {error?.message}</div>
  }

  if (!response?.results.length) {
    return <div>No hay empleados</div>
  }

  return (
    <div>
      <h2>Empleados ({response.count})</h2>
      <div className="grid">
        {response.results.map(emp => (
          <EmpleadoCard key={emp.id} empleado={emp} />
        ))}
      </div>
    </div>
  )
}

/**
 * EJEMPLO 2: Componente de formulario con creación
 */

interface EmpleadoFormProps {
  onSuccess?: () => void
}

export const EmpleadoForm: React.FC<EmpleadoFormProps> = ({ onSuccess }) => {
  const [formData, setFormData] = React.useState<CreateEmpleadoInput>({
    nombre: '',
    apellido: '',
    email: '',
    departamento_id: 1,
  })

  // Usar mutation para crear
  const { mutate: createEmpleado, isPending } = useCreateEmpleado()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createEmpleado(formData, {
      onSuccess: () => {
        setFormData({ nombre: '', apellido: '', email: '', departamento_id: 1 })
        onSuccess?.()
      },
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={formData.nombre}
        onChange={e => setFormData({ ...formData, nombre: e.target.value })}
        placeholder="Nombre"
        required
      />
      <input
        value={formData.apellido}
        onChange={e => setFormData({ ...formData, apellido: e.target.value })}
        placeholder="Apellido"
        required
      />
      <input
        type="email"
        value={formData.email}
        onChange={e => setFormData({ ...formData, email: e.target.value })}
        placeholder="Email"
        required
      />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Creando...' : 'Crear Empleado'}
      </button>
    </form>
  )
}

/**
 * EJEMPLO 3: Componente de detalle con actualización
 */

interface EmpleadoDetailProps {
  id: number
  onDelete?: () => void
}

export const EmpleadoDetail: React.FC<EmpleadoDetailProps> = ({ id, onDelete }) => {
  // Query para obtener detalles
  const { data: empleado, isLoading: loadingDetail } = useEmpleado(id)

  // Mutation para actualizar
  const { mutate: updateEmpleado, isPending: updatingStatus } = useUpdateEmpleado()

  // Mutation para eliminar
  const { mutate: deleteEmpleado, isPending: deletingStatus } = useDeleteEmpleado()

  if (loadingDetail) {
    return <div>Cargando...</div>
  }

  if (!empleado) {
    return <div>Empleado no encontrado</div>
  }

  const handleDelete = () => {
    if (confirm('¿Estás seguro de que deseas eliminar este empleado?')) {
      deleteEmpleado(id, {
        onSuccess: () => onDelete?.(),
      })
    }
  }

  return (
    <div>
      <h1>{empleado.nombre} {empleado.apellido}</h1>
      <p>Email: {empleado.email}</p>

      <button
        onClick={() => updateEmpleado({
          id: empleado.id,
          input: {
            nombre: empleado.nombre + ' (Actualizado)',
          },
        })}
        disabled={updatingStatus}
      >
        {updatingStatus ? 'Actualizando...' : 'Actualizar'}
      </button>

      <button onClick={handleDelete} disabled={deletingStatus}>
        {deletingStatus ? 'Eliminando...' : 'Eliminar'}
      </button>
    </div>
  )
}
