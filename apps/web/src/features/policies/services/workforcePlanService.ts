import { apiClient } from '@/shared/api/api'

/**
 * workforcePlanService — frontend client for B.15b Workforce + Succession (Module 01 § 3).
 */

export type WorkforcePlanStatus = 'draft' | 'active' | 'completed' | 'archived'
export type SuccessionPlanStatus = 'draft' | 'active' | 'archived'
export type Quarter = 'Q1' | 'Q2' | 'Q3' | 'Q4'
export type Criticality = 'alta' | 'media' | 'baja'
export type ReadinessLevel = 1 | 2 | 3 | 4

export interface WorkforcePlan {
  id: string
  tenant?: string | null
  name: string
  fiscal_year: number
  period_start: string
  period_end: string
  description: string
  status: WorkforcePlanStatus
  status_display: string
  owner_user: string
  created_at: string
  updated_at: string
}

export interface HeadcountProjection {
  id: string
  plan: string
  area: string | null
  position: string | null
  current_headcount: number
  projected_headcount: number
  delta_required: number
  target_quarter: Quarter
  justification: string
  created_at: string
  updated_at: string
}

export interface SuccessionPlan {
  id: string
  tenant?: string | null
  name: string
  fiscal_year: number
  notes: string
  status: SuccessionPlanStatus
  status_display: string
  owner_user: string
  created_at: string
  updated_at: string
}

export interface KeyPosition {
  id: string
  plan: string
  position: string
  criticality: Criticality
  criticality_display: string
  risk_notes: string
  current_holder: string | null
  created_at: string
  updated_at: string
}

export interface SuccessorCandidate {
  id: string
  key_position: string
  employee: string
  readiness_level: ReadinessLevel
  readiness_display: string
  order: number
  notes: string
  created_at: string
  updated_at: string
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

export const workforcePlanService = {
  async listPlans(): Promise<WorkforcePlan[]> {
    const r = await apiClient.get<ApiEnvelope<WorkforcePlan>>(
      '/api/v1/workforce-plans/?page_size=100',
    )
    return unwrapList(r)
  },

  async createPlan(payload: {
    name: string
    fiscal_year: number
    period_start: string
    period_end: string
    owner_user: string
    description?: string
  }): Promise<WorkforcePlan> {
    const r = await apiClient.post<ApiEnvelope<WorkforcePlan>>(
      '/api/v1/workforce-plans/', payload,
    )
    return unwrapItem(r)
  },

  async listProjections(planId?: string): Promise<HeadcountProjection[]> {
    const qs = planId ? `?plan=${planId}&page_size=100` : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<HeadcountProjection>>(
      `/api/v1/headcount-projections/${qs}`,
    )
    return unwrapList(r)
  },

  async createProjection(payload: {
    plan: string
    current_headcount: number
    projected_headcount: number
    target_quarter: Quarter
    area?: string | null
    position?: string | null
    justification?: string
  }): Promise<HeadcountProjection> {
    const r = await apiClient.post<ApiEnvelope<HeadcountProjection>>(
      '/api/v1/headcount-projections/', payload,
    )
    return unwrapItem(r)
  },

  async listSuccessionPlans(): Promise<SuccessionPlan[]> {
    const r = await apiClient.get<ApiEnvelope<SuccessionPlan>>(
      '/api/v1/succession-plans/?page_size=100',
    )
    return unwrapList(r)
  },

  async createSuccessionPlan(payload: {
    name: string
    fiscal_year: number
    owner_user: string
    notes?: string
  }): Promise<SuccessionPlan> {
    const r = await apiClient.post<ApiEnvelope<SuccessionPlan>>(
      '/api/v1/succession-plans/', payload,
    )
    return unwrapItem(r)
  },

  async listKeyPositions(planId?: string): Promise<KeyPosition[]> {
    const qs = planId ? `?plan=${planId}&page_size=100` : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<KeyPosition>>(`/api/v1/key-positions/${qs}`)
    return unwrapList(r)
  },

  async createKeyPosition(payload: {
    plan: string
    position: string
    criticality: Criticality
    current_holder?: string | null
    risk_notes?: string
  }): Promise<KeyPosition> {
    const r = await apiClient.post<ApiEnvelope<KeyPosition>>(
      '/api/v1/key-positions/', payload,
    )
    return unwrapItem(r)
  },

  async listCandidates(keyPositionId?: string): Promise<SuccessorCandidate[]> {
    const qs = keyPositionId
      ? `?key_position=${keyPositionId}&page_size=100`
      : '?page_size=100'
    const r = await apiClient.get<ApiEnvelope<SuccessorCandidate>>(
      `/api/v1/successor-candidates/${qs}`,
    )
    return unwrapList(r)
  },

  async createCandidate(payload: {
    key_position: string
    employee: string
    readiness_level: ReadinessLevel
    order?: number
    notes?: string
  }): Promise<SuccessorCandidate> {
    const r = await apiClient.post<ApiEnvelope<SuccessorCandidate>>(
      '/api/v1/successor-candidates/', payload,
    )
    return unwrapItem(r)
  },
}
