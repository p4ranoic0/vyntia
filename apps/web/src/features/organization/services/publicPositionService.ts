import { apiClient } from '@/shared/api/api'
import { unwrapBlobError } from '@/shared/api/blob'

/**
 * publicPositionService — frontend client for B.8 public-sector instruments:
 *   - PositionRegister (CPE — Ley 30057 SERVIR / CAP — DL 276/728)
 *   - PositionRegisterEntry (rows for either)
 *   - MPP (Manual de Perfiles de Puestos) PDF download
 *
 * Inverse sector gating from B.7: shown for `useTenantSector() === 'public'`.
 */

export type RegisterType = 'cpe' | 'cap'

export type RegisterStatus =
  | 'draft'
  | 'approved'
  | 'registered_servir'
  | 'superseded'
  | 'archived'

export type EntrySituation = 'ocupada' | 'vacante' | 'prevista'

export type CapClassification =
  | 'fp'
  | 'ec'
  | 'sp_ds'
  | 'sp_ej'
  | 'sp_es'
  | 'sp_ap'
  | 're'

export interface PositionRegister {
  id: string
  tenant?: string | null
  register_type: RegisterType
  register_type_display: string
  title: string
  description?: string
  version: number
  parent_version?: string | null
  status: RegisterStatus
  status_display: string
  effective_date?: string | null
  approved_at?: string | null
  approved_by?: string | null
  servir_registered_at?: string | null
  servir_registration_ref?: string
  entry_count: number
  created_at: string
  updated_at: string
  created_by?: string | null
}

export interface PositionRegisterEntry {
  id: string
  register: string
  position: string
  position_code?: string
  position_name?: string
  sequence: number
  plaza_code?: string
  plaza_count: number
  situacion: EntrySituation
  situacion_display?: string
  nivel_organizacional?: string
  nivel_remunerativo?: string
  clasificacion_cap?: CapClassification | ''
  clasificacion_cap_display?: string
  notes?: string
  created_at: string
  updated_at: string
}

interface PaginatedResponse<T> {
  success?: boolean
  message?: string
  data?: T[] | { results?: T[] } | T
  results?: T[]
  meta?: { pagination?: { total_items?: number; current_page?: number } }
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

export const publicPositionService = {
  // Registers (CPE / CAP)
  async listRegisters(type?: RegisterType): Promise<PositionRegister[]> {
    const qs = new URLSearchParams({ page_size: '100' })
    if (type) qs.set('register_type', type)
    const r = await apiClient.get<PaginatedResponse<PositionRegister>>(
      `/api/v1/organization/position-registers/?${qs.toString()}`,
    )
    return unwrapList(r)
  },

  async getRegister(id: string): Promise<PositionRegister> {
    const r = await apiClient.get<PaginatedResponse<PositionRegister>>(
      `/api/v1/organization/position-registers/${id}/`,
    )
    return unwrapItem<PositionRegister>(r)
  },

  async createRegister(payload: {
    register_type: RegisterType
    title: string
    description?: string
  }): Promise<PositionRegister> {
    const r = await apiClient.post<PaginatedResponse<PositionRegister>>(
      '/api/v1/organization/position-registers/',
      payload,
    )
    return unwrapItem<PositionRegister>(r)
  },

  async approveRegister(id: string, effective_date?: string): Promise<PositionRegister> {
    const r = await apiClient.post<PaginatedResponse<PositionRegister>>(
      `/api/v1/organization/position-registers/${id}/approve/`,
      effective_date ? { effective_date } : {},
    )
    return unwrapItem<PositionRegister>(r)
  },

  async registerInServir(id: string, reference: string): Promise<PositionRegister> {
    const r = await apiClient.post<PaginatedResponse<PositionRegister>>(
      `/api/v1/organization/position-registers/${id}/register-in-servir/`,
      { reference },
    )
    return unwrapItem<PositionRegister>(r)
  },

  // Entries
  async listEntries(registerId: string): Promise<PositionRegisterEntry[]> {
    const r = await apiClient.get<PaginatedResponse<PositionRegisterEntry>>(
      `/api/v1/organization/position-register-entries/?register=${registerId}&page_size=200`,
    )
    return unwrapList(r)
  },

  async upsertEntry(payload: {
    id?: string
    register: string
    position: string
    sequence?: number
    plaza_code?: string
    plaza_count?: number
    situacion?: EntrySituation
    nivel_organizacional?: string
    nivel_remunerativo?: string
    clasificacion_cap?: CapClassification | ''
    notes?: string
  }): Promise<PositionRegisterEntry> {
    if (payload.id) {
      const r = await apiClient.patch<PaginatedResponse<PositionRegisterEntry>>(
        `/api/v1/organization/position-register-entries/${payload.id}/`,
        payload,
      )
      return unwrapItem<PositionRegisterEntry>(r)
    }
    const r = await apiClient.post<PaginatedResponse<PositionRegisterEntry>>(
      '/api/v1/organization/position-register-entries/',
      payload,
    )
    return unwrapItem<PositionRegisterEntry>(r)
  },

  async deleteEntry(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/organization/position-register-entries/${id}/`)
  },

  // MPP
  async downloadMPP(registerId: string): Promise<Blob> {
    try {
      const r = await apiClient.get(
        `/api/v1/organization/position-registers/${registerId}/mpp-pdf/`,
        { responseType: 'blob' },
      )
      return r.data as Blob
    } catch (err) {
      throw await unwrapBlobError(err)
    }
  },
}
