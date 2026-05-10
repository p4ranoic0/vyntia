import { apiClient } from '@/shared/api/api'

/** Position (B.6) — catalog of jobs with inline versioning per ADR-B.7. */
export interface Position {
  id: string
  tenant?: string | null
  code: string
  name: string
  description?: string
  version: number
  parent_version?: string | null
  effective_date: string
  is_current: boolean
  department: string
  department_name?: string
  occupational_category?: string | null
  occupational_category_name?: string
  ciuo_code?: string | null
  ciuo_code_name?: string
  reports_to?: string | null
  is_active: boolean
  has_successors: boolean
  created_at: string
  updated_at: string
  created_by?: string | null
}

/** Plaza — actual occupied/vacant position slot. */
export interface Plaza {
  id: string
  tenant?: string | null
  code: string
  position: string
  position_code?: string
  position_name?: string
  current_employee?: string | null
  current_employee_name?: string
  status: 'vacante' | 'ocupada' | 'congelada' | 'eliminada'
  status_display: string
  opened_at?: string | null
  closed_at?: string | null
  notes?: string
  created_at: string
  updated_at: string
}

export interface OccupationalCategory {
  id: string
  code: string
  name: string
  description?: string
  is_active: boolean
}

export interface CIUOCode {
  id: string
  code: string
  name: string
  description?: string
  big_group?: string
  is_active: boolean
}

/** Department row — augmented with B.6 unit_type + cost_center. */
export interface OrgDepartment {
  id: string
  nombre_organo: string
  nombre_unidad_organica?: string
  siglas_area: string
  unit_type?: 'direccion' | 'gerencia' | 'subgerencia' | 'oficina' | 'area' | 'equipo'
  cost_center?: string | null
  area_padre?: string | null
  nivel_jerarquico?: number
  estado_area: string
  nombre_completo?: string
}

/** Generic paginated wrapper from the VYNTIA APIResponse shape. */
interface PaginatedResponse<T> {
  success?: boolean
  message?: string
  data?: T[] | { results?: T[] }
  results?: T[]
  meta?: { pagination?: { total_items?: number; current_page?: number } }
}

function unwrap<T>(resp: { data: PaginatedResponse<T> }): T[] {
  const raw = resp.data
  const fromData = (raw?.data as { results?: T[] } | undefined)?.results
  if (Array.isArray(fromData)) return fromData
  if (Array.isArray(raw?.data)) return raw.data as T[]
  if (Array.isArray(raw?.results)) return raw.results
  return []
}

export const orgchartService = {
  async listDepartments(): Promise<OrgDepartment[]> {
    const response = await apiClient.get<PaginatedResponse<OrgDepartment>>(
      '/api/v1/organization/departments/?page_size=100',
    )
    return unwrap(response)
  },

  async listPositions(params?: { is_current?: boolean }): Promise<Position[]> {
    const qs = new URLSearchParams()
    qs.set('page_size', '200')
    if (params?.is_current !== undefined) qs.set('is_current', String(params.is_current))
    const response = await apiClient.get<PaginatedResponse<Position>>(
      `/api/v1/organization/positions/?${qs.toString()}`,
    )
    return unwrap(response)
  },

  async listPlazas(params?: { status?: Plaza['status'] }): Promise<Plaza[]> {
    const qs = new URLSearchParams()
    qs.set('page_size', '200')
    if (params?.status) qs.set('status', params.status)
    const response = await apiClient.get<PaginatedResponse<Plaza>>(
      `/api/v1/organization/plazas/?${qs.toString()}`,
    )
    return unwrap(response)
  },

  async listOccupationalCategories(): Promise<OccupationalCategory[]> {
    const response = await apiClient.get<PaginatedResponse<OccupationalCategory>>(
      '/api/v1/organization/occupational-categories/',
    )
    return unwrap(response)
  },

  async listCIUOCodes(): Promise<CIUOCode[]> {
    const response = await apiClient.get<PaginatedResponse<CIUOCode>>(
      '/api/v1/organization/ciuo-codes/?page_size=500',
    )
    return unwrap(response)
  },

  /** Update Department.area_padre (drag-drop reparent). */
  async reparentDepartment(departmentId: string, newParentId: string | null): Promise<void> {
    await apiClient.patch(`/api/v1/organization/departments/${departmentId}/`, {
      area_padre: newParentId,
    })
  },

  /** Change a Position's department (drag-drop). */
  async movePositionToDepartment(positionId: string, departmentId: string): Promise<void> {
    await apiClient.patch(`/api/v1/organization/positions/${positionId}/`, {
      department: departmentId,
    })
  },

  /** Reassign Plaza to a different employee via vacate + occupy. */
  async reassignPlaza(plazaId: string, newEmployeeId: string): Promise<void> {
    await apiClient.post(`/api/v1/organization/plazas/${plazaId}/vacate/`, {})
    await apiClient.post(`/api/v1/organization/plazas/${plazaId}/occupy/`, {
      employee: newEmployeeId,
    })
  },
}
