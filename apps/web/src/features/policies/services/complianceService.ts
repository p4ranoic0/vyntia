import { apiClient } from '@/shared/api/api'

/**
 * complianceService — frontend client for B.15b Compliance Matrix (Module 01 § 4).
 */

export type MatrixStatus = 'active' | 'archived'
export type ObligationSource =
  | 'sunat' | 'sunafil' | 'mintra' | 'mtpe'
  | 'servir' | 'essalud' | 'onp' | 'afp'
  | 'interno' | 'otro'
export type ObligationFrequency =
  | 'mensual' | 'trimestral' | 'semestral' | 'anual' | 'unica' | 'ad_hoc'
export type ObligationStatus = 'pendiente' | 'en_curso' | 'cumplido' | 'vencido'
export type Severity = 'alta' | 'media' | 'baja'
export type EvidenceKind = 'archivo' | 'link' | 'nota'

export interface ComplianceMatrix {
  id: string
  tenant?: string | null
  name: string
  fiscal_year: number
  description: string
  status: MatrixStatus
  status_display: string
  owner_user: string
  created_at: string
  updated_at: string
}

export interface ComplianceObligation {
  id: string
  matrix: string
  code: string
  title: string
  description: string
  source: ObligationSource
  source_display: string
  frequency: ObligationFrequency
  frequency_display: string
  severity: Severity
  severity_display: string
  next_due_date: string
  last_completed_at: string | null
  status: ObligationStatus
  status_display: string
  responsible_user: string | null
  days_to_due: number
  is_overdue: boolean
  created_at: string
  updated_at: string
}

export interface Evidence {
  id: string
  tenant?: string | null
  obligation: string
  kind: EvidenceKind
  kind_display: string
  file: string | null
  url: string
  note: string
  captured_at: string
  captured_by: string | null
}

export interface ComplianceAlerts {
  overdue: ComplianceObligation[]
  due_soon: ComplianceObligation[]
  cutoff_date: string
}

interface ApiEnvelope<T> {
  data?: T[] | { results?: T[] } | T
  results?: T[]
}

function unwrapList<T>(resp: { data: ApiEnvelope<T> }): T[] {
  const raw = resp.data
  const fromData = (raw?.data as { results?: T[] } | undefined)?.results
  if (Array.isArray(fromData)) return fromData
  if (Array.isArray(raw?.data)) return raw.data as T[]
  if (Array.isArray(raw?.results)) return raw.results
  return []
}

function unwrapItem<T>(resp: { data: ApiEnvelope<T> }): T {
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

export const complianceService = {
  async listMatrices(): Promise<ComplianceMatrix[]> {
    const r = await apiClient.get<ApiEnvelope<ComplianceMatrix>>(
      '/api/v1/compliance-matrices/?page_size=100',
    )
    return unwrapList(r)
  },

  async createMatrix(payload: {
    name: string
    fiscal_year: number
    owner_user: string
    description?: string
  }): Promise<ComplianceMatrix> {
    const r = await apiClient.post<ApiEnvelope<ComplianceMatrix>>(
      '/api/v1/compliance-matrices/', payload,
    )
    return unwrapItem(r)
  },

  async listObligations(matrixId?: string): Promise<ComplianceObligation[]> {
    const qs = matrixId ? `?matrix=${matrixId}&page_size=100` : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<ComplianceObligation>>(
      `/api/v1/compliance-obligations/${qs}`,
    )
    return unwrapList(r)
  },

  async createObligation(payload: {
    matrix: string
    code: string
    title: string
    source: ObligationSource
    frequency: ObligationFrequency
    next_due_date: string
    severity?: Severity
    description?: string
    responsible_user?: string | null
  }): Promise<ComplianceObligation> {
    const r = await apiClient.post<ApiEnvelope<ComplianceObligation>>(
      '/api/v1/compliance-obligations/', payload,
    )
    return unwrapItem(r)
  },

  async markCompleted(id: string, completedAt?: string): Promise<ComplianceObligation> {
    const r = await apiClient.post<ApiEnvelope<ComplianceObligation>>(
      `/api/v1/compliance-obligations/${id}/mark-completed/`,
      completedAt ? { completed_at: completedAt } : {},
    )
    return unwrapItem(r)
  },

  async getAlerts(daysAhead = 30): Promise<ComplianceAlerts> {
    const r = await apiClient.get<ApiEnvelope<ComplianceAlerts>>(
      `/api/v1/compliance-obligations/alertas/?days_ahead=${daysAhead}`,
    )
    return unwrapItem(r)
  },

  async markOverdue(): Promise<{ flagged_overdue: number }> {
    const r = await apiClient.post<ApiEnvelope<{ flagged_overdue: number }>>(
      '/api/v1/compliance-obligations/mark-overdue/',
    )
    return unwrapItem(r)
  },

  async listEvidences(obligationId?: string): Promise<Evidence[]> {
    const qs = obligationId ? `?obligation=${obligationId}&page_size=100` : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<Evidence>>(`/api/v1/evidences/${qs}`)
    return unwrapList(r)
  },
}
