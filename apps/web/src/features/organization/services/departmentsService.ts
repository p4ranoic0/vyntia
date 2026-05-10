import { apiClient } from '@/shared/api/api'

// Interfaces para Áreas
export interface Area {
  id: string
  nombre_organo: string
  nombre_unidad_organica?: string
  siglas_area: string
  descripcion_area?: string
  estado_area: 'activo' | 'inactivo'
  nombre_completo?: string
  es_activa?: boolean
  empleados_activos_count?: number
  empleados_count?: number
}

export interface CreateAreaData {
  nombre_organo: string
  nombre_unidad_organica?: string
  siglas_area: string
  descripcion_area?: string
  estado_area?: 'activo' | 'inactivo'
}

export interface UpdateAreaData extends Partial<CreateAreaData> {
  id: string
}

export interface AreaEmployee {
  id: string
  nombres: string
  apellidos: string
  numero_documento: string
  cargo?: string
  fecha_ingreso?: string
  estado?: string
}

// Parámetros de consulta
export interface AreasQueryParams {
  page?: number
  page_size?: number
  search?: string
  nombre_organo?: string
  estado_area?: 'activo' | 'inactivo'
  ordering?: string
}

export interface AreasResponse {
  success: boolean
  message: string
  data: Area[]
  meta?: {
    pagination: {
      current_page: number
      total_pages: number
      total_items: number
      page_size: number
      has_next: boolean
      has_previous: boolean
      next_page: number | null
      previous_page: number | null
      links: {
        next: string | null
        previous: string | null
      }
    }
  }
}

// Servicio de Áreas
export const departmentsService = {
  // Operaciones CRUD básicas
  async getAreas(params?: AreasQueryParams): Promise<AreasResponse> {
    const response = await apiClient.get('/api/v1/organization/departments/', { params })
    return response.data
  },

  async getArea(id: string): Promise<Area> {
    const response = await apiClient.get(`/api/v1/organization/departments/${id}/`)
    return response.data
  },

  async createArea(data: CreateAreaData): Promise<Area> {
    const response = await apiClient.post('/api/v1/organization/departments/', data)
    return response.data.data || response.data
  },

  async updateArea(id: string, data: Partial<CreateAreaData>): Promise<Area> {
    const response = await apiClient.patch(`/api/v1/organization/departments/${id}/`, data)
    return response.data.data || response.data
  },

  async deleteArea(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/organization/departments/${id}/`)
  },

  // Gestión de empleados por área
  async getAreaEmployees(areaId: string, params?: {
    page?: number
    page_size?: number
    search?: string
    cargo?: string
    estado?: string
  }): Promise<{
    count: number
    results: AreaEmployee[]
  }> {
    const response = await apiClient.get(`/api/v1/organization/departments/${areaId}/empleados/`, { params })
    return response.data.data || response.data
  },

}

export default departmentsService