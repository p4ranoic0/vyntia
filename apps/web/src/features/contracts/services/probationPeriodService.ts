import { apiClient } from '@/shared/api/api'

/**
 * probationPeriodService — frontend client for B.11 ProbationPeriod
 * (Module 03.4 período de prueba).
 *
 * Routes at /api/v1/probation-periods/ (flat under /api/v1/).
 */

export type Regimen =
  | '728_comun'
  | '728_calificado'
  | '728_direccion'
  | 'mype_pequena'
  | '276_carrera'
  | 'no_aplica'

export type ProbationStatus =
  | 'pending'
  | 'in_progress'
  | 'evaluated'
  | 'ratified'
  | 'not_renewed'

export interface ProbationPeriod {
  id: string
  tenant?: string | null
  contract: string
  regimen: Regimen
  regimen_display: string
  plazo_dias: number
  start_date: string
  end_date: string
  status: ProbationStatus
  status_display: string
  evaluation_score: number | null
  evaluation_competencies: Record<string, unknown>
  evaluator: string | null
  evaluated_at: string | null
  decision_reason: string
  decided_by: string | null
  decided_at: string | null
  days_remaining: number
  is_within_30_days: boolean
  is_within_15_days: boolean
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

const BASE = '/api/v1/probation-periods'

export const probationPeriodService = {
  async list(): Promise<ProbationPeriod[]> {
    const r = await apiClient.get<PaginatedResponse<ProbationPeriod>>(
      `${BASE}/?page_size=100`,
    )
    return unwrapList(r)
  },

  async get(id: string): Promise<ProbationPeriod> {
    const r = await apiClient.get<PaginatedResponse<ProbationPeriod>>(`${BASE}/${id}/`)
    return unwrapItem<ProbationPeriod>(r)
  },

  async create(payload: {
    contract: string
    regimen?: Regimen
    start_date?: string
  }): Promise<ProbationPeriod> {
    const r = await apiClient.post<PaginatedResponse<ProbationPeriod>>(`${BASE}/`, payload)
    return unwrapItem<ProbationPeriod>(r)
  },

  async start(id: string): Promise<ProbationPeriod> {
    const r = await apiClient.post<PaginatedResponse<ProbationPeriod>>(`${BASE}/${id}/start/`)
    return unwrapItem<ProbationPeriod>(r)
  },

  async evaluate(
    id: string,
    payload: { score: number; competencies?: Record<string, unknown>; comments?: string },
  ): Promise<ProbationPeriod> {
    const r = await apiClient.post<PaginatedResponse<ProbationPeriod>>(
      `${BASE}/${id}/evaluate/`, payload,
    )
    return unwrapItem<ProbationPeriod>(r)
  },

  async ratify(id: string): Promise<ProbationPeriod> {
    const r = await apiClient.post<PaginatedResponse<ProbationPeriod>>(`${BASE}/${id}/ratify/`)
    return unwrapItem<ProbationPeriod>(r)
  },

  async notRenew(id: string, reason: string): Promise<ProbationPeriod> {
    const r = await apiClient.post<PaginatedResponse<ProbationPeriod>>(
      `${BASE}/${id}/not-renew/`,
      { reason },
    )
    return unwrapItem<ProbationPeriod>(r)
  },

  async alertas(): Promise<{
    within_30_days: ProbationPeriod[]
    within_15_days: ProbationPeriod[]
  }> {
    const r = await apiClient.get<
      PaginatedResponse<{ within_30_days: ProbationPeriod[]; within_15_days: ProbationPeriod[] }>
    >(`${BASE}/alertas/`)
    return unwrapItem(r)
  },
}
