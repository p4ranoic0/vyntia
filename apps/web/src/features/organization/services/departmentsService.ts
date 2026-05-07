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

export interface AreaStats {
  total_areas: number
  areas_activas: number
  areas_inactivas: number
  total_empleados: number
  areas_sin_jefe: number
  promedio_empleados_por_area: number
  distribucion_por_organo: Array<{
    organo: string
    cantidad: number
    porcentaje: number
  }>
  top_areas_empleados: Array<{
    id: string
    unidad_organica: string
    siglas: string
    empleados_count: number
  }>
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

export interface AreaHierarchy {
  id: string
  unidad_organica: string
  siglas: string
  nivel: number
  parent_id?: string
  children?: AreaHierarchy[]
}

export interface AreaReport {
  id: string
  nombre: string
  descripcion: string
  tipo: 'general' | 'empleados' | 'eficiencia' | 'historico'
  formato: 'pdf' | 'excel' | 'csv'
  parametros?: Record<string, any>
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

  // Estadísticas y análisis
  async getAreasStats(): Promise<AreaStats> {
    const response = await apiClient.get('/api/v1/organization/departments/stats/')
    return response.data.data || response.data
  },

  async getAreasByOrgano(organo?: string): Promise<Area[]> {
    const response = await apiClient.get('/api/v1/organization/departments/', {
      params: organo ? { nombre_organo: organo } : undefined
    })
    return response.data.data || response.data.results || []
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

  async assignEmployeeToArea(areaId: string, empleadoId: string, cargo?: string): Promise<void> {
    const response = await apiClient.post(`/api/v1/organization/departments/${areaId}/empleados/`, {
      empleado_id: empleadoId,
      cargo
    })
    return response.data.data || response.data
  },

  async removeEmployeeFromArea(areaId: string, empleadoId: string): Promise<void> {
    await apiClient.delete(`/api/v1/organization/departments/${areaId}/empleados/${empleadoId}/`)
  },

  async updateEmployeeInArea(areaId: string, empleadoId: string, data: {
    cargo?: string
    fecha_asignacion?: string
  }): Promise<void> {
    const response = await apiClient.patch(`/api/v1/organization/departments/${areaId}/empleados/${empleadoId}/`, data)
    return response.data.data || response.data
  },

  // Jerarquía organizacional
  async getAreaHierarchy(): Promise<AreaHierarchy[]> {
    const response = await apiClient.get('/api/v1/organization/departments/hierarchy/')
    return response.data.data || response.data.results || response.data
  },

  async getAreaChildren(areaId: string): Promise<Area[]> {
    const response = await apiClient.get(`/api/v1/organization/departments/${areaId}/children/`)
    return response.data.data || response.data.results || response.data
  },

  async getAreaParent(areaId: string): Promise<Area | null> {
    const response = await apiClient.get(`/api/v1/organization/departments/${areaId}/parent/`)
    return response.data.data || response.data
  },

  // Reportes y exportación
  async generateReport(params: {
    format: 'pdf' | 'excel' | 'csv'
    areas?: string[]
    include_employees?: boolean
    include_stats?: boolean
    date_range?: {
      start: string
      end: string
    }
  }): Promise<Blob> {
    const response = await apiClient.get('/api/v1/organization/departments/report/', {
      params,
      responseType: 'blob'
    })
    return response.data
  },

  async exportAreas(format: 'excel' | 'csv', filters?: AreasQueryParams): Promise<Blob> {
    const response = await apiClient.get('/api/v1/organization/departments/export/', {
      params: {
        format,
        ...filters
      },
      responseType: 'blob'
    })
    return response.data
  },

  // Búsqueda y filtros avanzados
  async searchAreas(query: string, filters?: {
    organo?: string[]
    estado?: string[]
    tiene_jefe?: boolean
    rango_empleados?: [number, number]
  }): Promise<Area[]> {
    const response = await apiClient.post('/api/v1/organization/departments/search/', {
      query,
      filters
    })
    return response.data.data || response.data.results || response.data
  },

  // Validaciones
  async validateAreaSiglas(siglas: string, excludeId?: string): Promise<{
    is_valid: boolean
    message?: string
  }> {
    const response = await apiClient.post('/api/v1/organization/departments/validate-siglas/', {
      siglas,
      exclude_id: excludeId
    })
    return response.data.data || response.data
  },

  async validateAreaStructure(data: CreateAreaData): Promise<{
    is_valid: boolean
    errors?: Record<string, string[]>
    warnings?: string[]
  }> {
    const response = await apiClient.post('/api/v1/organization/departments/validate/', data)
    return response.data.data || response.data
  },

  // Operaciones masivas
  async bulkUpdateAreas(updates: Array<{
    id: string
    data: Partial<CreateAreaData>
  }>): Promise<{
    success: number
    errors: Array<{
      id: string
      error: string
    }>
  }> {
    const response = await apiClient.post('/api/v1/organization/departments/bulk-update/', { updates })
    return response.data.data || response.data
  },

  async bulkDeleteAreas(ids: string[]): Promise<{
    deleted: number
    errors: Array<{
      id: string
      error: string
    }>
  }> {
    const response = await apiClient.post('/api/v1/organization/departments/bulk-delete/', { ids })
    return response.data.data || response.data
  },

  // Historial y auditoría
  async getAreaHistory(areaId: string): Promise<Array<{
    id: string
    action: string
    changes: Record<string, any>
    user: string
    timestamp: string
  }>> {
    const response = await apiClient.get(`/api/v1/organization/departments/${areaId}/history/`)
    return response.data.data || response.data.results || response.data
  },

  // Configuración y metadatos
  async getAreaMetadata(): Promise<{
    organos_disponibles: string[]
    estados_disponibles: Array<{ value: string, label: string }>
    campos_requeridos: string[]
    validaciones: Record<string, any>
  }> {
    const response = await apiClient.get('/api/v1/organization/departments/metadata/')
    return response.data.data || response.data
  }
}

export default departmentsService