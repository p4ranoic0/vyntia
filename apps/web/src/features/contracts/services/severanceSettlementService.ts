import { apiClient } from '@/shared/api/api'

/**
 * severanceSettlementService — frontend client for B.14 liquidación (Module 03.7).
 *
 * Routes at /api/v1/severance-settlements/.
 */

export type SeveranceStatus = 'draft' | 'computed' | 'paid' | 'void'

export type SeveranceComponent =
  | 'cts'
  | 'vac_truncas'
  | 'grat_trunca'
  | 'indemnizacion'
  | 'otros'

export interface SeveranceLine {
  id: string
  settlement: string
  component: SeveranceComponent
  component_display: string
  amount: string
  base_calculation: Record<string, unknown>
  formula_note: string
  created_at: string
  updated_at: string
}

export interface SeveranceSettlement {
  id: string
  tenant?: string | null
  termination: string
  status: SeveranceStatus
  status_display: string
  sueldo_base: string
  fecha_inicio_contrato: string | null
  fecha_cese: string | null
  total_amount: string
  paid_amount: string
  computed_at: string | null
  computed_by: string | null
  paid_at: string | null
  paid_by: string | null
  manual_override: Record<string, unknown>
  notes: string
  lines: SeveranceLine[]
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

const BASE = '/api/v1/severance-settlements'

export const severanceSettlementService = {
  async list(): Promise<SeveranceSettlement[]> {
    const r = await apiClient.get<PaginatedResponse<SeveranceSettlement>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<SeveranceSettlement> {
    const r = await apiClient.get<PaginatedResponse<SeveranceSettlement>>(
      `${BASE}/${id}/`,
    )
    return unwrapItem<SeveranceSettlement>(r)
  },

  async create(payload: { termination: string; sueldo_base?: string }): Promise<SeveranceSettlement> {
    const r = await apiClient.post<PaginatedResponse<SeveranceSettlement>>(
      `${BASE}/`, payload,
    )
    return unwrapItem<SeveranceSettlement>(r)
  },

  async compute(
    id: string,
    payload: { dias_acumulados_no_gozados?: string | null } = {},
  ): Promise<SeveranceSettlement> {
    const r = await apiClient.post<PaginatedResponse<SeveranceSettlement>>(
      `${BASE}/${id}/compute/`, payload,
    )
    return unwrapItem<SeveranceSettlement>(r)
  },

  async markPaid(
    id: string,
    payload: { paid_total: string; paid_at?: string },
  ): Promise<SeveranceSettlement> {
    const r = await apiClient.post<PaginatedResponse<SeveranceSettlement>>(
      `${BASE}/${id}/mark-paid/`, payload,
    )
    return unwrapItem<SeveranceSettlement>(r)
  },
}
