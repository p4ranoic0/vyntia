import { apiClient } from '@/lib/api'

// Interfaces para Áreas
export interface Area {
  area_id: number
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
  id: number
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
    id: number
    unidad_organica: string
    siglas: string
    empleados_count: number
  }>
}

export interface AreaEmployee {
  id: number
  nombres: string
  apellidos: string
  numero_documento: string
  cargo?: string
  fecha_ingreso?: string
  estado?: string
}

export interface AreaHierarchy {
  id: number
  unidad_organica: string
  siglas: string
  nivel: number
  parent_id?: number
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
export const areasService = {
  // Operaciones CRUD básicas
  async getAreas(params?: AreasQueryParams): Promise<AreasResponse> {
    const response = await apiClient.get('/api/v1/rrhh/areas/', { params })
    return response.data
  },

  async getArea(id: number): Promise<Area> {
    const response = await apiClient.get(`/api/v1/rrhh/areas/${id}/`)
    return response.data
  },

  async createArea(data: CreateAreaData): Promise<Area> {
    const response = await apiClient.post('/api/v1/rrhh/areas/', data)
    return response.data.data || response.data
  },

  async updateArea(id: number, data: Partial<CreateAreaData>): Promise<Area> {
    const response = await apiClient.patch(`/api/v1/rrhh/areas/${id}/`, data)
    return response.data.data || response.data
  },

  async deleteArea(id: number): Promise<void> {
    await apiClient.delete(`/api/v1/rrhh/areas/${id}/`)
  },

  // Estadísticas y análisis
  async getAreasStats(): Promise<AreaStats> {
    const response = await apiClient.get('/api/v1/rrhh/areas/stats/')
    return response.data.data || response.data
  },

  async getAreasByOrgano(organo?: string): Promise<Area[]> {
    const response = await apiClient.get('/api/v1/rrhh/areas/', {
      params: organo ? { nombre_organo: organo } : undefined
    })
    return response.data.data || response.data.results || []
  },

  // Gestión de empleados por área
  async getAreaEmployees(areaId: number, params?: {
    page?: number
    page_size?: number
    search?: string
    cargo?: string
    estado?: string
  }): Promise<{
    count: number
    results: AreaEmployee[]
  }> {
    const response = await apiClient.get(`/api/v1/rrhh/areas/${areaId}/empleados/`, { params })
    return response.data.data || response.data
  },

  async assignEmployeeToArea(areaId: number, empleadoId: number, cargo?: string): Promise<void> {
    const response = await apiClient.post(`/api/v1/rrhh/areas/${areaId}/empleados/`, {
      empleado_id: empleadoId,
      cargo
    })
    return response.data.data || response.data
  },

  async removeEmployeeFromArea(areaId: number, empleadoId: number): Promise<void> {
    await apiClient.delete(`/api/v1/rrhh/areas/${areaId}/empleados/${empleadoId}/`)
  },

  async updateEmployeeInArea(areaId: number, empleadoId: number, data: {
    cargo?: string
    fecha_asignacion?: string
  }): Promise<void> {
    const response = await apiClient.patch(`/api/v1/rrhh/areas/${areaId}/empleados/${empleadoId}/`, data)
    return response.data.data || response.data
  },

  // Jerarquía organizacional
  async getAreaHierarchy(): Promise<AreaHierarchy[]> {
    const response = await apiClient.get('/api/v1/rrhh/areas/hierarchy/')
    return response.data.data || response.data.results || response.data
  },

  async getAreaChildren(areaId: number): Promise<Area[]> {
    const response = await apiClient.get(`/api/v1/rrhh/areas/${areaId}/children/`)
    return response.data.data || response.data.results || response.data
  },

  async getAreaParent(areaId: number): Promise<Area | null> {
    const response = await apiClient.get(`/api/v1/rrhh/areas/${areaId}/parent/`)
    return response.data.data || response.data
  },

  // Reportes y exportación
  async generateReport(params: {
    format: 'pdf' | 'excel' | 'csv'
    areas?: number[]
    include_employees?: boolean
    include_stats?: boolean
    date_range?: {
      start: string
      end: string
    }
  }): Promise<Blob> {
    const response = await apiClient.get('/api/v1/rrhh/areas/report/', {
      params,
      responseType: 'blob'
    })
    return response.data
  },

  async exportAreas(format: 'excel' | 'csv', filters?: AreasQueryParams): Promise<Blob> {
    const response = await apiClient.get('/api/v1/rrhh/areas/export/', {
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
    const response = await apiClient.post('/api/v1/rrhh/areas/search/', {
      query,
      filters
    })
    return response.data.data || response.data.results || response.data
  },

  // Validaciones
  async validateAreaSiglas(siglas: string, excludeId?: number): Promise<{
    is_valid: boolean
    message?: string
  }> {
    const response = await apiClient.post('/api/v1/rrhh/areas/validate-siglas/', {
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
    const response = await apiClient.post('/api/v1/rrhh/areas/validate/', data)
    return response.data.data || response.data
  },

  // Operaciones masivas
  async bulkUpdateAreas(updates: Array<{
    id: number
    data: Partial<CreateAreaData>
  }>): Promise<{
    success: number
    errors: Array<{
      id: number
      error: string
    }>
  }> {
    const response = await apiClient.post('/api/v1/rrhh/areas/bulk-update/', { updates })
    return response.data.data || response.data
  },

  async bulkDeleteAreas(ids: number[]): Promise<{
    deleted: number
    errors: Array<{
      id: number
      error: string
    }>
  }> {
    const response = await apiClient.post('/api/v1/rrhh/areas/bulk-delete/', { ids })
    return response.data.data || response.data
  },

  // Historial y auditoría
  async getAreaHistory(areaId: number): Promise<Array<{
    id: number
    action: string
    changes: Record<string, any>
    user: string
    timestamp: string
  }>> {
    const response = await apiClient.get(`/api/v1/rrhh/areas/${areaId}/history/`)
    return response.data.data || response.data.results || response.data
  },

  // Configuración y metadatos
  async getAreaMetadata(): Promise<{
    organos_disponibles: string[]
    estados_disponibles: Array<{ value: string, label: string }>
    campos_requeridos: string[]
    validaciones: Record<string, any>
  }> {
    const response = await apiClient.get('/api/v1/rrhh/areas/metadata/')
    return response.data.data || response.data
  }
}

export default areasService