import { apiClient } from '@/shared/api/api'
import { unwrapBlobError } from '@/shared/api/blob'

/**
 * displacementService — frontend client for B.13 Displacement (Module 03.6).
 *
 * Routes at /api/v1/organization/displacements/ +
 * /api/v1/organization/displacement-extensions/.
 */

export type DisplacementKind =
  | 'rotacion'
  | 'encargatura'
  | 'destaque'
  | 'comision'
  | 'designacion'
  | 'transferencia'
  | 'permuta'

export type DisplacementStatus =
  | 'draft'
  | 'pending_supervisor'
  | 'pending_hr'
  | 'pending_titular'
  | 'approved'
  | 'active'
  | 'completed'
  | 'cancelled'

export interface DisplacementExtension {
  id: string
  displacement: string
  previous_end_date: string
  new_end_date: string
  reason: string
  resolution_number: string
  granted_by: string | null
  granted_at: string
}

export interface Displacement {
  id: string
  tenant?: string | null
  employee: string
  kind: DisplacementKind
  kind_display: string
  status: DisplacementStatus
  status_display: string
  origen_department: string
  destino_department: string
  origen_position: string | null
  destino_position: string | null
  destino_entidad_externa: string
  start_date: string
  end_date: string | null
  justification: string
  resolution_number: string
  requested_by: string | null
  approved_by_supervisor: string | null
  approved_by_supervisor_at: string | null
  approved_by_hr: string | null
  approved_by_hr_at: string | null
  approved_by_titular: string | null
  approved_by_titular_at: string | null
  cancelled_reason: string
  cancelled_at: string | null
  activated_at: string | null
  completed_at: string | null
  resolution_pdf: string | null
  created_at: string
  updated_at: string
  extensions: DisplacementExtension[]
}

interface PaginatedResponse<T> {
  success?: boolean
  message?: string
  data?: T[] | { results?: T[] } | T
  results?: T[]
}

function unwrapList<T>(resp: { data: PaginatedResponse<T> }): T[] {
  const raw = resp.data
  const fromData = (raw?.data as { results?: T[] } | undefined)?.results
  if (Array.isArray(fromData)) return fromData
  if (Array.isArray(raw?.data)) return raw.data as T[]
  if (Array.isArray(raw?.results)) return raw.results
  return []
}

function unwrapItem<T>(resp: { data: PaginatedResponse<T> }): T {
  const raw = resp.data
  if (
    raw &&
    typeof raw === 'object' &&
    'data' in raw &&
    raw.data &&
    typeof raw.data === 'object' &&
    !Array.isArray(raw.data)
  ) {
    return raw.data as T
  }
  return raw as unknown as T
}

const BASE = '/api/v1/organization/displacements'

export const displacementService = {
  async list(): Promise<Displacement[]> {
    const r = await apiClient.get<PaginatedResponse<Displacement>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<Displacement> {
    const r = await apiClient.get<PaginatedResponse<Displacement>>(`${BASE}/${id}/`)
    return unwrapItem<Displacement>(r)
  },

  async create(payload: Partial<Displacement>): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(`${BASE}/`, payload)
    return unwrapItem<Displacement>(r)
  },

  async submit(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(`${BASE}/${id}/submit/`)
    return unwrapItem<Displacement>(r)
  },

  async approveSupervisor(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(
      `${BASE}/${id}/approve-supervisor/`,
    )
    return unwrapItem<Displacement>(r)
  },

  async approveHR(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(`${BASE}/${id}/approve-hr/`)
    return unwrapItem<Displacement>(r)
  },

  async approveTitular(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(
      `${BASE}/${id}/approve-titular/`,
    )
    return unwrapItem<Displacement>(r)
  },

  async activate(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(`${BASE}/${id}/activate/`)
    return unwrapItem<Displacement>(r)
  },

  async complete(id: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(`${BASE}/${id}/complete/`)
    return unwrapItem<Displacement>(r)
  },

  async cancel(id: string, reason: string): Promise<Displacement> {
    const r = await apiClient.post<PaginatedResponse<Displacement>>(
      `${BASE}/${id}/cancel/`, { reason },
    )
    return unwrapItem<Displacement>(r)
  },

  async extend(
    id: string,
    payload: { new_end_date: string; reason: string; resolution_number?: string },
  ): Promise<DisplacementExtension> {
    const r = await apiClient.post<PaginatedResponse<DisplacementExtension>>(
      `${BASE}/${id}/extend/`, payload,
    )
    return unwrapItem<DisplacementExtension>(r)
  },

  async downloadResolutionPdf(id: string): Promise<Blob> {
    try {
      const r = await apiClient.get<Blob>(`${BASE}/${id}/resolution-pdf/`, {
        responseType: 'blob',
      })
      return r.data
    } catch (err) {
      throw await unwrapBlobError(err)
    }
  },
}
