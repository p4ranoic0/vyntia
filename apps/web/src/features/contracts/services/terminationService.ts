import { apiClient } from '@/shared/api/api'

/**
 * terminationService — frontend client for B.14 Termination (Module 03.7).
 *
 * Routes at /api/v1/terminations/.
 */

export type TerminationStatus =
  | 'draft'
  | 'in_progress'
  | 'completed'
  | 'liquidated'
  | 'baja_t_registro_done'
  | 'cancelled'

export type TerminationCausal =
  | 'renuncia'
  | 'mutuo_acuerdo'
  | 'jubilacion'
  | 'fallecimiento'
  | 'despido_justificado'
  | 'despido_arbitrario'
  | 'despido_indirecto'
  | 'vencimiento_plazo'
  | 'destitucion'
  | 'cese_definitivo'
  | 'resolucion_anticipada'
  | 'otros'

export type TerminationRegimen = '728' | '276' | 'cas' | 'mype' | 'otros'

export interface Termination {
  id: string
  tenant?: string | null
  contract: string
  employee: string
  regimen: TerminationRegimen
  regimen_display: string
  causal: TerminationCausal
  causal_display: string
  status: TerminationStatus
  status_display: string
  fecha_cese: string
  last_day_worked: string | null
  motivo: string
  carta_renuncia_file: string | null
  acta_cese_file: string | null
  baja_t_registro: string | null
  initiated_by: string | null
  initiated_at: string | null
  completed_by: string | null
  completed_at: string | null
  liquidated_by: string | null
  liquidated_at: string | null
  cancelled_reason: string
  cancelled_at: string | null
  cancelled_by: string | null
  baja_tregistro_overdue_48h: boolean
  hours_since_completion: number | null
  created_at: string
  updated_at: string
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

const BASE = '/api/v1/terminations'

export const terminationService = {
  async list(): Promise<Termination[]> {
    const r = await apiClient.get<PaginatedResponse<Termination>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<Termination> {
    const r = await apiClient.get<PaginatedResponse<Termination>>(`${BASE}/${id}/`)
    return unwrapItem<Termination>(r)
  },

  async initiate(payload: {
    contract: string
    causal: TerminationCausal
    regimen?: TerminationRegimen
    fecha_cese: string
    last_day_worked?: string
    motivo?: string
  }): Promise<Termination> {
    const r = await apiClient.post<PaginatedResponse<Termination>>(`${BASE}/`, payload)
    return unwrapItem<Termination>(r)
  },

  async complete(id: string): Promise<Termination> {
    const r = await apiClient.post<PaginatedResponse<Termination>>(
      `${BASE}/${id}/complete/`,
    )
    return unwrapItem<Termination>(r)
  },

  async liquidate(id: string): Promise<Termination> {
    const r = await apiClient.post<PaginatedResponse<Termination>>(
      `${BASE}/${id}/liquidate/`,
    )
    return unwrapItem<Termination>(r)
  },

  async markBajaTRegistroDone(
    id: string,
    declaration: string,
  ): Promise<Termination> {
    const r = await apiClient.post<PaginatedResponse<Termination>>(
      `${BASE}/${id}/mark-baja-tregistro-done/`, { declaration },
    )
    return unwrapItem<Termination>(r)
  },

  async cancel(id: string, reason: string): Promise<Termination> {
    const r = await apiClient.post<PaginatedResponse<Termination>>(
      `${BASE}/${id}/cancel/`, { reason },
    )
    return unwrapItem<Termination>(r)
  },

  async alertas48hSLA(): Promise<Termination[]> {
    const r = await apiClient.get<PaginatedResponse<Termination>>(
      `${BASE}/alertas-48h-sla/`,
    )
    const raw = r.data
    if (Array.isArray((raw as { data?: unknown }).data)) {
      return (raw as { data: Termination[] }).data
    }
    return unwrapList(r)
  },
}
